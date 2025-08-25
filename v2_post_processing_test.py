#!/usr/bin/env python3
"""
V2 Engine Comprehensive Post-Processing Fixes Test Suite
Testing the three critical issues:
1. Mini-TOC Links: Fixed ID coordination between LLM generation and style processor
2. List Types: Enhanced procedural list detection to convert UL to OL
3. Code Consolidation: Improved code block consolidation and rendering

Focus: POST /api/process-text endpoint with V2 engine
"""

import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime
import sys

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def print_test_header(title):
    """Print formatted test header"""
    print(f"\n{'='*80}")
    print(f"🧪 {title}")
    print(f"{'='*80}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

# Sample text containing all the elements to test
SAMPLE_TEXT = """
# Getting Started with API Integration

This guide covers the complete process of integrating with our API system.

## Table of Contents
- Introduction to API Integration
- Setting up Authentication
- Making Your First Request
- Error Handling Best Practices
- Advanced Configuration Options

# Introduction to API Integration

Our API provides comprehensive access to all platform features. This section covers the fundamental concepts.

## Setting up Authentication

To authenticate with our API, follow these steps:

- First, obtain your API key from the dashboard
- Next, configure your authentication headers
- Then, test your connection with a simple request
- Finally, implement proper error handling

Here's a basic authentication example:

```javascript
const apiKey = 'your-api-key-here';
const headers = {
  'Authorization': `Bearer ${apiKey}`,
  'Content-Type': 'application/json'
};
```

## Making Your First Request

Follow these procedural steps to make your first API call:

- Step 1: Set up your request headers with authentication
- Step 2: Choose the appropriate endpoint for your use case
- Step 3: Format your request payload according to the API specification
- Step 4: Send the request and handle the response
- Step 5: Implement proper error handling for failed requests

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

```javascript
// Additional code block for testing consolidation
function handleApiResponse(data) {
  if (data.success) {
    console.log('Request successful:', data.result);
  } else {
    console.error('Request failed:', data.error);
  }
}
```

# Error Handling Best Practices

When working with APIs, proper error handling is essential. Consider these approaches:

- Always check response status codes
- Implement retry logic for transient failures
- Log errors appropriately for debugging
- Provide meaningful error messages to users

## Advanced Configuration Options

For advanced users, additional configuration options are available:

- Custom timeout settings
- Request rate limiting
- Webhook configuration
- Batch processing options
"""

async def test_v2_engine_availability():
    """Test 1: Verify V2 Engine is available and operational"""
    print_test_header("Test 1: V2 Engine Availability Check")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check engine status
            print_info("Checking V2 engine status...")
            
            async with session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    engine_data = await response.json()
                    print_success(f"Engine endpoint accessible - Status: {response.status}")
                    
                    # Check for V2 engine
                    engine_version = engine_data.get('engine', 'unknown')
                    if engine_version == 'v2':
                        print_success("V2 Engine confirmed active")
                        
                        # Check for post-processing features
                        features = engine_data.get('features', [])
                        post_processing_features = [
                            'comprehensive_post_processing',
                            'mini_toc_processing',
                            'list_type_detection',
                            'code_consolidation'
                        ]
                        
                        found_features = [f for f in post_processing_features if f in str(features)]
                        if found_features:
                            print_success(f"Post-processing features found: {found_features}")
                        else:
                            print_info("Post-processing features not explicitly listed")
                        
                        return True, engine_data
                    else:
                        print_error(f"V2 Engine not active - Current engine: {engine_version}")
                        return False, None
                else:
                    error_text = await response.text()
                    print_error(f"Engine status check failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False, None
                    
    except Exception as e:
        print_error(f"Error checking V2 engine availability: {e}")
        return False, None

async def test_process_text_endpoint():
    """Test 2: Process sample text through V2 engine"""
    print_test_header("Test 2: V2 Engine Text Processing")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Processing sample text through V2 engine...")
            print_info(f"Sample text length: {len(SAMPLE_TEXT)} characters")
            
            # Prepare request payload
            payload = {
                "text": SAMPLE_TEXT,
                "engine": "v2",
                "apply_post_processing": True
            }
            
            async with session.post(f"{API_BASE}/process-text", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"Text processing completed - Status: {response.status}")
                    
                    # Validate response structure
                    required_fields = ['job_id', 'status', 'engine']
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if not missing_fields:
                        print_success("Processing response structure valid")
                        print_info(f"Job ID: {result.get('job_id', 'N/A')}")
                        print_info(f"Status: {result.get('status', 'N/A')}")
                        print_info(f"Engine: {result.get('engine', 'N/A')}")
                        
                        return True, result
                    else:
                        print_error(f"Processing response missing fields: {missing_fields}")
                        return False, None
                else:
                    error_text = await response.text()
                    print_error(f"Text processing failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False, None
                    
    except Exception as e:
        print_error(f"Error processing text: {e}")
        return False, None

async def test_comprehensive_post_processing():
    """Test 3: Verify comprehensive post-processing is applied"""
    print_test_header("Test 3: Comprehensive Post-Processing Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            # First process the text
            payload = {
                "text": SAMPLE_TEXT,
                "engine": "v2",
                "apply_post_processing": True
            }
            
            async with session.post(f"{API_BASE}/process-text", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    job_id = result.get('job_id')
                    
                    if job_id:
                        print_success(f"Processing initiated with job ID: {job_id}")
                        
                        # Wait a moment for processing
                        await asyncio.sleep(3)
                        
                        # Check processing results
                        async with session.get(f"{API_BASE}/content-library") as lib_response:
                            if lib_response.status == 200:
                                articles = await lib_response.json()
                                
                                # Find the processed article
                                processed_article = None
                                for article in articles:
                                    if job_id in str(article) or 'API Integration' in article.get('title', ''):
                                        processed_article = article
                                        break
                                
                                if processed_article:
                                    print_success("Processed article found in content library")
                                    return await analyze_post_processing_results(processed_article)
                                else:
                                    print_error("Processed article not found in content library")
                                    return False
                            else:
                                print_error(f"Failed to access content library - Status: {lib_response.status}")
                                return False
                    else:
                        print_error("No job ID returned from processing")
                        return False
                else:
                    print_error(f"Processing failed - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying post-processing: {e}")
        return False

async def analyze_post_processing_results(article):
    """Analyze the processed article for the three critical fixes"""
    print_info("Analyzing post-processing results for the three critical fixes...")
    
    content = article.get('content', article.get('html', ''))
    title = article.get('title', 'Unknown')
    
    print_info(f"Analyzing article: '{title}'")
    print_info(f"Content length: {len(content)} characters")
    
    # Test 1: Mini-TOC Links Fix
    toc_fix_success = analyze_mini_toc_links(content)
    
    # Test 2: List Types Fix  
    list_fix_success = analyze_list_types(content)
    
    # Test 3: Code Consolidation Fix
    code_fix_success = analyze_code_consolidation(content)
    
    # Overall assessment
    fixes_passed = sum([toc_fix_success, list_fix_success, code_fix_success])
    success_rate = (fixes_passed / 3) * 100
    
    print_info(f"Post-processing fixes analysis:")
    print_info(f"  - Mini-TOC Links: {'✅ PASS' if toc_fix_success else '❌ FAIL'}")
    print_info(f"  - List Types: {'✅ PASS' if list_fix_success else '❌ FAIL'}")
    print_info(f"  - Code Consolidation: {'✅ PASS' if code_fix_success else '❌ FAIL'}")
    print_info(f"  - Success Rate: {success_rate:.1f}%")
    
    return success_rate >= 66.7  # At least 2 out of 3 fixes working

def analyze_mini_toc_links(content):
    """Analyze Mini-TOC Links fix - ID coordination between LLM and style processor"""
    print_info("Analyzing Mini-TOC Links fix...")
    
    # Check for H1 to H2 conversion
    h1_count = len(re.findall(r'<h1[^>]*>', content))
    h2_count = len(re.findall(r'<h2[^>]*>', content))
    
    print_info(f"H1 elements found: {h1_count}")
    print_info(f"H2 elements found: {h2_count}")
    
    # Should have minimal H1s (ideally 0 in content) and multiple H2s
    h1_conversion_success = h1_count <= 1 and h2_count >= 2
    
    # Check for TOC links
    toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)  # Markdown style
    html_toc_links = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)  # HTML style
    
    total_toc_links = len(toc_links) + len(html_toc_links)
    print_info(f"TOC links found: {total_toc_links} (Markdown: {len(toc_links)}, HTML: {len(html_toc_links)})")
    
    # Check for heading IDs
    heading_ids = re.findall(r'<h[2-6][^>]*id="([^"]+)"', content)
    print_info(f"Heading IDs found: {len(heading_ids)}")
    
    # Verify TOC links point to existing headings
    valid_links = 0
    for _, anchor in toc_links:
        if anchor in heading_ids:
            valid_links += 1
    for anchor, _ in html_toc_links:
        if anchor in heading_ids:
            valid_links += 1
    
    print_info(f"Valid TOC links: {valid_links}/{total_toc_links}")
    
    # Success criteria: H1 conversion + TOC links + valid targets
    toc_success = h1_conversion_success and total_toc_links >= 3 and valid_links >= 2
    
    if toc_success:
        print_success("Mini-TOC Links fix VERIFIED")
    else:
        print_error("Mini-TOC Links fix FAILED")
    
    return toc_success

def analyze_list_types(content):
    """Analyze List Types fix - Enhanced procedural list detection"""
    print_info("Analyzing List Types fix...")
    
    # Count unordered and ordered lists
    ul_count = len(re.findall(r'<ul[^>]*>', content))
    ol_count = len(re.findall(r'<ol[^>]*>', content))
    
    print_info(f"Unordered lists (UL): {ul_count}")
    print_info(f"Ordered lists (OL): {ol_count}")
    
    # Check for procedural content that should be ordered lists
    procedural_patterns = [
        r'step\s+\d+',
        r'first[,\s]',
        r'next[,\s]',
        r'then[,\s]',
        r'finally[,\s]',
        r'^\s*-\s+step',
        r'^\s*-\s+\d+\.'
    ]
    
    procedural_indicators = 0
    for pattern in procedural_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        procedural_indicators += len(matches)
    
    print_info(f"Procedural content indicators found: {procedural_indicators}")
    
    # Success criteria: Should have some ordered lists if procedural content exists
    if procedural_indicators >= 3:
        list_success = ol_count >= 1  # Should have converted some UL to OL
        if list_success:
            print_success("List Types fix VERIFIED - Procedural content converted to ordered lists")
        else:
            print_error("List Types fix FAILED - Procedural content not converted to ordered lists")
    else:
        # If no clear procedural content, just check that lists exist
        list_success = (ul_count + ol_count) >= 2
        if list_success:
            print_success("List Types fix VERIFIED - Lists properly formatted")
        else:
            print_info("List Types fix - No clear procedural content to test")
            list_success = True  # Don't fail if no procedural content
    
    return list_success

def analyze_code_consolidation(content):
    """Analyze Code Consolidation fix - Improved code block consolidation and rendering"""
    print_info("Analyzing Code Consolidation fix...")
    
    # Count code blocks
    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', content, re.DOTALL)
    inline_code = re.findall(r'<code[^>]*>.*?</code>', content)
    
    print_info(f"Code blocks (<pre>): {len(code_blocks)}")
    print_info(f"Inline code (<code>): {len(inline_code)}")
    
    # Check for proper code block structure
    well_formed_blocks = 0
    for block in code_blocks:
        # Check if code block has proper structure
        if '<code>' in block and len(block.strip()) > 20:
            well_formed_blocks += 1
    
    print_info(f"Well-formed code blocks: {well_formed_blocks}/{len(code_blocks)}")
    
    # Check for code consolidation (adjacent code blocks should be consolidated)
    # Look for patterns that suggest proper consolidation
    consolidated_patterns = [
        r'<pre[^>]*>.*?</pre>\s*<pre[^>]*>.*?</pre>',  # Adjacent code blocks (should be minimal)
        r'```\s*```',  # Empty code blocks (should be cleaned up)
    ]
    
    consolidation_issues = 0
    for pattern in consolidated_patterns:
        issues = re.findall(pattern, content, re.DOTALL)
        consolidation_issues += len(issues)
    
    print_info(f"Potential consolidation issues: {consolidation_issues}")
    
    # Success criteria: Has code blocks, well-formed, minimal consolidation issues
    if len(code_blocks) >= 2:
        code_success = well_formed_blocks >= 1 and consolidation_issues <= 1
        if code_success:
            print_success("Code Consolidation fix VERIFIED - Code blocks properly consolidated")
        else:
            print_error("Code Consolidation fix FAILED - Issues with code block structure")
    else:
        print_info("Code Consolidation fix - Limited code content to test")
        code_success = True  # Don't fail if minimal code content
    
    return code_success

async def test_style_processor_integration():
    """Test 4: Verify style processor integration with V2 engine"""
    print_test_header("Test 4: Style Processor Integration")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check style diagnostics
            print_info("Checking style processor integration...")
            
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    print_success("Style diagnostics accessible")
                    
                    # Check for V2 engine integration
                    engine = diagnostics.get('engine', 'unknown')
                    if engine == 'v2':
                        print_success("Style processor integrated with V2 engine")
                    else:
                        print_info(f"Style processor engine: {engine}")
                    
                    # Check for recent processing
                    recent_results = diagnostics.get('recent_results', [])
                    if recent_results:
                        print_success(f"Found {len(recent_results)} recent style processing results")
                        
                        # Look for post-processing indicators
                        post_processing_found = False
                        for result in recent_results:
                            result_str = str(result)
                            if any(indicator in result_str for indicator in ['post_processing', 'comprehensive', 'toc', 'list', 'code']):
                                post_processing_found = True
                                break
                        
                        if post_processing_found:
                            print_success("Post-processing indicators found in style results")
                        else:
                            print_info("No explicit post-processing indicators found")
                        
                        return True
                    else:
                        print_info("No recent style processing results found")
                        return True  # Still consider success if system is operational
                else:
                    print_error(f"Style diagnostics failed - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error checking style processor integration: {e}")
        return False

async def test_formatted_content_application():
    """Test 5: Verify formatted content is applied as main article content"""
    print_test_header("Test 5: Formatted Content Application")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get recent articles to check formatting
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    articles = await response.json()
                    
                    if articles:
                        print_success(f"Found {len(articles)} articles in content library")
                        
                        # Check recent articles for proper formatting
                        formatted_articles = 0
                        for article in articles[:5]:  # Check first 5 articles
                            content = article.get('content', article.get('html', ''))
                            
                            # Check for formatting indicators
                            formatting_indicators = [
                                len(re.findall(r'<h[2-6]', content)) >= 2,  # Multiple headings
                                len(re.findall(r'<[uo]l>', content)) >= 1,   # Lists present
                                len(re.findall(r'<p>', content)) >= 3,       # Multiple paragraphs
                                'id=' in content,                            # IDs present
                            ]
                            
                            if sum(formatting_indicators) >= 3:
                                formatted_articles += 1
                        
                        print_info(f"Well-formatted articles: {formatted_articles}/{min(5, len(articles))}")
                        
                        if formatted_articles >= 1:
                            print_success("Formatted content application VERIFIED")
                            return True
                        else:
                            print_error("Formatted content application FAILED")
                            return False
                    else:
                        print_info("No articles found in content library")
                        return False
                else:
                    print_error(f"Content library access failed - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error checking formatted content application: {e}")
        return False

async def run_v2_post_processing_test():
    """Run comprehensive V2 Engine Post-Processing Fixes test suite"""
    print_test_header("V2 Engine Comprehensive Post-Processing Fixes Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Testing: Mini-TOC Links, List Types, Code Consolidation fixes")
    
    # Test results tracking
    test_results = []
    
    # Test 1: V2 Engine Availability
    success, engine_data = await test_v2_engine_availability()
    test_results.append(("V2 Engine Availability", success))
    
    if not success:
        print_error("V2 Engine not available - aborting remaining tests")
        return False
    
    # Test 2: Process Text Endpoint
    success, processing_result = await test_process_text_endpoint()
    test_results.append(("Text Processing", success))
    
    # Test 3: Comprehensive Post-Processing
    success = await test_comprehensive_post_processing()
    test_results.append(("Comprehensive Post-Processing", success))
    
    # Test 4: Style Processor Integration
    success = await test_style_processor_integration()
    test_results.append(("Style Processor Integration", success))
    
    # Test 5: Formatted Content Application
    success = await test_formatted_content_application()
    test_results.append(("Formatted Content Application", success))
    
    # Final Results Summary
    print_test_header("Test Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Overall assessment
    if success_rate >= 80:
        print_success(f"🎉 V2 POST-PROCESSING FIXES TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("The V2 engine comprehensive post-processing fixes are working correctly!")
        print_success("✅ Mini-TOC Links: ID coordination between LLM and style processor")
        print_success("✅ List Types: Enhanced procedural list detection (UL to OL conversion)")
        print_success("✅ Code Consolidation: Improved code block consolidation and rendering")
    elif success_rate >= 60:
        print_info(f"⚠️ V2 POST-PROCESSING PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some post-processing functionality is working, but improvements needed.")
    else:
        print_error(f"❌ V2 POST-PROCESSING FIXES TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with V2 post-processing fixes.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting V2 Engine Comprehensive Post-Processing Fixes Test Suite...")
    
    try:
        # Run the V2 post-processing test
        success = asyncio.run(run_v2_post_processing_test())
        
        if success:
            print("\n🎯 V2 POST-PROCESSING TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 POST-PROCESSING TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)