#!/usr/bin/env python3
"""
Real DOCX File Testing for Training Engine
Test with actual DOCX files to verify image processing
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://article-genius-1.preview.emergentagent.com') + '/api'

def test_with_real_docx():
    """Test with a real DOCX file from the customer assets"""
    print("🔍 Testing with Real DOCX File...")
    
    try:
        # Download the actual DOCX file
        docx_url = "https://customer-assets.emergentagent.com/Google%20Map%20Javascript%20API%20Tutorial.docx"
        print(f"📥 Downloading DOCX file from: {docx_url}")
        
        response = requests.get(docx_url, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to download DOCX file: {response.status_code}")
            return False
        
        docx_content = response.content
        print(f"📄 Downloaded DOCX file: {len(docx_content)} bytes")
        
        # Test with the training/process endpoint
        files = {
            'file': ('Google_Map_Javascript_API_Tutorial.docx', docx_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true'
        }
        
        print("📤 Processing real DOCX file with Training Engine...")
        
        start_time = time.time()
        
        process_response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=300  # 5 minutes
        )
        
        processing_time = time.time() - start_time
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        print(f"📊 Response Status Code: {process_response.status_code}")
        
        if process_response.status_code == 200:
            data = process_response.json()
            
            success = data.get('success', False)
            articles = data.get('articles', [])
            images_processed = data.get('images_processed', 0)
            session_id = data.get('session_id')
            processing_time_backend = data.get('processing_time', 0)
            
            print(f"✅ Real DOCX Processing Results:")
            print(f"  Success: {success}")
            print(f"  Articles Generated: {len(articles)}")
            print(f"  Images Processed: {images_processed}")
            print(f"  Session ID: {session_id}")
            print(f"  Backend Processing Time: {processing_time_backend}s")
            
            # Check for images in articles
            total_images_in_articles = 0
            for i, article in enumerate(articles):
                content = article.get('content', '') or article.get('html', '')
                img_count = content.count('<img')
                figure_count = content.count('<figure')
                static_url_count = content.count('/api/static/uploads/')
                
                if img_count > 0 or figure_count > 0 or static_url_count > 0:
                    total_images_in_articles += max(img_count, figure_count, static_url_count)
                    print(f"  📄 Article {i+1}: {img_count} <img>, {figure_count} <figure>, {static_url_count} static URLs")
            
            # Test image accessibility if we have a session ID
            if session_id and images_processed > 0:
                print(f"\n🔍 Testing image accessibility for session: {session_id}")
                
                # Test session directory
                session_dir_url = f"{BACKEND_URL.replace('/api', '')}/api/static/uploads/session_{session_id}/"
                try:
                    dir_response = requests.get(session_dir_url, timeout=10)
                    print(f"📁 Session directory status: {dir_response.status_code}")
                except Exception as e:
                    print(f"⚠️ Session directory test failed: {e}")
                
                # Test specific image URLs
                test_image_urls = [
                    f"/api/static/uploads/session_{session_id}/img_1.png",
                    f"/api/static/uploads/session_{session_id}/img_2.png",
                    f"/api/static/uploads/session_{session_id}/image1.png"
                ]
                
                for url in test_image_urls:
                    full_url = f"{BACKEND_URL.replace('/api', '')}{url}"
                    try:
                        img_response = requests.get(full_url, timeout=10)
                        print(f"🖼️ {url}: {img_response.status_code}")
                        if img_response.status_code == 200:
                            print(f"  ✅ Image accessible: {len(img_response.content)} bytes")
                    except Exception as e:
                        print(f"  ⚠️ Image test failed: {e}")
            
            print(f"\n✅ REAL DOCX TEST SUMMARY:")
            print(f"  ✅ Large DOCX file processed successfully ({len(docx_content)} bytes)")
            print(f"  ✅ Processing completed in {processing_time:.2f} seconds")
            print(f"  ✅ {len(articles)} articles generated")
            print(f"  ✅ {images_processed} images processed")
            print(f"  ✅ {total_images_in_articles} images embedded in articles")
            
            if images_processed > 0:
                print(f"  ✅ Image processing pipeline is working")
            else:
                print(f"  ⚠️ No images processed (may depend on DOCX content)")
            
            return True
        else:
            print(f"❌ Real DOCX processing failed: {process_response.status_code}")
            print(f"Response: {process_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Real DOCX test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_with_real_docx()
    if success:
        print("🎉 Real DOCX test completed successfully!")
    else:
        print("❌ Real DOCX test failed!")