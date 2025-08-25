#!/usr/bin/env python3
"""
Simple Image Processing Debug Test
Quick test to understand the image processing issue
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com') + '/api'

def simple_image_test():
    """Simple test with a small DOCX file"""
    print("🔍 Simple Image Processing Debug Test")
    print("=" * 50)
    
    # Test with the smallest DOCX file
    test_file = '/app/simple_test.docx'
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📄 Testing with: {os.path.basename(test_file)}")
    print(f"📊 File size: {os.path.getsize(test_file)} bytes")
    
    try:
        with open(test_file, 'rb') as f:
            files = {
                'file': (os.path.basename(test_file), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true'
            }
            
            print("📤 Sending request...")
            
            response = requests.post(
                f"{BACKEND_URL}/training/process",
                files=files,
                data=form_data,
                timeout=60
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Success: {data.get('success', False)}")
                print(f"📋 Session ID: {data.get('session_id')}")
                print(f"🖼️ Images processed: {data.get('images_processed', 0)}")
                print(f"📚 Articles: {len(data.get('articles', []))}")
                
                # Check if session directory was created
                session_id = data.get('session_id')
                if session_id:
                    session_dir = f"/app/backend/static/uploads/session_{session_id}"
                    if os.path.exists(session_dir):
                        files_in_dir = os.listdir(session_dir)
                        print(f"📁 Session directory: {len(files_in_dir)} files")
                    else:
                        print(f"📁 No session directory created")
                
                # Check article content for image references
                articles = data.get('articles', [])
                if articles:
                    content = articles[0].get('content', '') or articles[0].get('html', '')
                    print(f"📄 Article content length: {len(content)} chars")
                    
                    # Look for image indicators
                    indicators = {
                        'figure_tags': content.count('<figure'),
                        'img_tags': content.count('<img'),
                        'api_static': content.count('/api/static'),
                        'image_blocks': content.count('IMAGE_BLOCK:'),
                        'image_tokens': content.count('[IMAGE:')
                    }
                    
                    print(f"🔍 Image indicators: {indicators}")
                    
                    if any(indicators.values()):
                        print("✅ Article contains image references")
                    else:
                        print("❌ Article contains no image references")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

def check_backend_health():
    """Check if backend is responding"""
    print("\n🔍 Backend Health Check")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"📊 Health status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"📋 Services: {list(data.get('services', {}).keys())}")
        else:
            print(f"❌ Backend health check failed")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def main():
    """Run the simple debug test"""
    check_backend_health()
    simple_image_test()

if __name__ == "__main__":
    main()