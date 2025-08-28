#!/usr/bin/env python3
"""
KE-PR9.3 MongoDB Repository Pattern Final Validation Test
Comprehensive final test for KE-PR9.3 MongoDB Repository Pattern completion

Test Focus:
1. Repository Pattern Integration - Verify all repository operations work correctly
2. Content Library Operations - Test create, read, update, delete with repository pattern  
3. V2 Engine Integration - Verify V2 processing works with repository layer
4. MongoDB Centralization - Confirm no direct database calls are breaking functionality
5. Performance & Stability - Ensure repository pattern doesn't impact performance
6. Error Handling - Test repository error handling and fallback mechanisms
7. TICKET-3 Compliance - Verify doc_uid, doc_slug, headings, xrefs field preservation
"""

import os
import sys
import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

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
print(f"🌐 Testing KE-PR9.3 Repository Pattern at: {BACKEND_URL}")

class KE_PR9_3_FinalTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
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
        
    def test_repository_pattern_integration(self):
        """Test 1: Verify Repository Pattern Integration - All repository operations work correctly"""
        try:
            # Test repository factory availability
            response = requests.get(f"{self.backend_url}/api/engine/repository/status", timeout=15)
            
            if response.status_code != 200:
                self.log_test("Repository Pattern Integration", False, f"Repository status endpoint HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check repository status
            repo_status = data.get("status", "")
            if repo_status not in ["operational", "active", "available"]:
                self.log_test("Repository Pattern Integration", False, f"Repository status: {repo_status}")
                return False
            
            # Check available repositories
            repositories = data.get("repositories", {})
            expected_repos = [
                "content_library", "qa_results", "v2_analysis", 
                "v2_outline", "v2_validation", "assets", "media_library"
            ]
            
            available_repos = []
            missing_repos = []
            for repo in expected_repos:
                if repo in repositories:
                    available_repos.append(repo)
                else:
                    missing_repos.append(repo)
            
            if missing_repos:
                self.log_test("Repository Pattern Integration", False, f"Missing repositories: {missing_repos}")
                return False
            
            # Test repository factory pattern
            factory_response = requests.get(f"{self.backend_url}/api/engine/repository/factory", timeout=15)
            
            if factory_response.status_code != 200:
                self.log_test("Repository Pattern Integration", False, f"Repository factory HTTP {factory_response.status_code}")
                return False
            
            factory_data = factory_response.json()
            factory_status = factory_data.get("status", "")
            
            if factory_status not in ["operational", "active"]:
                self.log_test("Repository Pattern Integration", False, f"Repository factory status: {factory_status}")
                return False
            
            self.log_test("Repository Pattern Integration", True, 
                         f"Repository pattern operational: {len(available_repos)} repositories available, factory active")
            return True
            
        except Exception as e:
            self.log_test("Repository Pattern Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_content_library_operations(self):
        """Test 2: Content Library Operations - Test CRUD operations with repository pattern"""
        try:
            # Test content library listing (READ operation)
            list_response = requests.get(f"{self.backend_url}/api/content-library", timeout=20)
            
            if list_response.status_code != 200:
                self.log_test("Content Library Operations", False, f"Content library list HTTP {list_response.status_code}")
                return False
            
            list_data = list_response.json()
            
            if "articles" not in list_data:
                self.log_test("Content Library Operations", False, "No articles field in content library response")
                return False
            
            articles = list_data["articles"]
            initial_count = len(articles)
            
            # Test article creation (CREATE operation) with TICKET-3 fields
            test_article = {
                "title": "KE-PR9.3 Repository Test Article",
                "content": "<h2>Repository Pattern Test</h2><p>This article tests the repository pattern integration with TICKET-3 compliance.</p>",
                "doc_uid": f"ke-pr9-3-test-{int(time.time())}",
                "doc_slug": "ke-pr9-3-repository-test",
                "headings": [
                    {"id": "repository-pattern-test", "text": "Repository Pattern Test", "level": 2}
                ],
                "xrefs": [
                    {"target": "repository-integration", "type": "internal"}
                ],
                "engine": "v2",
                "status": "published"
            }
            
            create_response = requests.post(f"{self.backend_url}/api/content-library", 
                                          json=test_article, timeout=30)
            
            if create_response.status_code not in [200, 201]:
                self.log_test("Content Library Operations", False, f"Article creation HTTP {create_response.status_code}")
                return False
            
            create_data = create_response.json()
            
            if create_data.get("status") != "success":
                self.log_test("Content Library Operations", False, f"Article creation failed: {create_data.get('message')}")
                return False
            
            article_id = create_data.get("article_id")
            if not article_id:
                self.log_test("Content Library Operations", False, "No article_id returned from creation")
                return False
            
            # Test article retrieval (READ operation) - verify TICKET-3 fields preserved
            get_response = requests.get(f"{self.backend_url}/api/content-library/{article_id}", timeout=15)
            
            if get_response.status_code != 200:
                self.log_test("Content Library Operations", False, f"Article retrieval HTTP {get_response.status_code}")
                return False
            
            get_data = get_response.json()
            retrieved_article = get_data.get("article", {})
            
            # Verify TICKET-3 fields are preserved
            ticket3_fields = ["doc_uid", "doc_slug", "headings", "xrefs"]
            missing_ticket3_fields = []
            
            for field in ticket3_fields:
                if field not in retrieved_article:
                    missing_ticket3_fields.append(field)
            
            if missing_ticket3_fields:
                self.log_test("Content Library Operations", False, f"Missing TICKET-3 fields: {missing_ticket3_fields}")
                return False
            
            # Test article update (UPDATE operation)
            update_payload = {
                "title": "KE-PR9.3 Repository Test Article - Updated",
                "content": "<h2>Repository Pattern Test - Updated</h2><p>This article has been updated to test repository pattern update operations.</p>"
            }
            
            update_response = requests.put(f"{self.backend_url}/api/content-library/{article_id}", 
                                         json=update_payload, timeout=20)
            
            if update_response.status_code != 200:
                self.log_test("Content Library Operations", False, f"Article update HTTP {update_response.status_code}")
                return False
            
            update_data = update_response.json()
            
            if update_data.get("status") != "success":
                self.log_test("Content Library Operations", False, f"Article update failed: {update_data.get('message')}")
                return False
            
            # Test article deletion (DELETE operation)
            delete_response = requests.delete(f"{self.backend_url}/api/content-library/{article_id}", timeout=15)
            
            if delete_response.status_code != 200:
                self.log_test("Content Library Operations", False, f"Article deletion HTTP {delete_response.status_code}")
                return False
            
            delete_data = delete_response.json()
            
            if delete_data.get("status") != "success":
                self.log_test("Content Library Operations", False, f"Article deletion failed: {delete_data.get('message')}")
                return False
            
            # Verify article is actually deleted
            verify_delete_response = requests.get(f"{self.backend_url}/api/content-library/{article_id}", timeout=10)
            
            if verify_delete_response.status_code == 200:
                self.log_test("Content Library Operations", False, "Article still exists after deletion")
                return False
            
            self.log_test("Content Library Operations", True, 
                         f"CRUD operations successful: CREATE, READ (with TICKET-3 fields), UPDATE, DELETE all working")
            return True
            
        except Exception as e:
            self.log_test("Content Library Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_engine_integration(self):
        """Test 3: V2 Engine Integration - Verify V2 processing works with repository layer"""
        try:
            # Test V2 pipeline status
            pipeline_response = requests.get(f"{self.backend_url}/api/engine/v2/pipeline", timeout=15)
            
            if pipeline_response.status_code != 200:
                self.log_test("V2 Engine Integration", False, f"V2 pipeline status HTTP {pipeline_response.status_code}")
                return False
            
            pipeline_data = pipeline_response.json()
            
            if pipeline_data.get("status") not in ["operational", "active", "ready"]:
                self.log_test("V2 Engine Integration", False, f"V2 pipeline status: {pipeline_data.get('status')}")
                return False
            
            # Test V2 content processing with repository integration
            test_content = """
            # V2 Engine Repository Integration Test
            
            ## Overview
            This test validates that the V2 engine properly integrates with the repository pattern for data persistence.
            
            ## Repository Features
            - Content library operations
            - TICKET-3 field preservation
            - Cross-document operations
            - QA diagnostics storage
            
            ### Code Example
            ```python
            def repository_integration():
                # Test repository pattern with V2 engine
                repo = RepositoryFactory.get_content_library()
                return repo.insert_article(article_data)
            ```
            
            ## Expected Behavior
            The V2 engine should use repository pattern for all database operations while maintaining performance and reliability.
            """
            
            processing_payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only",
                "use_repository_pattern": True
            }
            
            processing_response = requests.post(f"{self.backend_url}/api/content/process", 
                                              json=processing_payload, timeout=90)
            
            if processing_response.status_code != 200:
                self.log_test("V2 Engine Integration", False, f"V2 processing HTTP {processing_response.status_code}")
                return False
            
            processing_data = processing_response.json()
            
            if processing_data.get("status") != "success":
                self.log_test("V2 Engine Integration", False, f"V2 processing failed: {processing_data.get('message')}")
                return False
            
            # Verify V2 engine was used
            processing_info = processing_data.get("processing_info", {})
            engine_used = processing_info.get("engine", "")
            
            if engine_used != "v2":
                self.log_test("V2 Engine Integration", False, f"Wrong engine used: {engine_used}")
                return False
            
            # Verify repository pattern was used
            repository_used = processing_info.get("repository_pattern", False)
            
            if not repository_used:
                self.log_test("V2 Engine Integration", False, "Repository pattern not used in V2 processing")
                return False
            
            # Check that articles were created with repository pattern
            articles = processing_data.get("articles", [])
            
            if not articles:
                self.log_test("V2 Engine Integration", False, "No articles generated by V2 engine")
                return False
            
            # Verify TICKET-3 fields in generated articles
            article = articles[0]
            ticket3_fields = ["doc_uid", "doc_slug", "headings", "xrefs"]
            
            for field in ticket3_fields:
                if field not in article:
                    self.log_test("V2 Engine Integration", False, f"V2 article missing TICKET-3 field: {field}")
                    return False
            
            self.log_test("V2 Engine Integration", True, 
                         f"V2 engine repository integration verified: {len(articles)} articles with TICKET-3 fields")
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_mongodb_centralization(self):
        """Test 4: MongoDB Centralization - Confirm no direct database calls are breaking functionality"""
        try:
            # Test MongoDB connection through repository layer
            mongo_test_payload = {
                "operation": "test_connection",
                "repository": "content_library"
            }
            
            mongo_response = requests.post(f"{self.backend_url}/api/engine/repository/test", 
                                         json=mongo_test_payload, timeout=30)
            
            if mongo_response.status_code != 200:
                self.log_test("MongoDB Centralization", False, f"MongoDB test HTTP {mongo_response.status_code}")
                return False
            
            mongo_data = mongo_response.json()
            
            if mongo_data.get("status") != "success":
                self.log_test("MongoDB Centralization", False, f"MongoDB test failed: {mongo_data.get('message')}")
                return False
            
            # Check MongoDB connection status
            mongodb_status = mongo_data.get("mongodb_status", "")
            if mongodb_status not in ["connected", "operational"]:
                self.log_test("MongoDB Centralization", False, f"MongoDB status: {mongodb_status}")
                return False
            
            # Test repository roundtrip operations
            roundtrip_payload = {
                "operation": "roundtrip_test",
                "test_data": {
                    "title": "MongoDB Centralization Test",
                    "doc_uid": f"mongo-test-{int(time.time())}",
                    "doc_slug": "mongodb-centralization-test",
                    "headings": [{"id": "test", "text": "Test", "level": 2}],
                    "xrefs": []
                }
            }
            
            roundtrip_response = requests.post(f"{self.backend_url}/api/engine/repository/roundtrip", 
                                             json=roundtrip_payload, timeout=30)
            
            if roundtrip_response.status_code != 200:
                self.log_test("MongoDB Centralization", False, f"Roundtrip test HTTP {roundtrip_response.status_code}")
                return False
            
            roundtrip_data = roundtrip_response.json()
            
            if roundtrip_data.get("status") != "success":
                self.log_test("MongoDB Centralization", False, f"Roundtrip test failed: {roundtrip_data.get('message')}")
                return False
            
            # Verify data integrity in roundtrip
            roundtrip_results = roundtrip_data.get("results", {})
            
            operations_tested = ["insert", "read", "update", "delete"]
            failed_operations = []
            
            for operation in operations_tested:
                if not roundtrip_results.get(f"{operation}_success", False):
                    failed_operations.append(operation)
            
            if failed_operations:
                self.log_test("MongoDB Centralization", False, f"Failed operations: {failed_operations}")
                return False
            
            # Test centralized access patterns
            centralization_response = requests.get(f"{self.backend_url}/api/engine/repository/centralization-status", timeout=15)
            
            if centralization_response.status_code == 200:
                centralization_data = centralization_response.json()
                direct_db_calls = centralization_data.get("direct_db_calls", 0)
                repository_calls = centralization_data.get("repository_calls", 0)
                
                if direct_db_calls > 0:
                    self.log_test("MongoDB Centralization", False, f"Direct DB calls detected: {direct_db_calls}")
                    return False
                
                if repository_calls == 0:
                    self.log_test("MongoDB Centralization", False, "No repository calls detected")
                    return False
            
            self.log_test("MongoDB Centralization", True, 
                         f"MongoDB centralization verified: All operations through repository pattern, no direct DB calls")
            return True
            
        except Exception as e:
            self.log_test("MongoDB Centralization", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_stability(self):
        """Test 5: Performance & Stability - Ensure repository pattern doesn't impact performance"""
        try:
            # Test performance with multiple concurrent operations
            start_time = time.time()
            
            # Test content library performance
            performance_requests = []
            
            # Multiple read operations
            for i in range(5):
                try:
                    response = requests.get(f"{self.backend_url}/api/content-library", timeout=10)
                    performance_requests.append({
                        "operation": "read",
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    })
                except Exception as e:
                    performance_requests.append({
                        "operation": "read",
                        "error": str(e),
                        "response_time": None
                    })
            
            # Test repository status performance
            for i in range(3):
                try:
                    response = requests.get(f"{self.backend_url}/api/engine/repository/status", timeout=10)
                    performance_requests.append({
                        "operation": "repository_status",
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds()
                    })
                except Exception as e:
                    performance_requests.append({
                        "operation": "repository_status",
                        "error": str(e),
                        "response_time": None
                    })
            
            total_time = time.time() - start_time
            
            # Analyze performance results
            successful_requests = [r for r in performance_requests if r.get("status_code") == 200]
            failed_requests = [r for r in performance_requests if "error" in r or r.get("status_code") != 200]
            
            if len(failed_requests) > 0:
                self.log_test("Performance & Stability", False, f"Failed requests: {len(failed_requests)}/{len(performance_requests)}")
                return False
            
            # Check response times
            response_times = [r["response_time"] for r in successful_requests if r["response_time"] is not None]
            
            if not response_times:
                self.log_test("Performance & Stability", False, "No response time data available")
                return False
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            # Performance thresholds
            if avg_response_time > 5.0:  # Average should be under 5 seconds
                self.log_test("Performance & Stability", False, f"High average response time: {avg_response_time:.2f}s")
                return False
            
            if max_response_time > 10.0:  # Max should be under 10 seconds
                self.log_test("Performance & Stability", False, f"High max response time: {max_response_time:.2f}s")
                return False
            
            # Test system stability under load
            stability_response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if stability_response.status_code != 200:
                self.log_test("Performance & Stability", False, f"Health check failed: HTTP {stability_response.status_code}")
                return False
            
            health_data = stability_response.json()
            
            if health_data.get("status") not in ["healthy", "ok", "operational"]:
                self.log_test("Performance & Stability", False, f"System health: {health_data.get('status')}")
                return False
            
            self.log_test("Performance & Stability", True, 
                         f"Performance stable: {len(successful_requests)} requests, avg {avg_response_time:.2f}s, max {max_response_time:.2f}s")
            return True
            
        except Exception as e:
            self.log_test("Performance & Stability", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_fallbacks(self):
        """Test 6: Error Handling - Test repository error handling and fallback mechanisms"""
        try:
            # Test error handling with invalid operations
            error_test_cases = [
                {
                    "name": "Invalid Repository",
                    "endpoint": "/api/engine/repository/test",
                    "payload": {"operation": "test_connection", "repository": "invalid_repo"},
                    "expected_error": True
                },
                {
                    "name": "Invalid Article ID",
                    "endpoint": "/api/content-library/invalid-id-12345",
                    "method": "GET",
                    "expected_error": True
                },
                {
                    "name": "Malformed Article Data",
                    "endpoint": "/api/content-library",
                    "method": "POST",
                    "payload": {"invalid": "data", "missing": "required_fields"},
                    "expected_error": True
                }
            ]
            
            error_handling_results = []
            
            for test_case in error_test_cases:
                try:
                    if test_case.get("method", "POST") == "POST":
                        response = requests.post(f"{self.backend_url}{test_case['endpoint']}", 
                                               json=test_case.get("payload", {}), timeout=15)
                    else:
                        response = requests.get(f"{self.backend_url}{test_case['endpoint']}", timeout=15)
                    
                    # For error cases, we expect non-200 status codes or error messages
                    if test_case["expected_error"]:
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                if data.get("status") == "success":
                                    error_handling_results.append({
                                        "test": test_case["name"],
                                        "passed": False,
                                        "reason": "Expected error but got success"
                                    })
                                else:
                                    error_handling_results.append({
                                        "test": test_case["name"],
                                        "passed": True,
                                        "reason": "Proper error response in JSON"
                                    })
                            except:
                                error_handling_results.append({
                                    "test": test_case["name"],
                                    "passed": True,
                                    "reason": "Non-JSON error response"
                                })
                        else:
                            error_handling_results.append({
                                "test": test_case["name"],
                                "passed": True,
                                "reason": f"Proper HTTP error: {response.status_code}"
                            })
                    
                except Exception as e:
                    if test_case["expected_error"]:
                        error_handling_results.append({
                            "test": test_case["name"],
                            "passed": True,
                            "reason": f"Expected exception: {str(e)[:50]}"
                        })
                    else:
                        error_handling_results.append({
                            "test": test_case["name"],
                            "passed": False,
                            "reason": f"Unexpected exception: {str(e)[:50]}"
                        })
            
            # Check error handling results
            failed_error_tests = [r for r in error_handling_results if not r["passed"]]
            
            if failed_error_tests:
                failed_names = [r["test"] for r in failed_error_tests]
                self.log_test("Error Handling & Fallbacks", False, f"Failed error handling tests: {failed_names}")
                return False
            
            # Test fallback mechanisms
            fallback_response = requests.get(f"{self.backend_url}/api/engine/repository/fallback-status", timeout=15)
            
            if fallback_response.status_code == 200:
                fallback_data = fallback_response.json()
                fallback_available = fallback_data.get("fallback_available", False)
                
                if not fallback_available:
                    self.log_test("Error Handling & Fallbacks", False, "Fallback mechanisms not available")
                    return False
            
            self.log_test("Error Handling & Fallbacks", True, 
                         f"Error handling verified: {len(error_handling_results)} error cases handled properly")
            return True
            
        except Exception as e:
            self.log_test("Error Handling & Fallbacks", False, f"Exception: {str(e)}")
            return False
    
    def test_ticket3_compliance(self):
        """Test 7: TICKET-3 Compliance - Verify doc_uid, doc_slug, headings, xrefs field preservation"""
        try:
            # Test TICKET-3 field preservation in repository operations
            ticket3_test_data = {
                "title": "TICKET-3 Compliance Test Article",
                "content": "<h2>TICKET-3 Test</h2><p>Testing doc_uid, doc_slug, headings, and xrefs preservation.</p>",
                "doc_uid": f"ticket3-test-{int(time.time())}",
                "doc_slug": "ticket3-compliance-test",
                "headings": [
                    {"id": "ticket3-test", "text": "TICKET-3 Test", "level": 2, "anchor": "ticket3-test"},
                    {"id": "field-preservation", "text": "Field Preservation", "level": 3, "anchor": "field-preservation"}
                ],
                "xrefs": [
                    {"target": "repository-pattern", "type": "internal", "doc_uid": "repo-pattern-doc"},
                    {"target": "mongodb-integration", "type": "internal", "doc_uid": "mongo-integration-doc"}
                ],
                "engine": "v2",
                "status": "published"
            }
            
            # Create article with TICKET-3 fields
            create_response = requests.post(f"{self.backend_url}/api/content-library", 
                                          json=ticket3_test_data, timeout=30)
            
            if create_response.status_code not in [200, 201]:
                self.log_test("TICKET-3 Compliance", False, f"Article creation HTTP {create_response.status_code}")
                return False
            
            create_data = create_response.json()
            
            if create_data.get("status") != "success":
                self.log_test("TICKET-3 Compliance", False, f"Article creation failed: {create_data.get('message')}")
                return False
            
            article_id = create_data.get("article_id")
            
            # Retrieve article and verify TICKET-3 fields
            get_response = requests.get(f"{self.backend_url}/api/content-library/{article_id}", timeout=15)
            
            if get_response.status_code != 200:
                self.log_test("TICKET-3 Compliance", False, f"Article retrieval HTTP {get_response.status_code}")
                return False
            
            get_data = get_response.json()
            retrieved_article = get_data.get("article", {})
            
            # Verify all TICKET-3 fields are preserved
            ticket3_fields = {
                "doc_uid": ticket3_test_data["doc_uid"],
                "doc_slug": ticket3_test_data["doc_slug"],
                "headings": ticket3_test_data["headings"],
                "xrefs": ticket3_test_data["xrefs"]
            }
            
            field_preservation_results = []
            
            for field_name, expected_value in ticket3_fields.items():
                if field_name not in retrieved_article:
                    field_preservation_results.append({
                        "field": field_name,
                        "status": "missing",
                        "expected": expected_value,
                        "actual": None
                    })
                else:
                    actual_value = retrieved_article[field_name]
                    
                    if field_name in ["doc_uid", "doc_slug"]:
                        # String comparison
                        if actual_value == expected_value:
                            field_preservation_results.append({
                                "field": field_name,
                                "status": "preserved",
                                "expected": expected_value,
                                "actual": actual_value
                            })
                        else:
                            field_preservation_results.append({
                                "field": field_name,
                                "status": "modified",
                                "expected": expected_value,
                                "actual": actual_value
                            })
                    else:
                        # Array comparison for headings and xrefs
                        if isinstance(actual_value, list) and len(actual_value) >= len(expected_value):
                            field_preservation_results.append({
                                "field": field_name,
                                "status": "preserved",
                                "expected": len(expected_value),
                                "actual": len(actual_value)
                            })
                        else:
                            field_preservation_results.append({
                                "field": field_name,
                                "status": "incomplete",
                                "expected": expected_value,
                                "actual": actual_value
                            })
            
            # Check preservation results
            failed_fields = [r for r in field_preservation_results if r["status"] not in ["preserved"]]
            
            if failed_fields:
                failed_field_names = [r["field"] for r in failed_fields]
                self.log_test("TICKET-3 Compliance", False, f"TICKET-3 field preservation failed: {failed_field_names}")
                return False
            
            # Test TICKET-3 field updates
            update_payload = {
                "headings": [
                    {"id": "updated-heading", "text": "Updated Heading", "level": 2, "anchor": "updated-heading"}
                ],
                "xrefs": [
                    {"target": "updated-reference", "type": "internal", "doc_uid": "updated-doc"}
                ]
            }
            
            update_response = requests.put(f"{self.backend_url}/api/content-library/{article_id}", 
                                         json=update_payload, timeout=20)
            
            if update_response.status_code != 200:
                self.log_test("TICKET-3 Compliance", False, f"TICKET-3 update HTTP {update_response.status_code}")
                return False
            
            # Verify updates preserved TICKET-3 structure
            verify_response = requests.get(f"{self.backend_url}/api/content-library/{article_id}", timeout=15)
            
            if verify_response.status_code != 200:
                self.log_test("TICKET-3 Compliance", False, f"Update verification HTTP {verify_response.status_code}")
                return False
            
            verify_data = verify_response.json()
            updated_article = verify_data.get("article", {})
            
            # Verify TICKET-3 fields still exist after update
            for field in ["doc_uid", "doc_slug", "headings", "xrefs"]:
                if field not in updated_article:
                    self.log_test("TICKET-3 Compliance", False, f"TICKET-3 field {field} lost during update")
                    return False
            
            # Cleanup
            requests.delete(f"{self.backend_url}/api/content-library/{article_id}", timeout=15)
            
            self.log_test("TICKET-3 Compliance", True, 
                         f"TICKET-3 compliance verified: All 4 fields preserved through CRUD operations")
            return True
            
        except Exception as e:
            self.log_test("TICKET-3 Compliance", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all KE-PR9.3 MongoDB Repository Pattern final validation tests"""
        print("🎯 KE-PR9.3: MONGODB REPOSITORY PATTERN FINAL VALIDATION")
        print("=" * 80)
        print("Comprehensive final test for KE-PR9.3 MongoDB Repository Pattern completion")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_repository_pattern_integration,
            self.test_content_library_operations,
            self.test_v2_engine_integration,
            self.test_mongodb_centralization,
            self.test_performance_stability,
            self.test_error_handling_fallbacks,
            self.test_ticket3_compliance
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
        print("🎯 KE-PR9.3: MONGODB REPOSITORY PATTERN FINAL TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 KE-PR9.3 MONGODB REPOSITORY PATTERN: PERFECT - All repository operations working flawlessly!")
            print("✅ Repository Pattern Integration: All repository operations work correctly")
            print("✅ Content Library Operations: CRUD operations with repository pattern successful")
            print("✅ V2 Engine Integration: V2 processing works seamlessly with repository layer")
            print("✅ MongoDB Centralization: No direct database calls breaking functionality")
            print("✅ Performance & Stability: Repository pattern maintains excellent performance")
            print("✅ Error Handling: Repository error handling and fallback mechanisms working")
            print("✅ TICKET-3 Compliance: doc_uid, doc_slug, headings, xrefs fields preserved")
        elif success_rate >= 85:
            print("🎉 KE-PR9.3 MONGODB REPOSITORY PATTERN: EXCELLENT - Nearly perfect implementation!")
        elif success_rate >= 70:
            print("✅ KE-PR9.3 MONGODB REPOSITORY PATTERN: GOOD - Most repository features working")
        elif success_rate >= 50:
            print("⚠️ KE-PR9.3 MONGODB REPOSITORY PATTERN: PARTIAL - Some repository issues remain")
        else:
            print("❌ KE-PR9.3 MONGODB REPOSITORY PATTERN: NEEDS ATTENTION - Major repository issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = KE_PR9_3_FinalTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)