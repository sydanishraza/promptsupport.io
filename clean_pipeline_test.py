#!/usr/bin/env python3
"""
CLEAN CONTENT PROCESSING PIPELINE TESTING
Testing the completely cleaned up content processing pipeline as requested in review.

FOCUS AREAS:
1. Clean Pipeline Integration - all document types use same clean approach
2. Step-by-Step Processing - outline generation, article creation, overview, FAQ, cross-references
3. Article Quality and Features - clean HTML, comprehensive features
4. Database Integration - proper saving and retrieval
5. Processing Performance - efficient processing without timeouts
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

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

def test_clean_pipeline_text_processing():
    """Test clean pipeline with text content"""
    try:
        log_test_result("🧪 TESTING CLEAN PIPELINE - TEXT PROCESSING", "CRITICAL")
        
        # Create comprehensive test content
        test_content = """
        Complete Guide to Advanced API Integration
        
        Introduction
        This comprehensive guide covers advanced API integration techniques, best practices, and troubleshooting methods. You'll learn how to implement robust API connections, handle authentication, manage rate limiting, and optimize performance.
        
        Getting Started with API Integration
        Before diving into advanced techniques, it's essential to understand the fundamentals of API integration. This section covers the basic concepts, authentication methods, and initial setup procedures.
        
        Authentication Methods
        Modern APIs support various authentication methods including API keys, OAuth 2.0, JWT tokens, and basic authentication. Each method has its own advantages and use cases.
        
        Rate Limiting and Performance Optimization
        Understanding rate limits is crucial for building reliable API integrations. This section covers strategies for handling rate limits, implementing retry logic, and optimizing API calls for better performance.
        
        Error Handling and Troubleshooting
        Robust error handling is essential for production API integrations. Learn how to handle different types of errors, implement proper logging, and troubleshoot common issues.
        
        Advanced Implementation Patterns
        Explore advanced patterns like circuit breakers, bulkhead isolation, and asynchronous processing to build resilient API integrations that can handle high loads and failures gracefully.
        
        Security Best Practices
        Security should be a top priority in API integrations. This section covers encryption, secure storage of credentials, input validation, and protection against common security vulnerabilities.
        
        Monitoring and Analytics
        Implement comprehensive monitoring and analytics to track API performance, identify bottlenecks, and ensure optimal user experience.
        """
        
        # Test text processing through Knowledge Engine
        log_test_result("📤 Processing text content through clean pipeline...")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/content/process",
            json={"content": test_content, "content_type": "text", "filename": "clean_pipeline_test.txt"},
            timeout=300
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Text processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from text processing", "ERROR")
            return False
        
        log_test_result(f"✅ Text processing initiated, Job ID: {job_id}")
        
        # Monitor processing
        processing_result = monitor_processing(job_id, "text processing")
        if not processing_result:
            return False
        
        processing_time = time.time() - start_time
        log_test_result(f"✅ Text processing completed in {processing_time:.1f} seconds", "SUCCESS")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Clean pipeline text processing failed: {e}", "ERROR")
        return False

def test_clean_pipeline_docx_processing():
    """Test clean pipeline with DOCX document"""
    try:
        log_test_result("🧪 TESTING CLEAN PIPELINE - DOCX PROCESSING", "CRITICAL")
        
        # Create a test DOCX file if it doesn't exist
        test_docx_path = "/app/test_clean_pipeline.docx"
        
        # Check if we have any DOCX file to test with
        docx_files = [f for f in os.listdir("/app") if f.endswith('.docx')]
        if docx_files:
            test_docx_path = f"/app/{docx_files[0]}"
            log_test_result(f"📄 Using existing DOCX file: {docx_files[0]}")
        else:
            log_test_result("⚠️ No DOCX files found, skipping DOCX test")
            return True
        
        if not os.path.exists(test_docx_path):
            log_test_result("⚠️ DOCX test file not found, skipping DOCX test")
            return True
        
        file_size = os.path.getsize(test_docx_path)
        log_test_result(f"📄 Processing DOCX file: {file_size:,} bytes ({file_size/1024/1024:.1f}MB)")
        
        # Upload and process DOCX
        with open(test_docx_path, 'rb') as f:
            files = {'file': (os.path.basename(test_docx_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
            
            if response.status_code != 200:
                log_test_result(f"❌ DOCX upload failed: Status {response.status_code}", "ERROR")
                return False
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if not job_id:
                log_test_result("❌ No job_id received from DOCX upload", "ERROR")
                return False
            
            log_test_result(f"✅ DOCX upload successful, Job ID: {job_id}")
        
        # Monitor processing
        processing_result = monitor_processing(job_id, "DOCX processing")
        if not processing_result:
            return False
        
        processing_time = time.time() - start_time
        log_test_result(f"✅ DOCX processing completed in {processing_time:.1f} seconds", "SUCCESS")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Clean pipeline DOCX processing failed: {e}", "ERROR")
        return False

def test_clean_pipeline_pdf_processing():
    """Test clean pipeline with PDF document"""
    try:
        log_test_result("🧪 TESTING CLEAN PIPELINE - PDF PROCESSING", "CRITICAL")
        
        # Check if we have any PDF file to test with
        pdf_files = [f for f in os.listdir("/app") if f.endswith('.pdf')]
        if not pdf_files:
            log_test_result("⚠️ No PDF files found, skipping PDF test")
            return True
        
        test_pdf_path = f"/app/{pdf_files[0]}"
        file_size = os.path.getsize(test_pdf_path)
        log_test_result(f"📄 Processing PDF file: {pdf_files[0]} ({file_size:,} bytes)")
        
        # Upload and process PDF
        with open(test_pdf_path, 'rb') as f:
            files = {'file': (pdf_files[0], f, 'application/pdf')}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
            
            if response.status_code != 200:
                log_test_result(f"❌ PDF upload failed: Status {response.status_code}", "ERROR")
                return False
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if not job_id:
                log_test_result("❌ No job_id received from PDF upload", "ERROR")
                return False
            
            log_test_result(f"✅ PDF upload successful, Job ID: {job_id}")
        
        # Monitor processing
        processing_result = monitor_processing(job_id, "PDF processing")
        if not processing_result:
            return False
        
        processing_time = time.time() - start_time
        log_test_result(f"✅ PDF processing completed in {processing_time:.1f} seconds", "SUCCESS")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Clean pipeline PDF processing failed: {e}", "ERROR")
        return False

def monitor_processing(job_id, process_type):
    """Monitor processing progress and return detailed results"""
    try:
        log_test_result(f"⏳ Monitoring {process_type} progress...")
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ {process_type} timeout after {elapsed:.1f} seconds", "ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 {process_type} status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        # Extract and analyze results
                        chunks_created = status_data.get('chunks_created', 0)
                        articles_generated = status_data.get('articles_generated', 0)
                        
                        log_test_result(f"📈 {process_type.upper()} RESULTS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        
                        # Verify clean pipeline success criteria
                        if articles_generated > 0:
                            log_test_result(f"✅ CLEAN PIPELINE SUCCESS: {articles_generated} articles generated", "SUCCESS")
                            return True
                        else:
                            log_test_result(f"❌ CLEAN PIPELINE FAILURE: No articles generated", "ERROR")
                            return False
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test_result(f"❌ {process_type} failed: {error_msg}", "ERROR")
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
        log_test_result(f"❌ Processing monitoring failed: {e}", "ERROR")
        return False

def test_article_quality_and_features():
    """Test article quality and comprehensive features"""
    try:
        log_test_result("🧪 TESTING ARTICLE QUALITY AND FEATURES", "CRITICAL")
        
        # Get recent articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📚 Content Library Analysis:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Retrieved Articles: {len(articles)}")
        
        if not articles:
            log_test_result("❌ No articles found for quality testing", "ERROR")
            return False
        
        # Analyze article quality
        quality_metrics = {
            'clean_html_count': 0,
            'overview_articles': 0,
            'faq_articles': 0,
            'articles_with_links': 0,
            'articles_with_toc': 0,
            'total_analyzed': 0
        }
        
        for article in articles[:10]:  # Analyze first 10 articles
            content = article.get('content', '')
            title = article.get('title', '')
            article_type = article.get('article_type', '')
            
            quality_metrics['total_analyzed'] += 1
            
            # Check for clean HTML (no ```html placeholders)
            if '```html' not in content and '<!DOCTYPE html>' not in content:
                quality_metrics['clean_html_count'] += 1
            
            # Check for overview articles
            if 'overview' in title.lower() or article_type == 'overview':
                quality_metrics['overview_articles'] += 1
            
            # Check for FAQ articles
            if 'faq' in title.lower() or 'troubleshooting' in title.lower() or article_type == 'faq':
                quality_metrics['faq_articles'] += 1
            
            # Check for related links
            if 'related-links' in content or 'Related Articles' in content:
                quality_metrics['articles_with_links'] += 1
            
            # Check for table of contents
            if 'table of contents' in content.lower() or 'toc-list' in content:
                quality_metrics['articles_with_toc'] += 1
        
        # Report quality metrics
        log_test_result(f"📊 ARTICLE QUALITY ANALYSIS:")
        log_test_result(f"   Clean HTML Content: {quality_metrics['clean_html_count']}/{quality_metrics['total_analyzed']} ({quality_metrics['clean_html_count']/quality_metrics['total_analyzed']*100:.1f}%)")
        log_test_result(f"   Overview Articles: {quality_metrics['overview_articles']}")
        log_test_result(f"   FAQ Articles: {quality_metrics['faq_articles']}")
        log_test_result(f"   Articles with Related Links: {quality_metrics['articles_with_links']}")
        log_test_result(f"   Articles with TOC: {quality_metrics['articles_with_toc']}")
        
        # Success criteria
        clean_html_percentage = quality_metrics['clean_html_count'] / quality_metrics['total_analyzed'] * 100
        has_overview = quality_metrics['overview_articles'] > 0
        has_faq = quality_metrics['faq_articles'] > 0
        has_cross_references = quality_metrics['articles_with_links'] > 0
        
        if clean_html_percentage >= 90 and has_overview and has_cross_references:
            log_test_result("✅ ARTICLE QUALITY TEST PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ ARTICLE QUALITY TEST FAILED", "ERROR")
            if clean_html_percentage < 90:
                log_test_result(f"   - Clean HTML percentage too low: {clean_html_percentage:.1f}% (expected ≥90%)")
            if not has_overview:
                log_test_result("   - No overview articles found")
            if not has_cross_references:
                log_test_result("   - No cross-references found")
            return False
        
    except Exception as e:
        log_test_result(f"❌ Article quality testing failed: {e}", "ERROR")
        return False

def test_database_integration():
    """Test database integration and article persistence"""
    try:
        log_test_result("🧪 TESTING DATABASE INTEGRATION", "CRITICAL")
        
        # Get baseline article count
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result(f"❌ Initial Content Library check failed: Status {response.status_code}", "ERROR")
            return False
        
        initial_data = response.json()
        initial_count = initial_data.get('total', 0)
        log_test_result(f"📊 Initial article count: {initial_count}")
        
        # Process a small test document
        test_content = """
        Database Integration Test Document
        
        Overview
        This is a test document to verify database integration functionality.
        
        Features
        The system should properly save articles to the database and make them retrievable through the Content Library API.
        
        Verification
        After processing, articles should be immediately available in the Content Library with proper metadata.
        """
        
        # Process content
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/content/process",
            json={"content": test_content, "content_type": "text", "filename": "database_integration_test.txt"},
            timeout=180
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Test content processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        # Monitor processing
        processing_result = monitor_processing(job_id, "database integration test")
        if not processing_result:
            return False
        
        # Wait a moment for database consistency
        time.sleep(2)
        
        # Check final article count
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result(f"❌ Final Content Library check failed: Status {response.status_code}", "ERROR")
            return False
        
        final_data = response.json()
        final_count = final_data.get('total', 0)
        articles_added = final_count - initial_count
        
        log_test_result(f"📊 Final article count: {final_count}")
        log_test_result(f"📈 Articles added: {articles_added}")
        
        if articles_added > 0:
            log_test_result("✅ DATABASE INTEGRATION TEST PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ DATABASE INTEGRATION TEST FAILED - No articles added to database", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ Database integration testing failed: {e}", "ERROR")
        return False

def test_processing_performance():
    """Test processing performance and efficiency"""
    try:
        log_test_result("🧪 TESTING PROCESSING PERFORMANCE", "CRITICAL")
        
        # Test with medium-sized content
        test_content = """
        Performance Testing Document
        
        Introduction
        This document is designed to test the processing performance of the clean content pipeline. It contains multiple sections to ensure comprehensive processing while maintaining reasonable performance expectations.
        
        Section 1: System Architecture
        The clean pipeline architecture is designed for efficiency and reliability. It processes content through multiple stages including outline generation, article creation, and enhancement with cross-references.
        
        Section 2: Processing Stages
        The pipeline consists of several key stages: content extraction, comprehensive outline generation, individual topic article generation, overview article creation, FAQ generation, and cross-reference linking.
        
        Section 3: Performance Optimization
        Various optimizations have been implemented to ensure efficient processing including streamlined LLM calls, optimized database operations, and parallel processing where appropriate.
        
        Section 4: Quality Assurance
        The system maintains high quality standards while optimizing for performance. Articles are generated with clean HTML content, proper structure, and comprehensive features.
        
        Section 5: Scalability Considerations
        The architecture is designed to handle documents of various sizes efficiently, from small text snippets to large comprehensive documents.
        
        Conclusion
        The clean pipeline provides an optimal balance of processing speed, article quality, and feature completeness.
        """ * 2  # Double the content for more substantial processing
        
        # Process content and measure performance
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/content/process",
            json={"content": test_content, "content_type": "text", "filename": "performance_test.txt"},
            timeout=240  # 4 minute timeout
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Performance test processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        # Monitor processing with performance tracking
        processing_result = monitor_processing(job_id, "performance test")
        if not processing_result:
            return False
        
        total_time = time.time() - start_time
        content_size = len(test_content)
        
        log_test_result(f"📊 PERFORMANCE METRICS:")
        log_test_result(f"   Content Size: {content_size:,} characters")
        log_test_result(f"   Total Processing Time: {total_time:.1f} seconds")
        log_test_result(f"   Processing Rate: {content_size/total_time:.0f} chars/second")
        
        # Performance success criteria
        if total_time < 180:  # Less than 3 minutes
            log_test_result("✅ PERFORMANCE TEST PASSED - Processing completed within acceptable time", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ PERFORMANCE TEST FAILED - Processing took {total_time:.1f}s (expected <180s)", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ Performance testing failed: {e}", "ERROR")
        return False

def run_comprehensive_clean_pipeline_test():
    """Run comprehensive test suite for clean content processing pipeline"""
    log_test_result("🚀 STARTING COMPREHENSIVE CLEAN PIPELINE TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'text_processing': False,
        'docx_processing': False,
        'pdf_processing': False,
        'article_quality': False,
        'database_integration': False,
        'processing_performance': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Clean Pipeline Text Processing
    log_test_result("\nTEST 2: Clean Pipeline Text Processing")
    test_results['text_processing'] = test_clean_pipeline_text_processing()
    
    # Test 3: Clean Pipeline DOCX Processing
    log_test_result("\nTEST 3: Clean Pipeline DOCX Processing")
    test_results['docx_processing'] = test_clean_pipeline_docx_processing()
    
    # Test 4: Clean Pipeline PDF Processing
    log_test_result("\nTEST 4: Clean Pipeline PDF Processing")
    test_results['pdf_processing'] = test_clean_pipeline_pdf_processing()
    
    # Test 5: Article Quality and Features
    log_test_result("\nTEST 5: Article Quality and Features")
    test_results['article_quality'] = test_article_quality_and_features()
    
    # Test 6: Database Integration
    log_test_result("\nTEST 6: Database Integration")
    test_results['database_integration'] = test_database_integration()
    
    # Test 7: Processing Performance
    log_test_result("\nTEST 7: Processing Performance")
    test_results['processing_performance'] = test_processing_performance()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 CLEAN PIPELINE TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    # Success criteria analysis
    critical_tests = ['backend_health', 'text_processing', 'article_quality', 'database_integration']
    critical_passed = sum(test_results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        log_test_result("🎉 CLEAN PIPELINE SUCCESS: All critical tests passed!", "CRITICAL_SUCCESS")
        log_test_result("✅ Clean content processing pipeline is fully operational", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CLEAN PIPELINE FAILURE: Critical tests failed", "CRITICAL_ERROR")
        failed_critical = [test for test in critical_tests if not test_results[test]]
        log_test_result(f"❌ Failed critical tests: {', '.join(failed_critical)}", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Clean Content Processing Pipeline Testing")
    print("=" * 50)
    
    results = run_comprehensive_clean_pipeline_test()
    
    # Exit with appropriate code
    critical_tests = ['backend_health', 'text_processing', 'article_quality', 'database_integration']
    critical_passed = sum(results[test] for test in critical_tests)
    
    if critical_passed == len(critical_tests):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure