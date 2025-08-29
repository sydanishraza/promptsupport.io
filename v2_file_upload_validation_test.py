#!/usr/bin/env python3
"""
V2 File Upload Validation Testing - Google Maps DOCX Testing
Comprehensive test suite for validating V2 pipeline file upload functionality
Focus: DOCX file processing, V2 engine integration, error handling, and performance
"""

import os
import sys
import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

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
print(f"🌐 Testing V2 file upload at: {BACKEND_URL}")

class V2FileUploadTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Test files configuration
        self.google_maps_docx = "/app/Google_Map_JavaScript_API_Tutorial.docx"
        
        # Expected success criteria from review
        self.success_criteria = {
            "min_content_length": 1000,  # >1000 chars for substantial articles
            "max_processing_time": 60,   # <60 seconds processing time
            "expected_engine": "v2",     # V2 engine metadata
            "expected_status": "completed"  # Successful completion
        }
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
            
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_google_maps_docx_upload(self):
        """Test 1: DOCX File Upload Validation - Google Maps DOCX file processing"""
        try:
            print(f"📄 Testing Google Maps DOCX upload: {self.google_maps_docx}")
            
            # Check if file exists
            if not os.path.exists(self.google_maps_docx):
                self.log_test("Google Maps DOCX Upload", False, f"Test file not found: {self.google_maps_docx}")
                return False
            
            # Get file size for validation
            file_size = os.path.getsize(self.google_maps_docx)
            print(f"📊 File size: {file_size} bytes")
            
            # Prepare file upload
            with open(self.google_maps_docx, 'rb') as f:
                files = {'file': ('Google_Map_JavaScript_API_Tutorial.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                
                # Record start time for performance testing
                start_time = time.time()
                
                # Upload file to V2 pipeline
                response = requests.post(
                    f"{self.backend_url}/api/content/upload",
                    files=files,
                    timeout=120  # 2 minute timeout for large files
                )
                
                # Record processing time
                processing_time = time.time() - start_time
                
            print(f"⏱️ Processing time: {processing_time:.2f} seconds")
            
            # Check HTTP response
            if response.status_code != 200:
                self.log_test("Google Maps DOCX Upload", False, 
                             f"HTTP {response.status_code}: {response.text[:200]}")
                return False
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Google Maps DOCX Upload", False, f"Invalid JSON response: {str(e)}")
                return False
            
            # Validate response structure
            if not isinstance(data, dict):
                self.log_test("Google Maps DOCX Upload", False, f"Invalid response format: {type(data)}")
                return False
            
            # Check processing status
            status = data.get('status', '')
            if status != self.success_criteria['expected_status']:
                self.log_test("Google Maps DOCX Upload", False, 
                             f"Status: {status} (expected: {self.success_criteria['expected_status']})")
                return False
            
            # Check V2 engine usage
            engine = data.get('engine', '')
            if engine != self.success_criteria['expected_engine']:
                self.log_test("Google Maps DOCX Upload", False, 
                             f"Engine: {engine} (expected: {self.success_criteria['expected_engine']})")
                return False
            
            # Check file type detection
            file_type = data.get('file_type', '')
            if file_type != 'docx':
                self.log_test("Google Maps DOCX Upload", False, 
                             f"File type: {file_type} (expected: docx)")
                return False
            
            # Check content extraction
            content_length = data.get('content_length', 0)
            if content_length < self.success_criteria['min_content_length']:
                self.log_test("Google Maps DOCX Upload", False, 
                             f"Content length: {content_length} chars (expected: >{self.success_criteria['min_content_length']})")
                return False
            
            # Check processing time
            if processing_time > self.success_criteria['max_processing_time']:
                self.log_test("Google Maps DOCX Upload", False, 
                             f"Processing time: {processing_time:.2f}s (expected: <{self.success_criteria['max_processing_time']}s)")
                return False
            
            # Check articles generation
            articles_created = data.get('articles_created', 0)
            if articles_created < 1:
                self.log_test("Google Maps DOCX Upload", False, 
                             f"Articles created: {articles_created} (expected: >=1)")
                return False
            
            # Check V2 pipeline message
            v2_message = data.get('message', '')
            if 'v2' not in v2_message.lower():
                self.log_test("Google Maps DOCX Upload", False, 
                             f"Missing V2 pipeline confirmation in message: {v2_message}")
                return False
            
            # Success - log detailed results
            success_details = (
                f"Status: {status}, Engine: {engine}, File Type: {file_type}, "
                f"Content: {content_length} chars, Articles: {articles_created}, "
                f"Time: {processing_time:.2f}s, V2 Message: '{v2_message}'"
            )
            
            self.log_test("Google Maps DOCX Upload", True, success_details)
            return True
            
        except Exception as e:
            self.log_test("Google Maps DOCX Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_file_upload_error_handling(self):
        """Test 2: File Upload Error Handling - Various file types and edge cases"""
        try:
            print("🛡️ Testing file upload error handling...")
            
            # Test cases for error handling
            test_cases = [
                {
                    "name": "Empty file",
                    "content": b"",
                    "filename": "empty.txt",
                    "content_type": "text/plain",
                    "expected_error": True
                },
                {
                    "name": "Unsupported file type",
                    "content": b"This is a test executable file",
                    "filename": "test.exe",
                    "content_type": "application/octet-stream",
                    "expected_error": True
                },
                {
                    "name": "Valid TXT file",
                    "content": b"This is a valid text file with sufficient content for processing. It contains multiple sentences and should be processed successfully by the V2 engine.",
                    "filename": "test.txt",
                    "content_type": "text/plain",
                    "expected_error": False
                },
                {
                    "name": "Invalid file extension",
                    "content": b"Valid content but wrong extension",
                    "filename": "test.invalid",
                    "content_type": "text/plain",
                    "expected_error": True
                }
            ]
            
            error_handling_results = []
            
            for test_case in test_cases:
                try:
                    print(f"  Testing: {test_case['name']}")
                    
                    # Create temporary file-like object
                    import io
                    file_obj = io.BytesIO(test_case['content'])
                    
                    files = {
                        'file': (test_case['filename'], file_obj, test_case['content_type'])
                    }
                    
                    response = requests.post(
                        f"{self.backend_url}/api/content/upload",
                        files=files,
                        timeout=30
                    )
                    
                    # Analyze response
                    is_error = response.status_code != 200
                    expected_error = test_case['expected_error']
                    
                    if is_error == expected_error:
                        error_handling_results.append({
                            "test": test_case['name'],
                            "passed": True,
                            "details": f"HTTP {response.status_code} (expected error: {expected_error})"
                        })
                    else:
                        error_handling_results.append({
                            "test": test_case['name'],
                            "passed": False,
                            "details": f"HTTP {response.status_code} (expected error: {expected_error})"
                        })
                    
                except Exception as e:
                    error_handling_results.append({
                        "test": test_case['name'],
                        "passed": test_case['expected_error'],  # Exception is expected for error cases
                        "details": f"Exception: {str(e)}"
                    })
            
            # Evaluate overall error handling
            passed_cases = sum(1 for result in error_handling_results if result['passed'])
            total_cases = len(error_handling_results)
            success_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
            
            if success_rate >= 75:  # At least 75% of error handling cases should pass
                self.log_test("File Upload Error Handling", True, 
                             f"{passed_cases}/{total_cases} cases passed ({success_rate:.1f}%)")
                return True
            else:
                self.log_test("File Upload Error Handling", False, 
                             f"Low success rate: {passed_cases}/{total_cases} cases passed ({success_rate:.1f}%)")
                return False
            
        except Exception as e:
            self.log_test("File Upload Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_pipeline_integration(self):
        """Test 3: V2 Pipeline Integration - Verify V2 metadata and repository pattern"""
        try:
            print("🔗 Testing V2 pipeline integration...")
            
            # Check if Google Maps file was processed and stored
            if not os.path.exists(self.google_maps_docx):
                self.log_test("V2 Pipeline Integration", False, "Google Maps DOCX file not found")
                return False
            
            # Upload file and check integration
            with open(self.google_maps_docx, 'rb') as f:
                files = {'file': ('Google_Map_JavaScript_API_Tutorial.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                
                response = requests.post(
                    f"{self.backend_url}/api/content/upload",
                    files=files,
                    timeout=120
                )
            
            if response.status_code != 200:
                self.log_test("V2 Pipeline Integration", False, f"Upload failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Check V2 engine metadata
            v2_metadata_checks = [
                data.get('engine') == 'v2',
                data.get('v2_only_mode') == True,
                'v2' in data.get('message', '').lower(),
                data.get('status') == 'completed'
            ]
            
            v2_metadata_score = sum(v2_metadata_checks)
            
            if v2_metadata_score < 3:  # At least 3/4 V2 metadata indicators should be present
                self.log_test("V2 Pipeline Integration", False, 
                             f"Insufficient V2 metadata: {v2_metadata_score}/4 indicators")
                return False
            
            # Check content library integration
            try:
                library_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
                
                if library_response.status_code == 200:
                    library_data = library_response.json()
                    articles = library_data.get('articles', [])
                    
                    # Look for recently uploaded articles with V2 metadata
                    v2_articles = [
                        article for article in articles 
                        if article.get('metadata', {}).get('engine') == 'v2' or 
                           'v2' in str(article.get('metadata', {})).lower()
                    ]
                    
                    if len(v2_articles) > 0:
                        repository_integration = True
                        repository_details = f"Found {len(v2_articles)} V2 articles in content library"
                    else:
                        repository_integration = False
                        repository_details = "No V2 articles found in content library"
                else:
                    repository_integration = False
                    repository_details = f"Content library access failed: HTTP {library_response.status_code}"
                    
            except Exception as e:
                repository_integration = False
                repository_details = f"Repository check exception: {str(e)}"
            
            # Overall integration assessment
            integration_score = v2_metadata_score + (1 if repository_integration else 0)
            max_score = 5
            
            if integration_score >= 4:  # At least 4/5 integration indicators
                self.log_test("V2 Pipeline Integration", True, 
                             f"V2 integration verified: {integration_score}/{max_score} indicators. {repository_details}")
                return True
            else:
                self.log_test("V2 Pipeline Integration", False, 
                             f"Insufficient V2 integration: {integration_score}/{max_score} indicators. {repository_details}")
                return False
            
        except Exception as e:
            self.log_test("V2 Pipeline Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_upload_performance(self):
        """Test 4: Upload Performance - Processing time and concurrent handling"""
        try:
            print("⚡ Testing upload performance...")
            
            if not os.path.exists(self.google_maps_docx):
                self.log_test("Upload Performance", False, "Google Maps DOCX file not found")
                return False
            
            # Test 1: Single file processing time
            performance_results = []
            
            for attempt in range(3):  # Test 3 times for consistency
                try:
                    with open(self.google_maps_docx, 'rb') as f:
                        files = {'file': ('Google_Map_JavaScript_API_Tutorial.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                        
                        start_time = time.time()
                        response = requests.post(
                            f"{self.backend_url}/api/content/upload",
                            files=files,
                            timeout=120
                        )
                        processing_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        content_length = data.get('content_length', 0)
                        
                        performance_results.append({
                            "attempt": attempt + 1,
                            "processing_time": processing_time,
                            "content_length": content_length,
                            "success": True
                        })
                    else:
                        performance_results.append({
                            "attempt": attempt + 1,
                            "processing_time": processing_time,
                            "success": False,
                            "error": f"HTTP {response.status_code}"
                        })
                        
                except Exception as e:
                    performance_results.append({
                        "attempt": attempt + 1,
                        "success": False,
                        "error": str(e)
                    })
                
                # Small delay between attempts
                time.sleep(2)
            
            # Analyze performance results
            successful_attempts = [r for r in performance_results if r.get('success')]
            
            if not successful_attempts:
                self.log_test("Upload Performance", False, "No successful upload attempts")
                return False
            
            # Calculate average processing time
            avg_processing_time = sum(r['processing_time'] for r in successful_attempts) / len(successful_attempts)
            max_processing_time = max(r['processing_time'] for r in successful_attempts)
            min_processing_time = min(r['processing_time'] for r in successful_attempts)
            
            # Performance criteria
            performance_checks = [
                avg_processing_time < self.success_criteria['max_processing_time'],  # Average under 60s
                max_processing_time < (self.success_criteria['max_processing_time'] * 1.5),  # Max under 90s
                len(successful_attempts) >= 2,  # At least 2/3 attempts successful
                all(r.get('content_length', 0) > self.success_criteria['min_content_length'] for r in successful_attempts)  # Consistent content extraction
            ]
            
            performance_score = sum(performance_checks)
            
            performance_details = (
                f"Avg: {avg_processing_time:.2f}s, Min: {min_processing_time:.2f}s, "
                f"Max: {max_processing_time:.2f}s, Success: {len(successful_attempts)}/3 attempts"
            )
            
            if performance_score >= 3:  # At least 3/4 performance criteria met
                self.log_test("Upload Performance", True, performance_details)
                return True
            else:
                self.log_test("Upload Performance", False, 
                             f"Performance issues: {performance_score}/4 criteria met. {performance_details}")
                return False
            
        except Exception as e:
            self.log_test("Upload Performance", False, f"Exception: {str(e)}")
            return False
    
    def test_content_quality_validation(self):
        """Test 5: Content Quality Validation - Verify substantial article generation"""
        try:
            print("📝 Testing content quality validation...")
            
            if not os.path.exists(self.google_maps_docx):
                self.log_test("Content Quality Validation", False, "Google Maps DOCX file not found")
                return False
            
            # Upload file and analyze content quality
            with open(self.google_maps_docx, 'rb') as f:
                files = {'file': ('Google_Map_JavaScript_API_Tutorial.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                
                response = requests.post(
                    f"{self.backend_url}/api/content/upload",
                    files=files,
                    timeout=120
                )
            
            if response.status_code != 200:
                self.log_test("Content Quality Validation", False, f"Upload failed: HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Content quality checks
            content_length = data.get('content_length', 0)
            articles_created = data.get('articles_created', 0)
            
            # Check if we can access the generated articles
            try:
                library_response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
                
                if library_response.status_code == 200:
                    library_data = library_response.json()
                    articles = library_data.get('articles', [])
                    
                    # Find recently created articles (within last 5 minutes)
                    import datetime
                    recent_cutoff = datetime.datetime.now() - datetime.timedelta(minutes=5)
                    
                    recent_articles = []
                    for article in articles:
                        try:
                            created_at = article.get('created_at', '')
                            if created_at:
                                # Handle different datetime formats
                                if isinstance(created_at, str):
                                    if 'T' in created_at:
                                        article_time = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                    else:
                                        article_time = datetime.datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                                else:
                                    continue
                                
                                if article_time > recent_cutoff:
                                    recent_articles.append(article)
                        except Exception:
                            continue  # Skip articles with invalid timestamps
                    
                    # Analyze content quality of recent articles
                    quality_metrics = {
                        "total_articles": len(recent_articles),
                        "substantial_articles": 0,
                        "v2_articles": 0,
                        "total_content_length": 0,
                        "avg_content_length": 0
                    }
                    
                    for article in recent_articles:
                        content = article.get('content', '') or article.get('html', '')
                        
                        # Remove HTML tags for accurate character count
                        import re
                        text_content = re.sub(r'<[^>]+>', '', content)
                        content_length_clean = len(text_content.strip())
                        
                        quality_metrics["total_content_length"] += content_length_clean
                        
                        if content_length_clean > self.success_criteria['min_content_length']:
                            quality_metrics["substantial_articles"] += 1
                        
                        # Check for V2 metadata
                        metadata = article.get('metadata', {})
                        if (metadata.get('engine') == 'v2' or 
                            'v2' in str(metadata).lower() or
                            article.get('engine') == 'v2'):
                            quality_metrics["v2_articles"] += 1
                    
                    if quality_metrics["total_articles"] > 0:
                        quality_metrics["avg_content_length"] = quality_metrics["total_content_length"] / quality_metrics["total_articles"]
                    
                    # Quality assessment
                    quality_checks = [
                        quality_metrics["total_articles"] >= 1,  # At least 1 article created
                        quality_metrics["substantial_articles"] >= 1,  # At least 1 substantial article
                        quality_metrics["v2_articles"] >= 1,  # At least 1 V2 article
                        quality_metrics["avg_content_length"] > self.success_criteria['min_content_length']  # Average content substantial
                    ]
                    
                    quality_score = sum(quality_checks)
                    
                    quality_details = (
                        f"Articles: {quality_metrics['total_articles']}, "
                        f"Substantial: {quality_metrics['substantial_articles']}, "
                        f"V2: {quality_metrics['v2_articles']}, "
                        f"Avg Length: {quality_metrics['avg_content_length']:.0f} chars"
                    )
                    
                    if quality_score >= 3:  # At least 3/4 quality criteria met
                        self.log_test("Content Quality Validation", True, quality_details)
                        return True
                    else:
                        self.log_test("Content Quality Validation", False, 
                                     f"Quality issues: {quality_score}/4 criteria met. {quality_details}")
                        return False
                else:
                    # Fallback to upload response data
                    basic_quality_checks = [
                        content_length > self.success_criteria['min_content_length'],
                        articles_created >= 1,
                        data.get('engine') == 'v2'
                    ]
                    
                    basic_quality_score = sum(basic_quality_checks)
                    
                    if basic_quality_score >= 2:
                        self.log_test("Content Quality Validation", True, 
                                     f"Basic quality verified: {content_length} chars, {articles_created} articles")
                        return True
                    else:
                        self.log_test("Content Quality Validation", False, 
                                     f"Basic quality issues: {basic_quality_score}/3 criteria met")
                        return False
                        
            except Exception as e:
                # Fallback to basic validation
                basic_checks = [
                    content_length > self.success_criteria['min_content_length'],
                    articles_created >= 1
                ]
                
                if sum(basic_checks) >= 2:
                    self.log_test("Content Quality Validation", True, 
                                 f"Fallback validation: {content_length} chars, {articles_created} articles")
                    return True
                else:
                    self.log_test("Content Quality Validation", False, f"Fallback validation failed: {str(e)}")
                    return False
            
        except Exception as e:
            self.log_test("Content Quality Validation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all V2 file upload validation tests"""
        print("🎯 V2 FILE UPLOAD VALIDATION - GOOGLE MAPS DOCX TESTING")
        print("=" * 80)
        print("Comprehensive validation of V2 pipeline file upload functionality")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test File: {self.google_maps_docx}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_google_maps_docx_upload,
            self.test_file_upload_error_handling,
            self.test_v2_pipeline_integration,
            self.test_upload_performance,
            self.test_content_quality_validation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(2)
        
        # Print summary
        print()
        print("=" * 80)
        print("🎯 V2 FILE UPLOAD VALIDATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Success criteria assessment
        if success_rate == 100:
            print("🎉 V2 FILE UPLOAD VALIDATION: PERFECT - All success criteria met!")
            print("✅ Google Maps DOCX uploads and processes successfully")
            print("✅ Generated articles have proper V2 metadata (engine: v2)")
            print("✅ Content extraction produces substantial text (>1000 chars)")
            print("✅ Articles stored via repository pattern")
            print("✅ Processing time under 60 seconds for typical documents")
            print("✅ No 500 Internal Server Errors during upload")
        elif success_rate >= 80:
            print("🎉 V2 FILE UPLOAD VALIDATION: EXCELLENT - Most success criteria met!")
        elif success_rate >= 60:
            print("✅ V2 FILE UPLOAD VALIDATION: GOOD - Core functionality working")
        elif success_rate >= 40:
            print("⚠️ V2 FILE UPLOAD VALIDATION: PARTIAL - Some issues remain")
        else:
            print("❌ V2 FILE UPLOAD VALIDATION: NEEDS ATTENTION - Major issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = V2FileUploadTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)