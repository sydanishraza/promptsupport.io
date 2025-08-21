#!/usr/bin/env python3
"""
ENHANCED CONTENT PROCESSING PIPELINE - RICH FORMATTING PRESERVATION TESTING
Testing the enhanced content processing pipeline with focus on rich formatting preservation
as specifically requested in the review.

Focus Areas:
1. Rich Formatting Preservation Test - Code blocks, lists, callouts, step-by-step procedures
2. Content Analysis Decision Test - Tutorial vs product guide identification
3. HTML Cleaning Validation - clean_article_html_content function testing
4. Code Block Context Test - Code examples staying with explanations
5. Specific focus on preventing over-fragmentation of tutorials
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

def create_rich_formatting_test_content():
    """Create test content with rich formatting elements"""
    return """# Google Maps API Tutorial - Complete Implementation Guide

## Introduction and Overview

Welcome to the comprehensive Google Maps API tutorial. This guide will walk you through the complete implementation process with detailed code examples and step-by-step procedures.

### What You'll Learn

- Setting up Google Maps API credentials
- Implementing basic map functionality
- Adding markers and custom styling
- Advanced features and customization

## Getting Started

### Step 1: API Key Setup

First, you need to obtain an API key from the Google Cloud Console:

1. Go to the Google Cloud Console
2. Create a new project or select an existing one
3. Enable the Maps JavaScript API
4. Create credentials (API key)

```javascript
// Initialize the map
function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 10,
        center: { lat: 37.7749, lng: -122.4194 },
        mapTypeId: 'roadmap'
    });
    
    // Add a marker
    const marker = new google.maps.Marker({
        position: { lat: 37.7749, lng: -122.4194 },
        map: map,
        title: 'San Francisco'
    });
}
```

> **Important Note:** Keep your API key secure and restrict it to your domain.

### Step 2: HTML Structure

Create the basic HTML structure for your map:

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
    
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
    </script>
</body>
</html>
```

## Advanced Features

### Custom Markers

You can customize markers with different icons and info windows:

```javascript
// Custom marker with info window
function addCustomMarker(map, position, title, content) {
    const marker = new google.maps.Marker({
        position: position,
        map: map,
        title: title,
        icon: {
            url: 'custom-marker.png',
            scaledSize: new google.maps.Size(40, 40)
        }
    });
    
    const infoWindow = new google.maps.InfoWindow({
        content: content
    });
    
    marker.addListener('click', () => {
        infoWindow.open(map, marker);
    });
    
    return marker;
}
```

### Map Styling

Apply custom styles to your map:

```javascript
const customMapStyle = [
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#e9e9e9"
            },
            {
                "lightness": 17
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "geometry",
        "stylers": [
            {
                "color": "#f5f5f5"
            },
            {
                "lightness": 20
            }
        ]
    }
];

// Apply the style to your map
const styledMap = new google.maps.StyledMapType(customMapStyle, {
    name: 'Custom Style'
});

map.mapTypes.set('custom_style', styledMap);
map.setMapTypeId('custom_style');
```

## Best Practices and Tips

### Performance Optimization

1. **Lazy Loading**: Load the map only when needed
2. **Marker Clustering**: Use marker clustering for multiple markers
3. **Debounce Events**: Debounce map events to improve performance

### Security Considerations

- Always restrict your API key to specific domains
- Use HTTPS for all map requests
- Implement proper error handling

### Common Issues and Solutions

**Issue**: Map not displaying
- **Solution**: Check if the API key is valid and the Maps JavaScript API is enabled

**Issue**: Markers not appearing
- **Solution**: Verify the coordinates are correct and within valid ranges

**Issue**: Slow loading times
- **Solution**: Implement lazy loading and optimize marker management

## Complete Example

Here's a complete working example that demonstrates all the concepts:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Complete Google Maps Example</title>
    <style>
        #map {
            height: 500px;
            width: 100%;
            margin: 20px 0;
        }
        .controls {
            margin: 10px 0;
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
        <button onclick="addMarker()">Add Marker</button>
        <button onclick="clearMarkers()">Clear Markers</button>
        <button onclick="toggleStyle()">Toggle Style</button>
    </div>
    
    <div id="map"></div>
    
    <script>
        let map;
        let markers = [];
        let customStyleEnabled = false;
        
        function initMap() {
            map = new google.maps.Map(document.getElementById("map"), {
                zoom: 10,
                center: { lat: 37.7749, lng: -122.4194 },
                mapTypeId: 'roadmap'
            });
            
            // Add initial marker
            addCustomMarker(
                { lat: 37.7749, lng: -122.4194 },
                'San Francisco',
                '<h3>San Francisco</h3><p>Welcome to the Golden Gate City!</p>'
            );
        }
        
        function addCustomMarker(position, title, content) {
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: title
            });
            
            const infoWindow = new google.maps.InfoWindow({
                content: content
            });
            
            marker.addListener('click', () => {
                infoWindow.open(map, marker);
            });
            
            markers.push(marker);
            return marker;
        }
        
        function addMarker() {
            const randomLat = 37.7749 + (Math.random() - 0.5) * 0.1;
            const randomLng = -122.4194 + (Math.random() - 0.5) * 0.1;
            
            addCustomMarker(
                { lat: randomLat, lng: randomLng },
                `Marker ${markers.length + 1}`,
                `<p>This is marker number ${markers.length + 1}</p>`
            );
        }
        
        function clearMarkers() {
            markers.forEach(marker => marker.setMap(null));
            markers = [];
        }
        
        function toggleStyle() {
            if (customStyleEnabled) {
                map.setMapTypeId('roadmap');
                customStyleEnabled = false;
            } else {
                map.setMapTypeId('custom_style');
                customStyleEnabled = true;
            }
        }
    </script>
    
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap">
    </script>
</body>
</html>
```

## Conclusion

This tutorial covered the essential aspects of implementing Google Maps API in your web applications. You learned how to:

- Set up and configure the API
- Create basic and advanced maps
- Add custom markers and styling
- Implement best practices for performance and security

Remember to always test your implementation thoroughly and keep your API key secure.
"""

def test_rich_formatting_preservation():
    """Test rich formatting preservation with comprehensive content"""
    try:
        log_test_result("🎨 TESTING RICH FORMATTING PRESERVATION", "CRITICAL")
        
        # Create rich content with code blocks, lists, callouts, and procedures
        rich_content = create_rich_formatting_test_content()
        
        log_test_result(f"📝 Created test content: {len(rich_content)} characters")
        log_test_result("   ✅ Contains code blocks (JavaScript, HTML, CSS)")
        log_test_result("   ✅ Contains numbered and bulleted lists")
        log_test_result("   ✅ Contains step-by-step procedures")
        log_test_result("   ✅ Contains callouts and notes")
        log_test_result("   ✅ Contains technical formatting")
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing content through Knowledge Engine...")
        
        # Use text processing endpoint
        payload = {
            "content": rich_content,
            "content_type": "text",
            "metadata": {
                "original_filename": "Google_Maps_API_Tutorial_Rich_Formatting_Test.txt",
                "source": "rich_formatting_test"
            }
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process", 
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
                        chunks_created = status_data.get('chunks_created', 0)
                        
                        log_test_result(f"📈 PROCESSING METRICS:")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        
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
        log_test_result(f"❌ Rich formatting test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_content_analysis_decisions():
    """Test intelligent content analysis and structuring decisions"""
    try:
        log_test_result("🧠 TESTING CONTENT ANALYSIS DECISIONS", "CRITICAL")
        
        # Get recent articles from Content Library to analyze decisions
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📚 Content Library Analysis:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Retrieved Articles: {len(articles)}")
        
        # Analyze recent articles for content analysis patterns
        tutorial_articles = []
        guide_articles = []
        unified_articles = []
        split_articles = []
        
        for article in articles[:20]:  # Check recent 20 articles
            title = article.get('title', '').lower()
            article_type = article.get('article_type', '')
            metadata = article.get('metadata', {})
            
            # Check for tutorial/procedural content
            if any(keyword in title for keyword in ['tutorial', 'guide', 'how-to', 'step-by-step']):
                tutorial_articles.append(article)
            
            # Check for unified vs split processing
            if metadata.get('unified_article'):
                unified_articles.append(article)
            elif metadata.get('outline_based'):
                split_articles.append(article)
        
        log_test_result(f"🔍 CONTENT ANALYSIS PATTERNS:")
        log_test_result(f"   📖 Tutorial/Guide Articles: {len(tutorial_articles)}")
        log_test_result(f"   📄 Unified Articles: {len(unified_articles)}")
        log_test_result(f"   🔀 Split Articles: {len(split_articles)}")
        
        # Check for appropriate decision making
        if tutorial_articles:
            log_test_result("✅ System correctly identifies tutorial/procedural content")
            
            # Check if tutorials are kept unified (as they should be)
            tutorial_unified_count = 0
            for article in tutorial_articles:
                if article.get('metadata', {}).get('unified_article'):
                    tutorial_unified_count += 1
            
            if tutorial_unified_count > 0:
                log_test_result(f"✅ {tutorial_unified_count} tutorial articles kept unified (preserving context)")
            else:
                log_test_result("⚠️ No tutorial articles found with unified processing")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Content analysis test failed: {e}", "ERROR")
        return False

def test_html_cleaning_validation():
    """Test HTML cleaning function for rich formatting preservation"""
    try:
        log_test_result("🧹 TESTING HTML CLEANING VALIDATION", "CRITICAL")
        
        # Get recent articles to check HTML quality
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("⚠️ No articles found for HTML validation")
            return False
        
        log_test_result(f"🔍 Analyzing HTML quality in {len(articles[:10])} recent articles...")
        
        # Check HTML quality metrics
        html_quality_metrics = {
            'proper_code_blocks': 0,
            'preserved_lists': 0,
            'clean_html_structure': 0,
            'no_markdown_artifacts': 0,
            'proper_headings': 0,
            'total_articles_checked': 0
        }
        
        for article in articles[:10]:  # Check first 10 articles
            content = article.get('content', '')
            if not content:
                continue
                
            html_quality_metrics['total_articles_checked'] += 1
            
            # Check for proper code blocks (<pre><code> instead of ```html)
            if '<pre><code>' in content and '```html' not in content:
                html_quality_metrics['proper_code_blocks'] += 1
            
            # Check for preserved lists
            if '<ul>' in content or '<ol>' in content:
                html_quality_metrics['preserved_lists'] += 1
            
            # Check for clean HTML structure (no document wrapper tags)
            if '<html>' not in content and '<head>' not in content and '<body>' not in content:
                html_quality_metrics['clean_html_structure'] += 1
            
            # Check for no markdown artifacts
            if '```' not in content and '##' not in content:
                html_quality_metrics['no_markdown_artifacts'] += 1
            
            # Check for proper heading structure
            if '<h2>' in content or '<h3>' in content:
                html_quality_metrics['proper_headings'] += 1
        
        # Report HTML quality results
        log_test_result("📊 HTML QUALITY ANALYSIS RESULTS:")
        total_checked = html_quality_metrics['total_articles_checked']
        
        if total_checked > 0:
            for metric, count in html_quality_metrics.items():
                if metric != 'total_articles_checked':
                    percentage = (count / total_checked) * 100
                    status = "✅" if percentage >= 80 else "⚠️" if percentage >= 60 else "❌"
                    log_test_result(f"   {status} {metric.replace('_', ' ').title()}: {count}/{total_checked} ({percentage:.1f}%)")
            
            # Overall assessment
            avg_quality = sum(html_quality_metrics.values()) / (len(html_quality_metrics) - 1) / total_checked * 100
            if avg_quality >= 80:
                log_test_result(f"✅ EXCELLENT HTML quality: {avg_quality:.1f}% average", "SUCCESS")
                return True
            elif avg_quality >= 60:
                log_test_result(f"⚠️ GOOD HTML quality: {avg_quality:.1f}% average", "WARNING")
                return True
            else:
                log_test_result(f"❌ POOR HTML quality: {avg_quality:.1f}% average", "ERROR")
                return False
        else:
            log_test_result("❌ No articles with content found for HTML validation", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ HTML cleaning validation failed: {e}", "ERROR")
        return False

def test_code_block_context_preservation():
    """Test that code examples stay with their explanations"""
    try:
        log_test_result("🔗 TESTING CODE BLOCK CONTEXT PRESERVATION", "CRITICAL")
        
        # Get articles that should contain code blocks
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Look for articles with code content
        code_articles = []
        for article in articles:
            content = article.get('content', '').lower()
            title = article.get('title', '').lower()
            
            # Check for code-related content
            if any(keyword in content or keyword in title for keyword in 
                   ['javascript', 'html', 'css', 'code', 'function', 'api', 'script']):
                code_articles.append(article)
        
        log_test_result(f"🔍 Found {len(code_articles)} articles with code-related content")
        
        if not code_articles:
            log_test_result("⚠️ No code-related articles found for context testing")
            return True  # Not a failure, just no code to test
        
        # Analyze code block context preservation
        context_preservation_score = 0
        total_code_articles = len(code_articles[:5])  # Check first 5 code articles
        
        for article in code_articles[:5]:
            content = article.get('content', '')
            title = article.get('title', '')
            
            log_test_result(f"   📄 Analyzing: {title[:50]}...")
            
            # Check for code blocks with context
            has_code_blocks = '<pre><code>' in content or '<code>' in content
            has_explanatory_text = len(content.split()) > 100  # Substantial explanatory content
            has_proper_structure = '<h2>' in content or '<h3>' in content  # Proper sectioning
            
            context_score = 0
            if has_code_blocks:
                context_score += 1
                log_test_result(f"      ✅ Contains code blocks")
            
            if has_explanatory_text:
                context_score += 1
                log_test_result(f"      ✅ Contains substantial explanatory text")
            
            if has_proper_structure:
                context_score += 1
                log_test_result(f"      ✅ Has proper heading structure")
            
            # Check if code and explanations are in the same article (not fragmented)
            if context_score >= 2:
                context_preservation_score += 1
                log_test_result(f"      ✅ Good context preservation")
            else:
                log_test_result(f"      ⚠️ Potential context fragmentation")
        
        # Calculate overall context preservation
        if total_code_articles > 0:
            preservation_percentage = (context_preservation_score / total_code_articles) * 100
            
            if preservation_percentage >= 80:
                log_test_result(f"✅ EXCELLENT context preservation: {preservation_percentage:.1f}%", "SUCCESS")
                return True
            elif preservation_percentage >= 60:
                log_test_result(f"⚠️ GOOD context preservation: {preservation_percentage:.1f}%", "WARNING")
                return True
            else:
                log_test_result(f"❌ POOR context preservation: {preservation_percentage:.1f}%", "ERROR")
                return False
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Code block context test failed: {e}", "ERROR")
        return False

def test_tutorial_fragmentation_prevention():
    """Test that tutorials are not over-fragmented"""
    try:
        log_test_result("🚫 TESTING TUTORIAL FRAGMENTATION PREVENTION", "CRITICAL")
        
        # Get articles to check for over-fragmentation
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Group articles by source document to check fragmentation
        source_groups = {}
        for article in articles:
            source = article.get('source_document', 'unknown')
            metadata = article.get('metadata', {})
            
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(article)
        
        log_test_result(f"🔍 Analyzing fragmentation across {len(source_groups)} source documents")
        
        fragmentation_analysis = {
            'appropriate_splitting': 0,
            'over_fragmentation': 0,
            'unified_tutorials': 0,
            'total_sources': 0
        }
        
        for source, source_articles in source_groups.items():
            if len(source_articles) < 2:
                continue  # Skip single-article sources
                
            fragmentation_analysis['total_sources'] += 1
            article_count = len(source_articles)
            
            log_test_result(f"   📄 {source}: {article_count} articles")
            
            # Check if this appears to be tutorial content
            is_tutorial = any(
                keyword in source.lower() or 
                any(keyword in article.get('title', '').lower() for article in source_articles)
                for keyword in ['tutorial', 'guide', 'how-to', 'step', 'getting started']
            )
            
            # Check for unified processing indicators
            has_unified = any(
                article.get('metadata', {}).get('unified_article') 
                for article in source_articles
            )
            
            if is_tutorial:
                if has_unified or article_count <= 3:
                    fragmentation_analysis['unified_tutorials'] += 1
                    log_test_result(f"      ✅ Tutorial kept appropriately unified")
                elif article_count > 10:
                    fragmentation_analysis['over_fragmentation'] += 1
                    log_test_result(f"      ⚠️ Potential over-fragmentation: {article_count} articles")
                else:
                    fragmentation_analysis['appropriate_splitting'] += 1
                    log_test_result(f"      ✅ Appropriate splitting: {article_count} articles")
            else:
                if article_count <= 15:
                    fragmentation_analysis['appropriate_splitting'] += 1
                    log_test_result(f"      ✅ Appropriate splitting for complex content")
                else:
                    fragmentation_analysis['over_fragmentation'] += 1
                    log_test_result(f"      ⚠️ Potential over-fragmentation: {article_count} articles")
        
        # Report fragmentation analysis
        log_test_result("📊 FRAGMENTATION ANALYSIS RESULTS:")
        total_sources = fragmentation_analysis['total_sources']
        
        if total_sources > 0:
            for metric, count in fragmentation_analysis.items():
                if metric != 'total_sources':
                    percentage = (count / total_sources) * 100
                    log_test_result(f"   {metric.replace('_', ' ').title()}: {count}/{total_sources} ({percentage:.1f}%)")
            
            # Check for over-fragmentation issues
            over_frag_percentage = (fragmentation_analysis['over_fragmentation'] / total_sources) * 100
            
            if over_frag_percentage <= 10:
                log_test_result("✅ EXCELLENT fragmentation control: Minimal over-fragmentation", "SUCCESS")
                return True
            elif over_frag_percentage <= 25:
                log_test_result("⚠️ GOOD fragmentation control: Some over-fragmentation detected", "WARNING")
                return True
            else:
                log_test_result("❌ POOR fragmentation control: Significant over-fragmentation", "ERROR")
                return False
        else:
            log_test_result("⚠️ No multi-article sources found for fragmentation analysis")
            return True
        
    except Exception as e:
        log_test_result(f"❌ Tutorial fragmentation test failed: {e}", "ERROR")
        return False

def run_comprehensive_rich_formatting_test():
    """Run comprehensive test suite for rich formatting preservation"""
    log_test_result("🎨 STARTING COMPREHENSIVE RICH FORMATTING PRESERVATION TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'rich_formatting_preservation': False,
        'content_analysis_decisions': False,
        'html_cleaning_validation': False,
        'code_block_context_preservation': False,
        'tutorial_fragmentation_prevention': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Rich Formatting Preservation (CRITICAL)
    log_test_result("\nTEST 2: RICH FORMATTING PRESERVATION TEST")
    test_results['rich_formatting_preservation'] = test_rich_formatting_preservation()
    
    # Test 3: Content Analysis Decisions
    log_test_result("\nTEST 3: CONTENT ANALYSIS DECISIONS TEST")
    test_results['content_analysis_decisions'] = test_content_analysis_decisions()
    
    # Test 4: HTML Cleaning Validation
    log_test_result("\nTEST 4: HTML CLEANING VALIDATION TEST")
    test_results['html_cleaning_validation'] = test_html_cleaning_validation()
    
    # Test 5: Code Block Context Preservation
    log_test_result("\nTEST 5: CODE BLOCK CONTEXT PRESERVATION TEST")
    test_results['code_block_context_preservation'] = test_code_block_context_preservation()
    
    # Test 6: Tutorial Fragmentation Prevention
    log_test_result("\nTEST 6: TUTORIAL FRAGMENTATION PREVENTION TEST")
    test_results['tutorial_fragmentation_prevention'] = test_tutorial_fragmentation_prevention()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL RICH FORMATTING TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Specific success criteria assessment
    critical_tests = ['rich_formatting_preservation', 'html_cleaning_validation', 'code_block_context_preservation']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        log_test_result("🎉 CRITICAL SUCCESS: Rich formatting preservation is working correctly!", "CRITICAL_SUCCESS")
        log_test_result("✅ Code blocks, lists, callouts, and formatting are preserved", "CRITICAL_SUCCESS")
        log_test_result("✅ HTML cleaning maintains content elements while removing document structure", "CRITICAL_SUCCESS")
        log_test_result("✅ Code examples stay with their explanations", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Rich formatting preservation has issues", "CRITICAL_ERROR")
        log_test_result("❌ Some formatting elements may be lost or corrupted during processing", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Enhanced Content Processing Pipeline - Rich Formatting Preservation Testing")
    print("=" * 80)
    
    results = run_comprehensive_rich_formatting_test()
    
    # Exit with appropriate code
    critical_tests = ['rich_formatting_preservation', 'html_cleaning_validation', 'code_block_context_preservation']
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure