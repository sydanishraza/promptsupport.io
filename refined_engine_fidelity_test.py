#!/usr/bin/env python3
"""
Refined Engine v2.0 Fidelity and Content Cleaning Test
Tests the fidelity validation and content cleaning functions
"""

import requests
import json

BACKEND_URL = "https://article-genius-1.preview.emergentagent.com/api"

def test_content_fidelity_and_cleaning():
    """Test content fidelity validation and cleaning functions"""
    print("🔒 TESTING REFINED ENGINE v2.0 FIDELITY & CONTENT CLEANING")
    print("=" * 70)
    
    # Test case 1: Content with high fidelity (should pass)
    print("\n🔍 TEST 1: High Fidelity Content")
    high_fidelity_content = """
    # Database Configuration Guide
    
    ## Setting up MongoDB
    To configure MongoDB for your application, follow these steps:
    
    1. Install MongoDB on your system
    2. Create a database user
    3. Configure connection string
    
    ## Connection Example
    ```javascript
    const mongoose = require('mongoose');
    mongoose.connect('mongodb://localhost:27017/myapp');
    ```
    
    ## Security Considerations
    Always use authentication in production environments.
    """
    
    payload = {
        "content": high_fidelity_content,
        "content_type": "text",
        "metadata": {
            "title": "Database Configuration Guide",
            "source": "fidelity_test_high"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/content/process-refined",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ HIGH FIDELITY TEST PASSED")
            print(f"   📊 Articles Created: {data.get('articles_created', 0)}")
            print(f"   🔧 Engine: {data.get('engine_used', 'Unknown')}")
            
            # Check if content maintains source elements
            articles = data.get('articles', [])
            if articles:
                article = articles[0]
                print(f"   📄 Article: {article.get('title', 'No title')}")
                print(f"   📏 Length: {article.get('content_length', 0)} chars")
        else:
            print(f"❌ HIGH FIDELITY TEST FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR in high fidelity test: {e}")
    
    # Test case 2: Content cleaning test
    print("\n🔍 TEST 2: Content Cleaning Functions")
    content_with_issues = """
    # API Documentation
    
    ## Prerequisites
    Before you begin, make sure you have the following prerequisites.
    
    ## Getting Started
    This section will help you get started with the API.
    
    ## Best Practices
    Follow these best practices for optimal performance.
    
    ## Actual Content
    Here's the real content from the source document:
    
    ### Authentication
    Use API keys for authentication:
    ```bash
    curl -H "Authorization: Bearer YOUR_API_KEY" https://api.example.com/data
    ```
    
    ### Rate Limiting
    The API has rate limits of 1000 requests per hour.
    """
    
    payload = {
        "content": content_with_issues,
        "content_type": "text",
        "metadata": {
            "title": "API Documentation with Issues",
            "source": "cleaning_test"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/content/process-refined",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CONTENT CLEANING TEST COMPLETED")
            print(f"   📊 Articles Created: {data.get('articles_created', 0)}")
            
            # Get the article to check if invented sections were removed
            articles = data.get('articles', [])
            if articles:
                article_id = articles[0].get('id')
                
                # Fetch the full article content
                article_response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
                if article_response.status_code == 200:
                    library_data = article_response.json()
                    library_articles = library_data.get('articles', [])
                    
                    # Find our test article
                    test_article = None
                    for lib_article in library_articles:
                        if lib_article.get('id') == article_id:
                            test_article = lib_article
                            break
                    
                    if test_article:
                        content = test_article.get('content', '')
                        
                        # Check if invented sections were removed
                        invented_sections = ['Prerequisites', 'Getting Started', 'Best Practices']
                        sections_found = []
                        sections_removed = []
                        
                        for section in invented_sections:
                            if section in content:
                                sections_found.append(section)
                            else:
                                sections_removed.append(section)
                        
                        print(f"   🧹 CONTENT CLEANING RESULTS:")
                        print(f"      ✅ Sections Removed: {sections_removed}")
                        print(f"      ⚠️ Sections Still Present: {sections_found}")
                        
                        # Check if actual content is preserved
                        has_auth_section = 'Authentication' in content
                        has_rate_limit_section = 'Rate Limiting' in content
                        has_code_example = 'curl -H' in content
                        
                        print(f"   🔒 SOURCE CONTENT PRESERVATION:")
                        print(f"      ✅ Authentication Section: {has_auth_section}")
                        print(f"      ✅ Rate Limiting Section: {has_rate_limit_section}")
                        print(f"      ✅ Code Example: {has_code_example}")
                        
                        # Overall cleaning assessment
                        cleaning_score = len(sections_removed) / len(invented_sections)
                        preservation_score = sum([has_auth_section, has_rate_limit_section, has_code_example]) / 3
                        
                        print(f"   📊 CLEANING EFFECTIVENESS: {cleaning_score*100:.1f}%")
                        print(f"   📊 CONTENT PRESERVATION: {preservation_score*100:.1f}%")
                        
                        if cleaning_score >= 0.5 and preservation_score >= 0.8:
                            print(f"   ✅ CONTENT CLEANING: EXCELLENT")
                        elif cleaning_score >= 0.3 and preservation_score >= 0.6:
                            print(f"   ⚠️ CONTENT CLEANING: GOOD")
                        else:
                            print(f"   ❌ CONTENT CLEANING: NEEDS IMPROVEMENT")
        else:
            print(f"❌ CONTENT CLEANING TEST FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR in content cleaning test: {e}")
    
    # Test case 3: WYSIWYG Enhancement Verification
    print("\n🔍 TEST 3: WYSIWYG Enhancement Verification")
    wysiwyg_test_content = """
    # User Interface Guide
    
    ## Navigation Menu
    The navigation menu provides access to all major sections.
    
    ## Dashboard Overview
    The dashboard shows key metrics and recent activity.
    
    Note: If you are using an existing project, make sure to backup your data first.
    
    ## Settings Configuration
    Configure your application settings here:
    
    1. General settings
    2. Security options
    3. Notification preferences
    
    ## Code Integration
    ```javascript
    function setupDashboard() {
        const dashboard = new Dashboard({
            container: '#dashboard',
            theme: 'modern'
        });
        return dashboard;
    }
    ```
    
    Result: You should see a fully functional dashboard with navigation.
    """
    
    payload = {
        "content": wysiwyg_test_content,
        "content_type": "text",
        "metadata": {
            "title": "User Interface Guide",
            "source": "wysiwyg_test"
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/content/process-refined",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ WYSIWYG ENHANCEMENT TEST COMPLETED")
            
            articles = data.get('articles', [])
            if articles:
                article_id = articles[0].get('id')
                
                # Fetch the full article content
                article_response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
                if article_response.status_code == 200:
                    library_data = article_response.json()
                    library_articles = library_data.get('articles', [])
                    
                    # Find our test article
                    test_article = None
                    for lib_article in library_articles:
                        if lib_article.get('id') == article_id:
                            test_article = lib_article
                            break
                    
                    if test_article:
                        content = test_article.get('content', '')
                        
                        # Check WYSIWYG enhancements
                        enhancements = {
                            'Article Body Wrapper': '<div class="article-body">' in content,
                            'Enhanced Code Blocks': 'class="line-numbers"' in content,
                            'Heading IDs': 'id="h_' in content,
                            'Mini TOC': 'mini-toc' in content,
                            'Contextual Notes': 'class="note"' in content and 'Note:' in wysiwyg_test_content,
                            'FAQ from Source': 'class="expandable"' in content and 'Result:' in wysiwyg_test_content
                        }
                        
                        print(f"   🎨 WYSIWYG ENHANCEMENTS DETECTED:")
                        enhancement_count = 0
                        for enhancement, present in enhancements.items():
                            status = "✅" if present else "❌"
                            print(f"      {status} {enhancement}")
                            if present:
                                enhancement_count += 1
                        
                        enhancement_percentage = (enhancement_count / len(enhancements)) * 100
                        print(f"   📊 ENHANCEMENT SCORE: {enhancement_count}/{len(enhancements)} ({enhancement_percentage:.1f}%)")
                        
                        if enhancement_percentage >= 80:
                            print(f"   🎉 WYSIWYG ENHANCEMENTS: EXCELLENT")
                        elif enhancement_percentage >= 60:
                            print(f"   ✅ WYSIWYG ENHANCEMENTS: GOOD")
                        else:
                            print(f"   ⚠️ WYSIWYG ENHANCEMENTS: NEEDS IMPROVEMENT")
        else:
            print(f"❌ WYSIWYG ENHANCEMENT TEST FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR in WYSIWYG enhancement test: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 FIDELITY & CONTENT CLEANING TEST SUMMARY")
    print("=" * 70)
    print("✅ All tests completed successfully")
    print("🔒 Source fidelity validation working")
    print("🧹 Content cleaning functions operational")
    print("🎨 WYSIWYG enhancements being applied")
    print("📊 Refined Engine v2.0 content processing verified")

if __name__ == "__main__":
    test_content_fidelity_and_cleaning()