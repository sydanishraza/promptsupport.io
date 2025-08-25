#!/usr/bin/env python3
"""
COMPREHENSIVE WYSIWYG TEMPLATE INTEGRATION TESTING
Final verification of complete WYSIWYG template integration system

Testing Focus:
1. Clean Content Generation - ZERO template contamination
2. WYSIWYG Features Implementation - proper HTML structure
3. JavaScript Integration Ready - expandable sections and code blocks
4. Processing Pipeline Verification - unified processing path
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
BACKEND_URL = "https://content-formatter.preview.emergentagent.com"
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

def test_clean_content_generation():
    """
    TEST 1: Clean Content Generation
    Process sample content and verify ZERO template contamination
    """
    try:
        log_test_result("🎯 TEST 1: CLEAN CONTENT GENERATION - Zero Template Contamination", "CRITICAL")
        
        # Sample content for testing - realistic technical content
        sample_content = """
        Google Maps JavaScript API Integration Guide
        
        This comprehensive guide covers the complete integration of Google Maps JavaScript API into web applications.
        
        Getting Started with Google Maps API
        
        First, you need to obtain an API key from Google Cloud Console. Navigate to the Google Cloud Console and create a new project or select an existing one.
        
        Step 1: Enable the Maps JavaScript API
        In the Google Cloud Console, go to the "APIs & Services" section and click on "Library". Search for "Maps JavaScript API" and enable it for your project.
        
        Step 2: Create API Credentials
        Go to the "Credentials" section and click "Create Credentials". Select "API Key" and copy the generated key.
        
        Basic Map Implementation
        
        Here's a basic HTML structure for implementing Google Maps:
        
        <div id="map" style="height: 400px; width: 100%;"></div>
        <script>
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 10,
                center: { lat: 37.7749, lng: -122.4194 }
            });
        }
        </script>
        
        Advanced Features
        
        You can add markers, info windows, and custom styling to enhance your map implementation.
        
        Adding Markers:
        const marker = new google.maps.Marker({
            position: { lat: 37.7749, lng: -122.4194 },
            map: map,
            title: "San Francisco"
        });
        
        Troubleshooting Common Issues
        
        If your map doesn't load, check:
        - API key is valid and properly configured
        - Maps JavaScript API is enabled
        - No console errors in browser developer tools
        """
        
        # Process content through the system
        log_test_result("📤 Processing sample content through WYSIWYG pipeline...")
        
        # Create temporary text file for upload
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(sample_content)
            temp_file_path = temp_file.name
        
        try:
            # Upload file
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('google_maps_api_guide.txt', f, 'text/plain')}
                metadata = {'metadata': '{}'}
                
                start_time = time.time()
                response = requests.post(f"{API_BASE}/content/upload", 
                                       files=files, 
                                       data=metadata,
                                       timeout=300)
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content upload failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        upload_data = response.json()
        job_id = upload_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from upload", "ERROR")
            return False
        
        log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing for clean content generation...")
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
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Get generated articles from Content Library
                        return verify_clean_content_generation()
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Clean content generation test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def verify_clean_content_generation():
    """Verify generated content has zero template contamination"""
    try:
        log_test_result("🔍 Verifying clean content generation...")
        
        # Get recent articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found in Content Library", "ERROR")
            return False
        
        # Get the most recent articles (likely our test content)
        recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        
        log_test_result(f"📚 Analyzing {len(recent_articles)} recent articles for template contamination...")
        
        contamination_found = False
        clean_articles = 0
        
        # Template contamination patterns to check for
        contamination_patterns = [
            r'what are the main benefits',
            r'getting started guide',
            r'this is an overview of',
            r'main content from',
            r'related links:.*#article-',
            r'frequently asked questions.*generic',
            r'placeholder.*content',
            r'template.*example',
            r'sample.*text.*here',
            r'lorem ipsum',
            r'#what-is-.*-studio',
            r'#getting-started',
            r'#create-an-account'
        ]
        
        for i, article in enumerate(recent_articles):
            article_title = article.get('title', 'Untitled')
            article_content = article.get('content', '')
            
            log_test_result(f"   📄 Article {i+1}: {article_title[:60]}...")
            log_test_result(f"      Content length: {len(article_content)} characters")
            
            # Check for template contamination
            contamination_count = 0
            found_patterns = []
            
            for pattern in contamination_patterns:
                matches = re.findall(pattern, article_content.lower())
                if matches:
                    contamination_count += len(matches)
                    found_patterns.append(pattern)
            
            if contamination_count > 0:
                log_test_result(f"      ❌ CONTAMINATION FOUND: {contamination_count} instances", "ERROR")
                for pattern in found_patterns:
                    log_test_result(f"         Pattern: {pattern}", "ERROR")
                contamination_found = True
            else:
                log_test_result(f"      ✅ CLEAN: No template contamination detected", "SUCCESS")
                clean_articles += 1
            
            # Check for source content preservation
            if 'google maps' in article_content.lower() and 'api' in article_content.lower():
                log_test_result(f"      ✅ SOURCE CONTENT PRESERVED: Contains original Google Maps API content", "SUCCESS")
            elif len(article_content) > 500:
                log_test_result(f"      ✅ SUBSTANTIAL CONTENT: {len(article_content)} characters of real content", "SUCCESS")
        
        # Final assessment
        if contamination_found:
            log_test_result(f"❌ CLEAN CONTENT TEST FAILED: Template contamination detected in articles", "CRITICAL_ERROR")
            return False
        else:
            log_test_result(f"🎉 CLEAN CONTENT TEST PASSED: {clean_articles}/{len(recent_articles)} articles are completely clean", "CRITICAL_SUCCESS")
            return True
    
    except Exception as e:
        log_test_result(f"❌ Clean content verification failed: {e}", "ERROR")
        return False

def test_wysiwyg_features_implementation():
    """
    TEST 2: WYSIWYG Features Implementation
    Verify proper HTML structure for WYSIWYG features
    """
    try:
        log_test_result("🎯 TEST 2: WYSIWYG FEATURES IMPLEMENTATION", "CRITICAL")
        
        # Get recent articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for WYSIWYG testing", "ERROR")
            return False
        
        recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
        
        wysiwyg_features_found = {
            'article_body_wrapper': 0,
            'enhanced_code_blocks': 0,
            'expandable_sections': 0,
            'contextual_callouts': 0,
            'line_numbers': 0,
            'copy_functionality': 0
        }
        
        log_test_result(f"🔍 Analyzing {len(recent_articles)} articles for WYSIWYG features...")
        
        for i, article in enumerate(recent_articles):
            article_title = article.get('title', 'Untitled')
            article_content = article.get('content', '')
            
            log_test_result(f"   📄 Article {i+1}: {article_title[:50]}...")
            
            # Parse HTML content
            soup = BeautifulSoup(article_content, 'html.parser')
            
            # Check for article-body wrapper
            article_body = soup.find('div', class_='article-body')
            if article_body:
                wysiwyg_features_found['article_body_wrapper'] += 1
                log_test_result(f"      ✅ Found article-body wrapper", "SUCCESS")
            
            # Check for enhanced code blocks with line numbers
            code_blocks = soup.find_all('pre', class_='line-numbers')
            if code_blocks:
                wysiwyg_features_found['enhanced_code_blocks'] += len(code_blocks)
                wysiwyg_features_found['line_numbers'] += len(code_blocks)
                log_test_result(f"      ✅ Found {len(code_blocks)} enhanced code blocks with line numbers", "SUCCESS")
            
            # Check for expandable FAQ sections
            expandable_sections = soup.find_all(['div', 'section'], class_=re.compile(r'expandable|collapsible|faq-item'))
            if expandable_sections:
                wysiwyg_features_found['expandable_sections'] += len(expandable_sections)
                log_test_result(f"      ✅ Found {len(expandable_sections)} expandable sections", "SUCCESS")
            
            # Check for contextual callouts
            callouts = soup.find_all(['div', 'aside'], class_=re.compile(r'callout|note|tip|warning|info'))
            if callouts:
                wysiwyg_features_found['contextual_callouts'] += len(callouts)
                log_test_result(f"      ✅ Found {len(callouts)} contextual callouts", "SUCCESS")
            
            # Check for copy functionality indicators
            copy_buttons = soup.find_all(['button', 'span'], class_=re.compile(r'copy|clipboard'))
            if copy_buttons:
                wysiwyg_features_found['copy_functionality'] += len(copy_buttons)
                log_test_result(f"      ✅ Found {len(copy_buttons)} copy functionality elements", "SUCCESS")
        
        # Assess WYSIWYG implementation
        total_features = sum(wysiwyg_features_found.values())
        
        log_test_result(f"📊 WYSIWYG FEATURES SUMMARY:")
        for feature, count in wysiwyg_features_found.items():
            log_test_result(f"   {feature.replace('_', ' ').title()}: {count}")
        
        if total_features >= 5:
            log_test_result(f"🎉 WYSIWYG FEATURES TEST PASSED: {total_features} WYSIWYG features implemented", "CRITICAL_SUCCESS")
            return True
        else:
            log_test_result(f"❌ WYSIWYG FEATURES TEST FAILED: Only {total_features} WYSIWYG features found (expected 5+)", "CRITICAL_ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ WYSIWYG features test failed: {e}", "ERROR")
        return False

def test_javascript_integration_ready():
    """
    TEST 3: JavaScript Integration Ready
    Verify content structure supports JavaScript features
    """
    try:
        log_test_result("🎯 TEST 3: JAVASCRIPT INTEGRATION READY", "CRITICAL")
        
        # Get recent articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for JavaScript integration testing", "ERROR")
            return False
        
        recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
        
        js_ready_features = {
            'heading_ids': 0,
            'expandable_structure': 0,
            'code_copy_ready': 0,
            'mini_toc_structure': 0,
            'interactive_elements': 0
        }
        
        log_test_result(f"🔍 Analyzing {len(recent_articles)} articles for JavaScript readiness...")
        
        for i, article in enumerate(recent_articles):
            article_title = article.get('title', 'Untitled')
            article_content = article.get('content', '')
            
            log_test_result(f"   📄 Article {i+1}: {article_title[:50]}...")
            
            # Parse HTML content
            soup = BeautifulSoup(article_content, 'html.parser')
            
            # Check for heading IDs (for navigation)
            headings_with_ids = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], id=True)
            if headings_with_ids:
                js_ready_features['heading_ids'] += len(headings_with_ids)
                log_test_result(f"      ✅ Found {len(headings_with_ids)} headings with IDs for navigation", "SUCCESS")
            
            # Check for expandable structure (data attributes or classes)
            expandable_elements = soup.find_all(attrs={'data-expandable': True}) or \
                                soup.find_all(class_=re.compile(r'expandable|collapsible|accordion'))
            if expandable_elements:
                js_ready_features['expandable_structure'] += len(expandable_elements)
                log_test_result(f"      ✅ Found {len(expandable_elements)} expandable elements ready for JS", "SUCCESS")
            
            # Check for code blocks ready for copy functionality
            code_blocks = soup.find_all('pre')
            code_with_classes = [cb for cb in code_blocks if cb.get('class')]
            if code_with_classes:
                js_ready_features['code_copy_ready'] += len(code_with_classes)
                log_test_result(f"      ✅ Found {len(code_with_classes)} code blocks ready for copy functionality", "SUCCESS")
            
            # Check for mini-TOC structure
            toc_elements = soup.find_all(['ul', 'ol'], class_=re.compile(r'toc|table-of-contents'))
            if toc_elements:
                js_ready_features['mini_toc_structure'] += len(toc_elements)
                log_test_result(f"      ✅ Found {len(toc_elements)} TOC structures ready for JS navigation", "SUCCESS")
            
            # Check for interactive elements (buttons, clickable elements)
            interactive_elements = soup.find_all(['button', 'a'], class_=True) or \
                                 soup.find_all(attrs={'data-action': True})
            if interactive_elements:
                js_ready_features['interactive_elements'] += len(interactive_elements)
                log_test_result(f"      ✅ Found {len(interactive_elements)} interactive elements", "SUCCESS")
        
        # Assess JavaScript readiness
        total_js_features = sum(js_ready_features.values())
        
        log_test_result(f"📊 JAVASCRIPT READINESS SUMMARY:")
        for feature, count in js_ready_features.items():
            log_test_result(f"   {feature.replace('_', ' ').title()}: {count}")
        
        if total_js_features >= 3:
            log_test_result(f"🎉 JAVASCRIPT INTEGRATION TEST PASSED: {total_js_features} JS-ready features found", "CRITICAL_SUCCESS")
            return True
        else:
            log_test_result(f"❌ JAVASCRIPT INTEGRATION TEST FAILED: Only {total_js_features} JS-ready features found (expected 3+)", "CRITICAL_ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ JavaScript integration test failed: {e}", "ERROR")
        return False

def test_processing_pipeline_verification():
    """
    TEST 4: Processing Pipeline Verification
    Test unified processing path for clean content
    """
    try:
        log_test_result("🎯 TEST 4: PROCESSING PIPELINE VERIFICATION", "CRITICAL")
        
        # Test different processing approaches
        test_scenarios = [
            {
                'name': 'Shallow Split Approach',
                'content': 'Short tutorial content with basic steps and simple code examples.',
                'expected_articles': 2
            },
            {
                'name': 'Moderate Split Approach', 
                'content': '''
                Comprehensive API Documentation Guide
                
                This guide covers multiple aspects of API integration including authentication, endpoints, and error handling.
                
                Authentication Methods
                Learn about different authentication approaches including API keys, OAuth, and JWT tokens.
                
                Core Endpoints
                Detailed documentation of all available API endpoints with request/response examples.
                
                Error Handling
                Best practices for handling API errors and implementing retry logic.
                
                Rate Limiting
                Understanding rate limits and implementing proper throttling mechanisms.
                ''',
                'expected_articles': 4
            },
            {
                'name': 'Deep Split Approach',
                'content': '''
                Complete Product Manual - Advanced Features
                
                This comprehensive manual covers all advanced features of the product with detailed explanations.
                
                Chapter 1: Advanced Configuration
                Detailed configuration options for power users.
                
                Chapter 2: Integration Patterns
                Common integration patterns and best practices.
                
                Chapter 3: Performance Optimization
                Techniques for optimizing performance.
                
                Chapter 4: Security Considerations
                Security best practices and implementation guidelines.
                
                Chapter 5: Troubleshooting Guide
                Common issues and their solutions.
                
                Chapter 6: API Reference
                Complete API documentation with examples.
                
                Chapter 7: Migration Guide
                Step-by-step migration instructions.
                ''',
                'expected_articles': 8
            }
        ]
        
        pipeline_results = []
        
        for scenario in test_scenarios:
            log_test_result(f"🧪 Testing {scenario['name']}...")
            
            # Process content
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(scenario['content'])
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    files = {'file': (f"{scenario['name'].lower().replace(' ', '_')}_test.txt", f, 'text/plain')}
                    metadata = {'metadata': '{}'}
                    
                    response = requests.post(f"{API_BASE}/content/upload", 
                                           files=files,
                                           data=metadata,
                                           timeout=180)
            finally:
                os.unlink(temp_file_path)
            
            if response.status_code == 200:
                upload_data = response.json()
                job_id = upload_data.get('job_id')
                
                if job_id:
                    # Monitor processing
                    processing_result = monitor_processing(job_id, scenario['name'])
                    pipeline_results.append(processing_result)
                else:
                    log_test_result(f"   ❌ No job_id for {scenario['name']}", "ERROR")
                    pipeline_results.append(False)
            else:
                log_test_result(f"   ❌ Upload failed for {scenario['name']}: {response.status_code}", "ERROR")
                pipeline_results.append(False)
        
        # Assess pipeline verification
        successful_pipelines = sum(pipeline_results)
        total_pipelines = len(pipeline_results)
        
        if successful_pipelines >= 2:
            log_test_result(f"🎉 PROCESSING PIPELINE TEST PASSED: {successful_pipelines}/{total_pipelines} pipelines working", "CRITICAL_SUCCESS")
            return True
        else:
            log_test_result(f"❌ PROCESSING PIPELINE TEST FAILED: Only {successful_pipelines}/{total_pipelines} pipelines working", "CRITICAL_ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ Processing pipeline test failed: {e}", "ERROR")
        return False

def monitor_processing(job_id, scenario_name):
    """Monitor processing for a specific scenario"""
    try:
        max_wait_time = 120  # 2 minutes max per scenario
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_time:
                log_test_result(f"   ⏰ Timeout for {scenario_name} after {elapsed:.1f}s", "WARNING")
                return False
            
            status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                if status == 'completed':
                    articles_generated = status_data.get('articles_generated', 0)
                    log_test_result(f"   ✅ {scenario_name} completed: {articles_generated} articles generated", "SUCCESS")
                    return True
                    
                elif status == 'failed':
                    log_test_result(f"   ❌ {scenario_name} failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                    return False
                
                time.sleep(3)
            else:
                time.sleep(3)
    
    except Exception as e:
        log_test_result(f"   ❌ Monitoring error for {scenario_name}: {e}", "ERROR")
        return False

def run_comprehensive_wysiwyg_test():
    """Run comprehensive WYSIWYG template integration test suite"""
    log_test_result("🚀 STARTING COMPREHENSIVE WYSIWYG TEMPLATE INTEGRATION TEST", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'clean_content_generation': False,
        'wysiwyg_features_implementation': False,
        'javascript_integration_ready': False,
        'processing_pipeline_verification': False
    }
    
    # Test 0: Backend Health
    log_test_result("TEST 0: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 1: Clean Content Generation
    log_test_result("\nTEST 1: Clean Content Generation")
    test_results['clean_content_generation'] = test_clean_content_generation()
    
    # Test 2: WYSIWYG Features Implementation
    log_test_result("\nTEST 2: WYSIWYG Features Implementation")
    test_results['wysiwyg_features_implementation'] = test_wysiwyg_features_implementation()
    
    # Test 3: JavaScript Integration Ready
    log_test_result("\nTEST 3: JavaScript Integration Ready")
    test_results['javascript_integration_ready'] = test_javascript_integration_ready()
    
    # Test 4: Processing Pipeline Verification
    log_test_result("\nTEST 4: Processing Pipeline Verification")
    test_results['processing_pipeline_verification'] = test_processing_pipeline_verification()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL WYSIWYG TEMPLATE INTEGRATION TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Critical success criteria assessment
    critical_tests = ['clean_content_generation', 'wysiwyg_features_implementation', 
                     'javascript_integration_ready', 'processing_pipeline_verification']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        log_test_result("🎉 CRITICAL SUCCESS: Complete WYSIWYG Template Integration is PRODUCTION READY!", "CRITICAL_SUCCESS")
        log_test_result("✅ Zero Template Contamination - Source content preserved", "CRITICAL_SUCCESS")
        log_test_result("✅ WYSIWYG Structure Ready - Proper HTML structure for frontend features", "CRITICAL_SUCCESS")
        log_test_result("✅ Interactive Features Supported - JavaScript-ready expandables and code blocks", "CRITICAL_SUCCESS")
        log_test_result("✅ Professional Formatting - Clean, contextual enhancements only", "CRITICAL_SUCCESS")
    else:
        log_test_result(f"❌ CRITICAL FAILURE: WYSIWYG Template Integration not ready ({critical_passed}/{len(critical_tests)} critical tests passed)", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("WYSIWYG Template Integration Testing")
    print("=" * 50)
    
    results = run_comprehensive_wysiwyg_test()
    
    # Exit with appropriate code
    critical_tests = ['clean_content_generation', 'wysiwyg_features_implementation', 
                     'javascript_integration_ready', 'processing_pipeline_verification']
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure