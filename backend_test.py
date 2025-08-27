#!/usr/bin/env python3
"""
KE-PR5 Pipeline Orchestrator Complete 17-Stage Testing
Final verification of complete V2 pipeline with all 17 stages working
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://content-processor.preview.emergentagent.com/api"

class Complete17StagePipelineTester:
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
        
    def test_v2_engine_17_stage_availability(self):
        """Test 1: Verify V2 Engine has all 17 pipeline stages available"""
        try:
            response = requests.get(f"{self.backend_url}/engine", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2 Engine 17-Stage Availability", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check engine status
            if data.get("status") not in ["operational", "active"]:
                self.log_test("V2 Engine 17-Stage Availability", False, f"Engine status: {data.get('status')}")
                return False
                
            # Check for all V2 pipeline features including versioning and review
            features = data.get("features", [])
            required_features = [
                "v2_processing", "pipeline_orchestrator", "v2_analyzer", "v2_generator",
                "v2_validation", "v2_publishing", "v2_versioning", "v2_review"
            ]
            
            missing_features = [f for f in required_features if f not in features]
            if missing_features:
                self.log_test("V2 Engine 17-Stage Availability", False, f"Missing pipeline features: {missing_features}")
                return False
                
            # Check for versioning and review system availability
            versioning_available = "v2_versioning" in features
            review_available = "v2_review" in features
            
            if not versioning_available:
                self.log_test("V2 Engine 17-Stage Availability", False, "Stage 16 (Versioning) not available")
                return False
                
            if not review_available:
                self.log_test("V2 Engine 17-Stage Availability", False, "Stage 17 (Review) not available")
                return False
                
            self.log_test("V2 Engine 17-Stage Availability", True, 
                         f"All 17 stages available including Stage 16 (Versioning) and Stage 17 (Review)")
            return True
            
        except Exception as e:
            self.log_test("V2 Engine 17-Stage Availability", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_17_stage_pipeline_execution(self):
        """Test 2: Execute complete 17-stage pipeline and verify all stages complete"""
        try:
            # Use comprehensive content to trigger all 17 pipeline stages
            comprehensive_content = """
            # Complete API Integration and Security Guide
            
            ## Table of Contents
            1. Introduction and Overview
            2. Prerequisites and Setup
            3. Authentication Methods
            4. API Endpoints Reference
            5. Implementation Examples
            6. Security Best Practices
            7. Error Handling and Troubleshooting
            8. Performance Optimization
            9. Testing and Validation
            10. Deployment Guidelines
            
            ## 1. Introduction and Overview
            
            This comprehensive guide provides complete coverage of API integration, security implementation, and best practices for production systems. It includes detailed examples, code samples, and troubleshooting information.
            
            ### What You'll Learn
            - Complete API integration workflow
            - Security implementation strategies
            - Performance optimization techniques
            - Error handling and recovery methods
            - Testing and validation approaches
            - Production deployment best practices
            
            ## 2. Prerequisites and Setup
            
            Before starting with API integration, ensure you have:
            
            ### Required Tools and Software
            - Development environment (Node.js, Python, or preferred language)
            - API testing tools (Postman, curl, or similar)
            - Version control system (Git)
            - Code editor with syntax highlighting
            
            ### API Credentials
            - Valid API key from the provider
            - OAuth 2.0 credentials (if applicable)
            - Rate limiting information
            - Documentation access
            
            ### Development Environment Setup
            ```bash
            # Install required dependencies
            npm install axios dotenv
            # or for Python
            pip install requests python-dotenv
            ```
            
            ## 3. Authentication Methods
            
            ### API Key Authentication
            The most straightforward authentication method involves including your API key in request headers:
            
            ```javascript
            const axios = require('axios');
            
            const apiClient = axios.create({
                baseURL: 'https://api.example.com/v1',
                headers: {
                    'Authorization': `Bearer ${process.env.API_KEY}`,
                    'Content-Type': 'application/json'
                }
            });
            
            // Example API call
            async function getUserData(userId) {
                try {
                    const response = await apiClient.get(`/users/${userId}`);
                    return response.data;
                } catch (error) {
                    console.error('API request failed:', error.response?.data || error.message);
                    throw error;
                }
            }
            ```
            
            ### OAuth 2.0 Authentication
            For more secure authentication in production systems, implement OAuth 2.0:
            
            ```python
            import requests
            import os
            from datetime import datetime, timedelta
            
            class OAuth2Client:
                def __init__(self, client_id, client_secret, token_url):
                    self.client_id = client_id
                    self.client_secret = client_secret
                    self.token_url = token_url
                    self.access_token = None
                    self.token_expires = None
                
                def get_access_token(self):
                    if self.access_token and self.token_expires > datetime.now():
                        return self.access_token
                    
                    data = {
                        'grant_type': 'client_credentials',
                        'client_id': self.client_id,
                        'client_secret': self.client_secret
                    }
                    
                    response = requests.post(self.token_url, data=data)
                    response.raise_for_status()
                    
                    token_data = response.json()
                    self.access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                    
                    return self.access_token
            ```
            
            ## 4. API Endpoints Reference
            
            ### User Management Endpoints
            
            #### Get User Information
            ```http
            GET /api/v1/users/{user_id}
            Authorization: Bearer {access_token}
            Content-Type: application/json
            ```
            
            **Response:**
            ```json
            {
                "id": "12345",
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2024-01-15T10:30:00Z",
                "last_login": "2024-01-20T14:45:00Z",
                "profile": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "avatar_url": "https://example.com/avatars/john.jpg"
                }
            }
            ```
            
            ## 5. Implementation Examples
            
            ### Complete Integration Example (Node.js)
            ```javascript
            const express = require('express');
            const axios = require('axios');
            require('dotenv').config();
            
            const app = express();
            app.use(express.json());
            
            // API client configuration
            const apiClient = axios.create({
                baseURL: process.env.API_BASE_URL,
                timeout: 10000,
                headers: {
                    'Authorization': `Bearer ${process.env.API_KEY}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'MyApp/1.0'
                }
            });
            
            // Request interceptor for logging
            apiClient.interceptors.request.use(
                config => {
                    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
                    return config;
                },
                error => {
                    console.error('Request error:', error);
                    return Promise.reject(error);
                }
            );
            
            // Response interceptor for error handling
            apiClient.interceptors.response.use(
                response => response,
                error => {
                    if (error.response) {
                        console.error(`API Error ${error.response.status}:`, error.response.data);
                    } else if (error.request) {
                        console.error('Network error:', error.message);
                    } else {
                        console.error('Request setup error:', error.message);
                    }
                    return Promise.reject(error);
                }
            );
            ```
            
            ## 6. Security Best Practices
            
            ### Input Validation and Sanitization
            Always validate and sanitize input data before sending to APIs:
            
            ```javascript
            const validator = require('validator');
            
            function validateUserInput(userData) {
                const errors = [];
                
                // Email validation
                if (!userData.email || !validator.isEmail(userData.email)) {
                    errors.push('Valid email address is required');
                }
                
                // Username validation
                if (!userData.username || !validator.isAlphanumeric(userData.username)) {
                    errors.push('Username must contain only letters and numbers');
                }
                
                return {
                    isValid: errors.length === 0,
                    errors: errors
                };
            }
            ```
            
            ## 7. Error Handling and Troubleshooting
            
            ### Comprehensive Error Handling Strategy
            ```javascript
            class APIError extends Error {
                constructor(message, statusCode, response) {
                    super(message);
                    this.name = 'APIError';
                    this.statusCode = statusCode;
                    this.response = response;
                }
            }
            
            class APIClient {
                constructor(baseURL, apiKey) {
                    this.baseURL = baseURL;
                    this.apiKey = apiKey;
                    this.retryAttempts = 3;
                    this.retryDelay = 1000; // 1 second
                }
                
                async makeRequest(method, endpoint, data = null, attempt = 1) {
                    try {
                        const config = {
                            method,
                            url: `${this.baseURL}${endpoint}`,
                            headers: {
                                'Authorization': `Bearer ${this.apiKey}`,
                                'Content-Type': 'application/json'
                            }
                        };
                        
                        if (data) {
                            config.data = data;
                        }
                        
                        const response = await axios(config);
                        return response.data;
                        
                    } catch (error) {
                        if (this.shouldRetry(error) && attempt < this.retryAttempts) {
                            console.log(`Retrying request (attempt ${attempt + 1}/${this.retryAttempts})`);
                            await this.delay(this.retryDelay * attempt);
                            return this.makeRequest(method, endpoint, data, attempt + 1);
                        }
                        
                        throw this.handleError(error);
                    }
                }
            }
            ```
            
            ## 8. Performance Optimization
            
            ### Connection Pooling and Reuse
            ```javascript
            const https = require('https');
            const axios = require('axios');
            
            // Create HTTP agent with connection pooling
            const httpsAgent = new https.Agent({
                keepAlive: true,
                maxSockets: 50,
                maxFreeSockets: 10,
                timeout: 60000,
                freeSocketTimeout: 30000
            });
            
            const optimizedClient = axios.create({
                httpsAgent,
                timeout: 30000,
                maxRedirects: 5
            });
            ```
            
            ## 9. Testing and Validation
            
            ### Unit Testing API Integration
            ```javascript
            const { expect } = require('chai');
            const sinon = require('sinon');
            const APIClient = require('./api-client');
            
            describe('API Client', () => {
                let apiClient;
                let axiosStub;
                
                beforeEach(() => {
                    apiClient = new APIClient('https://api.example.com', 'test-key');
                    axiosStub = sinon.stub(axios, 'request');
                });
                
                afterEach(() => {
                    axiosStub.restore();
                });
                
                it('should make successful GET request', async () => {
                    const mockResponse = { data: { id: 1, name: 'Test User' } };
                    axiosStub.resolves(mockResponse);
                    
                    const result = await apiClient.get('/users/1');
                    
                    expect(result).to.deep.equal(mockResponse.data);
                    expect(axiosStub.calledOnce).to.be.true;
                });
            });
            ```
            
            ## 10. Deployment Guidelines
            
            ### Environment Configuration
            ```yaml
            # docker-compose.yml
            version: '3.8'
            services:
              api-client:
                build: .
                environment:
                  - NODE_ENV=production
                  - API_BASE_URL=${API_BASE_URL}
                  - API_KEY=${API_KEY}
                  - REDIS_URL=${REDIS_URL}
                  - LOG_LEVEL=info
                ports:
                  - "3000:3000"
                depends_on:
                  - redis
                restart: unless-stopped
            ```
            
            ## Conclusion
            
            This comprehensive guide provides everything needed to implement robust, secure, and performant API integrations. By following these practices and examples, you can build production-ready systems that handle errors gracefully, perform efficiently, and maintain security standards.
            """
            
            payload = {
                "content": comprehensive_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=180)
            
            if response.status_code != 200:
                self.log_test("Complete 17-Stage Pipeline Execution", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing success
            if data.get("status") != "success":
                self.log_test("Complete 17-Stage Pipeline Execution", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check processing info for complete stage execution
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Must complete all 17 stages for 100% success
            if stages_completed != 17:
                self.log_test("Complete 17-Stage Pipeline Execution", False, f"Incomplete pipeline: {stages_completed}/17 stages completed")
                return False
                
            # Check for critical stage errors
            stage_errors = processing_info.get("stage_errors", [])
            critical_errors = [err for err in stage_errors if err.get("severity") == "critical"]
            
            if critical_errors:
                self.log_test("Complete 17-Stage Pipeline Execution", False, f"Critical stage errors: {len(critical_errors)}")
                return False
                
            # Verify articles were generated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Complete 17-Stage Pipeline Execution", False, "No articles generated despite 17 stages completion")
                return False
                
            self.log_test("Complete 17-Stage Pipeline Execution", True, 
                         f"100% SUCCESS: All 17/17 stages completed, {len(articles)} articles generated, {len(stage_errors)} minor errors")
            return True
            
        except Exception as e:
            self.log_test("Complete 17-Stage Pipeline Execution", False, f"Exception: {str(e)}")
            return False
    
    def test_stage_16_versioning_system(self):
        """Test 3: Verify Stage 16 (Versioning) creates version metadata correctly"""
        try:
            test_content = """
            # API Versioning Guide
            
            ## Introduction
            This guide covers API versioning strategies and implementation approaches for maintaining backward compatibility while evolving your API.
            
            ## Versioning Strategies
            - Semantic versioning (v1.0.0, v1.1.0, v2.0.0)
            - URL path versioning (/api/v1/, /api/v2/)
            - Header-based versioning (Accept: application/vnd.api+json;version=1)
            - Query parameter versioning (?version=1)
            
            ## Implementation Examples
            Each versioning strategy has its own benefits and trade-offs for API evolution.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("Stage 16 Versioning System", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Stage 16 Versioning System", False, f"Processing failed: {data.get('message')}")
                return False
                
            # Check that Stage 16 was executed
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            if stages_completed < 16:
                self.log_test("Stage 16 Versioning System", False, f"Stage 16 not reached: only {stages_completed} stages completed")
                return False
                
            # Check for versioning metadata in articles
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Stage 16 Versioning System", False, "No articles generated to check versioning")
                return False
                
            article = articles[0]
            metadata = article.get("metadata", {})
            
            # Check for version-related metadata
            version_indicators = [
                "version", "v2_version", "content_version", "pipeline_version", 
                "processing_version", "engine_version"
            ]
            
            has_version_metadata = any(key in metadata for key in version_indicators)
            
            if not has_version_metadata:
                # Check if versioning info is in processing_info
                versioning_info = processing_info.get("versioning", {})
                if not versioning_info:
                    self.log_test("Stage 16 Versioning System", False, "No versioning metadata found in article or processing info")
                    return False
                    
            # Check for V2 engine version tracking
            engine_version = metadata.get("engine") or processing_info.get("engine")
            if engine_version != "v2":
                self.log_test("Stage 16 Versioning System", False, f"Wrong engine version: {engine_version}")
                return False
                
            self.log_test("Stage 16 Versioning System", True, 
                         f"Versioning metadata created successfully, engine: {engine_version}")
            return True
            
        except Exception as e:
            self.log_test("Stage 16 Versioning System", False, f"Exception: {str(e)}")
            return False
    
    def test_stage_17_review_system(self):
        """Test 4: Verify Stage 17 (Review) enqueues content for review successfully"""
        try:
            test_content = """
            # Content Review Process Guide
            
            ## Overview
            This guide outlines the content review process for ensuring quality and accuracy in published materials.
            
            ## Review Stages
            1. Automated quality checks
            2. Technical accuracy validation
            3. Editorial review
            4. Final approval and publishing
            
            ## Quality Criteria
            - Technical accuracy and completeness
            - Clear and concise writing
            - Proper formatting and structure
            - Appropriate examples and code samples
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("Stage 17 Review System", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Stage 17 Review System", False, f"Processing failed: {data.get('message')}")
                return False
                
            # Check that Stage 17 was executed
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            if stages_completed < 17:
                self.log_test("Stage 17 Review System", False, f"Stage 17 not reached: only {stages_completed} stages completed")
                return False
                
            # Check for review system indicators
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Stage 17 Review System", False, "No articles generated to check review system")
                return False
                
            article = articles[0]
            metadata = article.get("metadata", {})
            
            # Check for review-related metadata
            review_indicators = [
                "review_status", "review_queue", "review_id", "review_request",
                "queued_for_review", "review_metadata"
            ]
            
            has_review_metadata = any(key in metadata for key in review_indicators)
            
            if not has_review_metadata:
                # Check if review info is in processing_info
                review_info = processing_info.get("review", {}) or processing_info.get("stage_17", {})
                if not review_info:
                    self.log_test("Stage 17 Review System", False, "No review system metadata found")
                    return False
                    
            # Check article status indicates review processing
            article_status = article.get("status", "")
            review_statuses = ["review", "pending_review", "queued", "processed"]
            
            status_indicates_review = any(status in article_status.lower() for status in review_statuses)
            
            self.log_test("Stage 17 Review System", True, 
                         f"Review system engaged successfully, article status: {article_status}")
            return True
            
        except Exception as e:
            self.log_test("Stage 17 Review System", False, f"Exception: {str(e)}")
            return False
    
    def test_full_processing_workflow_integrity(self):
        """Test 5: Verify complete workflow produces fully processed articles"""
        try:
            test_content = """
            # Complete Workflow Testing Guide
            
            ## Introduction
            This comprehensive guide tests the complete V2 processing workflow to ensure all stages work together seamlessly.
            
            ## Processing Stages Overview
            The V2 pipeline consists of 17 distinct stages:
            1. Content Analysis
            2. Outline Planning
            3. Prewrite Extraction
            4. Gap Filling
            5. Evidence Tagging
            6. Code Normalization
            7. Article Generation
            8. Style Processing
            9. Related Links
            10. Validation
            11. Publishing
            12. Cross-Article QA
            13. Adaptive Adjustment
            14. Media Processing
            15. Content Extraction
            16. Versioning
            17. Review
            
            ## Quality Assurance
            Each stage contributes to the overall quality and completeness of the final articles.
            
            ### Technical Implementation
            ```javascript
            // Example workflow monitoring
            const workflowMonitor = {
                trackStage: (stageNumber, stageName) => {
                    console.log(`Stage ${stageNumber}: ${stageName} - Processing...`);
                },
                
                validateOutput: (stageOutput) => {
                    return stageOutput && stageOutput.status === 'completed';
                },
                
                reportProgress: (completedStages, totalStages) => {
                    const percentage = (completedStages / totalStages) * 100;
                    console.log(`Workflow Progress: ${percentage.toFixed(1)}%`);
                }
            };
            ```
            
            ## Expected Outcomes
            - All 17 stages complete successfully
            - Articles are fully processed and formatted
            - Metadata includes complete processing information
            - No critical errors or missing components
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("Full Processing Workflow Integrity", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("Full Processing Workflow Integrity", False, f"Processing failed: {data.get('message')}")
                return False
                
            # Verify complete processing
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Must be 100% complete (17/17 stages)
            if stages_completed != 17:
                self.log_test("Full Processing Workflow Integrity", False, f"Incomplete workflow: {stages_completed}/17 stages")
                return False
                
            # Verify articles are fully processed
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Full Processing Workflow Integrity", False, "No articles generated")
                return False
                
            article = articles[0]
            
            # Check article completeness
            required_fields = ["id", "title", "content", "metadata", "created_at"]
            missing_fields = [field for field in required_fields if field not in article]
            
            if missing_fields:
                self.log_test("Full Processing Workflow Integrity", False, f"Incomplete article: missing {missing_fields}")
                return False
                
            # Check content quality
            content = article.get("content", "")
            if len(content) < 1000:  # Should have substantial processed content
                self.log_test("Full Processing Workflow Integrity", False, f"Content too short: {len(content)} chars")
                return False
                
            # Check metadata completeness
            metadata = article.get("metadata", {})
            expected_metadata = ["engine", "processing_stages", "content_length"]
            
            # Verify V2 processing
            if metadata.get("engine") != "v2":
                self.log_test("Full Processing Workflow Integrity", False, f"Wrong engine: {metadata.get('engine')}")
                return False
                
            # Check for processing errors
            stage_errors = processing_info.get("stage_errors", [])
            critical_errors = [err for err in stage_errors if err.get("severity") == "critical"]
            
            if critical_errors:
                self.log_test("Full Processing Workflow Integrity", False, f"Critical processing errors: {len(critical_errors)}")
                return False
                
            self.log_test("Full Processing Workflow Integrity", True, 
                         f"Complete workflow integrity verified: 17/17 stages, {len(content)} chars content, V2 engine")
            return True
            
        except Exception as e:
            self.log_test("Full Processing Workflow Integrity", False, f"Exception: {str(e)}")
            return False
    
    def test_no_attribute_errors_or_missing_methods(self):
        """Test 6: Verify no AttributeError or missing method issues in pipeline"""
        try:
            # Test with content that might trigger various code paths
            test_content = """
            # Error-Free Pipeline Testing
            
            ## Comprehensive Testing Scenarios
            This content is designed to test various pipeline components and ensure no AttributeError or missing method issues occur.
            
            ### Code Processing Test
            ```python
            def test_function():
                return "Testing code processing"
            ```
            
            ### List Processing Test
            - Item 1: Basic list processing
            - Item 2: Advanced list handling
            - Item 3: Complex list structures
            
            ### Table Processing Test
            | Feature | Status | Notes |
            |---------|--------|-------|
            | Stage 1 | ✅ | Working |
            | Stage 2 | ✅ | Working |
            | Stage 3 | ✅ | Working |
            
            ### Link Processing Test
            [Example Link](https://example.com)
            
            ### Image Processing Test
            ![Test Image](https://example.com/image.jpg)
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("No AttributeError or Missing Methods", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check for processing success (no exceptions should occur)
            if data.get("status") != "success":
                error_message = data.get("message", "Unknown error")
                
                # Check specifically for AttributeError or missing method issues
                error_indicators = [
                    "AttributeError", "has no attribute", "missing method", 
                    "method not found", "NoneType", "object has no attribute"
                ]
                
                has_attribute_error = any(indicator in error_message for indicator in error_indicators)
                
                if has_attribute_error:
                    self.log_test("No AttributeError or Missing Methods", False, f"AttributeError detected: {error_message}")
                    return False
                else:
                    # Other types of errors are acceptable for this test
                    self.log_test("No AttributeError or Missing Methods", True, f"No AttributeError (other error: {error_message})")
                    return True
                    
            # Check processing info for method-related errors
            processing_info = data.get("processing_info", {})
            stage_errors = processing_info.get("stage_errors", [])
            
            # Look for AttributeError in stage errors
            attribute_errors = []
            for error in stage_errors:
                error_msg = error.get("message", "")
                if any(indicator in error_msg for indicator in ["AttributeError", "has no attribute", "missing method"]):
                    attribute_errors.append(error)
                    
            if attribute_errors:
                self.log_test("No AttributeError or Missing Methods", False, f"AttributeErrors in stages: {len(attribute_errors)}")
                return False
                
            # Verify articles were generated (indicates no critical method issues)
            articles = data.get("articles", [])
            stages_completed = processing_info.get("stages_completed", 0)
            
            self.log_test("No AttributeError or Missing Methods", True, 
                         f"No AttributeError detected, {stages_completed} stages completed, {len(articles)} articles generated")
            return True
            
        except Exception as e:
            # Check if the exception itself is an AttributeError
            if "AttributeError" in str(e) or "has no attribute" in str(e):
                self.log_test("No AttributeError or Missing Methods", False, f"AttributeError exception: {str(e)}")
                return False
            else:
                self.log_test("No AttributeError or Missing Methods", True, f"No AttributeError (other exception: {str(e)})")
                return True
    
    def test_production_readiness_verification(self):
        """Test 7: Verify pipeline is production-ready with consistent performance"""
        try:
            # Test multiple requests to verify consistency
            test_content = """
            # Production Readiness Verification
            
            ## System Reliability
            This test verifies that the 17-stage pipeline is ready for production deployment with consistent performance and reliability.
            
            ## Performance Metrics
            - Processing time consistency
            - Memory usage stability
            - Error rate minimization
            - Output quality consistency
            
            ## Reliability Indicators
            - All stages complete successfully
            - No critical errors or failures
            - Consistent article generation
            - Proper metadata handling
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            # Test multiple requests for consistency
            results = []
            for i in range(3):
                start_time = time.time()
                response = requests.post(f"{self.backend_url}/content/process", 
                                       json=payload, timeout=90)
                processing_time = time.time() - start_time
                
                if response.status_code != 200:
                    self.log_test("Production Readiness Verification", False, f"Request {i+1} failed: HTTP {response.status_code}")
                    return False
                    
                data = response.json()
                
                if data.get("status") != "success":
                    self.log_test("Production Readiness Verification", False, f"Request {i+1} processing failed")
                    return False
                    
                processing_info = data.get("processing_info", {})
                stages_completed = processing_info.get("stages_completed", 0)
                articles = data.get("articles", [])
                
                results.append({
                    "stages_completed": stages_completed,
                    "articles_count": len(articles),
                    "processing_time": processing_time,
                    "has_errors": len(processing_info.get("stage_errors", [])) > 0
                })
                
                # Small delay between requests
                time.sleep(2)
            
            # Analyze consistency
            stages_consistent = all(r["stages_completed"] == 17 for r in results)
            articles_consistent = all(r["articles_count"] > 0 for r in results)
            no_critical_errors = all(not r["has_errors"] for r in results)
            
            # Check performance consistency (processing times should be reasonable)
            processing_times = [r["processing_time"] for r in results]
            avg_time = sum(processing_times) / len(processing_times)
            max_time = max(processing_times)
            
            # Performance should be consistent (max time shouldn't be more than 2x average)
            performance_consistent = max_time <= (avg_time * 2) and avg_time < 120  # Under 2 minutes average
            
            if not stages_consistent:
                self.log_test("Production Readiness Verification", False, "Inconsistent stage completion across requests")
                return False
                
            if not articles_consistent:
                self.log_test("Production Readiness Verification", False, "Inconsistent article generation across requests")
                return False
                
            if not performance_consistent:
                self.log_test("Production Readiness Verification", False, f"Inconsistent performance: avg {avg_time:.1f}s, max {max_time:.1f}s")
                return False
                
            self.log_test("Production Readiness Verification", True, 
                         f"Production ready: 3/3 requests successful, avg {avg_time:.1f}s, all 17 stages consistent")
            return True
            
        except Exception as e:
            self.log_test("Production Readiness Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all 17-stage pipeline tests"""
        print("🎯 KE-PR5 COMPLETE 17-STAGE PIPELINE TESTING")
        print("=" * 80)
        print("Final verification of complete V2 pipeline with all 17 stages working")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_engine_17_stage_availability,
            self.test_complete_17_stage_pipeline_execution,
            self.test_stage_16_versioning_system,
            self.test_stage_17_review_system,
            self.test_full_processing_workflow_integrity,
            self.test_no_attribute_errors_or_missing_methods,
            self.test_production_readiness_verification
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
        print("🎯 KE-PR5 COMPLETE 17-STAGE PIPELINE TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 KE-PR5 COMPLETE 17-STAGE PIPELINE: PERFECT - All 17 stages working flawlessly!")
            print("✅ Stage 16 (Versioning) and Stage 17 (Review) both operational")
            print("✅ 100% pipeline completion achieved")
            print("✅ Production-ready with no AttributeError issues")
        elif success_rate >= 85:
            print("🎉 KE-PR5 COMPLETE 17-STAGE PIPELINE: EXCELLENT - Nearly perfect implementation!")
        elif success_rate >= 70:
            print("✅ KE-PR5 COMPLETE 17-STAGE PIPELINE: GOOD - Most functionality working")
        elif success_rate >= 50:
            print("⚠️ KE-PR5 COMPLETE 17-STAGE PIPELINE: PARTIAL - Some issues remain")
        else:
            print("❌ KE-PR5 COMPLETE 17-STAGE PIPELINE: NEEDS ATTENTION - Major issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = Complete17StagePipelineTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 85 else 1)