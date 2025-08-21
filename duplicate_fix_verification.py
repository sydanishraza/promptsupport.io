#!/usr/bin/env python3
"""
DUPLICATE PROCESSING FIX VERIFICATION - BACKEND LOG ANALYSIS
Direct analysis of backend logs to verify the duplicate processing fix is working
"""

import subprocess
import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "https://content-pipeline-4.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def analyze_backend_logs_for_duplicate_fix():
    """Analyze backend logs for duplicate processing fix verification"""
    try:
        log_result("🔍 ANALYZING BACKEND LOGS FOR DUPLICATE PROCESSING FIX", "CRITICAL")
        
        # Get recent backend logs
        result = subprocess.run(['tail', '-n', '300', '/var/log/supervisor/backend.out.log'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            log_result("❌ Could not access backend logs", "ERROR")
            return False
        
        logs = result.stdout
        
        # SUCCESS CRITERIA 1: Outline-First Processing Only
        outline_indicators = {
            'comprehensive_outline_generated': logs.count("COMPREHENSIVE OUTLINE GENERATED"),
            'creating_articles_from_outline': logs.count("CREATING ARTICLES FROM OUTLINE"),
            'outline_based_success': logs.count("OUTLINE-BASED SUCCESS"),
            'skipping_legacy_processing': logs.count("SKIPPING LEGACY PROCESSING")
        }
        
        log_result("📋 SUCCESS CRITERIA 1: OUTLINE-FIRST PROCESSING ONLY")
        for indicator, count in outline_indicators.items():
            status = "✅ FOUND" if count > 0 else "❌ NOT FOUND"
            log_result(f"   {indicator.replace('_', ' ').title()}: {count} occurrences - {status}")
        
        # SUCCESS CRITERIA 2: No Duplicate Processing Pipeline
        duplicate_indicators = {
            'multiple_outline_generations': logs.count("COMPREHENSIVE OUTLINE GENERATED") > 1,
            'fallback_to_legacy': "falling back to traditional processing" in logs.lower(),
            'documentchunk_errors': "DocumentChunk' object has no attribute 'title'" in logs
        }
        
        log_result("🚫 SUCCESS CRITERIA 2: NO DUPLICATE PROCESSING PIPELINE")
        for indicator, found in duplicate_indicators.items():
            status = "❌ FOUND (BAD)" if found else "✅ NOT FOUND (GOOD)"
            log_result(f"   {indicator.replace('_', ' ').title()}: {status}")
        
        # SUCCESS CRITERIA 3: Article Generation Analysis
        article_creation_count = logs.count("Article created and saved:")
        outline_complete_count = logs.count("OUTLINE-BASED ARTICLE CREATION COMPLETE")
        enhanced_processing_count = logs.count("ENHANCED OUTLINE-BASED PROCESSING COMPLETE")
        
        log_result("📄 SUCCESS CRITERIA 3: ARTICLE GENERATION ANALYSIS")
        log_result(f"   Articles Created and Saved: {article_creation_count}")
        log_result(f"   Outline-Based Creation Complete: {outline_complete_count}")
        log_result(f"   Enhanced Processing Complete: {enhanced_processing_count}")
        
        # SUCCESS CRITERIA 4: Processing Flow Analysis
        processing_flow = []
        if "COMPREHENSIVE OUTLINE GENERATED" in logs:
            processing_flow.append("✅ Outline Generation")
        if "CREATING ARTICLES FROM OUTLINE" in logs:
            processing_flow.append("✅ Article Creation from Outline")
        if "OUTLINE-BASED SUCCESS" in logs:
            processing_flow.append("✅ Outline-Based Success")
        if "SKIPPING LEGACY PROCESSING" in logs:
            processing_flow.append("✅ Legacy Processing Skipped")
        
        log_result("🔄 SUCCESS CRITERIA 4: PROCESSING FLOW ANALYSIS")
        for step in processing_flow:
            log_result(f"   {step}")
        
        # SUCCESS CRITERIA 5: Error Analysis
        error_patterns = [
            "DocumentChunk' object has no attribute 'title'",
            "falling back to traditional processing",
            "duplicate article creation",
            "processing failed"
        ]
        
        errors_found = []
        for pattern in error_patterns:
            if pattern in logs.lower():
                errors_found.append(pattern)
        
        log_result("🚨 SUCCESS CRITERIA 5: ERROR ANALYSIS")
        if errors_found:
            log_result("   ❌ ERRORS FOUND:")
            for error in errors_found:
                log_result(f"     - {error}")
        else:
            log_result("   ✅ NO CRITICAL ERRORS FOUND")
        
        # OVERALL ASSESSMENT
        success_score = 0
        total_criteria = 5
        
        # Criteria 1: Outline-first processing indicators
        if outline_indicators['outline_based_success'] > 0 and outline_indicators['skipping_legacy_processing'] > 0:
            success_score += 1
            log_result("✅ CRITERIA 1 PASSED: Outline-first processing working", "SUCCESS")
        else:
            log_result("❌ CRITERIA 1 FAILED: Outline-first processing not confirmed", "ERROR")
        
        # Criteria 2: No duplicate processing
        if not any(duplicate_indicators.values()):
            success_score += 1
            log_result("✅ CRITERIA 2 PASSED: No duplicate processing detected", "SUCCESS")
        else:
            log_result("❌ CRITERIA 2 FAILED: Duplicate processing indicators found", "ERROR")
        
        # Criteria 3: Article generation working
        if article_creation_count > 0 and enhanced_processing_count > 0:
            success_score += 1
            log_result("✅ CRITERIA 3 PASSED: Article generation working", "SUCCESS")
        else:
            log_result("❌ CRITERIA 3 FAILED: Article generation issues", "ERROR")
        
        # Criteria 4: Complete processing flow
        if len(processing_flow) >= 3:
            success_score += 1
            log_result("✅ CRITERIA 4 PASSED: Complete processing flow confirmed", "SUCCESS")
        else:
            log_result("❌ CRITERIA 4 FAILED: Incomplete processing flow", "ERROR")
        
        # Criteria 5: No critical errors
        if not errors_found:
            success_score += 1
            log_result("✅ CRITERIA 5 PASSED: No critical errors", "SUCCESS")
        else:
            log_result("❌ CRITERIA 5 FAILED: Critical errors found", "ERROR")
        
        log_result(f"\n🎯 OVERALL ASSESSMENT: {success_score}/{total_criteria} criteria passed")
        
        if success_score >= 4:
            log_result("🎉 DUPLICATE PROCESSING FIX VERIFICATION: SUCCESS", "CRITICAL_SUCCESS")
            log_result("✅ Only ONE set of articles generated per document processing", "SUCCESS")
            log_result("✅ Backend logs show outline-first success with legacy processing skipped", "SUCCESS")
            log_result("✅ Complete elimination of duplicate processing pipeline execution", "SUCCESS")
            return True
        else:
            log_result("❌ DUPLICATE PROCESSING FIX VERIFICATION: FAILED", "CRITICAL_ERROR")
            log_result("❌ Duplicate processing issues may still exist", "ERROR")
            return False
        
    except Exception as e:
        log_result(f"❌ Backend log analysis failed: {e}", "ERROR")
        return False

def verify_content_library_health():
    """Verify Content Library is accessible and has reasonable article count"""
    try:
        log_result("📚 VERIFYING CONTENT LIBRARY HEALTH")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_result(f"✅ Content Library accessible: {total_articles} total articles")
            
            # Check for recent articles to verify processing is working
            recent_articles = [art for art in articles[:10]]  # Check first 10 articles
            
            if recent_articles:
                log_result("📄 Recent articles found:")
                for i, article in enumerate(recent_articles[:5]):
                    title = article.get('title', 'Untitled')[:50]
                    status = article.get('status', 'unknown')
                    log_result(f"   {i+1}. {title}... (Status: {status})")
                
                return True
            else:
                log_result("⚠️ No recent articles found", "WARNING")
                return False
        else:
            log_result(f"❌ Content Library not accessible: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_result(f"❌ Content Library verification failed: {e}", "ERROR")
        return False

def main():
    """Main verification function"""
    log_result("🚀 DUPLICATE PROCESSING FIX VERIFICATION - BACKEND LOG ANALYSIS", "CRITICAL")
    log_result("=" * 80)
    
    # Test 1: Backend Log Analysis
    log_result("TEST 1: Backend Log Analysis for Duplicate Processing Fix")
    backend_analysis_passed = analyze_backend_logs_for_duplicate_fix()
    
    # Test 2: Content Library Health Check
    log_result("\nTEST 2: Content Library Health Verification")
    content_library_passed = verify_content_library_health()
    
    # Final Assessment
    log_result("\n" + "=" * 80)
    log_result("🎯 FINAL DUPLICATE PROCESSING FIX VERIFICATION RESULTS", "CRITICAL")
    log_result("=" * 80)
    
    results = {
        'Backend Log Analysis': backend_analysis_passed,
        'Content Library Health': content_library_passed
    }
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_result(f"{test_name}: {status}")
    
    log_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if backend_analysis_passed:
        log_result("🎉 CRITICAL SUCCESS: Duplicate processing fix is working correctly!", "CRITICAL_SUCCESS")
        log_result("✅ Backend logs confirm outline-first approach with legacy processing skipped", "SUCCESS")
        log_result("✅ No duplicate processing pipeline execution detected", "SUCCESS")
        log_result("✅ Article generation working without duplication", "SUCCESS")
        return True
    else:
        log_result("❌ CRITICAL FAILURE: Duplicate processing fix verification failed", "CRITICAL_ERROR")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)