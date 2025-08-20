#!/usr/bin/env python3
"""
REAL CONTENT LIBRARY ISSUES FIX VALIDATION
Test the actual implementation of fixes using real content processing
"""

import requests
import json
import time
import re
from datetime import datetime

# Backend URL
BACKEND_URL = "https://article-genius-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_real_content_processing():
    """Test real content processing with comprehensive content"""
    try:
        log_test("🔍 TESTING REAL CONTENT PROCESSING WITH QUALITY FIXES", "TEST")
        
        # Create comprehensive test content that should trigger all the fixes
        test_content = """
        Google Maps JavaScript API Tutorial - Complete Implementation Guide
        
        This comprehensive guide covers everything you need to know about implementing Google Maps JavaScript API in your web applications.
        
        ## Getting Started
        
        To get started with Google Maps JavaScript API, you need to follow these steps:
        
        1. First, you need to obtain an API key from Google Cloud Console
        2. Next, include the Google Maps JavaScript API in your HTML
        3. Then, initialize the map with your desired configuration
        4. Finally, add markers and customize your map
        
        ### Step-by-Step Implementation
        
        Here's a detailed step-by-step process:
        
        1. Create a new HTML file with proper structure
        2. Add the Google Maps API script to your HTML head
        3. Initialize the map object in your JavaScript
        4. Configure map options including center and zoom
        5. Add event listeners for user interactions
        6. Test your implementation thoroughly
        
        ## Code Examples
        
        Here's a basic HTML structure:
        
        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Maps Tutorial</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"></script>
        </head>
        <body>
            <div id="map" style="height: 400px;"></div>
        </body>
        </html>
        ```
        
        And here's the JavaScript initialization:
        
        ```javascript
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 10,
                center: { lat: 37.7749, lng: -122.4194 }
            });
            
            const marker = new google.maps.Marker({
                position: { lat: 37.7749, lng: -122.4194 },
                map: map,
                title: "San Francisco"
            });
        }
        ```
        
        ## Advanced Features
        
        The Google Maps API offers many advanced features:
        
        - Custom markers and info windows
        - Geocoding and reverse geocoding
        - Directions and routing services
        - Places API integration
        - Street View integration
        - Drawing tools and overlays
        
        ## Common Issues and Solutions
        
        Q: Why is my map not loading?
        A: Check your API key and ensure it's properly configured in the Google Cloud Console.
        
        Q: How do I add custom markers?
        A: Use the google.maps.Marker constructor with custom icon properties.
        
        Q: Can I customize the map style?
        A: Yes, you can use the styles property in the map options to apply custom styling.
        
        ## Best Practices
        
        When working with Google Maps API, follow these best practices:
        
        1. Always use HTTPS for production applications
        2. Implement proper error handling
        3. Optimize marker clustering for large datasets
        4. Use appropriate zoom levels for your use case
        5. Consider mobile responsiveness
        6. Implement lazy loading for better performance
        """
        
        log_test(f"📝 Test content prepared: {len(test_content)} characters")
        
        # Process content through the backend
        log_test("📤 Sending content for processing...")
        
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content,
                "filename": "Google_Maps_API_Tutorial.txt"
            },
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            
            if job_id:
                log_test(f"✅ Processing started with job ID: {job_id}")
                
                # Wait for processing to complete
                success = wait_for_processing(job_id)
                
                if success:
                    # Check generated articles
                    articles = get_content_library_articles()
                    if articles:
                        log_test(f"✅ REAL CONTENT PROCESSING SUCCESSFUL: {len(articles)} articles generated")
                        return validate_content_quality(articles)
                    else:
                        log_test("❌ No articles found in Content Library after processing", "ERROR")
                        return False
                else:
                    log_test("❌ Processing failed or timed out", "ERROR")
                    return False
            else:
                log_test("❌ No job ID returned from processing", "ERROR")
                return False
        else:
            log_test(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            if response.text:
                log_test(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test(f"❌ Real content processing test failed: {e}", "ERROR")
        return False

def wait_for_processing(job_id, timeout=180):
    """Wait for content processing to complete"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status', 'unknown')
                
                log_test(f"⏳ Processing status: {status}")
                
                if status == 'completed':
                    log_test("✅ Processing completed successfully")
                    return True
                elif status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    log_test(f"❌ Processing failed: {error}", "ERROR")
                    return False
                    
                time.sleep(10)
            else:
                log_test(f"⚠️ Status check failed: {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            log_test(f"⚠️ Error checking status: {e}")
            time.sleep(5)
    
    log_test(f"⏰ Processing timeout after {timeout} seconds", "ERROR")
    return False

def get_content_library_articles():
    """Get articles from Content Library"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            total = data.get('total', 0)
            
            log_test(f"📚 Content Library: {total} total articles, {len(articles)} retrieved")
            return articles
        else:
            log_test(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return []
            
    except Exception as e:
        log_test(f"❌ Error accessing Content Library: {e}", "ERROR")
        return []

def validate_content_quality(articles):
    """Validate the quality fixes in generated articles"""
    try:
        log_test("🔍 VALIDATING CONTENT QUALITY FIXES", "TEST")
        
        validation_results = {
            'ordered_lists_fixed': False,
            'overview_vs_complete_guide': False,
            'faq_standardization': False,
            'wysiwyg_features': False,
            'content_quality': False,
            'no_text_duplication': False,
            'proper_code_blocks': False,
            'enhanced_formatting': False
        }
        
        overview_articles = []
        complete_guide_articles = []
        faq_articles = []
        
        total_ordered_lists = 0
        total_code_blocks = 0
        wysiwyg_features_count = 0
        quality_issues = []
        
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '')
            article_type = article.get('article_type', '').lower()
            
            log_test(f"📄 Analyzing article: {article.get('title', 'Untitled')[:50]}...")
            
            # Categorize articles
            if 'overview' in title or 'overview' in article_type:
                overview_articles.append(article)
            elif 'complete' in title or 'guide' in title or 'tutorial' in title:
                complete_guide_articles.append(article)
            elif 'faq' in title or 'frequently asked' in title or 'faq' in article_type:
                faq_articles.append(article)
            
            # Check for ordered lists
            ol_matches = re.findall(r'<ol[^>]*>(.*?)</ol>', content, re.DOTALL)
            total_ordered_lists += len(ol_matches)
            
            # Check for text duplication in lists
            for ol_content in ol_matches:
                if re.search(r'(\b\w+(?:\s+\w+)*)\.\1\.', ol_content):
                    quality_issues.append(f"Text duplication in '{article.get('title', 'Unknown')}'")
            
            # Check for code blocks
            code_blocks = re.findall(r'<pre><code[^>]*>(.*?)</code></pre>', content, re.DOTALL)
            total_code_blocks += len(code_blocks)
            
            # Check for empty code blocks
            empty_code_blocks = re.findall(r'<pre><code[^>]*>\s*</code></pre>', content)
            if empty_code_blocks:
                quality_issues.append(f"Empty code blocks in '{article.get('title', 'Unknown')}'")
            
            # Check for WYSIWYG features
            if re.search(r'<div[^>]*class="mini-toc"', content):
                wysiwyg_features_count += 1
            if re.search(r'<div[^>]*class="callout', content):
                wysiwyg_features_count += 1
            if re.search(r'<[ou]l[^>]*class="doc-list', content):
                wysiwyg_features_count += 1
            if re.search(r'<[^>]+id="[^"]*"', content):
                wysiwyg_features_count += 1
        
        # Validate results
        log_test("📊 VALIDATION RESULTS:")
        
        # 1. Ordered Lists Fixed
        if total_ordered_lists > 0:
            duplication_issues = [issue for issue in quality_issues if 'duplication' in issue]
            if len(duplication_issues) == 0:
                validation_results['ordered_lists_fixed'] = True
                log_test(f"✅ Ordered Lists: {total_ordered_lists} lists found, no duplication issues")
            else:
                log_test(f"❌ Ordered Lists: {len(duplication_issues)} duplication issues found")
        else:
            log_test("⚠️ Ordered Lists: No ordered lists found to validate")
        
        # 2. Overview vs Complete Guide Separation
        if len(overview_articles) > 0 or len(complete_guide_articles) > 0:
            # Check if overview articles don't have detailed implementation
            overview_issues = 0
            for article in overview_articles:
                content = article.get('content', '')
                if re.search(r'<pre><code|step \d+', content, re.IGNORECASE):
                    overview_issues += 1
            
            # Check if complete guides have substantial content
            guide_issues = 0
            for article in complete_guide_articles:
                content = article.get('content', '')
                if len(content) < 1000:
                    guide_issues += 1
            
            if overview_issues == 0 and guide_issues == 0:
                validation_results['overview_vs_complete_guide'] = True
                log_test(f"✅ Article Separation: {len(overview_articles)} overview, {len(complete_guide_articles)} complete guides - proper separation")
            else:
                log_test(f"❌ Article Separation: {overview_issues} overview issues, {guide_issues} guide issues")
        else:
            log_test("⚠️ Article Separation: No categorized articles found")
        
        # 3. FAQ Standardization
        if len(faq_articles) > 0:
            faq_issues = 0
            for article in faq_articles:
                content = article.get('content', '')
                title = article.get('title', '')
                
                # Check for proper HTML formatting
                if re.search(r'##\s|###\s', content):
                    faq_issues += 1
                
                # Check for proper structure
                if not re.search(r'<h[2-4][^>]*>', content):
                    faq_issues += 1
            
            if faq_issues == 0:
                validation_results['faq_standardization'] = True
                log_test(f"✅ FAQ Standardization: {len(faq_articles)} FAQ articles with proper HTML formatting")
            else:
                log_test(f"❌ FAQ Standardization: {faq_issues} formatting issues found")
        else:
            log_test("⚠️ FAQ Standardization: No FAQ articles found")
        
        # 4. WYSIWYG Features
        if wysiwyg_features_count >= 3:
            validation_results['wysiwyg_features'] = True
            log_test(f"✅ WYSIWYG Features: {wysiwyg_features_count} features found across articles")
        else:
            log_test(f"❌ WYSIWYG Features: Only {wysiwyg_features_count} features found (need at least 3)")
        
        # 5. Content Quality
        if len(quality_issues) == 0:
            validation_results['content_quality'] = True
            log_test("✅ Content Quality: No quality issues detected")
        else:
            log_test(f"❌ Content Quality: {len(quality_issues)} issues found: {'; '.join(quality_issues[:3])}")
        
        # 6. Code Blocks
        if total_code_blocks > 0:
            empty_code_issues = [issue for issue in quality_issues if 'Empty code' in issue]
            if len(empty_code_issues) == 0:
                validation_results['proper_code_blocks'] = True
                log_test(f"✅ Code Blocks: {total_code_blocks} code blocks found, all have content")
            else:
                log_test(f"❌ Code Blocks: {len(empty_code_issues)} empty code blocks found")
        else:
            log_test("⚠️ Code Blocks: No code blocks found to validate")
        
        # Calculate overall success
        passed_validations = sum(validation_results.values())
        total_validations = len(validation_results)
        success_rate = (passed_validations / total_validations) * 100
        
        log_test(f"📈 OVERALL VALIDATION: {passed_validations}/{total_validations} checks passed ({success_rate:.1f}%)")
        
        return success_rate >= 70  # 70% success rate required
        
    except Exception as e:
        log_test(f"❌ Content quality validation failed: {e}", "ERROR")
        return False

def run_comprehensive_test():
    """Run comprehensive Content Library fix validation"""
    log_test("🚀 STARTING REAL CONTENT LIBRARY ISSUES FIX VALIDATION", "START")
    log_test("=" * 80)
    
    # Test backend health first
    try:
        response = requests.get(f"{API_BASE}/health", timeout=30)
        if response.status_code == 200:
            log_test("✅ Backend health check passed")
        else:
            log_test(f"❌ Backend health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_test(f"❌ Backend health check failed: {e}", "ERROR")
        return False
    
    # Run real content processing test
    success = test_real_content_processing()
    
    log_test("=" * 80)
    if success:
        log_test("🎉 CONTENT LIBRARY FIX VALIDATION SUCCESSFUL!", "SUCCESS")
        log_test("✅ High-quality article generation working")
        log_test("✅ Quality fixes applied successfully")
        log_test("✅ Content processing pipeline operational")
    else:
        log_test("❌ CONTENT LIBRARY FIX VALIDATION FAILED", "ERROR")
        log_test("❌ Some fixes need attention")
    
    return success

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)