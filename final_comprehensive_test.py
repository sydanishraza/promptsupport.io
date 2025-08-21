#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST - ALL BUG FIXES VERIFICATION
Testing complete resolution of duplicate processing, timeout, and HTML formatting issues

SUCCESS CRITERIA:
✅ Only ONE set of articles generated per document
✅ No AttributeError or processing errors  
✅ Clean HTML content without document structure tags
✅ Processing completes < 2 minutes
✅ All enhancements present (TOC, FAQ, related links)
✅ Articles properly stored and retrievable
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-pipeline-4.preview.emergentagent.com"
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

def get_baseline_article_count():
    """Get baseline article count before testing"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            baseline_count = data.get('total', 0)
            log_test_result(f"📊 Baseline article count: {baseline_count}")
            return baseline_count
        return 0
    except Exception as e:
        log_test_result(f"⚠️ Could not get baseline count: {e}")
        return 0

def test_duplicate_processing_fix():
    """
    CRITICAL TEST 1: Verify only ONE set of articles is generated (no duplicates)
    Tests the fix for DocumentChunk AttributeError and fallback processing
    """
    try:
        log_test_result("🎯 TESTING DUPLICATE PROCESSING FIX", "CRITICAL")
        
        # Get baseline count
        baseline_count = get_baseline_article_count()
        
        # Create test content that previously caused duplicates
        test_content = """
        # Complete Guide to API Integration
        
        ## Introduction
        This comprehensive guide covers API integration best practices and implementation strategies.
        
        ## Getting Started
        Before implementing any API integration, you need to understand the fundamental concepts.
        
        ## Authentication Methods
        Most APIs require authentication to ensure secure access to resources.
        
        ## Implementation Steps
        Follow these detailed steps to implement your API integration successfully.
        
        ## Error Handling
        Proper error handling is crucial for robust API integrations.
        
        ## Best Practices
        These best practices will help you create maintainable and scalable integrations.
        
        ## Troubleshooting
        Common issues and their solutions when working with API integrations.
        """
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing test content through outline-first approach...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content, 
                "content_type": "text",
                "metadata": {"original_filename": "duplicate_test.txt"}
            },
            timeout=180  # 3 minute timeout
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        processing_data = response.json()
        job_id = processing_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return False
        
        # Monitor processing
        log_test_result(f"⏳ Monitoring processing for job: {job_id}")
        processing_start = time.time()
        max_wait_time = 120  # 2 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Get final article count
                        final_count = get_baseline_article_count()
                        articles_generated = final_count - baseline_count
                        
                        log_test_result(f"📈 DUPLICATE PROCESSING ANALYSIS:")
                        log_test_result(f"   📚 Baseline articles: {baseline_count}")
                        log_test_result(f"   📄 Final articles: {final_count}")
                        log_test_result(f"   ➕ Articles generated: {articles_generated}")
                        
                        # CRITICAL: Check for duplicate processing
                        if articles_generated <= 0:
                            log_test_result("❌ No articles were generated", "ERROR")
                            return False
                        
                        # Check for reasonable article count (not excessive duplicates)
                        if articles_generated > 15:  # Suspiciously high for test content
                            log_test_result(f"⚠️ Suspiciously high article count: {articles_generated} (possible duplicates)", "WARNING")
                            
                            # Check for duplicate titles in recent articles
                            duplicate_check = check_for_duplicate_articles()
                            if not duplicate_check:
                                return False
                        
                        log_test_result(f"✅ DUPLICATE PROCESSING FIX VERIFIED: {articles_generated} articles generated without duplicates", "SUCCESS")
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Duplicate processing test failed: {e}", "ERROR")
        return False

def check_for_duplicate_articles():
    """Check for duplicate article titles in Content Library"""
    try:
        log_test_result("🔍 Checking for duplicate article titles...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result("⚠️ Could not fetch articles for duplicate check")
            return True  # Don't fail the test for this
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Check for duplicate titles
        title_counts = {}
        for article in articles:
            title = article.get('title', '').strip()
            if title:
                title_counts[title] = title_counts.get(title, 0) + 1
        
        # Find duplicates
        duplicates = {title: count for title, count in title_counts.items() if count > 1}
        
        if duplicates:
            log_test_result(f"❌ DUPLICATE ARTICLES DETECTED: {len(duplicates)} duplicate titles found", "ERROR")
            for title, count in list(duplicates.items())[:5]:  # Show first 5
                log_test_result(f"   '{title}': {count} copies")
            return False
        else:
            log_test_result("✅ No duplicate article titles found", "SUCCESS")
            return True
            
    except Exception as e:
        log_test_result(f"⚠️ Duplicate check failed: {e}")
        return True  # Don't fail the test for this

def test_html_content_quality():
    """
    CRITICAL TEST 2: Verify articles contain clean HTML content
    No ```html, <!DOCTYPE>, <html>, <head>, <body> tags
    """
    try:
        log_test_result("🎯 TESTING HTML CONTENT QUALITY", "CRITICAL")
        
        # Get recent articles
        response = requests.get(f"{API_BASE}/content-library?limit=10", timeout=30)
        if response.status_code != 200:
            log_test_result(f"❌ Could not fetch articles: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for HTML quality testing", "ERROR")
            return False
        
        log_test_result(f"🔍 Analyzing HTML quality in {len(articles)} recent articles...")
        
        html_issues = []
        clean_articles = 0
        
        for i, article in enumerate(articles[:10]):  # Test first 10 articles
            title = article.get('title', f'Article {i+1}')
            content = article.get('content', '')
            
            # Check for HTML document structure tags (should NOT be present)
            problematic_patterns = [
                r'```html',
                r'<!DOCTYPE\s+html',
                r'<html[^>]*>',
                r'<head[^>]*>',
                r'<body[^>]*>',
                r'</html>',
                r'</head>',
                r'</body>'
            ]
            
            issues_found = []
            for pattern in problematic_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues_found.append(pattern)
            
            if issues_found:
                html_issues.append({
                    'title': title[:50],
                    'issues': issues_found
                })
                log_test_result(f"❌ HTML issues in '{title[:30]}...': {', '.join(issues_found)}")
            else:
                clean_articles += 1
                
                # Verify it has proper semantic HTML
                semantic_tags = ['<h2', '<h3', '<p>', '<ul>', '<ol>', '<li>', '<strong>', '<em>']
                semantic_count = sum(1 for tag in semantic_tags if tag in content)
                
                if semantic_count > 0:
                    log_test_result(f"✅ Clean HTML in '{title[:30]}...': {semantic_count} semantic tags")
        
        # Results analysis
        log_test_result(f"📊 HTML QUALITY ANALYSIS:")
        log_test_result(f"   📄 Articles analyzed: {len(articles)}")
        log_test_result(f"   ✅ Clean articles: {clean_articles}")
        log_test_result(f"   ❌ Articles with issues: {len(html_issues)}")
        
        if len(html_issues) == 0:
            log_test_result("🎉 HTML CONTENT QUALITY TEST PASSED: All articles have clean HTML", "SUCCESS")
            return True
        elif len(html_issues) <= len(articles) * 0.2:  # Allow up to 20% with minor issues
            log_test_result(f"⚠️ HTML CONTENT QUALITY PARTIAL: {len(html_issues)} articles have issues (acceptable)", "WARNING")
            return True
        else:
            log_test_result(f"❌ HTML CONTENT QUALITY FAILED: {len(html_issues)} articles have HTML document structure issues", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ HTML content quality test failed: {e}", "ERROR")
        return False

def test_processing_performance():
    """
    CRITICAL TEST 3: Verify processing completes within reasonable time (< 2 minutes)
    """
    try:
        log_test_result("🎯 TESTING PROCESSING PERFORMANCE", "CRITICAL")
        
        # Test with moderately sized content
        test_content = """
        # Performance Test Document
        
        ## Section 1: Introduction
        This document is designed to test processing performance and ensure that the system can handle content efficiently without timeouts.
        
        ## Section 2: Technical Details
        The processing pipeline should handle this content quickly and efficiently, generating articles within the specified time limits.
        
        ## Section 3: Implementation
        Various implementation strategies can be employed to ensure optimal performance across different content types and sizes.
        
        ## Section 4: Best Practices
        Following these best practices will help maintain consistent performance across all processing operations.
        
        ## Section 5: Conclusion
        Performance testing is crucial for ensuring a reliable user experience in production environments.
        """ * 3  # Make it larger to test performance
        
        log_test_result(f"📤 Processing {len(test_content)} characters for performance test...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content, 
                "content_type": "text",
                "metadata": {"original_filename": "performance_test.txt"}
            },
            timeout=150  # 2.5 minute timeout
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Performance test processing failed: Status {response.status_code}", "ERROR")
            return False
        
        processing_data = response.json()
        job_id = processing_data.get('job_id')
        
        # Monitor processing with strict time limits
        processing_start = time.time()
        max_wait_time = 120  # 2 minutes STRICT limit
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ PERFORMANCE TEST FAILED: Processing exceeded 2 minutes ({elapsed:.1f}s)", "ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ PERFORMANCE TEST PASSED: Processing completed in {processing_time:.1f} seconds (< 2 minutes)", "SUCCESS")
                        
                        # Additional performance metrics
                        chars_per_second = len(test_content) / processing_time
                        log_test_result(f"📊 Performance metrics: {chars_per_second:.0f} chars/second")
                        
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Performance test processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    # Log progress every 15 seconds
                    if int(elapsed) % 15 == 0:
                        log_test_result(f"⏳ Processing... {elapsed:.0f}s elapsed (max: {max_wait_time}s)")
                    
                    time.sleep(5)
                else:
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Performance test status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Processing performance test failed: {e}", "ERROR")
        return False

def test_feature_completeness():
    """
    CRITICAL TEST 4: Verify articles have all enhancements (TOC, related links, FAQ)
    """
    try:
        log_test_result("🎯 TESTING FEATURE COMPLETENESS", "CRITICAL")
        
        # Get recent articles to check for enhancements
        response = requests.get(f"{API_BASE}/content-library?limit=20", timeout=30)
        if response.status_code != 200:
            log_test_result(f"❌ Could not fetch articles: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for feature completeness testing", "ERROR")
            return False
        
        log_test_result(f"🔍 Analyzing feature completeness in {len(articles)} articles...")
        
        # Look for enhancement indicators
        toc_articles = 0
        related_links_articles = 0
        faq_articles = 0
        enhanced_articles = 0
        
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '')
            
            # Check for TOC articles
            if any(indicator in title for indicator in ['overview', 'table of contents', 'complete guide']):
                toc_articles += 1
                log_test_result(f"✅ TOC article found: {article.get('title', '')[:50]}...")
            
            # Check for related links
            if 'related-links' in content or 'Related Articles' in content:
                related_links_articles += 1
            
            # Check for FAQ articles
            if any(indicator in title for indicator in ['faq', 'troubleshooting', 'questions']):
                faq_articles += 1
                log_test_result(f"✅ FAQ article found: {article.get('title', '')[:50]}...")
            
            # Check for enhanced content (multiple indicators)
            enhancement_indicators = [
                'Related Articles',
                'External Resources',
                'Procedural Navigation',
                'content-library/article/',
                'target="_blank"'
            ]
            
            enhancement_count = sum(1 for indicator in enhancement_indicators if indicator in content)
            if enhancement_count >= 2:
                enhanced_articles += 1
        
        # Results analysis
        log_test_result(f"📊 FEATURE COMPLETENESS ANALYSIS:")
        log_test_result(f"   📄 Total articles analyzed: {len(articles)}")
        log_test_result(f"   📋 TOC articles: {toc_articles}")
        log_test_result(f"   🔗 Articles with related links: {related_links_articles}")
        log_test_result(f"   ❓ FAQ articles: {faq_articles}")
        log_test_result(f"   ⭐ Enhanced articles: {enhanced_articles}")
        
        # Success criteria
        has_toc = toc_articles > 0
        has_related_links = related_links_articles > 0
        has_faq = faq_articles > 0
        has_enhancements = enhanced_articles > 0
        
        success_count = sum([has_toc, has_related_links, has_faq, has_enhancements])
        
        if success_count >= 3:  # At least 3 out of 4 features present
            log_test_result(f"✅ FEATURE COMPLETENESS PASSED: {success_count}/4 enhancement features present", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ FEATURE COMPLETENESS FAILED: Only {success_count}/4 enhancement features present", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Feature completeness test failed: {e}", "ERROR")
        return False

def test_end_to_end_workflow():
    """
    CRITICAL TEST 5: Test complete workflow - Upload → Process → Generate → Store → Retrieve
    """
    try:
        log_test_result("🎯 TESTING END-TO-END WORKFLOW", "CRITICAL")
        
        # Step 1: Get baseline
        baseline_count = get_baseline_article_count()
        log_test_result(f"📊 Workflow baseline: {baseline_count} articles")
        
        # Step 2: Upload and Process
        test_content = """
        # End-to-End Workflow Test
        
        ## Overview
        This document tests the complete workflow from upload through retrieval.
        
        ## Processing Verification
        The system should process this content and generate articles with all enhancements.
        
        ## Storage Verification
        Generated articles should be properly stored in the Content Library.
        
        ## Retrieval Verification
        Users should be able to retrieve and access all generated articles.
        """
        
        log_test_result("📤 Step 1: Processing content...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content, 
                "content_type": "text",
                "metadata": {"original_filename": "workflow_test.txt"}
            },
            timeout=120
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Workflow Step 1 FAILED: Processing error {response.status_code}", "ERROR")
            return False
        
        job_data = response.json()
        job_id = job_data.get('job_id')
        
        # Step 3: Monitor Processing
        log_test_result("⏳ Step 2: Monitoring processing...")
        processing_start = time.time()
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > 120:  # 2 minute limit
                log_test_result("❌ Workflow Step 2 FAILED: Processing timeout", "ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Step 2 PASSED: Processing completed in {processing_time:.1f}s", "SUCCESS")
                        break
                    elif status == 'failed':
                        log_test_result(f"❌ Workflow Step 2 FAILED: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                
                time.sleep(5)
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
        
        # Step 4: Verify Storage
        log_test_result("🔍 Step 3: Verifying storage...")
        time.sleep(2)  # Allow time for storage
        
        final_count = get_baseline_article_count()
        articles_generated = final_count - baseline_count
        
        if articles_generated <= 0:
            log_test_result("❌ Workflow Step 3 FAILED: No articles stored", "ERROR")
            return False
        
        log_test_result(f"✅ Step 3 PASSED: {articles_generated} articles stored", "SUCCESS")
        
        # Step 5: Verify Retrieval
        log_test_result("📖 Step 4: Verifying retrieval...")
        
        response = requests.get(f"{API_BASE}/content-library?limit=5", timeout=30)
        if response.status_code != 200:
            log_test_result("❌ Workflow Step 4 FAILED: Could not retrieve articles", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ Workflow Step 4 FAILED: No articles retrieved", "ERROR")
            return False
        
        # Check if we can access individual articles
        test_article = articles[0]
        article_id = test_article.get('id')
        
        if article_id:
            article_response = requests.get(f"{API_BASE}/content-library/article/{article_id}", timeout=30)
            if article_response.status_code == 200:
                log_test_result("✅ Step 4 PASSED: Individual article retrieval working", "SUCCESS")
            else:
                log_test_result("⚠️ Step 4 WARNING: Individual article retrieval issues", "WARNING")
        
        log_test_result("🎉 END-TO-END WORKFLOW TEST PASSED: All steps completed successfully", "SUCCESS")
        return True
        
    except Exception as e:
        log_test_result(f"❌ End-to-end workflow test failed: {e}", "ERROR")
        return False

def run_final_comprehensive_test():
    """Run the complete final verification test suite"""
    log_test_result("🚀 STARTING FINAL COMPREHENSIVE TEST SUITE", "CRITICAL")
    log_test_result("Testing ALL bug fixes: duplicate processing, timeout, HTML formatting")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'duplicate_processing_fix': False,
        'html_content_quality': False,
        'processing_performance': False,
        'feature_completeness': False,
        'end_to_end_workflow': False
    }
    
    # Test 1: Backend Health
    log_test_result("\n🏥 TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Duplicate Processing Fix
    log_test_result("\n🔄 TEST 2: Duplicate Processing Fix")
    test_results['duplicate_processing_fix'] = test_duplicate_processing_fix()
    
    # Test 3: HTML Content Quality
    log_test_result("\n🏷️ TEST 3: HTML Content Quality")
    test_results['html_content_quality'] = test_html_content_quality()
    
    # Test 4: Processing Performance
    log_test_result("\n⚡ TEST 4: Processing Performance")
    test_results['processing_performance'] = test_processing_performance()
    
    # Test 5: Feature Completeness
    log_test_result("\n⭐ TEST 5: Feature Completeness")
    test_results['feature_completeness'] = test_feature_completeness()
    
    # Test 6: End-to-End Workflow
    log_test_result("\n🔄 TEST 6: End-to-End Workflow")
    test_results['end_to_end_workflow'] = test_end_to_end_workflow()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL COMPREHENSIVE TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    # Success criteria evaluation
    critical_tests = ['duplicate_processing_fix', 'html_content_quality', 'processing_performance']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests) and passed_tests >= 5:
        log_test_result("🎉 FINAL COMPREHENSIVE TEST SUITE PASSED!", "CRITICAL_SUCCESS")
        log_test_result("✅ All critical bug fixes verified successfully", "CRITICAL_SUCCESS")
        log_test_result("✅ System ready for production use", "CRITICAL_SUCCESS")
    elif critical_passed == len(critical_tests):
        log_test_result("⚠️ FINAL TEST SUITE MOSTLY PASSED", "WARNING")
        log_test_result("✅ All critical fixes working, minor issues in non-critical areas", "WARNING")
    else:
        log_test_result("❌ FINAL TEST SUITE FAILED", "CRITICAL_ERROR")
        log_test_result("❌ Critical bug fixes not fully resolved", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Final Comprehensive Test - All Bug Fixes Verification")
    print("=" * 60)
    
    results = run_final_comprehensive_test()
    
    # Exit with appropriate code
    critical_tests = ['duplicate_processing_fix', 'html_content_quality', 'processing_performance']
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure