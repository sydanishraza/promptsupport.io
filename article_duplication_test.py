#!/usr/bin/env python3
"""
ARTICLE DUPLICATION FIX TESTING
Testing the fix for duplicate overview articles when introduction content exists
Focus: Verify that create_overview_article_with_sections() properly checks for existing intro sections
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

def get_content_library_baseline():
    """Get baseline count of articles in Content Library"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            log_test_result(f"📊 Content Library baseline: {total_articles} articles")
            return total_articles, data.get('articles', [])
        else:
            log_test_result(f"❌ Failed to get Content Library baseline: {response.status_code}")
            return 0, []
    except Exception as e:
        log_test_result(f"❌ Error getting Content Library baseline: {e}")
        return 0, []

def test_content_with_introduction_section():
    """Test content that contains introduction/overview sections to verify no duplication"""
    try:
        log_test_result("🎯 TESTING CONTENT WITH INTRODUCTION SECTION", "CRITICAL")
        
        # Create test content that includes introduction/overview sections
        test_content = """
# Google Maps JavaScript API Tutorial - Complete Guide

## Introduction

Welcome to the comprehensive Google Maps JavaScript API tutorial. This guide will walk you through everything you need to know to integrate Google Maps into your web applications.

The Google Maps JavaScript API is a powerful tool that allows developers to embed customized maps into web pages. Whether you're building a simple location finder or a complex mapping application, this API provides the functionality you need.

### What You'll Learn

In this tutorial, you will learn:
- How to set up your Google Maps API key
- Basic map initialization and configuration
- Adding markers and info windows
- Customizing map styles and controls
- Advanced features like geocoding and directions

## Getting Started

Before you can use the Google Maps JavaScript API, you need to obtain an API key from the Google Cloud Console.

### Step 1: Create a Google Cloud Project

1. Go to the Google Cloud Console
2. Create a new project or select an existing one
3. Enable the Maps JavaScript API

### Step 2: Generate API Key

1. Navigate to the Credentials page
2. Click "Create Credentials" and select "API Key"
3. Copy your API key for use in your application

## Basic Map Implementation

Now let's create your first Google Maps implementation:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My First Google Map</title>
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

You can add markers to your map to highlight specific locations:

```javascript
var marker = new google.maps.Marker({
    position: {lat: -34.397, lng: 150.644},
    map: map,
    title: 'Hello World!'
});
```

### Custom Styling

Customize your map appearance with custom styles:

```javascript
var styledMapType = new google.maps.StyledMapType([
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [{"color": "#e9e9e9"}, {"lightness": 17}]
    }
]);
```

## Troubleshooting

Common issues and solutions:

### API Key Issues
- Ensure your API key is valid and has the correct permissions
- Check that the Maps JavaScript API is enabled in your Google Cloud project

### Map Not Loading
- Verify the callback function name matches your script tag
- Check browser console for JavaScript errors

## Conclusion

This tutorial covered the fundamentals of the Google Maps JavaScript API. You now have the knowledge to create interactive maps for your web applications.

For more advanced features, refer to the official Google Maps JavaScript API documentation.
"""

        log_test_result("📤 Processing content with Introduction section...")
        
        # Process the content through the Knowledge Engine
        response = requests.post(
            f"{API_BASE}/content/process-text",
            json={"content": test_content},
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
        
        log_test_result(f"✅ Content processing started, Job ID: {job_id}")
        
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
                    
                    time.sleep(10)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Introduction section test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_content_without_introduction_section():
    """Test content without introduction sections to verify overview creation works"""
    try:
        log_test_result("🎯 TESTING CONTENT WITHOUT INTRODUCTION SECTION", "CRITICAL")
        
        # Create test content WITHOUT introduction/overview sections
        test_content = """
# Database Configuration Guide

## Database Setup

Setting up your database connection requires several configuration steps.

### Connection Parameters

Configure the following parameters in your application:

```javascript
const dbConfig = {
    host: 'localhost',
    port: 5432,
    database: 'myapp',
    username: 'admin',
    password: 'secure_password'
};
```

## Security Configuration

Database security is crucial for protecting your application data.

### Authentication Setup

1. Create dedicated database users
2. Configure role-based permissions
3. Enable SSL connections
4. Set up connection pooling

### Firewall Rules

Configure your firewall to allow database connections:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 5432
```

## Performance Optimization

Optimize your database performance with these techniques:

### Indexing Strategy

Create indexes on frequently queried columns:

```sql
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_date ON orders(created_at);
```

### Query Optimization

Use EXPLAIN to analyze query performance:

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';
```

## Backup and Recovery

Implement a robust backup strategy:

### Automated Backups

Set up automated daily backups:

```bash
#!/bin/bash
pg_dump myapp > backup_$(date +%Y%m%d).sql
```

### Recovery Procedures

Test your recovery procedures regularly to ensure data integrity.
"""

        log_test_result("📤 Processing content without Introduction section...")
        
        # Process the content through the Knowledge Engine
        response = requests.post(
            f"{API_BASE}/content/process-text",
            json={"content": test_content},
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
        
        log_test_result(f"✅ Content processing started, Job ID: {job_id}")
        
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
                    
                    time.sleep(10)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ No introduction section test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def analyze_generated_articles():
    """Analyze generated articles to check for duplication patterns"""
    try:
        log_test_result("🔍 ANALYZING GENERATED ARTICLES FOR DUPLICATION", "CRITICAL")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result(f"❌ Failed to get Content Library: {response.status_code}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = len(articles)
        
        log_test_result(f"📚 Total articles in Content Library: {total_articles}")
        
        # Analyze article types and titles for duplication patterns
        overview_articles = []
        introduction_articles = []
        complete_guide_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            article_type = article.get('article_type', '')
            
            # Check for overview articles
            if 'overview' in title or article_type == 'overview':
                overview_articles.append(article)
            
            # Check for introduction articles
            if 'introduction' in title or 'intro' in title:
                introduction_articles.append(article)
            
            # Check for complete guide articles
            if 'complete' in title and 'guide' in title:
                complete_guide_articles.append(article)
        
        log_test_result(f"📊 ARTICLE TYPE ANALYSIS:")
        log_test_result(f"   📖 Overview articles: {len(overview_articles)}")
        log_test_result(f"   🎯 Introduction articles: {len(introduction_articles)}")
        log_test_result(f"   📚 Complete guide articles: {len(complete_guide_articles)}")
        
        # Check for duplication patterns
        duplication_issues = []
        
        # Look for articles from the same source document
        source_groups = {}
        for article in articles:
            source = article.get('source_document', 'Unknown')
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(article)
        
        for source, source_articles in source_groups.items():
            if len(source_articles) > 1:
                source_overviews = [a for a in source_articles if 'overview' in a.get('title', '').lower()]
                source_intros = [a for a in source_articles if 'introduction' in a.get('title', '').lower()]
                
                if len(source_overviews) > 0 and len(source_intros) > 0:
                    duplication_issues.append({
                        'source': source,
                        'overview_count': len(source_overviews),
                        'intro_count': len(source_intros),
                        'total_articles': len(source_articles)
                    })
                    log_test_result(f"⚠️ POTENTIAL DUPLICATION in {source}: {len(source_overviews)} overviews + {len(source_intros)} intros")
        
        # Show recent articles for detailed analysis
        log_test_result(f"📄 RECENT ARTICLES ANALYSIS:")
        recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
        
        for i, article in enumerate(recent_articles, 1):
            title = article.get('title', 'Untitled')
            article_type = article.get('article_type', 'unknown')
            source = article.get('source_document', 'Unknown')
            created = article.get('created_at', 'unknown')
            
            log_test_result(f"   {i}. {title[:60]}... (Type: {article_type}, Source: {source})")
        
        # Final duplication assessment
        if duplication_issues:
            log_test_result(f"❌ DUPLICATION ISSUES DETECTED: {len(duplication_issues)} sources with potential duplicates", "ERROR")
            for issue in duplication_issues:
                log_test_result(f"   Source: {issue['source']} - {issue['overview_count']} overviews + {issue['intro_count']} intros")
            return False
        else:
            log_test_result(f"✅ NO DUPLICATION ISSUES DETECTED", "SUCCESS")
            return True
        
    except Exception as e:
        log_test_result(f"❌ Article analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_article_duplication_test():
    """Run comprehensive test suite for article duplication fix verification"""
    log_test_result("🚀 STARTING ARTICLE DUPLICATION FIX TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'baseline_check': False,
        'content_with_intro': False,
        'content_without_intro': False,
        'duplication_analysis': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Get baseline
    log_test_result("\nTEST 2: Content Library Baseline")
    baseline_count, baseline_articles = get_content_library_baseline()
    test_results['baseline_check'] = baseline_count >= 0
    
    # Test 3: Content WITH introduction section
    log_test_result("\nTEST 3: CONTENT WITH INTRODUCTION SECTION")
    test_results['content_with_intro'] = test_content_with_introduction_section()
    
    # Test 4: Content WITHOUT introduction section
    log_test_result("\nTEST 4: CONTENT WITHOUT INTRODUCTION SECTION")
    test_results['content_without_intro'] = test_content_without_introduction_section()
    
    # Test 5: Analyze for duplication
    log_test_result("\nTEST 5: DUPLICATION ANALYSIS")
    test_results['duplication_analysis'] = analyze_generated_articles()
    
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
    
    if test_results['duplication_analysis']:
        log_test_result("🎉 CRITICAL SUCCESS: Article duplication fix is working correctly!", "CRITICAL_SUCCESS")
        log_test_result("✅ No duplicate overview articles detected when introduction content exists", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Article duplication issues still present", "CRITICAL_ERROR")
        log_test_result("❌ System is still creating both Introduction and Overview articles", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Article Duplication Fix Testing")
    print("=" * 50)
    
    results = run_article_duplication_test()
    
    # Exit with appropriate code
    if results['duplication_analysis']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure