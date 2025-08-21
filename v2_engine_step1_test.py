#!/usr/bin/env python3
"""
V2 Engine Step 1 Implementation Testing
Tests the V2 Engine Step 1 requirements as specified in the review request
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime

# Backend URL configuration
BACKEND_URL = "http://localhost:8001"

class V2EngineStep1Tester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = None
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🔧 V2 Engine Step 1 Test Setup Complete")
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        print("🧹 V2 Engine Step 1 Test Cleanup Complete")
        
    def log_test_result(self, test_name: str, success: bool, details: str, response_data: dict = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    async def test_1_health_check_verification(self):
        """Test 1: Health Check Verification - GET /api/engine endpoint"""
        print("\n🏥 TEST 1: Health Check Verification")
        
        try:
            async with self.session.get(f"{self.backend_url}/api/engine") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify engine=v2
                    if data.get("engine") == "v2":
                        self.log_test_result(
                            "Health Check - Engine V2", 
                            True, 
                            f"Engine correctly reports v2: {data.get('engine')}", 
                            data
                        )
                    else:
                        self.log_test_result(
                            "Health Check - Engine V2", 
                            False, 
                            f"Engine reports {data.get('engine')} instead of v2", 
                            data
                        )
                    
                    # Verify legacy=disabled
                    if data.get("legacy") == "disabled":
                        self.log_test_result(
                            "Health Check - Legacy Disabled", 
                            True, 
                            f"Legacy correctly disabled: {data.get('legacy')}", 
                            data
                        )
                    else:
                        self.log_test_result(
                            "Health Check - Legacy Disabled", 
                            False, 
                            f"Legacy reports {data.get('legacy')} instead of disabled", 
                            data
                        )
                    
                    # Verify additional V2 fields
                    expected_fields = ["status", "version", "endpoints", "features", "message"]
                    for field in expected_fields:
                        if field in data:
                            self.log_test_result(
                                f"Health Check - {field.title()} Field", 
                                True, 
                                f"{field} field present: {data.get(field)}", 
                                data
                            )
                        else:
                            self.log_test_result(
                                f"Health Check - {field.title()} Field", 
                                False, 
                                f"{field} field missing from response", 
                                data
                            )
                            
                else:
                    self.log_test_result(
                        "Health Check - HTTP Status", 
                        False, 
                        f"Expected 200, got {response.status}", 
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Health Check - Connection", 
                False, 
                f"Failed to connect to health check endpoint: {str(e)}"
            )
            
    async def test_2_v2_text_processing(self):
        """Test 2: V2 Text Processing - POST /api/content/process"""
        print("\n📝 TEST 2: V2 Text Processing")
        
        # Sample text content as specified in the review request
        sample_text = "This is a test document about API integration best practices. It covers authentication, rate limiting, and error handling strategies."
        
        payload = {
            "content": sample_text,
            "content_type": "text",
            "metadata": {
                "source": "v2_engine_test",
                "test_case": "step1_verification"
            }
        }
        
        try:
            async with self.session.post(
                f"{self.backend_url}/api/content/process",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify engine=v2 in response
                    if data.get("engine") == "v2":
                        self.log_test_result(
                            "Text Processing - Engine V2 Response", 
                            True, 
                            f"Response correctly shows engine=v2: {data.get('engine')}", 
                            data
                        )
                    else:
                        self.log_test_result(
                            "Text Processing - Engine V2 Response", 
                            False, 
                            f"Response shows engine={data.get('engine')} instead of v2", 
                            data
                        )
                    
                    # Verify V2 message
                    message = data.get("message", "")
                    if "V2 Engine" in message:
                        self.log_test_result(
                            "Text Processing - V2 Message", 
                            True, 
                            f"Response contains V2 Engine message: {message}", 
                            data
                        )
                    else:
                        self.log_test_result(
                            "Text Processing - V2 Message", 
                            False, 
                            f"Response message doesn't contain V2 Engine reference: {message}", 
                            data
                        )
                    
                    # Verify processing success
                    if data.get("status") == "completed":
                        self.log_test_result(
                            "Text Processing - Completion Status", 
                            True, 
                            f"Processing completed successfully: {data.get('status')}", 
                            data
                        )
                    else:
                        self.log_test_result(
                            "Text Processing - Completion Status", 
                            False, 
                            f"Processing status: {data.get('status')}", 
                            data
                        )
                    
                    # Verify chunks created
                    chunks_created = data.get("chunks_created", 0)
                    if chunks_created > 0:
                        self.log_test_result(
                            "Text Processing - Chunks Created", 
                            True, 
                            f"Successfully created {chunks_created} chunks", 
                            data
                        )
                    else:
                        self.log_test_result(
                            "Text Processing - Chunks Created", 
                            False, 
                            f"No chunks created: {chunks_created}", 
                            data
                        )
                        
                else:
                    self.log_test_result(
                        "Text Processing - HTTP Status", 
                        False, 
                        f"Expected 200, got {response.status}", 
                        {"status": response.status, "text": await response.text()}
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Text Processing - Connection", 
                False, 
                f"Failed to process text content: {str(e)}"
            )
            
    async def test_3_v2_logging_verification(self):
        """Test 3: V2 Logging Verification - Check backend logs for engine=v2"""
        print("\n📋 TEST 3: V2 Logging Verification")
        
        try:
            # Trigger a processing request to generate logs
            sample_text = "Test content for logging verification with V2 engine."
            payload = {
                "content": sample_text,
                "content_type": "text",
                "metadata": {"source": "logging_test"}
            }
            
            # Make request to generate logs
            async with self.session.post(
                f"{self.backend_url}/api/content/process",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    # Wait a moment for logs to be written
                    await asyncio.sleep(1)
                    
                    # Check backend logs for V2 engine identifiers
                    import subprocess
                    try:
                        # Get recent backend logs
                        result = subprocess.run(
                            ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        log_content = result.stdout
                        
                        # Check for V2 engine log entries
                        v2_log_patterns = [
                            "V2 ENGINE:",
                            "engine=v2",
                            "🚀 V2 ENGINE:",
                            "✅ V2 ENGINE:"
                        ]
                        
                        found_patterns = []
                        for pattern in v2_log_patterns:
                            if pattern in log_content:
                                found_patterns.append(pattern)
                        
                        if found_patterns:
                            self.log_test_result(
                                "V2 Logging - Engine Identifiers", 
                                True, 
                                f"Found V2 engine log patterns: {found_patterns}", 
                                {"patterns_found": found_patterns}
                            )
                        else:
                            self.log_test_result(
                                "V2 Logging - Engine Identifiers", 
                                False, 
                                "No V2 engine identifiers found in recent logs", 
                                {"log_sample": log_content[-500:]}
                            )
                            
                        # Check for specific V2 processing messages
                        processing_messages = [
                            "Processing text content - engine=v2",
                            "Processing complete - ",
                            "Job created - "
                        ]
                        
                        found_processing = []
                        for msg in processing_messages:
                            if msg in log_content:
                                found_processing.append(msg)
                        
                        if found_processing:
                            self.log_test_result(
                                "V2 Logging - Processing Messages", 
                                True, 
                                f"Found V2 processing messages: {found_processing}", 
                                {"processing_messages": found_processing}
                            )
                        else:
                            self.log_test_result(
                                "V2 Logging - Processing Messages", 
                                False, 
                                "No V2 processing messages found in logs", 
                                {"log_sample": log_content[-500:]}
                            )
                            
                    except subprocess.TimeoutExpired:
                        self.log_test_result(
                            "V2 Logging - Log Access", 
                            False, 
                            "Timeout accessing backend logs"
                        )
                    except Exception as log_error:
                        self.log_test_result(
                            "V2 Logging - Log Access", 
                            False, 
                            f"Error accessing logs: {str(log_error)}"
                        )
                else:
                    self.log_test_result(
                        "V2 Logging - Test Request", 
                        False, 
                        f"Test request failed with status {response.status}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                "V2 Logging - Test Setup", 
                False, 
                f"Failed to setup logging test: {str(e)}"
            )
            
    async def test_4_legacy_bypass_verification(self):
        """Test 4: Legacy Bypass Verification - Confirm no v1 processing functions called"""
        print("\n🚫 TEST 4: Legacy Bypass Verification")
        
        try:
            # Make a processing request and check that no v1 functions are called
            sample_text = "Legacy bypass test content for V2 engine verification."
            payload = {
                "content": sample_text,
                "content_type": "text",
                "metadata": {"source": "legacy_bypass_test"}
            }
            
            async with self.session.post(
                f"{self.backend_url}/api/content/process",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Wait for processing to complete and logs to be written
                    await asyncio.sleep(2)
                    
                    # Check logs for absence of v1 processing
                    import subprocess
                    try:
                        result = subprocess.run(
                            ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        
                        log_content = result.stdout
                        
                        # Check for v1 patterns that should NOT be present
                        v1_patterns = [
                            "v1 engine",
                            "engine=v1",
                            "legacy processing",
                            "V1 ENGINE:",
                            "process_content_v1"
                        ]
                        
                        found_v1_patterns = []
                        for pattern in v1_patterns:
                            if pattern.lower() in log_content.lower():
                                found_v1_patterns.append(pattern)
                        
                        if not found_v1_patterns:
                            self.log_test_result(
                                "Legacy Bypass - No V1 Processing", 
                                True, 
                                "No v1 processing patterns found in logs - legacy successfully bypassed", 
                                {"v1_patterns_checked": v1_patterns}
                            )
                        else:
                            self.log_test_result(
                                "Legacy Bypass - No V1 Processing", 
                                False, 
                                f"Found v1 processing patterns: {found_v1_patterns}", 
                                {"v1_patterns_found": found_v1_patterns}
                            )
                        
                        # Verify only V2 processing occurred
                        v2_only_patterns = [
                            "V2 ENGINE:",
                            "engine=v2"
                        ]
                        
                        found_v2_patterns = []
                        for pattern in v2_only_patterns:
                            if pattern in log_content:
                                found_v2_patterns.append(pattern)
                        
                        if found_v2_patterns:
                            self.log_test_result(
                                "Legacy Bypass - V2 Only Processing", 
                                True, 
                                f"Confirmed V2-only processing: {found_v2_patterns}", 
                                {"v2_patterns_found": found_v2_patterns}
                            )
                        else:
                            self.log_test_result(
                                "Legacy Bypass - V2 Only Processing", 
                                False, 
                                "No V2 processing patterns found", 
                                {"log_sample": log_content[-500:]}
                            )
                            
                    except Exception as log_error:
                        self.log_test_result(
                            "Legacy Bypass - Log Analysis", 
                            False, 
                            f"Error analyzing logs: {str(log_error)}"
                        )
                else:
                    self.log_test_result(
                        "Legacy Bypass - Test Request", 
                        False, 
                        f"Test request failed with status {response.status}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                "Legacy Bypass - Test Setup", 
                False, 
                f"Failed to setup legacy bypass test: {str(e)}"
            )
            
    async def test_5_response_validation(self):
        """Test 5: Response Validation - Verify all endpoints return proper V2 responses"""
        print("\n✅ TEST 5: Response Validation")
        
        # Test multiple endpoints for V2 response consistency
        endpoints_to_test = [
            {
                "name": "Health Check",
                "method": "GET",
                "url": "/api/engine",
                "payload": None
            },
            {
                "name": "Text Processing",
                "method": "POST", 
                "url": "/api/content/process",
                "payload": {
                    "content": "Response validation test content for V2 engine.",
                    "content_type": "text",
                    "metadata": {"source": "response_validation_test"}
                }
            }
        ]
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint["method"] == "GET":
                    async with self.session.get(f"{self.backend_url}{endpoint['url']}") as response:
                        await self._validate_v2_response(endpoint["name"], response)
                elif endpoint["method"] == "POST":
                    async with self.session.post(
                        f"{self.backend_url}{endpoint['url']}",
                        json=endpoint["payload"],
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        await self._validate_v2_response(endpoint["name"], response)
                        
            except Exception as e:
                self.log_test_result(
                    f"Response Validation - {endpoint['name']}", 
                    False, 
                    f"Failed to test endpoint: {str(e)}"
                )
                
    async def _validate_v2_response(self, endpoint_name: str, response):
        """Helper method to validate V2 response format"""
        try:
            if response.status == 200:
                data = await response.json()
                
                # Check for V2 engine identifier
                if data.get("engine") == "v2":
                    self.log_test_result(
                        f"Response Validation - {endpoint_name} Engine", 
                        True, 
                        f"Endpoint correctly returns engine=v2", 
                        data
                    )
                else:
                    self.log_test_result(
                        f"Response Validation - {endpoint_name} Engine", 
                        False, 
                        f"Endpoint returns engine={data.get('engine')} instead of v2", 
                        data
                    )
                
                # Check for enhanced V2 messaging
                message = data.get("message", "")
                if "V2 Engine" in message or "v2" in message.lower():
                    self.log_test_result(
                        f"Response Validation - {endpoint_name} Enhanced Messaging", 
                        True, 
                        f"Response contains V2 enhanced messaging: {message}", 
                        data
                    )
                else:
                    self.log_test_result(
                        f"Response Validation - {endpoint_name} Enhanced Messaging", 
                        False, 
                        f"Response lacks V2 enhanced messaging: {message}", 
                        data
                    )
                    
                # Check response structure
                if isinstance(data, dict) and len(data) > 0:
                    self.log_test_result(
                        f"Response Validation - {endpoint_name} Structure", 
                        True, 
                        f"Response has proper JSON structure with {len(data)} fields", 
                        data
                    )
                else:
                    self.log_test_result(
                        f"Response Validation - {endpoint_name} Structure", 
                        False, 
                        f"Response structure invalid: {type(data)}", 
                        data
                    )
                    
            else:
                self.log_test_result(
                    f"Response Validation - {endpoint_name} HTTP Status", 
                    False, 
                    f"Expected 200, got {response.status}", 
                    {"status": response.status}
                )
                
        except Exception as e:
            self.log_test_result(
                f"Response Validation - {endpoint_name} Processing", 
                False, 
                f"Error validating response: {str(e)}"
            )
            
    async def run_all_tests(self):
        """Run all V2 Engine Step 1 tests"""
        print("🚀 Starting V2 Engine Step 1 Implementation Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all tests in sequence
            await self.test_1_health_check_verification()
            await self.test_2_v2_text_processing()
            await self.test_3_v2_logging_verification()
            await self.test_4_legacy_bypass_verification()
            await self.test_5_response_validation()
            
        finally:
            await self.cleanup()
            
        # Generate test summary
        self.generate_test_summary()
        
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 V2 ENGINE STEP 1 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test_name']}: {result['details']}")
        
        print(f"\n🎯 V2 ENGINE STEP 1 REQUIREMENTS VERIFICATION:")
        
        # Check specific requirements
        requirements = {
            "Health Check Returns engine=v2, legacy=disabled": any(
                "Health Check - Engine V2" in r["test_name"] and r["success"] for r in self.test_results
            ) and any(
                "Health Check - Legacy Disabled" in r["test_name"] and r["success"] for r in self.test_results
            ),
            "V2 Text Processing Routes to V2 Engine": any(
                "Text Processing - Engine V2 Response" in r["test_name"] and r["success"] for r in self.test_results
            ),
            "V2 Logging Shows engine=v2 Identifiers": any(
                "V2 Logging - Engine Identifiers" in r["test_name"] and r["success"] for r in self.test_results
            ),
            "Legacy Bypass - No V1 Functions Called": any(
                "Legacy Bypass - No V1 Processing" in r["test_name"] and r["success"] for r in self.test_results
            ),
            "All Endpoints Return Proper V2 Responses": any(
                "Response Validation" in r["test_name"] and r["success"] for r in self.test_results
            )
        }
        
        for requirement, met in requirements.items():
            status = "✅ MET" if met else "❌ NOT MET"
            print(f"   {status} {requirement}")
        
        # Overall assessment
        requirements_met = sum(requirements.values())
        total_requirements = len(requirements)
        
        if requirements_met == total_requirements:
            print(f"\n🎉 V2 ENGINE STEP 1 IMPLEMENTATION: FULLY COMPLIANT")
            print(f"   All {total_requirements} requirements successfully verified!")
        else:
            print(f"\n⚠️ V2 ENGINE STEP 1 IMPLEMENTATION: PARTIALLY COMPLIANT")
            print(f"   {requirements_met}/{total_requirements} requirements met")
            print(f"   {total_requirements - requirements_met} requirements need attention")
        
        print("=" * 60)

async def main():
    """Main test execution function"""
    tester = V2EngineStep1Tester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())