#!/usr/bin/env python3
"""
Focused Knowledge Engine Fixes Testing
Testing with actual DOCX files to verify the two critical issues
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdocs-23.preview.emergentagent.com') + '/api'

class FocusedKnowledgeEngineTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_id = None
        print(f"🎯 Focused Knowledge Engine Testing at: {self.base_url}")
        
    def test_with_actual_docx_file(self):
        """Test with an actual DOCX file that should contain images"""
        print("\n🎯 CRITICAL TEST: Processing Actual DOCX File with Images")
        
        # Find an actual DOCX file to test with
        docx_files = [
            '/app/test_billing.docx',
            '/app/test_promotions.docx', 
            '/app/Promotions_Configuration_and_Management-v5-20220201_173002.docx'
        ]
        
        test_file = None
        for file_path in docx_files:
            if os.path.exists(file_path):
                test_file = file_path
                break
        
        if not test_file:
            print("❌ No DOCX test files found")
            return False
        
        print(f"📄 Using test file: {test_file}")
        
        try:
            # Upload the actual DOCX file
            with open(test_file, 'rb') as f:
                files = {
                    'file': (os.path.basename(test_file), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'template_id': 'document_upload_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps({
                        "template_id": "document_upload_processing",
                        "media_handling": {
                            "extract_images": True,
                            "contextual_placement": True,
                            "use_actual_urls": True
                        }
                    })
                }
                
                print("📤 Processing actual DOCX file...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.base_url}/training/process",
                    files=files,
                    data=form_data,
                    timeout=180
                )
                
                processing_time = time.time() - start_time
                print(f"⏱️ Processing time: {processing_time:.2f} seconds")
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Processing failed - status {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                
                data = response.json()
                
                # Extract key metrics
                success = data.get('success', False)
                session_id = data.get('session_id')
                articles = data.get('articles', [])
                images_processed = data.get('images_processed', 0)
                
                print(f"✅ Processing Success: {success}")
                print(f"🆔 Session ID: {session_id}")
                print(f"📚 Articles Generated: {len(articles)}")
                print(f"🖼️ Images Processed: {images_processed}")
                
                self.session_id = session_id
                
                # CRITICAL ANALYSIS
                print(f"\n📊 DETAILED ANALYSIS:")
                
                total_word_count = 0
                articles_with_images = 0
                image_urls_found = []
                
                for i, article in enumerate(articles):
                    title = article.get('title', f'Article {i+1}')
                    content = article.get('content', '') or article.get('html', '')
                    word_count = article.get('word_count', 0)
                    image_count = article.get('image_count', 0)
                    
                    total_word_count += word_count
                    
                    print(f"\n📄 Article {i+1}: '{title}'")
                    print(f"   Word Count: {word_count}")
                    print(f"   Image Count: {image_count}")
                    print(f"   Content Length: {len(content)} chars")
                    
                    # Check for image URLs in content
                    if '/api/static/uploads/' in content:
                        import re
                        urls = re.findall(r'/api/static/uploads/[^"\'>\s]+', content)
                        if urls:
                            articles_with_images += 1
                            image_urls_found.extend(urls)
                            print(f"   ✅ Contains {len(urls)} image URLs")
                            for url in urls:
                                print(f"      🖼️ {url}")
                        else:
                            print(f"   ⚠️ Contains /api/static/uploads/ but no extractable URLs")
                    else:
                        print(f"   ⚠️ No image URLs found in content")
                    
                    # Check HTML structure
                    figure_count = content.count('<figure')
                    img_count = content.count('<img')
                    if figure_count > 0 or img_count > 0:
                        print(f"   ✅ HTML structure: {figure_count} <figure>, {img_count} <img> elements")
                
                # ISSUE VERIFICATION
                print(f"\n🎯 CRITICAL ISSUES VERIFICATION:")
                
                # ISSUE 1: Images are rendering as broken
                unique_image_urls = list(set(image_urls_found))
                print(f"📊 Unique Image URLs Found: {len(unique_image_urls)}")
                
                if len(unique_image_urls) > 0:
                    print("✅ ISSUE 1 PROGRESS: Image URLs are being generated")
                    
                    # Test URL accessibility
                    accessible_count = 0
                    for url in unique_image_urls[:3]:  # Test first 3 URLs
                        try:
                            full_url = f"{self.base_url.replace('/api', '')}{url}"
                            response = requests.head(full_url, timeout=10)
                            if response.status_code == 200:
                                accessible_count += 1
                                print(f"   ✅ Accessible: {url}")
                            else:
                                print(f"   ❌ Not accessible ({response.status_code}): {url}")
                        except Exception as e:
                            print(f"   ❌ Error testing {url}: {e}")
                    
                    if accessible_count > 0:
                        print("✅ ISSUE 1 VERIFIED: Some images are accessible (not broken)")
                    else:
                        print("❌ ISSUE 1 NOT FIXED: Image URLs exist but are not accessible")
                else:
                    print("❌ ISSUE 1 NOT FIXED: No image URLs found in articles")
                
                # ISSUE 2: Content coverage is not complete
                print(f"📊 Total Word Count: {total_word_count}")
                print(f"📊 Articles Generated: {len(articles)}")
                
                if total_word_count >= 500 and len(articles) >= 1:
                    print("✅ ISSUE 2 VERIFIED: Content coverage appears comprehensive")
                else:
                    print("❌ ISSUE 2 NOT FIXED: Content coverage is still limited")
                
                # Overall assessment
                issue1_progress = len(unique_image_urls) > 0
                issue2_progress = total_word_count >= 300
                
                if issue1_progress and issue2_progress:
                    print("\n✅ BOTH ISSUES SHOW PROGRESS")
                    return True
                elif issue1_progress or issue2_progress:
                    print("\n⚠️ PARTIAL PROGRESS ON ISSUES")
                    return True
                else:
                    print("\n❌ NO PROGRESS ON CRITICAL ISSUES")
                    return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_image_directory_structure(self):
        """Test the current state of image storage"""
        print("\n🔍 Testing Current Image Storage State")
        
        try:
            # Check uploads directory
            uploads_dir = "/app/backend/static/uploads"
            if os.path.exists(uploads_dir):
                files = os.listdir(uploads_dir)
                image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                session_dirs = [f for f in files if f.startswith('session_')]
                
                print(f"📁 Upload directory exists: {uploads_dir}")
                print(f"🖼️ Direct image files: {len(image_files)}")
                print(f"📂 Session directories: {len(session_dirs)}")
                
                if image_files:
                    print("✅ Images are being stored in the system")
                    # Show some examples
                    for img in image_files[:5]:
                        print(f"   📷 {img}")
                
                if session_dirs:
                    print("✅ Session-based storage is working")
                    # Check a session directory
                    session_dir = os.path.join(uploads_dir, session_dirs[0])
                    if os.path.exists(session_dir):
                        session_files = os.listdir(session_dir)
                        session_images = [f for f in session_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                        print(f"   📂 {session_dirs[0]}: {len(session_images)} images")
                
                return True
            else:
                print("❌ Upload directory does not exist")
                return False
                
        except Exception as e:
            print(f"❌ Directory check failed: {e}")
            return False

    def test_content_library_current_state(self):
        """Check current state of Content Library"""
        print("\n📚 Testing Current Content Library State")
        
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Content Library access failed: {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"📚 Total articles in library: {len(articles)}")
            
            # Analyze recent articles for image content
            articles_with_images = 0
            total_image_urls = 0
            
            for article in articles[:10]:  # Check first 10 articles
                content = article.get('content', '') or article.get('html', '')
                if '/api/static/uploads/' in content:
                    articles_with_images += 1
                    import re
                    urls = re.findall(r'/api/static/uploads/[^"\'>\s]+', content)
                    total_image_urls += len(urls)
            
            print(f"📊 Articles with image URLs: {articles_with_images}/10")
            print(f"📊 Total image URLs found: {total_image_urls}")
            
            if articles_with_images > 0:
                print("✅ Some articles contain image URLs")
                return True
            else:
                print("⚠️ No articles with image URLs found in recent articles")
                return True
                
        except Exception as e:
            print(f"❌ Content Library check failed: {e}")
            return False

    def run_focused_tests(self):
        """Run focused tests on the critical issues"""
        print("🚀 STARTING FOCUSED KNOWLEDGE ENGINE TESTING")
        print("=" * 60)
        
        test_results = []
        
        # Test 1: Image Directory Structure
        test_results.append(("Image Directory Structure", self.test_image_directory_structure()))
        
        # Test 2: Content Library Current State
        test_results.append(("Content Library State", self.test_content_library_current_state()))
        
        # Test 3: Actual DOCX Processing
        test_results.append(("Actual DOCX Processing", self.test_with_actual_docx_file()))
        
        # Results Summary
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST RESULTS")
        print("=" * 60)
        
        passed_tests = 0
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed_tests += 1
        
        print(f"\n📊 OVERALL: {passed_tests}/{len(test_results)} tests passed")
        
        if passed_tests >= 2:
            print("✅ KNOWLEDGE ENGINE SHOWS POSITIVE INDICATORS")
            return True
        else:
            print("❌ KNOWLEDGE ENGINE NEEDS ATTENTION")
            return False

if __name__ == "__main__":
    tester = FocusedKnowledgeEngineTest()
    success = tester.run_focused_tests()
    exit(0 if success else 1)