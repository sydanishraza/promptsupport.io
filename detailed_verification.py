#!/usr/bin/env python3
"""
DETAILED VERIFICATION OF BEAUTIFULSOUP-BASED FIXES
Comprehensive analysis of the specific fixes mentioned in the review request
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Backend URL
BACKEND_URL = "https://smartchunk.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_result(message, status="INFO"):
    """Log results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def detailed_html_wrapper_analysis():
    """Detailed analysis of HTML wrapper cleaning"""
    try:
        log_result("🔍 DETAILED HTML WRAPPER CLEANING ANALYSIS", "CRITICAL")
        log_result("=" * 70)
        
        # Get articles
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_result("❌ Failed to get articles", "ERROR")
            return False
        
        articles = response.json().get('articles', [])
        log_result(f"📚 Analyzing {len(articles)} articles for wrapper issues")
        
        # Specific patterns mentioned in review request
        wrapper_patterns = {
            'markdown_code_blocks': [r'```html', r'```js', r'```javascript', r'```css'],
            'html_document_structure': [r'<!DOCTYPE[^>]*>', r'<html[^>]*>', r'<head[^>]*>', r'<body[^>]*>'],
            'meta_elements': [r'<title[^>]*>', r'<meta[^>]*>', r'<link[^>]*>', r'<style[^>]*>', r'<script[^>]*>'],
            'wrapper_artifacts': [r'```', r'`{3,}', r'^\s*```\s*$']
        }
        
        total_issues = 0
        clean_articles = 0
        
        for i, article in enumerate(articles):
            title = article.get('title', 'Untitled')[:60]
            content = article.get('content', '')
            
            log_result(f"\n📄 Article {i+1}: {title}")
            log_result(f"   Content length: {len(content)} characters")
            
            article_issues = {}
            article_clean = True
            
            # Check each pattern category
            for category, patterns in wrapper_patterns.items():
                found_patterns = []
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        found_patterns.extend(matches)
                
                if found_patterns:
                    article_issues[category] = found_patterns
                    article_clean = False
                    log_result(f"   ❌ {category}: {len(found_patterns)} issues found")
                    for match in found_patterns[:2]:  # Show first 2
                        log_result(f"      - '{match[:50]}...'")
                else:
                    log_result(f"   ✅ {category}: Clean")
            
            # Check if article starts with proper semantic HTML
            soup = BeautifulSoup(content, 'html.parser')
            first_element = soup.find()
            if first_element:
                if first_element.name in ['h2', 'h3', 'p', 'div']:
                    log_result(f"   ✅ Starts with proper semantic HTML: <{first_element.name}>")
                else:
                    log_result(f"   ⚠️ Starts with: <{first_element.name}> (not ideal)")
            
            if article_clean:
                clean_articles += 1
                log_result(f"   🎉 Article is CLEAN - no wrapper issues")
            else:
                total_issues += len([item for sublist in article_issues.values() for item in sublist])
        
        # Summary
        log_result("\n" + "=" * 70)
        log_result("📊 HTML WRAPPER CLEANING RESULTS SUMMARY:")
        log_result(f"   Total Articles: {len(articles)}")
        log_result(f"   Clean Articles: {clean_articles}")
        log_result(f"   Articles with Issues: {len(articles) - clean_articles}")
        log_result(f"   Total Issues Found: {total_issues}")
        
        success_rate = (clean_articles / len(articles)) * 100 if articles else 0
        log_result(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            log_result("🎉 HTML WRAPPER ELIMINATION: 100% SUCCESS ACHIEVED", "CRITICAL_SUCCESS")
            return True
        else:
            log_result(f"❌ HTML WRAPPER ELIMINATION: {success_rate:.1f}% success (not 100%)", "CRITICAL_ERROR")
            return False
            
    except Exception as e:
        log_result(f"❌ HTML wrapper analysis failed: {e}", "ERROR")
        return False

def detailed_text_deduplication_analysis():
    """Detailed analysis of text deduplication using BeautifulSoup"""
    try:
        log_result("🔍 DETAILED TEXT DEDUPLICATION ANALYSIS", "CRITICAL")
        log_result("=" * 70)
        
        # Get articles
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_result("❌ Failed to get articles", "ERROR")
            return False
        
        articles = response.json().get('articles', [])
        log_result(f"📚 Analyzing {len(articles)} articles for text duplication")
        
        total_duplications = 0
        clean_articles = 0
        
        for i, article in enumerate(articles):
            title = article.get('title', 'Untitled')[:60]
            content = article.get('content', '')
            
            log_result(f"\n📄 Article {i+1}: {title}")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            
            log_result(f"   Text content length: {len(text_content)} characters")
            
            # Specific duplication patterns mentioned in review
            duplication_patterns = {
                'sentence_level': r'([^.!?]{10,}[.!?])\s*\1',  # "Text.Text." patterns (min 10 chars)
                'word_level': r'\b(\w{3,})\s+\1\b',  # "Word Word" patterns (min 3 chars)
                'phrase_level': r'(\b\w+(?:\s+\w+){2,5}\b)\s+\1',  # "Complete phrase complete phrase"
                'coordinate_duplication': r'(\{[^}]+\})\s*\1',  # Coordinate duplications
                'list_item_duplication': r'([^.]{20,}\.)\s*\1',  # List item duplications (min 20 chars)
                'technical_duplication': r'(\b(?:function|const|var|let)\s+\w+[^;]{10,};?)\s*\1'  # Technical content duplication
            }
            
            article_duplications = {}
            article_clean = True
            
            for pattern_name, pattern in duplication_patterns.items():
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    article_duplications[pattern_name] = matches
                    article_clean = False
                    log_result(f"   ❌ {pattern_name}: {len(matches)} duplications found")
                    for match in matches[:2]:  # Show first 2
                        match_text = match if isinstance(match, str) else match[0] if isinstance(match, tuple) else str(match)
                        log_result(f"      - '{match_text[:40]}...'")
                else:
                    log_result(f"   ✅ {pattern_name}: Clean")
            
            if article_clean:
                clean_articles += 1
                log_result(f"   🎉 Article is CLEAN - no text duplications")
            else:
                total_duplications += sum(len(matches) for matches in article_duplications.values())
        
        # Summary
        log_result("\n" + "=" * 70)
        log_result("📊 TEXT DEDUPLICATION RESULTS SUMMARY:")
        log_result(f"   Total Articles: {len(articles)}")
        log_result(f"   Clean Articles: {clean_articles}")
        log_result(f"   Articles with Duplications: {len(articles) - clean_articles}")
        log_result(f"   Total Duplications Found: {total_duplications}")
        
        success_rate = (clean_articles / len(articles)) * 100 if articles else 0
        log_result(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            log_result("🎉 TEXT DEDUPLICATION: 100% SUCCESS ACHIEVED", "CRITICAL_SUCCESS")
            return True
        else:
            log_result(f"❌ TEXT DEDUPLICATION: {success_rate:.1f}% success (not 100%)", "CRITICAL_ERROR")
            return False
            
    except Exception as e:
        log_result(f"❌ Text deduplication analysis failed: {e}", "ERROR")
        return False

def detailed_wysiwyg_features_analysis():
    """Detailed analysis of WYSIWYG editor features"""
    try:
        log_result("🔍 DETAILED WYSIWYG FEATURES ANALYSIS", "CRITICAL")
        log_result("=" * 70)
        
        # Get articles
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_result("❌ Failed to get articles", "ERROR")
            return False
        
        articles = response.json().get('articles', [])
        log_result(f"📚 Analyzing {len(articles)} articles for WYSIWYG features")
        
        wysiwyg_features = {
            'mini_toc': 0,
            'callouts': 0,
            'anchor_links': 0,
            'enhanced_lists': 0,
            'code_blocks': 0,
            'semantic_headings': 0,
            'cross_references': 0
        }
        
        for i, article in enumerate(articles):
            title = article.get('title', 'Untitled')[:60]
            content = article.get('content', '')
            
            log_result(f"\n📄 Article {i+1}: {title}")
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for Mini-TOC
            mini_toc = soup.find_all(['div'], class_=re.compile(r'mini-toc|toc'))
            if mini_toc:
                wysiwyg_features['mini_toc'] += 1
                log_result(f"   ✅ Mini-TOC: {len(mini_toc)} found")
            else:
                log_result(f"   ❌ Mini-TOC: Not found")
            
            # Check for Callouts
            callouts = soup.find_all(['div'], class_=re.compile(r'callout'))
            if callouts:
                wysiwyg_features['callouts'] += 1
                log_result(f"   ✅ Callouts: {len(callouts)} found")
            else:
                log_result(f"   ❌ Callouts: Not found")
            
            # Check for Anchor Links
            anchor_links = soup.find_all('a', href=re.compile(r'^#'))
            if anchor_links:
                wysiwyg_features['anchor_links'] += 1
                log_result(f"   ✅ Anchor Links: {len(anchor_links)} found")
            else:
                log_result(f"   ❌ Anchor Links: Not found")
            
            # Check for Enhanced Lists
            enhanced_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'doc-list'))
            if enhanced_lists:
                wysiwyg_features['enhanced_lists'] += 1
                log_result(f"   ✅ Enhanced Lists: {len(enhanced_lists)} found")
            else:
                log_result(f"   ❌ Enhanced Lists: Not found")
            
            # Check for Code Blocks
            code_blocks = soup.find_all(['pre', 'code'])
            working_code_blocks = 0
            for block in code_blocks:
                if len(block.get_text().strip()) > 10:
                    working_code_blocks += 1
            if working_code_blocks > 0:
                wysiwyg_features['code_blocks'] += 1
                log_result(f"   ✅ Working Code Blocks: {working_code_blocks} found")
            else:
                log_result(f"   ❌ Working Code Blocks: Not found")
            
            # Check for Semantic Headings
            headings = soup.find_all(['h2', 'h3', 'h4'])
            if headings:
                wysiwyg_features['semantic_headings'] += 1
                log_result(f"   ✅ Semantic Headings: {len(headings)} found")
            else:
                log_result(f"   ❌ Semantic Headings: Not found")
            
            # Check for Cross-References
            cross_refs = soup.find_all('a', href=re.compile(r'/content-library/article/'))
            if cross_refs:
                wysiwyg_features['cross_references'] += 1
                log_result(f"   ✅ Cross-References: {len(cross_refs)} found")
            else:
                log_result(f"   ❌ Cross-References: Not found")
        
        # Summary
        log_result("\n" + "=" * 70)
        log_result("📊 WYSIWYG FEATURES ANALYSIS SUMMARY:")
        total_articles = len(articles)
        for feature, count in wysiwyg_features.items():
            percentage = (count / total_articles) * 100 if total_articles > 0 else 0
            status = "✅" if percentage >= 50 else "⚠️"
            log_result(f"   {feature.replace('_', ' ').title()}: {count}/{total_articles} ({percentage:.1f}%) {status}")
        
        # Overall WYSIWYG success
        avg_percentage = sum((count / total_articles) * 100 for count in wysiwyg_features.values()) / len(wysiwyg_features) if total_articles > 0 else 0
        log_result(f"   Overall WYSIWYG Features: {avg_percentage:.1f}%")
        
        return avg_percentage >= 60  # 60% threshold for WYSIWYG features
        
    except Exception as e:
        log_result(f"❌ WYSIWYG features analysis failed: {e}", "ERROR")
        return False

def run_detailed_verification():
    """Run detailed verification of BeautifulSoup-based fixes"""
    log_result("🚀 STARTING DETAILED BEAUTIFULSOUP FIXES VERIFICATION", "CRITICAL")
    log_result("Testing specific fixes mentioned in review request")
    log_result("=" * 80)
    
    results = {
        'html_wrapper_cleaning': False,
        'text_deduplication': False,
        'wysiwyg_features': False
    }
    
    # Test 1: HTML Wrapper Cleaning
    log_result("\nTEST 1: COMPREHENSIVE HTML WRAPPER CLEANING")
    results['html_wrapper_cleaning'] = detailed_html_wrapper_analysis()
    
    # Test 2: Text Deduplication
    log_result("\nTEST 2: COMPREHENSIVE TEXT DEDUPLICATION")
    results['text_deduplication'] = detailed_text_deduplication_analysis()
    
    # Test 3: WYSIWYG Features
    log_result("\nTEST 3: WYSIWYG EDITOR FEATURES")
    results['wysiwyg_features'] = detailed_wysiwyg_features_analysis()
    
    # Final Summary
    log_result("\n" + "=" * 80)
    log_result("🎯 DETAILED VERIFICATION RESULTS", "CRITICAL")
    log_result("=" * 80)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Critical success criteria from review request
    critical_tests = ['html_wrapper_cleaning', 'text_deduplication']
    critical_passed = all(results[test] for test in critical_tests)
    
    if critical_passed:
        log_result("🎉 CRITICAL SUCCESS: BeautifulSoup-based fixes working perfectly!", "CRITICAL_SUCCESS")
        log_result("✅ HTML wrapper elimination: 100% success rate achieved", "CRITICAL_SUCCESS")
        log_result("✅ Text deduplication: 100% success rate achieved", "CRITICAL_SUCCESS")
        log_result("✅ All remaining Content Library issues completely resolved", "CRITICAL_SUCCESS")
        log_result("✅ User feedback requirements met with 100% success", "CRITICAL_SUCCESS")
    else:
        log_result("❌ CRITICAL FAILURE: Some BeautifulSoup fixes not working", "CRITICAL_ERROR")
        if not results['html_wrapper_cleaning']:
            log_result("❌ HTML wrapper cleaning still has issues", "CRITICAL_ERROR")
        if not results['text_deduplication']:
            log_result("❌ Text deduplication still has issues", "CRITICAL_ERROR")
    
    return results

if __name__ == "__main__":
    print("Detailed BeautifulSoup Fixes Verification")
    print("=" * 50)
    
    results = run_detailed_verification()
    
    # Exit with appropriate code
    critical_tests = ['html_wrapper_cleaning', 'text_deduplication']
    critical_passed = all(results.get(test, False) for test in critical_tests)
    
    if critical_passed:
        exit(0)  # Success
    else:
        exit(1)  # Failure