#!/usr/bin/env python3
"""
ID Coordination Fix Test Suite for Mini-TOC Links
Testing the enhanced _process_clickable_anchors method with 3-step ID matching process

FOCUS: Verify that TOC links use existing heading IDs instead of generating new ones
- Step 1: Prioritize existing heading IDs (section1, section2, etc.)
- Step 2: Use generated heading IDs from processing
- Step 3: Create appropriate IDs maintaining consistency
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

async def test_existing_heading_ids_priority():
    """Test 1: Verify TOC links prioritize existing heading IDs (section1, section2)"""
    print_test_header("Test 1: Existing Heading IDs Priority")
    
    # Test content with existing section-style IDs
    test_content = """
    <h1>API Integration Guide</h1>
    
    <p>This comprehensive guide covers API integration from start to finish.</p>
    
    <ul>
        <li>Introduction to APIs</li>
        <li>Authentication Setup</li>
        <li>Making Requests</li>
        <li>Error Handling</li>
    </ul>
    
    <h2 id="section1">Introduction to APIs</h2>
    <p>APIs are the foundation of modern web applications...</p>
    
    <h2 id="section2">Authentication Setup</h2>
    <p>Proper authentication is crucial for API security...</p>
    
    <h2 id="section3">Making Requests</h2>
    <p>Learn how to make your first API request...</p>
    
    <h2 id="section4">Error Handling</h2>
    <p>Handle errors gracefully in your applications...</p>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Processing content with existing section-style IDs...")
            
            payload = {
                "content": test_content,
                "source_type": "html",
                "processing_options": {
                    "enable_style_processing": True,
                    "enable_anchor_processing": True
                }
            }
            
            async with session.post(f"{API_BASE}/v2/process-content", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success("Content processing completed")
                    
                    # Get the processed content from content library
                    job_id = result.get('job_id')
                    if job_id:
                        # Wait a moment for processing to complete
                        await asyncio.sleep(2)
                        
                        # Get articles from content library
                        async with session.get(f"{API_BASE}/content-library") as lib_response:
                            if lib_response.status == 200:
                                lib_data = await lib_response.json()
                                articles = lib_data.get('articles', []) if isinstance(lib_data, dict) else lib_data
                                
                                # Find the most recent article
                                if articles:
                                    latest_article = max(articles, key=lambda x: x.get('created_at', ''))
                                    content = latest_article.get('content', latest_article.get('html', ''))
                                    
                                    print_info(f"Analyzing processed content from article: {latest_article.get('title', 'Untitled')}")
                                    
                                    # Check if TOC links use existing section IDs
                                    toc_links = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                                    existing_section_ids = re.findall(r'id="(section\d+)"', content)
                                    
                                    print_info(f"Found {len(toc_links)} TOC links")
                                    print_info(f"Found {len(existing_section_ids)} section-style IDs: {existing_section_ids}")
                                    
                                    # Verify TOC links use existing section IDs
                                    section_id_matches = 0
                                    for link_target, link_text in toc_links:
                                        if link_target in existing_section_ids:
                                            section_id_matches += 1
                                            print_success(f"TOC link '{link_text}' correctly uses existing ID: #{link_target}")
                                        else:
                                            print_error(f"TOC link '{link_text}' uses new ID: #{link_target} (should use existing section ID)")
                                    
                                    if len(toc_links) > 0:
                                        match_rate = (section_id_matches / len(toc_links)) * 100
                                        print_info(f"Existing ID usage rate: {section_id_matches}/{len(toc_links)} ({match_rate:.1f}%)")
                                        
                                        if match_rate >= 75:
                                            print_success(f"EXCELLENT: TOC links prioritize existing section IDs ({match_rate:.1f}%)")
                                            return True
                                        elif match_rate >= 50:
                                            print_info(f"GOOD: Most TOC links use existing IDs ({match_rate:.1f}%)")
                                            return True
                                        else:
                                            print_error(f"POOR: TOC links not using existing IDs ({match_rate:.1f}%)")
                                            return False
                                    else:
                                        print_error("No TOC links found in processed content")
                                        return False
                                else:
                                    print_error("No articles found in content library")
                                    return False
                            else:
                                print_error(f"Failed to access content library - Status: {lib_response.status}")
                                return False
                    else:
                        print_error("No job ID returned from processing")
                        return False
                else:
                    error_text = await response.text()
                    print_error(f"Content processing failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing existing heading IDs priority: {e}")
        return False

async def test_flexible_text_matching():
    """Test 2: Verify enhanced flexible text matching between TOC items and headings"""
    print_test_header("Test 2: Flexible Text Matching")
    
    # Test content with variations in TOC vs heading text
    test_content = """
    <h1>Complete Development Guide</h1>
    
    <ul>
        <li>Getting Started</li>
        <li>API Authentication</li>
        <li>Making Your First Request</li>
        <li>Best Practices</li>
    </ul>
    
    <h2>Getting Started with Development</h2>
    <p>Start your development journey here...</p>
    
    <h2>Authentication and API Keys</h2>
    <p>Learn about API authentication...</p>
    
    <h2>Making Your First API Request</h2>
    <p>Step-by-step guide to your first request...</p>
    
    <h2>Development Best Practices</h2>
    <p>Follow these best practices...</p>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Testing flexible text matching between TOC and headings...")
            
            payload = {
                "content": test_content,
                "source_type": "html",
                "processing_options": {
                    "enable_style_processing": True
                }
            }
            
            async with session.post(f"{API_BASE}/v2/process-content", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Wait for processing
                    await asyncio.sleep(2)
                    
                    # Get processed content
                    async with session.get(f"{API_BASE}/content-library") as lib_response:
                        if lib_response.status == 200:
                            lib_data = await lib_response.json()
                            articles = lib_data.get('articles', []) if isinstance(lib_data, dict) else lib_data
                            
                            if articles:
                                latest_article = max(articles, key=lambda x: x.get('created_at', ''))
                                content = latest_article.get('content', latest_article.get('html', ''))
                                
                                # Extract TOC links and headings
                                toc_links = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                                headings = re.findall(r'<h[2-6][^>]*id="([^"]+)"[^>]*>([^<]+)</h[2-6]>', content)
                                
                                print_info(f"Found {len(toc_links)} TOC links and {len(headings)} headings with IDs")
                                
                                # Check matching quality
                                successful_matches = 0
                                for link_target, link_text in toc_links:
                                    # Find corresponding heading
                                    matching_heading = None
                                    for heading_id, heading_text in headings:
                                        if heading_id == link_target:
                                            matching_heading = heading_text
                                            break
                                    
                                    if matching_heading:
                                        # Check if text matching was successful (flexible matching)
                                        link_words = set(link_text.lower().split())
                                        heading_words = set(matching_heading.lower().split())
                                        
                                        if link_words and heading_words:
                                            similarity = len(link_words & heading_words) / max(len(link_words), len(heading_words))
                                            if similarity >= 0.3:  # 30% word overlap is good flexible matching
                                                successful_matches += 1
                                                print_success(f"Good match: '{link_text}' -> '{matching_heading}' (similarity: {similarity:.2f})")
                                            else:
                                                print_info(f"Weak match: '{link_text}' -> '{matching_heading}' (similarity: {similarity:.2f})")
                                        else:
                                            print_error(f"No word overlap: '{link_text}' -> '{matching_heading}'")
                                    else:
                                        print_error(f"No target heading found for TOC link: '{link_text}' -> #{link_target}")
                                
                                if len(toc_links) > 0:
                                    match_quality = (successful_matches / len(toc_links)) * 100
                                    print_info(f"Flexible matching quality: {successful_matches}/{len(toc_links)} ({match_quality:.1f}%)")
                                    
                                    if match_quality >= 75:
                                        print_success(f"EXCELLENT: Flexible text matching working well ({match_quality:.1f}%)")
                                        return True
                                    elif match_quality >= 50:
                                        print_info(f"GOOD: Flexible matching mostly working ({match_quality:.1f}%)")
                                        return True
                                    else:
                                        print_error(f"POOR: Flexible matching needs improvement ({match_quality:.1f}%)")
                                        return False
                                else:
                                    print_error("No TOC links found for matching analysis")
                                    return False
                            else:
                                print_error("No articles found")
                                return False
                        else:
                            print_error("Failed to access content library")
                            return False
                else:
                    print_error(f"Processing failed - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing flexible text matching: {e}")
        return False

async def test_section_id_pattern_detection():
    """Test 3: Verify section-style ID pattern detection and continuation"""
    print_test_header("Test 3: Section ID Pattern Detection")
    
    # Test content with mixed ID patterns
    test_content = """
    <h1>Mixed ID Pattern Guide</h1>
    
    <ul>
        <li>Overview</li>
        <li>Setup Process</li>
        <li>Configuration</li>
        <li>Testing</li>
    </ul>
    
    <h2 id="section1">Overview</h2>
    <p>This is the overview section...</p>
    
    <h2 id="section2">Setup Process</h2>
    <p>Follow these setup steps...</p>
    
    <h2>Configuration</h2>
    <p>Configure your system...</p>
    
    <h2>Testing</h2>
    <p>Test your implementation...</p>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Testing section-style ID pattern detection...")
            
            payload = {
                "content": test_content,
                "source_type": "html",
                "processing_options": {
                    "enable_style_processing": True
                }
            }
            
            async with session.post(f"{API_BASE}/v2/process-content", json=payload) as response:
                if response.status == 200:
                    await asyncio.sleep(2)
                    
                    # Get processed content
                    async with session.get(f"{API_BASE}/content-library") as lib_response:
                        if lib_response.status == 200:
                            lib_data = await lib_response.json()
                            articles = lib_data.get('articles', []) if isinstance(lib_data, dict) else lib_data
                            
                            if articles:
                                latest_article = max(articles, key=lambda x: x.get('created_at', ''))
                                content = latest_article.get('content', latest_article.get('html', ''))
                                
                                # Check for section ID pattern continuation
                                section_ids = re.findall(r'id="(section\d+)"', content)
                                all_heading_ids = re.findall(r'<h[2-6][^>]*id="([^"]+)"', content)
                                
                                print_info(f"Found section IDs: {section_ids}")
                                print_info(f"All heading IDs: {all_heading_ids}")
                                
                                # Check if new headings got section-style IDs
                                section_pattern_continued = False
                                if len(section_ids) >= 2:  # Original had section1, section2
                                    # Check if new headings got section3, section4, etc.
                                    expected_sections = [f"section{i}" for i in range(1, len(all_heading_ids) + 1)]
                                    section_continuation_count = sum(1 for sid in section_ids if sid in expected_sections)
                                    
                                    if section_continuation_count >= len(section_ids) * 0.8:  # 80% follow pattern
                                        section_pattern_continued = True
                                        print_success(f"Section ID pattern continued: {section_continuation_count}/{len(section_ids)} follow pattern")
                                    else:
                                        print_info(f"Partial section pattern: {section_continuation_count}/{len(section_ids)} follow pattern")
                                
                                # Check TOC links use section IDs
                                toc_links = re.findall(r'<a href="#([^"]+)"', content)
                                section_link_usage = sum(1 for link in toc_links if link.startswith('section'))
                                
                                if len(toc_links) > 0:
                                    section_usage_rate = (section_link_usage / len(toc_links)) * 100
                                    print_info(f"TOC links using section IDs: {section_link_usage}/{len(toc_links)} ({section_usage_rate:.1f}%)")
                                    
                                    if section_pattern_continued and section_usage_rate >= 75:
                                        print_success("EXCELLENT: Section ID pattern detection and continuation working")
                                        return True
                                    elif section_usage_rate >= 50:
                                        print_info("GOOD: Section ID pattern mostly detected")
                                        return True
                                    else:
                                        print_error("POOR: Section ID pattern not properly detected")
                                        return False
                                else:
                                    print_error("No TOC links found")
                                    return False
                            else:
                                print_error("No articles found")
                                return False
                        else:
                            print_error("Failed to access content library")
                            return False
                else:
                    print_error(f"Processing failed - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing section ID pattern detection: {e}")
        return False

async def test_functional_navigation():
    """Test 4: Verify functional navigation - TOC links point to valid heading IDs"""
    print_test_header("Test 4: Functional Navigation Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get recent articles from content library
            print_info("Analyzing functional navigation in recent articles...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    if articles:
                        # Analyze multiple recent articles
                        navigation_results = []
                        
                        for article in articles[-5:]:  # Last 5 articles
                            content = article.get('content', article.get('html', ''))
                            title = article.get('title', 'Untitled')
                            
                            if content and '<a href="#' in content:
                                print_info(f"Analyzing navigation in: {title[:50]}...")
                                
                                # Extract all anchor links and heading IDs
                                anchor_links = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                                heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"', content)
                                
                                # Check functional navigation
                                valid_links = 0
                                broken_links = 0
                                
                                for link_target, link_text in anchor_links:
                                    if link_target in heading_ids:
                                        valid_links += 1
                                        print_success(f"Valid navigation: '{link_text}' -> #{link_target}")
                                    else:
                                        broken_links += 1
                                        print_error(f"Broken navigation: '{link_text}' -> #{link_target} (no target)")
                                
                                if len(anchor_links) > 0:
                                    navigation_rate = (valid_links / len(anchor_links)) * 100
                                    navigation_results.append({
                                        'title': title,
                                        'total_links': len(anchor_links),
                                        'valid_links': valid_links,
                                        'navigation_rate': navigation_rate
                                    })
                                    
                                    print_info(f"Navigation rate: {valid_links}/{len(anchor_links)} ({navigation_rate:.1f}%)")
                        
                        if navigation_results:
                            # Calculate overall navigation success
                            total_links = sum(r['total_links'] for r in navigation_results)
                            total_valid = sum(r['valid_links'] for r in navigation_results)
                            overall_rate = (total_valid / total_links) * 100 if total_links > 0 else 0
                            
                            print_info(f"Overall functional navigation: {total_valid}/{total_links} ({overall_rate:.1f}%)")
                            
                            if overall_rate >= 90:
                                print_success(f"EXCELLENT: Functional navigation working perfectly ({overall_rate:.1f}%)")
                                return True
                            elif overall_rate >= 75:
                                print_success(f"GOOD: Functional navigation mostly working ({overall_rate:.1f}%)")
                                return True
                            elif overall_rate >= 50:
                                print_info(f"MODERATE: Functional navigation partially working ({overall_rate:.1f}%)")
                                return True
                            else:
                                print_error(f"POOR: Functional navigation broken ({overall_rate:.1f}%)")
                                return False
                        else:
                            print_error("No articles with anchor links found for navigation testing")
                            return False
                    else:
                        print_error("No articles found in content library")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing functional navigation: {e}")
        return False

async def test_id_coordination_rate():
    """Test 5: Measure overall ID coordination rate and broken link reduction"""
    print_test_header("Test 5: ID Coordination Rate Measurement")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check style diagnostics for coordination metrics
            print_info("Checking style diagnostics for ID coordination metrics...")
            
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    
                    recent_results = diagnostics.get('recent_results', [])
                    if recent_results:
                        print_success(f"Found {len(recent_results)} recent style processing results")
                        
                        # Analyze coordination metrics
                        total_anchors = 0
                        total_broken = 0
                        coordination_samples = 0
                        
                        for result in recent_results:
                            result_str = str(result)
                            
                            # Look for anchor and broken link metrics
                            anchor_match = re.search(r'anchor_links_generated["\']:\s*(\d+)', result_str)
                            broken_match = re.search(r'toc_broken_links["\']:\s*\[([^\]]*)\]', result_str)
                            
                            if anchor_match:
                                anchors = int(anchor_match.group(1))
                                total_anchors += anchors
                                coordination_samples += 1
                                
                                if broken_match:
                                    broken_content = broken_match.group(1)
                                    # Count broken links (rough estimate)
                                    broken_count = broken_content.count('{') if broken_content.strip() else 0
                                    total_broken += broken_count
                                    
                                    print_info(f"Sample: {anchors} anchors, {broken_count} broken links")
                        
                        if coordination_samples > 0:
                            avg_anchors = total_anchors / coordination_samples
                            avg_broken = total_broken / coordination_samples
                            
                            if total_anchors > 0:
                                coordination_rate = ((total_anchors - total_broken) / total_anchors) * 100
                                print_info(f"ID Coordination Analysis:")
                                print_info(f"  Total anchors: {total_anchors}")
                                print_info(f"  Total broken: {total_broken}")
                                print_info(f"  Coordination rate: {coordination_rate:.1f}%")
                                
                                if coordination_rate >= 90:
                                    print_success(f"EXCELLENT: ID coordination rate ({coordination_rate:.1f}%)")
                                    return True
                                elif coordination_rate >= 75:
                                    print_success(f"GOOD: ID coordination rate ({coordination_rate:.1f}%)")
                                    return True
                                elif coordination_rate >= 50:
                                    print_info(f"MODERATE: ID coordination rate ({coordination_rate:.1f}%)")
                                    return True
                                else:
                                    print_error(f"POOR: ID coordination rate ({coordination_rate:.1f}%)")
                                    return False
                            else:
                                print_error("No anchor generation data found")
                                return False
                        else:
                            print_error("No coordination samples found in diagnostics")
                            return False
                    else:
                        print_error("No recent processing results found")
                        return False
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error measuring ID coordination rate: {e}")
        return False

async def test_html_anchor_format_maintenance():
    """Test 6: Confirm HTML anchor format is maintained"""
    print_test_header("Test 6: HTML Anchor Format Maintenance")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get recent articles and check anchor format
            print_info("Verifying HTML anchor format maintenance...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    if articles:
                        html_format_count = 0
                        markdown_format_count = 0
                        total_articles_checked = 0
                        
                        for article in articles[-10:]:  # Check last 10 articles
                            content = article.get('content', article.get('html', ''))
                            title = article.get('title', 'Untitled')
                            
                            if content and ('href="#' in content or '[' in content):
                                total_articles_checked += 1
                                
                                # Count HTML anchor format: <a href="#slug">text</a>
                                html_anchors = re.findall(r'<a[^>]*href="#[^"]+"[^>]*>[^<]+</a>', content)
                                
                                # Count Markdown format: [text](#slug)
                                markdown_anchors = re.findall(r'\[[^\]]+\]\(#[^)]+\)', content)
                                
                                if html_anchors:
                                    html_format_count += len(html_anchors)
                                    print_success(f"HTML format in '{title[:30]}...': {len(html_anchors)} anchors")
                                
                                if markdown_anchors:
                                    markdown_format_count += len(markdown_anchors)
                                    print_info(f"Markdown format in '{title[:30]}...': {len(markdown_anchors)} anchors")
                        
                        total_anchors = html_format_count + markdown_format_count
                        
                        if total_anchors > 0:
                            html_format_rate = (html_format_count / total_anchors) * 100
                            print_info(f"Anchor format analysis:")
                            print_info(f"  HTML format: {html_format_count}")
                            print_info(f"  Markdown format: {markdown_format_count}")
                            print_info(f"  HTML format rate: {html_format_rate:.1f}%")
                            
                            if html_format_rate >= 90:
                                print_success(f"EXCELLENT: HTML anchor format maintained ({html_format_rate:.1f}%)")
                                return True
                            elif html_format_rate >= 75:
                                print_success(f"GOOD: Mostly HTML format ({html_format_rate:.1f}%)")
                                return True
                            elif html_format_rate >= 50:
                                print_info(f"MODERATE: Mixed format usage ({html_format_rate:.1f}%)")
                                return True
                            else:
                                print_error(f"POOR: HTML format not maintained ({html_format_rate:.1f}%)")
                                return False
                        else:
                            print_error("No anchor links found for format analysis")
                            return False
                    else:
                        print_error("No articles found")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing HTML anchor format maintenance: {e}")
        return False

async def run_id_coordination_test_suite():
    """Run comprehensive ID coordination fix test suite"""
    print_test_header("ID Coordination Fix for Mini-TOC Links - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Testing 3-step ID matching process and coordination improvements")
    
    # Test results tracking
    test_results = []
    
    # Test 1: Existing Heading IDs Priority
    success = await test_existing_heading_ids_priority()
    test_results.append(("Existing Heading IDs Priority", success))
    
    # Test 2: Flexible Text Matching
    success = await test_flexible_text_matching()
    test_results.append(("Flexible Text Matching", success))
    
    # Test 3: Section ID Pattern Detection
    success = await test_section_id_pattern_detection()
    test_results.append(("Section ID Pattern Detection", success))
    
    # Test 4: Functional Navigation
    success = await test_functional_navigation()
    test_results.append(("Functional Navigation", success))
    
    # Test 5: ID Coordination Rate
    success = await test_id_coordination_rate()
    test_results.append(("ID Coordination Rate", success))
    
    # Test 6: HTML Anchor Format Maintenance
    success = await test_html_anchor_format_maintenance()
    test_results.append(("HTML Anchor Format Maintenance", success))
    
    # Final Results Summary
    print_test_header("ID Coordination Test Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Overall assessment
    if success_rate >= 85:
        print_success(f"🎉 ID COORDINATION FIX TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("The ID coordination fix is working excellently!")
        print_success("✅ TOC links prioritize existing heading IDs (section1, section2, etc.)")
        print_success("✅ 3-step matching process operational")
        print_success("✅ Section-style ID detection and continuation working")
        print_success("✅ Enhanced flexible text matching functional")
        print_success("✅ Functional navigation verified")
        print_success("✅ HTML anchor format maintained")
    elif success_rate >= 70:
        print_info(f"⚠️ ID COORDINATION MOSTLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Good progress made, minor improvements needed.")
    elif success_rate >= 50:
        print_info(f"⚠️ ID COORDINATION PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some functionality working, significant improvements needed.")
    else:
        print_error(f"❌ ID COORDINATION FIX TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Critical issues detected with ID coordination fix.")
    
    return success_rate >= 70

if __name__ == "__main__":
    print("🚀 Starting ID Coordination Fix Test Suite...")
    
    try:
        # Run the ID coordination test
        success = asyncio.run(run_id_coordination_test_suite())
        
        if success:
            print("\n🎯 ID COORDINATION TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 ID COORDINATION TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)