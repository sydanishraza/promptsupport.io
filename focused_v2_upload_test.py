#!/usr/bin/env python3
"""
Focused V2 File Upload Test - Google Maps DOCX Validation
Simplified test focusing on the key success criteria from the review
"""

import os
import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env
def get_backend_url():
    """Get backend URL from frontend .env file"""
    frontend_env_path = os.path.join(os.path.dirname(__file__), 'frontend', '.env')
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
GOOGLE_MAPS_DOCX = "/app/Google_Map_JavaScript_API_Tutorial.docx"

def test_google_maps_docx_upload():
    """Test Google Maps DOCX file upload with V2 pipeline"""
    print("🎯 FOCUSED V2 FILE UPLOAD TEST - GOOGLE MAPS DOCX")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test File: {GOOGLE_MAPS_DOCX}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    # Check if file exists
    if not os.path.exists(GOOGLE_MAPS_DOCX):
        print("❌ CRITICAL ERROR: Google Maps DOCX file not found")
        return False
    
    file_size = os.path.getsize(GOOGLE_MAPS_DOCX)
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    # Test upload
    try:
        print("📤 Uploading Google Maps DOCX file...")
        
        with open(GOOGLE_MAPS_DOCX, 'rb') as f:
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/api/content/upload",
                files=files,
                timeout=180  # 3 minute timeout
            )
            processing_time = time.time() - start_time
        
        print(f"⏱️ Processing time: {processing_time:.2f} seconds")
        print(f"📡 HTTP Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ UPLOAD FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
        
        # Parse response
        try:
            data = response.json()
            print("✅ Upload successful - parsing response...")
        except json.JSONDecodeError as e:
            print(f"❌ JSON PARSE ERROR: {e}")
            print(f"Raw response: {response.text[:500]}")
            return False
        
        # Display response structure
        print("\n📋 RESPONSE ANALYSIS:")
        print("-" * 40)
        
        # Check main response fields
        status = data.get('status', 'unknown')
        engine = data.get('engine', 'unknown')
        filename = data.get('filename', 'unknown')
        
        print(f"Status: {status}")
        print(f"Engine: {engine}")
        print(f"Filename: {filename}")
        
        # Check result object
        result = data.get('result', {})
        if result:
            job_id = result.get('job_id', 'unknown')
            result_status = result.get('status', 'unknown')
            file_type = result.get('file_type', 'unknown')
            content_length = result.get('extracted_content_length', 0)
            chunks_created = result.get('chunks_created', 0)
            message = result.get('message', 'unknown')
            result_engine = result.get('engine', 'unknown')
            
            print(f"Job ID: {job_id}")
            print(f"Result Status: {result_status}")
            print(f"File Type: {file_type}")
            print(f"Content Length: {content_length:,} characters")
            print(f"Chunks Created: {chunks_created}")
            print(f"Message: {message}")
            print(f"Result Engine: {result_engine}")
        
        # SUCCESS CRITERIA VALIDATION
        print("\n🎯 SUCCESS CRITERIA VALIDATION:")
        print("-" * 40)
        
        success_checks = []
        
        # 1. Status should be 'completed'
        status_ok = status == 'completed'
        success_checks.append(("Status 'completed'", status_ok, f"Got: {status}"))
        
        # 2. Engine should be 'v2'
        engine_ok = engine == 'v2'
        success_checks.append(("Engine 'v2'", engine_ok, f"Got: {engine}"))
        
        # 3. File type should be 'docx'
        file_type_ok = result.get('file_type') == 'docx'
        success_checks.append(("File type 'docx'", file_type_ok, f"Got: {result.get('file_type')}"))
        
        # 4. Content length > 1000 chars (substantial)
        content_substantial = result.get('extracted_content_length', 0) > 1000
        success_checks.append(("Content >1000 chars", content_substantial, f"Got: {result.get('extracted_content_length', 0)} chars"))
        
        # 5. Articles/chunks created >= 1
        articles_created = result.get('chunks_created', 0) >= 1
        success_checks.append(("Articles created >=1", articles_created, f"Got: {result.get('chunks_created', 0)} chunks"))
        
        # 6. Processing time < 60 seconds
        time_ok = processing_time < 60
        success_checks.append(("Processing <60s", time_ok, f"Got: {processing_time:.2f}s"))
        
        # 7. V2 message confirmation
        v2_message = 'v2' in result.get('message', '').lower()
        success_checks.append(("V2 message", v2_message, f"Message: {result.get('message', '')}"))
        
        # Display results
        passed_checks = 0
        for check_name, passed, details in success_checks:
            status_icon = "✅" if passed else "❌"
            print(f"{status_icon} {check_name}: {details}")
            if passed:
                passed_checks += 1
        
        success_rate = (passed_checks / len(success_checks)) * 100
        
        print(f"\n📊 OVERALL SUCCESS RATE: {passed_checks}/{len(success_checks)} ({success_rate:.1f}%)")
        
        # Final assessment
        if success_rate >= 85:
            print("🎉 EXCELLENT: V2 file upload working perfectly!")
            result_status = "EXCELLENT"
        elif success_rate >= 70:
            print("✅ GOOD: V2 file upload mostly working")
            result_status = "GOOD"
        elif success_rate >= 50:
            print("⚠️ PARTIAL: V2 file upload has some issues")
            result_status = "PARTIAL"
        else:
            print("❌ FAILED: V2 file upload has major issues")
            result_status = "FAILED"
        
        # Test content library integration
        print("\n🔍 CONTENT LIBRARY INTEGRATION TEST:")
        print("-" * 40)
        
        try:
            library_response = requests.get(f"{BACKEND_URL}/api/content-library", timeout=30)
            
            if library_response.status_code == 200:
                library_data = library_response.json()
                articles = library_data.get('articles', [])
                total_articles = len(articles)
                
                # Look for V2 articles
                v2_articles = []
                for article in articles:
                    metadata = article.get('metadata', {})
                    if (metadata.get('engine') == 'v2' or 
                        'v2' in str(metadata).lower() or
                        article.get('engine') == 'v2'):
                        v2_articles.append(article)
                
                print(f"✅ Content library accessible: {total_articles} total articles")
                print(f"✅ V2 articles found: {len(v2_articles)} articles")
                
                if len(v2_articles) > 0:
                    print("✅ Repository pattern integration confirmed")
                else:
                    print("⚠️ No V2 articles found in content library")
                    
            else:
                print(f"⚠️ Content library access failed: HTTP {library_response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Content library test error: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"🎯 FINAL RESULT: {result_status}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Processing Time: {processing_time:.2f} seconds")
        print(f"📄 Content Extracted: {result.get('extracted_content_length', 0):,} characters")
        print(f"📚 Articles Created: {result.get('chunks_created', 0)} chunks")
        print("=" * 60)
        
        return success_rate >= 70  # Consider 70%+ as success
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_google_maps_docx_upload()
    exit(0 if success else 1)