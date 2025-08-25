#!/usr/bin/env python3
"""
V2 Content Analysis Test
Analyze the generated Google Maps API content for the 5 specific issues
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

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

async def get_google_maps_articles():
    """Get Google Maps API articles from content library"""
    print_test_header("Content Library Analysis")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Fetching articles from content library...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    print_success(f"Content library accessible - {len(articles)} total articles")
                    
                    # Look for Google Maps API related articles
                    google_maps_articles = []
                    for article in articles:
                        title = article.get('title', '').lower()
                        content = str(article.get('content', '')).lower()
                        
                        # Check for Google Maps API keywords
                        if any(keyword in title or keyword in content for keyword in [
                            'google map', 'javascript api', 'maps api', 'google maps'
                        ]):
                            google_maps_articles.append(article)
                    
                    if google_maps_articles:
                        print_success(f"Found {len(google_maps_articles)} Google Maps API related articles")
                        
                        # Show article details
                        for i, article in enumerate(google_maps_articles):
                            title = article.get('title', 'Untitled')
                            article_id = article.get('id', 'No ID')
                            created_at = article.get('created_at', 'Unknown')
                            content_length = len(str(article.get('content', '')))
                            print_info(f"  {i+1}. {title}")
                            print_info(f"     ID: {article_id}")
                            print_info(f"     Content length: {content_length} chars")
                            print_info(f"     Created: {created_at}")
                        
                        return google_maps_articles
                    else:
                        print_warning("No Google Maps API related articles found")
                        
                        # Show recent articles for debugging
                        print_info("Recent articles (last 10):")
                        for article in articles[-10:]:
                            title = article.get('title', 'Untitled')
                            created_at = article.get('created_at', 'Unknown')
                            print_info(f"  - {title} ({created_at})")
                        
                        return []
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return []
                    
    except Exception as e:
        print_error(f"Error fetching articles: {e}")
        return []

def analyze_h1_duplication(content):
    """Analyze H1 duplication in content body"""
    print_info("🔍 Issue 1: H1 duplication in content body")
    
    # Find all H1 elements
    h1_elements = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    h1_count = len(h1_elements)
    
    print_info(f"   Found {h1_count} H1 elements")
    
    if h1_elements:
        for i, h1_text in enumerate(h1_elements[:3]):  # Show first 3
            clean_text = re.sub(r'<[^>]+>', '', h1_text).strip()
            print_info(f"   H1 {i+1}: {clean_text[:60]}...")
    
    # Check for duplicate H1s (same text content)
    h1_texts = [re.sub(r'<[^>]+>', '', h1).strip().lower() for h1 in h1_elements]
    unique_h1s = set(h1_texts)
    has_duplicates = len(h1_texts) != len(unique_h1s)
    
    # Ideal: Only 1 H1 (article title), or no H1s in content body
    resolved = h1_count <= 1
    
    if resolved:
        print_success(f"   ✅ H1 duplication RESOLVED - {h1_count} H1 elements (acceptable)")
    else:
        print_error(f"   ❌ H1 duplication PRESENT - {h1_count} H1 elements (should be ≤1)")
        if has_duplicates:
            print_error(f"   ❌ Duplicate H1 content detected")
    
    return {
        'resolved': resolved,
        'h1_count': h1_count,
        'has_duplicates': has_duplicates,
        'issue_description': f"{h1_count} H1 elements found (should be ≤1)"
    }

def analyze_mini_toc_links(content):
    """Analyze Mini-TOC linking functionality"""
    print_info("🔍 Issue 2: Static Mini-TOC lists (not clickable)")
    
    # Look for TOC anchor links
    anchor_links = re.findall(r'<a href="#[^"]+">([^<]+)</a>', content)
    markdown_links = re.findall(r'\[([^\]]+)\]\(#[^)]+\)', content)
    
    total_clickable_links = len(anchor_links) + len(markdown_links)
    
    # Look for static list items that might be TOC
    list_items = re.findall(r'<li[^>]*>([^<]+)</li>', content)
    static_items = len([item for item in list_items if '<a' not in item and '[' not in item])
    
    print_info(f"   Clickable TOC links (HTML): {len(anchor_links)}")
    print_info(f"   Clickable TOC links (Markdown): {len(markdown_links)}")
    print_info(f"   Total clickable links: {total_clickable_links}")
    print_info(f"   Static list items: {static_items}")
    
    if anchor_links:
        print_info(f"   Sample HTML links:")
        for link in anchor_links[:3]:
            print_info(f"     - {link}")
    
    if markdown_links:
        print_info(f"   Sample Markdown links:")
        for link in markdown_links[:3]:
            print_info(f"     - {link}")
    
    # Resolved if we have clickable links
    resolved = total_clickable_links > 0
    
    if resolved:
        print_success(f"   ✅ Mini-TOC linking RESOLVED - {total_clickable_links} clickable links")
    else:
        print_error(f"   ❌ Mini-TOC linking BROKEN - No clickable links found")
    
    return {
        'resolved': resolved,
        'clickable_links': total_clickable_links,
        'static_items': static_items,
        'issue_description': f"{total_clickable_links} clickable links, {static_items} static items"
    }

def analyze_list_types(content):
    """Analyze list types (UL vs OL for procedural steps)"""
    print_info("🔍 Issue 3: Incorrect list types (UL instead of OL for procedural steps)")
    
    # Count UL and OL elements
    ul_count = len(re.findall(r'<ul[^>]*>', content, re.IGNORECASE))
    ol_count = len(re.findall(r'<ol[^>]*>', content, re.IGNORECASE))
    
    print_info(f"   Unordered lists (UL): {ul_count}")
    print_info(f"   Ordered lists (OL): {ol_count}")
    
    # Look for procedural content indicators
    procedural_indicators = [
        r'step\s+\d+', r'first[,\s]', r'second[,\s]', r'third[,\s]',
        r'then[,\s]', r'next[,\s]', r'finally[,\s]', r'\d+\.\s',
        r'authenticate.*api.*key', r'create.*html.*page', r'add.*map.*marker'
    ]
    
    procedural_content_found = 0
    for indicator in procedural_indicators:
        matches = re.findall(indicator, content, re.IGNORECASE)
        procedural_content_found += len(matches)
    
    print_info(f"   Procedural content indicators: {procedural_content_found}")
    
    # Check if procedural content is in UL (should be OL)
    ul_sections = re.findall(r'<ul[^>]*>(.*?)</ul>', content, re.IGNORECASE | re.DOTALL)
    procedural_in_ul = 0
    
    for ul_section in ul_sections:
        for indicator in procedural_indicators:
            if re.search(indicator, ul_section, re.IGNORECASE):
                procedural_in_ul += 1
                break
    
    print_info(f"   Procedural content in UL (should be OL): {procedural_in_ul}")
    
    # Resolved if we have OL lists or minimal procedural content in UL
    resolved = ol_count > 0 or procedural_in_ul == 0
    
    if resolved:
        print_success(f"   ✅ List types RESOLVED - {ol_count} OL lists, {procedural_in_ul} procedural UL")
    else:
        print_error(f"   ❌ List types INCORRECT - {procedural_in_ul} procedural content in UL (should be OL)")
    
    return {
        'resolved': resolved,
        'ul_count': ul_count,
        'ol_count': ol_count,
        'procedural_in_ul': procedural_in_ul,
        'issue_description': f"{ul_count} UL, {ol_count} OL, {procedural_in_ul} procedural in UL"
    }

def analyze_code_blocks(content):
    """Analyze code block fragmentation"""
    print_info("🔍 Issue 4: Fragmented code blocks (each line separate)")
    
    # Find code blocks
    code_patterns = [
        r'<pre[^>]*><code[^>]*>(.*?)</code></pre>',
        r'<code[^>]*>(.*?)</code>',
        r'<pre[^>]*>(.*?)</pre>',
        r'```[^`]*```'
    ]
    
    code_blocks = []
    for pattern in code_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        code_blocks.extend(matches)
    
    print_info(f"   Found {len(code_blocks)} code blocks")
    
    # Analyze code block structure
    fragmented_blocks = 0
    consolidated_blocks = 0
    single_line_blocks = 0
    multi_line_blocks = 0
    
    for code_block in code_blocks:
        # Clean code content
        clean_code = re.sub(r'<[^>]+>', '', code_block).strip()
        lines = [line.strip() for line in clean_code.split('\n') if line.strip()]
        
        if len(lines) == 1:
            single_line_blocks += 1
            # Check if it looks like it should be part of a larger block
            if any(indicator in clean_code for indicator in ['function', 'var ', 'const ', '{', '}', ';']):
                fragmented_blocks += 1
        else:
            multi_line_blocks += 1
            consolidated_blocks += 1
    
    print_info(f"   Single-line code blocks: {single_line_blocks}")
    print_info(f"   Multi-line code blocks: {multi_line_blocks}")
    print_info(f"   Potentially fragmented blocks: {fragmented_blocks}")
    print_info(f"   Consolidated blocks: {consolidated_blocks}")
    
    # Show sample code blocks
    if code_blocks:
        print_info(f"   Sample code blocks:")
        for i, block in enumerate(code_blocks[:2]):
            clean_code = re.sub(r'<[^>]+>', '', block).strip()
            preview = clean_code[:100].replace('\n', '\\n')
            print_info(f"     Block {i+1}: {preview}...")
    
    # Resolved if we have more consolidated than fragmented blocks
    resolved = consolidated_blocks >= fragmented_blocks or fragmented_blocks == 0
    
    if resolved:
        print_success(f"   ✅ Code blocks RESOLVED - {consolidated_blocks} consolidated, {fragmented_blocks} fragmented")
    else:
        print_error(f"   ❌ Code blocks FRAGMENTED - {fragmented_blocks} fragmented blocks")
    
    return {
        'resolved': resolved,
        'total_blocks': len(code_blocks),
        'fragmented_blocks': fragmented_blocks,
        'consolidated_blocks': consolidated_blocks,
        'issue_description': f"{len(code_blocks)} total, {fragmented_blocks} fragmented, {consolidated_blocks} consolidated"
    }

def analyze_code_quality(content):
    """Analyze code quality issues"""
    print_info("🔍 Issue 5: Code quality issues")
    
    # Find code blocks for quality analysis
    code_patterns = [
        r'<pre[^>]*><code[^>]*>(.*?)</code></pre>',
        r'<code[^>]*>(.*?)</code>',
        r'<pre[^>]*>(.*?)</pre>'
    ]
    
    code_blocks = []
    for pattern in code_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        code_blocks.extend(matches)
    
    print_info(f"   Analyzing {len(code_blocks)} code blocks for quality")
    
    # Quality indicators
    quality_issues = 0
    quality_good = 0
    
    # Check for copy buttons
    copy_buttons = len(re.findall(r'copy[^>]*button|button[^>]*copy', content, re.IGNORECASE))
    print_info(f"   Copy buttons found: {copy_buttons}")
    
    # Check for syntax highlighting
    syntax_highlighting = len(re.findall(r'class="[^"]*highlight|class="[^"]*syntax|class="[^"]*language', content, re.IGNORECASE))
    print_info(f"   Syntax highlighting indicators: {syntax_highlighting}")
    
    # Check for proper code formatting
    for code_block in code_blocks:
        clean_code = re.sub(r'<[^>]+>', '', code_block).strip()
        
        # Quality checks
        has_proper_indentation = '  ' in clean_code or '\t' in clean_code
        has_proper_structure = any(char in clean_code for char in ['{', '}', '(', ')', ';'])
        is_readable = len(clean_code) > 10 and not clean_code.isdigit()
        
        if has_proper_indentation and has_proper_structure and is_readable:
            quality_good += 1
        else:
            quality_issues += 1
    
    print_info(f"   Good quality code blocks: {quality_good}")
    print_info(f"   Code blocks with issues: {quality_issues}")
    
    # Check for visual distortion indicators
    visual_issues = len(re.findall(r'pixelat|distort|blur|corrupt', content, re.IGNORECASE))
    print_info(f"   Visual distortion indicators: {visual_issues}")
    
    # Resolved if we have good quality indicators and minimal issues
    resolved = (quality_good >= quality_issues and visual_issues == 0)
    
    if resolved:
        print_success(f"   ✅ Code quality GOOD - {quality_good} good blocks, {copy_buttons} copy buttons")
    else:
        print_error(f"   ❌ Code quality ISSUES - {quality_issues} problematic blocks, {visual_issues} visual issues")
    
    return {
        'resolved': resolved,
        'total_blocks': len(code_blocks),
        'quality_good': quality_good,
        'quality_issues': quality_issues,
        'copy_buttons': copy_buttons,
        'visual_issues': visual_issues,
        'issue_description': f"{len(code_blocks)} total, {quality_good} good, {quality_issues} issues"
    }

async def analyze_content_issues(articles):
    """Analyze all content issues for the articles"""
    print_test_header("Content Issues Analysis")
    
    if not articles:
        print_error("No articles provided for analysis")
        return False, {}
    
    print_info(f"Analyzing {len(articles)} articles for content issues...")
    
    # Select the most relevant article for analysis
    target_article = None
    for article in articles:
        title = article.get('title', '').lower()
        # Look for the most comprehensive article
        if any(keyword in title for keyword in ['building', 'basic', 'complete', 'tutorial', 'guide']):
            target_article = article
            break
    
    if not target_article:
        # Fallback to first article
        target_article = articles[0]
    
    print_info(f"Analyzing article: '{target_article.get('title', 'Untitled')}'")
    
    content = target_article.get('content', target_article.get('html', ''))
    if not content:
        print_error("Article content is empty")
        return False, {}
    
    print_info(f"Content length: {len(content)} characters")
    
    # Analyze all 5 issues
    issue1_result = analyze_h1_duplication(content)
    issue2_result = analyze_mini_toc_links(content)
    issue3_result = analyze_list_types(content)
    issue4_result = analyze_code_blocks(content)
    issue5_result = analyze_code_quality(content)
    
    # Compile results
    analysis_results = {
        'h1_duplication': issue1_result,
        'mini_toc_links': issue2_result,
        'list_types': issue3_result,
        'code_blocks': issue4_result,
        'code_quality': issue5_result,
        'article_title': target_article.get('title', 'Untitled'),
        'article_id': target_article.get('id', 'No ID'),
        'content_length': len(content)
    }
    
    # Calculate overall success rate
    issues_resolved = sum(1 for result in [issue1_result, issue2_result, issue3_result, issue4_result, issue5_result] 
                         if result.get('resolved', False))
    total_issues = 5
    success_rate = (issues_resolved / total_issues) * 100
    
    print_test_header("Content Issues Summary")
    print_info(f"Article: {target_article.get('title', 'Untitled')}")
    print_info(f"Content length: {len(content)} characters")
    print_info(f"Issues resolved: {issues_resolved}/{total_issues}")
    print_info(f"Success rate: {success_rate:.1f}%")
    
    # Detailed issue breakdown
    issues = [
        ("H1 Duplication", issue1_result),
        ("Mini-TOC Links", issue2_result),
        ("List Types", issue3_result),
        ("Code Blocks", issue4_result),
        ("Code Quality", issue5_result)
    ]
    
    for issue_name, result in issues:
        status = "✅ RESOLVED" if result.get('resolved', False) else "❌ PRESENT"
        description = result.get('issue_description', 'No details')
        print_info(f"{status} - {issue_name}: {description}")
    
    return success_rate >= 60, analysis_results

async def run_content_analysis():
    """Run the content analysis"""
    print_test_header("V2 Generated Content Analysis")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Analyzing V2 generated Google Maps API content for 5 specific issues")
    
    # Get articles
    articles = await get_google_maps_articles()
    
    if not articles:
        print_error("No Google Maps API articles found - cannot analyze content")
        return False
    
    # Analyze content issues
    success, analysis_results = await analyze_content_issues(articles)
    
    # Final assessment
    if success:
        print_success("🎉 CONTENT ANALYSIS COMPLETED - ACCEPTABLE RESULTS")
        print_success("Most critical content issues have been resolved by V2 processing")
    else:
        print_warning("⚠️ CONTENT ANALYSIS COMPLETED - ISSUES REMAIN")
        print_warning("Some content issues still need attention")
    
    return success

if __name__ == "__main__":
    print("🚀 Starting V2 Content Analysis...")
    
    try:
        success = asyncio.run(run_content_analysis())
        
        if success:
            print("\n🎯 V2 CONTENT ANALYSIS COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 CONTENT ANALYSIS COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        sys.exit(1)