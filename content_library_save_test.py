#!/usr/bin/env python3
"""
Content Library Save Functionality Testing
Testing the specific save functionality issues reported by the user:
1. New Article Creation (POST /api/content-library)
2. Existing Article Editing (PUT /api/content-library/{article_id} with 404 errors)
3. Database Investigation (ID format mismatches)
"""

import os
import sys
import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any
from pymongo import MongoClient
from bson import ObjectId

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

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/promptsupport")
DATABASE_NAME = os.getenv("DATABASE_NAME", "promptsupport_db")

class ContentLibrarySaveTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.mongo_client = None
        self.db = None
        
        # Connect to MongoDB for direct database investigation
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[DATABASE_NAME]
            print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            
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
        
    def test_database_investigation(self):
        """Test: Investigate database structure and article ID formats"""
        try:
            if self.db is None:
                self.log_test("Database Investigation", False, "MongoDB connection not available")
                return False
                
            # Check content_library collection
            collection = self.db.content_library
            
            # Get total count
            total_articles = collection.count_documents({})
            print(f"📊 Total articles in database: {total_articles}")
            
            if total_articles == 0:
                self.log_test("Database Investigation", False, "No articles found in database")
                return False
            
            # Sample some articles to check ID formats
            sample_articles = list(collection.find({}).limit(10))
            
            id_formats = {
                "uuid_format": 0,
                "objectid_format": 0,
                "string_format": 0,
                "other_format": 0
            }
            
            sample_ids = []
            
            for article in sample_articles:
                article_id = article.get('id') or article.get('_id')
                sample_ids.append(str(article_id))
                
                # Check ID format
                if isinstance(article_id, ObjectId):
                    id_formats["objectid_format"] += 1
                elif isinstance(article_id, str):
                    if len(article_id) == 36 and article_id.count('-') == 4:
                        id_formats["uuid_format"] += 1
                    else:
                        id_formats["string_format"] += 1
                else:
                    id_formats["other_format"] += 1
            
            print(f"📋 ID Format Analysis:")
            for format_type, count in id_formats.items():
                print(f"  - {format_type}: {count}")
            
            print(f"📋 Sample Article IDs:")
            for i, sample_id in enumerate(sample_ids[:5]):
                print(f"  - Article {i+1}: {sample_id}")
            
            # Check field structure
            sample_article = sample_articles[0] if sample_articles else {}
            fields_present = list(sample_article.keys())
            
            print(f"📋 Article Fields Present: {fields_present}")
            
            # Check for both 'id' and '_id' fields
            has_id_field = any('id' in article for article in sample_articles)
            has_underscore_id = any('_id' in article for article in sample_articles)
            
            print(f"📋 Field Analysis:")
            print(f"  - Articles with 'id' field: {has_id_field}")
            print(f"  - Articles with '_id' field: {has_underscore_id}")
            
            self.log_test("Database Investigation", True, 
                         f"Found {total_articles} articles, ID formats: UUID={id_formats['uuid_format']}, ObjectId={id_formats['objectid_format']}")
            
            return {
                "total_articles": total_articles,
                "id_formats": id_formats,
                "sample_ids": sample_ids,
                "has_id_field": has_id_field,
                "has_underscore_id": has_underscore_id,
                "sample_article": sample_article
            }
            
        except Exception as e:
            self.log_test("Database Investigation", False, f"Exception: {str(e)}")
            return False
    
    def test_get_existing_articles(self):
        """Test: Get list of existing articles from /api/content/library"""
        try:
            # Test the corrected endpoint
            response = requests.get(f"{self.backend_url}/api/content/library", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Get Existing Articles", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check response structure
            if not isinstance(data, dict):
                self.log_test("Get Existing Articles", False, f"Invalid response format: {type(data)}")
                return False
            
            articles = data.get('articles', [])
            total = data.get('total', 0)
            
            print(f"📊 API Response: {len(articles)} articles returned, total: {total}")
            
            if len(articles) == 0:
                self.log_test("Get Existing Articles", False, "No articles returned from API")
                return False
            
            # Analyze article ID formats from API
            api_id_formats = {
                "uuid_format": 0,
                "objectid_format": 0,
                "string_format": 0,
                "other_format": 0
            }
            
            sample_api_ids = []
            
            for article in articles[:10]:  # Sample first 10
                article_id = article.get('id')
                sample_api_ids.append(str(article_id))
                
                # Check ID format
                if isinstance(article_id, str):
                    if len(article_id) == 36 and article_id.count('-') == 4:
                        api_id_formats["uuid_format"] += 1
                    elif len(article_id) == 24:  # ObjectId string length
                        api_id_formats["objectid_format"] += 1
                    else:
                        api_id_formats["string_format"] += 1
                else:
                    api_id_formats["other_format"] += 1
            
            print(f"📋 API ID Format Analysis:")
            for format_type, count in api_id_formats.items():
                print(f"  - {format_type}: {count}")
            
            print(f"📋 Sample API Article IDs:")
            for i, sample_id in enumerate(sample_api_ids[:5]):
                print(f"  - Article {i+1}: {sample_id}")
            
            self.log_test("Get Existing Articles", True, 
                         f"Retrieved {len(articles)} articles, API ID formats: UUID={api_id_formats['uuid_format']}, ObjectId={api_id_formats['objectid_format']}")
            
            return {
                "articles": articles,
                "total": total,
                "api_id_formats": api_id_formats,
                "sample_api_ids": sample_api_ids
            }
            
        except Exception as e:
            self.log_test("Get Existing Articles", False, f"Exception: {str(e)}")
            return False
    
    def test_new_article_creation(self):
        """Test: Create new article via POST /api/content-library"""
        try:
            # Create sample article data
            test_article = {
                "title": f"Test Article - Save Functionality Test {int(time.time())}",
                "content": "<h2>Test Content</h2><p>This is a test article created to verify the save functionality. Created at " + datetime.now().isoformat() + "</p>",
                "status": "published",
                "tags": ["test", "save-functionality", "automated-test"],
                "article_type": "test",
                "metadata": {
                    "test_purpose": "save_functionality_verification",
                    "created_by": "automated_test",
                    "test_timestamp": datetime.now().isoformat()
                }
            }
            
            print(f"📝 Creating test article: {test_article['title']}")
            
            # POST to create new article
            response = requests.post(f"{self.backend_url}/api/content-library", 
                                   json=test_article, 
                                   timeout=30)
            
            print(f"📤 POST Response: HTTP {response.status_code}")
            
            if response.status_code not in [200, 201]:
                self.log_test("New Article Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            response_data = response.json()
            print(f"📥 Response data: {json.dumps(response_data, indent=2)}")
            
            # Check if article was created successfully
            created_id = response_data.get('id')
            if not created_id:
                self.log_test("New Article Creation", False, "No ID in response")
                return False
            
            print(f"✅ Article created with ID: {created_id}")
            
            # The response format is different - it's a success response with ID
            created_article = {
                "id": created_id,
                "title": test_article["title"],
                "content": test_article["content"]
            }
            
            # Verify article appears in content library
            time.sleep(2)  # Wait for database consistency
            
            library_response = requests.get(f"{self.backend_url}/api/content/library", timeout=30)
            if library_response.status_code == 200:
                library_data = library_response.json()
                articles = library_data.get('articles', [])
                
                # Check if our article appears in the list
                found_article = None
                for article in articles:
                    if article.get('id') == created_id:
                        found_article = article
                        break
                
                if found_article:
                    print(f"✅ Article found in content library: {found_article.get('title')}")
                    verification_status = "Article appears in content library"
                else:
                    print(f"❌ Article NOT found in content library")
                    verification_status = "Article missing from content library"
            else:
                verification_status = f"Could not verify (HTTP {library_response.status_code})"
            
            self.log_test("New Article Creation", True, 
                         f"Article created with ID {created_id}, {verification_status}")
            
            return {
                "created_article": created_article,
                "created_id": created_id,
                "verification_status": verification_status
            }
            
        except Exception as e:
            self.log_test("New Article Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_existing_article_editing(self, existing_articles_data):
        """Test: Edit existing article via PUT /api/content-library/{article_id}"""
        try:
            if not existing_articles_data or not existing_articles_data.get('articles'):
                self.log_test("Existing Article Editing", False, "No existing articles to test with")
                return False
            
            articles = existing_articles_data['articles']
            
            # Test with multiple article IDs to identify patterns
            test_results = []
            
            for i, article in enumerate(articles[:3]):  # Test first 3 articles
                article_id = article.get('id')
                article_title = article.get('title', 'Unknown Title')
                
                print(f"🔄 Testing edit for Article {i+1}: {article_title}")
                print(f"   Article ID: {article_id}")
                print(f"   ID Type: {type(article_id)}")
                print(f"   ID Length: {len(str(article_id))}")
                
                # Create update data
                updated_content = f"<h2>Updated Content</h2><p>This article was updated during save functionality testing at {datetime.now().isoformat()}</p><p>Original content preserved below:</p>" + article.get('content', '')
                
                update_data = {
                    "title": article.get('title', 'Updated Title'),
                    "content": updated_content,
                    "status": article.get('status', 'published'),
                    "tags": article.get('tags', []) + ['updated-by-test'],
                    "metadata": {
                        **article.get('metadata', {}),
                        "last_updated": datetime.now().isoformat(),
                        "updated_by": "automated_test"
                    }
                }
                
                # Test PUT request
                put_url = f"{self.backend_url}/api/content-library/{article_id}"
                print(f"📤 PUT URL: {put_url}")
                
                response = requests.put(put_url, json=update_data, timeout=30)
                
                print(f"📥 PUT Response: HTTP {response.status_code}")
                
                result = {
                    "article_id": article_id,
                    "article_title": article_title,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_text": response.text[:500] if response.text else ""
                }
                
                if response.status_code == 404:
                    print(f"❌ 404 Error for ID {article_id}")
                    result["error_type"] = "404_not_found"
                elif response.status_code == 200:
                    print(f"✅ Successfully updated article {article_id}")
                    try:
                        response_data = response.json()
                        result["response_data"] = response_data
                    except:
                        pass
                else:
                    print(f"⚠️ Unexpected status code {response.status_code}")
                    result["error_type"] = f"http_{response.status_code}"
                
                test_results.append(result)
                time.sleep(1)  # Brief pause between requests
            
            # Analyze results
            successful_updates = [r for r in test_results if r['success']]
            failed_404 = [r for r in test_results if r['status_code'] == 404]
            other_failures = [r for r in test_results if not r['success'] and r['status_code'] != 404]
            
            print(f"📊 Edit Test Results:")
            print(f"   Successful updates: {len(successful_updates)}")
            print(f"   404 errors: {len(failed_404)}")
            print(f"   Other failures: {len(other_failures)}")
            
            # Determine overall result
            if len(successful_updates) == len(test_results):
                self.log_test("Existing Article Editing", True, 
                             f"All {len(test_results)} articles updated successfully")
                overall_success = True
            elif len(failed_404) > 0:
                self.log_test("Existing Article Editing", False, 
                             f"{len(failed_404)}/{len(test_results)} articles returned 404 errors")
                overall_success = False
            else:
                self.log_test("Existing Article Editing", False, 
                             f"{len(other_failures)}/{len(test_results)} articles failed with other errors")
                overall_success = False
            
            return {
                "test_results": test_results,
                "successful_updates": successful_updates,
                "failed_404": failed_404,
                "other_failures": other_failures,
                "overall_success": overall_success
            }
            
        except Exception as e:
            self.log_test("Existing Article Editing", False, f"Exception: {str(e)}")
            return False
    
    def test_id_format_compatibility(self, db_data, api_data):
        """Test: Compare ID formats between database and API"""
        try:
            if not db_data or not api_data:
                self.log_test("ID Format Compatibility", False, "Missing database or API data")
                return False
            
            db_id_formats = db_data.get('id_formats', {})
            api_id_formats = api_data.get('api_id_formats', {})
            
            print(f"🔍 ID Format Comparison:")
            print(f"   Database - UUID: {db_id_formats.get('uuid_format', 0)}, ObjectId: {db_id_formats.get('objectid_format', 0)}")
            print(f"   API      - UUID: {api_id_formats.get('uuid_format', 0)}, ObjectId: {api_id_formats.get('objectid_format', 0)}")
            
            # Check for mismatches
            mismatches = []
            
            if db_id_formats.get('objectid_format', 0) > 0 and api_id_formats.get('uuid_format', 0) > 0:
                mismatches.append("Database has ObjectIds but API returns UUIDs")
            
            if db_id_formats.get('uuid_format', 0) > 0 and api_id_formats.get('objectid_format', 0) > 0:
                mismatches.append("Database has UUIDs but API returns ObjectIds")
            
            # Check field consistency
            has_id_field = db_data.get('has_id_field', False)
            has_underscore_id = db_data.get('has_underscore_id', False)
            
            field_issues = []
            if has_id_field and has_underscore_id:
                field_issues.append("Articles have both 'id' and '_id' fields")
            elif not has_id_field and not has_underscore_id:
                field_issues.append("Articles missing both 'id' and '_id' fields")
            
            all_issues = mismatches + field_issues
            
            if all_issues:
                self.log_test("ID Format Compatibility", False, f"Issues found: {'; '.join(all_issues)}")
                return False
            else:
                self.log_test("ID Format Compatibility", True, "ID formats consistent between database and API")
                return True
            
        except Exception as e:
            self.log_test("ID Format Compatibility", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all content library save functionality tests"""
        print("🎯 CONTENT LIBRARY SAVE FUNCTIONALITY TESTING")
        print("=" * 80)
        print("Testing specific save functionality issues:")
        print("1. New Article Creation (POST /api/content-library)")
        print("2. Existing Article Editing (PUT /api/content-library/{article_id})")
        print("3. Database Investigation (ID format mismatches)")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Database Investigation
        print("🔍 TEST 1: DATABASE INVESTIGATION")
        db_data = self.test_database_investigation()
        print()
        
        # Test 2: Get Existing Articles
        print("📋 TEST 2: GET EXISTING ARTICLES")
        api_data = self.test_get_existing_articles()
        print()
        
        # Test 3: ID Format Compatibility
        print("🔄 TEST 3: ID FORMAT COMPATIBILITY")
        self.test_id_format_compatibility(db_data, api_data)
        print()
        
        # Test 4: New Article Creation
        print("📝 TEST 4: NEW ARTICLE CREATION")
        creation_data = self.test_new_article_creation()
        print()
        
        # Test 5: Existing Article Editing
        print("✏️ TEST 5: EXISTING ARTICLE EDITING")
        if api_data:
            editing_data = self.test_existing_article_editing(api_data)
        else:
            self.log_test("Existing Article Editing", False, "No API data available for testing")
            editing_data = None
        print()
        
        # Print summary
        print("=" * 80)
        print("🎯 CONTENT LIBRARY SAVE FUNCTIONALITY TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed analysis
        print("🔍 DETAILED FINDINGS:")
        
        if db_data:
            print(f"📊 Database: {db_data.get('total_articles', 0)} articles found")
            id_formats = db_data.get('id_formats', {})
            print(f"   ID Formats - UUID: {id_formats.get('uuid_format', 0)}, ObjectId: {id_formats.get('objectid_format', 0)}")
        
        if api_data:
            print(f"📋 API: {len(api_data.get('articles', []))} articles retrieved")
            api_id_formats = api_data.get('api_id_formats', {})
            print(f"   ID Formats - UUID: {api_id_formats.get('uuid_format', 0)}, ObjectId: {api_id_formats.get('objectid_format', 0)}")
        
        if creation_data:
            print(f"📝 Creation: Article created with ID {creation_data.get('created_id')}")
            print(f"   Status: {creation_data.get('verification_status')}")
        
        if editing_data:
            successful = len(editing_data.get('successful_updates', []))
            failed_404 = len(editing_data.get('failed_404', []))
            total_tested = len(editing_data.get('test_results', []))
            print(f"✏️ Editing: {successful}/{total_tested} successful, {failed_404} returned 404 errors")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Close MongoDB connection
        if self.mongo_client:
            self.mongo_client.close()
        
        return success_rate

if __name__ == "__main__":
    tester = ContentLibrarySaveTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)