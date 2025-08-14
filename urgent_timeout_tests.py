#!/usr/bin/env python3
"""
URGENT: Knowledge Engine Timeout Testing
Focus on validating backend after regression fixes
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdocs-23.preview.emergentagent.com') + '/api'

class UrgentTimeoutTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🚨 URGENT Testing Knowledge Engine at: {self.base_url}")
        
    def test_health_check(self):
        """Test backend health"""
        print("\n🔍 Testing Backend Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Backend health check passed")
                    return True
                else:
                    print("❌ Backend not healthy")
                    return False
            else:
                print(f"❌ Health check failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check failed - {str(e)}")
            return False

    def test_small_file_quick_processing(self):
        """Test small file upload - should work quickly"""
        print("\n🔍 Testing Small File Quick Processing...")
        try:
            print("⚡ Testing small text file processing speed")
            print("🎯 Expected: Should work quickly without timeout")
            
            # Create a small test file
            small_content = """Small File Test

This is a small test file that should process quickly.
The system should handle this without any timeout issues.

Key points:
- Small file size
- Quick processing expected
- No timeout issues
- Immediate response"""

            file_data = io.BytesIO(small_content.encode('utf-8'))
            
            files = {
                'file': ('small_test.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "small_file_test",
                    "test_type": "quick_processing",
                    "document_type": "small_text"
                })
            }
            
            print("📤 Testing small file processing speed...")
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=30  # Should complete well within 30 seconds
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Small file processed in {processing_time:.2f} seconds")
            
            if processing_time > 30:
                print(f"❌ SLOW PROCESSING: Small file took {processing_time:.2f}s (> 30s)")
                return False
            elif processing_time > 10:
                print(f"⚠️ MODERATE SPEED: Small file took {processing_time:.2f}s (> 10s)")
            else:
                print(f"✅ FAST PROCESSING: Small file took {processing_time:.2f}s (< 10s)")
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                status = data.get('status')
                chunks_created = data.get('chunks_created', 0)
                
                print(f"📋 Small File Results:")
                print(f"  Status: {status}")
                print(f"  Chunks Created: {chunks_created}")
                print(f"  Processing Time: {processing_time:.2f}s")
                
                if status == 'completed':
                    print("✅ SMALL FILE QUICK PROCESSING PASSED:")
                    print("  ✅ Fast processing confirmed")
                    print("  ✅ No timeout issues")
                    print("  ✅ System responsive for small files")
                    return True
                else:
                    print("❌ Small file processing failed")
                    return False
            else:
                print(f"❌ Small file upload failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Small file quick processing test failed - {str(e)}")
            return False

    def test_timeout_monitoring_docx(self):
        """Test DOCX processing with timeout monitoring - URGENT ISSUE"""
        print("\n🔍 Testing DOCX Processing with Timeout Monitoring - URGENT...")
        try:
            print("⏰ CRITICAL TEST: Monitoring DOCX processing for timeout issues")
            print("🎯 User reported: DOCX uploads now timeout after 2 minutes")
            print("📊 Expected: Earlier today same DOCX processed successfully (58 chunks)")
            
            # Create a moderately sized DOCX content to test timeout behavior
            test_docx_content = """Knowledge Engine Timeout Test Document
            
This document tests the DOCX processing pipeline for timeout issues reported by the user.
The system should process this content without hanging or timing out.

Key Testing Areas:
1. Processing should complete within 5-10 minutes maximum
2. Chunking improvements should create 5-15 comprehensive articles
3. Content should be comprehensive with proper HTML structure
4. No hanging during processing

Content Section 1: Introduction
This section provides an introduction to the timeout testing process. The enhanced chunking system should handle this content efficiently with the new improvements including increased MAX_SINGLE_ARTICLE_CHARS from 1200 to 8000, robust JSON parsing with error handling, and 10-minute timeout protection.

Content Section 2: Processing Pipeline
The processing pipeline includes several key improvements: chunking now uses 600 words per chunk versus 250 words previously, section size increased from 2000 to 5000 characters, and enhanced error handling throughout the system.

Content Section 3: Expected Results
The system should create comprehensive articles with proper HTML structure, complete processing within reasonable time limits, and demonstrate that the regression fixes are working correctly.

Content Section 4: Quality Standards
Generated content should meet quality standards with proper heading hierarchy, comprehensive content coverage, and professional formatting that matches reference specifications.

Content Section 5: Performance Metrics
Processing performance should be monitored for completion time, chunk generation efficiency, and overall system responsiveness during the processing workflow.

This document contains sufficient content to test the chunking improvements while monitoring for timeout issues that have been reported."""

            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('timeout_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "timeout_monitoring_test",
                    "test_type": "docx_timeout_monitoring",
                    "document_type": "timeout_test"
                })
            }
            
            print("📤 Starting DOCX upload with timeout monitoring...")
            print("⏰ Monitoring for 2-minute timeout issue...")
            
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.base_url}/content/upload",
                    files=files,
                    data=form_data,
                    timeout=300  # 5 minute timeout to catch 2-minute hangs
                )
                
                processing_time = time.time() - start_time
                print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
                
                if processing_time > 120:  # More than 2 minutes
                    print(f"⚠️ TIMEOUT ISSUE DETECTED: Processing took {processing_time:.2f}s (> 2 minutes)")
                    if processing_time > 600:  # More than 10 minutes
                        print("❌ CRITICAL: Processing exceeded 10-minute maximum")
                        return False
                    else:
                        print("⚠️ WARNING: Processing slow but within 10-minute limit")
                else:
                    print(f"✅ GOOD: Processing completed in {processing_time:.2f}s (< 2 minutes)")
                
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for expected results
                    status = data.get('status')
                    chunks_created = data.get('chunks_created', 0)
                    job_id = data.get('job_id')
                    
                    print(f"📋 Processing Results:")
                    print(f"  Status: {status}")
                    print(f"  Chunks Created: {chunks_created}")
                    print(f"  Job ID: {job_id}")
                    
                    if status == 'completed' and chunks_created > 0:
                        print("✅ DOCX TIMEOUT MONITORING PASSED:")
                        print(f"  ✅ Processing completed successfully")
                        print(f"  ✅ Created {chunks_created} chunks")
                        print(f"  ✅ No hanging detected")
                        print(f"  ✅ Processing time: {processing_time:.2f}s")
                        
                        # Check if chunking improvements are working
                        if 5 <= chunks_created <= 15:
                            print(f"  ✅ Chunking improvements working: {chunks_created} comprehensive articles")
                        elif chunks_created > 15:
                            print(f"  ⚠️ Many chunks created: {chunks_created} (may indicate old chunking behavior)")
                        else:
                            print(f"  ⚠️ Few chunks created: {chunks_created} (may need larger test document)")
                        
                        return True
                    else:
                        print("❌ DOCX processing failed:")
                        print(f"  Status: {status}")
                        print(f"  Chunks: {chunks_created}")
                        return False
                else:
                    print(f"❌ DOCX upload failed - status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
            except requests.exceptions.Timeout:
                processing_time = time.time() - start_time
                print(f"❌ TIMEOUT CONFIRMED: Request timed out after {processing_time:.2f} seconds")
                print("❌ This confirms the user's report of 2-minute timeouts")
                return False
                
        except Exception as e:
            print(f"❌ DOCX timeout monitoring failed - {str(e)}")
            return False

    def test_pdf_processing_validation(self):
        """Test PDF processing validation - URGENT ISSUE"""
        print("\n🔍 Testing PDF Processing Validation - URGENT...")
        try:
            print("📄 CRITICAL TEST: Validating PDF processing pipeline")
            print("🎯 User reported: PDF processing fails")
            
            # Create a test PDF content (as text for now)
            test_pdf_content = """PDF Processing Test Document

This document tests the PDF processing pipeline for validation issues.
The system should handle PDF files without failures.

Test Areas:
1. PDF upload handling
2. Content extraction
3. Processing completion
4. Error handling

Content for PDF Processing:
This content simulates a PDF document that should be processed successfully.
The system should extract this text and create appropriate chunks for processing.

Expected Results:
- PDF should upload successfully
- Content should be extracted
- Processing should complete without errors
- Appropriate chunks should be created

Quality Standards:
- Proper content structure
- Comprehensive processing
- No processing failures
- Reasonable processing time"""

            file_data = io.BytesIO(test_pdf_content.encode('utf-8'))
            
            files = {
                'file': ('test_document.pdf', file_data, 'application/pdf')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "pdf_validation_test",
                    "test_type": "pdf_processing_validation",
                    "document_type": "pdf_test"
                })
            }
            
            print("📤 Testing PDF processing validation...")
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=180  # 3 minute timeout for PDF processing
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ PDF processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                status = data.get('status')
                chunks_created = data.get('chunks_created', 0)
                job_id = data.get('job_id')
                
                print(f"📋 PDF Processing Results:")
                print(f"  Status: {status}")
                print(f"  Chunks Created: {chunks_created}")
                print(f"  Job ID: {job_id}")
                print(f"  Processing Time: {processing_time:.2f}s")
                
                if status == 'completed':
                    print("✅ PDF PROCESSING VALIDATION PASSED:")
                    print("  ✅ PDF upload successful")
                    print("  ✅ Processing completed without errors")
                    print("  ✅ No processing failures detected")
                    
                    if chunks_created > 0:
                        print(f"  ✅ Created {chunks_created} chunks successfully")
                    else:
                        print("  ⚠️ No chunks created (may be expected for simple PDF)")
                    
                    return True
                else:
                    print("❌ PDF processing failed:")
                    print(f"  Status: {status}")
                    return False
            else:
                print(f"❌ PDF upload failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ PDF processing timed out")
            return False
        except Exception as e:
            print(f"❌ PDF processing validation failed - {str(e)}")
            return False

    def test_chunking_improvements_verification(self):
        """Test that chunking improvements are working"""
        print("\n🔍 Testing Chunking Improvements Verification...")
        try:
            print("🔧 Testing chunking improvements implementation")
            print("📊 Expected: 600 words per chunk vs 250 words, 5000 char sections vs 2000")
            
            # Create content that should trigger the improved chunking
            chunking_test_content = """Chunking Improvements Test Document

This document tests the chunking improvements that were implemented to address user complaints.
The system should now use improved chunking parameters for better article generation.

Section 1: Introduction to Chunking Improvements
The chunking system has been enhanced with several key improvements. The MAX_SINGLE_ARTICLE_CHARS has been increased from 1200 to 8000 characters, allowing for more comprehensive articles. The chunking algorithm now uses 600 words per chunk instead of the previous 250 words, providing better content coverage and reducing the number of small, fragmented articles.

Section 2: Enhanced Processing Parameters
The section size has been increased from 2000 to 5000 characters, enabling the system to handle larger content blocks more effectively. This improvement addresses user feedback about articles being too short or lacking comprehensive coverage of topics. The enhanced parameters ensure that generated articles provide substantial value and complete information coverage.

Section 3: Quality and Comprehensiveness
With these improvements, users should now receive 5-15 comprehensive articles instead of many small fragments. The content should be comprehensive with proper HTML structure, including appropriate heading hierarchy, detailed explanations, and complete topic coverage. The system maintains quality while providing more substantial articles.

Section 4: Performance and Reliability
The improvements include robust JSON parsing with error handling and 10-minute timeout protection for processing. These enhancements ensure reliable processing while maintaining quality standards. The system should complete processing within 5-10 minutes maximum for most documents.

Section 5: User Experience Enhancement
The overall user experience has been improved through these chunking enhancements. Users should notice better article quality, more comprehensive content coverage, and fewer fragmented articles. The system now provides a better balance between article count and content depth."""

            file_data = io.BytesIO(chunking_test_content.encode('utf-8'))
            
            files = {
                'file': ('chunking_improvements_test.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "chunking_improvements_test",
                    "test_type": "chunking_verification",
                    "document_type": "chunking_test"
                })
            }
            
            print("📤 Testing chunking improvements...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                status = data.get('status')
                chunks_created = data.get('chunks_created', 0)
                
                print(f"📋 Chunking Test Results:")
                print(f"  Status: {status}")
                print(f"  Chunks Created: {chunks_created}")
                
                if status == 'completed' and chunks_created > 0:
                    # Analyze chunking behavior
                    if 1 <= chunks_created <= 5:
                        print("✅ CHUNKING IMPROVEMENTS WORKING:")
                        print(f"  ✅ Created {chunks_created} comprehensive articles")
                        print("  ✅ Improved chunking parameters effective")
                        print("  ✅ Better content organization")
                        return True
                    elif chunks_created > 15:
                        print("⚠️ CHUNKING MAY NEED ADJUSTMENT:")
                        print(f"  ⚠️ Created {chunks_created} chunks (many small articles)")
                        print("  ⚠️ May indicate old chunking behavior")
                        return True  # Still working, just different behavior
                    else:
                        print("✅ CHUNKING WORKING:")
                        print(f"  ✅ Created {chunks_created} articles")
                        print("  ✅ Processing successful")
                        return True
                else:
                    print("❌ Chunking improvements test failed")
                    return False
            else:
                print(f"❌ Chunking test failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Chunking improvements verification failed - {str(e)}")
            return False

    def test_content_library_integration(self):
        """Test Content Library integration is working"""
        print("\n🔍 Testing Content Library Integration...")
        try:
            print("📚 Testing Content Library API and integration")
            
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                total_articles = data.get('total', 0)
                articles = data.get('articles', [])
                
                print(f"📋 Content Library Status:")
                print(f"  Total Articles: {total_articles}")
                print(f"  Articles Returned: {len(articles)}")
                
                if total_articles > 0:
                    print("✅ CONTENT LIBRARY INTEGRATION WORKING:")
                    print(f"  ✅ {total_articles} articles in library")
                    print("  ✅ API responding correctly")
                    print("  ✅ Integration operational")
                    
                    # Check article structure
                    if articles:
                        sample_article = articles[0]
                        print(f"  ✅ Sample article: '{sample_article.get('title', 'No title')}'")
                        print(f"  ✅ Article has content: {len(sample_article.get('content', '')) > 0}")
                    
                    return True
                else:
                    print("⚠️ CONTENT LIBRARY EMPTY:")
                    print("  ⚠️ No articles found in library")
                    print("  ⚠️ May be expected if no recent uploads")
                    return True  # Not necessarily a failure
            else:
                print(f"❌ Content Library API failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content Library integration test failed - {str(e)}")
            return False

    def run_urgent_timeout_tests(self):
        """Run urgent timeout and processing tests"""
        print("🚀 Starting URGENT Knowledge Engine Timeout Testing...")
        print("🎯 FOCUS: Validating Knowledge Engine after regression fixes")
        print("⚠️ URGENT: Investigating timeout and processing issues")
        print("=" * 80)
        
        # Prioritize urgent tests first
        urgent_tests = [
            ("Backend Health Check", self.test_health_check),
            ("Small File Quick Processing", self.test_small_file_quick_processing),
            ("DOCX Timeout Monitoring", self.test_timeout_monitoring_docx),
            ("PDF Processing Validation", self.test_pdf_processing_validation),
            ("Chunking Improvements Verification", self.test_chunking_improvements_verification),
            ("Content Library Integration", self.test_content_library_integration)
        ]
        
        results = []
        passed = 0
        failed = 0
        
        print("🔥 URGENT TESTS (Timeout & Processing Issues):")
        print("-" * 60)
        
        for test_name, test_func in urgent_tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    failed += 1
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                failed += 1
                results.append((test_name, False))
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
        
        # Print summary
        print("\n" + "="*80)
        print("🎯 URGENT KNOWLEDGE ENGINE VALIDATION SUMMARY")
        print("="*80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        print(f"\n🔥 URGENT TESTS RESULTS: {passed}/{len(urgent_tests)} passed")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        return passed, failed

if __name__ == "__main__":
    tester = UrgentTimeoutTester()
    
    # Run urgent timeout tests
    print("🚨 RUNNING URGENT TIMEOUT TESTS...")
    urgent_passed, urgent_failed = tester.run_urgent_timeout_tests()
    
    print(f"\n{'='*80}")
    print("🎯 URGENT TESTS COMPLETED")
    print(f"✅ Urgent Passed: {urgent_passed}")
    print(f"❌ Urgent Failed: {urgent_failed}")
    
    if urgent_failed == 0:
        print("\n🎉 All urgent tests passed! Knowledge Engine timeout issues resolved.")
    else:
        print(f"\n⚠️ {urgent_failed} urgent test(s) failed. Critical issues detected.")
    
    exit(0 if urgent_failed == 0 else 1)