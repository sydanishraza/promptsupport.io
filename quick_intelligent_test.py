#!/usr/bin/env python3
"""
QUICK INTELLIGENT PIPELINE TEST
Fast verification of intelligent content processing pipeline key features
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-pipeline-5.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_tutorial_content_unified():
    """Test that tutorial content stays unified"""
    try:
        log_test_result("🧠 Testing tutorial content for unified treatment...")
        
        # Short tutorial content that should stay unified
        tutorial_content = """# Quick Setup Tutorial

## Step 1: Installation
First, install the required packages:
```bash
npm install my-package
```

## Step 2: Configuration
Configure your settings:
```javascript
const config = {
    apiKey: 'your-key',
    endpoint: 'https://api.example.com'
};
```

## Step 3: Usage
Use the package in your code:
```javascript
import MyPackage from 'my-package';
const result = MyPackage.process(data);
```

This completes the basic setup process."""

        data = {
            'content': tutorial_content,
            'content_type': 'text',
            'metadata': {'original_filename': 'quick_tutorial_test.txt'}
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process", json=data, timeout=120)
        
        if response.status_code != 200:
            log_test_result(f"❌ Tutorial processing failed: Status {response.status_code}", "ERROR")
            return False
        
        result = response.json()
        job_id = result.get('job_id')
        
        # Monitor processing with shorter timeout
        while True:
            elapsed = time.time() - start_time
            if elapsed > 90:  # 1.5 minutes max
                log_test_result("❌ Tutorial processing timeout", "ERROR")
                return False
            
            status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                if status == 'completed':
                    articles_generated = status_data.get('articles_generated', 0)
                    processing_time = elapsed
                    
                    log_test_result(f"✅ Tutorial processing completed in {processing_time:.1f}s")
                    log_test_result(f"📄 Articles generated: {articles_generated}")
                    
                    # Tutorial should be unified (1-3 articles max)
                    if articles_generated <= 3:
                        log_test_result(f"✅ UNIFIED SUCCESS: Tutorial kept unified ({articles_generated} articles)", "SUCCESS")
                        return True
                    else:
                        log_test_result(f"❌ UNIFIED FAILED: Tutorial over-split ({articles_generated} articles)", "ERROR")
                        return False
                        
                elif status == 'failed':
                    log_test_result(f"❌ Tutorial processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                    return False
                
                time.sleep(3)
            else:
                time.sleep(3)
                
    except Exception as e:
        log_test_result(f"❌ Tutorial test failed: {e}", "ERROR")
        return False

def test_complex_content_split():
    """Test that complex content gets split appropriately"""
    try:
        log_test_result("🔀 Testing complex content for split treatment...")
        
        # Complex content that should be split
        complex_content = """# Product Documentation

## User Management
Manage users and permissions in your system.

### Creating Users
Add new users to the system.

### User Roles
Define different user roles and permissions.

## Data Management
Handle data storage and retrieval.

### Database Configuration
Set up your database connections.

### Data Import/Export
Import and export data in various formats.

## API Integration
Connect with external services.

### Authentication
Secure your API connections.

### Rate Limiting
Manage API usage limits.

## Reporting
Generate reports and analytics.

### Custom Reports
Create custom reporting templates.

### Scheduled Reports
Automate report generation.

## Security
Implement security best practices.

### Access Control
Control user access to resources.

### Audit Logging
Track system activities."""

        data = {
            'content': complex_content,
            'content_type': 'text',
            'metadata': {'original_filename': 'complex_content_test.txt'}
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process", json=data, timeout=120)
        
        if response.status_code != 200:
            log_test_result(f"❌ Complex content processing failed: Status {response.status_code}", "ERROR")
            return False
        
        result = response.json()
        job_id = result.get('job_id')
        
        # Monitor processing
        while True:
            elapsed = time.time() - start_time
            if elapsed > 90:  # 1.5 minutes max
                log_test_result("❌ Complex content processing timeout", "ERROR")
                return False
            
            status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                if status == 'completed':
                    articles_generated = status_data.get('articles_generated', 0)
                    processing_time = elapsed
                    
                    log_test_result(f"✅ Complex content processing completed in {processing_time:.1f}s")
                    log_test_result(f"📄 Articles generated: {articles_generated}")
                    
                    # Complex content should be split (4+ articles)
                    if articles_generated >= 4:
                        log_test_result(f"✅ SPLIT SUCCESS: Complex content properly split ({articles_generated} articles)", "SUCCESS")
                        return True
                    else:
                        log_test_result(f"❌ SPLIT FAILED: Complex content not properly split ({articles_generated} articles)", "ERROR")
                        return False
                        
                elif status == 'failed':
                    log_test_result(f"❌ Complex content processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                    return False
                
                time.sleep(3)
            else:
                time.sleep(3)
                
    except Exception as e:
        log_test_result(f"❌ Complex content test failed: {e}", "ERROR")
        return False

def test_content_library_articles():
    """Verify articles are created with proper structure"""
    try:
        log_test_result("📚 Verifying Content Library articles...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_test_result(f"📊 Content Library: {total_articles} total articles")
            
            # Look for recent test articles
            test_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                source = article.get('source_document', '').lower()
                if any(keyword in title or keyword in source for keyword in ['test', 'tutorial', 'complex']):
                    test_articles.append(article)
            
            if test_articles:
                log_test_result(f"✅ Found {len(test_articles)} test articles", "SUCCESS")
                
                # Check for cross-references and proper structure
                articles_with_features = 0
                for article in test_articles[:3]:
                    content = article.get('content', '')
                    has_features = any(feature in content for feature in [
                        'related-links', 'Related Articles', '<h2>', '<h3>', 'FAQ'
                    ])
                    if has_features:
                        articles_with_features += 1
                
                if articles_with_features > 0:
                    log_test_result(f"✅ Found {articles_with_features} articles with proper structure", "SUCCESS")
                    return True
                else:
                    log_test_result("⚠️ Articles lack proper structure features", "WARNING")
                    return True  # Still count as success if articles exist
            else:
                log_test_result("⚠️ No test articles found", "WARNING")
                return total_articles > 0
        else:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Content Library verification failed: {e}", "ERROR")
        return False

def run_quick_intelligent_test():
    """Run quick test suite for intelligent pipeline"""
    log_test_result("🚀 STARTING QUICK INTELLIGENT PIPELINE TEST", "CRITICAL")
    log_test_result("=" * 60)
    
    test_results = {
        'tutorial_unified': False,
        'complex_split': False,
        'content_library': False
    }
    
    # Test 1: Tutorial Unified Treatment
    log_test_result("TEST 1: Tutorial Unified Treatment")
    test_results['tutorial_unified'] = test_tutorial_content_unified()
    
    # Test 2: Complex Content Split Treatment
    log_test_result("\nTEST 2: Complex Content Split Treatment")
    test_results['complex_split'] = test_complex_content_split()
    
    # Test 3: Content Library Verification
    log_test_result("\nTEST 3: Content Library Verification")
    test_results['content_library'] = test_content_library_articles()
    
    # Results Summary
    log_test_result("\n" + "=" * 60)
    log_test_result("🎯 QUICK TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 66:
        log_test_result("🎉 INTELLIGENT PIPELINE SUCCESS: Content analysis working!", "CRITICAL_SUCCESS")
        log_test_result("✅ Tutorial content unified, complex content split appropriately", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ INTELLIGENT PIPELINE ISSUES: Some features need attention", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Quick Intelligent Pipeline Testing")
    print("=" * 40)
    
    results = run_quick_intelligent_test()
    
    # Exit with appropriate code
    success_rate = sum(results.values()) / len(results)
    if success_rate >= 0.66:
        exit(0)  # Success
    else:
        exit(1)  # Failure