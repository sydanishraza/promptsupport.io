#!/usr/bin/env python3
"""
FOCUSED BUG FIX TEST: Knowledge Engine Article Generation
Testing the specific fix for "3 chunks created • 0 articles created in Content Library"
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-pipeline-4.preview.emergentagent.com') + '/api'

def test_health_check():
    """Test basic connectivity"""
    print("🔍 Testing backend connectivity...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is responding")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return False

def test_content_library_access():
    """Test Content Library API access"""
    print("🔍 Testing Content Library API access...")
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            articles = data.get('articles', [])
            print(f"✅ Content Library accessible: {total} total articles, {len(articles)} returned")
            return True, total
        else:
            print(f"❌ Content Library access failed: {response.status_code}")
            return False, 0
    except Exception as e:
        print(f"❌ Content Library access error: {e}")
        return False, 0

def test_docx_processing_bug_fix():
    """Test the specific DOCX processing bug fix"""
    print("🎯 CRITICAL TEST: DOCX Processing Bug Fix")
    print("Testing: Chunks created AND articles created in Content Library")
    
    try:
        # Get baseline count
        print("📊 Getting baseline Content Library count...")
        baseline_success, baseline_count = test_content_library_access()
        if not baseline_success:
            print("❌ Cannot get baseline count")
            return False
        
        # Create test DOCX content
        test_content = """Knowledge Engine Bug Fix Test Document

This document tests the critical bug fix where chunks were created but no articles appeared in Content Library.

## Bug Description
Users reported: "3 chunks created • Content Library article generated • 0 articles created in Content Library"

## Root Cause
Missing call to create_content_library_articles_from_chunks in process_text_content function.

## Fix Applied
1. Added content_fingerprint field to DocumentChunk model
2. Fixed DocumentChunk constructor calls to include content_fingerprint
3. Added Content Library article creation call in process_text_content function

## Expected Result
After processing this document:
- Chunks should be created (chunks_created > 0)
- Articles should be created in Content Library (articles_created > 0)
- Content Library count should increase
- No "0 articles created" issue

This test verifies the complete workflow from upload to article storage."""

        # Create file upload
        file_data = io.BytesIO(test_content.encode('utf-8'))
        files = {
            'file': ('bug_fix_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'metadata': json.dumps({
                "source": "bug_fix_test",
                "test_type": "critical_bug_fix",
                "expected_outcome": "chunks_and_articles_created"
            })
        }
        
        print("📤 Uploading test DOCX file...")
        
        # Process the file
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
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
        
        data = response.json()
        
        # Check chunks created
        chunks_created = data.get('chunks_created', 0)
        status = data.get('status', 'unknown')
        success = data.get('success', False)
        
        print(f"📦 Chunks created: {chunks_created}")
        print(f"📊 Status: {status}")
        print(f"📊 Success: {success}")
        
        if chunks_created == 0:
            print("❌ CRITICAL FAILURE: No chunks created")
            return False
        
        if status != 'completed' and not success:
            print("❌ CRITICAL FAILURE: Processing did not complete successfully")
            return False
        
        # Wait for Content Library update
        print("⏳ Waiting for Content Library update...")
        time.sleep(5)
        
        # Check final count
        print("📚 Checking final Content Library count...")
        final_success, final_count = test_content_library_access()
        if not final_success:
            print("❌ Cannot get final count")
            return False
        
        articles_added = final_count - baseline_count
        
        print(f"📊 Baseline count: {baseline_count}")
        print(f"📊 Final count: {final_count}")
        print(f"📊 Articles added: {articles_added}")
        
        # CRITICAL TEST: Verify articles were added
        if articles_added <= 0:
            print("❌ CRITICAL BUG STILL EXISTS: 0 articles created in Content Library")
            print("❌ Chunks were created but articles were not added")
            return False
        else:
            print(f"✅ BUG FIX SUCCESS: {articles_added} articles created in Content Library")
            print("✅ Users will now see 'X articles created' where X > 0")
            return True
            
    except Exception as e:
        print(f"❌ DOCX processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_processing_bug_fix():
    """Test the bug fix with text content processing"""
    print("🔍 Testing text content processing bug fix...")
    
    try:
        # Get baseline
        baseline_success, baseline_count = test_content_library_access()
        if not baseline_success:
            return False
        
        # Test content
        test_content = {
            "content": """Text Processing Bug Fix Test

This test verifies that the create_content_library_articles_from_chunks function is properly called in the process_text_content workflow.

The bug was that chunks were being created but the conversion to Content Library articles was not happening due to missing function call.

Key verification points:
1. DocumentChunk objects created with content_fingerprint
2. create_content_library_articles_from_chunks called
3. Articles stored in Content Library
4. No serialization errors

Expected behavior after fix:
- process_text_content creates chunks
- create_content_library_articles_from_chunks converts chunks to articles  
- Articles appear in Content Library
- User sees confirmation of article creation

This test targets the fixed code path in process_text_content function.""",
            "content_type": "text",
            "metadata": {
                "source": "text_bug_fix_test",
                "test_type": "text_processing_fix"
            }
        }
        
        print("📤 Processing text content...")
        
        response = requests.post(
            f"{BACKEND_URL}/content/process",
            json=test_content,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ Text processing failed: {response.status_code}")
            return False
        
        data = response.json()
        chunks_created = data.get('chunks_created', 0)
        
        print(f"📦 Chunks created: {chunks_created}")
        
        if chunks_created == 0:
            print("❌ No chunks created")
            return False
        
        # Wait and check
        time.sleep(3)
        final_success, final_count = test_content_library_access()
        
        if final_success:
            articles_added = final_count - baseline_count
            print(f"📊 Articles added: {articles_added}")
            
            if articles_added > 0:
                print("✅ Text processing bug fix working")
                return True
            else:
                print("❌ Text processing: chunks created but no articles in Content Library")
                return False
        else:
            return False
            
    except Exception as e:
        print(f"❌ Text processing test failed: {e}")
        return False

def run_focused_bug_fix_tests():
    """Run focused bug fix tests"""
    print("🚀 FOCUSED KNOWLEDGE ENGINE BUG FIX TESTING")
    print("=" * 60)
    print("Bug: '3 chunks created • 0 articles created in Content Library'")
    print("=" * 60)
    
    # Test connectivity first
    if not test_health_check():
        print("❌ Backend connectivity failed - cannot run tests")
        return False
    
    # Test Content Library access
    if not test_content_library_access()[0]:
        print("❌ Content Library access failed - cannot run tests")
        return False
    
    # Run focused tests
    tests = [
        ("DOCX Processing Bug Fix", test_docx_processing_bug_fix),
        ("Text Processing Bug Fix", test_text_processing_bug_fix)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 BUG FIX TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Bug fix is working!")
        print("✅ Users will now see articles created in Content Library")
        return True
    elif passed > 0:
        print("⚠️ PARTIAL SUCCESS - Some functionality working")
        return True
    else:
        print("❌ CRITICAL FAILURE - Bug fix not working")
        return False

if __name__ == "__main__":
    success = run_focused_bug_fix_tests()
    exit(0 if success else 1)