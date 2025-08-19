#!/usr/bin/env python3
"""
FINAL VALIDATION - HTML WRAPPER CLEANING & TEXT DEDUPLICATION TESTING
Testing the enhanced fixes for the 2 remaining critical issues:
1. Complete HTML wrapper cleaning (no ```html, <!DOCTYPE>, <html>, <head>, <body>)
2. Advanced text deduplication (no "TextText" patterns)
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
BACKEND_URL = "https://prompt-support-app.preview.emergentagent.com"
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
    """Generate test content and process it through the Knowledge Engine"""
    try:
        log_test_result("🎯 GENERATING TEST CONTENT FOR HTML WRAPPER & DEDUPLICATION TESTING", "CRITICAL")
        
        # Create comprehensive test content that would trigger both issues
        test_content = """
        Google Cloud Platform Complete Guide
        
        Getting Started with Google Cloud Platform
        
        A Google Cloud Platform account is essential for cloud computing. A Google Cloud Platform account provides access to all services.
        
        Step 1: Create Account
        First, you need to obtain an API key from Google Cloud Console. First, you need to obtain an API key from Google Cloud Console.
        
        Step 2: Setup Configuration
        The configuration process involves multiple steps. The configuration process involves multiple steps.
        
        Code Example:
        ```javascript
        function initializeGCP() {
            console.log("Initializing GCP");
            return gcp.initialize();
        }
        ```
        
        FAQ Section
        
        Q: How do I get started?
        A: Getting started is simple. Getting started is simple. You need to create an account first.
        
        Q: What are the requirements?
        A: The requirements include a valid email address. The requirements include a valid email address.
        
        Advanced Configuration
        
        For advanced users, the system provides extensive customization options. For advanced users, the system provides extensive customization options.
        
        List of Features:
        1. Cloud Storage - provides unlimited storage capacity
        2. Compute Engine - provides unlimited storage capacity  
        3. App Engine - provides scalable web applications
        4. BigQuery - provides scalable web applications
        
        Troubleshooting Common Issues
        
        Issue 1: Authentication Problems
        Authentication problems can occur when credentials are invalid. Authentication problems can occur when credentials are invalid.
        
        Issue 2: Network Connectivity
        Network issues may prevent proper connection to services. Network issues may prevent proper connection to services.
        """
        
        log_test_result(f"📝 Test content created: {len(test_content)} characters")
        log_test_result("🔍 Content contains intentional duplications and patterns that should trigger fixes")
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing content through Knowledge Engine...")
        
        # Use content processing endpoint
        payload = {
            "content": test_content,
            "content_type": "text",
            "metadata": {
                "filename": "html_deduplication_test.txt",
                "source": "test_validation"
            }
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process", 
                               json=payload, 
                               timeout=300)  # 5 minute timeout
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return None
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return None
        
        log_test_result(f"✅ Processing started, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing progress...")
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return None
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 Processing status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        return job_id
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return None
                    
                    # Continue monitoring
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Content generation and processing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None

def analyze_html_wrapper_issues(articles):
    """Analyze articles for HTML wrapper issues"""
    try:
        log_test_result("🔍 ANALYZING HTML WRAPPER CLEANING", "CRITICAL")
        
        wrapper_issues = []
        total_articles = len(articles)
        
        for i, article in enumerate(articles):
            article_id = article.get('id', f'article_{i}')
            title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"📄 Analyzing Article {i+1}/{total_articles}: {title}...")
            
            # Check for markdown code block wrappers
            if '```html' in content:
                wrapper_issues.append({
                    'article_id': article_id,
                    'title': title,
                    'issue': 'markdown_code_block',
                    'pattern': '```html code block wrapper found'
                })
                log_test_result(f"❌ Found ```html wrapper in: {title}", "ERROR")
            
            # Check for HTML document structure
            html_doc_patterns = [
                ('<!DOCTYPE html>', 'DOCTYPE declaration'),
                ('<html>', 'HTML root element'),
                ('<head>', 'HEAD element'),
                ('<body>', 'BODY element'),
                ('</html>', 'HTML closing tag'),
                ('</head>', 'HEAD closing tag'),
                ('</body>', 'BODY closing tag')
            ]
            
            for pattern, description in html_doc_patterns:
                if pattern.lower() in content.lower():
                    wrapper_issues.append({
                        'article_id': article_id,
                        'title': title,
                        'issue': 'html_document_structure',
                        'pattern': f'{description} found: {pattern}'
                    })
                    log_test_result(f"❌ Found {description} in: {title}", "ERROR")
            
            # Check if article starts with clean semantic HTML
            content_start = content.strip()[:100].lower()
            if content_start.startswith('<!doctype') or content_start.startswith('<html'):
                wrapper_issues.append({
                    'article_id': article_id,
                    'title': title,
                    'issue': 'document_wrapper_start',
                    'pattern': 'Article starts with document structure instead of semantic HTML'
                })
                log_test_result(f"❌ Article starts with document wrapper: {title}", "ERROR")
            elif content_start.startswith('<h2>') or content_start.startswith('<p>') or content_start.startswith('<div>'):
                log_test_result(f"✅ Article starts with clean semantic HTML: {title}", "SUCCESS")
        
        # Summary
        articles_with_wrappers = len(set(issue['article_id'] for issue in wrapper_issues))
        clean_articles = total_articles - articles_with_wrappers
        
        log_test_result(f"📊 HTML WRAPPER ANALYSIS RESULTS:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Clean Articles: {clean_articles}")
        log_test_result(f"   Articles with Wrappers: {articles_with_wrappers}")
        log_test_result(f"   Total Wrapper Issues: {len(wrapper_issues)}")
        
        if articles_with_wrappers == 0:
            log_test_result("🎉 HTML WRAPPER CLEANING: 100% SUCCESS - No wrapper issues found!", "CRITICAL_SUCCESS")
            return True, wrapper_issues
        else:
            log_test_result(f"❌ HTML WRAPPER CLEANING: FAILED - {articles_with_wrappers}/{total_articles} articles have wrapper issues", "CRITICAL_ERROR")
            
            # Show details of issues
            for issue in wrapper_issues[:10]:  # Show first 10 issues
                log_test_result(f"   Issue: {issue['pattern']} in '{issue['title']}'")
            
            return False, wrapper_issues
        
    except Exception as e:
        log_test_result(f"❌ HTML wrapper analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False, []

def analyze_text_deduplication_issues(articles):
    """Analyze articles for text deduplication issues"""
    try:
        log_test_result("🔍 ANALYZING TEXT DEDUPLICATION", "CRITICAL")
        
        deduplication_issues = []
        total_articles = len(articles)
        
        for i, article in enumerate(articles):
            article_id = article.get('id', f'article_{i}')
            title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"📄 Analyzing Article {i+1}/{total_articles}: {title}...")
            
            # Parse HTML content
            try:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check different elements for duplication
                elements_to_check = [
                    ('paragraphs', soup.find_all('p')),
                    ('list_items', soup.find_all('li')),
                    ('headings', soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                    ('divs', soup.find_all('div'))
                ]
                
                for element_type, elements in elements_to_check:
                    for j, element in enumerate(elements):
                        text = element.get_text().strip()
                        if not text:
                            continue
                        
                        # Pattern 1: Immediate word/phrase duplications (TextText)
                        duplication_patterns = [
                            r'\b(\w+(?:\s+\w+)*)\.\1\.',  # "Word phrase.Word phrase."
                            r'\b(\w+(?:\s+\w+)*)\s+\1\b',  # "Word phrase Word phrase"
                            r'\b(\w{3,})\1\b',  # "WordWord" (3+ chars to avoid false positives)
                        ]
                        
                        for pattern in duplication_patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            if matches:
                                for match in matches:
                                    deduplication_issues.append({
                                        'article_id': article_id,
                                        'title': title,
                                        'element_type': element_type,
                                        'element_index': j,
                                        'issue': 'text_duplication',
                                        'pattern': f'Duplicated text: "{match}"',
                                        'full_text': text[:200] + '...' if len(text) > 200 else text
                                    })
                                    log_test_result(f"❌ Found text duplication in {element_type}: '{match}' in {title}", "ERROR")
                        
                        # Pattern 2: Sentence-level duplication
                        sentences = re.split(r'[.!?]+', text)
                        seen_sentences = set()
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if len(sentence) > 10:  # Only check substantial sentences
                                if sentence.lower() in seen_sentences:
                                    deduplication_issues.append({
                                        'article_id': article_id,
                                        'title': title,
                                        'element_type': element_type,
                                        'element_index': j,
                                        'issue': 'sentence_duplication',
                                        'pattern': f'Duplicated sentence: "{sentence[:100]}..."',
                                        'full_text': text[:200] + '...' if len(text) > 200 else text
                                    })
                                    log_test_result(f"❌ Found sentence duplication in {element_type}: '{sentence[:50]}...' in {title}", "ERROR")
                                else:
                                    seen_sentences.add(sentence.lower())
                
            except Exception as parse_error:
                log_test_result(f"⚠️ Could not parse HTML for article {title}: {parse_error}")
                
                # Fallback: Check raw text for obvious duplications
                simple_patterns = [
                    r'\b(\w+(?:\s+\w+){1,5})\.\s*\1\.',  # "Phrase. Phrase."
                    r'\b(\w+(?:\s+\w+){1,5})\s+\1\b',    # "Phrase Phrase"
                ]
                
                for pattern in simple_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            deduplication_issues.append({
                                'article_id': article_id,
                                'title': title,
                                'element_type': 'raw_text',
                                'element_index': 0,
                                'issue': 'text_duplication_fallback',
                                'pattern': f'Duplicated text (fallback): "{match}"',
                                'full_text': 'Raw text analysis'
                            })
                            log_test_result(f"❌ Found text duplication (fallback) in: {title}", "ERROR")
        
        # Summary
        articles_with_duplications = len(set(issue['article_id'] for issue in deduplication_issues))
        clean_articles = total_articles - articles_with_duplications
        
        log_test_result(f"📊 TEXT DEDUPLICATION ANALYSIS RESULTS:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Clean Articles: {clean_articles}")
        log_test_result(f"   Articles with Duplications: {articles_with_duplications}")
        log_test_result(f"   Total Duplication Issues: {len(deduplication_issues)}")
        
        if len(deduplication_issues) == 0:
            log_test_result("🎉 TEXT DEDUPLICATION: 100% SUCCESS - No duplication issues found!", "CRITICAL_SUCCESS")
            return True, deduplication_issues
        else:
            log_test_result(f"❌ TEXT DEDUPLICATION: FAILED - {len(deduplication_issues)} duplication issues found", "CRITICAL_ERROR")
            
            # Show details of issues
            for issue in deduplication_issues[:10]:  # Show first 10 issues
                log_test_result(f"   Issue: {issue['pattern']} in '{issue['title']}'")
            
            return False, deduplication_issues
        
    except Exception as e:
        log_test_result(f"❌ Text deduplication analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False, []

def get_generated_articles():
    """Retrieve generated articles from Content Library"""
    try:
        log_test_result("📚 Retrieving articles from Content Library...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            total = data.get('total', 0)
            
            log_test_result(f"✅ Retrieved {len(articles)} articles (Total: {total})")
            
            # Filter for recent articles (last 10 minutes)
            recent_articles = []
            current_time = datetime.now()
            
            for article in articles:
                created_at = article.get('created_at')
                if created_at:
                    try:
                        # Handle different datetime formats
                        if isinstance(created_at, str):
                            if 'T' in created_at:
                                article_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            else:
                                article_time = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                        else:
                            continue
                        
                        # Check if article was created in last 10 minutes
                        time_diff = (current_time - article_time.replace(tzinfo=None)).total_seconds()
                        if time_diff < 600:  # 10 minutes
                            recent_articles.append(article)
                    except Exception as date_error:
                        log_test_result(f"⚠️ Could not parse date for article: {date_error}")
                        # Include article anyway if we can't parse the date
                        recent_articles.append(article)
            
            if recent_articles:
                log_test_result(f"🔍 Found {len(recent_articles)} recent articles for analysis")
                return recent_articles
            else:
                log_test_result("⚠️ No recent articles found, using all articles for analysis")
                return articles[:10]  # Use first 10 articles as fallback
        else:
            log_test_result(f"❌ Failed to retrieve articles: Status {response.status_code}", "ERROR")
            return []
            
    except Exception as e:
        log_test_result(f"❌ Article retrieval failed: {e}", "ERROR")
        return []

def run_comprehensive_validation_test():
    """Run comprehensive validation test for HTML wrapper cleaning and text deduplication"""
    log_test_result("🚀 STARTING COMPREHENSIVE HTML WRAPPER & DEDUPLICATION VALIDATION", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'content_processing': False,
        'html_wrapper_cleaning': False,
        'text_deduplication': False,
        'overall_success': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Generate and Process Test Content
    log_test_result("\nTEST 2: Content Generation and Processing")
    job_id = generate_test_content_and_process()
    test_results['content_processing'] = job_id is not None
    
    if not test_results['content_processing']:
        log_test_result("❌ Content processing failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 3: Retrieve Generated Articles
    log_test_result("\nTEST 3: Article Retrieval and Analysis")
    articles = get_generated_articles()
    
    if not articles:
        log_test_result("❌ No articles found for analysis - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 4: HTML Wrapper Cleaning Validation
    log_test_result("\nTEST 4: HTML WRAPPER CLEANING VALIDATION")
    wrapper_success, wrapper_issues = analyze_html_wrapper_issues(articles)
    test_results['html_wrapper_cleaning'] = wrapper_success
    
    # Test 5: Text Deduplication Validation
    log_test_result("\nTEST 5: TEXT DEDUPLICATION VALIDATION")
    dedup_success, dedup_issues = analyze_text_deduplication_issues(articles)
    test_results['text_deduplication'] = dedup_success
    
    # Overall Success Calculation
    test_results['overall_success'] = (
        test_results['html_wrapper_cleaning'] and 
        test_results['text_deduplication']
    )
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL VALIDATION RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Critical Success Criteria
    if test_results['overall_success']:
        log_test_result("🎉 CRITICAL SUCCESS: ALL REMAINING ISSUES HAVE BEEN COMPLETELY RESOLVED!", "CRITICAL_SUCCESS")
        log_test_result("✅ HTML wrapper cleaning: 100% success - No wrapper issues found", "CRITICAL_SUCCESS")
        log_test_result("✅ Text deduplication: 100% success - No duplication issues found", "CRITICAL_SUCCESS")
        log_test_result("✅ Enhanced fixes are working perfectly with 100% resolution rate", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Some issues remain unresolved", "CRITICAL_ERROR")
        
        if not test_results['html_wrapper_cleaning']:
            log_test_result("❌ HTML wrapper cleaning still has issues", "CRITICAL_ERROR")
        
        if not test_results['text_deduplication']:
            log_test_result("❌ Text deduplication still has issues", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("HTML Wrapper Cleaning & Text Deduplication Validation Testing")
    print("=" * 60)
    
    results = run_comprehensive_validation_test()
    
    # Exit with appropriate code
    if results['overall_success']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure