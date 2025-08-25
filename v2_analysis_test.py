#!/usr/bin/env python3
"""
V2 Engine Post-Processing Analysis Test
Analyze existing content to verify the three critical fixes are working
"""

import requests
import json
import re
import sys

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

def analyze_comprehensive_post_processing(content, title):
    """Analyze content for the three critical V2 post-processing fixes"""
    print_info(f"Analyzing '{title}' for V2 post-processing fixes...")
    
    # Fix 1: Mini-TOC Links - ID coordination between LLM generation and style processor
    print_info("=== Fix 1: Mini-TOC Links Analysis ===")
    
    # Check H1 to H2 conversion
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    h2_matches = re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.IGNORECASE | re.DOTALL)
    
    print_info(f"H1 elements found: {len(h1_matches)}")
    print_info(f"H2 elements found: {len(h2_matches)}")
    
    # Check for TOC links (both markdown and HTML style)
    markdown_toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
    html_toc_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', content)
    
    print_info(f"Markdown TOC links: {len(markdown_toc_links)}")
    print_info(f"HTML TOC links: {len(html_toc_links)}")
    
    # Check for heading IDs
    heading_ids = re.findall(r'<h[2-6][^>]*id="([^"]+)"', content)
    print_info(f"Heading IDs found: {len(heading_ids)} - {heading_ids[:5]}")
    
    # Verify TOC links point to existing headings
    all_toc_links = [(text, anchor) for text, anchor in markdown_toc_links] + [(text, anchor) for anchor, text in html_toc_links]
    valid_toc_links = 0
    for text, anchor in all_toc_links:
        if anchor in heading_ids:
            valid_toc_links += 1
            print_info(f"  Valid TOC link: '{text}' -> #{anchor}")
    
    # Mini-TOC fix success criteria
    mini_toc_success = (
        len(h1_matches) <= 1 and  # H1 to H2 conversion working
        len(h2_matches) >= 2 and  # Multiple H2 headings
        len(all_toc_links) >= 2 and  # TOC links present
        valid_toc_links >= 1  # At least some valid links
    )
    
    print_info(f"Mini-TOC Links Fix: {'✅ PASS' if mini_toc_success else '❌ FAIL'}")
    
    # Fix 2: List Types - Enhanced procedural list detection (UL to OL conversion)
    print_info("=== Fix 2: List Types Analysis ===")
    
    ul_count = len(re.findall(r'<ul[^>]*>', content))
    ol_count = len(re.findall(r'<ol[^>]*>', content))
    
    print_info(f"Unordered lists (UL): {ul_count}")
    print_info(f"Ordered lists (OL): {ol_count}")
    
    # Check for procedural content indicators
    procedural_patterns = [
        (r'step\s+\d+', 'step numbers'),
        (r'first[,\s]', 'first'),
        (r'next[,\s]', 'next'),
        (r'then[,\s]', 'then'),
        (r'finally[,\s]', 'finally'),
        (r'^\s*-\s+step', 'step bullets'),
        (r'^\s*\d+\.', 'numbered items')
    ]
    
    total_procedural_indicators = 0
    for pattern, name in procedural_patterns:
        matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
        if matches > 0:
            print_info(f"  {name}: {matches} occurrences")
            total_procedural_indicators += matches
    
    print_info(f"Total procedural indicators: {total_procedural_indicators}")
    
    # List types fix success criteria
    if total_procedural_indicators >= 3:
        list_types_success = ol_count >= 1  # Should have converted some UL to OL
        print_info(f"Expected OL conversion due to procedural content: {'✅ PASS' if list_types_success else '❌ FAIL'}")
    else:
        list_types_success = (ul_count + ol_count) >= 1  # At least some lists
        print_info(f"General list formatting: {'✅ PASS' if list_types_success else '❌ FAIL'}")
    
    # Fix 3: Code Consolidation - Improved code block consolidation and rendering
    print_info("=== Fix 3: Code Consolidation Analysis ===")
    
    # Count different types of code elements
    pre_blocks = re.findall(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
    code_blocks = re.findall(r'<code[^>]*>(.*?)</code>', content, re.DOTALL)
    
    print_info(f"<pre> blocks: {len(pre_blocks)}")
    print_info(f"<code> elements: {len(code_blocks)}")
    
    # Check for well-formed code blocks
    well_formed_blocks = 0
    for block in pre_blocks:
        if '<code>' in block and len(block.strip()) > 10:
            well_formed_blocks += 1
    
    print_info(f"Well-formed code blocks: {well_formed_blocks}/{len(pre_blocks)}")
    
    # Check for consolidation issues (adjacent empty blocks, etc.)
    consolidation_issues = len(re.findall(r'<pre[^>]*>\s*</pre>', content))  # Empty blocks
    print_info(f"Empty code blocks (consolidation issues): {consolidation_issues}")
    
    # Code consolidation success criteria
    if len(pre_blocks) >= 1:
        code_consolidation_success = well_formed_blocks >= 1 and consolidation_issues == 0
    else:
        code_consolidation_success = True  # No code to consolidate
    
    print_info(f"Code Consolidation Fix: {'✅ PASS' if code_consolidation_success else '❌ FAIL'}")
    
    # Overall assessment
    fixes_passed = sum([mini_toc_success, list_types_success, code_consolidation_success])
    success_rate = (fixes_passed / 3) * 100
    
    print_info(f"=== Overall V2 Post-Processing Assessment ===")
    print_info(f"Fixes passed: {fixes_passed}/3 ({success_rate:.1f}%)")
    
    return {
        'mini_toc_links': mini_toc_success,
        'list_types': list_types_success,
        'code_consolidation': code_consolidation_success,
        'success_rate': success_rate
    }

def test_content_library_analysis():
    """Analyze all articles in content library for V2 post-processing"""
    print_test_header("V2 Post-Processing Content Library Analysis")
    
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', []) if isinstance(data, dict) else data
            print_success(f"Content library accessible - {len(articles)} articles found")
            
            if not articles:
                print_error("No articles found to analyze")
                return False
            
            # Analyze each article
            analysis_results = []
            
            for i, article in enumerate(articles[:5]):  # Analyze first 5 articles
                if not isinstance(article, dict):
                    continue
                    
                title = article.get('title', f'Article {i+1}')
                content = article.get('content', article.get('html', ''))
                
                if not content:
                    print_info(f"Skipping '{title}' - no content")
                    continue
                
                print_info(f"\n--- Analyzing Article {i+1}: '{title}' ---")
                print_info(f"Content length: {len(content)} characters")
                
                result = analyze_comprehensive_post_processing(content, title)
                result['title'] = title
                analysis_results.append(result)
            
            # Summary of all analyses
            print_test_header("V2 Post-Processing Analysis Summary")
            
            if analysis_results:
                total_articles = len(analysis_results)
                mini_toc_passes = sum(1 for r in analysis_results if r['mini_toc_links'])
                list_type_passes = sum(1 for r in analysis_results if r['list_types'])
                code_consolidation_passes = sum(1 for r in analysis_results if r['code_consolidation'])
                
                avg_success_rate = sum(r['success_rate'] for r in analysis_results) / total_articles
                
                print_info(f"Articles analyzed: {total_articles}")
                print_info(f"Mini-TOC Links fixes: {mini_toc_passes}/{total_articles} ({mini_toc_passes/total_articles*100:.1f}%)")
                print_info(f"List Types fixes: {list_type_passes}/{total_articles} ({list_type_passes/total_articles*100:.1f}%)")
                print_info(f"Code Consolidation fixes: {code_consolidation_passes}/{total_articles} ({code_consolidation_passes/total_articles*100:.1f}%)")
                print_info(f"Average success rate: {avg_success_rate:.1f}%")
                
                # Overall assessment
                if avg_success_rate >= 75:
                    print_success(f"🎉 V2 POST-PROCESSING FIXES WORKING WELL - {avg_success_rate:.1f}% average success")
                    return True
                elif avg_success_rate >= 50:
                    print_info(f"⚠️ V2 POST-PROCESSING PARTIALLY WORKING - {avg_success_rate:.1f}% average success")
                    return True
                else:
                    print_error(f"❌ V2 POST-PROCESSING NEEDS IMPROVEMENT - {avg_success_rate:.1f}% average success")
                    return False
            else:
                print_error("No articles could be analyzed")
                return False
                
        else:
            print_error(f"Content library access failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error analyzing content library: {e}")
        return False

def test_style_processor_status():
    """Check style processor integration with V2 engine"""
    print_test_header("Style Processor V2 Integration Check")
    
    try:
        response = requests.get(f"{API_BASE}/style/diagnostics", timeout=10)
        
        if response.status_code == 200:
            diagnostics = response.json()
            print_success("Style diagnostics accessible")
            
            engine = diagnostics.get('engine', 'unknown')
            system_status = diagnostics.get('system_status', 'unknown')
            recent_results = diagnostics.get('recent_results', [])
            
            print_info(f"Style processor engine: {engine}")
            print_info(f"System status: {system_status}")
            print_info(f"Recent processing results: {len(recent_results)}")
            
            # Look for post-processing indicators in recent results
            post_processing_indicators = 0
            for result in recent_results:
                result_str = str(result)
                if any(indicator in result_str.lower() for indicator in [
                    'comprehensive_post_processing', 'mini_toc', 'list_type', 'code_consolidation',
                    'anchor_links', 'toc_broken_links', 'structural_changes'
                ]):
                    post_processing_indicators += 1
            
            print_info(f"Results with post-processing indicators: {post_processing_indicators}/{len(recent_results)}")
            
            success = engine == 'v2' and (system_status == 'active' or len(recent_results) > 0)
            
            if success:
                print_success("Style processor V2 integration confirmed")
            else:
                print_info("Style processor status unclear but accessible")
            
            return success
            
        else:
            print_error(f"Style diagnostics failed - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error checking style processor: {e}")
        return False

def run_v2_analysis_test():
    """Run comprehensive V2 post-processing analysis"""
    print_test_header("V2 Engine Post-Processing Comprehensive Analysis")
    print_info("Analyzing existing content for the three critical fixes:")
    print_info("1. Mini-TOC Links: ID coordination between LLM and style processor")
    print_info("2. List Types: Enhanced procedural list detection (UL to OL)")
    print_info("3. Code Consolidation: Improved code block consolidation")
    
    test_results = []
    
    # Test 1: Content Library Analysis
    success = test_content_library_analysis()
    test_results.append(("Content Analysis", success))
    
    # Test 2: Style Processor Status
    success = test_style_processor_status()
    test_results.append(("Style Processor", success))
    
    # Final Results
    print_test_header("Final Test Results")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    return success_rate >= 50

if __name__ == "__main__":
    print("🚀 Starting V2 Engine Post-Processing Analysis...")
    
    try:
        success = run_v2_analysis_test()
        
        if success:
            print("\n🎯 V2 POST-PROCESSING ANALYSIS COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 POST-PROCESSING ANALYSIS COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        sys.exit(1)