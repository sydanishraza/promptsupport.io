#!/usr/bin/env python3
"""
PHASE 2 ADVANCED REFINED ENGINE v2.1 BACKEND TESTING
Comprehensive testing of the new Advanced Refined Engine v2.1 and migration tools
"""

import asyncio
import aiohttp
import json
import time
import io
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com/api"

class AdvancedEngineV21Tester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.start_time = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.start_time = time.time()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str, response_data: Dict = None):
        """Log test result with details"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
    
    async def test_process_advanced_endpoint(self):
        """Test /api/content/process-advanced endpoint"""
        test_name = "Advanced Engine v2.1 - Process Text Content"
        
        try:
            # Sample content for testing advanced analysis
            test_content = """
            # Advanced API Documentation Guide
            
            This comprehensive guide covers the implementation of RESTful APIs with advanced authentication mechanisms and rate limiting strategies.
            
            ## Authentication Methods
            
            ### OAuth 2.0 Implementation
            OAuth 2.0 provides secure authorization flows for API access. Here's how to implement it:
            
            ```javascript
            const oauth = {
                clientId: 'your-client-id',
                clientSecret: 'your-client-secret',
                redirectUri: 'https://yourapp.com/callback',
                scope: 'read write'
            };
            
            function getAuthorizationUrl() {
                const params = new URLSearchParams({
                    response_type: 'code',
                    client_id: oauth.clientId,
                    redirect_uri: oauth.redirectUri,
                    scope: oauth.scope
                });
                return `https://auth.example.com/oauth/authorize?${params}`;
            }
            ```
            
            ### JWT Token Validation
            JSON Web Tokens provide stateless authentication:
            
            ```python
            import jwt
            import datetime
            
            def create_jwt_token(user_id, secret_key):
                payload = {
                    'user_id': user_id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                    'iat': datetime.datetime.utcnow()
                }
                return jwt.encode(payload, secret_key, algorithm='HS256')
            
            def validate_jwt_token(token, secret_key):
                try:
                    payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                    return payload['user_id']
                except jwt.ExpiredSignatureError:
                    return None
            ```
            
            ## Rate Limiting Strategies
            
            ### Token Bucket Algorithm
            The token bucket algorithm provides flexible rate limiting:
            
            1. Initialize bucket with maximum tokens
            2. Tokens are consumed for each request
            3. Tokens are replenished at a fixed rate
            4. Requests are denied when bucket is empty
            
            ### Implementation Example
            
            ```python
            import time
            from threading import Lock
            
            class TokenBucket:
                def __init__(self, capacity, refill_rate):
                    self.capacity = capacity
                    self.tokens = capacity
                    self.refill_rate = refill_rate
                    self.last_refill = time.time()
                    self.lock = Lock()
                
                def consume(self, tokens=1):
                    with self.lock:
                        self._refill()
                        if self.tokens >= tokens:
                            self.tokens -= tokens
                            return True
                        return False
                
                def _refill(self):
                    now = time.time()
                    tokens_to_add = (now - self.last_refill) * self.refill_rate
                    self.tokens = min(self.capacity, self.tokens + tokens_to_add)
                    self.last_refill = now
            ```
            
            ## Error Handling Best Practices
            
            ### HTTP Status Codes
            - 200: Success
            - 400: Bad Request - Invalid parameters
            - 401: Unauthorized - Authentication required
            - 403: Forbidden - Insufficient permissions
            - 429: Too Many Requests - Rate limit exceeded
            - 500: Internal Server Error
            
            ### Error Response Format
            
            ```json
            {
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "details": {
                        "limit": 100,
                        "window": "1 hour",
                        "retry_after": 3600
                    }
                }
            }
            ```
            
            ## Performance Optimization
            
            ### Caching Strategies
            1. **Redis Caching**: Store frequently accessed data
            2. **CDN Integration**: Cache static responses
            3. **Database Query Optimization**: Use indexes and query optimization
            4. **Connection Pooling**: Reuse database connections
            
            ### Monitoring and Metrics
            Track these key metrics:
            - Request latency (p50, p95, p99)
            - Error rates by endpoint
            - Rate limit violations
            - Authentication failures
            - Database query performance
            """
            
            payload = {
                "content": test_content,
                "metadata": {
                    "title": "Advanced API Documentation Test",
                    "content_type": "api_documentation",
                    "complexity": "advanced"
                }
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/process-advanced",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    required_fields = ["success", "message", "articles_created", "engine_used", "processing_analytics", "articles"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing response fields: {missing_fields}", data)
                        return False
                    
                    # Verify engine version
                    if data.get("engine_used") != "advanced_refined_2.1":
                        self.log_result(test_name, False, f"Wrong engine used: {data.get('engine_used')}", data)
                        return False
                    
                    # Verify articles were created
                    articles_created = data.get("articles_created", 0)
                    if articles_created == 0:
                        self.log_result(test_name, False, "No articles were created", data)
                        return False
                    
                    # Verify article metadata
                    articles = data.get("articles", [])
                    if not articles:
                        self.log_result(test_name, False, "No article details returned", data)
                        return False
                    
                    # Check for advanced engine metadata
                    advanced_features = []
                    for article in articles:
                        if article.get("confidence_score", 0) > 0:
                            advanced_features.append("confidence_scoring")
                        if article.get("processing_approach"):
                            advanced_features.append("processing_approach")
                        if article.get("article_type"):
                            advanced_features.append("content_type_detection")
                    
                    # Verify processing analytics
                    analytics = data.get("processing_analytics", {})
                    if not analytics.get("processing_time") and not analytics.get("chars_per_second"):
                        self.log_result(test_name, False, "Missing processing analytics", data)
                        return False
                    
                    self.log_result(
                        test_name, 
                        True, 
                        f"Successfully created {articles_created} articles with advanced features: {list(set(advanced_features))}", 
                        {
                            "articles_created": articles_created,
                            "engine_used": data.get("engine_used"),
                            "advanced_features": list(set(advanced_features)),
                            "processing_time": analytics.get("processing_time", 0),
                            "chars_per_second": analytics.get("chars_per_second", 0)
                        }
                    )
                    return True
                    
                else:
                    error_data = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    async def test_upload_advanced_endpoint(self):
        """Test /api/content/upload-advanced endpoint with file upload"""
        test_name = "Advanced Engine v2.1 - File Upload Processing"
        
        try:
            # Create a test document content
            test_document = """
            Compliance Documentation: Data Privacy and Security Standards
            
            1. INTRODUCTION
            
            This document outlines the comprehensive data privacy and security standards that must be implemented across all systems and processes. These standards ensure compliance with GDPR, CCPA, and other regulatory requirements.
            
            2. DATA CLASSIFICATION
            
            2.1 Personal Data Categories
            - Personally Identifiable Information (PII)
            - Sensitive Personal Data (SPD)
            - Financial Information
            - Health Records
            - Biometric Data
            
            2.2 Data Sensitivity Levels
            - Public: No restrictions
            - Internal: Company employees only
            - Confidential: Authorized personnel only
            - Restricted: Highest security level
            
            3. SECURITY CONTROLS
            
            3.1 Access Controls
            - Multi-factor authentication required
            - Role-based access control (RBAC)
            - Principle of least privilege
            - Regular access reviews
            
            3.2 Encryption Standards
            - Data at rest: AES-256 encryption
            - Data in transit: TLS 1.3 minimum
            - Key management: Hardware Security Modules (HSM)
            - Certificate lifecycle management
            
            3.3 Network Security
            - Firewall configurations
            - Intrusion detection systems
            - Network segmentation
            - VPN requirements for remote access
            
            4. DATA PROCESSING PROCEDURES
            
            4.1 Data Collection
            - Lawful basis identification
            - Purpose limitation principle
            - Data minimization requirements
            - Consent management procedures
            
            4.2 Data Storage
            - Geographic restrictions
            - Retention period limits
            - Secure deletion procedures
            - Backup and recovery protocols
            
            4.3 Data Sharing
            - Third-party agreements
            - Data processing agreements (DPA)
            - Cross-border transfer mechanisms
            - Vendor risk assessments
            
            5. INCIDENT RESPONSE
            
            5.1 Breach Detection
            - Automated monitoring systems
            - Anomaly detection algorithms
            - Employee reporting procedures
            - Third-party notifications
            
            5.2 Response Procedures
            - Incident classification matrix
            - Escalation procedures
            - Communication protocols
            - Regulatory notification timelines
            
            6. COMPLIANCE MONITORING
            
            6.1 Regular Audits
            - Internal audit schedule
            - External audit requirements
            - Compliance testing procedures
            - Remediation tracking
            
            6.2 Training and Awareness
            - Employee training programs
            - Awareness campaigns
            - Competency assessments
            - Continuous education requirements
            
            7. GOVERNANCE STRUCTURE
            
            7.1 Roles and Responsibilities
            - Data Protection Officer (DPO)
            - Data Controllers
            - Data Processors
            - Security Team
            
            7.2 Policy Management
            - Policy review cycles
            - Update procedures
            - Approval workflows
            - Version control
            """
            
            # Create form data for file upload
            data = aiohttp.FormData()
            data.add_field('file', 
                          io.StringIO(test_document), 
                          filename='compliance_documentation.txt',
                          content_type='text/plain')
            data.add_field('metadata', json.dumps({
                "document_type": "compliance_documentation",
                "classification": "confidential",
                "department": "legal"
            }))
            
            async with self.session.post(
                f"{BACKEND_URL}/content/upload-advanced",
                data=data
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    required_fields = ["success", "message", "filename", "content_extracted", "articles_created", "engine_used", "processing_analytics", "articles"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing response fields: {missing_fields}", data)
                        return False
                    
                    # Verify engine version
                    if data.get("engine_used") != "advanced_refined_2.1":
                        self.log_result(test_name, False, f"Wrong engine used: {data.get('engine_used')}", data)
                        return False
                    
                    # Verify content extraction
                    content_extracted = data.get("content_extracted", 0)
                    if content_extracted < 1000:  # Should extract substantial content
                        self.log_result(test_name, False, f"Insufficient content extracted: {content_extracted} chars", data)
                        return False
                    
                    # Verify articles were created
                    articles_created = data.get("articles_created", 0)
                    if articles_created == 0:
                        self.log_result(test_name, False, "No articles were created", data)
                        return False
                    
                    # Check for sophisticated content type detection
                    articles = data.get("articles", [])
                    content_types_detected = set()
                    for article in articles:
                        if article.get("content_type"):
                            content_types_detected.add(article["content_type"])
                    
                    # Verify processing analytics
                    analytics = data.get("processing_analytics", {})
                    confidence_avg = analytics.get("confidence_average", 0)
                    
                    self.log_result(
                        test_name, 
                        True, 
                        f"Successfully processed file: {articles_created} articles, {content_extracted} chars extracted, content types: {list(content_types_detected)}", 
                        {
                            "filename": data.get("filename"),
                            "articles_created": articles_created,
                            "content_extracted": content_extracted,
                            "engine_used": data.get("engine_used"),
                            "content_types": list(content_types_detected),
                            "confidence_average": confidence_avg
                        }
                    )
                    return True
                    
                else:
                    error_data = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    async def test_batch_processing_endpoint(self):
        """Test /api/content/upload-batch-advanced endpoint"""
        test_name = "Advanced Engine v2.1 - Batch Processing"
        
        try:
            # Create multiple test files
            file1_content = """
            Release Notes v3.2.0
            
            NEW FEATURES:
            - Advanced search functionality with filters
            - Real-time collaboration features
            - Enhanced mobile responsiveness
            - API rate limiting improvements
            
            BUG FIXES:
            - Fixed authentication timeout issues
            - Resolved data synchronization problems
            - Corrected UI rendering on Safari
            - Fixed memory leaks in background processes
            
            PERFORMANCE IMPROVEMENTS:
            - 40% faster page load times
            - Optimized database queries
            - Reduced memory usage by 25%
            - Enhanced caching mechanisms
            """
            
            file2_content = """
            User Guide: Getting Started
            
            STEP 1: Account Setup
            1. Visit the registration page
            2. Enter your email address
            3. Create a secure password
            4. Verify your email
            
            STEP 2: Profile Configuration
            1. Upload a profile picture
            2. Add your personal information
            3. Set notification preferences
            4. Configure privacy settings
            
            STEP 3: First Project
            1. Click "Create New Project"
            2. Choose a project template
            3. Invite team members
            4. Start collaborating
            """
            
            # Create form data for batch upload
            data = aiohttp.FormData()
            
            # Add first file
            data.add_field('files', 
                          io.StringIO(file1_content), 
                          filename='release_notes_v3.2.0.txt',
                          content_type='text/plain')
            
            # Add second file
            data.add_field('files', 
                          io.StringIO(file2_content), 
                          filename='user_guide_getting_started.txt',
                          content_type='text/plain')
            
            data.add_field('metadata', json.dumps({
                "batch_name": "Documentation Update",
                "department": "product",
                "priority": "high"
            }))
            
            async with self.session.post(
                f"{BACKEND_URL}/content/upload-batch-advanced",
                data=data
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    required_fields = ["success", "message", "batch_id", "files_processed", "files_successful", "total_articles_created", "engine_used", "processing_analytics", "results"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing response fields: {missing_fields}", data)
                        return False
                    
                    # Verify engine version
                    if data.get("engine_used") != "advanced_refined_2.1":
                        self.log_result(test_name, False, f"Wrong engine used: {data.get('engine_used')}", data)
                        return False
                    
                    # Verify batch processing results
                    files_processed = data.get("files_processed", 0)
                    files_successful = data.get("files_successful", 0)
                    total_articles = data.get("total_articles_created", 0)
                    
                    if files_processed != 2:
                        self.log_result(test_name, False, f"Expected 2 files processed, got {files_processed}", data)
                        return False
                    
                    if files_successful != 2:
                        self.log_result(test_name, False, f"Expected 2 successful files, got {files_successful}", data)
                        return False
                    
                    if total_articles == 0:
                        self.log_result(test_name, False, "No articles created from batch processing", data)
                        return False
                    
                    # Verify individual file results
                    results = data.get("results", [])
                    if len(results) != 2:
                        self.log_result(test_name, False, f"Expected 2 file results, got {len(results)}", data)
                        return False
                    
                    successful_results = [r for r in results if r.get("success")]
                    if len(successful_results) != 2:
                        self.log_result(test_name, False, f"Expected 2 successful results, got {len(successful_results)}", data)
                        return False
                    
                    self.log_result(
                        test_name, 
                        True, 
                        f"Batch processing successful: {files_successful}/{files_processed} files, {total_articles} total articles", 
                        {
                            "batch_id": data.get("batch_id"),
                            "files_processed": files_processed,
                            "files_successful": files_successful,
                            "total_articles_created": total_articles,
                            "engine_used": data.get("engine_used")
                        }
                    )
                    return True
                    
                else:
                    error_data = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    async def test_engine_comparison_endpoint(self):
        """Test /api/content/compare-engines endpoint"""
        test_name = "Migration Tools - Engine Comparison"
        
        try:
            test_content = """
            API Reference: User Management
            
            The User Management API provides endpoints for creating, updating, and managing user accounts.
            
            ## Authentication
            All endpoints require Bearer token authentication.
            
            ## Endpoints
            
            ### GET /api/users
            Retrieve a list of users.
            
            Parameters:
            - limit (optional): Number of users to return (default: 20)
            - offset (optional): Number of users to skip (default: 0)
            - filter (optional): Filter criteria
            
            Response:
            ```json
            {
                "users": [
                    {
                        "id": "user123",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 150,
                "limit": 20,
                "offset": 0
            }
            ```
            
            ### POST /api/users
            Create a new user account.
            
            Request Body:
            ```json
            {
                "email": "newuser@example.com",
                "name": "Jane Smith",
                "password": "securepassword123"
            }
            ```
            
            Response:
            ```json
            {
                "id": "user456",
                "email": "newuser@example.com",
                "name": "Jane Smith",
                "created_at": "2024-01-15T10:30:00Z"
            }
            ```
            """
            
            payload = {
                "content": test_content,
                "metadata": {
                    "title": "API Reference Comparison Test",
                    "content_type": "api_documentation"
                }
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/content/compare-engines",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    required_fields = ["success", "message", "comparison"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing response fields: {missing_fields}", data)
                        return False
                    
                    comparison = data.get("comparison", {})
                    if not comparison:
                        self.log_result(test_name, False, "No comparison data returned", data)
                        return False
                    
                    # Check for engine comparison results
                    engines_compared = list(comparison.keys()) if isinstance(comparison, dict) else []
                    
                    self.log_result(
                        test_name, 
                        True, 
                        f"Engine comparison completed successfully, engines: {engines_compared}", 
                        {
                            "engines_compared": engines_compared,
                            "comparison_available": bool(comparison)
                        }
                    )
                    return True
                    
                else:
                    error_data = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    async def test_engine_statistics_endpoint(self):
        """Test /api/content/engine-statistics endpoint"""
        test_name = "Migration Tools - Engine Statistics"
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/content/engine-statistics"
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    required_fields = ["success", "message", "statistics"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, f"Missing response fields: {missing_fields}", data)
                        return False
                    
                    statistics = data.get("statistics", {})
                    if not statistics:
                        self.log_result(test_name, False, "No statistics data returned", data)
                        return False
                    
                    # Check for expected statistics fields
                    stats_keys = list(statistics.keys()) if isinstance(statistics, dict) else []
                    
                    self.log_result(
                        test_name, 
                        True, 
                        f"Engine statistics retrieved successfully, metrics: {stats_keys}", 
                        {
                            "statistics_available": bool(statistics),
                            "metrics_count": len(stats_keys)
                        }
                    )
                    return True
                    
                else:
                    error_data = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    async def test_advanced_analytics_endpoint(self):
        """Test /api/content/analytics/advanced endpoint"""
        test_name = "Analytics - Advanced Processing Metrics"
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/content/analytics/advanced"
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify analytics data structure
                    if not isinstance(data, dict):
                        self.log_result(test_name, False, "Analytics data is not a dictionary", data)
                        return False
                    
                    # Check for expected analytics fields
                    expected_fields = ["database_stats", "performance_trend", "total_processed"]
                    available_fields = [field for field in expected_fields if field in data]
                    
                    if not available_fields:
                        self.log_result(test_name, False, f"No expected analytics fields found: {list(data.keys())}", data)
                        return False
                    
                    # Check database stats if available
                    db_stats = data.get("database_stats", {})
                    if db_stats and isinstance(db_stats, dict):
                        stats_info = {
                            "total_articles": db_stats.get("total_articles", 0),
                            "advanced_articles": db_stats.get("advanced_refined_articles", 0),
                            "refined_articles": db_stats.get("refined_articles", 0)
                        }
                    else:
                        stats_info = {"database_stats": "not_available"}
                    
                    self.log_result(
                        test_name, 
                        True, 
                        f"Advanced analytics retrieved successfully, fields: {available_fields}", 
                        {
                            "available_fields": available_fields,
                            "database_stats": stats_info,
                            "total_processed": data.get("total_processed", 0)
                        }
                    )
                    return True
                    
                else:
                    error_data = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    async def test_content_library_integration(self):
        """Test that advanced engine articles are properly stored in Content Library"""
        test_name = "Content Library Integration - Advanced Engine Articles"
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/content-library"
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    articles = data.get("articles", [])
                    if not articles:
                        self.log_result(test_name, False, "No articles found in Content Library", data)
                        return False
                    
                    # Look for advanced engine articles
                    advanced_articles = []
                    for article in articles:
                        metadata = article.get("metadata", {})
                        if (metadata.get("advanced_refined_engine") or 
                            metadata.get("engine_version") == "advanced_2.1" or
                            "advanced" in str(metadata).lower()):
                            advanced_articles.append({
                                "id": article.get("id"),
                                "title": article.get("title"),
                                "engine_version": metadata.get("engine_version"),
                                "advanced_refined_engine": metadata.get("advanced_refined_engine")
                            })
                    
                    total_articles = len(articles)
                    advanced_count = len(advanced_articles)
                    
                    self.log_result(
                        test_name, 
                        True, 
                        f"Content Library integration verified: {advanced_count} advanced engine articles out of {total_articles} total", 
                        {
                            "total_articles": total_articles,
                            "advanced_engine_articles": advanced_count,
                            "advanced_percentage": (advanced_count / max(1, total_articles)) * 100,
                            "sample_advanced_articles": advanced_articles[:3]  # Show first 3 as sample
                        }
                    )
                    return True
                    
                else:
                    error_data = await response.text()
                    self.log_result(test_name, False, f"HTTP {response.status}: {error_data}")
                    return False
                    
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all Advanced Refined Engine v2.1 tests"""
        print("🚀 STARTING PHASE 2 ADVANCED REFINED ENGINE v2.1 COMPREHENSIVE TESTING")
        print("=" * 80)
        
        tests = [
            self.test_process_advanced_endpoint,
            self.test_upload_advanced_endpoint,
            self.test_batch_processing_endpoint,
            self.test_engine_comparison_endpoint,
            self.test_engine_statistics_endpoint,
            self.test_advanced_analytics_endpoint,
            self.test_content_library_integration
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                result = await test()
                if result:
                    passed += 1
                print("-" * 40)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                print("-" * 40)
        
        # Final summary
        print("=" * 80)
        print(f"🎯 PHASE 2 ADVANCED REFINED ENGINE v2.1 TESTING COMPLETE")
        print(f"📊 RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("✅ ALL TESTS PASSED - Advanced Refined Engine v2.1 is fully operational!")
        else:
            print(f"⚠️  {total - passed} tests failed - Review required")
        
        print(f"⏱️  Total testing time: {time.time() - self.start_time:.2f} seconds")
        print("=" * 80)
        
        return passed, total, self.test_results

async def main():
    """Main test execution function"""
    async with AdvancedEngineV21Tester() as tester:
        passed, total, results = await tester.run_all_tests()
        
        # Return results for integration with test_result.md
        return {
            "passed": passed,
            "total": total,
            "success_rate": (passed / total) * 100,
            "results": results
        }

if __name__ == "__main__":
    asyncio.run(main())