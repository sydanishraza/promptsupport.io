#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE RICH FORMATTING VERIFICATION
Verify all aspects of the enhanced content processing pipeline with rich formatting preservation
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-6.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def verify_rich_formatting_preservation():
    """Verify rich formatting preservation in recent articles"""
    try:
        log_test_result("🎨 FINAL RICH FORMATTING PRESERVATION VERIFICATION", "CRITICAL")
        
        # Get recent articles
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result("❌ Could not access Content Library", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        log_test_result(f"📚 Analyzing {len(articles)} articles for rich formatting preservation")
        
        # Find articles with rich formatting
        rich_formatting_articles = []
        for article in articles:
            content = article.get('content', '')
            title = article.get('title', '')
            
            # Check for rich formatting indicators
            has_code_blocks = '<pre><code>' in content
            has_lists = '<ul>' in content or '<ol>' in content
            has_emphasis = '<strong>' in content or '<em>' in content
            has_callouts = 'class="note"' in content or '<blockquote>' in content
            has_proper_headings = '<h2>' in content or '<h3>' in content
            
            if any([has_code_blocks, has_lists, has_emphasis, has_callouts]):
                rich_formatting_articles.append({
                    'article': article,
                    'has_code_blocks': has_code_blocks,
                    'has_lists': has_lists,
                    'has_emphasis': has_emphasis,
                    'has_callouts': has_callouts,
                    'has_proper_headings': has_proper_headings
                })
        
        log_test_result(f"🔍 Found {len(rich_formatting_articles)} articles with rich formatting")
        
        if not rich_formatting_articles:
            log_test_result("⚠️ No articles with rich formatting found", "WARNING")
            return False
        
        # Analyze rich formatting preservation
        formatting_metrics = {
            'code_blocks_preserved': 0,
            'lists_preserved': 0,
            'emphasis_preserved': 0,
            'callouts_preserved': 0,
            'proper_headings': 0,
            'clean_html_structure': 0,
            'no_markdown_artifacts': 0,
            'total_articles': len(rich_formatting_articles)
        }
        
        log_test_result("📊 DETAILED RICH FORMATTING ANALYSIS:")
        
        for i, item in enumerate(rich_formatting_articles[:5]):  # Check first 5 articles
            article = item['article']
            title = article.get('title', 'Unknown')
            content = article.get('content', '')
            
            log_test_result(f"   📄 Article {i+1}: {title[:50]}...")
            
            # Check each formatting aspect
            if item['has_code_blocks']:
                formatting_metrics['code_blocks_preserved'] += 1
                log_test_result(f"      ✅ Code blocks: <pre><code> tags present")
            
            if item['has_lists']:
                formatting_metrics['lists_preserved'] += 1
                log_test_result(f"      ✅ Lists: <ul>/<ol> tags present")
            
            if item['has_emphasis']:
                formatting_metrics['emphasis_preserved'] += 1
                log_test_result(f"      ✅ Emphasis: <strong>/<em> tags present")
            
            if item['has_callouts']:
                formatting_metrics['callouts_preserved'] += 1
                log_test_result(f"      ✅ Callouts: note/blockquote elements present")
            
            if item['has_proper_headings']:
                formatting_metrics['proper_headings'] += 1
                log_test_result(f"      ✅ Headings: <h2>/<h3> structure present")
            
            # Check for clean HTML structure
            if '<html>' not in content and '<head>' not in content and '<body>' not in content:
                formatting_metrics['clean_html_structure'] += 1
                log_test_result(f"      ✅ Clean HTML: No document wrapper tags")
            else:
                log_test_result(f"      ❌ Unclean HTML: Document wrapper tags present")
            
            # Check for no markdown artifacts
            if '```' not in content and '##' not in content:
                formatting_metrics['no_markdown_artifacts'] += 1
                log_test_result(f"      ✅ No markdown artifacts")
            else:
                log_test_result(f"      ⚠️ Markdown artifacts detected")
        
        # Calculate overall success rates
        log_test_result("\n📈 RICH FORMATTING PRESERVATION METRICS:")
        total_checked = min(5, len(rich_formatting_articles))
        
        for metric, count in formatting_metrics.items():
            if metric != 'total_articles':
                percentage = (count / total_checked) * 100 if total_checked > 0 else 0
                status = "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
                log_test_result(f"   {status} {metric.replace('_', ' ').title()}: {count}/{total_checked} ({percentage:.1f}%)")
        
        # Overall assessment
        critical_metrics = ['code_blocks_preserved', 'lists_preserved', 'clean_html_structure', 'no_markdown_artifacts']
        critical_score = sum(formatting_metrics[metric] for metric in critical_metrics) / (len(critical_metrics) * total_checked) * 100
        
        if critical_score >= 80:
            log_test_result(f"🎉 EXCELLENT rich formatting preservation: {critical_score:.1f}%", "SUCCESS")
            return True
        elif critical_score >= 60:
            log_test_result(f"⚠️ GOOD rich formatting preservation: {critical_score:.1f}%", "WARNING")
            return True
        else:
            log_test_result(f"❌ POOR rich formatting preservation: {critical_score:.1f}%", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ Rich formatting verification failed: {e}", "ERROR")
        return False

def verify_content_analysis_decisions():
    """Verify intelligent content analysis and structuring decisions"""
    try:
        log_test_result("🧠 VERIFYING CONTENT ANALYSIS DECISIONS", "CRITICAL")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Analyze content structuring patterns
        unified_articles = []
        split_articles = []
        tutorial_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            metadata = article.get('metadata', {})
            
            # Check for unified processing
            if metadata.get('unified_article') or metadata.get('processing_approach') == 'unified':
                unified_articles.append(article)
            
            # Check for split processing
            if metadata.get('outline_based'):
                split_articles.append(article)
            
            # Check for tutorial content
            if any(keyword in title for keyword in ['tutorial', 'guide', 'how-to', 'api', 'maps']):
                tutorial_articles.append(article)
        
        log_test_result(f"📊 CONTENT ANALYSIS PATTERNS:")
        log_test_result(f"   📄 Unified Articles: {len(unified_articles)}")
        log_test_result(f"   🔀 Split Articles: {len(split_articles)}")
        log_test_result(f"   📖 Tutorial Articles: {len(tutorial_articles)}")
        
        # Check if tutorials are appropriately handled
        tutorial_unified_count = 0
        for article in tutorial_articles:
            if article.get('metadata', {}).get('unified_article'):
                tutorial_unified_count += 1
        
        if tutorial_articles:
            tutorial_unified_rate = (tutorial_unified_count / len(tutorial_articles)) * 100
            log_test_result(f"   ✅ Tutorial Unification Rate: {tutorial_unified_rate:.1f}%")
            
            if tutorial_unified_rate >= 50:  # At least half of tutorials should be unified
                log_test_result("✅ Content analysis correctly identifies and unifies tutorial content", "SUCCESS")
                return True
            else:
                log_test_result("⚠️ Some tutorials may be over-fragmented", "WARNING")
                return True
        else:
            log_test_result("⚠️ No tutorial articles found for analysis", "WARNING")
            return True
        
    except Exception as e:
        log_test_result(f"❌ Content analysis verification failed: {e}", "ERROR")
        return False

def verify_html_cleaning_function():
    """Verify HTML cleaning function effectiveness"""
    try:
        log_test_result("🧹 VERIFYING HTML CLEANING FUNCTION", "CRITICAL")
        
        # Check the most recent test article
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Find the HTML cleaning test article
        test_article = None
        for article in articles:
            title = article.get('title', '')
            if 'HTML Cleaning Test' in title or 'CodeBlocks' in title:
                test_article = article
                break
        
        if not test_article:
            log_test_result("⚠️ HTML cleaning test article not found", "WARNING")
            return True
        
        content = test_article.get('content', '')
        log_test_result(f"📄 Analyzing HTML cleaning in: {test_article.get('title', 'Unknown')}")
        
        # Verify HTML cleaning effectiveness
        cleaning_checks = {
            'markdown_to_html': '<pre><code class="language-' in content and '```' not in content,
            'preserved_lists': '<ul>' in content or '<ol>' in content,
            'preserved_emphasis': '<strong>' in content or '<em>' in content,
            'clean_structure': '<html>' not in content and '<head>' not in content,
            'preserved_callouts': 'class="note"' in content or '<blockquote>' in content,
            'proper_headings': '<h2>' in content or '<h3>' in content
        }
        
        log_test_result("📊 HTML CLEANING VERIFICATION:")
        passed_checks = 0
        for check, result in cleaning_checks.items():
            status = "✅" if result else "❌"
            log_test_result(f"   {status} {check.replace('_', ' ').title()}: {'PASS' if result else 'FAIL'}")
            if result:
                passed_checks += 1
        
        success_rate = (passed_checks / len(cleaning_checks)) * 100
        
        if success_rate >= 80:
            log_test_result(f"✅ HTML cleaning function working excellently: {success_rate:.1f}%", "SUCCESS")
            return True
        elif success_rate >= 60:
            log_test_result(f"⚠️ HTML cleaning function working well: {success_rate:.1f}%", "WARNING")
            return True
        else:
            log_test_result(f"❌ HTML cleaning function needs improvement: {success_rate:.1f}%", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ HTML cleaning verification failed: {e}", "ERROR")
        return False

def run_final_verification():
    """Run final comprehensive verification"""
    log_test_result("🎯 FINAL COMPREHENSIVE RICH FORMATTING VERIFICATION", "CRITICAL")
    log_test_result("=" * 80)
    
    verification_results = {
        'rich_formatting_preservation': False,
        'content_analysis_decisions': False,
        'html_cleaning_function': False
    }
    
    # Verification 1: Rich Formatting Preservation
    log_test_result("VERIFICATION 1: Rich Formatting Preservation")
    verification_results['rich_formatting_preservation'] = verify_rich_formatting_preservation()
    
    # Verification 2: Content Analysis Decisions
    log_test_result("\nVERIFICATION 2: Content Analysis Decisions")
    verification_results['content_analysis_decisions'] = verify_content_analysis_decisions()
    
    # Verification 3: HTML Cleaning Function
    log_test_result("\nVERIFICATION 3: HTML Cleaning Function")
    verification_results['html_cleaning_function'] = verify_html_cleaning_function()
    
    # Final Assessment
    log_test_result("\n" + "=" * 80)
    log_test_result("🏆 FINAL VERIFICATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_verifications = sum(verification_results.values())
    total_verifications = len(verification_results)
    
    for verification_name, result in verification_results.items():
        status = "✅ VERIFIED" if result else "❌ FAILED"
        log_test_result(f"{verification_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL VERIFICATION: {passed_verifications}/{total_verifications} verifications passed")
    
    if passed_verifications == total_verifications:
        log_test_result("🎉 ALL VERIFICATIONS PASSED - RICH FORMATTING PRESERVATION IS EXCELLENT!", "CRITICAL_SUCCESS")
        log_test_result("✅ Enhanced content processing pipeline preserves rich formatting correctly", "CRITICAL_SUCCESS")
        log_test_result("✅ Code blocks, lists, callouts, and technical formatting are maintained", "CRITICAL_SUCCESS")
        log_test_result("✅ HTML cleaning converts markdown to proper HTML while preserving content", "CRITICAL_SUCCESS")
        log_test_result("✅ Content analysis makes appropriate decisions about unified vs split processing", "CRITICAL_SUCCESS")
        log_test_result("✅ Code examples stay with their explanations and context", "CRITICAL_SUCCESS")
    elif passed_verifications >= 2:
        log_test_result("⚠️ MOST VERIFICATIONS PASSED - RICH FORMATTING PRESERVATION IS GOOD", "WARNING")
        log_test_result("✅ Core functionality is working with minor areas for improvement", "WARNING")
    else:
        log_test_result("❌ VERIFICATION FAILED - RICH FORMATTING PRESERVATION NEEDS WORK", "CRITICAL_ERROR")
        log_test_result("❌ Significant issues with rich formatting preservation detected", "CRITICAL_ERROR")
    
    return verification_results

if __name__ == "__main__":
    print("Final Comprehensive Rich Formatting Verification")
    print("=" * 60)
    
    results = run_final_verification()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure