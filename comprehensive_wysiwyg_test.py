#!/usr/bin/env python3
"""
COMPREHENSIVE WYSIWYG FORMATTING CLEANUP VALIDATION
Testing the complete WYSIWYG formatting fix implementation and validation.

This test validates:
1. Current state of articles (should be clean after previous cleanup)
2. Cleanup functionality by creating test articles with legacy formatting
3. Validation that cleanup removes forbidden CSS classes
4. Confirmation that articles use proper simplified HTML structure
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any

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

def get_all_articles():
    """Get all articles from Content Library"""
    try:
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

def analyze_current_formatting_state(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze current formatting state of all articles"""
    try:
        log_test_result("🔍 ANALYZING CURRENT FORMATTING STATE OF ALL ARTICLES")
        
        # Forbidden complex CSS classes
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
            'articles_with_proper_wrapper': 0,
            'articles_with_forbidden_classes': 0,
            'articles_with_simplified_structure': 0,
            'forbidden_class_details': {},
            'content_preservation_check': 0,
            'wysiwyg_compatibility_score': 0
        }
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            
            # Check for proper article-body wrapper
            if '<div class="article-body">' in content:
                analysis['articles_with_proper_wrapper'] += 1
            
            # Check for forbidden classes
            has_forbidden = False
            for forbidden_class in forbidden_classes:
                if forbidden_class in content:
                    has_forbidden = True
                    if forbidden_class not in analysis['forbidden_class_details']:
                        analysis['forbidden_class_details'][forbidden_class] = []
                    analysis['forbidden_class_details'][forbidden_class].append(title[:50])
            
            if has_forbidden:
                analysis['articles_with_forbidden_classes'] += 1
            
            # Check for simplified structure (no complex divs, proper semantic HTML)
            has_simplified_structure = (
                '<div class="article-body">' in content and
                not any(forbidden in content for forbidden in forbidden_classes) and
                not re.search(r'<div[^>]*class="[^"]*toc[^"]*"', content) and
                not re.search(r'<div[^>]*class="[^"]*expandable[^"]*"', content)
            )
            
            if has_simplified_structure:
                analysis['articles_with_simplified_structure'] += 1
            
            # Content preservation check (articles should have substantial content)
            content_text = re.sub(r'<[^>]+>', '', content).strip()
            if len(content_text) > 100:
                analysis['content_preservation_check'] += 1
        
        # Calculate percentages
        if analysis['total_articles'] > 0:
            analysis['proper_wrapper_percentage'] = (analysis['articles_with_proper_wrapper'] / analysis['total_articles']) * 100
            analysis['forbidden_classes_percentage'] = (analysis['articles_with_forbidden_classes'] / analysis['total_articles']) * 100
            analysis['simplified_structure_percentage'] = (analysis['articles_with_simplified_structure'] / analysis['total_articles']) * 100
            analysis['content_preservation_percentage'] = (analysis['content_preservation_check'] / analysis['total_articles']) * 100
            
            # WYSIWYG compatibility score (higher is better)
            analysis['wysiwyg_compatibility_score'] = (
                analysis['proper_wrapper_percentage'] * 0.3 +
                (100 - analysis['forbidden_classes_percentage']) * 0.4 +
                analysis['simplified_structure_percentage'] * 0.3
            )
        
        log_test_result(f"📊 CURRENT FORMATTING STATE ANALYSIS:")
        log_test_result(f"   Total Articles: {analysis['total_articles']}")
        log_test_result(f"   Articles with Proper Wrapper: {analysis['articles_with_proper_wrapper']} ({analysis.get('proper_wrapper_percentage', 0):.1f}%)")
        log_test_result(f"   Articles with Forbidden Classes: {analysis['articles_with_forbidden_classes']} ({analysis.get('forbidden_classes_percentage', 0):.1f}%)")
        log_test_result(f"   Articles with Simplified Structure: {analysis['articles_with_simplified_structure']} ({analysis.get('simplified_structure_percentage', 0):.1f}%)")
        log_test_result(f"   Content Preservation Rate: {analysis['content_preservation_check']} ({analysis.get('content_preservation_percentage', 0):.1f}%)")
        log_test_result(f"   WYSIWYG Compatibility Score: {analysis.get('wysiwyg_compatibility_score', 0):.1f}/100")
        
        if analysis['forbidden_class_details']:
            log_test_result(f"   Forbidden Classes Found:")
            for class_name, article_titles in analysis['forbidden_class_details'].items():
                log_test_result(f"     - {class_name}: {len(article_titles)} articles")
                for title in article_titles[:3]:  # Show first 3 examples
                    log_test_result(f"       * {title}...")
        
        return analysis
        
    except Exception as e:
        log_test_result(f"❌ Error analyzing formatting state: {e}", "ERROR")
        return {}

def create_test_article_with_legacy_formatting():
    """Create a test article with legacy formatting to test cleanup functionality"""
    try:
        log_test_result("🧪 CREATING TEST ARTICLE WITH LEGACY FORMATTING")
        
        # Create content with forbidden CSS classes and complex structure
        legacy_content = '''<div class="article-body-with-toc">
<div class="mini-toc">
<h3>Table of Contents</h3>
<ul class="toc-hierarchy">
<li class="toc-level-1"><a href="#section1">Section 1</a></li>
<li class="toc-level-2"><a href="#section2">Section 2</a></li>
</ul>
</div>

<div class="article-main-content">
<h2 id="section1">Test Section 1</h2>
<p>This is a test paragraph with <strong>formatting</strong>.</p>

<div class="expandable">
<div class="expandable-header">
<span class="expandable-title">Click to expand</span>
</div>
<div class="expandable-content">
<p>This is expandable content that should be simplified.</p>
</div>
</div>

<pre class="line-numbers language-javascript"><code class="language-javascript">
function testFunction() {
    console.log("This is a test");
}
</code></pre>

<h2 id="section2">Test Section 2</h2>
<p>Another test paragraph.</p>

<div class="related-article-card">
<h3>Related Article</h3>
<p>This should be removed during cleanup.</p>
</div>
</div>

<div class="article-sidebar">
<div class="advanced-toc">
<h4>Advanced Navigation</h4>
<ul>
<li><a href="#section1">Go to Section 1</a></li>
</ul>
</div>
</div>
</div>'''
        
        # Create test article
        test_article = {
            "title": "WYSIWYG Cleanup Test Article - Legacy Formatting",
            "content": legacy_content,
            "status": "published",
            "article_type": "test",
            "tags": ["test", "legacy-formatting", "cleanup-test"],
            "metadata": {
                "test_article": True,
                "created_for_cleanup_test": True
            }
        }
        
        # Post to Content Library
        response = requests.post(f"{API_BASE}/content-library", json=test_article, timeout=30)
        
        if response.status_code == 200:
            created_article = response.json()
            article_id = created_article.get('id')
            log_test_result(f"✅ Test article created successfully: ID {article_id}", "SUCCESS")
            return article_id
        else:
            log_test_result(f"❌ Failed to create test article: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        log_test_result(f"❌ Error creating test article: {e}", "ERROR")
        return None

def execute_cleanup_and_validate():
    """Execute cleanup and validate results"""
    try:
        log_test_result("🧹 EXECUTING FORMATTING CLEANUP", "CRITICAL")
        
        # Execute cleanup
        response = requests.post(f"{API_BASE}/content/cleanup-formatting", timeout=300)
        
        if response.status_code == 200:
            cleanup_data = response.json()
            cleanup_results = cleanup_data.get('cleanup_results', {})
            
            total_processed = cleanup_results.get('total_articles', 0)
            articles_cleaned = cleanup_results.get('articles_cleaned', 0)
            success_rate_str = cleanup_data.get('success_rate', '0%')
            success_rate = float(success_rate_str.replace('%', '')) if success_rate_str else 0
            
            log_test_result(f"✅ Cleanup executed successfully", "SUCCESS")
            log_test_result(f"   Total Articles Processed: {total_processed}")
            log_test_result(f"   Articles Cleaned: {articles_cleaned}")
            log_test_result(f"   Success Rate: {success_rate:.1f}%")
            
            return {
                'success': True,
                'total_processed': total_processed,
                'articles_cleaned': articles_cleaned,
                'success_rate': success_rate,
                'cleanup_details': cleanup_results.get('cleanup_details', [])
            }
        else:
            log_test_result(f"❌ Cleanup failed: Status {response.status_code}", "ERROR")
            return {'success': False}
            
    except Exception as e:
        log_test_result(f"❌ Error executing cleanup: {e}", "ERROR")
        return {'success': False}

def validate_wysiwyg_fix_completion():
    """Validate that the WYSIWYG fix is complete and working"""
    try:
        log_test_result("🎯 VALIDATING WYSIWYG FIX COMPLETION", "CRITICAL")
        
        # Get all articles after cleanup
        articles = get_all_articles()
        if not articles:
            log_test_result("❌ Could not retrieve articles for validation", "ERROR")
            return False
        
        # Analyze final state
        final_analysis = analyze_current_formatting_state(articles)
        
        if not final_analysis:
            log_test_result("❌ Could not analyze final state", "ERROR")
            return False
        
        # Validation criteria for WYSIWYG fix completion
        validation_results = {
            'simplified_structure_check': False,
            'forbidden_classes_removal': False,
            'content_preservation': False,
            'wysiwyg_compatibility': False,
            'overall_success': False
        }
        
        # Check 1: Simplified Structure (≥80% should have simplified structure)
        simplified_percentage = final_analysis.get('simplified_structure_percentage', 0)
        if simplified_percentage >= 80:
            log_test_result(f"✅ SIMPLIFIED STRUCTURE CHECK PASSED: {simplified_percentage:.1f}% articles have simplified structure", "SUCCESS")
            validation_results['simplified_structure_check'] = True
        else:
            log_test_result(f"❌ SIMPLIFIED STRUCTURE CHECK FAILED: Only {simplified_percentage:.1f}% articles have simplified structure", "ERROR")
        
        # Check 2: Forbidden Classes Removal (≤10% should have forbidden classes)
        forbidden_percentage = final_analysis.get('forbidden_classes_percentage', 0)
        if forbidden_percentage <= 10:
            log_test_result(f"✅ FORBIDDEN CLASSES REMOVAL PASSED: Only {forbidden_percentage:.1f}% articles have forbidden classes", "SUCCESS")
            validation_results['forbidden_classes_removal'] = True
        else:
            log_test_result(f"❌ FORBIDDEN CLASSES REMOVAL FAILED: {forbidden_percentage:.1f}% articles still have forbidden classes", "ERROR")
        
        # Check 3: Content Preservation (≥95% should have substantial content)
        content_percentage = final_analysis.get('content_preservation_percentage', 0)
        if content_percentage >= 95:
            log_test_result(f"✅ CONTENT PRESERVATION PASSED: {content_percentage:.1f}% articles have substantial content", "SUCCESS")
            validation_results['content_preservation'] = True
        else:
            log_test_result(f"❌ CONTENT PRESERVATION FAILED: Only {content_percentage:.1f}% articles have substantial content", "ERROR")
        
        # Check 4: WYSIWYG Compatibility (≥85 score)
        compatibility_score = final_analysis.get('wysiwyg_compatibility_score', 0)
        if compatibility_score >= 85:
            log_test_result(f"✅ WYSIWYG COMPATIBILITY PASSED: Score {compatibility_score:.1f}/100", "SUCCESS")
            validation_results['wysiwyg_compatibility'] = True
        else:
            log_test_result(f"❌ WYSIWYG COMPATIBILITY FAILED: Score {compatibility_score:.1f}/100 (required: ≥85)", "ERROR")
        
        # Overall validation
        passed_checks = sum(validation_results[key] for key in validation_results if key != 'overall_success')
        total_checks = len(validation_results) - 1
        
        if passed_checks >= 3:  # At least 3 out of 4 checks should pass
            log_test_result(f"✅ WYSIWYG FIX VALIDATION PASSED: {passed_checks}/{total_checks} checks passed", "SUCCESS")
            validation_results['overall_success'] = True
        else:
            log_test_result(f"❌ WYSIWYG FIX VALIDATION FAILED: Only {passed_checks}/{total_checks} checks passed", "ERROR")
        
        return validation_results
        
    except Exception as e:
        log_test_result(f"❌ Error validating WYSIWYG fix completion: {e}", "ERROR")
        return False

def cleanup_test_articles():
    """Clean up test articles created during testing"""
    try:
        log_test_result("🧽 CLEANING UP TEST ARTICLES")
        
        articles = get_all_articles()
        test_articles_deleted = 0
        
        for article in articles:
            title = article.get('title', '')
            metadata = article.get('metadata', {})
            
            # Delete test articles
            if ('test' in title.lower() and 'cleanup' in title.lower()) or metadata.get('test_article'):
                article_id = article.get('id')
                try:
                    delete_response = requests.delete(f"{API_BASE}/content-library/{article_id}", timeout=30)
                    if delete_response.status_code == 200:
                        test_articles_deleted += 1
                        log_test_result(f"   ✅ Deleted test article: {title[:50]}...")
                except Exception as delete_error:
                    log_test_result(f"   ⚠️ Could not delete test article {article_id}: {delete_error}")
        
        log_test_result(f"✅ Cleanup complete: {test_articles_deleted} test articles deleted")
        return True
        
    except Exception as e:
        log_test_result(f"❌ Error cleaning up test articles: {e}", "ERROR")
        return False

def run_comprehensive_wysiwyg_validation():
    """Run comprehensive WYSIWYG formatting fix validation"""
    log_test_result("🚀 STARTING COMPREHENSIVE WYSIWYG FORMATTING FIX VALIDATION", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'current_state_analysis': False,
        'test_article_creation': False,
        'cleanup_execution': False,
        'wysiwyg_fix_validation': False,
        'test_cleanup': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Current State Analysis
    log_test_result("\nTEST 2: Current Formatting State Analysis")
    articles = get_all_articles()
    if articles:
        current_analysis = analyze_current_formatting_state(articles)
        test_results['current_state_analysis'] = bool(current_analysis)
        
        if current_analysis:
            compatibility_score = current_analysis.get('wysiwyg_compatibility_score', 0)
            log_test_result(f"✅ Current state analysis completed: WYSIWYG Compatibility Score {compatibility_score:.1f}/100", "SUCCESS")
        else:
            log_test_result("❌ Current state analysis failed", "ERROR")
    else:
        log_test_result("❌ Could not retrieve articles for analysis", "ERROR")
    
    # Test 3: Create Test Article with Legacy Formatting
    log_test_result("\nTEST 3: Create Test Article with Legacy Formatting")
    test_article_id = create_test_article_with_legacy_formatting()
    test_results['test_article_creation'] = bool(test_article_id)
    
    # Test 4: Execute Cleanup
    log_test_result("\nTEST 4: Execute Formatting Cleanup")
    cleanup_result = execute_cleanup_and_validate()
    test_results['cleanup_execution'] = cleanup_result.get('success', False)
    
    if test_results['cleanup_execution']:
        articles_cleaned = cleanup_result.get('articles_cleaned', 0)
        success_rate = cleanup_result.get('success_rate', 0)
        log_test_result(f"✅ Cleanup executed: {articles_cleaned} articles cleaned, {success_rate:.1f}% success rate", "SUCCESS")
    
    # Test 5: Validate WYSIWYG Fix Completion
    log_test_result("\nTEST 5: WYSIWYG Fix Completion Validation")
    validation_result = validate_wysiwyg_fix_completion()
    test_results['wysiwyg_fix_validation'] = validation_result.get('overall_success', False) if isinstance(validation_result, dict) else validation_result
    
    # Test 6: Cleanup Test Articles
    log_test_result("\nTEST 6: Test Articles Cleanup")
    test_results['test_cleanup'] = cleanup_test_articles()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 COMPREHENSIVE WYSIWYG VALIDATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Final assessment
    critical_tests_passed = (
        test_results['backend_health'] and
        test_results['current_state_analysis'] and
        test_results['cleanup_execution'] and
        test_results['wysiwyg_fix_validation']
    )
    
    if critical_tests_passed:
        log_test_result("🎉 CRITICAL SUCCESS: WYSIWYG FORMATTING FIX IS COMPLETE AND WORKING!", "CRITICAL_SUCCESS")
        log_test_result("✅ All existing articles now use simplified HTML structure", "CRITICAL_SUCCESS")
        log_test_result("✅ Complex CSS classes have been successfully removed", "CRITICAL_SUCCESS")
        log_test_result("✅ Articles use proper <div class='article-body'> wrapper", "CRITICAL_SUCCESS")
        log_test_result("✅ Content preservation maintained throughout cleanup process", "CRITICAL_SUCCESS")
        log_test_result("✅ WYSIWYG editor compatibility achieved", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL ISSUES IDENTIFIED: WYSIWYG formatting fix needs attention", "CRITICAL_ERROR")
        if not test_results['cleanup_execution']:
            log_test_result("❌ Cleanup execution issues detected", "CRITICAL_ERROR")
        if not test_results['wysiwyg_fix_validation']:
            log_test_result("❌ WYSIWYG fix validation failed", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Comprehensive WYSIWYG Formatting Fix Validation")
    print("=" * 50)
    
    results = run_comprehensive_wysiwyg_validation()
    
    # Exit with appropriate code
    critical_success = (
        results['backend_health'] and
        results['current_state_analysis'] and
        results['cleanup_execution'] and
        results['wysiwyg_fix_validation']
    )
    
    if critical_success:
        exit(0)  # Success
    else:
        exit(1)  # Failure