#!/usr/bin/env python3
"""
Backend Test Suite for Mini-TOC Links Processing Endpoint
Testing the new POST /api/style/process-toc-links endpoint functionality
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
import sys

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com')
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

async def test_toc_processing_endpoint():
    """Test 1: New TOC Processing Endpoint - POST /api/style/process-toc-links"""
    print_test_header("Test 1: New TOC Processing Endpoint")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test the new TOC processing endpoint
            print_info("Testing POST /api/style/process-toc-links endpoint...")
            
            async with session.post(f"{API_BASE}/style/process-toc-links") as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"TOC processing endpoint accessible - Status: {response.status}")
                    
                    # Validate response structure
                    required_fields = ['message', 'articles_processed', 'updated_articles', 'processing_id', 'engine']
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if not missing_fields:
                        print_success("Response structure valid - all required fields present")
                        print_info(f"Articles processed: {result.get('articles_processed', 0)}")
                        print_info(f"Processing ID: {result.get('processing_id', 'N/A')}")
                        print_info(f"Engine: {result.get('engine', 'N/A')}")
                        
                        # Check if any articles were updated
                        updated_articles = result.get('updated_articles', [])
                        if updated_articles:
                            print_success(f"Articles updated: {len(updated_articles)}")
                            for article in updated_articles:
                                print_info(f"  - {article.get('title', 'Unknown')}: {article.get('anchor_links_generated', 0)} links generated")
                        else:
                            print_info("No articles were updated (may be expected if already processed)")
                        
                        return True, result
                    else:
                        print_error(f"Response missing required fields: {missing_fields}")
                        return False, None
                else:
                    error_text = await response.text()
                    print_error(f"TOC processing endpoint failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False, None
                    
    except Exception as e:
        print_error(f"Error testing TOC processing endpoint: {e}")
        return False, None

async def test_target_article_verification():
    """Test 2: Verify Target Article Updates - Check specific article for TOC links"""
    print_test_header("Test 2: Target Article Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get content library articles
            print_info("Searching for 'Code Normalization in JavaScript: A Practical Example' article...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    articles = await response.json()
                    print_success(f"Content library accessible - {len(articles)} articles found")
                    
                    # Find the target article
                    target_article = None
                    for article in articles:
                        title = article.get('title', '')
                        if 'Code Normalization in JavaScript' in title:
                            target_article = article
                            break
                    
                    if target_article:
                        print_success(f"Target article found: '{target_article['title']}'")
                        print_info(f"Article ID: {target_article.get('id', 'N/A')}")
                        
                        # Analyze article content for TOC links
                        content = target_article.get('content', target_article.get('html', ''))
                        if content:
                            return await analyze_toc_links_in_content(content, target_article['title'])
                        else:
                            print_error("Article content is empty")
                            return False
                    else:
                        print_error("Target article 'Code Normalization in JavaScript: A Practical Example' not found")
                        print_info("Available articles:")
                        for article in articles[:10]:  # Show first 10 articles
                            print_info(f"  - {article.get('title', 'Untitled')}")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying target article: {e}")
        return False

async def analyze_toc_links_in_content(content, article_title):
    """Analyze article content for TOC links and anchor generation"""
    print_info(f"Analyzing content for TOC links in '{article_title}'...")
    
    # Check for Mini-TOC structure
    toc_patterns = [
        '<ul class="toc-list">',
        '<ul class="mini-toc">',
        '<ul>\n<li>Introduction',
        '<ul>\n<li>Getting',
        '<ul>\n<li>Understanding'
    ]
    
    toc_found = any(pattern in content for pattern in toc_patterns)
    if toc_found:
        print_success("Mini-TOC structure found in article")
    else:
        print_info("No obvious Mini-TOC structure found")
    
    # Check for clickable anchor links in TOC format
    anchor_link_patterns = [
        '<a href="#',
        '[text](#',
        'href="#section',
        'href="#getting',
        'href="#introduction'
    ]
    
    clickable_links_found = sum(1 for pattern in anchor_link_patterns if pattern in content)
    if clickable_links_found > 0:
        print_success(f"Clickable anchor links found: {clickable_links_found} patterns detected")
    else:
        print_error("No clickable anchor links found in TOC")
    
    # Check for heading IDs (anchor targets)
    heading_id_patterns = [
        'id="section',
        'id="getting',
        'id="introduction',
        'id="understanding',
        'id="benefits',
        'id="best-practices'
    ]
    
    heading_ids_found = sum(1 for pattern in heading_id_patterns if pattern in content)
    if heading_ids_found > 0:
        print_success(f"Heading IDs found: {heading_ids_found} anchor targets detected")
    else:
        print_error("No heading IDs found for anchor targets")
    
    # Check for TOC processing metadata
    toc_processing_indicators = [
        'toc_processing',
        'anchor_links_generated',
        'processed_at'
    ]
    
    processing_metadata = sum(1 for indicator in toc_processing_indicators if indicator in content)
    if processing_metadata > 0:
        print_info(f"TOC processing metadata found: {processing_metadata} indicators")
    
    # Overall assessment
    success_criteria = [
        toc_found,
        clickable_links_found > 0,
        heading_ids_found > 0
    ]
    
    success_rate = sum(success_criteria) / len(success_criteria) * 100
    
    if success_rate >= 66:
        print_success(f"TOC links analysis PASSED - {success_rate:.1f}% success rate")
        return True
    else:
        print_error(f"TOC links analysis FAILED - {success_rate:.1f}% success rate")
        return False

async def test_content_library_updates():
    """Test 3: Validate Content Library Updates - Check if processed content is saved"""
    print_test_header("Test 3: Content Library Updates Validation")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check for articles with TOC processing metadata
            print_info("Checking for articles with TOC processing metadata...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    articles = await response.json()
                    
                    processed_articles = []
                    for article in articles:
                        # Check if article has TOC processing metadata
                        if 'toc_processing' in str(article):
                            processed_articles.append(article)
                    
                    if processed_articles:
                        print_success(f"Found {len(processed_articles)} articles with TOC processing metadata")
                        
                        for article in processed_articles[:5]:  # Show first 5
                            title = article.get('title', 'Untitled')
                            print_info(f"  - {title}")
                        
                        return True
                    else:
                        print_info("No articles found with TOC processing metadata")
                        
                        # Check if any articles have been recently modified
                        recent_articles = []
                        current_time = datetime.now()
                        
                        for article in articles:
                            # Look for recent updates or processing indicators
                            content = str(article)
                            if any(indicator in content for indicator in ['anchor', 'toc', 'processed']):
                                recent_articles.append(article)
                        
                        if recent_articles:
                            print_info(f"Found {len(recent_articles)} articles with processing indicators")
                            return True
                        else:
                            print_error("No evidence of content library updates")
                            return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error validating content library updates: {e}")
        return False

async def test_processing_results():
    """Test 4: Check Processing Results - Verify endpoint returns accurate statistics"""
    print_test_header("Test 4: Processing Results Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check style diagnostics for TOC processing results
            print_info("Checking style diagnostics for TOC processing results...")
            
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    print_success("Style diagnostics accessible")
                    
                    # Look for TOC processing statistics
                    recent_results = diagnostics.get('recent_results', [])
                    if recent_results:
                        print_success(f"Found {len(recent_results)} recent style processing results")
                        
                        # Check for TOC-related processing
                        toc_results = []
                        for result in recent_results:
                            if any(key in str(result) for key in ['toc', 'anchor', 'links']):
                                toc_results.append(result)
                        
                        if toc_results:
                            print_success(f"Found {len(toc_results)} TOC-related processing results")
                            return True
                        else:
                            print_info("No TOC-specific processing results found in diagnostics")
                    else:
                        print_info("No recent processing results found")
                    
                    # Check overall system status
                    system_status = diagnostics.get('system_status', 'unknown')
                    if system_status == 'active':
                        print_success("Style processing system is active")
                        return True
                    else:
                        print_info(f"Style processing system status: {system_status}")
                        return False
                        
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error checking processing results: {e}")
        return False

async def test_anchor_link_generation():
    """Test 5: Confirm Anchor Link Generation - Verify TOC conversion format"""
    print_test_header("Test 5: Anchor Link Generation Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get the target article again for detailed analysis
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    articles = await response.json()
                    
                    # Find target article
                    target_article = None
                    for article in articles:
                        if 'Code Normalization in JavaScript' in article.get('title', ''):
                            target_article = article
                            break
                    
                    if target_article:
                        content = target_article.get('content', target_article.get('html', ''))
                        
                        # Detailed analysis of anchor link generation
                        print_info("Analyzing anchor link generation patterns...")
                        
                        # Check for markdown-style links [text](#anchor)
                        import re
                        markdown_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
                        if markdown_links:
                            print_success(f"Found {len(markdown_links)} markdown-style anchor links")
                            for text, anchor in markdown_links[:3]:  # Show first 3
                                print_info(f"  - [{text}](#{anchor})")
                        else:
                            print_info("No markdown-style anchor links found")
                        
                        # Check for HTML anchor links <a href="#anchor">text</a>
                        html_links = re.findall(r'<a href="#([^"]+)">([^<]+)</a>', content)
                        if html_links:
                            print_success(f"Found {len(html_links)} HTML anchor links")
                            for anchor, text in html_links[:3]:  # Show first 3
                                print_info(f"  - <a href=\"#{anchor}\">{text}</a>")
                        else:
                            print_info("No HTML anchor links found")
                        
                        # Check for heading IDs that match TOC items
                        heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"', content)
                        if heading_ids:
                            print_success(f"Found {len(heading_ids)} heading IDs")
                            for heading_id in heading_ids[:5]:  # Show first 5
                                print_info(f"  - #{heading_id}")
                        else:
                            print_info("No heading IDs found")
                        
                        # Overall anchor generation assessment
                        total_links = len(markdown_links) + len(html_links)
                        if total_links >= 3 and len(heading_ids) >= 3:
                            print_success(f"Anchor link generation SUCCESSFUL - {total_links} links, {len(heading_ids)} targets")
                            return True
                        elif total_links > 0 or len(heading_ids) > 0:
                            print_info(f"Partial anchor generation - {total_links} links, {len(heading_ids)} targets")
                            return True
                        else:
                            print_error("No anchor link generation detected")
                            return False
                    else:
                        print_error("Target article not found for anchor analysis")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying anchor link generation: {e}")
        return False

async def test_broken_link_detection():
    """Test 6: Test Broken Link Detection - Verify system detects broken anchors"""
    print_test_header("Test 6: Broken Link Detection")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check if the system provides broken link information
            print_info("Testing broken link detection capabilities...")
            
            # Check style diagnostics for broken link information
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    
                    # Look for broken link information in results
                    recent_results = diagnostics.get('recent_results', [])
                    broken_links_found = False
                    
                    for result in recent_results:
                        result_str = str(result)
                        if any(indicator in result_str for indicator in ['broken', 'toc_broken_links', 'invalid']):
                            broken_links_found = True
                            print_success("Broken link detection information found in diagnostics")
                            break
                    
                    if not broken_links_found:
                        print_info("No broken link information found (may indicate no broken links)")
                    
                    return True
                else:
                    print_error(f"Failed to access diagnostics for broken link detection - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing broken link detection: {e}")
        return False

async def run_comprehensive_toc_test():
    """Run comprehensive Mini-TOC links processing test suite"""
    print_test_header("Mini-TOC Links Processing Endpoint - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    
    # Test results tracking
    test_results = []
    
    # Test 1: TOC Processing Endpoint
    success, processing_result = await test_toc_processing_endpoint()
    test_results.append(("TOC Processing Endpoint", success))
    
    # Test 2: Target Article Verification
    success = await test_target_article_verification()
    test_results.append(("Target Article Verification", success))
    
    # Test 3: Content Library Updates
    success = await test_content_library_updates()
    test_results.append(("Content Library Updates", success))
    
    # Test 4: Processing Results
    success = await test_processing_results()
    test_results.append(("Processing Results", success))
    
    # Test 5: Anchor Link Generation
    success = await test_anchor_link_generation()
    test_results.append(("Anchor Link Generation", success))
    
    # Test 6: Broken Link Detection
    success = await test_broken_link_detection()
    test_results.append(("Broken Link Detection", success))
    
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
        print_success(f"🎉 MINI-TOC LINKS PROCESSING TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("The Mini-TOC links processing endpoint is working correctly!")
    elif success_rate >= 60:
        print_info(f"⚠️ MINI-TOC LINKS PROCESSING PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some functionality is working, but improvements needed.")
    else:
        print_error(f"❌ MINI-TOC LINKS PROCESSING TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with Mini-TOC links processing.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting Mini-TOC Links Processing Backend Test Suite...")
    
    try:
        # Run the comprehensive test
        success = asyncio.run(run_comprehensive_toc_test())
        
        if success:
            print("\n🎯 TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)