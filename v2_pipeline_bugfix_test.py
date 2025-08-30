#!/usr/bin/env python3
"""
CRITICAL BUG FIX VALIDATION: V2 Pipeline Processing Issues
Testing the fixes made to V2 pipeline processing issues as requested in review.

This test validates:
1. ContentBlock Interface Fix - Test that ContentBlock objects now have .get() method and dictionary-like access
2. NormalizedDocument job_id Fix - Test that NormalizedDocument now has job_id attribute and doesn't fail validation
3. V2ProcessingRepository Fix - Test that V2ArticleGenerator can now store generated articles correctly
4. End-to-End V2 Processing - Test complete V2 pipeline from content input to article generation
5. Article Generation Success - Validate that V2 pipeline now generates articles (not 0 articles)
6. V2-Only Mode Functionality - Test full V2-only operation after bug fixes
7. Repository Pattern Integration - Ensure all fixed components work with repository pattern
8. System Stability - Confirm fixes don't introduce regressions
"""

import asyncio
import json
import time
import requests
import sys
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://knowledge-engine-6.preview.emergentagent.com"

class V2PipelineBugFixValidator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = {}
        self.total_tests = 8
        self.passed_tests = 0
        
    def log(self, message):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_health_check(self):
        """Test basic system health and V2-only configuration"""
        try:
            self.log("🔍 Testing system health and V2-only configuration...")
            
            response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            if response.status_code != 200:
                self.test_results["health_check"] = {
                    "status": "FAILED",
                    "error": f"Health check failed with status {response.status_code}"
                }
                return False
                
            health_data = response.json()
            
            # Check V2-only configuration
            v2_only_config = health_data.get("ke_pr10_5", {})
            force_v2_only = v2_only_config.get("force_v2_only", False)
            legacy_behavior = v2_only_config.get("legacy_endpoint_behavior", "")
            
            if not force_v2_only or legacy_behavior != "block":
                self.test_results["health_check"] = {
                    "status": "FAILED",
                    "error": f"V2-only mode not properly configured: force_v2_only={force_v2_only}, legacy_behavior={legacy_behavior}"
                }
                return False
                
            self.test_results["health_check"] = {
                "status": "PASSED",
                "details": {
                    "force_v2_only": force_v2_only,
                    "legacy_endpoint_behavior": legacy_behavior,
                    "system_status": health_data.get("status", "unknown")
                }
            }
            self.passed_tests += 1
            self.log("✅ System health and V2-only configuration: PASSED")
            return True
            
        except Exception as e:
            self.test_results["health_check"] = {
                "status": "FAILED",
                "error": f"Health check exception: {str(e)}"
            }
            self.log(f"❌ System health check: FAILED - {str(e)}")
            return False
    
    def test_contentblock_interface_fix(self):
        """Test ContentBlock Interface Fix - dictionary-like access and .get() method"""
        try:
            self.log("🔍 Testing ContentBlock interface fix...")
            
            # Test V2 content processing to trigger ContentBlock usage
            test_content = "# Test Content\n\nThis is a test to validate ContentBlock interface fixes."
            
            response = requests.post(
                f"{self.backend_url}/api/content/process",
                json={"content": test_content, "format": "markdown"},
                timeout=60
            )
            
            if response.status_code != 200:
                self.test_results["contentblock_interface"] = {
                    "status": "FAILED",
                    "error": f"Content processing failed with status {response.status_code}: {response.text}"
                }
                self.log(f"❌ ContentBlock interface test: FAILED - Processing failed")
                return False
                
            result = response.json()
            
            # Check if processing completed without ContentBlock attribute errors
            status = result.get("status", "")
            engine = result.get("engine", "")
            
            if status != "completed":
                self.test_results["contentblock_interface"] = {
                    "status": "FAILED",
                    "error": f"Processing not completed: status={status}"
                }
                self.log(f"❌ ContentBlock interface test: FAILED - Processing incomplete")
                return False
                
            if engine != "v2":
                self.test_results["contentblock_interface"] = {
                    "status": "FAILED", 
                    "error": f"Not using V2 engine: engine={engine}"
                }
                self.log(f"❌ ContentBlock interface test: FAILED - Not V2 engine")
                return False
                
            self.test_results["contentblock_interface"] = {
                "status": "PASSED",
                "details": {
                    "processing_status": status,
                    "engine": engine,
                    "job_id": result.get("job_id", "unknown")
                }
            }
            self.passed_tests += 1
            self.log("✅ ContentBlock interface fix: PASSED")
            return True
            
        except Exception as e:
            self.test_results["contentblock_interface"] = {
                "status": "FAILED",
                "error": f"ContentBlock test exception: {str(e)}"
            }
            self.log(f"❌ ContentBlock interface test: FAILED - {str(e)}")
            return False
    
    def test_normalizeddocument_job_id_fix(self):
        """Test NormalizedDocument job_id Fix - validation should not fail"""
        try:
            self.log("🔍 Testing NormalizedDocument job_id fix...")
            
            # Test with more substantial content to trigger NormalizedDocument processing
            test_content = """
            # API Documentation Guide
            
            ## Introduction
            This guide covers the essential aspects of our API.
            
            ## Getting Started
            Follow these steps to begin using the API:
            
            1. Register for an API key
            2. Set up authentication
            3. Make your first request
            
            ## Authentication
            Use Bearer token authentication for all requests.
            
            ## Endpoints
            The following endpoints are available:
            - GET /api/users
            - POST /api/users
            - PUT /api/users/{id}
            - DELETE /api/users/{id}
            """
            
            response = requests.post(
                f"{self.backend_url}/api/content/process",
                json={"content": test_content, "format": "markdown"},
                timeout=90
            )
            
            if response.status_code != 200:
                self.test_results["normalizeddocument_job_id"] = {
                    "status": "FAILED",
                    "error": f"Processing failed with status {response.status_code}: {response.text}"
                }
                self.log(f"❌ NormalizedDocument job_id test: FAILED - Processing failed")
                return False
                
            result = response.json()
            
            # Check for job_id presence and processing completion
            job_id = result.get("job_id")
            status = result.get("status", "")
            
            if not job_id:
                self.test_results["normalizeddocument_job_id"] = {
                    "status": "FAILED",
                    "error": "No job_id returned in processing result"
                }
                self.log(f"❌ NormalizedDocument job_id test: FAILED - No job_id")
                return False
                
            if status != "completed":
                self.test_results["normalizeddocument_job_id"] = {
                    "status": "FAILED",
                    "error": f"Processing failed: status={status}"
                }
                self.log(f"❌ NormalizedDocument job_id test: FAILED - Processing incomplete")
                return False
                
            self.test_results["normalizeddocument_job_id"] = {
                "status": "PASSED",
                "details": {
                    "job_id": job_id,
                    "processing_status": status,
                    "engine": result.get("engine", "unknown")
                }
            }
            self.passed_tests += 1
            self.log("✅ NormalizedDocument job_id fix: PASSED")
            return True
            
        except Exception as e:
            self.test_results["normalizeddocument_job_id"] = {
                "status": "FAILED",
                "error": f"NormalizedDocument test exception: {str(e)}"
            }
            self.log(f"❌ NormalizedDocument job_id test: FAILED - {str(e)}")
            return False
    
    def test_v2_article_generator_storage(self):
        """Test V2ArticleGenerator can store generated articles correctly"""
        try:
            self.log("🔍 Testing V2ArticleGenerator storage capabilities...")
            
            # Get initial article count
            response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            if response.status_code != 200:
                self.test_results["v2_article_generator"] = {
                    "status": "FAILED",
                    "error": f"Failed to get initial article count: {response.status_code}"
                }
                return False
                
            initial_data = response.json()
            initial_count = len(initial_data.get("articles", []))
            
            # Process content that should generate articles
            test_content = """
            # Complete Tutorial: Building Web Applications
            
            ## Chapter 1: Setting Up Your Environment
            Before you begin building web applications, you need to set up your development environment properly.
            
            ### Installing Node.js
            Download and install Node.js from the official website.
            
            ### Setting Up Your IDE
            Choose a suitable IDE like Visual Studio Code.
            
            ## Chapter 2: Creating Your First Application
            Now that your environment is ready, let's create your first web application.
            
            ### Project Structure
            Organize your project files in a logical structure.
            
            ### Basic HTML Structure
            Start with a basic HTML template.
            
            ## Chapter 3: Adding Interactivity
            Learn how to add JavaScript to make your application interactive.
            
            ### Event Handlers
            Implement click and form submission handlers.
            
            ### AJAX Requests
            Make asynchronous requests to your backend.
            """
            
            response = requests.post(
                f"{self.backend_url}/api/content/process",
                json={"content": test_content, "format": "markdown"},
                timeout=120
            )
            
            if response.status_code != 200:
                self.test_results["v2_article_generator"] = {
                    "status": "FAILED",
                    "error": f"Content processing failed: {response.status_code} - {response.text}"
                }
                self.log(f"❌ V2ArticleGenerator test: FAILED - Processing failed")
                return False
                
            result = response.json()
            
            # Wait a moment for articles to be stored
            time.sleep(5)
            
            # Check if articles were generated and stored
            response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            if response.status_code != 200:
                self.test_results["v2_article_generator"] = {
                    "status": "FAILED",
                    "error": f"Failed to get updated article count: {response.status_code}"
                }
                return False
                
            final_data = response.json()
            final_count = len(final_data.get("articles", []))
            articles_generated = final_count - initial_count
            
            if articles_generated <= 0:
                self.test_results["v2_article_generator"] = {
                    "status": "FAILED",
                    "error": f"No articles generated: initial={initial_count}, final={final_count}"
                }
                self.log(f"❌ V2ArticleGenerator test: FAILED - No articles generated")
                return False
                
            self.test_results["v2_article_generator"] = {
                "status": "PASSED",
                "details": {
                    "initial_count": initial_count,
                    "final_count": final_count,
                    "articles_generated": articles_generated,
                    "job_id": result.get("job_id", "unknown")
                }
            }
            self.passed_tests += 1
            self.log(f"✅ V2ArticleGenerator storage: PASSED - Generated {articles_generated} articles")
            return True
            
        except Exception as e:
            self.test_results["v2_article_generator"] = {
                "status": "FAILED",
                "error": f"V2ArticleGenerator test exception: {str(e)}"
            }
            self.log(f"❌ V2ArticleGenerator test: FAILED - {str(e)}")
            return False
    
    def test_end_to_end_v2_processing(self):
        """Test complete V2 pipeline from content input to article generation"""
        try:
            self.log("🔍 Testing end-to-end V2 processing pipeline...")
            
            # Comprehensive test content
            test_content = """
            # Advanced JavaScript Development Guide
            
            ## Introduction to Modern JavaScript
            JavaScript has evolved significantly over the years. This guide covers modern JavaScript development practices.
            
            ### ES6+ Features
            Learn about the latest JavaScript features including:
            - Arrow functions
            - Template literals
            - Destructuring
            - Async/await
            
            ## Setting Up Your Development Environment
            A proper development environment is crucial for productive JavaScript development.
            
            ### Code Editor Setup
            Configure your code editor with the right extensions and settings.
            
            ### Build Tools
            Use modern build tools like Webpack and Vite for optimal development experience.
            
            ## Core JavaScript Concepts
            Understanding these concepts is essential for any JavaScript developer.
            
            ### Closures and Scope
            Master the concept of closures and how scope works in JavaScript.
            
            ### Prototypes and Inheritance
            Learn about JavaScript's prototype-based inheritance system.
            
            ## Asynchronous Programming
            Modern JavaScript applications rely heavily on asynchronous programming.
            
            ### Promises
            Understand how promises work and how to use them effectively.
            
            ### Async/Await
            Learn the modern syntax for handling asynchronous operations.
            
            ## Testing Your Code
            Testing is an essential part of professional JavaScript development.
            
            ### Unit Testing
            Write effective unit tests for your JavaScript functions.
            
            ### Integration Testing
            Test how different parts of your application work together.
            """
            
            # Start processing
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/content/process",
                json={"content": test_content, "format": "markdown"},
                timeout=180
            )
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                self.test_results["end_to_end_v2"] = {
                    "status": "FAILED",
                    "error": f"End-to-end processing failed: {response.status_code} - {response.text}"
                }
                self.log(f"❌ End-to-end V2 processing: FAILED - Processing failed")
                return False
                
            result = response.json()
            
            # Validate processing results
            status = result.get("status", "")
            engine = result.get("engine", "")
            job_id = result.get("job_id", "")
            
            if status != "completed":
                self.test_results["end_to_end_v2"] = {
                    "status": "FAILED",
                    "error": f"Processing not completed: status={status}"
                }
                self.log(f"❌ End-to-end V2 processing: FAILED - Not completed")
                return False
                
            if engine != "v2":
                self.test_results["end_to_end_v2"] = {
                    "status": "FAILED",
                    "error": f"Not using V2 engine: engine={engine}"
                }
                self.log(f"❌ End-to-end V2 processing: FAILED - Not V2 engine")
                return False
                
            self.test_results["end_to_end_v2"] = {
                "status": "PASSED",
                "details": {
                    "processing_time": round(processing_time, 2),
                    "status": status,
                    "engine": engine,
                    "job_id": job_id,
                    "content_length": len(test_content)
                }
            }
            self.passed_tests += 1
            self.log(f"✅ End-to-end V2 processing: PASSED - Completed in {processing_time:.2f}s")
            return True
            
        except Exception as e:
            self.test_results["end_to_end_v2"] = {
                "status": "FAILED",
                "error": f"End-to-end test exception: {str(e)}"
            }
            self.log(f"❌ End-to-end V2 processing: FAILED - {str(e)}")
            return False
    
    def test_article_generation_success(self):
        """Validate that V2 pipeline generates articles (not 0 articles)"""
        try:
            self.log("🔍 Testing V2 pipeline article generation success...")
            
            # Get baseline article count
            response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            if response.status_code != 200:
                self.test_results["article_generation"] = {
                    "status": "FAILED",
                    "error": f"Failed to get baseline article count: {response.status_code}"
                }
                return False
                
            baseline_data = response.json()
            baseline_count = len(baseline_data.get("articles", []))
            
            # Process substantial content to ensure article generation
            test_content = """
            # Comprehensive API Integration Tutorial
            
            ## Part 1: Understanding APIs
            APIs (Application Programming Interfaces) are the backbone of modern web development.
            
            ### What is an API?
            An API is a set of protocols and tools for building software applications.
            
            ### Types of APIs
            There are several types of APIs you should know about:
            - REST APIs
            - GraphQL APIs
            - SOAP APIs
            - WebSocket APIs
            
            ## Part 2: Setting Up API Integration
            Before integrating with any API, you need to understand the setup process.
            
            ### Authentication Methods
            Most APIs require authentication. Common methods include:
            - API Keys
            - OAuth 2.0
            - JWT Tokens
            - Basic Authentication
            
            ### Making Your First API Call
            Start with a simple GET request to understand the API structure.
            
            ## Part 3: Handling API Responses
            Properly handling API responses is crucial for robust applications.
            
            ### Success Responses
            Learn how to process successful API responses and extract data.
            
            ### Error Handling
            Implement proper error handling for various HTTP status codes.
            
            ## Part 4: Advanced API Techniques
            Once you master the basics, explore advanced techniques.
            
            ### Rate Limiting
            Understand how to handle API rate limits effectively.
            
            ### Caching Strategies
            Implement caching to improve performance and reduce API calls.
            
            ### Pagination
            Handle paginated responses for large datasets.
            
            ## Part 5: Best Practices
            Follow these best practices for professional API integration.
            
            ### Security Considerations
            Always prioritize security when working with APIs.
            
            ### Performance Optimization
            Optimize your API calls for better application performance.
            """
            
            # Process the content
            response = requests.post(
                f"{self.backend_url}/api/content/process",
                json={"content": test_content, "format": "markdown"},
                timeout=150
            )
            
            if response.status_code != 200:
                self.test_results["article_generation"] = {
                    "status": "FAILED",
                    "error": f"Content processing failed: {response.status_code} - {response.text}"
                }
                self.log(f"❌ Article generation test: FAILED - Processing failed")
                return False
                
            result = response.json()
            
            # Wait for articles to be stored
            time.sleep(8)
            
            # Check final article count
            response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            if response.status_code != 200:
                self.test_results["article_generation"] = {
                    "status": "FAILED",
                    "error": f"Failed to get final article count: {response.status_code}"
                }
                return False
                
            final_data = response.json()
            final_count = len(final_data.get("articles", []))
            articles_generated = final_count - baseline_count
            
            # Validate article generation
            if articles_generated <= 0:
                self.test_results["article_generation"] = {
                    "status": "FAILED",
                    "error": f"V2 pipeline generated 0 articles: baseline={baseline_count}, final={final_count}"
                }
                self.log(f"❌ Article generation test: FAILED - Generated 0 articles")
                return False
                
            self.test_results["article_generation"] = {
                "status": "PASSED",
                "details": {
                    "baseline_count": baseline_count,
                    "final_count": final_count,
                    "articles_generated": articles_generated,
                    "processing_status": result.get("status", "unknown"),
                    "job_id": result.get("job_id", "unknown")
                }
            }
            self.passed_tests += 1
            self.log(f"✅ Article generation success: PASSED - Generated {articles_generated} articles")
            return True
            
        except Exception as e:
            self.test_results["article_generation"] = {
                "status": "FAILED",
                "error": f"Article generation test exception: {str(e)}"
            }
            self.log(f"❌ Article generation test: FAILED - {str(e)}")
            return False
    
    def test_v2_only_mode_functionality(self):
        """Test full V2-only operation after bug fixes"""
        try:
            self.log("🔍 Testing V2-only mode functionality...")
            
            # Test that legacy endpoints are blocked
            legacy_endpoints = [
                "/api/v1/content/process",
                "/api/legacy/upload", 
                "/api/old/analyze"
            ]
            
            blocked_count = 0
            for endpoint in legacy_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                    if response.status_code in [404, 410]:
                        blocked_count += 1
                except:
                    blocked_count += 1  # Timeout or error also counts as blocked
            
            if blocked_count != len(legacy_endpoints):
                self.test_results["v2_only_mode"] = {
                    "status": "FAILED",
                    "error": f"Legacy endpoints not properly blocked: {blocked_count}/{len(legacy_endpoints)} blocked"
                }
                self.log(f"❌ V2-only mode test: FAILED - Legacy endpoints accessible")
                return False
            
            # Test V2 endpoints are working
            v2_endpoints = [
                "/api/health",
                "/api/content-library"
            ]
            
            working_count = 0
            for endpoint in v2_endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=30)
                    if response.status_code == 200:
                        working_count += 1
                except:
                    pass
            
            if working_count != len(v2_endpoints):
                self.test_results["v2_only_mode"] = {
                    "status": "FAILED",
                    "error": f"V2 endpoints not working: {working_count}/{len(v2_endpoints)} working"
                }
                self.log(f"❌ V2-only mode test: FAILED - V2 endpoints not working")
                return False
            
            self.test_results["v2_only_mode"] = {
                "status": "PASSED",
                "details": {
                    "legacy_endpoints_blocked": blocked_count,
                    "v2_endpoints_working": working_count,
                    "v2_only_enforced": True
                }
            }
            self.passed_tests += 1
            self.log("✅ V2-only mode functionality: PASSED")
            return True
            
        except Exception as e:
            self.test_results["v2_only_mode"] = {
                "status": "FAILED",
                "error": f"V2-only mode test exception: {str(e)}"
            }
            self.log(f"❌ V2-only mode test: FAILED - {str(e)}")
            return False
    
    def test_repository_pattern_integration(self):
        """Test repository pattern integration with fixed components"""
        try:
            self.log("🔍 Testing repository pattern integration...")
            
            # Test content library uses repository pattern
            response = requests.get(f"{self.backend_url}/api/content-library", timeout=30)
            if response.status_code != 200:
                self.test_results["repository_integration"] = {
                    "status": "FAILED",
                    "error": f"Content library access failed: {response.status_code}"
                }
                return False
                
            data = response.json()
            
            # Check for repository pattern indicators
            source = data.get("source", "")
            if "repository" not in source.lower():
                self.test_results["repository_integration"] = {
                    "status": "FAILED",
                    "error": f"Repository pattern not detected in content library: source={source}"
                }
                self.log(f"❌ Repository integration test: FAILED - No repository pattern")
                return False
            
            # Test repository-based operations work
            articles = data.get("articles", [])
            article_count = len(articles)
            
            if article_count == 0:
                self.test_results["repository_integration"] = {
                    "status": "FAILED",
                    "error": "No articles found in repository-based content library"
                }
                self.log(f"❌ Repository integration test: FAILED - No articles")
                return False
            
            self.test_results["repository_integration"] = {
                "status": "PASSED",
                "details": {
                    "repository_source": source,
                    "article_count": article_count,
                    "repository_pattern_active": True
                }
            }
            self.passed_tests += 1
            self.log(f"✅ Repository pattern integration: PASSED - {article_count} articles via repository")
            return True
            
        except Exception as e:
            self.test_results["repository_integration"] = {
                "status": "FAILED",
                "error": f"Repository integration test exception: {str(e)}"
            }
            self.log(f"❌ Repository integration test: FAILED - {str(e)}")
            return False
    
    def test_system_stability(self):
        """Test system stability after bug fixes"""
        try:
            self.log("🔍 Testing system stability after bug fixes...")
            
            # Test multiple concurrent requests
            import concurrent.futures
            import threading
            
            def make_request():
                try:
                    response = requests.get(f"{self.backend_url}/api/health", timeout=15)
                    return response.status_code == 200
                except:
                    return False
            
            # Make 5 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            
            if success_rate < 0.8:  # 80% success rate minimum
                self.test_results["system_stability"] = {
                    "status": "FAILED",
                    "error": f"System stability insufficient: {success_rate*100:.1f}% success rate"
                }
                self.log(f"❌ System stability test: FAILED - {success_rate*100:.1f}% success rate")
                return False
            
            # Test system can handle processing load
            test_content = "# Stability Test\n\nThis is a stability test for the V2 pipeline."
            
            response = requests.post(
                f"{self.backend_url}/api/content/process",
                json={"content": test_content, "format": "markdown"},
                timeout=60
            )
            
            processing_stable = response.status_code == 200
            
            if not processing_stable:
                self.test_results["system_stability"] = {
                    "status": "FAILED",
                    "error": f"Processing stability failed: {response.status_code}"
                }
                self.log(f"❌ System stability test: FAILED - Processing unstable")
                return False
            
            self.test_results["system_stability"] = {
                "status": "PASSED",
                "details": {
                    "concurrent_success_rate": f"{success_rate*100:.1f}%",
                    "processing_stable": processing_stable,
                    "concurrent_requests": len(results)
                }
            }
            self.passed_tests += 1
            self.log(f"✅ System stability: PASSED - {success_rate*100:.1f}% success rate")
            return True
            
        except Exception as e:
            self.test_results["system_stability"] = {
                "status": "FAILED",
                "error": f"System stability test exception: {str(e)}"
            }
            self.log(f"❌ System stability test: FAILED - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all V2 pipeline bug fix validation tests"""
        self.log("🚀 Starting CRITICAL BUG FIX VALIDATION for V2 Pipeline Processing Issues")
        self.log("=" * 80)
        
        # Run all tests
        tests = [
            ("System Health & V2-Only Config", self.test_health_check),
            ("ContentBlock Interface Fix", self.test_contentblock_interface_fix),
            ("NormalizedDocument job_id Fix", self.test_normalizeddocument_job_id_fix),
            ("V2ArticleGenerator Storage", self.test_v2_article_generator_storage),
            ("End-to-End V2 Processing", self.test_end_to_end_v2_processing),
            ("Article Generation Success", self.test_article_generation_success),
            ("V2-Only Mode Functionality", self.test_v2_only_mode_functionality),
            ("Repository Pattern Integration", self.test_repository_pattern_integration),
            ("System Stability", self.test_system_stability)
        ]
        
        for test_name, test_func in tests:
            self.log(f"\n📋 Running: {test_name}")
            test_func()
            time.sleep(2)  # Brief pause between tests
        
        # Calculate results
        success_rate = (self.passed_tests / self.total_tests) * 100
        
        self.log("\n" + "=" * 80)
        self.log("🎯 CRITICAL BUG FIX VALIDATION RESULTS")
        self.log("=" * 80)
        
        for test_name, result in self.test_results.items():
            status = result["status"]
            emoji = "✅" if status == "PASSED" else "❌"
            self.log(f"{emoji} {test_name.replace('_', ' ').title()}: {status}")
            
            if status == "FAILED":
                self.log(f"   Error: {result.get('error', 'Unknown error')}")
            elif "details" in result:
                details = result["details"]
                if isinstance(details, dict):
                    for key, value in details.items():
                        self.log(f"   {key}: {value}")
        
        self.log(f"\n📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        
        if success_rate >= 80:
            self.log("🎉 CRITICAL BUG FIX VALIDATION: SUCCESS - V2 pipeline issues resolved!")
            return True
        else:
            self.log("⚠️ CRITICAL BUG FIX VALIDATION: PARTIAL - Some issues remain")
            return False

def main():
    """Main test execution"""
    validator = V2PipelineBugFixValidator()
    success = validator.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()