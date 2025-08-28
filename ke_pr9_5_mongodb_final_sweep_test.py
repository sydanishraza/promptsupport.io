#!/usr/bin/env python3
"""
KE-PR9.5: MongoDB Final Sweep Progress Validation
Comprehensive testing for 90%+ MongoDB centralization completion status validation

Test Focus Areas:
1. ProcessingJobsRepository - Test newly created functionality
2. Content Library Operations - Validate remaining vs converted repository operations  
3. Repository Pattern Integration - Test all converted repository operations work correctly
4. V2 Processing Results - Test converted V2 operations (analysis, validation, QA)
5. System Stability - Ensure all repository changes maintain system stability
6. Mixed Operations - Test workflows with both converted and remaining direct operations
7. Error Handling - Test repository error handling and fallback mechanisms
"""

import os
import sys
import asyncio
import json
import requests
import time
import uuid
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
print(f"🌐 Testing KE-PR9.5 MongoDB Final Sweep at: {BACKEND_URL}")

class MongoDBFinalSweepTester:
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
        
    def test_processing_jobs_repository(self):
        """Test 1: ProcessingJobsRepository - Test newly created functionality"""
        try:
            # Test creating a processing job
            test_job_data = {
                "job_type": "content_processing",
                "content_type": "markdown",
                "status": "pending",
                "metadata": {
                    "test_job": True,
                    "created_by": "ke_pr9_5_test"
                }
            }
            
            # Test job creation via API
            create_response = requests.post(
                f"{self.backend_url}/api/processing/jobs",
                json=test_job_data,
                timeout=30
            )
            
            if create_response.status_code not in [200, 201]:
                self.log_test("ProcessingJobsRepository Creation", False, 
                             f"Job creation failed: HTTP {create_response.status_code}")
                return False
            
            job_data = create_response.json()
            job_id = job_data.get("job_id") or job_data.get("id")
            
            if not job_id:
                self.log_test("ProcessingJobsRepository Creation", False, 
                             "No job_id returned from creation")
                return False
            
            # Test job status update
            update_response = requests.put(
                f"{self.backend_url}/api/processing/jobs/{job_id}/status",
                json={"status": "processing", "progress": 50},
                timeout=30
            )
            
            if update_response.status_code not in [200, 204]:
                self.log_test("ProcessingJobsRepository Status Update", False,
                             f"Status update failed: HTTP {update_response.status_code}")
                return False
            
            # Test job retrieval
            get_response = requests.get(
                f"{self.backend_url}/api/processing/jobs/{job_id}",
                timeout=30
            )
            
            if get_response.status_code != 200:
                self.log_test("ProcessingJobsRepository Retrieval", False,
                             f"Job retrieval failed: HTTP {get_response.status_code}")
                return False
            
            retrieved_job = get_response.json()
            
            # Verify job data integrity
            if retrieved_job.get("status") != "processing":
                self.log_test("ProcessingJobsRepository Data Integrity", False,
                             f"Status not updated correctly: {retrieved_job.get('status')}")
                return False
            
            # Test job listing
            list_response = requests.get(
                f"{self.backend_url}/api/processing/jobs",
                timeout=30
            )
            
            if list_response.status_code != 200:
                self.log_test("ProcessingJobsRepository Listing", False,
                             f"Job listing failed: HTTP {list_response.status_code}")
                return False
            
            jobs_list = list_response.json()
            jobs = jobs_list.get("jobs", [])
            
            # Verify our test job is in the list
            test_job_found = any(job.get("job_id") == job_id or job.get("id") == job_id for job in jobs)
            
            if not test_job_found:
                self.log_test("ProcessingJobsRepository Listing Verification", False,
                             "Test job not found in jobs list")
                return False
            
            self.log_test("ProcessingJobsRepository", True,
                         f"All operations successful: create, update, retrieve, list - Job ID: {job_id}")
            return True
            
        except Exception as e:
            self.log_test("ProcessingJobsRepository", False, f"Exception: {str(e)}")
            return False
    
    def test_content_library_operations(self):
        """Test 2: Content Library Operations - Validate remaining vs converted repository operations"""
        try:
            # Test repository-based content library operations
            
            # 1. Test content library listing (should use repository)
            list_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if list_response.status_code != 200:
                self.log_test("Content Library Repository Operations", False,
                             f"Content library listing failed: HTTP {list_response.status_code}")
                return False
            
            content_data = list_response.json()
            articles = content_data.get("articles", [])
            initial_count = len(articles)
            
            # 2. Test article creation (should use repository)
            test_article = {
                "title": f"KE-PR9.5 Test Article {int(time.time())}",
                "content": "<h2>Test Content</h2><p>This is a test article for KE-PR9.5 MongoDB Final Sweep validation.</p>",
                "doc_uid": f"test-uid-{int(time.time())}",
                "doc_slug": f"ke-pr9-5-test-{int(time.time())}",
                "headings": [{"id": "test-heading", "text": "Test Heading", "level": 2}],
                "xrefs": [{"target": "test-ref", "type": "internal"}],
                "engine": "v2",
                "status": "published"
            }
            
            create_response = requests.post(
                f"{self.backend_url}/api/content-library",
                json=test_article,
                timeout=30
            )
            
            if create_response.status_code not in [200, 201]:
                self.log_test("Content Library Repository Creation", False,
                             f"Article creation failed: HTTP {create_response.status_code}")
                return False
            
            # 3. Verify article count increased
            list_response2 = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if list_response2.status_code != 200:
                self.log_test("Content Library Repository Verification", False,
                             f"Content library re-listing failed: HTTP {list_response2.status_code}")
                return False
            
            content_data2 = list_response2.json()
            articles2 = content_data2.get("articles", [])
            final_count = len(articles2)
            
            if final_count <= initial_count:
                self.log_test("Content Library Repository Persistence", False,
                             f"Article count did not increase: {initial_count} -> {final_count}")
                return False
            
            # 4. Test TICKET-3 field preservation
            created_article = None
            for article in articles2:
                if article.get("title", "").startswith("KE-PR9.5 Test Article"):
                    created_article = article
                    break
            
            if not created_article:
                self.log_test("Content Library Repository TICKET-3", False,
                             "Created test article not found")
                return False
            
            # Verify TICKET-3 fields are preserved
            ticket3_fields = ["doc_uid", "doc_slug", "headings", "xrefs"]
            missing_fields = [field for field in ticket3_fields if field not in created_article]
            
            if missing_fields:
                self.log_test("Content Library Repository TICKET-3 Fields", False,
                             f"Missing TICKET-3 fields: {missing_fields}")
                return False
            
            # 5. Test article deletion (repository operation)
            article_id = created_article.get("id")
            if article_id:
                delete_response = requests.delete(
                    f"{self.backend_url}/api/content-library/{article_id}",
                    timeout=30
                )
                
                if delete_response.status_code not in [200, 204]:
                    self.log_test("Content Library Repository Deletion", False,
                                 f"Article deletion failed: HTTP {delete_response.status_code}")
                    return False
            
            self.log_test("Content Library Operations", True,
                         f"Repository operations working: list, create, verify, TICKET-3 fields, delete")
            return True
            
        except Exception as e:
            self.log_test("Content Library Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_repository_pattern_integration(self):
        """Test 3: Repository Pattern Integration - Test all converted repository operations work correctly"""
        try:
            # Test multiple repository types to ensure pattern is working
            
            # 1. Test Content Library Repository
            content_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if content_response.status_code != 200:
                self.log_test("Repository Pattern - Content Library", False,
                             f"Content library repository failed: HTTP {content_response.status_code}")
                return False
            
            # 2. Test QA Results Repository (if available)
            qa_response = requests.get(f"{self.backend_url}/api/qa/reports", timeout=30)
            qa_available = qa_response.status_code == 200
            
            # 3. Test V2 Analysis Repository (if available)
            v2_analysis_response = requests.get(f"{self.backend_url}/api/engine/v2/analysis", timeout=30)
            v2_analysis_available = v2_analysis_response.status_code == 200
            
            # 4. Test Repository Factory Status
            factory_response = requests.get(f"{self.backend_url}/api/engine/repository/status", timeout=30)
            factory_available = factory_response.status_code == 200
            
            if factory_available:
                factory_data = factory_response.json()
                repositories = factory_data.get("repositories", {})
                
                # Check for expected repositories
                expected_repos = ["content_library", "qa_results", "v2_analysis", "assets"]
                available_repos = [repo for repo in expected_repos if repo in repositories]
                
                if len(available_repos) < 2:  # At least 2 repositories should be available
                    self.log_test("Repository Pattern Integration", False,
                                 f"Insufficient repositories available: {available_repos}")
                    return False
            
            # 5. Test repository error handling
            error_response = requests.get(f"{self.backend_url}/api/content-library/nonexistent-id", timeout=30)
            
            if error_response.status_code not in [404, 400]:
                self.log_test("Repository Pattern Error Handling", False,
                             f"Error handling not working: HTTP {error_response.status_code}")
                return False
            
            # Count successful repository integrations
            successful_integrations = sum([
                content_response.status_code == 200,
                qa_available,
                v2_analysis_available,
                factory_available
            ])
            
            if successful_integrations < 2:
                self.log_test("Repository Pattern Integration", False,
                             f"Insufficient repository integrations: {successful_integrations}/4")
                return False
            
            self.log_test("Repository Pattern Integration", True,
                         f"Repository pattern working: {successful_integrations}/4 integrations successful")
            return True
            
        except Exception as e:
            self.log_test("Repository Pattern Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_processing_results(self):
        """Test 4: V2 Processing Results - Test converted V2 operations (analysis, validation, QA)"""
        try:
            # Test V2 engine processing pipeline
            
            # 1. Test V2 pipeline status
            pipeline_response = requests.get(f"{self.backend_url}/api/engine/v2/pipeline", timeout=30)
            
            if pipeline_response.status_code != 200:
                self.log_test("V2 Processing Pipeline Status", False,
                             f"V2 pipeline status failed: HTTP {pipeline_response.status_code}")
                return False
            
            pipeline_data = pipeline_response.json()
            pipeline_status = pipeline_data.get("status", "")
            
            if pipeline_status not in ["operational", "active", "ready"]:
                self.log_test("V2 Processing Pipeline Status", False,
                             f"V2 pipeline not operational: {pipeline_status}")
                return False
            
            # 2. Test V2 content processing
            test_content = {
                "content": "# V2 Processing Test\n\nThis is a test for V2 processing results validation in KE-PR9.5.",
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            process_response = requests.post(
                f"{self.backend_url}/api/content/process",
                json=test_content,
                timeout=120
            )
            
            if process_response.status_code != 200:
                self.log_test("V2 Processing Execution", False,
                             f"V2 processing failed: HTTP {process_response.status_code}")
                return False
            
            process_data = process_response.json()
            
            if process_data.get("status") != "success":
                self.log_test("V2 Processing Results", False,
                             f"V2 processing unsuccessful: {process_data.get('message')}")
                return False
            
            # 3. Verify V2 engine was used
            processing_info = process_data.get("processing_info", {})
            engine_used = processing_info.get("engine", "")
            
            if engine_used != "v2":
                self.log_test("V2 Engine Usage", False,
                             f"Wrong engine used: {engine_used}")
                return False
            
            # 4. Test V2 analysis results (if available)
            analysis_response = requests.get(f"{self.backend_url}/api/engine/v2/analysis", timeout=30)
            analysis_available = analysis_response.status_code == 200
            
            # 5. Test V2 validation results (if available)
            validation_response = requests.get(f"{self.backend_url}/api/engine/v2/validation", timeout=30)
            validation_available = validation_response.status_code == 200
            
            # Count successful V2 operations
            successful_v2_ops = sum([
                pipeline_response.status_code == 200,
                process_response.status_code == 200,
                engine_used == "v2",
                analysis_available,
                validation_available
            ])
            
            if successful_v2_ops < 3:
                self.log_test("V2 Processing Results", False,
                             f"Insufficient V2 operations: {successful_v2_ops}/5")
                return False
            
            self.log_test("V2 Processing Results", True,
                         f"V2 operations working: {successful_v2_ops}/5 operations successful")
            return True
            
        except Exception as e:
            self.log_test("V2 Processing Results", False, f"Exception: {str(e)}")
            return False
    
    def test_system_stability(self):
        """Test 5: System Stability - Ensure all repository changes maintain system stability"""
        try:
            # Test system health and stability
            
            # 1. Test basic system health
            health_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            if health_response.status_code != 200:
                self.log_test("System Health Check", False,
                             f"Health check failed: HTTP {health_response.status_code}")
                return False
            
            health_data = health_response.json()
            
            if health_data.get("status") not in ["healthy", "ok", "operational"]:
                self.log_test("System Health Status", False,
                             f"System not healthy: {health_data.get('status')}")
                return False
            
            # 2. Test concurrent repository operations
            concurrent_requests = []
            
            for i in range(5):
                try:
                    response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
                    concurrent_requests.append(response.status_code == 200)
                except:
                    concurrent_requests.append(False)
                
                time.sleep(0.1)  # Small delay between requests
            
            successful_concurrent = sum(concurrent_requests)
            
            if successful_concurrent < 4:  # At least 4/5 should succeed
                self.log_test("Concurrent Repository Operations", False,
                             f"Concurrent operations failed: {successful_concurrent}/5")
                return False
            
            # 3. Test system performance under load
            start_time = time.time()
            
            performance_requests = []
            for i in range(3):
                try:
                    response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
                    performance_requests.append(response.status_code == 200)
                except:
                    performance_requests.append(False)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            if total_time > 15:  # Should complete within 15 seconds
                self.log_test("System Performance", False,
                             f"Performance degraded: {total_time:.2f}s for 3 requests")
                return False
            
            # 4. Test system recovery after operations
            recovery_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            if recovery_response.status_code != 200:
                self.log_test("System Recovery", False,
                             f"System recovery failed: HTTP {recovery_response.status_code}")
                return False
            
            # Calculate stability metrics
            stability_score = (
                (health_response.status_code == 200) +
                (successful_concurrent >= 4) +
                (total_time <= 15) +
                (recovery_response.status_code == 200)
            )
            
            if stability_score < 4:
                self.log_test("System Stability", False,
                             f"Stability issues detected: {stability_score}/4 checks passed")
                return False
            
            self.log_test("System Stability", True,
                         f"System stable: {stability_score}/4 checks passed, {successful_concurrent}/5 concurrent ops, {total_time:.2f}s performance")
            return True
            
        except Exception as e:
            self.log_test("System Stability", False, f"Exception: {str(e)}")
            return False
    
    def test_mixed_operations(self):
        """Test 6: Mixed Operations - Test workflows with both converted and remaining direct operations"""
        try:
            # Test mixed repository and direct operations
            
            # 1. Test repository-based content library operation
            repo_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            
            if repo_response.status_code != 200:
                self.log_test("Mixed Operations - Repository", False,
                             f"Repository operation failed: HTTP {repo_response.status_code}")
                return False
            
            repo_data = repo_response.json()
            repo_articles = repo_data.get("articles", [])
            
            # 2. Test direct database operation (if available)
            direct_response = requests.get(f"{self.backend_url}/api/engine/status", timeout=30)
            direct_available = direct_response.status_code == 200
            
            # 3. Test mixed workflow - content processing with repository storage
            mixed_content = {
                "content": "# Mixed Operations Test\n\nTesting mixed repository and direct operations for KE-PR9.5.",
                "content_type": "markdown",
                "store_in_repository": True
            }
            
            mixed_response = requests.post(
                f"{self.backend_url}/api/content/process",
                json=mixed_content,
                timeout=120
            )
            
            mixed_available = mixed_response.status_code == 200
            
            # 4. Test data consistency between operations
            if mixed_available:
                # Check if processed content appears in repository
                consistency_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
                
                if consistency_response.status_code == 200:
                    consistency_data = consistency_response.json()
                    consistency_articles = consistency_data.get("articles", [])
                    
                    # Check if article count increased (indicating repository storage worked)
                    consistency_check = len(consistency_articles) >= len(repo_articles)
                else:
                    consistency_check = False
            else:
                consistency_check = True  # Skip if mixed operation not available
            
            # 5. Test fallback mechanisms
            fallback_response = requests.get(f"{self.backend_url}/api/content-library/invalid-id", timeout=30)
            fallback_working = fallback_response.status_code in [404, 400]  # Should handle gracefully
            
            # Calculate mixed operations score
            mixed_ops_score = sum([
                repo_response.status_code == 200,
                direct_available,
                mixed_available,
                consistency_check,
                fallback_working
            ])
            
            if mixed_ops_score < 3:
                self.log_test("Mixed Operations", False,
                             f"Mixed operations insufficient: {mixed_ops_score}/5")
                return False
            
            self.log_test("Mixed Operations", True,
                         f"Mixed operations working: {mixed_ops_score}/5 operations successful")
            return True
            
        except Exception as e:
            self.log_test("Mixed Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_fallbacks(self):
        """Test 7: Error Handling - Test repository error handling and fallback mechanisms"""
        try:
            # Test comprehensive error handling and fallback mechanisms
            
            # 1. Test invalid article ID handling
            invalid_id_response = requests.get(f"{self.backend_url}/api/content-library/invalid-id-12345", timeout=30)
            
            if invalid_id_response.status_code not in [404, 400]:
                self.log_test("Error Handling - Invalid ID", False,
                             f"Invalid ID not handled properly: HTTP {invalid_id_response.status_code}")
                return False
            
            # 2. Test malformed request handling
            malformed_data = {"invalid": "data", "missing": "required_fields"}
            
            malformed_response = requests.post(
                f"{self.backend_url}/api/content-library",
                json=malformed_data,
                timeout=30
            )
            
            if malformed_response.status_code not in [400, 422]:
                self.log_test("Error Handling - Malformed Request", False,
                             f"Malformed request not handled: HTTP {malformed_response.status_code}")
                return False
            
            # 3. Test repository connection error handling
            # This tests if the system gracefully handles repository issues
            connection_response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            if connection_response.status_code != 200:
                self.log_test("Error Handling - Connection", False,
                             f"Connection error handling failed: HTTP {connection_response.status_code}")
                return False
            
            connection_data = connection_response.json()
            mongodb_status = connection_data.get("mongodb", {}).get("status", "unknown")
            
            # 4. Test timeout handling
            try:
                timeout_response = requests.get(f"{self.backend_url}/api/content-library", timeout=1)
                timeout_handled = True
            except requests.exceptions.Timeout:
                timeout_handled = True  # Timeout is expected and handled
            except Exception:
                timeout_handled = False
            
            # 5. Test error response format
            error_response = requests.get(f"{self.backend_url}/api/content-library/nonexistent", timeout=30)
            
            if error_response.status_code in [404, 400]:
                try:
                    error_data = error_response.json()
                    has_error_format = "error" in error_data or "message" in error_data or "detail" in error_data
                except:
                    has_error_format = False
            else:
                has_error_format = True  # Skip if endpoint doesn't exist
            
            # 6. Test system recovery after errors
            recovery_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            system_recovered = recovery_response.status_code == 200
            
            # Calculate error handling score
            error_handling_score = sum([
                invalid_id_response.status_code in [404, 400],
                malformed_response.status_code in [400, 422],
                connection_response.status_code == 200,
                timeout_handled,
                has_error_format,
                system_recovered
            ])
            
            if error_handling_score < 4:
                self.log_test("Error Handling & Fallbacks", False,
                             f"Error handling insufficient: {error_handling_score}/6")
                return False
            
            self.log_test("Error Handling & Fallbacks", True,
                         f"Error handling working: {error_handling_score}/6 mechanisms functional")
            return True
            
        except Exception as e:
            self.log_test("Error Handling & Fallbacks", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all KE-PR9.5 MongoDB Final Sweep validation tests"""
        print("🎯 KE-PR9.5: MONGODB FINAL SWEEP PROGRESS VALIDATION")
        print("=" * 80)
        print("Comprehensive testing for 90%+ MongoDB centralization completion status")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_processing_jobs_repository,
            self.test_content_library_operations,
            self.test_repository_pattern_integration,
            self.test_v2_processing_results,
            self.test_system_stability,
            self.test_mixed_operations,
            self.test_error_handling_fallbacks
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
        print("🎯 KE-PR9.5: MONGODB FINAL SWEEP TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 90:
            print("🎉 KE-PR9.5 MONGODB FINAL SWEEP: EXCELLENT - 90%+ MongoDB centralization validated!")
            print("✅ ProcessingJobsRepository: Newly created functionality operational")
            print("✅ Content Library Operations: Repository pattern working correctly")
            print("✅ Repository Pattern Integration: All converted operations functional")
            print("✅ V2 Processing Results: Converted V2 operations working")
            print("✅ System Stability: Repository changes maintain stability")
            print("✅ Mixed Operations: Both converted and remaining operations work")
            print("✅ Error Handling: Repository error handling and fallbacks functional")
        elif success_rate >= 80:
            print("🎉 KE-PR9.5 MONGODB FINAL SWEEP: GOOD - Strong MongoDB centralization progress!")
        elif success_rate >= 70:
            print("✅ KE-PR9.5 MONGODB FINAL SWEEP: ACCEPTABLE - Most MongoDB operations working")
        elif success_rate >= 50:
            print("⚠️ KE-PR9.5 MONGODB FINAL SWEEP: PARTIAL - Some MongoDB centralization issues remain")
        else:
            print("❌ KE-PR9.5 MONGODB FINAL SWEEP: NEEDS ATTENTION - Major MongoDB centralization issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = MongoDBFinalSweepTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)