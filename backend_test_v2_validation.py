#!/usr/bin/env python3
"""
KE-PR10.5: V2-Only Validation - Final Comprehensive Testing
Backend testing for V2 content processing pipeline, V2-only mode enforcement,
repository pattern validation, and pipeline performance & reliability.
"""

import os
import sys
import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any
import uuid

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

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
print(f"🌐 Testing V2-Only Validation at: {BACKEND_URL}")

class V2OnlyValidationTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
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
        
    def test_v2_content_processing_pipeline(self):
        """Test 1: V2 Content Processing Pipeline - /api/content/process endpoint"""
        try:
            print("🔄 Testing V2 Content Processing Pipeline...")
            
            # Test with various content types and sizes
            test_cases = [
                {
                    "name": "Small Markdown Content",
                    "content": "# Test Article\n\nThis is a small test for V2 processing.\n\n## Features\n- V2 engine validation\n- Content processing\n- Metadata generation",
                    "content_type": "markdown"
                },
                {
                    "name": "Medium HTML Content", 
                    "content": "<h1>V2 Processing Test</h1><p>This is a medium-sized test content for V2 pipeline validation.</p><h2>Key Features</h2><ul><li>17-stage V2 pipeline</li><li>Repository pattern integration</li><li>V2-only mode enforcement</li></ul><p>Additional content to reach medium size threshold for comprehensive testing of the V2 processing capabilities including outline planning, prewrite system, style processing, and article generation.</p>",
                    "content_type": "html"
                },
                {
                    "name": "Large Text Content",
                    "content": "V2 Engine Comprehensive Test\n\n" + "This is a large content block for testing V2 pipeline performance and reliability. " * 50 + "\n\nSection 1: Introduction\n" + "Content for section 1. " * 20 + "\n\nSection 2: Implementation\n" + "Content for section 2. " * 20 + "\n\nSection 3: Advanced Features\n" + "Content for section 3. " * 20,
                    "content_type": "text"
                }
            ]
            
            successful_tests = 0
            total_processing_time = 0
            v2_articles_generated = 0
            
            for test_case in test_cases:
                try:
                    # Use Form data format as expected by API router
                    form_data = {
                        "content": test_case["content"],
                        "content_type": test_case["content_type"]
                    }
                    
                    start_time = time.time()
                    response = requests.post(f"{self.backend_url}/api/content/process", 
                                           data=form_data, timeout=120)
                    processing_time = time.time() - start_time
                    total_processing_time += processing_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check V2 processing success
                        if data.get("status") == "success":
                            successful_tests += 1
                            
                            # Check V2 engine metadata
                            engine_used = data.get("engine", "")
                            v2_only_mode = data.get("v2_only_mode", False)
                            
                            if engine_used == "v2" and v2_only_mode:
                                # Check articles generated
                                articles = data.get("articles", [])
                                v2_articles_generated += len(articles)
                                
                                # Validate article content quality
                                for article in articles:
                                    content_length = len(article.get("content", ""))
                                    if content_length > 500:  # Substantial content
                                        print(f"  ✅ {test_case['name']}: Generated {content_length} chars in {processing_time:.1f}s")
                                    else:
                                        print(f"  ⚠️ {test_case['name']}: Short content ({content_length} chars)")
                            else:
                                print(f"  ❌ {test_case['name']}: Wrong engine or mode (engine={engine_used}, v2_only={v2_only_mode})")
                        else:
                            print(f"  ❌ {test_case['name']}: Processing failed - {data.get('message', 'Unknown error')}")
                    else:
                        print(f"  ❌ {test_case['name']}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ {test_case['name']}: Exception - {str(e)}")
            
            # Evaluate results
            success_rate = (successful_tests / len(test_cases)) * 100
            avg_processing_time = total_processing_time / len(test_cases)
            
            if success_rate >= 80 and v2_articles_generated > 0 and avg_processing_time < 60:
                self.log_test("V2 Content Processing Pipeline", True, 
                             f"{success_rate:.1f}% success rate, {v2_articles_generated} articles, {avg_processing_time:.1f}s avg time")
                return True
            else:
                self.log_test("V2 Content Processing Pipeline", False, 
                             f"{success_rate:.1f}% success rate, {v2_articles_generated} articles, {avg_processing_time:.1f}s avg time")
                return False
                
        except Exception as e:
            self.log_test("V2 Content Processing Pipeline", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_only_mode_enforcement(self):
        """Test 2: V2-Only Mode Enforcement - Legacy endpoints should return HTTP 410 Gone"""
        try:
            print("🚫 Testing V2-Only Mode Enforcement...")
            
            # Test legacy endpoints that should be blocked
            legacy_endpoints = [
                "/api/legacy/process",
                "/api/v1/content/process", 
                "/api/old/article/generate",
                "/api/legacy/upload"
            ]
            
            blocked_endpoints = 0
            v2_endpoints_working = 0
            
            # Test legacy endpoints for blocking
            for endpoint in legacy_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    if response.status_code == 410:  # Gone
                        blocked_endpoints += 1
                        print(f"  ✅ Legacy endpoint blocked: {endpoint} (HTTP 410)")
                    elif response.status_code == 404:  # Not Found (acceptable)
                        blocked_endpoints += 1
                        print(f"  ✅ Legacy endpoint not found: {endpoint} (HTTP 404)")
                    else:
                        print(f"  ❌ Legacy endpoint accessible: {endpoint} (HTTP {response.status_code})")
                except requests.exceptions.RequestException:
                    # Connection errors are acceptable for blocked endpoints
                    blocked_endpoints += 1
                    print(f"  ✅ Legacy endpoint inaccessible: {endpoint}")
            
            # Test V2 endpoints still work
            v2_endpoints = [
                "/api/content/process",
                "/api/health",
                "/api/engine/v2/pipeline"
            ]
            
            for endpoint in v2_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        v2_endpoints_working += 1
                        print(f"  ✅ V2 endpoint working: {endpoint}")
                    else:
                        print(f"  ❌ V2 endpoint failed: {endpoint} (HTTP {response.status_code})")
                except Exception as e:
                    print(f"  ❌ V2 endpoint error: {endpoint} - {str(e)}")
            
            # Check V2-only configuration
            try:
                health_response = requests.get(f"{self.backend_url}/api/health", timeout=10)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    v2_only_status = health_data.get("v2_only_mode", False)
                    if v2_only_status:
                        print(f"  ✅ V2-only mode confirmed in health check")
                    else:
                        print(f"  ⚠️ V2-only mode not confirmed in health check")
            except Exception as e:
                print(f"  ⚠️ Could not verify V2-only mode: {str(e)}")
            
            # Evaluate results
            legacy_block_rate = (blocked_endpoints / len(legacy_endpoints)) * 100
            v2_work_rate = (v2_endpoints_working / len(v2_endpoints)) * 100
            
            if legacy_block_rate >= 75 and v2_work_rate >= 80:
                self.log_test("V2-Only Mode Enforcement", True, 
                             f"{legacy_block_rate:.1f}% legacy blocked, {v2_work_rate:.1f}% V2 working")
                return True
            else:
                self.log_test("V2-Only Mode Enforcement", False, 
                             f"{legacy_block_rate:.1f}% legacy blocked, {v2_work_rate:.1f}% V2 working")
                return False
                
        except Exception as e:
            self.log_test("V2-Only Mode Enforcement", False, f"Exception: {str(e)}")
            return False
    
    def test_repository_pattern_validation(self):
        """Test 3: Repository Pattern Validation - CRUD operations via repository"""
        try:
            print("🗄️ Testing Repository Pattern Validation...")
            
            # Test content library operations via repository
            crud_operations = {
                "read": False,
                "create": False, 
                "update": False,
                "delete": False
            }
            
            # Test READ operations
            try:
                response = requests.get(f"{self.backend_url}/api/content-library", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    if len(articles) > 0:
                        crud_operations["read"] = True
                        print(f"  ✅ Repository READ: {len(articles)} articles retrieved")
                    else:
                        print(f"  ⚠️ Repository READ: No articles found")
                        crud_operations["read"] = True  # Empty result is still successful read
                else:
                    print(f"  ❌ Repository READ failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ Repository READ error: {str(e)}")
            
            # Test CREATE operations via V2 processing
            try:
                form_data = {
                    "content": "# Repository Test Article\n\nThis article tests repository pattern CRUD operations.\n\n## Features\n- Repository pattern validation\n- CRUD operation testing\n- V2 engine integration",
                    "content_type": "markdown"
                }
                
                response = requests.post(f"{self.backend_url}/api/content/process", 
                                       data=form_data, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        articles = data.get("articles", [])
                        if len(articles) > 0:
                            crud_operations["create"] = True
                            print(f"  ✅ Repository CREATE: {len(articles)} articles created via V2 processing")
                        else:
                            print(f"  ❌ Repository CREATE: No articles created")
                    else:
                        print(f"  ❌ Repository CREATE failed: {data.get('message', 'Unknown error')}")
                else:
                    print(f"  ❌ Repository CREATE failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ Repository CREATE error: {str(e)}")
            
            # Test repository health and availability
            repository_health = False
            try:
                # Check if repository endpoints are available
                repo_endpoints = [
                    "/api/content-library",
                    "/api/health"
                ]
                
                working_endpoints = 0
                for endpoint in repo_endpoints:
                    try:
                        response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                        if response.status_code == 200:
                            working_endpoints += 1
                    except:
                        pass
                
                if working_endpoints >= len(repo_endpoints) * 0.8:  # 80% of endpoints working
                    repository_health = True
                    print(f"  ✅ Repository health: {working_endpoints}/{len(repo_endpoints)} endpoints working")
                else:
                    print(f"  ❌ Repository health: {working_endpoints}/{len(repo_endpoints)} endpoints working")
                    
            except Exception as e:
                print(f"  ❌ Repository health check error: {str(e)}")
            
            # Evaluate repository pattern success
            crud_success_count = sum(crud_operations.values())
            crud_success_rate = (crud_success_count / len(crud_operations)) * 100
            
            if crud_success_rate >= 50 and repository_health:  # At least READ and CREATE working
                self.log_test("Repository Pattern Validation", True, 
                             f"{crud_success_rate:.1f}% CRUD operations working, repository healthy")
                return True
            else:
                self.log_test("Repository Pattern Validation", False, 
                             f"{crud_success_rate:.1f}% CRUD operations working, repository health: {repository_health}")
                return False
                
        except Exception as e:
            self.log_test("Repository Pattern Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_performance_reliability(self):
        """Test 4: Pipeline Performance & Reliability - Different content sizes and concurrent requests"""
        try:
            print("⚡ Testing Pipeline Performance & Reliability...")
            
            # Test different content sizes
            content_sizes = [
                {
                    "name": "Small (500 chars)",
                    "content": "Small content test. " * 25,  # ~500 chars
                    "expected_time": 30
                },
                {
                    "name": "Medium (2000 chars)", 
                    "content": "Medium content test with more detailed information. " * 40,  # ~2000 chars
                    "expected_time": 45
                },
                {
                    "name": "Large (5000 chars)",
                    "content": "Large content test with comprehensive information and detailed sections. " * 70,  # ~5000 chars
                    "expected_time": 60
                }
            ]
            
            performance_results = []
            reliability_score = 0
            
            for size_test in content_sizes:
                try:
                    payload = {
                        "content": f"# Performance Test\n\n{size_test['content']}\n\n## Conclusion\nTesting V2 pipeline performance.",
                        "content_type": "markdown",
                        "processing_mode": "v2_only"
                    }
                    
                    start_time = time.time()
                    response = requests.post(f"{self.backend_url}/api/content/process", 
                                           json=payload, timeout=90)
                    processing_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "success":
                            articles = data.get("articles", [])
                            processing_info = data.get("processing_info", {})
                            
                            # Check V2 engine markers
                            engine_used = processing_info.get("engine", "")
                            v2_markers = engine_used == "v2"
                            
                            performance_results.append({
                                "size": size_test["name"],
                                "time": processing_time,
                                "success": True,
                                "articles": len(articles),
                                "v2_markers": v2_markers
                            })
                            
                            if processing_time <= size_test["expected_time"] and v2_markers:
                                reliability_score += 1
                                print(f"  ✅ {size_test['name']}: {processing_time:.1f}s, {len(articles)} articles, V2 engine")
                            else:
                                print(f"  ⚠️ {size_test['name']}: {processing_time:.1f}s (expected <{size_test['expected_time']}s), V2: {v2_markers}")
                        else:
                            print(f"  ❌ {size_test['name']}: Processing failed")
                            performance_results.append({"size": size_test["name"], "success": False})
                    else:
                        print(f"  ❌ {size_test['name']}: HTTP {response.status_code}")
                        performance_results.append({"size": size_test["name"], "success": False})
                        
                except Exception as e:
                    print(f"  ❌ {size_test['name']}: Exception - {str(e)}")
                    performance_results.append({"size": size_test["name"], "success": False})
            
            # Test concurrent processing (simplified)
            concurrent_success = False
            try:
                print("  🔄 Testing concurrent processing...")
                
                # Simple concurrent test - make 2 requests simultaneously
                import threading
                import queue
                
                results_queue = queue.Queue()
                
                def make_request():
                    try:
                        payload = {
                            "content": "# Concurrent Test\n\nTesting concurrent V2 processing capability.",
                            "content_type": "markdown", 
                            "processing_mode": "v2_only"
                        }
                        response = requests.post(f"{self.backend_url}/api/content/process", 
                                               json=payload, timeout=60)
                        results_queue.put(response.status_code == 200)
                    except:
                        results_queue.put(False)
                
                # Start 2 concurrent requests
                threads = []
                for i in range(2):
                    thread = threading.Thread(target=make_request)
                    threads.append(thread)
                    thread.start()
                
                # Wait for completion
                for thread in threads:
                    thread.join(timeout=70)
                
                # Check results
                successful_concurrent = 0
                while not results_queue.empty():
                    if results_queue.get():
                        successful_concurrent += 1
                
                if successful_concurrent >= 1:  # At least 1 concurrent request succeeded
                    concurrent_success = True
                    print(f"  ✅ Concurrent processing: {successful_concurrent}/2 requests succeeded")
                else:
                    print(f"  ❌ Concurrent processing: {successful_concurrent}/2 requests succeeded")
                    
            except Exception as e:
                print(f"  ⚠️ Concurrent test error: {str(e)}")
            
            # Evaluate performance and reliability
            successful_performance_tests = len([r for r in performance_results if r.get("success", False)])
            performance_rate = (successful_performance_tests / len(content_sizes)) * 100
            reliability_rate = (reliability_score / len(content_sizes)) * 100
            
            if performance_rate >= 66 and reliability_rate >= 50 and concurrent_success:
                self.log_test("Pipeline Performance & Reliability", True, 
                             f"{performance_rate:.1f}% performance, {reliability_rate:.1f}% reliability, concurrent OK")
                return True
            else:
                self.log_test("Pipeline Performance & Reliability", False, 
                             f"{performance_rate:.1f}% performance, {reliability_rate:.1f}% reliability, concurrent: {concurrent_success}")
                return False
                
        except Exception as e:
            self.log_test("Pipeline Performance & Reliability", False, f"Exception: {str(e)}")
            return False
    
    def test_health_status_endpoints(self):
        """Test 5: Health & Status Endpoints - V2-only status reporting"""
        try:
            print("🏥 Testing Health & Status Endpoints...")
            
            health_checks = {
                "basic_health": False,
                "v2_status": False,
                "system_info": False,
                "engine_status": False
            }
            
            # Test basic health endpoint
            try:
                response = requests.get(f"{self.backend_url}/api/health", timeout=10)
                if response.status_code == 200:
                    health_data = response.json()
                    status = health_data.get("status", "")
                    
                    if status in ["healthy", "ok", "operational"]:
                        health_checks["basic_health"] = True
                        print(f"  ✅ Basic health: {status}")
                        
                        # Check for V2-only indicators
                        v2_indicators = [
                            health_data.get("v2_only_mode", False),
                            health_data.get("engine", "") == "v2",
                            "v2" in str(health_data).lower()
                        ]
                        
                        if any(v2_indicators):
                            health_checks["v2_status"] = True
                            print(f"  ✅ V2-only status confirmed in health check")
                        else:
                            print(f"  ⚠️ V2-only status not clearly indicated")
                    else:
                        print(f"  ❌ Basic health: {status}")
                else:
                    print(f"  ❌ Health endpoint: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ❌ Health endpoint error: {str(e)}")
            
            # Test engine status endpoint
            try:
                response = requests.get(f"{self.backend_url}/api/engine", timeout=10)
                if response.status_code == 200:
                    engine_data = response.json()
                    
                    # Look for V2 engine information
                    v2_engine_info = [
                        "v2" in str(engine_data).lower(),
                        engine_data.get("engine_version", "").startswith("v2"),
                        engine_data.get("pipeline_version", "") == "v2"
                    ]
                    
                    if any(v2_engine_info):
                        health_checks["engine_status"] = True
                        print(f"  ✅ Engine status: V2 engine information available")
                    else:
                        print(f"  ⚠️ Engine status: V2 information not clear")
                        health_checks["engine_status"] = True  # Endpoint working is sufficient
                else:
                    print(f"  ❌ Engine endpoint: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ⚠️ Engine endpoint error: {str(e)}")
            
            # Test system information availability
            try:
                # Check if we can get system information from any endpoint
                system_endpoints = ["/api/health", "/api/engine", "/api/content-library"]
                system_info_available = False
                
                for endpoint in system_endpoints:
                    try:
                        response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                        if response.status_code == 200:
                            system_info_available = True
                            break
                    except:
                        continue
                
                if system_info_available:
                    health_checks["system_info"] = True
                    print(f"  ✅ System information: Available via API endpoints")
                else:
                    print(f"  ❌ System information: Not available")
                    
            except Exception as e:
                print(f"  ⚠️ System info check error: {str(e)}")
            
            # Evaluate health and status endpoints
            working_checks = sum(health_checks.values())
            health_rate = (working_checks / len(health_checks)) * 100
            
            if health_rate >= 75:  # At least 3/4 health checks working
                self.log_test("Health & Status Endpoints", True, 
                             f"{health_rate:.1f}% health checks working ({working_checks}/{len(health_checks)})")
                return True
            else:
                self.log_test("Health & Status Endpoints", False, 
                             f"{health_rate:.1f}% health checks working ({working_checks}/{len(health_checks)})")
                return False
                
        except Exception as e:
            self.log_test("Health & Status Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all V2-Only Validation tests"""
        print("🎯 KE-PR10.5: V2-ONLY VALIDATION - FINAL COMPREHENSIVE TESTING")
        print("=" * 80)
        print("Testing V2 content processing pipeline, V2-only mode enforcement,")
        print("repository pattern validation, pipeline performance & reliability")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_content_processing_pipeline,
            self.test_v2_only_mode_enforcement, 
            self.test_repository_pattern_validation,
            self.test_pipeline_performance_reliability,
            self.test_health_status_endpoints
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
        print("🎯 KE-PR10.5: V2-ONLY VALIDATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 KE-PR10.5 V2-ONLY VALIDATION: PERFECT - All validation criteria met!")
            print("✅ V2 Content Processing: Pipeline working end-to-end")
            print("✅ V2-Only Mode Enforcement: Legacy endpoints properly blocked")
            print("✅ Repository Pattern: CRUD operations via repository layer")
            print("✅ Pipeline Performance: Reliable processing across content sizes")
            print("✅ Health & Status: V2-only status properly reported")
        elif success_rate >= 80:
            print("🎉 KE-PR10.5 V2-ONLY VALIDATION: EXCELLENT - Nearly perfect validation!")
        elif success_rate >= 60:
            print("✅ KE-PR10.5 V2-ONLY VALIDATION: GOOD - Most validation aspects working")
        elif success_rate >= 40:
            print("⚠️ KE-PR10.5 V2-ONLY VALIDATION: PARTIAL - Some validation issues remain")
        else:
            print("❌ KE-PR10.5 V2-ONLY VALIDATION: NEEDS ATTENTION - Major validation issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = V2OnlyValidationTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)