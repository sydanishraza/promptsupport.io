#!/usr/bin/env python3
"""
SPECIFIC TEST: Google Maps API Tutorial DOCX
Reproduce the empty articles issue reported by the user
"""

import requests
import json
import time
import os
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://smartchunk.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test(message, level="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_google_maps_api_file():
    """Test the Google Maps API Tutorial file specifically"""
    filename = "Google_Map_JavaScript_API_Tutorial.docx"
    file_path = f"/app/{filename}"
    
    log_test("🎯 TESTING GOOGLE MAPS API TUTORIAL FILE", "CRITICAL")
    log_test("This is the user's main concern - generates 2 empty articles")
    
    if not os.path.exists(file_path):
        log_test(f"❌ File not found: {file_path}", "ERROR")
        return
    
    file_size = os.path.getsize(file_path)
    log_test(f"📄 File: {filename}")
    log_test(f"📊 Size: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)")
    
    try:
        # Get current content library state
        baseline_response = requests.get(f"{API_BASE}/content-library", timeout=60)
        if baseline_response.status_code != 200:
            log_test("❌ Cannot get baseline content library", "ERROR")
            return
        
        baseline_data = baseline_response.json()
        baseline_count = baseline_data.get('total', 0)
        baseline_articles = baseline_data.get('articles', [])
        
        log_test(f"📚 Baseline: {baseline_count} articles in Content Library")
        
        # Upload the Google Maps API file
        log_test("📤 Uploading Google Maps API Tutorial...")
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
            
            if response.status_code != 200:
                log_test(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                log_test(f"Response: {response.text[:500]}")
                return
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if not job_id:
                log_test("❌ No job_id received", "ERROR")
                return
            
            log_test(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing with detailed logging
        log_test("⏳ Monitoring processing...")
        processing_start = time.time()
        max_wait = 300  # 5 minutes
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait:
                log_test(f"❌ Processing timeout after {elapsed:.1f}s", "ERROR")
                return
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test(f"📊 Status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        articles_generated = status_data.get('articles_generated', 0)
                        chunks_created = status_data.get('chunks_created', 0)
                        
                        log_test(f"✅ Processing completed in {processing_time:.1f}s")
                        log_test(f"📄 Articles generated: {articles_generated}")
                        log_test(f"📚 Chunks created: {chunks_created}")
                        
                        break
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test(f"❌ Processing failed: {error_msg}", "ERROR")
                        return
                    
                    time.sleep(5)
                else:
                    log_test(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(3)
                    
            except Exception as e:
                log_test(f"⚠️ Status check error: {e}")
                time.sleep(3)
        
        # Wait for database consistency
        log_test("⏳ Waiting for database consistency...")
        time.sleep(5)
        
        # Get updated content library
        final_response = requests.get(f"{API_BASE}/content-library", timeout=60)
        if final_response.status_code != 200:
            log_test("❌ Cannot get final content library", "ERROR")
            return
        
        final_data = final_response.json()
        final_count = final_data.get('total', 0)
        final_articles = final_data.get('articles', [])
        
        new_articles_count = final_count - baseline_count
        log_test(f"📚 Final: {final_count} articles (+{new_articles_count} new)")
        
        # Find the new articles (most recent ones)
        sorted_articles = sorted(final_articles, key=lambda x: x.get('created_at', ''), reverse=True)
        new_articles = sorted_articles[:articles_generated] if articles_generated > 0 else []
        
        log_test(f"🔍 ANALYZING {len(new_articles)} NEW ARTICLES:")
        
        empty_articles = []
        populated_articles = []
        html_issue_articles = []
        
        for i, article in enumerate(new_articles):
            article_id = article.get('id', f'article-{i}')
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            status = article.get('status', 'unknown')
            article_type = article.get('article_type', 'unknown')
            
            content_length = len(content.strip())
            
            log_test(f"   📄 Article {i+1}: '{title}'")
            log_test(f"      ID: {article_id}")
            log_test(f"      Type: {article_type}")
            log_test(f"      Status: {status}")
            log_test(f"      Content Length: {content_length} chars")
            
            if content_length == 0:
                empty_articles.append(article)
                log_test(f"      🚨 EMPTY ARTICLE DETECTED", "CRITICAL")
            elif '```html' in content or '<!DOCTYPE html>' in content:
                html_issue_articles.append(article)
                log_test(f"      ⚠️ HTML PLACEHOLDER ISSUE", "WARNING")
                log_test(f"      Content preview: {content[:200]}...")
            elif content_length < 500:
                log_test(f"      ⚠️ VERY SHORT CONTENT", "WARNING")
                log_test(f"      Content preview: {content[:200]}...")
            else:
                populated_articles.append(article)
                log_test(f"      ✅ PROPERLY POPULATED", "SUCCESS")
                log_test(f"      Content preview: {content[:200]}...")
        
        # Final analysis
        log_test(f"\n🎯 GOOGLE MAPS API FILE ANALYSIS RESULTS:", "CRITICAL")
        log_test(f"   📄 File processed: {filename} ({file_size/1024/1024:.1f}MB)")
        log_test(f"   ⏱️ Processing time: {processing_time:.1f} seconds")
        log_test(f"   📊 Articles generated: {articles_generated}")
        log_test(f"   🚨 Empty articles: {len(empty_articles)}")
        log_test(f"   ⚠️ HTML issue articles: {len(html_issue_articles)}")
        log_test(f"   ✅ Populated articles: {len(populated_articles)}")
        
        if empty_articles:
            log_test(f"\n🚨 CRITICAL BUG CONFIRMED:", "CRITICAL")
            log_test(f"   Google Maps API Tutorial generates {len(empty_articles)} empty articles")
            
            for article in empty_articles:
                log_test(f"   - Empty article: '{article['title']}' (ID: {article['id']})")
        
        if html_issue_articles:
            log_test(f"\n⚠️ HTML CLEANING ISSUES FOUND:")
            for article in html_issue_articles:
                log_test(f"   - HTML issue: '{article['title']}' (ID: {article['id']})")
        
        # Root cause investigation
        log_test(f"\n🔍 ROOT CAUSE INVESTIGATION:")
        
        # Check if this was unified or split processing
        if len(new_articles) == 1:
            log_test(f"   📋 Processing type: UNIFIED (single article)")
        else:
            log_test(f"   📋 Processing type: SPLIT ({len(new_articles)} articles)")
        
        # Check article types
        article_types = [a.get('article_type', 'unknown') for a in new_articles]
        log_test(f"   📊 Article types: {', '.join(set(article_types))}")
        
        # Check for FAQ articles specifically
        faq_articles = [a for a in new_articles if 'faq' in a.get('article_type', '').lower()]
        if faq_articles:
            log_test(f"   ❓ FAQ articles found: {len(faq_articles)}")
            for faq in faq_articles:
                faq_content_length = len(faq.get('content', '').strip())
                log_test(f"      FAQ: '{faq['title']}' ({faq_content_length} chars)")
        
        return {
            'filename': filename,
            'file_size_mb': file_size / 1024 / 1024,
            'processing_time': processing_time,
            'articles_generated': articles_generated,
            'empty_articles': len(empty_articles),
            'html_issue_articles': len(html_issue_articles),
            'populated_articles': len(populated_articles),
            'processing_type': 'unified' if len(new_articles) == 1 else 'split'
        }
        
    except Exception as e:
        log_test(f"❌ Test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Google Maps API Tutorial Empty Articles Test")
    print("=" * 50)
    
    result = test_google_maps_api_file()
    
    if result and result['empty_articles'] > 0:
        print(f"\n❌ CRITICAL BUG CONFIRMED: {result['empty_articles']} empty articles found")
        exit(1)
    elif result:
        print(f"\n✅ NO EMPTY ARTICLES FOUND in Google Maps API file")
        exit(0)
    else:
        print(f"\n❌ TEST FAILED")
        exit(2)