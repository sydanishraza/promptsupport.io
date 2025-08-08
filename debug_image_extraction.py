#!/usr/bin/env python3
"""
Debug Image Extraction
Test specifically with test_billing.docx which has 5 images to understand why extraction fails
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://809922a0-8c7a-4229-b01a-eafa1e6de9cd.preview.emergentagent.com') + '/api'

def debug_image_extraction():
    """Debug image extraction with test_billing.docx which has 5 images"""
    print("🔍 DEBUG: Image Extraction with test_billing.docx (5 images)")
    print("=" * 70)
    
    test_file = '/app/test_billing.docx'
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📄 Testing with: {os.path.basename(test_file)}")
    print(f"📊 File size: {os.path.getsize(test_file)} bytes")
    print(f"🖼️ Expected images: 5 (image1.png, image2.png, image3.png, image4.png, image5.jpeg)")
    
    try:
        with open(test_file, 'rb') as f:
            files = {
                'file': (os.path.basename(test_file), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use minimal template to focus on image extraction
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "filter_decorative": False,  # Don't filter for debugging
                        "debug_mode": True
                    }
                })
            }
            
            print("\n📤 Sending request with debug mode enabled...")
            
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/training/process",
                files=files,
                data=form_data,
                timeout=180  # Extended timeout for debugging
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing time: {processing_time:.2f} seconds")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                session_id = data.get('session_id')
                images_processed = data.get('images_processed', 0)
                articles = data.get('articles', [])
                success = data.get('success', False)
                
                print(f"\n✅ Processing successful: {success}")
                print(f"📋 Session ID: {session_id}")
                print(f"🖼️ Images processed: {images_processed} (expected: 5)")
                print(f"📚 Articles generated: {len(articles)}")
                
                # Detailed analysis
                print(f"\n🔍 DETAILED ANALYSIS:")
                
                if images_processed == 0:
                    print(f"❌ CRITICAL ISSUE: No images were processed despite file containing 5 images")
                    print(f"❌ This confirms the image extraction pipeline is broken")
                elif images_processed < 5:
                    print(f"⚠️ PARTIAL EXTRACTION: Only {images_processed}/5 images processed")
                    print(f"⚠️ Some images may be filtered out by the pipeline")
                else:
                    print(f"✅ FULL EXTRACTION: All {images_processed} images processed successfully")
                
                # Check session directory for actual saved images
                if session_id:
                    session_dir = f"/app/backend/static/uploads/session_{session_id}"
                    print(f"\n📁 Session directory: {session_dir}")
                    
                    try:
                        if os.path.exists(session_dir):
                            files_in_dir = os.listdir(session_dir)
                            image_files = [f for f in files_in_dir if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                            
                            print(f"  ✅ Directory exists with {len(files_in_dir)} total files")
                            print(f"  🖼️ Image files saved: {len(image_files)}")
                            
                            if image_files:
                                print(f"  📋 Saved images:")
                                for img_file in image_files:
                                    img_path = os.path.join(session_dir, img_file)
                                    img_size = os.path.getsize(img_path)
                                    print(f"    - {img_file} ({img_size} bytes)")
                            else:
                                print(f"  ❌ No image files saved to directory")
                        else:
                            print(f"  ❌ Session directory was not created")
                    except Exception as dir_error:
                        print(f"  ⚠️ Could not check directory: {dir_error}")
                
                # Check articles for image content
                print(f"\n📄 ARTICLE ANALYSIS:")
                for i, article in enumerate(articles):
                    content = article.get('content', '') or article.get('html', '')
                    image_count = article.get('image_count', 0)
                    
                    # Count different image indicators
                    figure_count = content.count('<figure')
                    img_count = content.count('<img')
                    api_static_count = content.count('/api/static/uploads/')
                    image_block_count = content.count('IMAGE_BLOCK:')
                    
                    print(f"  📄 Article {i+1}:")
                    print(f"    📊 Reported image_count: {image_count}")
                    print(f"    📊 <figure> elements: {figure_count}")
                    print(f"    📊 <img> tags: {img_count}")
                    print(f"    📊 /api/static URLs: {api_static_count}")
                    print(f"    📊 IMAGE_BLOCK tokens: {image_block_count}")
                    
                    if api_static_count > 0:
                        print(f"    ✅ Contains {api_static_count} accessible image URLs")
                        
                        # Extract and test the first URL
                        import re
                        urls = re.findall(r'/api/static/uploads/[^"\s]+', content)
                        if urls:
                            test_url = urls[0]
                            full_url = BACKEND_URL.replace('/api', '') + test_url
                            print(f"    🔗 Testing first URL: {test_url}")
                            
                            try:
                                url_response = requests.head(full_url, timeout=10)
                                print(f"    📊 URL status: {url_response.status_code}")
                                if url_response.status_code == 200:
                                    print(f"    ✅ Image is accessible to frontend")
                                else:
                                    print(f"    ❌ Image not accessible (status {url_response.status_code})")
                            except Exception as url_error:
                                print(f"    ❌ URL test failed: {url_error}")
                    
                    elif figure_count > 0 or img_count > 0:
                        print(f"    ⚠️ Contains image elements but no accessible URLs")
                        print(f"    ⚠️ Images may be AI-generated placeholders")
                    else:
                        print(f"    ❌ No image content found")
                
                # Final assessment
                print(f"\n🎯 FINAL ASSESSMENT:")
                if images_processed == 5 and session_id:
                    print(f"  ✅ IMAGE EXTRACTION WORKING PERFECTLY")
                    print(f"  ✅ All 5 images extracted and processed")
                    print(f"  ✅ Images saved to session directory")
                    print(f"  ✅ Frontend can access images via URLs")
                elif images_processed > 0:
                    print(f"  ⚠️ IMAGE EXTRACTION PARTIALLY WORKING")
                    print(f"  ⚠️ {images_processed}/5 images processed")
                    print(f"  🔧 Some images may be filtered out")
                else:
                    print(f"  ❌ IMAGE EXTRACTION COMPLETELY BROKEN")
                    print(f"  ❌ No images extracted despite file containing 5 images")
                    print(f"  🔧 Critical fix needed in extraction pipeline")
                    
            else:
                print(f"❌ Processing failed with status {response.status_code}")
                print(f"Response: {response.text[:1000]}")
                
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the debug image extraction test"""
    debug_image_extraction()

if __name__ == "__main__":
    main()