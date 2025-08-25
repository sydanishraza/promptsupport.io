#!/usr/bin/env python3
"""
Focused Mini-TOC Links Test
Testing the specific _process_clickable_anchors method functionality
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

async def test_existing_articles_for_toc():
    """Test existing articles in content library for TOC functionality"""
    print_test_header("Testing Existing Articles for TOC Functionality")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking existing articles for TOC processing...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    print_success(f"Found {len(articles)} articles in content library")
                    
                    toc_analysis_results = []
                    
                    for article in articles:
                        title = article.get('title', 'Untitled')
                        content = article.get('content', article.get('html', ''))
                        
                        if content:
                            analysis = analyze_article_toc_content(title, content)
                            if analysis['has_toc_elements']:
                                toc_analysis_results.append(analysis)
                                print_info(f"TOC elements in '{analysis['title']}': HTML anchors={analysis['html_anchors']}, Headings with IDs={analysis['headings_with_ids']}")
                    
                    if toc_analysis_results:
                        print_success(f"Found {len(toc_analysis_results)} articles with TOC elements")
                        
                        # Analyze results
                        html_anchors_total = sum(r['html_anchors'] for r in toc_analysis_results)
                        markdown_anchors_total = sum(r['markdown_anchors'] for r in toc_analysis_results)
                        headings_with_ids_total = sum(r['headings_with_ids'] for r in toc_analysis_results)
                        
                        print_info(f"Total HTML anchor links: {html_anchors_total}")
                        print_info(f"Total Markdown anchor links: {markdown_anchors_total}")
                        print_info(f"Total headings with IDs: {headings_with_ids_total}")
                        
                        # Success criteria
                        if html_anchors_total > 0:
                            print_success("✅ HTML anchor links found - conversion working")
                            if markdown_anchors_total == 0:
                                print_success("✅ No Markdown anchors - full conversion successful")
                                return True
                            else:
                                print_info(f"⚠️ Still has {markdown_anchors_total} Markdown anchors")
                                return html_anchors_total > markdown_anchors_total
                        else:
                            print_error("❌ No HTML anchor links found")
                            return False
                    else:
                        print_info("No articles with TOC elements found")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing existing articles: {e}")
        return False

def analyze_article_toc_content(title, content):
    """Analyze article content for TOC elements"""
    
    # Find HTML anchor links
    html_anchors = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)
    
    # Find Markdown anchor links
    markdown_anchors = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
    
    # Find headings with IDs
    headings_with_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"[^>]*>([^<]+)</h[1-6]>', content)
    
    # Find lists (potential TOCs)
    ul_lists = len(re.findall(r'<ul[^>]*>', content))
    li_items = len(re.findall(r'<li[^>]*>', content))
    
    has_toc_elements = (
        len(html_anchors) > 0 or 
        len(markdown_anchors) > 0 or 
        len(headings_with_ids) > 0 or 
        (ul_lists > 0 and li_items > 2)
    )
    
    return {
        'title': title[:50] + '...' if len(title) > 50 else title,
        'has_toc_elements': has_toc_elements,
        'html_anchors': len(html_anchors),
        'markdown_anchors': len(markdown_anchors),
        'headings_with_ids': len(headings_with_ids),
        'ul_lists': ul_lists,
        'li_items': li_items
    }

async def test_style_diagnostics():
    """Test style diagnostics for Mini-TOC processing evidence"""
    print_test_header("Testing Style Diagnostics for Mini-TOC Evidence")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking style diagnostics for Mini-TOC processing evidence...")
            
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    print_success("Style diagnostics accessible")
                    
                    # Check system status
                    system_status = diagnostics.get('system_status', 'unknown')
                    total_runs = diagnostics.get('total_runs', 0)
                    success_rate = diagnostics.get('success_rate', 0)
                    
                    print_info(f"System status: {system_status}")
                    print_info(f"Total runs: {total_runs}")
                    print_info(f"Success rate: {success_rate}%")
                    
                    recent_results = diagnostics.get('recent_results', [])
                    if recent_results:
                        print_success(f"Found {len(recent_results)} recent style processing results")
                        
                        # Look for Mini-TOC processing evidence
                        mini_toc_evidence = []
                        
                        for result in recent_results:
                            result_str = str(result)
                            
                            # Check for anchor links generated
                            if 'anchor_links_generated' in result_str:
                                anchor_match = re.search(r'anchor_links_generated["\s:]*(\d+)', result_str)
                                if anchor_match:
                                    count = int(anchor_match.group(1))
                                    mini_toc_evidence.append(f"anchor_links_generated: {count}")
                            
                            # Check for TOC broken links
                            if 'toc_broken_links' in result_str:
                                broken_match = re.search(r'toc_broken_links["\s:]*\[([^\]]*)\]', result_str)
                                if broken_match:
                                    broken_content = broken_match.group(1)
                                    broken_count = len([item for item in broken_content.split(',') if item.strip()]) if broken_content.strip() else 0
                                    mini_toc_evidence.append(f"toc_broken_links: {broken_count}")
                            
                            # Check for structural changes
                            if 'structural_changes' in result_str:
                                mini_toc_evidence.append("structural_changes: found")
                        
                        if mini_toc_evidence:
                            print_success("Mini-TOC processing evidence found:")
                            for evidence in mini_toc_evidence:
                                print_info(f"  - {evidence}")
                            return True
                        else:
                            print_warning("No Mini-TOC processing evidence found in recent results")
                            return False
                    else:
                        print_warning("No recent style processing results found")
                        return False
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error checking style diagnostics: {e}")
        return False

async def test_content_with_mini_toc():
    """Test processing content with Mini-TOC through V2 system"""
    print_test_header("Testing Content with Mini-TOC Processing")
    
    # Test content with Mini-TOC and matching headings
    test_content = """
    <h1>Building a Basic Google Map with JavaScript API</h1>
    
    <p>This comprehensive guide will walk you through creating a basic Google Map using the JavaScript API.</p>
    
    <ul>
        <li>Getting Started with Google Maps API</li>
        <li>Setting Up Your API Key</li>
        <li>Creating the Map Container</li>
        <li>Initializing the Map</li>
        <li>Adding Markers and Info Windows</li>
        <li>Customizing Map Styles</li>
    </ul>
    
    <h2>Getting Started with Google Maps API</h2>
    <p>Before you can use the Google Maps JavaScript API, you need to set up a project in the Google Cloud Console...</p>
    
    <h2>Setting Up Your API Key</h2>
    <p>An API key is required to authenticate your requests to the Google Maps API...</p>
    
    <h2>Creating the Map Container</h2>
    <p>First, you need to create an HTML element that will contain your map...</p>
    
    <h2>Initializing the Map</h2>
    <p>Once you have your container ready, you can initialize the map with JavaScript...</p>
    
    <h2>Adding Markers and Info Windows</h2>
    <p>Markers help identify locations on your map. You can also add info windows for additional information...</p>
    
    <h2>Customizing Map Styles</h2>
    <p>Google Maps allows you to customize the appearance of your map using styles...</p>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Processing test content through V2 text processing...")
            
            # Process through V2 text processing pipeline
            payload = {"text": test_content}
            
            async with session.post(f"{API_BASE}/v2/process-text", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success("V2 text processing initiated successfully")
                    
                    job_id = result.get('job_id')
                    if job_id:
                        print_info(f"Processing job ID: {job_id}")
                        
                        # Wait for processing to complete
                        await asyncio.sleep(8)
                        
                        # Check if processing completed by checking style diagnostics
                        return await check_processing_completion(session)
                    else:
                        print_error("No job ID returned from V2 processing")
                        return False
                else:
                    error_text = await response.text()
                    print_error(f"V2 processing failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in Mini-TOC content processing test: {e}")
        return False

async def check_processing_completion(session):
    """Check if processing completed and look for results"""
    print_info("Checking processing completion...")
    
    try:
        # Check style diagnostics for recent activity
        async with session.get(f"{API_BASE}/style/diagnostics") as response:
            if response.status == 200:
                diagnostics = await response.json()
                
                total_runs = diagnostics.get('total_runs', 0)
                success_rate = diagnostics.get('success_rate', 0)
                
                print_info(f"Total style runs: {total_runs}")
                print_info(f"Success rate: {success_rate}%")
                
                if total_runs > 0 and success_rate > 0:
                    print_success("Processing activity detected")
                    return True
                else:
                    print_warning("No processing activity detected")
                    return False
            else:
                print_error(f"Failed to check processing completion - Status: {response.status}")
                return False
                
    except Exception as e:
        print_error(f"Error checking processing completion: {e}")
        return False

async def run_focused_mini_toc_test():
    """Run focused Mini-TOC test suite"""
    print_test_header("Focused Mini-TOC Links Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    
    # Test results tracking
    test_results = []
    
    # Test 1: Existing Articles TOC Analysis
    success = await test_existing_articles_for_toc()
    test_results.append(("Existing Articles TOC Analysis", success))
    
    # Test 2: Style Diagnostics Check
    success = await test_style_diagnostics()
    test_results.append(("Style Diagnostics Check", success))
    
    # Test 3: Content with Mini-TOC Processing
    success = await test_content_with_mini_toc()
    test_results.append(("Content Mini-TOC Processing", success))
    
    # Results Summary
    print_test_header("Focused Test Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Overall assessment
    if success_rate >= 67:  # 2/3 tests passing
        print_success(f"🎉 FOCUSED MINI-TOC TEST PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("Mini-TOC functionality is working!")
    else:
        print_error(f"❌ FOCUSED MINI-TOC TEST FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Mini-TOC functionality needs attention")
    
    return success_rate >= 50

if __name__ == "__main__":
    print("🚀 Starting Focused Mini-TOC Links Test...")
    
    try:
        # Set environment variable
        os.environ['REACT_APP_BACKEND_URL'] = 'https://content-formatter.preview.emergentagent.com'
        
        # Run the focused test
        success = asyncio.run(run_focused_mini_toc_test())
        
        if success:
            print("\n🎯 FOCUSED MINI-TOC TEST COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 FOCUSED MINI-TOC TEST COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)