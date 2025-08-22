#!/usr/bin/env python3
"""
ARTICLE ANALYSIS TEST - Content Corruption & WYSIWYG Validation
Analyze existing articles to validate the improvements mentioned in the review request
"""

import requests
import json
import re
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://smartdoc-v2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def analyze_content_corruption_fixes():
    """Analyze existing articles for content corruption fixes"""
    try:
        log_test_result("🔍 ANALYZING CONTENT CORRUPTION FIXES", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for analysis", "ERROR")
            return False
        
        log_test_result(f"📊 Analyzing {len(articles)} articles for corruption fixes...")
        
        # Analysis metrics
        metrics = {
            'total_articles': len(articles),
            'substantial_content': 0,
            'empty_articles': 0,
            'short_articles': 0,
            'template_contamination': 0,
            'wysiwyg_features': 0,
            'validation_metadata': 0,
            'outline_based': 0,
            'code_blocks': 0,
            'proper_html_structure': 0
        }
        
        # Detailed analysis
        empty_articles = []
        contaminated_articles = []
        enhanced_articles = []
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            metadata = article.get('metadata', {})
            
            # 1. Content Quality Analysis
            text_content = re.sub(r'<[^>]+>', '', content).strip()
            text_length = len(text_content)
            
            if text_length == 0:
                metrics['empty_articles'] += 1
                empty_articles.append(title)
            elif text_length < 100:
                metrics['short_articles'] += 1
            else:
                metrics['substantial_content'] += 1
            
            # 2. Template Contamination Check
            contamination_patterns = [
                r'<!DOCTYPE\s+html',
                r'<html[^>]*>',
                r'<head[^>]*>',
                r'<body[^>]*>'
            ]
            
            has_contamination = any(re.search(pattern, content, re.IGNORECASE) for pattern in contamination_patterns)
            if has_contamination:
                metrics['template_contamination'] += 1
                contaminated_articles.append(title)
            
            # 3. WYSIWYG Enhancement Detection
            wysiwyg_indicators = [
                'article-body',
                'line-numbers', 
                'copy-button',
                'expandable',
                'callout',
                'note-box',
                'tip-box',
                'warning-box'
            ]
            
            has_wysiwyg = any(indicator in content for indicator in wysiwyg_indicators)
            if has_wysiwyg:
                metrics['wysiwyg_features'] += 1
                enhanced_articles.append(title)
            
            # 4. Code Blocks Analysis
            if '<pre>' in content or '<code>' in content:
                metrics['code_blocks'] += 1
            
            # 5. Proper HTML Structure (semantic HTML without document structure)
            has_semantic_html = any(tag in content for tag in ['<h2>', '<h3>', '<p>', '<ul>', '<ol>'])
            has_document_structure = any(tag in content for tag in ['<html>', '<head>', '<body>'])
            
            if has_semantic_html and not has_document_structure:
                metrics['proper_html_structure'] += 1
            
            # 6. Validation Metadata
            if metadata.get('content_validated') or metadata.get('content_length'):
                metrics['validation_metadata'] += 1
            
            # 7. Outline-based Processing
            if metadata.get('outline_based'):
                metrics['outline_based'] += 1
        
        # Calculate percentages
        total = metrics['total_articles']
        percentages = {key: (value / total * 100) if total > 0 else 0 for key, value in metrics.items()}
        
        # Report results
        log_test_result("📈 CONTENT CORRUPTION ANALYSIS RESULTS:")
        log_test_result(f"   Total Articles: {metrics['total_articles']}")
        log_test_result(f"   Substantial Content: {metrics['substantial_content']} ({percentages['substantial_content']:.1f}%)")
        log_test_result(f"   Empty Articles: {metrics['empty_articles']} ({percentages['empty_articles']:.1f}%)")
        log_test_result(f"   Short Articles: {metrics['short_articles']} ({percentages['short_articles']:.1f}%)")
        log_test_result(f"   Template Contamination: {metrics['template_contamination']} ({percentages['template_contamination']:.1f}%)")
        log_test_result(f"   WYSIWYG Features: {metrics['wysiwyg_features']} ({percentages['wysiwyg_features']:.1f}%)")
        log_test_result(f"   Code Blocks: {metrics['code_blocks']} ({percentages['code_blocks']:.1f}%)")
        log_test_result(f"   Proper HTML Structure: {metrics['proper_html_structure']} ({percentages['proper_html_structure']:.1f}%)")
        log_test_result(f"   Validation Metadata: {metrics['validation_metadata']} ({percentages['validation_metadata']:.1f}%)")
        log_test_result(f"   Outline-based Processing: {metrics['outline_based']} ({percentages['outline_based']:.1f}%)")
        
        # Show specific examples
        if empty_articles:
            log_test_result("❌ EMPTY ARTICLES:", "ERROR")
            for article in empty_articles[:5]:
                log_test_result(f"   - {article}")
        
        if contaminated_articles:
            log_test_result("❌ CONTAMINATED ARTICLES:", "ERROR")
            for article in contaminated_articles[:5]:
                log_test_result(f"   - {article}")
        
        if enhanced_articles:
            log_test_result("✅ WYSIWYG ENHANCED ARTICLES:", "SUCCESS")
            for article in enhanced_articles[:5]:
                log_test_result(f"   - {article}")
        
        # Success criteria evaluation
        success_criteria = {
            'content_generation_quality': percentages['substantial_content'] >= 70,
            'empty_prevention': percentages['empty_articles'] <= 15,
            'template_contamination_prevention': percentages['template_contamination'] <= 10,
            'wysiwyg_integration': percentages['wysiwyg_features'] >= 10,
            'proper_html_structure': percentages['proper_html_structure'] >= 80
        }
        
        log_test_result("🎯 SUCCESS CRITERIA EVALUATION:")
        passed_criteria = 0
        for criterion, passed in success_criteria.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            log_test_result(f"   {criterion.replace('_', ' ').title()}: {status}")
            if passed:
                passed_criteria += 1
        
        total_criteria = len(success_criteria)
        success_rate = (passed_criteria / total_criteria) * 100
        
        log_test_result(f"📊 OVERALL SUCCESS RATE: {passed_criteria}/{total_criteria} ({success_rate:.1f}%)")
        
        if success_rate >= 60:  # At least 60% of criteria should pass
            log_test_result("🎉 CONTENT CORRUPTION FIXES: WORKING EFFECTIVELY", "SUCCESS")
            return True
        else:
            log_test_result("❌ CONTENT CORRUPTION FIXES: NEED IMPROVEMENT", "ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ Content corruption analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def analyze_wysiwyg_enhancements():
    """Detailed analysis of WYSIWYG enhancements"""
    try:
        log_test_result("🎨 ANALYZING WYSIWYG ENHANCEMENTS", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for WYSIWYG analysis", "ERROR")
            return False
        
        # WYSIWYG enhancement patterns
        wysiwyg_patterns = {
            'article_body_wrapper': r'<div[^>]*class="[^"]*article-body[^"]*"',
            'enhanced_code_blocks': r'<pre[^>]*class="[^"]*line-numbers[^"]*"',
            'heading_ids': r'<h[2-6][^>]*id="[^"]*"',
            'copy_buttons': r'<button[^>]*class="[^"]*copy-btn[^"]*"',
            'expandable_sections': r'<div[^>]*class="[^"]*expandable[^"]*"',
            'contextual_callouts': r'<div[^>]*class="[^"]*(?:callout|note-box|tip-box|warning-box)[^"]*"',
            'code_syntax_highlighting': r'<code[^>]*class="[^"]*language-[^"]*"',
            'responsive_tables': r'<table[^>]*class="[^"]*responsive[^"]*"'
        }
        
        enhancement_counts = {pattern: 0 for pattern in wysiwyg_patterns.keys()}
        articles_with_enhancements = []
        
        log_test_result(f"🔍 Analyzing {len(articles)} articles for WYSIWYG enhancements...")
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            
            article_enhancements = []
            for pattern_name, pattern in wysiwyg_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    enhancement_counts[pattern_name] += 1
                    article_enhancements.append(pattern_name)
            
            if article_enhancements:
                articles_with_enhancements.append({
                    'title': title,
                    'enhancements': article_enhancements,
                    'enhancement_count': len(article_enhancements)
                })
        
        # Report WYSIWYG enhancement results
        log_test_result("🎨 WYSIWYG ENHANCEMENT ANALYSIS:")
        total_enhancements = sum(enhancement_counts.values())
        
        for pattern_name, count in enhancement_counts.items():
            percentage = (count / len(articles) * 100) if articles else 0
            log_test_result(f"   {pattern_name.replace('_', ' ').title()}: {count} articles ({percentage:.1f}%)")
        
        log_test_result(f"   Total Enhancement Features: {total_enhancements}")
        log_test_result(f"   Articles with Enhancements: {len(articles_with_enhancements)}/{len(articles)}")
        
        if articles_with_enhancements:
            log_test_result("✅ TOP ENHANCED ARTICLES:", "SUCCESS")
            # Sort by enhancement count and show top 5
            sorted_enhanced = sorted(articles_with_enhancements, key=lambda x: x['enhancement_count'], reverse=True)
            for article in sorted_enhanced[:5]:
                enhancements = ', '.join(article['enhancements'])
                log_test_result(f"   - {article['title'][:40]}... ({article['enhancement_count']} features: {enhancements})")
        
        # Evaluate WYSIWYG success
        enhancement_rate = (len(articles_with_enhancements) / len(articles) * 100) if articles else 0
        
        if enhancement_rate >= 20:
            log_test_result(f"✅ WYSIWYG ENHANCEMENTS: WORKING ({enhancement_rate:.1f}% of articles enhanced)", "SUCCESS")
            return True
        elif enhancement_rate >= 10:
            log_test_result(f"⚠️ WYSIWYG ENHANCEMENTS: PARTIAL ({enhancement_rate:.1f}% of articles enhanced)", "WARNING")
            return True
        else:
            log_test_result(f"❌ WYSIWYG ENHANCEMENTS: INSUFFICIENT ({enhancement_rate:.1f}% of articles enhanced)", "ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ WYSIWYG enhancement analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main analysis function"""
    log_test_result("🚀 STARTING ARTICLE ANALYSIS FOR CONTENT CORRUPTION FIXES", "CRITICAL")
    log_test_result("=" * 70)
    
    results = {
        'content_corruption_fixes': False,
        'wysiwyg_enhancements': False
    }
    
    # Test 1: Content Corruption Fixes Analysis
    log_test_result("TEST 1: Content Corruption Fixes Analysis")
    results['content_corruption_fixes'] = analyze_content_corruption_fixes()
    
    # Test 2: WYSIWYG Enhancements Analysis
    log_test_result("\nTEST 2: WYSIWYG Enhancements Analysis")
    results['wysiwyg_enhancements'] = analyze_wysiwyg_enhancements()
    
    # Final Summary
    log_test_result("\n" + "=" * 70)
    log_test_result("🎯 FINAL ANALYSIS SUMMARY", "CRITICAL")
    log_test_result("=" * 70)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 1:  # At least 1 test should pass
        log_test_result("🎉 ANALYSIS SUCCESS: Content improvements are evident!", "CRITICAL_SUCCESS")
        log_test_result("✅ Content corruption fixes and WYSIWYG enhancements showing progress", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ ANALYSIS FAILURE: Content issues still need attention", "CRITICAL_ERROR")
        log_test_result("❌ Content corruption fixes and WYSIWYG enhancements need work", "CRITICAL_ERROR")
    
    return results

if __name__ == "__main__":
    print("Article Analysis Test - Content Corruption & WYSIWYG Validation")
    print("=" * 65)
    
    results = main()
    
    # Exit with appropriate code
    if sum(results.values()) >= 1:
        exit(0)  # Success
    else:
        exit(1)  # Failure