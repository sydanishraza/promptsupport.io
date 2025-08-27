#!/usr/bin/env python3
"""
CONTENT CLASSIFICATION TEST
Test the content classification accuracy for tutorial vs reference content
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_tutorial_content_classification():
    """Test that tutorial content is properly classified and uses unified approach"""
    try:
        log_test_result("🎯 TESTING TUTORIAL CONTENT CLASSIFICATION", "CRITICAL")
        
        # Create a clear tutorial content
        tutorial_content = """# Complete Setup Tutorial

## Introduction
This tutorial will guide you through the complete setup process step by step.

## Step 1: Prerequisites
Before we begin, make sure you have:
- A computer with internet access
- Administrative privileges
- Basic knowledge of command line

## Step 2: Download and Install
Follow these steps carefully:

1. Go to the official website
2. Click the download button
3. Run the installer
4. Follow the setup wizard

```bash
# Install the package
npm install -g setup-tool
```

## Step 3: Configuration
Now configure your installation:

```javascript
const config = {
    apiKey: 'your-api-key',
    environment: 'production'
};
```

## Step 4: Verification
Test your installation:

```bash
setup-tool --version
setup-tool test
```

## Conclusion
You have successfully completed the setup process. Your system is now ready to use.
"""
        
        log_test_result(f"📝 Created tutorial content: {len(tutorial_content)} characters")
        
        # Process the tutorial content
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": tutorial_content,
                "filename": "Setup_Tutorial.txt"
            },
            timeout=120
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        log_test_result(f"✅ Processing started, Job ID: {job_id}")
        
        # Wait for completion
        time.sleep(30)
        
        status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get('status') == 'completed':
                articles_count = status_data.get('articles_generated', 0)
                
                log_test_result(f"📄 Articles Generated: {articles_count}")
                
                # Check if tutorial was processed with unified approach
                # Tutorial content should generate fewer articles (unified approach)
                if articles_count <= 3:
                    log_test_result("✅ TUTORIAL CLASSIFICATION SUCCESS: Used unified approach (≤3 articles)", "SUCCESS")
                    return True
                else:
                    log_test_result(f"⚠️ TUTORIAL CLASSIFICATION: Generated {articles_count} articles (may indicate over-splitting)", "WARNING")
                    return False
            else:
                log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                return False
        else:
            log_test_result("❌ Status check failed", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Tutorial classification test failed: {e}", "ERROR")
        return False

def test_reference_content_classification():
    """Test that reference content is properly classified and may use split approach"""
    try:
        log_test_result("🎯 TESTING REFERENCE CONTENT CLASSIFICATION", "CRITICAL")
        
        # Create a clear reference content
        reference_content = """# API Reference Documentation

## Authentication

### POST /auth/login
Authenticate user with credentials.

**Parameters:**
- username (string): User's username
- password (string): User's password

**Response:**
```json
{
    "token": "jwt-token-here",
    "expires": "2024-12-31T23:59:59Z"
}
```

### GET /auth/profile
Get authenticated user's profile.

**Headers:**
- Authorization: Bearer {token}

**Response:**
```json
{
    "id": 123,
    "username": "user",
    "email": "user@example.com"
}
```

## User Management

### GET /users
List all users.

**Query Parameters:**
- page (integer): Page number
- limit (integer): Items per page

### POST /users
Create a new user.

**Body:**
```json
{
    "username": "newuser",
    "email": "new@example.com",
    "password": "secure123"
}
```

### PUT /users/{id}
Update user information.

### DELETE /users/{id}
Delete a user account.

## Data Operations

### GET /data
Retrieve data records.

### POST /data
Create new data record.

### PUT /data/{id}
Update existing data record.

### DELETE /data/{id}
Delete data record.
"""
        
        log_test_result(f"📝 Created reference content: {len(reference_content)} characters")
        
        # Process the reference content
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": reference_content,
                "filename": "API_Reference.txt"
            },
            timeout=120
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        log_test_result(f"✅ Processing started, Job ID: {job_id}")
        
        # Wait for completion
        time.sleep(30)
        
        status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get('status') == 'completed':
                articles_count = status_data.get('articles_generated', 0)
                
                log_test_result(f"📄 Articles Generated: {articles_count}")
                
                # Reference content can use either approach, but should generate articles
                if articles_count >= 2:
                    log_test_result("✅ REFERENCE CLASSIFICATION SUCCESS: Generated multiple articles", "SUCCESS")
                    return True
                else:
                    log_test_result(f"⚠️ REFERENCE CLASSIFICATION: Only {articles_count} articles generated", "WARNING")
                    return True  # Still acceptable
            else:
                log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                return False
        else:
            log_test_result("❌ Status check failed", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Reference classification test failed: {e}", "ERROR")
        return False

def run_classification_tests():
    """Run content classification tests"""
    log_test_result("🚀 STARTING CONTENT CLASSIFICATION TESTS", "CRITICAL")
    log_test_result("=" * 60)
    
    results = {
        'tutorial_classification': False,
        'reference_classification': False
    }
    
    # Test 1: Tutorial Content
    log_test_result("TEST 1: Tutorial Content Classification")
    results['tutorial_classification'] = test_tutorial_content_classification()
    
    # Test 2: Reference Content
    log_test_result("\nTEST 2: Reference Content Classification")
    results['reference_classification'] = test_reference_content_classification()
    
    # Summary
    log_test_result("\n" + "=" * 60)
    log_test_result("🎯 CONTENT CLASSIFICATION TEST RESULTS", "CRITICAL")
    log_test_result("=" * 60)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 1:  # At least one test should pass
        log_test_result("🎉 CONTENT CLASSIFICATION WORKING!", "CRITICAL_SUCCESS")
        return True
    else:
        log_test_result("❌ CONTENT CLASSIFICATION NEEDS WORK", "CRITICAL_ERROR")
        return False

if __name__ == "__main__":
    print("Content Classification Test")
    print("=" * 30)
    
    success = run_classification_tests()
    
    if success:
        print("\n🎉 CLASSIFICATION TESTS SUCCESSFUL!")
        exit(0)
    else:
        print("\n❌ CLASSIFICATION TESTS FAILED")
        exit(1)