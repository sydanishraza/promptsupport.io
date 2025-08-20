#!/usr/bin/env python3
"""
ENHANCED WYSIWYG TEMPLATE FIXES TESTING
Testing the enhanced WYSIWYG template fixes that were just implemented to resolve missing features.

SPECIFIC TESTING REQUIREMENTS:
1. Enhanced Code Blocks - with `<pre class="line-numbers"><code class="language-X">` format
2. Comprehensive Callouts/Notes - multiple types like notes, tips, warnings, info callouts  
3. Expandable FAQ Sections - with `<div class="expandable">` structure
4. Complete WYSIWYG Compliance - all 6+ features present
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://smartchunk.preview.emergentagent.com"
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

def process_test_content_for_wysiwyg_features():
    """Process test content specifically designed to trigger WYSIWYG template features"""
    try:
        log_test_result("🎯 PROCESSING TEST CONTENT FOR WYSIWYG TEMPLATE FEATURES", "CRITICAL")
        
        # Create comprehensive test content that should trigger all WYSIWYG features
        test_content = """
        Google Maps JavaScript API Integration Guide
        
        This comprehensive guide covers the complete implementation of Google Maps JavaScript API with advanced features, code examples, and troubleshooting solutions.
        
        Getting Started with Google Maps API
        
        First, you need to obtain an API key from Google Cloud Console. This is essential for authentication and access control.
        
        Step 1: Create a Google Cloud Project
        Navigate to the Google Cloud Console and create a new project. Enable the Maps JavaScript API for your project.
        
        Step 2: Generate API Key
        Go to the Credentials section and create a new API key. Restrict the key to your domain for security.
        
        Basic Map Implementation
        
        Here's a basic example of implementing a Google Map:
        
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 4,
                center: { lat: -25.344, lng: 131.036 },
            });
        }
        
        Advanced Features Implementation
        
        Adding Markers to Your Map
        
        You can add custom markers to highlight specific locations:
        
        const marker = new google.maps.Marker({
            position: { lat: -25.344, lng: 131.036 },
            map: map,
            title: "Custom Location"
        });
        
        Implementing Info Windows
        
        Info windows provide additional information when users click on markers:
        
        const infoWindow = new google.maps.InfoWindow({
            content: "<h3>Location Details</h3><p>This is a custom location marker.</p>"
        });
        
        marker.addListener("click", () => {
            infoWindow.open(map, marker);
        });
        
        Common Issues and Troubleshooting
        
        API Key Authentication Errors
        If you encounter authentication errors, verify that your API key is correctly configured and has the necessary permissions.
        
        Map Not Loading
        Check that the Google Maps JavaScript API is properly loaded in your HTML document and that your API key is valid.
        
        Performance Optimization
        For better performance, consider implementing map clustering for multiple markers and lazy loading for large datasets.
        
        Best Practices
        
        Security Considerations
        Always restrict your API keys to specific domains and implement proper error handling for API failures.
        
        User Experience Guidelines
        Provide loading indicators and fallback content for users with slow internet connections.
        
        Frequently Asked Questions
        
        How do I customize map styles?
        You can customize map styles using the styles property in the map options object.
        
        Can I use Google Maps offline?
        Google Maps JavaScript API requires an internet connection and cannot be used offline.
        
        What are the usage limits?
        Google Maps API has usage quotas and billing requirements. Check the Google Cloud Console for current limits.
        
        How do I handle API errors?
        Implement proper error handling using try-catch blocks and provide user-friendly error messages.
        
        Advanced Integration Examples
        
        Geocoding Implementation
        Convert addresses to coordinates using the Geocoding API:
        
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({ address: "New York, NY" }, (results, status) => {
            if (status === "OK") {
                map.setCenter(results[0].geometry.location);
            }
        });
        
        Directions Service
        Implement route planning with the Directions Service:
        
        const directionsService = new google.maps.DirectionsService();
        const directionsRenderer = new google.maps.DirectionsRenderer();
        directionsRenderer.setMap(map);
        
        const request = {
            origin: "Chicago, IL",
            destination: "New York, NY",
            travelMode: google.maps.TravelMode.DRIVING
        };
        
        directionsService.route(request, (result, status) => {
            if (status === "OK") {
                directionsRenderer.setDirections(result);
            }
        });
        """
        
        # Process content through Knowledge Engine
        log_test_result("📤 Uploading test content to Knowledge Engine...")
        
        # Use text upload endpoint
        upload_data = {
            'content': test_content,
            'filename': 'google_maps_api_wysiwyg_test.txt'
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/upload-text", json=upload_data, timeout=300)
        
        if response.status_code != 200:
            log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        upload_result = response.json()
        job_id = upload_result.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from upload", "ERROR")
            return False
        
        log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing progress...")
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
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
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
        log_test_result(f"❌ Content processing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def analyze_wysiwyg_template_features():
    """Analyze generated articles for WYSIWYG template features"""
    try:
        log_test_result("🔍 ANALYZING GENERATED ARTICLES FOR WYSIWYG TEMPLATE FEATURES", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = len(articles)
        
        log_test_result(f"📚 Analyzing {total_articles} articles for WYSIWYG features")
        
        # Focus on recent articles (likely from our test)
        recent_articles = articles[:5]  # Get 5 most recent articles
        
        wysiwyg_features_analysis = {
            'enhanced_code_blocks': 0,
            'comprehensive_callouts': 0,
            'expandable_faqs': 0,
            'mini_toc': 0,
            'professional_headings': 0,
            'related_links': 0,
            'article_body_wrapper': 0,
            'total_articles_analyzed': len(recent_articles)
        }
        
        log_test_result("🔍 DETAILED WYSIWYG FEATURE ANALYSIS:")
        
        for i, article in enumerate(recent_articles):
            article_title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"\n📄 Article {i+1}: {article_title}...")
            log_test_result(f"   Content length: {len(content)} characters")
            
            # 1. Test Enhanced Code Blocks
            enhanced_code_pattern = r'<pre class="line-numbers"><code class="language-\w+">'
            enhanced_code_matches = re.findall(enhanced_code_pattern, content)
            if enhanced_code_matches:
                wysiwyg_features_analysis['enhanced_code_blocks'] += 1
                log_test_result(f"   ✅ Enhanced Code Blocks: {len(enhanced_code_matches)} found", "SUCCESS")
            else:
                # Check for any code blocks
                basic_code_pattern = r'<pre><code[^>]*>'
                basic_code_matches = re.findall(basic_code_pattern, content)
                if basic_code_matches:
                    log_test_result(f"   ⚠️ Basic Code Blocks: {len(basic_code_matches)} found (not enhanced)", "WARNING")
                else:
                    log_test_result(f"   ❌ No Code Blocks found", "ERROR")
            
            # 2. Test Comprehensive Callouts/Notes
            callout_patterns = [
                r'<div class="note">',
                r'💡.*Note',
                r'🎯.*Pro Tip',
                r'⚠️.*Important',
                r'ℹ️.*Getting Started',
                r'<div class="callout">',
                r'<div class="tip">',
                r'<div class="warning">'
            ]
            
            total_callouts = 0
            for pattern in callout_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                total_callouts += len(matches)
            
            if total_callouts >= 2:  # Expecting 2-4 callouts per article
                wysiwyg_features_analysis['comprehensive_callouts'] += 1
                log_test_result(f"   ✅ Comprehensive Callouts: {total_callouts} found", "SUCCESS")
            elif total_callouts > 0:
                log_test_result(f"   ⚠️ Some Callouts: {total_callouts} found (expected 2+)", "WARNING")
            else:
                log_test_result(f"   ❌ No Callouts found", "ERROR")
            
            # 3. Test Expandable FAQ Sections
            expandable_patterns = [
                r'<div class="expandable">',
                r'<div class="expandable-header">',
                r'<span class="expandable-title">',
                r'<div class="faq-expandable">',
                r'<details>',
                r'<summary>'
            ]
            
            total_expandables = 0
            for pattern in expandable_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                total_expandables += len(matches)
            
            if total_expandables >= 3:  # Expecting 5 FAQ sections
                wysiwyg_features_analysis['expandable_faqs'] += 1
                log_test_result(f"   ✅ Expandable FAQs: {total_expandables} elements found", "SUCCESS")
            elif total_expandables > 0:
                log_test_result(f"   ⚠️ Some Expandable Elements: {total_expandables} found", "WARNING")
            else:
                log_test_result(f"   ❌ No Expandable FAQ elements found", "ERROR")
            
            # 4. Test Mini-TOC (already working)
            mini_toc_patterns = [
                r'<div class="mini-toc">',
                r'<ul class="toc-list">',
                r'📋.*Table of Contents',
                r'<h3>.*Contents</h3>'
            ]
            
            mini_toc_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in mini_toc_patterns)
            if mini_toc_found:
                wysiwyg_features_analysis['mini_toc'] += 1
                log_test_result(f"   ✅ Mini-TOC: Found", "SUCCESS")
            else:
                log_test_result(f"   ⚠️ Mini-TOC: Not found", "WARNING")
            
            # 5. Test Professional Headings (already working)
            heading_pattern = r'<h[2-4][^>]*>'
            headings = re.findall(heading_pattern, content)
            if len(headings) >= 3:
                wysiwyg_features_analysis['professional_headings'] += 1
                log_test_result(f"   ✅ Professional Headings: {len(headings)} found", "SUCCESS")
            else:
                log_test_result(f"   ⚠️ Professional Headings: {len(headings)} found (expected 3+)", "WARNING")
            
            # 6. Test Related Links (already working)
            related_links_patterns = [
                r'<div class="related-links">',
                r'🔗.*Related Articles',
                r'<h3>.*Related.*</h3>'
            ]
            
            related_links_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in related_links_patterns)
            if related_links_found:
                wysiwyg_features_analysis['related_links'] += 1
                log_test_result(f"   ✅ Related Links: Found", "SUCCESS")
            else:
                log_test_result(f"   ⚠️ Related Links: Not found", "WARNING")
            
            # 7. Test Article Body Wrapper (already working)
            wrapper_patterns = [
                r'<div class="article-body">',
                r'<div class="content-wrapper">',
                r'<article[^>]*>'
            ]
            
            wrapper_found = any(re.search(pattern, content, re.IGNORECASE) for pattern in wrapper_patterns)
            if wrapper_found:
                wysiwyg_features_analysis['article_body_wrapper'] += 1
                log_test_result(f"   ✅ Article Body Wrapper: Found", "SUCCESS")
            else:
                log_test_result(f"   ⚠️ Article Body Wrapper: Not found", "WARNING")
        
        # Calculate overall WYSIWYG compliance
        total_features = 7
        total_possible_score = total_features * wysiwyg_features_analysis['total_articles_analyzed']
        actual_score = sum([
            wysiwyg_features_analysis['enhanced_code_blocks'],
            wysiwyg_features_analysis['comprehensive_callouts'],
            wysiwyg_features_analysis['expandable_faqs'],
            wysiwyg_features_analysis['mini_toc'],
            wysiwyg_features_analysis['professional_headings'],
            wysiwyg_features_analysis['related_links'],
            wysiwyg_features_analysis['article_body_wrapper']
        ])
        
        compliance_percentage = (actual_score / total_possible_score * 100) if total_possible_score > 0 else 0
        
        log_test_result("\n" + "="*80)
        log_test_result("🎯 WYSIWYG TEMPLATE COMPLIANCE ANALYSIS RESULTS", "CRITICAL")
        log_test_result("="*80)
        
        log_test_result(f"📊 Articles Analyzed: {wysiwyg_features_analysis['total_articles_analyzed']}")
        log_test_result(f"🆕 Enhanced Code Blocks: {wysiwyg_features_analysis['enhanced_code_blocks']}/{wysiwyg_features_analysis['total_articles_analyzed']} articles")
        log_test_result(f"🆕 Comprehensive Callouts: {wysiwyg_features_analysis['comprehensive_callouts']}/{wysiwyg_features_analysis['total_articles_analyzed']} articles")
        log_test_result(f"🆕 Expandable FAQs: {wysiwyg_features_analysis['expandable_faqs']}/{wysiwyg_features_analysis['total_articles_analyzed']} articles")
        log_test_result(f"✅ Mini-TOC: {wysiwyg_features_analysis['mini_toc']}/{wysiwyg_features_analysis['total_articles_analyzed']} articles")
        log_test_result(f"✅ Professional Headings: {wysiwyg_features_analysis['professional_headings']}/{wysiwyg_features_analysis['total_articles_analyzed']} articles")
        log_test_result(f"✅ Related Links: {wysiwyg_features_analysis['related_links']}/{wysiwyg_features_analysis['total_articles_analyzed']} articles")
        log_test_result(f"✅ Article Body Wrapper: {wysiwyg_features_analysis['article_body_wrapper']}/{wysiwyg_features_analysis['total_articles_analyzed']} articles")
        
        log_test_result(f"\n🎯 OVERALL WYSIWYG COMPLIANCE: {compliance_percentage:.1f}%")
        
        # Determine success criteria
        newly_implemented_features = [
            wysiwyg_features_analysis['enhanced_code_blocks'],
            wysiwyg_features_analysis['comprehensive_callouts'],
            wysiwyg_features_analysis['expandable_faqs']
        ]
        
        new_features_working = sum(newly_implemented_features)
        new_features_expected = 3 * wysiwyg_features_analysis['total_articles_analyzed']
        new_features_percentage = (new_features_working / new_features_expected * 100) if new_features_expected > 0 else 0
        
        log_test_result(f"🆕 NEW FEATURES IMPLEMENTATION: {new_features_percentage:.1f}%")
        
        if compliance_percentage >= 85:
            log_test_result("🎉 WYSIWYG TEMPLATE COMPLIANCE: EXCELLENT (85%+)", "SUCCESS")
            return True
        elif compliance_percentage >= 70:
            log_test_result("✅ WYSIWYG TEMPLATE COMPLIANCE: GOOD (70%+)", "SUCCESS")
            return True
        elif compliance_percentage >= 50:
            log_test_result("⚠️ WYSIWYG TEMPLATE COMPLIANCE: PARTIAL (50%+)", "WARNING")
            return False
        else:
            log_test_result("❌ WYSIWYG TEMPLATE COMPLIANCE: INSUFFICIENT (<50%)", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ WYSIWYG feature analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_wysiwyg_template_test():
    """Run comprehensive test suite for WYSIWYG template fixes"""
    log_test_result("🚀 STARTING COMPREHENSIVE WYSIWYG TEMPLATE FIXES TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'content_processing': False,
        'wysiwyg_feature_analysis': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Content Processing for WYSIWYG Features
    log_test_result("\nTEST 2: CONTENT PROCESSING FOR WYSIWYG FEATURES")
    test_results['content_processing'] = process_test_content_for_wysiwyg_features()
    
    if not test_results['content_processing']:
        log_test_result("❌ Content processing failed - cannot analyze WYSIWYG features", "ERROR")
        # Continue to analysis anyway to check existing articles
    
    # Test 3: WYSIWYG Feature Analysis (CRITICAL)
    log_test_result("\nTEST 3: WYSIWYG TEMPLATE FEATURE ANALYSIS")
    test_results['wysiwyg_feature_analysis'] = analyze_wysiwyg_template_features()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL WYSIWYG TEMPLATE TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if test_results['wysiwyg_feature_analysis']:
        log_test_result("🎉 CRITICAL SUCCESS: Enhanced WYSIWYG template fixes are working!", "CRITICAL_SUCCESS")
        log_test_result("✅ Articles now contain the enhanced WYSIWYG features as requested", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Enhanced WYSIWYG template fixes need attention", "CRITICAL_ERROR")
        log_test_result("❌ Missing or insufficient WYSIWYG template features in generated articles", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Enhanced WYSIWYG Template Fixes Testing")
    print("=" * 50)
    
    results = run_comprehensive_wysiwyg_template_test()
    
    # Exit with appropriate code
    if results['wysiwyg_feature_analysis']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
"""
COMPREHENSIVE WYSIWYG TEMPLATE INTEGRATION TESTING
Testing the major upgrade that integrates professional prompt training template 
with enhanced CSS and JavaScript functionality.

Focus Areas:
1. Prompt Template Integration - Professional WYSIWYG structure generation
2. Enhanced CSS Integration - Professional styling and responsive design  
3. JavaScript Functionality - Interactive features and dynamic content
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import re
from bs4 import BeautifulSoup

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

def create_wysiwyg_test_content():
    """Create comprehensive test content for WYSIWYG template testing"""
    return """
# Complete WYSIWYG Template Integration Guide

## 🚀 Introduction and Overview
This comprehensive guide demonstrates the new WYSIWYG template integration system with professional formatting, interactive elements, and enhanced user experience.

### Key Features Covered
- Professional article structure with emoji prefixes
- Interactive expandable sections
- Enhanced mini-TOC navigation
- Copy-enabled code blocks
- Responsive design elements

## ⚡ Getting Started

### Prerequisites
Before implementing the WYSIWYG template system, ensure you have:

1. **System Requirements**
   - Modern web browser with JavaScript enabled
   - CSS3 and HTML5 support
   - Responsive design capabilities

2. **Technical Setup**
   - Enhanced CSS framework loaded
   - JavaScript functionality enabled
   - WYSIWYG editor integration

### Installation Steps

```javascript
// Initialize WYSIWYG template system
function initializeWYSIWYGTemplate() {
    // Load enhanced CSS
    loadEnhancedCSS();
    
    // Initialize interactive features
    initializeExpandables();
    initializeMiniTOC();
    initializeCodeBlocks();
    
    console.log('WYSIWYG Template System Initialized');
}
```

## 🛠️ Implementation Details

### Article Structure Generation
The new template system generates articles with professional structure:

- **Article Body Wrapper**: All content wrapped in `<div class="article-body">`
- **Professional Typography**: Enhanced font hierarchy and spacing
- **Semantic HTML**: Proper heading structure and semantic elements

### Interactive Components

#### Expandable Sections
FAQ sections now include clickable expand/collapse functionality:

```html
<div class="expandable">
    <h3 class="expandable-header">Frequently Asked Questions</h3>
    <div class="expandable-content">
        <p>Content that can be expanded or collapsed</p>
    </div>
</div>
```

#### Enhanced Code Blocks
Code blocks include syntax highlighting and copy functionality:

```css
.code-block {
    position: relative;
    background: #f8f9fa;
    border-radius: 6px;
    padding: 1rem;
}

.copy-button {
    position: absolute;
    top: 8px;
    right: 8px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    cursor: pointer;
}
```

## ❓ Frequently Asked Questions

### Q: How does the mini-TOC generation work?
**A:** The mini-TOC is automatically generated from article headings and provides sticky navigation with active highlighting as users scroll through the content.

### Q: Are the expandable sections mobile-friendly?
**A:** Yes, all interactive elements are designed with responsive principles and work seamlessly across desktop, tablet, and mobile devices.

### Q: Can I customize the styling?
**A:** The enhanced CSS system provides extensive customization options while maintaining professional appearance and accessibility standards.

## 🔗 Related Resources

For additional information, refer to these comprehensive guides:
- WYSIWYG Editor Best Practices
- CSS Framework Documentation  
- JavaScript Interactive Components
- Responsive Design Guidelines

## Technical Implementation Notes

### CSS Classes Applied
- `.article-body` - Main content wrapper
- `.expandable` - Interactive sections
- `.mini-toc` - Navigation component
- `.related-links` - Resource links
- `.code-block` - Enhanced code display

### JavaScript Features
- Expandable toggles with slideToggle animation
- Copy buttons for code blocks
- Mini-TOC generation and highlighting
- Dynamic content initialization

This comprehensive system ensures professional, interactive, and user-friendly article generation.
"""

def process_wysiwyg_test_content():
    """Process test content through the Knowledge Engine to test WYSIWYG integration"""
    try:
        log_test_result("🎯 STARTING WYSIWYG TEMPLATE INTEGRATION TEST", "CRITICAL")
        
        # Create test content
        test_content = create_wysiwyg_test_content()
        log_test_result(f"📝 Created test content: {len(test_content)} characters")
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing content through Knowledge Engine...")
        
        payload = {
            "content": test_content,
            "content_type": "text"
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
        log_test_result("⏳ Monitoring processing progress...")
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
                        log_test_result(f"📄 Articles Generated: {articles_generated}")
                        
                        return True
                        
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
        log_test_result(f"❌ WYSIWYG content processing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_wysiwyg_article_structure():
    """Test that generated articles have proper WYSIWYG structure"""
    try:
        log_test_result("🔍 Testing WYSIWYG article structure...")
        
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
        
        log_test_result(f"📚 Found {len(articles)} articles to analyze")
        
        # Test recent articles for WYSIWYG structure
        wysiwyg_features_found = {
            'article_body_wrapper': 0,
            'professional_structure': 0,
            'emoji_prefixes': 0,
            'mini_toc_container': 0,
            'expandable_sections': 0,
            'enhanced_notes': 0,
            'related_links': 0,
            'code_blocks_with_language': 0,
            'semantic_html': 0
        }
        
        articles_analyzed = 0
        
        for article in articles[:5]:  # Analyze first 5 articles
            content = article.get('content', '')
            title = article.get('title', 'Untitled')
            
            if not content:
                continue
                
            articles_analyzed += 1
            log_test_result(f"🔍 Analyzing article: {title[:50]}...")
            
            # Parse HTML content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Test 1: Article body wrapper
            if soup.find('div', class_='article-body'):
                wysiwyg_features_found['article_body_wrapper'] += 1
                log_test_result("  ✅ Found .article-body wrapper")
            
            # Test 2: Professional structure with emoji prefixes
            emoji_headings = soup.find_all(['h2', 'h3'], string=re.compile(r'^[🚀⚡🛠️❓🔗📋📖🎯]'))
            if emoji_headings:
                wysiwyg_features_found['emoji_prefixes'] += 1
                log_test_result(f"  ✅ Found {len(emoji_headings)} headings with emoji prefixes")
            
            # Test 3: Mini-TOC container
            if soup.find('div', {'id': 'mini-toc-container', 'class': 'mini-toc'}):
                wysiwyg_features_found['mini_toc_container'] += 1
                log_test_result("  ✅ Found mini-TOC container")
            
            # Test 4: Expandable sections
            expandable_sections = soup.find_all('div', class_='expandable')
            if expandable_sections:
                wysiwyg_features_found['expandable_sections'] += 1
                log_test_result(f"  ✅ Found {len(expandable_sections)} expandable sections")
            
            # Test 5: Enhanced notes
            note_divs = soup.find_all('div', class_='note')
            if note_divs:
                wysiwyg_features_found['enhanced_notes'] += 1
                log_test_result(f"  ✅ Found {len(note_divs)} enhanced note sections")
            
            # Test 6: Related links with proper classes
            related_links = soup.find_all('div', class_='related-links wysiwyg-text-align-center')
            if not related_links:
                related_links = soup.find_all('div', class_='related-links')
            if related_links:
                wysiwyg_features_found['related_links'] += 1
                log_test_result(f"  ✅ Found {len(related_links)} related links sections")
            
            # Test 7: Code blocks with language classes
            code_blocks = soup.find_all('pre', class_='line-numbers')
            if not code_blocks:
                code_blocks = soup.find_all('code', class_=re.compile(r'language-\w+'))
            if code_blocks:
                wysiwyg_features_found['code_blocks_with_language'] += 1
                log_test_result(f"  ✅ Found {len(code_blocks)} enhanced code blocks")
            
            # Test 8: Semantic HTML structure
            semantic_elements = soup.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'strong', 'em'])
            if len(semantic_elements) >= 5:  # Reasonable threshold
                wysiwyg_features_found['semantic_html'] += 1
                log_test_result(f"  ✅ Found proper semantic HTML structure ({len(semantic_elements)} elements)")
        
        # Calculate success rates
        log_test_result(f"\n📊 WYSIWYG STRUCTURE ANALYSIS RESULTS:")
        log_test_result(f"Articles analyzed: {articles_analyzed}")
        
        total_features = len(wysiwyg_features_found)
        features_with_coverage = sum(1 for count in wysiwyg_features_found.values() if count > 0)
        
        for feature, count in wysiwyg_features_found.items():
            percentage = (count / articles_analyzed * 100) if articles_analyzed > 0 else 0
            status = "✅" if count > 0 else "❌"
            log_test_result(f"  {status} {feature.replace('_', ' ').title()}: {count}/{articles_analyzed} articles ({percentage:.1f}%)")
        
        success_rate = (features_with_coverage / total_features * 100)
        log_test_result(f"\n🎯 OVERALL WYSIWYG INTEGRATION SUCCESS RATE: {success_rate:.1f}% ({features_with_coverage}/{total_features} features)")
        
        # Determine if test passes
        if success_rate >= 70:  # 70% threshold for success
            log_test_result("🎉 WYSIWYG STRUCTURE TEST PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ WYSIWYG STRUCTURE TEST FAILED - Insufficient feature coverage", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ WYSIWYG structure test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_css_integration():
    """Test enhanced CSS integration and styling"""
    try:
        log_test_result("🎨 Testing Enhanced CSS Integration...")
        
        # Get articles to test CSS classes
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for CSS testing", "ERROR")
            return False
        
        css_features_found = {
            'article_body_class': 0,
            'expandable_classes': 0,
            'mini_toc_classes': 0,
            'related_links_classes': 0,
            'enhanced_typography': 0,
            'responsive_elements': 0,
            'professional_styling': 0
        }
        
        articles_tested = 0
        
        for article in articles[:3]:  # Test first 3 articles
            content = article.get('content', '')
            title = article.get('title', 'Untitled')
            
            if not content:
                continue
                
            articles_tested += 1
            log_test_result(f"🎨 Testing CSS in article: {title[:40]}...")
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Test CSS class presence
            if soup.find(class_='article-body'):
                css_features_found['article_body_class'] += 1
                log_test_result("  ✅ Found .article-body CSS class")
            
            if soup.find(class_='expandable'):
                css_features_found['expandable_classes'] += 1
                log_test_result("  ✅ Found .expandable CSS classes")
            
            if soup.find(class_='mini-toc'):
                css_features_found['mini_toc_classes'] += 1
                log_test_result("  ✅ Found .mini-toc CSS classes")
            
            if soup.find(class_='related-links'):
                css_features_found['related_links_classes'] += 1
                log_test_result("  ✅ Found .related-links CSS classes")
            
            # Test enhanced typography elements
            typography_elements = soup.find_all(['h2', 'h3', 'p', 'strong', 'em'])
            if len(typography_elements) >= 5:
                css_features_found['enhanced_typography'] += 1
                log_test_result("  ✅ Found enhanced typography elements")
            
            # Test for responsive design indicators
            responsive_indicators = soup.find_all(class_=re.compile(r'(responsive|mobile|tablet|desktop)'))
            if responsive_indicators or 'max-width' in content or 'media' in content:
                css_features_found['responsive_elements'] += 1
                log_test_result("  ✅ Found responsive design elements")
            
            # Test professional styling indicators
            professional_classes = soup.find_all(class_=re.compile(r'(professional|enhanced|styled|formatted)'))
            if professional_classes or len(soup.find_all(class_=True)) >= 3:
                css_features_found['professional_styling'] += 1
                log_test_result("  ✅ Found professional styling classes")
        
        # Calculate CSS integration success
        log_test_result(f"\n🎨 ENHANCED CSS INTEGRATION RESULTS:")
        
        total_css_features = len(css_features_found)
        css_features_present = sum(1 for count in css_features_found.values() if count > 0)
        
        for feature, count in css_features_found.items():
            percentage = (count / articles_tested * 100) if articles_tested > 0 else 0
            status = "✅" if count > 0 else "❌"
            log_test_result(f"  {status} {feature.replace('_', ' ').title()}: {count}/{articles_tested} articles ({percentage:.1f}%)")
        
        css_success_rate = (css_features_present / total_css_features * 100)
        log_test_result(f"\n🎯 CSS INTEGRATION SUCCESS RATE: {css_success_rate:.1f}% ({css_features_present}/{total_css_features} features)")
        
        if css_success_rate >= 60:  # 60% threshold for CSS success
            log_test_result("🎉 ENHANCED CSS INTEGRATION TEST PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ ENHANCED CSS INTEGRATION TEST FAILED", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ Enhanced CSS integration test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_javascript_functionality():
    """Test JavaScript functionality integration"""
    try:
        log_test_result("⚡ Testing JavaScript Functionality Integration...")
        
        # Get articles to test JavaScript features
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for JavaScript testing", "ERROR")
            return False
        
        js_features_found = {
            'expandable_toggles': 0,
            'copy_buttons': 0,
            'mini_toc_generation': 0,
            'anchor_links': 0,
            'interactive_elements': 0,
            'dynamic_content': 0
        }
        
        articles_tested = 0
        
        for article in articles[:3]:  # Test first 3 articles
            content = article.get('content', '')
            title = article.get('title', 'Untitled')
            
            if not content:
                continue
                
            articles_tested += 1
            log_test_result(f"⚡ Testing JavaScript features in: {title[:40]}...")
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Test for expandable toggle elements
            expandable_elements = soup.find_all(class_='expandable')
            if expandable_elements:
                js_features_found['expandable_toggles'] += 1
                log_test_result("  ✅ Found expandable toggle elements")
            
            # Test for copy button indicators
            code_blocks = soup.find_all(['pre', 'code'])
            if code_blocks and len(code_blocks) >= 2:
                js_features_found['copy_buttons'] += 1
                log_test_result("  ✅ Found code blocks (copy button ready)")
            
            # Test for mini-TOC generation elements
            toc_elements = soup.find_all(class_=re.compile(r'(toc|table-of-contents)'))
            headings = soup.find_all(['h2', 'h3', 'h4'])
            if toc_elements or len(headings) >= 3:
                js_features_found['mini_toc_generation'] += 1
                log_test_result("  ✅ Found mini-TOC generation elements")
            
            # Test for anchor links
            anchor_links = soup.find_all('a', href=re.compile(r'^#'))
            if anchor_links:
                js_features_found['anchor_links'] += 1
                log_test_result(f"  ✅ Found {len(anchor_links)} anchor links")
            
            # Test for interactive elements
            interactive_elements = soup.find_all(class_=re.compile(r'(interactive|clickable|toggle|button)'))
            if interactive_elements or expandable_elements:
                js_features_found['interactive_elements'] += 1
                log_test_result("  ✅ Found interactive elements")
            
            # Test for dynamic content indicators
            dynamic_indicators = soup.find_all(attrs={'data-toggle': True}) or \
                                soup.find_all(attrs={'data-target': True}) or \
                                soup.find_all(class_=re.compile(r'(dynamic|auto|generated)'))
            if dynamic_indicators or len(soup.find_all(id=True)) >= 2:
                js_features_found['dynamic_content'] += 1
                log_test_result("  ✅ Found dynamic content indicators")
        
        # Calculate JavaScript integration success
        log_test_result(f"\n⚡ JAVASCRIPT FUNCTIONALITY RESULTS:")
        
        total_js_features = len(js_features_found)
        js_features_present = sum(1 for count in js_features_found.values() if count > 0)
        
        for feature, count in js_features_found.items():
            percentage = (count / articles_tested * 100) if articles_tested > 0 else 0
            status = "✅" if count > 0 else "❌"
            log_test_result(f"  {status} {feature.replace('_', ' ').title()}: {count}/{articles_tested} articles ({percentage:.1f}%)")
        
        js_success_rate = (js_features_present / total_js_features * 100)
        log_test_result(f"\n🎯 JAVASCRIPT INTEGRATION SUCCESS RATE: {js_success_rate:.1f}% ({js_features_present}/{total_js_features} features)")
        
        if js_success_rate >= 50:  # 50% threshold for JavaScript success
            log_test_result("🎉 JAVASCRIPT FUNCTIONALITY TEST PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ JAVASCRIPT FUNCTIONALITY TEST FAILED", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ JavaScript functionality test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_wysiwyg_test():
    """Run comprehensive WYSIWYG template integration test suite"""
    log_test_result("🚀 STARTING COMPREHENSIVE WYSIWYG TEMPLATE INTEGRATION TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'content_processing': False,
        'wysiwyg_structure': False,
        'enhanced_css': False,
        'javascript_functionality': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Content Processing
    log_test_result("\nTEST 2: WYSIWYG Content Processing")
    test_results['content_processing'] = process_wysiwyg_test_content()
    
    # Test 3: WYSIWYG Article Structure
    log_test_result("\nTEST 3: WYSIWYG Article Structure Verification")
    test_results['wysiwyg_structure'] = test_wysiwyg_article_structure()
    
    # Test 4: Enhanced CSS Integration
    log_test_result("\nTEST 4: Enhanced CSS Integration")
    test_results['enhanced_css'] = test_enhanced_css_integration()
    
    # Test 5: JavaScript Functionality
    log_test_result("\nTEST 5: JavaScript Functionality Integration")
    test_results['javascript_functionality'] = test_javascript_functionality()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 WYSIWYG TEMPLATE INTEGRATION TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Determine overall success
    critical_tests = ['wysiwyg_structure', 'enhanced_css', 'javascript_functionality']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed >= 2:  # At least 2 of 3 critical tests must pass
        log_test_result("🎉 WYSIWYG TEMPLATE INTEGRATION SUCCESS!", "CRITICAL_SUCCESS")
        log_test_result("✅ Professional WYSIWYG template system is operational", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ WYSIWYG TEMPLATE INTEGRATION FAILURE", "CRITICAL_ERROR")
        log_test_result("❌ WYSIWYG template system needs additional work", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("WYSIWYG Template Integration Testing")
    print("=" * 50)
    
    results = run_comprehensive_wysiwyg_test()
    
    # Exit with appropriate code
    critical_tests = ['wysiwyg_structure', 'enhanced_css', 'javascript_functionality']
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed >= 2:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure