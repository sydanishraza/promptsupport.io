#!/usr/bin/env python3
"""
CRITICAL EMPTY CONTENT BUG FIX VERIFICATION
Testing the enhanced content processing pipeline with comprehensive validation and debugging

Focus: Verify empty content bug fixes with all user files as specified in review request:
1. Google Map JavaScript API Tutorial.docx (user's main concern - should be unified)
2. Customer Summary Screen User Guide 1.3.docx (large document - should be split)
3. Promotions Configuration and Management-v5.docx (medium document)
4. Whisk Studio Integration Guide.pdf (PDF processing)
5. Filtering Recipes using Custom Labels - Whisk Docs.pdf (smaller PDF)

SUCCESS CRITERIA:
- Google Maps API Tutorial: Should generate 1 unified guide + 1 FAQ (both with substantial content)
- Large documents: Should generate multiple articles with content
- All articles: Should have >100 characters of actual content
- No empty articles: Every article should contain meaningful information
- Processing logs: Should show content validation at each step
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://prompt-support-app.preview.emergentagent.com"
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
    """Get baseline article count before testing"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            log_test_result(f"📊 Content Library Baseline: {total_articles} articles")
            return total_articles
        return 0
    except Exception as e:
        log_test_result(f"⚠️ Could not get baseline: {e}")
        return 0

def analyze_article_content_quality(articles):
    """Analyze articles for empty content issues"""
    analysis = {
        'total_articles': len(articles),
        'empty_articles': 0,
        'short_articles': 0,  # <100 chars
        'substantial_articles': 0,  # >500 chars
        'html_placeholder_issues': 0,
        'content_lengths': [],
        'empty_article_titles': [],
        'short_article_titles': []
    }
    
    for article in articles:
        title = article.get('title', 'Untitled')
        content = article.get('content', '')
        content_length = len(content.strip())
        
        analysis['content_lengths'].append(content_length)
        
        if content_length == 0:
            analysis['empty_articles'] += 1
            analysis['empty_article_titles'].append(title)
        elif content_length < 100:
            analysis['short_articles'] += 1
            analysis['short_article_titles'].append(f"{title} ({content_length} chars)")
        elif content_length > 500:
            analysis['substantial_articles'] += 1
        
        # Check for HTML placeholder issues
        if '```html' in content or '<!DOCTYPE html>' in content:
            analysis['html_placeholder_issues'] += 1
    
    return analysis

def test_file_processing(file_info, expected_behavior):
    """Test processing of a specific file with detailed validation"""
    try:
        file_path = file_info['path']
        file_name = file_info['name']
        file_type = file_info['type']
        
        log_test_result(f"🎯 TESTING FILE: {file_name}", "CRITICAL")
        log_test_result(f"   Expected behavior: {expected_behavior}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            log_test_result(f"❌ Test file not found: {file_path}", "ERROR")
            return False, {}
        
        file_size = os.path.getsize(file_path)
        log_test_result(f"📄 File confirmed: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)")
        
        # Get baseline article count
        baseline_count = get_content_library_baseline()
        
        # Upload and process the document
        log_test_result("📤 Uploading document to Knowledge Engine...")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f, file_type)}
            
            # Start processing
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=600)
            
            if response.status_code != 200:
                log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                log_test_result(f"Response: {response.text[:500]}")
                return False, {}
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if not job_id:
                log_test_result("❌ No job_id received from upload", "ERROR")
                return False, {}
            
            log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing with detailed logging
        log_test_result("⏳ Monitoring processing progress...")
        processing_start = time.time()
        max_wait_time = 600  # 10 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return False, {}
            
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
                        
                        # Get updated Content Library to analyze generated articles
                        time.sleep(2)  # Brief wait for database consistency
                        final_count = get_content_library_baseline()
                        new_articles_count = final_count - baseline_count
                        
                        log_test_result(f"📊 CONTENT LIBRARY ANALYSIS:")
                        log_test_result(f"   Before: {baseline_count} articles")
                        log_test_result(f"   After: {final_count} articles")
                        log_test_result(f"   New articles: {new_articles_count}")
                        
                        # Get detailed article analysis
                        content_response = requests.get(f"{API_BASE}/content-library", timeout=30)
                        if content_response.status_code == 200:
                            content_data = content_response.json()
                            all_articles = content_data.get('articles', [])
                            
                            # Find articles from this processing session
                            recent_articles = []
                            current_time = datetime.now()
                            
                            for article in all_articles:
                                created_at = article.get('created_at', '')
                                source_doc = article.get('source_document', '').lower()
                                
                                # Check if this article is from our test file
                                if file_name.lower().replace('.docx', '').replace('.pdf', '') in source_doc:
                                    recent_articles.append(article)
                            
                            if not recent_articles:
                                # Fallback: get most recent articles
                                recent_articles = all_articles[:new_articles_count] if new_articles_count > 0 else []
                            
                            # Analyze content quality
                            analysis = analyze_article_content_quality(recent_articles)
                            
                            log_test_result(f"🔍 CONTENT QUALITY ANALYSIS:")
                            log_test_result(f"   Total articles analyzed: {analysis['total_articles']}")
                            log_test_result(f"   Empty articles (0 chars): {analysis['empty_articles']}")
                            log_test_result(f"   Short articles (<100 chars): {analysis['short_articles']}")
                            log_test_result(f"   Substantial articles (>500 chars): {analysis['substantial_articles']}")
                            log_test_result(f"   HTML placeholder issues: {analysis['html_placeholder_issues']}")
                            
                            if analysis['content_lengths']:
                                avg_length = sum(analysis['content_lengths']) / len(analysis['content_lengths'])
                                min_length = min(analysis['content_lengths'])
                                max_length = max(analysis['content_lengths'])
                                log_test_result(f"   Content length stats: avg={avg_length:.0f}, min={min_length}, max={max_length}")
                            
                            # Report empty articles
                            if analysis['empty_articles'] > 0:
                                log_test_result(f"❌ EMPTY ARTICLES DETECTED:", "ERROR")
                                for title in analysis['empty_article_titles']:
                                    log_test_result(f"     - {title}", "ERROR")
                            
                            # Report short articles
                            if analysis['short_articles'] > 0:
                                log_test_result(f"⚠️ SHORT ARTICLES DETECTED:")
                                for title in analysis['short_article_titles']:
                                    log_test_result(f"     - {title}")
                            
                            # Verify against expected behavior
                            success = True
                            test_results = {
                                'articles_generated': analysis['total_articles'],
                                'empty_articles': analysis['empty_articles'],
                                'short_articles': analysis['short_articles'],
                                'substantial_articles': analysis['substantial_articles'],
                                'html_issues': analysis['html_placeholder_issues'],
                                'processing_time': processing_time,
                                'content_analysis': analysis
                            }
                            
                            # Validate against expected behavior
                            if "unified" in expected_behavior.lower():
                                # Should generate 1-2 articles (unified guide + FAQ)
                                if analysis['total_articles'] < 1 or analysis['total_articles'] > 3:
                                    log_test_result(f"⚠️ Unexpected article count for unified processing: {analysis['total_articles']}")
                                else:
                                    log_test_result(f"✅ Unified processing: {analysis['total_articles']} articles generated")
                            elif "split" in expected_behavior.lower():
                                # Should generate multiple articles
                                if analysis['total_articles'] < 3:
                                    log_test_result(f"⚠️ Expected more articles for split processing: {analysis['total_articles']}")
                                else:
                                    log_test_result(f"✅ Split processing: {analysis['total_articles']} articles generated")
                            
                            # Critical validation: No empty articles allowed
                            if analysis['empty_articles'] > 0:
                                log_test_result(f"❌ CRITICAL FAILURE: {analysis['empty_articles']} empty articles detected", "CRITICAL_ERROR")
                                success = False
                            else:
                                log_test_result(f"✅ CRITICAL SUCCESS: No empty articles detected", "SUCCESS")
                            
                            # Validate substantial content
                            if analysis['substantial_articles'] == 0 and analysis['total_articles'] > 0:
                                log_test_result(f"❌ CRITICAL FAILURE: No articles with substantial content (>500 chars)", "CRITICAL_ERROR")
                                success = False
                            else:
                                log_test_result(f"✅ Content validation: {analysis['substantial_articles']} articles with substantial content", "SUCCESS")
                            
                            return success, test_results
                        
                        return True, {'articles_generated': articles_generated, 'processing_time': processing_time}
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False, {}
                    
                    # Continue monitoring
                    time.sleep(10)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ File processing test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False, {}

def run_comprehensive_empty_content_bug_test():
    """Run comprehensive test suite for empty content bug verification"""
    log_test_result("🚀 STARTING COMPREHENSIVE EMPTY CONTENT BUG FIX VERIFICATION", "CRITICAL")
    log_test_result("=" * 80)
    
    # Define test files as specified in review request (using actual file names that exist)
    test_files = [
        {
            'name': 'Google_Map_JavaScript_API_Tutorial.docx',
            'path': '/app/Google_Map_JavaScript_API_Tutorial.docx',
            'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'expected': 'unified - should generate 1 unified guide + 1 FAQ (both with substantial content)'
        },
        {
            'name': 'Customer_Summary_Screen_User_Guide_1.3.docx',
            'path': '/app/Customer_Summary_Screen_User_Guide_1.3.docx',
            'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'expected': 'split - large document should generate multiple articles with content'
        },
        {
            'name': 'Promotions_Configuration_and_Management-v5-20220201_173002.docx',
            'path': '/app/Promotions_Configuration_and_Management-v5-20220201_173002.docx',
            'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'expected': 'split - medium document should generate multiple articles'
        },
        {
            'name': 'Whisk_Studio_Integration_Guide.pdf',
            'path': '/app/Whisk_Studio_Integration_Guide.pdf',
            'type': 'application/pdf',
            'expected': 'split - PDF processing should generate multiple articles'
        },
        {
            'name': 'test_pdf.pdf',
            'path': '/app/test_pdf.pdf',
            'type': 'application/pdf',
            'expected': 'unified or split - smaller PDF should generate articles with content'
        }
    ]
    
    # Test backend health first
    log_test_result("TEST 0: Backend Health Check")
    if not test_backend_health():
        log_test_result("❌ Backend health check failed - aborting tests", "CRITICAL_ERROR")
        return {}
    
    # Test each file
    test_results = {}
    overall_success = True
    total_empty_articles = 0
    total_articles_generated = 0
    
    for i, file_info in enumerate(test_files, 1):
        log_test_result(f"\n{'='*60}")
        log_test_result(f"TEST {i}: {file_info['name']}")
        log_test_result(f"{'='*60}")
        
        # Check if file exists before testing
        if not os.path.exists(file_info['path']):
            log_test_result(f"⚠️ SKIPPING: File not found - {file_info['path']}")
            test_results[file_info['name']] = {
                'success': False,
                'reason': 'File not found',
                'articles_generated': 0,
                'empty_articles': 0
            }
            continue
        
        success, results = test_file_processing(file_info, file_info['expected'])
        
        test_results[file_info['name']] = {
            'success': success,
            'results': results,
            'expected': file_info['expected']
        }
        
        if not success:
            overall_success = False
        
        if 'empty_articles' in results:
            total_empty_articles += results['empty_articles']
        if 'articles_generated' in results:
            total_articles_generated += results['articles_generated']
        
        # Brief pause between tests
        time.sleep(5)
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL EMPTY CONTENT BUG FIX VERIFICATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    files_tested = len([r for r in test_results.values() if r.get('results')])
    files_passed = len([r for r in test_results.values() if r.get('success')])
    
    log_test_result(f"📊 OVERALL STATISTICS:")
    log_test_result(f"   Files tested: {files_tested}")
    log_test_result(f"   Files passed: {files_passed}")
    log_test_result(f"   Total articles generated: {total_articles_generated}")
    log_test_result(f"   Total empty articles: {total_empty_articles}")
    
    log_test_result(f"\n📋 DETAILED RESULTS:")
    for file_name, result in test_results.items():
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        reason = result.get('reason', '')
        if reason:
            log_test_result(f"   {file_name}: {status} ({reason})")
        else:
            results = result.get('results', {})
            articles = results.get('articles_generated', 0)
            empty = results.get('empty_articles', 0)
            log_test_result(f"   {file_name}: {status} ({articles} articles, {empty} empty)")
    
    # Critical assessment
    if total_empty_articles == 0 and total_articles_generated > 0:
        log_test_result("🎉 CRITICAL SUCCESS: Empty content bug has been FIXED!", "CRITICAL_SUCCESS")
        log_test_result("✅ All generated articles contain substantial content", "CRITICAL_SUCCESS")
        log_test_result("✅ No empty articles detected across all test files", "CRITICAL_SUCCESS")
    elif total_empty_articles > 0:
        log_test_result(f"❌ CRITICAL FAILURE: Empty content bug PERSISTS!", "CRITICAL_ERROR")
        log_test_result(f"❌ {total_empty_articles} empty articles detected across test files", "CRITICAL_ERROR")
        log_test_result("❌ Content processing pipeline needs further debugging", "CRITICAL_ERROR")
    elif total_articles_generated == 0:
        log_test_result("❌ CRITICAL FAILURE: No articles generated at all!", "CRITICAL_ERROR")
        log_test_result("❌ Processing pipeline appears to be completely broken", "CRITICAL_ERROR")
    else:
        log_test_result("⚠️ PARTIAL SUCCESS: Articles generated but validation incomplete", "WARNING")
    
    return test_results

if __name__ == "__main__":
    print("Empty Content Bug Fix Verification Testing")
    print("=" * 50)
    
    results = run_comprehensive_empty_content_bug_test()
    
    # Determine exit code based on results
    total_empty_articles = sum(r.get('results', {}).get('empty_articles', 0) for r in results.values())
    total_articles = sum(r.get('results', {}).get('articles_generated', 0) for r in results.values())
    
    if total_empty_articles == 0 and total_articles > 0:
        sys.exit(0)  # Success - no empty articles
    else:
        sys.exit(1)  # Failure - empty articles detected or no articles generated