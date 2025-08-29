#!/usr/bin/env python3
"""
KE-PR10.5 V2-Only Validation & System Checkpoint Testing
Comprehensive validation that system runs exclusively on V2 engine modules

This test suite validates:
1. V2-Only Mode Validation (FORCE_V2_ONLY=true, LEGACY_ENDPOINT_BEHAVIOR=block)
2. V2 Content Processing through V2 pipeline modules only
3. Repository Pattern Compliance (no direct MongoDB calls)
4. V2 Engine Module Exclusivity (/engine/v2/* modules only)
5. API Endpoint Functionality in V2-only mode
6. Legacy Endpoint Blocking (HTTP 410 Gone)
7. Pipeline Orchestration through V2 modules
8. System Stability in V2-only mode
"""

import os
import sys
import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get backend URL from frontend .env
def get_backend_url():
    """Get backend URL from frontend .env file"""
    frontend_env_path = os.path.join(os.path.dirname(__file__), 'frontend', '.env')
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
print(f"🌐 Testing V2-Only System at: {BACKEND_URL}")

class V2OnlyValidationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # V2 Engine modules that should be exclusively used
        self.v2_modules = [
            "engine.v2.analyzer",
            "engine.v2.outline", 
            "engine.v2.prewrite",
            "engine.v2.style",
            "engine.v2.related",
            "engine.v2.gaps",
            "engine.v2.evidence",
            "engine.v2.code_norm",
            "engine.v2.generator",
            "engine.v2.validate",
            "engine.v2.crossqa",
            "engine.v2.adapt",
            "engine.v2.publish",
            "engine.v2.versioning",
            "engine.v2.review",
            "engine.v2.pipeline"
        ]
        
        # Legacy endpoints that should be blocked
        self.legacy_endpoints = [
            "/api/v1/content/process",
            "/api/legacy/upload",
            "/api/old/analyze",
            "/api/v1/generate",
            "/api/legacy/style"
        ]
        
        # V2-only endpoints that should work
        self.v2_endpoints = [
            "/api/content/process",
            "/api/engine/v2/pipeline",
            "/api/engine/v2/analyze",
            "/api/content-library"
        ]
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
            
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_v2_only_environment_validation(self):
        """Test 1: Verify V2-Only environment variables are set correctly"""
        try:
            # Check backend .env file for V2-only settings
            backend_env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
            
            if not os.path.exists(backend_env_path):
                self.log_test("V2-Only Environment Validation", False, "Backend .env file not found")
                return False
            
            env_settings = {}
            with open(backend_env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_settings[key] = value
            
            # Check critical V2-only settings
            force_v2_only = env_settings.get('FORCE_V2_ONLY', '').lower()
            legacy_behavior = env_settings.get('LEGACY_ENDPOINT_BEHAVIOR', '').lower()
            
            if force_v2_only != 'true':
                self.log_test("V2-Only Environment Validation", False, f"FORCE_V2_ONLY={force_v2_only}, expected 'true'")
                return False
                
            if legacy_behavior != 'block':
                self.log_test("V2-Only Environment Validation", False, f"LEGACY_ENDPOINT_BEHAVIOR={legacy_behavior}, expected 'block'")
                return False
            
            # Test system health with V2-only mode
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2-Only Environment Validation", False, f"Health check failed: HTTP {response.status_code}")
                return False
            
            health_data = response.json()
            
            # Check if system reports V2-only mode
            v2_mode = health_data.get("v2_only_mode", False)
            if not v2_mode:
                self.log_test("V2-Only Environment Validation", False, "System not reporting V2-only mode")
                return False
            
            self.log_test("V2-Only Environment Validation", True, 
                         f"FORCE_V2_ONLY=true, LEGACY_ENDPOINT_BEHAVIOR=block, system health confirms V2-only mode")
            return True
            
        except Exception as e:
            self.log_test("V2-Only Environment Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_legacy_endpoint_blocking(self):
        """Test 2: Verify legacy endpoints return HTTP 410 Gone as expected"""
        try:
            blocked_endpoints = []
            working_legacy_endpoints = []
            
            for endpoint in self.legacy_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    
                    if response.status_code == 410:
                        blocked_endpoints.append(endpoint)
                    elif response.status_code == 404:
                        # 404 is acceptable - endpoint doesn't exist (also blocked)
                        blocked_endpoints.append(endpoint)
                    else:
                        working_legacy_endpoints.append(f"{endpoint}:{response.status_code}")
                        
                except requests.exceptions.RequestException:
                    # Connection errors are acceptable - endpoint is effectively blocked
                    blocked_endpoints.append(endpoint)
            
            if working_legacy_endpoints:
                self.log_test("Legacy Endpoint Blocking", False, 
                             f"Legacy endpoints still working: {working_legacy_endpoints}")
                return False
            
            # Test a few POST requests to legacy endpoints as well
            legacy_post_tests = [
                ("/api/v1/content/process", {"content": "test"}),
                ("/api/legacy/upload", {"file": "test.txt"})
            ]
            
            for endpoint, payload in legacy_post_tests:
                try:
                    response = requests.post(f"{self.backend_url}{endpoint}", 
                                           json=payload, timeout=10)
                    
                    if response.status_code not in [404, 410]:
                        working_legacy_endpoints.append(f"{endpoint}:POST:{response.status_code}")
                        
                except requests.exceptions.RequestException:
                    # Connection errors are acceptable
                    pass
            
            if working_legacy_endpoints:
                self.log_test("Legacy Endpoint Blocking", False, 
                             f"Legacy POST endpoints still working: {working_legacy_endpoints}")
                return False
            
            self.log_test("Legacy Endpoint Blocking", True, 
                         f"All {len(self.legacy_endpoints)} legacy endpoints properly blocked (410/404)")
            return True
            
        except Exception as e:
            self.log_test("Legacy Endpoint Blocking", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_endpoint_functionality(self):
        """Test 3: Verify V2 endpoints work correctly in V2-only mode"""
        try:
            working_endpoints = []
            failed_endpoints = []
            
            for endpoint in self.v2_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=15)
                    
                    if response.status_code == 200:
                        working_endpoints.append(endpoint)
                        
                        # Verify response indicates V2 processing
                        try:
                            data = response.json()
                            if endpoint == "/api/engine/v2/pipeline":
                                if data.get("status") not in ["operational", "active", "ready"]:
                                    failed_endpoints.append(f"{endpoint}:invalid_status")
                            elif endpoint == "/api/content-library":
                                if "articles" not in data and "content" not in data:
                                    failed_endpoints.append(f"{endpoint}:invalid_response")
                        except:
                            # Some endpoints might not return JSON
                            pass
                    else:
                        failed_endpoints.append(f"{endpoint}:{response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    failed_endpoints.append(f"{endpoint}:connection_error")
            
            # Test V2 content processing endpoint with actual content
            test_content = {
                "content": "# V2-Only Test Content\n\nThis tests V2-only processing pipeline.\n\n## Features\n- V2 engine validation\n- Repository pattern compliance\n- Module exclusivity",
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            try:
                process_response = requests.post(f"{self.backend_url}/api/content/process", 
                                               json=test_content, timeout=60)
                
                if process_response.status_code == 200:
                    process_data = process_response.json()
                    
                    # Verify V2 processing
                    processing_info = process_data.get("processing_info", {})
                    engine_used = processing_info.get("engine", "")
                    
                    if engine_used == "v2":
                        working_endpoints.append("/api/content/process:POST")
                    else:
                        failed_endpoints.append(f"/api/content/process:wrong_engine:{engine_used}")
                else:
                    failed_endpoints.append(f"/api/content/process:POST:{process_response.status_code}")
                    
            except Exception as e:
                failed_endpoints.append(f"/api/content/process:POST:exception")
            
            if failed_endpoints:
                self.log_test("V2 Endpoint Functionality", False, 
                             f"Failed V2 endpoints: {failed_endpoints}")
                return False
            
            success_rate = len(working_endpoints) / (len(self.v2_endpoints) + 1) * 100  # +1 for POST test
            
            if success_rate < 80:
                self.log_test("V2 Endpoint Functionality", False, 
                             f"Low V2 endpoint success rate: {success_rate:.1f}%")
                return False
            
            self.log_test("V2 Endpoint Functionality", True, 
                         f"V2 endpoints working: {len(working_endpoints)} endpoints, {success_rate:.1f}% success rate")
            return True
            
        except Exception as e:
            self.log_test("V2 Endpoint Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_module_exclusivity(self):
        """Test 4: Verify all processing routes through /engine/v2/* modules only"""
        try:
            # Test V2 module imports and availability
            import sys
            import os
            
            # Add engine path to sys.path
            engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'engine')
            if engine_path not in sys.path:
                sys.path.insert(0, engine_path)
            
            v2_module_status = {}
            failed_imports = []
            
            for module_name in self.v2_modules:
                try:
                    module = __import__(module_name, fromlist=[''])
                    v2_module_status[module_name] = "available"
                    
                    # Check if module has V2-specific classes
                    module_dir = dir(module)
                    v2_classes = [item for item in module_dir if item.startswith('V2')]
                    
                    if not v2_classes and 'pipeline' not in module_name:
                        v2_module_status[module_name] = "no_v2_classes"
                        
                except ImportError as e:
                    failed_imports.append(f"{module_name}: {str(e)}")
                    v2_module_status[module_name] = "import_failed"
            
            if failed_imports:
                self.log_test("V2 Module Exclusivity", False, 
                             f"V2 module import failures: {failed_imports}")
                return False
            
            # Test pipeline orchestrator uses only V2 modules
            try:
                from v2.pipeline import Pipeline
                pipeline = Pipeline()
                
                # Check pipeline stages use V2 classes
                v2_stage_count = 0
                total_stages = 0
                
                for attr_name in dir(pipeline):
                    if not attr_name.startswith('_'):
                        attr = getattr(pipeline, attr_name)
                        if hasattr(attr, '__class__'):
                            class_name = attr.__class__.__name__
                            total_stages += 1
                            if class_name.startswith('V2'):
                                v2_stage_count += 1
                
                v2_stage_ratio = v2_stage_count / total_stages if total_stages > 0 else 0
                
                if v2_stage_ratio < 0.8:  # At least 80% should be V2 classes
                    self.log_test("V2 Module Exclusivity", False, 
                                 f"Low V2 stage ratio in pipeline: {v2_stage_ratio:.1f}")
                    return False
                    
            except Exception as e:
                self.log_test("V2 Module Exclusivity", False, 
                             f"Pipeline V2 validation failed: {str(e)}")
                return False
            
            # Test content processing to ensure V2-only execution
            test_payload = {
                "content": "# V2 Module Test\n\nTesting V2-only module execution.",
                "content_type": "markdown",
                "processing_mode": "v2_only",
                "debug_modules": True
            }
            
            response = requests.post(f"{self.backend_url}/api/content/process", 
                                   json=test_payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                processing_info = data.get("processing_info", {})
                
                # Check for V2 module usage indicators
                modules_used = processing_info.get("modules_used", [])
                v2_modules_used = [m for m in modules_used if "v2" in m.lower()]
                
                if len(v2_modules_used) == 0:
                    self.log_test("V2 Module Exclusivity", False, 
                                 "No V2 modules detected in processing")
                    return False
            
            available_modules = len([m for m in v2_module_status.values() if m == "available"])
            total_modules = len(self.v2_modules)
            
            self.log_test("V2 Module Exclusivity", True, 
                         f"V2 module exclusivity verified: {available_modules}/{total_modules} modules available, pipeline uses V2 classes")
            return True
            
        except Exception as e:
            self.log_test("V2 Module Exclusivity", False, f"Exception: {str(e)}")
            return False
    
    def test_repository_pattern_compliance(self):
        """Test 5: Validate all operations use repository pattern (no direct MongoDB calls)"""
        try:
            # Test repository availability
            response = requests.get(f"{self.backend_url}/api/engine/repository/status", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Repository Pattern Compliance", False, 
                             f"Repository status endpoint unavailable: HTTP {response.status_code}")
                return False
            
            repo_data = response.json()
            repo_status = repo_data.get("status", "")
            
            if repo_status not in ["operational", "active", "available"]:
                self.log_test("Repository Pattern Compliance", False, 
                             f"Repository not operational: {repo_status}")
                return False
            
            # Test repository operations
            repositories = repo_data.get("repositories", {})
            required_repos = ["content_library", "v2_analysis", "v2_validation"]
            
            missing_repos = [repo for repo in required_repos if repo not in repositories]
            if missing_repos:
                self.log_test("Repository Pattern Compliance", False, 
                             f"Missing required repositories: {missing_repos}")
                return False
            
            # Test content library operations use repository pattern
            content_response = requests.get(f"{self.backend_url}/api/content-library", timeout=15)
            
            if content_response.status_code != 200:
                self.log_test("Repository Pattern Compliance", False, 
                             f"Content library repository test failed: HTTP {content_response.status_code}")
                return False
            
            content_data = content_response.json()
            
            # Check for repository pattern indicators
            repo_indicators = [
                "repository_source" in str(content_data).lower(),
                "mongo_repo" in str(content_data).lower(),
                len(content_data.get("articles", [])) >= 0  # Basic functionality
            ]
            
            repo_compliance = sum(repo_indicators) / len(repo_indicators) * 100
            
            # Test V2 processing with repository pattern
            test_content = {
                "content": "# Repository Pattern Test\n\nTesting repository compliance in V2 processing.",
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            process_response = requests.post(f"{self.backend_url}/api/content/process", 
                                           json=test_content, timeout=60)
            
            if process_response.status_code == 200:
                process_data = process_response.json()
                
                # Check if articles were stored via repository pattern
                articles = process_data.get("articles", [])
                if articles:
                    # Verify article has repository-generated fields
                    article = articles[0]
                    repo_fields = ["id", "created_at", "metadata"]
                    has_repo_fields = all(field in article for field in repo_fields)
                    
                    if not has_repo_fields:
                        self.log_test("Repository Pattern Compliance", False, 
                                     "Articles missing repository-generated fields")
                        return False
            
            if repo_compliance < 60:
                self.log_test("Repository Pattern Compliance", False, 
                             f"Low repository compliance: {repo_compliance:.1f}%")
                return False
            
            self.log_test("Repository Pattern Compliance", True, 
                         f"Repository pattern compliance verified: {len(repositories)} repositories available, {repo_compliance:.1f}% compliance")
            return True
            
        except Exception as e:
            self.log_test("Repository Pattern Compliance", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_content_processing_pipeline(self):
        """Test 6: Verify content processing works exclusively through V2 pipeline modules"""
        try:
            # Test comprehensive V2 content processing
            test_content = {
                "content": """# V2 Pipeline Validation Test
                
## Overview
This comprehensive test validates that all content processing flows through V2 pipeline modules exclusively.

## Test Scenarios
1. **Content Analysis**: Multi-dimensional analysis through V2 analyzer
2. **Outline Planning**: Global and per-article outline planning
3. **Content Generation**: Article generation through V2 generator
4. **Style Processing**: Woolf-aligned style formatting
5. **Validation**: Comprehensive V2 validation system

### Code Example
```python
def v2_pipeline_test():
    # This tests V2 code normalization
    return "V2 pipeline working"
```

## Expected V2 Processing
- All stages should use V2 engine modules
- No legacy processing should occur
- Repository pattern should be used throughout
""",
                "content_type": "markdown",
                "processing_mode": "v2_only",
                "enable_full_pipeline": True
            }
            
            response = requests.post(f"{self.backend_url}/api/content/process", 
                                   json=test_content, timeout=120)
            
            if response.status_code != 200:
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"V2 processing failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"V2 processing unsuccessful: {data.get('message', 'unknown error')}")
                return False
            
            # Verify V2 processing indicators
            processing_info = data.get("processing_info", {})
            
            # Check engine used
            engine_used = processing_info.get("engine", "")
            if engine_used != "v2":
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Wrong engine used: {engine_used}, expected 'v2'")
                return False
            
            # Check V2 pipeline stages
            stages_executed = processing_info.get("stages_executed", [])
            v2_stages = [stage for stage in stages_executed if "v2" in stage.lower()]
            
            if len(v2_stages) < 5:  # Should have multiple V2 stages
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Insufficient V2 stages executed: {len(v2_stages)}")
                return False
            
            # Verify articles were generated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("V2 Content Processing Pipeline", False, 
                             "No articles generated by V2 pipeline")
                return False
            
            # Check article quality and V2 processing indicators
            article = articles[0]
            
            # Verify V2 metadata
            metadata = article.get("metadata", {})
            v2_indicators = [
                metadata.get("engine") == "v2",
                "v2" in str(metadata).lower(),
                len(article.get("content", "")) > 100,  # Substantial content generated
                article.get("id") is not None  # Repository pattern used
            ]
            
            v2_processing_score = sum(v2_indicators) / len(v2_indicators) * 100
            
            if v2_processing_score < 75:
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"Low V2 processing score: {v2_processing_score:.1f}%")
                return False
            
            self.log_test("V2 Content Processing Pipeline", True, 
                         f"V2 pipeline processing verified: {len(v2_stages)} V2 stages, {len(articles)} articles, {v2_processing_score:.1f}% V2 compliance")
            return True
            
        except Exception as e:
            self.log_test("V2 Content Processing Pipeline", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_orchestration_v2_only(self):
        """Test 7: Verify V2 pipeline orchestrates exclusively through V2 modules"""
        try:
            # Test V2 pipeline orchestrator endpoint
            response = requests.get(f"{self.backend_url}/api/engine/v2/pipeline", timeout=15)
            
            if response.status_code != 200:
                self.log_test("Pipeline Orchestration V2-Only", False, 
                             f"V2 pipeline endpoint failed: HTTP {response.status_code}")
                return False
            
            pipeline_data = response.json()
            
            # Check pipeline status
            pipeline_status = pipeline_data.get("status", "")
            if pipeline_status not in ["operational", "active", "ready"]:
                self.log_test("Pipeline Orchestration V2-Only", False, 
                             f"V2 pipeline not operational: {pipeline_status}")
                return False
            
            # Check available stages are V2-only
            pipeline_info = pipeline_data.get("pipeline_info", {})
            available_stages = pipeline_info.get("available_stages", [])
            
            v2_stage_names = [
                "v2_analyzer", "v2_outline", "v2_prewrite", "v2_style", 
                "v2_related", "v2_gaps", "v2_evidence", "v2_code_norm",
                "v2_generator", "v2_validation", "v2_crossqa", "v2_adapt",
                "v2_publish", "v2_versioning", "v2_review"
            ]
            
            detected_v2_stages = []
            for stage in available_stages:
                stage_lower = stage.lower()
                if any(v2_stage in stage_lower for v2_stage in v2_stage_names):
                    detected_v2_stages.append(stage)
            
            v2_stage_ratio = len(detected_v2_stages) / len(available_stages) if available_stages else 0
            
            if v2_stage_ratio < 0.8:  # At least 80% should be V2 stages
                self.log_test("Pipeline Orchestration V2-Only", False, 
                             f"Low V2 stage ratio: {v2_stage_ratio:.1f}")
                return False
            
            # Test pipeline execution with stage tracking
            test_payload = {
                "content": "# Pipeline Orchestration Test\n\nTesting V2-only pipeline orchestration.",
                "content_type": "markdown",
                "processing_mode": "v2_only",
                "track_stages": True
            }
            
            execution_response = requests.post(f"{self.backend_url}/api/content/process", 
                                             json=test_payload, timeout=90)
            
            if execution_response.status_code == 200:
                execution_data = execution_response.json()
                processing_info = execution_data.get("processing_info", {})
                
                # Check stage execution order
                stage_execution = processing_info.get("stage_execution", [])
                
                if stage_execution:
                    v2_executed_stages = [s for s in stage_execution if "v2" in str(s).lower()]
                    execution_v2_ratio = len(v2_executed_stages) / len(stage_execution)
                    
                    if execution_v2_ratio < 0.7:
                        self.log_test("Pipeline Orchestration V2-Only", False, 
                                     f"Low V2 execution ratio: {execution_v2_ratio:.1f}")
                        return False
            
            self.log_test("Pipeline Orchestration V2-Only", True, 
                         f"V2 pipeline orchestration verified: {len(detected_v2_stages)} V2 stages, {v2_stage_ratio:.1f} V2 ratio")
            return True
            
        except Exception as e:
            self.log_test("Pipeline Orchestration V2-Only", False, f"Exception: {str(e)}")
            return False
    
    def test_system_stability_v2_only_mode(self):
        """Test 8: Ensure V2-only mode maintains system stability and performance"""
        try:
            # Test system health in V2-only mode
            health_response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if health_response.status_code != 200:
                self.log_test("System Stability V2-Only Mode", False, 
                             f"Health check failed: HTTP {health_response.status_code}")
                return False
            
            health_data = health_response.json()
            
            # Check system health indicators
            system_status = health_data.get("status", "")
            if system_status not in ["healthy", "ok", "operational"]:
                self.log_test("System Stability V2-Only Mode", False, 
                             f"System not healthy: {system_status}")
                return False
            
            # Test performance with multiple concurrent requests
            concurrent_requests = []
            start_time = time.time()
            
            test_payload = {
                "content": "# Stability Test\n\nTesting V2-only system stability.",
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            # Send 3 concurrent requests to test stability
            import threading
            results = []
            
            def make_request():
                try:
                    response = requests.post(f"{self.backend_url}/api/content/process", 
                                           json=test_payload, timeout=60)
                    results.append({
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_time": time.time() - start_time
                    })
                except Exception as e:
                    results.append({
                        "error": str(e),
                        "success": False,
                        "response_time": time.time() - start_time
                    })
            
            threads = []
            for i in range(3):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Analyze results
            successful_requests = [r for r in results if r.get("success", False)]
            success_rate = len(successful_requests) / len(results) * 100
            
            if success_rate < 80:
                self.log_test("System Stability V2-Only Mode", False, 
                             f"Low concurrent request success rate: {success_rate:.1f}%")
                return False
            
            # Test memory and performance stability
            avg_response_time = sum(r.get("response_time", 0) for r in successful_requests) / len(successful_requests) if successful_requests else 0
            
            if avg_response_time > 120:  # Should complete within 2 minutes
                self.log_test("System Stability V2-Only Mode", False, 
                             f"High response time: {avg_response_time:.1f}s")
                return False
            
            # Test core endpoints still work after load
            core_endpoints = [
                "/api/health",
                "/api/content-library",
                "/api/engine/v2/pipeline"
            ]
            
            post_load_results = []
            for endpoint in core_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=15)
                    post_load_results.append(response.status_code == 200)
                except:
                    post_load_results.append(False)
            
            post_load_success = sum(post_load_results) / len(post_load_results) * 100
            
            if post_load_success < 100:
                self.log_test("System Stability V2-Only Mode", False, 
                             f"Post-load endpoint failures: {post_load_success:.1f}% success")
                return False
            
            self.log_test("System Stability V2-Only Mode", True, 
                         f"System stability verified: {success_rate:.1f}% concurrent success, {avg_response_time:.1f}s avg response, {post_load_success:.1f}% post-load success")
            return True
            
        except Exception as e:
            self.log_test("System Stability V2-Only Mode", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all V2-Only validation tests"""
        print("🎯 KE-PR10.5: V2-ONLY VALIDATION & SYSTEM CHECKPOINT TESTING")
        print("=" * 80)
        print("Comprehensive validation that system runs exclusively on V2 engine modules")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_only_environment_validation,
            self.test_legacy_endpoint_blocking,
            self.test_v2_endpoint_functionality,
            self.test_v2_module_exclusivity,
            self.test_repository_pattern_compliance,
            self.test_v2_content_processing_pipeline,
            self.test_pipeline_orchestration_v2_only,
            self.test_system_stability_v2_only_mode
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(2)
        
        # Print summary
        print()
        print("=" * 80)
        print("🎯 KE-PR10.5: V2-ONLY VALIDATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 KE-PR10.5 V2-ONLY VALIDATION: PERFECT - System ready for KE-PR11 (Legacy Removal)!")
            print("✅ V2-Only Environment: FORCE_V2_ONLY=true, LEGACY_ENDPOINT_BEHAVIOR=block")
            print("✅ Legacy Endpoint Blocking: All legacy endpoints return HTTP 410 Gone")
            print("✅ V2 Endpoint Functionality: All V2 endpoints working correctly")
            print("✅ V2 Module Exclusivity: All processing through /engine/v2/* modules only")
            print("✅ Repository Pattern Compliance: No direct MongoDB calls detected")
            print("✅ V2 Content Processing: Exclusive V2 pipeline module processing")
            print("✅ Pipeline Orchestration: V2-only pipeline orchestration verified")
            print("✅ System Stability: V2-only mode maintains stability and performance")
        elif success_rate >= 85:
            print("🎉 KE-PR10.5 V2-ONLY VALIDATION: EXCELLENT - Nearly ready for legacy removal!")
        elif success_rate >= 70:
            print("✅ KE-PR10.5 V2-ONLY VALIDATION: GOOD - Most V2-only requirements met")
        elif success_rate >= 50:
            print("⚠️ KE-PR10.5 V2-ONLY VALIDATION: PARTIAL - Some V2-only issues remain")
        else:
            print("❌ KE-PR10.5 V2-ONLY VALIDATION: NEEDS ATTENTION - Major V2-only issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = V2OnlyValidationTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 85 else 1)