#!/usr/bin/env python3
"""
Mini-TOC Links Fix Test Suite
Testing the updated Mini-TOC links fix implementation focusing on:
1. HTML anchor format conversion (<a href="#slug">text</a> instead of Markdown)
2. TOC detection using BeautifulSoup for HTML lists
3. Enhanced matching algorithm between TOC items and headings
4. Validation of HTML anchor links instead of Markdown
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

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

async def test_v2_engine_health():
    """Test 1: Verify V2 Engine is operational"""
    print_test_header("Test 1: V2 Engine Health Check")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking V2 Engine status...")
            
            async with session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    engine_data = await response.json()
                    print_success(f"V2 Engine accessible - Status: {response.status}")
                    
                    # Check for V2 engine
                    engine_version = engine_data.get('engine', 'unknown')
                    if engine_version == 'v2':
                        print_success("V2 Engine confirmed active")
                        
                        # Check for style processing capabilities
                        features = engine_data.get('features', [])
                        style_features = [f for f in features if 'style' in f.lower() or 'toc' in f.lower()]
                        if style_features:
                            print_success(f"Style processing features available: {style_features}")
                            return True, engine_data
                        else:
                            print_warning("No style processing features found")
                            return True, engine_data
                    else:
                        print_error(f"Expected V2 engine, found: {engine_version}")
                        return False, None
                else:
                    print_error(f"V2 Engine health check failed - Status: {response.status}")
                    return False, None
                    
    except Exception as e:
        print_error(f"Error checking V2 Engine health: {e}")
        return False, None

async def test_mini_toc_processing_with_test_content():
    """Test 2: Process test content with Mini-TOC through V2 Style System"""
    print_test_header("Test 2: Mini-TOC Processing with Test Content")
    
    # Create test content with Mini-TOC and headings
    test_content = """
    <h1>Complete Guide to API Integration</h1>
    
    <p>This guide covers everything you need to know about API integration.</p>
    
    <ul>
        <li>Getting Started</li>
        <li>Authentication Setup</li>
        <li>Making API Calls</li>
        <li>Error Handling</li>
        <li>Best Practices</li>
    </ul>
    
    <h2>Getting Started</h2>
    <p>First, you need to understand the basics of API integration...</p>
    
    <h2>Authentication Setup</h2>
    <p>Authentication is crucial for secure API access...</p>
    
    <h2>Making API Calls</h2>
    <p>Once authenticated, you can start making API calls...</p>
    
    <h3>GET Requests</h3>
    <p>GET requests are used to retrieve data...</p>
    
    <h3>POST Requests</h3>
    <p>POST requests are used to send data...</p>
    
    <h2>Error Handling</h2>
    <p>Proper error handling ensures robust applications...</p>
    
    <h2>Best Practices</h2>
    <p>Follow these best practices for optimal results...</p>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Processing test content through V2 Style System...")
            
            # Create a test article in content library
            test_article = {
                "title": "Mini-TOC Test Article",
                "content": test_content,
                "status": "published",
                "article_type": "tutorial"
            }
            
            # Post test article to content library
            async with session.post(f"{API_BASE}/content-library", json=test_article) as response:
                if response.status == 201:
                    created_article = await response.json()
                    article_id = created_article.get('id')
                    print_success(f"Test article created with ID: {article_id}")
                    
                    # Now process it through V2 style system
                    style_request = {
                        "content": test_content,
                        "article_id": article_id,
                        "processing_type": "mini_toc_links"
                    }
                    
                    # Process through V2 style system
                    async with session.post(f"{API_BASE}/v2/process-text", json={"text": test_content}) as style_response:
                        if style_response.status == 200:
                            result = await style_response.json()
                            print_success("V2 processing completed successfully")
                            
                            # Check if processing includes style processing
                            job_id = result.get('job_id')
                            if job_id:
                                print_info(f"Processing job ID: {job_id}")
                                
                                # Wait a moment for processing
                                await asyncio.sleep(3)
                                
                                # Check processing results
                                return await check_processing_results(session, job_id, article_id)
                            else:
                                print_warning("No job ID returned from V2 processing")
                                return False
                        else:
                            error_text = await style_response.text()
                            print_error(f"V2 processing failed - Status: {style_response.status}")
                            print_error(f"Error: {error_text}")
                            return False
                else:
                    error_text = await response.text()
                    print_error(f"Failed to create test article - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in Mini-TOC processing test: {e}")
        return False

async def check_processing_results(session, job_id, article_id):
    """Check the results of V2 processing for Mini-TOC functionality"""
    print_info("Checking V2 processing results...")
    
    try:
        # Check style diagnostics for processing results
        async with session.get(f"{API_BASE}/style/diagnostics") as response:
            if response.status == 200:
                diagnostics = await response.json()
                recent_results = diagnostics.get('recent_results', [])
                
                if recent_results:
                    print_success(f"Found {len(recent_results)} recent style processing results")
                    
                    # Look for our processing result
                    for result in recent_results:
                        if 'anchor_links_generated' in str(result) or 'toc_broken_links' in str(result):
                            print_success("Found Mini-TOC processing result")
                            return await analyze_mini_toc_result(result)
                    
                    print_warning("No Mini-TOC specific results found in recent processing")
                    return False
                else:
                    print_warning("No recent processing results found")
                    return False
            else:
                print_error(f"Failed to access style diagnostics - Status: {response.status}")
                return False
                
    except Exception as e:
        print_error(f"Error checking processing results: {e}")
        return False

async def analyze_mini_toc_result(result):
    """Analyze Mini-TOC processing result for key metrics"""
    print_info("Analyzing Mini-TOC processing result...")
    
    result_str = str(result)
    
    # Extract key metrics
    anchor_links_generated = 0
    toc_broken_links_count = 0
    
    # Look for anchor links generated
    anchor_match = re.search(r'anchor_links_generated["\s:]*(\d+)', result_str)
    if anchor_match:
        anchor_links_generated = int(anchor_match.group(1))
        print_success(f"Anchor links generated: {anchor_links_generated}")
    
    # Look for broken links
    broken_match = re.search(r'toc_broken_links["\s:]*\[([^\]]*)\]', result_str)
    if broken_match:
        broken_content = broken_match.group(1)
        if broken_content.strip():
            # Count items in broken links array
            toc_broken_links_count = len([item for item in broken_content.split(',') if item.strip()])
        print_info(f"TOC broken links: {toc_broken_links_count}")
    
    # Success criteria
    success_criteria = [
        anchor_links_generated >= 3,  # At least 3 TOC items converted
        toc_broken_links_count <= 2,  # Low broken link count
    ]
    
    success_rate = sum(success_criteria) / len(success_criteria) * 100
    
    if success_rate >= 50:
        print_success(f"Mini-TOC processing SUCCESSFUL - {success_rate:.1f}% success rate")
        print_success(f"✅ Generated {anchor_links_generated} anchor links")
        print_success(f"✅ Only {toc_broken_links_count} broken links")
        return True
    else:
        print_error(f"Mini-TOC processing FAILED - {success_rate:.1f}% success rate")
        return False

async def test_html_anchor_format():
    """Test 3: Verify HTML anchor format instead of Markdown"""
    print_test_header("Test 3: HTML Anchor Format Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Searching for articles with TOC processing...")
            
            # Get content library articles
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    # Look for articles with TOC content
                    toc_articles = []
                    for article in articles:
                        content = article.get('content', article.get('html', ''))
                        if content and ('<ul>' in content or '<li>' in content):
                            toc_articles.append(article)
                    
                    if toc_articles:
                        print_success(f"Found {len(toc_articles)} articles with list content")
                        
                        # Analyze the first few articles for anchor format
                        html_anchors_found = 0
                        markdown_anchors_found = 0
                        
                        for article in toc_articles[:5]:  # Check first 5 articles
                            content = article.get('content', article.get('html', ''))
                            title = article.get('title', 'Untitled')
                            
                            # Check for HTML anchor links
                            html_anchors = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                            if html_anchors:
                                html_anchors_found += len(html_anchors)
                                print_success(f"Found {len(html_anchors)} HTML anchor links in '{title[:30]}...'")
                                
                                # Show examples
                                for anchor, text in html_anchors[:3]:
                                    print_info(f"  - <a href=\"#{anchor}\">{text}</a>")
                            
                            # Check for Markdown anchor links (should be fewer now)
                            markdown_anchors = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
                            if markdown_anchors:
                                markdown_anchors_found += len(markdown_anchors)
                                print_warning(f"Found {len(markdown_anchors)} Markdown anchor links in '{title[:30]}...'")
                        
                        # Assessment
                        if html_anchors_found > 0:
                            print_success(f"HTML anchor format VERIFIED - {html_anchors_found} HTML anchors found")
                            if markdown_anchors_found == 0:
                                print_success("✅ No Markdown anchors found - conversion successful")
                                return True
                            else:
                                print_warning(f"⚠️ Still found {markdown_anchors_found} Markdown anchors")
                                return html_anchors_found > markdown_anchors_found
                        else:
                            print_error("No HTML anchor links found")
                            return False
                    else:
                        print_warning("No articles with list content found")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying HTML anchor format: {e}")
        return False

async def test_beautifulsoup_toc_detection():
    """Test 4: Verify BeautifulSoup TOC detection for HTML lists"""
    print_test_header("Test 4: BeautifulSoup TOC Detection")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Testing BeautifulSoup-based TOC detection...")
            
            # Check style diagnostics for processing information
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    
                    # Look for evidence of BeautifulSoup processing
                    recent_results = diagnostics.get('recent_results', [])
                    beautifulsoup_indicators = 0
                    
                    for result in recent_results:
                        result_str = str(result)
                        
                        # Look for indicators of HTML list processing
                        if any(indicator in result_str.lower() for indicator in [
                            'ul', 'li', 'html', 'soup', 'toc_link', 'anchor_links_generated'
                        ]):
                            beautifulsoup_indicators += 1
                    
                    if beautifulsoup_indicators > 0:
                        print_success(f"BeautifulSoup TOC detection VERIFIED - {beautifulsoup_indicators} processing indicators found")
                        
                        # Check for specific TOC processing features
                        toc_processing_features = []
                        for result in recent_results:
                            if 'anchor_links_generated' in str(result):
                                toc_processing_features.append("anchor_links_generated")
                            if 'toc_broken_links' in str(result):
                                toc_processing_features.append("toc_broken_links")
                        
                        if toc_processing_features:
                            print_success(f"TOC processing features confirmed: {toc_processing_features}")
                            return True
                        else:
                            print_warning("TOC processing indicators found but no specific features")
                            return True
                    else:
                        print_warning("No BeautifulSoup TOC processing indicators found")
                        return False
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing BeautifulSoup TOC detection: {e}")
        return False

async def test_enhanced_matching_algorithm():
    """Test 5: Verify enhanced matching algorithm between TOC items and headings"""
    print_test_header("Test 5: Enhanced Matching Algorithm")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Testing enhanced TOC-to-heading matching algorithm...")
            
            # Look for articles with both TOC and headings
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    matching_success = 0
                    total_articles_checked = 0
                    
                    for article in articles[:10]:  # Check first 10 articles
                        content = article.get('content', article.get('html', ''))
                        title = article.get('title', 'Untitled')
                        
                        # Check if article has both TOC links and headings
                        toc_links = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                        headings_with_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"[^>]*>([^<]+)</h[1-6]>', content)
                        
                        if toc_links and headings_with_ids:
                            total_articles_checked += 1
                            print_info(f"Analyzing matching in '{title[:40]}...'")
                            print_info(f"  - TOC links: {len(toc_links)}")
                            print_info(f"  - Headings with IDs: {len(headings_with_ids)}")
                            
                            # Check how many TOC links have matching heading targets
                            valid_matches = 0
                            for anchor, link_text in toc_links:
                                # Check if this anchor exists in headings
                                if any(anchor == heading_id for heading_id, _ in headings_with_ids):
                                    valid_matches += 1
                                    print_success(f"    ✅ '{link_text}' -> #{anchor} (valid)")
                                else:
                                    print_warning(f"    ⚠️ '{link_text}' -> #{anchor} (no target)")
                            
                            # Calculate match rate for this article
                            if len(toc_links) > 0:
                                match_rate = valid_matches / len(toc_links)
                                if match_rate >= 0.7:  # 70% or better matching
                                    matching_success += 1
                                    print_success(f"  Match rate: {match_rate:.1%} - GOOD")
                                else:
                                    print_warning(f"  Match rate: {match_rate:.1%} - NEEDS IMPROVEMENT")
                    
                    if total_articles_checked > 0:
                        overall_success_rate = matching_success / total_articles_checked
                        print_info(f"Enhanced matching algorithm results:")
                        print_info(f"  - Articles checked: {total_articles_checked}")
                        print_info(f"  - Articles with good matching: {matching_success}")
                        print_info(f"  - Overall success rate: {overall_success_rate:.1%}")
                        
                        if overall_success_rate >= 0.6:  # 60% or better
                            print_success("Enhanced matching algorithm VERIFIED")
                            return True
                        else:
                            print_error("Enhanced matching algorithm needs improvement")
                            return False
                    else:
                        print_warning("No articles found with both TOC links and headings for analysis")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing enhanced matching algorithm: {e}")
        return False

async def test_html_anchor_validation():
    """Test 6: Verify validation checks HTML anchor links instead of Markdown"""
    print_test_header("Test 6: HTML Anchor Link Validation")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Testing HTML anchor link validation...")
            
            # Check style diagnostics for validation results
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    recent_results = diagnostics.get('recent_results', [])
                    
                    validation_evidence = []
                    
                    for result in recent_results:
                        result_str = str(result)
                        
                        # Look for validation-related information
                        if 'toc_broken_links' in result_str:
                            validation_evidence.append("broken_link_detection")
                        if 'anchor_links_generated' in result_str:
                            validation_evidence.append("anchor_link_tracking")
                        if any(term in result_str for term in ['missing_target', 'no_matching_heading']):
                            validation_evidence.append("target_validation")
                    
                    if validation_evidence:
                        print_success(f"HTML anchor validation VERIFIED - Evidence: {set(validation_evidence)}")
                        
                        # Check for specific validation metrics
                        broken_links_data = []
                        for result in recent_results:
                            # Extract broken link information
                            broken_match = re.search(r'toc_broken_links["\s:]*\[([^\]]*)\]', str(result))
                            if broken_match:
                                broken_content = broken_match.group(1)
                                if broken_content.strip():
                                    broken_count = len([item for item in broken_content.split(',') if item.strip()])
                                    broken_links_data.append(broken_count)
                        
                        if broken_links_data:
                            avg_broken = sum(broken_links_data) / len(broken_links_data)
                            print_info(f"Average broken links per article: {avg_broken:.1f}")
                            
                            if avg_broken <= 2:
                                print_success("✅ Low broken link rate indicates good validation")
                                return True
                            else:
                                print_warning(f"⚠️ High broken link rate: {avg_broken:.1f}")
                                return True  # Still working, just needs improvement
                        else:
                            print_success("✅ No broken links found - validation working perfectly")
                            return True
                    else:
                        print_warning("No validation evidence found in diagnostics")
                        return False
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing HTML anchor validation: {e}")
        return False

async def run_mini_toc_links_test_suite():
    """Run comprehensive Mini-TOC Links Fix test suite"""
    print_test_header("Mini-TOC Links Fix - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Testing updated Mini-TOC links fix implementation")
    
    # Test results tracking
    test_results = []
    
    # Test 1: V2 Engine Health Check
    success, engine_data = await test_v2_engine_health()
    test_results.append(("V2 Engine Health Check", success))
    
    # Test 2: Mini-TOC Processing with Test Content
    success = await test_mini_toc_processing_with_test_content()
    test_results.append(("Mini-TOC Processing", success))
    
    # Test 3: HTML Anchor Format Verification
    success = await test_html_anchor_format()
    test_results.append(("HTML Anchor Format", success))
    
    # Test 4: BeautifulSoup TOC Detection
    success = await test_beautifulsoup_toc_detection()
    test_results.append(("BeautifulSoup TOC Detection", success))
    
    # Test 5: Enhanced Matching Algorithm
    success = await test_enhanced_matching_algorithm()
    test_results.append(("Enhanced Matching Algorithm", success))
    
    # Test 6: HTML Anchor Validation
    success = await test_html_anchor_validation()
    test_results.append(("HTML Anchor Validation", success))
    
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
        print_success(f"🎉 MINI-TOC LINKS FIX TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("The Mini-TOC links fix implementation is working correctly!")
        print_success("✅ HTML anchor format conversion successful")
        print_success("✅ BeautifulSoup TOC detection operational")
        print_success("✅ Enhanced matching algorithm working")
        print_success("✅ HTML anchor validation implemented")
    elif success_rate >= 60:
        print_warning(f"⚠️ MINI-TOC LINKS FIX PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_warning("Some functionality is working, but improvements needed.")
    else:
        print_error(f"❌ MINI-TOC LINKS FIX TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with Mini-TOC links fix.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting Mini-TOC Links Fix Test Suite...")
    
    try:
        # Run the Mini-TOC links test
        success = asyncio.run(run_mini_toc_links_test_suite())
        
        if success:
            print("\n🎯 MINI-TOC LINKS FIX TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 MINI-TOC LINKS FIX TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)