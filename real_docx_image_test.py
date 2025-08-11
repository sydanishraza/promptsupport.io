#!/usr/bin/env python3
"""
Real DOCX Image Processing Test
Test image processing with actual DOCX files to understand the issue
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://5281eecc-eac8-4f65-9a23-23445575ef21.preview.emergentagent.com') + '/api'

def test_real_docx_image_processing():
    """Test image processing with actual DOCX files"""
    print("🔍 Testing Image Processing with Real DOCX Files")
    print("=" * 60)
    
    # Test with multiple DOCX files
    docx_files = [
        '/app/test_billing.docx',
        '/app/test_promotions.docx', 
        '/app/simple_test.docx'
    ]
    
    for docx_path in docx_files:
        if not os.path.exists(docx_path):
            print(f"⚠️ File not found: {docx_path}")
            continue
            
        print(f"\n📄 Testing with: {os.path.basename(docx_path)}")
        print(f"📊 File size: {os.path.getsize(docx_path)} bytes")
        
        try:
            with open(docx_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(docx_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'template_id': 'phase1_document_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps({
                        "template_id": "phase1_document_processing",
                        "media_handling": {
                            "extract_images": True,
                            "contextual_placement": True,
                            "filter_decorative": False  # Don't filter for testing
                        }
                    })
                }
                
                print("📤 Processing real DOCX file...")
                
                start_time = time.time()
                response = requests.post(
                    f"{BACKEND_URL}/training/process",
                    files=files,
                    data=form_data,
                    timeout=120
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
                    
                    print(f"✅ Processing successful: {success}")
                    print(f"📋 Session ID: {session_id}")
                    print(f"🖼️ Images processed: {images_processed}")
                    print(f"📚 Articles generated: {len(articles)}")
                    
                    # Check for images in articles
                    if articles:
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
                                print(f"    ✅ Contains accessible image URLs")
                            elif figure_count > 0 or img_count > 0:
                                print(f"    ⚠️ Contains image elements but no accessible URLs")
                            else:
                                print(f"    ❌ No image content found")
                    
                    # Check session directory
                    if session_id:
                        session_dir = f"/app/backend/static/uploads/session_{session_id}"
                        print(f"\n📁 Checking session directory: {session_dir}")
                        
                        try:
                            if os.path.exists(session_dir):
                                files_in_dir = os.listdir(session_dir)
                                image_files = [f for f in files_in_dir if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                                print(f"  ✅ Session directory exists")
                                print(f"  📁 Total files: {len(files_in_dir)}")
                                print(f"  🖼️ Image files: {len(image_files)}")
                                if image_files:
                                    print(f"  📋 Image files: {image_files}")
                            else:
                                print(f"  ❌ Session directory not found")
                        except Exception as dir_error:
                            print(f"  ⚠️ Could not check directory: {dir_error}")
                    
                    print(f"\n🎯 ANALYSIS FOR {os.path.basename(docx_path)}:")
                    if images_processed > 0:
                        print(f"  ✅ Image extraction is working ({images_processed} images)")
                        if any(article.get('image_count', 0) > 0 for article in articles):
                            print(f"  ✅ Images are integrated into articles")
                        else:
                            print(f"  ❌ Images extracted but not integrated into articles")
                    else:
                        print(f"  ❌ No images extracted from this DOCX file")
                        print(f"  ❌ Either file has no images or extraction is broken")
                        
                else:
                    print(f"❌ Processing failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Test failed for {docx_path}: {e}")
            
        print("-" * 60)

def check_mammoth_functionality():
    """Test mammoth library directly to see if it can extract images"""
    print("\n🔍 Testing Mammoth Library Directly")
    print("=" * 60)
    
    try:
        import mammoth
        print("✅ Mammoth library is available")
        
        # Test with a real DOCX file
        test_file = '/app/test_billing.docx'
        if os.path.exists(test_file):
            print(f"📄 Testing mammoth with: {os.path.basename(test_file)}")
            
            with open(test_file, "rb") as docx_file:
                # Test basic conversion
                result = mammoth.convert_to_html(docx_file)
                html_content = result.value
                messages = result.messages
                
                print(f"📊 HTML content length: {len(html_content)} characters")
                print(f"📊 Conversion messages: {len(messages)}")
                
                for message in messages[:5]:  # Show first 5 messages
                    print(f"  📋 {message.type}: {message.message}")
                
                # Check for image references in HTML
                if 'img' in html_content.lower():
                    print("✅ HTML contains image references")
                else:
                    print("❌ HTML does not contain image references")
                
                # Test with image handler
                print("\n🖼️ Testing with image handler...")
                
                def test_image_handler(image):
                    print(f"  📷 Image found: {type(image)}")
                    print(f"  📋 Image attributes: {dir(image)}")
                    
                    # Try to get image data
                    try:
                        if hasattr(image, 'open'):
                            with image.open() as img_data:
                                data = img_data.read()
                                print(f"  📊 Image data size: {len(data)} bytes")
                        elif hasattr(image, 'bytes'):
                            print(f"  📊 Image bytes size: {len(image.bytes)} bytes")
                        else:
                            print(f"  ⚠️ Unknown image data format")
                    except Exception as img_error:
                        print(f"  ❌ Could not extract image data: {img_error}")
                    
                    return {"src": "test_placeholder"}
                
                # Reset file pointer
                docx_file.seek(0)
                result_with_images = mammoth.convert_to_html(docx_file, convert_image=test_image_handler)
                
                print(f"📊 HTML with image handler length: {len(result_with_images.value)} characters")
                
        else:
            print(f"❌ Test file not found: {test_file}")
            
    except ImportError:
        print("❌ Mammoth library not available")
    except Exception as e:
        print(f"❌ Mammoth test failed: {e}")

def main():
    """Run the real DOCX image processing tests"""
    test_real_docx_image_processing()
    check_mammoth_functionality()

if __name__ == "__main__":
    main()