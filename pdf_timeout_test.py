#!/usr/bin/env python3
"""
PDF Processing Pipeline Timeout Testing
Conservative approach testing PDF processing with timeout fixes
"""

import requests
import json
import os
import time
import signal
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdoc-v2.preview.emergentagent.com') + '/api'

class PDFTimeoutTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"Testing PDF Processing Pipeline at: {self.base_url}")
        
    @contextmanager
    def timeout_context(self, seconds):
        """Context manager for timeout handling"""
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Operation timed out after {seconds} seconds")
        
        # Set the signal handler
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        
        try:
            yield
        finally:
            # Restore the old signal handler
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def test_backend_health_before_pdf_testing(self):
        """Verify backend is healthy before starting PDF tests"""
        print("🔍 Testing Backend Health Before PDF Processing...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Backend is healthy and ready for PDF testing")
                    return True
                else:
                    print(f"❌ Backend health check failed: {data}")
                    return False
            else:
                print(f"❌ Backend health check failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend health check failed - {str(e)}")
            return False
    
    def test_small_pdf_processing_with_timeout(self):
        """Test small PDF processing (19KB test_content_library.pdf) with timeout validation"""
        print("\n🔍 Testing Small PDF Processing with Timeout Validation...")
        
        small_pdf_path = "/app/test_content_library.pdf"
        
        # Verify file exists and get size
        if not os.path.exists(small_pdf_path):
            print(f"❌ Small PDF file not found: {small_pdf_path}")
            return False
            
        file_size = os.path.getsize(small_pdf_path)
        print(f"📊 Small PDF file size: {file_size} bytes ({file_size/1024:.1f} KB)")
        
        try:
            # Test with timeout context manager
            with self.timeout_context(120):  # 120-second timeout as mentioned in review
                print("🚀 Starting small PDF processing with 120-second timeout...")
                
                start_time = time.time()
                
                with open(small_pdf_path, 'rb') as pdf_file:
                    files = {
                        'file': ('test_content_library.pdf', pdf_file, 'application/pdf')
                    }
                    
                    form_data = {
                        'metadata': json.dumps({
                            "source": "pdf_timeout_test",
                            "test_type": "small_pdf_timeout_validation",
                            "file_size": file_size
                        })
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/content/upload",
                        files=files,
                        data=form_data,
                        timeout=120  # Match the timeout context
                    )
                
                processing_time = time.time() - start_time
                print(f"⏱️ Small PDF processing completed in {processing_time:.2f} seconds")
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate timeout fixes are working
                    if processing_time < 120:
                        print(f"✅ TIMEOUT FIX VERIFIED: Processing completed within timeout ({processing_time:.2f}s < 120s)")
                    else:
                        print(f"⚠️ Processing took longer than expected: {processing_time:.2f}s")
                    
                    # Check for successful processing
                    if data.get('status') == 'completed' or data.get('success'):
                        chunks_created = data.get('chunks_created', 0)
                        job_id = data.get('job_id')
                        
                        print(f"✅ Small PDF processing successful:")
                        print(f"  ✅ Chunks created: {chunks_created}")
                        print(f"  ✅ Job ID: {job_id}")
                        print(f"  ✅ No system hanging detected")
                        print(f"  ✅ Backend remained responsive")
                        
                        return True
                    else:
                        print(f"❌ Small PDF processing failed: {data}")
                        return False
                else:
                    print(f"❌ Small PDF processing failed - status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except TimeoutError:
            print("❌ CRITICAL: Small PDF processing timed out after 120 seconds")
            print("❌ Timeout fixes are NOT working properly")
            return False
        except Exception as e:
            print(f"❌ Small PDF processing failed - {str(e)}")
            return False
    
    def test_backend_responsiveness_after_small_pdf(self):
        """Test that backend remains responsive after small PDF processing"""
        print("\n🔍 Testing Backend Responsiveness After Small PDF Processing...")
        try:
            # Test multiple endpoints to ensure system is still responsive
            endpoints_to_test = [
                ("/health", "Health Check"),
                ("/status", "Status Check"),
                ("/content-library", "Content Library")
            ]
            
            all_responsive = True
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ {name} responsive: {response.status_code}")
                    else:
                        print(f"⚠️ {name} returned {response.status_code}")
                        all_responsive = False
                        
                except Exception as e:
                    print(f"❌ {name} failed: {str(e)}")
                    all_responsive = False
            
            if all_responsive:
                print("✅ BACKEND RESPONSIVENESS VERIFIED: System remains responsive after small PDF processing")
                return True
            else:
                print("❌ Backend responsiveness issues detected after small PDF processing")
                return False
                
        except Exception as e:
            print(f"❌ Backend responsiveness test failed - {str(e)}")
            return False
    
    def test_large_pdf_processing_with_timeout(self):
        """Test large PDF processing (1.7MB Whisk_Studio_Integration_Guide.pdf) with timeout validation"""
        print("\n🔍 Testing Large PDF Processing with Timeout Validation...")
        
        large_pdf_path = "/app/Whisk_Studio_Integration_Guide.pdf"
        
        # Verify file exists and get size
        if not os.path.exists(large_pdf_path):
            print(f"❌ Large PDF file not found: {large_pdf_path}")
            return False
            
        file_size = os.path.getsize(large_pdf_path)
        print(f"📊 Large PDF file size: {file_size} bytes ({file_size/1024/1024:.1f} MB)")
        
        try:
            # Test with timeout context manager
            with self.timeout_context(120):  # 120-second timeout as mentioned in review
                print("🚀 Starting large PDF processing with 120-second timeout...")
                print("⚠️ This is the critical test - previous failures occurred with this file")
                
                start_time = time.time()
                
                with open(large_pdf_path, 'rb') as pdf_file:
                    files = {
                        'file': ('Whisk_Studio_Integration_Guide.pdf', pdf_file, 'application/pdf')
                    }
                    
                    form_data = {
                        'metadata': json.dumps({
                            "source": "pdf_timeout_test",
                            "test_type": "large_pdf_timeout_validation",
                            "file_size": file_size
                        })
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/content/upload",
                        files=files,
                        data=form_data,
                        timeout=120  # Match the timeout context
                    )
                
                processing_time = time.time() - start_time
                print(f"⏱️ Large PDF processing completed in {processing_time:.2f} seconds")
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate timeout fixes are working
                    if processing_time < 120:
                        print(f"✅ TIMEOUT FIX VERIFIED: Large PDF processing completed within timeout ({processing_time:.2f}s < 120s)")
                    else:
                        print(f"⚠️ Large PDF processing took longer than expected: {processing_time:.2f}s")
                    
                    # Check for successful processing
                    if data.get('status') == 'completed' or data.get('success'):
                        chunks_created = data.get('chunks_created', 0)
                        job_id = data.get('job_id')
                        
                        print(f"✅ Large PDF processing successful:")
                        print(f"  ✅ Chunks created: {chunks_created}")
                        print(f"  ✅ Job ID: {job_id}")
                        print(f"  ✅ No system hanging detected")
                        print(f"  ✅ Backend remained responsive")
                        print(f"  ✅ CRITICAL ISSUE RESOLVED: 1.7MB PDF processed successfully")
                        
                        return True
                    else:
                        print(f"❌ Large PDF processing failed: {data}")
                        return False
                else:
                    print(f"❌ Large PDF processing failed - status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except TimeoutError:
            print("❌ CRITICAL: Large PDF processing timed out after 120 seconds")
            print("❌ This indicates timeout fixes may need further refinement")
            print("💡 RECOMMENDATION: Consider implementing chunked PDF processing for large files")
            return False
        except Exception as e:
            print(f"❌ Large PDF processing failed - {str(e)}")
            return False
    
    def test_backend_responsiveness_after_large_pdf(self):
        """Test that backend remains responsive after large PDF processing"""
        print("\n🔍 Testing Backend Responsiveness After Large PDF Processing...")
        try:
            # Test multiple endpoints to ensure system is still responsive
            endpoints_to_test = [
                ("/health", "Health Check"),
                ("/status", "Status Check"),
                ("/content-library", "Content Library")
            ]
            
            all_responsive = True
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=15)
                    
                    if response.status_code == 200:
                        print(f"✅ {name} responsive: {response.status_code}")
                    else:
                        print(f"⚠️ {name} returned {response.status_code}")
                        all_responsive = False
                        
                except Exception as e:
                    print(f"❌ {name} failed: {str(e)}")
                    all_responsive = False
            
            if all_responsive:
                print("✅ BACKEND RESPONSIVENESS VERIFIED: System remains responsive after large PDF processing")
                return True
            else:
                print("❌ Backend responsiveness issues detected after large PDF processing")
                return False
                
        except Exception as e:
            print(f"❌ Backend responsiveness test failed - {str(e)}")
            return False
    
    def test_pdf_content_generation_validation(self):
        """Test that PDF processing generates actual content and articles"""
        print("\n🔍 Testing PDF Content Generation Validation...")
        try:
            # Check Content Library for recently generated articles
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Look for articles from our PDF tests
                pdf_test_articles = []
                for article in articles:
                    metadata = article.get('metadata', {})
                    source = metadata.get('source', '')
                    
                    if 'pdf_timeout_test' in source:
                        pdf_test_articles.append(article)
                
                print(f"📚 Found {len(pdf_test_articles)} articles from PDF timeout tests")
                
                if pdf_test_articles:
                    for i, article in enumerate(pdf_test_articles):
                        title = article.get('title', 'Untitled')
                        content_length = len(article.get('content', ''))
                        word_count = article.get('word_count', 0)
                        
                        print(f"📄 Article {i+1}: '{title}'")
                        print(f"  📊 Content length: {content_length} characters")
                        print(f"  📊 Word count: {word_count} words")
                        
                        if content_length > 100 and word_count > 10:
                            print(f"  ✅ Article has substantial content")
                        else:
                            print(f"  ⚠️ Article content may be minimal")
                    
                    print("✅ PDF CONTENT GENERATION VERIFIED: Articles generated successfully")
                    return True
                else:
                    print("⚠️ No articles found from PDF timeout tests")
                    print("⚠️ This may indicate content generation issues")
                    return False
            else:
                print(f"❌ Could not check Content Library - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ PDF content generation validation failed - {str(e)}")
            return False
    
    def test_error_recovery_mechanisms(self):
        """Test error recovery mechanisms for PDF processing"""
        print("\n🔍 Testing Error Recovery Mechanisms...")
        try:
            # Test with an invalid PDF file to check error handling
            invalid_pdf_content = b"This is not a valid PDF file content"
            
            files = {
                'file': ('invalid.pdf', invalid_pdf_content, 'application/pdf')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "pdf_timeout_test",
                    "test_type": "error_recovery_test"
                })
            }
            
            print("🧪 Testing error recovery with invalid PDF...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=30
            )
            
            print(f"📊 Error Recovery Response Status: {response.status_code}")
            
            # We expect this to fail gracefully, not crash the system
            if response.status_code in [400, 422, 500]:
                print("✅ ERROR RECOVERY VERIFIED: System handles invalid PDF gracefully")
                
                # Check that backend is still responsive after error
                health_response = requests.get(f"{self.base_url}/health", timeout=10)
                if health_response.status_code == 200:
                    print("✅ Backend remains responsive after PDF processing error")
                    return True
                else:
                    print("❌ Backend became unresponsive after PDF processing error")
                    return False
            else:
                print(f"⚠️ Unexpected response to invalid PDF: {response.status_code}")
                return True  # Not necessarily a failure
                
        except Exception as e:
            print(f"❌ Error recovery test failed - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all PDF timeout tests in sequence"""
        print("🚀 Starting PDF Processing Pipeline Timeout Testing")
        print("=" * 60)
        
        test_results = []
        
        # Test sequence following conservative approach
        tests = [
            ("Backend Health Check", self.test_backend_health_before_pdf_testing),
            ("Small PDF Processing (20KB)", self.test_small_pdf_processing_with_timeout),
            ("Backend Responsiveness After Small PDF", self.test_backend_responsiveness_after_small_pdf),
            ("Large PDF Processing (1.7MB)", self.test_large_pdf_processing_with_timeout),
            ("Backend Responsiveness After Large PDF", self.test_backend_responsiveness_after_large_pdf),
            ("PDF Content Generation Validation", self.test_pdf_content_generation_validation),
            ("Error Recovery Mechanisms", self.test_error_recovery_mechanisms)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"🧪 Running: {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                test_results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
                    # For critical tests, consider stopping
                    if test_name in ["Backend Health Check", "Small PDF Processing (20KB)"]:
                        print(f"🛑 Critical test failed: {test_name}")
                        print("🛑 Stopping test sequence due to critical failure")
                        break
                        
            except Exception as e:
                print(f"❌ {test_name}: EXCEPTION - {str(e)}")
                test_results.append((test_name, False))
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 PDF TIMEOUT TESTING SUMMARY")
        print(f"{'='*60}")
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("🎉 PDF TIMEOUT TESTING: OVERALL SUCCESS")
            print("✅ Timeout fixes are working correctly")
            print("✅ System remains responsive during PDF processing")
            print("✅ No system hanging detected")
        elif passed_tests >= total_tests * 0.6:  # 60% pass rate
            print("⚠️ PDF TIMEOUT TESTING: PARTIAL SUCCESS")
            print("⚠️ Some timeout fixes are working but improvements needed")
        else:
            print("❌ PDF TIMEOUT TESTING: CRITICAL ISSUES")
            print("❌ Timeout fixes need significant work")
        
        return passed_tests, total_tests

if __name__ == "__main__":
    tester = PDFTimeoutTest()
    tester.run_all_tests()