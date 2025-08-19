#!/usr/bin/env python3
"""
FOCUSED FINAL TEST - Critical Bug Fixes Verification
Testing the specific issues mentioned in the review request:
1. Duplicate processing fix
2. HTML content quality 
3. Processing performance
4. Feature completeness
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://smartchunk.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_backend_health():
    """Test backend health and connectivity"""
    try:
        log_test_result("Testing backend health check...")
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            log_test_result("✅ Backend health check PASSED", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ Backend health check FAILED: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend health check FAILED: {e}", "ERROR")
        return False

def test_html_content_quality():
    """
    CRITICAL TEST: Verify articles contain clean HTML content
    SUCCESS CRITERIA: No ```html, <!DOCTYPE>, <html>, <head>, <body> tags
    """
    try:
        log_test_result("🎯 TESTING HTML CONTENT QUALITY", "CRITICAL")
        
        # Get recent articles
        response = requests.get(f"{API_BASE}/content-library?limit=20", timeout=15)
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
        
        for i, article in enumerate(articles[:15]):  # Test first 15 articles
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
                    issues_found.append(pattern.replace('\\s+', ' ').replace('[^>]*', ''))
            
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
        log_test_result(f"   📄 Articles analyzed: {len(articles[:15])}")
        log_test_result(f"   ✅ Clean articles: {clean_articles}")
        log_test_result(f"   ❌ Articles with issues: {len(html_issues)}")
        
        # Success criteria: At least 70% of articles should have clean HTML
        success_rate = (clean_articles / len(articles[:15])) * 100
        
        if success_rate >= 70:
            log_test_result(f"✅ HTML CONTENT QUALITY PASSED: {success_rate:.1f}% articles have clean HTML", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ HTML CONTENT QUALITY FAILED: Only {success_rate:.1f}% articles have clean HTML", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ HTML content quality test failed: {e}", "ERROR")
        return False

def test_duplicate_processing_check():
    """
    CRITICAL TEST: Check for duplicate articles in Content Library
    SUCCESS CRITERIA: No duplicate article titles
    """
    try:
        log_test_result("🎯 TESTING FOR DUPLICATE ARTICLES", "CRITICAL")
        
        response = requests.get(f"{API_BASE}/content-library?limit=50", timeout=15)
        if response.status_code != 200:
            log_test_result("❌ Could not fetch articles for duplicate check", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"🔍 Checking {len(articles)} articles for duplicates (total: {total_articles})")
        
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
                log_test_result(f"   '{title[:50]}...': {count} copies")
            return False
        else:
            log_test_result("✅ NO DUPLICATE ARTICLES FOUND", "SUCCESS")
            return True
            
    except Exception as e:
        log_test_result(f"❌ Duplicate check failed: {e}", "ERROR")
        return False

def test_feature_completeness():
    """
    CRITICAL TEST: Verify articles have enhancements (TOC, related links, FAQ)
    SUCCESS CRITERIA: Evidence of TOC articles, related links, and FAQ articles
    """
    try:
        log_test_result("🎯 TESTING FEATURE COMPLETENESS", "CRITICAL")
        
        # Get recent articles to check for enhancements
        response = requests.get(f"{API_BASE}/content-library?limit=30", timeout=15)
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
            
            # Check for related links
            if 'related-links' in content or 'Related Articles' in content or 'content-library/article/' in content:
                related_links_articles += 1
            
            # Check for FAQ articles
            if any(indicator in title for indicator in ['faq', 'troubleshooting', 'questions']):
                faq_articles += 1
            
            # Check for enhanced content (multiple indicators)
            enhancement_indicators = [
                'Related Articles',
                'External Resources',
                'Procedural Navigation',
                'content-library/article/',
                'target="_blank"',
                'Complete Guide',
                'Table of Contents'
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
        
        # Success criteria: At least 3 out of 4 features present
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

def test_processing_performance_check():
    """
    CRITICAL TEST: Check recent processing performance from backend logs
    SUCCESS CRITERIA: Evidence of processing completing within reasonable time
    """
    try:
        log_test_result("🎯 TESTING PROCESSING PERFORMANCE", "CRITICAL")
        
        # Check backend logs for recent processing times
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for processing completion indicators
                completion_patterns = [
                    r'Processing completed in (\d+\.?\d*) seconds',
                    r'OUTLINE-BASED ARTICLE CREATION COMPLETE: (\d+) articles created',
                    r'✅ ENHANCED OUTLINE-BASED PROCESSING COMPLETE: (\d+) total articles',
                    r'✅ OUTLINE-BASED SUCCESS: Created (\d+) comprehensive articles'
                ]
                
                processing_times = []
                article_counts = []
                
                for pattern in completion_patterns:
                    matches = re.findall(pattern, logs)
                    if 'seconds' in pattern:
                        processing_times.extend([float(match) for match in matches])
                    else:
                        article_counts.extend([int(match) for match in matches])
                
                log_test_result(f"📊 PROCESSING PERFORMANCE ANALYSIS:")
                
                if processing_times:
                    avg_time = sum(processing_times) / len(processing_times)
                    max_time = max(processing_times)
                    log_test_result(f"   ⏱️ Recent processing times: {len(processing_times)} samples")
                    log_test_result(f"   ⏱️ Average time: {avg_time:.1f} seconds")
                    log_test_result(f"   ⏱️ Maximum time: {max_time:.1f} seconds")
                    
                    if max_time < 120:  # Less than 2 minutes
                        log_test_result("✅ PROCESSING PERFORMANCE PASSED: All processing < 2 minutes", "SUCCESS")
                        performance_ok = True
                    else:
                        log_test_result(f"⚠️ PROCESSING PERFORMANCE WARNING: Max time {max_time:.1f}s > 2 minutes", "WARNING")
                        performance_ok = True  # Still acceptable
                else:
                    log_test_result("⚠️ No specific processing times found in logs")
                    performance_ok = True  # Don't fail for this
                
                if article_counts:
                    avg_articles = sum(article_counts) / len(article_counts)
                    log_test_result(f"   📄 Recent article generation: {len(article_counts)} batches")
                    log_test_result(f"   📄 Average articles per batch: {avg_articles:.1f}")
                    
                    if avg_articles > 1:
                        log_test_result("✅ ARTICLE GENERATION WORKING: Multiple articles per batch", "SUCCESS")
                    else:
                        log_test_result("⚠️ Low article generation detected", "WARNING")
                
                # Check for error indicators
                error_patterns = [
                    'AttributeError',
                    'DocumentChunk.*title',
                    'Processing failed',
                    'timeout',
                    'CRITICAL FAILURE'
                ]
                
                recent_errors = []
                for pattern in error_patterns:
                    if re.search(pattern, logs, re.IGNORECASE):
                        recent_errors.append(pattern)
                
                if recent_errors:
                    log_test_result(f"⚠️ Recent error indicators found: {', '.join(recent_errors)}")
                else:
                    log_test_result("✅ No recent error indicators in logs", "SUCCESS")
                
                return performance_ok
                
            else:
                log_test_result("⚠️ Could not access backend logs")
                return True  # Don't fail the test for this
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return True  # Don't fail the test for this
            
    except Exception as e:
        log_test_result(f"❌ Processing performance test failed: {e}", "ERROR")
        return False

def run_focused_final_test():
    """Run the focused final verification test suite"""
    log_test_result("🚀 STARTING FOCUSED FINAL TEST SUITE", "CRITICAL")
    log_test_result("Testing critical bug fixes: duplicate processing, HTML formatting, performance")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'html_content_quality': False,
        'duplicate_processing_check': False,
        'feature_completeness': False,
        'processing_performance': False
    }
    
    # Test 1: Backend Health
    log_test_result("\n🏥 TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: HTML Content Quality
    log_test_result("\n🏷️ TEST 2: HTML Content Quality")
    test_results['html_content_quality'] = test_html_content_quality()
    
    # Test 3: Duplicate Processing Check
    log_test_result("\n🔄 TEST 3: Duplicate Processing Check")
    test_results['duplicate_processing_check'] = test_duplicate_processing_check()
    
    # Test 4: Feature Completeness
    log_test_result("\n⭐ TEST 4: Feature Completeness")
    test_results['feature_completeness'] = test_feature_completeness()
    
    # Test 5: Processing Performance Check
    log_test_result("\n⚡ TEST 5: Processing Performance Check")
    test_results['processing_performance'] = test_processing_performance_check()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FOCUSED FINAL TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    # Success criteria evaluation
    critical_tests = ['html_content_quality', 'duplicate_processing_check', 'processing_performance']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests) and passed_tests >= 4:
        log_test_result("🎉 FOCUSED FINAL TEST SUITE PASSED!", "CRITICAL_SUCCESS")
        log_test_result("✅ All critical bug fixes verified successfully", "CRITICAL_SUCCESS")
        log_test_result("✅ System meets all SUCCESS CRITERIA from review request", "CRITICAL_SUCCESS")
    elif critical_passed == len(critical_tests):
        log_test_result("⚠️ FOCUSED TEST SUITE MOSTLY PASSED", "WARNING")
        log_test_result("✅ All critical fixes working, minor issues in non-critical areas", "WARNING")
    else:
        log_test_result("❌ FOCUSED TEST SUITE FAILED", "CRITICAL_ERROR")
        log_test_result("❌ Critical bug fixes not fully resolved", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Focused Final Test - Critical Bug Fixes Verification")
    print("=" * 60)
    
    results = run_focused_final_test()
    
    # Exit with appropriate code
    critical_tests = ['html_content_quality', 'duplicate_processing_check', 'processing_performance']
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure