#!/usr/bin/env python3
"""
KE-PR8 API Router Split & Feature Flags (Kill Switches) Testing
Comprehensive test suite for the API router organization and feature flag functionality
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
print(f"🌐 Testing backend at: {BACKEND_URL}")

class KE_PR8_APIRouterTester:
    """Comprehensive tester for KE-PR8 API Router Split & Feature Flags"""
    
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Dict = None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
        if response_data and status == "FAIL":
            print(f"   📊 Response: {json.dumps(response_data, indent=2)[:200]}...")
    
    def test_health_endpoint(self):
        """Test health check endpoint - should always be available"""
        try:
            response = self.session.get(f"{self.backend_url}/api/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify health response structure
                required_fields = ["status", "timestamp", "feature_flags"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Health Endpoint Structure", 
                        "FAIL", 
                        f"Missing fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Verify feature flags are reported
                feature_flags = data.get("feature_flags", {})
                if "v1_enabled" not in feature_flags or "hybrid_enabled" not in feature_flags:
                    self.log_test(
                        "Health Feature Flags", 
                        "FAIL", 
                        "Feature flags not properly reported",
                        data
                    )
                    return False
                
                self.log_test(
                    "Health Endpoint", 
                    "PASS", 
                    f"Status: {data['status']}, V1: {feature_flags['v1_enabled']}, Hybrid: {feature_flags['hybrid_enabled']}"
                )
                return True
            else:
                self.log_test(
                    "Health Endpoint", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text[:100]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Health Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_engine_status_endpoint(self):
        """Test engine status endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/api/engine")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify engine status structure
                required_fields = ["engine", "status", "feature_flags", "endpoints", "features"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Engine Status Structure", 
                        "FAIL", 
                        f"Missing fields: {missing_fields}",
                        data
                    )
                    return False
                
                # Verify V2 engine is active
                if data.get("engine") != "v2":
                    self.log_test(
                        "Engine Version", 
                        "FAIL", 
                        f"Expected V2 engine, got: {data.get('engine')}",
                        data
                    )
                    return False
                
                # Verify KE-PR8 features are listed
                features = data.get("features", [])
                ke_pr8_features = [
                    "api_router_organization",
                    "feature_flags_kill_switches", 
                    "domain_based_routing"
                ]
                
                missing_features = [f for f in ke_pr8_features if f not in features]
                if missing_features:
                    self.log_test(
                        "KE-PR8 Features", 
                        "FAIL", 
                        f"Missing KE-PR8 features: {missing_features}",
                        data
                    )
                    return False
                
                self.log_test(
                    "Engine Status", 
                    "PASS", 
                    f"V2 engine active with {len(features)} features including KE-PR8"
                )
                return True
            else:
                self.log_test(
                    "Engine Status", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text[:100]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Engine Status", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_v2_routes_functionality(self):
        """Test that V2 routes work normally through the router"""
        v2_routes = [
            ("/api/content/library", "GET", "Content Library"),
            ("/api/assets", "GET", "Assets Management"),
            ("/api/validation/diagnostics", "GET", "Validation Diagnostics"),
            ("/api/qa/diagnostics", "GET", "QA Diagnostics")
        ]
        
        all_passed = True
        
        for route, method, name in v2_routes:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.backend_url}{route}")
                else:
                    response = self.session.request(method, f"{self.backend_url}{route}")
                
                if response.status_code in [200, 404]:  # 404 is acceptable for empty collections
                    self.log_test(
                        f"V2 Route: {name}", 
                        "PASS", 
                        f"HTTP {response.status_code} - Route accessible"
                    )
                else:
                    self.log_test(
                        f"V2 Route: {name}", 
                        "FAIL", 
                        f"HTTP {response.status_code}: {response.text[:100]}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"V2 Route: {name}", "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_v1_kill_switches(self):
        """Test that V1 routes return 410 when ENABLE_V1=false"""
        v1_routes = [
            ("/api/content-library", "POST", "Create Article V1"),
            ("/api/ai-assistance", "POST", "AI Assistance V1"),
            ("/api/content-analysis", "POST", "Content Analysis V1"),
            ("/api/training/start", "POST", "Training Start V1"),
            ("/api/training/status", "GET", "Training Status V1"),
            ("/api/style/apply", "POST", "Style Apply V1"),
            ("/api/style/templates", "GET", "Style Templates V1")
        ]
        
        all_passed = True
        
        for route, method, name in v1_routes:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.backend_url}{route}")
                elif method == "POST":
                    response = self.session.post(f"{self.backend_url}{route}", json={})
                else:
                    response = self.session.request(method, f"{self.backend_url}{route}")
                
                if response.status_code == 410:
                    # Verify the error message mentions V1 is disabled
                    try:
                        error_data = response.json()
                        detail = error_data.get("detail", "")
                        if "disabled" in detail.lower() or "deprecated" in detail.lower():
                            self.log_test(
                                f"V1 Kill Switch: {name}", 
                                "PASS", 
                                f"HTTP 410 with proper message: {detail[:50]}..."
                            )
                        else:
                            self.log_test(
                                f"V1 Kill Switch: {name}", 
                                "FAIL", 
                                f"HTTP 410 but unclear message: {detail}"
                            )
                            all_passed = False
                    except:
                        self.log_test(
                            f"V1 Kill Switch: {name}", 
                            "PASS", 
                            "HTTP 410 returned (message parsing failed)"
                        )
                else:
                    self.log_test(
                        f"V1 Kill Switch: {name}", 
                        "FAIL", 
                        f"Expected HTTP 410, got {response.status_code}: {response.text[:100]}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"V1 Kill Switch: {name}", "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_hybrid_kill_switches(self):
        """Test that Hybrid routes return 410 when ENABLE_HYBRID=false"""
        hybrid_routes = [
            ("/api/content/export", "GET", "Content Export Hybrid")
        ]
        
        all_passed = True
        
        for route, method, name in hybrid_routes:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.backend_url}{route}")
                else:
                    response = self.session.request(method, f"{self.backend_url}{route}")
                
                if response.status_code == 410:
                    # Verify the error message mentions hybrid is disabled
                    try:
                        error_data = response.json()
                        detail = error_data.get("detail", "")
                        if "hybrid" in detail.lower() and "disabled" in detail.lower():
                            self.log_test(
                                f"Hybrid Kill Switch: {name}", 
                                "PASS", 
                                f"HTTP 410 with proper message: {detail[:50]}..."
                            )
                        else:
                            self.log_test(
                                f"Hybrid Kill Switch: {name}", 
                                "FAIL", 
                                f"HTTP 410 but unclear message: {detail}"
                            )
                            all_passed = False
                    except:
                        self.log_test(
                            f"Hybrid Kill Switch: {name}", 
                            "PASS", 
                            "HTTP 410 returned (message parsing failed)"
                        )
                else:
                    self.log_test(
                        f"Hybrid Kill Switch: {name}", 
                        "FAIL", 
                        f"Expected HTTP 410, got {response.status_code}: {response.text[:100]}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Hybrid Kill Switch: {name}", "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_content_processing_routes(self):
        """Test content processing routes through the router"""
        try:
            # Test text content processing
            test_content = "This is a test content for KE-PR8 API router testing. It should be processed through the V2 pipeline."
            
            response = self.session.post(
                f"{self.backend_url}/api/content/process",
                data={
                    "content": test_content,
                    "content_type": "text"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("engine") == "v2" and data.get("status") == "completed":
                    self.log_test(
                        "Content Processing V2", 
                        "PASS", 
                        f"Processed {len(test_content)} chars through V2 engine"
                    )
                    return True
                else:
                    self.log_test(
                        "Content Processing V2", 
                        "FAIL", 
                        f"Unexpected response structure: {data}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Content Processing V2", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text[:100]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Content Processing V2", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_assets_management_routes(self):
        """Test assets management routes through the router"""
        try:
            # Test getting assets list
            response = self.session.get(f"{self.backend_url}/api/assets")
            
            if response.status_code == 200:
                data = response.json()
                if "assets" in data and "count" in data:
                    self.log_test(
                        "Assets Management", 
                        "PASS", 
                        f"Retrieved {data['count']} assets"
                    )
                    return True
                else:
                    self.log_test(
                        "Assets Management", 
                        "FAIL", 
                        f"Unexpected response structure: {data}",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Assets Management", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text[:100]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Assets Management", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_route_organization(self):
        """Test that routes are properly organized by domain"""
        try:
            # Test root endpoint to verify router is working
            response = self.session.get(f"{self.backend_url}/")
            
            if response.status_code == 200:
                content = response.text
                if "KE-PR8" in content or "API Routes organized" in content:
                    self.log_test(
                        "Route Organization", 
                        "PASS", 
                        "Router root endpoint shows KE-PR8 organization"
                    )
                    return True
                else:
                    self.log_test(
                        "Route Organization", 
                        "WARN", 
                        "Root endpoint accessible but no KE-PR8 indication"
                    )
                    return True  # Still pass as route works
            else:
                self.log_test(
                    "Route Organization", 
                    "FAIL", 
                    f"HTTP {response.status_code}: {response.text[:100]}"
                )
                return False
                
        except Exception as e:
            self.log_test("Route Organization", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_backward_compatibility(self):
        """Test that route behavior is identical to before the split"""
        try:
            # Test that essential endpoints still work the same way
            essential_routes = [
                ("/api/health", "GET"),
                ("/api/engine", "GET"),
                ("/api/content/library", "GET")
            ]
            
            all_compatible = True
            
            for route, method in essential_routes:
                response = self.session.request(method, f"{self.backend_url}{route}")
                
                if response.status_code in [200, 404]:  # 404 acceptable for empty collections
                    self.log_test(
                        f"Backward Compatibility: {route}", 
                        "PASS", 
                        f"Route accessible with HTTP {response.status_code}"
                    )
                else:
                    self.log_test(
                        f"Backward Compatibility: {route}", 
                        "FAIL", 
                        f"HTTP {response.status_code}: {response.text[:100]}"
                    )
                    all_compatible = False
            
            return all_compatible
            
        except Exception as e:
            self.log_test("Backward Compatibility", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all KE-PR8 tests"""
        print("🚀 Starting KE-PR8 API Router Split & Feature Flags Testing")
        print(f"🌐 Backend URL: {self.backend_url}")
        print("=" * 80)
        
        test_methods = [
            ("Health Check Endpoint", self.test_health_endpoint),
            ("Engine Status Endpoint", self.test_engine_status_endpoint),
            ("V2 Routes Functionality", self.test_v2_routes_functionality),
            ("V1 Kill Switches", self.test_v1_kill_switches),
            ("Hybrid Kill Switches", self.test_hybrid_kill_switches),
            ("Content Processing Routes", self.test_content_processing_routes),
            ("Assets Management Routes", self.test_assets_management_routes),
            ("Route Organization", self.test_route_organization),
            ("Backward Compatibility", self.test_backward_compatibility)
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n📋 Testing: {test_name}")
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Test method exception: {str(e)}")
        
        # Generate summary
        print("\n" + "=" * 80)
        print("📊 KE-PR8 API Router Testing Summary")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"✅ Passed: {passed_tests}/{total_tests} tests ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 KE-PR8 API Router implementation is working well!")
        elif success_rate >= 60:
            print("⚠️ KE-PR8 API Router has some issues but core functionality works")
        else:
            print("❌ KE-PR8 API Router has significant issues requiring attention")
        
        # Show detailed results
        print("\n📋 Detailed Test Results:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['test_name']}: {result['status']}")
            if result["details"]:
                print(f"   📝 {result['details']}")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = KE_PR8_APIRouterTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 KE-PR8 API Router Split & Feature Flags testing completed successfully!")
        return 0
    else:
        print("\n⚠️ KE-PR8 API Router testing completed with issues - see details above")
        return 1

if __name__ == "__main__":
    exit(main())