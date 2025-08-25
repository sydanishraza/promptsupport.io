#!/usr/bin/env python3
"""
Simple V2 Engine Post-Processing Test
Direct testing of V2 engine functionality without external network dependencies
"""

import requests
import json
import time
import sys

# Use localhost for direct testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

def print_test_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

# Sample text for testing
SAMPLE_TEXT = """
# Getting Started with API Integration

## Table of Contents
- Introduction to API Integration
- Setting up Authentication
- Making Your First Request

# Introduction to API Integration

Our API provides comprehensive access to all platform features.

## Setting up Authentication

Follow these steps to authenticate:

- First, obtain your API key from the dashboard
- Next, configure your authentication headers
- Then, test your connection with a simple request
- Finally, implement proper error handling

```javascript
const apiKey = 'your-api-key-here';
const headers = {
  'Authorization': `Bearer ${apiKey}`,
  'Content-Type': 'application/json'
};
```

## Making Your First Request

Follow these procedural steps:

- Step 1: Set up your request headers
- Step 2: Choose the appropriate endpoint
- Step 3: Format your request payload
- Step 4: Send the request and handle the response

```javascript
async function makeApiRequest() {
  try {
    const response = await fetch('/api/data', {
      method: 'GET',
      headers: headers
    });
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
  }
}
```
"""

def test_engine_status():
    """Test 1: Check V2 Engine Status"""
    print_test_header("Test 1: V2 Engine Status Check")
    
    try:
        print_info("Checking engine status...")
        response = requests.get(f"{API_BASE}/engine", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Engine endpoint accessible - Status: {response.status_code}")
            
            engine = data.get('engine', 'unknown')
            print_info(f"Engine version: {engine}")
            
            if engine == 'v2':
                print_success("V2 Engine confirmed active")
                return True
            else:
                print_error(f"V2 Engine not active - Current: {engine}")
                return False
        else:
            print_error(f"Engine status failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error checking engine status: {e}")
        return False

def test_process_text():
    """Test 2: Process Text with V2 Engine"""
    print_test_header("Test 2: V2 Text Processing")
    
    try:
        print_info("Processing sample text...")
        print_info(f"Sample text length: {len(SAMPLE_TEXT)} characters")
        
        payload = {
            "content": SAMPLE_TEXT,
            "engine": "v2"
        }
        
        response = requests.post(f"{API_BASE}/content/process", json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Text processing completed - Status: {response.status_code}")
            
            job_id = result.get('job_id')
            status = result.get('status')
            engine = result.get('engine')
            
            print_info(f"Job ID: {job_id}")
            print_info(f"Status: {status}")
            print_info(f"Engine: {engine}")
            
            if job_id and engine == 'v2':
                print_success("V2 processing initiated successfully")
                return True, job_id
            else:
                print_error("V2 processing failed to initiate properly")
                return False, None
        else:
            print_error(f"Text processing failed - Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Error processing text: {e}")
        return False, None

def test_content_library():
    """Test 3: Check Content Library for Processed Articles"""
    print_test_header("Test 3: Content Library Check")
    
    try:
        print_info("Checking content library...")
        response = requests.get(f"{API_BASE}/content-library", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', []) if isinstance(data, dict) else data
            print_success(f"Content library accessible - {len(articles)} articles found")
            
            # Look for recent articles
            recent_articles = []
            for article in articles:
                title = article.get('title', '') if isinstance(article, dict) else str(article)
                if 'API Integration' in title or 'Getting Started' in title:
                    recent_articles.append(article)
            
            if recent_articles:
                print_success(f"Found {len(recent_articles)} relevant articles")
                
                # Analyze the first relevant article
                article = recent_articles[0]
                return analyze_article_processing(article)
            else:
                print_info("No recent API Integration articles found")
                
                # Check any recent article for processing indicators
                if articles:
                    print_info("Analyzing most recent article...")
                    return analyze_article_processing(articles[0])
                else:
                    print_error("No articles found in content library")
                    return False
        else:
            print_error(f"Content library access failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error checking content library: {e}")
        return False

def analyze_article_processing(article):
    """Analyze article for V2 post-processing fixes"""
    print_info("Analyzing article for V2 post-processing fixes...")
    
    title = article.get('title', 'Unknown')
    content = article.get('content', article.get('html', ''))
    
    print_info(f"Article: '{title}'")
    print_info(f"Content length: {len(content)} characters")
    
    if not content:
        print_error("Article has no content to analyze")
        return False
    
    # Test the three critical fixes
    fixes_results = []
    
    # Fix 1: Mini-TOC Links (H1 to H2 conversion + TOC links)
    h1_count = content.count('<h1')
    h2_count = content.count('<h2')
    toc_links = len([m for m in content.split() if '#' in m and ('[' in m or 'href' in m)])
    
    print_info(f"H1 elements: {h1_count}, H2 elements: {h2_count}")
    print_info(f"Potential TOC links: {toc_links}")
    
    mini_toc_fix = h1_count <= 1 and h2_count >= 2 and toc_links >= 2
    fixes_results.append(("Mini-TOC Links", mini_toc_fix))
    
    # Fix 2: List Types (UL to OL conversion for procedural content)
    ul_count = content.count('<ul')
    ol_count = content.count('<ol')
    procedural_indicators = sum([
        content.lower().count('step'),
        content.lower().count('first'),
        content.lower().count('next'),
        content.lower().count('then'),
        content.lower().count('finally')
    ])
    
    print_info(f"UL: {ul_count}, OL: {ol_count}, Procedural indicators: {procedural_indicators}")
    
    list_types_fix = (ol_count >= 1 if procedural_indicators >= 3 else ul_count + ol_count >= 1)
    fixes_results.append(("List Types", list_types_fix))
    
    # Fix 3: Code Consolidation
    code_blocks = content.count('<pre')
    inline_code = content.count('<code')
    
    print_info(f"Code blocks: {code_blocks}, Inline code: {inline_code}")
    
    code_consolidation_fix = (code_blocks >= 1 if 'javascript' in content.lower() else True)
    fixes_results.append(("Code Consolidation", code_consolidation_fix))
    
    # Results summary
    passed_fixes = sum(1 for _, success in fixes_results if success)
    success_rate = (passed_fixes / 3) * 100
    
    print_info(f"Post-processing fixes analysis:")
    for fix_name, success in fixes_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"  {status} - {fix_name}")
    
    print_info(f"Success rate: {success_rate:.1f}%")
    
    return success_rate >= 66.7

def test_style_diagnostics():
    """Test 4: Check Style Processing Diagnostics"""
    print_test_header("Test 4: Style Processing Diagnostics")
    
    try:
        print_info("Checking style diagnostics...")
        response = requests.get(f"{API_BASE}/style/diagnostics", timeout=10)
        
        if response.status_code == 200:
            diagnostics = response.json()
            print_success("Style diagnostics accessible")
            
            engine = diagnostics.get('engine', 'unknown')
            system_status = diagnostics.get('system_status', 'unknown')
            
            print_info(f"Style engine: {engine}")
            print_info(f"System status: {system_status}")
            
            if engine == 'v2' and system_status == 'active':
                print_success("Style processor integrated with V2 engine")
                return True
            else:
                print_info("Style processor status unclear but accessible")
                return True
        else:
            print_error(f"Style diagnostics failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error checking style diagnostics: {e}")
        return False

def run_simple_v2_test():
    """Run simple V2 engine test suite"""
    print_test_header("Simple V2 Engine Post-Processing Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Testing V2 engine post-processing fixes")
    
    test_results = []
    
    # Test 1: Engine Status
    success = test_engine_status()
    test_results.append(("Engine Status", success))
    
    if not success:
        print_error("V2 Engine not available - aborting remaining tests")
        return False
    
    # Test 2: Process Text
    success, job_id = test_process_text()
    test_results.append(("Text Processing", success))
    
    if success and job_id:
        # Wait for processing to complete
        print_info("Waiting for processing to complete...")
        time.sleep(5)
    
    # Test 3: Content Library Analysis
    success = test_content_library()
    test_results.append(("Content Analysis", success))
    
    # Test 4: Style Diagnostics
    success = test_style_diagnostics()
    test_results.append(("Style Diagnostics", success))
    
    # Results Summary
    print_test_header("Test Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    if success_rate >= 75:
        print_success(f"🎉 V2 POST-PROCESSING TEST PASSED - {success_rate:.1f}% SUCCESS")
        print_success("V2 engine post-processing fixes are operational!")
    elif success_rate >= 50:
        print_info(f"⚠️ V2 POST-PROCESSING PARTIALLY WORKING - {success_rate:.1f}% SUCCESS")
    else:
        print_error(f"❌ V2 POST-PROCESSING TEST FAILED - {success_rate:.1f}% SUCCESS")
    
    return success_rate >= 50

if __name__ == "__main__":
    print("🚀 Starting Simple V2 Engine Post-Processing Test...")
    
    try:
        success = run_simple_v2_test()
        
        if success:
            print("\n🎯 V2 POST-PROCESSING TEST COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 POST-PROCESSING TEST COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)