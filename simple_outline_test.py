#!/usr/bin/env python3
"""
SIMPLE OUTLINE-FIRST APPROACH TEST
Quick test to verify outline-first implementation is working
"""

import requests
import json
import time
import os
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-formatter.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_backend_connectivity():
    """Test basic backend connectivity"""
    try:
        log_test_result("Testing backend connectivity...")
        response = requests.get(f"{API_BASE}/health", timeout=60)
        
        if response.status_code == 200:
            log_test_result("✅ Backend connectivity PASSED", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ Backend connectivity FAILED: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend connectivity FAILED: {e}", "ERROR")
        return False

def check_content_library_current_state():
    """Check current state of Content Library"""
    try:
        log_test_result("🔍 Checking current Content Library state...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_test_result(f"📚 Content Library Current State:")
            log_test_result(f"   Total Articles: {total_articles}")
            log_test_result(f"   Articles Retrieved: {len(articles)}")
            
            # Look for Customer Guide articles
            customer_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                source = article.get('source_document', '').lower()
                if ('customer' in title or 'customer' in source or 
                    'summary' in title or 'guide' in title):
                    customer_articles.append(article)
            
            log_test_result(f"📄 Customer Guide Related Articles: {len(customer_articles)}")
            
            # Show recent articles
            if articles:
                log_test_result("📋 Recent Articles (first 5):")
                for i, article in enumerate(articles[:5]):
                    title = article.get('title', 'Untitled')
                    status = article.get('status', 'unknown')
                    created = article.get('created_at', 'unknown')
                    log_test_result(f"   {i+1}. {title[:50]}... (Status: {status})")
            
            return {
                'total_articles': total_articles,
                'customer_articles': len(customer_articles),
                'success': True
            }
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return {'success': False}
            
    except Exception as e:
        log_test_result(f"❌ Content Library check failed: {e}", "ERROR")
        return {'success': False}

def check_backend_logs_for_outline_evidence():
    """Check backend logs for evidence of outline-first approach"""
    try:
        log_test_result("🔍 Checking backend logs for outline-first evidence...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '300', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for outline-first specific messages
                outline_indicators = {
                    'comprehensive_outline_generated': "COMPREHENSIVE OUTLINE GENERATED" in logs,
                    'creating_articles_from_outline': "CREATING ARTICLES FROM OUTLINE" in logs,
                    'outline_based_success': "OUTLINE-BASED SUCCESS" in logs,
                    'ultra_large_detected': "ULTRA-LARGE DOCUMENT DETECTED" in logs,
                    'dynamic_limit_used': "USING DYNAMIC LIMIT" in logs,
                    'conservative_merging': "conservative merging" in logs.lower()
                }
                
                log_test_result("📋 OUTLINE-FIRST EVIDENCE IN LOGS:")
                evidence_found = False
                for indicator, found in outline_indicators.items():
                    status = "✅ FOUND" if found else "❌ NOT FOUND"
                    log_test_result(f"   {indicator.replace('_', ' ').title()}: {status}")
                    if found:
                        evidence_found = True
                
                # Extract specific numbers if found
                if outline_indicators['comprehensive_outline_generated']:
                    import re
                    outline_matches = re.findall(r'COMPREHENSIVE OUTLINE GENERATED: (\d+) articles planned', logs)
                    if outline_matches:
                        for match in outline_matches[-3:]:  # Show last 3 matches
                            log_test_result(f"   📊 Found: {match} articles planned from outline")
                
                if outline_indicators['outline_based_success']:
                    success_matches = re.findall(r'OUTLINE-BASED SUCCESS: Created (\d+) comprehensive articles', logs)
                    if success_matches:
                        for match in success_matches[-3:]:  # Show last 3 matches
                            log_test_result(f"   📊 Found: {match} articles created from outline")
                
                if outline_indicators['dynamic_limit_used']:
                    dynamic_matches = re.findall(r'USING DYNAMIC LIMIT: (\d+) articles', logs)
                    if dynamic_matches:
                        for match in dynamic_matches[-3:]:  # Show last 3 matches
                            log_test_result(f"   📊 Found: Dynamic limit of {match} articles used")
                
                if evidence_found:
                    log_test_result("✅ OUTLINE-FIRST EVIDENCE FOUND in backend logs", "SUCCESS")
                else:
                    log_test_result("⚠️ NO OUTLINE-FIRST EVIDENCE found in recent logs", "WARNING")
                
                return outline_indicators
            else:
                log_test_result("⚠️ Could not access backend logs")
                return {}
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return {}
            
    except Exception as e:
        log_test_result(f"❌ Backend log verification failed: {e}", "ERROR")
        return {}

def run_simple_outline_test():
    """Run simple test to check outline-first approach status"""
    log_test_result("🚀 STARTING SIMPLE OUTLINE-FIRST VERIFICATION", "CRITICAL")
    log_test_result("=" * 60)
    
    # Test 1: Backend Connectivity
    log_test_result("TEST 1: Backend Connectivity")
    if not test_backend_connectivity():
        log_test_result("❌ Cannot proceed without backend connectivity", "CRITICAL_ERROR")
        return False
    
    # Test 2: Content Library State
    log_test_result("\nTEST 2: Content Library Current State")
    library_result = check_content_library_current_state()
    
    # Test 3: Backend Logs Analysis
    log_test_result("\nTEST 3: Backend Logs Analysis")
    log_evidence = check_backend_logs_for_outline_evidence()
    
    # Summary
    log_test_result("\n" + "=" * 60)
    log_test_result("🎯 SIMPLE OUTLINE-FIRST VERIFICATION SUMMARY", "CRITICAL")
    log_test_result("=" * 60)
    
    # Evaluate results
    has_evidence = any(log_evidence.values()) if log_evidence else False
    has_comprehensive_articles = library_result.get('customer_articles', 0) > 6 if library_result.get('success') else False
    
    log_test_result("📊 VERIFICATION RESULTS:")
    log_test_result(f"   Backend Connectivity: ✅ WORKING")
    log_test_result(f"   Outline-First Evidence in Logs: {'✅ FOUND' if has_evidence else '❌ NOT FOUND'}")
    log_test_result(f"   Comprehensive Articles (>6): {'✅ YES' if has_comprehensive_articles else '❌ NO'}")
    log_test_result(f"   Total Articles in Library: {library_result.get('total_articles', 'Unknown')}")
    log_test_result(f"   Customer Guide Articles: {library_result.get('customer_articles', 'Unknown')}")
    
    if has_evidence and has_comprehensive_articles:
        log_test_result("🎉 OUTLINE-FIRST APPROACH: WORKING CORRECTLY", "CRITICAL_SUCCESS")
        return True
    elif has_evidence:
        log_test_result("⚠️ OUTLINE-FIRST APPROACH: EVIDENCE FOUND BUT NEEDS MORE TESTING", "WARNING")
        return True
    elif has_comprehensive_articles:
        log_test_result("⚠️ COMPREHENSIVE ARTICLES FOUND BUT NO LOG EVIDENCE", "WARNING")
        return True
    else:
        log_test_result("❌ OUTLINE-FIRST APPROACH: NO CLEAR EVIDENCE", "ERROR")
        return False

if __name__ == "__main__":
    print("Simple Outline-First Approach Verification")
    print("=" * 50)
    
    success = run_simple_outline_test()
    
    if success:
        print("\n✅ VERIFICATION COMPLETED - Outline-first approach shows positive indicators")
    else:
        print("\n❌ VERIFICATION COMPLETED - Outline-first approach needs investigation")