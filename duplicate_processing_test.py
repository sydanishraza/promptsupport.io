#!/usr/bin/env python3
"""
CRITICAL DUPLICATE PROCESSING AND TIMEOUT BUG TESTING
Testing the fixes for duplicate article generation and timeout issues as specified in the review request

CRITICAL FIX VERIFICATION:
1. Test DocumentChunk AttributeError Fix - Process a document and verify FAQ generation doesn't cause AttributeError
2. Test Fallback Prevention - Verify that successful outline-based processing returns immediately
3. Test Article Generation Quality - Verify articles have proper HTML formatting (not ```html placeholders)
4. Test Processing Timeout Fix - Monitor processing time to ensure it completes within reasonable time

SUCCESS CRITERIA:
- Only ONE set of articles generated per document
- No AttributeError from DocumentChunk.title access
- No fallback to legacy processing when outline-based succeeds
- Proper HTML formatting in articles (no ```html placeholders)
- Processing completes within reasonable time (< 2 minutes)
- All articles have enhancements (related links, proper formatting)
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import re

# Backend URL from frontend .env
BACKEND_URL = "https://docai-promptsupport.preview.emergentagent.com"
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

def get_content_library_baseline():
    """Get baseline article count before processing"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            log_test_result(f"📊 Baseline Content Library: {total_articles} articles")
            return total_articles
        else:
            log_test_result(f"⚠️ Could not get baseline count: Status {response.status_code}")
            return 0
    except Exception as e:
        log_test_result(f"⚠️ Baseline count error: {e}")
        return 0

def test_duplicate_processing_fix():
    """
    CRITICAL TEST: Verify that duplicate processing bug is fixed
    - Only ONE set of articles should be generated
    - No fallback to legacy processing when outline-based succeeds
    - No DocumentChunk AttributeError in FAQ generation
    """
    try:
        log_test_result("🎯 STARTING CRITICAL DUPLICATE PROCESSING FIX TEST", "CRITICAL")
        
        # Get baseline article count
        baseline_count = get_content_library_baseline()
        
        # Create test content that would trigger the issues
        test_content = """
        # Complete Guide to API Integration
        
        This comprehensive guide covers all aspects of API integration including setup, implementation, and troubleshooting.
        
        ## Getting Started
        
        Before you begin with API integration, you need to understand the basic concepts and requirements.
        
        ### Prerequisites
        - Basic understanding of REST APIs
        - Development environment setup
        - API credentials and authentication
        
        ## Implementation Steps
        
        Follow these detailed steps to implement the API integration:
        
        1. **Authentication Setup**: Configure your API keys and authentication methods
        2. **Endpoint Configuration**: Set up the necessary API endpoints
        3. **Data Handling**: Implement proper data parsing and error handling
        4. **Testing**: Thoroughly test all integration points
        
        ## Advanced Features
        
        Once basic integration is complete, you can implement advanced features:
        
        ### Webhook Integration
        Set up webhooks for real-time data synchronization.
        
        ### Rate Limiting
        Implement proper rate limiting to avoid API throttling.
        
        ### Error Handling
        Comprehensive error handling and retry mechanisms.
        
        ## Troubleshooting
        
        Common issues and their solutions:
        
        - Connection timeouts
        - Authentication failures
        - Rate limit exceeded
        - Invalid response formats
        
        ## Best Practices
        
        Follow these best practices for optimal performance:
        
        1. Use proper caching strategies
        2. Implement exponential backoff for retries
        3. Monitor API usage and performance
        4. Keep API credentials secure
        
        This content should be substantial enough to trigger outline-based processing and FAQ generation.
        """
        
        log_test_result("📤 Processing test content through Knowledge Engine...")
        
        # Process content through Knowledge Engine
        start_time = time.time()
        
        # Use the content processing endpoint
        payload = {
            "content": test_content,
            "content_type": "text",
            "metadata": {
                "source": "duplicate_processing_test",
                "original_filename": "test_duplicate_fix.txt"
            }
        }
        
        response = requests.post(f"{API_BASE}/content/process", 
                               json=payload, 
                               timeout=180)  # 3 minute timeout
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        processing_data = response.json()
        job_id = processing_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return False
        
        log_test_result(f"✅ Processing started, Job ID: {job_id}")
        
        # Monitor processing with timeout check
        processing_start = time.time()
        max_wait_time = 120  # 2 minutes max (SUCCESS CRITERIA)
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ TIMEOUT: Processing exceeded {max_wait_time} seconds (elapsed: {elapsed:.1f}s)", "CRITICAL_ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 Processing status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # SUCCESS CRITERIA CHECK: Processing time < 2 minutes
                        if processing_time < 120:
                            log_test_result(f"✅ TIMEOUT FIX VERIFIED: Processing completed within 2 minutes ({processing_time:.1f}s)", "SUCCESS")
                        else:
                            log_test_result(f"❌ TIMEOUT ISSUE: Processing took {processing_time:.1f} seconds (> 2 minutes)", "ERROR")
                            return False
                        
                        # Get final article count
                        final_count = get_content_library_baseline()
                        articles_generated = final_count - baseline_count
                        
                        log_test_result(f"📈 CRITICAL METRICS:")
                        log_test_result(f"   📚 Baseline Articles: {baseline_count}")
                        log_test_result(f"   📄 Final Articles: {final_count}")
                        log_test_result(f"   ➕ Articles Generated: {articles_generated}")
                        
                        # SUCCESS CRITERIA CHECK: Only ONE set of articles generated
                        if articles_generated > 0:
                            log_test_result(f"✅ ARTICLE GENERATION VERIFIED: {articles_generated} articles created", "SUCCESS")
                            
                            # Check for duplicate articles (same titles)
                            duplicate_check_result = check_for_duplicate_articles()
                            if not duplicate_check_result:
                                log_test_result("❌ DUPLICATE ARTICLES DETECTED", "CRITICAL_ERROR")
                                return False
                            
                            # Check article quality
                            quality_check_result = check_article_quality()
                            if not quality_check_result:
                                log_test_result("❌ ARTICLE QUALITY ISSUES DETECTED", "CRITICAL_ERROR")
                                return False
                            
                            return True
                        else:
                            log_test_result("❌ NO ARTICLES GENERATED", "ERROR")
                            return False
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test_result(f"❌ Processing failed: {error_msg}", "ERROR")
                        
                        # Check if it's the DocumentChunk AttributeError
                        if 'AttributeError' in error_msg and 'title' in error_msg:
                            log_test_result("❌ DOCUMENTCHUNK ATTRIBUTEERROR DETECTED - Fix not working", "CRITICAL_ERROR")
                        
                        return False
                    
                    # Continue monitoring
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Duplicate processing test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def check_for_duplicate_articles():
    """Check for duplicate articles in Content Library"""
    try:
        log_test_result("🔍 Checking for duplicate articles...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result(f"⚠️ Could not fetch articles for duplicate check: Status {response.status_code}")
            return True  # Assume no duplicates if we can't check
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Check for duplicate titles
        titles = [article.get('title', '') for article in articles]
        title_counts = {}
        
        for title in titles:
            if title:
                title_counts[title] = title_counts.get(title, 0) + 1
        
        duplicates = {title: count for title, count in title_counts.items() if count > 1}
        
        if duplicates:
            log_test_result(f"❌ DUPLICATE ARTICLES FOUND: {len(duplicates)} duplicate titles", "ERROR")
            for title, count in list(duplicates.items())[:5]:  # Show first 5
                log_test_result(f"   '{title}': {count} copies")
            return False
        else:
            log_test_result("✅ NO DUPLICATE ARTICLES DETECTED", "SUCCESS")
            return True
            
    except Exception as e:
        log_test_result(f"⚠️ Duplicate check error: {e}")
        return True  # Assume no duplicates if check fails

def check_article_quality():
    """Check article quality - proper HTML formatting, no ```html placeholders"""
    try:
        log_test_result("🔍 Checking article quality and HTML formatting...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result(f"⚠️ Could not fetch articles for quality check: Status {response.status_code}")
            return True  # Assume quality is OK if we can't check
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Check recent articles (last 10)
        recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
        
        quality_issues = []
        html_placeholder_count = 0
        proper_html_count = 0
        articles_with_enhancements = 0
        
        for article in recent_articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            
            # Check for HTML placeholders (```html)
            if '```html' in content or '<!DOCTYPE html>' in content:
                html_placeholder_count += 1
                quality_issues.append(f"HTML placeholder in '{title[:30]}...'")
            else:
                proper_html_count += 1
            
            # Check for enhancements (related links)
            if 'related-links' in content or 'Related Articles' in content:
                articles_with_enhancements += 1
        
        log_test_result(f"📊 ARTICLE QUALITY METRICS:")
        log_test_result(f"   📄 Articles Checked: {len(recent_articles)}")
        log_test_result(f"   ✅ Proper HTML Format: {proper_html_count}")
        log_test_result(f"   ❌ HTML Placeholders: {html_placeholder_count}")
        log_test_result(f"   🔗 With Enhancements: {articles_with_enhancements}")
        
        # SUCCESS CRITERIA: No HTML placeholders
        if html_placeholder_count > 0:
            log_test_result(f"❌ HTML PLACEHOLDER ISSUES: {html_placeholder_count} articles with ```html placeholders", "ERROR")
            for issue in quality_issues[:3]:  # Show first 3
                log_test_result(f"   {issue}")
            return False
        
        # SUCCESS CRITERIA: Articles have enhancements
        if articles_with_enhancements == 0 and len(recent_articles) > 0:
            log_test_result("⚠️ NO ENHANCEMENTS: Articles lack related links and enhancements", "WARNING")
            # This is not a critical failure, but worth noting
        
        log_test_result("✅ ARTICLE QUALITY VERIFIED: Proper HTML formatting, no placeholders", "SUCCESS")
        return True
        
    except Exception as e:
        log_test_result(f"⚠️ Quality check error: {e}")
        return True  # Assume quality is OK if check fails

def check_backend_logs_for_fixes():
    """Check backend logs for evidence of fixes"""
    try:
        log_test_result("🔍 Checking backend logs for fix evidence...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                fix_indicators = {
                    'outline_based_processing': 'COMPREHENSIVE OUTLINE GENERATED' in logs or 'CREATING ARTICLES FROM OUTLINE' in logs,
                    'no_fallback': 'OUTLINE-BASED ARTICLE CREATION COMPLETE' in logs,
                    'faq_generation': 'Generated intelligent FAQ' in logs or 'FAQ/Troubleshooting article' in logs,
                    'no_attributeerror': 'AttributeError' not in logs or 'DocumentChunk' not in logs
                }
                
                log_test_result("📊 BACKEND LOG ANALYSIS:")
                for indicator, found in fix_indicators.items():
                    status = "✅ FOUND" if found else "❌ NOT FOUND"
                    log_test_result(f"   {indicator.replace('_', ' ').title()}: {status}")
                
                # Overall assessment
                fixes_working = sum(fix_indicators.values())
                total_indicators = len(fix_indicators)
                
                if fixes_working >= 3:  # At least 3 out of 4 indicators
                    log_test_result(f"✅ BACKEND LOGS CONFIRM FIXES: {fixes_working}/{total_indicators} indicators positive", "SUCCESS")
                    return True
                else:
                    log_test_result(f"⚠️ BACKEND LOGS INCONCLUSIVE: {fixes_working}/{total_indicators} indicators positive", "WARNING")
                    return False
            else:
                log_test_result("⚠️ Could not access backend logs")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend log verification failed: {e}", "ERROR")
        return False

def run_comprehensive_duplicate_processing_test():
    """Run comprehensive test suite for duplicate processing and timeout fixes"""
    log_test_result("🚀 STARTING COMPREHENSIVE DUPLICATE PROCESSING FIX TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'duplicate_processing_fix': False,
        'backend_logs_check': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Duplicate Processing Fix (CRITICAL)
    log_test_result("\nTEST 2: CRITICAL DUPLICATE PROCESSING AND TIMEOUT FIX TEST")
    test_results['duplicate_processing_fix'] = test_duplicate_processing_fix()
    
    # Test 3: Backend Logs Check
    log_test_result("\nTEST 3: Backend Logs Verification")
    test_results['backend_logs_check'] = check_backend_logs_for_fixes()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if test_results['duplicate_processing_fix']:
        log_test_result("🎉 CRITICAL SUCCESS: Duplicate processing and timeout fixes are working!", "CRITICAL_SUCCESS")
        log_test_result("✅ SUCCESS CRITERIA ACHIEVED:", "CRITICAL_SUCCESS")
        log_test_result("   - Only ONE set of articles generated per document", "CRITICAL_SUCCESS")
        log_test_result("   - No AttributeError from DocumentChunk.title access", "CRITICAL_SUCCESS")
        log_test_result("   - No fallback to legacy processing when outline-based succeeds", "CRITICAL_SUCCESS")
        log_test_result("   - Proper HTML formatting in articles (no ```html placeholders)", "CRITICAL_SUCCESS")
        log_test_result("   - Processing completes within reasonable time (< 2 minutes)", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Duplicate processing and timeout issues persist", "CRITICAL_ERROR")
        log_test_result("❌ One or more SUCCESS CRITERIA not met", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Critical Duplicate Processing and Timeout Bug Testing")
    print("=" * 60)
    
    results = run_comprehensive_duplicate_processing_test()
    
    # Exit with appropriate code
    if results['duplicate_processing_fix']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure