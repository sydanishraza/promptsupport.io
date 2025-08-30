#!/usr/bin/env python3
"""
V2 PUT Endpoint Testing - Specific Issue Investigation
Testing the V2 PUT endpoint /api/content-library/{article_id} with article ID "cb0162f2-a05d-477c-a5aa-fbdad8c615ac"
Issue: 500 error with "Error updating article: (Type: HTTPException)" but database operations work fine
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

class V2PutEndpointTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.target_article_id = "cb0162f2-a05d-477c-a5aa-fbdad8c615ac"
        
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

    def test_backend_connectivity(self):
        """Test 1: Verify backend is accessible"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Backend Connectivity", True, f"Backend accessible at {self.backend_url}")
                return True
            else:
                self.log_test("Backend Connectivity", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Backend Connectivity", False, f"Connection failed: {str(e)}")
            return False

    def test_database_direct_operations(self):
        """Test 2: Test database operations directly to verify they work"""
        try:
            import motor.motor_asyncio
            from bson import ObjectId
            
            # Use same connection pattern as the API
            MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/promptsupport')
            DATABASE_NAME = os.getenv("DATABASE_NAME", "promptsupport")
            
            async def test_db_operations():
                mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
                db = mongo_client[DATABASE_NAME]
                collection = db["content_library"]
                
                # Test finding the specific article
                article_id = self.target_article_id
                
                # Try UUID query first
                query_uuid = {"id": article_id}
                doc_uuid = await collection.find_one(query_uuid)
                print(f"🔍 UUID query result: {'Found' if doc_uuid else 'Not Found'}")
                
                # Try ObjectId query if UUID fails
                doc_objectid = None
                if not doc_uuid:
                    try:
                        if len(article_id) == 24 and all(c in '0123456789abcdef' for c in article_id):
                            query_objectid = {"_id": ObjectId(article_id)}
                            doc_objectid = await collection.find_one(query_objectid)
                            print(f"🔍 ObjectId query result: {'Found' if doc_objectid else 'Not Found'}")
                    except Exception as e:
                        print(f"🔍 ObjectId query failed: {e}")
                
                found_doc = doc_uuid or doc_objectid
                if not found_doc:
                    print(f"🔍 Article {article_id} not found in database")
                    return False, "Article not found in database"
                
                print(f"🔍 Found article: {found_doc.get('title', 'No title')}")
                
                # Test update operation directly
                update_data = {
                    "title": "Test Title - Direct DB",
                    "content": "Test content - Direct DB", 
                    "status": "draft",
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                # Use the same query that found the document
                query = query_uuid if doc_uuid else {"_id": ObjectId(article_id)}
                result = await collection.update_one(query, {"$set": update_data})
                
                print(f"🔍 Direct DB update result - matched: {result.matched_count}, modified: {result.modified_count}")
                
                # Verify the update worked
                updated_doc = await collection.find_one(query)
                if updated_doc and updated_doc.get('title') == "Test Title - Direct DB":
                    print(f"✅ Direct DB update successful")
                    return True, f"Direct DB operations work - matched: {result.matched_count}, modified: {result.modified_count}"
                else:
                    print(f"❌ Direct DB update failed")
                    return False, "Direct DB update verification failed"
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success, details = loop.run_until_complete(test_db_operations())
            loop.close()
            
            self.log_test("Database Direct Operations", success, details)
            return success
            
        except Exception as e:
            self.log_test("Database Direct Operations", False, f"Exception: {str(e)}")
            return False

    def test_api_router_accessibility(self):
        """Test 3: Verify the API router is accessible and the route exists"""
        try:
            # Test if the API router is loaded
            response = requests.get(f"{self.backend_url}/api/content-library", timeout=10)
            
            if response.status_code in [200, 404]:  # 404 is OK, means route exists but no content
                self.log_test("API Router Accessibility", True, f"API router accessible - HTTP {response.status_code}")
                return True
            else:
                self.log_test("API Router Accessibility", False, f"Unexpected HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("API Router Accessibility", False, f"Exception: {str(e)}")
            return False

    def test_put_endpoint_with_target_article(self):
        """Test 4: Test the specific PUT endpoint with the target article ID"""
        try:
            article_id = self.target_article_id
            test_payload = {
                "title": "Test Title",
                "content": "Test content", 
                "status": "draft"
            }
            
            print(f"🔧 Testing PUT /api/content-library/{article_id}")
            print(f"🔧 Payload: {test_payload}")
            
            response = requests.put(
                f"{self.backend_url}/api/content-library/{article_id}",
                json=test_payload,
                timeout=30
            )
            
            print(f"🔧 Response status: {response.status_code}")
            print(f"🔧 Response headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"🔧 Response data: {response_data}")
            except:
                print(f"🔧 Response text: {response.text}")
            
            if response.status_code == 200:
                self.log_test("PUT Endpoint Target Article", True, f"Successfully updated article {article_id}")
                return True
            elif response.status_code == 500:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'No detail provided')
                except:
                    error_detail = response.text
                
                self.log_test("PUT Endpoint Target Article", False, f"500 Error: {error_detail}")
                return False
            else:
                self.log_test("PUT Endpoint Target Article", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PUT Endpoint Target Article", False, f"Exception: {str(e)}")
            return False

    def test_backend_logs_capture(self):
        """Test 5: Capture backend logs during PUT request to see debug messages"""
        try:
            print(f"🔧 Capturing backend logs during PUT request...")
            
            # Make the PUT request
            article_id = self.target_article_id
            test_payload = {
                "title": "Test Title - Log Capture",
                "content": "Test content - Log Capture",
                "status": "draft"
            }
            
            print(f"🔧 Making PUT request to capture logs...")
            response = requests.put(
                f"{self.backend_url}/api/content-library/{article_id}",
                json=test_payload,
                timeout=30
            )
            
            print(f"🔧 PUT Response: {response.status_code}")
            
            # Try to get backend logs (this might not work in all environments)
            try:
                import subprocess
                
                # Try to get supervisor logs for backend
                log_commands = [
                    "tail -n 50 /var/log/supervisor/backend.*.log",
                    "tail -n 50 /var/log/supervisor/backend-stdout*.log",
                    "journalctl -u backend --no-pager -n 50"
                ]
                
                logs_captured = False
                for cmd in log_commands:
                    try:
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0 and result.stdout.strip():
                            print(f"🔧 Backend logs from '{cmd}':")
                            print(result.stdout[-1000:])  # Last 1000 chars
                            logs_captured = True
                            break
                    except:
                        continue
                
                if not logs_captured:
                    print(f"🔧 Could not capture backend logs via standard methods")
                
            except Exception as log_error:
                print(f"🔧 Log capture failed: {log_error}")
            
            # The test passes if we made the request, regardless of log capture
            self.log_test("Backend Logs Capture", True, f"PUT request made, response: {response.status_code}")
            return True
            
        except Exception as e:
            self.log_test("Backend Logs Capture", False, f"Exception: {str(e)}")
            return False

    def test_duplicate_routes_check(self):
        """Test 6: Check for duplicate routes or middleware issues"""
        try:
            # Test different variations of the endpoint to check for conflicts
            article_id = self.target_article_id
            
            endpoints_to_test = [
                f"/api/content-library/{article_id}",
                f"/api/content-library/{article_id}/",
                f"/api/content-library/{article_id}/legacy"
            ]
            
            results = []
            for endpoint in endpoints_to_test:
                try:
                    response = requests.put(
                        f"{self.backend_url}{endpoint}",
                        json={"title": "Test", "content": "Test", "status": "draft"},
                        timeout=10
                    )
                    results.append({
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "accessible": True
                    })
                    print(f"🔧 {endpoint}: HTTP {response.status_code}")
                except Exception as e:
                    results.append({
                        "endpoint": endpoint,
                        "error": str(e),
                        "accessible": False
                    })
                    print(f"🔧 {endpoint}: Error - {e}")
            
            # Check for unexpected route conflicts
            main_route_result = next((r for r in results if r["endpoint"].endswith(article_id)), None)
            
            if main_route_result and main_route_result.get("accessible"):
                self.log_test("Duplicate Routes Check", True, f"Main route accessible, {len(results)} endpoints tested")
                return True
            else:
                self.log_test("Duplicate Routes Check", False, f"Main route issues detected")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Routes Check", False, f"Exception: {str(e)}")
            return False

    def test_error_pattern_analysis(self):
        """Test 7: Analyze error patterns to identify root cause"""
        try:
            article_id = self.target_article_id
            
            # Test with different payloads to see if specific data causes issues
            test_payloads = [
                {"title": "Simple", "content": "Simple", "status": "draft"},
                {"title": "", "content": "", "status": "draft"},
                {"title": "Test Title", "content": "Test content", "status": "published"},
                {"title": "Test Title", "content": "Test content"},  # Missing status
                {}  # Empty payload
            ]
            
            error_patterns = []
            
            for i, payload in enumerate(test_payloads):
                try:
                    print(f"🔧 Testing payload {i+1}: {payload}")
                    response = requests.put(
                        f"{self.backend_url}/api/content-library/{article_id}",
                        json=payload,
                        timeout=15
                    )
                    
                    if response.status_code == 500:
                        try:
                            error_data = response.json()
                            error_detail = error_data.get('detail', '')
                            error_patterns.append({
                                "payload": payload,
                                "error": error_detail,
                                "status_code": response.status_code
                            })
                            print(f"🔧 Payload {i+1} - 500 Error: {error_detail}")
                        except:
                            error_patterns.append({
                                "payload": payload,
                                "error": response.text,
                                "status_code": response.status_code
                            })
                            print(f"🔧 Payload {i+1} - 500 Error (text): {response.text}")
                    else:
                        print(f"🔧 Payload {i+1} - HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"🔧 Payload {i+1} - Exception: {e}")
            
            # Analyze patterns
            if error_patterns:
                # Check if all errors are the same
                unique_errors = set(ep.get('error', '') for ep in error_patterns)
                
                if len(unique_errors) == 1 and "(Type: HTTPException)" in list(unique_errors)[0]:
                    self.log_test("Error Pattern Analysis", True, 
                                f"Consistent error pattern found: Empty HTTPException being raised - {len(error_patterns)} errors analyzed")
                else:
                    self.log_test("Error Pattern Analysis", True,
                                f"Multiple error patterns found - {len(unique_errors)} unique errors")
            else:
                self.log_test("Error Pattern Analysis", True, "No 500 errors found in pattern testing")
            
            return True
            
        except Exception as e:
            self.log_test("Error Pattern Analysis", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all V2 PUT endpoint tests"""
        print("🎯 V2 PUT ENDPOINT TESTING - SPECIFIC ISSUE INVESTIGATION")
        print("=" * 80)
        print(f"Target Article ID: {self.target_article_id}")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_backend_connectivity,
            self.test_database_direct_operations,
            self.test_api_router_accessibility,
            self.test_put_endpoint_with_target_article,
            self.test_backend_logs_capture,
            self.test_duplicate_routes_check,
            self.test_error_pattern_analysis
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
        print("🎯 V2 PUT ENDPOINT TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Analysis and recommendations
        print()
        print("🔍 ANALYSIS & RECOMMENDATIONS:")
        print("=" * 50)
        
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        if any("PUT Endpoint Target Article" in r["test"] and "500 Error" in r["details"] for r in failed_tests):
            print("🚨 CONFIRMED: V2 PUT endpoint returns 500 error")
            print("🔧 ISSUE: Empty HTTPException being raised in API endpoint")
            print("💡 RECOMMENDATION: Check exception handling in /app/api/router.py line 488")
            print("💡 LIKELY CAUSE: Exception being caught and re-raised as HTTPException without proper message")
        
        if any("Database Direct Operations" in r["test"] and r["passed"] for r in self.test_results):
            print("✅ CONFIRMED: Database operations work correctly when tested directly")
            print("💡 CONCLUSION: Issue is in the API endpoint layer, not database layer")
        
        return success_rate

if __name__ == "__main__":
    tester = V2PutEndpointTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)