#!/usr/bin/env python3
"""
Content Library API Endpoints Testing - Review Request Verification
Testing the specific fixes mentioned in the review request:

1. Test Article Status Update API: PUT /api/content/library/{article_id} for status updates
2. Test Article Rename API: PUT /api/content/library/{article_id} for title updates  
3. Test Article Creation API: POST /api/content/library
4. Test Bulk Operations API: Multiple PUT requests for bulk status changes

Changes being tested:
- Updated API endpoints from /api/content-library/ to /api/content/library/
- Updated router.py endpoints to match frontend calls
- Enhanced More Actions button visibility
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

class ContentLibraryEndpointTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.created_articles = []  # Track articles created during testing
        
        print(f"🎯 CONTENT LIBRARY API ENDPOINTS TESTING")
        print("=" * 80)
        print("Testing the specific fixes mentioned in the review request:")
        print("- Article Status Update API: PUT /api/content/library/{article_id}")
        print("- Article Rename API: PUT /api/content/library/{article_id}")  
        print("- Article Creation API: POST /api/content/library")
        print("- Bulk Operations API: Multiple PUT requests")
        print(f"Backend URL: {self.backend_url}")
        print("=" * 80)
        
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
        
    def test_new_endpoint_get(self):
        """Test 1: Verify new GET /api/content/library endpoint works"""
        print("\n🔍 Test 1: GET /api/content/library endpoint")
        try:
            response = requests.get(f"{self.backend_url}/api/content/library", timeout=10)
            
            if response.status_code != 200:
                self.log_test("GET /api/content/library", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check response structure
            if not isinstance(data, dict):
                self.log_test("GET /api/content/library", False, "Response not a dict")
                return False
                
            if "articles" not in data:
                self.log_test("GET /api/content/library", False, "No articles field in response")
                return False
                
            articles = data["articles"]
            article_count = len(articles)
            
            self.log_test("GET /api/content/library", True, 
                         f"{article_count} articles retrieved, source: {data.get('source', 'unknown')}")
            return True
            
        except Exception as e:
            self.log_test("GET /api/content/library", False, f"Exception: {str(e)}")
            return False
    
    def test_article_creation_api(self):
        """Test 2: POST /api/content/library endpoint for article creation"""
        print("\n🔍 Test 2: POST /api/content/library endpoint")
        try:
            # Create test article with realistic data
            test_article = {
                "title": "Content Library API Test Article",
                "content": "<h2>Introduction</h2><p>This is a test article created to verify the Content Library API endpoints are working correctly after the /api/content-library to /api/content/library migration.</p><h3>Features Tested</h3><ul><li>Article creation via POST</li><li>Article updates via PUT</li><li>Status changes</li><li>Title updates</li></ul><p>This article will be used for testing various API operations including status updates and title changes.</p>",
                "status": "draft"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/content/library",
                json=test_article,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code != 200:
                self.log_test("POST /api/content/library", False, f"HTTP {response.status_code} - {response.text[:200]}")
                return None
                
            data = response.json()
            
            # Check response structure
            if not isinstance(data, dict) or "id" not in data:
                self.log_test("POST /api/content/library", False, "Invalid response structure")
                return None
                
            article_id = data["id"]
            self.created_articles.append(article_id)
            
            # Verify article was created with correct data
            if data.get("title") != test_article["title"]:
                self.log_test("POST /api/content/library", False, "Title mismatch in response")
                return None
                
            if data.get("status") != test_article["status"]:
                self.log_test("POST /api/content/library", False, "Status mismatch in response")
                return None
            
            self.log_test("POST /api/content/library", True, 
                         f"Article created with ID: {article_id}, status: {data.get('status')}")
            return article_id
            
        except Exception as e:
            self.log_test("POST /api/content/library", False, f"Exception: {str(e)}")
            return None
    
    def test_article_status_update_api(self, article_id: str):
        """Test 3: PUT /api/content/library/{article_id} for status updates"""
        print(f"\n🔍 Test 3: PUT /api/content/library/{article_id} for status update")
        try:
            # Test status update from draft to published
            update_data = {
                "title": "Content Library API Test Article",  # Keep same title
                "content": "<h2>Introduction</h2><p>This is a test article created to verify the Content Library API endpoints are working correctly after the /api/content-library to /api/content/library migration.</p><h3>Features Tested</h3><ul><li>Article creation via POST</li><li>Article updates via PUT</li><li>Status changes</li><li>Title updates</li></ul><p>This article will be used for testing various API operations including status updates and title changes.</p>",
                "status": "published"  # Change status
            }
            
            response = requests.put(
                f"{self.backend_url}/api/content/library/{article_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code != 200:
                self.log_test("PUT Status Update", False, f"HTTP {response.status_code} - {response.text[:200]}")
                return False
                
            data = response.json()
            
            # Verify status was updated
            if data.get("status") != "published":
                self.log_test("PUT Status Update", False, f"Status not updated: {data.get('status')}")
                return False
            
            self.log_test("PUT Status Update", True, 
                         f"Status updated from draft to published for article {article_id}")
            return True
            
        except Exception as e:
            self.log_test("PUT Status Update", False, f"Exception: {str(e)}")
            return False
    
    def test_article_rename_api(self, article_id: str):
        """Test 4: PUT /api/content/library/{article_id} for title updates (rename)"""
        print(f"\n🔍 Test 4: PUT /api/content/library/{article_id} for title rename")
        try:
            # Test title update (rename)
            new_title = "Content Library API Test Article - RENAMED"
            update_data = {
                "title": new_title,
                "content": "<h2>Introduction</h2><p>This is a test article created to verify the Content Library API endpoints are working correctly after the /api/content-library to /api/content/library migration.</p><h3>Features Tested</h3><ul><li>Article creation via POST</li><li>Article updates via PUT</li><li>Status changes</li><li>Title updates</li></ul><p>This article has been renamed to test the article rename functionality.</p>",
                "status": "published"  # Keep same status
            }
            
            response = requests.put(
                f"{self.backend_url}/api/content/library/{article_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code != 200:
                self.log_test("PUT Title Rename", False, f"HTTP {response.status_code} - {response.text[:200]}")
                return False
                
            data = response.json()
            
            # Verify title was updated
            if data.get("title") != new_title:
                self.log_test("PUT Title Rename", False, f"Title not updated: {data.get('title')}")
                return False
            
            self.log_test("PUT Title Rename", True, 
                         f"Title updated to '{new_title}' for article {article_id}")
            return True
            
        except Exception as e:
            self.log_test("PUT Title Rename", False, f"Exception: {str(e)}")
            return False
    
    def test_bulk_operations_api(self):
        """Test 5: Bulk operations with multiple PUT requests for status changes"""
        print("\n🔍 Test 5: Bulk Operations - Multiple PUT requests")
        try:
            # Create multiple test articles for bulk operations
            bulk_articles = []
            
            for i in range(3):
                test_article = {
                    "title": f"Bulk Test Article {i+1}",
                    "content": f"<h2>Bulk Test Article {i+1}</h2><p>This is test article {i+1} created for bulk operations testing. It will be used to verify that multiple PUT requests work correctly for bulk status changes.</p>",
                    "status": "draft"
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/content/library",
                    json=test_article,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    article_id = data.get("id")
                    if article_id:
                        bulk_articles.append(article_id)
                        self.created_articles.append(article_id)
            
            if len(bulk_articles) < 3:
                self.log_test("Bulk Operations", False, f"Only created {len(bulk_articles)}/3 articles")
                return False
            
            # Perform bulk status updates
            successful_updates = 0
            
            for i, article_id in enumerate(bulk_articles):
                update_data = {
                    "title": f"Bulk Test Article {i+1} - PUBLISHED",
                    "content": f"<h2>Bulk Test Article {i+1}</h2><p>This article has been updated as part of bulk operations testing. Status changed from draft to published.</p>",
                    "status": "published"
                }
                
                response = requests.put(
                    f"{self.backend_url}/api/content/library/{article_id}",
                    json=update_data,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "published":
                        successful_updates += 1
                
                # Small delay between requests to avoid overwhelming the server
                time.sleep(0.5)
            
            if successful_updates == 3:
                self.log_test("Bulk Operations", True, 
                             f"Successfully updated status for all {successful_updates}/3 articles")
                return True
            else:
                self.log_test("Bulk Operations", False, 
                             f"Only {successful_updates}/3 articles updated successfully")
                return False
            
        except Exception as e:
            self.log_test("Bulk Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_endpoint_migration_verification(self):
        """Test 6: Verify endpoint migration from /api/content-library to /api/content/library"""
        print("\n🔍 Test 6: Endpoint Migration Verification")
        try:
            # Test that new endpoint works
            new_response = requests.get(f"{self.backend_url}/api/content/library", timeout=10)
            
            if new_response.status_code != 200:
                self.log_test("Endpoint Migration", False, 
                             f"New endpoint /api/content/library failed: HTTP {new_response.status_code}")
                return False
            
            # Test that old endpoint behavior (may still exist for compatibility)
            old_endpoint_response = None
            try:
                old_endpoint_response = requests.get(f"{self.backend_url}/api/content-library", timeout=5)
            except:
                pass  # Old endpoint might not exist
            
            # Check migration status
            migration_status = "New endpoint /api/content/library working"
            if old_endpoint_response:
                if old_endpoint_response.status_code in [404, 410]:
                    migration_status += ", old endpoint properly deprecated"
                elif old_endpoint_response.status_code == 200:
                    migration_status += ", old endpoint still works (backward compatibility)"
                else:
                    migration_status += f", old endpoint returns HTTP {old_endpoint_response.status_code}"
            else:
                migration_status += ", old endpoint not accessible"
            
            self.log_test("Endpoint Migration", True, migration_status)
            return True
            
        except Exception as e:
            self.log_test("Endpoint Migration", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_articles(self):
        """Clean up articles created during testing"""
        print("\n🧹 Cleaning up test articles...")
        try:
            cleaned_count = 0
            for article_id in self.created_articles:
                try:
                    response = requests.delete(f"{self.backend_url}/api/content/library/{article_id}", timeout=10)
                    if response.status_code == 200:
                        cleaned_count += 1
                except:
                    pass  # Continue cleanup even if some fail
            
            if cleaned_count > 0:
                print(f"🧹 Cleaned up {cleaned_count}/{len(self.created_articles)} test articles")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")
    
    def run_all_tests(self):
        """Run all Content Library API endpoint tests"""
        
        # Test 1: Basic GET functionality
        self.test_new_endpoint_get()
        time.sleep(1)
        
        # Test 2: Article creation
        article_id = self.test_article_creation_api()
        time.sleep(1)
        
        # Test 3 & 4: Article updates (if creation succeeded)
        if article_id:
            self.test_article_status_update_api(article_id)
            time.sleep(1)
            
            self.test_article_rename_api(article_id)
            time.sleep(1)
        
        # Test 5: Bulk operations
        self.test_bulk_operations_api()
        time.sleep(1)
        
        # Test 6: Endpoint migration verification
        self.test_endpoint_migration_verification()
        
        # Cleanup
        self.cleanup_test_articles()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 CONTENT LIBRARY API ENDPOINTS TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 CONTENT LIBRARY API ENDPOINTS: PERFECT - All fixes working correctly!")
            print("✅ GET /api/content/library: Working correctly")
            print("✅ POST /api/content/library: Article creation working")
            print("✅ PUT /api/content/library/{id}: Status updates working")
            print("✅ PUT /api/content/library/{id}: Title updates (rename) working")
            print("✅ Bulk operations: Multiple PUT requests working")
            print("✅ Endpoint migration: /api/content-library → /api/content/library successful")
        elif success_rate >= 85:
            print("🎉 CONTENT LIBRARY API ENDPOINTS: EXCELLENT - Most fixes working!")
        elif success_rate >= 70:
            print("✅ CONTENT LIBRARY API ENDPOINTS: GOOD - Major functionality working")
        elif success_rate >= 50:
            print("⚠️ CONTENT LIBRARY API ENDPOINTS: PARTIAL - Some issues remain")
        else:
            print("❌ CONTENT LIBRARY API ENDPOINTS: NEEDS ATTENTION - Major issues detected")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = ContentLibraryEndpointTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)