#!/usr/bin/env python3
"""
DOCX Content Field Fix Verification - Focused Testing
Testing that the V2PublishingSystem._create_content_library_article() fix is working correctly
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_content_field_fix():
    """Test the content field fix with a new article"""
    print("🎯 TESTING CONTENT FIELD FIX VERIFICATION")
    
    # Test content that simulates DOCX processing
    test_content = """
    <h1>Google Maps JavaScript API Tutorial - Content Field Fix Test</h1>
    <p>This comprehensive tutorial demonstrates the Google Maps JavaScript API implementation with proper content field population.</p>
    
    <h2>Overview</h2>
    <p>The Google Maps JavaScript API allows developers to embed interactive maps in web applications.</p>
    
    <h3>Key Features</h3>
    <ul>
        <li>Interactive map display</li>
        <li>Custom markers and overlays</li>
        <li>Geocoding and reverse geocoding</li>
        <li>Street View integration</li>
    </ul>
    
    <h2>Getting Started</h2>
    <p>To begin using the Google Maps JavaScript API, follow these steps:</p>
    
    <h3>Step 1: Obtain API Key</h3>
    <p>Visit the Google Cloud Console and create a new project or select an existing one.</p>
    
    <h3>Step 2: Enable the API</h3>
    <p>Navigate to the API Library and enable the Maps JavaScript API.</p>
    
    <h2>Implementation</h2>
    <p>Here's a basic implementation example:</p>
    
    <pre><code>
    function initMap() {
        const map = new google.maps.Map(document.getElementById("map"), {
            zoom: 10,
            center: { lat: 37.7749, lng: -122.4194 },
        });
        
        const marker = new google.maps.Marker({
            position: { lat: 37.7749, lng: -122.4194 },
            map: map,
            title: "San Francisco"
        });
    }
    </code></pre>
    
    <h2>Advanced Features</h2>
    <p>The API provides numerous advanced features for enhanced functionality.</p>
    
    <h3>Custom Styling</h3>
    <p>You can customize the map appearance using style arrays.</p>
    
    <h3>Event Handling</h3>
    <p>Add event listeners to handle user interactions with the map.</p>
    
    <h2>Best Practices</h2>
    <p>Follow these best practices for optimal performance:</p>
    <ul>
        <li>Use API keys with proper restrictions</li>
        <li>Implement error handling</li>
        <li>Optimize marker clustering for large datasets</li>
        <li>Use lazy loading for better page performance</li>
    </ul>
    
    <h2>Troubleshooting</h2>
    <p>Common issues and their solutions:</p>
    
    <h3>Map Not Loading</h3>
    <p>Check your API key and ensure the Maps JavaScript API is enabled.</p>
    
    <h3>Quota Exceeded</h3>
    <p>Monitor your API usage and consider implementing caching strategies.</p>
    """
    
    # Process the content
    payload = {
        "content": test_content,
        "metadata": {
            "original_filename": "Google_Maps_API_Tutorial_Content_Fix_Test.docx",
            "file_extension": ".docx",
            "content_type": "tutorial",
            "test_scenario": "content_field_fix_verification",
            "test_timestamp": datetime.utcnow().isoformat()
        }
    }
    
    print("📤 Sending content for V2 processing...")
    response = requests.post(f"{API_BASE}/content/process", 
                           json=payload, 
                           timeout=60)
    
    if response.status_code != 200:
        print(f"❌ Processing failed: {response.status_code} - {response.text}")
        return False
    
    result = response.json()
    job_id = result.get('job_id')
    print(f"✅ Processing started: Job ID {job_id}")
    
    # Wait for processing to complete
    print("⏳ Waiting for processing to complete...")
    time.sleep(8)
    
    # Check the content library for the new article
    print("📚 Checking content library for new article...")
    library_response = requests.get(f"{API_BASE}/content-library?limit=10", timeout=30)
    
    if library_response.status_code != 200:
        print(f"❌ Content library check failed: {library_response.status_code}")
        return False
    
    library_data = library_response.json()
    articles = library_data.get('articles', [])
    
    # Find the test article
    test_article = None
    for article in articles:
        if 'Content Field Fix Test' in article.get('title', ''):
            test_article = article
            break
    
    if not test_article:
        print("❌ Test article not found in content library")
        return False
    
    # Verify the content field fix
    print(f"🔍 Analyzing article: {test_article['title']}")
    
    content_field = test_article.get('content', '')
    html_field = test_article.get('html', '')
    markdown_field = test_article.get('markdown', '')
    
    print(f"📊 Content field length: {len(content_field)} characters")
    print(f"📊 HTML field length: {len(html_field)} characters")
    print(f"📊 Markdown field length: {len(markdown_field)} characters")
    
    # Critical tests
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Content field is not empty
    if content_field and len(content_field.strip()) > 0:
        print("✅ Test 1 PASSED: Content field is populated")
        tests_passed += 1
    else:
        print("❌ Test 1 FAILED: Content field is empty")
    
    # Test 2: Content field matches HTML field
    if content_field == html_field:
        print("✅ Test 2 PASSED: Content field matches HTML field")
        tests_passed += 1
    else:
        print("❌ Test 2 FAILED: Content field does not match HTML field")
    
    # Test 3: HTML field has substantial content
    if html_field and len(html_field.strip()) > 500:
        print("✅ Test 3 PASSED: HTML field has substantial content")
        tests_passed += 1
    else:
        print("❌ Test 3 FAILED: HTML field lacks substantial content")
    
    # Test 4: Article has V2 engine metadata
    engine = test_article.get('engine', '')
    if engine == 'v2':
        print("✅ Test 4 PASSED: Article has V2 engine metadata")
        tests_passed += 1
    else:
        print(f"❌ Test 4 FAILED: Article has incorrect engine metadata: {engine}")
    
    # Calculate success rate
    success_rate = (tests_passed / total_tests) * 100
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Tests passed: {tests_passed}/{total_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    
    # Verify fix status
    fix_successful = (tests_passed >= 3 and content_field == html_field and len(content_field) > 0)
    
    print(f"\n🎯 CONTENT FIELD FIX STATUS:")
    if fix_successful:
        print("✅ CONTENT FIELD FIX VERIFIED SUCCESSFULLY")
        print("   - Content field is properly populated")
        print("   - Content field matches HTML field")
        print("   - V2 publishing system is working correctly")
    else:
        print("❌ CONTENT FIELD FIX VERIFICATION FAILED")
        print("   - Fix may not be working as expected")
    
    return fix_successful

def test_existing_article_comparison():
    """Compare old vs new articles to show the fix"""
    print("\n🔍 COMPARING OLD VS NEW ARTICLES")
    
    library_response = requests.get(f"{API_BASE}/content-library?limit=10", timeout=30)
    if library_response.status_code != 200:
        print("❌ Could not retrieve articles for comparison")
        return
    
    articles = library_response.json().get('articles', [])
    
    old_articles = []
    new_articles = []
    
    for article in articles:
        content_field = article.get('content', '')
        html_field = article.get('html', '')
        
        if len(content_field) == 0 and len(html_field) > 0:
            old_articles.append(article)
        elif len(content_field) > 0 and content_field == html_field:
            new_articles.append(article)
    
    print(f"📊 Found {len(old_articles)} articles with empty content field (old bug)")
    print(f"📊 Found {len(new_articles)} articles with populated content field (fix applied)")
    
    if old_articles:
        old_article = old_articles[0]
        print(f"\n❌ OLD ARTICLE (Bug present): {old_article['title'][:50]}...")
        print(f"   Content field: {len(old_article.get('content', ''))} chars")
        print(f"   HTML field: {len(old_article.get('html', ''))} chars")
        print(f"   Content populated: {'No' if len(old_article.get('content', '')) == 0 else 'Yes'}")
    
    if new_articles:
        new_article = new_articles[0]
        print(f"\n✅ NEW ARTICLE (Fix applied): {new_article['title'][:50]}...")
        print(f"   Content field: {len(new_article.get('content', ''))} chars")
        print(f"   HTML field: {len(new_article.get('html', ''))} chars")
        print(f"   Content populated: {'Yes' if len(new_article.get('content', '')) > 0 else 'No'}")
        print(f"   Fields match: {'Yes' if new_article.get('content') == new_article.get('html') else 'No'}")

if __name__ == "__main__":
    print("🚀 DOCX CONTENT FIELD FIX VERIFICATION")
    print("="*60)
    
    # Test the fix with new content
    fix_verified = test_content_field_fix()
    
    # Compare old vs new articles
    test_existing_article_comparison()
    
    print("\n" + "="*60)
    print("🎯 FINAL VERIFICATION RESULT:")
    if fix_verified:
        print("✅ CONTENT FIELD FIX IS WORKING CORRECTLY")
        print("   New articles have properly populated content fields")
        print("   V2PublishingSystem._create_content_library_article() fix verified")
    else:
        print("❌ CONTENT FIELD FIX NEEDS INVESTIGATION")
        print("   Fix may not be working as expected")
    print("="*60)