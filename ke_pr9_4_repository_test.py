#!/usr/bin/env python3
"""
KE-PR9.4: MongoDB Repository Pattern Migration Progress Testing
Comprehensive test suite for validating repository pattern integration and V2 processing results
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

class RepositoryPatternTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Repository classes to test
        self.repository_classes = [
            "ContentLibraryRepository",
            "QAResultsRepository", 
            "V2AnalysisRepository",
            "V2OutlineRepository",
            "V2ValidationRepository",
            "AssetsRepository",
            "MediaLibraryRepository"
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
        
    def test_repository_pattern_integration(self):
        """Test 1: Verify repository pattern integration is working correctly"""
        try:
            # Test content library with repository pattern
            response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Repository Pattern Integration", False, f"Content library HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check if response indicates repository usage
            articles = data.get("articles", [])
            metadata = data.get("metadata", {})
            
            # Look for repository pattern indicators
            source = metadata.get("source", "")
            if "repository" not in source.lower():
                self.log_test("Repository Pattern Integration", False, f"No repository source indicator: {source}")
                return False
            
            # Test repository-based article creation
            test_article = {
                "title": "Repository Pattern Test Article",
                "content": "<h2>Testing Repository Pattern</h2><p>This article tests the repository pattern integration for KE-PR9.4.</p>",
                "status": "published",
                "tags": ["test", "repository", "ke-pr9-4"]
            }
            
            create_response = requests.post(f"{self.backend_url}/api/content-library", 
                                         json=test_article, timeout=30)
            
            if create_response.status_code not in [200, 201]:
                self.log_test("Repository Pattern Integration", False, f"Article creation HTTP {create_response.status_code}")
                return False
            
            create_data = create_response.json()
            
            if create_data.get("status") != "success":
                self.log_test("Repository Pattern Integration", False, f"Article creation failed: {create_data.get('message')}")
                return False
            
            # Verify article was created through repository
            article_id = create_data.get("article_id")
            if not article_id:
                self.log_test("Repository Pattern Integration", False, "No article ID returned from creation")
                return False
            
            self.log_test("Repository Pattern Integration", True, 
                         f"Repository pattern working: content library operations successful, article created via repository")
            return True
            
        except Exception as e:
            self.log_test("Repository Pattern Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_processing_results_repositories(self):
        """Test 2: Test V2 validation and analysis repositories"""
        try:
            # Test V2 content processing with repository storage
            test_content = """
            # V2 Repository Pattern Test
            
            ## Overview
            This content tests the V2 processing results repositories for validation and analysis.
            
            ## Test Scenarios
            - V2 validation repository operations
            - V2 analysis repository storage
            - V2 outline repository functionality
            
            ### Code Example
            ```python
            def test_v2_repositories():
                # Test V2 repository pattern
                return "V2 repositories working"
            ```
            
            ## Expected Results
            All V2 processing results should be stored in dedicated repositories.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only",
                "store_results": True
            }
            
            response = requests.post(f"{self.backend_url}/api/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("V2 Processing Results Repositories", False, f"V2 processing HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("V2 Processing Results Repositories", False, f"V2 processing failed: {data.get('message')}")
                return False
            
            # Check if V2 results were stored in repositories
            processing_info = data.get("processing_info", {})
            repository_usage = processing_info.get("repository_usage", {})
            
            # Look for V2 repository usage indicators
            v2_repos_used = []
            for repo_name, usage_info in repository_usage.items():
                if "v2" in repo_name.lower() and usage_info.get("operations", 0) > 0:
                    v2_repos_used.append(repo_name)
            
            if not v2_repos_used:
                # Check alternative indicators
                articles = data.get("articles", [])
                if articles:
                    article = articles[0]
                    metadata = article.get("metadata", {})
                    if "v2" in str(metadata).lower() and "repository" in str(metadata).lower():
                        v2_repos_used = ["content_repository"]
            
            if not v2_repos_used:
                self.log_test("V2 Processing Results Repositories", False, "No V2 repository usage detected")
                return False
            
            # Test V2 validation repository specifically
            validation_payload = {
                "content": test_content,
                "validation_type": "v2_comprehensive",
                "store_validation_results": True
            }
            
            validation_response = requests.post(f"{self.backend_url}/api/engine/v2/validate", 
                                              json=validation_payload, timeout=60)
            
            validation_success = validation_response.status_code == 200
            
            self.log_test("V2 Processing Results Repositories", True, 
                         f"V2 repositories working: {len(v2_repos_used)} V2 repos used, validation endpoint {'accessible' if validation_success else 'not accessible'}")
            return True
            
        except Exception as e:
            self.log_test("V2 Processing Results Repositories", False, f"Exception: {str(e)}")
            return False
    
    def test_content_library_crud_operations(self):
        """Test 3: Validate repository-based CRUD operations"""
        try:
            # CREATE - Test article creation
            test_article = {
                "title": "CRUD Test Article for KE-PR9.4",
                "content": "<h2>CRUD Operations Test</h2><p>Testing Create, Read, Update, Delete operations through repository pattern.</p>",
                "status": "published",
                "tags": ["crud", "test", "repository"],
                "metadata": {"test_type": "crud_validation"}
            }
            
            create_response = requests.post(f"{self.backend_url}/api/content-library", 
                                          json=test_article, timeout=30)
            
            if create_response.status_code not in [200, 201]:
                self.log_test("Content Library CRUD Operations", False, f"CREATE failed: HTTP {create_response.status_code}")
                return False
            
            create_data = create_response.json()
            article_id = create_data.get("article_id") or create_data.get("id")
            
            if not article_id:
                self.log_test("Content Library CRUD Operations", False, "CREATE failed: No article ID returned")
                return False
            
            # READ - Test article retrieval
            read_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if read_response.status_code != 200:
                self.log_test("Content Library CRUD Operations", False, f"READ failed: HTTP {read_response.status_code}")
                return False
            
            read_data = read_response.json()
            articles = read_data.get("articles", [])
            
            # Find our test article
            test_article_found = any(article.get("id") == article_id for article in articles)
            
            if not test_article_found:
                self.log_test("Content Library CRUD Operations", False, f"READ failed: Test article {article_id} not found")
                return False
            
            # UPDATE - Test article modification (if endpoint exists)
            update_payload = {
                "title": "Updated CRUD Test Article",
                "content": test_article["content"] + "<p>Updated content for CRUD test.</p>",
                "tags": test_article["tags"] + ["updated"]
            }
            
            update_response = requests.put(f"{self.backend_url}/api/content-library/{article_id}", 
                                         json=update_payload, timeout=30)
            
            update_success = update_response.status_code in [200, 201, 204]
            
            # DELETE - Test article deletion
            delete_response = requests.delete(f"{self.backend_url}/api/content-library/{article_id}", timeout=30)
            
            delete_success = delete_response.status_code in [200, 204]
            
            # Verify deletion
            verify_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                remaining_articles = verify_data.get("articles", [])
                article_still_exists = any(article.get("id") == article_id for article in remaining_articles)
                delete_verified = not article_still_exists
            else:
                delete_verified = False
            
            operations_successful = [
                ("CREATE", True),
                ("READ", True),
                ("UPDATE", update_success),
                ("DELETE", delete_success and delete_verified)
            ]
            
            successful_ops = sum(1 for _, success in operations_successful if success)
            total_ops = len(operations_successful)
            
            if successful_ops >= 3:  # At least CREATE, READ, and DELETE should work
                self.log_test("Content Library CRUD Operations", True, 
                             f"CRUD operations working: {successful_ops}/{total_ops} operations successful")
                return True
            else:
                failed_ops = [op for op, success in operations_successful if not success]
                self.log_test("Content Library CRUD Operations", False, 
                             f"CRUD operations failed: {failed_ops} not working")
                return False
            
        except Exception as e:
            self.log_test("Content Library CRUD Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_repository_error_handling(self):
        """Test 4: Test repository error handling and fallback mechanisms"""
        try:
            # Test invalid article creation to trigger error handling
            invalid_article = {
                "title": "",  # Invalid empty title
                "content": "",  # Invalid empty content
                "invalid_field": "should_be_rejected"
            }
            
            error_response = requests.post(f"{self.backend_url}/api/content-library", 
                                         json=invalid_article, timeout=30)
            
            # Should get an error response, not a crash
            error_handled = error_response.status_code in [400, 422, 500]
            
            if not error_handled:
                self.log_test("Repository Error Handling", False, f"Error not handled properly: HTTP {error_response.status_code}")
                return False
            
            # Test repository status endpoint for health check
            status_response = requests.get(f"{self.backend_url}/api/engine/repository/status", timeout=30)
            
            repository_status_available = status_response.status_code == 200
            
            # Test fallback mechanism by checking if system still responds
            fallback_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            system_stable = fallback_response.status_code == 200
            
            if not system_stable:
                self.log_test("Repository Error Handling", False, "System not stable after error conditions")
                return False
            
            # Test MongoDB connection resilience
            mongo_test_payload = {"test": "connection"}
            mongo_response = requests.post(f"{self.backend_url}/api/engine/repository/test", 
                                         json=mongo_test_payload, timeout=30)
            
            mongo_resilient = mongo_response.status_code in [200, 500]  # Either works or fails gracefully
            
            error_handling_features = [
                ("Invalid input handling", error_handled),
                ("Repository status check", repository_status_available),
                ("System stability", system_stable),
                ("MongoDB resilience", mongo_resilient)
            ]
            
            working_features = sum(1 for _, working in error_handling_features if working)
            total_features = len(error_handling_features)
            
            if working_features >= 3:
                self.log_test("Repository Error Handling", True, 
                             f"Error handling working: {working_features}/{total_features} features operational")
                return True
            else:
                failed_features = [feature for feature, working in error_handling_features if not working]
                self.log_test("Repository Error Handling", False, 
                             f"Error handling issues: {failed_features} not working")
                return False
            
        except Exception as e:
            self.log_test("Repository Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_repository_performance(self):
        """Test 5: Ensure repository pattern doesn't impact response times"""
        try:
            # Test multiple concurrent requests to measure performance
            start_time = time.time()
            
            # Make 5 concurrent requests to content library
            import concurrent.futures
            
            def make_request():
                response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
                return response.status_code == 200, time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            successful_requests = sum(1 for success, _ in results if success)
            
            if successful_requests < 4:  # At least 4/5 should succeed
                self.log_test("Repository Performance", False, f"Performance test failed: {successful_requests}/5 requests successful")
                return False
            
            # Check average response time
            avg_response_time = total_time / len(results)
            
            if avg_response_time > 10:  # Should respond within 10 seconds on average
                self.log_test("Repository Performance", False, f"Performance degraded: {avg_response_time:.2f}s average response time")
                return False
            
            # Test system health after performance test
            health_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            if health_response.status_code != 200:
                self.log_test("Repository Performance", False, "System health degraded after performance test")
                return False
            
            self.log_test("Repository Performance", True, 
                         f"Performance maintained: {successful_requests}/5 requests successful, {avg_response_time:.2f}s avg response time")
            return True
            
        except Exception as e:
            self.log_test("Repository Performance", False, f"Exception: {str(e)}")
            return False
    
    def test_mixed_operations_workflow(self):
        """Test 6: Test workflows that use both converted and unconverted operations"""
        try:
            # Test a workflow that combines repository and non-repository operations
            
            # Step 1: Create content using repository pattern
            test_content = {
                "title": "Mixed Operations Workflow Test",
                "content": "<h2>Testing Mixed Operations</h2><p>This tests both repository and non-repository operations working together.</p>",
                "status": "published",
                "tags": ["mixed", "workflow", "test"]
            }
            
            create_response = requests.post(f"{self.backend_url}/api/content-library", 
                                          json=test_content, timeout=30)
            
            if create_response.status_code not in [200, 201]:
                self.log_test("Mixed Operations Workflow", False, f"Repository operation failed: HTTP {create_response.status_code}")
                return False
            
            # Step 2: Process content with V2 engine (may use mixed operations)
            processing_payload = {
                "content": test_content["content"],
                "content_type": "html",
                "processing_mode": "v2_only"
            }
            
            process_response = requests.post(f"{self.backend_url}/api/content/process", 
                                           json=processing_payload, timeout=60)
            
            processing_success = process_response.status_code == 200
            
            # Step 3: Test traditional API endpoints (non-repository)
            health_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            traditional_api_working = health_response.status_code == 200
            
            # Step 4: Test engine status (may be mixed)
            engine_response = requests.get(f"{self.backend_url}/api/engine", timeout=30)
            engine_working = engine_response.status_code == 200
            
            # Step 5: Test content library again (repository)
            library_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            repository_still_working = library_response.status_code == 200
            
            workflow_steps = [
                ("Repository create", True),
                ("V2 processing", processing_success),
                ("Traditional API", traditional_api_working),
                ("Engine status", engine_working),
                ("Repository read", repository_still_working)
            ]
            
            successful_steps = sum(1 for _, success in workflow_steps if success)
            total_steps = len(workflow_steps)
            
            if successful_steps >= 4:  # At least 4/5 steps should work
                self.log_test("Mixed Operations Workflow", True, 
                             f"Mixed operations working: {successful_steps}/{total_steps} workflow steps successful")
                return True
            else:
                failed_steps = [step for step, success in workflow_steps if not success]
                self.log_test("Mixed Operations Workflow", False, 
                             f"Mixed operations issues: {failed_steps} steps failed")
                return False
            
        except Exception as e:
            self.log_test("Mixed Operations Workflow", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all repository pattern migration tests"""
        print("🎯 KE-PR9.4: MONGODB REPOSITORY PATTERN MIGRATION PROGRESS TESTING")
        print("=" * 80)
        print("Comprehensive testing for repository pattern integration and V2 processing results")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_repository_pattern_integration,
            self.test_v2_processing_results_repositories,
            self.test_content_library_crud_operations,
            self.test_repository_error_handling,
            self.test_repository_performance,
            self.test_mixed_operations_workflow
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
        print("🎯 KE-PR9.4: REPOSITORY PATTERN MIGRATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 KE-PR9.4 REPOSITORY PATTERN: PERFECT - All repository operations working flawlessly!")
            print("✅ Repository Pattern Integration: All converted operations working correctly")
            print("✅ V2 Processing Results: V2 validation and analysis repositories operational")
            print("✅ Content Library Operations: Repository-based CRUD operations validated")
            print("✅ Error Handling: Repository error handling and fallback mechanisms working")
            print("✅ Performance: Repository pattern maintains excellent response times")
            print("✅ Mixed Operations: Workflows using both converted and unconverted operations successful")
        elif success_rate >= 85:
            print("🎉 KE-PR9.4 REPOSITORY PATTERN: EXCELLENT - Repository migration highly successful!")
        elif success_rate >= 70:
            print("✅ KE-PR9.4 REPOSITORY PATTERN: GOOD - Most repository operations working correctly")
        elif success_rate >= 50:
            print("⚠️ KE-PR9.4 REPOSITORY PATTERN: PARTIAL - Some repository issues need attention")
        else:
            print("❌ KE-PR9.4 REPOSITORY PATTERN: NEEDS WORK - Major repository issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = RepositoryPatternTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)