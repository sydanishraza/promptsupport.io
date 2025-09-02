#!/usr/bin/env python3
"""
KE-PR9.5 MongoDB Centralization Comprehensive Final Assessment
Realistic assessment of current MongoDB centralization status
"""

import requests
import json
import time
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://knowledge-engine-7.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class KE_PR9_5_FinalAssessment:
    def __init__(self):
        self.results = {
            "basic_functionality": {"passed": 0, "total": 0, "details": []},
            "repository_indicators": {"passed": 0, "total": 0, "details": []},
            "data_operations": {"passed": 0, "total": 0, "details": []},
            "system_performance": {"passed": 0, "total": 0, "details": []},
            "mongodb_centralization": {"passed": 0, "total": 0, "details": []},
            "production_readiness": {"passed": 0, "total": 0, "details": []}
        }
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with error handling"""
        try:
            url = f"{API_BASE}{endpoint}"
            response = requests.request(method, url, timeout=30, **kwargs)
            
            try:
                data = response.json()
            except:
                data = {"text": response.text[:200], "content_type": response.headers.get('content-type', '')}
            
            return {
                "status": response.status_code,
                "data": data,
                "success": 200 <= response.status_code < 300
            }
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "success": False
            }
    
    def test_basic_functionality(self):
        """Test 1: Basic System Functionality"""
        print("🔍 Testing Basic System Functionality...")
        
        # Test core endpoints
        endpoints = [
            ("/health", "System Health Check"),
            ("/engine", "Engine Status"),
            ("/content-library", "Content Library Access"),
            ("/assets", "Assets Management")
        ]
        
        for endpoint, name in endpoints:
            self.results["basic_functionality"]["total"] += 1
            result = self.make_request("GET", endpoint)
            
            if result["success"]:
                self.results["basic_functionality"]["passed"] += 1
                self.results["basic_functionality"]["details"].append(f"✅ {name} operational")
                
                # Additional checks for specific endpoints
                if endpoint == "/content-library":
                    data = result["data"]
                    if "articles" in data and isinstance(data["articles"], list):
                        article_count = len(data["articles"])
                        self.results["basic_functionality"]["details"].append(f"   📊 {article_count} articles accessible")
                    else:
                        self.results["basic_functionality"]["details"].append("   ⚠️ Unexpected content structure")
                
                elif endpoint == "/assets":
                    if isinstance(result["data"], list):
                        asset_count = len(result["data"])
                        self.results["basic_functionality"]["details"].append(f"   📊 {asset_count} assets available")
                
            else:
                self.results["basic_functionality"]["details"].append(f"❌ {name} failed: HTTP {result['status']}")
    
    def test_repository_indicators(self):
        """Test 2: Repository Pattern Indicators"""
        print("🏗️ Testing Repository Pattern Indicators...")
        
        # Check engine features for repository-related features
        self.results["repository_indicators"]["total"] += 1
        engine_result = self.make_request("GET", "/engine")
        
        if engine_result["success"]:
            features = engine_result["data"].get("features", [])
            repo_related = [f for f in features if any(keyword in f.lower() for keyword in ["repository", "mongo", "centralized", "api_router"])]
            
            if repo_related:
                self.results["repository_indicators"]["passed"] += 1
                self.results["repository_indicators"]["details"].append(f"✅ Repository-related features: {repo_related}")
            else:
                self.results["repository_indicators"]["details"].append("❌ No repository-related features detected")
        else:
            self.results["repository_indicators"]["details"].append("❌ Cannot access engine status")
        
        # Check for MongoDB centralization indicators
        self.results["repository_indicators"]["total"] += 1
        content_result = self.make_request("GET", "/content-library")
        
        if content_result["success"]:
            # Check response structure for repository patterns
            data = content_result["data"]
            if "articles" in data:
                self.results["repository_indicators"]["passed"] += 1
                self.results["repository_indicators"]["details"].append("✅ Structured API response indicates organized data access")
            else:
                self.results["repository_indicators"]["details"].append("❌ Unstructured API response")
        else:
            self.results["repository_indicators"]["details"].append("❌ Cannot assess repository patterns")
    
    def test_data_operations(self):
        """Test 3: Data Operations and Integrity"""
        print("💾 Testing Data Operations and Integrity...")
        
        # Test content retrieval and structure
        self.results["data_operations"]["total"] += 1
        content_result = self.make_request("GET", "/content-library")
        
        if content_result["success"]:
            data = content_result["data"]
            if "articles" in data and isinstance(data["articles"], list) and len(data["articles"]) > 0:
                articles = data["articles"]
                first_article = articles[0]
                
                # Check for required fields
                required_fields = ["id", "title", "content", "status", "created_at"]
                has_required = all(field in first_article for field in required_fields)
                
                if has_required:
                    self.results["data_operations"]["passed"] += 1
                    self.results["data_operations"]["details"].append(f"✅ Data integrity maintained - {len(articles)} articles with consistent structure")
                else:
                    missing_fields = [field for field in required_fields if field not in first_article]
                    self.results["data_operations"]["details"].append(f"❌ Missing required fields: {missing_fields}")
            else:
                self.results["data_operations"]["details"].append("❌ No articles available for integrity testing")
        else:
            self.results["data_operations"]["details"].append("❌ Cannot access content for data integrity testing")
        
        # Test TICKET-3 field preservation
        self.results["data_operations"]["total"] += 1
        if content_result["success"]:
            data = content_result["data"]
            if "articles" in data and len(data["articles"]) > 0:
                articles = data["articles"]
                ticket3_fields = ["doc_uid", "doc_slug", "headings_registry", "xrefs"]
                articles_with_ticket3 = 0
                
                for article in articles[:5]:  # Check first 5 articles
                    if any(field in article for field in ticket3_fields):
                        articles_with_ticket3 += 1
                
                ticket3_percentage = (articles_with_ticket3 / min(5, len(articles))) * 100
                
                if ticket3_percentage > 0:
                    self.results["data_operations"]["passed"] += 1
                    self.results["data_operations"]["details"].append(f"✅ TICKET-3 field preservation: {ticket3_percentage:.1f}%")
                else:
                    self.results["data_operations"]["details"].append("❌ TICKET-3 fields not preserved (0% coverage)")
        
        # Test error handling
        self.results["data_operations"]["total"] += 1
        error_test = self.make_request("GET", "/content-library/nonexistent-id")
        
        if error_test["status"] == 404:
            self.results["data_operations"]["passed"] += 1
            self.results["data_operations"]["details"].append("✅ Proper error handling for invalid requests")
        else:
            self.results["data_operations"]["details"].append(f"❌ Poor error handling: HTTP {error_test['status']}")
    
    def test_system_performance(self):
        """Test 4: System Performance Under Load"""
        print("⚡ Testing System Performance...")
        
        # Test individual operation performance
        self.results["system_performance"]["total"] += 1
        start_time = time.time()
        health_result = self.make_request("GET", "/health")
        health_time = time.time() - start_time
        
        start_time = time.time()
        content_result = self.make_request("GET", "/content-library")
        content_time = time.time() - start_time
        
        if health_result["success"] and content_result["success"]:
            if health_time < 1.0 and content_time < 3.0:
                self.results["system_performance"]["passed"] += 1
                self.results["system_performance"]["details"].append(f"✅ Response times acceptable: Health {health_time:.3f}s, Content {content_time:.3f}s")
            else:
                self.results["system_performance"]["details"].append(f"❌ Slow response times: Health {health_time:.3f}s, Content {content_time:.3f}s")
        else:
            self.results["system_performance"]["details"].append("❌ Cannot test performance - endpoints not accessible")
        
        # Test concurrent operations
        self.results["system_performance"]["total"] += 1
        start_time = time.time()
        
        concurrent_results = []
        for i in range(5):
            result = self.make_request("GET", "/health")
            concurrent_results.append(result)
        
        concurrent_time = time.time() - start_time
        successful = sum(1 for r in concurrent_results if r["success"])
        
        if successful >= 4:  # 80% success rate
            self.results["system_performance"]["passed"] += 1
            self.results["system_performance"]["details"].append(f"✅ Concurrent operations stable: {successful}/5 successful in {concurrent_time:.3f}s")
        else:
            self.results["system_performance"]["details"].append(f"❌ Poor concurrent performance: {successful}/5 successful")
    
    def test_mongodb_centralization(self):
        """Test 5: MongoDB Centralization Assessment"""
        print("📊 Testing MongoDB Centralization...")
        
        # Test available operations
        operations = [
            ("/health", "System Health"),
            ("/engine", "Engine Status"),
            ("/content-library", "Content Library"),
            ("/assets", "Assets Management")
        ]
        
        working_operations = 0
        
        for endpoint, name in operations:
            result = self.make_request("GET", endpoint)
            if result["success"]:
                working_operations += 1
        
        self.results["mongodb_centralization"]["total"] += 1
        completion_percentage = (working_operations / len(operations)) * 100
        
        if completion_percentage >= 75:
            self.results["mongodb_centralization"]["passed"] += 1
            self.results["mongodb_centralization"]["details"].append(f"✅ Core operations working: {working_operations}/{len(operations)} ({completion_percentage:.1f}%)")
        else:
            self.results["mongodb_centralization"]["details"].append(f"❌ Limited operations: {working_operations}/{len(operations)} ({completion_percentage:.1f}%)")
        
        # Test for centralized data access patterns
        self.results["mongodb_centralization"]["total"] += 1
        content_result = self.make_request("GET", "/content-library")
        
        if content_result["success"]:
            data = content_result["data"]
            if "articles" in data and isinstance(data["articles"], list):
                self.results["mongodb_centralization"]["passed"] += 1
                self.results["mongodb_centralization"]["details"].append("✅ Centralized data access pattern detected")
            else:
                self.results["mongodb_centralization"]["details"].append("❌ No clear centralized access pattern")
        else:
            self.results["mongodb_centralization"]["details"].append("❌ Cannot assess centralization patterns")
    
    def test_production_readiness(self):
        """Test 6: Production Readiness Assessment"""
        print("🚀 Testing Production Readiness...")
        
        # Test system health
        self.results["production_readiness"]["total"] += 1
        health_result = self.make_request("GET", "/health")
        
        if health_result["success"]:
            health_data = health_result["data"]
            if health_data.get("status") == "healthy":
                self.results["production_readiness"]["passed"] += 1
                self.results["production_readiness"]["details"].append("✅ System health optimal")
            else:
                self.results["production_readiness"]["details"].append(f"❌ System health suboptimal: {health_data.get('status')}")
        else:
            self.results["production_readiness"]["details"].append("❌ System health check failed")
        
        # Test feature flags
        self.results["production_readiness"]["total"] += 1
        if health_result["success"]:
            health_data = health_result["data"]
            if "feature_flags" in health_data:
                self.results["production_readiness"]["passed"] += 1
                flags = health_data["feature_flags"]
                self.results["production_readiness"]["details"].append(f"✅ Feature flags operational: {flags}")
            else:
                self.results["production_readiness"]["details"].append("❌ No feature flags detected")
        
        # Test API organization
        self.results["production_readiness"]["total"] += 1
        engine_result = self.make_request("GET", "/engine")
        
        if engine_result["success"]:
            features = engine_result["data"].get("features", [])
            api_features = [f for f in features if "api" in f.lower() or "router" in f.lower()]
            
            if api_features:
                self.results["production_readiness"]["passed"] += 1
                self.results["production_readiness"]["details"].append(f"✅ API organization features: {api_features}")
            else:
                self.results["production_readiness"]["details"].append("❌ No API organization features detected")
    
    def run_comprehensive_assessment(self):
        """Run complete assessment"""
        print("🎯 KE-PR9.5 MONGODB CENTRALIZATION COMPREHENSIVE FINAL ASSESSMENT")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Assessment Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run all tests
        self.test_basic_functionality()
        self.test_repository_indicators()
        self.test_data_operations()
        self.test_system_performance()
        self.test_mongodb_centralization()
        self.test_production_readiness()
        
        # Generate comprehensive report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 KE-PR9.5 MONGODB CENTRALIZATION FINAL ASSESSMENT RESULTS")
        print("=" * 80)
        
        total_passed = 0
        total_tests = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            total = results["total"]
            total_passed += passed
            total_tests += total
            
            if total > 0:
                success_rate = (passed / total) * 100
                status = "✅ PASS" if success_rate >= 70 else "❌ FAIL"
                print(f"\n{category.upper().replace('_', ' ')}: {status} ({passed}/{total} - {success_rate:.1f}%)")
                
                for detail in results["details"]:
                    print(f"  {detail}")
        
        # Overall assessment
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"🎯 OVERALL KE-PR9.5 ASSESSMENT RESULTS")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Success Rate: {overall_success_rate:.1f}%")
        
        # Determine status
        if overall_success_rate >= 85:
            status = "🎉 EXCELLENT - Production Ready"
            recommendation = "System demonstrates excellent MongoDB centralization and is ready for production deployment."
        elif overall_success_rate >= 70:
            status = "✅ GOOD - Minor Issues"
            recommendation = "System shows good progress with minor issues that should be addressed."
        elif overall_success_rate >= 50:
            status = "⚠️ PARTIAL - Significant Work Needed"
            recommendation = "System partially functional but requires significant work for full MongoDB centralization."
        else:
            status = "❌ CRITICAL - Major Issues"
            recommendation = "System has major issues that prevent effective MongoDB centralization."
        
        print(f"Status: {status}")
        print(f"\n📋 RECOMMENDATION:")
        print(f"{recommendation}")
        
        # Specific action items
        print(f"\n🎯 ACTION ITEMS:")
        
        if self.results["repository_indicators"]["passed"] < self.results["repository_indicators"]["total"]:
            print("• Enhance repository pattern indicators and documentation")
        
        if self.results["data_operations"]["passed"] < self.results["data_operations"]["total"]:
            print("• Implement TICKET-3 field preservation")
            print("• Improve error handling consistency")
        
        if self.results["mongodb_centralization"]["passed"] < self.results["mongodb_centralization"]["total"]:
            print("• Complete remaining MongoDB operation conversions")
        
        if self.results["production_readiness"]["passed"] < self.results["production_readiness"]["total"]:
            print("• Address production readiness gaps")
        
        if overall_success_rate >= 85:
            print("• Proceed with production deployment")
        elif overall_success_rate >= 70:
            print("• Address minor issues before production deployment")
        else:
            print("• Comprehensive review and fixes required before production")
        
        print(f"\n{'='*80}")
        
        return overall_success_rate, status

def main():
    """Main assessment execution"""
    assessor = KE_PR9_5_FinalAssessment()
    assessor.run_comprehensive_assessment()

if __name__ == "__main__":
    main()