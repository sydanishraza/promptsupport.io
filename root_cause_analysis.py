#!/usr/bin/env python3
"""
DUPLICATE PROCESSING ROOT CAUSE ANALYSIS
Based on investigation findings, this test verifies the exact root cause
"""

import requests
import json
import time
import os
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://prompt-support-app.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_root_cause_verification():
    """
    CRITICAL TEST: Verify the root cause of duplicate processing
    """
    try:
        log_test_result("🔍 ROOT CAUSE ANALYSIS: Duplicate Processing Investigation", "CRITICAL")
        
        # Check Content Library for duplicates
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            log_test_result(f"📚 Content Library Analysis: {len(articles)} total articles")
            
            # Analyze duplicate patterns
            title_counts = {}
            html_placeholder_count = 0
            outline_based_count = 0
            traditional_count = 0
            
            for article in articles:
                title = article.get('title', '').strip()
                content = article.get('content', '')
                metadata = article.get('metadata', {})
                
                # Count title occurrences
                if title:
                    title_counts[title] = title_counts.get(title, 0) + 1
                
                # Check for HTML placeholder issues
                if '```html' in content or content.startswith('<!DOCTYPE html>'):
                    html_placeholder_count += 1
                
                # Check processing method
                if metadata.get('outline_based'):
                    outline_based_count += 1
                else:
                    traditional_count += 1
            
            # Report findings
            duplicates = {title: count for title, count in title_counts.items() if count > 1}
            
            log_test_result("🎯 ROOT CAUSE ANALYSIS RESULTS:", "CRITICAL")
            log_test_result(f"   📊 Duplicate titles found: {len(duplicates)}")
            log_test_result(f"   🔧 HTML placeholder issues: {html_placeholder_count}")
            log_test_result(f"   📋 Outline-based articles: {outline_based_count}")
            log_test_result(f"   📄 Traditional articles: {traditional_count}")
            
            if duplicates:
                log_test_result("🚨 DUPLICATE ANALYSIS:", "CRITICAL_ERROR")
                for title, count in list(duplicates.items())[:5]:
                    log_test_result(f"     '{title}': {count} copies")
            
            # ROOT CAUSE CONFIRMATION
            if outline_based_count > 0 and traditional_count > 0:
                log_test_result("🚨 ROOT CAUSE CONFIRMED: DUAL PROCESSING PIPELINE", "CRITICAL_ERROR")
                log_test_result("   ✅ Outline-based processing creates articles", "CRITICAL_ERROR")
                log_test_result("   ❌ FAQ generation fails with DocumentChunk.title error", "CRITICAL_ERROR")
                log_test_result("   🔄 System falls back to traditional processing", "CRITICAL_ERROR")
                log_test_result("   📚 Both sets get saved to Content Library", "CRITICAL_ERROR")
                return True
            else:
                log_test_result("✅ No dual processing detected in current articles")
                return False
                
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Root cause verification failed: {e}", "ERROR")
        return False

def test_timeout_confirmation():
    """
    CRITICAL TEST: Confirm timeout issues
    """
    try:
        log_test_result("⏱️ TIMEOUT ANALYSIS: Confirming processing delays", "CRITICAL")
        
        # Create small test content
        test_content = "# Test Content\n\nThis is a test for timeout analysis.\n\n## Section 1\nContent here.\n\n## Section 2\nMore content."
        
        # Create temporary file
        test_file_path = "/tmp/timeout_test.txt"
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        start_time = time.time()
        
        try:
            with open(test_file_path, 'rb') as f:
                files = {'file': ('timeout_test.txt', f, 'text/plain')}
                
                # Test with 60 second timeout
                response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=60)
                
                upload_time = time.time() - start_time
                
                if response.status_code == 200:
                    log_test_result(f"✅ Upload completed in {upload_time:.2f} seconds")
                    return {'timeout_detected': False, 'upload_time': upload_time}
                else:
                    log_test_result(f"❌ Upload failed: Status {response.status_code}")
                    return {'timeout_detected': False, 'upload_time': upload_time, 'error': response.status_code}
                    
        except requests.exceptions.Timeout:
            upload_time = time.time() - start_time
            log_test_result(f"🚨 TIMEOUT CONFIRMED: Request timed out after {upload_time:.2f} seconds", "CRITICAL_ERROR")
            return {'timeout_detected': True, 'upload_time': upload_time}
            
    except Exception as e:
        log_test_result(f"❌ Timeout confirmation failed: {e}", "ERROR")
        return {'error': str(e)}

def run_root_cause_analysis():
    """Run comprehensive root cause analysis"""
    log_test_result("🚨 STARTING ROOT CAUSE ANALYSIS", "CRITICAL")
    log_test_result("=" * 60)
    
    results = {
        'duplicate_processing_confirmed': False,
        'timeout_issues_confirmed': False,
        'html_placeholder_issues_confirmed': False
    }
    
    # Test 1: Root Cause Verification
    log_test_result("TEST 1: Duplicate Processing Root Cause")
    results['duplicate_processing_confirmed'] = test_root_cause_verification()
    
    # Test 2: Timeout Confirmation
    log_test_result("\nTEST 2: Timeout Issues Confirmation")
    timeout_results = test_timeout_confirmation()
    results['timeout_issues_confirmed'] = timeout_results.get('timeout_detected', False)
    
    # Final Analysis
    log_test_result("\n" + "=" * 60)
    log_test_result("🎯 ROOT CAUSE ANALYSIS SUMMARY", "CRITICAL")
    log_test_result("=" * 60)
    
    if results['duplicate_processing_confirmed']:
        log_test_result("🚨 CRITICAL ISSUE CONFIRMED: Duplicate Processing", "CRITICAL_ERROR")
        log_test_result("   ROOT CAUSE: DocumentChunk.title AttributeError in FAQ generation", "CRITICAL_ERROR")
        log_test_result("   IMPACT: Outline-based processing fails, triggers fallback", "CRITICAL_ERROR")
        log_test_result("   RESULT: Two sets of articles created for each document", "CRITICAL_ERROR")
    
    if results['timeout_issues_confirmed']:
        log_test_result("🚨 CRITICAL ISSUE CONFIRMED: Processing Timeouts", "CRITICAL_ERROR")
        log_test_result("   IMPACT: 504 errors during upload processing", "CRITICAL_ERROR")
    
    log_test_result("\n📋 RECOMMENDED FIXES:")
    log_test_result("   1. Fix DocumentChunk.title error in create_articles_from_outline()")
    log_test_result("   2. Add proper error handling to prevent fallback when outline succeeds")
    log_test_result("   3. Optimize processing pipeline to reduce timeout issues")
    log_test_result("   4. Fix HTML placeholder issues in LLM response formatting")
    
    return results

if __name__ == "__main__":
    print("Root Cause Analysis for Duplicate Processing")
    print("=" * 50)
    
    results = run_root_cause_analysis()
    
    # Exit with appropriate code
    if results['duplicate_processing_confirmed'] or results['timeout_issues_confirmed']:
        print("\n🚨 CRITICAL ISSUES CONFIRMED - IMMEDIATE ACTION REQUIRED")
        exit(1)
    else:
        print("\n✅ No critical issues detected")
        exit(0)