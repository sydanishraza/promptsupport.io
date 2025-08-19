#!/usr/bin/env python3
"""
CRITICAL REGRESSION INVESTIGATION: 0 Articles Generated After Outline-First Implementation
Testing to identify exactly where the processing pipeline is failing
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

def test_simple_document_processing():
    """
    CRITICAL TEST: Process a simple document to trace the processing pipeline
    Focus: Identify where exactly the processing is failing (outline vs article creation)
    """
    try:
        log_test_result("🎯 STARTING CRITICAL REGRESSION INVESTIGATION", "CRITICAL")
        log_test_result("Testing simple document processing to trace pipeline failure")
        
        # Create a simple test document content
        test_content = """
        # Test Document for Regression Investigation
        
        ## Introduction
        This is a test document to investigate the 0 articles regression issue.
        
        ## Section 1: Basic Content
        This section contains basic content that should be processed into articles.
        The content is substantial enough to warrant article generation.
        
        ## Section 2: Additional Content  
        This section provides additional content to ensure we have enough material
        for the outline-first processing to work correctly.
        
        ## Conclusion
        This concludes our test document with sufficient content for processing.
        """
        
        # Test with file upload
        log_test_result("📤 Testing file upload...")
        
        # Create a temporary text file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('regression_test.txt', f, 'text/plain')}
                metadata = {'metadata': '{}'}
                
                start_time = time.time()
                response = requests.post(f"{API_BASE}/content/upload", 
                                       files=files, 
                                       data=metadata,
                                       timeout=300)
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
        if response.status_code != 200:
            log_test_result(f"❌ Text upload failed: Status {response.status_code}", "ERROR")
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
        max_wait_time = 300  # 5 minutes max
        
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
                        
                        log_test_result(f"📈 CRITICAL REGRESSION ANALYSIS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        
                        # CRITICAL VERIFICATION: Check for 0 articles regression
                        if articles_generated == 0:
                            log_test_result(f"❌ CRITICAL REGRESSION CONFIRMED: 0 articles generated", "CRITICAL_ERROR")
                            log_test_result("❌ OUTLINE-FIRST IMPLEMENTATION HAS BROKEN ARTICLE GENERATION", "CRITICAL_ERROR")
                            
                            # Try to get more details from the job status
                            if 'error' in status_data:
                                log_test_result(f"❌ Error details: {status_data['error']}", "ERROR")
                            
                            return False
                        else:
                            log_test_result(f"✅ Articles generated: {articles_generated} (regression not present)", "SUCCESS")
                            return True
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test_result(f"❌ Processing failed: {error_msg}", "ERROR")
                        
                        # Log detailed error for debugging
                        if 'traceback' in status_data:
                            log_test_result(f"❌ Traceback: {status_data['traceback'][:500]}...", "ERROR")
                        
                        return False
                    
                    # Continue monitoring
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Regression test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_outline_generation_directly():
    """Test if outline generation is working by checking backend logs"""
    try:
        log_test_result("🔍 Checking backend logs for outline generation issues...")
        
        # Try to get recent backend logs
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Check for outline generation indicators
                outline_indicators = [
                    "GENERATING COMPREHENSIVE OUTLINE",
                    "COMPREHENSIVE OUTLINE GENERATED",
                    "Outline JSON parsing error",
                    "Error generating comprehensive outline",
                    "CREATING ARTICLES FROM OUTLINE",
                    "OUTLINE-BASED ARTICLE CREATION COMPLETE"
                ]
                
                found_indicators = []
                for indicator in outline_indicators:
                    if indicator in logs:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    log_test_result(f"✅ Found outline processing indicators: {found_indicators}", "SUCCESS")
                    
                    # Check for specific errors
                    if "Outline JSON parsing error" in logs:
                        log_test_result("❌ FOUND JSON PARSING ERROR in outline generation", "ERROR")
                        return False
                    elif "Error generating comprehensive outline" in logs:
                        log_test_result("❌ FOUND OUTLINE GENERATION ERROR", "ERROR")
                        return False
                    else:
                        log_test_result("✅ Outline generation appears to be working", "SUCCESS")
                        return True
                else:
                    log_test_result("⚠️ No outline processing indicators found in logs")
                    return False
            else:
                log_test_result("⚠️ Could not access backend logs")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Outline generation test failed: {e}", "ERROR")
        return False

def test_llm_call_functionality():
    """Test if LLM calls are working by checking for LLM-related errors in logs"""
    try:
        log_test_result("🔍 Checking for LLM call issues in backend logs...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Check for LLM-related errors
                llm_error_indicators = [
                    "call_llm_with_fallback",
                    "LLM call failed",
                    "OpenAI API error",
                    "Anthropic API error",
                    "JSON parsing error",
                    "function signature",
                    "TypeError",
                    "AttributeError"
                ]
                
                found_errors = []
                for indicator in llm_error_indicators:
                    if indicator in logs:
                        found_errors.append(indicator)
                
                if found_errors:
                    log_test_result(f"⚠️ Found potential LLM issues: {found_errors}", "WARNING")
                    
                    # Check for specific critical errors
                    if "TypeError" in logs or "AttributeError" in logs:
                        log_test_result("❌ FOUND FUNCTION SIGNATURE ERRORS - likely cause of 0 articles", "ERROR")
                        return False
                    elif "JSON parsing error" in logs:
                        log_test_result("❌ FOUND JSON PARSING ERRORS - likely cause of 0 articles", "ERROR")
                        return False
                    else:
                        log_test_result("⚠️ Found LLM-related indicators but no critical errors", "WARNING")
                        return True
                else:
                    log_test_result("✅ No obvious LLM call errors found", "SUCCESS")
                    return True
            else:
                log_test_result("⚠️ Could not access backend logs")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ LLM log check failed: {log_error}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ LLM functionality test failed: {e}", "ERROR")
        return False

def test_fallback_mechanism():
    """Test if fallback to legacy processing is working"""
    try:
        log_test_result("🔍 Checking for fallback mechanism indicators...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Check for fallback indicators
                fallback_indicators = [
                    "Falling back to section-based analysis",
                    "fallback to legacy processing",
                    "outline generation failed",
                    "using legacy chunking"
                ]
                
                found_fallbacks = []
                for indicator in fallback_indicators:
                    if indicator in logs:
                        found_fallbacks.append(indicator)
                
                if found_fallbacks:
                    log_test_result(f"⚠️ Found fallback indicators: {found_fallbacks}", "WARNING")
                    log_test_result("⚠️ System is falling back but may not be working correctly", "WARNING")
                    return False
                else:
                    log_test_result("✅ No fallback indicators found - outline processing may be working", "SUCCESS")
                    return True
            else:
                log_test_result("⚠️ Could not access backend logs")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ Fallback mechanism check failed: {log_error}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Fallback mechanism test failed: {e}", "ERROR")
        return False

def run_regression_investigation():
    """Run comprehensive regression investigation"""
    log_test_result("🚀 STARTING CRITICAL REGRESSION INVESTIGATION", "CRITICAL")
    log_test_result("Investigating 0 articles generated after outline-first implementation")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'simple_processing': False,
        'outline_generation': False,
        'llm_functionality': False,
        'fallback_mechanism': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Simple Document Processing (CRITICAL)
    log_test_result("\nTEST 2: CRITICAL SIMPLE DOCUMENT PROCESSING TEST")
    test_results['simple_processing'] = test_simple_document_processing()
    
    # Test 3: Outline Generation Check
    log_test_result("\nTEST 3: Outline Generation Investigation")
    test_results['outline_generation'] = test_outline_generation_directly()
    
    # Test 4: LLM Call Functionality
    log_test_result("\nTEST 4: LLM Call Functionality Check")
    test_results['llm_functionality'] = test_llm_call_functionality()
    
    # Test 5: Fallback Mechanism
    log_test_result("\nTEST 5: Fallback Mechanism Check")
    test_results['fallback_mechanism'] = test_fallback_mechanism()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 REGRESSION INVESTIGATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Provide specific diagnosis
    if not test_results['simple_processing']:
        log_test_result("❌ CRITICAL REGRESSION CONFIRMED: 0 articles being generated", "CRITICAL_ERROR")
        
        if not test_results['outline_generation']:
            log_test_result("🔍 ROOT CAUSE: Outline generation is failing", "CRITICAL_ERROR")
        elif not test_results['llm_functionality']:
            log_test_result("🔍 ROOT CAUSE: LLM calls are failing (function signature issues)", "CRITICAL_ERROR")
        elif not test_results['fallback_mechanism']:
            log_test_result("🔍 ROOT CAUSE: Fallback mechanism is not working", "CRITICAL_ERROR")
        else:
            log_test_result("🔍 ROOT CAUSE: Unknown - requires deeper investigation", "CRITICAL_ERROR")
    else:
        log_test_result("✅ No regression detected - articles are being generated correctly", "SUCCESS")
    
    return test_results

if __name__ == "__main__":
    print("Critical Regression Investigation: 0 Articles Generated")
    print("=" * 60)
    
    results = run_regression_investigation()
    
    # Exit with appropriate code
    if results['simple_processing']:
        sys.exit(0)  # Success - no regression
    else:
        sys.exit(1)  # Failure - regression confirmed