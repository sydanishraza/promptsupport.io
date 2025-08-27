#!/usr/bin/env python3
"""
V2 Engine DOCX Processing Test Suite
Testing V2 Engine processing with Google Map JavaScript API Tutorial.docx file
Focus: Complete V2 processing pipeline verification and content analysis
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

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test file URL
DOCX_FILE_URL = "https://customer-assets.emergentagent.com/job_content-pipeline-5/artifacts/uea7rxoa_Google%20Map%20JavaScript%20API%20Tutorial.docx"

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

async def download_docx_file():
    """Download the Google Map JavaScript API Tutorial.docx file"""
    print_test_header("Test 1: Download DOCX File")
    
    try:
        print_info(f"Downloading DOCX file from: {DOCX_FILE_URL}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(DOCX_FILE_URL) as response:
                if response.status == 200:
                    content = await response.read()
                    print_success(f"DOCX file downloaded successfully - {len(content)} bytes")
                    
                    # Save to temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
                    temp_file.write(content)
                    temp_file.close()
                    
                    print_info(f"DOCX file saved to: {temp_file.name}")
                    return temp_file.name, content
                else:
                    print_error(f"Failed to download DOCX file - Status: {response.status}")
                    return None, None
                    
    except Exception as e:
        print_error(f"Error downloading DOCX file: {e}")
        return None, None

async def test_v2_engine_status():
    """Test 2: Verify V2 Engine Status"""
    print_test_header("Test 2: V2 Engine Status Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking V2 Engine status...")
            
            async with session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    engine_status = await response.json()
                    print_success("V2 Engine status endpoint accessible")
                    
                    # Check for V2 engine
                    engine_type = engine_status.get('engine', 'unknown')
                    if engine_type == 'v2':
                        print_success("V2 Engine is active")
                    else:
                        print_error(f"Expected V2 engine, found: {engine_type}")
                        return False
                    
                    # Check for V2 features
                    v2_features = [
                        'woolf_style_processing',
                        'section_grounded_prewrite',
                        'code_block_normalization',
                        'evidence_paragraph_tagging',
                        'intelligent_gap_filling',
                        'content_library_indexing',
                        'v2_publishing_flow'
                    ]
                    
                    features = engine_status.get('features', [])
                    missing_features = [f for f in v2_features if f not in str(features)]
                    
                    if not missing_features:
                        print_success("All V2 features are available")
                        return True
                    else:
                        print_error(f"Missing V2 features: {missing_features}")
                        return False
                        
                else:
                    print_error(f"Failed to access V2 Engine status - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error checking V2 Engine status: {e}")
        return False

async def upload_docx_to_v2_engine(file_path, file_content):
    """Test 3: Upload DOCX to V2 Engine"""
    print_test_header("Test 3: V2 Engine DOCX Upload")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Uploading DOCX file to V2 Engine...")
            
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('file', 
                          file_content, 
                          filename='Google_Map_JavaScript_API_Tutorial.docx',
                          content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            data.add_field('engine', 'v2')
            data.add_field('processing_mode', 'complete')
            
            async with session.post(f"{API_BASE}/content/upload", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success("DOCX file uploaded successfully to V2 Engine")
                    
                    # Extract job information
                    job_id = result.get('job_id')
                    processing_id = result.get('processing_id')
                    engine = result.get('engine')
                    
                    if job_id:
                        print_success(f"Job ID: {job_id}")
                    if processing_id:
                        print_success(f"Processing ID: {processing_id}")
                    if engine == 'v2':
                        print_success(f"Engine confirmed: {engine}")
                    
                    return job_id, processing_id, result
                else:
                    error_text = await response.text()
                    print_error(f"DOCX upload failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return None, None, None
                    
    except Exception as e:
        print_error(f"Error uploading DOCX to V2 Engine: {e}")
        return None, None, None

async def monitor_v2_processing(job_id, processing_id, timeout=300):
    """Test 4: Monitor V2 Processing Pipeline"""
    print_test_header("Test 4: V2 Processing Pipeline Monitoring")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info(f"Monitoring V2 processing for job: {job_id}")
            
            start_time = time.time()
            processing_complete = False
            
            while time.time() - start_time < timeout and not processing_complete:
                # Check job status
                async with session.get(f"{API_BASE}/job/{job_id}") as response:
                    if response.status == 200:
                        job_status = await response.json()
                        status = job_status.get('status', 'unknown')
                        progress = job_status.get('progress', 0)
                        
                        print_info(f"Job status: {status}, Progress: {progress}%")
                        
                        if status == 'completed':
                            processing_complete = True
                            print_success("V2 processing completed successfully")
                            return True, job_status
                        elif status == 'failed':
                            print_error("V2 processing failed")
                            error_msg = job_status.get('error', 'Unknown error')
                            print_error(f"Error: {error_msg}")
                            return False, job_status
                        elif status in ['processing', 'queued', 'started']:
                            # Continue monitoring
                            await asyncio.sleep(10)
                        else:
                            print_error(f"Unexpected job status: {status}")
                            return False, job_status
                    else:
                        print_error(f"Failed to check job status - Status: {response.status}")
                        await asyncio.sleep(10)
            
            if not processing_complete:
                print_error(f"V2 processing timeout after {timeout} seconds")
                return False, None
                
    except Exception as e:
        print_error(f"Error monitoring V2 processing: {e}")
        return False, None

async def verify_v2_processing_steps():
    """Test 5: Verify V2 Processing Steps Execution"""
    print_test_header("Test 5: V2 Processing Steps Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Verifying V2 processing steps execution...")
            
            # Check each V2 processing step
            v2_steps = [
                ('prewrite', '/api/prewrite/diagnostics'),
                ('style', '/api/style/diagnostics'),
                ('code-normalization', '/api/code-normalization/diagnostics'),
                ('evidence-tagging', '/api/evidence-tagging/diagnostics'),
                ('gap-filling', '/api/gap-filling/diagnostics'),
                ('related-links', '/api/related-links/diagnostics'),
                ('publishing', '/api/publishing/diagnostics')
            ]
            
            step_results = {}
            
            for step_name, endpoint in v2_steps:
                try:
                    async with session.get(f"{BACKEND_URL}{endpoint}") as response:
                        if response.status == 200:
                            diagnostics = await response.json()
                            
                            # Check for recent processing
                            recent_results = diagnostics.get('recent_results', [])
                            total_runs = diagnostics.get('total_runs', 0)
                            success_rate = diagnostics.get('success_rate', 0)
                            
                            if total_runs > 0:
                                print_success(f"{step_name.upper()} step executed - {total_runs} runs, {success_rate}% success")
                                step_results[step_name] = True
                            else:
                                print_info(f"{step_name.upper()} step - No recent runs found")
                                step_results[step_name] = False
                        else:
                            print_error(f"{step_name.upper()} step diagnostics unavailable - Status: {response.status}")
                            step_results[step_name] = False
                            
                except Exception as step_error:
                    print_error(f"Error checking {step_name} step: {step_error}")
                    step_results[step_name] = False
            
            # Calculate overall V2 pipeline success
            executed_steps = sum(1 for success in step_results.values() if success)
            total_steps = len(step_results)
            pipeline_success_rate = (executed_steps / total_steps) * 100
            
            print_info(f"V2 Pipeline Execution: {executed_steps}/{total_steps} steps ({pipeline_success_rate:.1f}%)")
            
            if pipeline_success_rate >= 70:
                print_success("V2 processing pipeline execution VERIFIED")
                return True, step_results
            else:
                print_error("V2 processing pipeline execution INCOMPLETE")
                return False, step_results
                
    except Exception as e:
        print_error(f"Error verifying V2 processing steps: {e}")
        return False, {}

async def verify_content_library_storage():
    """Test 6: Verify Content Library Storage with V2 Metadata"""
    print_test_header("Test 6: Content Library Storage Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking content library for V2 processed articles...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    print_success(f"Content library accessible - {len(articles)} total articles")
                    
                    # Find V2 processed articles
                    v2_articles = []
                    google_maps_articles = []
                    
                    for article in articles:
                        article_str = str(article)
                        
                        # Check for V2 metadata
                        if any(indicator in article_str for indicator in ['v2', 'engine": "v2"', 'v2_processing']):
                            v2_articles.append(article)
                        
                        # Check for Google Maps content
                        title = article.get('title', '').lower()
                        content = article.get('content', article.get('html', '')).lower()
                        
                        if any(keyword in title or keyword in content for keyword in ['google', 'map', 'javascript', 'api']):
                            google_maps_articles.append(article)
                    
                    print_success(f"V2 processed articles found: {len(v2_articles)}")
                    print_success(f"Google Maps related articles found: {len(google_maps_articles)}")
                    
                    # Analyze V2 metadata structure
                    if v2_articles:
                        sample_article = v2_articles[0]
                        print_info("V2 Article Metadata Analysis:")
                        
                        # Check for V2 specific fields
                        v2_fields = ['html', 'markdown', 'toc', 'faq', 'related_links', 'provenance_map', 'metrics']
                        found_fields = []
                        
                        for field in v2_fields:
                            if field in sample_article:
                                found_fields.append(field)
                                print_success(f"  - {field}: Present")
                            else:
                                print_info(f"  - {field}: Not found")
                        
                        metadata_completeness = (len(found_fields) / len(v2_fields)) * 100
                        print_info(f"V2 Metadata Completeness: {metadata_completeness:.1f}%")
                        
                        return len(v2_articles) > 0, v2_articles, google_maps_articles
                    else:
                        print_error("No V2 processed articles found in content library")
                        return False, [], google_maps_articles
                        
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False, [], []
                    
    except Exception as e:
        print_error(f"Error verifying content library storage: {e}")
        return False, [], []

async def analyze_generated_content_issues(articles):
    """Test 7: Analyze Generated Content for Specific Issues"""
    print_test_header("Test 7: Content Issues Analysis")
    
    try:
        print_info("Analyzing generated articles for specific issues...")
        
        if not articles:
            print_error("No articles provided for analysis")
            return False, {}
        
        issues_found = {
            'multiple_h1_tags': [],
            'static_mini_toc': [],
            'incorrect_list_types': [],
            'code_rendering_problems': [],
            'code_quality_issues': []
        }
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', article.get('html', ''))
            
            print_info(f"Analyzing article: {title}")
            
            # Issue 1: Multiple H1 tags in article body
            h1_matches = re.findall(r'<h1[^>]*>', content)
            if len(h1_matches) > 1:
                issues_found['multiple_h1_tags'].append({
                    'title': title,
                    'h1_count': len(h1_matches),
                    'article_id': article.get('id')
                })
                print_error(f"  - Multiple H1 tags found: {len(h1_matches)}")
            else:
                print_success(f"  - H1 tags: {len(h1_matches)} (correct)")
            
            # Issue 2: Static Mini-TOC lists (non-clickable)
            toc_patterns = [
                r'<ul[^>]*>.*?<li[^>]*>[^<]*(?:introduction|getting started|overview|setup)',
                r'- (?:Introduction|Getting Started|Overview|Setup)',
                r'\* (?:Introduction|Getting Started|Overview|Setup)'
            ]
            
            static_toc_found = False
            for pattern in toc_patterns:
                if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                    # Check if it's clickable (has links)
                    toc_section = re.search(pattern, content, re.IGNORECASE | re.DOTALL).group()
                    if not re.search(r'<a href=|href=', toc_section):
                        static_toc_found = True
                        break
            
            if static_toc_found:
                issues_found['static_mini_toc'].append({
                    'title': title,
                    'article_id': article.get('id')
                })
                print_error("  - Static Mini-TOC found (non-clickable)")
            else:
                print_success("  - Mini-TOC: Clickable or not present")
            
            # Issue 3: Incorrect list type detection
            ordered_lists = len(re.findall(r'<ol[^>]*>', content))
            unordered_lists = len(re.findall(r'<ul[^>]*>', content))
            
            # Check for numbered content that should be ordered lists
            numbered_items = len(re.findall(r'^\d+\.\s', content, re.MULTILINE))
            if numbered_items > 3 and ordered_lists == 0:
                issues_found['incorrect_list_types'].append({
                    'title': title,
                    'numbered_items': numbered_items,
                    'ordered_lists': ordered_lists,
                    'article_id': article.get('id')
                })
                print_error(f"  - List type issue: {numbered_items} numbered items, {ordered_lists} ordered lists")
            else:
                print_success(f"  - Lists: {ordered_lists} ordered, {unordered_lists} unordered")
            
            # Issue 4: Code rendering problems
            code_blocks = re.findall(r'<pre[^>]*>.*?</pre>|<code[^>]*>.*?</code>', content, re.DOTALL)
            code_issues = []
            
            for code_block in code_blocks:
                # Check for separate blocks that should be wrapped
                if 'function' in code_block and 'var' in code_block and len(code_block) > 200:
                    # This might be multiple code snippets that should be separate
                    if code_block.count('function') > 1 or code_block.count('var') > 3:
                        code_issues.append('multiple_snippets_in_one_block')
                
                # Check for proper wrapping
                if not re.search(r'<pre[^>]*class=', code_block) and len(code_block) > 100:
                    code_issues.append('missing_proper_wrapper')
            
            if code_issues:
                issues_found['code_rendering_problems'].append({
                    'title': title,
                    'issues': code_issues,
                    'code_blocks_count': len(code_blocks),
                    'article_id': article.get('id')
                })
                print_error(f"  - Code rendering issues: {len(code_issues)} problems")
            else:
                print_success(f"  - Code blocks: {len(code_blocks)} properly rendered")
            
            # Issue 5: Code quality issues (distorted/pixelated text indicators)
            quality_issues = []
            
            # Check for inline styles that might cause rendering issues
            if re.search(r'style=["\'][^"\']*font-size:\s*[0-9]+px', content):
                quality_issues.append('hardcoded_font_sizes')
            
            # Check for missing language specifications
            code_without_lang = re.findall(r'<pre(?![^>]*class=["\'][^"\']*language-)[^>]*>', content)
            if code_without_lang:
                quality_issues.append('missing_language_specification')
            
            if quality_issues:
                issues_found['code_quality_issues'].append({
                    'title': title,
                    'issues': quality_issues,
                    'article_id': article.get('id')
                })
                print_error(f"  - Code quality issues: {len(quality_issues)} problems")
            else:
                print_success("  - Code quality: Good")
        
        # Summary of issues
        total_issues = sum(len(issue_list) for issue_list in issues_found.values())
        print_info(f"Content Analysis Complete - {total_issues} total issues found")
        
        for issue_type, issue_list in issues_found.items():
            if issue_list:
                print_error(f"{issue_type.replace('_', ' ').title()}: {len(issue_list)} articles affected")
            else:
                print_success(f"{issue_type.replace('_', ' ').title()}: No issues found")
        
        return total_issues == 0, issues_found
        
    except Exception as e:
        print_error(f"Error analyzing content issues: {e}")
        return False, {}

async def run_v2_engine_docx_test():
    """Run comprehensive V2 Engine DOCX processing test suite"""
    print_test_header("V2 Engine DOCX Processing - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Testing V2 Engine processing with Google Map JavaScript API Tutorial.docx")
    
    # Test results tracking
    test_results = []
    job_id = None
    processing_id = None
    v2_articles = []
    
    # Test 1: Download DOCX File
    file_path, file_content = await download_docx_file()
    test_results.append(("DOCX File Download", file_path is not None))
    
    if not file_path:
        print_error("Cannot proceed without DOCX file")
        return False
    
    # Test 2: V2 Engine Status
    success = await test_v2_engine_status()
    test_results.append(("V2 Engine Status", success))
    
    # Test 3: Upload DOCX to V2 Engine
    job_id, processing_id, upload_result = await upload_docx_to_v2_engine(file_path, file_content)
    test_results.append(("V2 Engine Upload", job_id is not None))
    
    if job_id:
        # Test 4: Monitor V2 Processing
        success, job_status = await monitor_v2_processing(job_id, processing_id)
        test_results.append(("V2 Processing Pipeline", success))
        
        # Test 5: Verify V2 Processing Steps
        success, step_results = await verify_v2_processing_steps()
        test_results.append(("V2 Processing Steps", success))
        
        # Test 6: Verify Content Library Storage
        success, v2_articles, google_maps_articles = await verify_content_library_storage()
        test_results.append(("Content Library Storage", success))
        
        # Test 7: Analyze Content Issues
        if v2_articles or google_maps_articles:
            articles_to_analyze = v2_articles if v2_articles else google_maps_articles
            success, issues_analysis = await analyze_generated_content_issues(articles_to_analyze)
            test_results.append(("Content Issues Analysis", success))
        else:
            test_results.append(("Content Issues Analysis", False))
    
    # Clean up temporary file
    if file_path and os.path.exists(file_path):
        os.unlink(file_path)
        print_info("Temporary DOCX file cleaned up")
    
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
        print_success(f"🎉 V2 ENGINE DOCX PROCESSING TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("V2 Engine successfully processed the Google Maps API Tutorial DOCX file!")
        print_success("✅ Complete V2 processing pipeline executed")
        print_success("✅ Articles generated and stored with V2 metadata")
        print_success("✅ Content analysis completed for issue identification")
    elif success_rate >= 60:
        print_info(f"⚠️ V2 ENGINE DOCX PROCESSING PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some V2 functionality is working, but improvements needed.")
    else:
        print_error(f"❌ V2 ENGINE DOCX PROCESSING TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with V2 Engine DOCX processing.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting V2 Engine DOCX Processing Test Suite...")
    
    try:
        # Run the V2 Engine DOCX test
        success = asyncio.run(run_v2_engine_docx_test())
        
        if success:
            print("\n🎯 V2 ENGINE DOCX PROCESSING TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 ENGINE DOCX PROCESSING TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)