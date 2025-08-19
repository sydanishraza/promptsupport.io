#!/usr/bin/env python3
"""
SIMPLE STORAGE TEST - Critical Regression Fix Verification
Direct test of Content Library API and article storage functionality
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

def test_content_library_api():
    """Test Content Library API functionality"""
    try:
        log_test_result("🔍 Testing Content Library API...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_test_result(f"✅ Content Library API working")
            log_test_result(f"📚 Total articles: {total_articles}")
            log_test_result(f"📄 Articles retrieved: {len(articles)}")
            
            # Show some article details
            for i, article in enumerate(articles[:3]):
                title = article.get('title', 'Untitled')
                status = article.get('status', 'unknown')
                created_at = article.get('created_at', 'unknown')
                article_id = article.get('id', 'no-id')
                log_test_result(f"   Article {i+1}: {title[:40]}... (Status: {status}, ID: {article_id[:8]}...)")
            
            return True, total_articles, articles
        else:
            log_test_result(f"❌ Content Library API failed: Status {response.status_code}", "ERROR")
            return False, 0, []
            
    except Exception as e:
        log_test_result(f"❌ Content Library API test failed: {e}", "ERROR")
        return False, 0, []

def test_simple_document_upload():
    """Test simple document upload and processing"""
    try:
        log_test_result("📤 Testing simple document upload and processing...")
        
        # Create a simple test document
        simple_content = """
# API Testing Guide

## Introduction
This is a simple guide for testing API functionality.

## Getting Started
Follow these basic steps to get started with API testing.

## Basic Operations
Learn about the fundamental API operations.

## Conclusion
This concludes our simple API testing guide.
        """
        
        # Save as temporary file
        temp_file = "/tmp/simple_api_guide.txt"
        with open(temp_file, 'w') as f:
            f.write(simple_content)
        
        log_test_result(f"📄 Created simple test document: {len(simple_content)} characters")
        
        # Get baseline count
        success, baseline_count, baseline_articles = test_content_library_api()
        if not success:
            log_test_result("❌ Cannot get baseline count - aborting test", "ERROR")
            return False
        
        # Upload the document
        with open(temp_file, 'rb') as f:
            files = {'file': ('simple_api_guide.txt', f, 'text/plain')}
            
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=120)
        
        if response.status_code != 200:
            log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:300]}")
            return False
        
        upload_data = response.json()
        job_id = upload_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from upload", "ERROR")
            return False
        
        log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing (simplified)
        log_test_result("⏳ Monitoring processing...")
        max_wait = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 Status: {status}")
                    
                    if status == 'completed':
                        log_test_result("✅ Processing completed")
                        
                        # Extract metrics
                        articles_generated = status_data.get('articles_generated', 0)
                        log_test_result(f"📄 Articles generated: {articles_generated}")
                        
                        # Wait for database operations
                        time.sleep(3)
                        
                        # Check if articles were stored
                        success, new_count, new_articles = test_content_library_api()
                        if success:
                            articles_added = new_count - baseline_count
                            log_test_result(f"📊 DATABASE VERIFICATION:")
                            log_test_result(f"   Baseline: {baseline_count} articles")
                            log_test_result(f"   New count: {new_count} articles")
                            log_test_result(f"   Articles added: {articles_added}")
                            
                            if articles_added > 0:
                                log_test_result("🎉 SUCCESS: Articles were stored in database!", "SUCCESS")
                                log_test_result("✅ Database storage regression is FIXED", "SUCCESS")
                                return True
                            else:
                                log_test_result("❌ FAILURE: No articles stored in database", "ERROR")
                                log_test_result("❌ Database storage regression still present", "ERROR")
                                return False
                        else:
                            log_test_result("❌ Could not verify database storage", "ERROR")
                            return False
                    
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown')}", "ERROR")
                        return False
                    
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
        
        log_test_result("❌ Processing timeout", "ERROR")
        return False
        
    except Exception as e:
        log_test_result(f"❌ Document upload test failed: {e}", "ERROR")
        return False
    finally:
        # Clean up
        if os.path.exists("/tmp/simple_api_guide.txt"):
            os.remove("/tmp/simple_api_guide.txt")

def run_simple_storage_test():
    """Run the simple storage test"""
    log_test_result("🚀 STARTING SIMPLE STORAGE TEST", "CRITICAL")
    log_test_result("Testing: Article generation and database storage")
    log_test_result("=" * 60)
    
    # Test 1: Backend health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=30)
        if response.status_code != 200:
            log_test_result("❌ Backend health check failed", "ERROR")
            return False
        log_test_result("✅ Backend health check passed")
    except Exception as e:
        log_test_result(f"❌ Backend health check failed: {e}", "ERROR")
        return False
    
    # Test 2: Content Library API
    success, count, articles = test_content_library_api()
    if not success:
        log_test_result("❌ Content Library API test failed", "ERROR")
        return False
    
    # Test 3: Document upload and storage
    result = test_simple_document_upload()
    
    # Final summary
    log_test_result("\n" + "=" * 60)
    log_test_result("🎯 SIMPLE STORAGE TEST RESULTS", "CRITICAL")
    log_test_result("=" * 60)
    
    if result:
        log_test_result("🎉 CRITICAL SUCCESS: Database storage is working!", "CRITICAL_SUCCESS")
        log_test_result("✅ Articles are generated AND saved to database", "CRITICAL_SUCCESS")
        log_test_result("✅ The 0-article regression has been FIXED", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Database storage is not working", "CRITICAL_ERROR")
        log_test_result("❌ The 0-article regression is still present", "CRITICAL_ERROR")
    
    return result

if __name__ == "__main__":
    print("Simple Storage Test - Critical Regression Fix Verification")
    print("=" * 55)
    
    success = run_simple_storage_test()
    
    # Exit with appropriate code
    if success:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure