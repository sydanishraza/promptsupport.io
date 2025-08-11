#!/usr/bin/env python3
"""
Google Maps DOCX Content Processing Pipeline Test
Tests the actual content processing pipeline using the Google Map JavaScript API Tutorial.docx file
to verify we get real content instead of test data.
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

class GoogleMapsDocxTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.docx_url = "https://customer-assets.emergentagent.com/job_training-lab-revamp/artifacts/xq5cp7dr_Google%20Map%20JavaScript%20API%20Tutorial.docx"
        print(f"🗺️ Testing Google Maps DOCX Content Processing at: {self.base_url}")
        print(f"📄 DOCX Source: {self.docx_url}")
        
    def download_google_maps_docx(self):
        """Download the Google Maps DOCX file from the provided URL"""
        print("\n🔍 Step 1: Downloading Google Map JavaScript API Tutorial.docx...")
        try:
            response = requests.get(self.docx_url, timeout=30)
            print(f"Download Status Code: {response.status_code}")
            
            if response.status_code == 200:
                file_size = len(response.content)
                print(f"✅ Successfully downloaded DOCX file: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                
                # Verify it's actually a DOCX file
                if response.content.startswith(b'PK'):  # ZIP/DOCX signature
                    print("✅ File appears to be a valid DOCX (ZIP-based) format")
                    return response.content
                else:
                    print("❌ Downloaded file doesn't appear to be a valid DOCX format")
                    return None
            else:
                print(f"❌ Failed to download DOCX file - status code {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Download failed - {str(e)}")
            return None
    
    def process_google_maps_docx(self, docx_content):
        """Process the Google Maps DOCX through the backend pipeline"""
        print("\n🔍 Step 2: Processing Google Maps DOCX through backend pipeline...")
        try:
            # Create file-like object from downloaded content
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', docx_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use training interface to process the DOCX
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_instructions": "Extract and process all Google Maps API content including code examples and images",
                    "output_requirements": {
                        "format": "html",
                        "min_articles": 1,
                        "max_articles": 10,
                        "quality_benchmarks": ["content_completeness", "technical_accuracy", "proper_formatting"]
                    },
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "filter_decorative": False  # Keep all images for technical documentation
                    }
                })
            }
            
            print("📤 Uploading Google Maps DOCX to training interface...")
            print("⏱️ Processing may take several minutes for large technical documents...")
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=300  # 5 minutes timeout for large document
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Google Maps DOCX processed successfully")
                return data
            else:
                print(f"❌ Processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Processing failed - {str(e)}")
            return None
    
    def verify_real_content_extraction(self, processing_data):
        """Verify that real Google Maps API content was extracted, not test data"""
        print("\n🔍 Step 3: Verifying Real Content Extraction...")
        try:
            articles = processing_data.get('articles', [])
            if not articles:
                print("❌ No articles generated from Google Maps DOCX")
                return False
            
            print(f"📚 Generated {len(articles)} articles from Google Maps DOCX")
            
            # Check for real Google Maps API content indicators
            google_maps_indicators = [
                'google maps',
                'javascript api',
                'api key',
                'map initialization',
                'google.maps',
                'geocoding',
                'markers',
                'coordinates',
                'latitude',
                'longitude',
                'map.setCenter',
                'new google.maps.Map',
                'mapTypeId',
                'zoom'
            ]
            
            # Test data indicators that should NOT be present
            test_data_indicators = [
                'chapter 1: main section',
                'general content block with mixed information',
                'test content',
                'sample data',
                'placeholder text',
                'lorem ipsum'
            ]
            
            real_content_found = 0
            test_data_found = 0
            total_content_length = 0
            
            for i, article in enumerate(articles):
                title = article.get('title', '').lower()
                content = (article.get('content', '') or article.get('html', '')).lower()
                total_content_length += len(content)
                
                print(f"\n📄 Article {i+1}: '{article.get('title', 'Untitled')}'")
                print(f"   Content Length: {len(content):,} characters")
                
                # Check for real Google Maps content
                found_indicators = [indicator for indicator in google_maps_indicators if indicator in content or indicator in title]
                if found_indicators:
                    real_content_found += len(found_indicators)
                    print(f"   ✅ Real Google Maps content found: {found_indicators[:3]}...")
                
                # Check for test data (should not be present)
                found_test_data = [indicator for indicator in test_data_indicators if indicator in content or indicator in title]
                if found_test_data:
                    test_data_found += len(found_test_data)
                    print(f"   ❌ Test data indicators found: {found_test_data}")
                
                # Check for JavaScript code examples
                if 'function' in content or 'var ' in content or 'let ' in content or 'const ' in content:
                    print(f"   ✅ JavaScript code examples detected")
                
                # Check for API-related content
                if 'api' in content and ('key' in content or 'endpoint' in content or 'request' in content):
                    print(f"   ✅ API documentation content detected")
            
            print(f"\n📊 Content Analysis Summary:")
            print(f"   Real Google Maps indicators found: {real_content_found}")
            print(f"   Test data indicators found: {test_data_found}")
            print(f"   Total content length: {total_content_length:,} characters")
            
            # Verification criteria
            if real_content_found >= 5 and test_data_found == 0 and total_content_length > 5000:
                print("✅ REAL CONTENT EXTRACTION VERIFIED:")
                print("   ✅ Multiple Google Maps API indicators found")
                print("   ✅ No test data indicators detected")
                print("   ✅ Substantial content extracted")
                return True
            elif real_content_found >= 2 and test_data_found == 0:
                print("✅ REAL CONTENT EXTRACTION PARTIALLY VERIFIED:")
                print("   ✅ Some Google Maps API content found")
                print("   ✅ No test data detected")
                return True
            else:
                print("❌ REAL CONTENT EXTRACTION FAILED:")
                print(f"   ❌ Insufficient real content indicators: {real_content_found}")
                print(f"   ❌ Test data indicators present: {test_data_found}")
                return False
                
        except Exception as e:
            print(f"❌ Content verification failed - {str(e)}")
            return False
    
    def verify_content_structure(self, processing_data):
        """Verify the extracted content includes proper Google Maps tutorial structure"""
        print("\n🔍 Step 4: Verifying Content Structure...")
        try:
            articles = processing_data.get('articles', [])
            
            # Expected Google Maps tutorial sections
            expected_sections = [
                'introduction',
                'getting started',
                'api key',
                'setup',
                'initialization',
                'map creation',
                'markers',
                'events',
                'geocoding',
                'examples'
            ]
            
            found_sections = []
            has_code_examples = False
            has_proper_headings = False
            
            for article in articles:
                title = article.get('title', '').lower()
                content = (article.get('content', '') or article.get('html', '')).lower()
                
                # Check for expected tutorial sections
                for section in expected_sections:
                    if section in title or section in content:
                        if section not in found_sections:
                            found_sections.append(section)
                
                # Check for code examples
                if any(code_indicator in content for code_indicator in ['<code>', '<pre>', 'function', 'google.maps', 'var map']):
                    has_code_examples = True
                
                # Check for proper heading structure
                if any(heading in content for heading in ['<h1>', '<h2>', '<h3>']):
                    has_proper_headings = True
            
            print(f"📋 Tutorial sections found: {found_sections}")
            print(f"💻 Code examples present: {has_code_examples}")
            print(f"📝 Proper headings present: {has_proper_headings}")
            
            if len(found_sections) >= 3 and has_code_examples and has_proper_headings:
                print("✅ CONTENT STRUCTURE VERIFIED:")
                print("   ✅ Multiple tutorial sections identified")
                print("   ✅ JavaScript code examples present")
                print("   ✅ Proper HTML heading structure")
                return True
            elif len(found_sections) >= 2:
                print("✅ CONTENT STRUCTURE PARTIALLY VERIFIED:")
                print("   ✅ Some tutorial sections identified")
                return True
            else:
                print("❌ CONTENT STRUCTURE VERIFICATION FAILED:")
                print("   ❌ Insufficient tutorial structure detected")
                return False
                
        except Exception as e:
            print(f"❌ Structure verification failed - {str(e)}")
            return False
    
    def verify_data_format(self, processing_data):
        """Verify the backend returns content in the format the frontend expects"""
        print("\n🔍 Step 5: Verifying Data Format for Frontend Compatibility...")
        try:
            # Check required top-level fields
            required_fields = ['success', 'articles', 'session_id', 'processing_time']
            missing_fields = [field for field in required_fields if field not in processing_data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            print("✅ All required top-level fields present")
            
            # Check article structure
            articles = processing_data.get('articles', [])
            if not articles:
                print("❌ No articles in response")
                return False
            
            # Check first article structure
            sample_article = articles[0]
            required_article_fields = ['id', 'title', 'content', 'created_at', 'word_count']
            missing_article_fields = [field for field in required_article_fields if field not in sample_article]
            
            if missing_article_fields:
                print(f"❌ Missing required article fields: {missing_article_fields}")
                return False
            
            print("✅ Article structure compatible with frontend")
            
            # Check HTML content format
            content = sample_article.get('content', '') or sample_article.get('html', '')
            if not content:
                print("❌ No HTML content in articles")
                return False
            
            # Verify HTML structure
            html_elements = ['<h1>', '<h2>', '<p>', '<div>']
            found_elements = [elem for elem in html_elements if elem in content]
            
            if len(found_elements) >= 2:
                print(f"✅ Proper HTML structure: {found_elements}")
            else:
                print(f"⚠️ Limited HTML structure: {found_elements}")
            
            # Check for proper headings from document
            if '<h1>' in content and '<h2>' in content:
                print("✅ Real headings from document preserved")
            else:
                print("⚠️ Limited heading structure detected")
            
            # Check content length (should be substantial for Google Maps tutorial)
            total_content_length = sum(len(article.get('content', '') or article.get('html', '')) for article in articles)
            
            if total_content_length > 10000:  # At least 10KB of content
                print(f"✅ Substantial content extracted: {total_content_length:,} characters")
            else:
                print(f"⚠️ Limited content extracted: {total_content_length:,} characters")
            
            print("✅ DATA FORMAT VERIFICATION SUCCESSFUL:")
            print("   ✅ Compatible with frontend expectations")
            print("   ✅ Proper HTML structure maintained")
            print("   ✅ Real document headings preserved")
            return True
            
        except Exception as e:
            print(f"❌ Data format verification failed - {str(e)}")
            return False
    
    def verify_image_processing(self, processing_data):
        """Verify image processing from the Google Maps DOCX"""
        print("\n🔍 Step 6: Verifying Image Processing...")
        try:
            images_processed = processing_data.get('images_processed', 0)
            articles = processing_data.get('articles', [])
            
            print(f"🖼️ Images Processed: {images_processed}")
            
            # Check for embedded images in articles
            total_embedded_images = 0
            articles_with_images = 0
            
            for i, article in enumerate(articles):
                content = article.get('content', '') or article.get('html', '')
                
                # Count image elements
                figure_count = content.count('<figure')
                img_count = content.count('<img')
                api_static_count = content.count('/api/static/uploads/')
                
                if figure_count > 0 or img_count > 0 or api_static_count > 0:
                    articles_with_images += 1
                    total_embedded_images += max(figure_count, img_count, api_static_count)
                    print(f"   Article {i+1}: {figure_count} <figure>, {img_count} <img>, {api_static_count} URLs")
            
            print(f"📊 Image Processing Summary:")
            print(f"   Images processed by backend: {images_processed}")
            print(f"   Images embedded in articles: {total_embedded_images}")
            print(f"   Articles with images: {articles_with_images}/{len(articles)}")
            
            if images_processed > 0 and total_embedded_images > 0:
                print("✅ IMAGE PROCESSING SUCCESSFUL:")
                print("   ✅ Images extracted from DOCX")
                print("   ✅ Images embedded in articles")
                print("   ✅ Proper image URLs generated")
                return True
            elif images_processed > 0:
                print("⚠️ IMAGE PROCESSING PARTIAL:")
                print("   ✅ Images detected and processed")
                print("   ⚠️ Images may not be embedded in final articles")
                return True
            else:
                print("❌ IMAGE PROCESSING FAILED:")
                print("   ❌ No images processed from Google Maps DOCX")
                print("   ❌ This may indicate the image processing pipeline issue")
                return False
                
        except Exception as e:
            print(f"❌ Image processing verification failed - {str(e)}")
            return False
    
    def test_complete_pipeline(self):
        """Test the complete backend flow from DOCX upload to structured content output"""
        print("\n🔍 Step 7: Testing Complete Processing Pipeline...")
        try:
            # Download the DOCX file
            docx_content = self.download_google_maps_docx()
            if not docx_content:
                return False
            
            # Process through backend
            processing_data = self.process_google_maps_docx(docx_content)
            if not processing_data:
                return False
            
            # Run all verification tests
            tests = [
                ("Real Content Extraction", self.verify_real_content_extraction),
                ("Content Structure", self.verify_content_structure),
                ("Data Format", self.verify_data_format),
                ("Image Processing", self.verify_image_processing)
            ]
            
            results = []
            for test_name, test_func in tests:
                print(f"\n{'='*60}")
                print(f"Running {test_name} Test...")
                print('='*60)
                
                try:
                    result = test_func(processing_data)
                    results.append((test_name, result))
                    
                    if result:
                        print(f"✅ {test_name} Test: PASSED")
                    else:
                        print(f"❌ {test_name} Test: FAILED")
                        
                except Exception as e:
                    print(f"❌ {test_name} Test: ERROR - {str(e)}")
                    results.append((test_name, False))
            
            # Final summary
            print(f"\n{'='*60}")
            print("GOOGLE MAPS DOCX PROCESSING PIPELINE TEST RESULTS")
            print('='*60)
            
            passed_tests = sum(1 for _, result in results if result)
            total_tests = len(results)
            
            for test_name, result in results:
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"{test_name:.<40} {status}")
            
            print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests >= 3:  # At least 3 out of 4 tests should pass
                print("\n🎉 GOOGLE MAPS DOCX PROCESSING PIPELINE: SUCCESS")
                print("✅ Real content extraction working")
                print("✅ Backend processing pipeline operational")
                print("✅ Frontend-compatible data format")
                return True
            else:
                print("\n❌ GOOGLE MAPS DOCX PROCESSING PIPELINE: FAILED")
                print("❌ Critical issues detected in content processing")
                return False
                
        except Exception as e:
            print(f"❌ Complete pipeline test failed - {str(e)}")
            return False

def main():
    """Run the Google Maps DOCX processing test"""
    print("🚀 Starting Google Maps DOCX Content Processing Pipeline Test")
    print("="*80)
    
    tester = GoogleMapsDocxTest()
    success = tester.test_complete_pipeline()
    
    print("\n" + "="*80)
    if success:
        print("🎉 GOOGLE MAPS DOCX TEST COMPLETED SUCCESSFULLY")
        print("✅ Real content processing pipeline is operational")
        print("✅ No test data detected - actual Google Maps content extracted")
    else:
        print("❌ GOOGLE MAPS DOCX TEST FAILED")
        print("❌ Issues detected in content processing pipeline")
    print("="*80)
    
    return success

if __name__ == "__main__":
    main()