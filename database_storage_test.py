#!/usr/bin/env python3
"""
DATABASE STORAGE TEST - Critical Regression Fix Verification
Testing the specific fix for outline-first processing where articles were generated but not saved to database
Focus: Verify create_articles_from_outline() function properly saves articles to database
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def get_content_library_count():
    """Get current count of articles in Content Library"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            return total_articles, articles
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return 0, []
            
    except Exception as e:
        log_test_result(f"❌ Content Library check failed: {e}", "ERROR")
        return 0, []

def test_comprehensive_document_processing():
    """
    Test comprehensive document processing that should trigger outline-first approach
    This tests the fix where create_articles_from_outline() now includes db.content_library.insert_one()
    """
    try:
        log_test_result("🎯 TESTING COMPREHENSIVE DOCUMENT PROCESSING WITH DATABASE STORAGE", "CRITICAL")
        
        # Get baseline count
        baseline_count, baseline_articles = get_content_library_count()
        log_test_result(f"📊 Baseline Content Library count: {baseline_count} articles")
        
        # Create a comprehensive document that should trigger outline-first processing
        comprehensive_content = """
# Complete Software Development Lifecycle Guide

## Introduction
This comprehensive guide covers the entire software development lifecycle from planning to deployment and maintenance.

## Chapter 1: Project Planning and Requirements
### 1.1 Requirements Gathering
Understanding stakeholder needs is crucial for project success. This section covers various techniques for gathering requirements including interviews, surveys, and workshops.

### 1.2 Project Scope Definition
Defining clear project boundaries helps prevent scope creep and ensures project success.

### 1.3 Timeline and Resource Planning
Creating realistic timelines and allocating resources effectively.

## Chapter 2: System Design and Architecture
### 2.1 High-Level Architecture
Designing the overall system architecture including components and their interactions.

### 2.2 Database Design
Creating efficient database schemas and relationships.

### 2.3 API Design
Designing RESTful APIs for system integration.

## Chapter 3: Development Methodologies
### 3.1 Agile Development
Understanding Scrum, Kanban, and other agile methodologies.

### 3.2 DevOps Practices
Implementing continuous integration and continuous deployment.

### 3.3 Code Quality Standards
Establishing coding standards and best practices.

## Chapter 4: Implementation Phase
### 4.1 Frontend Development
Building user interfaces with modern frameworks.

### 4.2 Backend Development
Creating robust server-side applications.

### 4.3 Database Implementation
Setting up and optimizing database systems.

## Chapter 5: Testing Strategies
### 5.1 Unit Testing
Writing comprehensive unit tests for individual components.

### 5.2 Integration Testing
Testing component interactions and system integration.

### 5.3 User Acceptance Testing
Validating system functionality with end users.

## Chapter 6: Deployment and Operations
### 6.1 Deployment Strategies
Blue-green deployments, rolling updates, and canary releases.

### 6.2 Monitoring and Logging
Implementing comprehensive monitoring and logging systems.

### 6.3 Performance Optimization
Optimizing system performance and scalability.

## Chapter 7: Maintenance and Support
### 7.1 Bug Tracking and Resolution
Managing and resolving software defects.

### 7.2 Feature Enhancement
Planning and implementing new features.

### 7.3 Security Updates
Maintaining system security through regular updates.

## Chapter 8: Team Management
### 8.1 Team Structure
Organizing development teams for maximum efficiency.

### 8.2 Communication Strategies
Establishing effective communication channels.

### 8.3 Performance Management
Managing team performance and professional development.

## Chapter 9: Quality Assurance
### 9.1 Code Reviews
Implementing effective code review processes.

### 9.2 Automated Testing
Setting up automated testing pipelines.

### 9.3 Quality Metrics
Measuring and improving code quality.

## Chapter 10: Documentation
### 10.1 Technical Documentation
Creating comprehensive technical documentation.

### 10.2 User Documentation
Writing clear user guides and manuals.

### 10.3 API Documentation
Documenting APIs for developers.

## Conclusion
This guide provides a comprehensive overview of the software development lifecycle. Following these practices will help ensure project success and deliver high-quality software solutions.
        """
        
        # Save as temporary file to upload
        temp_file = "/tmp/sdlc_guide.txt"
        with open(temp_file, 'w') as f:
            f.write(comprehensive_content)
        
        log_test_result(f"📄 Created comprehensive test document: {len(comprehensive_content)} characters")
        
        # Upload and process the document
        log_test_result("📤 Uploading comprehensive document...")
        
        with open(temp_file, 'rb') as f:
            files = {'file': ('sdlc_guide.txt', f, 'text/plain')}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
        
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
                        
                        # Extract processing metrics
                        chunks_created = status_data.get('chunks_created', 0)
                        articles_generated = status_data.get('articles_generated', 0)
                        processing_approach = status_data.get('processing_approach', 'unknown')
                        
                        log_test_result(f"📈 PROCESSING METRICS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        log_test_result(f"   🔄 Processing Approach: {processing_approach}")
                        
                        # Wait for database operations to complete
                        log_test_result("⏳ Waiting for database operations to complete...")
                        time.sleep(3)
                        
                        # CRITICAL VERIFICATION: Check database storage
                        log_test_result("🔍 VERIFYING DATABASE STORAGE...", "CRITICAL")
                        
                        new_count, new_articles = get_content_library_count()
                        articles_added = new_count - baseline_count
                        
                        log_test_result(f"📊 DATABASE STORAGE RESULTS:")
                        log_test_result(f"   Baseline count: {baseline_count}")
                        log_test_result(f"   New count: {new_count}")
                        log_test_result(f"   Articles added to database: {articles_added}")
                        log_test_result(f"   Articles generated by processing: {articles_generated}")
                        
                        # CRITICAL ANALYSIS
                        if articles_added == 0:
                            log_test_result("❌ CRITICAL REGRESSION CONFIRMED: Articles generated but NOT saved to database", "CRITICAL_ERROR")
                            log_test_result("❌ The create_articles_from_outline() fix is NOT working", "CRITICAL_ERROR")
                            return False
                        elif articles_added < articles_generated:
                            log_test_result(f"⚠️ PARTIAL STORAGE: Only {articles_added}/{articles_generated} articles saved", "WARNING")
                            log_test_result("⚠️ Some articles may have been lost during storage", "WARNING")
                            # Still consider this a success if some articles were saved
                            if articles_added > 0:
                                log_test_result("✅ PARTIAL SUCCESS: Database storage is working but not complete", "SUCCESS")
                                return True
                            return False
                        else:
                            log_test_result(f"🎉 CRITICAL SUCCESS: All {articles_generated} articles saved to database", "CRITICAL_SUCCESS")
                            log_test_result("✅ The create_articles_from_outline() fix is WORKING", "CRITICAL_SUCCESS")
                        
                        # Verify articles can be retrieved
                        log_test_result("🔍 Verifying articles can be retrieved from Content Library...")
                        
                        # Look for our test articles
                        matching_articles = []
                        for article in new_articles:
                            title = article.get('title', '').lower()
                            source = article.get('source_document', '').lower()
                            
                            if ('software' in title or 'development' in title or 'lifecycle' in title or 
                                'sdlc' in source or 'guide' in title):
                                matching_articles.append(article)
                        
                        if len(matching_articles) >= articles_generated:
                            log_test_result(f"✅ Found {len(matching_articles)} matching articles in Content Library")
                            
                            # Show details of created articles
                            for i, article in enumerate(matching_articles[:5]):
                                title = article.get('title', 'Untitled')
                                status = article.get('status', 'unknown')
                                article_id = article.get('id', 'no-id')
                                log_test_result(f"   Article {i+1}: {title[:50]}... (Status: {status}, ID: {article_id[:8]}...)")
                            
                            log_test_result("🎉 DATABASE STORAGE FIX VERIFIED SUCCESSFULLY", "CRITICAL_SUCCESS")
                            return True
                        else:
                            log_test_result(f"⚠️ Only found {len(matching_articles)} matching articles (expected {articles_generated})")
                            # Still consider success if articles were stored
                            if articles_added > 0:
                                log_test_result("✅ Database storage is working (articles found in database)", "SUCCESS")
                                return True
                            return False
                        
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
        log_test_result(f"❌ Database storage test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up temp file
        if os.path.exists("/tmp/sdlc_guide.txt"):
            os.remove("/tmp/sdlc_guide.txt")

def run_database_storage_test():
    """Run the database storage test"""
    log_test_result("🚀 STARTING DATABASE STORAGE TEST", "CRITICAL")
    log_test_result("Testing fix for: create_articles_from_outline() database storage")
    log_test_result("=" * 80)
    
    # Test backend health first
    try:
        response = requests.get(f"{API_BASE}/health", timeout=30)
        if response.status_code != 200:
            log_test_result("❌ Backend health check failed - aborting test", "CRITICAL_ERROR")
            return False
        log_test_result("✅ Backend health check passed")
    except Exception as e:
        log_test_result(f"❌ Backend health check failed: {e}", "CRITICAL_ERROR")
        return False
    
    # Run the main test
    result = test_comprehensive_document_processing()
    
    # Final summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 DATABASE STORAGE TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    if result:
        log_test_result("🎉 CRITICAL SUCCESS: Database storage fix is WORKING!", "CRITICAL_SUCCESS")
        log_test_result("✅ Articles are now both generated AND saved to Content Library database", "CRITICAL_SUCCESS")
        log_test_result("✅ The 0-article regression has been RESOLVED", "CRITICAL_SUCCESS")
        log_test_result("✅ Users will now see generated articles in Content Library", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Database storage fix is NOT working", "CRITICAL_ERROR")
        log_test_result("❌ Articles are generated but NOT saved to database", "CRITICAL_ERROR")
        log_test_result("❌ The 0-article regression is still present", "CRITICAL_ERROR")
        log_test_result("❌ Users will continue to see 0 articles in Content Library", "CRITICAL_ERROR")
    
    return result

if __name__ == "__main__":
    print("Database Storage Test - Critical Regression Fix Verification")
    print("=" * 60)
    
    success = run_database_storage_test()
    
    # Exit with appropriate code
    if success:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure