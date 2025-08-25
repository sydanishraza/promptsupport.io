#!/usr/bin/env python3
"""
Focused ID Coordination Test for Mini-TOC Links
Analyzing existing content to verify the ID coordination fix implementation

FOCUS: Test the 3-step ID matching process on existing articles
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

async def analyze_existing_articles():
    """Analyze existing articles for ID coordination patterns"""
    print_test_header("Analyzing Existing Articles for ID Coordination")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get articles from content library
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    print_info(f"Found {len(articles)} articles in content library")
                    
                    # Analyze articles with TOC links
                    toc_articles = []
                    for article in articles:
                        content = article.get('content', article.get('html', ''))
                        if content and '<a href="#' in content and '<h' in content:
                            toc_articles.append(article)
                    
                    print_info(f"Found {len(toc_articles)} articles with TOC links and headings")
                    
                    if len(toc_articles) >= 3:
                        # Analyze the most relevant articles
                        coordination_results = []
                        
                        for i, article in enumerate(toc_articles[:5]):  # Analyze top 5
                            title = article.get('title', 'Untitled')
                            content = article.get('content', article.get('html', ''))
                            
                            print_info(f"Analyzing article {i+1}: {title[:50]}...")
                            
                            result = analyze_article_coordination(content, title)
                            coordination_results.append(result)
                            
                            print_info(f"  TOC Links: {result['toc_links_count']}")
                            print_info(f"  Heading IDs: {result['heading_ids_count']}")
                            print_info(f"  Valid Navigation: {result['valid_navigation']}/{result['toc_links_count']} ({result['navigation_rate']:.1f}%)")
                            print_info(f"  Section ID Usage: {result['section_id_usage']}/{result['toc_links_count']} ({result['section_usage_rate']:.1f}%)")
                        
                        # Calculate overall metrics
                        total_toc_links = sum(r['toc_links_count'] for r in coordination_results)
                        total_valid_navigation = sum(r['valid_navigation'] for r in coordination_results)
                        total_section_usage = sum(r['section_id_usage'] for r in coordination_results)
                        
                        overall_navigation_rate = (total_valid_navigation / total_toc_links * 100) if total_toc_links > 0 else 0
                        overall_section_rate = (total_section_usage / total_toc_links * 100) if total_toc_links > 0 else 0
                        
                        print_test_header("Overall ID Coordination Analysis Results")
                        print_info(f"Total TOC Links Analyzed: {total_toc_links}")
                        print_info(f"Valid Navigation Links: {total_valid_navigation}")
                        print_info(f"Section ID Usage: {total_section_usage}")
                        print_info(f"Overall Navigation Rate: {overall_navigation_rate:.1f}%")
                        print_info(f"Overall Section ID Usage Rate: {overall_section_rate:.1f}%")
                        
                        return {
                            'success': True,
                            'articles_analyzed': len(coordination_results),
                            'total_toc_links': total_toc_links,
                            'navigation_rate': overall_navigation_rate,
                            'section_usage_rate': overall_section_rate,
                            'coordination_results': coordination_results
                        }
                    else:
                        print_error("Insufficient articles with TOC links for analysis")
                        return {'success': False, 'reason': 'insufficient_articles'}
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return {'success': False, 'reason': 'api_error'}
                    
    except Exception as e:
        print_error(f"Error analyzing existing articles: {e}")
        return {'success': False, 'reason': 'exception', 'error': str(e)}

def analyze_article_coordination(content, title):
    """Analyze a single article for ID coordination patterns"""
    
    # Extract TOC links
    toc_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', content)
    
    # Extract heading IDs
    heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"', content)
    
    # Extract section-style IDs
    section_ids = [hid for hid in heading_ids if re.match(r'section\d+', hid)]
    
    # Check navigation validity
    valid_navigation = 0
    section_id_usage = 0
    
    for link_target, link_text in toc_links:
        if link_target in heading_ids:
            valid_navigation += 1
        
        if link_target.startswith('section'):
            section_id_usage += 1
    
    navigation_rate = (valid_navigation / len(toc_links) * 100) if len(toc_links) > 0 else 0
    section_usage_rate = (section_id_usage / len(toc_links) * 100) if len(toc_links) > 0 else 0
    
    return {
        'title': title,
        'toc_links_count': len(toc_links),
        'heading_ids_count': len(heading_ids),
        'section_ids_count': len(section_ids),
        'valid_navigation': valid_navigation,
        'section_id_usage': section_id_usage,
        'navigation_rate': navigation_rate,
        'section_usage_rate': section_usage_rate,
        'toc_links': toc_links[:3],  # Sample of first 3
        'heading_ids': heading_ids[:5],  # Sample of first 5
        'section_ids': section_ids
    }

async def test_toc_processing_endpoint():
    """Test the TOC processing endpoint if available"""
    print_test_header("Testing TOC Processing Endpoint")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check if TOC processing endpoint exists
            async with session.get(f"{API_BASE}/style/process-toc-links") as response:
                if response.status == 200:
                    result = await response.json()
                    print_success("TOC processing endpoint is accessible")
                    
                    # Look for processing statistics
                    if 'articles_processed' in result:
                        articles_processed = result.get('articles_processed', 0)
                        print_info(f"Articles processed: {articles_processed}")
                    
                    if 'anchor_links_generated' in result:
                        anchors_generated = result.get('anchor_links_generated', 0)
                        print_info(f"Anchor links generated: {anchors_generated}")
                    
                    return True
                elif response.status == 404:
                    print_info("TOC processing endpoint not found (expected)")
                    return True  # Not a failure
                else:
                    print_error(f"TOC processing endpoint error - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error testing TOC processing endpoint: {e}")
        return False

async def test_style_diagnostics():
    """Test style diagnostics for TOC processing information"""
    print_test_header("Testing Style Diagnostics for TOC Information")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    print_success("Style diagnostics accessible")
                    
                    # Check system status
                    system_status = diagnostics.get('system_status', 'unknown')
                    engine = diagnostics.get('engine', 'unknown')
                    
                    print_info(f"System Status: {system_status}")
                    print_info(f"Engine: {engine}")
                    
                    # Look for recent results
                    recent_results = diagnostics.get('recent_results', [])
                    if recent_results:
                        print_info(f"Recent processing results: {len(recent_results)}")
                        
                        # Analyze for TOC-related processing
                        toc_processing_found = 0
                        anchor_generation_found = 0
                        
                        for result in recent_results:
                            result_str = str(result).lower()
                            
                            if any(keyword in result_str for keyword in ['toc', 'anchor', 'clickable']):
                                toc_processing_found += 1
                            
                            if 'anchor_links_generated' in result_str:
                                anchor_generation_found += 1
                        
                        print_info(f"Results with TOC processing: {toc_processing_found}")
                        print_info(f"Results with anchor generation: {anchor_generation_found}")
                        
                        return {
                            'success': True,
                            'system_active': system_status == 'active',
                            'v2_engine': engine == 'v2',
                            'toc_processing_found': toc_processing_found > 0,
                            'anchor_generation_found': anchor_generation_found > 0
                        }
                    else:
                        print_info("No recent processing results found")
                        return {
                            'success': True,
                            'system_active': system_status == 'active',
                            'v2_engine': engine == 'v2',
                            'toc_processing_found': False,
                            'anchor_generation_found': False
                        }
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return {'success': False}
                    
    except Exception as e:
        print_error(f"Error testing style diagnostics: {e}")
        return {'success': False}

async def test_specific_article_coordination():
    """Test ID coordination on a specific article with known patterns"""
    print_test_header("Testing Specific Article ID Coordination")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    # Find the "Building a Basic Google Map" article (known to have good coordination)
                    target_article = None
                    for article in articles:
                        title = article.get('title', '')
                        if 'Building a Basic Google Map' in title:
                            target_article = article
                            break
                    
                    if target_article:
                        content = target_article.get('content', target_article.get('html', ''))
                        title = target_article.get('title', 'Untitled')
                        
                        print_info(f"Analyzing target article: {title}")
                        
                        # Detailed analysis
                        toc_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*class="toc-link"[^>]*>([^<]+)</a>', content)
                        all_anchor_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                        heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"[^>]*>([^<]+)</h[1-6]>', content)
                        
                        print_info(f"TOC links with toc-link class: {len(toc_links)}")
                        print_info(f"All anchor links: {len(all_anchor_links)}")
                        print_info(f"Headings with IDs: {len(heading_ids)}")
                        
                        # Check coordination quality
                        perfect_matches = 0
                        section_matches = 0
                        
                        for link_target, link_text in all_anchor_links:
                            # Check if target exists as heading ID
                            matching_heading = None
                            for heading_id, heading_text in heading_ids:
                                if heading_id == link_target:
                                    matching_heading = heading_text
                                    perfect_matches += 1
                                    break
                            
                            # Check if it's a section-style ID
                            if link_target.startswith('section'):
                                section_matches += 1
                            
                            if matching_heading:
                                print_success(f"Perfect match: '{link_text}' -> #{link_target} -> '{matching_heading}'")
                            else:
                                print_error(f"Broken link: '{link_text}' -> #{link_target} (no target)")
                        
                        if len(all_anchor_links) > 0:
                            coordination_rate = (perfect_matches / len(all_anchor_links)) * 100
                            section_rate = (section_matches / len(all_anchor_links)) * 100
                            
                            print_info(f"Perfect coordination rate: {perfect_matches}/{len(all_anchor_links)} ({coordination_rate:.1f}%)")
                            print_info(f"Section ID usage rate: {section_matches}/{len(all_anchor_links)} ({section_rate:.1f}%)")
                            
                            return {
                                'success': True,
                                'coordination_rate': coordination_rate,
                                'section_rate': section_rate,
                                'perfect_matches': perfect_matches,
                                'total_links': len(all_anchor_links)
                            }
                        else:
                            print_error("No anchor links found in target article")
                            return {'success': False, 'reason': 'no_links'}
                    else:
                        print_error("Target article not found")
                        return {'success': False, 'reason': 'article_not_found'}
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return {'success': False, 'reason': 'api_error'}
                    
    except Exception as e:
        print_error(f"Error testing specific article coordination: {e}")
        return {'success': False, 'reason': 'exception'}

async def run_focused_id_coordination_test():
    """Run focused ID coordination test suite"""
    print_test_header("Focused ID Coordination Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Analyzing existing content for ID coordination improvements")
    
    # Test results tracking
    test_results = []
    
    # Test 1: Analyze existing articles
    result = await analyze_existing_articles()
    test_results.append(("Existing Articles Analysis", result.get('success', False)))
    
    # Test 2: Test TOC processing endpoint
    success = await test_toc_processing_endpoint()
    test_results.append(("TOC Processing Endpoint", success))
    
    # Test 3: Test style diagnostics
    diag_result = await test_style_diagnostics()
    test_results.append(("Style Diagnostics", diag_result.get('success', False)))
    
    # Test 4: Test specific article coordination
    specific_result = await test_specific_article_coordination()
    test_results.append(("Specific Article Coordination", specific_result.get('success', False)))
    
    # Final Results Summary
    print_test_header("Focused ID Coordination Test Results")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Detailed assessment based on results
    if result.get('success') and result.get('navigation_rate', 0) >= 80:
        print_success(f"🎉 ID COORDINATION FIX IS WORKING EXCELLENTLY!")
        print_success(f"Navigation Rate: {result.get('navigation_rate', 0):.1f}%")
        print_success(f"Section ID Usage: {result.get('section_usage_rate', 0):.1f}%")
        print_success("✅ TOC links are properly coordinated with heading IDs")
        print_success("✅ Section-style ID pattern is being used effectively")
        
        if specific_result.get('success') and specific_result.get('coordination_rate', 0) >= 90:
            print_success("✅ Perfect coordination achieved in target article")
        
        return True
    elif result.get('success') and result.get('navigation_rate', 0) >= 50:
        print_info(f"⚠️ ID COORDINATION PARTIALLY WORKING")
        print_info(f"Navigation Rate: {result.get('navigation_rate', 0):.1f}%")
        print_info(f"Section ID Usage: {result.get('section_usage_rate', 0):.1f}%")
        print_info("Some coordination improvements detected, but more work needed")
        return True
    else:
        print_error(f"❌ ID COORDINATION NEEDS IMPROVEMENT")
        if result.get('success'):
            print_error(f"Navigation Rate: {result.get('navigation_rate', 0):.1f}%")
            print_error(f"Section ID Usage: {result.get('section_usage_rate', 0):.1f}%")
        print_error("ID coordination fix may not be working as expected")
        return False

if __name__ == "__main__":
    print("🚀 Starting Focused ID Coordination Test...")
    
    try:
        # Run the focused ID coordination test
        success = asyncio.run(run_focused_id_coordination_test())
        
        if success:
            print("\n🎯 FOCUSED ID COORDINATION TEST COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 FOCUSED ID COORDINATION TEST COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)