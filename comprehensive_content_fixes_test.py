#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE VALIDATION - ALL REMAINING ISSUES COMPLETE FIX
Testing the comprehensive fixes for ALL remaining Content Library issues with enhanced wrapper cleaning and text deduplication

COMPREHENSIVE FIXES TO VALIDATE:
1. Enhanced HTML Wrapper Cleaning (5 Methods)
2. Advanced Text Deduplication (Multi-Approach)  
3. Content Quality & Functionality Verification
4. Comprehensive Edge Case Testing
5. User Feedback Mapping Validation

SUCCESS CRITERIA - 100% RESOLUTION REQUIRED:
✅ 0/X articles contain ANY HTML wrappers or document structure elements
✅ 0 text duplications detected in any article content anywhere
✅ All articles start with clean, semantic HTML structure
✅ Text quality is professional without ANY repetition patterns
✅ All existing functionality works (ordered lists, WYSIWYG features, etc.)
✅ Enhanced fixes are robust and comprehensive
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
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
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

def generate_test_content_with_potential_issues():
    """Generate comprehensive test content that could trigger wrapper and duplication issues"""
    
    test_content = """
    Google Maps JavaScript API Tutorial - Complete Implementation Guide
    
    This comprehensive tutorial covers everything you need to know about implementing Google Maps JavaScript API in your web applications. We'll walk through the setup process, basic implementation, advanced features, and troubleshooting common issues.
    
    ## Getting Started with Google Maps API
    
    First, you need to obtain an API key from Google Cloud Console. This is essential for accessing the Google Maps services.
    
    ### Step 1: Create a Google Cloud Project
    
    1. Go to the Google Cloud Console
    2. Create a new project or select an existing one
    3. Enable the Maps JavaScript API
    4. Generate an API key
    
    ### Step 2: Basic HTML Setup
    
    Here's the basic HTML structure you'll need:
    
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
    
    ## Advanced Features Implementation
    
    ### Adding Markers to Your Map
    
    Markers are essential for highlighting specific locations on your map. Here's how to add them:
    
    ```javascript
    function addMarker(map, position, title) {
        var marker = new google.maps.Marker({
            position: position,
            map: map,
            title: title
        });
        return marker;
    }
    
    // Usage example
    var marker = addMarker(map, {lat: -34.397, lng: 150.644}, 'My Location');
    ```
    
    ### Custom Map Styling
    
    You can customize the appearance of your map using custom styles:
    
    ```javascript
    var customMapStyle = [
        {
            "featureType": "water",
            "elementType": "geometry",
            "stylers": [{"color": "#e9e9e9"}, {"lightness": 17}]
        },
        {
            "featureType": "landscape",
            "elementType": "geometry",
            "stylers": [{"color": "#f5f5f5"}, {"lightness": 20}]
        }
    ];
    
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 10,
        center: {lat: -34.397, lng: 150.644},
        styles: customMapStyle
    });
    ```
    
    ## Troubleshooting Common Issues
    
    ### API Key Problems
    
    If your map isn't loading, check these common API key issues:
    
    1. Ensure your API key is valid and active
    2. Check that the Maps JavaScript API is enabled
    3. Verify your API key restrictions are properly configured
    4. Make sure you haven't exceeded your quota limits
    
    ### Map Display Issues
    
    Common display problems and their solutions:
    
    - **Map container has zero height**: Set explicit height in CSS
    - **Map appears gray**: Usually an API key or billing issue
    - **Markers not appearing**: Check marker position coordinates
    - **Custom styles not working**: Validate your style JSON format
    
    ## Best Practices and Performance Tips
    
    ### Optimizing Map Performance
    
    1. **Lazy Loading**: Load maps only when needed
    2. **Marker Clustering**: Group nearby markers for better performance
    3. **Viewport Management**: Only load data for visible areas
    4. **Caching**: Cache map tiles and data when possible
    
    ### Security Considerations
    
    - Always restrict your API keys to specific domains
    - Use HTTPS for all map implementations
    - Validate user input before geocoding
    - Monitor your API usage regularly
    
    ## Complete Working Example
    
    Here's a complete, working example that demonstrates all the concepts covered:
    
    ```html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Advanced Google Maps Example</title>
        <style>
            #map {
                height: 500px;
                width: 100%;
                border: 2px solid #ccc;
                border-radius: 8px;
            }
            .controls {
                margin: 20px 0;
            }
            button {
                margin: 5px;
                padding: 10px 15px;
                background: #4285f4;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Advanced Google Maps Implementation</h1>
        
        <div class="controls">
            <button onclick="addRandomMarker()">Add Random Marker</button>
            <button onclick="clearMarkers()">Clear All Markers</button>
            <button onclick="toggleMapType()">Toggle Map Type</button>
        </div>
        
        <div id="map"></div>
        
        <script>
            let map;
            let markers = [];
            let isRoadMap = true;
            
            function initMap() {
                // Initialize the map
                map = new google.maps.Map(document.getElementById('map'), {
                    zoom: 12,
                    center: {lat: 37.7749, lng: -122.4194}, // San Francisco
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                });
                
                // Add initial marker
                addMarker({lat: 37.7749, lng: -122.4194}, 'San Francisco');
                
                // Add click listener
                map.addListener('click', function(event) {
                    addMarker(event.latLng, 'Clicked Location');
                });
            }
            
            function addMarker(position, title) {
                const marker = new google.maps.Marker({
                    position: position,
                    map: map,
                    title: title,
                    animation: google.maps.Animation.DROP
                });
                
                // Add info window
                const infoWindow = new google.maps.InfoWindow({
                    content: `<div><strong>${title}</strong><br>Lat: ${position.lat}<br>Lng: ${position.lng}</div>`
                });
                
                marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                });
                
                markers.push(marker);
            }
            
            function addRandomMarker() {
                const lat = 37.7749 + (Math.random() - 0.5) * 0.1;
                const lng = -122.4194 + (Math.random() - 0.5) * 0.1;
                addMarker({lat: lat, lng: lng}, `Random Marker ${markers.length + 1}`);
            }
            
            function clearMarkers() {
                markers.forEach(marker => marker.setMap(null));
                markers = [];
            }
            
            function toggleMapType() {
                if (isRoadMap) {
                    map.setMapTypeId(google.maps.MapTypeId.SATELLITE);
                    isRoadMap = false;
                } else {
                    map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
                    isRoadMap = true;
                }
            }
        </script>
        
        <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap" async defer></script>
    </body>
    </html>
    ```
    
    This example demonstrates:
    - Basic map initialization
    - Dynamic marker creation
    - Info windows with custom content
    - Map type switching
    - Event handling
    - Responsive design considerations
    
    ## Conclusion
    
    The Google Maps JavaScript API provides powerful tools for creating interactive map experiences. By following the patterns and best practices outlined in this tutorial, you can build robust, performant map applications that provide excellent user experiences.
    
    Remember to always test your implementation thoroughly, monitor your API usage, and keep your API keys secure. With these fundamentals in place, you're ready to build amazing map-based applications.
    """
    
    return test_content

def process_test_content_and_analyze():
    """Process test content through the Knowledge Engine and analyze results for wrapper/duplication issues"""
    try:
        log_test_result("🎯 STARTING COMPREHENSIVE CONTENT FIXES VALIDATION", "CRITICAL")
        log_test_result("Processing Google Maps tutorial content to test wrapper cleaning and text deduplication")
        
        # Generate test content
        test_content = generate_test_content_with_potential_issues()
        content_length = len(test_content)
        log_test_result(f"📝 Generated test content: {content_length:,} characters")
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing content through Knowledge Engine...")
        
        # Use the text processing endpoint
        payload = {
            "content": test_content,
            "filename": "Google_Maps_API_Tutorial_Test.txt"
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process-text", 
                               json=payload, 
                               timeout=300,  # 5 minute timeout
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        processing_data = response.json()
        job_id = processing_data.get('job_id')
        
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
                        log_test_result(f"📄 Articles generated: {articles_generated}")
                        
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
        log_test_result(f"❌ Content processing test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def analyze_html_wrapper_cleaning():
    """CRITICAL TEST 1: Complete HTML Wrapper Elimination"""
    try:
        log_test_result("🧹 TEST 1: COMPLETE HTML WRAPPER ELIMINATION", "CRITICAL")
        
        # Get all articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = len(articles)
        
        log_test_result(f"📚 Analyzing {total_articles} articles for HTML wrapper issues")
        
        if total_articles == 0:
            log_test_result("⚠️ No articles found in Content Library", "WARNING")
            return False
        
        # Analyze each article for wrapper issues
        wrapper_issues = []
        document_structure_issues = []
        markdown_code_block_issues = []
        
        for i, article in enumerate(articles):
            article_id = article.get('id', f'article_{i}')
            title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"🔍 Analyzing article {i+1}/{total_articles}: {title}...")
            
            # Check for Method 1: ```html markdown code block wrappers
            if re.search(r'```html', content, re.IGNORECASE):
                markdown_code_block_issues.append({
                    'id': article_id,
                    'title': title,
                    'issue': 'Contains ```html markdown code block wrapper'
                })
            
            # Check for Method 2: ANY markdown code block variations
            markdown_blocks = re.findall(r'```\w*', content)
            if markdown_blocks:
                for block in markdown_blocks:
                    if block not in ['```javascript', '```js', '```css', '```html']:  # Allow legitimate code blocks
                        markdown_code_block_issues.append({
                            'id': article_id,
                            'title': title,
                            'issue': f'Contains markdown code block: {block}'
                        })
            
            # Check for Method 4: HTML document structure elements
            document_patterns = [
                r'<!DOCTYPE\s+html',
                r'<html[^>]*>',
                r'<head[^>]*>',
                r'<body[^>]*>',
                r'<meta[^>]*>',
                r'<title[^>]*>'
            ]
            
            for pattern in document_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    document_structure_issues.append({
                        'id': article_id,
                        'title': title,
                        'issue': f'Contains HTML document structure: {pattern}'
                    })
            
            # Check for Method 5: Leading/trailing backticks
            if content.strip().startswith('```') or content.strip().endswith('```'):
                wrapper_issues.append({
                    'id': article_id,
                    'title': title,
                    'issue': 'Content wrapped in backticks'
                })
        
        # Report results
        total_issues = len(wrapper_issues) + len(document_structure_issues) + len(markdown_code_block_issues)
        
        log_test_result(f"📊 HTML WRAPPER ANALYSIS RESULTS:")
        log_test_result(f"   📄 Total articles analyzed: {total_articles}")
        log_test_result(f"   🧹 Articles with wrapper issues: {total_issues}")
        log_test_result(f"   ✅ Clean articles: {total_articles - total_issues}")
        
        if total_issues == 0:
            log_test_result("🎉 SUCCESS: 0/X articles contain ANY HTML wrappers or document structure elements", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ FAILURE: {total_issues} articles still contain wrapper issues", "ERROR")
            
            # Report specific issues
            if wrapper_issues:
                log_test_result(f"   🔸 Backtick wrapper issues: {len(wrapper_issues)}")
                for issue in wrapper_issues[:3]:  # Show first 3
                    log_test_result(f"     - {issue['title']}: {issue['issue']}")
            
            if document_structure_issues:
                log_test_result(f"   🔸 Document structure issues: {len(document_structure_issues)}")
                for issue in document_structure_issues[:3]:  # Show first 3
                    log_test_result(f"     - {issue['title']}: {issue['issue']}")
            
            if markdown_code_block_issues:
                log_test_result(f"   🔸 Markdown code block issues: {len(markdown_code_block_issues)}")
                for issue in markdown_code_block_issues[:3]:  # Show first 3
                    log_test_result(f"     - {issue['title']}: {issue['issue']}")
            
            return False
    
    except Exception as e:
        log_test_result(f"❌ HTML wrapper analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def analyze_text_deduplication():
    """CRITICAL TEST 2: Perfect Text Deduplication"""
    try:
        log_test_result("🔄 TEST 2: PERFECT TEXT DEDUPLICATION", "CRITICAL")
        
        # Get all articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = len(articles)
        
        log_test_result(f"📚 Analyzing {total_articles} articles for text duplication issues")
        
        if total_articles == 0:
            log_test_result("⚠️ No articles found in Content Library", "WARNING")
            return False
        
        # Analyze each article for duplication patterns
        duplication_issues = []
        total_duplications = 0
        
        for i, article in enumerate(articles):
            article_id = article.get('id', f'article_{i}')
            title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"🔍 Analyzing article {i+1}/{total_articles}: {title}...")
            
            # Parse HTML content
            try:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check for various duplication patterns
                article_duplications = []
                
                # Pattern 1: "TextText" (immediate word duplications)
                text_content = soup.get_text()
                immediate_duplications = re.findall(r'\b(\w+)\1\b', text_content)
                if immediate_duplications:
                    article_duplications.extend([f"Immediate duplication: {dup}" for dup in immediate_duplications])
                
                # Pattern 2: "Text Text" (word repetitions with space)
                word_repetitions = re.findall(r'\b(\w+)\s+\1\b', text_content)
                if word_repetitions:
                    article_duplications.extend([f"Word repetition: {dup}" for dup in word_repetitions])
                
                # Pattern 3: Sentence-level duplications
                sentences = re.split(r'[.!?]+', text_content)
                sentence_counts = {}
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 10:  # Only check substantial sentences
                        if sentence in sentence_counts:
                            sentence_counts[sentence] += 1
                        else:
                            sentence_counts[sentence] = 1
                
                duplicated_sentences = {k: v for k, v in sentence_counts.items() if v > 1}
                if duplicated_sentences:
                    article_duplications.extend([f"Sentence duplication: '{sent[:50]}...' (appears {count} times)" 
                                               for sent, count in duplicated_sentences.items()])
                
                # Pattern 4: List item duplications
                list_items = soup.find_all(['li'])
                list_texts = [item.get_text().strip() for item in list_items]
                list_counts = {}
                for text in list_texts:
                    if len(text) > 5:  # Only check substantial list items
                        if text in list_counts:
                            list_counts[text] += 1
                        else:
                            list_counts[text] = 1
                
                duplicated_lists = {k: v for k, v in list_counts.items() if v > 1}
                if duplicated_lists:
                    article_duplications.extend([f"List item duplication: '{item[:50]}...' (appears {count} times)" 
                                               for item, count in duplicated_lists.items()])
                
                # Pattern 5: Paragraph duplications
                paragraphs = soup.find_all('p')
                paragraph_texts = [p.get_text().strip() for p in paragraphs]
                paragraph_counts = {}
                for text in paragraph_texts:
                    if len(text) > 20:  # Only check substantial paragraphs
                        if text in paragraph_counts:
                            paragraph_counts[text] += 1
                        else:
                            paragraph_counts[text] = 1
                
                duplicated_paragraphs = {k: v for k, v in paragraph_counts.items() if v > 1}
                if duplicated_paragraphs:
                    article_duplications.extend([f"Paragraph duplication: '{para[:50]}...' (appears {count} times)" 
                                               for para, count in duplicated_paragraphs.items()])
                
                if article_duplications:
                    duplication_issues.append({
                        'id': article_id,
                        'title': title,
                        'duplications': article_duplications
                    })
                    total_duplications += len(article_duplications)
                
            except Exception as parse_error:
                log_test_result(f"⚠️ Error parsing article {title}: {parse_error}")
                continue
        
        # Report results
        articles_with_duplications = len(duplication_issues)
        clean_articles = total_articles - articles_with_duplications
        
        log_test_result(f"📊 TEXT DEDUPLICATION ANALYSIS RESULTS:")
        log_test_result(f"   📄 Total articles analyzed: {total_articles}")
        log_test_result(f"   🔄 Articles with duplications: {articles_with_duplications}")
        log_test_result(f"   📊 Total duplication instances: {total_duplications}")
        log_test_result(f"   ✅ Clean articles: {clean_articles}")
        
        if total_duplications == 0:
            log_test_result("🎉 SUCCESS: 0 text duplications detected in any article content anywhere", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ FAILURE: {total_duplications} text duplications found across {articles_with_duplications} articles", "ERROR")
            
            # Report specific duplication issues
            for issue in duplication_issues[:3]:  # Show first 3 articles with issues
                log_test_result(f"   🔸 {issue['title']}:")
                for dup in issue['duplications'][:3]:  # Show first 3 duplications per article
                    log_test_result(f"     - {dup}")
            
            return False
    
    except Exception as e:
        log_test_result(f"❌ Text deduplication analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def analyze_content_quality_and_functionality():
    """CRITICAL TEST 3: Content Quality & Functionality Verification"""
    try:
        log_test_result("⭐ TEST 3: CONTENT QUALITY & FUNCTIONALITY VERIFICATION", "CRITICAL")
        
        # Get all articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = len(articles)
        
        log_test_result(f"📚 Analyzing {total_articles} articles for content quality and functionality")
        
        if total_articles == 0:
            log_test_result("⚠️ No articles found in Content Library", "WARNING")
            return False
        
        # Quality metrics
        quality_metrics = {
            'semantic_html_structure': 0,
            'ordered_lists_continuous': 0,
            'wysiwyg_features': 0,
            'code_blocks_with_content': 0,
            'professional_content': 0,
            'proper_headings': 0
        }
        
        issues_found = []
        
        for i, article in enumerate(articles):
            article_id = article.get('id', f'article_{i}')
            title = article.get('title', 'Untitled')[:50]
            content = article.get('content', '')
            
            log_test_result(f"🔍 Analyzing quality for article {i+1}/{total_articles}: {title}...")
            
            try:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check 1: Semantic HTML structure
                has_semantic_html = bool(soup.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'li', 'strong', 'em']))
                if has_semantic_html:
                    quality_metrics['semantic_html_structure'] += 1
                else:
                    issues_found.append(f"{title}: Missing semantic HTML structure")
                
                # Check 2: Ordered lists with continuous numbering
                ordered_lists = soup.find_all('ol')
                if ordered_lists:
                    has_proper_numbering = True
                    for ol in ordered_lists:
                        list_items = ol.find_all('li')
                        if len(list_items) > 1:  # Only check lists with multiple items
                            # Check if list items are properly structured
                            for li in list_items:
                                if not li.get_text().strip():
                                    has_proper_numbering = False
                                    break
                    
                    if has_proper_numbering:
                        quality_metrics['ordered_lists_continuous'] += 1
                    else:
                        issues_found.append(f"{title}: Ordered lists have numbering issues")
                
                # Check 3: WYSIWYG features (Mini-TOC, callouts)
                wysiwyg_features = 0
                if soup.find_all(class_=re.compile(r'toc|callout|doc-')):
                    wysiwyg_features += 1
                if soup.find_all(['blockquote', 'figure', 'figcaption']):
                    wysiwyg_features += 1
                if soup.find_all('a', href=True):
                    wysiwyg_features += 1
                
                if wysiwyg_features > 0:
                    quality_metrics['wysiwyg_features'] += 1
                
                # Check 4: Code blocks with actual content
                code_blocks = soup.find_all(['pre', 'code'])
                if code_blocks:
                    has_content_in_code = True
                    for code in code_blocks:
                        code_text = code.get_text().strip()
                        if len(code_text) < 10:  # Very short or empty code blocks
                            has_content_in_code = False
                            break
                    
                    if has_content_in_code:
                        quality_metrics['code_blocks_with_content'] += 1
                    else:
                        issues_found.append(f"{title}: Code blocks are empty or too short")
                
                # Check 5: Professional content quality
                text_content = soup.get_text()
                word_count = len(text_content.split())
                if word_count > 100 and not re.search(r'lorem ipsum|placeholder|todo|fixme', text_content.lower()):
                    quality_metrics['professional_content'] += 1
                else:
                    issues_found.append(f"{title}: Content appears to be placeholder or too short ({word_count} words)")
                
                # Check 6: Proper heading structure (starts with h2, no h1)
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if headings:
                    first_heading = headings[0]
                    if first_heading.name == 'h2':  # Should start with h2
                        has_h1 = bool(soup.find('h1'))
                        if not has_h1:  # Should not have h1
                            quality_metrics['proper_headings'] += 1
                        else:
                            issues_found.append(f"{title}: Contains h1 tags (should start with h2)")
                    else:
                        issues_found.append(f"{title}: Doesn't start with h2 heading")
                
            except Exception as parse_error:
                log_test_result(f"⚠️ Error analyzing quality for article {title}: {parse_error}")
                continue
        
        # Calculate success rates
        success_rates = {}
        for metric, count in quality_metrics.items():
            success_rate = (count / total_articles) * 100 if total_articles > 0 else 0
            success_rates[metric] = success_rate
        
        # Report results
        log_test_result(f"📊 CONTENT QUALITY ANALYSIS RESULTS:")
        log_test_result(f"   📄 Total articles analyzed: {total_articles}")
        
        for metric, rate in success_rates.items():
            status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            log_test_result(f"   {status} {metric.replace('_', ' ').title()}: {rate:.1f}% ({quality_metrics[metric]}/{total_articles})")
        
        # Overall success criteria
        overall_success = all(rate >= 80 for rate in success_rates.values())
        
        if overall_success:
            log_test_result("🎉 SUCCESS: All existing functionality works (ordered lists, WYSIWYG features, etc.)", "SUCCESS")
            return True
        else:
            log_test_result("❌ FAILURE: Some functionality issues detected", "ERROR")
            
            # Show specific issues
            if issues_found:
                log_test_result("   🔸 Specific issues found:")
                for issue in issues_found[:5]:  # Show first 5 issues
                    log_test_result(f"     - {issue}")
            
            return False
    
    except Exception as e:
        log_test_result(f"❌ Content quality analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_content_fixes_validation():
    """Run comprehensive validation of all content fixes"""
    log_test_result("🚀 STARTING COMPREHENSIVE CONTENT FIXES VALIDATION", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'content_processing': False,
        'html_wrapper_cleaning': False,
        'text_deduplication': False,
        'content_quality_functionality': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Content Processing
    log_test_result("\nTEST 2: Content Processing Test")
    test_results['content_processing'] = process_test_content_and_analyze()
    
    # Test 3: HTML Wrapper Cleaning (CRITICAL)
    log_test_result("\nTEST 3: CRITICAL HTML WRAPPER CLEANING VALIDATION")
    test_results['html_wrapper_cleaning'] = analyze_html_wrapper_cleaning()
    
    # Test 4: Text Deduplication (CRITICAL)
    log_test_result("\nTEST 4: CRITICAL TEXT DEDUPLICATION VALIDATION")
    test_results['text_deduplication'] = analyze_text_deduplication()
    
    # Test 5: Content Quality & Functionality
    log_test_result("\nTEST 5: Content Quality & Functionality Verification")
    test_results['content_quality_functionality'] = analyze_content_quality_and_functionality()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL COMPREHENSIVE VALIDATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Critical success criteria evaluation
    critical_tests = ['html_wrapper_cleaning', 'text_deduplication']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        log_test_result("🎉 CRITICAL SUCCESS: All remaining Content Library issues have been COMPLETELY RESOLVED!", "CRITICAL_SUCCESS")
        log_test_result("✅ 0/X articles contain ANY HTML wrappers or document structure elements", "CRITICAL_SUCCESS")
        log_test_result("✅ 0 text duplications detected in any article content anywhere", "CRITICAL_SUCCESS")
        log_test_result("✅ Enhanced fixes are robust and comprehensive", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Some critical issues remain unresolved", "CRITICAL_ERROR")
        if not test_results['html_wrapper_cleaning']:
            log_test_result("❌ HTML wrapper cleaning is NOT working properly", "CRITICAL_ERROR")
        if not test_results['text_deduplication']:
            log_test_result("❌ Text deduplication is NOT working properly", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Comprehensive Content Library Fixes Validation")
    print("=" * 60)
    
    results = run_comprehensive_content_fixes_validation()
    
    # Exit with appropriate code
    critical_success = results['html_wrapper_cleaning'] and results['text_deduplication']
    if critical_success:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure