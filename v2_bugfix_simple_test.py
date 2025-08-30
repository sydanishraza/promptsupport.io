#!/usr/bin/env python3
"""
CRITICAL BUG FIX VALIDATION: V2 Pipeline Processing Issues
Simple test to validate the V2 pipeline bug fixes
"""

import requests
import time
import json
from datetime import datetime

BACKEND_URL = "https://knowledge-engine-6.preview.emergentagent.com"

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_v2_pipeline_fixes():
    """Test the V2 pipeline bug fixes"""
    log("🚀 Starting V2 Pipeline Bug Fix Validation")
    
    # Test 1: Health check and V2-only configuration
    log("🔍 Testing system health and V2-only configuration...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=30)
        if response.status_code == 200:
            health_data = response.json()
            v2_config = health_data.get("ke_pr10_5", {})
            force_v2_only = v2_config.get("force_v2_only", False)
            legacy_behavior = v2_config.get("legacy_endpoint_behavior", "")
            
            if force_v2_only and legacy_behavior == "block":
                log("✅ V2-only configuration: PASSED")
            else:
                log(f"❌ V2-only configuration: FAILED - force_v2_only={force_v2_only}, legacy_behavior={legacy_behavior}")
                return False
        else:
            log(f"❌ Health check: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Health check: FAILED - {str(e)}")
        return False
    
    # Test 2: Content processing with V2 pipeline
    log("🔍 Testing V2 content processing...")
    try:
        test_content = """# V2 Pipeline Test
        
This is a test to validate the V2 pipeline bug fixes including:
- ContentBlock interface fixes
- NormalizedDocument job_id fixes  
- V2ArticleGenerator storage fixes
- End-to-end V2 processing

## Test Section
This section should be processed by the V2 engine without errors.
"""
        
        response = requests.post(
            f"{BACKEND_URL}/api/content/process",
            data={"content": test_content, "content_type": "text"},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "")
            engine = result.get("engine", "")
            job_id = result.get("job_id", "")
            
            if status == "completed" and engine == "v2" and job_id:
                log(f"✅ V2 content processing: PASSED - Status: {status}, Engine: {engine}, Job ID: {job_id}")
            else:
                log(f"❌ V2 content processing: FAILED - Status: {status}, Engine: {engine}, Job ID: {job_id}")
                return False
        else:
            log(f"❌ V2 content processing: FAILED - Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log(f"❌ V2 content processing: FAILED - {str(e)}")
        return False
    
    # Test 3: Article generation validation
    log("🔍 Testing article generation...")
    try:
        # Get initial article count
        response = requests.get(f"{BACKEND_URL}/api/content-library", timeout=30)
        if response.status_code == 200:
            initial_data = response.json()
            initial_count = len(initial_data.get("articles", []))
            log(f"Initial article count: {initial_count}")
            
            # Process content that should generate articles
            substantial_content = """# Comprehensive Guide to API Development
            
## Introduction
API development is a crucial skill for modern software developers. This guide covers the essential concepts and best practices.

## Getting Started
Before diving into API development, you need to understand the fundamentals of HTTP protocols and RESTful design principles.

### HTTP Methods
- GET: Retrieve data
- POST: Create new resources
- PUT: Update existing resources
- DELETE: Remove resources

## Authentication and Security
Proper authentication is essential for API security. Common methods include:
- API Keys
- OAuth 2.0
- JWT Tokens

## Best Practices
Follow these best practices for robust API development:
1. Use consistent naming conventions
2. Implement proper error handling
3. Provide comprehensive documentation
4. Version your APIs appropriately

## Conclusion
Building well-designed APIs requires careful planning and adherence to established patterns and practices.
"""
            
            response = requests.post(
                f"{BACKEND_URL}/api/content/process",
                data={"content": substantial_content, "content_type": "text"},
                timeout=150
            )
            
            if response.status_code == 200:
                result = response.json()
                log(f"Processing completed: {result.get('status', 'unknown')}")
                
                # Wait for articles to be stored
                time.sleep(10)
                
                # Check final article count
                response = requests.get(f"{BACKEND_URL}/api/content-library", timeout=30)
                if response.status_code == 200:
                    final_data = response.json()
                    final_count = len(final_data.get("articles", []))
                    articles_generated = final_count - initial_count
                    
                    log(f"Final article count: {final_count}, Articles generated: {articles_generated}")
                    
                    if articles_generated > 0:
                        log("✅ Article generation: PASSED - Articles successfully generated")
                    else:
                        log("❌ Article generation: FAILED - No articles generated")
                        return False
                else:
                    log(f"❌ Article generation check: FAILED - Status {response.status_code}")
                    return False
            else:
                log(f"❌ Article generation processing: FAILED - Status {response.status_code}")
                return False
        else:
            log(f"❌ Initial article count check: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Article generation test: FAILED - {str(e)}")
        return False
    
    # Test 4: System stability
    log("🔍 Testing system stability...")
    try:
        # Make multiple requests to test stability
        success_count = 0
        total_requests = 5
        
        for i in range(total_requests):
            response = requests.get(f"{BACKEND_URL}/api/health", timeout=15)
            if response.status_code == 200:
                success_count += 1
            time.sleep(1)
        
        success_rate = (success_count / total_requests) * 100
        
        if success_rate >= 80:
            log(f"✅ System stability: PASSED - {success_rate:.1f}% success rate")
        else:
            log(f"❌ System stability: FAILED - {success_rate:.1f}% success rate")
            return False
    except Exception as e:
        log(f"❌ System stability test: FAILED - {str(e)}")
        return False
    
    log("🎉 V2 Pipeline Bug Fix Validation: ALL TESTS PASSED")
    return True

if __name__ == "__main__":
    success = test_v2_pipeline_fixes()
    exit(0 if success else 1)
