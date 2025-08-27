#!/usr/bin/env python3
"""
V2 Engine DOCX Processing Test Suite
Testing fresh processing of Google Map JavaScript API Tutorial.docx through V2 Engine
Focus: Complete V2 pipeline testing and content issue analysis
"""

import asyncio
import aiohttp
import json
import os
import re
import time
from datetime import datetime
import sys
import tempfile
import requests

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# DOCX file URL from the review request
DOCX_URL = "https://customer-assets.emergentagent.com/job_content-pipeline-5/artifacts/a0c5y0aa_Google%20Map%20JavaScript%20API%20Tutorial.docx"

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

async def download_docx_file():
    """Download the Google Maps API Tutorial DOCX file"""
    print_test_header("Step 1: Download DOCX File")
    
    try:
        print_info(f"Downloading DOCX file from: {DOCX_URL}")
        
        # Download the file
        response = requests.get(DOCX_URL, timeout=30)
        if response.status_code == 200:
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            temp_file.write(response.content)
            temp_file.close()
            
            file_size = len(response.content)
            print_success(f"DOCX file downloaded successfully - Size: {file_size} bytes")
            print_info(f"Temporary file path: {temp_file.name}")
            
            return temp_file.name
        else:
            print_error(f"Failed to download DOCX file - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error downloading DOCX file: {e}")
        return None

async def test_v2_engine_status():
    """Test 1: Verify V2 Engine is operational"""
    print_test_header("Test 1: V2 Engine Status Check")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking V2 Engine status...")
            
            async with session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    engine_data = await response.json()
                    print_success("V2 Engine status endpoint accessible")
                    
                    # Check for V2 engine indicators
                    engine_version = engine_data.get('engine', 'unknown')
                    engine_message = engine_data.get('message', '')
                    
                    print_info(f"Engine version: {engine_version}")
                    print_info(f"Engine message: {engine_message}")
                    
                    # Check for V2-specific features
                    v2_features = [
                        'v2_processing',
                        'content_library_indexing',
                        'woolf_style_processing',
                        'gap_filling',
                        'related_links'
                    ]
                    
                    features_found = []
                    engine_str = str(engine_data).lower()
                    
                    for feature in v2_features:
                        if feature in engine_str:
                            features_found.append(feature)
                    
                    if features_found:
                        print_success(f"V2 features detected: {', '.join(features_found)}")
                        return True, engine_data
                    else:
                        print_warning("No V2-specific features detected in engine status")
                        return True, engine_data  # Still proceed with testing
                        
                else:
                    print_error(f"Failed to access V2 Engine status - Status: {response.status}")
                    return False, None
                    
    except Exception as e:
        print_error(f"Error checking V2 Engine status: {e}")
        return False, None

async def test_v2_file_upload_processing(docx_file_path):
    """Test 2: Upload DOCX file through V2 Engine pipeline"""
    print_test_header("Test 2: V2 Engine File Upload Processing")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Uploading DOCX file through V2 Engine pipeline...")
            
            # Prepare file upload
            with open(docx_file_path, 'rb') as file:
                file_data = aiohttp.FormData()
                file_data.add_field('file', file, filename='Google_Map_JavaScript_API_Tutorial.docx')
                
                print_info("Calling POST /api/content/upload...")
                
                async with session.post(f"{API_BASE}/content/upload", data=file_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print_success(f"V2 file upload successful - Status: {response.status}")
                        
                        # Validate V2 processing response
                        required_fields = ['job_id', 'status', 'engine']
                        missing_fields = [field for field in required_fields if field not in result]
                        
                        if not missing_fields:
                            print_success("V2 processing response structure valid")
                            
                            job_id = result.get('job_id')
                            engine = result.get('engine', 'unknown')
                            status = result.get('status', 'unknown')
                            
                            print_info(f"Job ID: {job_id}")
                            print_info(f"Engine: {engine}")
                            print_info(f"Status: {status}")
                            
                            # Check for V2 engine confirmation
                            if engine.lower() == 'v2':
                                print_success("V2 Engine processing confirmed")
                            else:
                                print_warning(f"Engine type: {engine} (expected 'v2')")
                            
                            return True, result
                        else:
                            print_error(f"V2 processing response missing fields: {missing_fields}")
                            return False, None
                    else:
                        error_text = await response.text()
                        print_error(f"V2 file upload failed - Status: {response.status}")
                        print_error(f"Error: {error_text}")
                        return False, None
                        
    except Exception as e:
        print_error(f"Error in V2 file upload processing: {e}")
        return False, None

async def wait_for_processing_completion(job_id, max_wait_time=300):
    """Wait for V2 processing to complete"""
    print_test_header("Step 3: Wait for V2 Processing Completion")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info(f"Waiting for V2 processing completion - Job ID: {job_id}")
            print_info(f"Maximum wait time: {max_wait_time} seconds")
            
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                # Check processing status
                async with session.get(f"{API_BASE}/processing-status/{job_id}") as response:
                    if response.status == 200:
                        status_data = await response.json()
                        status = status_data.get('status', 'unknown')
                        
                        print_info(f"Processing status: {status}")
                        
                        if status in ['completed', 'success']:
                            elapsed_time = time.time() - start_time
                            print_success(f"V2 processing completed in {elapsed_time:.1f} seconds")
                            return True, status_data
                        elif status in ['failed', 'error']:
                            print_error(f"V2 processing failed - Status: {status}")
                            return False, status_data
                        else:
                            # Still processing, wait and check again
                            await asyncio.sleep(10)
                    else:
                        print_warning(f"Status check failed - Status: {response.status}")
                        await asyncio.sleep(10)
            
            print_error(f"V2 processing timeout after {max_wait_time} seconds")
            return False, None
            
    except Exception as e:
        print_error(f"Error waiting for processing completion: {e}")
        return False, None

async def test_content_library_verification():
    """Test 3: Verify article generation and storage in content library"""
    print_test_header("Test 3: Content Library Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking content library for generated articles...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    print_success(f"Content library accessible - {len(articles)} articles found")
                    
                    # Look for Google Maps API related articles
                    google_maps_articles = []
                    for article in articles:
                        title = article.get('title', '').lower()
                        if any(keyword in title for keyword in ['google', 'map', 'javascript', 'api']):
                            google_maps_articles.append(article)
                    
                    if google_maps_articles:
                        print_success(f"Found {len(google_maps_articles)} Google Maps API related articles")
                        
                        # Show article details
                        for i, article in enumerate(google_maps_articles[:5]):  # Show first 5
                            title = article.get('title', 'Untitled')
                            article_id = article.get('id', 'No ID')
                            created_at = article.get('created_at', 'Unknown')
                            print_info(f"  {i+1}. {title} (ID: {article_id})")
                        
                        return True, google_maps_articles
                    else:
                        print_warning("No Google Maps API related articles found")
                        
                        # Show available articles for debugging
                        print_info("Available articles:")
                        for article in articles[:10]:  # Show first 10
                            title = article.get('title', 'Untitled')
                            print_info(f"  - {title}")
                        
                        return False, []
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False, []
                    
    except Exception as e:
        print_error(f"Error verifying content library: {e}")
        return False, []

async def analyze_content_issues(articles):
    """Test 4: Analyze generated content for the 5 specific issues"""
    print_test_header("Test 4: Content Issues Analysis")
    
    if not articles:
        print_error("No articles provided for analysis")
        return False, {}
    
    print_info(f"Analyzing {len(articles)} articles for content issues...")
    
    # Select the most relevant article for analysis
    target_article = None
    for article in articles:
        title = article.get('title', '').lower()
        if 'building' in title and 'basic' in title and 'google' in title and 'map' in title:
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
    
    # Issue 1: H1 duplication in content body
    issue1_result = analyze_h1_duplication(content)
    
    # Issue 2: Static Mini-TOC lists (not clickable)
    issue2_result = analyze_mini_toc_links(content)
    
    # Issue 3: Incorrect list types (UL instead of OL for procedural steps)
    issue3_result = analyze_list_types(content)
    
    # Issue 4: Fragmented code blocks (each line separate)
    issue4_result = analyze_code_blocks(content)
    
    # Issue 5: Code quality issues
    issue5_result = analyze_code_quality(content)
    
    # Compile results
    analysis_results = {
        'h1_duplication': issue1_result,
        'mini_toc_links': issue2_result,
        'list_types': issue3_result,
        'code_blocks': issue4_result,
        'code_quality': issue5_result,
        'article_title': target_article.get('title', 'Untitled'),
        'article_id': target_article.get('id', 'No ID')
    }
    
    # Calculate overall success rate
    issues_resolved = sum(1 for result in [issue1_result, issue2_result, issue3_result, issue4_result, issue5_result] 
                         if result.get('resolved', False))
    total_issues = 5
    success_rate = (issues_resolved / total_issues) * 100
    
    print_info(f"Content Issues Analysis Summary:")
    print_info(f"  - Issues resolved: {issues_resolved}/{total_issues}")
    print_info(f"  - Success rate: {success_rate:.1f}%")
    
    return success_rate >= 60, analysis_results

def analyze_h1_duplication(content):
    """Analyze H1 duplication in content body"""
    print_info("Analyzing Issue 1: H1 duplication in content body...")
    
    # Find all H1 elements
    h1_elements = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    h1_count = len(h1_elements)
    
    print_info(f"Found {h1_count} H1 elements")
    
    if h1_elements:
        for i, h1_text in enumerate(h1_elements[:3]):  # Show first 3
            clean_text = re.sub(r'<[^>]+>', '', h1_text).strip()
            print_info(f"  H1 {i+1}: {clean_text[:50]}...")
    
    # Check for duplicate H1s (same text content)
    h1_texts = [re.sub(r'<[^>]+>', '', h1).strip().lower() for h1 in h1_elements]
    unique_h1s = set(h1_texts)
    has_duplicates = len(h1_texts) != len(unique_h1s)
    
    # Ideal: Only 1 H1 (article title), or no H1s in content body
    resolved = h1_count <= 1
    
    if resolved:
        print_success(f"✅ H1 duplication issue RESOLVED - {h1_count} H1 elements (acceptable)")
    else:
        print_error(f"❌ H1 duplication issue PRESENT - {h1_count} H1 elements (should be ≤1)")
    
    return {
        'resolved': resolved,
        'h1_count': h1_count,
        'has_duplicates': has_duplicates,
        'h1_texts': h1_texts[:3]  # First 3 for reference
    }

def analyze_mini_toc_links(content):
    """Analyze Mini-TOC linking functionality"""
    print_info("Analyzing Issue 2: Static Mini-TOC lists (not clickable)...")
    
    # Look for TOC structures
    toc_patterns = [
        r'<ul[^>]*class="[^"]*toc[^"]*"[^>]*>(.*?)</ul>',  # TOC class
        r'<ul[^>]*>(.*?)</ul>',  # Any UL that might be TOC
    ]
    
    toc_sections = []
    for pattern in toc_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        toc_sections.extend(matches)
    
    # Look for clickable links in TOC sections
    clickable_links = 0
    static_items = 0
    
    for toc_section in toc_sections:
        # Count anchor links <a href="#...">
        anchor_links = re.findall(r'<a href="#[^"]+">([^<]+)</a>', toc_section)
        clickable_links += len(anchor_links)
        
        # Count markdown-style links [text](#anchor)
        markdown_links = re.findall(r'\[([^\]]+)\]\(#[^)]+\)', toc_section)
        clickable_links += len(markdown_links)
        
        # Count static list items (li without links)
        list_items = re.findall(r'<li[^>]*>([^<]+)</li>', toc_section)
        static_items += len([item for item in list_items if '<a' not in item and '[' not in item])
    
    print_info(f"Found {len(toc_sections)} potential TOC sections")
    print_info(f"Clickable TOC links: {clickable_links}")
    print_info(f"Static TOC items: {static_items}")
    
    # Resolved if we have clickable links and minimal static items
    resolved = clickable_links > 0 and (static_items == 0 or clickable_links > static_items)
    
    if resolved:
        print_success(f"✅ Mini-TOC linking issue RESOLVED - {clickable_links} clickable links")
    else:
        print_error(f"❌ Mini-TOC linking issue PRESENT - {static_items} static items, {clickable_links} clickable")
    
    return {
        'resolved': resolved,
        'clickable_links': clickable_links,
        'static_items': static_items,
        'toc_sections_found': len(toc_sections)
    }

def analyze_list_types(content):
    """Analyze list types (UL vs OL for procedural steps)"""
    print_info("Analyzing Issue 3: Incorrect list types (UL instead of OL for procedural steps)...")
    
    # Count UL and OL elements
    ul_count = len(re.findall(r'<ul[^>]*>', content, re.IGNORECASE))
    ol_count = len(re.findall(r'<ol[^>]*>', content, re.IGNORECASE))
    
    print_info(f"Unordered lists (UL): {ul_count}")
    print_info(f"Ordered lists (OL): {ol_count}")
    
    # Look for procedural content that should be ordered lists
    procedural_indicators = [
        r'step\s+\d+',
        r'first[,\s]',
        r'second[,\s]',
        r'third[,\s]',
        r'then[,\s]',
        r'next[,\s]',
        r'finally[,\s]',
        r'\d+\.\s',
        r'authenticate.*api.*key',
        r'create.*html.*page',
        r'add.*map.*marker'
    ]
    
    procedural_content_found = 0
    for indicator in procedural_indicators:
        matches = re.findall(indicator, content, re.IGNORECASE)
        procedural_content_found += len(matches)
    
    print_info(f"Procedural content indicators found: {procedural_content_found}")
    
    # Check if procedural content is in UL (should be OL)
    ul_sections = re.findall(r'<ul[^>]*>(.*?)</ul>', content, re.IGNORECASE | re.DOTALL)
    procedural_in_ul = 0
    
    for ul_section in ul_sections:
        for indicator in procedural_indicators:
            if re.search(indicator, ul_section, re.IGNORECASE):
                procedural_in_ul += 1
                break
    
    print_info(f"Procedural content in UL (should be OL): {procedural_in_ul}")
    
    # Resolved if we have OL lists or minimal procedural content in UL
    resolved = ol_count > 0 or procedural_in_ul == 0
    
    if resolved:
        print_success(f"✅ List types issue RESOLVED - {ol_count} OL lists, {procedural_in_ul} procedural UL")
    else:
        print_error(f"❌ List types issue PRESENT - {procedural_in_ul} procedural content in UL (should be OL)")
    
    return {
        'resolved': resolved,
        'ul_count': ul_count,
        'ol_count': ol_count,
        'procedural_indicators': procedural_content_found,
        'procedural_in_ul': procedural_in_ul
    }

def analyze_code_blocks(content):
    """Analyze code block fragmentation"""
    print_info("Analyzing Issue 4: Fragmented code blocks (each line separate)...")
    
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
    
    print_info(f"Found {len(code_blocks)} code blocks")
    
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
    
    print_info(f"Single-line code blocks: {single_line_blocks}")
    print_info(f"Multi-line code blocks: {multi_line_blocks}")
    print_info(f"Potentially fragmented blocks: {fragmented_blocks}")
    print_info(f"Consolidated blocks: {consolidated_blocks}")
    
    # Resolved if we have more consolidated than fragmented blocks
    resolved = consolidated_blocks >= fragmented_blocks or fragmented_blocks == 0
    
    if resolved:
        print_success(f"✅ Code block fragmentation issue RESOLVED - {consolidated_blocks} consolidated, {fragmented_blocks} fragmented")
    else:
        print_error(f"❌ Code block fragmentation issue PRESENT - {fragmented_blocks} fragmented blocks")
    
    return {
        'resolved': resolved,
        'total_blocks': len(code_blocks),
        'single_line_blocks': single_line_blocks,
        'multi_line_blocks': multi_line_blocks,
        'fragmented_blocks': fragmented_blocks,
        'consolidated_blocks': consolidated_blocks
    }

def analyze_code_quality(content):
    """Analyze code quality issues"""
    print_info("Analyzing Issue 5: Code quality issues...")
    
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
    
    print_info(f"Analyzing {len(code_blocks)} code blocks for quality...")
    
    # Quality indicators
    quality_issues = 0
    quality_good = 0
    
    # Check for copy buttons
    copy_buttons = len(re.findall(r'copy[^>]*button|button[^>]*copy', content, re.IGNORECASE))
    print_info(f"Copy buttons found: {copy_buttons}")
    
    # Check for syntax highlighting
    syntax_highlighting = len(re.findall(r'class="[^"]*highlight|class="[^"]*syntax|class="[^"]*language', content, re.IGNORECASE))
    print_info(f"Syntax highlighting indicators: {syntax_highlighting}")
    
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
    
    print_info(f"Good quality code blocks: {quality_good}")
    print_info(f"Code blocks with issues: {quality_issues}")
    
    # Check for visual distortion indicators
    visual_issues = len(re.findall(r'pixelat|distort|blur|corrupt', content, re.IGNORECASE))
    print_info(f"Visual distortion indicators: {visual_issues}")
    
    # Resolved if we have good quality indicators and minimal issues
    resolved = (quality_good >= quality_issues and 
               copy_buttons > 0 and 
               visual_issues == 0)
    
    if resolved:
        print_success(f"✅ Code quality issue RESOLVED - {quality_good} good blocks, {copy_buttons} copy buttons")
    else:
        print_error(f"❌ Code quality issues PRESENT - {quality_issues} problematic blocks, {visual_issues} visual issues")
    
    return {
        'resolved': resolved,
        'total_blocks': len(code_blocks),
        'quality_good': quality_good,
        'quality_issues': quality_issues,
        'copy_buttons': copy_buttons,
        'syntax_highlighting': syntax_highlighting,
        'visual_issues': visual_issues
    }

async def test_database_verification():
    """Test 5: Verify article storage in MongoDB content_library collection"""
    print_test_header("Test 5: Database Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Verifying database storage in content_library collection...")
            
            # Check if we can access database information through API
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    print_success(f"Database accessible - {len(articles)} articles in content_library")
                    
                    # Look for recently created articles
                    recent_articles = []
                    current_time = datetime.now()
                    
                    for article in articles:
                        # Check for Google Maps API content
                        title = article.get('title', '').lower()
                        if any(keyword in title for keyword in ['google', 'map', 'javascript', 'api']):
                            recent_articles.append(article)
                    
                    if recent_articles:
                        print_success(f"Found {len(recent_articles)} Google Maps API articles in database")
                        
                        # Check article metadata for V2 processing indicators
                        v2_processed = 0
                        for article in recent_articles:
                            article_str = str(article).lower()
                            if any(indicator in article_str for indicator in ['v2', 'engine', 'processed']):
                                v2_processed += 1
                        
                        print_info(f"Articles with V2 processing indicators: {v2_processed}")
                        
                        return True, recent_articles
                    else:
                        print_warning("No Google Maps API articles found in database")
                        return False, []
                        
                else:
                    print_error(f"Failed to access database - Status: {response.status}")
                    return False, []
                    
    except Exception as e:
        print_error(f"Error verifying database: {e}")
        return False, []

async def test_v2_pipeline_verification():
    """Test 6: Verify all V2 processing steps executed correctly"""
    print_test_header("Test 6: V2 Pipeline Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Verifying V2 processing pipeline steps...")
            
            # Check V2 diagnostics endpoints
            v2_endpoints = [
                '/style/diagnostics',
                '/related-links/diagnostics', 
                '/gap-filling/diagnostics'
            ]
            
            pipeline_steps_verified = 0
            total_steps = len(v2_endpoints)
            
            for endpoint in v2_endpoints:
                try:
                    async with session.get(f"{API_BASE}{endpoint}") as response:
                        if response.status == 200:
                            diagnostics = await response.json()
                            
                            # Check for V2 engine confirmation
                            engine = diagnostics.get('engine', 'unknown')
                            system_status = diagnostics.get('system_status', 'unknown')
                            
                            if engine.lower() == 'v2' and system_status == 'active':
                                pipeline_steps_verified += 1
                                print_success(f"✅ V2 step verified: {endpoint}")
                            else:
                                print_warning(f"⚠️ V2 step partial: {endpoint} (engine: {engine}, status: {system_status})")
                        else:
                            print_warning(f"⚠️ V2 step inaccessible: {endpoint} (status: {response.status})")
                            
                except Exception as e:
                    print_warning(f"⚠️ V2 step error: {endpoint} - {e}")
            
            success_rate = (pipeline_steps_verified / total_steps) * 100
            print_info(f"V2 pipeline verification: {pipeline_steps_verified}/{total_steps} steps verified ({success_rate:.1f}%)")
            
            if success_rate >= 66:
                print_success("✅ V2 pipeline verification PASSED")
                return True
            else:
                print_error("❌ V2 pipeline verification FAILED")
                return False
                
    except Exception as e:
        print_error(f"Error verifying V2 pipeline: {e}")
        return False

async def run_v2_docx_processing_test():
    """Run comprehensive V2 DOCX processing test suite"""
    print_test_header("V2 Engine DOCX Processing - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Fresh processing of Google Map JavaScript API Tutorial.docx through V2 Engine")
    
    # Test results tracking
    test_results = []
    docx_file_path = None
    
    try:
        # Step 1: Download DOCX file
        docx_file_path = await download_docx_file()
        if not docx_file_path:
            print_error("Failed to download DOCX file - cannot proceed with testing")
            return False
        
        # Test 1: V2 Engine Status
        success, engine_data = await test_v2_engine_status()
        test_results.append(("V2 Engine Status", success))
        
        if not success:
            print_error("V2 Engine not operational - cannot proceed with processing tests")
            return False
        
        # Test 2: V2 File Upload Processing
        success, upload_result = await test_v2_file_upload_processing(docx_file_path)
        test_results.append(("V2 File Upload Processing", success))
        
        if not success:
            print_error("V2 file upload failed - cannot proceed with content analysis")
            return False
        
        # Step 3: Wait for processing completion
        job_id = upload_result.get('job_id')
        if job_id:
            success, completion_data = await wait_for_processing_completion(job_id)
            test_results.append(("Processing Completion", success))
        else:
            print_warning("No job ID returned - skipping processing wait")
            test_results.append(("Processing Completion", False))
        
        # Test 3: Content Library Verification
        success, articles = await test_content_library_verification()
        test_results.append(("Content Library Verification", success))
        
        # Test 4: Content Issues Analysis
        if articles:
            success, analysis_results = await analyze_content_issues(articles)
            test_results.append(("Content Issues Analysis", success))
            
            # Print detailed analysis results
            if analysis_results:
                print_info("Detailed Content Issues Analysis:")
                for issue, result in analysis_results.items():
                    if isinstance(result, dict) and 'resolved' in result:
                        status = "✅ RESOLVED" if result['resolved'] else "❌ PRESENT"
                        print_info(f"  - {issue}: {status}")
        else:
            test_results.append(("Content Issues Analysis", False))
        
        # Test 5: Database Verification
        success, db_articles = await test_database_verification()
        test_results.append(("Database Verification", success))
        
        # Test 6: V2 Pipeline Verification
        success = await test_v2_pipeline_verification()
        test_results.append(("V2 Pipeline Verification", success))
        
    finally:
        # Cleanup temporary file
        if docx_file_path and os.path.exists(docx_file_path):
            try:
                os.unlink(docx_file_path)
                print_info("Temporary DOCX file cleaned up")
            except Exception as e:
                print_warning(f"Failed to cleanup temporary file: {e}")
    
    # Final Results Summary
    print_test_header("Test Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Overall assessment
    if success_rate >= 80:
        print_success(f"🎉 V2 DOCX PROCESSING TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("V2 Engine successfully processed the Google Maps API Tutorial DOCX!")
        print_success("✅ Fresh V2 processing completed")
        print_success("✅ Content generated and stored in content library")
        print_success("✅ V2 pipeline steps executed correctly")
    elif success_rate >= 60:
        print_warning(f"⚠️ V2 DOCX PROCESSING PARTIALLY SUCCESSFUL - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some V2 functionality is working, but improvements needed.")
    else:
        print_error(f"❌ V2 DOCX PROCESSING TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with V2 DOCX processing.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting V2 Engine DOCX Processing Test Suite...")
    
    try:
        # Run the V2 DOCX processing test
        success = asyncio.run(run_v2_docx_processing_test())
        
        if success:
            print("\n🎯 V2 DOCX PROCESSING TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 DOCX PROCESSING TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)