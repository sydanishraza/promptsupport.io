#!/usr/bin/env python3
"""
CRITICAL CONTENT REGRESSION FIXES TESTING
Testing the CRITICAL fixes implemented for content preservation and enhancement validation

CRITICAL FIXES APPLIED:
1. Fixed apply_quality_fixes() function - STOP removing ALL content during HTML cleaning
2. Fixed ensure_enhanced_features() function - Only enhance articles with substantial content
3. Enhanced Content Validation - Check content length before applying templates

CRITICAL VERIFICATION REQUIRED:
- Test 1: Content Preservation - verify source content is preserved (not replaced with templates)
- Test 2: Re-test Existing Articles - check if articles still have template content vs real content  
- Test 3: WYSIWYG Enhancement Verification - verify features are added TO real content, not replacing it

Focus: Verify that real source content is now preserved and enhanced properly
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

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

def test_content_library_analysis():
    """CRITICAL TEST 1: Analyze current Content Library for content regression"""
    try:
        log_test_result("🔍 CRITICAL TEST 1: Content Library Analysis", "CRITICAL")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        total_articles = data.get('total', 0)
        articles = data.get('articles', [])
        
        log_test_result(f"📚 Content Library Status: {total_articles} total articles")
        
        # CRITICAL: Look for the specific Google Maps API Tutorial article
        google_maps_article = None
        faq_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            if 'google map' in title and 'javascript api tutorial' in title:
                google_maps_article = article
                log_test_result(f"🎯 FOUND TARGET ARTICLE: {article.get('title')}")
            elif 'faq' in title or 'frequently asked questions' in title:
                faq_articles.append(article)
        
        # CRITICAL VERIFICATION 1: Google Maps API Tutorial Content
        if google_maps_article:
            content = google_maps_article.get('content', '')
            content_length = len(content)
            
            log_test_result(f"📄 Google Maps API Tutorial Analysis:")
            log_test_result(f"   Title: {google_maps_article.get('title')}")
            log_test_result(f"   Content Length: {content_length} characters")
            log_test_result(f"   Status: {google_maps_article.get('status')}")
            log_test_result(f"   Created: {google_maps_article.get('created_at')}")
            
            # Check if content is just template placeholders
            if content_length < 500:
                log_test_result("❌ CRITICAL REGRESSION CONFIRMED: Google Maps article has minimal content", "CRITICAL_ERROR")
                log_test_result(f"   Content preview: {content[:200]}...", "ERROR")
                return False
            elif 'template' in content.lower() or 'placeholder' in content.lower():
                log_test_result("❌ CRITICAL REGRESSION: Article contains template placeholders instead of real content", "CRITICAL_ERROR")
                return False
            else:
                log_test_result("✅ Google Maps article has substantial content", "SUCCESS")
        else:
            log_test_result("❌ CRITICAL: Google Maps JavaScript API Tutorial article NOT FOUND", "CRITICAL_ERROR")
            return False
        
        # CRITICAL VERIFICATION 2: FAQ Structure Analysis
        log_test_result(f"❓ FAQ Articles Analysis: Found {len(faq_articles)} FAQ articles")
        
        wysiwyg_compliant_faqs = 0
        for faq in faq_articles:
            content = faq.get('content', '')
            title = faq.get('title', '')
            
            # Check for new WYSIWYG expandable format
            has_expandable_divs = '<div class="expandable">' in content
            has_modern_structure = any(pattern in content for pattern in [
                'class="faq-section"', 
                'class="faq-item"',
                '<details>',
                '<summary>'
            ])
            
            log_test_result(f"   FAQ: {title[:50]}...")
            log_test_result(f"      Content Length: {len(content)} chars")
            log_test_result(f"      Has Expandable Divs: {has_expandable_divs}")
            log_test_result(f"      Has Modern Structure: {has_modern_structure}")
            
            if has_expandable_divs or has_modern_structure:
                wysiwyg_compliant_faqs += 1
        
        if wysiwyg_compliant_faqs == 0 and len(faq_articles) > 0:
            log_test_result("❌ CRITICAL REGRESSION: FAQ articles still use old structure", "CRITICAL_ERROR")
            return False
        elif wysiwyg_compliant_faqs > 0:
            log_test_result(f"✅ Found {wysiwyg_compliant_faqs} WYSIWYG-compliant FAQ articles", "SUCCESS")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Content Library analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_content_generation_pipeline():
    """CRITICAL TEST 2: Test content generation pipeline with sample document"""
    try:
        log_test_result("🧪 CRITICAL TEST 2: Content Generation Pipeline Debug", "CRITICAL")
        
        # Create a test document with substantial content
        test_content = """
        # Google Maps JavaScript API Complete Tutorial
        
        ## Introduction
        Google Maps JavaScript API is a powerful tool for integrating interactive maps into web applications. This comprehensive guide will walk you through every aspect of implementation, from basic setup to advanced customization.
        
        ## Getting Started
        
        ### Step 1: Obtain API Key
        First, you need to obtain an API key from Google Cloud Console:
        1. Go to Google Cloud Console
        2. Create a new project or select existing
        3. Enable Maps JavaScript API
        4. Create credentials (API key)
        5. Restrict the API key for security
        
        ### Step 2: Basic HTML Setup
        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Maps Tutorial</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap" async defer></script>
        </head>
        <body>
            <div id="map" style="height: 400px; width: 100%;"></div>
            <script>
                function initMap() {
                    var map = new google.maps.Map(document.getElementById('map'), {
                        zoom: 10,
                        center: {lat: -34.397, lng: 150.644}
                    });
                }
            </script>
        </body>
        </html>
        ```
        
        ## Advanced Features
        
        ### Adding Markers
        ```javascript
        var marker = new google.maps.Marker({
            position: {lat: -34.397, lng: 150.644},
            map: map,
            title: 'Hello World!'
        });
        ```
        
        ### Custom Styling
        You can customize map appearance using styles:
        ```javascript
        var styledMapType = new google.maps.StyledMapType([
            {
                "featureType": "water",
                "elementType": "geometry",
                "stylers": [{"color": "#e9e9e9"}, {"lightness": 17}]
            }
        ], {name: 'Styled Map'});
        ```
        
        ## Frequently Asked Questions
        
        ### Q: How do I handle API key security?
        A: Always restrict your API keys and use environment variables in production.
        
        ### Q: Can I use custom markers?
        A: Yes, you can use custom images for markers by setting the icon property.
        
        ### Q: How do I handle map loading errors?
        A: Implement error handling in your callback functions and provide fallback content.
        """
        
        log_test_result(f"📝 Created test content: {len(test_content)} characters")
        
        # Test the content processing pipeline by uploading text content
        log_test_result("📤 Testing content processing via text upload...")
        
        payload = {
            'content': test_content,
            'filename': 'google_maps_api_tutorial_test.txt'
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process-text", 
                               json=payload, 
                               timeout=300)  # 5 minute timeout
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return False
        
        log_test_result(f"✅ Processing started, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring content generation...")
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 Processing status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Extract metrics
                        articles_generated = status_data.get('articles_generated', 0)
                        chunks_created = status_data.get('chunks_created', 0)
                        
                        log_test_result(f"📈 Generation Results:")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        
                        # CRITICAL: Verify articles were actually created with content
                        if articles_generated == 0:
                            log_test_result("❌ CRITICAL REGRESSION: No articles generated from substantial content", "CRITICAL_ERROR")
                            return False
                        else:
                            log_test_result(f"✅ Articles generated successfully", "SUCCESS")
                            return True
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test_result(f"❌ Processing failed: {error_msg}", "ERROR")
                        return False
                    
                    # Continue monitoring
                    time.sleep(10)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Content generation pipeline test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_wysiwyg_features_verification():
    """CRITICAL TEST 3: Verify WYSIWYG features are working correctly"""
    try:
        log_test_result("🎨 CRITICAL TEST 3: WYSIWYG Features Verification", "CRITICAL")
        
        # Get recent articles to check for WYSIWYG features
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for WYSIWYG verification", "ERROR")
            return False
        
        # Check recent articles for WYSIWYG features
        wysiwyg_features_found = {
            'expandable_sections': 0,
            'enhanced_lists': 0,
            'code_blocks': 0,
            'callouts': 0,
            'mini_toc': 0
        }
        
        articles_analyzed = 0
        
        for article in articles[:10]:  # Check first 10 articles
            content = article.get('content', '')
            title = article.get('title', '')
            
            articles_analyzed += 1
            
            # Check for WYSIWYG features
            if '<div class="expandable">' in content or '<details>' in content:
                wysiwyg_features_found['expandable_sections'] += 1
            
            if 'class="doc-list"' in content or 'class="enhanced-list"' in content:
                wysiwyg_features_found['enhanced_lists'] += 1
            
            if '<pre><code' in content and 'class="language-' in content:
                wysiwyg_features_found['code_blocks'] += 1
            
            if 'class="callout"' in content or 'class="note"' in content:
                wysiwyg_features_found['callouts'] += 1
            
            if 'class="toc-list"' in content or 'Table of Contents' in content:
                wysiwyg_features_found['mini_toc'] += 1
        
        log_test_result(f"🎨 WYSIWYG Features Analysis ({articles_analyzed} articles):")
        for feature, count in wysiwyg_features_found.items():
            percentage = (count / articles_analyzed) * 100 if articles_analyzed > 0 else 0
            log_test_result(f"   {feature.replace('_', ' ').title()}: {count} articles ({percentage:.1f}%)")
        
        # Verify that WYSIWYG features are present
        total_features = sum(wysiwyg_features_found.values())
        if total_features == 0:
            log_test_result("❌ CRITICAL REGRESSION: No WYSIWYG features found in any articles", "CRITICAL_ERROR")
            return False
        else:
            log_test_result(f"✅ WYSIWYG features detected: {total_features} total feature instances", "SUCCESS")
            return True
        
    except Exception as e:
        log_test_result(f"❌ WYSIWYG features verification failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_root_cause_analysis():
    """CRITICAL TEST 4: Root cause analysis of content loss"""
    try:
        log_test_result("🔍 CRITICAL TEST 4: Root Cause Analysis", "CRITICAL")
        
        # Check backend logs for content processing issues
        log_test_result("📋 Analyzing backend logs for content processing patterns...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for content processing indicators
                content_indicators = {
                    'outline_generation': 'COMPREHENSIVE OUTLINE GENERATED' in logs,
                    'article_creation': 'CREATING ARTICLES FROM OUTLINE' in logs,
                    'content_extraction': 'content extraction' in logs.lower(),
                    'llm_calls': 'LLM' in logs and 'response' in logs.lower(),
                    'content_cleaning': 'clean_article_html_content' in logs,
                    'database_storage': 'Article created and saved' in logs,
                    'empty_content_warnings': 'empty' in logs.lower() and 'content' in logs.lower(),
                    'template_processing': 'template' in logs.lower(),
                    'wysiwyg_processing': 'wysiwyg' in logs.lower() or 'expandable' in logs.lower()
                }
                
                log_test_result("🔍 Backend Log Analysis:")
                for indicator, found in content_indicators.items():
                    status = "✅ FOUND" if found else "❌ MISSING"
                    log_test_result(f"   {indicator.replace('_', ' ').title()}: {status}")
                
                # Look for specific error patterns
                error_patterns = [
                    'empty articles',
                    'content lost',
                    'template placeholder',
                    'LLM response empty',
                    'content cleaning removed',
                    'HTML wrapper'
                ]
                
                errors_found = []
                for pattern in error_patterns:
                    if pattern.lower() in logs.lower():
                        errors_found.append(pattern)
                
                if errors_found:
                    log_test_result(f"⚠️ Potential Issues Found: {', '.join(errors_found)}", "WARNING")
                else:
                    log_test_result("✅ No obvious error patterns detected in logs", "SUCCESS")
                
                return len(errors_found) == 0
                
            else:
                log_test_result("⚠️ Could not access backend logs for analysis")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log analysis failed: {log_error}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Root cause analysis failed: {e}", "ERROR")
        return False

def run_critical_content_regression_investigation():
    """Run comprehensive investigation of content regression issues"""
    log_test_result("🚨 STARTING CRITICAL CONTENT REGRESSION INVESTIGATION", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'content_library_analysis': False,
        'content_generation_pipeline': False,
        'wysiwyg_features_verification': False,
        'root_cause_analysis': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting investigation", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Content Library Analysis (CRITICAL)
    log_test_result("\nTEST 2: CRITICAL Content Library Analysis")
    test_results['content_library_analysis'] = test_content_library_analysis()
    
    # Test 3: Content Generation Pipeline Debug
    log_test_result("\nTEST 3: Content Generation Pipeline Debug")
    test_results['content_generation_pipeline'] = test_content_generation_pipeline()
    
    # Test 4: WYSIWYG Features Verification
    log_test_result("\nTEST 4: WYSIWYG Features Verification")
    test_results['wysiwyg_features_verification'] = test_wysiwyg_features_verification()
    
    # Test 5: Root Cause Analysis
    log_test_result("\nTEST 5: Root Cause Analysis")
    test_results['root_cause_analysis'] = test_root_cause_analysis()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 CRITICAL INVESTIGATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Critical assessment
    critical_tests = ['content_library_analysis', 'content_generation_pipeline']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        log_test_result("✅ CRITICAL TESTS PASSED: No major content regression detected", "SUCCESS")
    else:
        log_test_result("❌ CRITICAL REGRESSION CONFIRMED: Content generation pipeline has issues", "CRITICAL_ERROR")
        log_test_result("🔧 URGENT ACTION REQUIRED: Investigate content extraction and LLM processing", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Critical Content Regression Investigation")
    print("=" * 50)
    
    results = run_critical_content_regression_investigation()
    
    # Exit with appropriate code
    critical_tests_passed = results.get('content_library_analysis', False) and results.get('content_generation_pipeline', False)
    if critical_tests_passed:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Critical failure detected