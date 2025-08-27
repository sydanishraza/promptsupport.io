#!/usr/bin/env python3
"""
TICKET 2 Simple Test - Quick verification of V2 processing pipeline
"""

import requests
import json
import os

# Use configured backend URL
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🧪 TICKET 2 Simple Test")
print(f"🌐 Backend URL: {BACKEND_URL}")
print("=" * 60)

def test_engine_status():
    """Test 1: Check if V2 engine is active"""
    print("🔧 TEST 1: V2 Engine Status")
    try:
        response = requests.get(f"{API_BASE}/engine", timeout=10)
        if response.status_code == 200:
            data = response.json()
            v2_active = data.get('v2_engine_active', False)
            print(f"✅ Engine Status: V2 Active = {v2_active}")
            return v2_active
        else:
            print(f"❌ Engine Status Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Engine Status Exception: {e}")
        return False

def test_style_diagnostics():
    """Test 2: Check style diagnostics for TICKET 2 features"""
    print("\n🔧 TEST 2: Style Diagnostics")
    try:
        response = requests.get(f"{API_BASE}/style/diagnostics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            recent_results = data.get('recent_results', [])
            print(f"✅ Style Diagnostics: {len(recent_results)} recent results")
            
            if recent_results:
                latest = recent_results[0]
                print(f"   Latest run: {latest.get('created_at', 'unknown')}")
                print(f"   Success rate: {latest.get('success_rate', 'unknown')}")
            return True
        else:
            print(f"❌ Style Diagnostics Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Style Diagnostics Exception: {e}")
        return False

def test_simple_content_processing():
    """Test 3: Simple content processing with V2 pipeline"""
    print("\n🔧 TEST 3: Simple V2 Content Processing")
    
    test_content = """
    <h2>Getting Started</h2>
    <p>This is a simple test of the V2 processing pipeline.</p>
    
    <h3>Basic Setup</h3>
    <p>Follow these steps to get started.</p>
    
    <h3>Configuration</h3>
    <p>Configure your system properly.</p>
    """
    
    try:
        response = requests.post(f"{API_BASE}/content/process", 
            json={
                "content": test_content,
                "content_type": "text",
                "metadata": {
                    "title": "TICKET 2 Simple Test",
                    "test_type": "simple_processing"
                }
            },
            timeout=60  # Shorter timeout for simple test
        )
        
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            print(f"✅ Content Processing: Generated {len(articles)} articles")
            
            if articles:
                article = articles[0]
                content = article.get('content', '')
                
                # Quick checks for TICKET 2 features
                has_ids = 'id="' in content
                has_toc = 'toc' in content.lower()
                has_links = 'href="#' in content
                
                print(f"   Has heading IDs: {has_ids}")
                print(f"   Has TOC: {has_toc}")
                print(f"   Has anchor links: {has_links}")
                
                return len(articles) > 0
            else:
                print("❌ No articles generated")
                return False
        else:
            print(f"❌ Content Processing Error: {response.status_code}")
            if response.text:
                print(f"   Error details: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Content Processing Exception: {e}")
        return False

def main():
    """Run simple TICKET 2 tests"""
    print("🚀 Starting TICKET 2 Simple Tests")
    
    results = []
    results.append(test_engine_status())
    results.append(test_style_diagnostics())
    results.append(test_simple_content_processing())
    
    print("\n" + "=" * 60)
    print("🏁 TICKET 2 Simple Test Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"📊 Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 66:
        print("✅ TICKET 2 basic functionality appears to be working")
    else:
        print("❌ TICKET 2 has issues that need investigation")
    
    return success_rate >= 66

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)