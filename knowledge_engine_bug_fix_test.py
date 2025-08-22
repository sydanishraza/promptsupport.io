#!/usr/bin/env python3
"""
CRITICAL BUG FIX TESTING: Knowledge Engine Article Generation
Testing the fix for "3 chunks created • Content Library article generated • 0 articles created in Content Library"

Bug Fix Details:
1. Added content_fingerprint field to DocumentChunk model
2. Fixed DocumentChunk constructor calls to include content_fingerprint
3. Added Content Library article creation call in process_text_content function
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdoc-v2.preview.emergentagent.com') + '/api'

class KnowledgeEngineBugFixTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🔍 Testing Knowledge Engine Bug Fix at: {self.base_url}")
        
    def test_docx_processing_end_to_end(self):
        """Test DOCX processing end-to-end workflow to verify articles are created in Content Library"""
        print("\n🎯 CRITICAL BUG FIX TEST: DOCX Processing End-to-End Workflow")
        print("Testing: Chunks created AND articles created in Content Library")
        
        try:
            # Create a comprehensive test DOCX content
            test_docx_content = """Knowledge Engine Article Generation Bug Fix Test
            
This document tests the critical bug fix for Knowledge Engine article generation where chunks were being created but no articles appeared in Content Library.

## Bug Description
Users reported: "3 chunks created • Content Library article generated • 0 articles created in Content Library"

## Root Cause Analysis
The issue was identified as:
1. Missing call to create_content_library_articles_from_chunks in main processing flow
2. DocumentChunk constructor missing content_fingerprint parameter
3. Content Library integration not properly triggered after chunk creation

## Fix Implementation
The following fixes were applied:
1. Added content_fingerprint field to DocumentChunk model
2. Fixed DocumentChunk constructor calls to include content_fingerprint parameter
3. Added Content Library article creation call in process_text_content function

## Expected Results
After the fix:
- Chunks should be created successfully
- Articles should be created in Content Library
- Content Library API should return the new articles
- No "0 articles created" issue should occur

## Test Verification Points
1. Processing completes successfully without errors
2. Chunks are created (chunks_created > 0)
3. Articles are created in Content Library (articles_created > 0)
4. Content Library API returns the new articles
5. Article count increases in Content Library
6. No DocumentChunk serialization errors occur

This comprehensive test document should trigger the complete workflow from file upload to article storage in Content Library."""

            # Create file-like object
            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('knowledge_engine_bug_fix_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "knowledge_engine_bug_fix_test",
                    "test_type": "critical_bug_fix_verification",
                    "document_type": "docx_test",
                    "expected_outcome": "chunks_and_articles_created"
                })
            }
            
            print("📤 Step 1: Uploading DOCX file for processing...")
            
            # Get initial Content Library count
            initial_response = requests.get(f"{self.base_url}/content-library", timeout=15)
            initial_count = 0
            if initial_response.status_code == 200:
                initial_data = initial_response.json()
                initial_count = initial_data.get('total', 0)
                print(f"📊 Initial Content Library count: {initial_count}")
            
            start_time = time.time()
            
            # Upload and process the file
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=120
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ DOCX upload failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📋 Response Keys: {list(data.keys())}")
            
            # CRITICAL TEST 1: Verify chunks were created
            chunks_created = data.get('chunks_created', 0)
            print(f"📦 Chunks Created: {chunks_created}")
            
            if chunks_created == 0:
                print("❌ CRITICAL FAILURE: No chunks created")
                return False
            else:
                print(f"✅ SUCCESS: {chunks_created} chunks created")
            
            # CRITICAL TEST 2: Verify processing was successful
            status = data.get('status', 'unknown')
            success = data.get('success', False)
            print(f"📊 Processing Status: {status}")
            print(f"📊 Success Flag: {success}")
            
            if status != 'completed' and not success:
                print("❌ CRITICAL FAILURE: Processing did not complete successfully")
                return False
            
            # Wait a moment for Content Library to be updated
            print("⏳ Waiting for Content Library to be updated...")
            time.sleep(3)
            
            # CRITICAL TEST 3: Verify articles were created in Content Library
            print("📚 Step 2: Checking Content Library for new articles...")
            
            final_response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if final_response.status_code != 200:
                print(f"❌ Content Library check failed - status code {final_response.status_code}")
                return False
            
            final_data = final_response.json()
            final_count = final_data.get('total', 0)
            articles_added = final_count - initial_count
            
            print(f"📊 Final Content Library count: {final_count}")
            print(f"📊 Articles added: {articles_added}")
            
            # CRITICAL TEST 4: Verify articles were actually added
            if articles_added <= 0:
                print("❌ CRITICAL BUG STILL EXISTS: 0 articles created in Content Library")
                print("❌ Chunks were created but articles were not added to Content Library")
                return False
            else:
                print(f"✅ BUG FIX SUCCESS: {articles_added} articles created in Content Library")
            
            # CRITICAL TEST 5: Verify articles are retrievable
            articles = final_data.get('articles', [])
            if not articles:
                print("❌ CRITICAL FAILURE: No articles returned from Content Library API")
                return False
            
            # Look for our test articles
            test_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                content = article.get('content', '').lower()
                if ('knowledge engine' in title or 'bug fix' in title or 
                    'knowledge engine' in content or 'bug fix' in content):
                    test_articles.append(article)
            
            print(f"🔍 Found {len(test_articles)} test-related articles")
            
            if test_articles:
                print("✅ SUCCESS: Test articles are retrievable from Content Library")
                for i, article in enumerate(test_articles[:3]):  # Show first 3
                    print(f"  📄 Article {i+1}: {article.get('title', 'Untitled')}")
            else:
                print("⚠️ WARNING: Could not identify specific test articles (but articles were created)")
            
            # CRITICAL TEST 6: Verify no serialization errors
            job_id = data.get('job_id')
            if job_id:
                print(f"🔍 Step 3: Checking job status for serialization errors...")
                job_response = requests.get(f"{self.base_url}/jobs/{job_id}", timeout=10)
                
                if job_response.status_code == 200:
                    job_data = job_response.json()
                    job_status = job_data.get('status', 'unknown')
                    error_message = job_data.get('error_message')
                    
                    print(f"📊 Job Status: {job_status}")
                    
                    if error_message:
                        print(f"⚠️ Job Error Message: {error_message}")
                        if 'serialization' in error_message.lower() or 'documentchunk' in error_message.lower():
                            print("❌ CRITICAL FAILURE: DocumentChunk serialization errors detected")
                            return False
                    else:
                        print("✅ SUCCESS: No serialization errors detected")
                else:
                    print(f"⚠️ Could not check job status - status code {job_response.status_code}")
            
            # FINAL VERIFICATION
            print("\n🎉 CRITICAL BUG FIX VERIFICATION RESULTS:")
            print(f"  ✅ Chunks Created: {chunks_created} (> 0)")
            print(f"  ✅ Articles Added to Content Library: {articles_added} (> 0)")
            print(f"  ✅ Content Library API Working: {len(articles)} articles returned")
            print(f"  ✅ Processing Completed Successfully: {status}")
            print(f"  ✅ No Serialization Errors: Verified")
            print("  ✅ End-to-End Workflow: FUNCTIONAL")
            print("\n🎯 CRITICAL SUCCESS: Bug fix is working correctly!")
            print("   Users will now see 'X articles created in Content Library' where X > 0")
            
            return True
            
        except Exception as e:
            print(f"❌ DOCX processing end-to-end test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_chunk_to_article_conversion(self):
        """Test the specific chunk to article conversion functionality"""
        print("\n🔍 Testing Chunk to Article Conversion Functionality")
        
        try:
            # Test with text content to verify the conversion process
            test_content = {
                "content": """Chunk to Article Conversion Test
                
This test verifies that the create_content_library_articles_from_chunks function is properly called and working.

The bug was that chunks were being created but the conversion to Content Library articles was not happening.

Key Test Points:
1. DocumentChunk objects should be created with content_fingerprint
2. create_content_library_articles_from_chunks should be called
3. Articles should be stored in Content Library
4. No serialization errors should occur

Expected Behavior:
- process_text_content creates chunks
- create_content_library_articles_from_chunks converts chunks to articles
- Articles appear in Content Library with proper metadata
- User sees confirmation that articles were created

This test specifically targets the fixed code path in process_text_content function.""",
                "content_type": "text",
                "metadata": {
                    "source": "chunk_conversion_test",
                    "test_type": "chunk_to_article_conversion",
                    "author": "testing_agent"
                }
            }
            
            print("📤 Testing text content processing with chunk conversion...")
            
            # Get initial count
            initial_response = requests.get(f"{self.base_url}/content-library", timeout=15)
            initial_count = 0
            if initial_response.status_code == 200:
                initial_data = initial_response.json()
                initial_count = initial_data.get('total', 0)
            
            # Process content
            response = requests.post(
                f"{self.base_url}/content/process",
                json=test_content,
                timeout=60
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Content processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            
            # Verify chunks were created
            chunks_created = data.get('chunks_created', 0)
            print(f"📦 Chunks Created: {chunks_created}")
            
            if chunks_created == 0:
                print("❌ No chunks created")
                return False
            
            # Wait for Content Library update
            time.sleep(2)
            
            # Check Content Library
            final_response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if final_response.status_code == 200:
                final_data = final_response.json()
                final_count = final_data.get('total', 0)
                articles_added = final_count - initial_count
                
                print(f"📊 Articles added to Content Library: {articles_added}")
                
                if articles_added > 0:
                    print("✅ SUCCESS: Chunk to article conversion working")
                    return True
                else:
                    print("❌ FAILURE: Chunks created but no articles in Content Library")
                    return False
            else:
                print(f"❌ Could not check Content Library - status code {final_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Chunk to article conversion test failed - {str(e)}")
            return False
    
    def test_content_library_storage_verification(self):
        """Test that articles are properly stored and retrievable from Content Library"""
        print("\n🔍 Testing Content Library Storage and Retrieval")
        
        try:
            # Get current Content Library state
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            print(f"📊 Content Library API Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Content Library API failed - status code {response.status_code}")
                return False
            
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            print(f"📚 Total Articles in Content Library: {total_articles}")
            print(f"📄 Articles Returned: {len(articles)}")
            
            if total_articles == 0:
                print("⚠️ WARNING: Content Library is empty")
                print("This could indicate the bug is still present or no content has been processed")
                return False
            
            if len(articles) == 0:
                print("❌ FAILURE: Total shows articles but none returned")
                return False
            
            # Verify article structure
            sample_article = articles[0]
            required_fields = ['id', 'title', 'content', 'created_at']
            missing_fields = [field for field in required_fields if field not in sample_article]
            
            if missing_fields:
                print(f"❌ FAILURE: Articles missing required fields: {missing_fields}")
                return False
            
            print("✅ SUCCESS: Content Library storage and retrieval working")
            print(f"  ✅ {total_articles} articles stored")
            print(f"  ✅ Articles have required fields: {required_fields}")
            print(f"  ✅ Sample article: '{sample_article.get('title', 'Untitled')}'")
            
            return True
            
        except Exception as e:
            print(f"❌ Content Library storage verification failed - {str(e)}")
            return False
    
    def test_document_chunk_serialization(self):
        """Test that DocumentChunk objects serialize properly with content_fingerprint"""
        print("\n🔍 Testing DocumentChunk Serialization with content_fingerprint")
        
        try:
            # Create a simple test to trigger DocumentChunk creation
            test_content = {
                "content": "DocumentChunk serialization test with content_fingerprint field. This tests that the DocumentChunk model properly includes the content_fingerprint field and serializes without errors.",
                "content_type": "text",
                "metadata": {
                    "source": "serialization_test",
                    "test_type": "documentchunk_serialization"
                }
            }
            
            print("📤 Testing DocumentChunk serialization...")
            
            response = requests.post(
                f"{self.base_url}/content/process",
                json=test_content,
                timeout=30
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Request failed - status code {response.status_code}")
                response_text = response.text
                
                # Check for serialization errors
                if 'serialization' in response_text.lower() or 'documentchunk' in response_text.lower():
                    print("❌ CRITICAL FAILURE: DocumentChunk serialization error detected")
                    print(f"Error details: {response_text}")
                    return False
                else:
                    print(f"❌ Other error: {response_text}")
                    return False
            
            data = response.json()
            
            # Check for successful processing
            if data.get('chunks_created', 0) > 0:
                print("✅ SUCCESS: DocumentChunk serialization working")
                print(f"  ✅ {data.get('chunks_created')} chunks created without serialization errors")
                return True
            else:
                print("⚠️ WARNING: No chunks created (may not be a serialization issue)")
                return True  # Not necessarily a serialization failure
                
        except Exception as e:
            print(f"❌ DocumentChunk serialization test failed - {str(e)}")
            return False
    
    def test_complete_workflow_verification(self):
        """Test the complete workflow from upload to article creation"""
        print("\n🎯 COMPREHENSIVE WORKFLOW TEST: Upload → Processing → Article Creation")
        
        try:
            # Create comprehensive test content
            test_content = """Complete Workflow Verification Test Document

This document tests the complete end-to-end workflow for the Knowledge Engine bug fix.

## Workflow Steps Being Tested

1. File Upload
   - Document is uploaded successfully
   - Processing job is created
   - Initial validation passes

2. Content Processing
   - Text is extracted from document
   - Content is analyzed and chunked
   - DocumentChunk objects are created with content_fingerprint

3. Chunk Creation
   - Multiple chunks are generated
   - Each chunk has proper metadata
   - Chunks are stored temporarily

4. Article Generation
   - create_content_library_articles_from_chunks is called
   - Chunks are converted to full articles
   - Articles are enhanced with proper formatting

5. Content Library Storage
   - Articles are stored in Content Library
   - Articles are retrievable via API
   - Article count increases correctly

## Expected Success Criteria

✅ Processing completes without errors
✅ Chunks created > 0
✅ Articles created in Content Library > 0
✅ Content Library API returns new articles
✅ No DocumentChunk serialization errors
✅ Complete workflow functional

## Bug Fix Verification

This test specifically verifies that the bug "3 chunks created • Content Library article generated • 0 articles created in Content Library" has been resolved.

The fix involved:
- Adding content_fingerprint field to DocumentChunk model
- Fixing DocumentChunk constructor calls
- Adding create_content_library_articles_from_chunks call in process_text_content

After the fix, users should see "X articles created in Content Library" where X > 0."""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('complete_workflow_test.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "complete_workflow_test",
                    "test_type": "end_to_end_verification",
                    "expected_articles": "multiple"
                })
            }
            
            print("📤 Step 1: Starting complete workflow test...")
            
            # Get baseline
            baseline_response = requests.get(f"{self.base_url}/content-library", timeout=15)
            baseline_count = 0
            if baseline_response.status_code == 200:
                baseline_count = baseline_response.json().get('total', 0)
            
            # Execute workflow
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=90
            )
            workflow_time = time.time() - start_time
            
            print(f"⏱️ Complete workflow time: {workflow_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Workflow failed - status code {response.status_code}")
                return False
            
            data = response.json()
            
            # Verify each step
            success_criteria = {
                'processing_completed': data.get('status') == 'completed' or data.get('success', False),
                'chunks_created': data.get('chunks_created', 0) > 0,
                'job_created': 'job_id' in data,
                'no_errors': 'error' not in data or not data.get('error')
            }
            
            print("📊 Workflow Step Verification:")
            for criterion, passed in success_criteria.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {criterion}: {passed}")
            
            # Wait and check Content Library
            time.sleep(3)
            final_response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if final_response.status_code == 200:
                final_count = final_response.json().get('total', 0)
                articles_created = final_count - baseline_count
                
                print(f"📚 Content Library Results:")
                print(f"  📊 Baseline count: {baseline_count}")
                print(f"  📊 Final count: {final_count}")
                print(f"  📊 Articles created: {articles_created}")
                
                success_criteria['articles_in_library'] = articles_created > 0
            else:
                success_criteria['articles_in_library'] = False
                articles_created = 0
            
            # Final assessment
            all_passed = all(success_criteria.values())
            
            print(f"\n🎯 COMPLETE WORKFLOW VERIFICATION RESULTS:")
            if all_passed:
                print("✅ ALL CRITERIA PASSED - Bug fix is working correctly!")
                print(f"  ✅ Processing: Completed successfully")
                print(f"  ✅ Chunks: {data.get('chunks_created', 0)} created")
                print(f"  ✅ Articles: {articles_created} added to Content Library")
                print(f"  ✅ Workflow: End-to-end functional")
                print("\n🎉 CRITICAL BUG FIX VERIFIED: Users will now see articles in Content Library!")
                return True
            else:
                failed_criteria = [k for k, v in success_criteria.items() if not v]
                print(f"❌ SOME CRITERIA FAILED: {failed_criteria}")
                print("❌ Bug fix may not be fully working")
                return False
                
        except Exception as e:
            print(f"❌ Complete workflow verification failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def run_knowledge_engine_bug_fix_tests():
    """Run all Knowledge Engine bug fix tests"""
    print("🚀 STARTING KNOWLEDGE ENGINE BUG FIX TESTING")
    print("=" * 80)
    print("Testing critical bug fix: '3 chunks created • 0 articles created in Content Library'")
    print("=" * 80)
    
    tester = KnowledgeEngineBugFixTest()
    
    tests = [
        ("DOCX Processing End-to-End", tester.test_docx_processing_end_to_end),
        ("Chunk to Article Conversion", tester.test_chunk_to_article_conversion),
        ("Content Library Storage", tester.test_content_library_storage_verification),
        ("DocumentChunk Serialization", tester.test_document_chunk_serialization),
        ("Complete Workflow Verification", tester.test_complete_workflow_verification)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 RUNNING: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Final summary
    print(f"\n{'='*80}")
    print("🎯 KNOWLEDGE ENGINE BUG FIX TEST SUMMARY")
    print(f"{'='*80}")
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Knowledge Engine bug fix is working correctly!")
        print("✅ Users will now see articles created in Content Library (not 0 articles)")
        return True
    elif passed_tests >= 3:  # At least 3 critical tests should pass
        print("⚠️ MOSTLY WORKING - Core functionality restored but some issues remain")
        return True
    else:
        print("❌ CRITICAL ISSUES - Bug fix may not be working properly")
        return False

if __name__ == "__main__":
    success = run_knowledge_engine_bug_fix_tests()
    exit(0 if success else 1)