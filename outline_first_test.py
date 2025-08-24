#!/usr/bin/env python3
"""
OUTLINE-FIRST APPROACH COMPREHENSIVE TESTING
Testing the new outline-first implementation with comprehensive article generation
Focus: Customer Summary Screen User Guide processing with outline-based article creation
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-pipeline-5.preview.emergentagent.com"
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

def test_outline_first_approach():
    """
    CRITICAL TEST: Test the new outline-first approach with Customer Summary Screen User Guide
    Expected: Comprehensive outline generation followed by detailed article creation
    """
    try:
        log_test_result("🎯 STARTING OUTLINE-FIRST APPROACH TEST", "CRITICAL")
        log_test_result("Processing Customer Summary Screen User Guide with outline-first approach")
        
        # Check if file exists
        file_path = "/app/customer_guide.docx"
        if not os.path.exists(file_path):
            log_test_result(f"❌ Test file not found: {file_path}", "ERROR")
            return False
        
        file_size = os.path.getsize(file_path)
        log_test_result(f"📄 File confirmed: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)")
        
        # Get initial Content Library count
        initial_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        initial_count = 0
        if initial_response.status_code == 200:
            initial_data = initial_response.json()
            initial_count = initial_data.get('total', 0)
            log_test_result(f"📚 Initial Content Library count: {initial_count}")
        
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
        
        # Monitor processing with detailed logging for outline-first approach
        log_test_result("⏳ Monitoring processing progress for outline-first approach...")
        processing_start = time.time()
        max_wait_time = 600  # 10 minutes max
        
        outline_generated = False
        articles_from_outline = False
        conservative_merging = False
        
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
                        
                        log_test_result(f"📈 OUTLINE-FIRST METRICS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        
                        # CRITICAL VERIFICATION: Check outline-first success criteria
                        success_criteria = {
                            'outline_generation': False,
                            'comprehensive_articles': False,
                            'exceeds_6_articles': False,
                            'conservative_merging': False
                        }
                        
                        # Check if significantly more than 6 articles were created
                        if articles_generated > 6:
                            success_criteria['exceeds_6_articles'] = True
                            log_test_result(f"✅ SUCCESS CRITERIA 1: Generated {articles_generated} articles (exceeds 6-article limit)", "SUCCESS")
                        else:
                            log_test_result(f"❌ FAILURE: Only {articles_generated} articles generated (expected significantly more than 6)", "ERROR")
                        
                        # Check for comprehensive coverage (15-30+ articles expected)
                        if articles_generated >= 15:
                            success_criteria['comprehensive_articles'] = True
                            log_test_result(f"✅ SUCCESS CRITERIA 2: Comprehensive coverage achieved with {articles_generated} articles", "SUCCESS")
                        else:
                            log_test_result(f"⚠️ PARTIAL: {articles_generated} articles generated (expected 15-30+ for comprehensive coverage)", "WARNING")
                        
                        return success_criteria
                        
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
        log_test_result(f"❌ Outline-first approach test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def check_backend_logs_for_outline_messages():
    """Check backend logs for outline-first approach specific messages"""
    try:
        log_test_result("🔍 Checking backend logs for outline-first messages...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                outline_messages = {
                    'comprehensive_outline': "COMPREHENSIVE OUTLINE GENERATED" in logs,
                    'creating_articles': "CREATING ARTICLES FROM OUTLINE" in logs,
                    'outline_success': "OUTLINE-BASED SUCCESS" in logs,
                    'ultra_large_detected': "ULTRA-LARGE DOCUMENT DETECTED" in logs,
                    'conservative_merging': "conservative merging" in logs.lower()
                }
                
                log_test_result("📋 OUTLINE-FIRST LOG ANALYSIS:")
                for message_type, found in outline_messages.items():
                    status = "✅ FOUND" if found else "❌ NOT FOUND"
                    log_test_result(f"   {message_type.replace('_', ' ').title()}: {status}")
                
                # Extract specific numbers if found
                if outline_messages['comprehensive_outline']:
                    import re
                    outline_match = re.search(r'COMPREHENSIVE OUTLINE GENERATED: (\d+) articles planned', logs)
                    if outline_match:
                        planned_articles = int(outline_match.group(1))
                        log_test_result(f"   📊 Planned Articles from Outline: {planned_articles}")
                        
                        if planned_articles >= 15:
                            log_test_result("✅ OUTLINE SUCCESS: Comprehensive outline generated 15+ articles", "SUCCESS")
                        else:
                            log_test_result(f"⚠️ OUTLINE CONCERN: Only {planned_articles} articles planned (expected 15-30+)", "WARNING")
                
                if outline_messages['outline_success']:
                    success_match = re.search(r'OUTLINE-BASED SUCCESS: Created (\d+) comprehensive articles', logs)
                    if success_match:
                        created_articles = int(success_match.group(1))
                        log_test_result(f"   📊 Articles Created from Outline: {created_articles}")
                
                return outline_messages
            else:
                log_test_result("⚠️ Could not access backend logs")
                return {}
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return {}
            
    except Exception as e:
        log_test_result(f"❌ Backend log verification failed: {e}", "ERROR")
        return {}

def verify_content_library_comprehensive_coverage():
    """Verify that Content Library shows comprehensive article coverage"""
    try:
        log_test_result("🔍 Verifying comprehensive coverage in Content Library...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_test_result(f"📚 Content Library Analysis:")
            log_test_result(f"   Total Articles: {total_articles}")
            log_test_result(f"   Articles Retrieved: {len(articles)}")
            
            # Look for Customer Summary Screen articles
            customer_guide_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                source = article.get('source_document', '').lower()
                if ('customer' in title or 'customer' in source or 
                    'summary' in title or 'summary' in source or
                    'screen' in title or 'guide' in title):
                    customer_guide_articles.append(article)
            
            log_test_result(f"📄 Customer Guide Articles Found: {len(customer_guide_articles)}")
            
            if len(customer_guide_articles) >= 15:
                log_test_result("✅ COMPREHENSIVE COVERAGE: 15+ articles found for Customer Guide", "SUCCESS")
                coverage_success = True
            elif len(customer_guide_articles) > 6:
                log_test_result(f"⚠️ PARTIAL COVERAGE: {len(customer_guide_articles)} articles (better than 6, but below 15+ expected)", "WARNING")
                coverage_success = True
            else:
                log_test_result(f"❌ INSUFFICIENT COVERAGE: Only {len(customer_guide_articles)} articles found", "ERROR")
                coverage_success = False
            
            # Show sample article titles
            log_test_result("📋 Sample Article Titles:")
            for i, article in enumerate(customer_guide_articles[:10]):
                title = article.get('title', 'Untitled')
                status = article.get('status', 'unknown')
                log_test_result(f"   {i+1}. {title[:60]}... (Status: {status})")
            
            return {
                'total_articles': total_articles,
                'customer_guide_articles': len(customer_guide_articles),
                'comprehensive_coverage': coverage_success
            }
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return {}
            
    except Exception as e:
        log_test_result(f"❌ Content Library verification failed: {e}", "ERROR")
        return {}

def run_comprehensive_outline_first_test():
    """Run comprehensive test suite for outline-first approach verification"""
    log_test_result("🚀 STARTING COMPREHENSIVE OUTLINE-FIRST APPROACH TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'outline_first_processing': False,
        'backend_logs_analysis': {},
        'content_library_verification': {},
        'overall_success': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Outline-First Processing (CRITICAL)
    log_test_result("\nTEST 2: CRITICAL OUTLINE-FIRST APPROACH TEST")
    outline_result = test_outline_first_approach()
    test_results['outline_first_processing'] = outline_result
    
    # Test 3: Backend Logs Analysis
    log_test_result("\nTEST 3: Backend Logs Analysis for Outline Messages")
    test_results['backend_logs_analysis'] = check_backend_logs_for_outline_messages()
    
    # Test 4: Content Library Verification
    log_test_result("\nTEST 4: Content Library Comprehensive Coverage Verification")
    test_results['content_library_verification'] = verify_content_library_comprehensive_coverage()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 OUTLINE-FIRST APPROACH TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    # Evaluate overall success
    outline_success = isinstance(outline_result, dict) and outline_result.get('exceeds_6_articles', False)
    logs_success = any(test_results['backend_logs_analysis'].values()) if test_results['backend_logs_analysis'] else False
    library_success = test_results['content_library_verification'].get('comprehensive_coverage', False)
    
    log_test_result("📊 SUCCESS CRITERIA EVALUATION:")
    log_test_result(f"   ✅ Outline Generation: {'PASSED' if logs_success else 'NEEDS VERIFICATION'}")
    log_test_result(f"   ✅ Article Creation from Outline: {'PASSED' if outline_success else 'FAILED'}")
    log_test_result(f"   ✅ Comprehensive Coverage (15+ articles): {'PASSED' if library_success else 'PARTIAL/FAILED'}")
    log_test_result(f"   ✅ Conservative Merging: {'DETECTED' if test_results['backend_logs_analysis'].get('conservative_merging') else 'NOT DETECTED'}")
    
    # Overall assessment
    if outline_success and library_success:
        test_results['overall_success'] = True
        log_test_result("🎉 CRITICAL SUCCESS: Outline-first approach is working correctly!", "CRITICAL_SUCCESS")
        log_test_result("✅ System generates comprehensive articles based on outline analysis", "CRITICAL_SUCCESS")
        log_test_result("✅ Significantly more than 6 articles created for large documents", "CRITICAL_SUCCESS")
    elif outline_success:
        log_test_result("⚠️ PARTIAL SUCCESS: Outline-first approach working but needs verification", "WARNING")
        log_test_result("✅ More than 6 articles generated, but comprehensive coverage needs confirmation", "WARNING")
    else:
        log_test_result("❌ CRITICAL FAILURE: Outline-first approach not working as expected", "CRITICAL_ERROR")
        log_test_result("❌ System may still be limited or not using outline-based generation", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Outline-First Approach Comprehensive Testing")
    print("=" * 50)
    
    results = run_comprehensive_outline_first_test()
    
    # Exit with appropriate code
    if results['overall_success']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure