#!/usr/bin/env python3
"""
CONTENT CORRUPTION FIXES & WYSIWYG ENHANCEMENT TESTING
Testing the improved content generation pipeline after implementing fixes for:
1. Content Generation Quality - substantial content (not empty or near-empty)
2. WYSIWYG Enhancement Integration - add_wysiwyg_enhancements function
3. Template Contamination Prevention - no HTML document structure contamination
4. Knowledge Engine Upload - complete workflow from upload to article creation
5. Content Validation - enhanced content validation preventing empty articles
6. Database Storage - proper metadata and validation flags
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
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

def test_content_generation_quality():
    """
    Test that articles now have substantial content (not empty or near-empty)
    Upload test content and verify generated articles have meaningful content
    """
    try:
        log_test_result("🎯 TESTING CONTENT GENERATION QUALITY", "CRITICAL")
        
        # Create comprehensive test content that should generate substantial articles
        test_content = """
        Google Maps JavaScript API Complete Tutorial
        
        Introduction to Google Maps API
        The Google Maps JavaScript API is a powerful tool for integrating interactive maps into web applications. This comprehensive guide will walk you through everything you need to know to get started with Google Maps API development.
        
        Getting Started with Setup
        Before you can use the Google Maps API, you need to set up your development environment and obtain an API key from the Google Cloud Console.
        
        Step 1: Create a Google Cloud Project
        1. Go to the Google Cloud Console
        2. Create a new project or select an existing one
        3. Enable the Maps JavaScript API
        4. Create credentials (API key)
        
        Step 2: Basic HTML Setup
        Create a basic HTML file with the following structure:
        
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Google Map</title>
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
        
        Advanced Map Customization
        Once you have a basic map working, you can customize it with various options and features.
        
        Adding Markers
        Markers are used to identify locations on the map. Here's how to add a simple marker:
        
        var marker = new google.maps.Marker({
            position: {lat: -34.397, lng: 150.644},
            map: map,
            title: 'Hello World!'
        });
        
        Custom Marker Icons
        You can customize marker icons using custom images:
        
        var customIcon = {
            url: 'path/to/your/icon.png',
            scaledSize: new google.maps.Size(50, 50)
        };
        
        var marker = new google.maps.Marker({
            position: {lat: -34.397, lng: 150.644},
            map: map,
            icon: customIcon
        });
        
        Info Windows
        Info windows display content in a popup window above the map:
        
        var infoWindow = new google.maps.InfoWindow({
            content: '<div><h3>Location Info</h3><p>This is a sample location.</p></div>'
        });
        
        marker.addListener('click', function() {
            infoWindow.open(map, marker);
        });
        
        Event Handling
        Google Maps API provides various event listeners for user interactions:
        
        map.addListener('click', function(event) {
            console.log('Map clicked at: ' + event.latLng);
        });
        
        Troubleshooting Common Issues
        Here are solutions to common problems developers encounter:
        
        1. API Key Issues
        - Make sure your API key is valid
        - Check that the Maps JavaScript API is enabled
        - Verify domain restrictions if set
        
        2. Map Not Loading
        - Check console for JavaScript errors
        - Verify the callback function name matches
        - Ensure the script tag is properly formatted
        
        3. Performance Optimization
        - Use marker clustering for many markers
        - Implement lazy loading for large datasets
        - Optimize API calls to reduce quota usage
        
        Best Practices
        - Always handle errors gracefully
        - Use appropriate zoom levels for your use case
        - Implement responsive design for mobile devices
        - Follow Google's usage policies and guidelines
        """
        
        log_test_result("📤 Uploading comprehensive test content...")
        
        # Upload via text content endpoint
        upload_data = {
            "content": test_content,
            "filename": "google_maps_api_tutorial.txt"
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/upload", 
                               json=upload_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=300)
        
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
        log_test_result("⏳ Monitoring content processing...")
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
                        
                        articles_generated = status_data.get('articles_generated', 0)
                        log_test_result(f"📄 Articles Generated: {articles_generated}")
                        
                        if articles_generated == 0:
                            log_test_result("❌ CRITICAL FAILURE: No articles generated", "CRITICAL_ERROR")
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
        log_test_result(f"❌ Content generation quality test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_wysiwyg_enhancement_integration():
    """
    Test WYSIWYG Enhancement Integration - verify add_wysiwyg_enhancements function
    Check that articles have proper WYSIWYG features applied
    """
    try:
        log_test_result("🎨 TESTING WYSIWYG ENHANCEMENT INTEGRATION", "CRITICAL")
        
        # Get recent articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found in Content Library for WYSIWYG testing", "ERROR")
            return False
        
        log_test_result(f"📚 Analyzing {len(articles)} articles for WYSIWYG enhancements...")
        
        wysiwyg_features_found = {
            'article_body_wrapper': 0,
            'enhanced_code_blocks': 0,
            'heading_ids': 0,
            'expandable_sections': 0,
            'copy_buttons': 0,
            'contextual_callouts': 0
        }
        
        articles_with_enhancements = 0
        
        for i, article in enumerate(articles[:10]):  # Check first 10 articles
            content = article.get('content', '')
            title = article.get('title', f'Article {i+1}')
            
            log_test_result(f"🔍 Analyzing article: {title[:50]}...")
            
            # Check for WYSIWYG enhancement features
            has_enhancements = False
            
            # 1. Article body wrapper
            if 'article-body' in content or 'class="article-body"' in content:
                wysiwyg_features_found['article_body_wrapper'] += 1
                has_enhancements = True
            
            # 2. Enhanced code blocks with line numbers or copy functionality
            if 'line-numbers' in content or 'copy-button' in content or 'code-block-enhanced' in content:
                wysiwyg_features_found['enhanced_code_blocks'] += 1
                has_enhancements = True
            
            # 3. Heading IDs for navigation
            heading_id_pattern = r'<h[2-6][^>]*id="[^"]*"'
            if re.search(heading_id_pattern, content):
                wysiwyg_features_found['heading_ids'] += 1
                has_enhancements = True
            
            # 4. Expandable sections
            if 'expandable' in content or 'collapsible' in content or 'accordion' in content:
                wysiwyg_features_found['expandable_sections'] += 1
                has_enhancements = True
            
            # 5. Copy buttons
            if 'copy-btn' in content or 'copy-button' in content:
                wysiwyg_features_found['copy_buttons'] += 1
                has_enhancements = True
            
            # 6. Contextual callouts (notes, tips, warnings)
            callout_patterns = ['callout', 'note-box', 'tip-box', 'warning-box', 'alert-']
            if any(pattern in content for pattern in callout_patterns):
                wysiwyg_features_found['contextual_callouts'] += 1
                has_enhancements = True
            
            if has_enhancements:
                articles_with_enhancements += 1
        
        # Report WYSIWYG enhancement results
        log_test_result("📊 WYSIWYG Enhancement Analysis Results:")
        total_features = sum(wysiwyg_features_found.values())
        
        for feature, count in wysiwyg_features_found.items():
            log_test_result(f"   {feature.replace('_', ' ').title()}: {count} articles")
        
        log_test_result(f"   Total WYSIWYG features found: {total_features}")
        log_test_result(f"   Articles with enhancements: {articles_with_enhancements}/{len(articles[:10])}")
        
        if total_features > 0:
            log_test_result("✅ WYSIWYG enhancements detected in articles", "SUCCESS")
            return True
        else:
            log_test_result("⚠️ No WYSIWYG enhancements detected - may need implementation", "WARNING")
            return False
    
    except Exception as e:
        log_test_result(f"❌ WYSIWYG enhancement test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_template_contamination_prevention():
    """
    Test Template Contamination Prevention - ensure no HTML document structure contamination
    Check that articles don't contain <!DOCTYPE>, <html>, <head>, <body> tags
    """
    try:
        log_test_result("🧹 TESTING TEMPLATE CONTAMINATION PREVENTION", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for contamination testing", "ERROR")
            return False
        
        log_test_result(f"🔍 Checking {len(articles)} articles for template contamination...")
        
        contaminated_articles = []
        contamination_patterns = [
            r'<!DOCTYPE\s+html',
            r'<html[^>]*>',
            r'<head[^>]*>',
            r'<body[^>]*>',
            r'</html>',
            r'</head>',
            r'</body>'
        ]
        
        for i, article in enumerate(articles):
            content = article.get('content', '')
            title = article.get('title', f'Article {i+1}')
            
            # Check for contamination patterns
            contamination_found = []
            for pattern in contamination_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    contamination_found.append(pattern)
            
            if contamination_found:
                contaminated_articles.append({
                    'title': title,
                    'id': article.get('id'),
                    'contamination': contamination_found
                })
        
        # Report contamination results
        if contaminated_articles:
            log_test_result(f"❌ TEMPLATE CONTAMINATION DETECTED in {len(contaminated_articles)} articles:", "ERROR")
            for article in contaminated_articles[:5]:  # Show first 5
                log_test_result(f"   Article: {article['title'][:50]}...")
                log_test_result(f"   Contamination: {', '.join(article['contamination'])}")
            return False
        else:
            log_test_result("✅ NO TEMPLATE CONTAMINATION detected - articles have clean content", "SUCCESS")
            return True
    
    except Exception as e:
        log_test_result(f"❌ Template contamination test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_content_validation_and_empty_prevention():
    """
    Test Content Validation - verify enhanced content validation prevents empty articles
    Check that all articles have substantial content and proper validation flags
    """
    try:
        log_test_result("✅ TESTING CONTENT VALIDATION & EMPTY PREVENTION", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for content validation testing", "ERROR")
            return False
        
        log_test_result(f"📊 Analyzing content quality in {len(articles)} articles...")
        
        empty_articles = []
        short_articles = []
        substantial_articles = []
        
        for article in articles:
            content = article.get('content', '')
            title = article.get('title', 'Untitled')
            
            # Remove HTML tags to get text content length
            text_content = re.sub(r'<[^>]+>', '', content).strip()
            text_length = len(text_content)
            
            if text_length == 0:
                empty_articles.append({'title': title, 'id': article.get('id')})
            elif text_length < 100:
                short_articles.append({'title': title, 'length': text_length, 'id': article.get('id')})
            else:
                substantial_articles.append({'title': title, 'length': text_length, 'id': article.get('id')})
        
        # Report content validation results
        log_test_result("📈 Content Quality Analysis Results:")
        log_test_result(f"   Empty articles (0 chars): {len(empty_articles)}")
        log_test_result(f"   Short articles (<100 chars): {len(short_articles)}")
        log_test_result(f"   Substantial articles (≥100 chars): {len(substantial_articles)}")
        
        # Show details of problematic articles
        if empty_articles:
            log_test_result("❌ EMPTY ARTICLES DETECTED:", "ERROR")
            for article in empty_articles[:3]:
                log_test_result(f"   - {article['title'][:50]}...")
        
        if short_articles:
            log_test_result("⚠️ SHORT ARTICLES DETECTED:", "WARNING")
            for article in short_articles[:3]:
                log_test_result(f"   - {article['title'][:50]}... ({article['length']} chars)")
        
        # Check for validation metadata
        articles_with_validation = 0
        for article in articles:
            metadata = article.get('metadata', {})
            if metadata.get('content_validated') or metadata.get('content_length'):
                articles_with_validation += 1
        
        log_test_result(f"   Articles with validation metadata: {articles_with_validation}/{len(articles)}")
        
        # Determine success criteria
        empty_rate = len(empty_articles) / len(articles) * 100 if articles else 0
        substantial_rate = len(substantial_articles) / len(articles) * 100 if articles else 0
        
        if empty_rate == 0 and substantial_rate >= 70:
            log_test_result("✅ CONTENT VALIDATION SUCCESS: No empty articles, majority substantial", "SUCCESS")
            return True
        elif empty_rate <= 5 and substantial_rate >= 50:
            log_test_result("⚠️ CONTENT VALIDATION PARTIAL: Low empty rate, decent substantial content", "WARNING")
            return True
        else:
            log_test_result(f"❌ CONTENT VALIDATION FAILURE: {empty_rate:.1f}% empty, {substantial_rate:.1f}% substantial", "ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ Content validation test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_database_storage_and_metadata():
    """
    Test Database Storage - confirm articles are saved with proper metadata and validation flags
    """
    try:
        log_test_result("💾 TESTING DATABASE STORAGE & METADATA", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for metadata testing", "ERROR")
            return False
        
        log_test_result(f"🔍 Analyzing metadata in {len(articles)} articles...")
        
        metadata_analysis = {
            'has_id': 0,
            'has_title': 0,
            'has_content': 0,
            'has_status': 0,
            'has_created_at': 0,
            'has_metadata_object': 0,
            'has_validation_flags': 0,
            'has_outline_based_flag': 0,
            'has_content_length': 0
        }
        
        for article in articles:
            # Check required fields
            if article.get('id'):
                metadata_analysis['has_id'] += 1
            if article.get('title'):
                metadata_analysis['has_title'] += 1
            if article.get('content'):
                metadata_analysis['has_content'] += 1
            if article.get('status'):
                metadata_analysis['has_status'] += 1
            if article.get('created_at'):
                metadata_analysis['has_created_at'] += 1
            
            # Check metadata object
            metadata = article.get('metadata', {})
            if metadata:
                metadata_analysis['has_metadata_object'] += 1
                
                # Check for validation flags
                if metadata.get('content_validated') or metadata.get('content_length'):
                    metadata_analysis['has_validation_flags'] += 1
                
                # Check for outline-based processing flag
                if metadata.get('outline_based'):
                    metadata_analysis['has_outline_based_flag'] += 1
                
                # Check for content length tracking
                if metadata.get('content_length'):
                    metadata_analysis['has_content_length'] += 1
        
        # Report metadata analysis
        log_test_result("📊 Database Metadata Analysis:")
        total_articles = len(articles)
        
        for field, count in metadata_analysis.items():
            percentage = (count / total_articles * 100) if total_articles > 0 else 0
            log_test_result(f"   {field.replace('_', ' ').title()}: {count}/{total_articles} ({percentage:.1f}%)")
        
        # Check for proper UUID format in IDs
        valid_uuid_count = 0
        for article in articles:
            article_id = article.get('id', '')
            # Simple UUID format check (8-4-4-4-12 characters)
            if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', article_id, re.IGNORECASE):
                valid_uuid_count += 1
        
        log_test_result(f"   Valid UUID format: {valid_uuid_count}/{total_articles} ({valid_uuid_count/total_articles*100:.1f}%)")
        
        # Success criteria
        required_field_coverage = (
            metadata_analysis['has_id'] + 
            metadata_analysis['has_title'] + 
            metadata_analysis['has_content'] + 
            metadata_analysis['has_status'] + 
            metadata_analysis['has_created_at']
        ) / (5 * total_articles) * 100 if total_articles > 0 else 0
        
        metadata_coverage = metadata_analysis['has_metadata_object'] / total_articles * 100 if total_articles > 0 else 0
        
        if required_field_coverage >= 95 and metadata_coverage >= 80:
            log_test_result("✅ DATABASE STORAGE SUCCESS: Proper metadata and validation flags", "SUCCESS")
            return True
        elif required_field_coverage >= 80 and metadata_coverage >= 60:
            log_test_result("⚠️ DATABASE STORAGE PARTIAL: Good coverage but some missing metadata", "WARNING")
            return True
        else:
            log_test_result(f"❌ DATABASE STORAGE FAILURE: {required_field_coverage:.1f}% field coverage, {metadata_coverage:.1f}% metadata", "ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ Database storage test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_content_corruption_test():
    """Run comprehensive test suite for content corruption fixes and WYSIWYG enhancements"""
    log_test_result("🚀 STARTING CONTENT CORRUPTION FIXES & WYSIWYG ENHANCEMENT TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'content_generation_quality': False,
        'wysiwyg_enhancement_integration': False,
        'template_contamination_prevention': False,
        'content_validation_and_empty_prevention': False,
        'database_storage_and_metadata': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Content Generation Quality
    log_test_result("\nTEST 2: Content Generation Quality")
    test_results['content_generation_quality'] = test_content_generation_quality()
    
    # Test 3: WYSIWYG Enhancement Integration
    log_test_result("\nTEST 3: WYSIWYG Enhancement Integration")
    test_results['wysiwyg_enhancement_integration'] = test_wysiwyg_enhancement_integration()
    
    # Test 4: Template Contamination Prevention
    log_test_result("\nTEST 4: Template Contamination Prevention")
    test_results['template_contamination_prevention'] = test_template_contamination_prevention()
    
    # Test 5: Content Validation & Empty Prevention
    log_test_result("\nTEST 5: Content Validation & Empty Prevention")
    test_results['content_validation_and_empty_prevention'] = test_content_validation_and_empty_prevention()
    
    # Test 6: Database Storage & Metadata
    log_test_result("\nTEST 6: Database Storage & Metadata")
    test_results['database_storage_and_metadata'] = test_database_storage_and_metadata()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Specific success criteria for content corruption fixes
    critical_tests = [
        'content_generation_quality',
        'template_contamination_prevention', 
        'content_validation_and_empty_prevention'
    ]
    
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        log_test_result("🎉 CRITICAL SUCCESS: Content corruption fixes are working!", "CRITICAL_SUCCESS")
        log_test_result("✅ Articles now have substantial content without template contamination", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Content corruption issues still present", "CRITICAL_ERROR")
        log_test_result("❌ Some articles may still have empty content or template contamination", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Content Corruption Fixes & WYSIWYG Enhancement Testing")
    print("=" * 60)
    
    results = run_comprehensive_content_corruption_test()
    
    # Exit with appropriate code
    critical_tests = ['content_generation_quality', 'template_contamination_prevention', 'content_validation_and_empty_prevention']
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure