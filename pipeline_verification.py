#!/usr/bin/env python3
"""
INTELLIGENT PIPELINE VERIFICATION
Quick verification of key intelligent pipeline features based on backend logs
"""

import requests
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-pipeline-4.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_result(message, status="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def verify_backend_health():
    """Verify backend is healthy"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            log_result("✅ Backend health check PASSED", "SUCCESS")
            return True
        else:
            log_result(f"❌ Backend health check FAILED: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_result(f"❌ Backend health check FAILED: {e}", "ERROR")
        return False

def verify_content_library():
    """Verify Content Library has articles"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            log_result(f"✅ Content Library operational: {total_articles} articles", "SUCCESS")
            return total_articles > 0
        else:
            log_result(f"❌ Content Library check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_result(f"❌ Content Library check failed: {e}", "ERROR")
        return False

def test_simple_content_processing():
    """Test simple content processing to verify pipeline works"""
    try:
        log_result("🧠 Testing simple content processing...")
        
        simple_content = "This is a test document for verifying the intelligent content processing pipeline functionality."
        
        data = {
            'content': simple_content,
            'content_type': 'text',
            'metadata': {'original_filename': 'pipeline_verification_test.txt'}
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process", json=data, timeout=60)
        
        if response.status_code != 200:
            log_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            return False
        
        result = response.json()
        job_id = result.get('job_id')
        
        if not job_id:
            log_result("❌ No job_id received", "ERROR")
            return False
        
        # Monitor processing with short timeout
        max_wait = 45  # 45 seconds
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                log_result("❌ Processing timeout", "ERROR")
                return False
            
            status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                if status == 'completed':
                    articles_generated = status_data.get('articles_generated', 0)
                    log_result(f"✅ Content processing completed: {articles_generated} articles generated", "SUCCESS")
                    return articles_generated > 0
                    
                elif status == 'failed':
                    log_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                    return False
                
                time.sleep(2)
            else:
                time.sleep(2)
                
    except Exception as e:
        log_result(f"❌ Content processing test failed: {e}", "ERROR")
        return False

def main():
    log_result("🚀 INTELLIGENT PIPELINE VERIFICATION STARTED", "CRITICAL")
    log_result("=" * 50)
    
    results = {
        'backend_health': False,
        'content_library': False,
        'content_processing': False
    }
    
    # Test 1: Backend Health
    log_result("TEST 1: Backend Health")
    results['backend_health'] = verify_backend_health()
    
    # Test 2: Content Library
    log_result("\nTEST 2: Content Library")
    results['content_library'] = verify_content_library()
    
    # Test 3: Content Processing
    log_result("\nTEST 3: Content Processing")
    results['content_processing'] = test_simple_content_processing()
    
    # Summary
    log_result("\n" + "=" * 50)
    log_result("🎯 VERIFICATION RESULTS", "CRITICAL")
    log_result("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed / total) * 100
    log_result(f"\nOVERALL: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 66:
        log_result("🎉 INTELLIGENT PIPELINE VERIFICATION SUCCESS", "CRITICAL_SUCCESS")
        log_result("✅ Core functionality operational", "CRITICAL_SUCCESS")
    else:
        log_result("❌ INTELLIGENT PIPELINE VERIFICATION FAILED", "CRITICAL_ERROR")
    
    return results

if __name__ == "__main__":
    print("Intelligent Pipeline Verification")
    print("=" * 35)
    main()