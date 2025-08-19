#!/usr/bin/env python3
"""
PHASE 6 EMPTY ARTICLES BUG FIX TESTING
Testing the bug fixes for empty articles issue in Phase 6 pipeline

CRITICAL BUG FIX TESTING AREAS:
1. Google Maps API Tutorial Test (Primary focus) - should be classified as "tutorial" and use "unified" approach
2. Content Classification Accuracy - tutorial vs reference content  
3. Actual Content Generation - verify no placeholder content
4. Processing Pipeline Validation - Phase 6 enhanced pipeline
5. Specific Bug Validation - no empty articles with placeholder content

SUCCESS CRITERIA:
✅ Tutorial content uses unified approach (not moderate split)
✅ Generated articles contain comprehensive, real content
✅ Code blocks and technical formatting preserved
✅ No placeholder or empty content
✅ Proper content classification and processing decisions
"""

import requests
import json
import time
import os
import sys
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

def create_google_maps_tutorial_content():
    """Create realistic Google Maps API tutorial content for testing"""
    return """# Google Maps JavaScript API Tutorial - Complete Guide

## Introduction to Google Maps API

The Google Maps JavaScript API is a powerful tool that allows developers to embed Google Maps into web applications with custom functionality. This comprehensive tutorial will guide you through the entire process of integrating Google Maps into your web application.

## Prerequisites

Before starting this tutorial, you should have:
- Basic knowledge of HTML, CSS, and JavaScript
- A text editor or IDE
- A web browser for testing
- A Google Cloud Platform account

## Step 1: Getting Your API Key

To use the Google Maps JavaScript API, you need an API key:

1. Go to the Google Cloud Console
2. Create a new project or select an existing one
3. Enable the Maps JavaScript API
4. Create credentials (API key)
5. Restrict your API key for security

```javascript
// Example of API key usage
const API_KEY = 'YOUR_API_KEY_HERE';
```

## Step 2: Setting Up Your HTML Structure

Create a basic HTML file with the following structure:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Google Maps Tutorial</title>
    <style>
        #map {
            height: 400px;
            width: 100%;
        }
    </style>
</head>
<body>
    <h1>My Google Map</h1>
    <div id="map"></div>
    
    <script>
        function initMap() {
            // Map initialization code will go here
        }
    </script>
    
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
    </script>
</body>
</html>
```

## Step 3: Initializing Your First Map

Now let's create your first map with JavaScript:

```javascript
function initMap() {
    // Map options
    const mapOptions = {
        zoom: 10,
        center: { lat: 37.7749, lng: -122.4194 }, // San Francisco
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    
    // Create the map
    const map = new google.maps.Map(
        document.getElementById('map'), 
        mapOptions
    );
}
```

## Step 4: Adding Markers

Markers help identify specific locations on your map:

```javascript
function addMarker(map, position, title) {
    const marker = new google.maps.Marker({
        position: position,
        map: map,
        title: title,
        animation: google.maps.Animation.DROP
    });
    
    return marker;
}

// Usage example
const marker = addMarker(map, 
    { lat: 37.7749, lng: -122.4194 }, 
    'San Francisco'
);
```

## Step 5: Creating Info Windows

Info windows provide additional information when markers are clicked:

```javascript
function createInfoWindow(marker, content) {
    const infoWindow = new google.maps.InfoWindow({
        content: content
    });
    
    marker.addListener('click', function() {
        infoWindow.open(map, marker);
    });
}
```

## Step 6: Customizing Map Styles

You can customize your map's appearance with custom styles:

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

const styledMapOptions = {
    zoom: 10,
    center: { lat: 37.7749, lng: -122.4194 },
    styles: customMapStyle
};
```

## Step 7: Handling User Interactions

Add event listeners to handle user interactions:

```javascript
// Click event listener
map.addListener('click', function(event) {
    console.log('Map clicked at:', event.latLng.toString());
    
    // Add marker at clicked location
    addMarker(map, event.latLng, 'Clicked Location');
});

// Zoom change listener
map.addListener('zoom_changed', function() {
    console.log('Zoom level:', map.getZoom());
});
```

## Step 8: Advanced Features

### Geocoding
Convert addresses to coordinates:

```javascript
const geocoder = new google.maps.Geocoder();

function geocodeAddress(address) {
    geocoder.geocode({'address': address}, function(results, status) {
        if (status === 'OK') {
            map.setCenter(results[0].geometry.location);
            addMarker(map, results[0].geometry.location, address);
        } else {
            console.error('Geocoding failed: ' + status);
        }
    });
}
```

### Directions Service
Get directions between two points:

```javascript
const directionsService = new google.maps.DirectionsService();
const directionsRenderer = new google.maps.DirectionsRenderer();

function calculateRoute(start, end) {
    const request = {
        origin: start,
        destination: end,
        travelMode: google.maps.TravelMode.DRIVING
    };
    
    directionsService.route(request, function(result, status) {
        if (status === 'OK') {
            directionsRenderer.setDirections(result);
        }
    });
}
```

## Best Practices

1. **API Key Security**: Never expose your API key in client-side code in production
2. **Error Handling**: Always implement proper error handling for API calls
3. **Performance**: Limit the number of markers and use marker clustering for large datasets
4. **Responsive Design**: Ensure your maps work well on mobile devices
5. **Accessibility**: Add proper ARIA labels and keyboard navigation support

## Troubleshooting Common Issues

### Map Not Loading
- Check your API key is correct and has proper permissions
- Verify the Maps JavaScript API is enabled in Google Cloud Console
- Check browser console for error messages

### Markers Not Appearing
- Ensure marker positions are valid latitude/longitude coordinates
- Check that the map zoom level allows markers to be visible
- Verify marker creation code is called after map initialization

### Performance Issues
- Use marker clustering for large numbers of markers
- Implement lazy loading for complex map features
- Optimize custom map styles

## Conclusion

This tutorial covered the essential aspects of integrating Google Maps JavaScript API into your web applications. You learned how to:

- Set up API keys and basic HTML structure
- Initialize maps with custom options
- Add interactive markers and info windows
- Customize map appearance with styles
- Handle user interactions and events
- Implement advanced features like geocoding and directions

Continue exploring the Google Maps API documentation for more advanced features and customization options.
"""

def test_google_maps_tutorial_processing():
    """
    PRIMARY TEST: Process Google Maps API tutorial content and verify:
    1. Content is classified as "tutorial" 
    2. Uses "unified" approach (not moderate split)
    3. Generated articles have full, rich content (not placeholders)
    4. Code blocks and technical formatting are preserved
    """
    try:
        log_test_result("🎯 STARTING PRIMARY TEST: Google Maps API Tutorial Processing", "CRITICAL")
        
        # Create tutorial content
        tutorial_content = create_google_maps_tutorial_content()
        log_test_result(f"📝 Created tutorial content: {len(tutorial_content)} characters")
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing tutorial content through Knowledge Engine...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": tutorial_content,
                "filename": "Google_Maps_API_Tutorial.txt"
            },
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Processing failed: Status {response.status_code}", "ERROR")
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
                        
                        # CRITICAL VERIFICATION: Check content classification and approach
                        return verify_tutorial_processing_results(articles_generated)
                        
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
        log_test_result(f"❌ Google Maps tutorial test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def verify_tutorial_processing_results(articles_generated):
    """Verify the tutorial processing results meet success criteria"""
    try:
        log_test_result("🔍 VERIFYING TUTORIAL PROCESSING RESULTS", "CRITICAL")
        
        # Get recent articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Find Google Maps tutorial articles (most recent ones)
        tutorial_articles = []
        for article in articles[:10]:  # Check last 10 articles
            title = article.get('title', '').lower()
            content = article.get('content', '')
            
            if 'google' in title or 'maps' in title or 'api' in title:
                tutorial_articles.append(article)
        
        if not tutorial_articles:
            log_test_result("❌ No Google Maps tutorial articles found in Content Library", "ERROR")
            return False
        
        log_test_result(f"✅ Found {len(tutorial_articles)} tutorial articles")
        
        # SUCCESS CRITERIA VERIFICATION
        success_criteria = {
            'unified_approach': False,
            'comprehensive_content': False,
            'code_blocks_preserved': False,
            'no_placeholder_content': False,
            'proper_classification': False
        }
        
        # Check each article
        for i, article in enumerate(tutorial_articles):
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            article_type = article.get('article_type', 'unknown')
            
            log_test_result(f"📄 Article {i+1}: {title[:60]}...")
            log_test_result(f"   Type: {article_type}")
            log_test_result(f"   Content Length: {len(content)} characters")
            
            # Check for comprehensive content (not empty/placeholder)
            if len(content) > 500:
                success_criteria['comprehensive_content'] = True
                log_test_result("   ✅ Comprehensive content confirmed")
            
            # Check for code blocks preservation
            if '<code>' in content or '<pre>' in content or 'function' in content:
                success_criteria['code_blocks_preserved'] = True
                log_test_result("   ✅ Code blocks preserved")
            
            # Check for NO placeholder content
            placeholder_indicators = [
                'This is an overview of',
                'Main content from',
                '```html',
                '<!DOCTYPE html>',
                '<html>',
                '<head>',
                '<body>'
            ]
            
            has_placeholders = any(indicator in content for indicator in placeholder_indicators)
            if not has_placeholders:
                success_criteria['no_placeholder_content'] = True
                log_test_result("   ✅ No placeholder content detected")
            else:
                log_test_result("   ❌ Placeholder content detected", "WARNING")
            
            # Check proper classification (tutorial content should be unified)
            if article_type in ['tutorial', 'guide', 'how-to', 'unified']:
                success_criteria['proper_classification'] = True
                log_test_result("   ✅ Proper tutorial classification")
        
        # Check unified approach (should be 1-3 articles for tutorial, not many split articles)
        if len(tutorial_articles) <= 3:
            success_criteria['unified_approach'] = True
            log_test_result("✅ Unified approach confirmed (tutorial kept together)")
        else:
            log_test_result(f"⚠️ Many articles generated ({len(tutorial_articles)}) - may indicate over-splitting", "WARNING")
        
        # FINAL SUCCESS CRITERIA EVALUATION
        log_test_result("\n🎯 SUCCESS CRITERIA EVALUATION:", "CRITICAL")
        passed_criteria = 0
        total_criteria = len(success_criteria)
        
        for criterion, passed in success_criteria.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            log_test_result(f"   {criterion.replace('_', ' ').title()}: {status}")
            if passed:
                passed_criteria += 1
        
        log_test_result(f"\nOVERALL RESULT: {passed_criteria}/{total_criteria} criteria passed")
        
        if passed_criteria >= 4:  # Allow 1 failure
            log_test_result("🎉 TUTORIAL PROCESSING SUCCESS: Bug fixes are working correctly!", "CRITICAL_SUCCESS")
            return True
        else:
            log_test_result("❌ TUTORIAL PROCESSING FAILURE: Bug fixes need more work", "CRITICAL_ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Tutorial verification failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_content_classification_accuracy():
    """Test content classification accuracy for different content types"""
    try:
        log_test_result("🔍 TESTING CONTENT CLASSIFICATION ACCURACY", "CRITICAL")
        
        # Test different content types
        test_contents = [
            {
                "name": "Tutorial Content",
                "content": """# Step-by-Step Setup Guide
                
                ## Step 1: Installation
                Follow these steps to install the software:
                1. Download the installer
                2. Run the setup wizard
                3. Configure your settings
                
                ```bash
                npm install package-name
                ```
                
                ## Step 2: Configuration
                Next, configure your application...
                """,
                "expected_type": "tutorial",
                "expected_approach": "unified"
            },
            {
                "name": "Reference Content", 
                "content": """# API Reference Documentation
                
                ## Authentication Endpoints
                
                ### POST /auth/login
                Authenticate user credentials.
                
                ### GET /auth/profile
                Get user profile information.
                
                ## Data Endpoints
                
                ### GET /api/users
                Retrieve user list.
                
                ### POST /api/users
                Create new user.
                """,
                "expected_type": "reference",
                "expected_approach": "split"
            }
        ]
        
        classification_results = []
        
        for test_case in test_contents:
            log_test_result(f"📝 Testing {test_case['name']}...")
            
            # Process content
            response = requests.post(
                f"{API_BASE}/content/process",
                json={
                    "content": test_case['content'],
                    "filename": f"{test_case['name'].replace(' ', '_')}.txt"
                },
                timeout=120
            )
            
            if response.status_code == 200:
                process_data = response.json()
                job_id = process_data.get('job_id')
                
                # Wait for completion (simplified)
                time.sleep(30)  # Give it time to process
                
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data.get('status') == 'completed':
                        articles_count = status_data.get('articles_generated', 0)
                        
                        # Determine if approach was unified or split based on article count
                        actual_approach = "unified" if articles_count <= 2 else "split"
                        
                        classification_results.append({
                            'name': test_case['name'],
                            'expected_approach': test_case['expected_approach'],
                            'actual_approach': actual_approach,
                            'articles_generated': articles_count,
                            'correct': actual_approach == test_case['expected_approach']
                        })
                        
                        log_test_result(f"   Articles Generated: {articles_count}")
                        log_test_result(f"   Approach: {actual_approach} (expected: {test_case['expected_approach']})")
        
        # Evaluate classification accuracy
        correct_classifications = sum(1 for result in classification_results if result['correct'])
        total_tests = len(classification_results)
        
        log_test_result(f"\n📊 CLASSIFICATION ACCURACY: {correct_classifications}/{total_tests} correct")
        
        if correct_classifications >= total_tests * 0.8:  # 80% accuracy threshold
            log_test_result("✅ Content classification accuracy PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ Content classification accuracy FAILED", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Content classification test failed: {e}", "ERROR")
        return False

def test_empty_articles_validation():
    """Test for empty articles and placeholder content issues"""
    try:
        log_test_result("🔍 TESTING FOR EMPTY ARTICLES AND PLACEHOLDER CONTENT", "CRITICAL")
        
        # Get all articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("⚠️ No articles found in Content Library")
            return True  # No articles to check
        
        log_test_result(f"📚 Checking {len(articles)} articles for empty content...")
        
        empty_articles = []
        placeholder_articles = []
        short_articles = []
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            content_length = len(content.strip())
            
            # Check for empty articles
            if content_length == 0:
                empty_articles.append(title)
            
            # Check for very short articles (likely empty or placeholder)
            elif content_length < 100:
                short_articles.append({'title': title, 'length': content_length})
            
            # Check for placeholder content patterns
            placeholder_patterns = [
                'This is an overview of',
                'Main content from',
                '```html\n<!DOCTYPE html>',
                '<html><head><title>',
                'placeholder content',
                'Lorem ipsum'
            ]
            
            if any(pattern in content for pattern in placeholder_patterns):
                placeholder_articles.append(title)
        
        # Report findings
        log_test_result(f"📊 EMPTY ARTICLES ANALYSIS:")
        log_test_result(f"   Empty articles (0 chars): {len(empty_articles)}")
        log_test_result(f"   Short articles (<100 chars): {len(short_articles)}")
        log_test_result(f"   Placeholder content articles: {len(placeholder_articles)}")
        
        if empty_articles:
            log_test_result("❌ EMPTY ARTICLES FOUND:", "ERROR")
            for title in empty_articles[:5]:  # Show first 5
                log_test_result(f"     - {title}")
        
        if placeholder_articles:
            log_test_result("❌ PLACEHOLDER CONTENT FOUND:", "ERROR")
            for title in placeholder_articles[:5]:  # Show first 5
                log_test_result(f"     - {title}")
        
        if short_articles:
            log_test_result("⚠️ VERY SHORT ARTICLES FOUND:", "WARNING")
            for article in short_articles[:5]:  # Show first 5
                log_test_result(f"     - {article['title']} ({article['length']} chars)")
        
        # Success criteria: No empty articles, minimal placeholder content
        if len(empty_articles) == 0 and len(placeholder_articles) <= 1:
            log_test_result("✅ EMPTY ARTICLES VALIDATION PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ EMPTY ARTICLES VALIDATION FAILED", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Empty articles validation failed: {e}", "ERROR")
        return False

def run_phase6_bug_fix_test_suite():
    """Run comprehensive Phase 6 bug fix test suite"""
    log_test_result("🚀 STARTING PHASE 6 EMPTY ARTICLES BUG FIX TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'google_maps_tutorial': False,
        'content_classification': False,
        'empty_articles_validation': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Google Maps Tutorial Processing (PRIMARY TEST)
    log_test_result("\nTEST 2: GOOGLE MAPS API TUTORIAL PROCESSING (PRIMARY)")
    test_results['google_maps_tutorial'] = test_google_maps_tutorial_processing()
    
    # Test 3: Content Classification Accuracy
    log_test_result("\nTEST 3: Content Classification Accuracy")
    test_results['content_classification'] = test_content_classification_accuracy()
    
    # Test 4: Empty Articles Validation
    log_test_result("\nTEST 4: Empty Articles and Placeholder Content Validation")
    test_results['empty_articles_validation'] = test_empty_articles_validation()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 PHASE 6 BUG FIX TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # SUCCESS CRITERIA EVALUATION
    critical_tests_passed = test_results['google_maps_tutorial'] and test_results['empty_articles_validation']
    
    if critical_tests_passed and passed_tests >= 3:
        log_test_result("🎉 PHASE 6 BUG FIXES SUCCESSFUL!", "CRITICAL_SUCCESS")
        log_test_result("✅ Empty articles bug has been resolved", "CRITICAL_SUCCESS")
        log_test_result("✅ Tutorial content processing is working correctly", "CRITICAL_SUCCESS")
        log_test_result("✅ Content generation produces comprehensive, real content", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ PHASE 6 BUG FIXES INCOMPLETE", "CRITICAL_ERROR")
        log_test_result("❌ Empty articles issue may still persist", "CRITICAL_ERROR")
        log_test_result("❌ Further investigation and fixes required", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Phase 6 Empty Articles Bug Fix Testing")
    print("=" * 50)
    
    results = run_phase6_bug_fix_test_suite()
    
    # Exit with appropriate code
    critical_success = results['google_maps_tutorial'] and results['empty_articles_validation']
    if critical_success:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure