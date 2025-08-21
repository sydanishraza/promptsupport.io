#!/usr/bin/env python3
"""
FINAL CLEAN PIPELINE VERIFICATION TEST
Quick comprehensive test to verify the clean content processing pipeline
"""

import requests
import json
import time

BACKEND_URL = "https://content-engine-6.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_clean_pipeline():
    print("🧪 FINAL CLEAN PIPELINE VERIFICATION TEST")
    print("=" * 50)
    
    # Test 1: Backend Health
    print("TEST 1: Backend Health Check")
    response = requests.get(f"{API_BASE}/health", timeout=30)
    if response.status_code == 200:
        print("✅ Backend health check PASSED")
    else:
        print("❌ Backend health check FAILED")
        return False
    
    # Test 2: Clean Pipeline Processing
    print("\nTEST 2: Clean Pipeline Processing")
    test_content = """
    Advanced API Integration Guide

    Introduction and Overview
    This comprehensive guide covers advanced API integration techniques, best practices, and troubleshooting methods. You'll learn how to implement robust API connections, handle authentication, manage rate limiting, and optimize performance.

    Getting Started with API Integration
    Before diving into advanced techniques, it's essential to understand the fundamentals of API integration. This section covers the basic concepts, authentication methods, and initial setup procedures.

    Authentication Methods
    Modern APIs support various authentication methods including API keys, OAuth 2.0, JWT tokens, and basic authentication. Each method has its own advantages and use cases.

    Rate Limiting and Performance Optimization
    Understanding rate limits is crucial for building reliable API integrations. This section covers strategies for handling rate limits, implementing retry logic, and optimizing API calls for better performance.

    Error Handling and Troubleshooting
    Robust error handling is essential for production API integrations. Learn how to handle different types of errors, implement proper logging, and troubleshoot common issues.

    Advanced Implementation Patterns
    Explore advanced patterns like circuit breakers, bulkhead isolation, and asynchronous processing to build resilient API integrations that can handle high loads and failures gracefully.

    Security Best Practices
    Security should be a top priority in API integrations. This section covers encryption, secure storage of credentials, input validation, and protection against common security vulnerabilities.

    Monitoring and Analytics
    Implement comprehensive monitoring and analytics to track API performance, identify bottlenecks, and ensure optimal user experience.
    """
    
    start_time = time.time()
    response = requests.post(
        f"{API_BASE}/content/process",
        json={"content": test_content, "content_type": "text", "filename": "comprehensive_test.txt"},
        timeout=180
    )
    
    if response.status_code != 200:
        print(f"❌ Processing failed: {response.status_code}")
        print(response.text[:500])
        return False
    
    data = response.json()
    job_id = data.get("job_id")
    print(f"✅ Processing started, Job ID: {job_id}")
    
    # Monitor processing
    max_wait = 120
    elapsed = 0
    while elapsed < max_wait:
        time.sleep(5)
        elapsed += 5
        
        status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
        if status_response.status_code == 200:
            status_data = status_response.json()
            status = status_data.get("status")
            
            if status == "completed":
                articles_generated = status_data.get("articles_generated", 0)
                processing_time = time.time() - start_time
                
                print(f"✅ Processing completed in {processing_time:.1f} seconds")
                print(f"📄 Articles Generated: {articles_generated}")
                
                if articles_generated > 0:
                    print("✅ CLEAN PIPELINE SUCCESS: Articles generated")
                    break
                else:
                    print("❌ CLEAN PIPELINE FAILURE: No articles generated")
                    return False
            elif status == "failed":
                print(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}")
                return False
            else:
                print(f"⏳ Status: {status} (elapsed: {elapsed}s)")
        else:
            print(f"⚠️ Status check failed: {status_response.status_code}")
    
    # Test 3: Article Quality Check
    print("\nTEST 3: Article Quality and Features")
    response = requests.get(f"{API_BASE}/content-library", timeout=30)
    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])
        total_articles = data.get("total", 0)
        
        print(f"📚 Total Articles in Library: {total_articles}")
        
        # Analyze recent articles
        clean_html_count = 0
        overview_count = 0
        faq_count = 0
        cross_ref_count = 0
        toc_count = 0
        
        for article in articles[:10]:  # Check first 10 articles
            content = article.get("content", "")
            title = article.get("title", "")
            
            # Check for clean HTML
            if "```html" not in content and "<!DOCTYPE html>" not in content:
                clean_html_count += 1
            
            # Check for overview articles
            if "overview" in title.lower():
                overview_count += 1
            
            # Check for FAQ articles
            if "faq" in title.lower() or "troubleshooting" in title.lower():
                faq_count += 1
            
            # Check for cross-references
            if "related-links" in content or "Related Articles" in content:
                cross_ref_count += 1
            
            # Check for table of contents
            if "table of contents" in content.lower() or "toc-list" in content:
                toc_count += 1
        
        print(f"📊 Quality Analysis (first 10 articles):")
        print(f"   Clean HTML Content: {clean_html_count}/10 ({clean_html_count*10}%)")
        print(f"   Overview Articles: {overview_count}")
        print(f"   FAQ Articles: {faq_count}")
        print(f"   Articles with Cross-References: {cross_ref_count}")
        print(f"   Articles with TOC: {toc_count}")
        
        if clean_html_count >= 9 and overview_count > 0 and cross_ref_count > 0:
            print("✅ ARTICLE QUALITY TEST PASSED")
        else:
            print("❌ ARTICLE QUALITY TEST FAILED")
            return False
    else:
        print(f"❌ Content Library check failed: {response.status_code}")
        return False
    
    print("\n🎉 ALL TESTS PASSED - CLEAN PIPELINE IS FULLY OPERATIONAL")
    print("✅ Clean content processing pipeline verified successfully")
    return True

if __name__ == "__main__":
    success = test_clean_pipeline()
    exit(0 if success else 1)