#!/usr/bin/env python3
"""
DOCX REGRESSION TEST: Test with DOCX files to reproduce 0 articles issue
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-6.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_docx_processing(docx_file_path):
    """Test processing of a DOCX file"""
    try:
        if not os.path.exists(docx_file_path):
            log_test_result(f"❌ DOCX file not found: {docx_file_path}", "ERROR")
            return False
        
        file_size = os.path.getsize(docx_file_path)
        filename = os.path.basename(docx_file_path)
        
        log_test_result(f"🎯 TESTING DOCX PROCESSING: {filename}", "CRITICAL")
        log_test_result(f"📄 File size: {file_size:,} bytes ({file_size/1024:.1f}KB)")
        
        log_test_result("📤 Uploading DOCX file...")
        
        with open(docx_file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            metadata = {'metadata': '{}'}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", 
                                   files=files, 
                                   data=metadata,
                                   timeout=600)  # 10 minute timeout
            
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
                        
                        log_test_result(f"📈 DOCX PROCESSING RESULTS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        log_test_result(f"   ⏱️ Processing Time: {processing_time:.1f} seconds")
                        log_test_result(f"   📊 File Size: {file_size:,} bytes")
                        
                        # CRITICAL VERIFICATION: Check for 0 articles regression
                        if articles_generated == 0:
                            log_test_result(f"❌ CRITICAL REGRESSION CONFIRMED: 0 articles generated from DOCX file", "CRITICAL_ERROR")
                            log_test_result("❌ DOCX PROCESSING IS BROKEN", "CRITICAL_ERROR")
                            
                            # Try to get more details from the job status
                            if 'error' in status_data:
                                log_test_result(f"❌ Error details: {status_data['error']}", "ERROR")
                            
                            return False
                        else:
                            log_test_result(f"✅ DOCX processed successfully: {articles_generated} articles generated", "SUCCESS")
                            return True
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test_result(f"❌ Processing failed: {error_msg}", "ERROR")
                        
                        # Log detailed error for debugging
                        if 'traceback' in status_data:
                            log_test_result(f"❌ Traceback: {status_data['traceback'][:500]}...", "ERROR")
                        
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
        log_test_result(f"❌ DOCX test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_docx_files():
    """Test multiple DOCX files to identify patterns"""
    docx_files = [
        "/app/simple_test.docx",
        "/app/test_billing.docx", 
        "/app/source_document.docx"
    ]
    
    results = {}
    
    for docx_file in docx_files:
        if os.path.exists(docx_file):
            log_test_result(f"\n{'='*60}")
            result = test_docx_processing(docx_file)
            results[os.path.basename(docx_file)] = result
        else:
            log_test_result(f"⚠️ File not found: {docx_file}")
            results[os.path.basename(docx_file)] = None
    
    # Summary
    log_test_result(f"\n{'='*60}")
    log_test_result("🎯 DOCX REGRESSION TEST SUMMARY", "CRITICAL")
    log_test_result(f"{'='*60}")
    
    successful = 0
    failed = 0
    
    for filename, result in results.items():
        if result is True:
            log_test_result(f"✅ {filename}: SUCCESS")
            successful += 1
        elif result is False:
            log_test_result(f"❌ {filename}: FAILED (0 articles)")
            failed += 1
        else:
            log_test_result(f"⚠️ {filename}: NOT TESTED (file not found)")
    
    log_test_result(f"\nResults: {successful} successful, {failed} failed")
    
    if failed > 0:
        log_test_result("❌ DOCX REGRESSION CONFIRMED: Some DOCX files generate 0 articles", "CRITICAL_ERROR")
        return False
    elif successful > 0:
        log_test_result("✅ All tested DOCX files processed successfully", "SUCCESS")
        return True
    else:
        log_test_result("⚠️ No DOCX files could be tested", "WARNING")
        return False

if __name__ == "__main__":
    print("DOCX Regression Test")
    print("=" * 30)
    
    result = test_multiple_docx_files()
    
    if result:
        print("\n✅ DOCX processing is working correctly")
        sys.exit(0)
    else:
        print("\n❌ DOCX processing regression confirmed")
        sys.exit(1)