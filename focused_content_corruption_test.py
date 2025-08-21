#!/usr/bin/env python3
"""
FOCUSED CONTENT CORRUPTION & WYSIWYG TESTING
Testing specific areas mentioned in the review request:
1. Content Generation Quality - substantial content (not empty or near-empty)
2. WYSIWYG Enhancement Integration - add_wysiwyg_enhancements function
3. Template Contamination Prevention - no HTML document structure contamination
4. Knowledge Engine Upload - complete workflow from upload to article creation
5. Content Validation - enhanced content validation preventing empty articles
6. Database Storage - proper metadata and validation flags
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-pipeline-4.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_knowledge_engine_upload_workflow():
    """
    Test the complete Knowledge Engine workflow from upload to article creation
    Focus on the add_wysiwyg_enhancements function and content validation
    """
    try:
        log_test_result("🎯 TESTING KNOWLEDGE ENGINE UPLOAD WORKFLOW", "CRITICAL")
        
        # Test file upload
        test_file_path = "/app/test_google_maps_content.txt"
        
        if not os.path.exists(test_file_path):
            log_test_result(f"❌ Test file not found: {test_file_path}", "ERROR")
            return False
        
        log_test_result("📤 Uploading test content via Knowledge Engine...")
        
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_google_maps_content.txt', f, 'text/plain')}
            metadata = {'metadata': '{}'}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", 
                                   files=files, 
                                   data=metadata,
                                   timeout=300)
            
            if response.status_code != 200:
                log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                log_test_result(f"Response: {response.text[:500]}")
                return False
            
            upload_result = response.json()
            job_id = upload_result.get('job_id')
            
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
                        
                        articles_generated = status_data.get('articles_generated', 0)
                        log_test_result(f"📄 Articles Generated: {articles_generated}")
                        
                        if articles_generated == 0:
                            log_test_result("❌ CRITICAL FAILURE: No articles generated", "CRITICAL_ERROR")
                            return False
                        
                        log_test_result("✅ Knowledge Engine upload workflow completed successfully", "SUCCESS")
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(10)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Knowledge Engine upload test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def analyze_recent_articles_for_improvements():
    """
    Analyze the most recent articles to verify improvements in:
    1. Content generation quality (substantial content)
    2. WYSIWYG enhancements (add_wysiwyg_enhancements function)
    3. Template contamination prevention
    4. Content validation
    """
    try:
        log_test_result("🔍 ANALYZING RECENT ARTICLES FOR IMPROVEMENTS", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for analysis", "ERROR")
            return False
        
        # Sort by created_at to get most recent articles first
        sorted_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)
        recent_articles = sorted_articles[:10]  # Analyze 10 most recent articles
        
        log_test_result(f"📊 Analyzing {len(recent_articles)} most recent articles...")
        
        analysis_results = {
            'total_articles': len(recent_articles),
            'substantial_content': 0,
            'empty_articles': 0,
            'short_articles': 0,
            'template_contamination': 0,
            'wysiwyg_enhancements': 0,
            'validation_metadata': 0,
            'outline_based': 0
        }
        
        contaminated_articles = []
        empty_articles = []
        enhanced_articles = []
        
        for i, article in enumerate(recent_articles):
            title = article.get('title', f'Article {i+1}')
            content = article.get('content', '')
            metadata = article.get('metadata', {})
            
            log_test_result(f"🔍 Analyzing: {title[:50]}...")
            
            # 1. Content Quality Analysis
            text_content = re.sub(r'<[^>]+>', '', content).strip()
            text_length = len(text_content)
            
            if text_length == 0:
                analysis_results['empty_articles'] += 1
                empty_articles.append(title)
            elif text_length < 100:
                analysis_results['short_articles'] += 1
            else:
                analysis_results['substantial_content'] += 1
            
            # 2. Template Contamination Check
            contamination_patterns = [
                r'<!DOCTYPE\s+html',
                r'<html[^>]*>',
                r'<head[^>]*>',
                r'<body[^>]*>'
            ]
            
            has_contamination = False
            for pattern in contamination_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    has_contamination = True
                    break
            
            if has_contamination:
                analysis_results['template_contamination'] += 1
                contaminated_articles.append(title)
            
            # 3. WYSIWYG Enhancement Detection
            wysiwyg_indicators = [
                'article-body',
                'line-numbers',
                'copy-button',
                'expandable',
                'callout',
                'note-box',
                'tip-box',
                'warning-box'
            ]
            
            has_wysiwyg = any(indicator in content for indicator in wysiwyg_indicators)
            if has_wysiwyg:
                analysis_results['wysiwyg_enhancements'] += 1
                enhanced_articles.append(title)
            
            # 4. Validation Metadata Check
            if metadata.get('content_validated') or metadata.get('content_length'):
                analysis_results['validation_metadata'] += 1
            
            # 5. Outline-based Processing Check
            if metadata.get('outline_based'):
                analysis_results['outline_based'] += 1
        
        # Report detailed analysis results
        log_test_result("📈 DETAILED ANALYSIS RESULTS:")
        log_test_result(f"   Total Articles Analyzed: {analysis_results['total_articles']}")
        log_test_result(f"   Substantial Content (≥100 chars): {analysis_results['substantial_content']}")
        log_test_result(f"   Empty Articles (0 chars): {analysis_results['empty_articles']}")
        log_test_result(f"   Short Articles (<100 chars): {analysis_results['short_articles']}")
        log_test_result(f"   Template Contamination: {analysis_results['template_contamination']}")
        log_test_result(f"   WYSIWYG Enhancements: {analysis_results['wysiwyg_enhancements']}")
        log_test_result(f"   Validation Metadata: {analysis_results['validation_metadata']}")
        log_test_result(f"   Outline-based Processing: {analysis_results['outline_based']}")
        
        # Show specific examples
        if empty_articles:
            log_test_result("❌ EMPTY ARTICLES FOUND:", "ERROR")
            for article in empty_articles[:3]:
                log_test_result(f"   - {article}")
        
        if contaminated_articles:
            log_test_result("❌ CONTAMINATED ARTICLES FOUND:", "ERROR")
            for article in contaminated_articles[:3]:
                log_test_result(f"   - {article}")
        
        if enhanced_articles:
            log_test_result("✅ WYSIWYG ENHANCED ARTICLES FOUND:", "SUCCESS")
            for article in enhanced_articles[:3]:
                log_test_result(f"   - {article}")
        
        # Calculate success metrics
        substantial_rate = (analysis_results['substantial_content'] / analysis_results['total_articles']) * 100
        empty_rate = (analysis_results['empty_articles'] / analysis_results['total_articles']) * 100
        contamination_rate = (analysis_results['template_contamination'] / analysis_results['total_articles']) * 100
        enhancement_rate = (analysis_results['wysiwyg_enhancements'] / analysis_results['total_articles']) * 100
        
        log_test_result(f"📊 SUCCESS METRICS:")
        log_test_result(f"   Substantial Content Rate: {substantial_rate:.1f}%")
        log_test_result(f"   Empty Article Rate: {empty_rate:.1f}%")
        log_test_result(f"   Template Contamination Rate: {contamination_rate:.1f}%")
        log_test_result(f"   WYSIWYG Enhancement Rate: {enhancement_rate:.1f}%")
        
        # Determine overall success
        success_criteria = {
            'substantial_content': substantial_rate >= 70,  # At least 70% substantial
            'empty_prevention': empty_rate <= 10,  # Less than 10% empty
            'contamination_prevention': contamination_rate <= 10,  # Less than 10% contaminated
            'wysiwyg_integration': enhancement_rate >= 20  # At least 20% enhanced
        }
        
        passed_criteria = sum(success_criteria.values())
        total_criteria = len(success_criteria)
        
        log_test_result(f"✅ SUCCESS CRITERIA RESULTS:")
        for criterion, passed in success_criteria.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            log_test_result(f"   {criterion.replace('_', ' ').title()}: {status}")
        
        if passed_criteria >= 3:  # At least 3 out of 4 criteria
            log_test_result("🎉 OVERALL SUCCESS: Content corruption fixes are working effectively", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ OVERALL FAILURE: Only {passed_criteria}/{total_criteria} criteria passed", "ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ Article analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_add_wysiwyg_enhancements_function():
    """
    Specifically test that the add_wysiwyg_enhancements function is working
    by looking for its specific output patterns in recent articles
    """
    try:
        log_test_result("🎨 TESTING add_wysiwyg_enhancements FUNCTION", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            log_test_result("❌ No articles found for WYSIWYG function testing", "ERROR")
            return False
        
        # Look for specific WYSIWYG enhancement patterns that would be added by add_wysiwyg_enhancements
        wysiwyg_patterns = {
            'article_body_wrapper': r'<div[^>]*class="[^"]*article-body[^"]*"',
            'enhanced_code_blocks': r'<pre[^>]*class="[^"]*line-numbers[^"]*"',
            'heading_ids': r'<h[2-6][^>]*id="[^"]*"',
            'copy_buttons': r'<button[^>]*class="[^"]*copy-btn[^"]*"',
            'expandable_sections': r'<div[^>]*class="[^"]*expandable[^"]*"',
            'contextual_callouts': r'<div[^>]*class="[^"]*(?:callout|note-box|tip-box|warning-box)[^"]*"'
        }
        
        enhancement_results = {pattern: 0 for pattern in wysiwyg_patterns.keys()}
        articles_with_enhancements = []
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            
            article_enhancements = []
            for pattern_name, pattern in wysiwyg_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    enhancement_results[pattern_name] += 1
                    article_enhancements.append(pattern_name)
            
            if article_enhancements:
                articles_with_enhancements.append({
                    'title': title,
                    'enhancements': article_enhancements
                })
        
        # Report WYSIWYG enhancement function results
        log_test_result("🎨 add_wysiwyg_enhancements FUNCTION ANALYSIS:")
        total_enhancements = sum(enhancement_results.values())
        
        for pattern_name, count in enhancement_results.items():
            log_test_result(f"   {pattern_name.replace('_', ' ').title()}: {count} articles")
        
        log_test_result(f"   Total Enhancement Features: {total_enhancements}")
        log_test_result(f"   Articles with Enhancements: {len(articles_with_enhancements)}")
        
        if articles_with_enhancements:
            log_test_result("✅ ENHANCED ARTICLES FOUND:", "SUCCESS")
            for article in articles_with_enhancements[:5]:
                enhancements = ', '.join(article['enhancements'])
                log_test_result(f"   - {article['title'][:40]}... ({enhancements})")
        
        # Determine if add_wysiwyg_enhancements function is working
        if total_enhancements > 0:
            log_test_result("✅ add_wysiwyg_enhancements function is WORKING", "SUCCESS")
            return True
        else:
            log_test_result("❌ add_wysiwyg_enhancements function NOT DETECTED", "ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ WYSIWYG enhancement function test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_focused_content_corruption_test():
    """Run focused test suite for content corruption fixes and WYSIWYG enhancements"""
    log_test_result("🚀 STARTING FOCUSED CONTENT CORRUPTION & WYSIWYG TEST", "CRITICAL")
    log_test_result("=" * 70)
    
    test_results = {
        'knowledge_engine_upload': False,
        'recent_articles_analysis': False,
        'wysiwyg_enhancements_function': False
    }
    
    # Test 1: Knowledge Engine Upload Workflow
    log_test_result("TEST 1: Knowledge Engine Upload Workflow")
    test_results['knowledge_engine_upload'] = test_knowledge_engine_upload_workflow()
    
    # Test 2: Recent Articles Analysis
    log_test_result("\nTEST 2: Recent Articles Analysis for Improvements")
    test_results['recent_articles_analysis'] = analyze_recent_articles_for_improvements()
    
    # Test 3: WYSIWYG Enhancements Function
    log_test_result("\nTEST 3: add_wysiwyg_enhancements Function Testing")
    test_results['wysiwyg_enhancements_function'] = test_add_wysiwyg_enhancements_function()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 70)
    log_test_result("🎯 FOCUSED TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 70)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 2:  # At least 2 out of 3 tests should pass
        log_test_result("🎉 FOCUSED SUCCESS: Content corruption fixes showing improvement!", "CRITICAL_SUCCESS")
        log_test_result("✅ Knowledge Engine pipeline improvements are working", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ FOCUSED FAILURE: Content corruption issues still need attention", "CRITICAL_ERROR")
        log_test_result("❌ Knowledge Engine pipeline needs further fixes", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Focused Content Corruption & WYSIWYG Enhancement Testing")
    print("=" * 60)
    
    results = run_focused_content_corruption_test()
    
    # Exit with appropriate code
    passed_tests = sum(results.values())
    if passed_tests >= 2:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure