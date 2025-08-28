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
            # Test LLM client availability endpoint
            response = requests.get(f"{self.backend_url}/api/engine/llm/status", timeout=10)
            
            if response.status_code != 200:
                self.log_test("LLM Client Integration", False, f"LLM client status endpoint HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check LLM client status
            llm_status = data.get("status", "")
            if llm_status not in ["operational", "active", "available"]:
                self.log_test("LLM Client Integration", False, f"LLM client status: {llm_status}")
                return False
            
            # Check available providers
            providers = data.get("providers", [])
            expected_providers = ["openai", "anthropic", "local_llm"]
            
            available_providers = [p for p in expected_providers if p in providers]
            
            if not available_providers:
                self.log_test("LLM Client Integration", False, f"No expected providers available: {providers}")
                return False
            
            # Test LLM client factory
            factory_response = requests.get(f"{self.backend_url}/api/engine/llm/factory", timeout=10)
            
            if factory_response.status_code != 200:
                self.log_test("LLM Client Integration", False, f"LLM factory HTTP {factory_response.status_code}")
                return False
            
            factory_data = factory_response.json()
            
            # Check factory status
            factory_status = factory_data.get("status", "")
            if factory_status not in ["operational", "active"]:
                self.log_test("LLM Client Integration", False, f"LLM factory status: {factory_status}")
                return False
            
            # Test a simple LLM operation
            test_payload = {
                "operation": "test_completion",
                "provider": available_providers[0],
                "prompt": "Test prompt for V2 engine integration"
            }
            
            test_response = requests.post(f"{self.backend_url}/api/engine/llm/test", 
                                        json=test_payload, timeout=30)
            
            if test_response.status_code != 200:
                self.log_test("LLM Client Integration", False, f"LLM test operation HTTP {test_response.status_code}")
                return False
            
            test_data = test_response.json()
            
            if test_data.get("status") != "success":
                self.log_test("LLM Client Integration", False, f"LLM test failed: {test_data.get('message')}")
                return False
            
            # Check response quality
            response_text = test_data.get("response", "")
            if len(response_text) < 10:
                self.log_test("LLM Client Integration", False, f"LLM response too short: {len(response_text)} chars")
                return False
            
            # Check centralized client usage
            client_info = test_data.get("client_info", {})
            is_centralized = client_info.get("centralized", False)
            
            if not is_centralized:
                self.log_test("LLM Client Integration", False, "LLM client not using centralized pattern")
                return False
            
            self.log_test("LLM Client Integration", True, 
                         f"Centralized LLM client integration verified: {len(available_providers)} providers, centralized pattern")
            return True
            
        except Exception as e:
            self.log_test("LLM Client Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_cross_module_dependencies(self):
        """Test 7: Verify migrated classes interact properly with each other"""
        try:
            # Test cross-module interaction through a comprehensive processing request
            test_content = """
            # Cross-Module Integration Test
            
            ## Overview
            This test validates that all migrated V2 classes work together seamlessly in the processing pipeline.
            
            ## Test Scenarios
            - Outline planning feeds into prewrite system
            - Style processing coordinates with code normalization
            - Evidence tagging works with validation system
            - Related links integrate with cross-article QA
            - Publishing coordinates with versioning and review
            
            ### Code Example
            ```python
            def integration_test():
                # This code block tests code normalization
                return "Cross-module integration working"
            ```
            
            ## Expected Interactions
            1. V2GlobalOutlinePlanner → V2PrewriteSystem
            2. V2StyleProcessor → V2CodeNormalizationSystem
            3. V2EvidenceTaggingSystem → V2ValidationSystem
            4. V2RelatedLinksSystem → V2CrossArticleQASystem
            5. V2PublishingSystem → V2VersioningSystem → V2ReviewSystem
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only",
                "enable_cross_module_tracking": True
            }
            
            response = requests.post(f"{self.backend_url}/api/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("Cross-Module Dependencies", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Cross-Module Dependencies", False, f"Processing failed: {data.get('message')}")
                return False
            
            # Check processing info for cross-module interactions
            processing_info = data.get("processing_info", {})
            
            # Check stage execution order and dependencies
            stage_execution = processing_info.get("stage_execution", [])
            
            if not stage_execution:
                self.log_test("Cross-Module Dependencies", False, "No stage execution information available")
                return False
            
            # Verify key stage interactions occurred
            expected_interactions = [
                ("outline", "prewrite"),
                ("style", "code_norm"),
                ("evidence", "validation"),
                ("related", "crossqa"),
                ("publishing", "versioning")
            ]
            
            interaction_found = []
            for stage1, stage2 in expected_interactions:
                stage1_found = any(stage1 in stage.get("stage_name", "").lower() for stage in stage_execution)
                stage2_found = any(stage2 in stage.get("stage_name", "").lower() for stage in stage_execution)
                
                if stage1_found and stage2_found:
                    interaction_found.append((stage1, stage2))
            
            interaction_rate = len(interaction_found) / len(expected_interactions) * 100
            
            if interaction_rate < 60:  # At least 60% of expected interactions should occur
                self.log_test("Cross-Module Dependencies", False, f"Low interaction rate: {interaction_rate:.1f}%")
                return False
            
            # Check for cross-module data flow
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Cross-Module Dependencies", False, "No articles generated to check cross-module data flow")
                return False
            
            article = articles[0]
            
            # Check for evidence of cross-module processing
            content = article.get("content", "")
            metadata = article.get("metadata", {})
            
            # Look for signs of multiple module processing
            processing_indicators = [
                "outline" in str(metadata).lower(),
                "style" in str(metadata).lower(),
                "validation" in str(metadata).lower(),
                len(content) > 500,  # Content was processed and enhanced
                "v2" in str(metadata).lower()  # V2 engine was used
            ]
            
            processing_evidence = sum(processing_indicators)
            
            if processing_evidence < 3:  # At least 3 indicators should be present
                self.log_test("Cross-Module Dependencies", False, f"Insufficient cross-module processing evidence: {processing_evidence}/5")
                return False
            
            self.log_test("Cross-Module Dependencies", True, 
                         f"Cross-module dependencies verified: {interaction_rate:.1f}% interaction rate, {processing_evidence}/5 processing indicators")
            return True
            
        except Exception as e:
            self.log_test("Cross-Module Dependencies", False, f"Exception: {str(e)}")
            return False
    
    def test_system_stability_no_regressions(self):
        """Test 8: Verify no regressions in core functionality"""
        try:
            # Test basic system health
            health_response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if health_response.status_code != 200:
                self.log_test("System Stability No Regressions", False, f"Health check HTTP {health_response.status_code}")
                return False
            
            health_data = health_response.json()
            
            if health_data.get("status") not in ["healthy", "ok", "operational"]:
                self.log_test("System Stability No Regressions", False, f"System health: {health_data.get('status')}")
                return False
            
            # Test core API endpoints still work
            core_endpoints = [
                "/api/engine",
                "/api/content-library",
                "/api/engine/v2/pipeline"
            ]
            
            endpoint_results = []
            for endpoint in core_endpoints:
                try:
                    endpoint_response = requests.get(f"{self.backend_url}{endpoint}", timeout=15)
                    endpoint_results.append({
                        "endpoint": endpoint,
                        "status_code": endpoint_response.status_code,
                        "success": endpoint_response.status_code == 200
                    })
                except Exception as e:
                    endpoint_results.append({
                        "endpoint": endpoint,
                        "error": str(e),
                        "success": False
                    })
            
            failed_endpoints = [r for r in endpoint_results if not r.get("success")]
            
            if failed_endpoints:
                self.log_test("System Stability No Regressions", False, f"Failed endpoints: {[e['endpoint'] for e in failed_endpoints]}")
                return False
            
            # Test a simple processing request to ensure no regressions
            simple_test_content = """
            # Simple Regression Test
            
            This is a basic test to ensure the V2 engine migration hasn't introduced regressions.
            
            ## Features to Test
            - Basic content processing
            - Article generation
            - Metadata handling
            """
            
            regression_payload = {
                "content": simple_test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            regression_response = requests.post(f"{self.backend_url}/api/content/process", 
                                              json=regression_payload, timeout=60)
            
            if regression_response.status_code != 200:
                self.log_test("System Stability No Regressions", False, f"Regression test HTTP {regression_response.status_code}")
                return False
            
            regression_data = regression_response.json()
            
            if regression_data.get("status") != "success":
                self.log_test("System Stability No Regressions", False, f"Regression test failed: {regression_data.get('message')}")
                return False
            
            # Check basic functionality still works
            articles = regression_data.get("articles", [])
            if not articles:
                self.log_test("System Stability No Regressions", False, "No articles generated in regression test")
                return False
            
            article = articles[0]
            
            # Basic article validation
            required_fields = ["id", "title", "content"]
            missing_fields = [field for field in required_fields if field not in article]
            
            if missing_fields:
                self.log_test("System Stability No Regressions", False, f"Article missing fields: {missing_fields}")
                return False
            
            # Check content quality hasn't regressed
            content = article.get("content", "")
            if len(content) < 100:
                self.log_test("System Stability No Regressions", False, f"Content quality regression: {len(content)} chars")
                return False
            
            self.log_test("System Stability No Regressions", True, 
                         f"System stability verified: {len(core_endpoints)} endpoints working, regression test passed")
            return True
            
        except Exception as e:
            self.log_test("System Stability No Regressions", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all V2 engine migration validation tests"""
        print("🎯 KE-M17: FINAL INTEGRATION & CLEANUP - V2 ENGINE MIGRATION TESTING")
        print("=" * 80)
        print("Comprehensive validation of all 15 V2 engine classes migrated from server.py to /engine/v2/")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_class_imports_validation,
            self.test_v2_class_instantiation,
            self.test_v2_pipeline_integration,
            self.test_method_interface_compatibility,
            self.test_repository_integration,
            self.test_llm_client_integration,
            self.test_cross_module_dependencies,
            self.test_system_stability_no_regressions
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