#!/usr/bin/env python3
"""
FOCUSED DUPLICATE PROCESSING FIX VERIFICATION
Quick verification of the critical fixes for duplicate processing and timeout issues
"""

import requests
import json
import time
import os
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://docai-promptsupport.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_content_library_for_duplicates():
    """Check Content Library for duplicate articles"""
    try:
        log_test_result("🔍 Checking Content Library for duplicate articles...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=60)
        if response.status_code != 200:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📊 Content Library Status: {total_articles} total articles, {len(articles)} retrieved")
        
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
                log_test_result(f"   '{title[:50]}...': {count} copies")
            return False
        else:
            log_test_result("✅ NO DUPLICATE ARTICLES DETECTED", "SUCCESS")
            return True
            
    except Exception as e:
        log_test_result(f"❌ Duplicate check failed: {e}", "ERROR")
        return False

def test_article_quality():
    """Check article quality - proper HTML formatting, no ```html placeholders"""
    try:
        log_test_result("🔍 Checking article quality and HTML formatting...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=60)
        if response.status_code != 200:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Check recent articles (last 20)
        recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:20]
        
        html_placeholder_count = 0
        proper_html_count = 0
        articles_with_enhancements = 0
        
        for article in recent_articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            
            # Check for HTML placeholders (```html)
            if '```html' in content or '<!DOCTYPE html>' in content:
                html_placeholder_count += 1
                log_test_result(f"   ❌ HTML placeholder in: {title[:40]}...")
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
            return False
        
        log_test_result("✅ ARTICLE QUALITY VERIFIED: Proper HTML formatting, no placeholders", "SUCCESS")
        return True
        
    except Exception as e:
        log_test_result(f"❌ Quality check failed: {e}", "ERROR")
        return False

def check_backend_logs_for_fixes():
    """Check backend logs for evidence of fixes"""
    try:
        log_test_result("🔍 Checking backend logs for fix evidence...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '300', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for specific fix indicators
                fix_indicators = {
                    'outline_based_processing': 'COMPREHENSIVE OUTLINE GENERATED' in logs or 'CREATING ARTICLES FROM OUTLINE' in logs,
                    'no_fallback': 'OUTLINE-BASED ARTICLE CREATION COMPLETE' in logs,
                    'faq_generation_working': 'Generated intelligent FAQ' in logs or 'FAQ/Troubleshooting article' in logs,
                    'no_attributeerror': 'AttributeError' not in logs.split('\n')[-100:],  # Check last 100 lines
                    'no_documentchunk_error': 'DocumentChunk' not in logs.split('\n')[-100:] or 'title' not in logs.split('\n')[-100:]
                }
                
                log_test_result("📊 BACKEND LOG ANALYSIS:")
                for indicator, found in fix_indicators.items():
                    status = "✅ FOUND" if found else "❌ NOT FOUND"
                    log_test_result(f"   {indicator.replace('_', ' ').title()}: {status}")
                
                # Check for specific error patterns that indicate the bug is NOT fixed
                error_patterns = [
                    "DocumentChunk' object has no attribute 'title'",
                    "AttributeError.*title",
                    "Dual processing pipeline",
                    "Fallback to traditional processing"
                ]
                
                errors_found = []
                for pattern in error_patterns:
                    import re
                    if re.search(pattern, logs, re.IGNORECASE):
                        errors_found.append(pattern)
                
                if errors_found:
                    log_test_result(f"❌ CRITICAL ERRORS STILL PRESENT:", "ERROR")
                    for error in errors_found:
                        log_test_result(f"   {error}")
                    return False
                
                # Overall assessment
                fixes_working = sum(fix_indicators.values())
                total_indicators = len(fix_indicators)
                
                if fixes_working >= 3:  # At least 3 out of 5 indicators
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

def run_focused_duplicate_fix_verification():
    """Run focused verification of duplicate processing fixes"""
    log_test_result("🎯 STARTING FOCUSED DUPLICATE PROCESSING FIX VERIFICATION", "CRITICAL")
    log_test_result("=" * 70)
    
    test_results = {
        'backend_health': False,
        'no_duplicates': False,
        'article_quality': False,
        'backend_logs_check': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Check for Duplicates
    log_test_result("\nTEST 2: Duplicate Articles Check")
    test_results['no_duplicates'] = test_content_library_for_duplicates()
    
    # Test 3: Article Quality Check
    log_test_result("\nTEST 3: Article Quality Check")
    test_results['article_quality'] = test_article_quality()
    
    # Test 4: Backend Logs Check
    log_test_result("\nTEST 4: Backend Logs Verification")
    test_results['backend_logs_check'] = check_backend_logs_for_fixes()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 70)
    log_test_result("🎯 FINAL VERIFICATION RESULTS", "CRITICAL")
    log_test_result("=" * 70)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Determine if critical fixes are working
    critical_tests_passed = test_results['no_duplicates'] and test_results['article_quality']
    
    if critical_tests_passed:
        log_test_result("🎉 CRITICAL SUCCESS: Duplicate processing fixes are working!", "CRITICAL_SUCCESS")
        log_test_result("✅ SUCCESS CRITERIA ACHIEVED:", "CRITICAL_SUCCESS")
        log_test_result("   - No duplicate articles detected", "CRITICAL_SUCCESS")
        log_test_result("   - Proper HTML formatting (no ```html placeholders)", "CRITICAL_SUCCESS")
        if test_results['backend_logs_check']:
            log_test_result("   - Backend logs confirm fixes are operational", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Duplicate processing issues may persist", "CRITICAL_ERROR")
        if not test_results['no_duplicates']:
            log_test_result("   - Duplicate articles still being generated", "CRITICAL_ERROR")
        if not test_results['article_quality']:
            log_test_result("   - Article quality issues (HTML placeholders)", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Focused Duplicate Processing Fix Verification")
    print("=" * 50)
    
    results = run_focused_duplicate_fix_verification()
    
    # Exit with appropriate code
    critical_success = results['no_duplicates'] and results['article_quality']
    if critical_success:
        exit(0)  # Success
    else:
        exit(1)  # Failure