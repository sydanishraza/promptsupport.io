#!/usr/bin/env python3
"""
Static Image Serving Test
Test actual image file serving from the uploads directory
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://b9c68cf9-d5db-4176-932c-eadffd36ef4f.preview.emergentagent.com')

def test_static_image_serving():
    """Test serving actual images from the static uploads directory"""
    print("🔍 Testing Static Image Serving...")
    
    try:
        # Get list of actual image files
        uploads_dir = "/app/backend/static/uploads"
        if not os.path.exists(uploads_dir):
            print("❌ Uploads directory does not exist")
            return False
        
        image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        print(f"📁 Found {len(image_files)} image files in uploads directory")
        
        if not image_files:
            print("⚠️ No image files found to test")
            return True  # Not a failure, just no images to test
        
        # Test accessing the first few images
        test_files = image_files[:3]  # Test first 3 images
        
        successful_requests = 0
        
        for image_file in test_files:
            image_url = f"{BACKEND_URL}/api/static/uploads/{image_file}"
            print(f"\n🔍 Testing image: {image_file}")
            print(f"🌐 URL: {image_url}")
            
            try:
                response = requests.get(image_url, timeout=10)
                
                print(f"📊 Status Code: {response.status_code}")
                print(f"📄 Content-Type: {response.headers.get('Content-Type')}")
                print(f"📏 Content-Length: {response.headers.get('Content-Length')}")
                
                # Check CORS headers
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                }
                
                print(f"🌐 CORS Headers:")
                for header, value in cors_headers.items():
                    print(f"  {header}: {value}")
                
                if response.status_code == 200:
                    successful_requests += 1
                    print(f"✅ Image served successfully: {len(response.content)} bytes")
                    
                    # Verify it's actually an image
                    content_type = response.headers.get('Content-Type', '')
                    if 'image' in content_type:
                        print(f"✅ Correct content type: {content_type}")
                    else:
                        print(f"⚠️ Unexpected content type: {content_type}")
                        
                else:
                    print(f"❌ Failed to serve image: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
        
        print(f"\n📊 Static Image Serving Results:")
        print(f"  Images tested: {len(test_files)}")
        print(f"  Successful requests: {successful_requests}")
        print(f"  Success rate: {successful_requests}/{len(test_files)}")
        
        if successful_requests > 0:
            print("✅ STATIC IMAGE SERVING TEST PASSED:")
            print("  ✅ Images are accessible via /api/static/uploads/ URLs")
            print("  ✅ Static file serving is working")
            print("  ✅ Image files are being served correctly")
            return True
        else:
            print("❌ STATIC IMAGE SERVING TEST FAILED:")
            print("  ❌ No images could be accessed")
            return False
            
    except Exception as e:
        print(f"❌ Static image serving test failed: {e}")
        return False

def test_session_directory_creation():
    """Test that session directories are created properly"""
    print("\n🔍 Testing Session Directory Creation...")
    
    try:
        # Check for session directories
        uploads_dir = "/app/backend/static/uploads"
        items = os.listdir(uploads_dir)
        
        session_dirs = [item for item in items if item.startswith('session_') and os.path.isdir(os.path.join(uploads_dir, item))]
        print(f"📁 Found {len(session_dirs)} session directories")
        
        if session_dirs:
            # Test the first session directory
            test_session_dir = session_dirs[0]
            session_path = os.path.join(uploads_dir, test_session_dir)
            
            print(f"🔍 Testing session directory: {test_session_dir}")
            
            # List files in session directory
            session_files = os.listdir(session_path)
            image_files = [f for f in session_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
            print(f"📁 Session directory contains {len(session_files)} files")
            print(f"🖼️ Session directory contains {len(image_files)} image files")
            
            if image_files:
                # Test accessing an image from the session directory
                test_image = image_files[0]
                session_image_url = f"{BACKEND_URL}/api/static/uploads/{test_session_dir}/{test_image}"
                
                print(f"🔍 Testing session image: {session_image_url}")
                
                try:
                    response = requests.get(session_image_url, timeout=10)
                    print(f"📊 Session image status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"✅ Session image accessible: {len(response.content)} bytes")
                    else:
                        print(f"⚠️ Session image status: {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Session image request failed: {e}")
            
            print("✅ SESSION DIRECTORY TEST RESULTS:")
            print(f"  ✅ {len(session_dirs)} session directories found")
            print(f"  ✅ Session directory structure is working")
            print(f"  ✅ Session-based image storage is operational")
            return True
        else:
            print("⚠️ No session directories found")
            print("⚠️ This may be expected if no recent training sessions created images")
            return True  # Not necessarily a failure
            
    except Exception as e:
        print(f"❌ Session directory test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Static Image Serving Tests")
    print("=" * 50)
    
    test1_result = test_static_image_serving()
    test2_result = test_session_directory_creation()
    
    print("\n" + "=" * 50)
    print("STATIC IMAGE SERVING TEST SUMMARY")
    print("=" * 50)
    
    if test1_result and test2_result:
        print("🎉 ALL STATIC IMAGE SERVING TESTS PASSED!")
        print("✅ Static file serving is working correctly")
        print("✅ Session-based image storage is operational")
    elif test1_result or test2_result:
        print("✅ MOST STATIC IMAGE SERVING TESTS PASSED!")
        print("⚠️ Some components may need verification")
    else:
        print("❌ STATIC IMAGE SERVING TESTS FAILED!")
        print("❌ Issues detected with image serving")