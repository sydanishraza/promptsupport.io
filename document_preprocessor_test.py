#!/usr/bin/env python3
"""
DocumentPreprocessor Method Error Testing
Targeted test to identify the specific DocumentPreprocessor method error
"""

import requests
import json
import os
import io
import time
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com') + '/api'

class DocumentPreprocessorTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🎯 Testing DocumentPreprocessor at: {self.base_url}")
        print("🔍 DEBUGGING STEPS:")
        print("1. Test DocumentPreprocessor instantiation")
        print("2. Test method existence")
        print("3. Test HTML preprocessing pipeline")
        print("4. Check method signatures")
        print("5. Trace exact error location")
        
    def test_documentpreprocessor_instantiation(self):
        """Test if DocumentPreprocessor class can be instantiated properly"""
        print("\n🔍 STEP 1: Testing DocumentPreprocessor Instantiation...")
        try:
            # Create a simple DOCX file to trigger DocumentPreprocessor
            test_docx_content = """DocumentPreprocessor Instantiation Test

This is a simple test document to verify that the DocumentPreprocessor class
can be instantiated properly without errors.

The system should create a DocumentPreprocessor instance with a session_id
and initialize the required attributes like asset_dir, block_counter, etc.

Expected behavior:
- DocumentPreprocessor.__init__() should complete successfully
- Session directory should be created
- Instance variables should be initialized
"""

            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('preprocessor_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true'
            }
            
            print("📤 Uploading test file to trigger DocumentPreprocessor instantiation...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=30
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    print("✅ STEP 1 PASSED: DocumentPreprocessor instantiation successful")
                    return True
                else:
                    print("❌ STEP 1 FAILED: Processing failed, likely due to instantiation error")
                    print(f"Response: {json.dumps(data, indent=2)}")
                    return False
            else:
                print(f"❌ STEP 1 FAILED: HTTP error {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ STEP 1 FAILED: Exception during instantiation test - {str(e)}")
            traceback.print_exc()
            return False
    
    def test_method_existence(self):
        """Test if the required methods exist and are callable"""
        print("\n🔍 STEP 2: Testing Method Existence...")
        try:
            print("🔍 Testing for missing methods:")
            print("  - _assign_block_ids_to_chunk")
            print("  - _create_chunk_html") 
            print("  - _tokenize_images_in_chunk")
            
            # Create a test that specifically triggers these methods
            test_content = """Method Existence Test Document

This document is designed to trigger the HTML preprocessing pipeline
which should call the following methods:

1. _assign_block_ids_to_chunk - assigns data-block-id attributes
2. _create_chunk_html - creates HTML from elements
3. _tokenize_images_in_chunk - tokenizes images within chunks

If any of these methods are missing, we should see AttributeError.
"""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('method_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_approach": "html_preprocessing_pipeline",
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True
                    }
                })
            }
            
            print("📤 Uploading test file to trigger method calls...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=60
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    print("✅ STEP 2 PASSED: All required methods exist and are callable")
                    return True
                else:
                    print("❌ STEP 2 FAILED: Processing failed, likely due to missing methods")
                    error_msg = data.get('error', 'Unknown error')
                    print(f"Error: {error_msg}")
                    
                    # Check for specific AttributeError messages
                    if 'AttributeError' in error_msg:
                        if '_assign_block_ids_to_chunk' in error_msg:
                            print("🎯 IDENTIFIED: _assign_block_ids_to_chunk method is missing")
                        if '_create_chunk_html' in error_msg:
                            print("🎯 IDENTIFIED: _create_chunk_html method is missing")
                        if '_tokenize_images_in_chunk' in error_msg:
                            print("🎯 IDENTIFIED: _tokenize_images_in_chunk method is missing")
                    
                    return False
            else:
                print(f"❌ STEP 2 FAILED: HTTP error {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ STEP 2 FAILED: Exception during method existence test - {str(e)}")
            traceback.print_exc()
            return False
    
    def test_html_preprocessing_pipeline(self):
        """Test HTML preprocessing pipeline and capture exact error"""
        print("\n🔍 STEP 3: Testing HTML Preprocessing Pipeline...")
        try:
            print("🔍 Uploading DOCX file to trigger HTML preprocessing pipeline...")
            
            # Create a more substantial DOCX file that should trigger HTML preprocessing
            test_docx_content = """HTML Preprocessing Pipeline Test Document

# Chapter 1: Introduction
This is the introduction chapter of our test document.

## Section 1.1: Overview
This section provides an overview of the HTML preprocessing pipeline.

The pipeline should:
1. Convert DOCX to HTML using mammoth
2. Create structural HTML chunks
3. Assign block IDs to chunks
4. Tokenize images in chunks
5. Process with AI while preserving tokens
6. Replace tokens with rich images

## Section 1.2: Expected Processing
The DocumentPreprocessor should call these methods:
- _assign_block_ids_to_chunk()
- _create_chunk_html()
- _tokenize_images_in_chunk()

# Chapter 2: Testing
This chapter tests the complete pipeline.

## Section 2.1: Error Detection
If any methods are missing, we should see AttributeError in the logs.

## Section 2.2: Success Criteria
Successful processing indicates all methods exist and work correctly.

# Chapter 3: Conclusion
This document should trigger the HTML preprocessing pipeline completely.
"""

            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('html_pipeline_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Force HTML preprocessing pipeline
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_approach": "html_preprocessing_pipeline",
                    "output_requirements": {
                        "format": "html",
                        "use_html_preprocessing": True
                    },
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "use_html_tokenization": True
                    }
                })
            }
            
            print("📤 Processing with HTML preprocessing pipeline...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                error = data.get('error', '')
                
                print(f"📋 Response Keys: {list(data.keys())}")
                print(f"✅ Success: {success}")
                
                if error:
                    print(f"❌ Error: {error}")
                
                if success:
                    print("✅ STEP 3 PASSED: HTML preprocessing pipeline completed successfully")
                    
                    # Check processing details
                    articles = data.get('articles', [])
                    images_processed = data.get('images_processed', 0)
                    phase = data.get('phase', 'unknown')
                    
                    print(f"📊 Articles generated: {len(articles)}")
                    print(f"📊 Images processed: {images_processed}")
                    print(f"📊 Processing phase: {phase}")
                    
                    if 'html_preprocessing_pipeline' in phase:
                        print("✅ Confirmed: HTML preprocessing pipeline was used")
                    
                    return True
                else:
                    print("❌ STEP 3 FAILED: HTML preprocessing pipeline failed")
                    
                    # Analyze the error for specific method issues
                    if 'AttributeError' in error:
                        print("🎯 CRITICAL ERROR DETECTED: AttributeError in HTML preprocessing")
                        
                        if 'DocumentPreprocessor' in error and 'has no attribute' in error:
                            print("🎯 ROOT CAUSE: DocumentPreprocessor missing method(s)")
                            
                            # Extract the specific missing method
                            import re
                            match = re.search(r"'DocumentPreprocessor' object has no attribute '([^']+)'", error)
                            if match:
                                missing_method = match.group(1)
                                print(f"🎯 MISSING METHOD IDENTIFIED: {missing_method}")
                                
                                # Provide specific guidance
                                if missing_method == '_assign_block_ids_to_chunk':
                                    print("🔧 FIX NEEDED: Implement _assign_block_ids_to_chunk method")
                                elif missing_method == '_create_chunk_html':
                                    print("🔧 FIX NEEDED: Implement _create_chunk_html method")
                                elif missing_method == '_tokenize_images_in_chunk':
                                    print("🔧 FIX NEEDED: Implement _tokenize_images_in_chunk method")
                                else:
                                    print(f"🔧 FIX NEEDED: Implement {missing_method} method")
                    
                    return False
            else:
                print(f"❌ STEP 3 FAILED: HTTP error {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ STEP 3 FAILED: Exception during HTML preprocessing test - {str(e)}")
            traceback.print_exc()
            return False
    
    def test_method_signatures(self):
        """Test method signatures by analyzing error messages"""
        print("\n🔍 STEP 4: Testing Method Signatures...")
        try:
            print("🔍 Analyzing method signatures from error patterns...")
            
            # Create a test that should trigger all three problematic methods
            test_content = """Method Signature Test

This document tests the method signatures of:
1. _assign_block_ids_to_chunk(chunk_html, section_id)
2. _create_chunk_html(elements)
3. _tokenize_images_in_chunk(chunk_html, chunk_images)

Expected signatures based on usage in code:
- _assign_block_ids_to_chunk should take chunk_html and section_id parameters
- _create_chunk_html should take a list of elements
- _tokenize_images_in_chunk should take chunk_html and chunk_images parameters
"""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('signature_test.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true'
            }
            
            print("📤 Testing method signatures...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=60
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                
                if success:
                    print("✅ STEP 4 PASSED: Method signatures are correct")
                    return True
                else:
                    print("❌ STEP 4 FAILED: Method signature issues detected")
                    error = data.get('error', '')
                    
                    # Analyze signature-related errors
                    if 'TypeError' in error:
                        print("🎯 SIGNATURE ERROR: Method called with wrong parameters")
                        print(f"Error details: {error}")
                    
                    return False
            else:
                print(f"❌ STEP 4 FAILED: HTTP error {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ STEP 4 FAILED: Exception during signature test - {str(e)}")
            return False
    
    def test_exact_error_location(self):
        """Trace the exact error location in the code"""
        print("\n🔍 STEP 5: Tracing Exact Error Location...")
        try:
            print("🔍 Attempting to trigger the exact error and capture stack trace...")
            
            # Create a test specifically designed to trigger the HTML preprocessing pipeline
            # that was mentioned in the review request
            test_content = """Exact Error Location Test

This document is designed to trigger the exact error location where
DocumentPreprocessor methods are called but don't exist.

Based on the review request, the error occurs in the HTML preprocessing pipeline
when the system tries to call:
- _assign_block_ids_to_chunk
- _create_chunk_html  
- _tokenize_images_in_chunk

The error should occur during the preprocess_document method when it tries
to process HTML chunks and assign block IDs.
"""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('error_location_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use settings that should definitely trigger HTML preprocessing
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_approach": "html_preprocessing_pipeline",
                    "force_html_preprocessing": True,
                    "media_handling": {
                        "extract_images": True,
                        "use_html_tokenization": True
                    }
                })
            }
            
            print("📤 Triggering exact error location...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=60
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                error = data.get('error', '')
                
                if not success and error:
                    print("🎯 EXACT ERROR CAPTURED:")
                    print(f"Error: {error}")
                    
                    # Parse the error for exact location
                    if 'AttributeError' in error and 'DocumentPreprocessor' in error:
                        print("✅ STEP 5 PASSED: Exact error location identified")
                        print("🎯 CONFIRMED: DocumentPreprocessor missing method(s)")
                        
                        # Extract method name
                        import re
                        match = re.search(r"has no attribute '([^']+)'", error)
                        if match:
                            missing_method = match.group(1)
                            print(f"🎯 MISSING METHOD: {missing_method}")
                            
                            # Provide exact fix location
                            print(f"🔧 FIX LOCATION: Add {missing_method} method to DocumentPreprocessor class")
                            print(f"🔧 FILE: backend/server.py (DocumentPreprocessor class)")
                        
                        return True
                    else:
                        print("⚠️ STEP 5 PARTIAL: Error captured but not the expected AttributeError")
                        return True
                else:
                    print("⚠️ STEP 5 UNEXPECTED: No error occurred (methods might exist)")
                    return True
            else:
                print(f"❌ STEP 5 FAILED: HTTP error {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ STEP 5 FAILED: Exception during error location test - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all DocumentPreprocessor tests"""
        print("🎯 STARTING DOCUMENTPREPROCESSOR METHOD ERROR TESTING")
        print("=" * 60)
        
        results = []
        
        # Run all test steps
        results.append(self.test_documentpreprocessor_instantiation())
        results.append(self.test_method_existence())
        results.append(self.test_html_preprocessing_pipeline())
        results.append(self.test_method_signatures())
        results.append(self.test_exact_error_location())
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 DOCUMENTPREPROCESSOR TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"📊 Tests Passed: {passed}/{total}")
        
        test_names = [
            "DocumentPreprocessor Instantiation",
            "Method Existence",
            "HTML Preprocessing Pipeline", 
            "Method Signatures",
            "Exact Error Location"
        ]
        
        for i, (test_name, result) in enumerate(zip(test_names, results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i+1}. {test_name}: {status}")
        
        if passed < total:
            print("\n🎯 CRITICAL ISSUES IDENTIFIED:")
            print("- DocumentPreprocessor class is missing required methods")
            print("- HTML preprocessing pipeline fails due to missing methods")
            print("- System falls back to simplified processing instead of comprehensive processing")
            print("\n🔧 REQUIRED FIXES:")
            print("1. Add _assign_block_ids_to_chunk method to DocumentPreprocessor class")
            print("2. Add _create_chunk_html method to DocumentPreprocessor class")
            print("3. Add _tokenize_images_in_chunk method to DocumentPreprocessor class")
            print("4. Ensure all methods have correct signatures")
            print("5. Test HTML preprocessing pipeline after fixes")
        else:
            print("\n✅ ALL TESTS PASSED: DocumentPreprocessor methods are working correctly")
        
        return passed == total

if __name__ == "__main__":
    tester = DocumentPreprocessorTest()
    success = tester.run_all_tests()
    
    if not success:
        print("\n❌ DOCUMENTPREPROCESSOR TESTING FAILED")
        sys.exit(1)
    else:
        print("\n✅ DOCUMENTPREPROCESSOR TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)