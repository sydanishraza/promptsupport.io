#!/usr/bin/env python3
"""
KE-PR5 Pipeline Orchestrator Versioning Fix Testing
Testing V2 content processing pipeline after implementing create_version_from_articles method
Focus: Verify Stage 16 (Versioning) now works and pipeline completes all 17 stages
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://happy-buck.preview.emergentagent.com/api"

class KEPR5VersioningFixTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
            
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_v2_engine_versioning_availability(self):
        """Test 1: Verify V2 Engine has versioning system available"""
        try:
            response = requests.get(f"{self.backend_url}/engine", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2 Engine Versioning Availability", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check engine status
            if data.get("status") != "operational":
                self.log_test("V2 Engine Versioning Availability", False, f"Engine status: {data.get('status')}")
                return False
                
            # Check for versioning features
            features = data.get("features", [])
            versioning_features = ["v2_versioning", "version_management", "content_versioning"]
            
            found_versioning_features = [f for f in versioning_features if f in features]
            if not found_versioning_features:
                self.log_test("V2 Engine Versioning Availability", False, f"No versioning features found in {len(features)} features")
                return False
                
            self.log_test("V2 Engine Versioning Availability", True, f"Versioning features available: {found_versioning_features}")
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Versioning Availability", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_pipeline_17_stages(self):
        """Test 2: Verify pipeline completes all 17 stages including Stage 16 (Versioning)"""
        try:
            # Use comprehensive content to trigger all pipeline stages
            comprehensive_content = """
            # Complete API Integration Guide with Versioning Test
            
            ## Introduction
            This comprehensive guide covers all aspects of API integration including authentication, rate limiting, error handling, and best practices for production systems. This content is designed to test the complete V2 pipeline including the new versioning system.
            
            ## Prerequisites and Setup
            Before starting with API integration, ensure you have:
            - Valid API credentials and access tokens
            - Development environment properly configured
            - Basic understanding of REST API principles
            - Knowledge of HTTP methods and status codes
            - Testing tools like Postman or curl
            
            ## Authentication Methods
            
            ### API Key Authentication
            The most straightforward authentication method involves including your API key in request headers:
            
            ```javascript
            const apiKey = 'your-api-key-here';
            const headers = {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            };
            
            fetch('https://api.example.com/v1/data', {
                method: 'GET',
                headers: headers
            })
            .then(response => response.json())
            .then(data => console.log(data));
            ```
            
            ### OAuth 2.0 Authentication
            For more secure authentication in production systems, use OAuth 2.0:
            
            ```python
            import requests
            import json
            
            def get_oauth_token(client_id, client_secret):
                auth_url = 'https://api.example.com/oauth/token'
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'scope': 'read write'
                }
                
                response = requests.post(auth_url, data=data)
                if response.status_code == 200:
                    return response.json()['access_token']
                else:
                    raise Exception(f"Authentication failed: {response.status_code}")
            ```
            
            ## Implementation Guide
            
            ### Making Your First Request
            Start with a simple GET request to test connectivity:
            
            ```curl
            curl -X GET "https://api.example.com/v1/status" \
                 -H "Authorization: Bearer YOUR_TOKEN" \
                 -H "Content-Type: application/json" \
                 -H "User-Agent: MyApp/1.0"
            ```
            
            ### Error Handling Best Practices
            Always implement proper error handling for robust applications:
            
            ```javascript
            async function makeApiRequest(endpoint, options = {}) {
                const maxRetries = 3;
                let retryCount = 0;
                
                while (retryCount < maxRetries) {
                    try {
                        const response = await fetch(endpoint, {
                            ...options,
                            headers: {
                                'Authorization': `Bearer ${apiKey}`,
                                'Content-Type': 'application/json',
                                'Retry-Count': retryCount.toString(),
                                ...options.headers
                            }
                        });
                        
                        if (!response.ok) {
                            if (response.status === 429) {
                                // Rate limited - wait and retry
                                const retryAfter = response.headers.get('Retry-After') || 60;
                                await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
                                retryCount++;
                                continue;
                            }
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        
                        return await response.json();
                    } catch (error) {
                        console.error(`API request failed (attempt ${retryCount + 1}):`, error);
                        retryCount++;
                        if (retryCount >= maxRetries) {
                            throw error;
                        }
                        // Exponential backoff
                        await new Promise(resolve => setTimeout(resolve, Math.pow(2, retryCount) * 1000));
                    }
                }
            }
            ```
            
            ## Rate Limiting and Throttling
            
            ### Understanding Rate Limits
            Most APIs implement rate limiting to prevent abuse:
            - Monitor response headers for rate limit information
            - Implement exponential backoff for retries
            - Use connection pooling for efficiency
            - Cache responses when appropriate
            - Respect the API's fair use policy
            
            ### Implementation Strategy
            ```python
            import time
            import random
            from functools import wraps
            
            def rate_limited(max_calls_per_second=10):
                min_interval = 1.0 / max_calls_per_second
                last_called = [0.0]
                
                def decorator(func):
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        elapsed = time.time() - last_called[0]
                        left_to_wait = min_interval - elapsed
                        if left_to_wait > 0:
                            time.sleep(left_to_wait)
                        ret = func(*args, **kwargs)
                        last_called[0] = time.time()
                        return ret
                    return wrapper
                return decorator
            
            @rate_limited(max_calls_per_second=5)
            def api_call(endpoint, data=None):
                # Your API call implementation
                pass
            ```
            
            ## Troubleshooting Common Issues
            
            ### 401 Unauthorized Errors
            - Check API key validity and expiration
            - Verify authentication header format
            - Ensure proper scopes and permissions
            - Check for clock skew in timestamp-based auth
            
            ### 429 Too Many Requests
            - Implement rate limiting in your application
            - Add delays between requests
            - Use exponential backoff strategy
            - Consider request queuing
            
            ### 500 Internal Server Error
            - Check API status page for outages
            - Verify request payload format
            - Contact API support if persistent
            - Implement circuit breaker pattern
            
            ## Advanced Topics
            
            ### Webhook Integration
            For real-time updates, implement webhook endpoints:
            
            ```python
            from flask import Flask, request, jsonify
            import hmac
            import hashlib
            
            app = Flask(__name__)
            
            @app.route('/webhook', methods=['POST'])
            def handle_webhook():
                # Verify webhook signature
                signature = request.headers.get('X-Signature')
                payload = request.get_data()
                
                expected_signature = hmac.new(
                    webhook_secret.encode(),
                    payload,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected_signature):
                    return jsonify({'error': 'Invalid signature'}), 401
                
                # Process webhook data
                data = request.get_json()
                process_webhook_event(data)
                
                return jsonify({'status': 'success'}), 200
            ```
            
            ## Conclusion
            Following these guidelines will help you implement robust API integrations that handle errors gracefully and perform efficiently in production environments. Remember to always test thoroughly and monitor your API usage.
            """
            
            payload = {
                "content": comprehensive_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            print(f"🚀 Testing complete V2 pipeline with {len(comprehensive_content)} characters of content...")
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=180)
            
            if response.status_code != 200:
                self.log_test("Complete Pipeline 17 Stages", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing success
            if data.get("status") != "success":
                self.log_test("Complete Pipeline 17 Stages", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check processing info for stage completion
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Should complete all 17 stages now
            if stages_completed < 17:
                self.log_test("Complete Pipeline 17 Stages", False, f"Incomplete stages: {stages_completed}/17")
                return False
                
            # Check for critical stage errors
            stage_errors = processing_info.get("stage_errors", [])
            critical_errors = [err for err in stage_errors if err.get("severity") == "critical"]
            
            if critical_errors:
                self.log_test("Complete Pipeline 17 Stages", False, f"Critical stage errors: {len(critical_errors)}")
                return False
                
            # Check articles were generated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Complete Pipeline 17 Stages", False, "No articles generated")
                return False
                
            self.log_test("Complete Pipeline 17 Stages", True, 
                         f"All {stages_completed}/17 stages completed, {len(articles)} articles generated, {len(stage_errors)} minor errors")
            return True
            
        except Exception as e:
            self.log_test("Complete Pipeline 17 Stages", False, f"Exception: {str(e)}")
            return False
    
    def test_stage_16_versioning_success(self):
        """Test 3: Specifically verify Stage 16 (Versioning) completes successfully"""
        try:
            # Use content specifically designed to test versioning
            versioning_test_content = """
            # Versioning System Test Document
            
            ## Overview
            This document is designed to test the V2 pipeline versioning system (Stage 16) to ensure the create_version_from_articles method works correctly.
            
            ## Content for Version Testing
            
            ### Section 1: Basic Content
            This section contains basic content that should be processed through all pipeline stages including versioning.
            
            ### Section 2: Code Examples
            ```python
            def test_versioning():
                version_id = generate_version_id()
                return version_id
            ```
            
            ### Section 3: Lists and Structure
            - Item 1: First test item
            - Item 2: Second test item  
            - Item 3: Third test item
            
            ## Conclusion
            This content should successfully complete all 17 pipeline stages including the new versioning system.
            """
            
            payload = {
                "content": versioning_test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            print(f"🔍 Testing Stage 16 (Versioning) specifically...")
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("Stage 16 Versioning Success", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Stage 16 Versioning Success", False, f"Processing failed: {data.get('message')}")
                return False
                
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Must complete at least through Stage 16
            if stages_completed < 16:
                self.log_test("Stage 16 Versioning Success", False, f"Stage 16 not reached: {stages_completed}/17")
                return False
                
            # Check for versioning-specific errors
            stage_errors = processing_info.get("stage_errors", [])
            versioning_errors = [err for err in stage_errors if "versioning" in err.get("stage", "").lower() or "stage 16" in err.get("message", "").lower()]
            
            if versioning_errors:
                self.log_test("Stage 16 Versioning Success", False, f"Versioning errors: {versioning_errors}")
                return False
                
            # Check that articles were generated (indicates versioning didn't block completion)
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Stage 16 Versioning Success", False, "No articles generated - versioning may have failed")
                return False
                
            self.log_test("Stage 16 Versioning Success", True, 
                         f"Stage 16 (Versioning) completed successfully, {len(articles)} articles generated")
            return True
            
        except Exception as e:
            self.log_test("Stage 16 Versioning Success", False, f"Exception: {str(e)}")
            return False
    
    def test_version_metadata_generation(self):
        """Test 4: Verify version metadata is properly generated"""
        try:
            test_content = """
            # Version Metadata Test
            
            ## Content for Metadata Testing
            This content tests whether version metadata is properly generated by the versioning system.
            
            ### Features to Test
            - Version ID generation
            - Content hash calculation
            - Article count tracking
            - Timestamp creation
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("Version Metadata Generation", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Version Metadata Generation", False, f"Processing failed: {data.get('message')}")
                return False
                
            # Check if version metadata is present in processing info
            processing_info = data.get("processing_info", {})
            
            # Look for version-related information
            has_version_info = False
            version_details = ""
            
            if "version" in str(processing_info).lower():
                has_version_info = True
                version_details = "Version info found in processing_info"
            
            # Check articles for version metadata
            articles = data.get("articles", [])
            if articles:
                article = articles[0]
                metadata = article.get("metadata", {})
                
                if any(key in metadata for key in ["version", "version_id", "content_hash"]):
                    has_version_info = True
                    version_details += f", Version metadata in article: {list(metadata.keys())}"
            
            if not has_version_info:
                self.log_test("Version Metadata Generation", False, "No version metadata found")
                return False
                
            self.log_test("Version Metadata Generation", True, version_details)
            return True
            
        except Exception as e:
            self.log_test("Version Metadata Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_success_rate_improvement(self):
        """Test 5: Verify pipeline success rate is higher than previous 80%"""
        try:
            # Test multiple content types to verify consistent high success rate
            test_contents = [
                {
                    "name": "Technical Guide",
                    "content": """
                    # API Integration Technical Guide
                    
                    ## Setup Instructions
                    Follow these steps to integrate with our API system.
                    
                    ### Authentication
                    Use Bearer token authentication for all requests.
                    
                    ### Rate Limits
                    Respect the 1000 requests per hour limit.
                    """
                },
                {
                    "name": "Code Tutorial", 
                    "content": """
                    # JavaScript API Client Tutorial
                    
                    ## Installation
                    ```bash
                    npm install api-client
                    ```
                    
                    ## Usage
                    ```javascript
                    const client = new APIClient('your-token');
                    const data = await client.getData();
                    ```
                    """
                },
                {
                    "name": "Troubleshooting Guide",
                    "content": """
                    # API Troubleshooting Guide
                    
                    ## Common Issues
                    
                    ### 401 Errors
                    Check your authentication token.
                    
                    ### 429 Errors  
                    You've exceeded the rate limit.
                    
                    ### 500 Errors
                    Server-side issue - contact support.
                    """
                }
            ]
            
            successful_tests = 0
            total_tests = len(test_contents)
            
            for i, test_case in enumerate(test_contents):
                print(f"📊 Testing success rate {i+1}/{total_tests}: {test_case['name']}")
                
                payload = {
                    "content": test_case["content"],
                    "content_type": "markdown", 
                    "processing_mode": "v2_only"
                }
                
                try:
                    response = requests.post(f"{self.backend_url}/content/process", 
                                           json=payload, timeout=90)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "success":
                            processing_info = data.get("processing_info", {})
                            stages_completed = processing_info.get("stages_completed", 0)
                            
                            # Consider successful if completes 15+ stages (allowing for minor issues)
                            if stages_completed >= 15:
                                successful_tests += 1
                                print(f"  ✅ {test_case['name']}: {stages_completed} stages completed")
                            else:
                                print(f"  ❌ {test_case['name']}: Only {stages_completed} stages completed")
                        else:
                            print(f"  ❌ {test_case['name']}: Processing failed")
                    else:
                        print(f"  ❌ {test_case['name']}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ {test_case['name']}: Exception {e}")
                
                # Small delay between tests
                time.sleep(3)
            
            success_rate = (successful_tests / total_tests) * 100
            
            # Should be higher than the previous 80% rate
            if success_rate <= 80:
                self.log_test("Pipeline Success Rate Improvement", False, f"Success rate {success_rate:.1f}% not improved from 80%")
                return False
                
            self.log_test("Pipeline Success Rate Improvement", True, 
                         f"Success rate: {success_rate:.1f}% ({successful_tests}/{total_tests}) - improved from 80%")
            return True
            
        except Exception as e:
            self.log_test("Pipeline Success Rate Improvement", False, f"Exception: {str(e)}")
            return False
    
    def test_no_fallback_to_original_implementation(self):
        """Test 6: Verify pipeline uses V2 implementation and doesn't fall back"""
        try:
            test_content = """
            # V2 Implementation Verification Test
            
            ## Purpose
            This test verifies that the pipeline uses the V2 implementation exclusively and doesn't fall back to the original implementation.
            
            ## Test Content
            This content should be processed entirely through the V2 pipeline including all 17 stages.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("No Fallback to Original Implementation", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("No Fallback to Original Implementation", False, f"Processing failed: {data.get('message')}")
                return False
                
            # Check that V2 engine was used
            processing_info = data.get("processing_info", {})
            engine_used = processing_info.get("engine")
            
            if engine_used != "v2":
                self.log_test("No Fallback to Original Implementation", False, f"Wrong engine used: {engine_used}")
                return False
                
            # Check for any fallback indicators
            processing_message = str(processing_info).lower()
            fallback_indicators = ["fallback", "original", "v1", "legacy"]
            
            found_fallback = any(indicator in processing_message for indicator in fallback_indicators)
            if found_fallback:
                self.log_test("No Fallback to Original Implementation", False, "Fallback indicators found in processing")
                return False
                
            # Verify high stage completion (indicates V2 pipeline working)
            stages_completed = processing_info.get("stages_completed", 0)
            if stages_completed < 15:
                self.log_test("No Fallback to Original Implementation", False, f"Low stage completion suggests fallback: {stages_completed}")
                return False
                
            self.log_test("No Fallback to Original Implementation", True, 
                         f"V2 engine used exclusively, {stages_completed} stages completed")
            return True
            
        except Exception as e:
            self.log_test("No Fallback to Original Implementation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all KE-PR5 Versioning Fix tests"""
        print("🎯 KE-PR5 PIPELINE ORCHESTRATOR VERSIONING FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print(f"Focus: Verify Stage 16 (Versioning) now works with create_version_from_articles method")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_engine_versioning_availability,
            self.test_complete_pipeline_17_stages,
            self.test_stage_16_versioning_success,
            self.test_version_metadata_generation,
            self.test_pipeline_success_rate_improvement,
            self.test_no_fallback_to_original_implementation
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(3)
        
        # Print summary
        print()
        print("=" * 80)
        print("🎯 KE-PR5 VERSIONING FIX TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 90:
            print("🎉 KE-PR5 VERSIONING FIX: EXCELLENT - All 17 stages now complete successfully!")
        elif success_rate >= 80:
            print("✅ KE-PR5 VERSIONING FIX: GOOD - Major improvement achieved")
        elif success_rate >= 60:
            print("⚠️ KE-PR5 VERSIONING FIX: PARTIAL - Some issues remain")
        else:
            print("❌ KE-PR5 VERSIONING FIX: NEEDS ATTENTION - Major issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = KEPR5VersioningFixTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 90 else 1)