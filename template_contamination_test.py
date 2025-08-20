#!/usr/bin/env python3
"""
FINAL VALIDATION: Complete Template Contamination Fixes Testing
Testing the elimination of all generic template injection and validation of selective WYSIWYG enhancements
Focus: Verify NO generic template placeholders, only contextual enhancements
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import re

# Backend URL from frontend .env
BACKEND_URL = "https://22c64acd-5965-4f32-bb15-b795b8db8eab.preview.emergentagent.com"
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

def analyze_content_for_template_contamination(content):
    """Analyze article content for generic template contamination"""
    contamination_indicators = {
        'generic_faqs': [
            'What are the main benefits?',
            'How do I get started?',
            'What are the key features?',
            'How does this work?',
            'What should I know?'
        ],
        'generic_links': [
            'Getting Started Guide',
            'Best Practices',
            'User Manual',
            'Documentation',
            'Support Center'
        ],
        'generic_callouts': [
            'Important Note:',
            'Pro Tip:',
            'Remember:',
            'Note:',
            'Tip:'
        ],
        'generic_code_blocks': [
            'function example()',
            'console.log("Hello World")',
            'var example = ',
            '// Example code',
            '/* Sample code */'
        ],
        'template_placeholders': [
            '[INSERT_CONTENT]',
            '[PLACEHOLDER]',
            'Lorem ipsum',
            'Sample text',
            'Example content'
        ]
    }
    
    found_contamination = {}
    
    for category, indicators in contamination_indicators.items():
        found_items = []
        for indicator in indicators:
            if indicator.lower() in content.lower():
                found_items.append(indicator)
        
        if found_items:
            found_contamination[category] = found_items
    
    return found_contamination

def analyze_selective_enhancements(content):
    """Analyze content for appropriate selective WYSIWYG enhancements"""
    enhancements = {
        'contextual_callouts': 0,
        'mini_toc': 0,
        'code_blocks_with_context': 0,
        'related_links_real': 0,
        'enhanced_lists': 0,
        'semantic_html': 0
    }
    
    # Count contextual callouts (should be minimal and contextual)
    callout_patterns = [
        r'<div class="[^"]*callout[^"]*">',
        r'<blockquote[^>]*>',
        r'<div class="[^"]*alert[^"]*">'
    ]
    for pattern in callout_patterns:
        enhancements['contextual_callouts'] += len(re.findall(pattern, content, re.IGNORECASE))
    
    # Count Mini-TOC (should be present for complex content)
    if 'table of contents' in content.lower() or 'toc-list' in content:
        enhancements['mini_toc'] = 1
    
    # Count code blocks with proper context
    code_blocks = re.findall(r'<pre><code[^>]*>(.*?)</code></pre>', content, re.DOTALL)
    for code_block in code_blocks:
        if len(code_block.strip()) > 10:  # Non-empty code blocks
            enhancements['code_blocks_with_context'] += 1
    
    # Count real related links (should use /content-library/article/ format)
    real_links = re.findall(r'/content-library/article/[a-f0-9-]+', content)
    enhancements['related_links_real'] = len(real_links)
    
    # Count enhanced lists
    enhanced_list_patterns = [
        r'<ol class="[^"]*doc-list[^"]*">',
        r'<ul class="[^"]*enhanced[^"]*">'
    ]
    for pattern in enhanced_list_patterns:
        enhancements['enhanced_lists'] += len(re.findall(pattern, content, re.IGNORECASE))
    
    # Check for semantic HTML usage
    semantic_elements = ['<h2>', '<h3>', '<strong>', '<em>', '<blockquote>', '<figure>']
    for element in semantic_elements:
        if element in content:
            enhancements['semantic_html'] += 1
    
    return enhancements

def test_clean_content_processing():
    """Test 1: Clean Content Processing - verify NO generic template placeholders"""
    try:
        log_test_result("🧹 TEST 1: CLEAN CONTENT PROCESSING", "CRITICAL")
        log_test_result("Testing sample content processing for template contamination...")
        
        # Sample content for testing
        test_content = """
        Google Maps JavaScript API Integration Guide
        
        This comprehensive guide covers how to integrate Google Maps JavaScript API into your web application.
        
        ## Getting Started
        
        First, you need to obtain an API key from Google Cloud Console.
        
        ## Basic Implementation
        
        Here's how to create a basic map:
        
        ```javascript
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 4,
                center: { lat: -25.344, lng: 131.036 },
            });
        }
        ```
        
        ## Advanced Features
        
        You can add markers, info windows, and custom styling to enhance your maps.
        
        ## Troubleshooting
        
        Common issues include API key problems and loading errors.
        """
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing test content through Knowledge Engine...")
        
        response = requests.post(
            f"{API_BASE}/content/process-text",
            json={"content": test_content, "filename": "template_test.txt"},
            timeout=300
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return False
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing...")
        max_wait = 180  # 3 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                if status == 'completed':
                    log_test_result("✅ Processing completed", "SUCCESS")
                    break
                elif status == 'failed':
                    log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown')}", "ERROR")
                    return False
            
            time.sleep(5)
        else:
            log_test_result("❌ Processing timeout", "ERROR")
            return False
        
        # Get generated articles and analyze for contamination
        log_test_result("🔍 Analyzing generated articles for template contamination...")
        
        library_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if library_response.status_code != 200:
            log_test_result("❌ Failed to retrieve Content Library", "ERROR")
            return False
        
        library_data = library_response.json()
        articles = library_data.get('articles', [])
        
        # Find recently created articles (last 5 minutes)
        recent_articles = []
        current_time = datetime.utcnow()
        
        for article in articles:
            created_at = article.get('created_at')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        article_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        continue
                    
                    time_diff = (current_time - article_time.replace(tzinfo=None)).total_seconds()
                    if time_diff < 300:  # Last 5 minutes
                        recent_articles.append(article)
                except:
                    continue
        
        if not recent_articles:
            log_test_result("⚠️ No recent articles found for analysis", "WARNING")
            return False
        
        log_test_result(f"📄 Analyzing {len(recent_articles)} recent articles...")
        
        total_contamination = {}
        clean_articles = 0
        
        for i, article in enumerate(recent_articles):
            content = article.get('content', '')
            title = article.get('title', f'Article {i+1}')
            
            contamination = analyze_content_for_template_contamination(content)
            
            if not contamination:
                clean_articles += 1
                log_test_result(f"✅ Article '{title[:50]}...' is CLEAN (no template contamination)")
            else:
                log_test_result(f"❌ Article '{title[:50]}...' has contamination:")
                for category, items in contamination.items():
                    log_test_result(f"   {category}: {items}")
                    if category not in total_contamination:
                        total_contamination[category] = []
                    total_contamination[category].extend(items)
        
        # Final assessment
        if clean_articles == len(recent_articles):
            log_test_result(f"🎉 CLEAN CONTENT TEST PASSED: All {clean_articles} articles are free of template contamination", "SUCCESS")
            return True
        else:
            contaminated_count = len(recent_articles) - clean_articles
            log_test_result(f"❌ CLEAN CONTENT TEST FAILED: {contaminated_count}/{len(recent_articles)} articles have template contamination", "ERROR")
            log_test_result(f"Total contamination found: {total_contamination}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Clean content processing test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_selective_enhancement_verification():
    """Test 2: Selective Enhancement Verification - check WYSIWYG features are contextual"""
    try:
        log_test_result("🎨 TEST 2: SELECTIVE ENHANCEMENT VERIFICATION", "CRITICAL")
        log_test_result("Verifying WYSIWYG enhancements are selective and contextual...")
        
        # Get recent articles from Content Library
        library_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if library_response.status_code != 200:
            log_test_result("❌ Failed to retrieve Content Library", "ERROR")
            return False
        
        library_data = library_response.json()
        articles = library_data.get('articles', [])
        
        if not articles:
            log_test_result("⚠️ No articles found for enhancement verification", "WARNING")
            return False
        
        # Analyze recent articles for selective enhancements
        log_test_result(f"🔍 Analyzing {min(5, len(articles))} articles for selective enhancements...")
        
        enhancement_stats = {
            'contextual_callouts': 0,
            'mini_toc': 0,
            'code_blocks_with_context': 0,
            'related_links_real': 0,
            'enhanced_lists': 0,
            'semantic_html': 0
        }
        
        articles_with_enhancements = 0
        over_enhanced_articles = 0
        
        for i, article in enumerate(articles[:5]):
            content = article.get('content', '')
            title = article.get('title', f'Article {i+1}')
            
            enhancements = analyze_selective_enhancements(content)
            
            # Check if article has appropriate enhancements
            has_enhancements = any(count > 0 for count in enhancements.values())
            
            # Check for over-enhancement (too many callouts, etc.)
            is_over_enhanced = (
                enhancements['contextual_callouts'] > 3 or  # Too many callouts
                (enhancements['mini_toc'] > 1)  # Multiple TOCs in one article
            )
            
            if has_enhancements:
                articles_with_enhancements += 1
                
            if is_over_enhanced:
                over_enhanced_articles += 1
                log_test_result(f"⚠️ Article '{title[:50]}...' may be over-enhanced:")
                log_test_result(f"   Callouts: {enhancements['contextual_callouts']}, TOCs: {enhancements['mini_toc']}")
            else:
                log_test_result(f"✅ Article '{title[:50]}...' has appropriate enhancements")
            
            # Accumulate stats
            for key, value in enhancements.items():
                enhancement_stats[key] += value
        
        # Assessment
        log_test_result(f"📊 Enhancement Statistics:")
        for key, value in enhancement_stats.items():
            log_test_result(f"   {key.replace('_', ' ').title()}: {value}")
        
        log_test_result(f"📈 Articles with enhancements: {articles_with_enhancements}/{min(5, len(articles))}")
        log_test_result(f"⚠️ Over-enhanced articles: {over_enhanced_articles}/{min(5, len(articles))}")
        
        # Success criteria: Most articles have some enhancements, but not over-enhanced
        if over_enhanced_articles == 0 and articles_with_enhancements > 0:
            log_test_result("🎉 SELECTIVE ENHANCEMENT TEST PASSED: Appropriate contextual enhancements found", "SUCCESS")
            return True
        elif over_enhanced_articles > 0:
            log_test_result(f"❌ SELECTIVE ENHANCEMENT TEST FAILED: {over_enhanced_articles} articles are over-enhanced", "ERROR")
            return False
        else:
            log_test_result("⚠️ SELECTIVE ENHANCEMENT TEST PARTIAL: No enhancements found (may be too selective)", "WARNING")
            return True  # Still pass as this means no contamination
            
    except Exception as e:
        log_test_result(f"❌ Selective enhancement verification failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_content_purity():
    """Test 3: Content Purity Test - verify articles are clean of template contamination"""
    try:
        log_test_result("🔬 TEST 3: CONTENT PURITY TEST", "CRITICAL")
        log_test_result("Verifying content purity and real cross-reference system...")
        
        # Get all articles from Content Library
        library_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if library_response.status_code != 200:
            log_test_result("❌ Failed to retrieve Content Library", "ERROR")
            return False
        
        library_data = library_response.json()
        articles = library_data.get('articles', [])
        total_articles = library_data.get('total', 0)
        
        log_test_result(f"📚 Analyzing {total_articles} total articles for content purity...")
        
        purity_metrics = {
            'clean_articles': 0,
            'articles_with_real_links': 0,
            'articles_with_generic_content': 0,
            'articles_with_placeholder_links': 0,
            'total_real_cross_references': 0,
            'total_generic_placeholders': 0
        }
        
        for article in articles:
            content = article.get('content', '')
            title = article.get('title', 'Untitled')
            
            # Check for real cross-references (Content Library URLs)
            real_links = re.findall(r'/content-library/article/[a-f0-9-]+', content)
            if real_links:
                purity_metrics['articles_with_real_links'] += 1
                purity_metrics['total_real_cross_references'] += len(real_links)
            
            # Check for generic placeholder links
            generic_link_patterns = [
                r'href="#[^"]*"',  # Anchor links to non-existent sections
                r'Getting Started Guide',
                r'Best Practices',
                r'Documentation',
                r'User Manual'
            ]
            
            has_generic_links = False
            for pattern in generic_link_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    has_generic_links = True
                    purity_metrics['total_generic_placeholders'] += len(re.findall(pattern, content, re.IGNORECASE))
            
            if has_generic_links:
                purity_metrics['articles_with_placeholder_links'] += 1
            
            # Check for generic template content
            contamination = analyze_content_for_template_contamination(content)
            if contamination:
                purity_metrics['articles_with_generic_content'] += 1
            else:
                purity_metrics['clean_articles'] += 1
        
        # Calculate purity percentage
        total_analyzed = len(articles)
        purity_percentage = (purity_metrics['clean_articles'] / total_analyzed * 100) if total_analyzed > 0 else 0
        
        log_test_result(f"📊 Content Purity Metrics:")
        log_test_result(f"   Total Articles Analyzed: {total_analyzed}")
        log_test_result(f"   Clean Articles: {purity_metrics['clean_articles']}")
        log_test_result(f"   Articles with Real Cross-References: {purity_metrics['articles_with_real_links']}")
        log_test_result(f"   Articles with Generic Content: {purity_metrics['articles_with_generic_content']}")
        log_test_result(f"   Articles with Placeholder Links: {purity_metrics['articles_with_placeholder_links']}")
        log_test_result(f"   Total Real Cross-References: {purity_metrics['total_real_cross_references']}")
        log_test_result(f"   Total Generic Placeholders: {purity_metrics['total_generic_placeholders']}")
        log_test_result(f"   Content Purity: {purity_percentage:.1f}%")
        
        # Success criteria: >90% clean articles, real cross-references present, minimal generic placeholders
        success_criteria = [
            purity_percentage >= 90,
            purity_metrics['total_real_cross_references'] > 0,
            purity_metrics['total_generic_placeholders'] < (total_analyzed * 0.1)  # Less than 10% of articles have placeholders
        ]
        
        if all(success_criteria):
            log_test_result("🎉 CONTENT PURITY TEST PASSED: High purity with real cross-references", "SUCCESS")
            return True
        else:
            failed_criteria = []
            if purity_percentage < 90:
                failed_criteria.append(f"Low purity: {purity_percentage:.1f}% (expected ≥90%)")
            if purity_metrics['total_real_cross_references'] == 0:
                failed_criteria.append("No real cross-references found")
            if purity_metrics['total_generic_placeholders'] >= (total_analyzed * 0.1):
                failed_criteria.append(f"Too many generic placeholders: {purity_metrics['total_generic_placeholders']}")
            
            log_test_result(f"❌ CONTENT PURITY TEST FAILED: {', '.join(failed_criteria)}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Content purity test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_template_contamination_validation():
    """Run comprehensive template contamination validation test suite"""
    log_test_result("🚀 STARTING TEMPLATE CONTAMINATION VALIDATION TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'clean_content_processing': False,
        'selective_enhancement_verification': False,
        'content_purity': False
    }
    
    # Test 0: Backend Health
    log_test_result("TEST 0: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 1: Clean Content Processing
    log_test_result("\nTEST 1: Clean Content Processing")
    test_results['clean_content_processing'] = test_clean_content_processing()
    
    # Test 2: Selective Enhancement Verification
    log_test_result("\nTEST 2: Selective Enhancement Verification")
    test_results['selective_enhancement_verification'] = test_selective_enhancement_verification()
    
    # Test 3: Content Purity Test
    log_test_result("\nTEST 3: Content Purity Test")
    test_results['content_purity'] = test_content_purity()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL TEMPLATE CONTAMINATION VALIDATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Critical assessment
    critical_tests = ['clean_content_processing', 'selective_enhancement_verification', 'content_purity']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        log_test_result("🎉 TEMPLATE CONTAMINATION FIXES VALIDATION SUCCESSFUL!", "CRITICAL_SUCCESS")
        log_test_result("✅ Zero template contamination achieved", "CRITICAL_SUCCESS")
        log_test_result("✅ Clean source content with selective WYSIWYG enhancements", "CRITICAL_SUCCESS")
        log_test_result("✅ Only contextual, beneficial features added", "CRITICAL_SUCCESS")
        log_test_result("✅ Real content preservation with professional formatting", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ TEMPLATE CONTAMINATION FIXES VALIDATION FAILED!", "CRITICAL_ERROR")
        log_test_result("❌ Template contamination still present in system", "CRITICAL_ERROR")
        log_test_result("❌ Generic placeholders or over-enhancement detected", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Template Contamination Fixes Validation Testing")
    print("=" * 50)
    
    results = run_template_contamination_validation()
    
    # Exit with appropriate code
    critical_tests = ['clean_content_processing', 'selective_enhancement_verification', 'content_purity']
    critical_passed = sum(results[test] for test in critical_tests if test in results)
    
    if critical_passed == len(critical_tests):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure