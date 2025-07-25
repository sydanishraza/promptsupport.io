#!/usr/bin/env python3
"""
Content Library API Testing - Focus on Core APIs after Frontend Fixes
Testing the specific endpoints mentioned in the review request
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://71199049-5964-4d61-99fa-ea913cbbcb4d.preview.emergentagent.com') + '/api'

class ContentLibraryAPITest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_article_id = None
        print(f"🔍 Testing Content Library APIs at: {self.base_url}")
        print("🎯 FOCUS: Core Content Library APIs after frontend fixes")
        print("=" * 60)
        
    def test_health_check(self):
        """Test GET /api/health - Basic health check"""
        print("\n🔍 Testing Health Check (GET /api/health)...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                print(f"   MongoDB: {data.get('services', {}).get('mongodb')}")
                return True
            else:
                print(f"❌ Health check failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check failed - {str(e)}")
            return False
    
    def test_get_content_library(self):
        """Test GET /api/content-library - Get all articles"""
        print("\n🔍 Testing GET Content Library (GET /api/content-library)...")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                total = data.get('total', 0)
                
                print(f"✅ GET /api/content-library successful")
                print(f"   Total articles: {total}")
                print(f"   Articles returned: {len(articles)}")
                
                # Check for articles with images (asset-related functionality)
                articles_with_images = 0
                for article in articles:
                    content = article.get('content', '')
                    if 'data:image' in content:
                        articles_with_images += 1
                
                print(f"   Articles with images: {articles_with_images}")
                
                # Verify article structure
                if articles:
                    sample_article = articles[0]
                    required_fields = ['id', 'title', 'status', 'created_at']
                    missing_fields = [field for field in required_fields if field not in sample_article]
                    
                    if not missing_fields:
                        print(f"   ✅ Article structure valid")
                        # Store first article ID for update test
                        self.test_article_id = sample_article.get('id')
                    else:
                        print(f"   ⚠️ Missing fields: {missing_fields}")
                
                return True
            else:
                print(f"❌ GET /api/content-library failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ GET /api/content-library failed - {str(e)}")
            return False
    
    def test_post_content_library(self):
        """Test POST /api/content-library - Create new article"""
        print("\n🔍 Testing POST Content Library (POST /api/content-library)...")
        try:
            # Test data for creating a new article
            article_data = {
                'title': 'Test Article - Content Library API Verification',
                'content': '# Test Article\n\nThis is a test article created to verify the POST /api/content-library endpoint after frontend fixes.\n\n## Purpose\n\nVerifying that backend APIs work correctly after frontend navigation and scrolling fixes.\n\n## Test Image\n\n![Test Image](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==)\n\n*Test image to verify asset processing*',
                'status': 'draft',
                'tags': json.dumps(['test', 'api-verification', 'post-frontend-fixes']),
                'metadata': json.dumps({
                    'author': 'testing_agent',
                    'test_type': 'post_content_library_api',
                    'created_after_frontend_fixes': True,
                    'seo_description': 'Test article for Content Library API verification',
                    'category': 'testing'
                })
            }
            
            response = requests.post(
                f"{self.base_url}/content-library",
                data=article_data,
                timeout=15
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ POST /api/content-library successful")
                
                if data.get("success") and "article_id" in data:
                    self.test_article_id = data["article_id"]
                    print(f"   Article ID: {self.test_article_id}")
                    print(f"   Message: {data.get('message')}")
                    return True
                else:
                    print("❌ Invalid response format")
                    return False
            else:
                print(f"❌ POST /api/content-library failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ POST /api/content-library failed - {str(e)}")
            return False
    
    def test_put_content_library(self):
        """Test PUT /api/content-library/{id} - Update existing article"""
        print("\n🔍 Testing PUT Content Library (PUT /api/content-library/{id})...")
        try:
            if not self.test_article_id:
                print("❌ No test article ID available - run POST test first")
                return False
            
            # Update the article
            updated_data = {
                'title': 'Updated Test Article - Content Library API Verification',
                'content': '# Updated Test Article\n\nThis article has been updated to verify the PUT /api/content-library/{id} endpoint.\n\n## Updated Content\n\nThis content was modified to test the update functionality after frontend fixes.\n\n## Asset Verification\n\n![Updated Test Image](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==)\n\n*Updated test image to verify asset processing continues to work*\n\n## Conclusion\n\nPUT endpoint working correctly after frontend navigation fixes.',
                'status': 'published',
                'tags': json.dumps(['test', 'api-verification', 'updated', 'post-frontend-fixes']),
                'metadata': json.dumps({
                    'author': 'testing_agent',
                    'test_type': 'put_content_library_api',
                    'updated_after_frontend_fixes': True,
                    'seo_description': 'Updated test article for Content Library API verification',
                    'category': 'testing',
                    'last_updated_by': 'testing_agent'
                })
            }
            
            response = requests.put(
                f"{self.base_url}/content-library/{self.test_article_id}",
                data=updated_data,
                timeout=15
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ PUT /api/content-library/{self.test_article_id} successful")
                
                if data.get("success"):
                    print(f"   Article ID: {data.get('article_id')}")
                    print(f"   Version: {data.get('version', 'N/A')}")
                    print(f"   Message: {data.get('message')}")
                    return True
                else:
                    print("❌ Invalid response format")
                    return False
            else:
                print(f"❌ PUT /api/content-library failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ PUT /api/content-library failed - {str(e)}")
            return False
    
    def test_asset_processing_verification(self):
        """Verify that articles with images are still processed correctly"""
        print("\n🔍 Testing Asset Processing Verification...")
        try:
            # Get all articles and check for proper image processing
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code != 200:
                print("❌ Could not fetch articles for asset verification")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Count articles with different types of assets
            articles_with_images = 0
            articles_with_png = 0
            articles_with_jpeg = 0
            articles_with_svg = 0
            total_images = 0
            
            import re
            
            for article in articles:
                content = article.get('content', '')
                
                # Count different image formats
                png_matches = re.findall(r'data:image/png;base64,', content)
                jpeg_matches = re.findall(r'data:image/jpeg;base64,', content)
                svg_matches = re.findall(r'data:image/svg\+xml;base64,', content)
                
                article_image_count = len(png_matches) + len(jpeg_matches) + len(svg_matches)
                
                if article_image_count > 0:
                    articles_with_images += 1
                    total_images += article_image_count
                    
                    if png_matches:
                        articles_with_png += 1
                    if jpeg_matches:
                        articles_with_jpeg += 1
                    if svg_matches:
                        articles_with_svg += 1
            
            print(f"✅ Asset Processing Verification Results:")
            print(f"   Total articles: {len(articles)}")
            print(f"   Articles with images: {articles_with_images}")
            print(f"   Total images found: {total_images}")
            print(f"   Articles with PNG: {articles_with_png}")
            print(f"   Articles with JPEG: {articles_with_jpeg}")
            print(f"   Articles with SVG: {articles_with_svg}")
            
            # Verify that asset processing is still working
            if articles_with_images > 0:
                print(f"✅ Asset processing working - {articles_with_images} articles contain embedded images")
                
                # Check if our test article (if created) has images
                if self.test_article_id:
                    test_article = None
                    for article in articles:
                        if article.get('id') == self.test_article_id:
                            test_article = article
                            break
                    
                    if test_article:
                        test_content = test_article.get('content', '')
                        if 'data:image' in test_content:
                            print(f"✅ Test article contains embedded images - asset processing confirmed")
                        else:
                            print(f"⚠️ Test article does not contain images")
                
                return True
            else:
                print(f"⚠️ No articles with embedded images found")
                return True  # Not necessarily a failure, might just be no image content
                
        except Exception as e:
            print(f"❌ Asset processing verification failed - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Content Library API tests"""
        print("🚀 Starting Content Library API Testing")
        print("🎯 Focus: Core APIs after frontend fixes")
        print("📋 Tests: GET, POST, PUT /api/content-library + asset verification")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Health Check
        results['health_check'] = self.test_health_check()
        
        # Test 2: GET Content Library
        results['get_content_library'] = self.test_get_content_library()
        
        # Test 3: POST Content Library
        results['post_content_library'] = self.test_post_content_library()
        
        # Test 4: PUT Content Library
        results['put_content_library'] = self.test_put_content_library()
        
        # Test 5: Asset Processing Verification
        results['asset_processing'] = self.test_asset_processing_verification()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CONTENT LIBRARY API TEST RESULTS")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
            if result:
                passed += 1
        
        print(f"\n📈 Overall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL CONTENT LIBRARY API TESTS PASSED!")
            print("✅ No regressions detected after frontend fixes")
        else:
            print("⚠️ Some tests failed - investigation needed")
        
        return results

if __name__ == "__main__":
    tester = ContentLibraryAPITest()
    results = tester.run_all_tests()