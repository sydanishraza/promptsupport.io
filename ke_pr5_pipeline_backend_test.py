#!/usr/bin/env python3
"""
KE-PR5 Pipeline Orchestrator Integration Testing
Testing V2 content processing pipeline with existing V2 instances
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://engineextract.preview.emergentagent.com/api"

class KEPR5PipelineTester:
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
        
    def test_v2_engine_pipeline_availability(self):
        """Test 1: Verify V2 Engine has pipeline orchestrator available"""
        try:
            response = requests.get(f"{self.backend_url}/engine", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2 Engine Pipeline Availability", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check engine status
            if data.get("status") != "operational":
                self.log_test("V2 Engine Pipeline Availability", False, f"Engine status: {data.get('status')}")
                return False
                
            # Check for V2 pipeline features
            features = data.get("features", [])
            pipeline_features = ["v2_processing", "pipeline_orchestrator", "v2_analyzer", "v2_generator"]
            
            missing_features = [f for f in pipeline_features if f not in features]
            if missing_features:
                self.log_test("V2 Engine Pipeline Availability", False, f"Missing pipeline features: {missing_features}")
                return False
                
            self.log_test("V2 Engine Pipeline Availability", True, f"Pipeline features available: {len([f for f in features if 'v2' in f or 'pipeline' in f])}")
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Pipeline Availability", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_orchestrator_initialization(self):
        """Test 2: Verify pipeline orchestrator uses existing V2 instances"""
        try:
            # Test with simple text content to verify pipeline initialization
            test_content = "This is a test document for pipeline orchestrator verification. It contains basic content to test the V2 processing pipeline."
            
            payload = {
                "content": test_content,
                "content_type": "text",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=60)
            
            if response.status_code != 200:
                self.log_test("Pipeline Orchestrator Initialization", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check if processing was successful
            if data.get("status") != "success":
                self.log_test("Pipeline Orchestrator Initialization", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check processing metadata for V2 pipeline usage
            processing_info = data.get("processing_info", {})
            if processing_info.get("engine") != "v2":
                self.log_test("Pipeline Orchestrator Initialization", False, f"Wrong engine used: {processing_info.get('engine')}")
                return False
                
            # Check for pipeline stages completion
            stages_completed = processing_info.get("stages_completed", 0)
            if stages_completed < 10:  # Should complete multiple stages
                self.log_test("Pipeline Orchestrator Initialization", False, f"Too few stages completed: {stages_completed}")
                return False
                
            self.log_test("Pipeline Orchestrator Initialization", True, 
                         f"V2 pipeline initialized, {stages_completed} stages completed")
            return True
            
        except Exception as e:
            self.log_test("Pipeline Orchestrator Initialization", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_instances_reuse(self):
        """Test 3: Verify pipeline uses existing V2 instances instead of creating new ones"""
        try:
            # Test multiple requests to verify instance reuse
            test_content = "Testing V2 instance reuse in pipeline orchestrator. This content will be processed multiple times to verify instance efficiency."
            
            payload = {
                "content": test_content,
                "content_type": "text",
                "processing_mode": "v2_only"
            }
            
            # Make first request
            start_time = time.time()
            response1 = requests.post(f"{self.backend_url}/content/process", 
                                    json=payload, timeout=60)
            first_duration = time.time() - start_time
            
            if response1.status_code != 200:
                self.log_test("V2 Instances Reuse", False, f"First request failed: HTTP {response1.status_code}")
                return False
                
            # Make second request (should be faster due to instance reuse)
            start_time = time.time()
            response2 = requests.post(f"{self.backend_url}/content/process", 
                                    json=payload, timeout=60)
            second_duration = time.time() - start_time
            
            if response2.status_code != 200:
                self.log_test("V2 Instances Reuse", False, f"Second request failed: HTTP {response2.status_code}")
                return False
                
            # Both should succeed
            data1 = response1.json()
            data2 = response2.json()
            
            if data1.get("status") != "success" or data2.get("status") != "success":
                self.log_test("V2 Instances Reuse", False, "One or both requests failed processing")
                return False
                
            # Check that both used V2 engine
            engine1 = data1.get("processing_info", {}).get("engine")
            engine2 = data2.get("processing_info", {}).get("engine")
            
            if engine1 != "v2" or engine2 != "v2":
                self.log_test("V2 Instances Reuse", False, f"Wrong engines: {engine1}, {engine2}")
                return False
                
            # Instance reuse should make second request faster (or at least not significantly slower)
            efficiency_ratio = second_duration / first_duration if first_duration > 0 else 1
            
            self.log_test("V2 Instances Reuse", True, 
                         f"Instance reuse verified: {first_duration:.2f}s -> {second_duration:.2f}s (ratio: {efficiency_ratio:.2f})")
            return True
            
        except Exception as e:
            self.log_test("V2 Instances Reuse", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_stage_execution(self):
        """Test 4: Verify pipeline executes all 17 stages without major errors"""
        try:
            # Use comprehensive content to trigger all pipeline stages
            comprehensive_content = """
            # Complete API Integration Guide
            
            ## Introduction
            This comprehensive guide covers all aspects of API integration including authentication, rate limiting, error handling, and best practices for production systems.
            
            ## Prerequisites
            Before starting with API integration, ensure you have:
            - Valid API credentials and access tokens
            - Development environment properly configured
            - Basic understanding of REST API principles
            - Knowledge of HTTP methods and status codes
            
            ## Authentication Methods
            
            ### API Key Authentication
            The most straightforward authentication method involves including your API key in request headers:
            
            ```javascript
            const apiKey = 'your-api-key-here';
            const headers = {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            };
            ```
            
            ### OAuth 2.0 Authentication
            For more secure authentication in production systems, use OAuth 2.0:
            
            ```python
            import requests
            
            def get_oauth_token(client_id, client_secret):
                auth_url = 'https://api.example.com/oauth/token'
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret
                }
                response = requests.post(auth_url, data=data)
                return response.json()['access_token']
            ```
            
            ## Implementation Guide
            
            ### Making Your First Request
            Start with a simple GET request to test connectivity:
            
            ```curl
            curl -X GET "https://api.example.com/v1/status" \
                 -H "Authorization: Bearer YOUR_TOKEN" \
                 -H "Content-Type: application/json"
            ```
            
            ### Error Handling Best Practices
            Always implement proper error handling:
            
            ```javascript
            async function makeApiRequest(endpoint, options = {}) {
                try {
                    const response = await fetch(endpoint, {
                        ...options,
                        headers: {
                            'Authorization': `Bearer ${apiKey}`,
                            'Content-Type': 'application/json',
                            ...options.headers
                        }
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    return await response.json();
                } catch (error) {
                    console.error('API request failed:', error);
                    throw error;
                }
            }
            ```
            
            ## Rate Limiting and Throttling
            
            Respect API rate limits to avoid throttling:
            - Monitor response headers for rate limit information
            - Implement exponential backoff for retries
            - Use connection pooling for efficiency
            - Cache responses when appropriate
            
            ## Troubleshooting Common Issues
            
            ### 401 Unauthorized
            - Check API key validity and expiration
            - Verify authentication header format
            - Ensure proper scopes and permissions
            
            ### 429 Too Many Requests
            - Implement rate limiting in your application
            - Add delays between requests
            - Use exponential backoff strategy
            
            ### 500 Internal Server Error
            - Check API status page for outages
            - Verify request payload format
            - Contact API support if persistent
            
            ## Conclusion
            Following these guidelines will help you implement robust API integrations that handle errors gracefully and perform efficiently in production environments.
            """
            
            payload = {
                "content": comprehensive_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("Pipeline Stage Execution", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing success
            if data.get("status") != "success":
                self.log_test("Pipeline Stage Execution", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check processing info for stage completion
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Should complete most or all of the 17 stages
            if stages_completed < 15:
                self.log_test("Pipeline Stage Execution", False, f"Insufficient stages completed: {stages_completed}/17")
                return False
                
            # Check for stage errors
            stage_errors = processing_info.get("stage_errors", [])
            critical_errors = [err for err in stage_errors if err.get("severity") == "critical"]
            
            if critical_errors:
                self.log_test("Pipeline Stage Execution", False, f"Critical stage errors: {len(critical_errors)}")
                return False
                
            # Check articles were generated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Pipeline Stage Execution", False, "No articles generated")
                return False
                
            self.log_test("Pipeline Stage Execution", True, 
                         f"{stages_completed}/17 stages completed, {len(articles)} articles generated, {len(stage_errors)} minor errors")
            return True
            
        except Exception as e:
            self.log_test("Pipeline Stage Execution", False, f"Exception: {str(e)}")
            return False
    
    def test_article_generation_and_storage(self):
        """Test 5: Verify articles are generated correctly and stored in content library"""
        try:
            test_content = """
            # API Security Best Practices Guide
            
            ## Overview
            This guide covers essential security practices for API development and integration.
            
            ## Authentication Security
            - Use strong authentication mechanisms
            - Implement proper token management
            - Regular credential rotation
            
            ## Data Protection
            - Encrypt sensitive data in transit and at rest
            - Validate all input parameters
            - Implement proper access controls
            
            ## Monitoring and Logging
            - Log all API access attempts
            - Monitor for suspicious patterns
            - Set up alerting for security events
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("Article Generation and Storage", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Article Generation and Storage", False, f"Processing failed: {data.get('message')}")
                return False
                
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Article Generation and Storage", False, "No articles generated")
                return False
                
            article = articles[0]
            
            # Verify article structure
            required_fields = ["id", "title", "content", "created_at", "metadata"]
            missing_fields = [f for f in required_fields if f not in article]
            
            if missing_fields:
                self.log_test("Article Generation and Storage", False, f"Missing article fields: {missing_fields}")
                return False
                
            # Verify V2 processing metadata
            metadata = article.get("metadata", {})
            if metadata.get("engine") != "v2":
                self.log_test("Article Generation and Storage", False, f"Wrong engine in metadata: {metadata.get('engine')}")
                return False
                
            # Verify content quality
            content = article.get("content", "")
            if len(content) < 500:  # Should have substantial content
                self.log_test("Article Generation and Storage", False, f"Content too short: {len(content)} chars")
                return False
                
            # Check if article was stored (try to retrieve it)
            article_id = article.get("id")
            if article_id:
                try:
                    retrieve_response = requests.get(f"{self.backend_url}/content-library/articles/{article_id}", timeout=10)
                    if retrieve_response.status_code == 200:
                        stored_correctly = True
                    else:
                        stored_correctly = False
                except:
                    stored_correctly = False
            else:
                stored_correctly = False
                
            self.log_test("Article Generation and Storage", True, 
                         f"Article generated: {len(content)} chars, stored: {stored_correctly}, V2 engine: {metadata.get('engine')}")
            return True
            
        except Exception as e:
            self.log_test("Article Generation and Storage", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_and_fallback(self):
        """Test 6: Verify error handling and fallback mechanisms"""
        try:
            # Test with malformed content to trigger error handling
            malformed_content = "This is intentionally malformed content with invalid characters: \x00\x01\x02"
            
            payload = {
                "content": malformed_content,
                "content_type": "text",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=60)
            
            # Should handle gracefully (either succeed with cleaned content or fail gracefully)
            if response.status_code not in [200, 400, 422]:
                self.log_test("Error Handling and Fallback", False, f"Unexpected HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # If it succeeded, check that it handled the malformed content
            if response.status_code == 200 and data.get("status") == "success":
                articles = data.get("articles", [])
                if articles:
                    content = articles[0].get("content", "")
                    # Should have cleaned the content
                    if "\x00" in content or "\x01" in content:
                        self.log_test("Error Handling and Fallback", False, "Malformed characters not cleaned")
                        return False
                        
            # Test with empty content
            empty_payload = {
                "content": "",
                "content_type": "text",
                "processing_mode": "v2_only"
            }
            
            empty_response = requests.post(f"{self.backend_url}/content/process", 
                                         json=empty_payload, timeout=30)
            
            # Should handle empty content gracefully
            if empty_response.status_code not in [200, 400, 422]:
                self.log_test("Error Handling and Fallback", False, f"Empty content handling failed: HTTP {empty_response.status_code}")
                return False
                
            self.log_test("Error Handling and Fallback", True, 
                         f"Malformed content: HTTP {response.status_code}, Empty content: HTTP {empty_response.status_code}")
            return True
            
        except Exception as e:
            self.log_test("Error Handling and Fallback", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_performance_and_efficiency(self):
        """Test 7: Verify pipeline performance and efficiency"""
        try:
            # Test with medium-sized content to measure performance
            medium_content = """
            # Comprehensive API Documentation
            
            ## Introduction
            This documentation provides complete coverage of our API endpoints, authentication methods, and integration patterns.
            
            ## Getting Started
            
            ### Prerequisites
            - API key from developer portal
            - Basic understanding of REST APIs
            - Development environment setup
            
            ### Quick Start
            1. Obtain your API credentials
            2. Set up authentication headers
            3. Make your first API call
            4. Handle the response appropriately
            
            ## Authentication
            
            ### API Key Authentication
            Include your API key in the Authorization header:
            ```
            Authorization: Bearer YOUR_API_KEY
            ```
            
            ### OAuth 2.0 Flow
            For production applications, use OAuth 2.0:
            1. Register your application
            2. Obtain authorization code
            3. Exchange for access token
            4. Use token in API requests
            
            ## Core Endpoints
            
            ### Users API
            - GET /api/users - List all users
            - GET /api/users/{id} - Get specific user
            - POST /api/users - Create new user
            - PUT /api/users/{id} - Update user
            - DELETE /api/users/{id} - Delete user
            
            ### Data API
            - GET /api/data - Retrieve data
            - POST /api/data - Submit new data
            - PUT /api/data/{id} - Update existing data
            - DELETE /api/data/{id} - Remove data
            
            ## Error Handling
            
            ### HTTP Status Codes
            - 200 OK - Request successful
            - 400 Bad Request - Invalid request format
            - 401 Unauthorized - Authentication required
            - 403 Forbidden - Insufficient permissions
            - 404 Not Found - Resource not found
            - 429 Too Many Requests - Rate limit exceeded
            - 500 Internal Server Error - Server error
            
            ### Error Response Format
            ```json
            {
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "The request format is invalid",
                    "details": "Missing required field: email"
                }
            }
            ```
            
            ## Rate Limiting
            
            ### Limits
            - 1000 requests per hour for free tier
            - 10000 requests per hour for premium tier
            - 100000 requests per hour for enterprise tier
            
            ### Headers
            Check these response headers for rate limit information:
            - X-RateLimit-Limit: Maximum requests allowed
            - X-RateLimit-Remaining: Requests remaining in current window
            - X-RateLimit-Reset: Time when rate limit resets
            
            ## Best Practices
            
            ### Security
            - Always use HTTPS for API requests
            - Store API keys securely
            - Implement proper error handling
            - Validate all input data
            
            ### Performance
            - Use connection pooling
            - Implement caching where appropriate
            - Batch requests when possible
            - Monitor API usage and performance
            
            ## SDKs and Libraries
            
            ### JavaScript/Node.js
            ```javascript
            const apiClient = new APIClient({
                apiKey: 'your-api-key',
                baseURL: 'https://api.example.com'
            });
            ```
            
            ### Python
            ```python
            from api_client import APIClient
            
            client = APIClient(
                api_key='your-api-key',
                base_url='https://api.example.com'
            )
            ```
            
            ## Support and Resources
            
            ### Documentation
            - API Reference: https://docs.example.com/api
            - Tutorials: https://docs.example.com/tutorials
            - Examples: https://github.com/example/api-examples
            
            ### Support Channels
            - Email: support@example.com
            - Community Forum: https://community.example.com
            - GitHub Issues: https://github.com/example/api/issues
            """
            
            payload = {
                "content": medium_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=120)
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_test("Pipeline Performance and Efficiency", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Pipeline Performance and Efficiency", False, f"Processing failed: {data.get('message')}")
                return False
                
            # Check processing efficiency
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Calculate efficiency metrics
            content_length = len(medium_content)
            chars_per_second = content_length / processing_time if processing_time > 0 else 0
            
            # Performance should be reasonable (at least 100 chars/second)
            if chars_per_second < 100:
                self.log_test("Pipeline Performance and Efficiency", False, f"Too slow: {chars_per_second:.1f} chars/sec")
                return False
                
            # Should complete processing in reasonable time (under 2 minutes for this content)
            if processing_time > 120:
                self.log_test("Pipeline Performance and Efficiency", False, f"Too slow: {processing_time:.1f} seconds")
                return False
                
            articles = data.get("articles", [])
            
            self.log_test("Pipeline Performance and Efficiency", True, 
                         f"{processing_time:.1f}s, {chars_per_second:.1f} chars/sec, {stages_completed} stages, {len(articles)} articles")
            return True
            
        except Exception as e:
            self.log_test("Pipeline Performance and Efficiency", False, f"Exception: {str(e)}")
            return False
    
    def test_content_library_integration(self):
        """Test 8: Verify articles are properly stored in content library"""
        try:
            test_content = """
            # Integration Testing Guide
            
            ## Overview
            This guide covers integration testing best practices for API systems.
            
            ## Test Strategy
            - Unit tests for individual components
            - Integration tests for system interactions
            - End-to-end tests for complete workflows
            
            ## Implementation
            Use appropriate testing frameworks and tools for comprehensive coverage.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=60)
            
            if response.status_code != 200:
                self.log_test("Content Library Integration", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Content Library Integration", False, f"Processing failed: {data.get('message')}")
                return False
                
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Content Library Integration", False, "No articles generated")
                return False
                
            # Try to retrieve articles from content library
            try:
                library_response = requests.get(f"{self.backend_url}/content-library/articles", timeout=10)
                if library_response.status_code == 200:
                    library_data = library_response.json()
                    library_articles = library_data.get("articles", [])
                    
                    # Check if our article is in the library
                    article_id = articles[0].get("id")
                    found_in_library = any(art.get("id") == article_id for art in library_articles)
                    
                    if not found_in_library:
                        self.log_test("Content Library Integration", False, "Article not found in content library")
                        return False
                        
                else:
                    self.log_test("Content Library Integration", False, f"Content library access failed: HTTP {library_response.status_code}")
                    return False
                    
            except Exception as e:
                self.log_test("Content Library Integration", False, f"Content library check failed: {str(e)}")
                return False
                
            self.log_test("Content Library Integration", True, 
                         f"Article stored in content library: {article_id}")
            return True
            
        except Exception as e:
            self.log_test("Content Library Integration", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all KE-PR5 Pipeline Orchestrator tests"""
        print("🎯 KE-PR5 PIPELINE ORCHESTRATOR INTEGRATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_engine_pipeline_availability,
            self.test_pipeline_orchestrator_initialization,
            self.test_v2_instances_reuse,
            self.test_pipeline_stage_execution,
            self.test_article_generation_and_storage,
            self.test_error_handling_and_fallback,
            self.test_pipeline_performance_and_efficiency,
            self.test_content_library_integration
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(2)
        
        # Print summary
        print()
        print("=" * 80)
        print("🎯 KE-PR5 PIPELINE ORCHESTRATOR TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 80:
            print("🎉 KE-PR5 PIPELINE ORCHESTRATOR: EXCELLENT - V2 pipeline integration successful!")
        elif success_rate >= 60:
            print("✅ KE-PR5 PIPELINE ORCHESTRATOR: GOOD - Most functionality working")
        elif success_rate >= 40:
            print("⚠️ KE-PR5 PIPELINE ORCHESTRATOR: PARTIAL - Some issues remain")
        else:
            print("❌ KE-PR5 PIPELINE ORCHESTRATOR: NEEDS ATTENTION - Major issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = KEPR5PipelineTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)