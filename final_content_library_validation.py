#!/usr/bin/env python3
"""
FINAL CONTENT LIBRARY ISSUES FIX VALIDATION
Testing the comprehensive fixes for ALL specific Content Library issues reported by the user
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
import re

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
        response = requests.get(f"{API_BASE}/health", timeout=10)
        
        if response.status_code == 200:
            log_test_result("✅ Backend health check PASSED", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ Backend health check FAILED: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend health check FAILED: {e}", "ERROR")
        return False

def process_real_content_for_testing():
    """Process real content to generate articles for comprehensive validation"""
    try:
        log_test_result("🎯 PROCESSING REAL CONTENT FOR COMPREHENSIVE VALIDATION", "CRITICAL")
        
        # Create comprehensive test content that will trigger all the quality fixes
        test_content = """
        Google Maps JavaScript API Complete Tutorial
        
        Introduction and Overview
        The Google Maps JavaScript API provides powerful mapping capabilities for web applications. This comprehensive guide covers everything from basic setup to advanced customization techniques.
        
        Getting Started with Google Maps API
        First, you need to obtain an API key from Google Cloud Console. First, you need to obtain an API key from Google Cloud Console. This step is essential for accessing all Google Maps services.
        
        Step-by-Step Setup Process
        1. Create a new project in Google Cloud Console
        2. Enable the Maps JavaScript API for your project
        3. Generate your API key with proper restrictions
        4. Configure billing and usage limits
        5. Test your API key with a simple implementation
        
        Basic Map Implementation
        Here's how to create your first interactive map:
        
        ```javascript
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 10,
                center: { lat: 37.7749, lng: -122.4194 },
                mapTypeId: 'roadmap'
            });
        }
        
        // Initialize the map when the page loads
        window.onload = initMap;
        ```
        
        Adding Markers and Info Windows
        Markers help highlight important locations on your map:
        
        ```javascript
        const marker = new google.maps.Marker({
            position: { lat: 37.7749, lng: -122.4194 },
            map: map,
            title: "San Francisco",
            animation: google.maps.Animation.DROP
        });
        
        const infoWindow = new google.maps.InfoWindow({
            content: "<h3>San Francisco</h3><p>Beautiful city by the bay</p>"
        });
        
        marker.addListener('click', function() {
            infoWindow.open(map, marker);
        });
        ```
        
        Advanced Customization Features
        The Google Maps API offers extensive customization options for creating unique map experiences.
        
        Custom Map Styling
        You can completely customize the appearance of your maps:
        
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
        
        Geocoding and Reverse Geocoding
        Convert between addresses and coordinates:
        
        ```javascript
        const geocoder = new google.maps.Geocoder();
        
        function geocodeAddress(address) {
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
        
        Performance Optimization Best Practices
        When working with Google Maps API, follow these optimization guidelines:
        
        1. Use marker clustering for large datasets
        2. Implement lazy loading for better page performance
        3. Optimize API calls with proper caching strategies
        4. Use appropriate zoom levels for your use case
        5. Handle API errors gracefully with fallback options
        
        Common Issues and Troubleshooting
        Here are solutions to frequently encountered problems:
        
        API Key Issues
        If your map isn't loading, check your API key configuration and ensure the Maps JavaScript API is enabled for your project.
        
        Performance Problems
        Large numbers of markers can slow down your map. Consider using marker clustering or pagination to improve performance.
        
        Mobile Responsiveness
        Ensure your maps work well on mobile devices by implementing responsive design principles and touch-friendly controls.
        """
        
        log_test_result(f"📝 Test content prepared: {len(test_content)} characters")
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing content through Knowledge Engine...")
        
        payload = {
            "content": test_content,
            "filename": "google_maps_comprehensive_tutorial.txt"
        }
        
        response = requests.post(f"{API_BASE}/content/process-text", 
                               json=payload, 
                               timeout=120)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            return None
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return None
        
        log_test_result(f"✅ Processing started, Job ID: {job_id}")
        
        # Monitor processing with shorter timeout
        max_wait_time = 120  # 2 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        articles_generated = status_data.get('articles_generated', 0)
                        log_test_result(f"✅ Processing completed: {articles_generated} articles generated", "SUCCESS")
                        return {'job_id': job_id, 'articles_generated': articles_generated}
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return None
                
                time.sleep(5)
                
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
        
        log_test_result("❌ Processing timeout", "ERROR")
        return None
    
    except Exception as e:
        log_test_result(f"❌ Content processing failed: {e}", "ERROR")
        return None

def validate_content_library_fixes():
    """Comprehensive validation of all Content Library fixes"""
    try:
        log_test_result("🔍 COMPREHENSIVE CONTENT LIBRARY FIXES VALIDATION", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=15)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📚 Analyzing {len(articles)} articles from Content Library (Total: {total_articles})")
        
        if len(articles) == 0:
            log_test_result("❌ No articles found for validation", "ERROR")
            return False
        
        # Initialize validation results
        validation_results = {
            'text_deduplication': {'passed': 0, 'failed': 0, 'issues': []},
            'overview_vs_complete_guide': {'passed': 0, 'failed': 0, 'issues': []},
            'ordered_lists_quality': {'passed': 0, 'failed': 0, 'issues': []},
            'wysiwyg_features': {'found': 0, 'types': set()},
            'faq_standardization': {'passed': 0, 'failed': 0, 'issues': []},
            'code_block_quality': {'total': 0, 'empty': 0, 'working': 0},
            'database_integration': {'complete_metadata': 0, 'missing_fields': 0}
        }
        
        # Analyze each article
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            article_type = article.get('article_type', 'unknown')
            
            # 1. TEXT DEDUPLICATION VALIDATION
            soup = BeautifulSoup(content, 'html.parser')
            text_elements = soup.find_all(['p', 'li'])
            
            for element in text_elements:
                text = element.get_text().strip()
                if text:
                    # Check for sentence duplication pattern
                    sentences = re.split(r'[.!?]+', text)
                    for i in range(len(sentences) - 1):
                        sentence1 = sentences[i].strip()
                        sentence2 = sentences[i + 1].strip()
                        
                        if sentence1 and sentence2 and sentence1 == sentence2:
                            validation_results['text_deduplication']['failed'] += 1
                            validation_results['text_deduplication']['issues'].append({
                                'article': title[:50],
                                'duplicate': sentence1[:100]
                            })
                        else:
                            validation_results['text_deduplication']['passed'] += 1
            
            # 2. OVERVIEW VS COMPLETE GUIDE SEPARATION
            if 'overview' in title.lower() or article_type == 'overview':
                # Overview should be concise (max 2000 chars) and not have detailed procedures
                if len(content) > 2000:
                    validation_results['overview_vs_complete_guide']['failed'] += 1
                    validation_results['overview_vs_complete_guide']['issues'].append({
                        'article': title[:50],
                        'issue': f'Overview too long: {len(content)} chars'
                    })
                elif re.search(r'step\s+\d+|step-by-step|detailed implementation', content.lower()):
                    validation_results['overview_vs_complete_guide']['failed'] += 1
                    validation_results['overview_vs_complete_guide']['issues'].append({
                        'article': title[:50],
                        'issue': 'Overview contains detailed procedures'
                    })
                else:
                    validation_results['overview_vs_complete_guide']['passed'] += 1
            
            elif 'complete' in title.lower() or 'guide' in title.lower() or article_type in ['how-to', 'tutorial']:
                # Complete guides should be comprehensive (min 3000 chars)
                if len(content) < 3000:
                    validation_results['overview_vs_complete_guide']['failed'] += 1
                    validation_results['overview_vs_complete_guide']['issues'].append({
                        'article': title[:50],
                        'issue': f'Complete guide too short: {len(content)} chars'
                    })
                else:
                    validation_results['overview_vs_complete_guide']['passed'] += 1
            
            # 3. ORDERED LISTS QUALITY
            ordered_lists = soup.find_all('ol')
            for ol in ordered_lists:
                list_items = ol.find_all('li', recursive=False)
                
                if len(list_items) == 1:
                    # Single item lists indicate fragmentation
                    validation_results['ordered_lists_quality']['failed'] += 1
                    validation_results['ordered_lists_quality']['issues'].append({
                        'article': title[:50],
                        'issue': 'Fragmented list (single item)'
                    })
                else:
                    validation_results['ordered_lists_quality']['passed'] += 1
            
            # 4. WYSIWYG EDITOR FEATURES
            # Check for Mini-TOC
            if soup.find_all(['div', 'ul'], class_=re.compile(r'toc|table-of-contents')):
                validation_results['wysiwyg_features']['found'] += 1
                validation_results['wysiwyg_features']['types'].add('mini_toc')
            
            # Check for callout boxes
            if soup.find_all('div', class_=re.compile(r'callout')):
                validation_results['wysiwyg_features']['found'] += 1
                validation_results['wysiwyg_features']['types'].add('callouts')
            
            # Check for anchor links
            if soup.find_all('a', href=re.compile(r'^#')):
                validation_results['wysiwyg_features']['found'] += 1
                validation_results['wysiwyg_features']['types'].add('anchor_links')
            
            # 5. FAQ STANDARDIZATION
            if 'faq' in title.lower() or article_type == 'faq':
                if not re.search(r'frequently asked questions.*troubleshooting', title.lower()):
                    validation_results['faq_standardization']['failed'] += 1
                    validation_results['faq_standardization']['issues'].append({
                        'article': title[:50],
                        'issue': 'Non-standard FAQ title'
                    })
                elif '##' in content or '###' in content:
                    validation_results['faq_standardization']['failed'] += 1
                    validation_results['faq_standardization']['issues'].append({
                        'article': title[:50],
                        'issue': 'Contains Markdown formatting'
                    })
                else:
                    validation_results['faq_standardization']['passed'] += 1
            
            # 6. CODE BLOCK QUALITY
            code_blocks = soup.find_all(['pre', 'code'])
            for block in code_blocks:
                validation_results['code_block_quality']['total'] += 1
                code_text = block.get_text().strip()
                
                if not code_text:
                    validation_results['code_block_quality']['empty'] += 1
                else:
                    validation_results['code_block_quality']['working'] += 1
            
            # 7. DATABASE INTEGRATION
            required_fields = ['id', 'title', 'content', 'status', 'created_at']
            if all(field in article and article[field] for field in required_fields):
                validation_results['database_integration']['complete_metadata'] += 1
            else:
                validation_results['database_integration']['missing_fields'] += 1
        
        # Generate comprehensive results
        log_test_result("\n" + "=" * 80)
        log_test_result("🎯 COMPREHENSIVE VALIDATION RESULTS", "CRITICAL")
        log_test_result("=" * 80)
        
        # 1. Text Deduplication Results
        dedup_total = validation_results['text_deduplication']['passed'] + validation_results['text_deduplication']['failed']
        dedup_success_rate = (validation_results['text_deduplication']['passed'] / max(1, dedup_total)) * 100
        
        log_test_result(f"1. TEXT DEDUPLICATION: {dedup_success_rate:.1f}% success rate")
        log_test_result(f"   ✅ Clean text elements: {validation_results['text_deduplication']['passed']}")
        log_test_result(f"   ❌ Duplicated text found: {validation_results['text_deduplication']['failed']}")
        
        if validation_results['text_deduplication']['failed'] == 0:
            log_test_result("   🎉 TEXT DEDUPLICATION FIX WORKING PERFECTLY", "SUCCESS")
        
        # 2. Overview vs Complete Guide Results
        separation_total = validation_results['overview_vs_complete_guide']['passed'] + validation_results['overview_vs_complete_guide']['failed']
        if separation_total > 0:
            separation_success_rate = (validation_results['overview_vs_complete_guide']['passed'] / separation_total) * 100
            log_test_result(f"2. CONTENT SEPARATION: {separation_success_rate:.1f}% success rate")
            log_test_result(f"   ✅ Properly separated articles: {validation_results['overview_vs_complete_guide']['passed']}")
            log_test_result(f"   ❌ Separation issues: {validation_results['overview_vs_complete_guide']['failed']}")
        
        # 3. Ordered Lists Results
        lists_total = validation_results['ordered_lists_quality']['passed'] + validation_results['ordered_lists_quality']['failed']
        if lists_total > 0:
            lists_success_rate = (validation_results['ordered_lists_quality']['passed'] / lists_total) * 100
            log_test_result(f"3. ORDERED LISTS QUALITY: {lists_success_rate:.1f}% success rate")
            log_test_result(f"   ✅ Proper continuous lists: {validation_results['ordered_lists_quality']['passed']}")
            log_test_result(f"   ❌ Fragmented lists: {validation_results['ordered_lists_quality']['failed']}")
        
        # 4. WYSIWYG Features Results
        log_test_result(f"4. WYSIWYG FEATURES: {validation_results['wysiwyg_features']['found']} features found")
        log_test_result(f"   Feature types: {', '.join(validation_results['wysiwyg_features']['types'])}")
        
        # 5. FAQ Standardization Results
        faq_total = validation_results['faq_standardization']['passed'] + validation_results['faq_standardization']['failed']
        if faq_total > 0:
            faq_success_rate = (validation_results['faq_standardization']['passed'] / faq_total) * 100
            log_test_result(f"5. FAQ STANDARDIZATION: {faq_success_rate:.1f}% success rate")
        
        # 6. Code Block Quality Results
        code_total = validation_results['code_block_quality']['total']
        if code_total > 0:
            code_success_rate = (validation_results['code_block_quality']['working'] / code_total) * 100
            log_test_result(f"6. CODE BLOCK QUALITY: {code_success_rate:.1f}% success rate")
            log_test_result(f"   ✅ Working code blocks: {validation_results['code_block_quality']['working']}")
            log_test_result(f"   ❌ Empty code blocks: {validation_results['code_block_quality']['empty']}")
            
            if validation_results['code_block_quality']['empty'] == 0:
                log_test_result("   🎉 CODE BLOCK QUALITY FIX WORKING PERFECTLY", "SUCCESS")
        
        # 7. Database Integration Results
        db_total = validation_results['database_integration']['complete_metadata'] + validation_results['database_integration']['missing_fields']
        db_success_rate = (validation_results['database_integration']['complete_metadata'] / max(1, db_total)) * 100
        log_test_result(f"7. DATABASE INTEGRATION: {db_success_rate:.1f}% success rate")
        
        # Overall Assessment
        log_test_result("\n" + "=" * 80)
        log_test_result("🏆 OVERALL ASSESSMENT", "CRITICAL")
        log_test_result("=" * 80)
        
        critical_fixes_working = (
            validation_results['text_deduplication']['failed'] == 0 and
            validation_results['code_block_quality']['empty'] == 0 and
            validation_results['ordered_lists_quality']['failed'] <= validation_results['ordered_lists_quality']['passed']
        )
        
        if critical_fixes_working:
            log_test_result("🎉 CRITICAL SUCCESS: All major Content Library fixes are working!", "CRITICAL_SUCCESS")
            log_test_result("✅ Text deduplication eliminated", "SUCCESS")
            log_test_result("✅ Code blocks contain working content", "SUCCESS")
            log_test_result("✅ Ordered lists properly formatted", "SUCCESS")
            return True
        else:
            log_test_result("❌ CRITICAL ISSUES REMAIN: Some fixes need attention", "CRITICAL_ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Validation failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_final_validation():
    """Run the final comprehensive validation"""
    log_test_result("🚀 FINAL CONTENT LIBRARY ISSUES FIX VALIDATION", "CRITICAL")
    log_test_result("=" * 80)
    
    # Test 1: Backend Health
    if not test_backend_health():
        log_test_result("❌ Backend not available - aborting tests", "CRITICAL_ERROR")
        return False
    
    # Test 2: Process real content for testing
    log_test_result("\nProcessing real content for comprehensive validation...")
    processing_result = process_real_content_for_testing()
    
    if processing_result:
        log_test_result(f"✅ Content processing successful: {processing_result['articles_generated']} articles generated", "SUCCESS")
    else:
        log_test_result("⚠️ Content processing failed - validating existing articles", "WARNING")
    
    # Test 3: Comprehensive validation
    log_test_result("\nRunning comprehensive Content Library fixes validation...")
    validation_success = validate_content_library_fixes()
    
    return validation_success

if __name__ == "__main__":
    print("Final Content Library Issues Fix Validation")
    print("=" * 50)
    
    success = run_final_validation()
    
    if success:
        print("\n🎉 VALIDATION COMPLETE: Content Library fixes are working!")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED: Content Library issues remain")
        sys.exit(1)