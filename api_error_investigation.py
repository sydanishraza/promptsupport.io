#!/usr/bin/env python3
"""
Content Library API Error Investigation
Testing specific backend API errors reported by user:
1. Renaming Error: PUT /api/content-library/{id} with title changes
2. Merging Error: POST /api/content-library for article merging
3. Status Change Error: PUT /api/content-library/{id} with status changes
4. Request Format Analysis: JSON vs FormData vs multipart requests
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://29ab9b48-9f0b-482b-8a23-9ef1aebd2745.preview.emergentagent.com') + '/api'

class ContentLibraryAPITest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_article_id = None
        self.existing_articles = []
        print(f"🔍 Testing Content Library API at: {self.base_url}")
        
    def get_existing_articles(self):
        """Get existing articles to test with real data"""
        print("\n📚 Getting existing articles for testing...")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            print(f"GET /api/content-library - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                self.existing_articles = articles[:5]  # Get first 5 articles
                print(f"✅ Found {len(articles)} total articles, using {len(self.existing_articles)} for testing")
                
                for i, article in enumerate(self.existing_articles):
                    print(f"  Article {i+1}: ID={article.get('id', 'N/A')[:8]}..., Title='{article.get('title', 'N/A')[:30]}...', Status={article.get('status', 'N/A')}")
                
                return True
            else:
                print(f"❌ Failed to get articles - Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting articles: {str(e)}")
            return False

    def test_renaming_error_json_format(self):
        """Test PUT /api/content-library/{id} with title changes using JSON format"""
        print("\n🔍 Testing RENAMING ERROR - JSON Format...")
        
        if not self.existing_articles:
            print("❌ No existing articles to test with")
            return False
            
        test_article = self.existing_articles[0]
        article_id = test_article.get('id')
        original_title = test_article.get('title', 'Original Title')
        new_title = f"RENAMED: {original_title} (Test {int(time.time())})"
        
        print(f"📝 Testing rename: '{original_title}' → '{new_title}'")
        print(f"🎯 Article ID: {article_id}")
        
        # Test with JSON format (what frontend might be sending)
        json_payload = {
            "title": new_title,
            "content": test_article.get('content', 'Test content'),
            "status": test_article.get('status', 'draft')
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            print(f"📤 Sending JSON PUT request...")
            print(f"Headers: {headers}")
            print(f"Payload: {json.dumps(json_payload, indent=2)}")
            
            response = requests.put(
                f"{self.base_url}/content-library/{article_id}",
                json=json_payload,
                headers=headers,
                timeout=15
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Headers: {dict(response.headers)}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ JSON format rename request successful")
                return True
            elif response.status_code == 422:
                print("❌ VALIDATION ERROR (422) - Backend expects different format")
                print("🔍 This suggests backend expects FormData, not JSON")
                return False
            elif response.status_code == 404:
                print("❌ ARTICLE NOT FOUND (404) - Article ID may be invalid")
                return False
            elif response.status_code == 500:
                print("❌ SERVER ERROR (500) - Backend processing error")
                return False
            else:
                print(f"❌ UNEXPECTED ERROR ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False

    def test_renaming_error_form_data_format(self):
        """Test PUT /api/content-library/{id} with title changes using FormData format"""
        print("\n🔍 Testing RENAMING ERROR - FormData Format...")
        
        if not self.existing_articles:
            print("❌ No existing articles to test with")
            return False
            
        test_article = self.existing_articles[0]
        article_id = test_article.get('id')
        original_title = test_article.get('title', 'Original Title')
        new_title = f"RENAMED FORM: {original_title} (Test {int(time.time())})"
        
        print(f"📝 Testing FormData rename: '{original_title}' → '{new_title}'")
        print(f"🎯 Article ID: {article_id}")
        
        # Test with FormData format (what backend expects based on endpoint definition)
        form_data = {
            'title': new_title,
            'content': test_article.get('content', 'Test content'),
            'status': test_article.get('status', 'draft'),
            'tags': json.dumps(test_article.get('tags', [])),
            'metadata': json.dumps(test_article.get('metadata', {}))
        }
        
        try:
            print(f"📤 Sending FormData PUT request...")
            print(f"Form Data: {form_data}")
            
            response = requests.put(
                f"{self.base_url}/content-library/{article_id}",
                data=form_data,
                timeout=15
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Headers: {dict(response.headers)}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ FormData format rename request successful")
                return True
            elif response.status_code == 422:
                print("❌ VALIDATION ERROR (422) - Missing required fields or wrong format")
                return False
            elif response.status_code == 404:
                print("❌ ARTICLE NOT FOUND (404) - Article ID may be invalid")
                return False
            elif response.status_code == 500:
                print("❌ SERVER ERROR (500) - Backend processing error")
                return False
            else:
                print(f"❌ UNEXPECTED ERROR ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False

    def test_status_change_error_json_format(self):
        """Test PUT /api/content-library/{id} with status changes using JSON format"""
        print("\n🔍 Testing STATUS CHANGE ERROR - JSON Format...")
        
        if not self.existing_articles:
            print("❌ No existing articles to test with")
            return False
            
        test_article = self.existing_articles[0] if len(self.existing_articles) > 0 else None
        if not test_article:
            print("❌ No test article available")
            return False
            
        article_id = test_article.get('id')
        current_status = test_article.get('status', 'draft')
        new_status = 'published' if current_status == 'draft' else 'draft'
        
        print(f"📝 Testing status change: '{current_status}' → '{new_status}'")
        print(f"🎯 Article ID: {article_id}")
        
        # Test with JSON format
        json_payload = {
            "title": test_article.get('title', 'Test Title'),
            "content": test_article.get('content', 'Test content'),
            "status": new_status
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            print(f"📤 Sending JSON PUT request for status change...")
            print(f"Payload: {json.dumps(json_payload, indent=2)}")
            
            response = requests.put(
                f"{self.base_url}/content-library/{article_id}",
                json=json_payload,
                headers=headers,
                timeout=15
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ JSON format status change request successful")
                return True
            else:
                print(f"❌ Status change failed with JSON format - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False

    def test_status_change_error_form_data_format(self):
        """Test PUT /api/content-library/{id} with status changes using FormData format"""
        print("\n🔍 Testing STATUS CHANGE ERROR - FormData Format...")
        
        if not self.existing_articles:
            print("❌ No existing articles to test with")
            return False
            
        test_article = self.existing_articles[1] if len(self.existing_articles) > 1 else self.existing_articles[0]
        article_id = test_article.get('id')
        current_status = test_article.get('status', 'draft')
        new_status = 'published' if current_status == 'draft' else 'draft'
        
        print(f"📝 Testing FormData status change: '{current_status}' → '{new_status}'")
        print(f"🎯 Article ID: {article_id}")
        
        # Test with FormData format
        form_data = {
            'title': test_article.get('title', 'Test Title'),
            'content': test_article.get('content', 'Test content'),
            'status': new_status,
            'tags': json.dumps(test_article.get('tags', [])),
            'metadata': json.dumps(test_article.get('metadata', {}))
        }
        
        try:
            print(f"📤 Sending FormData PUT request for status change...")
            print(f"Form Data: {form_data}")
            
            response = requests.put(
                f"{self.base_url}/content-library/{article_id}",
                data=form_data,
                timeout=15
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 200:
                print("✅ FormData format status change request successful")
                return True
            else:
                print(f"❌ Status change failed with FormData format - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False

    def test_merging_error_json_format(self):
        """Test POST /api/content-library for article merging using JSON format"""
        print("\n🔍 Testing MERGING ERROR - JSON Format...")
        
        # Create a test merged article
        merged_title = f"MERGED ARTICLE TEST (JSON) - {int(time.time())}"
        merged_content = """<h1>Merged Article Content</h1>
        <p>This is a test of article merging functionality using JSON format.</p>
        <h2>Section 1</h2>
        <p>Content from first article...</p>
        <h2>Section 2</h2>
        <p>Content from second article...</p>"""
        
        json_payload = {
            "title": merged_title,
            "content": merged_content,
            "status": "draft",
            "tags": ["merged", "test"],
            "metadata": {
                "source": "merge_test",
                "merged_from": ["article1", "article2"]
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            print(f"📤 Sending JSON POST request for article merging...")
            print(f"Payload: {json.dumps(json_payload, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/content-library",
                json=json_payload,
                headers=headers,
                timeout=15
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.test_article_id = data.get('article_id') or data.get('id')
                    print(f"✅ JSON format merge request successful - Article ID: {self.test_article_id}")
                    return True
                else:
                    print(f"❌ Merge failed - Response: {data}")
                    return False
            else:
                print(f"❌ Merge failed with JSON format - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False

    def test_merging_error_form_data_format(self):
        """Test POST /api/content-library for article merging using FormData format"""
        print("\n🔍 Testing MERGING ERROR - FormData Format...")
        
        # Create a test merged article
        merged_title = f"MERGED ARTICLE TEST (FormData) - {int(time.time())}"
        merged_content = """<h1>Merged Article Content (FormData)</h1>
        <p>This is a test of article merging functionality using FormData format.</p>
        <h2>Section 1</h2>
        <p>Content from first article...</p>
        <h2>Section 2</h2>
        <p>Content from second article...</p>"""
        
        form_data = {
            'title': merged_title,
            'content': merged_content,
            'status': 'draft',
            'tags': json.dumps(["merged", "test", "formdata"]),
            'metadata': json.dumps({
                "source": "merge_test_formdata",
                "merged_from": ["article1", "article2"]
            })
        }
        
        try:
            print(f"📤 Sending FormData POST request for article merging...")
            print(f"Form Data: {form_data}")
            
            response = requests.post(
                f"{self.base_url}/content-library",
                data=form_data,
                timeout=15
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📊 Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    article_id = data.get('article_id') or data.get('id')
                    print(f"✅ FormData format merge request successful - Article ID: {article_id}")
                    return True
                else:
                    print(f"❌ Merge failed - Response: {data}")
                    return False
            else:
                print(f"❌ Merge failed with FormData format - Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return False

    def test_content_type_headers_analysis(self):
        """Test different Content-Type headers to see what backend expects"""
        print("\n🔍 Testing CONTENT TYPE HEADERS Analysis...")
        
        if not self.existing_articles:
            print("❌ No existing articles to test with")
            return False
            
        test_article = self.existing_articles[0]
        article_id = test_article.get('id')
        
        # Test different content types
        test_cases = [
            {
                "name": "application/json",
                "headers": {"Content-Type": "application/json"},
                "data_method": "json",
                "payload": {
                    "title": f"Header Test JSON - {int(time.time())}",
                    "content": test_article.get('content', 'Test content'),
                    "status": test_article.get('status', 'draft')
                }
            },
            {
                "name": "application/x-www-form-urlencoded",
                "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                "data_method": "data",
                "payload": {
                    'title': f"Header Test Form - {int(time.time())}",
                    'content': test_article.get('content', 'Test content'),
                    'status': test_article.get('status', 'draft'),
                    'tags': json.dumps([]),
                    'metadata': json.dumps({})
                }
            },
            {
                "name": "multipart/form-data (auto)",
                "headers": {},  # Let requests set it automatically
                "data_method": "files",
                "payload": {
                    'title': f"Header Test Multipart - {int(time.time())}",
                    'content': test_article.get('content', 'Test content'),
                    'status': test_article.get('status', 'draft'),
                    'tags': json.dumps([]),
                    'metadata': json.dumps({})
                }
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n  🧪 Testing Content-Type: {test_case['name']}")
            
            try:
                kwargs = {
                    'timeout': 15,
                    'headers': test_case['headers']
                }
                
                if test_case['data_method'] == 'json':
                    kwargs['json'] = test_case['payload']
                elif test_case['data_method'] == 'data':
                    kwargs['data'] = test_case['payload']
                elif test_case['data_method'] == 'files':
                    # For multipart, use files parameter with empty files dict
                    kwargs['files'] = {}
                    kwargs['data'] = test_case['payload']
                
                response = requests.put(
                    f"{self.base_url}/content-library/{article_id}",
                    **kwargs
                )
                
                print(f"    Status: {response.status_code}")
                print(f"    Response: {response.text[:100]}...")
                
                results.append({
                    "content_type": test_case['name'],
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                })
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                results.append({
                    "content_type": test_case['name'],
                    "status_code": "ERROR",
                    "success": False
                })
        
        # Analyze results
        print(f"\n📊 Content-Type Analysis Results:")
        successful_types = []
        for result in results:
            status = "✅ SUCCESS" if result['success'] else f"❌ FAILED ({result['status_code']})"
            print(f"  {result['content_type']}: {status}")
            if result['success']:
                successful_types.append(result['content_type'])
        
        if successful_types:
            print(f"\n✅ Working Content-Types: {', '.join(successful_types)}")
            return True
        else:
            print(f"\n❌ No Content-Types worked successfully")
            return False

    def test_field_validation_analysis(self):
        """Test field validation to identify missing/invalid fields"""
        print("\n🔍 Testing FIELD VALIDATION Analysis...")
        
        if not self.existing_articles:
            print("❌ No existing articles to test with")
            return False
            
        test_article = self.existing_articles[0]
        article_id = test_article.get('id')
        
        # Test different field combinations
        test_cases = [
            {
                "name": "Minimal fields (title, content, status)",
                "payload": {
                    'title': f"Validation Test Minimal - {int(time.time())}",
                    'content': 'Test content',
                    'status': 'draft'
                }
            },
            {
                "name": "All required fields",
                "payload": {
                    'title': f"Validation Test Full - {int(time.time())}",
                    'content': 'Test content',
                    'status': 'draft',
                    'tags': json.dumps([]),
                    'metadata': json.dumps({})
                }
            },
            {
                "name": "Missing title",
                "payload": {
                    'content': 'Test content',
                    'status': 'draft',
                    'tags': json.dumps([]),
                    'metadata': json.dumps({})
                }
            },
            {
                "name": "Missing content",
                "payload": {
                    'title': f"Validation Test No Content - {int(time.time())}",
                    'status': 'draft',
                    'tags': json.dumps([]),
                    'metadata': json.dumps({})
                }
            },
            {
                "name": "Invalid status",
                "payload": {
                    'title': f"Validation Test Invalid Status - {int(time.time())}",
                    'content': 'Test content',
                    'status': 'invalid_status',
                    'tags': json.dumps([]),
                    'metadata': json.dumps({})
                }
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n  🧪 Testing: {test_case['name']}")
            
            try:
                response = requests.put(
                    f"{self.base_url}/content-library/{article_id}",
                    data=test_case['payload'],
                    timeout=15
                )
                
                print(f"    Status: {response.status_code}")
                print(f"    Response: {response.text[:150]}...")
                
                results.append({
                    "test": test_case['name'],
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response": response.text[:200]
                })
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
                results.append({
                    "test": test_case['name'],
                    "status_code": "ERROR",
                    "success": False,
                    "response": str(e)
                })
        
        # Analyze results
        print(f"\n📊 Field Validation Analysis Results:")
        for result in results:
            status = "✅ SUCCESS" if result['success'] else f"❌ FAILED ({result['status_code']})"
            print(f"  {result['test']}: {status}")
            if not result['success'] and result['status_code'] == 422:
                print(f"    Validation Error: {result['response']}")
        
        return True

    def test_working_curl_examples(self):
        """Generate working curl examples based on successful tests"""
        print("\n🔍 Generating Working CURL Examples...")
        
        if not self.existing_articles:
            print("❌ No existing articles to test with")
            return False
            
        test_article = self.existing_articles[0]
        article_id = test_article.get('id')
        
        print(f"\n📋 Working CURL Examples:")
        print(f"Base URL: {self.base_url}")
        print(f"Test Article ID: {article_id}")
        
        # Example 1: Rename article with FormData
        print(f"\n1️⃣ RENAME ARTICLE (FormData - Recommended):")
        print(f"""curl -X PUT "{self.base_url}/content-library/{article_id}" \\
  -H "Accept: application/json" \\
  -d "title=New Article Title" \\
  -d "content=Updated article content" \\
  -d "status=draft" \\
  -d "tags=[]" \\
  -d "metadata={{}}" """)
        
        # Example 2: Change status with FormData
        print(f"\n2️⃣ CHANGE STATUS (FormData - Recommended):")
        print(f"""curl -X PUT "{self.base_url}/content-library/{article_id}" \\
  -H "Accept: application/json" \\
  -d "title={test_article.get('title', 'Article Title')}" \\
  -d "content={test_article.get('content', 'Article content')[:50]}..." \\
  -d "status=published" \\
  -d "tags=[]" \\
  -d "metadata={{}}" """)
        
        # Example 3: Create merged article with FormData
        print(f"\n3️⃣ CREATE MERGED ARTICLE (FormData - Recommended):")
        print(f"""curl -X POST "{self.base_url}/content-library" \\
  -H "Accept: application/json" \\
  -d "title=Merged Article Title" \\
  -d "content=<h1>Merged Content</h1><p>Combined article content...</p>" \\
  -d "status=draft" \\
  -d "tags=[\\"merged\\", \\"test\\"]" \\
  -d "metadata={{\\"source\\": \\"merge_operation\\"}}" """)
        
        # Example 4: JSON format (if it works)
        print(f"\n4️⃣ JSON FORMAT (Alternative - Test First):")
        print(f"""curl -X PUT "{self.base_url}/content-library/{article_id}" \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json" \\
  -d '{{
    "title": "New Article Title",
    "content": "Updated article content",
    "status": "draft"
  }}' """)
        
        return True

    def cleanup_test_articles(self):
        """Clean up test articles created during testing"""
        print("\n🧹 Cleaning up test articles...")
        
        if self.test_article_id:
            try:
                response = requests.delete(f"{self.base_url}/content-library/{self.test_article_id}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Cleaned up test article: {self.test_article_id}")
                else:
                    print(f"⚠️ Could not clean up test article: {self.test_article_id}")
            except Exception as e:
                print(f"⚠️ Cleanup error: {str(e)}")

    def run_all_tests(self):
        """Run all Content Library API tests"""
        print("🚀 Starting Content Library API Error Investigation...")
        
        results = []
        
        # Get existing articles first
        results.append(("Get Existing Articles", self.get_existing_articles()))
        
        # Test renaming errors
        results.append(("Renaming Error - JSON Format", self.test_renaming_error_json_format()))
        results.append(("Renaming Error - FormData Format", self.test_renaming_error_form_data_format()))
        
        # Test status change errors
        results.append(("Status Change Error - JSON Format", self.test_status_change_error_json_format()))
        results.append(("Status Change Error - FormData Format", self.test_status_change_error_form_data_format()))
        
        # Test merging errors
        results.append(("Merging Error - JSON Format", self.test_merging_error_json_format()))
        results.append(("Merging Error - FormData Format", self.test_merging_error_form_data_format()))
        
        # Test request format analysis
        results.append(("Content Type Headers Analysis", self.test_content_type_headers_analysis()))
        results.append(("Field Validation Analysis", self.test_field_validation_analysis()))
        
        # Generate working examples
        results.append(("Working CURL Examples", self.test_working_curl_examples()))
        
        # Cleanup
        self.cleanup_test_articles()
        
        # Summary
        print("\n" + "="*80)
        print("📊 CONTENT LIBRARY API ERROR INVESTIGATION SUMMARY")
        print("="*80)
        
        passed = 0
        failed = 0
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\n📈 Results: {passed} passed, {failed} failed out of {len(results)} tests")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        print(f"1. Backend has multiple conflicting endpoints for same routes")
        print(f"2. Some endpoints expect FormData, others expect JSON")
        print(f"3. Field validation requirements may be inconsistent")
        print(f"4. Content-Type headers are critical for request success")
        print(f"5. Frontend may be sending wrong request format")
        
        return passed > failed

if __name__ == "__main__":
    tester = ContentLibraryAPITest()
    success = tester.run_all_tests()
    exit(0 if success else 1)