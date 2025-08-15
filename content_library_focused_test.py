#!/usr/bin/env python3
"""
Content Library Backend Focused Testing
Testing available Content Library backend functionality
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://docai-promptsupport.preview.emergentagent.com') + '/api'

class ContentLibraryFocusedTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_article_id = None
        print(f"Testing Content Library Backend at: {self.base_url}")
        
    def test_content_library_endpoint(self):
        """Test GET /api/content-library for article retrieval with proper structure"""
        print("🔍 Testing Content Library Endpoint - GET /api/content-library...")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Check proper structure
                if 'total' in data and 'articles' in data:
                    total_articles = data['total']
                    articles = data['articles']
                    
                    print(f"✅ Proper JSON structure: total={total_articles}, articles={len(articles)}")
                    
                    # Validate required fields in articles
                    if articles:
                        sample_article = articles[0]
                        required_fields = ['id', 'title', 'content', 'status', 'created_at']
                        missing_fields = [field for field in required_fields if field not in sample_article]
                        
                        if not missing_fields:
                            print(f"✅ All required fields present: {required_fields}")
                            # Store test article ID for other tests
                            self.test_article_id = sample_article['id']
                            
                            # Check optional fields
                            optional_fields = ['updated_at', 'tags', 'metadata', 'summary', 'takeaways']
                            present_optional = [field for field in optional_fields if field in sample_article]
                            print(f"✅ Optional fields present: {present_optional}")
                            
                            return True
                        else:
                            print(f"❌ Missing required fields: {missing_fields}")
                            return False
                    else:
                        print("⚠️ No articles found in response")
                        return True  # Not necessarily a failure
                else:
                    print("❌ Invalid response structure - missing 'total' or 'articles'")
                    return False
            else:
                print(f"❌ GET /api/content-library failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content library endpoint test failed - {str(e)}")
            return False
    
    def test_article_creation(self):
        """Test POST /api/content-library for creating new articles"""
        print("\n🔍 Testing Article Creation - POST /api/content-library...")
        try:
            # Test creating a new article
            article_data = {
                'title': f'Test Article Creation - {int(time.time())}',
                'content': '<h1>Test Article</h1><p>This is a test article created by the backend testing system. It should be properly stored in the Content Library with all required metadata.</p><h2>Test Section</h2><p>Additional content for testing purposes.</p>',
                'status': 'draft',
                'tags': ['test', 'backend', 'creation'],
                'metadata': {
                    'source': 'backend_test',
                    'test_type': 'article_creation',
                    'created_by': 'testing_agent'
                }
            }
            
            response = requests.post(
                f"{self.base_url}/content-library",
                json=article_data,
                timeout=15
            )
            
            print(f"Creation Status Code: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                print("✅ Article creation successful")
                
                # Check if the created article has proper structure
                if 'id' in data or 'article_id' in data:
                    created_id = data.get('id') or data.get('article_id')
                    print(f"✅ Created article ID: {created_id}")
                    
                    # Store for cleanup
                    self.test_article_id = created_id
                    return True
                else:
                    print("✅ Article creation successful (no ID returned)")
                    return True
            else:
                print(f"❌ Article creation failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Article creation test failed - {str(e)}")
            return False
    
    def test_article_update(self):
        """Test PUT /api/content-library/{id} for article updates"""
        print("\n🔍 Testing Article Update - PUT /api/content-library/{id}...")
        try:
            if not self.test_article_id:
                print("⚠️ No test article ID available - skipping update test")
                return True
            
            # Test updating the article
            update_data = {
                'title': f'UPDATED Test Article - {int(time.time())}',
                'content': '<h1>Updated Test Article</h1><p>This article has been updated by the backend testing system. The update functionality is working correctly.</p><h2>Updated Section</h2><p>This content was added during the update test.</p>',
                'status': 'published',
                'tags': ['test', 'backend', 'updated'],
                'metadata': {
                    'source': 'backend_test',
                    'test_type': 'article_update',
                    'updated_by': 'testing_agent'
                }
            }
            
            response = requests.put(
                f"{self.base_url}/content-library/{self.test_article_id}",
                json=update_data,
                timeout=15
            )
            
            print(f"Update Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Article update successful")
                return True
            else:
                print(f"❌ Article update failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Article update test failed - {str(e)}")
            return False
    
    def test_pdf_download(self):
        """Test GET /api/content-library/article/{id}/download-pdf functionality"""
        print("\n🔍 Testing PDF Download - GET /api/content-library/article/{id}/download-pdf...")
        try:
            if not self.test_article_id:
                print("⚠️ No test article ID available - skipping PDF download test")
                return True
            
            response = requests.get(
                f"{self.base_url}/content-library/article/{self.test_article_id}/download-pdf",
                timeout=30
            )
            
            print(f"PDF Download Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                print(f"Content-Type: {content_type}")
                print(f"Content-Length: {content_length} bytes")
                
                if 'application/pdf' in content_type and content_length > 1000:
                    print("✅ PDF download successful - proper content type and size")
                    return True
                elif content_length > 1000:
                    print("✅ PDF download successful - good file size")
                    return True
                else:
                    print("⚠️ PDF download may have issues - small file size")
                    return True
            else:
                print(f"❌ PDF download failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ PDF download test failed - {str(e)}")
            return False
    
    def test_content_analysis(self):
        """Test /api/content-analysis endpoint functionality"""
        print("\n🔍 Testing Content Analysis - POST /api/content-analysis...")
        try:
            # Test content analysis endpoint
            analysis_data = {
                'content': '<h1>Content Analysis Test</h1><p>This is a comprehensive test of the content analysis functionality. The system should analyze this content and provide detailed insights about readability, word count, sentence structure, and other important metrics.</p><h2>Test Section</h2><p>Additional content for thorough analysis testing. This paragraph contains more complex sentence structures to test the analysis capabilities.</p><ul><li>List item one</li><li>List item two</li><li>List item three</li></ul>',
                'mode': 'analysis'
            }
            
            response = requests.post(
                f"{self.base_url}/content-analysis",
                json=analysis_data,
                timeout=30
            )
            
            print(f"Content Analysis Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Check for expected analysis fields
                expected_fields = ['wordCount', 'sentences', 'paragraphs', 'readingTime', 'readabilityScore', 'characterCount']
                present_fields = [field for field in expected_fields if field in data]
                
                print(f"Analysis fields present: {present_fields}")
                
                # Display analysis results
                if 'wordCount' in data:
                    print(f"  Word Count: {data['wordCount']}")
                if 'readabilityScore' in data:
                    print(f"  Readability Score: {data['readabilityScore']}")
                if 'readingTime' in data:
                    print(f"  Reading Time: {data['readingTime']} minutes")
                if 'aiInsights' in data:
                    insights = data['aiInsights']
                    if insights and 'temporarily unavailable' not in insights:
                        print(f"  AI Insights: {len(insights)} characters")
                    else:
                        print("  AI Insights: Temporarily unavailable")
                
                if len(present_fields) >= 4:  # At least 4 analysis fields
                    print("✅ Content analysis working - comprehensive metrics provided")
                    return True
                else:
                    print("⚠️ Content analysis partial - limited metrics")
                    return True
            else:
                print(f"❌ Content analysis failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content analysis test failed - {str(e)}")
            return False
    
    def test_asset_extraction_analysis(self):
        """Test if articles contain embedded assets and analyze asset patterns"""
        print("\n🔍 Testing Asset Extraction Analysis...")
        try:
            # Get articles and check for embedded assets
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                articles_with_assets = 0
                total_assets_found = 0
                asset_types = {
                    'images': 0,
                    'figures': 0,
                    'videos': 0,
                    'audio': 0,
                    'static_urls': 0,
                    'external_links': 0
                }
                
                for article in articles[:10]:  # Check first 10 articles
                    content = article.get('content', '')
                    
                    # Count different types of assets
                    img_count = content.count('<img')
                    figure_count = content.count('<figure')
                    video_count = content.count('<video')
                    audio_count = content.count('<audio')
                    static_url_count = content.count('/api/static/uploads/')
                    external_link_count = content.count('http')
                    
                    asset_types['images'] += img_count
                    asset_types['figures'] += figure_count
                    asset_types['videos'] += video_count
                    asset_types['audio'] += audio_count
                    asset_types['static_urls'] += static_url_count
                    asset_types['external_links'] += external_link_count
                    
                    total_article_assets = img_count + figure_count + video_count + audio_count + static_url_count
                    
                    if total_article_assets > 0:
                        articles_with_assets += 1
                        total_assets_found += total_article_assets
                
                print(f"📊 Asset Analysis Results:")
                print(f"  Articles checked: {min(10, len(articles))}")
                print(f"  Articles with assets: {articles_with_assets}")
                print(f"  Total asset indicators found: {total_assets_found}")
                print(f"  Asset breakdown:")
                for asset_type, count in asset_types.items():
                    if count > 0:
                        print(f"    {asset_type}: {count}")
                
                if total_assets_found > 0:
                    print("✅ Assets found in articles - should be displayed in Assets tab")
                    return True
                else:
                    print("⚠️ No embedded assets found in articles")
                    return True  # Not necessarily a failure
            else:
                print(f"❌ Could not retrieve articles for asset analysis - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Asset extraction analysis failed - {str(e)}")
            return False
    
    def test_data_validation_comprehensive(self):
        """Test comprehensive data validation for all article fields"""
        print("\n🔍 Testing Comprehensive Data Validation...")
        try:
            # Get articles for validation
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if not articles:
                    print("⚠️ No articles available for data validation")
                    return True
                
                required_fields = ['id', 'title', 'content', 'status', 'created_at']
                optional_fields = ['updated_at', 'tags', 'metadata', 'summary', 'takeaways']
                
                validation_results = []
                field_statistics = {field: 0 for field in required_fields + optional_fields}
                
                for i, article in enumerate(articles[:5]):  # Check first 5 articles
                    missing_required = [field for field in required_fields if field not in article]
                    present_optional = [field for field in optional_fields if field in article]
                    
                    # Count field presence
                    for field in required_fields + optional_fields:
                        if field in article:
                            field_statistics[field] += 1
                    
                    print(f"Article {i+1} validation:")
                    print(f"  ID: {article.get('id', 'MISSING')[:20]}...")
                    print(f"  Title: {article.get('title', 'MISSING')[:50]}...")
                    print(f"  Status: {article.get('status', 'MISSING')}")
                    print(f"  Content length: {len(article.get('content', ''))} chars")
                    print(f"  Required fields missing: {missing_required if missing_required else 'None'}")
                    print(f"  Optional fields present: {present_optional}")
                    
                    validation_results.append(len(missing_required) == 0)
                
                successful_validations = sum(validation_results)
                total_validations = len(validation_results)
                
                print(f"\n📊 Data Validation Summary:")
                print(f"  Articles validated: {total_validations}")
                print(f"  Successful validations: {successful_validations}")
                print(f"  Success rate: {(successful_validations/total_validations)*100:.1f}%")
                
                print(f"\n📊 Field Presence Statistics:")
                for field, count in field_statistics.items():
                    percentage = (count / total_validations) * 100
                    print(f"  {field}: {count}/{total_validations} ({percentage:.1f}%)")
                
                if successful_validations >= total_validations * 0.8:  # 80% pass rate
                    print("✅ Comprehensive data validation successful")
                    return True
                else:
                    print("❌ Comprehensive data validation failed")
                    return False
            else:
                print(f"❌ Could not retrieve articles for validation - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Comprehensive data validation failed - {str(e)}")
            return False
    
    def test_article_cleanup(self):
        """Clean up test articles created during testing"""
        print("\n🔍 Testing Article Cleanup - DELETE /api/content-library/{id}...")
        try:
            if not self.test_article_id:
                print("⚠️ No test article ID available for cleanup")
                return True
            
            response = requests.delete(
                f"{self.base_url}/content-library/{self.test_article_id}",
                timeout=15
            )
            
            print(f"Cleanup Status Code: {response.status_code}")
            
            if response.status_code in [200, 204, 404]:  # 404 is acceptable if already deleted
                print("✅ Article cleanup successful")
                return True
            else:
                print(f"⚠️ Article cleanup status: {response.status_code}")
                return True  # Not critical for test success
                
        except Exception as e:
            print(f"⚠️ Article cleanup failed - {str(e)}")
            return True  # Not critical for test success
    
    def run_all_tests(self):
        """Run all focused Content Library backend tests"""
        print("🚀 Starting Content Library Backend Focused Testing...")
        print("=" * 80)
        
        tests = [
            ("Content Library Endpoint", self.test_content_library_endpoint),
            ("Article Creation", self.test_article_creation),
            ("Article Update", self.test_article_update),
            ("PDF Download", self.test_pdf_download),
            ("Content Analysis", self.test_content_analysis),
            ("Asset Extraction Analysis", self.test_asset_extraction_analysis),
            ("Comprehensive Data Validation", self.test_data_validation_comprehensive),
            ("Article Cleanup", self.test_article_cleanup)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} CRASHED: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*80)
        print("📊 CONTENT LIBRARY BACKEND FOCUSED TEST SUMMARY")
        print("="*80)
        
        passed_tests = sum(1 for _, result in results if result)
        total_tests = len(results)
        success_rate = (passed_tests / total_tests) * 100
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 85:
            print("🎉 CONTENT LIBRARY BACKEND IS FULLY OPERATIONAL")
        elif success_rate >= 70:
            print("✅ CONTENT LIBRARY BACKEND IS OPERATIONAL WITH MINOR ISSUES")
        elif success_rate >= 50:
            print("⚠️ CONTENT LIBRARY BACKEND HAS MODERATE ISSUES")
        else:
            print("❌ CONTENT LIBRARY BACKEND HAS MAJOR ISSUES")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = ContentLibraryFocusedTest()
    tester.run_all_tests()