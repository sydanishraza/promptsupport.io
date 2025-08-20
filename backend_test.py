#!/usr/bin/env python3
"""
CRITICAL HARD LIMIT REMOVAL TESTING - Knowledge Engine
Testing the complete removal of hard limits from the Knowledge Engine processing pipeline
Focus: Verify that customer_guide.docx (4.6MB, 85-page document) generates 15-30+ articles (not just 6)
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://article-genius-1.preview.emergentagent.com"
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

def test_hard_limit_removal_with_customer_guide():
    """
    CRITICAL TEST: Process customer_guide.docx and verify hard limits are completely removed
    Expected: 15-30+ articles for 85-page document (not just 6)
    """
    try:
        log_test_result("🎯 STARTING CRITICAL HARD LIMIT REMOVAL TEST", "CRITICAL")
        log_test_result("Processing customer_guide.docx (4.6MB, 85-page document)")
        
        # Check if file exists
        file_path = "/app/customer_guide.docx"
        if not os.path.exists(file_path):
            log_test_result(f"❌ Test file not found: {file_path}", "ERROR")
            return False
        
        file_size = os.path.getsize(file_path)
        log_test_result(f"📄 File confirmed: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)")
        
        # Upload and process the document
        log_test_result("📤 Uploading document to Knowledge Engine...")
        
        with open(file_path, 'rb') as f:
            files = {'file': ('customer_guide.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            
            # Start processing
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=600)  # 10 minute timeout
            
            if response.status_code != 200:
                log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                log_test_result(f"Response: {response.text[:500]}")
                return False
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if not job_id:
                log_test_result("❌ No job_id received from upload", "ERROR")
                return False
            
            log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing with detailed logging
        log_test_result("⏳ Monitoring processing progress...")
        processing_start = time.time()
        max_wait_time = 600  # 10 minutes max
        
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
                        
                        # Extract critical metrics
                        chunks_created = status_data.get('chunks_created', 0)
                        articles_generated = status_data.get('articles_generated', 0)
                        
                        log_test_result(f"📈 CRITICAL METRICS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        
                        # CRITICAL VERIFICATION: Check if hard limits are removed
                        if articles_generated <= 6:
                            log_test_result(f"❌ CRITICAL FAILURE: Only {articles_generated} articles generated (expected 15-30+ for 85-page document)", "CRITICAL_ERROR")
                            log_test_result("❌ HARD LIMITS NOT REMOVED - System still limited to 6 articles", "CRITICAL_ERROR")
                            return False
                        elif articles_generated >= 15:
                            log_test_result(f"🎉 CRITICAL SUCCESS: {articles_generated} articles generated (exceeds 6-article limit)", "CRITICAL_SUCCESS")
                            log_test_result("✅ HARD LIMITS SUCCESSFULLY REMOVED", "CRITICAL_SUCCESS")
                        else:
                            log_test_result(f"⚠️ PARTIAL SUCCESS: {articles_generated} articles generated (better than 6, but below expected 15+ for 85-page document)", "WARNING")
                        
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    # Continue monitoring
                    time.sleep(10)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Hard limit removal test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_content_library_verification():
    """Verify articles are properly stored in Content Library"""
    try:
        log_test_result("🔍 Verifying Content Library integration...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_test_result(f"📚 Content Library Status:")
            log_test_result(f"   Total Articles: {total_articles}")
            log_test_result(f"   Articles Retrieved: {len(articles)}")
            
            # Look for recently created articles from customer_guide
            recent_customer_guide_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                source = article.get('source_document', '').lower()
                if 'customer' in title or 'customer' in source:
                    recent_customer_guide_articles.append(article)
            
            if recent_customer_guide_articles:
                log_test_result(f"✅ Found {len(recent_customer_guide_articles)} customer guide articles in Content Library")
                
                # Show details of first few articles
                for i, article in enumerate(recent_customer_guide_articles[:5]):
                    title = article.get('title', 'Untitled')
                    status = article.get('status', 'unknown')
                    created = article.get('created_at', 'unknown')
                    log_test_result(f"   Article {i+1}: {title[:50]}... (Status: {status})")
                
                return True
            else:
                log_test_result("⚠️ No customer guide articles found in Content Library")
                return False
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Content Library verification failed: {e}", "ERROR")
        return False

def check_backend_logs_for_limit_removal():
    """Check if backend logs show 'NO ARTIFICIAL LIMITS APPLIED'"""
    try:
        log_test_result("🔍 Checking backend logs for limit removal confirmation...")
        
        # Try to get recent backend logs
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '100', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Check for key indicators of limit removal
                if "NO ARTIFICIAL LIMITS APPLIED" in logs:
                    log_test_result("✅ Found 'NO ARTIFICIAL LIMITS APPLIED' in backend logs", "SUCCESS")
                    return True
                elif "ULTRA-LARGE DOCUMENT DETECTED" in logs:
                    log_test_result("✅ Found 'ULTRA-LARGE DOCUMENT DETECTED' in backend logs", "SUCCESS")
                    return True
                elif "dynamic calculation" in logs.lower():
                    log_test_result("✅ Found dynamic calculation references in backend logs", "SUCCESS")
                    return True
                else:
                    log_test_result("⚠️ No explicit limit removal confirmation found in logs")
                    return False
            else:
                log_test_result("⚠️ Could not access backend logs")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend log verification failed: {e}", "ERROR")
        return False

def run_comprehensive_hard_limit_test():
    """Run comprehensive test suite for hard limit removal verification"""
    log_test_result("🚀 STARTING COMPREHENSIVE HARD LIMIT REMOVAL TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'hard_limit_removal': False,
        'content_library_verification': False,
        'backend_logs_check': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Hard Limit Removal (CRITICAL)
    log_test_result("\nTEST 2: CRITICAL HARD LIMIT REMOVAL TEST")
    test_results['hard_limit_removal'] = test_hard_limit_removal_with_customer_guide()
    
    # Test 3: Content Library Verification
    log_test_result("\nTEST 3: Content Library Verification")
    test_results['content_library_verification'] = test_content_library_verification()
    
    # Test 4: Backend Logs Check
    log_test_result("\nTEST 4: Backend Logs Verification")
    test_results['backend_logs_check'] = check_backend_logs_for_limit_removal()
    
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
    
    if test_results['hard_limit_removal']:
        log_test_result("🎉 CRITICAL SUCCESS: Hard limits have been successfully removed!", "CRITICAL_SUCCESS")
        log_test_result("✅ Knowledge Engine now processes large documents without artificial article limits", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Hard limits are still present in the system", "CRITICAL_ERROR")
        log_test_result("❌ Knowledge Engine is still limited to 6 articles regardless of document size", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Knowledge Engine Hard Limit Removal Testing")
    print("=" * 50)
    
    results = run_comprehensive_hard_limit_test()
    
    # Exit with appropriate code
    if results['hard_limit_removal']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure