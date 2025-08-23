#!/usr/bin/env python3
"""
TARGETED EMPTY ARTICLES INVESTIGATION
Focus on the 5 specific files mentioned in the review request
"""

import requests
import json
import time
import os
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test(message, level="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_specific_file(filename, expected_description):
    """Test a specific file for empty articles"""
    log_test(f"🎯 TESTING: {filename}", "CRITICAL")
    log_test(f"📋 Expected: {expected_description}")
    
    file_path = f"/app/{filename}"
    if not os.path.exists(file_path):
        log_test(f"❌ File not found: {file_path}", "ERROR")
        return None
    
    file_size = os.path.getsize(file_path)
    log_test(f"📄 File size: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)")
    
    try:
        # Get baseline
        baseline_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        baseline_count = 0
        if baseline_response.status_code == 200:
            baseline_count = baseline_response.json().get('total', 0)
        
        log_test(f"📚 Baseline articles: {baseline_count}")
        
        # Upload file
        content_type = 'application/pdf' if filename.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, content_type)}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
            
            if response.status_code != 200:
                log_test(f"❌ Upload failed: {response.status_code}", "ERROR")
                return None
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            log_test(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing
        processing_start = time.time()
        max_wait = 300  # 5 minutes
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait:
                log_test(f"❌ Timeout after {elapsed:.1f}s", "ERROR")
                return None
            
            status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                if status == 'completed':
                    processing_time = time.time() - processing_start
                    articles_generated = status_data.get('articles_generated', 0)
                    
                    log_test(f"✅ Processing completed in {processing_time:.1f}s")
                    log_test(f"📄 Articles generated: {articles_generated}")
                    
                    # Get new articles and analyze
                    time.sleep(3)  # Wait for DB consistency
                    
                    final_response = requests.get(f"{API_BASE}/content-library", timeout=30)
                    if final_response.status_code == 200:
                        final_data = final_response.json()
                        final_count = final_data.get('total', 0)
                        articles = final_data.get('articles', [])
                        
                        new_articles_count = final_count - baseline_count
                        log_test(f"📚 New articles in library: {new_articles_count}")
                        
                        # Analyze recent articles (assume they are the new ones)
                        recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:articles_generated]
                        
                        empty_count = 0
                        populated_count = 0
                        html_issue_count = 0
                        
                        log_test(f"🔍 ANALYZING {len(recent_articles)} RECENT ARTICLES:")
                        
                        for i, article in enumerate(recent_articles):
                            title = article.get('title', 'Untitled')
                            content = article.get('content', '')
                            content_length = len(content.strip())
                            
                            if content_length == 0:
                                empty_count += 1
                                log_test(f"   ❌ EMPTY: '{title}' (0 chars)")
                            elif '```html' in content or '<!DOCTYPE html>' in content:
                                html_issue_count += 1
                                log_test(f"   ⚠️ HTML ISSUE: '{title}' ({content_length} chars)")
                            else:
                                populated_count += 1
                                log_test(f"   ✅ POPULATED: '{title}' ({content_length} chars)")
                        
                        # Summary for this file
                        log_test(f"📊 RESULTS FOR {filename}:")
                        log_test(f"   Empty articles: {empty_count}")
                        log_test(f"   HTML issues: {html_issue_count}")
                        log_test(f"   Populated articles: {populated_count}")
                        
                        if empty_count > 0:
                            log_test(f"🚨 CRITICAL: {empty_count} EMPTY ARTICLES FOUND", "CRITICAL")
                        
                        return {
                            'filename': filename,
                            'processing_time': processing_time,
                            'articles_generated': articles_generated,
                            'empty_articles': empty_count,
                            'populated_articles': populated_count,
                            'html_issues': html_issue_count
                        }
                    
                elif status == 'failed':
                    log_test(f"❌ Processing failed: {status_data.get('error', 'Unknown')}", "ERROR")
                    return None
                
                time.sleep(5)
            else:
                time.sleep(3)
    
    except Exception as e:
        log_test(f"❌ Test failed: {e}", "ERROR")
        return None

def run_targeted_investigation():
    """Run targeted investigation on the 5 specific files"""
    log_test("🎯 TARGETED EMPTY ARTICLES INVESTIGATION", "CRITICAL")
    log_test("=" * 60)
    
    # Test backend health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=30)
        if response.status_code != 200:
            log_test("❌ Backend health check failed", "CRITICAL")
            return
        log_test("✅ Backend health check passed")
    except Exception as e:
        log_test(f"❌ Backend health check failed: {e}", "CRITICAL")
        return
    
    # Target files from the review request
    target_files = [
        ("Google_Map_JavaScript_API_Tutorial.docx", "User's main concern - generates 2 empty articles"),
        ("customer_guide.docx", "Customer Summary Screen User Guide 1.3.docx (4.6MB, 85 pages)"),
        ("Promotions_Configuration_and_Management-v5-20220201_173002.docx", "Promotions Configuration and Management-v5.docx"),
        ("Whisk_Studio_Integration_Guide.pdf", "Whisk Studio Integration Guide.pdf"),
    ]
    
    # Also check for the filtering recipes file
    filtering_files = [f for f in os.listdir("/app") if "filtering" in f.lower() and "recipe" in f.lower()]
    if filtering_files:
        target_files.append((filtering_files[0], "Filtering Recipes using Custom Labels - Whisk Docs.pdf"))
    
    results = []
    
    for i, (filename, description) in enumerate(target_files, 1):
        log_test(f"\n{'='*50}")
        log_test(f"TEST {i}/{len(target_files)}: {filename}")
        log_test(f"{'='*50}")
        
        result = test_specific_file(filename, description)
        if result:
            results.append(result)
        
        # Wait between tests
        if i < len(target_files):
            log_test("⏳ Waiting 15 seconds before next test...")
            time.sleep(15)
    
    # Final analysis
    log_test(f"\n{'='*60}")
    log_test("🎯 FINAL ANALYSIS", "CRITICAL")
    log_test(f"{'='*60}")
    
    total_empty = sum(r['empty_articles'] for r in results)
    total_populated = sum(r['populated_articles'] for r in results)
    total_html_issues = sum(r['html_issues'] for r in results)
    
    log_test(f"📊 OVERALL RESULTS:")
    log_test(f"   Files tested: {len(results)}")
    log_test(f"   Total empty articles: {total_empty}")
    log_test(f"   Total populated articles: {total_populated}")
    log_test(f"   Total HTML issues: {total_html_issues}")
    
    for result in results:
        log_test(f"\n📄 {result['filename']}:")
        log_test(f"   Processing time: {result['processing_time']:.1f}s")
        log_test(f"   Articles generated: {result['articles_generated']}")
        log_test(f"   Empty: {result['empty_articles']}")
        log_test(f"   Populated: {result['populated_articles']}")
        log_test(f"   HTML issues: {result['html_issues']}")
    
    if total_empty > 0:
        log_test(f"🚨 CRITICAL BUG CONFIRMED: {total_empty} empty articles found across {len(results)} files", "CRITICAL")
    else:
        log_test("✅ NO EMPTY ARTICLES FOUND in targeted test files", "SUCCESS")
    
    return results

if __name__ == "__main__":
    results = run_targeted_investigation()