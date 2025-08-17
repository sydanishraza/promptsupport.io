#!/usr/bin/env python3
"""
CRITICAL REGRESSION FIX TESTING - Article Database Storage
Testing the fix for outline-first processing where articles were generated but not saved to database
Focus: Verify articles are both generated AND stored in Content Library database
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://docai-promptsupport.preview.emergentagent.com"
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

def get_content_library_count():
    """Get current count of articles in Content Library"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            log_test_result(f"📚 Content Library: {total_articles} total articles, {len(articles)} retrieved")
            return total_articles, articles
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return 0, []
            
    except Exception as e:
        log_test_result(f"❌ Content Library check failed: {e}", "ERROR")
        return 0, []

def test_outline_first_article_generation_and_storage():
    """
    CRITICAL TEST: Process document using outline-first approach and verify articles are saved to database
    This tests the fix for the 0-article regression where articles were generated but not stored
    """
    try:
        log_test_result("🎯 STARTING CRITICAL REGRESSION FIX TEST", "CRITICAL")
        log_test_result("Testing outline-first processing with database storage verification")
        
        # Get baseline Content Library count
        baseline_count, baseline_articles = get_content_library_count()
        log_test_result(f"📊 Baseline Content Library count: {baseline_count} articles")
        
        # Create test content for outline-first processing
        test_content = """
        # Comprehensive Guide to API Integration
        
        ## Introduction
        This guide covers the complete process of API integration from setup to deployment.
        
        ## Getting Started
        Before you begin, ensure you have the necessary prerequisites and tools installed.
        
        ### Prerequisites
        - API key from the service provider
        - Development environment setup
        - Basic understanding of REST APIs
        
        ## Authentication Setup
        Authentication is the first step in any API integration process.
        
        ### API Key Configuration
        Configure your API key in the environment variables for security.
        
        ### OAuth Implementation
        For OAuth-based authentication, follow these detailed steps.
        
        ## Making API Calls
        Learn how to make effective API calls with proper error handling.
        
        ### GET Requests
        Retrieve data from the API using GET requests with proper parameters.
        
        ### POST Requests
        Send data to the API using POST requests with JSON payloads.
        
        ### Error Handling
        Implement robust error handling for various API response scenarios.
        
        ## Advanced Features
        Explore advanced API features for enhanced functionality.
        
        ### Rate Limiting
        Understand and implement rate limiting to avoid API throttling.
        
        ### Caching Strategies
        Implement caching to improve performance and reduce API calls.
        
        ## Testing and Debugging
        Comprehensive testing strategies for API integrations.
        
        ### Unit Testing
        Write unit tests for your API integration code.
        
        ### Integration Testing
        Test the complete integration flow end-to-end.
        
        ## Deployment
        Deploy your API integration to production environments.
        
        ### Environment Configuration
        Configure different environments for development, staging, and production.
        
        ### Monitoring and Logging
        Implement monitoring and logging for production API usage.
        
        ## Troubleshooting
        Common issues and their solutions in API integrations.
        
        ### Connection Issues
        Resolve common connection problems with APIs.
        
        ### Authentication Errors
        Debug authentication-related issues effectively.
        """
        
        # Process content using Knowledge Engine (which should use outline-first approach)
        log_test_result("📤 Processing content using Knowledge Engine...")
        
        # Use the Knowledge Engine endpoint for processing
        payload = {
            "content": test_content,
            "processing_type": "outline_first"
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/knowledge-engine/process", 
                               json=payload, 
                               timeout=300)  # 5 minute timeout
        
        if response.status_code != 200:
            log_test_result(f"❌ Processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        processing_data = response.json()
        processing_time = time.time() - start_time
        
        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds")
        log_test_result(f"📊 Processing response: {json.dumps(processing_data, indent=2)[:500]}...")
        
        # Extract processing results
        articles_generated = processing_data.get('articles_generated', 0)
        articles_created = processing_data.get('articles_created', 0)
        status = processing_data.get('status', 'unknown')
        
        log_test_result(f"📈 PROCESSING RESULTS:")
        log_test_result(f"   Status: {status}")
        log_test_result(f"   Articles Generated: {articles_generated}")
        log_test_result(f"   Articles Created: {articles_created}")
        
        # CRITICAL VERIFICATION 1: Check if articles were generated
        if articles_generated == 0:
            log_test_result("❌ CRITICAL FAILURE: No articles were generated", "CRITICAL_ERROR")
            return False
        
        log_test_result(f"✅ Article generation working: {articles_generated} articles generated")
        
        # Wait a moment for database operations to complete
        time.sleep(2)
        
        # CRITICAL VERIFICATION 2: Check if articles were saved to database
        log_test_result("🔍 Verifying articles were saved to Content Library database...")
        
        new_count, new_articles = get_content_library_count()
        articles_added = new_count - baseline_count
        
        log_test_result(f"📊 DATABASE STORAGE VERIFICATION:")
        log_test_result(f"   Baseline count: {baseline_count}")
        log_test_result(f"   New count: {new_count}")
        log_test_result(f"   Articles added to database: {articles_added}")
        
        # CRITICAL CHECK: Verify articles were actually stored
        if articles_added == 0:
            log_test_result("❌ CRITICAL REGRESSION CONFIRMED: Articles generated but NOT saved to database", "CRITICAL_ERROR")
            log_test_result("❌ The 0-article regression is still present", "CRITICAL_ERROR")
            return False
        elif articles_added < articles_generated:
            log_test_result(f"⚠️ PARTIAL STORAGE: Only {articles_added}/{articles_generated} articles saved to database", "WARNING")
            log_test_result("⚠️ Some articles may have been lost during storage", "WARNING")
            return False
        else:
            log_test_result(f"🎉 CRITICAL SUCCESS: All {articles_generated} articles saved to database", "CRITICAL_SUCCESS")
            log_test_result("✅ Database storage regression has been FIXED", "CRITICAL_SUCCESS")
        
        # CRITICAL VERIFICATION 3: Verify articles can be retrieved from Content Library
        log_test_result("🔍 Verifying articles can be retrieved from Content Library API...")
        
        # Look for recently created articles
        recent_articles = []
        for article in new_articles:
            title = article.get('title', '').lower()
            created_at = article.get('created_at', '')
            
            # Check if this looks like one of our test articles
            if any(keyword in title for keyword in ['api', 'integration', 'guide', 'authentication', 'testing']):
                recent_articles.append(article)
        
        if len(recent_articles) >= articles_generated:
            log_test_result(f"✅ Found {len(recent_articles)} matching articles in Content Library")
            
            # Show details of created articles
            for i, article in enumerate(recent_articles[:5]):
                title = article.get('title', 'Untitled')
                status = article.get('status', 'unknown')
                article_id = article.get('id', 'no-id')
                log_test_result(f"   Article {i+1}: {title[:60]}... (Status: {status}, ID: {article_id[:8]}...)")
            
            return True
        else:
            log_test_result(f"⚠️ Only found {len(recent_articles)} matching articles (expected {articles_generated})")
            return False
        
    except Exception as e:
        log_test_result(f"❌ Critical regression test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_workflow():
    """Test complete end-to-end workflow: Upload → Process → Generate → Store → Retrieve"""
    try:
        log_test_result("🔄 Testing complete end-to-end workflow...")
        
        # Create a small test document
        test_doc_content = """
        # Quick Start Guide
        
        ## Overview
        This is a quick start guide for testing the complete workflow.
        
        ## Setup
        Follow these steps to get started quickly.
        
        ## Implementation
        Implement the solution using these guidelines.
        
        ## Testing
        Test your implementation thoroughly.
        """
        
        # Save as temporary file
        temp_file = "/tmp/test_workflow.txt"
        with open(temp_file, 'w') as f:
            f.write(test_doc_content)
        
        # Get baseline count
        baseline_count, _ = get_content_library_count()
        
        # Upload and process
        log_test_result("📤 Uploading test document...")
        
        with open(temp_file, 'rb') as f:
            files = {'file': ('test_workflow.txt', f, 'text/plain')}
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=120)
        
        if response.status_code != 200:
            log_test_result(f"❌ Upload failed: {response.status_code}", "ERROR")
            return False
        
        upload_data = response.json()
        job_id = upload_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received", "ERROR")
            return False
        
        log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing...")
        max_wait = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        log_test_result("✅ Processing completed")
                        
                        # Verify articles were created and stored
                        time.sleep(2)  # Wait for database operations
                        new_count, _ = get_content_library_count()
                        articles_added = new_count - baseline_count
                        
                        if articles_added > 0:
                            log_test_result(f"🎉 End-to-end workflow SUCCESS: {articles_added} articles created and stored")
                            return True
                        else:
                            log_test_result("❌ End-to-end workflow FAILED: No articles stored in database")
                            return False
                    
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown')}")
                        return False
                    
                    time.sleep(5)
                else:
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
        
        log_test_result("❌ End-to-end workflow timeout")
        return False
        
    except Exception as e:
        log_test_result(f"❌ End-to-end workflow test failed: {e}", "ERROR")
        return False
    finally:
        # Clean up temp file
        if os.path.exists("/tmp/test_workflow.txt"):
            os.remove("/tmp/test_workflow.txt")

def run_critical_regression_test_suite():
    """Run comprehensive test suite for critical regression fix verification"""
    log_test_result("🚀 STARTING CRITICAL REGRESSION FIX TEST SUITE", "CRITICAL")
    log_test_result("Testing fix for: Articles generated but not saved to database")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'outline_first_storage': False,
        'end_to_end_workflow': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Outline-First Article Generation and Storage (CRITICAL)
    log_test_result("\nTEST 2: CRITICAL OUTLINE-FIRST STORAGE TEST")
    test_results['outline_first_storage'] = test_outline_first_article_generation_and_storage()
    
    # Test 3: End-to-End Workflow
    log_test_result("\nTEST 3: End-to-End Workflow Test")
    test_results['end_to_end_workflow'] = test_end_to_end_workflow()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 CRITICAL REGRESSION FIX TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if test_results['outline_first_storage']:
        log_test_result("🎉 CRITICAL SUCCESS: Article database storage regression has been FIXED!", "CRITICAL_SUCCESS")
        log_test_result("✅ Articles are now both generated AND saved to Content Library database", "CRITICAL_SUCCESS")
        log_test_result("✅ Users will now see generated articles in Content Library", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Article database storage regression is still present", "CRITICAL_ERROR")
        log_test_result("❌ Articles are generated but NOT saved to database", "CRITICAL_ERROR")
        log_test_result("❌ Users will continue to see 0 articles in Content Library", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Critical Regression Fix Testing - Article Database Storage")
    print("=" * 60)
    
    results = run_critical_regression_test_suite()
    
    # Exit with appropriate code
    if results['outline_first_storage']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure