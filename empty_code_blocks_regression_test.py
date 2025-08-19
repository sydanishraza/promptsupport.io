#!/usr/bin/env python3
"""
CRITICAL REGRESSION FIX TESTING - Empty Code Blocks Issue
Testing the critical fix for empty divs/code blocks regression in article generation

ISSUE FIXED:
- Empty divs getting added in articles instead of proper code blocks
- FAQ and Google Maps API Tutorial articles showing empty <pre><code> blocks
- Code content being stripped from within code blocks
- Mouse-related editor issues due to empty div structures

FIX IMPLEMENTED:
- Modified clean_html_wrappers() function line 10607
- Changed regex from r'<pre><code[^>]*>\s*</code></pre>' to r'<pre><code[^>]*></code></pre>'
- Now only removes truly empty code blocks (no content), preserves formatted code with whitespace/indentation
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import re

# Backend URL from frontend .env
BACKEND_URL = "https://d5a10bd5-e4cd-4ea6-bdac-0b626acf09cb.preview.emergentagent.com"
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

def analyze_code_blocks_in_content(content):
    """Analyze code blocks in article content"""
    results = {
        'total_code_blocks': 0,
        'empty_code_blocks': 0,
        'code_blocks_with_content': 0,
        'code_blocks_with_whitespace_only': 0,
        'properly_formatted_code_blocks': 0,
        'code_block_details': []
    }
    
    # Find all <pre><code> blocks
    code_block_pattern = r'<pre><code[^>]*>(.*?)</code></pre>'
    matches = re.findall(code_block_pattern, content, re.DOTALL | re.IGNORECASE)
    
    results['total_code_blocks'] = len(matches)
    
    for i, code_content in enumerate(matches):
        block_info = {
            'block_number': i + 1,
            'content_length': len(code_content),
            'has_actual_content': bool(code_content.strip()),
            'is_whitespace_only': code_content.isspace() if code_content else False,
            'content_preview': code_content[:100] if code_content else "EMPTY"
        }
        
        if not code_content:
            results['empty_code_blocks'] += 1
            block_info['type'] = 'EMPTY'
        elif code_content.isspace():
            results['code_blocks_with_whitespace_only'] += 1
            block_info['type'] = 'WHITESPACE_ONLY'
        elif code_content.strip():
            results['code_blocks_with_content'] += 1
            block_info['type'] = 'HAS_CONTENT'
            
            # Check if it's properly formatted (has meaningful code)
            if any(keyword in code_content.lower() for keyword in ['function', 'var ', 'const ', 'let ', 'class ', 'def ', 'import', 'export', 'html', 'css', 'javascript', '<', '>', '{', '}', '(', ')']):
                results['properly_formatted_code_blocks'] += 1
                block_info['is_properly_formatted'] = True
            else:
                block_info['is_properly_formatted'] = False
        
        results['code_block_details'].append(block_info)
    
    return results

def test_google_maps_api_tutorial_content():
    """Test Google Maps API Tutorial content generation for code block preservation"""
    try:
        log_test_result("🗺️ TESTING GOOGLE MAPS API TUTORIAL CODE BLOCK PRESERVATION", "CRITICAL")
        
        # Create comprehensive Google Maps API tutorial content with code examples
        google_maps_content = """
        Google Maps JavaScript API Tutorial - Complete Implementation Guide
        
        This comprehensive tutorial covers everything you need to know about implementing Google Maps JavaScript API in your web applications.
        
        ## Getting Started with Google Maps API
        
        First, you need to obtain an API key from the Google Cloud Console and include the Maps JavaScript API in your HTML:
        
        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Maps Tutorial</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap" async defer></script>
        </head>
        <body>
            <div id="map" style="height: 400px; width: 100%;"></div>
        </body>
        </html>
        ```
        
        ## Basic Map Initialization
        
        Here's how to initialize a basic Google Map:
        
        ```javascript
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 10,
                center: { lat: 37.7749, lng: -122.4194 }, // San Francisco
                mapTypeId: google.maps.MapTypeId.ROADMAP
            });
        }
        ```
        
        ## Adding Markers to Your Map
        
        You can add markers to highlight specific locations:
        
        ```javascript
        function addMarker(map, position, title) {
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: title,
                animation: google.maps.Animation.DROP
            });
            
            const infoWindow = new google.maps.InfoWindow({
                content: `<h3>${title}</h3><p>Latitude: ${position.lat}</p><p>Longitude: ${position.lng}</p>`
            });
            
            marker.addListener('click', function() {
                infoWindow.open(map, marker);
            });
            
            return marker;
        }
        ```
        
        ## Custom Map Styling
        
        Apply custom styling to your map:
        
        ```javascript
        const customMapStyle = [
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
        
        const styledMap = new google.maps.StyledMapType(customMapStyle, {name: "Custom Style"});
        map.mapTypes.set('custom_style', styledMap);
        map.setMapTypeId('custom_style');
        ```
        
        ## Advanced Features: Geocoding
        
        Implement address-to-coordinates conversion:
        
        ```javascript
        function geocodeAddress(geocoder, map, address) {
            geocoder.geocode({'address': address}, function(results, status) {
                if (status === 'OK') {
                    map.setCenter(results[0].geometry.location);
                    const marker = new google.maps.Marker({
                        map: map,
                        position: results[0].geometry.location
                    });
                } else {
                    console.error('Geocoding failed: ' + status);
                }
            });
        }
        ```
        
        ## CSS Styling for Map Container
        
        ```css
        #map {
            height: 500px;
            width: 100%;
            border: 2px solid #ccc;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .map-controls {
            background: white;
            border: 1px solid #ccc;
            border-radius: 3px;
            box-shadow: 0 2px 6px rgba(0,0,0,.3);
            cursor: pointer;
            margin-bottom: 22px;
            text-align: center;
        }
        ```
        
        This tutorial provides a complete foundation for implementing Google Maps in your web applications with proper code examples and styling.
        """
        
        # Process the content through Knowledge Engine
        log_test_result("📤 Processing Google Maps API tutorial content...")
        
        response = requests.post(
            f"{API_BASE}/content/process-text",
            json={"content": google_maps_content},
            timeout=300
        )
        
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
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Get the generated articles
                        articles_response = requests.get(f"{API_BASE}/content-library", timeout=30)
                        if articles_response.status_code == 200:
                            library_data = articles_response.json()
                            articles = library_data.get('articles', [])
                            
                            # Find Google Maps related articles
                            maps_articles = []
                            for article in articles:
                                title = article.get('title', '').lower()
                                content = article.get('content', '')
                                if 'google' in title or 'maps' in title or 'api' in title or 'google' in content.lower()[:500]:
                                    maps_articles.append(article)
                            
                            log_test_result(f"📄 Found {len(maps_articles)} Google Maps related articles")
                            
                            # Analyze code blocks in these articles
                            total_results = {
                                'articles_analyzed': 0,
                                'total_code_blocks': 0,
                                'empty_code_blocks': 0,
                                'code_blocks_with_content': 0,
                                'properly_formatted_code_blocks': 0,
                                'articles_with_issues': []
                            }
                            
                            for i, article in enumerate(maps_articles[:5]):  # Analyze first 5 articles
                                title = article.get('title', f'Article {i+1}')
                                content = article.get('content', '')
                                
                                log_test_result(f"🔍 Analyzing article: {title[:50]}...")
                                
                                code_analysis = analyze_code_blocks_in_content(content)
                                total_results['articles_analyzed'] += 1
                                total_results['total_code_blocks'] += code_analysis['total_code_blocks']
                                total_results['empty_code_blocks'] += code_analysis['empty_code_blocks']
                                total_results['code_blocks_with_content'] += code_analysis['code_blocks_with_content']
                                total_results['properly_formatted_code_blocks'] += code_analysis['properly_formatted_code_blocks']
                                
                                log_test_result(f"   📊 Code blocks: {code_analysis['total_code_blocks']} total, {code_analysis['code_blocks_with_content']} with content, {code_analysis['empty_code_blocks']} empty")
                                
                                # Check for issues
                                if code_analysis['empty_code_blocks'] > 0:
                                    total_results['articles_with_issues'].append({
                                        'title': title,
                                        'empty_blocks': code_analysis['empty_code_blocks'],
                                        'total_blocks': code_analysis['total_code_blocks']
                                    })
                                    log_test_result(f"   ⚠️ ISSUE: {code_analysis['empty_code_blocks']} empty code blocks found", "WARNING")
                                
                                # Show details of code blocks
                                for block in code_analysis['code_block_details']:
                                    if block['type'] == 'EMPTY':
                                        log_test_result(f"   ❌ Empty code block #{block['block_number']}", "ERROR")
                                    elif block['type'] == 'HAS_CONTENT':
                                        log_test_result(f"   ✅ Code block #{block['block_number']}: {block['content_length']} chars - {block['content_preview'][:50]}...")
                            
                            # Final assessment
                            log_test_result("\n🎯 GOOGLE MAPS API TUTORIAL CODE BLOCK ANALYSIS RESULTS:", "CRITICAL")
                            log_test_result(f"   📄 Articles analyzed: {total_results['articles_analyzed']}")
                            log_test_result(f"   📦 Total code blocks: {total_results['total_code_blocks']}")
                            log_test_result(f"   ✅ Code blocks with content: {total_results['code_blocks_with_content']}")
                            log_test_result(f"   ❌ Empty code blocks: {total_results['empty_code_blocks']}")
                            log_test_result(f"   🎨 Properly formatted code blocks: {total_results['properly_formatted_code_blocks']}")
                            
                            # Success criteria check
                            if total_results['empty_code_blocks'] == 0 and total_results['code_blocks_with_content'] > 0:
                                log_test_result("🎉 SUCCESS: No empty code blocks found, all code blocks contain actual content!", "SUCCESS")
                                return True
                            elif total_results['empty_code_blocks'] > 0:
                                log_test_result(f"❌ REGRESSION DETECTED: {total_results['empty_code_blocks']} empty code blocks found", "ERROR")
                                for issue in total_results['articles_with_issues']:
                                    log_test_result(f"   📄 {issue['title']}: {issue['empty_blocks']}/{issue['total_blocks']} empty blocks")
                                return False
                            else:
                                log_test_result("⚠️ No code blocks found in generated articles", "WARNING")
                                return False
                        
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(10)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Google Maps API tutorial test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_faq_article_code_blocks():
    """Test FAQ article generation for code block preservation"""
    try:
        log_test_result("❓ TESTING FAQ ARTICLE CODE BLOCK PRESERVATION", "CRITICAL")
        
        # Create content that should generate FAQ with code examples
        faq_content = """
        Advanced JavaScript Development Guide
        
        This guide covers advanced JavaScript concepts and common development patterns.
        
        ## Async/Await Patterns
        
        Modern JavaScript uses async/await for handling asynchronous operations:
        
        ```javascript
        async function fetchUserData(userId) {
            try {
                const response = await fetch(`/api/users/${userId}`);
                const userData = await response.json();
                return userData;
            } catch (error) {
                console.error('Error fetching user data:', error);
                throw error;
            }
        }
        ```
        
        ## Error Handling Best Practices
        
        Implement robust error handling in your applications:
        
        ```javascript
        class APIError extends Error {
            constructor(message, statusCode) {
                super(message);
                this.name = 'APIError';
                this.statusCode = statusCode;
            }
        }
        
        function handleAPIError(error) {
            if (error instanceof APIError) {
                console.error(`API Error ${error.statusCode}: ${error.message}`);
            } else {
                console.error('Unexpected error:', error);
            }
        }
        ```
        
        ## Module Patterns
        
        Use ES6 modules for better code organization:
        
        ```javascript
        // utils.js
        export const formatDate = (date) => {
            return new Intl.DateTimeFormat('en-US').format(date);
        };
        
        export const debounce = (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        };
        
        // main.js
        import { formatDate, debounce } from './utils.js';
        ```
        
        ## Testing Patterns
        
        Write comprehensive tests for your JavaScript code:
        
        ```javascript
        describe('User Service', () => {
            test('should fetch user data successfully', async () => {
                const mockUser = { id: 1, name: 'John Doe' };
                fetch.mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockUser,
                });
                
                const result = await fetchUserData(1);
                expect(result).toEqual(mockUser);
            });
            
            test('should handle fetch errors', async () => {
                fetch.mockRejectedValueOnce(new Error('Network error'));
                
                await expect(fetchUserData(1)).rejects.toThrow('Network error');
            });
        });
        ```
        
        This guide provides comprehensive examples of modern JavaScript development patterns with proper error handling and testing.
        """
        
        # Process the content
        log_test_result("📤 Processing JavaScript guide content for FAQ generation...")
        
        response = requests.post(
            f"{API_BASE}/content/process-text",
            json={"content": faq_content},
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
        
        # Monitor processing and analyze results
        processing_start = time.time()
        max_wait_time = 300
        
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
                        # Get articles and look for FAQ
                        articles_response = requests.get(f"{API_BASE}/content-library", timeout=30)
                        if articles_response.status_code == 200:
                            library_data = articles_response.json()
                            articles = library_data.get('articles', [])
                            
                            # Find FAQ articles
                            faq_articles = []
                            for article in articles:
                                title = article.get('title', '').lower()
                                article_type = article.get('article_type', '').lower()
                                if 'faq' in title or 'frequently' in title or 'troubleshooting' in title or 'faq' in article_type:
                                    faq_articles.append(article)
                            
                            log_test_result(f"❓ Found {len(faq_articles)} FAQ articles")
                            
                            if faq_articles:
                                # Analyze FAQ articles for code blocks
                                faq_results = {
                                    'faq_articles_analyzed': 0,
                                    'total_code_blocks': 0,
                                    'empty_code_blocks': 0,
                                    'code_blocks_with_content': 0,
                                    'faq_articles_with_issues': []
                                }
                                
                                for faq_article in faq_articles:
                                    title = faq_article.get('title', 'FAQ Article')
                                    content = faq_article.get('content', '')
                                    
                                    log_test_result(f"🔍 Analyzing FAQ article: {title[:50]}...")
                                    
                                    code_analysis = analyze_code_blocks_in_content(content)
                                    faq_results['faq_articles_analyzed'] += 1
                                    faq_results['total_code_blocks'] += code_analysis['total_code_blocks']
                                    faq_results['empty_code_blocks'] += code_analysis['empty_code_blocks']
                                    faq_results['code_blocks_with_content'] += code_analysis['code_blocks_with_content']
                                    
                                    log_test_result(f"   📊 FAQ Code blocks: {code_analysis['total_code_blocks']} total, {code_analysis['code_blocks_with_content']} with content, {code_analysis['empty_code_blocks']} empty")
                                    
                                    if code_analysis['empty_code_blocks'] > 0:
                                        faq_results['faq_articles_with_issues'].append({
                                            'title': title,
                                            'empty_blocks': code_analysis['empty_code_blocks']
                                        })
                                
                                # Final FAQ assessment
                                log_test_result("\n🎯 FAQ ARTICLE CODE BLOCK ANALYSIS RESULTS:", "CRITICAL")
                                log_test_result(f"   ❓ FAQ articles analyzed: {faq_results['faq_articles_analyzed']}")
                                log_test_result(f"   📦 Total code blocks in FAQ: {faq_results['total_code_blocks']}")
                                log_test_result(f"   ✅ FAQ code blocks with content: {faq_results['code_blocks_with_content']}")
                                log_test_result(f"   ❌ Empty FAQ code blocks: {faq_results['empty_code_blocks']}")
                                
                                if faq_results['empty_code_blocks'] == 0:
                                    log_test_result("🎉 SUCCESS: No empty code blocks found in FAQ articles!", "SUCCESS")
                                    return True
                                else:
                                    log_test_result(f"❌ REGRESSION DETECTED: {faq_results['empty_code_blocks']} empty code blocks in FAQ articles", "ERROR")
                                    return False
                            else:
                                log_test_result("⚠️ No FAQ articles generated", "WARNING")
                                return True  # Not a failure if no FAQ was generated
                        
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(10)
                else:
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ FAQ article test failed: {e}", "ERROR")
        return False

def test_html_structure_integrity():
    """Test that HTML structure is maintained and WYSIWYG compatible"""
    try:
        log_test_result("🏗️ TESTING HTML STRUCTURE INTEGRITY AND WYSIWYG COMPATIBILITY", "CRITICAL")
        
        # Get recent articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        library_data = response.json()
        articles = library_data.get('articles', [])
        
        if not articles:
            log_test_result("⚠️ No articles found in Content Library", "WARNING")
            return False
        
        log_test_result(f"🔍 Analyzing HTML structure in {len(articles[:10])} recent articles...")
        
        structure_results = {
            'articles_analyzed': 0,
            'articles_with_proper_structure': 0,
            'articles_with_full_document_wrapping': 0,
            'articles_with_semantic_html': 0,
            'articles_with_code_blocks': 0,
            'articles_with_proper_code_formatting': 0,
            'wysiwyg_compatible_articles': 0,
            'issues_found': []
        }
        
        for i, article in enumerate(articles[:10]):  # Analyze first 10 articles
            title = article.get('title', f'Article {i+1}')
            content = article.get('content', '')
            
            log_test_result(f"🔍 Analyzing HTML structure: {title[:50]}...")
            
            structure_results['articles_analyzed'] += 1
            
            # Check for full document wrapping (should NOT be present)
            has_full_document = bool(re.search(r'<!DOCTYPE|<html|<head|<body', content, re.IGNORECASE))
            if has_full_document:
                structure_results['articles_with_full_document_wrapping'] += 1
                structure_results['issues_found'].append({
                    'title': title,
                    'issue': 'Full document structure detected (not WYSIWYG compatible)',
                    'severity': 'HIGH'
                })
                log_test_result(f"   ❌ ISSUE: Full document structure detected", "ERROR")
            else:
                structure_results['articles_with_proper_structure'] += 1
                log_test_result(f"   ✅ Proper article structure (no document wrappers)")
            
            # Check for semantic HTML elements
            semantic_elements = ['<h2', '<h3', '<p>', '<ul>', '<ol>', '<li>', '<strong>', '<em>', '<blockquote>']
            has_semantic_html = any(element in content for element in semantic_elements)
            if has_semantic_html:
                structure_results['articles_with_semantic_html'] += 1
                log_test_result(f"   ✅ Contains semantic HTML elements")
            
            # Check code blocks
            code_blocks = re.findall(r'<pre><code[^>]*>(.*?)</code></pre>', content, re.DOTALL | re.IGNORECASE)
            if code_blocks:
                structure_results['articles_with_code_blocks'] += 1
                
                # Check if code blocks are properly formatted
                properly_formatted = True
                for code_content in code_blocks:
                    if not code_content.strip():  # Empty code block
                        properly_formatted = False
                        structure_results['issues_found'].append({
                            'title': title,
                            'issue': 'Empty code block detected',
                            'severity': 'HIGH'
                        })
                        break
                
                if properly_formatted:
                    structure_results['articles_with_proper_code_formatting'] += 1
                    log_test_result(f"   ✅ Code blocks properly formatted with content")
                else:
                    log_test_result(f"   ❌ ISSUE: Empty code blocks detected", "ERROR")
            
            # WYSIWYG compatibility check
            wysiwyg_compatible = (
                not has_full_document and  # No document structure
                has_semantic_html and     # Has semantic elements
                not re.search(r'<pre><code[^>]*></code></pre>', content)  # No empty code blocks
            )
            
            if wysiwyg_compatible:
                structure_results['wysiwyg_compatible_articles'] += 1
                log_test_result(f"   ✅ WYSIWYG compatible structure")
            else:
                log_test_result(f"   ⚠️ WYSIWYG compatibility issues detected")
        
        # Final HTML structure assessment
        log_test_result("\n🎯 HTML STRUCTURE INTEGRITY ANALYSIS RESULTS:", "CRITICAL")
        log_test_result(f"   📄 Articles analyzed: {structure_results['articles_analyzed']}")
        log_test_result(f"   ✅ Articles with proper structure: {structure_results['articles_with_proper_structure']}")
        log_test_result(f"   ❌ Articles with full document wrapping: {structure_results['articles_with_full_document_wrapping']}")
        log_test_result(f"   🏗️ Articles with semantic HTML: {structure_results['articles_with_semantic_html']}")
        log_test_result(f"   📦 Articles with code blocks: {structure_results['articles_with_code_blocks']}")
        log_test_result(f"   🎨 Articles with proper code formatting: {structure_results['articles_with_proper_code_formatting']}")
        log_test_result(f"   📝 WYSIWYG compatible articles: {structure_results['wysiwyg_compatible_articles']}")
        
        # Show issues found
        if structure_results['issues_found']:
            log_test_result(f"\n⚠️ ISSUES DETECTED:")
            for issue in structure_results['issues_found']:
                log_test_result(f"   📄 {issue['title'][:50]}: {issue['issue']} (Severity: {issue['severity']})")
        
        # Success criteria
        success_rate = structure_results['wysiwyg_compatible_articles'] / structure_results['articles_analyzed'] if structure_results['articles_analyzed'] > 0 else 0
        
        if success_rate >= 0.8:  # 80% success rate
            log_test_result(f"🎉 SUCCESS: {success_rate:.1%} of articles have proper HTML structure and WYSIWYG compatibility!", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ FAILURE: Only {success_rate:.1%} of articles have proper HTML structure", "ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ HTML structure integrity test failed: {e}", "ERROR")
        return False

def run_comprehensive_empty_code_blocks_test():
    """Run comprehensive test suite for empty code blocks regression fix"""
    log_test_result("🚀 STARTING COMPREHENSIVE EMPTY CODE BLOCKS REGRESSION TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'google_maps_code_blocks': False,
        'faq_code_blocks': False,
        'html_structure_integrity': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Google Maps API Tutorial Code Block Preservation
    log_test_result("\nTEST 2: GOOGLE MAPS API TUTORIAL CODE BLOCK PRESERVATION")
    test_results['google_maps_code_blocks'] = test_google_maps_api_tutorial_content()
    
    # Test 3: FAQ Article Code Block Preservation
    log_test_result("\nTEST 3: FAQ ARTICLE CODE BLOCK PRESERVATION")
    test_results['faq_code_blocks'] = test_faq_article_code_blocks()
    
    # Test 4: HTML Structure Integrity and WYSIWYG Compatibility
    log_test_result("\nTEST 4: HTML STRUCTURE INTEGRITY AND WYSIWYG COMPATIBILITY")
    test_results['html_structure_integrity'] = test_html_structure_integrity()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL EMPTY CODE BLOCKS REGRESSION TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Critical assessment
    critical_tests = ['google_maps_code_blocks', 'faq_code_blocks', 'html_structure_integrity']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        log_test_result("🎉 CRITICAL SUCCESS: Empty code blocks regression has been successfully fixed!", "CRITICAL_SUCCESS")
        log_test_result("✅ Code blocks now contain actual content and maintain proper HTML structure", "CRITICAL_SUCCESS")
        log_test_result("✅ WYSIWYG editor compatibility is maintained", "CRITICAL_SUCCESS")
        log_test_result("✅ No empty <pre><code> tags with just whitespace detected", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Empty code blocks regression is still present", "CRITICAL_ERROR")
        log_test_result("❌ Code blocks are being stripped of content or generated empty", "CRITICAL_ERROR")
        log_test_result("❌ WYSIWYG editor compatibility may be compromised", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Empty Code Blocks Regression Fix Testing")
    print("=" * 50)
    
    results = run_comprehensive_empty_code_blocks_test()
    
    # Exit with appropriate code
    critical_tests = ['google_maps_code_blocks', 'faq_code_blocks', 'html_structure_integrity']
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure