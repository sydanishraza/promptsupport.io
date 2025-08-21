#!/usr/bin/env python3
"""
STORAGE INVESTIGATION: Articles are generated but not stored in Content Library
Root cause analysis of the storage/persistence issue
"""

import requests
import json
import time
import os
import sys
import tempfile
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-pipeline-4.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def check_content_library_before_and_after():
    """Check Content Library before and after processing to identify storage issue"""
    try:
        log_test_result("🔍 INVESTIGATING ARTICLE STORAGE ISSUE", "CRITICAL")
        
        # Check Content Library before processing
        log_test_result("📚 Checking Content Library BEFORE processing...")
        response_before = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response_before.status_code == 200:
            data_before = response_before.json()
            total_before = data_before.get('total', 0)
            log_test_result(f"📊 Content Library BEFORE: {total_before} articles")
        else:
            log_test_result(f"❌ Failed to check Content Library: {response_before.status_code}")
            return False
        
        # Create and process a simple document
        test_content = """
# Storage Test Document

## Section 1
This is a test to investigate why articles are generated but not stored.

## Section 2  
The backend logs show articles are created successfully.

## Section 3
But the Content Library shows 0 articles total.
"""
        
        log_test_result("📤 Processing test document...")
        
        # Create temporary file and upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('storage_test.txt', f, 'text/plain')}
                metadata = {'metadata': '{}'}
                
                response = requests.post(f"{API_BASE}/content/upload", 
                                       files=files, 
                                       data=metadata,
                                       timeout=300)
                
                if response.status_code != 200:
                    log_test_result(f"❌ Upload failed: {response.status_code}", "ERROR")
                    return False
                
                upload_data = response.json()
                job_id = upload_data.get('job_id')
                log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        finally:
            os.unlink(temp_file_path)
        
        # Wait for processing to complete
        log_test_result("⏳ Waiting for processing to complete...")
        max_wait = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        articles_generated = status_data.get('articles_generated', 0)
                        log_test_result(f"✅ Processing completed: {articles_generated} articles generated")
                        break
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown')}")
                        return False
                    
                    time.sleep(5)
                else:
                    time.sleep(5)
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
        
        # Check Content Library after processing
        log_test_result("📚 Checking Content Library AFTER processing...")
        time.sleep(5)  # Give a moment for storage to complete
        
        response_after = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response_after.status_code == 200:
            data_after = response_after.json()
            total_after = data_after.get('total', 0)
            articles_after = data_after.get('articles', [])
            
            log_test_result(f"📊 Content Library AFTER: {total_after} articles")
            
            # Analysis
            articles_added = total_after - total_before
            log_test_result(f"📈 Articles added to Content Library: {articles_added}")
            
            if articles_added == 0:
                log_test_result("❌ STORAGE ISSUE CONFIRMED: Articles generated but not stored in Content Library", "CRITICAL_ERROR")
                
                # Check if articles exist but with different status
                if articles_after:
                    log_test_result("🔍 Checking article statuses...")
                    for article in articles_after[:5]:
                        title = article.get('title', 'Untitled')
                        status = article.get('status', 'unknown')
                        created = article.get('created_at', 'unknown')
                        log_test_result(f"   📄 {title[:30]}... (Status: {status}, Created: {created})")
                
                return False
            else:
                log_test_result(f"✅ Articles successfully stored: {articles_added} new articles in Content Library", "SUCCESS")
                
                # Show details of new articles
                if articles_after:
                    log_test_result("📄 New articles found:")
                    recent_articles = sorted(articles_after, key=lambda x: x.get('created_at', ''), reverse=True)
                    for i, article in enumerate(recent_articles[:articles_added]):
                        title = article.get('title', 'Untitled')
                        status = article.get('status', 'unknown')
                        log_test_result(f"   {i+1}. {title} (Status: {status})")
                
                return True
        else:
            log_test_result(f"❌ Failed to check Content Library after processing: {response_after.status_code}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Storage investigation failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def check_database_connection():
    """Check if there are database connection issues"""
    try:
        log_test_result("🔍 Checking database connectivity...")
        
        # Try to get backend health which should include DB status
        response = requests.get(f"{API_BASE}/health", timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            log_test_result(f"✅ Backend health check passed: {health_data}")
            return True
        else:
            log_test_result(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Database connectivity check failed: {e}")
        return False

def check_backend_logs_for_storage_errors():
    """Check backend logs for storage-related errors"""
    try:
        log_test_result("🔍 Checking backend logs for storage errors...")
        
        import subprocess
        result = subprocess.run(['tail', '-n', '100', '/var/log/supervisor/backend.out.log'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logs = result.stdout
            
            # Look for storage-related errors
            storage_error_indicators = [
                "database error",
                "mongodb error", 
                "insert failed",
                "storage error",
                "content_library",
                "db.content_library",
                "ERROR",
                "Exception",
                "Traceback"
            ]
            
            found_errors = []
            for indicator in storage_error_indicators:
                if indicator.lower() in logs.lower():
                    found_errors.append(indicator)
            
            if found_errors:
                log_test_result(f"⚠️ Found potential storage issues in logs: {found_errors}", "WARNING")
                
                # Show relevant log lines
                log_lines = logs.split('\n')
                for line in log_lines[-20:]:  # Last 20 lines
                    if any(error.lower() in line.lower() for error in storage_error_indicators):
                        log_test_result(f"📋 LOG: {line}", "WARNING")
                
                return False
            else:
                log_test_result("✅ No obvious storage errors found in logs", "SUCCESS")
                return True
        else:
            log_test_result("⚠️ Could not access backend logs")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Log analysis failed: {e}")
        return False

def run_storage_investigation():
    """Run comprehensive storage investigation"""
    log_test_result("🚀 STARTING STORAGE INVESTIGATION", "CRITICAL")
    log_test_result("Investigating why articles are generated but not stored")
    log_test_result("=" * 70)
    
    test_results = {
        'database_connection': False,
        'backend_logs_check': False,
        'storage_test': False
    }
    
    # Test 1: Database Connection
    log_test_result("TEST 1: Database Connection Check")
    test_results['database_connection'] = check_database_connection()
    
    # Test 2: Backend Logs Analysis
    log_test_result("\nTEST 2: Backend Logs Analysis")
    test_results['backend_logs_check'] = check_backend_logs_for_storage_errors()
    
    # Test 3: Storage Test (CRITICAL)
    log_test_result("\nTEST 3: CRITICAL STORAGE TEST")
    test_results['storage_test'] = check_content_library_before_and_after()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 70)
    log_test_result("🎯 STORAGE INVESTIGATION RESULTS", "CRITICAL")
    log_test_result("=" * 70)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Provide diagnosis
    if not test_results['storage_test']:
        log_test_result("❌ CRITICAL ISSUE CONFIRMED: Articles generated but not stored", "CRITICAL_ERROR")
        log_test_result("🔍 ROOT CAUSE: Storage/persistence layer is broken", "CRITICAL_ERROR")
        
        if not test_results['database_connection']:
            log_test_result("🔍 LIKELY CAUSE: Database connection issues", "CRITICAL_ERROR")
        elif not test_results['backend_logs_check']:
            log_test_result("🔍 LIKELY CAUSE: Storage errors in backend processing", "CRITICAL_ERROR")
        else:
            log_test_result("🔍 LIKELY CAUSE: Article creation vs storage disconnect", "CRITICAL_ERROR")
    else:
        log_test_result("✅ Storage is working correctly - articles are being persisted", "SUCCESS")
    
    return test_results

if __name__ == "__main__":
    print("Storage Investigation: Articles Generated But Not Stored")
    print("=" * 60)
    
    results = run_storage_investigation()
    
    if results['storage_test']:
        print("\n✅ Storage is working correctly")
        sys.exit(0)
    else:
        print("\n❌ Storage issue confirmed - articles not being persisted")
        sys.exit(1)