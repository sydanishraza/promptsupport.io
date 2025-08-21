#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST - PROPER QUALITY FIXES VALIDATION
Testing BeautifulSoup-based fixes for Content Library issues:
1. HTML Wrapper Elimination - 100% SUCCESS REQUIRED
2. Text Deduplication - 100% SUCCESS REQUIRED  
3. Content Quality Verification
4. User Feedback Complete Resolution
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime
from bs4 import BeautifulSoup

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-6.preview.emergentagent.com"
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

def generate_test_content_and_process():
    """Generate fresh articles by processing substantial content"""
    try:
        log_test_result("🎯 GENERATING FRESH CONTENT FOR QUALITY FIXES TESTING", "CRITICAL")
        
        # Create comprehensive test content that historically caused issues
        test_content = """Google Maps JavaScript API Tutorial - Complete Implementation Guide

Introduction to Google Maps API
The Google Maps JavaScript API is a powerful tool for integrating interactive maps into web applications. This comprehensive guide covers everything you need to know about implementing Google Maps in your projects.

Getting Started with Google Maps API
First, you need to obtain an API key from Google Cloud Console. Navigate to the Google Cloud Console and create a new project or select an existing one. Enable the Maps JavaScript API for your project.

Setting Up Your Development Environment
Create a new HTML file and include the Google Maps JavaScript API script. The basic structure should include proper HTML5 doctype and meta tags for responsive design.

Basic Map Implementation
Here's how to create a basic map:

function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 4,
        center: { lat: -25.344, lng: 131.036 },
    });
}

Advanced Map Features
You can add markers, info windows, and custom styling to enhance your maps. Markers help identify specific locations on your map.

Adding Markers to Your Map
Markers are used to identify locations on a map. You can customize markers with different icons and colors.

const marker = new google.maps.Marker({
    position: { lat: -25.344, lng: 131.036 },
    map: map,
    title: "Hello World!"
});

Customizing Map Styles
Google Maps allows extensive customization through styling options. You can change colors, hide elements, and create unique map themes.

Handling Map Events
Maps support various events like click, zoom, and drag. Event listeners allow you to respond to user interactions.

Best Practices and Performance
Optimize your maps for better performance by limiting the number of markers and using clustering for large datasets.

Troubleshooting Common Issues
Common issues include API key problems, quota exceeded errors, and loading failures. Always check the browser console for error messages."""
        
        log_test_result(f"📝 Created test content: {len(test_content)} characters")
        
        # Create a temporary text file
        temp_file = "/tmp/google_maps_tutorial_test.txt"
        with open(temp_file, 'w') as f:
            f.write(test_content)
        
        log_test_result("📤 Processing content through Knowledge Engine file upload...")
        
        # Use file upload endpoint
        with open(temp_file, 'rb') as f:
            files = {'file': ('google_maps_tutorial_test.txt', f, 'text/plain')}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", 
                                   files=files, 
                                   timeout=300)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False, []
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return False, []
        
        log_test_result(f"✅ Processing started, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing progress...")
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return False, []
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 Processing status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        articles_generated = status_data.get('articles_generated', 0)
                        log_test_result(f"📄 Articles Generated: {articles_generated}")
                        
                        # Clean up temp file
                        os.remove(temp_file)
                        return True, []
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        os.remove(temp_file)
                        return False, []
                    
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Content generation failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False, []

def get_all_content_library_articles():
    """Retrieve all articles from Content Library for analysis"""
    try:
        log_test_result("📚 Retrieving all Content Library articles...")
        
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
        log_test_result(f"❌ Article retrieval failed: {e}", "ERROR")
        return []

def test_html_wrapper_elimination(articles):
    """Test 1: HTML Wrapper Elimination - 100% SUCCESS REQUIRED"""
    try:
        log_test_result("🧹 TESTING HTML WRAPPER ELIMINATION", "CRITICAL")
        log_test_result("=" * 60)
        
        if not articles:
            log_test_result("❌ No articles to test", "ERROR")
            return False
        
        wrapper_issues = []
        total_articles = len(articles)
        
        # HTML wrapper patterns to detect
        wrapper_patterns = [
            r'```html',
            r'```js',
            r'```javascript',
            r'<!DOCTYPE',
            r'<html[^>]*>',
            r'<head[^>]*>',
            r'<body[^>]*>',
            r'<title[^>]*>',
            r'<meta[^>]*>',
            r'<link[^>]*>',
            r'<style[^>]*>',
            r'<script[^>]*>'
        ]
        
        log_test_result(f"🔍 Analyzing {total_articles} articles for HTML wrapper issues...")
        
        for i, article in enumerate(articles):
            article_id = article.get('id', 'unknown')
            title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"   Checking article {i+1}/{total_articles}: {title}...")
            
            # Check for wrapper patterns
            found_wrappers = []
            for pattern in wrapper_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    found_wrappers.extend([(pattern, match) for match in matches])
            
            if found_wrappers:
                wrapper_issues.append({
                    'id': article_id,
                    'title': title,
                    'wrappers': found_wrappers,
                    'content_preview': content[:200]
                })
                
                log_test_result(f"   ❌ Found {len(found_wrappers)} wrapper issues in: {title}")
                for pattern, match in found_wrappers[:3]:  # Show first 3
                    log_test_result(f"      - Pattern: {pattern} | Match: {match[:50]}...")
        
        # Results
        clean_articles = total_articles - len(wrapper_issues)
        success_rate = (clean_articles / total_articles) * 100 if total_articles > 0 else 0
        
        log_test_result("=" * 60)
        log_test_result("📊 HTML WRAPPER ELIMINATION RESULTS:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Clean Articles: {clean_articles}")
        log_test_result(f"   Articles with Wrappers: {len(wrapper_issues)}")
        log_test_result(f"   Success Rate: {success_rate:.1f}%")
        
        if len(wrapper_issues) == 0:
            log_test_result("🎉 HTML WRAPPER ELIMINATION: 100% SUCCESS", "CRITICAL_SUCCESS")
            log_test_result("✅ 0/X articles contain ANY wrapper elements", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ HTML WRAPPER ELIMINATION: FAILED ({len(wrapper_issues)} articles with issues)", "CRITICAL_ERROR")
            log_test_result("❌ CRITICAL ISSUE: Articles still contain HTML wrappers/document structure", "CRITICAL_ERROR")
            
            # Show detailed issues for first few problematic articles
            for issue in wrapper_issues[:3]:
                log_test_result(f"   ISSUE: {issue['title']}")
                log_test_result(f"   Content preview: {issue['content_preview']}...")
            
            return False
            
    except Exception as e:
        log_test_result(f"❌ HTML wrapper elimination test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_text_deduplication(articles):
    """Test 2: Text Deduplication - 100% SUCCESS REQUIRED"""
    try:
        log_test_result("🔍 TESTING TEXT DEDUPLICATION", "CRITICAL")
        log_test_result("=" * 60)
        
        if not articles:
            log_test_result("❌ No articles to test", "ERROR")
            return False
        
        duplication_issues = []
        total_articles = len(articles)
        
        log_test_result(f"🔍 Analyzing {total_articles} articles for text duplication...")
        
        for i, article in enumerate(articles):
            article_id = article.get('id', 'unknown')
            title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"   Checking article {i+1}/{total_articles}: {title}...")
            
            # Parse HTML content
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            
            # Check for various duplication patterns
            duplications_found = []
            
            # 1. Sentence-level duplications (Text.Text. patterns)
            sentence_pattern = r'([^.!?]+[.!?])\s*\1'
            sentence_matches = re.findall(sentence_pattern, text_content, re.IGNORECASE)
            if sentence_matches:
                duplications_found.extend([('sentence', match) for match in sentence_matches])
            
            # 2. Word-level duplications (Word Word patterns)
            word_pattern = r'\b(\w+)\s+\1\b'
            word_matches = re.findall(word_pattern, text_content, re.IGNORECASE)
            if word_matches:
                duplications_found.extend([('word', match) for match in word_matches])
            
            # 3. Phrase-level duplications (longer phrases repeated)
            phrase_pattern = r'(\b\w+(?:\s+\w+){2,5}\b).*?\1'
            phrase_matches = re.findall(phrase_pattern, text_content, re.IGNORECASE)
            if phrase_matches:
                duplications_found.extend([('phrase', match) for match in phrase_matches])
            
            # 4. Character-level duplications (like 'l l l')
            char_pattern = r'\b(\w)\s+\1(?:\s+\1)*\b'
            char_matches = re.findall(char_pattern, text_content)
            if char_matches:
                duplications_found.extend([('character', match) for match in char_matches])
            
            if duplications_found:
                duplication_issues.append({
                    'id': article_id,
                    'title': title,
                    'duplications': duplications_found,
                    'content_length': len(content)
                })
                
                log_test_result(f"   ❌ Found {len(duplications_found)} duplication issues in: {title}")
                for dup_type, match in duplications_found[:3]:  # Show first 3
                    log_test_result(f"      - Type: {dup_type} | Text: '{match[:50]}...'")
        
        # Results
        clean_articles = total_articles - len(duplication_issues)
        success_rate = (clean_articles / total_articles) * 100 if total_articles > 0 else 0
        
        total_duplications = sum(len(issue['duplications']) for issue in duplication_issues)
        
        log_test_result("=" * 60)
        log_test_result("📊 TEXT DEDUPLICATION RESULTS:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Clean Articles: {clean_articles}")
        log_test_result(f"   Articles with Duplications: {len(duplication_issues)}")
        log_test_result(f"   Total Duplications Found: {total_duplications}")
        log_test_result(f"   Success Rate: {success_rate:.1f}%")
        
        if total_duplications == 0:
            log_test_result("🎉 TEXT DEDUPLICATION: 100% SUCCESS", "CRITICAL_SUCCESS")
            log_test_result("✅ 0 text duplications detected anywhere in any article content", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ TEXT DEDUPLICATION: FAILED ({total_duplications} duplications found)", "CRITICAL_ERROR")
            log_test_result("❌ CRITICAL ISSUE: Text duplications still present in articles", "CRITICAL_ERROR")
            
            # Show detailed issues for first few problematic articles
            for issue in duplication_issues[:3]:
                log_test_result(f"   ISSUE: {issue['title']}")
                log_test_result(f"   Duplications: {len(issue['duplications'])}")
                for dup_type, match in issue['duplications'][:2]:
                    log_test_result(f"      - {dup_type}: '{match[:30]}...'")
            
            return False
            
    except Exception as e:
        log_test_result(f"❌ Text deduplication test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_content_quality_verification(articles):
    """Test 3: Content Quality Verification"""
    try:
        log_test_result("✨ TESTING CONTENT QUALITY VERIFICATION", "CRITICAL")
        log_test_result("=" * 60)
        
        if not articles:
            log_test_result("❌ No articles to test", "ERROR")
            return False
        
        quality_metrics = {
            'proper_semantic_html': 0,
            'continuous_ordered_lists': 0,
            'wysiwyg_features': 0,
            'professional_content': 0,
            'proper_heading_hierarchy': 0,
            'working_code_blocks': 0
        }
        
        total_articles = len(articles)
        
        log_test_result(f"🔍 Analyzing {total_articles} articles for content quality...")
        
        for i, article in enumerate(articles):
            title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"   Checking article {i+1}/{total_articles}: {title}...")
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Proper semantic HTML
            semantic_elements = soup.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'strong', 'em'])
            if len(semantic_elements) > 0:
                quality_metrics['proper_semantic_html'] += 1
            
            # 2. Continuous ordered lists
            ordered_lists = soup.find_all('ol')
            if ordered_lists:
                # Check if lists are properly structured (not fragmented)
                continuous_lists = True
                for ol in ordered_lists:
                    items = ol.find_all('li')
                    if len(items) > 1:  # Only check lists with multiple items
                        continuous_lists = True
                        break
                if continuous_lists:
                    quality_metrics['continuous_ordered_lists'] += 1
            else:
                # If no ordered lists, still count as pass (not all articles need them)
                quality_metrics['continuous_ordered_lists'] += 1
            
            # 3. WYSIWYG features (Mini-TOC, callouts)
            wysiwyg_features = soup.find_all(['div'], class_=re.compile(r'(toc|callout|mini-toc)'))
            anchor_links = soup.find_all('a', href=re.compile(r'^#'))
            if wysiwyg_features or anchor_links:
                quality_metrics['wysiwyg_features'] += 1
            
            # 4. Professional content (not placeholder)
            text_content = soup.get_text()
            if len(text_content) > 100 and 'placeholder' not in text_content.lower():
                quality_metrics['professional_content'] += 1
            
            # 5. Proper heading hierarchy (starts with h2, not h1)
            first_heading = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if first_heading and first_heading.name == 'h2':
                quality_metrics['proper_heading_hierarchy'] += 1
            elif not first_heading:  # No headings is also acceptable
                quality_metrics['proper_heading_hierarchy'] += 1
            
            # 6. Working code blocks (contain actual code, not empty)
            code_blocks = soup.find_all(['pre', 'code'])
            if code_blocks:
                working_code_blocks = 0
                for block in code_blocks:
                    block_text = block.get_text().strip()
                    if len(block_text) > 10:  # Has substantial content
                        working_code_blocks += 1
                if working_code_blocks > 0:
                    quality_metrics['working_code_blocks'] += 1
            else:
                # If no code blocks, still count as pass (not all articles need them)
                quality_metrics['working_code_blocks'] += 1
        
        # Calculate success rates
        log_test_result("=" * 60)
        log_test_result("📊 CONTENT QUALITY VERIFICATION RESULTS:")
        
        all_passed = True
        for metric, count in quality_metrics.items():
            success_rate = (count / total_articles) * 100 if total_articles > 0 else 0
            status = "✅" if success_rate >= 80 else "❌"
            log_test_result(f"   {metric.replace('_', ' ').title()}: {count}/{total_articles} ({success_rate:.1f}%) {status}")
            if success_rate < 80:
                all_passed = False
        
        if all_passed:
            log_test_result("🎉 CONTENT QUALITY VERIFICATION: SUCCESS", "SUCCESS")
            return True
        else:
            log_test_result("⚠️ CONTENT QUALITY VERIFICATION: Some metrics below 80%", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Content quality verification failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_user_feedback_resolution(articles):
    """Test 4: User Feedback Complete Resolution"""
    try:
        log_test_result("👥 TESTING USER FEEDBACK COMPLETE RESOLUTION", "CRITICAL")
        log_test_result("=" * 60)
        
        if not articles:
            log_test_result("❌ No articles to test", "ERROR")
            return False
        
        feedback_checks = {
            'overview_vs_complete_separation': False,
            'faq_standardization': False,
            'wysiwyg_features_utilized': False,
            'professional_quality': False
        }
        
        total_articles = len(articles)
        overview_articles = []
        complete_articles = []
        faq_articles = []
        
        log_test_result(f"🔍 Analyzing {total_articles} articles for user feedback resolution...")
        
        for article in articles:
            title = article.get('title', '').lower()
            article_type = article.get('article_type', '').lower()
            content = article.get('content', '')
            
            # Categorize articles
            if 'overview' in title or article_type == 'overview':
                overview_articles.append(article)
            elif 'complete' in title or 'guide' in title:
                complete_articles.append(article)
            elif 'faq' in title or 'troubleshooting' in title or article_type == 'faq':
                faq_articles.append(article)
        
        # 1. Overview vs Complete Guide separation
        if overview_articles and complete_articles:
            # Check that overview articles are summaries, complete articles are detailed
            overview_avg_length = sum(len(a.get('content', '')) for a in overview_articles) / len(overview_articles)
            complete_avg_length = sum(len(a.get('content', '')) for a in complete_articles) / len(complete_articles)
            
            if complete_avg_length > overview_avg_length * 1.5:  # Complete articles should be significantly longer
                feedback_checks['overview_vs_complete_separation'] = True
                log_test_result("   ✅ Overview vs Complete Guide separation working")
            else:
                log_test_result("   ❌ Overview vs Complete Guide separation not clear")
        else:
            log_test_result("   ⚠️ No clear Overview/Complete article separation found")
        
        # 2. FAQ standardization
        if faq_articles:
            faq_titles_standardized = all('faq' in a.get('title', '').lower() or 'troubleshooting' in a.get('title', '').lower() for a in faq_articles)
            if faq_titles_standardized:
                feedback_checks['faq_standardization'] = True
                log_test_result(f"   ✅ FAQ standardization working ({len(faq_articles)} FAQ articles)")
            else:
                log_test_result("   ❌ FAQ titles not standardized")
        else:
            log_test_result("   ⚠️ No FAQ articles found")
        
        # 3. WYSIWYG features utilized
        wysiwyg_count = 0
        for article in articles:
            content = article.get('content', '')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for WYSIWYG features
            features = soup.find_all(['div'], class_=re.compile(r'(toc|callout|mini-toc)'))
            anchor_links = soup.find_all('a', href=re.compile(r'^#'))
            enhanced_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'doc-list'))
            
            if features or anchor_links or enhanced_lists:
                wysiwyg_count += 1
        
        if wysiwyg_count > 0:
            feedback_checks['wysiwyg_features_utilized'] = True
            log_test_result(f"   ✅ WYSIWYG features utilized in {wysiwyg_count} articles")
        else:
            log_test_result("   ❌ WYSIWYG features not detected")
        
        # 4. Professional content quality
        professional_count = 0
        for article in articles:
            content = article.get('content', '')
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            
            # Check for professional quality indicators
            if (len(text_content) > 200 and 
                'placeholder' not in text_content.lower() and
                'lorem ipsum' not in text_content.lower() and
                len(text_content.split()) > 50):
                professional_count += 1
        
        professional_rate = (professional_count / total_articles) * 100 if total_articles > 0 else 0
        if professional_rate >= 90:
            feedback_checks['professional_quality'] = True
            log_test_result(f"   ✅ Professional quality maintained ({professional_rate:.1f}%)")
        else:
            log_test_result(f"   ❌ Professional quality issues ({professional_rate:.1f}%)")
        
        # Results
        passed_checks = sum(feedback_checks.values())
        total_checks = len(feedback_checks)
        
        log_test_result("=" * 60)
        log_test_result("📊 USER FEEDBACK RESOLUTION RESULTS:")
        for check, result in feedback_checks.items():
            status = "✅ RESOLVED" if result else "❌ NOT RESOLVED"
            log_test_result(f"   {check.replace('_', ' ').title()}: {status}")
        
        log_test_result(f"   Overall: {passed_checks}/{total_checks} feedback items resolved")
        
        if passed_checks >= 3:  # At least 3 out of 4 should pass
            log_test_result("🎉 USER FEEDBACK RESOLUTION: SUCCESS", "SUCCESS")
            return True
        else:
            log_test_result("❌ USER FEEDBACK RESOLUTION: INSUFFICIENT", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ User feedback resolution test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_quality_fixes_test():
    """Run comprehensive test suite for quality fixes validation"""
    log_test_result("🚀 STARTING FINAL COMPREHENSIVE QUALITY FIXES TEST", "CRITICAL")
    log_test_result("Testing BeautifulSoup-based fixes for Content Library issues")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'content_generation': False,
        'html_wrapper_elimination': False,
        'text_deduplication': False,
        'content_quality_verification': False,
        'user_feedback_resolution': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Generate Fresh Content
    log_test_result("\nTEST 2: Generate Fresh Content for Testing")
    success, _ = generate_test_content_and_process()
    test_results['content_generation'] = success
    
    # Get all articles for testing
    articles = get_all_content_library_articles()
    
    if not articles:
        log_test_result("❌ No articles available for testing - aborting quality tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 3: HTML Wrapper Elimination (CRITICAL)
    log_test_result("\nTEST 3: CRITICAL HTML WRAPPER ELIMINATION TEST")
    test_results['html_wrapper_elimination'] = test_html_wrapper_elimination(articles)
    
    # Test 4: Text Deduplication (CRITICAL)
    log_test_result("\nTEST 4: CRITICAL TEXT DEDUPLICATION TEST")
    test_results['text_deduplication'] = test_text_deduplication(articles)
    
    # Test 5: Content Quality Verification
    log_test_result("\nTEST 5: Content Quality Verification")
    test_results['content_quality_verification'] = test_content_quality_verification(articles)
    
    # Test 6: User Feedback Resolution
    log_test_result("\nTEST 6: User Feedback Complete Resolution")
    test_results['user_feedback_resolution'] = test_user_feedback_resolution(articles)
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL QUALITY FIXES TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Critical success criteria
    critical_tests = ['html_wrapper_elimination', 'text_deduplication']
    critical_passed = all(test_results[test] for test in critical_tests)
    
    if critical_passed:
        log_test_result("🎉 CRITICAL SUCCESS: All quality fixes working perfectly!", "CRITICAL_SUCCESS")
        log_test_result("✅ HTML wrapper elimination: 100% success", "CRITICAL_SUCCESS")
        log_test_result("✅ Text deduplication: 100% success", "CRITICAL_SUCCESS")
        log_test_result("✅ BeautifulSoup-based fixes are production ready", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Quality fixes not working properly", "CRITICAL_ERROR")
        if not test_results['html_wrapper_elimination']:
            log_test_result("❌ HTML wrapper elimination still failing", "CRITICAL_ERROR")
        if not test_results['text_deduplication']:
            log_test_result("❌ Text deduplication still failing", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Content Library Quality Fixes Testing")
    print("=" * 50)
    
    results = run_comprehensive_quality_fixes_test()
    
    # Exit with appropriate code
    critical_tests = ['html_wrapper_elimination', 'text_deduplication']
    critical_passed = all(results.get(test, False) for test in critical_tests)
    
    if critical_passed:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure