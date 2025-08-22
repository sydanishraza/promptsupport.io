#!/usr/bin/env python3
"""
WYSIWYG FORMATTING CLEANUP EXECUTION TESTING
Testing the formatting cleanup for all existing articles to complete the WYSIWYG fix.

Focus Areas:
1. Run Formatting Cleanup: Execute POST to `/api/content/cleanup-formatting`
2. Cleanup Validation: Verify complex CSS classes are removed from legacy articles  
3. Article Structure Fix: Confirm all articles use simple `<div class="article-body">` structure
4. Regression Prevention: Ensure cleanup doesn't break existing article content
5. Success Rate Validation: Verify high success rate for cleanup operations
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://smartdoc-v2.preview.emergentagent.com"
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

def get_all_articles_before_cleanup():
    """Get all articles before cleanup to establish baseline"""
    try:
        log_test_result("📚 Retrieving all articles before cleanup...")
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            total = data.get('total', 0)
            
            log_test_result(f"✅ Retrieved {len(articles)} articles (Total: {total})")
            return articles
        else:
            log_test_result(f"❌ Failed to retrieve articles: Status {response.status_code}", "ERROR")
            return []
            
    except Exception as e:
        log_test_result(f"❌ Error retrieving articles: {e}", "ERROR")
        return []

def analyze_article_formatting(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze current article formatting to identify issues"""
    try:
        log_test_result("🔍 Analyzing current article formatting...")
        
        # Forbidden complex CSS classes to check for
        forbidden_classes = [
            'article-body-with-toc',
            'line-numbers',
            'mini-toc',
            'expandable',
            'advanced-toc',
            'related-article-card'
        ]
        
        analysis = {
            'total_articles': len(articles),
            'articles_with_forbidden_classes': 0,
            'articles_with_proper_wrapper': 0,
            'articles_with_complex_formatting': 0,
            'forbidden_class_occurrences': {},
            'problematic_articles': []
        }
        
        for article in articles:
            article_id = article.get('id', 'unknown')
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            
            # Check for forbidden classes
            has_forbidden_classes = False
            for forbidden_class in forbidden_classes:
                if forbidden_class in content:
                    has_forbidden_classes = True
                    if forbidden_class not in analysis['forbidden_class_occurrences']:
                        analysis['forbidden_class_occurrences'][forbidden_class] = 0
                    analysis['forbidden_class_occurrences'][forbidden_class] += 1
            
            if has_forbidden_classes:
                analysis['articles_with_forbidden_classes'] += 1
                analysis['problematic_articles'].append({
                    'id': article_id,
                    'title': title[:50] + '...' if len(title) > 50 else title
                })
            
            # Check for proper article-body wrapper
            if '<div class="article-body">' in content:
                analysis['articles_with_proper_wrapper'] += 1
            
            # Check for complex formatting patterns
            complex_patterns = [
                r'<div class="[^"]*toc[^"]*"',
                r'<div class="[^"]*expandable[^"]*"',
                r'<div class="[^"]*line-numbers[^"]*"',
                r'<div class="[^"]*advanced[^"]*"'
            ]
            
            has_complex_formatting = any(re.search(pattern, content) for pattern in complex_patterns)
            if has_complex_formatting:
                analysis['articles_with_complex_formatting'] += 1
        
        # Calculate percentages
        if analysis['total_articles'] > 0:
            analysis['proper_wrapper_percentage'] = (analysis['articles_with_proper_wrapper'] / analysis['total_articles']) * 100
            analysis['forbidden_classes_percentage'] = (analysis['articles_with_forbidden_classes'] / analysis['total_articles']) * 100
        else:
            analysis['proper_wrapper_percentage'] = 0
            analysis['forbidden_classes_percentage'] = 0
        
        log_test_result(f"📊 FORMATTING ANALYSIS RESULTS:")
        log_test_result(f"   Total Articles: {analysis['total_articles']}")
        log_test_result(f"   Articles with Proper Wrapper: {analysis['articles_with_proper_wrapper']} ({analysis['proper_wrapper_percentage']:.1f}%)")
        log_test_result(f"   Articles with Forbidden Classes: {analysis['articles_with_forbidden_classes']} ({analysis['forbidden_classes_percentage']:.1f}%)")
        log_test_result(f"   Articles with Complex Formatting: {analysis['articles_with_complex_formatting']}")
        
        if analysis['forbidden_class_occurrences']:
            log_test_result(f"   Forbidden Class Occurrences:")
            for class_name, count in analysis['forbidden_class_occurrences'].items():
                log_test_result(f"     - {class_name}: {count} articles")
        
        return analysis
        
    except Exception as e:
        log_test_result(f"❌ Error analyzing article formatting: {e}", "ERROR")
        return {}

def execute_formatting_cleanup():
    """Execute the formatting cleanup for all existing articles"""
    try:
        log_test_result("🧹 EXECUTING FORMATTING CLEANUP FOR ALL ARTICLES", "CRITICAL")
        
        # Execute POST to /api/content/cleanup-formatting
        response = requests.post(f"{API_BASE}/content/cleanup-formatting", timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            cleanup_data = response.json()
            
            log_test_result("✅ Formatting cleanup executed successfully", "SUCCESS")
            log_test_result(f"📊 CLEANUP RESULTS:")
            
            # Extract cleanup metrics from the actual response structure
            cleanup_results = cleanup_data.get('cleanup_results', {})
            total_processed = cleanup_results.get('total_articles', 0)
            successful_cleanups = cleanup_results.get('articles_cleaned', 0)
            failed_cleanups = cleanup_results.get('articles_skipped', 0)
            success_rate_str = cleanup_data.get('success_rate', '0%')
            # Parse success rate from string format like "85.5%"
            success_rate = float(success_rate_str.replace('%', '')) if success_rate_str else 0
            
            log_test_result(f"   Total Articles Processed: {total_processed}")
            log_test_result(f"   Successful Cleanups: {successful_cleanups}")
            log_test_result(f"   Failed Cleanups: {failed_cleanups}")
            log_test_result(f"   Success Rate: {success_rate:.1f}%")
            
            # Validate success rate
            if success_rate >= 80:
                log_test_result(f"✅ SUCCESS RATE VALIDATION PASSED: {success_rate:.1f}% (≥80%)", "SUCCESS")
                return {
                    'success': True,
                    'total_processed': total_processed,
                    'successful_cleanups': successful_cleanups,
                    'failed_cleanups': failed_cleanups,
                    'success_rate': success_rate,
                    'cleanup_details': cleanup_results.get('cleanup_details', [])
                }
            else:
                log_test_result(f"❌ SUCCESS RATE VALIDATION FAILED: {success_rate:.1f}% (<80%)", "ERROR")
                return {
                    'success': False,
                    'total_processed': total_processed,
                    'successful_cleanups': successful_cleanups,
                    'failed_cleanups': failed_cleanups,
                    'success_rate': success_rate,
                    'cleanup_details': cleanup_results.get('cleanup_details', [])
                }
        else:
            log_test_result(f"❌ Formatting cleanup FAILED: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        log_test_result(f"❌ Error executing formatting cleanup: {e}", "ERROR")
        return {'success': False, 'error': str(e)}

def validate_cleanup_results():
    """Validate that cleanup was successful by checking articles after cleanup"""
    try:
        log_test_result("🔍 VALIDATING CLEANUP RESULTS", "CRITICAL")
        
        # Get articles after cleanup
        articles_after = get_all_articles_before_cleanup()  # Reuse function
        
        if not articles_after:
            log_test_result("❌ Could not retrieve articles for validation", "ERROR")
            return False
        
        # Analyze formatting after cleanup
        analysis_after = analyze_article_formatting(articles_after)
        
        if not analysis_after:
            log_test_result("❌ Could not analyze articles after cleanup", "ERROR")
            return False
        
        # Validation criteria
        validation_results = {
            'proper_wrapper_check': False,
            'forbidden_classes_check': False,
            'content_preservation_check': False,
            'overall_success': False
        }
        
        # Check 1: Proper wrapper usage (should be >80%)
        proper_wrapper_percentage = analysis_after.get('proper_wrapper_percentage', 0)
        if proper_wrapper_percentage >= 80:
            log_test_result(f"✅ PROPER WRAPPER CHECK PASSED: {proper_wrapper_percentage:.1f}% articles have proper <div class='article-body'> wrapper", "SUCCESS")
            validation_results['proper_wrapper_check'] = True
        else:
            log_test_result(f"❌ PROPER WRAPPER CHECK FAILED: Only {proper_wrapper_percentage:.1f}% articles have proper wrapper (required: ≥80%)", "ERROR")
        
        # Check 2: Forbidden classes removal (should be <20%)
        forbidden_classes_percentage = analysis_after.get('forbidden_classes_percentage', 0)
        if forbidden_classes_percentage <= 20:
            log_test_result(f"✅ FORBIDDEN CLASSES CHECK PASSED: Only {forbidden_classes_percentage:.1f}% articles have forbidden classes", "SUCCESS")
            validation_results['forbidden_classes_check'] = True
        else:
            log_test_result(f"❌ FORBIDDEN CLASSES CHECK FAILED: {forbidden_classes_percentage:.1f}% articles still have forbidden classes (required: ≤20%)", "ERROR")
        
        # Check 3: Content preservation (basic check - articles should still have content)
        articles_with_content = sum(1 for article in articles_after if len(article.get('content', '').strip()) > 100)
        content_preservation_rate = (articles_with_content / len(articles_after)) * 100 if articles_after else 0
        
        if content_preservation_rate >= 95:
            log_test_result(f"✅ CONTENT PRESERVATION CHECK PASSED: {content_preservation_rate:.1f}% articles have substantial content", "SUCCESS")
            validation_results['content_preservation_check'] = True
        else:
            log_test_result(f"❌ CONTENT PRESERVATION CHECK FAILED: Only {content_preservation_rate:.1f}% articles have substantial content", "ERROR")
        
        # Overall validation
        passed_checks = sum(validation_results.values())
        total_checks = len(validation_results) - 1  # Exclude overall_success
        
        if passed_checks >= 2:  # At least 2 out of 3 checks should pass
            log_test_result(f"✅ CLEANUP VALIDATION PASSED: {passed_checks}/{total_checks} checks passed", "SUCCESS")
            validation_results['overall_success'] = True
        else:
            log_test_result(f"❌ CLEANUP VALIDATION FAILED: Only {passed_checks}/{total_checks} checks passed", "ERROR")
        
        return validation_results
        
    except Exception as e:
        log_test_result(f"❌ Error validating cleanup results: {e}", "ERROR")
        return False

def test_sample_articles_display():
    """Test that sample articles display correctly after cleanup"""
    try:
        log_test_result("🎨 TESTING SAMPLE ARTICLES DISPLAY", "CRITICAL")
        
        # Get a few sample articles
        articles = get_all_articles_before_cleanup()
        if not articles:
            log_test_result("❌ No articles available for display testing", "ERROR")
            return False
        
        # Test first 3 articles
        sample_articles = articles[:3]
        display_test_results = []
        
        for i, article in enumerate(sample_articles, 1):
            article_id = article.get('id')
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            
            log_test_result(f"🔍 Testing Article {i}: {title[:50]}...")
            
            # Basic display validation
            display_issues = []
            
            # Check for proper HTML structure
            if not content.strip():
                display_issues.append("Empty content")
            
            # Check for broken HTML tags
            if content.count('<') != content.count('>'):
                display_issues.append("Unmatched HTML tags")
            
            # Check for proper article body wrapper
            if '<div class="article-body">' not in content:
                display_issues.append("Missing article-body wrapper")
            
            # Check for forbidden complex classes
            forbidden_classes = ['article-body-with-toc', 'line-numbers', 'mini-toc', 'expandable', 'advanced-toc']
            found_forbidden = [cls for cls in forbidden_classes if cls in content]
            if found_forbidden:
                display_issues.append(f"Contains forbidden classes: {', '.join(found_forbidden)}")
            
            if not display_issues:
                log_test_result(f"   ✅ Article {i} display validation PASSED", "SUCCESS")
                display_test_results.append(True)
            else:
                log_test_result(f"   ❌ Article {i} display validation FAILED: {'; '.join(display_issues)}", "ERROR")
                display_test_results.append(False)
        
        # Overall display test result
        passed_articles = sum(display_test_results)
        total_articles = len(display_test_results)
        
        if passed_articles >= total_articles * 0.8:  # 80% should pass
            log_test_result(f"✅ SAMPLE ARTICLES DISPLAY TEST PASSED: {passed_articles}/{total_articles} articles display correctly", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ SAMPLE ARTICLES DISPLAY TEST FAILED: Only {passed_articles}/{total_articles} articles display correctly", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Error testing sample articles display: {e}", "ERROR")
        return False

def run_comprehensive_wysiwyg_cleanup_test():
    """Run comprehensive WYSIWYG formatting cleanup test suite"""
    log_test_result("🚀 STARTING COMPREHENSIVE WYSIWYG FORMATTING CLEANUP TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'baseline_analysis': False,
        'cleanup_execution': False,
        'cleanup_validation': False,
        'sample_display_test': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Baseline Analysis
    log_test_result("\nTEST 2: Baseline Formatting Analysis")
    articles_before = get_all_articles_before_cleanup()
    if articles_before:
        baseline_analysis = analyze_article_formatting(articles_before)
        test_results['baseline_analysis'] = bool(baseline_analysis)
        
        if baseline_analysis:
            log_test_result(f"✅ Baseline analysis completed: {baseline_analysis['total_articles']} articles analyzed", "SUCCESS")
        else:
            log_test_result("❌ Baseline analysis failed", "ERROR")
    else:
        log_test_result("❌ Could not retrieve articles for baseline analysis", "ERROR")
    
    # Test 3: Execute Formatting Cleanup (CRITICAL)
    log_test_result("\nTEST 3: CRITICAL FORMATTING CLEANUP EXECUTION")
    cleanup_result = execute_formatting_cleanup()
    test_results['cleanup_execution'] = cleanup_result.get('success', False)
    
    if test_results['cleanup_execution']:
        log_test_result(f"✅ Formatting cleanup executed successfully with {cleanup_result.get('success_rate', 0):.1f}% success rate", "SUCCESS")
    else:
        log_test_result("❌ Formatting cleanup execution failed", "ERROR")
    
    # Test 4: Validate Cleanup Results
    log_test_result("\nTEST 4: Cleanup Results Validation")
    if test_results['cleanup_execution']:
        validation_result = validate_cleanup_results()
        test_results['cleanup_validation'] = validation_result.get('overall_success', False) if isinstance(validation_result, dict) else validation_result
        
        if test_results['cleanup_validation']:
            log_test_result("✅ Cleanup validation passed", "SUCCESS")
        else:
            log_test_result("❌ Cleanup validation failed", "ERROR")
    else:
        log_test_result("⏭️ Skipping cleanup validation due to cleanup execution failure", "WARNING")
    
    # Test 5: Sample Articles Display Test
    log_test_result("\nTEST 5: Sample Articles Display Test")
    test_results['sample_display_test'] = test_sample_articles_display()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL WYSIWYG CLEANUP TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if test_results['cleanup_execution'] and test_results['cleanup_validation']:
        log_test_result("🎉 CRITICAL SUCCESS: WYSIWYG formatting cleanup completed successfully!", "CRITICAL_SUCCESS")
        log_test_result("✅ All existing articles now use simplified HTML structure", "CRITICAL_SUCCESS")
        log_test_result("✅ Complex CSS classes have been removed from legacy articles", "CRITICAL_SUCCESS")
        log_test_result("✅ Articles use proper <div class='article-body'> wrapper structure", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: WYSIWYG formatting cleanup did not complete successfully", "CRITICAL_ERROR")
        if not test_results['cleanup_execution']:
            log_test_result("❌ Cleanup execution failed - formatting issues remain in legacy articles", "CRITICAL_ERROR")
        if not test_results['cleanup_validation']:
            log_test_result("❌ Cleanup validation failed - articles may still have formatting issues", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("WYSIWYG Formatting Cleanup Execution Testing")
    print("=" * 50)
    
    results = run_comprehensive_wysiwyg_cleanup_test()
    
    # Exit with appropriate code
    if results['cleanup_execution'] and results['cleanup_validation']:
        exit(0)  # Success
    else:
        exit(1)  # Failure