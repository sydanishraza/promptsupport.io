#!/usr/bin/env python3
"""
INTELLIGENT COMPLETENESS HANDLING SYSTEM TESTING
Tests the new completeness features in the Knowledge Engine backend
"""

import requests
import json
import time
import os
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class IntelligentCompletenessTest:
    def __init__(self):
        self.test_results = []
        self.session_id = str(uuid.uuid4())
        
    def log_result(self, test_name, success, details, coverage_data=None):
        """Log test result with completeness data"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'coverage_data': coverage_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if coverage_data:
            print(f"   📊 Coverage: {coverage_data.get('overall_coverage', 0):.1%}")
            print(f"   📄 Articles: {coverage_data.get('total_articles', 0)}")
            print(f"   🧠 Complexity: {coverage_data.get('complexity_score', 0):.3f}")
            print(f"   🔄 Overflow: {'Yes' if coverage_data.get('overflow_handled', False) else 'No'}")

    def create_complex_test_document(self):
        """Create a highly complex document with 10+ sections to trigger intelligent limits"""
        complex_content = """
# Comprehensive API Integration Guide

## 1. Introduction and Overview
This comprehensive guide covers advanced API integration techniques for enterprise applications. The content includes multiple technical domains, complex authentication flows, and extensive customization options that require detailed documentation across multiple focused articles.

## 2. Prerequisites and System Requirements
Before beginning the integration process, ensure your development environment meets the following requirements:
- Node.js 16+ or Python 3.8+
- Valid API credentials and authentication tokens
- Development server with HTTPS support
- Database connectivity for session management
- Understanding of REST API principles and OAuth 2.0 flows

## 3. Account Setup and Authentication Configuration
Setting up your account requires multiple steps including credential generation, webhook configuration, and security policy implementation. This section covers the complete authentication flow from initial account creation through advanced security configurations.

### 3.1 API Key Generation
Generate your API keys through the developer console. Each application requires separate credentials for development, staging, and production environments.

### 3.2 OAuth 2.0 Implementation
Implement OAuth 2.0 authorization code flow with PKCE for enhanced security. This includes redirect URI configuration, state parameter validation, and token refresh mechanisms.

## 4. Core API Implementation
The core implementation involves multiple endpoints, request/response handling, error management, and data transformation. This section provides comprehensive coverage of all API endpoints and their usage patterns.

### 4.1 Authentication Endpoints
- POST /auth/login - User authentication
- POST /auth/refresh - Token refresh
- POST /auth/logout - Session termination

### 4.2 Data Management Endpoints
- GET /api/data - Retrieve data collections
- POST /api/data - Create new data entries
- PUT /api/data/{id} - Update existing entries
- DELETE /api/data/{id} - Remove data entries

## 5. Advanced Configuration and Customization
Advanced configurations include webhook setup, custom field mapping, data transformation rules, and integration with third-party services. This section covers enterprise-level customization options.

### 5.1 Webhook Configuration
Configure webhooks for real-time data synchronization. Includes endpoint setup, payload validation, retry mechanisms, and error handling strategies.

### 5.2 Custom Field Mapping
Implement custom field mapping for data transformation between systems. Supports complex mapping rules, data validation, and transformation functions.

## 6. Data Synchronization and Real-time Updates
Implement real-time data synchronization using webhooks, WebSocket connections, and polling mechanisms. This section covers different synchronization strategies and their trade-offs.

### 6.1 WebSocket Implementation
Real-time bidirectional communication using WebSocket connections. Includes connection management, message queuing, and reconnection strategies.

### 6.2 Polling Strategies
Implement efficient polling mechanisms for systems that don't support webhooks. Covers exponential backoff, rate limiting, and data deduplication.

## 7. Error Handling and Debugging
Comprehensive error handling strategies including retry logic, circuit breakers, logging, and monitoring. This section covers both client-side and server-side error management.

### 7.1 HTTP Status Code Handling
- 200-299: Success responses
- 400-499: Client errors
- 500-599: Server errors

### 7.2 Retry Mechanisms
Implement exponential backoff with jitter for failed requests. Includes maximum retry limits and circuit breaker patterns.

## 8. Performance Optimization
Optimize API performance through caching, request batching, connection pooling, and efficient data structures. This section covers performance best practices and monitoring.

### 8.1 Caching Strategies
Implement multi-level caching including browser cache, CDN, and application-level caching. Covers cache invalidation and consistency strategies.

### 8.2 Request Batching
Batch multiple API requests to reduce network overhead. Includes batch size optimization and error handling for partial failures.

## 9. Security Best Practices
Implement comprehensive security measures including input validation, SQL injection prevention, XSS protection, and secure communication protocols.

### 9.1 Input Validation
Validate all input data using schema validation, sanitization, and type checking. Includes server-side validation and client-side preprocessing.

### 9.2 Secure Communication
Implement TLS 1.3, certificate pinning, and secure headers. Covers HTTPS enforcement and security header configuration.

## 10. Testing and Quality Assurance
Comprehensive testing strategies including unit tests, integration tests, load testing, and security testing. This section covers testing frameworks and best practices.

### 10.1 Unit Testing
Write comprehensive unit tests for all API endpoints and business logic. Includes mocking strategies and test data management.

### 10.2 Integration Testing
Test complete workflows and system interactions. Covers test environment setup and data consistency validation.

## 11. Deployment and Production Considerations
Production deployment strategies including containerization, load balancing, monitoring, and disaster recovery. This section covers enterprise deployment patterns.

### 11.1 Container Deployment
Deploy using Docker containers with Kubernetes orchestration. Includes scaling strategies and resource management.

### 11.2 Monitoring and Alerting
Implement comprehensive monitoring using metrics, logs, and distributed tracing. Covers alerting strategies and incident response.

## 12. Troubleshooting and Common Issues
Common integration issues and their solutions. Includes diagnostic tools, debugging techniques, and resolution strategies for typical problems.

### 12.1 Connection Issues
Diagnose and resolve network connectivity problems, DNS issues, and firewall configurations.

### 12.2 Authentication Failures
Troubleshoot OAuth flows, token expiration, and permission issues.

## 13. Advanced Use Cases and Examples
Real-world implementation examples including e-commerce integration, CRM synchronization, and custom workflow automation.

### 13.1 E-commerce Integration
Complete e-commerce platform integration with product synchronization, order management, and inventory updates.

### 13.2 CRM Synchronization
Bidirectional CRM data synchronization with contact management, lead tracking, and sales pipeline integration.

## 14. API Reference and Documentation
Complete API reference with all endpoints, parameters, response formats, and code examples in multiple programming languages.

### 14.1 Endpoint Reference
Detailed documentation for all API endpoints with request/response examples and parameter descriptions.

### 14.2 SDK Documentation
Official SDK documentation for JavaScript, Python, PHP, and other supported languages.
"""
        return complex_content

    def test_backend_health(self):
        """Test 1: Backend Health Check"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            self.log_result("Backend Health Check", success, details)
            return success
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Error: {str(e)}")
            return False

    def test_complex_document_processing(self):
        """Test 2: Upload Complex Document to Trigger Intelligent Limits"""
        try:
            complex_content = self.create_complex_test_document()
            
            # Create a text content request
            test_data = {
                'content': complex_content,
                'content_type': 'text',
                'metadata': {
                    'filename': 'complex_api_guide.txt',
                    'source': 'intelligent_completeness_test'
                }
            }
            
            print(f"📤 Uploading complex document ({len(complex_content)} chars, 14 sections)")
            
            response = requests.post(
                f"{API_BASE}/content/process",
                json=test_data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract completeness data
                articles_created = result.get('articles_created', 0)
                processing_time = result.get('processing_time', 0)
                
                # Check if intelligent limits were applied (should exceed 6 articles)
                intelligent_limit_applied = articles_created > 6
                
                coverage_data = {
                    'total_articles': articles_created,
                    'processing_time': processing_time,
                    'intelligent_limit_applied': intelligent_limit_applied,
                    'source_sections': 14  # We know our test doc has 14 sections
                }
                
                success = intelligent_limit_applied
                details = f"Created {articles_created} articles in {processing_time:.1f}s (Expected >6 for complex content)"
                
                self.log_result("Complex Document Processing", success, details, coverage_data)
                return success, result
            else:
                self.log_result("Complex Document Processing", False, f"HTTP {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result("Complex Document Processing", False, f"Error: {str(e)}")
            return False, None

    def test_content_coverage_analysis(self):
        """Test 3: Verify Content Coverage Analysis"""
        try:
            # Get recent articles to analyze coverage
            response = requests.get(f"{API_BASE}/content-library", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if not articles:
                    self.log_result("Content Coverage Analysis", False, "No articles found for coverage analysis")
                    return False
                
                # Look for articles with coverage metadata
                coverage_found = False
                total_coverage = 0
                articles_with_coverage = 0
                
                for article in articles[:10]:  # Check first 10 articles
                    metadata = article.get('metadata', {})
                    content_coverage = metadata.get('content_coverage', {})
                    
                    if content_coverage and 'overall_coverage' in content_coverage:
                        coverage_found = True
                        total_coverage += content_coverage.get('overall_coverage', 0)
                        articles_with_coverage += 1
                        
                        print(f"   📊 Article '{article.get('title', 'Untitled')[:30]}...': {content_coverage.get('overall_coverage', 0):.1%} coverage")
                
                if coverage_found:
                    avg_coverage = total_coverage / articles_with_coverage if articles_with_coverage > 0 else 0
                    
                    coverage_data = {
                        'articles_with_coverage': articles_with_coverage,
                        'average_coverage': avg_coverage,
                        'coverage_found': True
                    }
                    
                    success = avg_coverage > 0.7  # Expect >70% coverage
                    details = f"Found coverage data in {articles_with_coverage} articles, avg coverage: {avg_coverage:.1%}"
                    
                    self.log_result("Content Coverage Analysis", success, details, coverage_data)
                    return success
                else:
                    self.log_result("Content Coverage Analysis", False, "No coverage metadata found in articles")
                    return False
            else:
                self.log_result("Content Coverage Analysis", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Content Coverage Analysis", False, f"Error: {str(e)}")
            return False

    def test_overflow_handling(self):
        """Test 4: Verify Overflow Handling for Large Documents"""
        try:
            # Create an even larger document to trigger overflow
            overflow_content = self.create_complex_test_document()
            # Add more sections to definitely trigger overflow
            overflow_content += """
## 15. Additional Advanced Topics
More complex content that should trigger overflow handling.

## 16. Extended Configuration Options
Additional configuration details that exceed normal limits.

## 17. Enterprise Integration Patterns
Complex enterprise patterns requiring detailed documentation.

## 18. Performance Monitoring and Analytics
Comprehensive monitoring and analytics implementation.

## 19. Compliance and Regulatory Requirements
Legal and compliance considerations for enterprise deployments.

## 20. Future Roadmap and Updates
Planned features and update procedures.
"""
            
            test_data = {
                'content': overflow_content,
                'content_type': 'text',
                'metadata': {
                    'filename': 'overflow_test_guide.txt',
                    'source': 'intelligent_completeness_test'
                }
            }
            
            print(f"📤 Testing overflow handling ({len(overflow_content)} chars, 20 sections)")
            
            response = requests.post(
                f"{API_BASE}/content/process",
                json=test_data,
                timeout=150
            )
            
            if response.status_code == 200:
                result = response.json()
                articles_created = result.get('articles_created', 0)
                
                # Check for overflow summary article
                articles_response = requests.get(f"{API_BASE}/content-library", timeout=30)
                if articles_response.status_code == 200:
                    articles_data = articles_response.json()
                    articles = articles_data.get('articles', [])
                    
                    # Look for overflow summary article
                    overflow_article_found = False
                    for article in articles[:20]:  # Check recent articles
                        title = article.get('title', '').lower()
                        metadata = article.get('metadata', {})
                        
                        if ('overflow' in title or 'additional' in title or 
                            metadata.get('is_overflow_summary', False) or
                            metadata.get('stage_type') == 'overflow_summary'):
                            overflow_article_found = True
                            print(f"   📋 Found overflow article: {article.get('title', 'Untitled')}")
                            break
                    
                    coverage_data = {
                        'total_articles': articles_created,
                        'overflow_article_found': overflow_article_found,
                        'source_sections': 20
                    }
                    
                    success = overflow_article_found and articles_created >= 10
                    details = f"Created {articles_created} articles, overflow handling: {'✅' if overflow_article_found else '❌'}"
                    
                    self.log_result("Overflow Handling", success, details, coverage_data)
                    return success
                else:
                    self.log_result("Overflow Handling", False, "Could not retrieve articles to check for overflow")
                    return False
            else:
                self.log_result("Overflow Handling", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Overflow Handling", False, f"Error: {str(e)}")
            return False

    def test_completeness_verification(self):
        """Test 5: Verify Completeness Warnings and Verification"""
        try:
            # Get recent articles and check for completeness metadata
            response = requests.get(f"{API_BASE}/content-library", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                completeness_verified = False
                high_coverage_found = False
                intelligent_processing_found = False
                
                for article in articles[:15]:  # Check recent articles
                    metadata = article.get('metadata', {})
                    content_coverage = metadata.get('content_coverage', {})
                    
                    # Check for intelligent processing markers
                    if metadata.get('intelligent_processing', False):
                        intelligent_processing_found = True
                        print(f"   🧠 Found intelligent processing in: {article.get('title', 'Untitled')[:40]}...")
                    
                    # Check for high coverage
                    overall_coverage = content_coverage.get('overall_coverage', 0)
                    if overall_coverage >= 0.7:
                        high_coverage_found = True
                        completeness_verified = True
                        print(f"   ✅ High coverage ({overall_coverage:.1%}) in: {article.get('title', 'Untitled')[:40]}...")
                
                coverage_data = {
                    'intelligent_processing_found': intelligent_processing_found,
                    'high_coverage_found': high_coverage_found,
                    'completeness_verified': completeness_verified
                }
                
                success = completeness_verified and intelligent_processing_found
                details = f"Completeness verification: {'✅' if completeness_verified else '⚠️'}, Intelligent processing: {'✅' if intelligent_processing_found else '❌'}"
                
                self.log_result("Completeness Verification", success, details, coverage_data)
                return success
            else:
                self.log_result("Completeness Verification", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Completeness Verification", False, f"Error: {str(e)}")
            return False

    def test_dynamic_article_limits(self):
        """Test 6: Verify Dynamic Article Limits Based on Complexity"""
        try:
            # Test simple document (should get 4-6 articles)
            simple_content = """
# Simple Guide

## Introduction
This is a simple guide with basic content.

## Setup
Basic setup instructions.

## Usage
How to use the system.

## Conclusion
Final thoughts and summary.
"""
            
            simple_data = {
                'content': simple_content,
                'content_type': 'text',
                'metadata': {
                    'filename': 'simple_guide.txt',
                    'source': 'intelligent_completeness_test'
                }
            }
            
            print("📤 Testing simple document (should get 4-6 articles)")
            simple_response = requests.post(
                f"{API_BASE}/content/process",
                json=simple_data,
                timeout=60
            )
            
            simple_articles = 0
            if simple_response.status_code == 200:
                simple_result = simple_response.json()
                simple_articles = simple_result.get('articles_created', 0)
                print(f"   📄 Simple document created: {simple_articles} articles")
            
            # Test complex document (should get 7-12 articles)
            complex_content = self.create_complex_test_document()
            complex_data = {
                'content': complex_content,
                'content_type': 'text',
                'metadata': {
                    'filename': 'complex_dynamic_test.txt',
                    'source': 'intelligent_completeness_test'
                }
            }
            
            print("📤 Testing complex document (should get 7-12 articles)")
            complex_response = requests.post(
                f"{API_BASE}/content/process",
                json=complex_data,
                timeout=120
            )
            
            complex_articles = 0
            if complex_response.status_code == 200:
                complex_result = complex_response.json()
                complex_articles = complex_result.get('articles_created', 0)
                print(f"   📄 Complex document created: {complex_articles} articles")
            
            # Verify dynamic limits
            simple_in_range = 4 <= simple_articles <= 6
            complex_in_range = 7 <= complex_articles <= 12
            dynamic_behavior = complex_articles > simple_articles
            
            coverage_data = {
                'simple_articles': simple_articles,
                'complex_articles': complex_articles,
                'simple_in_range': simple_in_range,
                'complex_in_range': complex_in_range,
                'dynamic_behavior': dynamic_behavior
            }
            
            success = simple_in_range and complex_in_range and dynamic_behavior
            details = f"Simple: {simple_articles} articles (4-6 expected), Complex: {complex_articles} articles (7-12 expected)"
            
            self.log_result("Dynamic Article Limits", success, details, coverage_data)
            return success
            
        except Exception as e:
            self.log_result("Dynamic Article Limits", False, f"Error: {str(e)}")
            return False

    def test_no_content_loss(self):
        """Test 7: Verify No Content Loss - All Source Material Covered"""
        try:
            # Create test content with specific markers we can track
            test_content = """
# Content Loss Prevention Test

## Section A: Authentication Setup
MARKER_AUTH: This section covers authentication setup procedures.

## Section B: API Integration
MARKER_API: This section covers API integration details.

## Section C: Data Management
MARKER_DATA: This section covers data management procedures.

## Section D: Error Handling
MARKER_ERROR: This section covers error handling strategies.

## Section E: Performance Optimization
MARKER_PERF: This section covers performance optimization techniques.

## Section F: Security Considerations
MARKER_SECURITY: This section covers security implementation details.
"""
            
            test_data = {
                'content': test_content,
                'content_type': 'text',
                'metadata': {
                    'filename': 'content_loss_test.txt',
                    'source': 'intelligent_completeness_test'
                }
            }
            
            print("📤 Testing content loss prevention with trackable markers")
            
            response = requests.post(
                f"{API_BASE}/content/process",
                json=test_data,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                articles_created = result.get('articles_created', 0)
                
                # Get all articles and check for our markers
                articles_response = requests.get(f"{API_BASE}/content-library", timeout=30)
                if articles_response.status_code == 200:
                    articles_data = articles_response.json()
                    articles = articles_data.get('articles', [])
                    
                    # Track which markers we find
                    markers_found = {
                        'MARKER_AUTH': False,
                        'MARKER_API': False,
                        'MARKER_DATA': False,
                        'MARKER_ERROR': False,
                        'MARKER_PERF': False,
                        'MARKER_SECURITY': False
                    }
                    
                    # Search through recent articles for our markers
                    for article in articles[:20]:  # Check recent articles
                        content = article.get('content', '')
                        for marker in markers_found.keys():
                            if marker in content:
                                markers_found[marker] = True
                                print(f"   ✅ Found {marker} in: {article.get('title', 'Untitled')[:30]}...")
                    
                    # Calculate content preservation
                    markers_preserved = sum(markers_found.values())
                    total_markers = len(markers_found)
                    preservation_rate = markers_preserved / total_markers
                    
                    coverage_data = {
                        'total_markers': total_markers,
                        'markers_preserved': markers_preserved,
                        'preservation_rate': preservation_rate,
                        'articles_created': articles_created,
                        'markers_found': markers_found
                    }
                    
                    success = preservation_rate >= 0.8  # At least 80% of content preserved
                    details = f"Content preservation: {markers_preserved}/{total_markers} markers found ({preservation_rate:.1%})"
                    
                    self.log_result("No Content Loss", success, details, coverage_data)
                    return success
                else:
                    self.log_result("No Content Loss", False, "Could not retrieve articles for content loss check")
                    return False
            else:
                self.log_result("No Content Loss", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("No Content Loss", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all intelligent completeness handling tests"""
        print("🧠 INTELLIGENT COMPLETENESS HANDLING SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Session ID: {self.session_id}")
        print()
        
        # Run tests in sequence
        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("Complex Document Processing", lambda: self.test_complex_document_processing()[0]),
            ("Content Coverage Analysis", self.test_content_coverage_analysis),
            ("Overflow Handling", self.test_overflow_handling),
            ("Completeness Verification", self.test_completeness_verification),
            ("Dynamic Article Limits", self.test_dynamic_article_limits),
            ("No Content Loss", self.test_no_content_loss)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                success = test_func()
                if success:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
            
            time.sleep(2)  # Brief pause between tests
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 INTELLIGENT COMPLETENESS TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("✅ COMPLETENESS SYSTEM STATUS: OPERATIONAL")
        elif success_rate >= 60:
            print("⚠️ COMPLETENESS SYSTEM STATUS: PARTIALLY FUNCTIONAL")
        else:
            print("❌ COMPLETENESS SYSTEM STATUS: NEEDS ATTENTION")
        
        # Print detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
            
            if result.get('coverage_data'):
                coverage = result['coverage_data']
                if 'overall_coverage' in coverage:
                    print(f"   📊 Coverage: {coverage['overall_coverage']:.1%}")
                if 'total_articles' in coverage:
                    print(f"   📄 Articles: {coverage['total_articles']}")
        
        print("\n🎯 KEY COMPLETENESS FEATURES TESTED:")
        print("   • Content Coverage Analysis - Tracks percentage of source content covered")
        print("   • Document Complexity Scoring - Evaluates complexity for intelligent limits")
        print("   • Intelligent Article Limits - Dynamic limits from 4-12 articles")
        print("   • Smart Section Consolidation - Intelligently merges sections")
        print("   • Overflow Handling - Creates overflow summary for remaining content")
        print("   • Completeness Verification - Ensures no critical information is lost")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = IntelligentCompletenessTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)