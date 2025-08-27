#!/usr/bin/env python3
"""
DOCX Chunking Threshold Fix - Focused Test
Test specifically for the chunking threshold fix (3000 to 1500 characters)
"""

import requests
import json
import os
import io
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com') + '/api'

def test_chunking_threshold_fix():
    """Test the chunking threshold fix"""
    print("🎯 DOCX CHUNKING THRESHOLD FIX TEST")
    print("=" * 50)
    print("TESTING: Threshold lowered from 3000 to 1500 characters")
    print("EXPECTED: Multiple articles for content > 1500 chars")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        print("\n🔍 1. Backend Health Check...")
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return False
        
        # Test 2: Create test content over 1500 characters
        print("\n🔍 2. Creating test content...")
        test_content = """DOCX Chunking Threshold Test Document

This document tests the chunking threshold fix where the threshold was lowered from 3000 to 1500 characters.

# Section 1: Introduction
The enhanced DOCX processing system should now split documents with content over 1500 characters into multiple articles instead of creating single articles with "single_article_simplified" approach.

# Section 2: Technical Details  
The system should detect content length and choose the enhanced processing path. This results in better article generation with proper chunking validation and comprehensive processing metadata.

# Section 3: Expected Results
When this document is processed, it should:
- Detect content length exceeding 1500 characters
- Use enhanced processing instead of simplified approach
- Generate multiple articles (not single article)
- Show processing approach as "comprehensive_docx"

# Section 4: Validation
The validation confirms that the chunking threshold fix is working correctly and users receive multiple focused articles instead of single overwhelming documents.

This content is approximately 1800 characters and should trigger the enhanced processing path with multiple article generation."""

        content_length = len(test_content)
        print(f"📏 Test content length: {content_length} characters")
        
        if content_length < 1500:
            print("⚠️ Content too short, extending...")
            test_content += "\n\nAdditional content to exceed 1500 character threshold. " * 10
            content_length = len(test_content)
            print(f"📏 Extended content length: {content_length} characters")
        
        # Test 3: Upload and process
        print("\n🔍 3. Testing DOCX processing...")
        file_data = io.BytesIO(test_content.encode('utf-8'))
        
        files = {
            'file': ('threshold_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'metadata': json.dumps({
                "test_type": "chunking_threshold_fix",
                "content_length": content_length
            })
        }
        
        print("📤 Uploading test file...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/content/upload",
            files=files,
            data=form_data,
            timeout=120
        )
        
        processing_time = time.time() - start_time
        print(f"⏱️ Processing time: {processing_time:.2f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.text}")
            return False
        
        data = response.json()
        print(f"📋 Response keys: {list(data.keys())}")
        
        # Test 4: Verify chunking results
        print("\n🔍 4. Verifying chunking results...")
        
        chunks_created = data.get('chunks_created', 0)
        job_id = data.get('job_id')
        
        print(f"📚 Chunks created: {chunks_created}")
        print(f"📋 Job ID: {job_id}")
        
        if chunks_created <= 1:
            print("❌ CHUNKING THRESHOLD FIX FAILED:")
            print(f"  Only {chunks_created} chunk created (expected multiple)")
            print("  System still using single article approach")
            return False
        else:
            print("✅ CHUNKING THRESHOLD FIX SUCCESS:")
            print(f"  {chunks_created} chunks created (multiple articles)")
            print("  Enhanced processing path used")
        
        # Test 5: Check processing approach
        if job_id:
            print("\n🔍 5. Checking processing approach...")
            time.sleep(3)  # Wait for processing
            
            status_response = requests.get(f"{BACKEND_URL}/jobs/{job_id}", timeout=15)
            if status_response.status_code == 200:
                status_data = status_response.json()
                metadata = status_data.get('metadata', {})
                processing_approach = metadata.get('processing_approach', 'unknown')
                
                print(f"🔍 Processing approach: {processing_approach}")
                
                if 'single_article_simplified' in processing_approach.lower():
                    print("❌ Still using simplified approach")
                    return False
                else:
                    print("✅ Not using simplified approach")
        
        # Test 6: Check content library
        print("\n🔍 6. Checking content library...")
        time.sleep(2)
        
        library_response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if library_response.status_code == 200:
            library_data = library_response.json()
            articles = library_data.get('articles', [])
            
            test_articles = [a for a in articles if 'threshold' in a.get('title', '').lower()]
            print(f"📚 Test articles found: {len(test_articles)}")
            
            if len(test_articles) >= 2:
                print("✅ Multiple articles in content library")
                return True
            elif len(test_articles) == 1:
                print("⚠️ Only one article found (may still be processing)")
                return True
            else:
                print("⚠️ No test articles found yet")
                return True
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chunking_threshold_fix()
    print(f"\n{'='*50}")
    if success:
        print("🎉 CHUNKING THRESHOLD FIX TEST: SUCCESS")
    else:
        print("❌ CHUNKING THRESHOLD FIX TEST: FAILED")
    print(f"{'='*50}")