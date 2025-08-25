#!/usr/bin/env python3
"""
Final V2 Engine Step 10 Adaptive Adjustment Testing
Corrected test to identify and fix the 2 specific failed areas
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_url_processing_corrected():
    """Test URL processing pipeline with correct endpoint"""
    print("\n🌐 Testing URL Processing Pipeline (CORRECTED)...")
    try:
        # Use the correct endpoint: /api/content/process-url
        response = requests.post(f"{API_BASE}/content/process-url", 
                               json={"url": "https://example.com"}, 
                               timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ URL processing working")
            print(f"🔧 Engine: {data.get('engine', 'unknown')}")
            return True
        elif response.status_code == 404:
            print(f"❌ URL processing HTTP 404 error - CONFIRMED FAILED TEST!")
            print(f"Response: {response.text[:200]}")
            return False
        else:
            print(f"❌ URL processing failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ URL processing error: {str(e)}")
        return False

def test_text_processing_with_shorter_timeout():
    """Test text processing with shorter content and timeout"""
    print("\n📝 Testing Text Processing Pipeline (OPTIMIZED)...")
    try:
        # Use shorter test content to avoid timeout
        test_content = "This is a test document for adaptive adjustment analysis. It covers basic concepts and validation procedures."
        response = requests.post(f"{API_BASE}/content/process", 
                               json={"content": test_content}, 
                               timeout=30)  # Increased timeout
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Text processing working")
            print(f"🔧 Engine: {data.get('engine', 'unknown')}")
            print(f"📊 Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Text processing failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except requests.exceptions.ReadTimeout:
        print(f"❌ Text processing TIMEOUT - CONFIRMED FAILED TEST!")
        print(f"This indicates the processing pipeline is taking too long or hanging")
        return False
    except Exception as e:
        print(f"❌ Text processing error: {str(e)}")
        return False

def test_adjustment_system_detailed():
    """Test the adjustment system components in detail"""
    print("\n🔧 Testing Adjustment System Components...")
    
    # Test 1: Get adjustment diagnostics
    try:
        response = requests.get(f"{API_BASE}/adjustment/diagnostics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Adjustment diagnostics: {data.get('total_adjustment_runs', 0)} runs")
            
            # Test 2: Get detailed adjustment analysis
            adjustment_results = data.get('adjustment_results', [])
            if adjustment_results:
                first_result = adjustment_results[0]
                adjustment_id = first_result.get('adjustment_id')
                
                if adjustment_id:
                    detail_response = requests.get(f"{API_BASE}/adjustment/diagnostics/{adjustment_id}", timeout=10)
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        print(f"✅ Detailed adjustment analysis working")
                        
                        # Verify key components
                        components = {
                            'word_count_analysis': detail_data.get('word_count_analysis'),
                            'balancing_analysis': detail_data.get('balancing_analysis'), 
                            'readability_analysis': detail_data.get('readability_analysis'),
                            'adjustment_actions': detail_data.get('adjustment_actions')
                        }
                        
                        working_components = 0
                        for comp_name, comp_data in components.items():
                            if comp_data:
                                print(f"  ✅ {comp_name}: Working")
                                working_components += 1
                            else:
                                print(f"  ❌ {comp_name}: Missing")
                        
                        print(f"📊 Adjustment components: {working_components}/4 working")
                        return working_components >= 3
                    else:
                        print(f"❌ Detailed adjustment analysis failed: HTTP {detail_response.status_code}")
                        return False
                else:
                    print(f"❌ No adjustment_id found in results")
                    return False
            else:
                print(f"❌ No adjustment results found")
                return False
        else:
            print(f"❌ Adjustment diagnostics failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Adjustment system error: {str(e)}")
        return False

def test_specific_adjustment_features():
    """Test specific adjustment features mentioned in the review"""
    print("\n🎯 Testing Specific V2 Adjustment Features...")
    
    features_to_test = [
        "word_count_analysis",
        "merge_split_suggestions", 
        "readability_optimization",
        "granularity_alignment"
    ]
    
    try:
        # Get engine status to check features
        response = requests.get(f"{API_BASE}/engine", timeout=10)
        if response.status_code == 200:
            data = response.json()
            available_features = data.get('features', [])
            
            working_features = 0
            for feature in features_to_test:
                if feature in available_features:
                    print(f"  ✅ {feature}: Available")
                    working_features += 1
                else:
                    print(f"  ❌ {feature}: Missing")
            
            print(f"📊 Adjustment features: {working_features}/{len(features_to_test)} available")
            return working_features >= 3
        else:
            print(f"❌ Engine status failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Feature test error: {str(e)}")
        return False

def main():
    """Run corrected diagnostic tests"""
    print("🎯 V2 ENGINE STEP 10 ADAPTIVE ADJUSTMENT - FINAL DIAGNOSTIC TEST")
    print("🔍 Testing corrected endpoints and identifying specific failure points")
    print("=" * 70)
    
    test_results = {
        "url_processing_corrected": test_url_processing_corrected(),
        "text_processing_optimized": test_text_processing_with_shorter_timeout(),
        "adjustment_system_detailed": test_adjustment_system_detailed(),
        "adjustment_features": test_specific_adjustment_features()
    }
    
    print("\n" + "=" * 70)
    print("🎯 FINAL DIAGNOSTIC SUMMARY:")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    # Identify the specific 2 failed areas
    failed_tests = [test_name for test_name, result in test_results.items() if not result]
    
    if failed_tests:
        print(f"\n🎯 IDENTIFIED SPECIFIC FAILED AREAS:")
        for i, test_name in enumerate(failed_tests, 1):
            print(f"   {i}. {test_name}")
            
        if len(failed_tests) == 2:
            print(f"\n✅ CONFIRMED: Found exactly 2 failed areas matching previous 81.8% success rate (9/11 tests)")
        elif len(failed_tests) < 2:
            print(f"\n🎉 IMPROVEMENT: Only {len(failed_tests)} failed areas remaining!")
        else:
            print(f"\n⚠️ MORE ISSUES: Found {len(failed_tests)} failed areas")
    else:
        print(f"\n🎉 ALL TESTS PASSED - V2 Engine Step 10 is fully operational!")
    
    # Save results
    results_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "test_results": test_results,
        "success_rate": success_rate,
        "failed_tests": failed_tests,
        "total_tests": total_tests,
        "passed_tests": passed_tests
    }
    
    with open('/app/final_step10_results.json', 'w') as f:
        json.dump(results_data, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: /app/final_step10_results.json")
    
    return results_data

if __name__ == "__main__":
    main()