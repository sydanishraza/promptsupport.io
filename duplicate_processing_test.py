#!/usr/bin/env python3
"""
CRITICAL DUPLICATE PROCESSING FIX VERIFICATION TEST
Testing the critical duplicate processing fix - verify only ONE set of articles is generated

SUCCESS CRITERIA:
- Only ONE set of articles generated per document processing
- Backend logs show outline-first success with legacy processing skipped
- No duplicate titles in Content Library from same processing session
- Reasonable article count proportional to document size
- Complete elimination of duplicate processing pipeline execution
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import subprocess

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
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

def get_content_library_baseline():
    """Get baseline article count before processing"""
    try:
        log_test_result("📊 Getting Content Library baseline...")
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_test_result(f"📚 Baseline: {total_articles} total articles in Content Library")
            return total_articles, articles
        else:
            log_test_result(f"❌ Failed to get baseline: Status {response.status_code}", "ERROR")
            return 0, []
            
    except Exception as e:
        log_test_result(f"❌ Baseline check failed: {e}", "ERROR")
        return 0, []

def create_test_document():
    """Create a test document for duplicate processing verification"""
    test_content = """# Duplicate Processing Test Document

## Introduction
This is a comprehensive test document designed to verify that the duplicate processing fix is working correctly. The document contains substantial content to trigger the outline-first processing approach.

## Getting Started
This section covers the initial setup and configuration steps required to begin using the system effectively.

### Prerequisites
Before you begin, ensure you have the following prerequisites in place:
- System requirements met
- Proper access credentials
- Network connectivity established

### Installation Steps
Follow these detailed installation steps:
1. Download the required components
2. Configure the system settings
3. Verify the installation
4. Test the basic functionality

## Advanced Features
This section explores the advanced features and capabilities of the system.

### Feature Set Overview
The system provides a comprehensive set of features including:
- Advanced processing capabilities
- Real-time monitoring
- Automated workflows
- Integration options

### Configuration Options
Multiple configuration options are available:
- Performance tuning parameters
- Security settings
- User interface customization
- API configuration

## Implementation Guide
This comprehensive implementation guide provides step-by-step instructions for deploying the system in your environment.

### Planning Phase
Proper planning is essential for successful implementation:
- Requirements analysis
- Resource allocation
- Timeline development
- Risk assessment

### Deployment Process
The deployment process involves several key stages:
- Environment preparation
- System installation
- Configuration setup
- Testing and validation

## Best Practices
Following best practices ensures optimal system performance and reliability.

### Performance Optimization
Key performance optimization strategies include:
- Resource monitoring
- Load balancing
- Caching strategies
- Database optimization

### Security Considerations
Important security considerations:
- Access control implementation
- Data encryption
- Audit logging
- Vulnerability management

## Troubleshooting
This section provides comprehensive troubleshooting guidance for common issues.

### Common Issues
Frequently encountered issues and their solutions:
- Connection problems
- Performance degradation
- Configuration errors
- Integration failures

### Diagnostic Tools
Available diagnostic tools and utilities:
- System health checks
- Performance monitors
- Log analyzers
- Network diagnostics

## Conclusion
This document provides comprehensive coverage of the system capabilities and implementation guidance. The content is designed to test the duplicate processing fix thoroughly.
"""
    
    # Write test document to file
    test_file_path = "/tmp/duplicate_test_document.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    log_test_result(f"📄 Created test document: {len(test_content)} characters")
    return test_file_path

def process_test_document(file_path):
    """Process the test document and monitor for duplicates"""
    try:
        log_test_result("🎯 STARTING DUPLICATE PROCESSING FIX VERIFICATION", "CRITICAL")
        log_test_result("Processing test document to verify only ONE set of articles is generated")
        
        # Upload and process the document
        log_test_result("📤 Uploading test document...")
        
        with open(file_path, 'rb') as f:
            files = {'file': ('duplicate_test_document.txt', f, 'text/plain')}
            
            # Start processing
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
            
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
        
        # Monitor processing with detailed logging
        log_test_result("⏳ Monitoring processing progress...")
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return None
            
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
                        
                        log_test_result(f"📈 PROCESSING METRICS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        
                        return {
                            'job_id': job_id,
                            'articles_generated': articles_generated,
                            'chunks_created': chunks_created,
                            'processing_time': processing_time
                        }
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return None
                    
                    # Continue monitoring
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Document processing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None

def verify_no_duplicates_in_content_library(baseline_count, baseline_articles, processing_result):
    """Verify no duplicate articles were created in Content Library"""
    try:
        log_test_result("🔍 VERIFYING NO DUPLICATE ARTICLES IN CONTENT LIBRARY", "CRITICAL")
        
        # Get updated Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Failed to get updated Content Library: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        current_total = data.get('total', 0)
        current_articles = data.get('articles', [])
        
        # Calculate new articles added
        new_articles_count = current_total - baseline_count
        expected_articles = processing_result.get('articles_generated', 0)
        
        log_test_result(f"📊 DUPLICATE ANALYSIS:")
        log_test_result(f"   Baseline articles: {baseline_count}")
        log_test_result(f"   Current articles: {current_total}")
        log_test_result(f"   New articles added: {new_articles_count}")
        log_test_result(f"   Expected articles: {expected_articles}")
        
        # CRITICAL CHECK 1: Article count should match exactly
        if new_articles_count == expected_articles:
            log_test_result("✅ ARTICLE COUNT VERIFICATION PASSED: Exact match between generated and stored", "SUCCESS")
        elif new_articles_count > expected_articles:
            log_test_result(f"❌ DUPLICATE ARTICLES DETECTED: {new_articles_count - expected_articles} extra articles found", "CRITICAL_ERROR")
            return False
        else:
            log_test_result(f"❌ MISSING ARTICLES: {expected_articles - new_articles_count} articles not stored", "ERROR")
            return False
        
        # CRITICAL CHECK 2: Look for duplicate titles from same processing session
        new_articles = [art for art in current_articles if art.get('id') not in [ba.get('id') for ba in baseline_articles]]
        titles = [art.get('title', '') for art in new_articles]
        
        # Check for duplicate titles
        title_counts = {}
        for title in titles:
            title_counts[title] = title_counts.get(title, 0) + 1
        
        duplicates = {title: count for title, count in title_counts.items() if count > 1}
        
        if duplicates:
            log_test_result(f"❌ DUPLICATE TITLES DETECTED:", "CRITICAL_ERROR")
            for title, count in duplicates.items():
                log_test_result(f"   '{title}': {count} copies")
            return False
        else:
            log_test_result("✅ NO DUPLICATE TITLES FOUND: All article titles are unique", "SUCCESS")
        
        # CRITICAL CHECK 3: Verify reasonable article count
        test_content_length = 2218  # Approximate length of test document
        articles_per_1000_chars = new_articles_count / (test_content_length / 1000)
        
        log_test_result(f"📈 ARTICLE GENERATION ANALYSIS:")
        log_test_result(f"   Content length: {test_content_length} characters")
        log_test_result(f"   Articles per 1000 chars: {articles_per_1000_chars:.1f}")
        
        if articles_per_1000_chars > 10:  # More than 10 articles per 1000 chars suggests duplication
            log_test_result(f"❌ EXCESSIVE ARTICLE GENERATION: {articles_per_1000_chars:.1f} articles per 1000 chars (suggests duplication)", "WARNING")
        else:
            log_test_result(f"✅ REASONABLE ARTICLE COUNT: {articles_per_1000_chars:.1f} articles per 1000 chars", "SUCCESS")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Duplicate verification failed: {e}", "ERROR")
        return False

def check_backend_logs_for_outline_first_success():
    """Check backend logs for outline-first processing success indicators"""
    try:
        log_test_result("🔍 CHECKING BACKEND LOGS FOR OUTLINE-FIRST SUCCESS", "CRITICAL")
        
        # Get recent backend logs
        try:
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Check for key indicators
                success_indicators = {
                    'outline_generated': "COMPREHENSIVE OUTLINE GENERATED" in logs,
                    'outline_based_success': "OUTLINE-BASED SUCCESS" in logs,
                    'creating_from_outline': "CREATING ARTICLES FROM OUTLINE" in logs,
                    'skipping_legacy': "SKIPPING LEGACY PROCESSING" in logs,
                    'outline_complete': "OUTLINE-BASED ARTICLE CREATION COMPLETE" in logs
                }
                
                log_test_result("📋 BACKEND LOG ANALYSIS:")
                for indicator, found in success_indicators.items():
                    status = "✅ FOUND" if found else "❌ NOT FOUND"
                    log_test_result(f"   {indicator.replace('_', ' ').title()}: {status}")
                
                # Check for error indicators
                error_indicators = {
                    'documentchunk_error': "DocumentChunk' object has no attribute 'title'" in logs,
                    'fallback_triggered': "falling back to traditional processing" in logs.lower(),
                    'dual_processing': logs.count("CREATING ARTICLES FROM OUTLINE") > 1
                }
                
                log_test_result("🚨 ERROR ANALYSIS:")
                for indicator, found in error_indicators.items():
                    status = "❌ FOUND" if found else "✅ NOT FOUND"
                    log_test_result(f"   {indicator.replace('_', ' ').title()}: {status}")
                
                # Overall assessment
                success_count = sum(success_indicators.values())
                error_count = sum(error_indicators.values())
                
                if success_count >= 3 and error_count == 0:
                    log_test_result("✅ OUTLINE-FIRST PROCESSING SUCCESS CONFIRMED", "SUCCESS")
                    return True
                elif error_count > 0:
                    log_test_result("❌ PROCESSING ERRORS DETECTED IN LOGS", "ERROR")
                    return False
                else:
                    log_test_result("⚠️ INSUFFICIENT LOG EVIDENCE FOR OUTLINE-FIRST SUCCESS", "WARNING")
                    return False
            else:
                log_test_result("⚠️ Could not access backend logs", "WARNING")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend log verification failed: {e}", "ERROR")
        return False

def run_comprehensive_duplicate_processing_test():
    """Run comprehensive test suite for duplicate processing fix verification"""
    log_test_result("🚀 STARTING COMPREHENSIVE DUPLICATE PROCESSING FIX TEST", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'outline_first_processing': False,
        'database_insertion_verification': False,
        'article_count_analysis': False,
        'backend_log_analysis': False,
        'end_to_end_duplicate_prevention': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Get baseline before processing
    log_test_result("\nTEST 2: Content Library Baseline")
    baseline_count, baseline_articles = get_content_library_baseline()
    
    # Test 3: Create and process test document
    log_test_result("\nTEST 3: Outline-First Processing Test")
    test_file_path = create_test_document()
    processing_result = process_test_document(test_file_path)
    
    if processing_result:
        test_results['outline_first_processing'] = True
        log_test_result("✅ OUTLINE-FIRST PROCESSING COMPLETED", "SUCCESS")
    else:
        log_test_result("❌ OUTLINE-FIRST PROCESSING FAILED", "ERROR")
        return test_results
    
    # Test 4: Database Insertion Verification
    log_test_result("\nTEST 4: Database Insertion Verification")
    test_results['database_insertion_verification'] = verify_no_duplicates_in_content_library(
        baseline_count, baseline_articles, processing_result
    )
    
    # Test 5: Article Count Analysis (already done in verification)
    test_results['article_count_analysis'] = test_results['database_insertion_verification']
    
    # Test 6: Backend Log Analysis
    log_test_result("\nTEST 5: Backend Log Analysis")
    test_results['backend_log_analysis'] = check_backend_logs_for_outline_first_success()
    
    # Test 7: End-to-End Duplicate Prevention
    log_test_result("\nTEST 6: End-to-End Duplicate Prevention")
    test_results['end_to_end_duplicate_prevention'] = (
        test_results['outline_first_processing'] and 
        test_results['database_insertion_verification'] and
        test_results['backend_log_analysis']
    )
    
    # Clean up test file
    try:
        os.remove(test_file_path)
        log_test_result("🧹 Cleaned up test file")
    except:
        pass
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 DUPLICATE PROCESSING FIX TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if test_results['end_to_end_duplicate_prevention']:
        log_test_result("🎉 CRITICAL SUCCESS: Duplicate processing fix is working correctly!", "CRITICAL_SUCCESS")
        log_test_result("✅ Only ONE set of articles generated per document processing", "CRITICAL_SUCCESS")
        log_test_result("✅ Complete elimination of duplicate processing pipeline execution", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Duplicate processing issues still exist", "CRITICAL_ERROR")
        log_test_result("❌ System may still be creating duplicate articles", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Duplicate Processing Fix Verification Test")
    print("=" * 50)
    
    results = run_comprehensive_duplicate_processing_test()
    
    # Exit with appropriate code
    if results['end_to_end_duplicate_prevention']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure