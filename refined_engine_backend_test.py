#!/usr/bin/env python3
"""
Refined PromptSupport Engine v2.0 Backend Testing
Tests the new refined engine endpoints and functionality
"""

import asyncio
import json
import requests
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://content-pipeline-5.preview.emergentagent.com/api"

def test_refined_engine_endpoints():
    """Test the new Refined Engine v2.0 endpoints"""
    print("🆕 TESTING REFINED PROMPTSUPPORT ENGINE v2.0")
    print("=" * 60)
    
    results = {
        "process_refined_endpoint": False,
        "upload_refined_endpoint": False,
        "content_processing": False,
        "multi_dimensional_analysis": False,
        "granularity_decision": False,
        "wysiwyg_enhancements": False,
        "content_validation": False,
        "database_storage": False,
        "metadata_verification": False
    }
    
    # Test 1: POST /api/content/process-refined endpoint
    print("\n🔍 TEST 1: Testing /api/content/process-refined endpoint")
    try:
        # Sample content for testing - Google Maps API Tutorial
        test_content = """
        # Google Maps JavaScript API Tutorial

        ## Introduction
        This tutorial will guide you through integrating the Google Maps JavaScript API into your web application.

        ## Prerequisites
        - Basic knowledge of HTML, CSS, and JavaScript
        - A Google Cloud Platform account
        - An API key for Google Maps JavaScript API

        ## Step 1: Get Your API Key
        1. Go to the Google Cloud Console
        2. Create a new project or select an existing one
        3. Enable the Maps JavaScript API
        4. Create credentials (API key)

        ## Step 2: Create HTML Structure
        ```html
        <!DOCTYPE html>
        <html>
        <head>
            <title>My Google Map</title>
            <style>
                #map {
                    height: 400px;
                    width: 100%;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script src="script.js"></script>
        </body>
        </html>
        ```

        ## Step 3: Initialize the Map
        ```javascript
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 10,
                center: { lat: 37.7749, lng: -122.4194 }
            });
        }
        ```

        ## Step 4: Add Markers
        ```javascript
        const marker = new google.maps.Marker({
            position: { lat: 37.7749, lng: -122.4194 },
            map: map,
            title: "San Francisco"
        });
        ```

        ## Troubleshooting
        - Make sure your API key is valid
        - Check that the Maps JavaScript API is enabled
        - Verify your domain is authorized

        ## Conclusion
        You now have a working Google Maps integration in your web application.
        """
        
        payload = {
            "content": test_content,
            "content_type": "text",
            "metadata": {
                "title": "Google Maps API Tutorial",
                "source": "test_input"
            }
        }
        
        print(f"📤 Sending request to {BACKEND_URL}/content/process-refined")
        response = requests.post(
            f"{BACKEND_URL}/content/process-refined",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {data.get('message', 'No message')}")
            print(f"📊 Articles Created: {data.get('articles_created', 0)}")
            print(f"🔧 Engine Used: {data.get('engine_used', 'Unknown')}")
            
            # Verify refined engine metadata
            if data.get('engine_used') == 'refined_2.0':
                results["process_refined_endpoint"] = True
                print("✅ REFINED ENGINE v2.0 CONFIRMED")
                
                # Check articles metadata
                articles = data.get('articles', [])
                if articles:
                    results["content_processing"] = True
                    print(f"✅ CONTENT PROCESSING: {len(articles)} articles generated")
                    
                    # Analyze first article for refined engine features
                    first_article = articles[0]
                    print(f"📄 First Article: {first_article.get('title', 'No title')}")
                    print(f"📏 Content Length: {first_article.get('content_length', 0)} characters")
                    print(f"🏷️ Article Type: {first_article.get('article_type', 'Unknown')}")
                    
                    # Test granularity decision (should default to unified for tutorials)
                    if len(articles) <= 2:  # Unified or unified + FAQ
                        results["granularity_decision"] = True
                        print("✅ GRANULARITY DECISION: Correctly defaulted to unified processing")
                    else:
                        print(f"⚠️ GRANULARITY DECISION: Generated {len(articles)} articles (expected unified)")
                else:
                    print("❌ No articles returned in response")
            else:
                print(f"❌ Wrong engine used: {data.get('engine_used')}")
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR in process-refined test: {e}")
    
    # Test 2: Check Content Library for refined engine articles
    print("\n🔍 TEST 2: Verifying articles in Content Library")
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            print(f"📚 Total Articles in Library: {total_articles}")
            
            # Look for refined engine articles
            refined_articles = []
            for article in articles:
                metadata = article.get('metadata', {})
                if metadata.get('refined_engine') == True and metadata.get('engine_version') == '2.0.0':
                    refined_articles.append(article)
            
            if refined_articles:
                results["database_storage"] = True
                results["metadata_verification"] = True
                print(f"✅ REFINED ENGINE ARTICLES FOUND: {len(refined_articles)} articles")
                
                # Analyze refined engine article features
                for i, article in enumerate(refined_articles[:2]):  # Check first 2
                    print(f"\n📄 REFINED ARTICLE {i+1}:")
                    print(f"   🏷️ Title: {article.get('title', 'No title')}")
                    print(f"   🔧 Engine Version: {article.get('metadata', {}).get('engine_version', 'Unknown')}")
                    print(f"   🎯 Processing Approach: {article.get('metadata', {}).get('processing_approach', 'Unknown')}")
                    print(f"   📏 Content Length: {len(article.get('content', ''))}")
                    print(f"   🏷️ Article Type: {article.get('article_type', 'Unknown')}")
                    
                    # Check for WYSIWYG enhancements
                    content = article.get('content', '')
                    wysiwyg_features = {
                        'article_body_wrapper': '<div class="article-body">' in content,
                        'enhanced_code_blocks': 'class="line-numbers"' in content,
                        'heading_ids': 'id="h_' in content,
                        'mini_toc': 'mini-toc' in content,
                        'expandable_sections': 'class="expandable"' in content,
                        'contextual_notes': 'class="note"' in content
                    }
                    
                    wysiwyg_count = sum(wysiwyg_features.values())
                    if wysiwyg_count >= 2:  # At least 2 WYSIWYG features
                        results["wysiwyg_enhancements"] = True
                        print(f"   ✅ WYSIWYG FEATURES: {wysiwyg_count}/6 features detected")
                        for feature, present in wysiwyg_features.items():
                            if present:
                                print(f"      ✅ {feature}")
                    else:
                        print(f"   ⚠️ WYSIWYG FEATURES: Only {wysiwyg_count}/6 features detected")
                    
                    # Check content validation (fidelity)
                    if len(content) > 500 and '<h2' in content and '<p>' in content:
                        results["content_validation"] = True
                        print(f"   ✅ CONTENT VALIDATION: Proper HTML structure and substantial content")
                    else:
                        print(f"   ⚠️ CONTENT VALIDATION: Content may be insufficient or poorly structured")
            else:
                print("❌ No refined engine articles found in Content Library")
        else:
            print(f"❌ Failed to fetch Content Library: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR in Content Library check: {e}")
    
    # Test 3: Multi-dimensional Analysis verification
    print("\n🔍 TEST 3: Testing Multi-dimensional Analysis")
    try:
        # Test with different content types to verify analysis
        test_cases = [
            {
                "name": "Short Tutorial",
                "content": "# Quick Start\n\n## Step 1\nDo this.\n\n## Step 2\nDo that.\n\n```javascript\nconsole.log('hello');\n```",
                "expected_granularity": "unified"
            },
            {
                "name": "Large Reference Manual", 
                "content": "# API Reference\n\n" + "\n\n".join([f"## Endpoint {i}\nDescription for endpoint {i}.\n\n### Parameters\n- param1\n- param2\n\n### Response\n```json\n{{'result': 'data'}}\n```" for i in range(1, 15)]),
                "expected_granularity": "moderate"
            }
        ]
        
        analysis_results = []
        for test_case in test_cases:
            payload = {
                "content": test_case["content"],
                "content_type": "text", 
                "metadata": {"title": test_case["name"]}
            }
            
            response = requests.post(
                f"{BACKEND_URL}/content/process-refined",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                articles_count = data.get('articles_created', 0)
                
                # Determine actual granularity based on article count
                if articles_count <= 2:
                    actual_granularity = "unified"
                elif articles_count <= 4:
                    actual_granularity = "moderate"
                else:
                    actual_granularity = "deep"
                
                analysis_results.append({
                    "name": test_case["name"],
                    "expected": test_case["expected_granularity"],
                    "actual": actual_granularity,
                    "articles_count": articles_count,
                    "correct": actual_granularity == test_case["expected_granularity"]
                })
                
                print(f"📊 {test_case['name']}: {articles_count} articles ({actual_granularity})")
            else:
                print(f"❌ Failed to test {test_case['name']}: {response.status_code}")
        
        # Check if multi-dimensional analysis is working
        correct_analyses = sum(1 for result in analysis_results if result["correct"])
        if correct_analyses >= len(analysis_results) * 0.5:  # At least 50% correct
            results["multi_dimensional_analysis"] = True
            print(f"✅ MULTI-DIMENSIONAL ANALYSIS: {correct_analyses}/{len(analysis_results)} correct decisions")
        else:
            print(f"⚠️ MULTI-DIMENSIONAL ANALYSIS: Only {correct_analyses}/{len(analysis_results)} correct decisions")
            
    except Exception as e:
        print(f"❌ ERROR in multi-dimensional analysis test: {e}")
    
    # Test 4: File Upload Endpoint (if we can create a test file)
    print("\n🔍 TEST 4: Testing /api/content/upload-refined endpoint")
    try:
        # Create a simple test file content
        test_file_content = """Google Maps Integration Guide

Introduction
This guide covers Google Maps API integration.

Setup Instructions
1. Get API key
2. Include script
3. Initialize map

Code Example
function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 10,
        center: { lat: 37.7749, lng: -122.4194 }
    });
}

Conclusion
Your map is now ready to use.
"""
        
        # Simulate file upload
        files = {
            'file': ('test_guide.txt', test_file_content, 'text/plain')
        }
        data = {
            'metadata': json.dumps({"source": "test_upload"})
        }
        
        print(f"📤 Uploading test file to {BACKEND_URL}/content/upload-refined")
        response = requests.post(
            f"{BACKEND_URL}/content/upload-refined",
            files=files,
            data=data,
            timeout=60
        )
        
        print(f"📥 Upload Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ UPLOAD SUCCESS: {data.get('message', 'No message')}")
            print(f"📊 Articles Created: {data.get('articles_created', 0)}")
            print(f"📄 Filename: {data.get('filename', 'Unknown')}")
            print(f"📏 Content Extracted: {data.get('content_extracted', 0)} characters")
            
            if data.get('engine_used') == 'refined_2.0':
                results["upload_refined_endpoint"] = True
                print("✅ UPLOAD REFINED ENDPOINT: Working correctly")
            else:
                print(f"❌ Wrong engine used in upload: {data.get('engine_used')}")
        else:
            print(f"❌ UPLOAD FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR in upload-refined test: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 REFINED ENGINE v2.0 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n📊 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 REFINED ENGINE v2.0: PRODUCTION READY")
    elif success_rate >= 60:
        print("⚠️ REFINED ENGINE v2.0: NEEDS MINOR FIXES")
    else:
        print("❌ REFINED ENGINE v2.0: NEEDS MAJOR FIXES")
    
    return results, success_rate

if __name__ == "__main__":
    print("🚀 Starting Refined PromptSupport Engine v2.0 Backend Testing")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results, success_rate = test_refined_engine_endpoints()
    
    print(f"\n⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Final Success Rate: {success_rate:.1f}%")