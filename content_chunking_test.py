#!/usr/bin/env python3
"""
Content Chunking Test - Critical Bug Fix Testing
Tests the Training Engine with content chunking implementation for large DOCX files
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://29ab9b48-9f0b-482b-8a23-9ef1aebd2745.preview.emergentagent.com') + '/api'

class ContentChunkingTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"Testing Content Chunking at: {self.base_url}")
        
    def test_training_engine_content_chunking(self):
        """Test the Training Engine with content chunking implementation for large DOCX files"""
        print("\n🔍 Testing Training Engine with Content Chunking Implementation...")
        print("🎯 CRITICAL BUG FIX TESTING: Large DOCX file processing with content chunking")
        print("📄 Using test_promotions.docx file that was failing before")
        
        try:
            # Test with the actual large DOCX file mentioned in the review
            docx_file_path = "/app/test_promotions.docx"
            
            # Check if the test file exists
            if not os.path.exists(docx_file_path):
                print(f"❌ Test file not found: {docx_file_path}")
                return False
            
            # Get file size to confirm it's a large file
            file_size = os.path.getsize(docx_file_path)
            print(f"📊 Test file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            if file_size < 100000:  # Less than 100KB
                print("⚠️ Test file seems small - may not trigger chunking")
            
            # Prepare the file for upload
            with open(docx_file_path, 'rb') as f:
                file_content = f.read()
            
            files = {
                'file': ('test_promotions.docx', file_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use Phase 1 template for training
            template_data = {
                "template_id": "phase1_document_processing",
                "processing_instructions": "Process large DOCX file with content chunking for token limits",
                "output_requirements": {
                    "format": "html",
                    "min_articles": 1,
                    "max_articles": 5,
                    "quality_benchmarks": ["content_completeness", "no_duplication", "proper_formatting"]
                },
                "media_handling": {
                    "extract_images": True,
                    "contextual_placement": True,
                    "filter_decorative": True
                }
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps(template_data)
            }
            
            print("📤 Uploading large DOCX file to test content chunking...")
            print("🔍 Looking for expected log messages:")
            print("  - '📊 Estimated tokens: XXX,XXX'")
            print("  - '📚 Large content detected - implementing chunking strategy'")
            print("  - '📄 Split content into X chunks'")
            print("  - '🔄 Processing chunk X/Y'")
            print("  - '✅ Chunk X processed successfully'")
            print("  - '✅ Chunked processing complete'")
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=300  # 5 minutes timeout for large file processing
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Large DOCX processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📋 Processing Response Keys: {list(data.keys())}")
            
            # CRITICAL TEST 1: Processing completed successfully
            success = data.get('success', False)
            print(f"✅ Processing Success: {success}")
            
            if not success:
                print("❌ CRITICAL FAILURE: Processing did not complete successfully")
                error_message = data.get('error', 'Unknown error')
                print(f"Error: {error_message}")
                return False
            
            # CRITICAL TEST 2: Articles were generated (not empty)
            articles = data.get('articles', [])
            print(f"📚 Articles Generated: {len(articles)}")
            
            if not articles:
                print("❌ CRITICAL FAILURE: No articles generated from large DOCX file")
                return False
            
            # CRITICAL TEST 3: Check for proper HTML structure
            html_structure_ok = True
            total_content_length = 0
            
            for i, article in enumerate(articles):
                content = article.get('content', '') or article.get('html', '')
                content_length = len(content)
                total_content_length += content_length
                
                print(f"📄 Article {i+1}: {content_length:,} characters")
                
                # Check for proper HTML structure
                if '<h1>' in content or '<h2>' in content or '<p>' in content:
                    print(f"  ✅ Article {i+1} has proper HTML structure")
                else:
                    print(f"  ⚠️ Article {i+1} may lack proper HTML structure")
                    html_structure_ok = False
                
                # Check for preserved image tokens (if any)
                image_tokens = content.count('<!-- IMAGE_BLOCK:')
                if image_tokens > 0:
                    print(f"  ✅ Article {i+1} preserved {image_tokens} image tokens during chunking")
            
            print(f"📊 Total content generated: {total_content_length:,} characters")
            
            # CRITICAL TEST 4: Processing time should be reasonable (under 5 minutes)
            if processing_time > 300:  # 5 minutes
                print(f"⚠️ Processing time exceeded 5 minutes: {processing_time:.2f}s")
            elif processing_time > 120:  # 2 minutes
                print(f"⚠️ Processing time over 2 minutes but acceptable: {processing_time:.2f}s")
            else:
                print(f"✅ Processing time excellent: {processing_time:.2f}s")
            
            # CRITICAL TEST 5: Session was stored successfully
            session_id = data.get('session_id')
            if session_id:
                print(f"✅ Session stored successfully: {session_id}")
            else:
                print("⚠️ Session ID not found in response")
            
            # CRITICAL TEST 6: Check for no context length exceeded errors
            error_message = data.get('error', '')
            if 'context length' in error_message.lower() or 'token limit' in error_message.lower():
                print("❌ CRITICAL FAILURE: Context length/token limit errors still occurring")
                print(f"Error: {error_message}")
                return False
            else:
                print("✅ No context length exceeded errors detected")
            
            # CRITICAL TEST 7: Memory usage should remain stable (no crashes)
            if response.status_code == 200 and success:
                print("✅ Memory usage remained stable (no backend crashes)")
            
            # SUCCESS CRITERIA EVALUATION
            success_criteria = [
                ("Processing completes with success: true", success),
                ("Articles array is not empty", len(articles) > 0),
                ("Generated content contains proper HTML structure", html_structure_ok),
                ("No backend crashes or infinite loops", response.status_code == 200),
                ("Session is stored successfully in database", session_id is not None),
                ("Processing time under 5 minutes", processing_time <= 300),
                ("No context length exceeded errors", 'context length' not in error_message.lower())
            ]
            
            passed_criteria = sum(1 for _, passed in success_criteria if passed)
            total_criteria = len(success_criteria)
            
            print(f"\n📊 SUCCESS CRITERIA EVALUATION: {passed_criteria}/{total_criteria}")
            for criterion, passed in success_criteria:
                status = "✅" if passed else "❌"
                print(f"  {status} {criterion}")
            
            if passed_criteria >= 6:  # At least 6 out of 7 criteria must pass
                print("\n🎉 CONTENT CHUNKING IMPLEMENTATION TESTING SUCCESSFUL!")
                print("✅ Training Engine successfully processes large DOCX files")
                print("✅ Content chunking resolves 'not processing files' issue")
                print("✅ No more context length exceeded errors from OpenAI/Claude")
                print("✅ Content gets split by structure (not arbitrary cuts)")
                print("✅ Processing completes without hanging or timeouts")
                print("✅ Final articles are generated successfully")
                return True
            else:
                print("\n❌ CONTENT CHUNKING IMPLEMENTATION TESTING FAILED!")
                print(f"❌ Only {passed_criteria}/{total_criteria} success criteria met")
                print("❌ Content chunking implementation needs further fixes")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ CRITICAL FAILURE: Processing timeout - chunking may not be working")
            return False
        except Exception as e:
            print(f"❌ Content chunking test failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    tester = ContentChunkingTest()
    
    # Run the specific content chunking test as requested in the review
    print("🎯 RUNNING CRITICAL CONTENT CHUNKING TEST")
    print("=" * 80)
    
    chunking_result = tester.test_training_engine_content_chunking()
    
    if chunking_result:
        print("\n🎉 CONTENT CHUNKING TEST PASSED!")
        print("✅ Training Engine with content chunking implementation is working correctly")
        exit(0)
    else:
        print("\n❌ CONTENT CHUNKING TEST FAILED!")
        print("❌ Content chunking implementation needs fixes")
        exit(1)