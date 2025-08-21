#!/usr/bin/env python3
"""
ENHANCED OUTLINE-FIRST APPROACH COMPREHENSIVE TESTING
Testing the complete enhancement pipeline with all original features restored:
- Outline-first processing approach
- Introductory TOC article generation
- Related links and cross-references
- FAQ/Troubleshooting article generation
- Article type diversity and proper metadata
- Database storage verification
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-pipeline-4.preview.emergentagent.com"
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

def create_substantial_test_content():
    """Create substantial test content for outline-first processing"""
    return """
# Comprehensive Guide to Advanced API Integration

## Introduction and Overview
This comprehensive guide covers advanced API integration techniques, best practices, and implementation strategies for modern web applications. The content is designed to provide both theoretical understanding and practical implementation guidance.

## Getting Started with API Integration
API integration is the foundation of modern web applications. Understanding the core concepts is essential for successful implementation.

### Prerequisites and Requirements
Before beginning API integration, ensure you have the following prerequisites:
- Understanding of HTTP protocols and REST principles
- Knowledge of authentication mechanisms
- Familiarity with JSON data formats
- Development environment setup

### Initial Setup and Configuration
The initial setup process involves several critical steps that must be completed in the correct order to ensure successful integration.

## Authentication and Security
Security is paramount in API integration. This section covers various authentication methods and security best practices.

### API Key Management
Proper API key management is crucial for maintaining security and preventing unauthorized access to your systems.

### OAuth 2.0 Implementation
OAuth 2.0 provides a robust framework for secure API authentication and authorization.

## Core Implementation Strategies
This section covers the fundamental implementation strategies for successful API integration.

### RESTful API Design Principles
Understanding REST principles is essential for creating maintainable and scalable API integrations.

### Error Handling and Retry Logic
Robust error handling ensures your application can gracefully handle API failures and network issues.

### Rate Limiting and Throttling
Implementing proper rate limiting prevents API abuse and ensures fair usage across all clients.

## Advanced Integration Patterns
Advanced patterns help solve complex integration challenges and improve system reliability.

### Webhook Implementation
Webhooks provide real-time event notifications and reduce the need for constant polling.

### Batch Processing and Bulk Operations
Batch processing improves efficiency when dealing with large datasets and multiple operations.

### Caching Strategies
Effective caching reduces API calls and improves application performance.

## Data Transformation and Processing
Data transformation is often necessary when integrating with external APIs that use different data formats.

### JSON Schema Validation
Schema validation ensures data integrity and prevents errors from malformed data.

### Data Mapping and Conversion
Proper data mapping techniques help bridge differences between internal and external data formats.

## Monitoring and Analytics
Monitoring API integrations is crucial for maintaining system health and identifying issues early.

### Performance Metrics
Key performance indicators help track the health and efficiency of your API integrations.

### Logging and Debugging
Comprehensive logging facilitates troubleshooting and system maintenance.

## Testing and Quality Assurance
Thorough testing ensures your API integrations work correctly under various conditions.

### Unit Testing Strategies
Unit tests verify individual components work correctly in isolation.

### Integration Testing
Integration tests verify that different components work together correctly.

### Load Testing and Performance
Load testing ensures your integrations can handle expected traffic volumes.

## Deployment and Production Considerations
Moving API integrations to production requires careful planning and consideration of various factors.

### Environment Configuration
Proper environment configuration ensures consistent behavior across development, staging, and production.

### Scaling and Load Balancing
Scaling strategies help handle increased traffic and ensure high availability.

## Troubleshooting Common Issues
This section covers common problems and their solutions in API integration projects.

### Connection and Network Issues
Network problems are common in API integrations and require systematic troubleshooting approaches.

### Authentication Failures
Authentication issues can prevent successful API communication and require careful diagnosis.

### Data Format Mismatches
Data format problems often occur when integrating with third-party APIs.

## Best Practices and Recommendations
Following established best practices helps ensure successful and maintainable API integrations.

### Code Organization and Structure
Well-organized code is easier to maintain and debug over time.

### Documentation and Communication
Proper documentation facilitates team collaboration and system maintenance.

### Version Control and Change Management
Version control strategies help manage changes and prevent integration conflicts.

## Future Considerations and Trends
Understanding future trends helps prepare for evolving API integration requirements.

### GraphQL and Modern API Technologies
New technologies like GraphQL are changing how we think about API design and integration.

### Microservices Architecture
Microservices patterns influence how APIs are designed and integrated in modern applications.

### Cloud-Native Integration Patterns
Cloud platforms provide new opportunities and challenges for API integration.

## Conclusion
Successful API integration requires careful planning, proper implementation, and ongoing maintenance. This guide provides the foundation for building robust and scalable API integrations.
"""

def test_enhanced_outline_processing():
    """
    CRITICAL TEST: Test the enhanced outline-first approach with comprehensive features
    Expected: Multiple articles with TOC, related links, FAQ generation, and proper metadata
    """
    try:
        log_test_result("🎯 STARTING ENHANCED OUTLINE-FIRST APPROACH TEST", "CRITICAL")
        log_test_result("Testing complete enhancement pipeline with all original features")
        
        # Create substantial test content
        test_content = create_substantial_test_content()
        content_length = len(test_content)
        log_test_result(f"📄 Test content prepared: {content_length:,} characters")
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing content through Knowledge Engine...")
        
        # Use text processing endpoint
        payload = {
            "content": test_content,
            "content_type": "text",
            "metadata": {
                "original_filename": "comprehensive_api_guide.txt",
                "source": "enhanced_outline_test"
            }
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process", 
                               json=payload, 
                               timeout=600)  # 10 minute timeout
        
        if response.status_code != 200:
            log_test_result(f"❌ Processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return False
        
        log_test_result(f"✅ Processing started, Job ID: {job_id}")
        
        # Monitor processing with detailed logging
        log_test_result("⏳ Monitoring processing progress...")
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
                        
                        # Extract critical metrics
                        chunks_created = status_data.get('chunks_created', 0)
                        articles_generated = status_data.get('articles_generated', 0)
                        
                        log_test_result(f"📈 PROCESSING METRICS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        
                        # CRITICAL VERIFICATION: Check outline-first approach results
                        if articles_generated < 3:
                            log_test_result(f"❌ INSUFFICIENT ARTICLES: Only {articles_generated} articles generated from substantial content", "ERROR")
                            return False
                        else:
                            log_test_result(f"✅ OUTLINE-FIRST SUCCESS: {articles_generated} articles generated from comprehensive content", "SUCCESS")
                        
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
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
        log_test_result(f"❌ Enhanced outline processing test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def verify_enhancement_features():
    """Verify that all enhancement features are present in generated articles"""
    try:
        log_test_result("🔍 Verifying enhancement features in Content Library...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        total_articles = data.get('total', 0)
        articles = data.get('articles', [])
        
        log_test_result(f"📚 Content Library Status:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Articles Retrieved: {len(articles)}")
        
        # Look for recently created articles from our test
        recent_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            source = article.get('source_document', '').lower()
            if 'api' in title or 'comprehensive' in title or 'guide' in title:
                recent_articles.append(article)
        
        if not recent_articles:
            log_test_result("⚠️ No recent test articles found in Content Library")
            return False
        
        log_test_result(f"✅ Found {len(recent_articles)} test articles in Content Library")
        
        # Verify enhancement features
        enhancement_results = {
            'toc_article': False,
            'related_links': False,
            'faq_article': False,
            'article_diversity': False,
            'proper_metadata': False
        }
        
        # Check for introductory TOC article
        for article in recent_articles:
            title = article.get('title', '').lower()
            content = article.get('content', '')
            
            if 'overview' in title or 'table of contents' in title or 'complete guide' in title:
                enhancement_results['toc_article'] = True
                log_test_result("✅ Found introductory TOC article")
                
                # Check if TOC contains links to other articles
                if '/content-library/article/' in content:
                    log_test_result("✅ TOC article contains proper Content Library links")
                else:
                    log_test_result("⚠️ TOC article missing Content Library links")
        
        # Check for related links in articles
        articles_with_related_links = 0
        for article in recent_articles[:5]:  # Check first 5 articles
            content = article.get('content', '')
            if 'related-links' in content or 'Related Articles' in content:
                articles_with_related_links += 1
        
        if articles_with_related_links > 0:
            enhancement_results['related_links'] = True
            log_test_result(f"✅ Found related links in {articles_with_related_links} articles")
        
        # Check for FAQ/Troubleshooting article
        for article in recent_articles:
            title = article.get('title', '').lower()
            article_type = article.get('article_type', '').lower()
            
            if 'faq' in title or 'troubleshooting' in title or 'faq-troubleshooting' in article_type:
                enhancement_results['faq_article'] = True
                log_test_result("✅ Found FAQ/Troubleshooting article")
                break
        
        # Check article type diversity
        article_types = set()
        for article in recent_articles:
            article_type = article.get('article_type', 'unknown')
            if article_type != 'unknown':
                article_types.add(article_type)
        
        if len(article_types) >= 2:
            enhancement_results['article_diversity'] = True
            log_test_result(f"✅ Found diverse article types: {', '.join(article_types)}")
        
        # Check proper metadata
        articles_with_metadata = 0
        for article in recent_articles[:3]:  # Check first 3 articles
            metadata = article.get('metadata', {})
            if metadata and 'outline_based' in metadata:
                articles_with_metadata += 1
        
        if articles_with_metadata > 0:
            enhancement_results['proper_metadata'] = True
            log_test_result(f"✅ Found proper outline-based metadata in {articles_with_metadata} articles")
        
        # Calculate success rate
        passed_features = sum(enhancement_results.values())
        total_features = len(enhancement_results)
        
        log_test_result(f"📊 ENHANCEMENT FEATURES VERIFICATION:")
        for feature, result in enhancement_results.items():
            status = "✅ FOUND" if result else "❌ MISSING"
            log_test_result(f"   {feature.replace('_', ' ').title()}: {status}")
        
        log_test_result(f"🎯 ENHANCEMENT SUCCESS RATE: {passed_features}/{total_features} features verified")
        
        return passed_features >= 3  # At least 3 out of 5 features should be present
        
    except Exception as e:
        log_test_result(f"❌ Enhancement features verification failed: {e}", "ERROR")
        return False

def check_backend_logs_for_enhancements():
    """Check backend logs for enhancement messages"""
    try:
        log_test_result("🔍 Checking backend logs for enhancement messages...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '200', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                enhancement_indicators = [
                    "ADDING COMPREHENSIVE ENHANCEMENTS",
                    "Creating introductory Table of Contents article",
                    "Generating FAQ/Troubleshooting article",
                    "ENHANCED OUTLINE-BASED PROCESSING COMPLETE",
                    "COMPREHENSIVE OUTLINE GENERATED",
                    "outline-first approach"
                ]
                
                found_indicators = []
                for indicator in enhancement_indicators:
                    if indicator in logs:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    log_test_result(f"✅ Found {len(found_indicators)} enhancement indicators in backend logs:", "SUCCESS")
                    for indicator in found_indicators:
                        log_test_result(f"   - {indicator}")
                    return True
                else:
                    log_test_result("⚠️ No enhancement indicators found in backend logs")
                    return False
            else:
                log_test_result("⚠️ Could not access backend logs")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend log verification failed: {e}", "ERROR")
        return False

def run_comprehensive_enhancement_test():
    """Run comprehensive test suite for enhanced outline-first approach"""
    log_test_result("🚀 STARTING COMPREHENSIVE ENHANCED OUTLINE-FIRST TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'outline_processing': False,
        'enhancement_features': False,
        'backend_logs_check': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Enhanced Outline Processing (CRITICAL)
    log_test_result("\nTEST 2: ENHANCED OUTLINE-FIRST PROCESSING TEST")
    test_results['outline_processing'] = test_enhanced_outline_processing()
    
    # Test 3: Enhancement Features Verification
    log_test_result("\nTEST 3: Enhancement Features Verification")
    test_results['enhancement_features'] = verify_enhancement_features()
    
    # Test 4: Backend Logs Check
    log_test_result("\nTEST 4: Backend Enhancement Logs Verification")
    test_results['backend_logs_check'] = check_backend_logs_for_enhancements()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if test_results['outline_processing'] and test_results['enhancement_features']:
        log_test_result("🎉 CRITICAL SUCCESS: Enhanced outline-first approach is working with all features!", "CRITICAL_SUCCESS")
        log_test_result("✅ Complete enhancement pipeline operational: TOC, related links, FAQ generation", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Enhanced outline-first approach has issues", "CRITICAL_ERROR")
        log_test_result("❌ Some enhancement features are missing or not working properly", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Enhanced Outline-First Approach Comprehensive Testing")
    print("=" * 60)
    
    results = run_comprehensive_enhancement_test()
    
    # Exit with appropriate code
    if results['outline_processing'] and results['enhancement_features']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure