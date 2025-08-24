#!/usr/bin/env python3
"""
Focused V2 Engine Step 10 Adaptive Adjustment Testing
Quick diagnostic test to identify the 2 specific failed areas
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_engine_status():
    """Test basic engine status"""
    print("🔍 Testing V2 Engine Status...")
    try:
        response = requests.get(f"{API_BASE}/engine", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Engine Status: {data.get('engine', 'unknown')}")
            print(f"📋 Available endpoints: {list(data.get('endpoints', {}).keys())}")
            print(f"🎯 Available features: {data.get('features', [])}")
            return data
        else:
            print(f"❌ Engine status failed: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Engine status error: {str(e)}")
        return None

def test_adjustment_diagnostics():
    """Test adjustment diagnostics endpoint"""
    print("\n📊 Testing Adjustment Diagnostics...")
    try:
        response = requests.get(f"{API_BASE}/adjustment/diagnostics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Adjustment diagnostics working")
            print(f"📈 Total runs: {data.get('total_adjustment_runs', 0)}")
            print(f"⚠️ Runs with issues: {data.get('adjustment_runs_with_issues', 0)}")
            print(f"📋 Results count: {len(data.get('adjustment_results', []))}")
            return data
        else:
            print(f"❌ Adjustment diagnostics failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Adjustment diagnostics error: {str(e)}")
        return None

def test_content_library():
    """Test content library access"""
    print("\n📚 Testing Content Library Access...")
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content library working")
            print(f"📄 Total articles: {len(data.get('articles', []))}")
            return data
        elif response.status_code == 500:
            print(f"❌ Content library HTTP 500 error - This may be one of the 2 failed tests!")
            print(f"Response: {response.text[:200]}")
            return None
        else:
            print(f"❌ Content library failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Content library error: {str(e)}")
        return None

def test_url_processing():
    """Test URL processing pipeline"""
    print("\n🌐 Testing URL Processing Pipeline...")
    try:
        response = requests.post(f"{API_BASE}/content/url", 
                               json={"url": "https://example.com"}, 
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ URL processing working")
            return data
        elif response.status_code == 404:
            print(f"❌ URL processing HTTP 404 error - This may be one of the 2 failed tests!")
            print(f"Response: {response.text[:200]}")
            return None
        else:
            print(f"❌ URL processing failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ URL processing error: {str(e)}")
        return None

def test_text_processing():
    """Test basic text processing"""
    print("\n📝 Testing Text Processing Pipeline...")
    try:
        test_content = "This is a test document for adaptive adjustment analysis. " * 20
        response = requests.post(f"{API_BASE}/content/process", 
                               json={"content": test_content}, 
                               timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Text processing working")
            print(f"🔧 Engine: {data.get('engine', 'unknown')}")
            return data
        else:
            print(f"❌ Text processing failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Text processing error: {str(e)}")
        return None

def main():
    """Run focused diagnostic tests"""
    print("🎯 V2 ENGINE STEP 10 ADAPTIVE ADJUSTMENT - FOCUSED DIAGNOSTIC TEST")
    print("🔍 Identifying the 2 specific failed areas from previous 81.8% success rate")
    print("=" * 70)
    
    results = {
        "engine_status": test_engine_status(),
        "adjustment_diagnostics": test_adjustment_diagnostics(),
        "content_library": test_content_library(),
        "url_processing": test_url_processing(),
        "text_processing": test_text_processing()
    }
    
    print("\n" + "=" * 70)
    print("🎯 DIAGNOSTIC SUMMARY:")
    
    failed_areas = []
    working_areas = []
    
    for test_name, result in results.items():
        if result is None:
            failed_areas.append(test_name)
            print(f"❌ {test_name}: FAILED")
        else:
            working_areas.append(test_name)
            print(f"✅ {test_name}: WORKING")
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Working: {len(working_areas)}/5 ({len(working_areas)/5*100:.1f}%)")
    print(f"❌ Failed: {len(failed_areas)}/5 ({len(failed_areas)/5*100:.1f}%)")
    
    if failed_areas:
        print(f"\n🎯 IDENTIFIED FAILED AREAS (likely the 2 mentioned in previous results):")
        for i, area in enumerate(failed_areas, 1):
            print(f"   {i}. {area}")
    
    # Save results
    with open('/app/focused_step10_results.json', 'w') as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "working_areas": working_areas,
            "failed_areas": failed_areas,
            "success_rate": len(working_areas)/5*100,
            "detailed_results": results
        }, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: /app/focused_step10_results.json")
    
    return results

if __name__ == "__main__":
    main()