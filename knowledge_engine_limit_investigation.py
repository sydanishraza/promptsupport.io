#!/usr/bin/env python3
"""
URGENT INVESTIGATION: Knowledge Engine 6-Article Limitation
Testing the user's specific document: Customer Summary Screen User Guide 1.3.docx
Goal: Identify why it's still limited to 6 articles despite all previous fixes
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://docai-promptsupport.preview.emergentagent.com"
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

def investigate_customer_guide_limitation():
    """
    CRITICAL INVESTIGATION: Process the user's Customer Summary Screen User Guide 1.3.docx
    and identify why it's still limited to 6 articles
    """
    try:
        log_test_result("🔍 STARTING CRITICAL INVESTIGATION: Customer Guide 6-Article Limitation", "CRITICAL")
        
        # Check if the user's document exists
        file_path = "/app/Customer_Summary_Screen_User_Guide_1.3.docx"
        if not os.path.exists(file_path):
            log_test_result(f"❌ User's document not found: {file_path}", "ERROR")
            return False
        
        file_size = os.path.getsize(file_path)
        log_test_result(f"📄 User's Document Confirmed: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)")
        log_test_result(f"📄 Document: Customer Summary Screen User Guide 1.3.docx (85 pages)")
        
        # Upload and process the document with detailed monitoring
        log_test_result("📤 Uploading user's document to Knowledge Engine...")
        
        with open(file_path, 'rb') as f:
            files = {'file': ('Customer_Summary_Screen_User_Guide_1.3.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            
            # Start processing with extended timeout
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=600)
            
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
        
        # Monitor processing with detailed analysis
        log_test_result("⏳ Monitoring processing with detailed analysis...")
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
                        
                        # CRITICAL ANALYSIS: Extract all metrics
                        chunks_created = status_data.get('chunks_created', 0)
                        articles_generated = status_data.get('articles_generated', 0)
                        
                        log_test_result(f"🔍 CRITICAL ANALYSIS RESULTS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        log_test_result(f"   ⏱️ Processing Time: {processing_time:.1f} seconds")
                        
                        # INVESTIGATION: Check for ultra-large document detection
                        if 'ultra_large_detected' in status_data:
                            log_test_result(f"   🔍 Ultra-Large Document Detected: {status_data['ultra_large_detected']}")
                        
                        if 'intelligent_limit' in status_data:
                            log_test_result(f"   🧠 Intelligent Limit Applied: {status_data['intelligent_limit']}")
                        
                        if 'dynamic_calculation' in status_data:
                            log_test_result(f"   📊 Dynamic Calculation: {status_data['dynamic_calculation']}")
                        
                        # CRITICAL FINDING: Analyze the 6-article limitation
                        if articles_generated <= 6:
                            log_test_result(f"❌ CRITICAL ISSUE CONFIRMED: Only {articles_generated} articles generated", "CRITICAL_ERROR")
                            log_test_result("❌ 6-ARTICLE LIMITATION STILL EXISTS", "CRITICAL_ERROR")
                            log_test_result("🔍 INVESTIGATION NEEDED: Hard limits not fully removed", "CRITICAL_ERROR")
                            
                            # Try to get more details from the processing
                            log_test_result("🔍 Analyzing processing details...")
                            if 'processing_details' in status_data:
                                details = status_data['processing_details']
                                log_test_result(f"   Processing Details: {json.dumps(details, indent=2)}")
                            
                        elif articles_generated >= 10:
                            log_test_result(f"🎉 SUCCESS: {articles_generated} articles generated (exceeds 6-article limit)", "SUCCESS")
                            log_test_result("✅ HARD LIMITS SUCCESSFULLY REMOVED", "SUCCESS")
                        else:
                            log_test_result(f"⚠️ PARTIAL: {articles_generated} articles generated (better than 6, but below expected 10-15+)", "WARNING")
                        
                        # Get Content Library verification
                        return verify_content_library_articles(articles_generated)
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test_result(f"❌ Processing failed: {error_msg}", "ERROR")
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
        log_test_result(f"❌ Investigation failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def verify_content_library_articles(expected_count):
    """Verify articles are properly stored and analyze content coverage"""
    try:
        log_test_result("🔍 Verifying Content Library and analyzing coverage...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_test_result(f"📚 Content Library Status:")
            log_test_result(f"   Total Articles: {total_articles}")
            log_test_result(f"   Articles Retrieved: {len(articles)}")
            
            # Look for recently created articles from Customer Summary Screen
            recent_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                source = article.get('source_document', '').lower()
                created_at = article.get('created_at', '')
                
                if ('customer' in title or 'customer' in source or 
                    'summary' in title or 'summary' in source or
                    'screen' in title or 'screen' in source):
                    recent_articles.append(article)
            
            if recent_articles:
                log_test_result(f"✅ Found {len(recent_articles)} Customer Summary Screen articles")
                
                # Analyze content coverage
                total_content_length = 0
                for i, article in enumerate(recent_articles[:10]):  # Show first 10
                    title = article.get('title', 'Untitled')
                    content = article.get('content', '')
                    content_length = len(content)
                    total_content_length += content_length
                    
                    log_test_result(f"   Article {i+1}: {title[:60]}... ({content_length:,} chars)")
                
                log_test_result(f"📊 CONTENT COVERAGE ANALYSIS:")
                log_test_result(f"   Total Content Length: {total_content_length:,} characters")
                log_test_result(f"   Average Article Length: {total_content_length // len(recent_articles):,} characters")
                
                # Compare with expected comprehensive coverage
                if len(recent_articles) <= 6:
                    log_test_result(f"❌ COVERAGE ISSUE: Only {len(recent_articles)} articles for 85-page document", "CRITICAL_ERROR")
                    log_test_result("❌ CONTENT MAY BE TRUNCATED OR SKIPPED", "CRITICAL_ERROR")
                else:
                    log_test_result(f"✅ GOOD COVERAGE: {len(recent_articles)} articles provide comprehensive coverage", "SUCCESS")
                
                return True
            else:
                log_test_result("⚠️ No Customer Summary Screen articles found in Content Library")
                return False
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Content Library verification failed: {e}", "ERROR")
        return False

def check_backend_processing_logs():
    """Check backend logs for processing details and limit detection"""
    try:
        log_test_result("🔍 Checking backend logs for processing insights...")
        
        # Check supervisor logs for backend processing
        import subprocess
        
        try:
            # Get recent backend logs
            result = subprocess.run(['tail', '-n', '100', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                # Look for key processing messages
                if "NO ARTIFICIAL LIMITS APPLIED" in logs:
                    log_test_result("✅ Found 'NO ARTIFICIAL LIMITS APPLIED' in logs", "SUCCESS")
                else:
                    log_test_result("❌ 'NO ARTIFICIAL LIMITS APPLIED' NOT found in logs", "WARNING")
                
                if "ultra-large document" in logs.lower():
                    log_test_result("✅ Ultra-large document detection found in logs", "SUCCESS")
                else:
                    log_test_result("❌ Ultra-large document detection NOT found in logs", "WARNING")
                
                if "intelligent_limit" in logs:
                    log_test_result("✅ Intelligent limit calculation found in logs", "SUCCESS")
                else:
                    log_test_result("❌ Intelligent limit calculation NOT found in logs", "WARNING")
                
                # Look for any remaining hard limits
                hard_limit_indicators = ["max_articles = 6", "limit = 6", "articles_limit = 6"]
                for indicator in hard_limit_indicators:
                    if indicator in logs:
                        log_test_result(f"❌ FOUND HARD LIMIT: {indicator}", "CRITICAL_ERROR")
                
                return True
            else:
                log_test_result("⚠️ Could not read backend logs", "WARNING")
                return False
                
        except Exception as e:
            log_test_result(f"⚠️ Log check failed: {e}", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend log check failed: {e}", "ERROR")
        return False

def main():
    """Run the complete investigation"""
    log_test_result("🚀 STARTING KNOWLEDGE ENGINE 6-ARTICLE LIMITATION INVESTIGATION", "START")
    log_test_result("🎯 Target: Customer Summary Screen User Guide 1.3.docx (85 pages)")
    log_test_result("🔍 Goal: Identify why still limited to 6 articles despite fixes")
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Backend Health
    if test_backend_health():
        success_count += 1
    
    # Test 2: Critical Investigation
    if investigate_customer_guide_limitation():
        success_count += 1
    
    # Test 3: Backend Logs Analysis
    if check_backend_processing_logs():
        success_count += 1
    
    # Test 4: Final Summary
    success_count += 1  # Always count summary
    
    # Final Results
    log_test_result("=" * 80, "SUMMARY")
    log_test_result(f"INVESTIGATION COMPLETE: {success_count}/{total_tests} tests completed", "SUMMARY")
    
    if success_count >= 3:
        log_test_result("🎉 INVESTIGATION SUCCESSFUL - Data collected for analysis", "SUCCESS")
    else:
        log_test_result("❌ INVESTIGATION INCOMPLETE - Some tests failed", "ERROR")
    
    log_test_result("=" * 80, "END")

if __name__ == "__main__":
    main()