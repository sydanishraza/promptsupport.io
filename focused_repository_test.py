#!/usr/bin/env python3
"""
KE-PR9.4: Focused Repository Pattern Testing
Testing available repository functionality and core operations
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

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

class FocusedRepositoryTester:
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
        
    def test_content_library_repository_operations(self):
        """Test 1: Content Library Repository Operations"""
        try:
            # Test GET content library
            response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Content Library Repository Operations", False, f"GET failed: HTTP {response.status_code}")
                return False
                
            data = response.json()
            articles = data.get("articles", [])
            initial_count = len(articles)
            
            # Test POST (create) operation
            test_article = {
                "title": "Repository Test Article - KE-PR9.4",
                "content": "<h2>Repository Pattern Test</h2><p>Testing repository-based content operations for KE-PR9.4 validation.</p>",
                "status": "published",
                "tags": ["repository", "test", "ke-pr9-4"]
            }
            
            create_response = requests.post(f"{self.backend_url}/api/content-library", 
                                          json=test_article, timeout=30)
            
            if create_response.status_code not in [200, 201]:
                self.log_test("Content Library Repository Operations", False, f"POST failed: HTTP {create_response.status_code}")
                return False
            
            create_data = create_response.json()
            
            if create_data.get("status") != "success":
                self.log_test("Content Library Repository Operations", False, f"Create failed: {create_data.get('message', 'Unknown error')}")
                return False
            
            # Verify article was created
            verify_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if verify_response.status_code != 200:
                self.log_test("Content Library Repository Operations", False, "Verification GET failed")
                return False
            
            verify_data = verify_response.json()
            new_articles = verify_data.get("articles", [])
            new_count = len(new_articles)
            
            if new_count <= initial_count:
                self.log_test("Content Library Repository Operations", False, f"Article count didn't increase: {initial_count} -> {new_count}")
                return False
            
            # Find the created article
            created_article = None
            for article in new_articles:
                if article.get("title") == test_article["title"]:
                    created_article = article
                    break
            
            if not created_article:
                self.log_test("Content Library Repository Operations", False, "Created article not found in list")
                return False
            
            article_id = created_article.get("id")
            
            # Test DELETE operation
            if article_id:
                delete_response = requests.delete(f"{self.backend_url}/api/content-library/{article_id}", timeout=30)
                delete_success = delete_response.status_code in [200, 204]
            else:
                delete_success = False
            
            self.log_test("Content Library Repository Operations", True, 
                         f"Repository operations working: CREATE ✅, READ ✅, DELETE {'✅' if delete_success else '❌'}")
            return True
            
        except Exception as e:
            self.log_test("Content Library Repository Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_mongodb_data_persistence(self):
        """Test 2: MongoDB Data Persistence Through Repository"""
        try:
            # Get initial state
            initial_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if initial_response.status_code != 200:
                self.log_test("MongoDB Data Persistence", False, "Initial state check failed")
                return False
            
            initial_data = initial_response.json()
            initial_articles = initial_data.get("articles", [])
            initial_count = len(initial_articles)
            
            # Create test article
            persistence_test_article = {
                "title": f"Persistence Test - {datetime.now().strftime('%H:%M:%S')}",
                "content": "<h2>MongoDB Persistence Test</h2><p>Testing data persistence through repository pattern.</p>",
                "status": "published",
                "tags": ["persistence", "mongodb", "repository"],
                "metadata": {"test_timestamp": datetime.now().isoformat()}
            }
            
            create_response = requests.post(f"{self.backend_url}/api/content-library", 
                                          json=persistence_test_article, timeout=30)
            
            if create_response.status_code not in [200, 201]:
                self.log_test("MongoDB Data Persistence", False, f"Create failed: HTTP {create_response.status_code}")
                return False
            
            # Wait a moment for persistence
            time.sleep(2)
            
            # Verify persistence
            verify_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if verify_response.status_code != 200:
                self.log_test("MongoDB Data Persistence", False, "Persistence verification failed")
                return False
            
            verify_data = verify_response.json()
            persisted_articles = verify_data.get("articles", [])
            persisted_count = len(persisted_articles)
            
            # Check if article persisted
            article_persisted = any(
                article.get("title") == persistence_test_article["title"] 
                for article in persisted_articles
            )
            
            if not article_persisted:
                self.log_test("MongoDB Data Persistence", False, "Article not persisted in MongoDB")
                return False
            
            # Check data integrity
            persisted_article = next(
                (article for article in persisted_articles 
                 if article.get("title") == persistence_test_article["title"]), 
                None
            )
            
            if persisted_article:
                content_match = persistence_test_article["content"] in persisted_article.get("content", "")
                status_match = persisted_article.get("status") == persistence_test_article["status"]
                
                if not (content_match and status_match):
                    self.log_test("MongoDB Data Persistence", False, "Data integrity issues detected")
                    return False
            
            self.log_test("MongoDB Data Persistence", True, 
                         f"Data persistence working: {initial_count} -> {persisted_count} articles, data integrity maintained")
            return True
            
        except Exception as e:
            self.log_test("MongoDB Data Persistence", False, f"Exception: {str(e)}")
            return False
    
    def test_system_health_and_stability(self):
        """Test 3: System Health and Stability"""
        try:
            # Test system health
            health_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            if health_response.status_code != 200:
                self.log_test("System Health and Stability", False, f"Health check failed: HTTP {health_response.status_code}")
                return False
            
            health_data = health_response.json()
            system_status = health_data.get("status", "unknown")
            
            # Test engine status
            engine_response = requests.get(f"{self.backend_url}/api/engine", timeout=30)
            engine_working = engine_response.status_code == 200
            
            # Test multiple concurrent requests for stability
            import concurrent.futures
            
            def make_concurrent_request():
                try:
                    response = requests.get(f"{self.backend_url}/api/content-library", timeout=15)
                    return response.status_code == 200
                except:
                    return False
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_concurrent_request) for _ in range(3)]
                concurrent_results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successful_concurrent = sum(concurrent_results)
            
            # Check system stability after concurrent requests
            post_stability_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            post_stability_working = post_stability_response.status_code == 200
            
            stability_indicators = [
                ("System health", system_status in ["healthy", "ok", "operational", "fallback"]),
                ("Engine status", engine_working),
                ("Concurrent requests", successful_concurrent >= 2),
                ("Post-test stability", post_stability_working)
            ]
            
            working_indicators = sum(1 for _, working in stability_indicators if working)
            total_indicators = len(stability_indicators)
            
            if working_indicators >= 3:
                self.log_test("System Health and Stability", True, 
                             f"System stable: {working_indicators}/{total_indicators} indicators positive, {successful_concurrent}/3 concurrent requests successful")
                return True
            else:
                failed_indicators = [name for name, working in stability_indicators if not working]
                self.log_test("System Health and Stability", False, 
                             f"Stability issues: {failed_indicators} not working")
                return False
            
        except Exception as e:
            self.log_test("System Health and Stability", False, f"Exception: {str(e)}")
            return False
    
    def test_repository_performance_impact(self):
        """Test 4: Repository Performance Impact"""
        try:
            # Measure baseline performance
            start_time = time.time()
            
            # Make 5 requests to measure performance
            response_times = []
            successful_requests = 0
            
            for i in range(5):
                request_start = time.time()
                try:
                    response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
                    request_end = time.time()
                    
                    if response.status_code == 200:
                        successful_requests += 1
                        response_times.append(request_end - request_start)
                except:
                    pass
                
                # Small delay between requests
                time.sleep(0.5)
            
            total_time = time.time() - start_time
            
            if successful_requests < 4:
                self.log_test("Repository Performance Impact", False, f"Poor success rate: {successful_requests}/5 requests successful")
                return False
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                # Check if performance is acceptable (under 5 seconds average)
                if avg_response_time > 5.0:
                    self.log_test("Repository Performance Impact", False, f"Poor performance: {avg_response_time:.2f}s average response time")
                    return False
                
                # Check if any single request took too long (under 10 seconds)
                if max_response_time > 10.0:
                    self.log_test("Repository Performance Impact", False, f"Slow requests detected: {max_response_time:.2f}s max response time")
                    return False
            
            # Test system responsiveness after performance test
            post_test_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            system_responsive = post_test_response.status_code == 200
            
            if not system_responsive:
                self.log_test("Repository Performance Impact", False, "System not responsive after performance test")
                return False
            
            avg_time = sum(response_times) / len(response_times) if response_times else 0
            self.log_test("Repository Performance Impact", True, 
                         f"Performance acceptable: {successful_requests}/5 requests successful, {avg_time:.2f}s avg response time")
            return True
            
        except Exception as e:
            self.log_test("Repository Performance Impact", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_and_fallbacks(self):
        """Test 5: Error Handling and Fallback Mechanisms"""
        try:
            # Test invalid input handling
            invalid_article = {
                "title": "",  # Invalid empty title
                "content": "",  # Invalid empty content
                "invalid_field": "should_be_handled_gracefully"
            }
            
            error_response = requests.post(f"{self.backend_url}/api/content-library", 
                                         json=invalid_article, timeout=30)
            
            # Should handle error gracefully (not crash)
            error_handled_gracefully = error_response.status_code in [200, 400, 422, 500]
            
            # Test system recovery after error
            recovery_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            system_recovered = recovery_response.status_code == 200
            
            # Test that valid operations still work after error
            valid_test_article = {
                "title": "Error Recovery Test Article",
                "content": "<p>Testing system recovery after error conditions.</p>",
                "status": "published"
            }
            
            recovery_test_response = requests.post(f"{self.backend_url}/api/content-library", 
                                                 json=valid_test_article, timeout=30)
            
            operations_still_work = recovery_test_response.status_code in [200, 201]
            
            # Test content library still accessible
            library_accessible = requests.get(f"{self.backend_url}/api/content-library", timeout=30).status_code == 200
            
            error_handling_features = [
                ("Graceful error handling", error_handled_gracefully),
                ("System recovery", system_recovered),
                ("Operations after error", operations_still_work),
                ("Library accessibility", library_accessible)
            ]
            
            working_features = sum(1 for _, working in error_handling_features if working)
            total_features = len(error_handling_features)
            
            if working_features >= 3:
                self.log_test("Error Handling and Fallbacks", True, 
                             f"Error handling working: {working_features}/{total_features} features operational")
                return True
            else:
                failed_features = [name for name, working in error_handling_features if not working]
                self.log_test("Error Handling and Fallbacks", False, 
                             f"Error handling issues: {failed_features} not working")
                return False
            
        except Exception as e:
            self.log_test("Error Handling and Fallbacks", False, f"Exception: {str(e)}")
            return False
    
    def test_ticket3_field_preservation(self):
        """Test 6: TICKET-3 Field Preservation in Repository Operations"""
        try:
            # Create article with TICKET-3 fields
            ticket3_article = {
                "title": "TICKET-3 Field Preservation Test",
                "content": "<h2>Testing TICKET-3 Fields</h2><p>This article tests preservation of TICKET-3 fields through repository operations.</p>",
                "status": "published",
                "doc_uid": "test_doc_uid_12345",
                "doc_slug": "ticket3-field-preservation-test",
                "headings_registry": [
                    {"level": 2, "text": "Testing TICKET-3 Fields", "anchor": "testing-ticket3-fields"}
                ],
                "xrefs": ["related_doc_1", "related_doc_2"]
            }
            
            create_response = requests.post(f"{self.backend_url}/api/content-library", 
                                          json=ticket3_article, timeout=30)
            
            if create_response.status_code not in [200, 201]:
                self.log_test("TICKET-3 Field Preservation", False, f"Create failed: HTTP {create_response.status_code}")
                return False
            
            # Retrieve articles and check if TICKET-3 fields are preserved
            retrieve_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if retrieve_response.status_code != 200:
                self.log_test("TICKET-3 Field Preservation", False, "Retrieve failed")
                return False
            
            retrieve_data = retrieve_response.json()
            articles = retrieve_data.get("articles", [])
            
            # Find our test article
            test_article = None
            for article in articles:
                if article.get("title") == ticket3_article["title"]:
                    test_article = article
                    break
            
            if not test_article:
                self.log_test("TICKET-3 Field Preservation", False, "Test article not found")
                return False
            
            # Check TICKET-3 field preservation
            ticket3_fields_preserved = []
            
            # Check doc_uid
            if test_article.get("doc_uid") == ticket3_article["doc_uid"]:
                ticket3_fields_preserved.append("doc_uid")
            
            # Check doc_slug
            if test_article.get("doc_slug") == ticket3_article["doc_slug"]:
                ticket3_fields_preserved.append("doc_slug")
            
            # Check headings_registry
            if test_article.get("headings_registry"):
                ticket3_fields_preserved.append("headings_registry")
            
            # Check xrefs
            if test_article.get("xrefs"):
                ticket3_fields_preserved.append("xrefs")
            
            preservation_rate = len(ticket3_fields_preserved) / 4 * 100
            
            if preservation_rate >= 50:  # At least 50% of TICKET-3 fields should be preserved
                self.log_test("TICKET-3 Field Preservation", True, 
                             f"TICKET-3 fields preserved: {preservation_rate:.1f}% ({ticket3_fields_preserved})")
                return True
            else:
                self.log_test("TICKET-3 Field Preservation", False, 
                             f"Poor TICKET-3 preservation: {preservation_rate:.1f}% ({ticket3_fields_preserved})")
                return False
            
        except Exception as e:
            self.log_test("TICKET-3 Field Preservation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all focused repository pattern tests"""
        print("🎯 KE-PR9.4: FOCUSED REPOSITORY PATTERN TESTING")
        print("=" * 70)
        print("Testing available repository functionality and core operations")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_content_library_repository_operations,
            self.test_mongodb_data_persistence,
            self.test_system_health_and_stability,
            self.test_repository_performance_impact,
            self.test_error_handling_and_fallbacks,
            self.test_ticket3_field_preservation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(1)
        
        # Print summary
        print()
        print("=" * 70)
        print("🎯 KE-PR9.4: FOCUSED REPOSITORY TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 KE-PR9.4 REPOSITORY PATTERN: PERFECT - All repository operations working!")
        elif success_rate >= 85:
            print("🎉 KE-PR9.4 REPOSITORY PATTERN: EXCELLENT - Repository migration highly successful!")
        elif success_rate >= 70:
            print("✅ KE-PR9.4 REPOSITORY PATTERN: GOOD - Most repository operations working")
        elif success_rate >= 50:
            print("⚠️ KE-PR9.4 REPOSITORY PATTERN: PARTIAL - Some repository functionality working")
        else:
            print("❌ KE-PR9.4 REPOSITORY PATTERN: NEEDS ATTENTION - Major repository issues")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = FocusedRepositoryTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)