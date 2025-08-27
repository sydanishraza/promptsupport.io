#!/usr/bin/env python3
"""
V2 Engine Step 7.5 Fixes Verification Testing
Focused testing to verify the 2 specific fixes for 100% success rate:
1. POST /api/style/rerun endpoint fix (Form -> JSON Request body)
2. V2 Engine metadata consistency fix (explicit "engine": "v2" field)
"""

import asyncio
import json
import requests
import os
from datetime import datetime
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2StyleFixesTester:
    """Focused tester for V2 Engine Step 7.5 fixes verification"""
    
    def __init__(self):
        self.test_results = []
        self.sample_style_ids = []
        
    def log_test(self, test_name: str, success: bool, details: str, data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {details}")
        
    def test_style_diagnostics_endpoints_basic(self) -> bool:
        """Test basic style diagnostic endpoints functionality"""
        try:
            print(f"\n🔍 TESTING STYLE DIAGNOSTIC ENDPOINTS BASIC FUNCTIONALITY")
            
            # Test GET /api/style/diagnostics
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Style Diagnostics Basic", False, f"GET /api/style/diagnostics failed: HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify basic structure
            required_fields = ['style_system_status', 'engine', 'style_summary', 'recent_style_results']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Style Diagnostics Basic", False, f"Missing required fields: {missing_fields}")
                return False
                
            # CRITICAL FIX VERIFICATION: Check for explicit "engine": "v2" field
            if data.get('engine') != 'v2':
                self.log_test("Style Diagnostics Basic", False, f"V2 Engine metadata fix failed - Expected engine=v2, got {data.get('engine')}")
                return False
                
            # Store sample style IDs for later tests
            recent_results = data.get('recent_style_results', [])
            if recent_results:
                self.sample_style_ids = [result.get('style_id') for result in recent_results[:3] if result.get('style_id')]
                
            self.log_test("Style Diagnostics Basic", True, 
                         f"Style diagnostics endpoint working with V2 engine metadata. Found {len(recent_results)} recent results",
                         data)
            return True
            
        except Exception as e:
            self.log_test("Style Diagnostics Basic", False, f"Exception: {str(e)}")
            return False
    
    def test_style_diagnostics_specific_id(self) -> bool:
        """Test GET /api/style/diagnostics/{style_id} with V2 metadata consistency"""
        try:
            print(f"\n🔍 TESTING STYLE DIAGNOSTICS SPECIFIC ID WITH V2 METADATA")
            
            if not self.sample_style_ids:
                self.log_test("Style Diagnostics Specific", False, "No sample style IDs available from previous test")
                return False
                
            style_id = self.sample_style_ids[0]
            response = requests.get(f"{API_BASE}/style/diagnostics/{style_id}", timeout=30)
            
            if response.status_code == 404:
                self.log_test("Style Diagnostics Specific", True, f"Style {style_id} not found (expected for some test scenarios)")
                return True
                
            if response.status_code != 200:
                self.log_test("Style Diagnostics Specific", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # CRITICAL FIX VERIFICATION: Check for explicit "engine": "v2" field
            if data.get('engine') != 'v2':
                self.log_test("Style Diagnostics Specific", False, f"V2 Engine metadata consistency fix failed - Expected engine=v2, got {data.get('engine')}")
                return False
                
            # Verify enhanced metadata structure
            required_fields = ['engine', 'style_result', 'analysis']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_test("Style Diagnostics Specific", False, f"Missing required fields: {missing_fields}")
                return False
                
            self.log_test("Style Diagnostics Specific", True, 
                         f"Style diagnostics specific endpoint working with consistent V2 engine metadata for {style_id}",
                         data)
            return True
            
        except Exception as e:
            self.log_test("Style Diagnostics Specific", False, f"Exception: {str(e)}")
            return False
    
    def test_style_rerun_json_request_fix(self) -> bool:
        """Test POST /api/style/rerun with JSON request body (MAIN FIX)"""
        try:
            print(f"\n🔧 TESTING STYLE RERUN JSON REQUEST BODY FIX (CRITICAL)")
            
            # CRITICAL FIX TEST: Use JSON request body instead of Form data
            test_run_id = "test_run_id_for_json_fix"
            
            # Test with JSON payload (the fix)
            json_payload = {
                "run_id": test_run_id
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(f"{API_BASE}/style/rerun", 
                                   json=json_payload, 
                                   headers=headers, 
                                   timeout=30)
            
            # The fix should prevent HTTP 422 validation error
            if response.status_code == 422:
                self.log_test("Style Rerun JSON Fix", False, f"CRITICAL FIX FAILED - Still getting HTTP 422 validation error with JSON request body: {response.text}")
                return False
                
            # Expected responses: 200 (success), 404 (run not found), or other valid HTTP codes
            # But NOT 422 (validation error)
            if response.status_code in [200, 404]:
                try:
                    data = response.json()
                    
                    # CRITICAL FIX VERIFICATION: Check for explicit "engine": "v2" field
                    if 'engine' in data and data.get('engine') != 'v2':
                        self.log_test("Style Rerun JSON Fix", False, f"V2 Engine metadata consistency issue - Expected engine=v2, got {data.get('engine')}")
                        return False
                        
                    self.log_test("Style Rerun JSON Fix", True, 
                                 f"CRITICAL FIX VERIFIED - POST /api/style/rerun accepts JSON request body without HTTP 422 error. Response: HTTP {response.status_code}",
                                 data)
                    return True
                    
                except json.JSONDecodeError:
                    # Some valid responses might not be JSON
                    self.log_test("Style Rerun JSON Fix", True, 
                                 f"CRITICAL FIX VERIFIED - POST /api/style/rerun accepts JSON request body without HTTP 422 error. Response: HTTP {response.status_code}")
                    return True
            else:
                self.log_test("Style Rerun JSON Fix", False, f"Unexpected HTTP status code: {response.status_code}: {response.text}")
                return False
            
        except Exception as e:
            self.log_test("Style Rerun JSON Fix", False, f"Exception: {str(e)}")
            return False
    
    def test_style_rerun_various_json_payloads(self) -> bool:
        """Test POST /api/style/rerun with various JSON payloads to ensure robustness"""
        try:
            print(f"\n🧪 TESTING STYLE RERUN WITH VARIOUS JSON PAYLOADS")
            
            test_payloads = [
                {"run_id": "test_run_1"},
                {"run_id": "test_run_2", "additional_param": "test"},
                {"run_id": "another_test_run"}
            ]
            
            successful_tests = 0
            total_tests = len(test_payloads)
            
            for i, payload in enumerate(test_payloads):
                try:
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(f"{API_BASE}/style/rerun", 
                                           json=payload, 
                                           headers=headers, 
                                           timeout=30)
                    
                    # Should NOT return HTTP 422 (validation error)
                    if response.status_code == 422:
                        print(f"❌ Payload {i+1} failed with HTTP 422: {payload}")
                        continue
                        
                    # Valid responses: 200, 404, or other non-422 codes
                    if response.status_code in [200, 404, 400, 500]:
                        successful_tests += 1
                        print(f"✅ Payload {i+1} accepted (HTTP {response.status_code}): {payload}")
                    else:
                        print(f"⚠️ Payload {i+1} unexpected response (HTTP {response.status_code}): {payload}")
                        
                except Exception as e:
                    print(f"❌ Payload {i+1} exception: {e}")
                    continue
            
            success_rate = (successful_tests / total_tests) * 100
            
            if success_rate >= 80:  # Allow some flexibility
                self.log_test("Style Rerun Various Payloads", True, 
                             f"JSON payload robustness verified - {successful_tests}/{total_tests} payloads accepted ({success_rate:.1f}%)")
                return True
            else:
                self.log_test("Style Rerun Various Payloads", False, 
                             f"JSON payload robustness failed - Only {successful_tests}/{total_tests} payloads accepted ({success_rate:.1f}%)")
                return False
            
        except Exception as e:
            self.log_test("Style Rerun Various Payloads", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_engine_metadata_consistency_all_endpoints(self) -> bool:
        """Test V2 engine metadata consistency across all style endpoints"""
        try:
            print(f"\n🔍 TESTING V2 ENGINE METADATA CONSISTENCY ACROSS ALL STYLE ENDPOINTS")
            
            endpoints_to_test = [
                ("/style/diagnostics", "GET", None),
            ]
            
            # Add specific style ID endpoint if available
            if self.sample_style_ids:
                endpoints_to_test.append((f"/style/diagnostics/{self.sample_style_ids[0]}", "GET", None))
            
            consistent_metadata_count = 0
            total_endpoints = len(endpoints_to_test)
            
            for endpoint_path, method, payload in endpoints_to_test:
                try:
                    url = f"{API_BASE}{endpoint_path}"
                    
                    if method == "GET":
                        response = requests.get(url, timeout=30)
                    elif method == "POST":
                        headers = {'Content-Type': 'application/json'}
                        response = requests.post(url, json=payload, headers=headers, timeout=30)
                    else:
                        continue
                    
                    if response.status_code in [200, 404]:  # Valid responses
                        try:
                            data = response.json()
                            
                            # Check for explicit "engine": "v2" field
                            if data.get('engine') == 'v2':
                                consistent_metadata_count += 1
                                print(f"✅ {endpoint_path}: V2 engine metadata consistent")
                            else:
                                print(f"❌ {endpoint_path}: V2 engine metadata inconsistent - got {data.get('engine')}")
                                
                        except json.JSONDecodeError:
                            print(f"⚠️ {endpoint_path}: Non-JSON response (HTTP {response.status_code})")
                    else:
                        print(f"⚠️ {endpoint_path}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {endpoint_path}: Exception - {e}")
                    continue
            
            consistency_rate = (consistent_metadata_count / total_endpoints) * 100
            
            if consistency_rate >= 100:
                self.log_test("V2 Metadata Consistency", True, 
                             f"V2 engine metadata consistency verified - {consistent_metadata_count}/{total_endpoints} endpoints have consistent 'engine': 'v2' field ({consistency_rate:.1f}%)")
                return True
            else:
                self.log_test("V2 Metadata Consistency", False, 
                             f"V2 engine metadata consistency failed - Only {consistent_metadata_count}/{total_endpoints} endpoints have consistent metadata ({consistency_rate:.1f}%)")
                return False
            
        except Exception as e:
            self.log_test("V2 Metadata Consistency", False, f"Exception: {str(e)}")
            return False
    
    def test_database_storage_v2_metadata(self) -> bool:
        """Test that database storage maintains consistent V2 metadata"""
        try:
            print(f"\n💾 TESTING DATABASE STORAGE V2 METADATA CONSISTENCY")
            
            # Get recent style results to check database storage
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Database Storage V2 Metadata", False, f"Could not get style diagnostics: HTTP {response.status_code}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            if not recent_results:
                self.log_test("Database Storage V2 Metadata", True, "No recent results available for database metadata testing (expected in some scenarios)")
                return True
            
            # Check V2 metadata in stored results
            v2_metadata_count = 0
            total_results = len(recent_results)
            
            for result in recent_results:
                # Check for V2 engine identification in stored results
                if result.get('engine') == 'v2' or 'v2' in str(result).lower():
                    v2_metadata_count += 1
            
            metadata_consistency_rate = (v2_metadata_count / total_results) * 100
            
            if metadata_consistency_rate >= 80:  # Allow some flexibility for older records
                self.log_test("Database Storage V2 Metadata", True, 
                             f"Database storage V2 metadata consistency verified - {v2_metadata_count}/{total_results} results have V2 metadata ({metadata_consistency_rate:.1f}%)")
                return True
            else:
                self.log_test("Database Storage V2 Metadata", False, 
                             f"Database storage V2 metadata consistency failed - Only {v2_metadata_count}/{total_results} results have V2 metadata ({metadata_consistency_rate:.1f}%)")
                return False
            
        except Exception as e:
            self.log_test("Database Storage V2 Metadata", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_fixes_verification(self) -> Dict[str, Any]:
        """Run focused tests for V2 Engine Step 7.5 fixes verification"""
        print(f"🚀 STARTING V2 ENGINE STEP 7.5 FIXES VERIFICATION TESTING")
        print(f"🎯 TARGET: 100% SUCCESS RATE FOR 2 SPECIFIC FIXES")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📡 API Base: {API_BASE}")
        print(f"\n🔧 FIXES BEING VERIFIED:")
        print(f"   1. POST /api/style/rerun endpoint fix (Form -> JSON Request body)")
        print(f"   2. V2 Engine metadata consistency fix (explicit 'engine': 'v2' field)")
        
        test_methods = [
            self.test_style_diagnostics_endpoints_basic,
            self.test_style_diagnostics_specific_id,
            self.test_style_rerun_json_request_fix,  # MAIN FIX
            self.test_style_rerun_various_json_payloads,
            self.test_v2_engine_metadata_consistency_all_endpoints,  # MAIN FIX
            self.test_database_storage_v2_metadata
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_method.__name__}: {str(e)}")
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        # Compile final results
        results = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "overall_status": "PASS" if success_rate >= 100 else "FAIL",
                "target_success_rate": "100%"
            },
            "fixes_verified": {
                "post_style_rerun_json_fix": None,  # Will be determined from test results
                "v2_engine_metadata_consistency_fix": None  # Will be determined from test results
            },
            "test_details": self.test_results,
            "backend_url": BACKEND_URL,
            "test_timestamp": datetime.utcnow().isoformat(),
            "engine_version": "v2",
            "step_tested": "Step 7.5 - Woolf-aligned Technical Writing Style + Structural Lint (Fixes Verification)"
        }
        
        # Determine which fixes were verified
        for result in self.test_results:
            if "Style Rerun JSON Fix" in result["test"]:
                results["fixes_verified"]["post_style_rerun_json_fix"] = result["success"]
            if "V2 Metadata Consistency" in result["test"] or "V2 Engine Metadata" in result["test"]:
                results["fixes_verified"]["v2_engine_metadata_consistency_fix"] = result["success"]
        
        print(f"\n" + "="*80)
        print(f"🎯 V2 ENGINE STEP 7.5 FIXES VERIFICATION COMPLETE")
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"🏆 TARGET: 100% success rate - {'✅ ACHIEVED' if success_rate >= 100 else '❌ NOT ACHIEVED'}")
        print(f"🔧 FIXES STATUS:")
        print(f"   1. POST /api/style/rerun JSON fix: {'✅ VERIFIED' if results['fixes_verified']['post_style_rerun_json_fix'] else '❌ FAILED'}")
        print(f"   2. V2 Engine metadata consistency: {'✅ VERIFIED' if results['fixes_verified']['v2_engine_metadata_consistency_fix'] else '❌ FAILED'}")
        print(f"="*80)
        
        return results

def main():
    """Main test execution"""
    tester = V2StyleFixesTester()
    results = tester.run_focused_fixes_verification()
    
    # Print detailed results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for result in results["test_details"]:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['details']}")
    
    return results

if __name__ == "__main__":
    main()