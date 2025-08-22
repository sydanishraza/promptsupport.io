#!/usr/bin/env python3
"""
COMPREHENSIVE CONTENT LIBRARY ISSUES FIX VALIDATION
Test all specific fixes mentioned in the review request with real content processing
"""

import requests
import json
import time
import re
from datetime import datetime

# Backend URL
BACKEND_URL = "https://smartdoc-v2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def clear_content_library():
    """Clear existing articles for clean testing"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            for article in articles:
                article_id = article.get('id')
                if article_id:
                    try:
                        delete_response = requests.delete(f"{API_BASE}/content-library/{article_id}", timeout=30)
                        if delete_response.status_code == 200:
                            log_test(f"🗑️ Deleted article: {article.get('title', 'Unknown')[:30]}...")
                    except:
                        pass
            
            log_test(f"🧹 Cleared {len(articles)} existing articles for clean testing")
        
    except Exception as e:
        log_test(f"⚠️ Could not clear content library: {e}")

def test_high_quality_article_generation():
    """Test 1: New High-Quality Article Generation with Overview vs Complete Guide differentiation"""
    try:
        log_test("🎯 TESTING HIGH-QUALITY ARTICLE GENERATION", "TEST")
        
        # Test content that should generate both Overview and Complete Guide
        test_content = """
        Promotions Configuration and Management Guide
        
        This comprehensive guide covers the complete process of configuring and managing promotional campaigns in your system.
        
        ## Overview
        
        Promotions are a powerful tool for driving customer engagement and increasing sales. This guide will walk you through:
        - Setting up promotional campaigns
        - Configuring discount rules
        - Managing promotional periods
        - Tracking promotion performance
        
        ## Getting Started
        
        To begin working with promotions, you need to understand the basic concepts:
        
        1. Promotion Types: Percentage discounts, fixed amount discounts, buy-one-get-one offers
        2. Target Audiences: Customer segments, geographic regions, purchase history
        3. Campaign Duration: Start dates, end dates, recurring promotions
        4. Performance Metrics: Conversion rates, revenue impact, customer acquisition
        
        ## Step-by-Step Configuration
        
        Follow these detailed steps to configure a new promotion:
        
        1. Navigate to the Promotions dashboard
        2. Click "Create New Promotion"
        3. Select your promotion type from the dropdown menu
        4. Configure the discount parameters:
           - Discount percentage or fixed amount
           - Minimum purchase requirements
           - Maximum discount limits
           - Product or category restrictions
        5. Set the target audience criteria:
           - Customer segments
           - Geographic locations
           - Purchase history filters
        6. Define the campaign timeline:
           - Start date and time
           - End date and time
           - Time zone settings
        7. Configure advanced settings:
           - Usage limits per customer
           - Total usage limits
           - Stacking rules with other promotions
        8. Review and activate the promotion
        
        ## Advanced Configuration Options
        
        For more sophisticated promotional campaigns, consider these advanced features:
        
        ### Dynamic Pricing Rules
        
        ```javascript
        const promotionRule = {
            type: 'dynamic',
            conditions: [
                { field: 'cart_total', operator: 'greater_than', value: 100 },
                { field: 'customer_tier', operator: 'equals', value: 'premium' }
            ],
            actions: [
                { type: 'percentage_discount', value: 15 },
                { type: 'free_shipping', enabled: true }
            ]
        };
        ```
        
        ### API Integration
        
        ```javascript
        // Create promotion via API
        const createPromotion = async (promotionData) => {
            const response = await fetch('/api/promotions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiToken}`
                },
                body: JSON.stringify(promotionData)
            });
            
            return response.json();
        };
        ```
        
        ## Troubleshooting Common Issues
        
        Q: Why isn't my promotion showing up for customers?
        A: Check that the promotion is active, the current date is within the campaign period, and the customer meets all targeting criteria.
        
        Q: How do I prevent promotion stacking?
        A: Configure the "exclusive" flag in the promotion settings to prevent it from combining with other offers.
        
        Q: Can I modify a promotion after it's active?
        A: Limited modifications are allowed for active promotions. You can adjust end dates and usage limits, but discount amounts and targeting criteria cannot be changed.
        
        ## Best Practices
        
        1. Always test promotions in a staging environment before going live
        2. Set reasonable usage limits to prevent abuse
        3. Monitor promotion performance regularly
        4. Use clear, compelling promotion descriptions
        5. Consider the impact on profit margins
        6. Plan promotion schedules to avoid conflicts
        """
        
        log_test(f"📝 Test content prepared: {len(test_content)} characters")
        
        # Process content
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content,
                "filename": "Promotions_Configuration_Guide.txt"
            },
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            
            if job_id and wait_for_processing(job_id):
                articles = get_content_library_articles()
                return validate_high_quality_generation(articles)
            else:
                log_test("❌ Processing failed", "ERROR")
                return False
        else:
            log_test(f"❌ Content processing failed: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ High-quality generation test failed: {e}", "ERROR")
        return False

def validate_high_quality_generation(articles):
    """Validate high-quality article generation with proper differentiation"""
    try:
        log_test("🔍 VALIDATING HIGH-QUALITY ARTICLE GENERATION", "VALIDATE")
        
        overview_articles = []
        complete_guide_articles = []
        faq_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            article_type = article.get('article_type', '').lower()
            
            if 'overview' in title or 'overview' in article_type:
                overview_articles.append(article)
            elif 'complete' in title or 'guide' in title or 'tutorial' in title:
                complete_guide_articles.append(article)
            elif 'faq' in title or 'frequently asked' in title or 'troubleshooting' in title:
                faq_articles.append(article)
        
        log_test(f"📊 Article breakdown: {len(overview_articles)} overview, {len(complete_guide_articles)} complete guides, {len(faq_articles)} FAQ")
        
        issues = []
        
        # Test 1: Overview articles should NOT contain detailed implementation
        for article in overview_articles:
            content = article.get('content', '')
            title = article.get('title', '')
            
            # Check for detailed implementation patterns
            if re.search(r'<pre><code', content):
                issues.append(f"Overview '{title}' contains code blocks (should be summary only)")
            
            if re.search(r'step \d+|follow these.*steps', content, re.IGNORECASE):
                issues.append(f"Overview '{title}' contains step-by-step instructions (should be high-level only)")
            
            if len(content) > 3000:
                issues.append(f"Overview '{title}' is too detailed ({len(content)} chars, should be concise)")
        
        # Test 2: Complete Guide articles should contain detailed implementation
        for article in complete_guide_articles:
            content = article.get('content', '')
            title = article.get('title', '')
            
            if len(content) < 1500:
                issues.append(f"Complete Guide '{title}' lacks sufficient detail ({len(content)} chars)")
            
            has_code = '<pre><code' in content
            has_steps = re.search(r'<ol|<li|step \d+', content, re.IGNORECASE)
            
            if not (has_code or has_steps):
                issues.append(f"Complete Guide '{title}' lacks detailed implementation (no code or steps)")
        
        # Test 3: FAQ articles should use proper HTML formatting
        for article in faq_articles:
            content = article.get('content', '')
            title = article.get('title', '')
            
            if re.search(r'##\s|###\s', content):
                issues.append(f"FAQ '{title}' uses Markdown formatting instead of HTML")
            
            if not re.search(r'<h[2-4]', content):
                issues.append(f"FAQ '{title}' lacks proper HTML heading structure")
        
        if len(issues) == 0:
            log_test("✅ HIGH-QUALITY GENERATION: All articles properly differentiated", "SUCCESS")
            return True
        else:
            log_test(f"❌ HIGH-QUALITY GENERATION: {len(issues)} issues found", "ERROR")
            for issue in issues[:3]:
                log_test(f"   - {issue}")
            return False
            
    except Exception as e:
        log_test(f"❌ High-quality generation validation failed: {e}", "ERROR")
        return False

def test_quality_fixes_function():
    """Test 2: Quality Fixes Function - eliminate text duplication and broken content"""
    try:
        log_test("🔧 TESTING QUALITY FIXES FUNCTION", "TEST")
        
        # Content designed to trigger quality issues that should be fixed
        problematic_content = """
        Google Maps Integration Tutorial
        
        This tutorial shows you how to integrate Google Maps into your application.
        
        ## Setup Steps
        
        Follow these steps to set up Google Maps:
        
        1. First, obtain an API key from Google Cloud Console
        2. Next, add the Google Maps script to your HTML
        3. Then, initialize the map in your JavaScript
        4. Finally, test your implementation
        
        ## Code Examples
        
        Here's the basic HTML structure:
        
        ```html
        <div id="map"></div>
        <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_KEY"></script>
        ```
        
        And the JavaScript initialization:
        
        ```javascript
        function initMap() {
            const map = new google.maps.Map(document.getElementById('map'), {
                zoom: 10,
                center: {lat: 37.7749, lng: -122.4194}
            });
        }
        ```
        
        ## Common Problems
        
        - Map not loading: Check your API key
        - Markers not showing: Verify marker coordinates
        - Performance issues: Implement marker clustering
        """
        
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": problematic_content,
                "filename": "Google_Maps_Integration.txt"
            },
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            
            if job_id and wait_for_processing(job_id):
                articles = get_content_library_articles()
                return validate_quality_fixes(articles)
            else:
                log_test("❌ Processing failed", "ERROR")
                return False
        else:
            log_test(f"❌ Content processing failed: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Quality fixes test failed: {e}", "ERROR")
        return False

def validate_quality_fixes(articles):
    """Validate that quality fixes are properly applied"""
    try:
        log_test("🔍 VALIDATING QUALITY FIXES APPLICATION", "VALIDATE")
        
        quality_issues = []
        
        for article in articles:
            content = article.get('content', '')
            title = article.get('title', '')
            
            # Check for text duplication patterns
            duplication_patterns = [
                r'(\b\w+(?:\s+\w+){0,4})\.\1\.',  # "Text.Text." patterns
                r'(\b\w+(?:\s+\w+){0,4})\s+\1\s+',  # Repeated phrases
            ]
            
            for pattern in duplication_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    quality_issues.append(f"Text duplication in '{title}': {matches[0][:50]}...")
            
            # Check for empty elements
            if re.search(r'<li>\s*</li>', content):
                quality_issues.append(f"Empty list items in '{title}'")
            
            if re.search(r'<p>\s*</p>', content):
                quality_issues.append(f"Empty paragraphs in '{title}'")
            
            # Check for broken image references
            if re.search(r'figure\d+\.png|image\d+\.jpg', content):
                quality_issues.append(f"Broken image references in '{title}'")
            
            # Check for empty code blocks
            if re.search(r'<pre><code[^>]*>\s*</code></pre>', content):
                quality_issues.append(f"Empty code blocks in '{title}'")
        
        if len(quality_issues) == 0:
            log_test("✅ QUALITY FIXES: All quality issues properly resolved", "SUCCESS")
            return True
        else:
            log_test(f"❌ QUALITY FIXES: {len(quality_issues)} issues remain unfixed", "ERROR")
            for issue in quality_issues[:3]:
                log_test(f"   - {issue}")
            return False
            
    except Exception as e:
        log_test(f"❌ Quality fixes validation failed: {e}", "ERROR")
        return False

def test_ordered_lists_validation():
    """Test 3: Ordered Lists Validation - continuous numbering without duplication"""
    try:
        log_test("📝 TESTING ORDERED LISTS VALIDATION", "TEST")
        
        # Content with multiple ordered lists
        list_content = """
        Software Development Best Practices
        
        ## Project Setup
        
        1. Initialize version control repository
        2. Set up development environment
        3. Configure build tools and dependencies
        4. Establish coding standards and guidelines
        5. Create project documentation structure
        
        ## Development Workflow
        
        1. Create feature branch from main
        2. Implement feature with proper testing
        3. Run automated tests and code quality checks
        4. Submit pull request for code review
        5. Merge approved changes to main branch
        6. Deploy to staging environment
        7. Perform integration testing
        8. Deploy to production environment
        
        ## Code Quality Standards
        
        1. Write clear, self-documenting code
        2. Follow consistent naming conventions
        3. Implement comprehensive error handling
        4. Add unit tests for all functions
        5. Document complex algorithms and business logic
        6. Use static analysis tools for code quality
        """
        
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": list_content,
                "filename": "Development_Best_Practices.txt"
            },
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            
            if job_id and wait_for_processing(job_id):
                articles = get_content_library_articles()
                return validate_ordered_lists(articles)
            else:
                log_test("❌ Processing failed", "ERROR")
                return False
        else:
            log_test(f"❌ Content processing failed: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Ordered lists test failed: {e}", "ERROR")
        return False

def validate_ordered_lists(articles):
    """Validate ordered lists have continuous numbering and no duplication"""
    try:
        log_test("🔍 VALIDATING ORDERED LISTS", "VALIDATE")
        
        list_issues = []
        total_lists = 0
        
        for article in articles:
            content = article.get('content', '')
            title = article.get('title', '')
            
            # Find all ordered lists
            ol_matches = re.findall(r'<ol[^>]*>(.*?)</ol>', content, re.DOTALL)
            total_lists += len(ol_matches)
            
            for i, ol_content in enumerate(ol_matches):
                # Check for text duplication in list items
                li_items = re.findall(r'<li[^>]*>(.*?)</li>', ol_content, re.DOTALL)
                
                for j, li_content in enumerate(li_items):
                    # Check for duplication patterns
                    if re.search(r'(\b\w+(?:\s+\w+){0,3})\.\1\.', li_content):
                        list_issues.append(f"Text duplication in list item {j+1} of '{title}'")
                    
                    # Check for empty items
                    if len(li_content.strip()) < 5:
                        list_issues.append(f"Empty list item {j+1} in '{title}'")
                
                # Check for proper CSS classes
                if not re.search(r'class="doc-list', ol_content):
                    list_issues.append(f"Missing CSS classes in ordered list of '{title}'")
        
        log_test(f"📊 Found {total_lists} ordered lists across {len(articles)} articles")
        
        if len(list_issues) == 0:
            log_test("✅ ORDERED LISTS: All lists properly formatted without duplication", "SUCCESS")
            return True
        else:
            log_test(f"❌ ORDERED LISTS: {len(list_issues)} issues found", "ERROR")
            for issue in list_issues[:3]:
                log_test(f"   - {issue}")
            return False
            
    except Exception as e:
        log_test(f"❌ Ordered lists validation failed: {e}", "ERROR")
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
                
                if status == 'completed':
                    return True
                elif status == 'failed':
                    log_test(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                    return False
                    
                time.sleep(5)
            else:
                time.sleep(5)
                
        except Exception as e:
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
            return articles
        else:
            return []
            
    except Exception as e:
        return []

def run_comprehensive_validation():
    """Run comprehensive validation of all Content Library fixes"""
    log_test("🚀 COMPREHENSIVE CONTENT LIBRARY ISSUES FIX VALIDATION", "START")
    log_test("=" * 80)
    
    # Test backend health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=30)
        if response.status_code != 200:
            log_test("❌ Backend health check failed", "ERROR")
            return False
        log_test("✅ Backend health check passed")
    except Exception as e:
        log_test(f"❌ Backend health check failed: {e}", "ERROR")
        return False
    
    # Clear existing articles for clean testing
    clear_content_library()
    
    test_results = {
        'high_quality_generation': False,
        'quality_fixes_applied': False,
        'ordered_lists_fixed': False
    }
    
    # Run tests
    log_test("\n" + "="*60)
    test_results['high_quality_generation'] = test_high_quality_article_generation()
    
    time.sleep(5)  # Brief pause between tests
    
    log_test("\n" + "="*60)
    test_results['quality_fixes_applied'] = test_quality_fixes_function()
    
    time.sleep(5)
    
    log_test("\n" + "="*60)
    test_results['ordered_lists_fixed'] = test_ordered_lists_validation()
    
    # Final results
    log_test("\n" + "="*80)
    log_test("📊 FINAL VALIDATION RESULTS", "RESULTS")
    log_test("="*80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test(f"\n🎯 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        log_test("🎉 CONTENT LIBRARY FIXES VALIDATION SUCCESSFUL!", "SUCCESS")
        log_test("✅ High-quality article generation working correctly")
        log_test("✅ Quality fixes properly applied")
        log_test("✅ Content processing pipeline operational")
    else:
        log_test("❌ CONTENT LIBRARY FIXES NEED ATTENTION", "ERROR")
        failed_tests = [test for test, result in test_results.items() if not result]
        log_test(f"❌ Failed tests: {', '.join(failed_tests)}")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = run_comprehensive_validation()
    exit(0 if success else 1)