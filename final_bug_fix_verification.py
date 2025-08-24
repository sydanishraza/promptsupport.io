#!/usr/bin/env python3
"""
FINAL BUG FIX VERIFICATION: Knowledge Engine Article Generation
Comprehensive testing of the fix for "3 chunks created • 0 articles created in Content Library"
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com') + '/api'

def test_training_endpoint_bug_fix():
    """Test the training endpoint bug fix - this is where the bug was originally reported"""
    print("🎯 CRITICAL TEST: Training Endpoint Bug Fix")
    print("Original bug: '3 chunks created • Content Library article generated • 0 articles created in Content Library'")
    
    try:
        # Get baseline count
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        if response.status_code != 200:
            print(f"❌ Cannot access Content Library: {response.status_code}")
            return False
        
        initial_count = response.json().get('total', 0)
        print(f"📊 Initial Content Library count: {initial_count}")
        
        # Create comprehensive test DOCX content
        test_content = """Knowledge Engine Training Endpoint Bug Fix Verification

This document comprehensively tests the critical bug fix for the Knowledge Engine training endpoint where articles were being created but not added to Content Library.

## Original Bug Report
Users reported seeing:
- "3 chunks created"
- "Content Library article generated" 
- "0 articles created in Content Library"

This indicated that the training process was creating articles but they were not being stored in the Content Library for users to access.

## Root Cause Analysis
Investigation revealed that:
1. The training endpoint was successfully creating articles
2. Articles were being stored in training sessions
3. The create_content_library_articles_from_chunks function was NOT being called
4. Articles remained in training sessions but never reached Content Library

## Fix Implementation
The fix involved adding the missing integration in the training endpoint:
1. Convert training articles to chunks format
2. Call create_content_library_articles_from_chunks function
3. Add articles to Content Library after training completion
4. Ensure users can access articles via Content Library API

## Expected Results After Fix
When this document is processed through the training endpoint:
1. Training articles should be created successfully
2. Articles should be converted to chunks format
3. create_content_library_articles_from_chunks should be called
4. Articles should be added to Content Library
5. Content Library count should increase
6. Users should see articles in Content Library, not 0 articles

## Test Verification Points
This comprehensive test verifies:
- Training endpoint creates articles (training functionality)
- Articles are added to Content Library (bug fix functionality)
- Content Library API returns new articles (user access)
- Complete workflow from training to user access works
- No more "0 articles created" issue

## Additional Content for Robust Testing
To ensure comprehensive testing with sufficient content:

### Section 1: Technical Implementation
The fix ensures proper integration between training article generation and Content Library storage systems.

### Section 2: User Experience Impact
Users will now see accurate feedback about article creation and can access articles immediately after training.

### Section 3: Quality Assurance
This test validates that the complete workflow from document upload through training to Content Library access is functional.

### Section 4: Future Reliability
The fix maintains the training functionality while adding the missing Content Library integration for complete user workflow."""

        # Create file upload for training endpoint
        file_data = io.BytesIO(test_content.encode('utf-8'))
        files = {
            'file': ('training_bug_fix_verification.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        # Use training endpoint template
        template_data = {
            'template_id': 'phase1_document_processing',
            'processing_instructions': 'Extract and process all content with Content Library integration',
            'output_requirements': {
                'format': 'html',
                'min_articles': 1,
                'max_articles': 5,
                'add_to_content_library': True
            }
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true',
            'template_instructions': json.dumps(template_data)
        }
        
        print("📤 Testing training endpoint with bug fix...")
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=120
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ Processing time: {processing_time:.2f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Training endpoint failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
        
        data = response.json()
        
        # Verify training results
        success = data.get('success', False)
        session_id = data.get('session_id')
        articles = data.get('articles', [])
        
        print(f"📊 Training success: {success}")
        print(f"📊 Session ID: {session_id}")
        print(f"📊 Articles created in training: {len(articles)}")
        
        if not success or len(articles) == 0:
            print("❌ Training endpoint did not create articles")
            return False
        
        print("✅ Training endpoint successfully created articles")
        
        # Wait for Content Library integration
        print("⏳ Waiting for Content Library integration...")
        time.sleep(5)
        
        # Check Content Library after processing
        final_response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        
        if final_response.status_code != 200:
            print(f"❌ Cannot check Content Library: {final_response.status_code}")
            return False
        
        final_data = final_response.json()
        final_count = final_data.get('total', 0)
        articles_added = final_count - initial_count
        
        print(f"📊 Final Content Library count: {final_count}")
        print(f"📊 Articles added to Content Library: {articles_added}")
        
        # CRITICAL VERIFICATION: Articles must be added to Content Library
        if articles_added <= 0:
            print("❌ CRITICAL BUG STILL EXISTS")
            print("❌ Training created articles but they were not added to Content Library")
            print("❌ Users will still see '0 articles created in Content Library'")
            return False
        
        # SUCCESS: Bug fix is working
        print("🎉 BUG FIX VERIFICATION SUCCESSFUL!")
        print(f"✅ Training created {len(articles)} articles")
        print(f"✅ Content Library received {articles_added} articles")
        print("✅ Users will now see articles in Content Library")
        print("✅ No more '0 articles created' issue")
        print("✅ Complete workflow from training to user access functional")
        
        # Additional verification: Check article accessibility
        articles_list = final_data.get('articles', [])
        if articles_list:
            print(f"✅ Articles are accessible via Content Library API")
            print(f"✅ Sample article: '{articles_list[0].get('title', 'Untitled')}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Training endpoint bug fix test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_processing_bug_fix():
    """Test the text processing bug fix"""
    print("\n🔍 Testing Text Processing Bug Fix")
    
    try:
        # Get baseline
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        if response.status_code != 200:
            return False
        
        initial_count = response.json().get('total', 0)
        
        # Test content
        test_content = {
            "content": """Text Processing Bug Fix Verification Test

This test verifies that the create_content_library_articles_from_chunks function is properly called in the text processing workflow.

The bug fix ensures that when text content is processed:
1. Chunks are created from the content
2. create_content_library_articles_from_chunks is called
3. Articles are added to Content Library
4. Users can access the articles

Key verification points:
- DocumentChunk objects created with content_fingerprint field
- Proper serialization without errors
- Content Library integration working
- Complete workflow functional

This test should result in both chunks being created AND articles being added to Content Library, resolving the '0 articles created' issue for text processing.""",
            "content_type": "text",
            "metadata": {
                "source": "text_bug_fix_verification",
                "test_type": "content_library_integration"
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
        
        # Wait and check Content Library
        time.sleep(3)
        final_response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        
        if final_response.status_code == 200:
            final_count = final_response.json().get('total', 0)
            articles_added = final_count - initial_count
            
            print(f"📊 Articles added to Content Library: {articles_added}")
            
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

def run_final_verification():
    """Run final comprehensive verification of the bug fix"""
    print("🚀 FINAL KNOWLEDGE ENGINE BUG FIX VERIFICATION")
    print("=" * 80)
    print("Bug: '3 chunks created • Content Library article generated • 0 articles created in Content Library'")
    print("Fix: Added create_content_library_articles_from_chunks call in processing workflows")
    print("=" * 80)
    
    # Test connectivity
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code != 200:
            print("❌ Backend connectivity failed")
            return False
        print("✅ Backend connectivity verified")
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return False
    
    # Test Content Library access
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        if response.status_code != 200:
            print("❌ Content Library access failed")
            return False
        
        data = response.json()
        total = data.get('total', 0)
        print(f"✅ Content Library accessible: {total} articles")
    except Exception as e:
        print(f"❌ Content Library access failed: {e}")
        return False
    
    # Run focused tests
    tests = [
        ("Training Endpoint Bug Fix (CRITICAL)", test_training_endpoint_bug_fix),
        ("Text Processing Bug Fix", test_text_processing_bug_fix)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
        
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
    
    # Final summary
    print(f"\n{'='*80}")
    print("🎯 FINAL BUG FIX VERIFICATION SUMMARY")
    print(f"{'='*80}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    # Determine overall status
    training_passed = results[0][1] if results else False  # Training endpoint is most critical
    
    if training_passed:
        print("\n🎉 CRITICAL BUG FIX SUCCESSFUL!")
        print("✅ Training endpoint now adds articles to Content Library")
        print("✅ Users will see articles created, not '0 articles created'")
        print("✅ Complete workflow from training to user access working")
        
        if passed == total:
            print("✅ ALL WORKFLOWS WORKING - Bug fix complete")
        else:
            print("⚠️ Some secondary workflows may need attention")
        
        return True
    else:
        print("\n❌ CRITICAL BUG FIX FAILED")
        print("❌ Training endpoint still not adding articles to Content Library")
        print("❌ Users will still see '0 articles created' issue")
        return False

if __name__ == "__main__":
    success = run_final_verification()
    exit(0 if success else 1)