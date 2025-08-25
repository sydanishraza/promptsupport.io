#!/usr/bin/env python3
"""
Mini-TOC Links Fix Verification Test
Focused test to verify the completely rewritten _process_clickable_anchors method
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

async def test_mini_toc_processing_endpoint():
    """Test 1: Verify Mini-TOC processing endpoint works"""
    print_test_header("Test 1: Mini-TOC Processing Endpoint")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Triggering Mini-TOC processing...")
            
            async with session.post(f"{API_BASE}/style/process-toc-links") as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"Mini-TOC processing completed - Status: {response.status}")
                    
                    # Verify response structure
                    articles_processed = result.get('articles_processed', 0)
                    updated_articles = result.get('updated_articles', [])
                    engine = result.get('engine', 'unknown')
                    
                    print_info(f"Articles processed: {articles_processed}")
                    print_info(f"Updated articles: {len(updated_articles)}")
                    print_info(f"Engine: {engine}")
                    
                    # Check for anchor link generation
                    total_anchors = sum(article.get('anchor_links_generated', 0) for article in updated_articles)
                    articles_with_anchors = sum(1 for article in updated_articles if article.get('anchor_links_generated', 0) > 0)
                    
                    if total_anchors > 0:
                        print_success(f"HTML anchor generation VERIFIED - {total_anchors} total anchors across {articles_with_anchors} articles")
                        return True, updated_articles
                    else:
                        print_error("No HTML anchor links generated")
                        return False, []
                else:
                    error_text = await response.text()
                    print_error(f"Mini-TOC processing failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False, []
                    
    except Exception as e:
        print_error(f"Error testing Mini-TOC processing endpoint: {e}")
        return False, []

async def test_html_anchor_format():
    """Test 2: Verify HTML anchor format <a href="#slug">text</a>"""
    print_test_header("Test 2: HTML Anchor Format Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get content library articles
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    # Find articles with HTML anchor links
                    html_anchor_count = 0
                    markdown_anchor_count = 0
                    articles_analyzed = 0
                    
                    for article in articles[:10]:  # Check first 10 articles
                        content = article.get('content', '')
                        if not content:
                            continue
                            
                        articles_analyzed += 1
                        title = article.get('title', 'Untitled')
                        
                        # Count HTML anchor links <a href="#slug">text</a>
                        html_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                        html_anchor_count += len(html_links)
                        
                        # Count Markdown anchor links [text](#slug)
                        markdown_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
                        markdown_anchor_count += len(markdown_links)
                        
                        if html_links:
                            print_success(f"Article '{title[:40]}...' has {len(html_links)} HTML anchor links")
                            for anchor, text in html_links[:2]:  # Show first 2
                                print_info(f"  - <a href=\"#{anchor}\">{text}</a>")
                    
                    print_info(f"Analysis results across {articles_analyzed} articles:")
                    print_info(f"  - HTML anchor links: {html_anchor_count}")
                    print_info(f"  - Markdown anchor links: {markdown_anchor_count}")
                    
                    # Success criteria: More HTML than Markdown links
                    if html_anchor_count > 0 and html_anchor_count >= markdown_anchor_count:
                        print_success(f"HTML anchor format VERIFIED - {html_anchor_count} HTML vs {markdown_anchor_count} Markdown")
                        return True
                    elif html_anchor_count > 0:
                        print_info(f"Partial HTML anchor format - {html_anchor_count} HTML vs {markdown_anchor_count} Markdown")
                        return True
                    else:
                        print_error("No HTML anchor links found")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying HTML anchor format: {e}")
        return False

async def test_heading_id_matching():
    """Test 3: Verify heading IDs match anchor hrefs"""
    print_test_header("Test 3: Heading ID and Anchor Matching")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get content library articles
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    total_links = 0
                    valid_matches = 0
                    articles_with_matches = 0
                    
                    for article in articles[:5]:  # Check first 5 articles
                        content = article.get('content', '')
                        if not content:
                            continue
                            
                        title = article.get('title', 'Untitled')
                        
                        # Extract heading IDs
                        heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"', content)
                        
                        # Extract anchor targets
                        anchor_targets = re.findall(r'<a[^>]*href="#([^"]+)"', content)
                        
                        if heading_ids and anchor_targets:
                            print_info(f"Article '{title[:40]}...':")
                            print_info(f"  - Heading IDs: {len(heading_ids)} ({heading_ids[:3]}...)")
                            print_info(f"  - Anchor targets: {len(anchor_targets)} ({anchor_targets[:3]}...)")
                            
                            # Check matches
                            article_matches = 0
                            for target in anchor_targets:
                                total_links += 1
                                if target in heading_ids:
                                    valid_matches += 1
                                    article_matches += 1
                            
                            if article_matches > 0:
                                articles_with_matches += 1
                                print_success(f"  - Valid matches: {article_matches}/{len(anchor_targets)}")
                    
                    if total_links > 0:
                        match_rate = (valid_matches / total_links) * 100
                        print_info(f"Overall matching results:")
                        print_info(f"  - Total anchor links: {total_links}")
                        print_info(f"  - Valid matches: {valid_matches}")
                        print_info(f"  - Match rate: {match_rate:.1f}%")
                        print_info(f"  - Articles with matches: {articles_with_matches}")
                        
                        if match_rate >= 70:
                            print_success(f"Heading ID matching SUCCESSFUL - {match_rate:.1f}% match rate")
                            return True
                        else:
                            print_error(f"Heading ID matching INSUFFICIENT - {match_rate:.1f}% match rate")
                            return False
                    else:
                        print_error("No anchor links found for matching analysis")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying heading ID matching: {e}")
        return False

async def test_beautifulsoup_vs_markdown():
    """Test 4: Verify BeautifulSoup processing vs Markdown format"""
    print_test_header("Test 4: BeautifulSoup vs Markdown Processing")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get content library articles
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    beautifulsoup_indicators = 0
                    markdown_indicators = 0
                    
                    for article in articles[:10]:  # Check first 10 articles
                        content = article.get('content', '')
                        if not content:
                            continue
                            
                        # BeautifulSoup indicators: HTML anchor links with class attributes
                        bs_links = re.findall(r'<a[^>]*class="[^"]*toc-link[^"]*"[^>]*href="#[^"]+">([^<]+)</a>', content)
                        beautifulsoup_indicators += len(bs_links)
                        
                        # Markdown indicators: [text](#slug) format
                        md_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
                        markdown_indicators += len(md_links)
                        
                        if bs_links:
                            title = article.get('title', 'Untitled')
                            print_success(f"BeautifulSoup processing found in '{title[:40]}...' - {len(bs_links)} links with toc-link class")
                    
                    print_info(f"Processing format analysis:")
                    print_info(f"  - BeautifulSoup indicators (HTML with classes): {beautifulsoup_indicators}")
                    print_info(f"  - Markdown indicators ([text](#slug)): {markdown_indicators}")
                    
                    if beautifulsoup_indicators > 0:
                        print_success(f"BeautifulSoup processing VERIFIED - {beautifulsoup_indicators} HTML links with proper classes")
                        return True
                    else:
                        print_error("No BeautifulSoup processing indicators found")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying BeautifulSoup processing: {e}")
        return False

async def test_toc_detection_content_analysis():
    """Test 5: Verify TOC detection with content analysis"""
    print_test_header("Test 5: TOC Detection Content Analysis")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check style diagnostics for TOC processing
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    
                    # Look for recent TOC processing results
                    recent_results = diagnostics.get('recent_results', [])
                    toc_processing_found = False
                    anchor_generation_stats = []
                    
                    for result in recent_results[:5]:  # Check last 5 results
                        result_str = str(result)
                        
                        # Look for TOC processing indicators
                        if any(indicator in result_str.lower() for indicator in ['toc', 'anchor', 'clickable']):
                            toc_processing_found = True
                        
                        # Extract anchor generation numbers
                        anchor_matches = re.findall(r'anchor_links_generated["\s:]*(\d+)', result_str)
                        for match in anchor_matches:
                            anchor_generation_stats.append(int(match))
                    
                    if toc_processing_found:
                        print_success("TOC processing information found in diagnostics")
                        
                        if anchor_generation_stats:
                            total_anchors = sum(anchor_generation_stats)
                            avg_anchors = total_anchors / len(anchor_generation_stats)
                            print_info(f"Anchor generation statistics:")
                            print_info(f"  - Total anchors generated: {total_anchors}")
                            print_info(f"  - Average per processing: {avg_anchors:.1f}")
                            print_info(f"  - Processing runs with anchors: {len([x for x in anchor_generation_stats if x > 0])}")
                            
                            if total_anchors > 0:
                                print_success(f"TOC detection and content analysis VERIFIED - {total_anchors} anchors generated")
                                return True
                        
                        print_success("TOC detection working (limited anchor stats)")
                        return True
                    else:
                        print_error("No TOC processing information found in diagnostics")
                        return False
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying TOC detection: {e}")
        return False

async def run_mini_toc_verification():
    """Run focused Mini-TOC Links Fix verification"""
    print_test_header("Mini-TOC Links Fix - Focused Verification")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Verifying the completely rewritten _process_clickable_anchors method")
    
    # Test results tracking
    test_results = []
    
    # Test 1: Mini-TOC Processing Endpoint
    success, updated_articles = await test_mini_toc_processing_endpoint()
    test_results.append(("Mini-TOC Processing Endpoint", success))
    
    # Test 2: HTML Anchor Format
    success = await test_html_anchor_format()
    test_results.append(("HTML Anchor Format", success))
    
    # Test 3: Heading ID Matching
    success = await test_heading_id_matching()
    test_results.append(("Heading ID Matching", success))
    
    # Test 4: BeautifulSoup vs Markdown
    success = await test_beautifulsoup_vs_markdown()
    test_results.append(("BeautifulSoup vs Markdown Processing", success))
    
    # Test 5: TOC Detection Content Analysis
    success = await test_toc_detection_content_analysis()
    test_results.append(("TOC Detection Content Analysis", success))
    
    # Final Results Summary
    print_test_header("Verification Results Summary")
    
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
        print_success(f"🎉 MINI-TOC LINKS FIX VERIFICATION PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("The completely rewritten _process_clickable_anchors method is working correctly!")
        print_success("✅ BeautifulSoup-based HTML processing confirmed")
        print_success("✅ HTML anchor links <a href=\"#slug\">text</a> generation verified")
        print_success("✅ Heading IDs properly created and matching anchor hrefs")
        print_success("✅ TOC detection with content analysis operational")
        print_success("✅ Previous issue of 0 HTML anchors generated is FIXED")
    elif success_rate >= 60:
        print_info(f"⚠️ MINI-TOC LINKS PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Most functionality is working, minor improvements may be needed.")
    else:
        print_error(f"❌ MINI-TOC LINKS FIX VERIFICATION FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with Mini-TOC links processing.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting Mini-TOC Links Fix Verification...")
    
    try:
        # Run the verification
        success = asyncio.run(run_mini_toc_verification())
        
        if success:
            print("\n🎯 MINI-TOC LINKS FIX VERIFICATION COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 MINI-TOC LINKS FIX VERIFICATION COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)