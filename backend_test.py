#!/usr/bin/env python3
"""
Backend Testing Suite for Mini-TOC Linking Issue Debug
Focus: V2StyleProcessor clickable anchors and content structure analysis
"""

import requests
import json
import sys
from datetime import datetime
import re
from bs4 import BeautifulSoup

# Backend URL from environment
BACKEND_URL = "https://content-pipeline-5.preview.emergentagent.com/api"

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*80}")
    print(f"🔍 {test_name}")
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

def test_v2_style_diagnostics():
    """Test 1: V2 Style Processing Diagnostic Check"""
    print_test_header("V2 Style Processing Diagnostic Check")
    
    try:
        # Test GET /api/style/diagnostics
        response = requests.get(f"{BACKEND_URL}/style/diagnostics", timeout=30)
        print_info(f"GET /api/style/diagnostics - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("V2 Style diagnostics endpoint accessible")
            
            # Check if V2StyleProcessor is running
            system_status = data.get('system_status', 'unknown')
            engine = data.get('engine', 'unknown')
            print_info(f"System Status: {system_status}")
            print_info(f"Engine: {engine}")
            
            # Check recent style results
            recent_results = data.get('recent_results', [])
            print_info(f"Recent style processing runs: {len(recent_results)}")
            
            if recent_results:
                latest_result = recent_results[0]
                print_info(f"Latest run ID: {latest_result.get('style_id', 'N/A')}")
                print_info(f"Latest run status: {latest_result.get('style_status', 'N/A')}")
                print_info(f"Latest run timestamp: {latest_result.get('timestamp', 'N/A')}")
                
                # Check for anchor-related metadata
                if 'anchor_links_generated' in latest_result:
                    print_success(f"Anchor links generated: {latest_result['anchor_links_generated']}")
                else:
                    print_error("No anchor_links_generated field found in latest result")
                
                if 'toc_broken_links' in latest_result:
                    broken_links = latest_result['toc_broken_links']
                    if isinstance(broken_links, list):
                        print_info(f"TOC broken links count: {len(broken_links)}")
                        if broken_links:
                            print_error(f"Found broken TOC links: {broken_links}")
                        else:
                            print_success("No broken TOC links detected")
                    else:
                        print_info(f"TOC broken links: {broken_links}")
                
                return latest_result.get('style_id')
            else:
                print_error("No recent style processing results found")
                return None
        else:
            print_error(f"Failed to access style diagnostics: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error testing style diagnostics: {e}")
        return None

def test_specific_style_result(style_id):
    """Test 2: Specific Style Result Analysis"""
    if not style_id:
        print_error("No style ID provided for specific analysis")
        return None
        
    print_test_header(f"Specific Style Result Analysis - ID: {style_id}")
    
    try:
        # Test GET /api/style/diagnostics/{style_id}
        response = requests.get(f"{BACKEND_URL}/style/diagnostics/{style_id}", timeout=30)
        print_info(f"GET /api/style/diagnostics/{style_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Specific style result accessible")
            
            # Check style result details
            style_result = data.get('style_result', {})
            analysis = data.get('analysis', {})
            
            print_info(f"Article title: {style_result.get('article_title', 'N/A')}")
            print_info(f"Style status: {style_result.get('style_status', 'N/A')}")
            
            # Check for clickable anchor processing
            if 'anchor_links_generated' in style_result:
                anchor_count = style_result['anchor_links_generated']
                print_success(f"Anchor links generated: {anchor_count}")
                
                if anchor_count > 0:
                    print_success("✓ Clickable anchors are being generated")
                else:
                    print_error("✗ No anchor links generated")
            
            # Check TOC broken links
            if 'toc_broken_links' in style_result:
                broken_links = style_result['toc_broken_links']
                if isinstance(broken_links, list) and len(broken_links) == 0:
                    print_success("✓ No broken TOC links")
                elif isinstance(broken_links, list) and len(broken_links) > 0:
                    print_error(f"✗ Found {len(broken_links)} broken TOC links:")
                    for link in broken_links:
                        print_error(f"  - {link}")
                else:
                    print_info(f"TOC broken links: {broken_links}")
            
            # Check structural compliance
            if 'structural_compliance' in analysis:
                compliance = analysis['structural_compliance']
                print_info(f"Structural compliance score: {compliance.get('compliance_score', 'N/A')}")
                
                if 'has_mini_toc' in compliance:
                    has_toc = compliance['has_mini_toc']
                    print_success(f"✓ Has Mini-TOC: {has_toc}") if has_toc else print_error(f"✗ No Mini-TOC: {has_toc}")
                
                if 'toc_anchor_count' in compliance:
                    toc_count = compliance['toc_anchor_count']
                    print_success(f"✓ TOC anchor count: {toc_count}") if toc_count > 0 else print_error(f"✗ No TOC anchors: {toc_count}")
            
            return style_result
        else:
            print_error(f"Failed to access specific style result: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error testing specific style result: {e}")
        return None

def test_content_library_search():
    """Test 3: Content Library Search for Target Article"""
    print_test_header("Content Library Search - Code Normalization Article")
    
    try:
        # Search for the specific article mentioned in the review
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        print_info(f"GET /api/content-library - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print_success(f"Content library accessible - {len(articles)} articles found")
            
            # Look for the specific article
            target_article = None
            for article in articles:
                title = article.get('title', '').lower()
                if 'code normalization' in title and 'javascript' in title:
                    target_article = article
                    break
            
            if target_article:
                print_success(f"✓ Found target article: {target_article['title']}")
                print_info(f"Article ID: {target_article.get('id', 'N/A')}")
                print_info(f"Article status: {target_article.get('status', 'N/A')}")
                return target_article
            else:
                print_error("✗ Target article 'Code Normalization in JavaScript: A Practical Example' not found")
                
                # Show available articles for debugging
                print_info("Available articles:")
                for i, article in enumerate(articles[:10]):  # Show first 10
                    print_info(f"  {i+1}. {article.get('title', 'Untitled')}")
                
                return None
        else:
            print_error(f"Failed to access content library: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error searching content library: {e}")
        return None

def analyze_article_content(article):
    """Test 4: Analyze Article Content Structure"""
    if not article:
        print_error("No article provided for content analysis")
        return
        
    print_test_header(f"Article Content Analysis - {article.get('title', 'Unknown')}")
    
    try:
        content = article.get('content', '') or article.get('html', '')
        if not content:
            print_error("No content found in article")
            return
        
        print_info(f"Content length: {len(content)} characters")
        
        # Parse HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check for Mini-TOC structure
        print_info("\n🔍 Mini-TOC Analysis:")
        
        # Look for TOC patterns
        toc_patterns = [
            soup.find_all('ul', class_='toc-list'),
            soup.find_all('ul', class_='mini-toc'),
            soup.find_all('div', class_='toc'),
            soup.find_all('ul')[:3]  # Check first few ul elements
        ]
        
        toc_found = False
        for pattern_group in toc_patterns:
            for toc_element in pattern_group:
                if toc_element:
                    toc_items = toc_element.find_all('li')
                    if len(toc_items) >= 3:  # Likely a TOC if it has multiple items
                        print_success(f"✓ Found potential Mini-TOC with {len(toc_items)} items")
                        toc_found = True
                        
                        # Analyze TOC items for clickable links
                        clickable_count = 0
                        for i, item in enumerate(toc_items):
                            item_text = item.get_text().strip()
                            links = item.find_all('a')
                            
                            print_info(f"  TOC Item {i+1}: {item_text[:50]}...")
                            
                            if links:
                                for link in links:
                                    href = link.get('href', '')
                                    if href.startswith('#'):
                                        print_success(f"    ✓ Clickable anchor link: {href}")
                                        clickable_count += 1
                                    else:
                                        print_info(f"    - Non-anchor link: {href}")
                            else:
                                print_error(f"    ✗ No clickable links found")
                        
                        print_info(f"Total clickable TOC links: {clickable_count}/{len(toc_items)}")
                        break
            if toc_found:
                break
        
        if not toc_found:
            print_error("✗ No Mini-TOC structure found")
            
            # Look for markdown-style TOC links in raw content
            markdown_toc_pattern = r'\[([^\]]+)\]\(#([^)]+)\)'
            markdown_matches = re.findall(markdown_toc_pattern, content)
            if markdown_matches:
                print_success(f"✓ Found {len(markdown_matches)} markdown-style TOC links:")
                for text, anchor in markdown_matches:
                    print_info(f"  - [{text}](#{anchor})")
            else:
                print_error("✗ No markdown-style TOC links found either")
        
        # Check for heading IDs
        print_info("\n🔍 Heading ID Analysis:")
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print_info(f"Total headings found: {len(headings)}")
        
        headings_with_ids = 0
        for i, heading in enumerate(headings):
            heading_id = heading.get('id', '')
            heading_text = heading.get_text().strip()
            
            if heading_id:
                print_success(f"  ✓ {heading.name.upper()}: '{heading_text[:40]}...' ID='{heading_id}'")
                headings_with_ids += 1
            else:
                print_error(f"  ✗ {heading.name.upper()}: '{heading_text[:40]}...' (No ID)")
        
        print_info(f"Headings with IDs: {headings_with_ids}/{len(headings)}")
        
        # Show raw content sample for debugging
        print_info("\n🔍 Raw Content Sample (first 1000 chars):")
        print_info(content[:1000])
        
        if len(content) > 1000:
            print_info("... (content truncated)")
        
        return {
            'toc_found': toc_found,
            'headings_total': len(headings),
            'headings_with_ids': headings_with_ids,
            'content_length': len(content)
        }
        
    except Exception as e:
        print_error(f"Error analyzing article content: {e}")
        return None

def test_v2_processing_pipeline():
    """Test 5: V2 Processing Pipeline Status"""
    print_test_header("V2 Processing Pipeline Status")
    
    try:
        # Check V2 engine status
        response = requests.get(f"{BACKEND_URL}/engine", timeout=30)
        print_info(f"GET /api/engine - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            engine_status = data.get('status', 'unknown')
            engine_version = data.get('engine', 'unknown')
            
            print_info(f"Engine status: {engine_status}")
            print_info(f"Engine version: {engine_version}")
            
            # Check for V2-specific features
            features = data.get('features', {})
            v2_features = [
                'woolf_style_processing',
                'structural_linting',
                'microsoft_style_guide',
                'technical_writing_standards'
            ]
            
            print_info("\n🔍 V2 Style Processing Features:")
            if isinstance(features, dict):
                for feature in v2_features:
                    if feature in features:
                        print_success(f"  ✓ {feature}: {features[feature]}")
                    else:
                        print_error(f"  ✗ {feature}: Not found")
            elif isinstance(features, list):
                print_info(f"Features (list format): {features}")
                for feature in v2_features:
                    if feature in features:
                        print_success(f"  ✓ {feature}: Present")
                    else:
                        print_error(f"  ✗ {feature}: Not found")
            else:
                print_error(f"Unexpected features format: {type(features)} - {features}")
            
            # Check for style diagnostics endpoint
            endpoints = data.get('endpoints', {})
            if 'style_diagnostics' in endpoints:
                print_success(f"  ✓ style_diagnostics endpoint: {endpoints['style_diagnostics']}")
            else:
                print_error("  ✗ style_diagnostics endpoint not found")
            
            return True
        else:
            print_error(f"Failed to access engine status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing V2 processing pipeline: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Mini-TOC Linking Issue Debug Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Test results tracking
    results = {
        'v2_diagnostics': False,
        'style_processing': False,
        'content_found': False,
        'toc_analysis': False,
        'pipeline_status': False
    }
    
    # Test 1: V2 Style Processing Diagnostics
    style_id = test_v2_style_diagnostics()
    results['v2_diagnostics'] = style_id is not None
    
    # Test 2: Specific Style Result Analysis
    if style_id:
        style_result = test_specific_style_result(style_id)
        results['style_processing'] = style_result is not None
    
    # Test 3: Content Library Search
    target_article = test_content_library_search()
    results['content_found'] = target_article is not None
    
    # Test 4: Article Content Analysis
    if target_article:
        content_analysis = analyze_article_content(target_article)
        results['toc_analysis'] = content_analysis is not None
    
    # Test 5: V2 Processing Pipeline Status
    pipeline_ok = test_v2_processing_pipeline()
    results['pipeline_status'] = pipeline_ok
    
    # Final Summary
    print_test_header("MINI-TOC LINKING DEBUG SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print_info(f"Tests completed: {passed_tests}/{total_tests}")
    
    for test_name, passed in results.items():
        if passed:
            print_success(f"✓ {test_name}")
        else:
            print_error(f"✗ {test_name}")
    
    # Diagnostic conclusions
    print_info("\n🔍 DIAGNOSTIC CONCLUSIONS:")
    
    if results['v2_diagnostics'] and results['style_processing']:
        print_success("✓ V2StyleProcessor is operational and processing content")
    else:
        print_error("✗ V2StyleProcessor may not be working correctly")
    
    if results['content_found'] and results['toc_analysis']:
        print_success("✓ Target article found and analyzed")
    else:
        print_error("✗ Could not analyze target article content")
    
    if results['pipeline_status']:
        print_success("✓ V2 processing pipeline is active")
    else:
        print_error("✗ V2 processing pipeline issues detected")
    
    print_info(f"\nTest completed at: {datetime.now().isoformat()}")
    
    # Return success rate for automation
    success_rate = (passed_tests / total_tests) * 100
    print_info(f"Overall success rate: {success_rate:.1f}%")
    
    return success_rate >= 60  # Consider 60%+ as acceptable for debugging

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)