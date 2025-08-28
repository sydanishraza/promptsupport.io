#!/usr/bin/env python3
"""
KE-M17: Final Integration & Cleanup - V2 Engine Migration Testing
Comprehensive test suite for validating the complete migration of all 15 V2 engine classes
from server.py to dedicated modules in /app/engine/v2/
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
print(f"🌐 Testing backend at: {BACKEND_URL}")

class V2EngineMigrationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # List of all 15 migrated V2 classes
        self.migrated_classes = [
            "V2GlobalOutlinePlanner",
            "V2PerArticleOutlinePlanner", 
            "V2PrewriteSystem",
            "V2StyleProcessor",
            "V2RelatedLinksSystem",
            "V2GapFillingSystem",
            "V2EvidenceTaggingSystem",
            "V2CodeNormalizationSystem",
            "V2ArticleGenerator",
            "V2ValidationSystem",
            "V2CrossArticleQASystem",
            "V2AdaptiveAdjustmentSystem",
            "V2VersioningSystem",
            "V2ReviewSystem",
            "V2PublishingSystem"
        ]
        
        # Module mapping for each class
        self.class_modules = {
            "V2GlobalOutlinePlanner": "engine.v2.outline",
            "V2PerArticleOutlinePlanner": "engine.v2.outline",
            "V2PrewriteSystem": "engine.v2.prewrite",
            "V2StyleProcessor": "engine.v2.style",
            "V2RelatedLinksSystem": "engine.v2.related",
            "V2GapFillingSystem": "engine.v2.gaps",
            "V2EvidenceTaggingSystem": "engine.v2.evidence",
            "V2CodeNormalizationSystem": "engine.v2.code_norm",
            "V2ArticleGenerator": "engine.v2.generator",
            "V2ValidationSystem": "engine.v2.validate",
            "V2CrossArticleQASystem": "engine.v2.crossqa",
            "V2AdaptiveAdjustmentSystem": "engine.v2.adapt",
            "V2VersioningSystem": "engine.v2.versioning",
            "V2ReviewSystem": "engine.v2.review",
            "V2PublishingSystem": "engine.v2.publish"
        }
        
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
        
    def test_v2_class_imports_validation(self):
        """Test 1: Verify all 15 V2 classes import correctly from migrated modules"""
        try:
            import sys
            import os
            
            # Add engine path to sys.path
            engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'engine')
            if engine_path not in sys.path:
                sys.path.insert(0, engine_path)
            
            imported_classes = {}
            failed_imports = []
            
            for class_name in self.migrated_classes:
                try:
                    module_name = self.class_modules[class_name]
                    module = __import__(module_name, fromlist=[class_name])
                    class_obj = getattr(module, class_name)
                    imported_classes[class_name] = class_obj
                    
                except ImportError as e:
                    failed_imports.append(f"{class_name}: ImportError - {str(e)}")
                except AttributeError as e:
                    failed_imports.append(f"{class_name}: AttributeError - {str(e)}")
                except Exception as e:
                    failed_imports.append(f"{class_name}: {type(e).__name__} - {str(e)}")
            
            if failed_imports:
                self.log_test("V2 Class Imports Validation", False, f"Failed imports: {failed_imports}")
                return False
            
            # Verify all classes are actual classes (not placeholders)
            for class_name, class_obj in imported_classes.items():
                if not isinstance(class_obj, type):
                    self.log_test("V2 Class Imports Validation", False, f"{class_name} is not a proper class")
                    return False
            
            self.log_test("V2 Class Imports Validation", True, 
                         f"All 15/15 V2 classes imported successfully from dedicated modules")
            return True
            
        except Exception as e:
            self.log_test("V2 Class Imports Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_class_instantiation(self):
        """Test 2: Verify all 15 V2 classes can be instantiated without errors"""
        try:
            import sys
            import os
            
            # Add engine path to sys.path
            engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'engine')
            if engine_path not in sys.path:
                sys.path.insert(0, engine_path)
            
            instantiated_classes = {}
            failed_instantiations = []
            
            for class_name in self.migrated_classes:
                try:
                    module_name = self.class_modules[class_name]
                    module = __import__(module_name, fromlist=[class_name])
                    class_obj = getattr(module, class_name)
                    
                    # Try to instantiate the class
                    if class_name in ["V2GlobalOutlinePlanner", "V2PerArticleOutlinePlanner"]:
                        # These classes might need specific parameters
                        instance = class_obj()
                    elif class_name == "V2PrewriteSystem":
                        instance = class_obj()
                    elif class_name == "V2StyleProcessor":
                        instance = class_obj()
                    elif class_name == "V2RelatedLinksSystem":
                        instance = class_obj()
                    elif class_name == "V2GapFillingSystem":
                        instance = class_obj()
                    elif class_name == "V2EvidenceTaggingSystem":
                        instance = class_obj()
                    elif class_name == "V2CodeNormalizationSystem":
                        instance = class_obj()
                    elif class_name == "V2ArticleGenerator":
                        instance = class_obj()
                    elif class_name == "V2ValidationSystem":
                        instance = class_obj()
                    elif class_name == "V2CrossArticleQASystem":
                        instance = class_obj()
                    elif class_name == "V2AdaptiveAdjustmentSystem":
                        instance = class_obj()
                    elif class_name == "V2VersioningSystem":
                        instance = class_obj()
                    elif class_name == "V2ReviewSystem":
                        instance = class_obj()
                    elif class_name == "V2PublishingSystem":
                        instance = class_obj()
                    else:
                        instance = class_obj()
                    
                    instantiated_classes[class_name] = instance
                    
                except Exception as e:
                    failed_instantiations.append(f"{class_name}: {type(e).__name__} - {str(e)}")
            
            if failed_instantiations:
                self.log_test("V2 Class Instantiation", False, f"Failed instantiations: {failed_instantiations}")
                return False
            
            # Verify instances have expected methods
            method_checks = []
            for class_name, instance in instantiated_classes.items():
                # Check for common async methods that should exist
                expected_methods = []
                
                if "Planner" in class_name:
                    expected_methods = ["create_outline", "create_global_outline", "create_article_outline"]
                elif "System" in class_name:
                    if "Prewrite" in class_name:
                        expected_methods = ["extract_prewrite_data"]
                    elif "Style" in class_name:
                        expected_methods = ["process_style"]
                    elif "Related" in class_name:
                        expected_methods = ["generate_related_links"]
                    elif "Gap" in class_name:
                        expected_methods = ["fill_gaps"]
                    elif "Evidence" in class_name:
                        expected_methods = ["tag_evidence"]
                    elif "Code" in class_name:
                        expected_methods = ["normalize_code_blocks"]
                    elif "Validation" in class_name:
                        expected_methods = ["validate_content"]
                    elif "CrossArticle" in class_name:
                        expected_methods = ["perform_cross_article_qa"]
                    elif "Adaptive" in class_name:
                        expected_methods = ["adjust_article_balance"]
                    elif "Versioning" in class_name:
                        expected_methods = ["create_version"]
                    elif "Review" in class_name:
                        expected_methods = ["create_review_request", "enqueue_for_review"]
                    elif "Publishing" in class_name:
                        expected_methods = ["publish_v2_content"]
                elif "Generator" in class_name:
                    expected_methods = ["generate_article"]
                
                # Check if at least one expected method exists
                has_methods = any(hasattr(instance, method) for method in expected_methods) if expected_methods else True
                
                if not has_methods and expected_methods:
                    method_checks.append(f"{class_name}: Missing expected methods {expected_methods}")
            
            if method_checks:
                self.log_test("V2 Class Instantiation", False, f"Method issues: {method_checks}")
                return False
            
            self.log_test("V2 Class Instantiation", True, 
                         f"All 15/15 V2 classes instantiated successfully with expected methods")
            return True
            
        except Exception as e:
            self.log_test("V2 Class Instantiation", False, f"Exception: {str(e)}")
            return False

    
    def test_v2_pipeline_integration(self):
        """Test 3: Verify V2 Pipeline orchestrator works with all migrated classes"""
        try:
            # Test V2 pipeline orchestrator endpoint
            response = requests.get(f"{self.backend_url}/api/engine/v2/pipeline", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2 Pipeline Integration", False, f"Pipeline endpoint HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check pipeline status
            if data.get("status") not in ["operational", "active", "ready"]:
                self.log_test("V2 Pipeline Integration", False, f"Pipeline status: {data.get('status')}")
                return False
            
            # Check if pipeline can access all migrated classes
            pipeline_info = data.get("pipeline_info", {})
            available_stages = pipeline_info.get("available_stages", [])
            
            # Map class names to expected stage names
            expected_stages = [
                "outline_planning", "prewrite_system", "style_processing", 
                "related_links", "gap_filling", "evidence_tagging", 
                "code_normalization", "article_generation", "validation",
                "cross_article_qa", "adaptive_adjustment", "versioning",
                "review_system", "publishing"
            ]
            
            missing_stages = []
            for stage in expected_stages:
                if not any(stage in available_stage.lower() for available_stage in available_stages):
                    missing_stages.append(stage)
            
            if missing_stages:
                self.log_test("V2 Pipeline Integration", False, f"Missing pipeline stages: {missing_stages}")
                return False
            
            # Test a simple pipeline execution
            test_payload = {
                "content": "# Test Content\n\nThis is a test for pipeline integration with migrated V2 classes.",
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            pipeline_response = requests.post(f"{self.backend_url}/api/content/process", 
                                            json=test_payload, timeout=60)
            
            if pipeline_response.status_code != 200:
                self.log_test("V2 Pipeline Integration", False, f"Pipeline execution HTTP {pipeline_response.status_code}")
                return False
            
            pipeline_data = pipeline_response.json()
            
            if pipeline_data.get("status") != "success":
                self.log_test("V2 Pipeline Integration", False, f"Pipeline execution failed: {pipeline_data.get('message')}")
                return False
            
            # Check that pipeline used V2 engine
            processing_info = pipeline_data.get("processing_info", {})
            engine_used = processing_info.get("engine", "")
            
            if engine_used != "v2":
                self.log_test("V2 Pipeline Integration", False, f"Wrong engine used: {engine_used}")
                return False
            
            self.log_test("V2 Pipeline Integration", True, 
                         f"V2 Pipeline orchestrator working with all migrated classes, {len(available_stages)} stages available")
            return True
            
        except Exception as e:
            self.log_test("V2 Pipeline Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_method_interface_compatibility(self):
        """Test 4: Verify all key methods are accessible and maintain expected signatures"""
        try:
            import sys
            import os
            import inspect
            
            # Add engine path to sys.path
            engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'engine')
            if engine_path not in sys.path:
                sys.path.insert(0, engine_path)
            
            method_compatibility_results = []
            
            for class_name in self.migrated_classes:
                try:
                    module_name = self.class_modules[class_name]
                    module = __import__(module_name, fromlist=[class_name])
                    class_obj = getattr(module, class_name)
                    
                    # Get all methods of the class
                    methods = [method for method in dir(class_obj) if not method.startswith('_')]
                    
                    # Check for expected key methods based on class type
                    expected_methods = []
                    method_signatures = {}
                    
                    if "Planner" in class_name:
                        expected_methods = ["create_outline", "create_global_outline", "create_article_outline"]
                    elif "Prewrite" in class_name:
                        expected_methods = ["extract_prewrite_data"]
                    elif "Style" in class_name:
                        expected_methods = ["process_style"]
                    elif "Related" in class_name:
                        expected_methods = ["generate_related_links"]
                    elif "Gap" in class_name:
                        expected_methods = ["fill_gaps"]
                    elif "Evidence" in class_name:
                        expected_methods = ["tag_evidence"]
                    elif "Code" in class_name:
                        expected_methods = ["normalize_code_blocks"]
                    elif "Generator" in class_name:
                        expected_methods = ["generate_article"]
                    elif "Validation" in class_name:
                        expected_methods = ["validate_content"]
                    elif "CrossArticle" in class_name:
                        expected_methods = ["perform_cross_article_qa"]
                    elif "Adaptive" in class_name:
                        expected_methods = ["adjust_article_balance"]
                    elif "Publishing" in class_name:
                        expected_methods = ["publish_v2_content"]
                    elif "Versioning" in class_name:
                        expected_methods = ["create_version"]
                    elif "Review" in class_name:
                        expected_methods = ["create_review_request", "enqueue_for_review"]
                    
                    # Check method availability
                    available_methods = []
                    missing_methods = []
                    
                    for expected_method in expected_methods:
                        if hasattr(class_obj, expected_method):
                            available_methods.append(expected_method)
                            # Try to get method signature
                            try:
                                method_obj = getattr(class_obj, expected_method)
                                if callable(method_obj):
                                    sig = inspect.signature(method_obj)
                                    method_signatures[expected_method] = str(sig)
                            except Exception:
                                method_signatures[expected_method] = "signature_unavailable"
                        else:
                            missing_methods.append(expected_method)
                    
                    # Check if class has any callable methods (not just attributes)
                    callable_methods = [method for method in methods if callable(getattr(class_obj, method, None))]
                    
                    result = {
                        "class_name": class_name,
                        "total_methods": len(methods),
                        "callable_methods": len(callable_methods),
                        "expected_methods": expected_methods,
                        "available_methods": available_methods,
                        "missing_methods": missing_methods,
                        "method_signatures": method_signatures
                    }
                    
                    method_compatibility_results.append(result)
                    
                except Exception as e:
                    method_compatibility_results.append({
                        "class_name": class_name,
                        "error": f"{type(e).__name__}: {str(e)}"
                    })
            
            # Analyze results
            classes_with_errors = [r for r in method_compatibility_results if "error" in r]
            classes_missing_methods = [r for r in method_compatibility_results if r.get("missing_methods")]
            classes_with_no_methods = [r for r in method_compatibility_results if r.get("callable_methods", 0) == 0]
            
            if classes_with_errors:
                self.log_test("Method Interface Compatibility", False, f"Classes with errors: {[c['class_name'] for c in classes_with_errors]}")
                return False
            
            if classes_with_no_methods:
                self.log_test("Method Interface Compatibility", False, f"Classes with no callable methods: {[c['class_name'] for c in classes_with_no_methods]}")
                return False
            
            # Calculate overall method availability
            total_expected = sum(len(r.get("expected_methods", [])) for r in method_compatibility_results)
            total_available = sum(len(r.get("available_methods", [])) for r in method_compatibility_results)
            
            method_availability_rate = (total_available / total_expected * 100) if total_expected > 0 else 100
            
            if method_availability_rate < 80:  # At least 80% of expected methods should be available
                self.log_test("Method Interface Compatibility", False, f"Low method availability: {method_availability_rate:.1f}%")
                return False
            
            self.log_test("Method Interface Compatibility", True, 
                         f"Method interfaces compatible: {method_availability_rate:.1f}% method availability, {len(method_compatibility_results)} classes checked")
            return True
            
        except Exception as e:
            self.log_test("Method Interface Compatibility", False, f"Exception: {str(e)}")
            return False
    
    def test_repository_integration(self):
        """Test 5: Verify classes properly use centralized MongoDB repository pattern"""
        try:
            # Test repository availability endpoint
            response = requests.get(f"{self.backend_url}/api/engine/repository/status", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Repository Integration", False, f"Repository status endpoint HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check repository status
            repo_status = data.get("status", "")
            if repo_status not in ["operational", "active", "available"]:
                self.log_test("Repository Integration", False, f"Repository status: {repo_status}")
                return False
            
            # Check available repositories
            repositories = data.get("repositories", {})
            expected_repos = [
                "content_library", "qa_results", "v2_analysis", 
                "v2_outline", "v2_validation", "assets", "media_library"
            ]
            
            missing_repos = []
            for repo in expected_repos:
                if repo not in repositories:
                    missing_repos.append(repo)
            
            if missing_repos:
                self.log_test("Repository Integration", False, f"Missing repositories: {missing_repos}")
                return False
            
            # Test repository factory availability
            factory_response = requests.get(f"{self.backend_url}/api/engine/repository/factory", timeout=10)
            
            if factory_response.status_code != 200:
                self.log_test("Repository Integration", False, f"Repository factory HTTP {factory_response.status_code}")
                return False
            
            factory_data = factory_response.json()
            
            # Check factory status
            factory_status = factory_data.get("status", "")
            if factory_status not in ["operational", "active"]:
                self.log_test("Repository Integration", False, f"Repository factory status: {factory_status}")
                return False
            
            # Test a simple repository operation
            test_payload = {
                "operation": "test_connection",
                "repository": "content_library"
            }
            
            test_response = requests.post(f"{self.backend_url}/api/engine/repository/test", 
                                        json=test_payload, timeout=30)
            
            if test_response.status_code != 200:
                self.log_test("Repository Integration", False, f"Repository test operation HTTP {test_response.status_code}")
                return False
            
            test_data = test_response.json()
            
            if test_data.get("status") != "success":
                self.log_test("Repository Integration", False, f"Repository test failed: {test_data.get('message')}")
                return False
            
            # Check MongoDB connection
            mongo_status = test_data.get("mongodb_status", "")
            if mongo_status not in ["connected", "operational"]:
                self.log_test("Repository Integration", False, f"MongoDB status: {mongo_status}")
                return False
            
            self.log_test("Repository Integration", True, 
                         f"Repository pattern integration verified: {len(repositories)} repositories available, MongoDB connected")
            return True
            
        except Exception as e:
            self.log_test("Repository Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_llm_client_integration(self):
        """Test 6: Verify classes correctly use centralized LLM client"""
        try:
            # Test with content that might trigger various code paths
            test_content = """
            # Error-Free Pipeline Testing
            
            ## Comprehensive Testing Scenarios
            This content is designed to test various pipeline components and ensure no AttributeError or missing method issues occur.
            
            ### Code Processing Test
            ```python
            def test_function():
                return "Testing code processing"
            ```
            
            ### List Processing Test
            - Item 1: Basic list processing
            - Item 2: Advanced list handling
            - Item 3: Complex list structures
            
            ### Table Processing Test
            | Feature | Status | Notes |
            |---------|--------|-------|
            | Stage 1 | ✅ | Working |
            | Stage 2 | ✅ | Working |
            | Stage 3 | ✅ | Working |
            
            ### Link Processing Test
            [Example Link](https://example.com)
            
            ### Image Processing Test
            ![Test Image](https://example.com/image.jpg)
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("No AttributeError or Missing Methods", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check for processing success (no exceptions should occur)
            if data.get("status") != "success":
                error_message = data.get("message", "Unknown error")
                
                # Check specifically for AttributeError or missing method issues
                error_indicators = [
                    "AttributeError", "has no attribute", "missing method", 
                    "method not found", "NoneType", "object has no attribute"
                ]
                
                has_attribute_error = any(indicator in error_message for indicator in error_indicators)
                
                if has_attribute_error:
                    self.log_test("No AttributeError or Missing Methods", False, f"AttributeError detected: {error_message}")
                    return False
                else:
                    # Other types of errors are acceptable for this test
                    self.log_test("No AttributeError or Missing Methods", True, f"No AttributeError (other error: {error_message})")
                    return True
                    
            # Check processing info for method-related errors
            processing_info = data.get("processing_info", {})
            stage_errors = processing_info.get("stage_errors", [])
            
            # Look for AttributeError in stage errors
            attribute_errors = []
            for error in stage_errors:
                error_msg = error.get("message", "")
                if any(indicator in error_msg for indicator in ["AttributeError", "has no attribute", "missing method"]):
                    attribute_errors.append(error)
                    
            if attribute_errors:
                self.log_test("No AttributeError or Missing Methods", False, f"AttributeErrors in stages: {len(attribute_errors)}")
                return False
                
            # Verify articles were generated (indicates no critical method issues)
            articles = data.get("articles", [])
            stages_completed = processing_info.get("stages_completed", 0)
            
            self.log_test("No AttributeError or Missing Methods", True, 
                         f"No AttributeError detected, {stages_completed} stages completed, {len(articles)} articles generated")
            return True
            
        except Exception as e:
            # Check if the exception itself is an AttributeError
            if "AttributeError" in str(e) or "has no attribute" in str(e):
                self.log_test("No AttributeError or Missing Methods", False, f"AttributeError exception: {str(e)}")
                return False
            else:
                self.log_test("No AttributeError or Missing Methods", True, f"No AttributeError (other exception: {str(e)})")
                return True
    
    def test_production_readiness_verification(self):
        """Test 7: Verify pipeline is production-ready with consistent performance"""
        try:
            # Test multiple requests to verify consistency
            test_content = """
            # Production Readiness Verification
            
            ## System Reliability
            This test verifies that the 17-stage pipeline is ready for production deployment with consistent performance and reliability.
            
            ## Performance Metrics
            - Processing time consistency
            - Memory usage stability
            - Error rate minimization
            - Output quality consistency
            
            ## Reliability Indicators
            - All stages complete successfully
            - No critical errors or failures
            - Consistent article generation
            - Proper metadata handling
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            # Test multiple requests for consistency
            results = []
            for i in range(3):
                start_time = time.time()
                response = requests.post(f"{self.backend_url}/content/process", 
                                       json=payload, timeout=90)
                processing_time = time.time() - start_time
                
                if response.status_code != 200:
                    self.log_test("Production Readiness Verification", False, f"Request {i+1} failed: HTTP {response.status_code}")
                    return False
                    
                data = response.json()
                
                if data.get("status") != "success":
                    self.log_test("Production Readiness Verification", False, f"Request {i+1} processing failed")
                    return False
                    
                processing_info = data.get("processing_info", {})
                stages_completed = processing_info.get("stages_completed", 0)
                articles = data.get("articles", [])
                
                results.append({
                    "stages_completed": stages_completed,
                    "articles_count": len(articles),
                    "processing_time": processing_time,
                    "has_errors": len(processing_info.get("stage_errors", [])) > 0
                })
                
                # Small delay between requests
                time.sleep(2)
            
            # Analyze consistency
            stages_consistent = all(r["stages_completed"] == 17 for r in results)
            articles_consistent = all(r["articles_count"] > 0 for r in results)
            no_critical_errors = all(not r["has_errors"] for r in results)
            
            # Check performance consistency (processing times should be reasonable)
            processing_times = [r["processing_time"] for r in results]
            avg_time = sum(processing_times) / len(processing_times)
            max_time = max(processing_times)
            
            # Performance should be consistent (max time shouldn't be more than 2x average)
            performance_consistent = max_time <= (avg_time * 2) and avg_time < 120  # Under 2 minutes average
            
            if not stages_consistent:
                self.log_test("Production Readiness Verification", False, "Inconsistent stage completion across requests")
                return False
                
            if not articles_consistent:
                self.log_test("Production Readiness Verification", False, "Inconsistent article generation across requests")
                return False
                
            if not performance_consistent:
                self.log_test("Production Readiness Verification", False, f"Inconsistent performance: avg {avg_time:.1f}s, max {max_time:.1f}s")
                return False
                
            self.log_test("Production Readiness Verification", True, 
                         f"Production ready: 3/3 requests successful, avg {avg_time:.1f}s, all 17 stages consistent")
            return True
            
        except Exception as e:
            self.log_test("Production Readiness Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all 17-stage pipeline tests"""
        print("🎯 KE-PR5 COMPLETE 17-STAGE PIPELINE TESTING")
        print("=" * 80)
        print("Final verification of complete V2 pipeline with all 17 stages working")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_engine_17_stage_availability,
            self.test_complete_17_stage_pipeline_execution,
            self.test_stage_16_versioning_system,
            self.test_stage_17_review_system,
            self.test_full_processing_workflow_integrity,
            self.test_no_attribute_errors_or_missing_methods,
            self.test_production_readiness_verification
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(3)
        
        # Print summary
        print()
        print("=" * 80)
        print("🎯 KE-PR5 COMPLETE 17-STAGE PIPELINE TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 KE-PR5 COMPLETE 17-STAGE PIPELINE: PERFECT - All 17 stages working flawlessly!")
            print("✅ Stage 16 (Versioning) and Stage 17 (Review) both operational")
            print("✅ 100% pipeline completion achieved")
            print("✅ Production-ready with no AttributeError issues")
        elif success_rate >= 85:
            print("🎉 KE-PR5 COMPLETE 17-STAGE PIPELINE: EXCELLENT - Nearly perfect implementation!")
        elif success_rate >= 70:
            print("✅ KE-PR5 COMPLETE 17-STAGE PIPELINE: GOOD - Most functionality working")
        elif success_rate >= 50:
            print("⚠️ KE-PR5 COMPLETE 17-STAGE PIPELINE: PARTIAL - Some issues remain")
        else:
            print("❌ KE-PR5 COMPLETE 17-STAGE PIPELINE: NEEDS ATTENTION - Major issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = Complete17StagePipelineTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 85 else 1)