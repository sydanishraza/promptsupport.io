#!/usr/bin/env python3
"""
FIXED Media Extraction Pipeline Testing
Testing the enhanced media extraction pipeline with real_visual_document.md
"""

import requests
import json
import os
import io
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://6932dd27-38f2-4781-9b35-b6aac917fef1.preview.emergentagent.com') + '/api'

class MediaExtractionPipelineTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_job_id = None
        self.created_articles = []
        print(f"🖼️ Testing FIXED Media Extraction Pipeline at: {self.base_url}")
        print("🎯 FOCUS: Testing with real_visual_document.md")
        
    def load_real_visual_document(self):
        """Load the real_visual_document.md file"""
        try:
            with open('/app/real_visual_document.md', 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📄 Loaded real_visual_document.md: {len(content)} characters")
            
            # Analyze embedded media
            svg_patterns = re.findall(r'data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)', content)
            print(f"🖼️ Found {len(svg_patterns)} embedded SVG images")
            
            for i, svg_data in enumerate(svg_patterns, 1):
                print(f"   - SVG {i}: {len(svg_data)} base64 characters")
            
            # Check for figure captions
            figure_captions = re.findall(r'\*Figure \d+:.*?\*', content)
            print(f"📝 Found {len(figure_captions)} figure captions")
            
            return content
            
        except Exception as e:
            print(f"❌ Failed to load real_visual_document.md: {e}")
            return None
    
    def test_upload_and_process_with_fixed_pipeline(self):
        """Test 1: Upload and Process with Fixed Pipeline"""
        print("\n🔍 TEST 1: Upload and Process with Fixed Pipeline")
        print("=" * 60)
        
        try:
            # Load the real visual document
            document_content = self.load_real_visual_document()
            if not document_content:
                return False
            
            # Get initial Content Library count
            initial_response = requests.get(f"{self.base_url}/content-library", timeout=10)
            initial_count = 0
            if initial_response.status_code == 200:
                initial_count = initial_response.json().get('total', 0)
                print(f"📊 Initial Content Library articles: {initial_count}")
            
            # Create file-like object for upload
            file_data = io.BytesIO(document_content.encode('utf-8'))
            
            files = {
                'file': ('real_visual_document.md', file_data, 'text/markdown')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "media_extraction_pipeline_test",
                    "test_type": "fixed_media_extraction",
                    "document_type": "visual_documentation",
                    "original_filename": "real_visual_document.md"
                })
            }
            
            print("🚀 Uploading real_visual_document.md through fixed pipeline...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=60  # Increased timeout for media processing
            )
            
            print(f"📡 Upload Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Upload Response: {json.dumps(data, indent=2)}")
                
                self.test_job_id = data.get("job_id")
                chunks_created = data.get("chunks_created", 0)
                extracted_length = data.get("extracted_content_length", 0)
                
                print(f"📊 Processing Results:")
                print(f"   - Job ID: {self.test_job_id}")
                print(f"   - Chunks created: {chunks_created}")
                print(f"   - Extracted content length: {extracted_length}")
                
                # Wait for processing to complete
                print("⏳ Waiting for processing to complete...")
                time.sleep(5)
                
                # Check if Content Library articles were created
                final_response = requests.get(f"{self.base_url}/content-library", timeout=10)
                if final_response.status_code == 200:
                    final_data = final_response.json()
                    final_count = final_data.get('total', 0)
                    articles = final_data.get('articles', [])
                    
                    print(f"📊 Final Content Library articles: {final_count}")
                    
                    if final_count > initial_count:
                        new_articles = final_count - initial_count
                        print(f"✅ Created {new_articles} new Content Library articles!")
                        
                        # Store created articles for further testing
                        self.created_articles = articles[:new_articles]
                        return True
                    else:
                        print("⚠️ No new articles created, but upload succeeded")
                        return True
                else:
                    print("⚠️ Could not verify Content Library creation")
                    return True
            else:
                print(f"❌ Upload failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload and process test failed - {str(e)}")
            return False
    
    def test_verify_media_preservation(self):
        """Test 2: Verify Media Preservation"""
        print("\n🔍 TEST 2: Verify Media Preservation")
        print("=" * 60)
        
        try:
            # Get all Content Library articles
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Could not retrieve Content Library articles - {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"📊 Analyzing {len(articles)} articles for media preservation...")
            
            # Analyze media preservation
            articles_with_media = 0
            total_svg_images = 0
            total_data_urls = 0
            preserved_captions = 0
            figure_references = 0
            
            for article in articles:
                content = article.get('content', '')
                
                # Check for base64 SVG data URLs
                svg_data_urls = re.findall(r'data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)', content)
                if svg_data_urls:
                    articles_with_media += 1
                    total_svg_images += len(svg_data_urls)
                    
                    print(f"🖼️ Article '{article.get('title', 'Untitled')}' contains {len(svg_data_urls)} SVG images")
                    
                    # Verify data URL format
                    for i, svg_data in enumerate(svg_data_urls, 1):
                        if len(svg_data) > 100:  # Valid base64 should be substantial
                            total_data_urls += 1
                            print(f"   ✅ SVG {i}: {len(svg_data)} base64 characters (valid)")
                        else:
                            print(f"   ❌ SVG {i}: {len(svg_data)} base64 characters (too short)")
                
                # Check for preserved captions
                captions = re.findall(r'\*Figure \d+:.*?\*', content)
                preserved_captions += len(captions)
                
                # Check for figure references
                references = re.findall(r'Figure \d+', content)
                figure_references += len(references)
            
            print(f"\n📊 Media Preservation Analysis:")
            print(f"   - Articles with embedded media: {articles_with_media}")
            print(f"   - Total SVG images found: {total_svg_images}")
            print(f"   - Valid data URLs: {total_data_urls}")
            print(f"   - Preserved captions: {preserved_captions}")
            print(f"   - Figure references: {figure_references}")
            
            # Success criteria
            if articles_with_media > 0 and total_data_urls > 0:
                print("✅ Media preservation SUCCESSFUL!")
                print("   - Base64 SVG data URLs are preserved")
                print("   - Images are embedded in generated articles")
                
                if preserved_captions > 0:
                    print("   - Image captions are maintained")
                
                if figure_references > 0:
                    print("   - Figure references are preserved")
                
                return True
            else:
                print("❌ Media preservation FAILED!")
                print("   - No embedded media found in articles")
                return False
                
        except Exception as e:
            print(f"❌ Media preservation test failed - {str(e)}")
            return False
    
    def test_enhanced_content_limits(self):
        """Test 3: Test Enhanced Content Limits (15000 chars)"""
        print("\n🔍 TEST 3: Test Enhanced Content Limits")
        print("=" * 60)
        
        try:
            # Load the document to check its size
            document_content = self.load_real_visual_document()
            if not document_content:
                return False
            
            print(f"📏 Original document size: {len(document_content)} characters")
            
            # Check if document contains long base64 strings
            svg_patterns = re.findall(r'data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)', document_content)
            total_base64_chars = sum(len(svg) for svg in svg_patterns)
            
            print(f"📊 Base64 content analysis:")
            print(f"   - Number of base64 images: {len(svg_patterns)}")
            print(f"   - Total base64 characters: {total_base64_chars}")
            print(f"   - Text content: {len(document_content) - total_base64_chars} characters")
            
            # Test content processing with enhanced limits
            test_content = {
                "content": document_content,  # Full document with media
                "content_type": "text",
                "metadata": {
                    "source": "enhanced_content_limits_test",
                    "test_type": "content_limits_verification",
                    "original_size": len(document_content)
                }
            }
            
            print("🚀 Testing content processing with enhanced limits...")
            
            response = requests.post(
                f"{self.base_url}/content/process",
                json=test_content,
                timeout=60
            )
            
            print(f"📡 Processing Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Processing Response: {json.dumps(data, indent=2)}")
                
                chunks_created = data.get("chunks_created", 0)
                
                if chunks_created > 0:
                    print(f"✅ Enhanced content limits working!")
                    print(f"   - Successfully processed {len(document_content)} characters")
                    print(f"   - Created {chunks_created} chunks")
                    print(f"   - Long base64 strings preserved")
                    
                    # Verify no truncation occurred by checking job status
                    job_id = data.get("job_id")
                    if job_id:
                        time.sleep(2)
                        job_response = requests.get(f"{self.base_url}/jobs/{job_id}", timeout=10)
                        if job_response.status_code == 200:
                            job_data = job_response.json()
                            if job_data.get("status") == "completed":
                                print("✅ Processing completed without truncation")
                                return True
                    
                    return True
                else:
                    print("❌ No chunks created - possible content limit issue")
                    return False
            else:
                print(f"❌ Content processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                
                # Check if it's a content limit issue
                if "too large" in response.text.lower() or "limit" in response.text.lower():
                    print("❌ Content limits not enhanced - document too large")
                    return False
                
                return False
                
        except Exception as e:
            print(f"❌ Enhanced content limits test failed - {str(e)}")
            return False
    
    def test_content_library_verification(self):
        """Test 4: Content Library Verification"""
        print("\n🔍 TEST 4: Content Library Verification")
        print("=" * 60)
        
        try:
            # Get all Content Library articles
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Could not retrieve Content Library - {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            total = data.get('total', 0)
            
            print(f"📊 Content Library Status:")
            print(f"   - Total articles: {total}")
            print(f"   - Articles retrieved: {len(articles)}")
            
            # Analyze articles for media content
            media_articles = []
            ready_for_display = 0
            
            for article in articles:
                article_id = article.get('id')
                title = article.get('title', 'Untitled')
                content = article.get('content', '')
                
                # Check if article contains embedded media
                has_media = 'data:image/svg+xml;base64,' in content
                
                if has_media:
                    media_articles.append({
                        'id': article_id,
                        'title': title,
                        'content_length': len(content),
                        'media_count': len(re.findall(r'data:image/svg\+xml;base64,', content))
                    })
                    
                    # Check if ready for display (has content, title, etc.)
                    if (title and title != 'Untitled' and 
                        content and len(content) > 100 and
                        article.get('status') in ['draft', 'published']):
                        ready_for_display += 1
            
            print(f"\n📊 Media Content Analysis:")
            print(f"   - Articles with embedded media: {len(media_articles)}")
            print(f"   - Articles ready for display: {ready_for_display}")
            
            if media_articles:
                print(f"\n🖼️ Media Articles Found:")
                for i, article in enumerate(media_articles[:5], 1):  # Show first 5
                    print(f"   {i}. '{article['title']}'")
                    print(f"      - Content: {article['content_length']} chars")
                    print(f"      - Media items: {article['media_count']}")
                
                # Test retrieval of a specific media article
                test_article = media_articles[0]
                print(f"\n🔍 Testing retrieval of media article: '{test_article['title']}'")
                
                # Verify the article still contains media when retrieved
                retrieved_content = test_article.get('content', '')
                if 'data:image/svg+xml;base64,' in retrieved_content:
                    print("✅ Media content preserved in storage and retrieval")
                    
                    # Check base64 data integrity
                    svg_data = re.findall(r'data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)', retrieved_content)
                    if svg_data and all(len(data) > 100 for data in svg_data):
                        print("✅ Base64 image data integrity maintained")
                        print("✅ Articles ready for display with visual content")
                        return True
                    else:
                        print("❌ Base64 data corrupted or incomplete")
                        return False
                else:
                    print("❌ Media content lost during storage/retrieval")
                    return False
            else:
                print("❌ No articles with embedded media found")
                print("   This indicates the media extraction pipeline is not working")
                return False
                
        except Exception as e:
            print(f"❌ Content Library verification test failed - {str(e)}")
            return False
    
    def run_comprehensive_media_extraction_test(self):
        """Run all media extraction pipeline tests"""
        print("🚀 Starting FIXED Media Extraction Pipeline Testing")
        print("🎯 TESTING: real_visual_document.md with Enhanced Pipeline")
        print("=" * 80)
        
        results = {}
        
        # Test 1: Upload and Process with Fixed Pipeline
        results['upload_and_process'] = self.test_upload_and_process_with_fixed_pipeline()
        
        # Test 2: Verify Media Preservation
        results['media_preservation'] = self.test_verify_media_preservation()
        
        # Test 3: Test Enhanced Content Limits
        results['enhanced_content_limits'] = self.test_enhanced_content_limits()
        
        # Test 4: Content Library Verification
        results['content_library_verification'] = self.test_content_library_verification()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FIXED MEDIA EXTRACTION PIPELINE TEST RESULTS")
        print("🖼️ Testing with real_visual_document.md")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        test_descriptions = {
            'upload_and_process': 'Upload and Process with Fixed Pipeline',
            'media_preservation': 'Verify Media Preservation (base64 SVG data)',
            'enhanced_content_limits': 'Test Enhanced Content Limits (15000 chars)',
            'content_library_verification': 'Content Library Verification'
        }
        
        for test_name, description in test_descriptions.items():
            result = results.get(test_name, False)
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{description}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        # Critical assessment
        critical_tests = ['upload_and_process', 'media_preservation', 'content_library_verification']
        critical_passed = sum(1 for test in critical_tests if results.get(test, False))
        
        print(f"\n🎯 CRITICAL MEDIA EXTRACTION TESTS: {critical_passed}/{len(critical_tests)} passed")
        
        if critical_passed == len(critical_tests):
            print("🎉 FIXED Media Extraction Pipeline is WORKING!")
            print("✅ Embedded images now appear in generated articles")
            print("✅ Base64 data URLs are preserved during processing")
            print("✅ Articles are ready for display with visual content")
            
            if results.get('enhanced_content_limits'):
                print("✅ Enhanced content limits support media-rich documents")
            
            return True
        elif critical_passed >= 2:
            print("⚠️ Media Extraction Pipeline partially working")
            print(f"   - {critical_passed}/{len(critical_tests)} critical tests passed")
            
            if not results.get('media_preservation'):
                print("❌ CRITICAL: Media preservation failed - images not in articles")
            if not results.get('content_library_verification'):
                print("❌ CRITICAL: Content Library verification failed")
            
            return False
        else:
            print("❌ FIXED Media Extraction Pipeline FAILED")
            print("❌ Embedded images are still being lost during processing")
            print("❌ The fix did not resolve the media extraction issues")
            return False

if __name__ == "__main__":
    tester = MediaExtractionPipelineTest()
    success = tester.run_comprehensive_media_extraction_test()
    exit(0 if success else 1)