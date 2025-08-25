#!/usr/bin/env python3
"""
V2 Engine Content Analysis Test Suite
Analyzing existing Google Maps API articles for specific issues
Focus: Content analysis for H1 tags, Mini-TOC, list types, code rendering, and code quality
"""

import asyncio
import aiohttp
import json
import os
import re
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

async def get_google_maps_articles():
    """Get Google Maps API articles from content library"""
    print_test_header("Test 1: Retrieve Google Maps API Articles")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Fetching articles from content library...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    print_success(f"Content library accessible - {len(articles)} total articles")
                    
                    # Filter Google Maps articles
                    google_maps_articles = []
                    for article in articles:
                        title = article.get('title', '').lower()
                        if 'google' in title and 'map' in title:
                            google_maps_articles.append(article)
                    
                    print_success(f"Found {len(google_maps_articles)} Google Maps API articles")
                    
                    for i, article in enumerate(google_maps_articles, 1):
                        print_info(f"  {i}. {article.get('title', 'Untitled')} (ID: {article.get('id', 'N/A')})")
                    
                    return google_maps_articles
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return []
                    
    except Exception as e:
        print_error(f"Error retrieving articles: {e}")
        return []

async def analyze_h1_tags_issue(articles):
    """Test 2: Analyze Multiple H1 Tags Issue"""
    print_test_header("Test 2: Multiple H1 Tags Analysis")
    
    try:
        print_info("Analyzing articles for multiple H1 tags in article body...")
        
        h1_issues = []
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', article.get('html', ''))
            article_id = article.get('id', 'N/A')
            
            print_info(f"Analyzing: {title}")
            
            # Find all H1 tags
            h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL | re.IGNORECASE)
            h1_count = len(h1_matches)
            
            print_info(f"  - H1 tags found: {h1_count}")
            
            if h1_count > 1:
                h1_issues.append({
                    'title': title,
                    'article_id': article_id,
                    'h1_count': h1_count,
                    'h1_texts': [h1.strip()[:50] + '...' if len(h1.strip()) > 50 else h1.strip() for h1 in h1_matches]
                })
                print_error(f"  - ISSUE: Multiple H1 tags found ({h1_count})")
                for i, h1_text in enumerate(h1_matches, 1):
                    clean_text = re.sub(r'<[^>]+>', '', h1_text).strip()
                    print_error(f"    H1 #{i}: {clean_text[:60]}...")
            else:
                print_success(f"  - OK: {h1_count} H1 tag (correct)")
        
        # Summary
        if h1_issues:
            print_error(f"H1 TAGS ISSUE DETECTED: {len(h1_issues)} articles have multiple H1 tags")
            return False, h1_issues
        else:
            print_success("H1 TAGS: All articles have correct H1 structure")
            return True, []
            
    except Exception as e:
        print_error(f"Error analyzing H1 tags: {e}")
        return False, []

async def analyze_mini_toc_issue(articles):
    """Test 3: Analyze Static Mini-TOC Lists Issue"""
    print_test_header("Test 3: Static Mini-TOC Lists Analysis")
    
    try:
        print_info("Analyzing articles for static (non-clickable) Mini-TOC lists...")
        
        toc_issues = []
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', article.get('html', ''))
            article_id = article.get('id', 'N/A')
            
            print_info(f"Analyzing: {title}")
            
            # Look for Mini-TOC patterns
            toc_patterns = [
                r'<ul[^>]*>.*?<li[^>]*>[^<]*(?:introduction|getting started|overview|setup|basic|advanced)',
                r'<ol[^>]*>.*?<li[^>]*>[^<]*(?:introduction|getting started|overview|setup|basic|advanced)',
                r'- (?:Introduction|Getting Started|Overview|Setup|Basic|Advanced)',
                r'\* (?:Introduction|Getting Started|Overview|Setup|Basic|Advanced)'
            ]
            
            toc_found = False
            static_toc_found = False
            clickable_toc_found = False
            
            for pattern in toc_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    toc_found = True
                    print_info(f"  - TOC pattern found: {len(matches)} matches")
                    
                    # Check if TOC items are clickable (contain links)
                    for match in matches:
                        if re.search(r'<a\s+href=|href=', match):
                            clickable_toc_found = True
                            print_success(f"  - Clickable TOC found")
                        else:
                            static_toc_found = True
                            print_error(f"  - Static TOC found (non-clickable)")
                    break
            
            # Also check for markdown-style TOC links
            markdown_toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
            if markdown_toc_links:
                clickable_toc_found = True
                print_success(f"  - Markdown TOC links found: {len(markdown_toc_links)}")
                for text, anchor in markdown_toc_links[:3]:  # Show first 3
                    print_info(f"    - [{text}](#{anchor})")
            
            if toc_found and static_toc_found and not clickable_toc_found:
                toc_issues.append({
                    'title': title,
                    'article_id': article_id,
                    'issue': 'static_mini_toc',
                    'description': 'Mini-TOC found but not clickable'
                })
                print_error(f"  - ISSUE: Static Mini-TOC (non-clickable)")
            elif not toc_found:
                print_info(f"  - No Mini-TOC found")
            else:
                print_success(f"  - OK: Clickable Mini-TOC present")
        
        # Summary
        if toc_issues:
            print_error(f"MINI-TOC ISSUE DETECTED: {len(toc_issues)} articles have static Mini-TOC")
            return False, toc_issues
        else:
            print_success("MINI-TOC: All articles have clickable TOC or no TOC")
            return True, []
            
    except Exception as e:
        print_error(f"Error analyzing Mini-TOC: {e}")
        return False, []

async def analyze_list_type_issue(articles):
    """Test 4: Analyze Incorrect List Type Detection"""
    print_test_header("Test 4: List Type Detection Analysis")
    
    try:
        print_info("Analyzing articles for incorrect list type detection...")
        
        list_issues = []
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', article.get('html', ''))
            article_id = article.get('id', 'N/A')
            
            print_info(f"Analyzing: {title}")
            
            # Count different list types
            ordered_lists = len(re.findall(r'<ol[^>]*>', content))
            unordered_lists = len(re.findall(r'<ul[^>]*>', content))
            
            # Look for numbered content that should be ordered lists
            numbered_items = re.findall(r'^\d+\.\s+(.+)', content, re.MULTILINE)
            numbered_in_paragraphs = re.findall(r'<p[^>]*>\s*\d+\.\s+(.+?)</p>', content, re.DOTALL)
            
            # Look for bullet points that should be unordered lists
            bullet_items = re.findall(r'^[-*]\s+(.+)', content, re.MULTILINE)
            bullet_in_paragraphs = re.findall(r'<p[^>]*>\s*[-*]\s+(.+?)</p>', content, re.DOTALL)
            
            total_numbered = len(numbered_items) + len(numbered_in_paragraphs)
            total_bullets = len(bullet_items) + len(bullet_in_paragraphs)
            
            print_info(f"  - Ordered lists: {ordered_lists}")
            print_info(f"  - Unordered lists: {unordered_lists}")
            print_info(f"  - Numbered items in text: {total_numbered}")
            print_info(f"  - Bullet items in text: {total_bullets}")
            
            # Check for issues
            issues = []
            
            if total_numbered > 3 and ordered_lists == 0:
                issues.append(f"Found {total_numbered} numbered items but no ordered lists")
                print_error(f"  - ISSUE: {total_numbered} numbered items should be <ol>")
            
            if total_bullets > 3 and unordered_lists == 0:
                issues.append(f"Found {total_bullets} bullet items but no unordered lists")
                print_error(f"  - ISSUE: {total_bullets} bullet items should be <ul>")
            
            if issues:
                list_issues.append({
                    'title': title,
                    'article_id': article_id,
                    'issues': issues,
                    'numbered_items': total_numbered,
                    'bullet_items': total_bullets,
                    'ordered_lists': ordered_lists,
                    'unordered_lists': unordered_lists
                })
            else:
                print_success(f"  - OK: List types properly detected")
        
        # Summary
        if list_issues:
            print_error(f"LIST TYPE ISSUE DETECTED: {len(list_issues)} articles have incorrect list detection")
            return False, list_issues
        else:
            print_success("LIST TYPES: All articles have correct list type detection")
            return True, []
            
    except Exception as e:
        print_error(f"Error analyzing list types: {e}")
        return False, []

async def analyze_code_rendering_issue(articles):
    """Test 5: Analyze Code Rendering Problems"""
    print_test_header("Test 5: Code Rendering Problems Analysis")
    
    try:
        print_info("Analyzing articles for code rendering problems...")
        
        code_issues = []
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', article.get('html', ''))
            article_id = article.get('id', 'N/A')
            
            print_info(f"Analyzing: {title}")
            
            # Find all code blocks
            code_blocks = re.findall(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
            inline_code = re.findall(r'<code[^>]*>(.*?)</code>', content, re.DOTALL)
            
            print_info(f"  - Code blocks (<pre>): {len(code_blocks)}")
            print_info(f"  - Inline code (<code>): {len(inline_code)}")
            
            issues = []
            
            # Check for code blocks that should be separate
            for i, code_block in enumerate(code_blocks):
                # Remove HTML tags for analysis
                clean_code = re.sub(r'<[^>]+>', '', code_block)
                
                # Check for multiple functions/methods in one block
                function_count = len(re.findall(r'\bfunction\b|\bdef\b|\bclass\b', clean_code))
                var_count = len(re.findall(r'\bvar\b|\blet\b|\bconst\b', clean_code))
                
                if function_count > 1 and len(clean_code) > 300:
                    issues.append(f"Code block {i+1}: Multiple functions ({function_count}) in single block")
                    print_error(f"  - ISSUE: Code block {i+1} has {function_count} functions (should be separate)")
                
                if var_count > 5 and len(clean_code) > 500:
                    issues.append(f"Code block {i+1}: Too many variables ({var_count}) - might need splitting")
                    print_error(f"  - ISSUE: Code block {i+1} has {var_count} variables (might be too complex)")
                
                # Check for proper wrapping
                if not re.search(r'<pre[^>]*class=', f'<pre>{code_block}</pre>') and len(clean_code) > 100:
                    issues.append(f"Code block {i+1}: Missing proper CSS class for styling")
                    print_error(f"  - ISSUE: Code block {i+1} missing proper wrapper class")
            
            # Check for inline code that should be blocks
            for i, inline in enumerate(inline_code):
                clean_inline = re.sub(r'<[^>]+>', '', inline)
                if len(clean_inline) > 100 or '\n' in clean_inline:
                    issues.append(f"Inline code {i+1}: Too long for inline ({len(clean_inline)} chars)")
                    print_error(f"  - ISSUE: Inline code {i+1} too long ({len(clean_inline)} chars) - should be block")
            
            if issues:
                code_issues.append({
                    'title': title,
                    'article_id': article_id,
                    'issues': issues,
                    'code_blocks_count': len(code_blocks),
                    'inline_code_count': len(inline_code)
                })
            else:
                print_success(f"  - OK: Code rendering properly structured")
        
        # Summary
        if code_issues:
            print_error(f"CODE RENDERING ISSUE DETECTED: {len(code_issues)} articles have code rendering problems")
            return False, code_issues
        else:
            print_success("CODE RENDERING: All articles have proper code structure")
            return True, []
            
    except Exception as e:
        print_error(f"Error analyzing code rendering: {e}")
        return False, []

async def analyze_code_quality_issue(articles):
    """Test 6: Analyze Code Quality Issues"""
    print_test_header("Test 6: Code Quality Issues Analysis")
    
    try:
        print_info("Analyzing articles for code quality issues (distorted/pixelated text)...")
        
        quality_issues = []
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', article.get('html', ''))
            article_id = article.get('id', 'N/A')
            
            print_info(f"Analyzing: {title}")
            
            issues = []
            
            # Check for hardcoded font sizes that might cause pixelation
            hardcoded_fonts = re.findall(r'style=["\'][^"\']*font-size:\s*([0-9]+)px', content)
            if hardcoded_fonts:
                issues.append(f"Hardcoded font sizes found: {hardcoded_fonts}")
                print_error(f"  - ISSUE: Hardcoded font sizes: {hardcoded_fonts}")
            
            # Check for missing language specifications
            code_blocks_without_lang = re.findall(r'<pre(?![^>]*class=["\'][^"\']*language-)[^>]*>', content)
            if code_blocks_without_lang:
                issues.append(f"Code blocks without language specification: {len(code_blocks_without_lang)}")
                print_error(f"  - ISSUE: {len(code_blocks_without_lang)} code blocks missing language specification")
            
            # Check for inline styles that might affect rendering
            inline_styles = re.findall(r'style=["\'][^"\']*["\']', content)
            problematic_styles = [style for style in inline_styles if any(prop in style for prop in ['font-family', 'font-size', 'line-height'])]
            if problematic_styles:
                issues.append(f"Problematic inline styles: {len(problematic_styles)}")
                print_error(f"  - ISSUE: {len(problematic_styles)} problematic inline styles found")
            
            # Check for proper monospace font usage in code
            code_with_fonts = re.findall(r'<code[^>]*style=[^>]*font-family[^>]*>', content)
            pre_with_fonts = re.findall(r'<pre[^>]*style=[^>]*font-family[^>]*>', content)
            
            if code_with_fonts or pre_with_fonts:
                font_usage = len(code_with_fonts) + len(pre_with_fonts)
                print_info(f"  - Code elements with font specifications: {font_usage}")
            
            # Check for copy-to-clipboard functionality
            copy_buttons = re.findall(r'copy|clipboard', content, re.IGNORECASE)
            if copy_buttons:
                print_success(f"  - Copy functionality indicators found: {len(copy_buttons)}")
            else:
                print_info(f"  - No copy functionality indicators found")
            
            if issues:
                quality_issues.append({
                    'title': title,
                    'article_id': article_id,
                    'issues': issues
                })
            else:
                print_success(f"  - OK: Code quality appears good")
        
        # Summary
        if quality_issues:
            print_error(f"CODE QUALITY ISSUE DETECTED: {len(quality_issues)} articles have code quality problems")
            return False, quality_issues
        else:
            print_success("CODE QUALITY: All articles have good code quality")
            return True, []
            
    except Exception as e:
        print_error(f"Error analyzing code quality: {e}")
        return False, []

async def test_v2_processing_diagnostics():
    """Test 7: Check V2 Processing Diagnostics"""
    print_test_header("Test 7: V2 Processing Diagnostics")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking V2 processing diagnostics...")
            
            # Check various V2 processing endpoints
            diagnostics_endpoints = [
                ('Style Processing', '/api/style/diagnostics'),
                ('Code Normalization', '/api/code-normalization/diagnostics'),
                ('Evidence Tagging', '/api/evidence-tagging/diagnostics'),
                ('Gap Filling', '/api/gap-filling/diagnostics'),
                ('Related Links', '/api/related-links/diagnostics'),
                ('Publishing', '/api/publishing/diagnostics')
            ]
            
            diagnostics_results = {}
            
            for name, endpoint in diagnostics_endpoints:
                try:
                    async with session.get(f"{BACKEND_URL}{endpoint}") as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            total_runs = data.get('total_runs', 0)
                            success_rate = data.get('success_rate', 0)
                            system_status = data.get('system_status', 'unknown')
                            
                            print_success(f"{name}: {total_runs} runs, {success_rate}% success, status: {system_status}")
                            diagnostics_results[name] = {
                                'status': 'active' if total_runs > 0 else 'inactive',
                                'runs': total_runs,
                                'success_rate': success_rate
                            }
                        else:
                            print_error(f"{name}: Endpoint unavailable (Status: {response.status})")
                            diagnostics_results[name] = {'status': 'unavailable'}
                            
                except Exception as e:
                    print_error(f"{name}: Error - {e}")
                    diagnostics_results[name] = {'status': 'error'}
            
            # Calculate overall V2 system health
            active_systems = sum(1 for result in diagnostics_results.values() if result.get('status') == 'active')
            total_systems = len(diagnostics_results)
            
            print_info(f"V2 System Health: {active_systems}/{total_systems} systems active")
            
            return active_systems >= total_systems // 2, diagnostics_results
            
    except Exception as e:
        print_error(f"Error checking V2 diagnostics: {e}")
        return False, {}

async def run_v2_content_analysis():
    """Run comprehensive V2 content analysis test suite"""
    print_test_header("V2 Engine Content Analysis - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Analyzing existing Google Maps API articles for specific content issues")
    
    # Test results tracking
    test_results = []
    
    # Test 1: Get Google Maps articles
    articles = await get_google_maps_articles()
    test_results.append(("Article Retrieval", len(articles) > 0))
    
    if not articles:
        print_error("No Google Maps articles found - cannot proceed with analysis")
        return False
    
    # Test 2: Analyze H1 tags issue
    success, h1_issues = await analyze_h1_tags_issue(articles)
    test_results.append(("H1 Tags Analysis", success))
    
    # Test 3: Analyze Mini-TOC issue
    success, toc_issues = await analyze_mini_toc_issue(articles)
    test_results.append(("Mini-TOC Analysis", success))
    
    # Test 4: Analyze list type issue
    success, list_issues = await analyze_list_type_issue(articles)
    test_results.append(("List Type Analysis", success))
    
    # Test 5: Analyze code rendering issue
    success, code_rendering_issues = await analyze_code_rendering_issue(articles)
    test_results.append(("Code Rendering Analysis", success))
    
    # Test 6: Analyze code quality issue
    success, code_quality_issues = await analyze_code_quality_issue(articles)
    test_results.append(("Code Quality Analysis", success))
    
    # Test 7: Check V2 processing diagnostics
    success, diagnostics = await test_v2_processing_diagnostics()
    test_results.append(("V2 Processing Diagnostics", success))
    
    # Final Results Summary
    print_test_header("Content Analysis Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Detailed Issue Summary
    print_test_header("Specific Issues Identified")
    
    all_issues = []
    
    if 'h1_issues' in locals() and h1_issues:
        all_issues.extend([f"Multiple H1 tags in {issue['title']}" for issue in h1_issues])
        print_error(f"H1 TAGS: {len(h1_issues)} articles with multiple H1 tags")
    
    if 'toc_issues' in locals() and toc_issues:
        all_issues.extend([f"Static Mini-TOC in {issue['title']}" for issue in toc_issues])
        print_error(f"MINI-TOC: {len(toc_issues)} articles with static Mini-TOC")
    
    if 'list_issues' in locals() and list_issues:
        all_issues.extend([f"List type issues in {issue['title']}" for issue in list_issues])
        print_error(f"LIST TYPES: {len(list_issues)} articles with incorrect list detection")
    
    if 'code_rendering_issues' in locals() and code_rendering_issues:
        all_issues.extend([f"Code rendering problems in {issue['title']}" for issue in code_rendering_issues])
        print_error(f"CODE RENDERING: {len(code_rendering_issues)} articles with code rendering problems")
    
    if 'code_quality_issues' in locals() and code_quality_issues:
        all_issues.extend([f"Code quality issues in {issue['title']}" for issue in code_quality_issues])
        print_error(f"CODE QUALITY: {len(code_quality_issues)} articles with code quality problems")
    
    if not all_issues:
        print_success("🎉 NO CRITICAL ISSUES FOUND - All articles appear to be properly formatted!")
    
    # Overall assessment
    if success_rate >= 80:
        print_success(f"🎉 V2 CONTENT ANALYSIS COMPLETED SUCCESSFULLY - {success_rate:.1f}% SUCCESS RATE")
        print_success("V2 Engine has successfully processed Google Maps API content!")
        if all_issues:
            print_info(f"Minor issues identified: {len(all_issues)} items for potential improvement")
    elif success_rate >= 60:
        print_info(f"⚠️ V2 CONTENT ANALYSIS PARTIALLY SUCCESSFUL - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some content processing is working well, but improvements needed.")
    else:
        print_error(f"❌ V2 CONTENT ANALYSIS FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant content issues detected.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting V2 Engine Content Analysis Test Suite...")
    
    try:
        # Run the V2 content analysis
        success = asyncio.run(run_v2_content_analysis())
        
        if success:
            print("\n🎯 V2 ENGINE CONTENT ANALYSIS COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 ENGINE CONTENT ANALYSIS COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)