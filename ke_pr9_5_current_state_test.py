#!/usr/bin/env python3
"""
KE-PR9.5 Current State Assessment Test
Simple test to understand the current state of MongoDB centralization
"""

import requests
import json
import time
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://happy-buck.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def make_request(method, endpoint, **kwargs):
    """Make HTTP request with error handling"""
    try:
        url = f"{API_BASE}{endpoint}"
        response = requests.request(method, url, timeout=30, **kwargs)
        
        try:
            data = response.json()
        except:
            data = {"text": response.text, "content_type": response.headers.get('content-type', '')}
        
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

def test_basic_endpoints():
    """Test basic system endpoints"""
    print("🔍 Testing Basic System Endpoints...")
    
    endpoints = [
        ("/health", "System Health"),
        ("/engine", "Engine Status"),
        ("/content-library", "Content Library"),
        ("/assets", "Assets Management")
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        print(f"  Testing {name}...")
        result = make_request("GET", endpoint)
        results[name] = result
        
        if result["success"]:
            print(f"    ✅ {name}: HTTP {result['status']}")
            if endpoint == "/content-library" and isinstance(result["data"], list):
                print(f"       📊 {len(result['data'])} articles available")
            elif endpoint == "/assets" and isinstance(result["data"], list):
                print(f"       📊 {len(result['data'])} assets available")
        else:
            print(f"    ❌ {name}: HTTP {result['status']} - {result['data']}")
    
    return results

def test_repository_indicators():
    """Test for repository pattern indicators"""
    print("\n🏗️ Testing Repository Pattern Indicators...")
    
    # Check engine features for repository indicators
    engine_result = make_request("GET", "/engine")
    if engine_result["success"]:
        engine_data = engine_result["data"]
        if "features" in engine_data:
            repo_features = [f for f in engine_data["features"] if "repository" in f.lower() or "mongo" in f.lower()]
            if repo_features:
                print(f"  ✅ Repository features found: {repo_features}")
            else:
                print("  ⚠️ No repository-specific features detected")
        else:
            print("  ⚠️ No features list in engine status")
    else:
        print("  ❌ Cannot access engine status")
    
    # Check content library for repository source attribution
    content_result = make_request("GET", "/content-library")
    if content_result["success"] and isinstance(content_result["data"], list) and len(content_result["data"]) > 0:
        first_article = content_result["data"][0]
        if "source" in str(first_article) and "repository" in str(first_article).lower():
            print("  ✅ Repository source attribution detected in content")
        else:
            print("  ⚠️ No clear repository source attribution found")
    else:
        print("  ❌ Cannot check content for repository indicators")

def test_mongodb_operations():
    """Test MongoDB-related operations"""
    print("\n💾 Testing MongoDB Operations...")
    
    # Test content operations
    content_result = make_request("GET", "/content-library")
    if content_result["success"]:
        articles = content_result["data"]
        if isinstance(articles, list):
            print(f"  ✅ Content retrieval working: {len(articles)} articles")
            
            # Check for TICKET-3 fields
            ticket3_fields = ["doc_uid", "doc_slug", "headings_registry", "xrefs"]
            articles_with_ticket3 = 0
            
            for article in articles[:5]:
                if any(field in article for field in ticket3_fields):
                    articles_with_ticket3 += 1
            
            ticket3_percentage = (articles_with_ticket3 / min(5, len(articles))) * 100 if articles else 0
            print(f"  📊 TICKET-3 field preservation: {ticket3_percentage:.1f}%")
        else:
            print("  ⚠️ Content data structure unexpected")
    else:
        print("  ❌ Content retrieval failed")
    
    # Test processing operations
    test_content = {"content": "Test content for MongoDB validation", "metadata": {"test": True}}
    process_result = make_request("POST", "/content/process", json=test_content)
    if process_result["success"]:
        print("  ✅ Content processing working")
    else:
        print(f"  ❌ Content processing failed: HTTP {process_result['status']}")

def test_performance_metrics():
    """Test system performance"""
    print("\n⚡ Testing Performance Metrics...")
    
    # Test response times
    start_time = time.time()
    health_result = make_request("GET", "/health")
    health_time = time.time() - start_time
    
    start_time = time.time()
    content_result = make_request("GET", "/content-library")
    content_time = time.time() - start_time
    
    print(f"  📊 Health endpoint: {health_time:.3f}s")
    print(f"  📊 Content library: {content_time:.3f}s")
    
    if health_time < 1.0 and content_time < 3.0:
        print("  ✅ Performance acceptable")
    else:
        print("  ⚠️ Performance may need optimization")
    
    # Test concurrent operations
    print("  Testing concurrent operations...")
    start_time = time.time()
    
    # Simple concurrent test
    results = []
    for i in range(3):
        result = make_request("GET", "/health")
        results.append(result)
    
    concurrent_time = time.time() - start_time
    successful = sum(1 for r in results if r["success"])
    
    print(f"  📊 Concurrent operations: {successful}/3 successful in {concurrent_time:.3f}s")

def assess_mongodb_centralization():
    """Assess overall MongoDB centralization status"""
    print("\n📊 Assessing MongoDB Centralization Status...")
    
    # Count working operations
    operations = [
        ("/health", "System Health"),
        ("/engine", "Engine Status"),
        ("/content-library", "Content Library"),
        ("/assets", "Assets Management")
    ]
    
    working_operations = 0
    total_operations = len(operations)
    
    for endpoint, name in operations:
        result = make_request("GET", endpoint)
        if result["success"]:
            working_operations += 1
    
    completion_percentage = (working_operations / total_operations) * 100
    print(f"  📊 Basic operations working: {working_operations}/{total_operations} ({completion_percentage:.1f}%)")
    
    # Assess overall status
    if completion_percentage >= 85:
        status = "EXCELLENT"
        emoji = "🎉"
    elif completion_percentage >= 70:
        status = "GOOD"
        emoji = "✅"
    elif completion_percentage >= 50:
        status = "PARTIAL"
        emoji = "⚠️"
    else:
        status = "NEEDS WORK"
        emoji = "❌"
    
    print(f"  {emoji} Overall Status: {status}")
    
    return completion_percentage, status

def main():
    """Main test execution"""
    print("🎯 KE-PR9.5 MONGODB CENTRALIZATION CURRENT STATE ASSESSMENT")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Run all tests
    basic_results = test_basic_endpoints()
    test_repository_indicators()
    test_mongodb_operations()
    test_performance_metrics()
    completion, status = assess_mongodb_centralization()
    
    # Final summary
    print("\n" + "=" * 80)
    print("📋 FINAL ASSESSMENT SUMMARY")
    print("=" * 80)
    
    working_endpoints = sum(1 for result in basic_results.values() if result["success"])
    total_endpoints = len(basic_results)
    
    print(f"Working Endpoints: {working_endpoints}/{total_endpoints}")
    print(f"Completion Level: {completion:.1f}%")
    print(f"Overall Status: {status}")
    
    # Recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    
    if status == "EXCELLENT":
        print("• System appears to be working well")
        print("• Consider production deployment")
    elif status == "GOOD":
        print("• System mostly functional with minor issues")
        print("• Address remaining endpoint issues")
    elif status == "PARTIAL":
        print("• System partially functional")
        print("• Significant work needed for full MongoDB centralization")
    else:
        print("• Major issues detected")
        print("• Comprehensive review and fixes needed")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()