#!/usr/bin/env python3
"""
CRITICAL DUPLICATE PROCESSING AND TIMEOUT BUG INVESTIGATION
Testing for the urgent issues reported in the review request:
1. Duplicate Article Generation (2 sets of articles)
2. Backend Processing Timeout (504 Error)
3. HTML Placeholder Issues
4. Processing Pipeline Analysis
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import asyncio
import aiohttp

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_backend_health():
    """Test backend health and connectivity"""
    try:
        log_test_result("Testing backend health check...")
        response = requests.get(f"{API_BASE}/health", timeout=30)
        
        if response.status_code == 200:
            log_test_result("✅ Backend health check PASSED", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ Backend health check FAILED: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend health check FAILED: {e}", "ERROR")
        return False

def test_upload_timeout_investigation():
    """
    CRITICAL TEST: Investigate 504 timeout errors during upload processing
    """
    try:
        log_test_result("🚨 INVESTIGATING UPLOAD TIMEOUT ISSUES", "CRITICAL")
        
        # Create a test document to upload
        test_content = """
        # Test Document for Duplicate Processing Investigation
        
        This is a comprehensive test document designed to investigate the duplicate processing bug.
        
        ## Section 1: Introduction
        This section contains substantial content to trigger article generation.
        
        ## Section 2: Implementation Details
        More content here to ensure multiple articles are generated.
        
        ## Section 3: Advanced Features
        Additional content to test the processing pipeline.
        
        ## Section 4: Troubleshooting
        Final section with troubleshooting information.
        """ * 10  # Multiply to create substantial content
        
        # Create temporary file
        test_file_path = "/tmp/test_duplicate_investigation.txt"
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        log_test_result(f"📄 Created test file: {len(test_content)} characters")
        
        # Test upload with timeout monitoring
        log_test_result("📤 Testing upload with timeout monitoring...")
        
        start_time = time.time()
        
        try:
            with open(test_file_path, 'rb') as f:
                files = {'file': ('test_duplicate_investigation.txt', f, 'text/plain')}
                
                # Monitor for 504 timeout
                response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=120)
                
                upload_time = time.time() - start_time
                log_test_result(f"⏱️ Upload completed in {upload_time:.2f} seconds")
                
                if response.status_code == 504:
                    log_test_result("🚨 CRITICAL: 504 TIMEOUT ERROR DETECTED", "CRITICAL_ERROR")
                    log_test_result(f"Response: {response.text[:500]}")
                    return {'timeout_detected': True, 'upload_time': upload_time}
                elif response.status_code == 200:
                    upload_data = response.json()
                    job_id = upload_data.get('job_id')
                    log_test_result(f"✅ Upload successful, Job ID: {job_id}")
                    return {'timeout_detected': False, 'upload_time': upload_time, 'job_id': job_id}
                else:
                    log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                    log_test_result(f"Response: {response.text[:500]}")
                    return {'timeout_detected': False, 'upload_time': upload_time, 'error': response.status_code}
                    
        except requests.exceptions.Timeout:
            upload_time = time.time() - start_time
            log_test_result(f"🚨 CRITICAL: REQUEST TIMEOUT AFTER {upload_time:.2f} SECONDS", "CRITICAL_ERROR")
            return {'timeout_detected': True, 'upload_time': upload_time, 'timeout_type': 'request_timeout'}
            
    except Exception as e:
        log_test_result(f"❌ Upload timeout investigation failed: {e}", "ERROR")
        return {'error': str(e)}

def test_duplicate_article_generation(job_id):
    """
    CRITICAL TEST: Monitor processing to detect duplicate article generation
    """
    try:
        log_test_result("🔍 INVESTIGATING DUPLICATE ARTICLE GENERATION", "CRITICAL")
        
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        article_counts = []
        processing_stages = []
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                break
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    # Track article counts throughout processing
                    articles_generated = status_data.get('articles_generated', 0)
                    if articles_generated > 0:
                        article_counts.append({
                            'timestamp': elapsed,
                            'count': articles_generated,
                            'status': status
                        })
                    
                    processing_stages.append({
                        'timestamp': elapsed,
                        'status': status,
                        'data': status_data
                    })
                    
                    log_test_result(f"📊 Processing status: {status} | Articles: {articles_generated} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # CRITICAL ANALYSIS: Check for duplicate generation patterns
                        log_test_result("🔍 ANALYZING ARTICLE GENERATION PATTERNS", "CRITICAL")
                        
                        if len(article_counts) > 1:
                            # Check for sudden jumps in article count (indicating duplicate processing)
                            for i in range(1, len(article_counts)):
                                prev_count = article_counts[i-1]['count']
                                curr_count = article_counts[i]['count']
                                time_diff = article_counts[i]['timestamp'] - article_counts[i-1]['timestamp']
                                
                                if curr_count > prev_count * 1.5 and time_diff < 30:  # 50% increase in <30 seconds
                                    log_test_result(f"🚨 POTENTIAL DUPLICATE PROCESSING DETECTED:", "CRITICAL_ERROR")
                                    log_test_result(f"   Articles jumped from {prev_count} to {curr_count} in {time_diff:.1f}s")
                        
                        return {
                            'processing_time': processing_time,
                            'final_article_count': articles_generated,
                            'article_count_history': article_counts,
                            'processing_stages': processing_stages
                        }
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return {'error': 'processing_failed', 'stages': processing_stages}
                    
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
                
    except Exception as e:
        log_test_result(f"❌ Duplicate article investigation failed: {e}", "ERROR")
        return {'error': str(e)}

def test_content_library_duplicate_check():
    """
    CRITICAL TEST: Check Content Library for duplicate articles
    """
    try:
        log_test_result("🔍 CHECKING CONTENT LIBRARY FOR DUPLICATES", "CRITICAL")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            log_test_result(f"📚 Found {len(articles)} articles in Content Library")
            
            # Check for duplicate titles or similar content
            title_counts = {}
            similar_articles = []
            
            for article in articles:
                title = article.get('title', '').strip()
                content = article.get('content', '')
                
                # Count title occurrences
                if title:
                    title_counts[title] = title_counts.get(title, 0) + 1
                
                # Check for HTML placeholder issues
                if '```html' in content or '<html>' in content.lower():
                    similar_articles.append({
                        'id': article.get('id'),
                        'title': title,
                        'has_html_placeholders': True,
                        'content_preview': content[:200]
                    })
            
            # Report duplicates
            duplicates_found = {title: count for title, count in title_counts.items() if count > 1}
            
            if duplicates_found:
                log_test_result("🚨 DUPLICATE TITLES DETECTED:", "CRITICAL_ERROR")
                for title, count in duplicates_found.items():
                    log_test_result(f"   '{title}': {count} occurrences")
            else:
                log_test_result("✅ No duplicate titles found")
            
            # Report HTML placeholder issues
            html_placeholder_articles = [a for a in similar_articles if a.get('has_html_placeholders')]
            if html_placeholder_articles:
                log_test_result("🚨 HTML PLACEHOLDER ISSUES DETECTED:", "CRITICAL_ERROR")
                for article in html_placeholder_articles[:3]:
                    log_test_result(f"   Article: {article['title'][:50]}...")
                    log_test_result(f"   Preview: {article['content_preview']}")
            else:
                log_test_result("✅ No HTML placeholder issues found")
            
            return {
                'total_articles': len(articles),
                'duplicate_titles': duplicates_found,
                'html_placeholder_issues': len(html_placeholder_articles),
                'articles_with_issues': html_placeholder_articles[:5]
            }
            
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return {'error': f'status_{response.status_code}'}
            
    except Exception as e:
        log_test_result(f"❌ Content Library duplicate check failed: {e}", "ERROR")
        return {'error': str(e)}

def test_processing_pipeline_analysis():
    """
    CRITICAL TEST: Analyze if both outline-first and legacy processing are running
    """
    try:
        log_test_result("🔍 ANALYZING PROCESSING PIPELINE FOR DUAL EXECUTION", "CRITICAL")
        
        # Check backend logs for processing pipeline indicators
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for indicators of both processing pipelines
                outline_indicators = [
                    "COMPREHENSIVE OUTLINE GENERATED",
                    "CREATING ARTICLES FROM OUTLINE",
                    "create_articles_from_outline",
                    "outline-based processing"
                ]
                
                legacy_indicators = [
                    "create_content_library_articles_from_chunks",
                    "traditional chunking",
                    "legacy processing",
                    "chunk-based processing"
                ]
                
                outline_found = []
                legacy_found = []
                
                for indicator in outline_indicators:
                    if indicator in logs:
                        outline_found.append(indicator)
                
                for indicator in legacy_indicators:
                    if indicator in logs:
                        legacy_found.append(indicator)
                
                log_test_result("📊 PROCESSING PIPELINE ANALYSIS RESULTS:")
                log_test_result(f"   Outline-first indicators found: {len(outline_found)}")
                for indicator in outline_found:
                    log_test_result(f"     - {indicator}")
                
                log_test_result(f"   Legacy processing indicators found: {len(legacy_found)}")
                for indicator in legacy_found:
                    log_test_result(f"     - {indicator}")
                
                # CRITICAL: Check if both are running simultaneously
                if outline_found and legacy_found:
                    log_test_result("🚨 CRITICAL: BOTH PROCESSING PIPELINES DETECTED", "CRITICAL_ERROR")
                    log_test_result("🚨 This explains the duplicate article generation!", "CRITICAL_ERROR")
                    return {
                        'dual_processing_detected': True,
                        'outline_indicators': outline_found,
                        'legacy_indicators': legacy_found
                    }
                elif outline_found:
                    log_test_result("✅ Only outline-first processing detected")
                    return {
                        'dual_processing_detected': False,
                        'primary_pipeline': 'outline-first',
                        'indicators': outline_found
                    }
                elif legacy_found:
                    log_test_result("✅ Only legacy processing detected")
                    return {
                        'dual_processing_detected': False,
                        'primary_pipeline': 'legacy',
                        'indicators': legacy_found
                    }
                else:
                    log_test_result("⚠️ No clear processing pipeline indicators found")
                    return {'dual_processing_detected': False, 'indicators_found': False}
                    
            else:
                log_test_result("⚠️ Could not access backend logs")
                return {'error': 'log_access_failed'}
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log analysis failed: {log_error}")
            return {'error': str(log_error)}
            
    except Exception as e:
        log_test_result(f"❌ Processing pipeline analysis failed: {e}", "ERROR")
        return {'error': str(e)}

def run_comprehensive_duplicate_investigation():
    """Run comprehensive investigation for duplicate processing and timeout issues"""
    log_test_result("🚨 STARTING CRITICAL DUPLICATE PROCESSING INVESTIGATION", "CRITICAL")
    log_test_result("=" * 80)
    
    investigation_results = {
        'backend_health': False,
        'timeout_investigation': {},
        'duplicate_generation': {},
        'content_library_duplicates': {},
        'pipeline_analysis': {}
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    investigation_results['backend_health'] = test_backend_health()
    
    if not investigation_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting investigation", "CRITICAL_ERROR")
        return investigation_results
    
    # Test 2: Upload Timeout Investigation
    log_test_result("\nTEST 2: UPLOAD TIMEOUT INVESTIGATION")
    timeout_results = test_upload_timeout_investigation()
    investigation_results['timeout_investigation'] = timeout_results
    
    # Test 3: Duplicate Article Generation (if upload succeeded)
    if timeout_results.get('job_id'):
        log_test_result("\nTEST 3: DUPLICATE ARTICLE GENERATION INVESTIGATION")
        duplicate_results = test_duplicate_article_generation(timeout_results['job_id'])
        investigation_results['duplicate_generation'] = duplicate_results
    
    # Test 4: Content Library Duplicate Check
    log_test_result("\nTEST 4: CONTENT LIBRARY DUPLICATE CHECK")
    library_results = test_content_library_duplicate_check()
    investigation_results['content_library_duplicates'] = library_results
    
    # Test 5: Processing Pipeline Analysis
    log_test_result("\nTEST 5: PROCESSING PIPELINE ANALYSIS")
    pipeline_results = test_processing_pipeline_analysis()
    investigation_results['pipeline_analysis'] = pipeline_results
    
    # Final Analysis and Recommendations
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 CRITICAL INVESTIGATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    # Analyze findings
    critical_issues = []
    
    if timeout_results.get('timeout_detected'):
        critical_issues.append("504 TIMEOUT ERRORS CONFIRMED")
    
    if pipeline_results.get('dual_processing_detected'):
        critical_issues.append("DUAL PROCESSING PIPELINE DETECTED")
    
    if library_results.get('duplicate_titles'):
        critical_issues.append(f"DUPLICATE ARTICLES FOUND: {len(library_results['duplicate_titles'])} sets")
    
    if library_results.get('html_placeholder_issues', 0) > 0:
        critical_issues.append(f"HTML PLACEHOLDER ISSUES: {library_results['html_placeholder_issues']} articles")
    
    if critical_issues:
        log_test_result("🚨 CRITICAL ISSUES CONFIRMED:", "CRITICAL_ERROR")
        for issue in critical_issues:
            log_test_result(f"   - {issue}", "CRITICAL_ERROR")
    else:
        log_test_result("✅ No critical duplicate processing issues detected")
    
    # Recommendations
    log_test_result("\n📋 RECOMMENDATIONS:")
    if pipeline_results.get('dual_processing_detected'):
        log_test_result("   1. URGENT: Disable one of the processing pipelines to prevent duplicates")
        log_test_result("   2. Add mutex/lock to prevent simultaneous processing")
        log_test_result("   3. Review fallback mechanisms that may trigger duplicate processing")
    
    if timeout_results.get('timeout_detected'):
        log_test_result("   4. Optimize processing pipeline to reduce timeout issues")
        log_test_result("   5. Implement async processing with status updates")
        log_test_result("   6. Add processing time limits and graceful degradation")
    
    if library_results.get('html_placeholder_issues', 0) > 0:
        log_test_result("   7. Fix LLM response formatting to prevent HTML placeholders")
        log_test_result("   8. Add content cleaning pipeline for HTML rendering")
    
    return investigation_results

if __name__ == "__main__":
    print("Critical Duplicate Processing Investigation")
    print("=" * 50)
    
    results = run_comprehensive_duplicate_investigation()
    
    # Determine if critical issues were found
    critical_found = (
        results.get('timeout_investigation', {}).get('timeout_detected', False) or
        results.get('pipeline_analysis', {}).get('dual_processing_detected', False) or
        bool(results.get('content_library_duplicates', {}).get('duplicate_titles', {})) or
        results.get('content_library_duplicates', {}).get('html_placeholder_issues', 0) > 0
    )
    
    if critical_found:
        print("\n🚨 CRITICAL ISSUES DETECTED - IMMEDIATE ACTION REQUIRED")
        sys.exit(1)
    else:
        print("\n✅ No critical duplicate processing issues found")
        sys.exit(0)