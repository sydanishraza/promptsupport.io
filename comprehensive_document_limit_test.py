#!/usr/bin/env python3
"""
COMPREHENSIVE KNOWLEDGE ENGINE DOCUMENT TESTING
Testing ALL 4 user documents to identify remaining limits as requested in review:

1. Customer Summary Screen User Guide 1.3.docx (4.6MB, 85 pages) - Expected: 15-25+ articles
2. Google Map JavaScript API Tutorial.docx (1.1MB) - Expected: 8-15 articles  
3. Promotions Configuration and Management-v5.docx (0.5MB) - Expected: 6-12 articles
4. Whisk Studio Integration Guide.pdf (1.7MB) - Expected: 10-20 articles

CRITICAL ANALYSIS NEEDED:
- Document which documents still hit limits
- Identify if certain processing paths still have hard limits
- Check if different document types (DOCX vs PDF) have different limits
- Verify if content extraction is incomplete
- Look for processing pathway differences
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import subprocess

# Backend URL from frontend .env
BACKEND_URL = "https://1c7fe221-5f78-4e90-bb7b-b530162b68ad.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test documents with expected article counts
TEST_DOCUMENTS = [
    {
        "filename": "Customer Summary Screen User Guide 1.3.docx",
        "path": "/app/Customer Summary Screen User Guide 1.3.docx",
        "size_mb": 4.6,
        "pages": 85,
        "expected_min": 15,
        "expected_max": 25,
        "type": "DOCX",
        "description": "Large comprehensive user guide"
    },
    {
        "filename": "Google Map JavaScript API Tutorial.docx", 
        "path": "/app/Google Map JavaScript API Tutorial.docx",
        "size_mb": 1.1,
        "pages": "unknown",
        "expected_min": 8,
        "expected_max": 15,
        "type": "DOCX",
        "description": "Medium technical tutorial"
    },
    {
        "filename": "Promotions Configuration and Management-v5.docx",
        "path": "/app/Promotions Configuration and Management-v5.docx", 
        "size_mb": 0.5,
        "pages": "unknown",
        "expected_min": 6,
        "expected_max": 12,
        "type": "DOCX",
        "description": "Small technical configuration guide"
    },
    {
        "filename": "Whisk Studio Integration Guide.pdf",
        "path": "/app/Whisk Studio Integration Guide.pdf",
        "size_mb": 1.7,
        "pages": "unknown", 
        "expected_min": 10,
        "expected_max": 20,
        "type": "PDF",
        "description": "Medium integration guide"
    }
]

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def check_file_exists(doc_info):
    """Check if test document exists and get actual file size"""
    try:
        if not os.path.exists(doc_info["path"]):
            log_test_result(f"❌ Test file not found: {doc_info['path']}", "ERROR")
            return False, None
        
        actual_size = os.path.getsize(doc_info["path"])
        actual_size_mb = actual_size / 1024 / 1024
        
        log_test_result(f"✅ File found: {doc_info['filename']}")
        log_test_result(f"   Expected size: {doc_info['size_mb']}MB, Actual size: {actual_size_mb:.1f}MB ({actual_size:,} bytes)")
        
        return True, actual_size
        
    except Exception as e:
        log_test_result(f"❌ Error checking file {doc_info['filename']}: {e}", "ERROR")
        return False, None

def upload_and_process_document(doc_info, actual_size):
    """Upload and process a single document, return processing results"""
    try:
        log_test_result(f"📤 Uploading {doc_info['filename']} ({doc_info['type']})...")
        
        # Determine content type based on file extension
        if doc_info['type'] == 'DOCX':
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif doc_info['type'] == 'PDF':
            content_type = 'application/pdf'
        else:
            content_type = 'application/octet-stream'
        
        with open(doc_info['path'], 'rb') as f:
            files = {'file': (doc_info['filename'], f, content_type)}
            
            # Start processing with extended timeout for large files
            start_time = time.time()
            timeout = 900 if actual_size > 1024*1024 else 600  # 15 min for large files, 10 min for smaller
            
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=timeout)
            
            if response.status_code != 200:
                log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                log_test_result(f"Response: {response.text[:500]}")
                return None
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if not job_id:
                log_test_result("❌ No job_id received from upload", "ERROR")
                return None
            
            log_test_result(f"✅ Upload successful, Job ID: {job_id}")
            return job_id
            
    except Exception as e:
        log_test_result(f"❌ Upload failed for {doc_info['filename']}: {e}", "ERROR")
        return None

def monitor_processing(job_id, doc_info, max_wait_minutes=15):
    """Monitor document processing and return results"""
    try:
        log_test_result(f"⏳ Monitoring processing for {doc_info['filename']}...")
        processing_start = time.time()
        max_wait_time = max_wait_minutes * 60
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed/60:.1f} minutes", "ERROR")
                return None
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 Processing status: {status} (elapsed: {elapsed/60:.1f}min)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time/60:.1f} minutes", "SUCCESS")
                        
                        # Extract all available metrics
                        result = {
                            'status': 'completed',
                            'processing_time': processing_time,
                            'chunks_created': status_data.get('chunks_created', 0),
                            'articles_generated': status_data.get('articles_generated', 0),
                            'job_data': status_data
                        }
                        
                        return result
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test_result(f"❌ Processing failed: {error_msg}", "ERROR")
                        return {'status': 'failed', 'error': error_msg}
                    
                    # Continue monitoring
                    time.sleep(15)  # Check every 15 seconds
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(10)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(10)
                
    except Exception as e:
        log_test_result(f"❌ Processing monitoring failed: {e}", "ERROR")
        return None

def analyze_processing_results(doc_info, result):
    """Analyze processing results and determine if limits are still present"""
    if not result or result.get('status') != 'completed':
        return {
            'document': doc_info['filename'],
            'status': 'failed',
            'limit_detected': 'unknown',
            'analysis': 'Processing failed'
        }
    
    articles_generated = result.get('articles_generated', 0)
    expected_min = doc_info['expected_min']
    expected_max = doc_info['expected_max']
    
    log_test_result(f"📈 ANALYSIS FOR {doc_info['filename']}:")
    log_test_result(f"   📄 Articles Generated: {articles_generated}")
    log_test_result(f"   📊 Expected Range: {expected_min}-{expected_max}")
    log_test_result(f"   ⏱️ Processing Time: {result['processing_time']/60:.1f} minutes")
    log_test_result(f"   📚 Chunks Created: {result.get('chunks_created', 0)}")
    
    # Determine if limits are still present
    if articles_generated <= 6 and expected_min > 6:
        limit_status = 'HARD_LIMIT_DETECTED'
        analysis = f"CRITICAL: Only {articles_generated} articles generated (expected {expected_min}+). Hard 6-article limit still present."
        log_test_result(f"❌ {analysis}", "CRITICAL_ERROR")
    elif articles_generated < expected_min:
        limit_status = 'SOFT_LIMIT_DETECTED' 
        analysis = f"WARNING: {articles_generated} articles generated (below expected minimum of {expected_min}). Possible processing limits."
        log_test_result(f"⚠️ {analysis}", "WARNING")
    elif articles_generated >= expected_min and articles_generated <= expected_max:
        limit_status = 'WITHIN_EXPECTED_RANGE'
        analysis = f"SUCCESS: {articles_generated} articles generated (within expected range {expected_min}-{expected_max}). No limits detected."
        log_test_result(f"✅ {analysis}", "SUCCESS")
    else:
        limit_status = 'ABOVE_EXPECTED'
        analysis = f"EXCELLENT: {articles_generated} articles generated (above expected maximum of {expected_max}). No limits detected."
        log_test_result(f"🎉 {analysis}", "SUCCESS")
    
    return {
        'document': doc_info['filename'],
        'type': doc_info['type'],
        'size_mb': doc_info['size_mb'],
        'status': 'completed',
        'articles_generated': articles_generated,
        'expected_min': expected_min,
        'expected_max': expected_max,
        'processing_time_minutes': result['processing_time'] / 60,
        'chunks_created': result.get('chunks_created', 0),
        'limit_detected': limit_status,
        'analysis': analysis
    }

def check_backend_logs_for_processing_details():
    """Check backend logs for processing pathway information"""
    try:
        log_test_result("🔍 Checking backend logs for processing details...")
        
        try:
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Check for key processing indicators
                indicators_found = []
                
                if "NO ARTIFICIAL LIMITS APPLIED" in logs:
                    indicators_found.append("✅ NO ARTIFICIAL LIMITS APPLIED")
                
                if "ULTRA-LARGE DOCUMENT DETECTED" in logs:
                    indicators_found.append("✅ ULTRA-LARGE DOCUMENT DETECTED")
                
                if "dynamic calculation" in logs.lower():
                    indicators_found.append("✅ Dynamic calculation active")
                
                if "allowing up to" in logs.lower():
                    indicators_found.append("✅ Dynamic article limit calculation")
                
                # Check for different processing pathways
                if "single_article_simplified" in logs:
                    indicators_found.append("⚠️ Single article simplified pathway used")
                
                if "chunking system operational" in logs.lower():
                    indicators_found.append("✅ Enhanced chunking system operational")
                
                log_test_result("📋 Backend Log Analysis:")
                if indicators_found:
                    for indicator in indicators_found:
                        log_test_result(f"   {indicator}")
                else:
                    log_test_result("   ⚠️ No specific processing indicators found")
                
                return indicators_found
            else:
                log_test_result("⚠️ Could not access backend logs")
                return []
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return []
            
    except Exception as e:
        log_test_result(f"❌ Backend log analysis failed: {e}", "ERROR")
        return []

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

def run_comprehensive_document_limit_test():
    """Run comprehensive test on all 4 documents to identify remaining limits"""
    log_test_result("🚀 STARTING COMPREHENSIVE KNOWLEDGE ENGINE DOCUMENT LIMIT TESTING", "CRITICAL")
    log_test_result("Testing ALL 4 user documents to identify remaining limits")
    log_test_result("=" * 100)
    
    # Test backend health first
    if not test_backend_health():
        log_test_result("❌ Backend health check failed - aborting tests", "CRITICAL_ERROR")
        return None
    
    # Check which documents exist
    available_documents = []
    for doc_info in TEST_DOCUMENTS:
        exists, actual_size = check_file_exists(doc_info)
        if exists:
            doc_info['actual_size'] = actual_size
            available_documents.append(doc_info)
        else:
            log_test_result(f"⚠️ Skipping {doc_info['filename']} - file not found")
    
    if not available_documents:
        log_test_result("❌ No test documents found - cannot proceed", "CRITICAL_ERROR")
        return None
    
    log_test_result(f"📋 Found {len(available_documents)} documents to test")
    
    # Process each document
    test_results = []
    
    for i, doc_info in enumerate(available_documents):
        log_test_result(f"\n{'='*60}")
        log_test_result(f"🔄 PROCESSING DOCUMENT {i+1}/{len(available_documents)}: {doc_info['filename']}", "CRITICAL")
        log_test_result(f"📊 Type: {doc_info['type']}, Size: {doc_info['size_mb']}MB, Expected: {doc_info['expected_min']}-{doc_info['expected_max']} articles")
        log_test_result(f"{'='*60}")
        
        # Upload and process
        job_id = upload_and_process_document(doc_info, doc_info['actual_size'])
        
        if job_id:
            # Monitor processing
            processing_result = monitor_processing(job_id, doc_info, max_wait_minutes=20)
            
            # Analyze results
            analysis = analyze_processing_results(doc_info, processing_result)
            test_results.append(analysis)
        else:
            # Failed to upload
            test_results.append({
                'document': doc_info['filename'],
                'type': doc_info['type'],
                'status': 'upload_failed',
                'limit_detected': 'unknown',
                'analysis': 'Failed to upload document'
            })
        
        # Add delay between documents to avoid overwhelming the system
        if i < len(available_documents) - 1:
            log_test_result("⏳ Waiting 30 seconds before next document...")
            time.sleep(30)
    
    # Check backend logs for processing details
    log_test_result(f"\n{'='*60}")
    log_test_result("🔍 BACKEND LOG ANALYSIS", "CRITICAL")
    log_test_result(f"{'='*60}")
    backend_indicators = check_backend_logs_for_processing_details()
    
    # Generate comprehensive analysis report
    log_test_result(f"\n{'='*100}")
    log_test_result("📊 COMPREHENSIVE ANALYSIS REPORT", "CRITICAL")
    log_test_result(f"{'='*100}")
    
    # Summary statistics
    completed_tests = [r for r in test_results if r['status'] == 'completed']
    failed_tests = [r for r in test_results if r['status'] != 'completed']
    
    hard_limits_detected = [r for r in completed_tests if r['limit_detected'] == 'HARD_LIMIT_DETECTED']
    soft_limits_detected = [r for r in completed_tests if r['limit_detected'] == 'SOFT_LIMIT_DETECTED']
    no_limits_detected = [r for r in completed_tests if r['limit_detected'] in ['WITHIN_EXPECTED_RANGE', 'ABOVE_EXPECTED']]
    
    log_test_result(f"📈 SUMMARY STATISTICS:")
    log_test_result(f"   📄 Total Documents Tested: {len(test_results)}")
    log_test_result(f"   ✅ Successfully Processed: {len(completed_tests)}")
    log_test_result(f"   ❌ Failed Processing: {len(failed_tests)}")
    log_test_result(f"   🚨 Hard Limits Detected: {len(hard_limits_detected)}")
    log_test_result(f"   ⚠️ Soft Limits Detected: {len(soft_limits_detected)}")
    log_test_result(f"   🎉 No Limits Detected: {len(no_limits_detected)}")
    
    # Detailed results for each document
    log_test_result(f"\n📋 DETAILED RESULTS BY DOCUMENT:")
    for result in test_results:
        log_test_result(f"\n📄 {result['document']} ({result.get('type', 'unknown')}):")
        if result['status'] == 'completed':
            log_test_result(f"   Articles Generated: {result['articles_generated']} (expected: {result['expected_min']}-{result['expected_max']})")
            log_test_result(f"   Processing Time: {result['processing_time_minutes']:.1f} minutes")
            log_test_result(f"   Limit Status: {result['limit_detected']}")
            log_test_result(f"   Analysis: {result['analysis']}")
        else:
            log_test_result(f"   Status: {result['status']}")
            log_test_result(f"   Analysis: {result['analysis']}")
    
    # Document type analysis
    docx_results = [r for r in completed_tests if r.get('type') == 'DOCX']
    pdf_results = [r for r in completed_tests if r.get('type') == 'PDF']
    
    if docx_results and pdf_results:
        log_test_result(f"\n📊 DOCUMENT TYPE ANALYSIS:")
        
        docx_avg_articles = sum(r['articles_generated'] for r in docx_results) / len(docx_results)
        pdf_avg_articles = sum(r['articles_generated'] for r in pdf_results) / len(pdf_results)
        
        log_test_result(f"   DOCX Documents: {len(docx_results)} tested, avg {docx_avg_articles:.1f} articles")
        log_test_result(f"   PDF Documents: {len(pdf_results)} tested, avg {pdf_avg_articles:.1f} articles")
        
        docx_limits = [r for r in docx_results if 'LIMIT_DETECTED' in r['limit_detected']]
        pdf_limits = [r for r in pdf_results if 'LIMIT_DETECTED' in r['limit_detected']]
        
        if docx_limits:
            log_test_result(f"   ⚠️ DOCX Limit Issues: {len(docx_limits)}/{len(docx_results)} documents")
        if pdf_limits:
            log_test_result(f"   ⚠️ PDF Limit Issues: {len(pdf_limits)}/{len(pdf_results)} documents")
    
    # Final recommendations
    log_test_result(f"\n🎯 CRITICAL FINDINGS & RECOMMENDATIONS:")
    
    if hard_limits_detected:
        log_test_result("❌ CRITICAL ISSUE: Hard limits (6-article cap) still detected in some documents", "CRITICAL_ERROR")
        for result in hard_limits_detected:
            log_test_result(f"   - {result['document']}: {result['articles_generated']} articles (expected {result['expected_min']}+)")
    
    if soft_limits_detected:
        log_test_result("⚠️ WARNING: Soft limits or processing constraints detected", "WARNING")
        for result in soft_limits_detected:
            log_test_result(f"   - {result['document']}: {result['articles_generated']} articles (expected {result['expected_min']}+)")
    
    if no_limits_detected:
        log_test_result("✅ SUCCESS: Some documents processed without limits", "SUCCESS")
        for result in no_limits_detected:
            log_test_result(f"   - {result['document']}: {result['articles_generated']} articles (expected {result['expected_min']}-{result['expected_max']})")
    
    # Backend processing pathway analysis
    if backend_indicators:
        log_test_result(f"\n🔧 PROCESSING PATHWAY ANALYSIS:")
        log_test_result("Backend logs show the following processing indicators:")
        for indicator in backend_indicators:
            log_test_result(f"   {indicator}")
    
    return {
        'test_results': test_results,
        'summary': {
            'total_tested': len(test_results),
            'completed': len(completed_tests),
            'failed': len(failed_tests),
            'hard_limits': len(hard_limits_detected),
            'soft_limits': len(soft_limits_detected),
            'no_limits': len(no_limits_detected)
        },
        'backend_indicators': backend_indicators,
        'critical_issues': hard_limits_detected + soft_limits_detected
    }

if __name__ == "__main__":
    print("Comprehensive Knowledge Engine Document Limit Testing")
    print("Testing ALL 4 user documents to identify remaining limits")
    print("=" * 80)
    
    results = run_comprehensive_document_limit_test()
    
    if results:
        # Determine exit code based on results
        if results['summary']['hard_limits'] > 0:
            print("\n❌ CRITICAL: Hard limits still detected in system")
            sys.exit(2)  # Critical failure
        elif results['summary']['soft_limits'] > 0:
            print("\n⚠️ WARNING: Soft limits or constraints detected")
            sys.exit(1)  # Warning
        elif results['summary']['completed'] > 0:
            print("\n✅ SUCCESS: No limits detected in processed documents")
            sys.exit(0)  # Success
        else:
            print("\n❌ ERROR: No documents could be processed")
            sys.exit(3)  # Processing failure
    else:
        print("\n❌ CRITICAL ERROR: Test suite failed to run")
        sys.exit(4)  # Test failure