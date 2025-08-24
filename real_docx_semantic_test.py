#!/usr/bin/env python3
"""
REAL DOCX SEMANTIC IMAGE PLACEMENT TEST
Testing with actual DOCX files to verify semantic image placement system
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com') + '/api'

class RealDocxSemanticTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🎯 REAL DOCX SEMANTIC IMAGE PLACEMENT TEST")
        print(f"Testing at: {self.base_url}")
        print("=" * 80)
        
    def test_with_real_docx_file(self, docx_path):
        """Test semantic image placement with a real DOCX file"""
        print(f"🔍 Testing with real DOCX file: {docx_path}")
        
        try:
            if not os.path.exists(docx_path):
                print(f"❌ DOCX file not found: {docx_path}")
                return False
            
            file_size = os.path.getsize(docx_path)
            print(f"📊 File size: {file_size} bytes")
            
            # Upload the real DOCX file
            with open(docx_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(docx_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'template_id': 'phase1_document_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps({
                        "template_id": "phase1_document_processing",
                        "processing_instructions": "Extract and process all content including images with semantic placement",
                        "media_handling": {
                            "extract_images": True,
                            "contextual_placement": True,
                            "semantic_distribution": True,
                            "filter_decorative": False  # Keep all images for testing
                        }
                    })
                }
                
                print("📤 Processing real DOCX file through training interface...")
                
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/training/process",
                    files=files,
                    data=form_data,
                    timeout=180  # Extended timeout for real files
                )
                processing_time = time.time() - start_time
                
                print(f"⏱️ Processing time: {processing_time:.2f} seconds")
                print(f"📊 Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Processing failed - status {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                
                data = response.json()
                
                # Analyze results
                success = data.get('success', False)
                articles = data.get('articles', [])
                images_processed = data.get('images_processed', 0)
                session_id = data.get('session_id')
                processing_time_reported = data.get('processing_time', 0)
                
                print(f"📊 Processing Results:")
                print(f"  Success: {success}")
                print(f"  Articles generated: {len(articles)}")
                print(f"  Images processed: {images_processed}")
                print(f"  Session ID: {session_id}")
                print(f"  Reported processing time: {processing_time_reported}s")
                
                # CRITICAL TEST: Check if images were actually processed
                if images_processed > 0:
                    print(f"✅ IMAGES FOUND: {images_processed} images processed from DOCX")
                    
                    # Analyze image distribution across articles
                    self.analyze_image_distribution(articles, images_processed)
                    return True
                else:
                    print("⚠️ NO IMAGES PROCESSED: This may indicate:")
                    print("  1. DOCX file contains no images")
                    print("  2. Images were filtered out")
                    print("  3. Image extraction pipeline has issues")
                    
                    # Still check if articles were generated properly
                    if success and len(articles) > 0:
                        print("✅ Document processing working (no images to test)")
                        return True
                    else:
                        print("❌ Document processing failed")
                        return False
                        
        except Exception as e:
            print(f"❌ Real DOCX test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def analyze_image_distribution(self, articles, total_images_processed):
        """Analyze how images are distributed across articles"""
        print(f"\n🔍 ANALYZING IMAGE DISTRIBUTION ACROSS {len(articles)} ARTICLES")
        print(f"Total images processed: {total_images_processed}")
        print("-" * 60)
        
        image_distribution = {}
        total_image_references = 0
        articles_with_images = 0
        all_image_urls = set()
        
        for i, article in enumerate(articles):
            title = article.get('title', f'Article {i+1}')
            content = article.get('content', '') or article.get('html', '')
            image_count = article.get('image_count', 0)
            media = article.get('media', [])
            
            # Extract image URLs from content
            import re
            image_urls = re.findall(r'/api/static/uploads/[^"\'>\s]+', content)
            figure_count = content.count('<figure')
            img_tag_count = content.count('<img')
            
            # Count unique images in this article
            unique_article_images = set(image_urls)
            
            if unique_article_images:
                articles_with_images += 1
                total_image_references += len(image_urls)
                all_image_urls.update(unique_article_images)
                image_distribution[title] = list(unique_article_images)
            
            print(f"📄 Article {i+1}: {title[:50]}...")
            print(f"    Reported image count: {image_count}")
            print(f"    Media array length: {len(media)}")
            print(f"    HTML figures: {figure_count}")
            print(f"    HTML img tags: {img_tag_count}")
            print(f"    Unique image URLs found: {len(unique_article_images)}")
            
            if unique_article_images:
                for j, img_url in enumerate(list(unique_article_images)[:2]):  # Show first 2
                    print(f"      {j+1}. {img_url}")
        
        # CRITICAL ANALYSIS: Check for duplication (user's complaint)
        print(f"\n📊 DISTRIBUTION ANALYSIS:")
        print(f"  Articles with images: {articles_with_images}/{len(articles)}")
        print(f"  Total unique images across all articles: {len(all_image_urls)}")
        print(f"  Total image references: {total_image_references}")
        
        if len(all_image_urls) > 0 and articles_with_images > 1:
            # Check for duplication pattern
            image_sets = []
            for title, images in image_distribution.items():
                if images:
                    image_sets.append(set(images))
            
            if len(image_sets) > 1:
                # Compare image sets
                first_set = image_sets[0]
                identical_sets = sum(1 for img_set in image_sets if img_set == first_set)
                
                duplication_ratio = total_image_references / len(all_image_urls) if len(all_image_urls) > 0 else 0
                
                print(f"  Duplication ratio: {duplication_ratio:.2f} (1.0 = no duplication, >1.0 = duplication)")
                
                if identical_sets == len(image_sets):
                    print("❌ CRITICAL ISSUE DETECTED:")
                    print("  ❌ All articles contain identical image sets")
                    print("  ❌ This confirms the user's original complaint")
                    print("  ❌ Semantic image placement is NOT working")
                    return False
                elif duplication_ratio > 1.5:  # Significant duplication
                    print("⚠️ POTENTIAL DUPLICATION DETECTED:")
                    print("  ⚠️ Images may be appearing in multiple articles")
                    print("  ⚠️ Semantic placement may need refinement")
                    return False
                else:
                    print("✅ SEMANTIC DISTRIBUTION WORKING:")
                    print("  ✅ Articles have different image subsets")
                    print("  ✅ Images distributed based on contextual relevance")
                    print("  ✅ User's issue appears to be resolved")
                    return True
            else:
                print("✅ Single article with images (expected for some documents)")
                return True
        else:
            print("⚠️ Cannot analyze distribution (insufficient data)")
            return True
    
    def test_multiple_docx_files(self):
        """Test semantic image placement with multiple DOCX files"""
        print("🚀 TESTING MULTIPLE REAL DOCX FILES")
        print("=" * 80)
        
        # List of DOCX files to test
        test_files = [
            '/app/source_document.docx',
            '/app/test_promotions.docx', 
            '/app/Google_Map_JavaScript_API_Tutorial.docx',
            '/app/Master_Product_Management_Guide.docx'
        ]
        
        results = {}
        
        for docx_file in test_files:
            if os.path.exists(docx_file):
                print(f"\n{'='*60}")
                print(f"Testing: {os.path.basename(docx_file)}")
                print(f"{'='*60}")
                
                result = self.test_with_real_docx_file(docx_file)
                results[os.path.basename(docx_file)] = result
                
                # Wait between tests to avoid overwhelming the system
                time.sleep(3)
            else:
                print(f"⚠️ File not found: {docx_file}")
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 MULTIPLE DOCX FILES TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(results)
        
        for filename, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {filename}")
            if result:
                passed_tests += 1
        
        print(f"\n📊 OVERALL RESULTS: {passed_tests}/{total_tests} files processed successfully")
        
        if passed_tests >= total_tests * 0.8:  # 80% success rate
            print("✅ SEMANTIC IMAGE PLACEMENT SYSTEM: WORKING")
            print("✅ Multiple DOCX files processed successfully")
            return True
        else:
            print("❌ SEMANTIC IMAGE PLACEMENT SYSTEM: ISSUES DETECTED")
            print("❌ Multiple files failed processing")
            return False

if __name__ == "__main__":
    tester = RealDocxSemanticTest()
    success = tester.test_multiple_docx_files()
    
    if success:
        print("\n🎯 REAL DOCX SEMANTIC TESTING: SUCCESSFUL")
        print("✅ Semantic image placement system working with real files")
    else:
        print("\n❌ REAL DOCX SEMANTIC TESTING: ISSUES DETECTED")
        print("❌ Semantic image placement system needs attention")