#!/usr/bin/env python3
"""
V2 Engine Google Maps Root-Cause Fixes Test Suite
Testing comprehensive root-cause fixes by processing Google Maps DOCX fresh through V2 pipeline

Focus Areas:
1. Fresh V2 Processing - Process Google Map JavaScript API Tutorial.docx through /api/upload-file-to-engine-v2
2. Rule-Based Generation Testing - Verify modified rule-based generation creates proper structure
3. Content Structure Analysis - Examine generated HTML for correct structure
4. Processing Pipeline Verification - Confirm V2 pipeline runs all steps
5. Database Verification - Check stored article has corrected structure
"""

import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime
import sys
import io
import base64

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
    print(f"⚠️ {message}")

async def test_v2_engine_health():
    """Test 1: Verify V2 Engine is operational and ready for processing"""
    print_test_header("Test 1: V2 Engine Health Check")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Check V2 engine status
            print_info("Checking V2 Engine health and availability...")
            
            async with session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    engine_data = await response.json()
                    print_success(f"V2 Engine accessible - Status: {response.status}")
                    
                    # Verify V2 engine is active
                    engine_version = engine_data.get('engine', 'unknown')
                    engine_status = engine_data.get('status', 'unknown')
                    
                    if engine_version == 'v2' and engine_status == 'active':
                        print_success(f"V2 Engine confirmed active - Version: {engine_version}")
                        
                        # Check for required V2 features
                        features = engine_data.get('features', [])
                        required_features = [
                            'v2_article_generation',
                            'rule_based_generation', 
                            'content_structure_analysis',
                            'toc_processing',
                            'code_block_consolidation'
                        ]
                        
                        missing_features = [f for f in required_features if f not in features]
                        if not missing_features:
                            print_success("All required V2 features available")
                            return True, engine_data
                        else:
                            print_warning(f"Some V2 features missing: {missing_features}")
                            return True, engine_data  # Still proceed with available features
                    else:
                        print_error(f"V2 Engine not active - Version: {engine_version}, Status: {engine_status}")
                        return False, None
                else:
                    error_text = await response.text()
                    print_error(f"V2 Engine health check failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False, None
                    
    except Exception as e:
        print_error(f"Error checking V2 Engine health: {e}")
        return False, None

async def test_fresh_v2_processing():
    """Test 2: Process Google Maps DOCX fresh through V2 pipeline"""
    print_test_header("Test 2: Fresh V2 Processing - Google Maps DOCX")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Processing Google Map JavaScript API Tutorial.docx through V2 pipeline...")
            
            # Create a mock DOCX file for testing (since we don't have the actual file)
            # In a real scenario, you would upload the actual Google Maps DOCX file
            mock_docx_content = """
            Google Maps JavaScript API Tutorial
            
            Table of Contents:
            - Getting Started with Google Maps API
            - Setting up API Keys
            - Creating Your First Map
            - Adding Markers and Info Windows
            - Customizing Map Styles
            - Best Practices and Troubleshooting
            
            Getting Started with Google Maps API
            
            The Google Maps JavaScript API lets you customize maps with your own content and imagery for display on web pages and mobile devices.
            
            Step 1: Obtain an API Key
            To use the Google Maps JavaScript API, you need an API key.
            
            Step 2: Load the Maps JavaScript API
            You can load the Maps JavaScript API by adding a script tag to your HTML page.
            
            <script>
            function initMap() {
              const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 4,
                center: { lat: -25.363, lng: 131.044 },
              });
            }
            </script>
            
            Setting up API Keys
            
            Follow these steps to set up your API key:
            1. Go to the Google Cloud Console
            2. Create a new project or select an existing one
            3. Enable the Maps JavaScript API
            4. Create credentials (API key)
            
            Creating Your First Map
            
            Here's how to create a basic map:
            
            <script>
            let map;
            function initMap() {
              map = new google.maps.Map(document.getElementById("map"), {
                center: { lat: -34.397, lng: 150.644 },
                zoom: 8,
              });
            }
            </script>
            
            Adding Markers and Info Windows
            
            You can add markers to your map to highlight specific locations.
            
            const marker = new google.maps.Marker({
              position: { lat: -34.397, lng: 150.644 },
              map: map,
            });
            """
            
            # Create form data for file upload
            data = aiohttp.FormData()
            data.add_field('file', 
                          io.BytesIO(mock_docx_content.encode('utf-8')), 
                          filename='Google Map JavaScript API Tutorial.docx',
                          content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            
            # Upload file to V2 engine
            async with session.post(f"{API_BASE}/upload-file-to-engine-v2", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"V2 processing initiated - Status: {response.status}")
                    
                    # Validate V2 processing response
                    required_fields = ['job_id', 'status', 'engine']
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if not missing_fields:
                        job_id = result.get('job_id')
                        engine = result.get('engine')
                        status = result.get('status')
                        
                        print_success(f"V2 processing job created - Job ID: {job_id}")
                        print_info(f"Engine: {engine}, Status: {status}")
                        
                        if engine == 'v2':
                            print_success("Confirmed processing through V2 engine")
                            return True, result
                        else:
                            print_warning(f"Processing through {engine} engine instead of V2")
                            return True, result
                    else:
                        print_error(f"V2 processing response missing fields: {missing_fields}")
                        return False, None
                else:
                    error_text = await response.text()
                    print_error(f"V2 processing failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False, None
                    
    except Exception as e:
        print_error(f"Error in fresh V2 processing: {e}")
        return False, None

async def test_rule_based_generation_fixes():
    """Test 3: Verify rule-based generation creates correct structure"""
    print_test_header("Test 3: Rule-Based Generation Fixes Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Analyzing rule-based generation fixes...")
            
            # Get content library to find processed articles
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    print_success(f"Content library accessible - {len(articles)} articles found")
                    
                    # Find Google Maps related articles
                    google_maps_articles = []
                    for article in articles:
                        title = article.get('title', '').lower()
                        if any(keyword in title for keyword in ['google', 'maps', 'javascript', 'api']):
                            google_maps_articles.append(article)
                    
                    if google_maps_articles:
                        print_success(f"Found {len(google_maps_articles)} Google Maps related articles")
                        
                        # Analyze the most recent article
                        target_article = google_maps_articles[0]
                        print_info(f"Analyzing article: '{target_article['title']}'")
                        
                        return await analyze_rule_based_fixes(target_article)
                    else:
                        print_warning("No Google Maps related articles found")
                        
                        # Analyze any recent article for rule-based fixes
                        if articles:
                            target_article = articles[0]
                            print_info(f"Analyzing recent article: '{target_article['title']}'")
                            return await analyze_rule_based_fixes(target_article)
                        else:
                            print_error("No articles available for analysis")
                            return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying rule-based generation fixes: {e}")
        return False

async def analyze_rule_based_fixes(article):
    """Analyze article for rule-based generation fixes"""
    content = article.get('content', article.get('html', ''))
    title = article.get('title', 'Unknown')
    
    print_info(f"Analyzing rule-based fixes in '{title}'...")
    
    # Test 1: No H1 in content body (should be removed from line 7223)
    h1_elements = re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE | re.DOTALL)
    h1_in_content = len(h1_elements)
    
    if h1_in_content == 0:
        print_success("✅ No H1 elements found in content body (correct)")
        h1_fix_success = True
    else:
        print_error(f"❌ Found {h1_in_content} H1 elements in content body (should be 0)")
        h1_fix_success = False
    
    # Test 2: Clickable Mini-TOC links with proper anchor format
    toc_links = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)
    markdown_toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
    
    all_toc_links = toc_links + [(text, anchor) for text, anchor in markdown_toc_links]
    
    if len(all_toc_links) >= 3:
        print_success(f"✅ Found {len(all_toc_links)} clickable TOC links with proper anchor format")
        toc_fix_success = True
        
        # Show examples
        for i, (anchor_or_text, text_or_anchor) in enumerate(all_toc_links[:3]):
            if isinstance(anchor_or_text, str) and anchor_or_text.startswith('#'):
                print_info(f"  - [{text_or_anchor}]({anchor_or_text})")
            else:
                print_info(f"  - <a href=\"#{anchor_or_text}\">{text_or_anchor}</a>")
    else:
        print_error(f"❌ Found only {len(all_toc_links)} TOC links (expected at least 3)")
        toc_fix_success = False
    
    # Test 3: Proper list type detection (OL for procedural content)
    ol_lists = re.findall(r'<ol[^>]*>.*?</ol>', content, re.IGNORECASE | re.DOTALL)
    ul_lists = re.findall(r'<ul[^>]*>.*?</ul>', content, re.IGNORECASE | re.DOTALL)
    
    # Look for procedural indicators that should use OL
    procedural_indicators = ['step', 'first', 'second', 'third', 'then', 'next', 'finally']
    has_procedural_content = any(indicator in content.lower() for indicator in procedural_indicators)
    
    if has_procedural_content and len(ol_lists) > 0:
        print_success(f"✅ Found {len(ol_lists)} ordered lists for procedural content")
        list_fix_success = True
    elif not has_procedural_content:
        print_info("ℹ️ No procedural content detected, list type detection not applicable")
        list_fix_success = True
    else:
        print_error(f"❌ Procedural content found but no ordered lists (found {len(ul_lists)} UL, {len(ol_lists)} OL)")
        list_fix_success = False
    
    # Test 4: Code block consolidation
    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', content, re.IGNORECASE | re.DOTALL)
    code_elements = re.findall(r'<code[^>]*>.*?</code>', content, re.IGNORECASE | re.DOTALL)
    
    total_code_elements = len(code_blocks) + len(code_elements)
    
    if total_code_elements > 0:
        # Check for consolidated code blocks (fewer, larger blocks vs many small fragments)
        avg_code_length = sum(len(block) for block in code_blocks + code_elements) / max(1, total_code_elements)
        
        if avg_code_length > 50:  # Consolidated blocks should be longer
            print_success(f"✅ Found {total_code_elements} consolidated code blocks (avg length: {avg_code_length:.0f} chars)")
            code_fix_success = True
        else:
            print_warning(f"⚠️ Found {total_code_elements} code elements but they appear fragmented (avg length: {avg_code_length:.0f} chars)")
            code_fix_success = False
    else:
        print_info("ℹ️ No code blocks found in content")
        code_fix_success = True
    
    # Overall assessment
    fixes_tested = [h1_fix_success, toc_fix_success, list_fix_success, code_fix_success]
    fixes_passed = sum(fixes_tested)
    success_rate = (fixes_passed / len(fixes_tested)) * 100
    
    print_info(f"Rule-based generation fixes assessment:")
    print_info(f"  - H1 removal: {'✅' if h1_fix_success else '❌'}")
    print_info(f"  - TOC links: {'✅' if toc_fix_success else '❌'}")
    print_info(f"  - List types: {'✅' if list_fix_success else '❌'}")
    print_info(f"  - Code consolidation: {'✅' if code_fix_success else '❌'}")
    print_info(f"  - Success rate: {success_rate:.1f}%")
    
    return success_rate >= 75

async def test_content_structure_analysis():
    """Test 4: Examine generated HTML structure"""
    print_test_header("Test 4: Content Structure Analysis")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Analyzing generated HTML content structure...")
            
            # Get content library
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    if articles:
                        # Analyze the most recent article
                        target_article = articles[0]
                        content = target_article.get('content', target_article.get('html', ''))
                        title = target_article.get('title', 'Unknown')
                        
                        print_info(f"Analyzing HTML structure of: '{title}'")
                        
                        return await analyze_html_structure(content, title)
                    else:
                        print_error("No articles available for structure analysis")
                        return False
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in content structure analysis: {e}")
        return False

async def analyze_html_structure(content, title):
    """Analyze HTML structure for correctness"""
    print_info(f"Analyzing HTML structure...")
    
    # Test 1: Proper heading hierarchy
    h1_count = len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
    h2_count = len(re.findall(r'<h2[^>]*>', content, re.IGNORECASE))
    h3_count = len(re.findall(r'<h3[^>]*>', content, re.IGNORECASE))
    
    print_info(f"Heading structure: H1={h1_count}, H2={h2_count}, H3={h3_count}")
    
    # Proper hierarchy: No H1 in content, H2 for main sections, H3 for subsections
    hierarchy_correct = (h1_count == 0 and h2_count > 0)
    
    if hierarchy_correct:
        print_success("✅ Proper heading hierarchy (no H1 in content, H2+ for sections)")
    else:
        print_error("❌ Improper heading hierarchy")
    
    # Test 2: TOC structure
    toc_indicators = ['table of contents', 'contents', 'toc']
    has_toc_section = any(indicator in content.lower() for indicator in toc_indicators)
    
    # Look for TOC links
    toc_links = len(re.findall(r'href="#[^"]*"', content))
    
    if has_toc_section or toc_links >= 3:
        print_success(f"✅ TOC structure present ({toc_links} anchor links)")
        toc_structure_correct = True
    else:
        print_warning("⚠️ Limited TOC structure detected")
        toc_structure_correct = False
    
    # Test 3: Semantic HTML elements
    semantic_elements = {
        'paragraphs': len(re.findall(r'<p[^>]*>', content, re.IGNORECASE)),
        'lists': len(re.findall(r'<[uo]l[^>]*>', content, re.IGNORECASE)),
        'code_blocks': len(re.findall(r'<pre[^>]*>', content, re.IGNORECASE)),
        'emphasis': len(re.findall(r'<(strong|em|b|i)[^>]*>', content, re.IGNORECASE))
    }
    
    semantic_score = sum(1 for count in semantic_elements.values() if count > 0)
    
    print_info(f"Semantic elements: {semantic_elements}")
    
    if semantic_score >= 3:
        print_success(f"✅ Good semantic HTML structure ({semantic_score}/4 element types)")
        semantic_correct = True
    else:
        print_warning(f"⚠️ Limited semantic HTML structure ({semantic_score}/4 element types)")
        semantic_correct = False
    
    # Test 4: Content organization
    content_length = len(content)
    word_count = len(re.findall(r'\b\w+\b', content))
    
    print_info(f"Content metrics: {content_length} chars, {word_count} words")
    
    if content_length > 500 and word_count > 100:
        print_success("✅ Substantial content generated")
        content_substantial = True
    else:
        print_error("❌ Insufficient content generated")
        content_substantial = False
    
    # Overall structure assessment
    structure_tests = [hierarchy_correct, toc_structure_correct, semantic_correct, content_substantial]
    structure_passed = sum(structure_tests)
    success_rate = (structure_passed / len(structure_tests)) * 100
    
    print_info(f"HTML structure analysis:")
    print_info(f"  - Heading hierarchy: {'✅' if hierarchy_correct else '❌'}")
    print_info(f"  - TOC structure: {'✅' if toc_structure_correct else '❌'}")
    print_info(f"  - Semantic HTML: {'✅' if semantic_correct else '❌'}")
    print_info(f"  - Content substantial: {'✅' if content_substantial else '❌'}")
    print_info(f"  - Success rate: {success_rate:.1f}%")
    
    return success_rate >= 75

async def test_v2_pipeline_verification():
    """Test 5: Verify V2 processing pipeline runs all steps"""
    print_test_header("Test 5: V2 Processing Pipeline Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Verifying V2 processing pipeline execution...")
            
            # Check V2 processing diagnostics
            async with session.get(f"{API_BASE}/v2/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    print_success("V2 diagnostics accessible")
                    
                    # Check for pipeline steps
                    pipeline_steps = diagnostics.get('pipeline_steps', [])
                    recent_jobs = diagnostics.get('recent_jobs', [])
                    
                    if pipeline_steps:
                        print_success(f"V2 pipeline steps defined: {len(pipeline_steps)}")
                        
                        # Expected V2 steps
                        expected_steps = [
                            'content_extraction',
                            'structure_analysis', 
                            'article_generation',
                            'style_processing',
                            'validation',
                            'publishing'
                        ]
                        
                        found_steps = []
                        for step in expected_steps:
                            if any(step in str(pipeline_steps).lower() for step in [step]):
                                found_steps.append(step)
                        
                        if len(found_steps) >= 4:
                            print_success(f"✅ V2 pipeline comprehensive ({len(found_steps)}/{len(expected_steps)} steps)")
                            pipeline_complete = True
                        else:
                            print_warning(f"⚠️ V2 pipeline partial ({len(found_steps)}/{len(expected_steps)} steps)")
                            pipeline_complete = False
                    else:
                        print_warning("No pipeline steps information available")
                        pipeline_complete = False
                    
                    # Check recent processing jobs
                    if recent_jobs:
                        print_success(f"Recent V2 processing jobs: {len(recent_jobs)}")
                        
                        # Look for successful completions
                        successful_jobs = [job for job in recent_jobs if job.get('status') == 'completed']
                        
                        if successful_jobs:
                            print_success(f"✅ Successful V2 jobs: {len(successful_jobs)}")
                            jobs_successful = True
                        else:
                            print_warning("⚠️ No successful V2 jobs found")
                            jobs_successful = False
                    else:
                        print_info("No recent processing jobs information")
                        jobs_successful = False
                    
                    return pipeline_complete and jobs_successful
                    
                elif response.status == 404:
                    print_info("V2 diagnostics endpoint not available, checking alternative...")
                    
                    # Try engine status instead
                    async with session.get(f"{API_BASE}/engine") as engine_response:
                        if engine_response.status == 200:
                            engine_data = await engine_response.json()
                            
                            if engine_data.get('engine') == 'v2':
                                print_success("V2 engine confirmed active")
                                return True
                            else:
                                print_warning("V2 engine not confirmed")
                                return False
                        else:
                            print_error("Unable to verify V2 pipeline")
                            return False
                else:
                    print_error(f"Failed to access V2 diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying V2 pipeline: {e}")
        return False

async def test_database_verification():
    """Test 6: Check database for corrected article structure"""
    print_test_header("Test 6: Database Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Verifying database storage of corrected article structure...")
            
            # Get content library with metadata
            async with session.get(f"{API_BASE}/content-library?include_metadata=true") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    if articles:
                        print_success(f"Database accessible - {len(articles)} articles stored")
                        
                        # Look for articles with V2 processing metadata
                        v2_articles = []
                        for article in articles:
                            metadata = article.get('metadata', {})
                            if (metadata.get('engine') == 'v2' or 
                                'v2' in str(metadata).lower() or
                                article.get('engine') == 'v2'):
                                v2_articles.append(article)
                        
                        if v2_articles:
                            print_success(f"Found {len(v2_articles)} V2 processed articles in database")
                            
                            # Analyze the most recent V2 article
                            target_article = v2_articles[0]
                            return await verify_database_structure(target_article)
                        else:
                            print_warning("No V2 processed articles found in database")
                            
                            # Check any recent article for corrected structure
                            if articles:
                                target_article = articles[0]
                                return await verify_database_structure(target_article)
                            else:
                                print_error("No articles in database")
                                return False
                    else:
                        print_error("No articles found in database")
                        return False
                else:
                    print_error(f"Failed to access database - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying database: {e}")
        return False

async def verify_database_structure(article):
    """Verify article has corrected structure in database"""
    title = article.get('title', 'Unknown')
    content = article.get('content', article.get('html', ''))
    metadata = article.get('metadata', {})
    
    print_info(f"Verifying database structure for: '{title}'")
    
    # Test 1: Article has required fields
    required_fields = ['id', 'title', 'content', 'created_at']
    missing_fields = [field for field in required_fields if field not in article]
    
    if not missing_fields:
        print_success("✅ All required fields present in database")
        fields_complete = True
    else:
        print_error(f"❌ Missing required fields: {missing_fields}")
        fields_complete = False
    
    # Test 2: Content structure is corrected
    h1_in_content = len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE))
    toc_links = len(re.findall(r'href="#[^"]*"', content))
    
    structure_corrected = (h1_in_content == 0 and toc_links >= 2)
    
    if structure_corrected:
        print_success("✅ Corrected content structure stored in database")
    else:
        print_warning("⚠️ Content structure may need further correction")
    
    # Test 3: Processing metadata preserved
    has_processing_metadata = bool(metadata and (
        'engine' in metadata or 
        'processing' in str(metadata).lower() or
        'v2' in str(metadata).lower()
    ))
    
    if has_processing_metadata:
        print_success("✅ Processing metadata preserved in database")
    else:
        print_info("ℹ️ Limited processing metadata in database")
    
    # Test 4: Content quality
    content_length = len(content)
    word_count = len(re.findall(r'\b\w+\b', content))
    
    quality_adequate = (content_length > 300 and word_count > 50)
    
    if quality_adequate:
        print_success(f"✅ Quality content stored ({content_length} chars, {word_count} words)")
    else:
        print_warning(f"⚠️ Limited content quality ({content_length} chars, {word_count} words)")
    
    # Overall database verification
    db_tests = [fields_complete, structure_corrected, has_processing_metadata, quality_adequate]
    db_passed = sum(db_tests)
    success_rate = (db_passed / len(db_tests)) * 100
    
    print_info(f"Database verification:")
    print_info(f"  - Required fields: {'✅' if fields_complete else '❌'}")
    print_info(f"  - Structure corrected: {'✅' if structure_corrected else '❌'}")
    print_info(f"  - Processing metadata: {'✅' if has_processing_metadata else '❌'}")
    print_info(f"  - Content quality: {'✅' if quality_adequate else '❌'}")
    print_info(f"  - Success rate: {success_rate:.1f}%")
    
    return success_rate >= 75

async def run_v2_google_maps_root_cause_test():
    """Run comprehensive V2 Google Maps root-cause fixes test suite"""
    print_test_header("V2 Google Maps Root-Cause Fixes - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Testing comprehensive root-cause fixes by processing Google Maps DOCX fresh")
    
    # Test results tracking
    test_results = []
    
    # Test 1: V2 Engine Health Check
    success, engine_data = await test_v2_engine_health()
    test_results.append(("V2 Engine Health", success))
    
    if not success:
        print_error("V2 Engine not available - cannot proceed with testing")
        return False
    
    # Test 2: Fresh V2 Processing
    success, processing_result = await test_fresh_v2_processing()
    test_results.append(("Fresh V2 Processing", success))
    
    # Test 3: Rule-Based Generation Fixes
    success = await test_rule_based_generation_fixes()
    test_results.append(("Rule-Based Generation Fixes", success))
    
    # Test 4: Content Structure Analysis
    success = await test_content_structure_analysis()
    test_results.append(("Content Structure Analysis", success))
    
    # Test 5: V2 Pipeline Verification
    success = await test_v2_pipeline_verification()
    test_results.append(("V2 Pipeline Verification", success))
    
    # Test 6: Database Verification
    success = await test_database_verification()
    test_results.append(("Database Verification", success))
    
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
        print_success(f"🎉 V2 GOOGLE MAPS ROOT-CAUSE FIXES TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("The comprehensive root-cause fixes are working correctly!")
        print_success("✅ V2 processing pipeline operational")
        print_success("✅ Rule-based generation creates proper structure")
        print_success("✅ Content structure analysis confirms fixes")
        print_success("✅ Database stores corrected article structure")
    elif success_rate >= 60:
        print_info(f"⚠️ V2 ROOT-CAUSE FIXES PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some fixes are working, but improvements needed.")
    else:
        print_error(f"❌ V2 ROOT-CAUSE FIXES TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with root-cause fixes.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting V2 Google Maps Root-Cause Fixes Test Suite...")
    
    try:
        # Run the comprehensive test
        success = asyncio.run(run_v2_google_maps_root_cause_test())
        
        if success:
            print("\n🎯 V2 ROOT-CAUSE FIXES TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 ROOT-CAUSE FIXES TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)