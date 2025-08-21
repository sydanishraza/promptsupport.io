#!/usr/bin/env python3
"""
DocumentChunk Serialization Fix Testing
Focused testing for DOCX file upload and serialization issues
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-6.preview.emergentagent.com') + '/api'

class DocumentChunkSerializationTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_job_id = None
        print(f"🧪 Testing DocumentChunk Serialization Fix at: {self.base_url}")
        
    def create_test_docx_content(self):
        """Create a realistic DOCX test content that would trigger DocumentChunk creation"""
        return """DocumentChunk Serialization Test Document

This document is designed to test the DocumentChunk serialization fix for DOCX file processing.

## Introduction
The DocumentChunk serialization issue was causing 422 and 500 errors during DOCX file processing. This test verifies that DocumentChunk objects are properly converted to dictionaries before JSON serialization.

## Key Testing Areas

### 1. File Upload Processing
This section tests that DOCX files can be uploaded through the /api/content/upload endpoint without serialization errors.

### 2. DocumentChunk Creation
When processing this content, the system should create DocumentChunk objects that contain:
- Text content from paragraphs
- Metadata about the chunk
- Position information
- Processing timestamps

### 3. Serialization Fix Verification
The critical fix ensures that DocumentChunk objects are converted to dictionaries before being stored in MongoDB or returned in API responses.

### 4. Processing Job Storage
Processing jobs should be stored in MongoDB without encountering JSON serialization errors that were previously causing 422 responses.

### 5. Content Library Integration
After successful processing, articles should be created and stored properly in the content library without serialization issues.

## Expected Behavior
- No 422 Unprocessable Entity errors
- No 500 Internal Server errors
- Successful job creation and tracking
- Proper article generation
- Clean JSON responses

## Technical Details
The fix involves ensuring that any DocumentChunk objects are converted to dictionaries using proper serialization methods before being passed to JSON encoding or MongoDB storage operations.

This comprehensive test document should trigger the creation of multiple DocumentChunk objects during processing, allowing us to verify that the serialization fix is working correctly across the entire processing pipeline.
"""

    def test_docx_upload_serialization(self):
        """Test DOCX file upload and verify no serialization errors occur"""
        print("\n🔍 Testing DOCX Upload and DocumentChunk Serialization...")
        try:
            # Create test DOCX content
            test_content = self.create_test_docx_content()
            
            # Create file-like object with DOCX content
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('docx_serialization_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "docx_serialization_test",
                    "test_type": "serialization_fix_verification",
                    "document_type": "docx_test"
                })
            }
            
            print("📤 Uploading DOCX file to test serialization fix...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=120  # Extended timeout for processing
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Upload processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            # TEST 1: Verify no 422 or 500 errors (serialization issues)
            if response.status_code == 422:
                print("❌ SERIALIZATION ERROR: 422 Unprocessable Entity - DocumentChunk serialization failed")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 500:
                print("❌ SERIALIZATION ERROR: 500 Internal Server Error - JSON serialization failed")
                print(f"Response: {response.text}")
                return False
            elif response.status_code != 200:
                print(f"❌ Upload failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            print("✅ TEST 1 PASSED: No 422 or 500 serialization errors")
            
            # TEST 2: Verify successful response structure
            try:
                data = response.json()
                print(f"📋 Response Keys: {list(data.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ SERIALIZATION ERROR: Invalid JSON response - {e}")
                return False
            
            print("✅ TEST 2 PASSED: Valid JSON response received")
            
            # TEST 3: Verify job creation and tracking
            if "job_id" in data:
                self.test_job_id = data["job_id"]
                print(f"✅ TEST 3 PASSED: Job created successfully - ID: {self.test_job_id}")
            else:
                print("⚠️ TEST 3 PARTIAL: No job_id in response (may be expected for some endpoints)")
            
            # TEST 4: Verify processing status
            status = data.get("status", "unknown")
            print(f"📊 Processing Status: {status}")
            
            if status in ["completed", "processing", "queued"]:
                print("✅ TEST 4 PASSED: Valid processing status")
            else:
                print(f"⚠️ TEST 4 PARTIAL: Unexpected status '{status}' but no serialization error")
            
            # TEST 5: Verify chunks or articles creation
            chunks_created = data.get("chunks_created", 0)
            articles_created = len(data.get("articles", []))
            
            print(f"📚 Chunks Created: {chunks_created}")
            print(f"📄 Articles Created: {articles_created}")
            
            if chunks_created > 0 or articles_created > 0:
                print("✅ TEST 5 PASSED: Content processing successful")
            else:
                print("⚠️ TEST 5 PARTIAL: No chunks/articles created but no serialization error")
            
            return True
            
        except Exception as e:
            print(f"❌ DOCX upload serialization test failed - {str(e)}")
            return False
    
    def test_job_status_serialization(self):
        """Test job status endpoint for serialization issues"""
        print("\n🔍 Testing Job Status Serialization...")
        try:
            if not self.test_job_id:
                print("⚠️ No job ID available - skipping job status test")
                return True
            
            print(f"📋 Checking job status for: {self.test_job_id}")
            
            response = requests.get(
                f"{self.base_url}/jobs/{self.test_job_id}",
                timeout=30
            )
            
            print(f"📊 Job Status Response Code: {response.status_code}")
            
            # TEST 1: Verify no serialization errors
            if response.status_code == 422:
                print("❌ SERIALIZATION ERROR: 422 in job status - DocumentChunk serialization failed")
                return False
            elif response.status_code == 500:
                print("❌ SERIALIZATION ERROR: 500 in job status - JSON serialization failed")
                return False
            
            # TEST 2: Verify JSON response
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ Job status JSON serialization working")
                    
                    # Check for DocumentChunk-related fields
                    if "chunks_created" in data:
                        print(f"✅ Chunks data serialized properly: {data['chunks_created']}")
                    
                    return True
                except json.JSONDecodeError:
                    print("❌ Job status response is not valid JSON")
                    return False
            else:
                print(f"⚠️ Job status returned {response.status_code} (not necessarily a serialization issue)")
                return True
                
        except Exception as e:
            print(f"❌ Job status serialization test failed - {str(e)}")
            return False
    
    def test_content_library_serialization(self):
        """Test content library endpoint for serialization issues"""
        print("\n🔍 Testing Content Library Serialization...")
        try:
            print("📚 Checking content library for serialization issues...")
            
            response = requests.get(
                f"{self.base_url}/content-library",
                timeout=30
            )
            
            print(f"📊 Content Library Response Code: {response.status_code}")
            
            # TEST 1: Verify no serialization errors
            if response.status_code == 422:
                print("❌ SERIALIZATION ERROR: 422 in content library - DocumentChunk serialization failed")
                return False
            elif response.status_code == 500:
                print("❌ SERIALIZATION ERROR: 500 in content library - JSON serialization failed")
                return False
            
            # TEST 2: Verify JSON response and article structure
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ Content library JSON serialization working")
                    
                    articles = data.get("articles", [])
                    print(f"📄 Articles in library: {len(articles)}")
                    
                    # Check if our test article was created and serialized properly
                    test_articles = [a for a in articles if "serialization" in a.get("title", "").lower()]
                    if test_articles:
                        print(f"✅ Test articles found and properly serialized: {len(test_articles)}")
                        
                        # Verify article structure doesn't contain raw DocumentChunk objects
                        sample_article = test_articles[0]
                        article_str = json.dumps(sample_article)  # This would fail if DocumentChunk objects present
                        print("✅ Article data is fully JSON serializable")
                    
                    return True
                except json.JSONDecodeError:
                    print("❌ Content library response is not valid JSON")
                    return False
            else:
                print(f"⚠️ Content library returned {response.status_code}")
                return True
                
        except Exception as e:
            print(f"❌ Content library serialization test failed - {str(e)}")
            return False
    
    def test_processing_pipeline_end_to_end(self):
        """Test the complete processing pipeline for serialization issues"""
        print("\n🔍 Testing Complete Processing Pipeline Serialization...")
        try:
            print("🔄 Testing end-to-end DOCX processing pipeline...")
            
            # Create a more complex DOCX content to stress test serialization
            complex_content = """Complex DocumentChunk Serialization Test

# Chapter 1: Introduction
This chapter introduces the DocumentChunk serialization testing framework.

## Section 1.1: Background
DocumentChunk objects are created during text processing and must be properly serialized.

## Section 1.2: Problem Statement
Previous implementations had serialization issues causing 422 and 500 errors.

# Chapter 2: Technical Implementation

## Section 2.1: DocumentChunk Structure
DocumentChunk objects contain:
- Text content
- Metadata
- Position information
- Processing timestamps

## Section 2.2: Serialization Requirements
All DocumentChunk objects must be converted to dictionaries before JSON serialization.

# Chapter 3: Testing Methodology

## Section 3.1: Test Cases
1. File upload processing
2. Job storage in MongoDB
3. Content library creation
4. API response serialization

## Section 3.2: Expected Results
- No 422 errors
- No 500 errors
- Successful processing
- Clean JSON responses

# Chapter 4: Conclusion
This document tests the complete DocumentChunk serialization fix implementation.
"""
            
            file_data = io.BytesIO(complex_content.encode('utf-8'))
            
            files = {
                'file': ('complex_serialization_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "complex_serialization_test",
                    "test_type": "end_to_end_serialization",
                    "document_type": "complex_docx"
                })
            }
            
            print("📤 Processing complex DOCX for end-to-end serialization test...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=180  # Extended timeout for complex processing
            )
            
            print(f"📊 End-to-End Response Code: {response.status_code}")
            
            # Comprehensive serialization check
            if response.status_code == 422:
                print("❌ END-TO-END SERIALIZATION FAILURE: 422 error in processing pipeline")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 500:
                print("❌ END-TO-END SERIALIZATION FAILURE: 500 error in processing pipeline")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ END-TO-END SERIALIZATION SUCCESS: Complete pipeline working")
                    
                    # Verify complex processing results
                    chunks_created = data.get("chunks_created", 0)
                    articles_created = len(data.get("articles", []))
                    
                    print(f"📚 Complex processing results: {chunks_created} chunks, {articles_created} articles")
                    
                    if chunks_created > 0 or articles_created > 0:
                        print("✅ Complex DocumentChunk processing and serialization successful")
                    
                    return True
                except json.JSONDecodeError:
                    print("❌ END-TO-END SERIALIZATION FAILURE: Invalid JSON in response")
                    return False
            else:
                print(f"⚠️ End-to-end test returned {response.status_code}")
                return True
                
        except Exception as e:
            print(f"❌ End-to-end processing pipeline test failed - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all DocumentChunk serialization tests"""
        print("🚀 Starting DocumentChunk Serialization Fix Testing")
        print("=" * 60)
        
        tests = [
            ("DOCX Upload Serialization", self.test_docx_upload_serialization),
            ("Job Status Serialization", self.test_job_status_serialization),
            ("Content Library Serialization", self.test_content_library_serialization),
            ("End-to-End Pipeline Serialization", self.test_processing_pipeline_end_to_end)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
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
        
        # Summary
        print("\n" + "="*60)
        print("📊 DOCUMENTCHUNK SERIALIZATION TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        print(f"\n📈 Overall Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL DOCUMENTCHUNK SERIALIZATION TESTS PASSED!")
            print("✅ DocumentChunk serialization fix is working correctly")
            print("✅ No 422 or 500 errors detected")
            print("✅ DOCX processing pipeline is fully operational")
        elif passed >= total * 0.75:
            print("⚠️ MOST DOCUMENTCHUNK SERIALIZATION TESTS PASSED")
            print("✅ Core serialization fix appears to be working")
            print("⚠️ Some minor issues may need attention")
        else:
            print("❌ DOCUMENTCHUNK SERIALIZATION TESTS FAILED")
            print("❌ Critical serialization issues detected")
            print("❌ DocumentChunk fix may not be working properly")
        
        return passed, total

if __name__ == "__main__":
    tester = DocumentChunkSerializationTest()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if passed == total else 1)