#!/usr/bin/env python3
"""
KE-PR5 Pipeline Orchestrator Success Rate Testing
Testing V2 content processing pipeline to measure current success rate vs previous 16.7%
Focus: Verify newly implemented V2 stage classes and identify remaining missing implementations
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://promptsupport-3.preview.emergentagent.com/api"

class KE_PR5_PipelineSuccessRateTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.stage_results = {}
        
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
        
    def test_v2_engine_availability(self):
        """Test 1: Verify V2 Engine is available and operational"""
        try:
            response = requests.get(f"{self.backend_url}/engine", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2 Engine Availability", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check engine status
            if data.get("status") != "operational":
                self.log_test("V2 Engine Availability", False, f"Engine status: {data.get('status')}")
                return False
                
            # Check for V2 features
            features = data.get("features", [])
            v2_features = [f for f in features if 'v2' in f.lower() or 'pipeline' in f.lower()]
            
            if len(v2_features) < 10:  # Should have many V2 features
                self.log_test("V2 Engine Availability", False, f"Insufficient V2 features: {len(v2_features)}")
                return False
                
            self.log_test("V2 Engine Availability", True, f"V2 features: {len(v2_features)}, Engine: {data.get('engine', 'unknown')}")
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Availability", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_multidimensional_analyzer(self):
        """Test 2: Test V2MultiDimensionalAnalyzer implementation"""
        try:
            # Test with simple content to check analyzer
            test_content = """
            # API Integration Guide
            
            ## Overview
            This guide covers API integration best practices and implementation strategies.
            
            ## Authentication
            - API key authentication
            - OAuth 2.0 flow
            - Token management
            
            ## Implementation
            Step-by-step implementation guide with code examples.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=90)
            
            if response.status_code != 200:
                self.log_test("V2MultiDimensionalAnalyzer", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check if processing succeeded
            if data.get("status") != "success":
                error_msg = data.get("message", "Unknown error")
                if "analyze_normalized_document" in error_msg:
                    self.log_test("V2MultiDimensionalAnalyzer", False, "Missing analyze_normalized_document method")
                else:
                    self.log_test("V2MultiDimensionalAnalyzer", False, f"Processing failed: {error_msg}")
                return False
                
            # Check processing info
            processing_info = data.get("processing_info", {})
            if processing_info.get("engine") != "v2":
                self.log_test("V2MultiDimensionalAnalyzer", False, f"Wrong engine: {processing_info.get('engine')}")
                return False
                
            stages_completed = processing_info.get("stages_completed", 0)
            if stages_completed < 1:
                self.log_test("V2MultiDimensionalAnalyzer", False, "No stages completed")
                return False
                
            self.log_test("V2MultiDimensionalAnalyzer", True, f"Analyzer working, {stages_completed} stages completed")
            return True
            
        except Exception as e:
            self.log_test("V2MultiDimensionalAnalyzer", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_global_outline_planner(self):
        """Test 3: Test V2GlobalOutlinePlanner implementation"""
        try:
            # Test with content that should trigger outline planning
            test_content = """
            # Comprehensive API Documentation
            
            ## Getting Started
            Initial setup and configuration steps for API integration.
            
            ## Authentication Methods
            ### API Key Authentication
            Simple authentication using API keys.
            
            ### OAuth 2.0 Flow
            Advanced authentication for production systems.
            
            ## Core Endpoints
            ### Users API
            User management endpoints and operations.
            
            ### Data API
            Data retrieval and manipulation endpoints.
            
            ## Error Handling
            Comprehensive error handling strategies.
            
            ## Best Practices
            Production-ready implementation guidelines.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("V2GlobalOutlinePlanner", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                error_msg = data.get("message", "Unknown error")
                if "create_global_outline" in error_msg:
                    self.log_test("V2GlobalOutlinePlanner", False, "Missing create_global_outline method")
                else:
                    self.log_test("V2GlobalOutlinePlanner", False, f"Processing failed: {error_msg}")
                return False
                
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Should complete at least 2 stages (analyzer + outline planner)
            if stages_completed < 2:
                self.log_test("V2GlobalOutlinePlanner", False, f"Only {stages_completed} stages completed")
                return False
                
            self.log_test("V2GlobalOutlinePlanner", True, f"Outline planner working, {stages_completed} stages completed")
            return True
            
        except Exception as e:
            self.log_test("V2GlobalOutlinePlanner", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_per_article_outline_planner(self):
        """Test 4: Test V2PerArticleOutlinePlanner implementation"""
        try:
            # Test with content that should trigger per-article outline planning
            test_content = """
            # Multi-Topic Documentation System
            
            ## Topic 1: User Management
            Complete user management system with authentication, authorization, and profile management.
            
            ### User Registration
            Step-by-step user registration process.
            
            ### User Authentication
            Secure authentication mechanisms.
            
            ## Topic 2: Data Processing
            Advanced data processing capabilities with real-time analytics.
            
            ### Data Ingestion
            Multiple data source integration.
            
            ### Data Transformation
            ETL processes and data cleaning.
            
            ## Topic 3: Reporting System
            Comprehensive reporting and analytics dashboard.
            
            ### Report Generation
            Automated report creation.
            
            ### Data Visualization
            Interactive charts and graphs.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("V2PerArticleOutlinePlanner", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                error_msg = data.get("message", "Unknown error")
                if "create_per_article_outlines" in error_msg or "create_article_outline" in error_msg:
                    self.log_test("V2PerArticleOutlinePlanner", False, "Missing create_per_article_outlines method")
                else:
                    self.log_test("V2PerArticleOutlinePlanner", False, f"Processing failed: {error_msg}")
                return False
                
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Should complete at least 3 stages (analyzer + global outline + per-article outline)
            if stages_completed < 3:
                self.log_test("V2PerArticleOutlinePlanner", False, f"Only {stages_completed} stages completed")
                return False
                
            self.log_test("V2PerArticleOutlinePlanner", True, f"Per-article planner working, {stages_completed} stages completed")
            return True
            
        except Exception as e:
            self.log_test("V2PerArticleOutlinePlanner", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_prewrite_system(self):
        """Test 5: Test V2PrewriteSystem implementation"""
        try:
            # Test with content that should trigger prewrite data extraction
            test_content = """
            # Technical Implementation Guide
            
            ## Prerequisites
            - Node.js 18+ installed
            - MongoDB database setup
            - API credentials configured
            
            ## Installation Steps
            1. Clone the repository
            2. Install dependencies: npm install
            3. Configure environment variables
            4. Run database migrations
            5. Start the application: npm start
            
            ## Configuration
            Update the config.json file with your specific settings:
            - Database connection string
            - API endpoint URLs
            - Authentication tokens
            
            ## Testing
            Run the test suite to verify installation:
            ```bash
            npm test
            ```
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("V2PrewriteSystem", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                error_msg = data.get("message", "Unknown error")
                if "extract_prewrite_data" in error_msg:
                    self.log_test("V2PrewriteSystem", False, "Missing extract_prewrite_data method")
                else:
                    self.log_test("V2PrewriteSystem", False, f"Processing failed: {error_msg}")
                return False
                
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Should complete at least 4 stages (analyzer + outlines + prewrite)
            if stages_completed < 4:
                self.log_test("V2PrewriteSystem", False, f"Only {stages_completed} stages completed")
                return False
                
            self.log_test("V2PrewriteSystem", True, f"Prewrite system working, {stages_completed} stages completed")
            return True
            
        except Exception as e:
            self.log_test("V2PrewriteSystem", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_article_generator(self):
        """Test 6: Test V2ArticleGenerator implementation"""
        try:
            # Test with content that should trigger article generation
            test_content = """
            # Database Optimization Guide
            
            ## Performance Tuning
            Optimize database performance through proper indexing and query optimization.
            
            ### Index Strategies
            - Create indexes on frequently queried columns
            - Use composite indexes for multi-column queries
            - Monitor index usage and remove unused indexes
            
            ### Query Optimization
            - Analyze query execution plans
            - Optimize JOIN operations
            - Use appropriate WHERE clauses
            
            ## Maintenance Tasks
            Regular maintenance ensures optimal database performance.
            
            ### Backup Procedures
            - Schedule regular automated backups
            - Test backup restoration procedures
            - Store backups in secure locations
            
            ### Performance Monitoring
            - Monitor query performance metrics
            - Track database growth patterns
            - Set up alerting for performance issues
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=150)
            
            if response.status_code != 200:
                self.log_test("V2ArticleGenerator", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                error_msg = data.get("message", "Unknown error")
                if "generate" in error_msg or "generate_article" in error_msg:
                    self.log_test("V2ArticleGenerator", False, "Missing generate method")
                else:
                    self.log_test("V2ArticleGenerator", False, f"Processing failed: {error_msg}")
                return False
                
            # Check if articles were generated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("V2ArticleGenerator", False, "No articles generated")
                return False
                
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Should complete at least 7 stages to reach article generation
            if stages_completed < 7:
                self.log_test("V2ArticleGenerator", False, f"Only {stages_completed} stages completed")
                return False
                
            self.log_test("V2ArticleGenerator", True, f"Article generator working, {len(articles)} articles, {stages_completed} stages")
            return True
            
        except Exception as e:
            self.log_test("V2ArticleGenerator", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_style_processor(self):
        """Test 7: Test V2StyleProcessor implementation"""
        try:
            # Test style processing endpoint directly
            response = requests.get(f"{self.backend_url}/style/diagnostics", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2StyleProcessor", False, f"Style diagnostics HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check if style processing is operational
            if data.get("engine") != "v2":
                self.log_test("V2StyleProcessor", False, f"Wrong engine: {data.get('engine')}")
                return False
                
            # Check for recent style processing
            recent_results = data.get("recent_results", [])
            if not recent_results:
                self.log_test("V2StyleProcessor", False, "No recent style processing results")
                return False
                
            # Check success rate
            success_rate = data.get("success_rate", 0)
            if success_rate < 50:  # Should have reasonable success rate
                self.log_test("V2StyleProcessor", False, f"Low success rate: {success_rate}%")
                return False
                
            self.log_test("V2StyleProcessor", True, f"Style processor working, {success_rate}% success rate, {len(recent_results)} recent results")
            return True
            
        except Exception as e:
            self.log_test("V2StyleProcessor", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_validation_system(self):
        """Test 8: Test V2ValidationSystem implementation"""
        try:
            # Test with content that should trigger validation
            test_content = """
            # Security Best Practices
            
            ## Authentication Security
            Implement strong authentication mechanisms to protect user accounts.
            
            ### Password Policies
            - Minimum 12 characters
            - Mix of uppercase, lowercase, numbers, symbols
            - Regular password rotation
            - No password reuse
            
            ### Multi-Factor Authentication
            - SMS-based verification
            - App-based TOTP tokens
            - Hardware security keys
            
            ## Data Protection
            Protect sensitive data through encryption and access controls.
            
            ### Encryption Standards
            - AES-256 for data at rest
            - TLS 1.3 for data in transit
            - Key rotation policies
            
            ### Access Controls
            - Role-based permissions
            - Principle of least privilege
            - Regular access reviews
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=150)
            
            if response.status_code != 200:
                self.log_test("V2ValidationSystem", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                error_msg = data.get("message", "Unknown error")
                if "validate_content" in error_msg:
                    self.log_test("V2ValidationSystem", False, "Missing validate_content method")
                else:
                    self.log_test("V2ValidationSystem", False, f"Processing failed: {error_msg}")
                return False
                
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            
            # Should complete at least 8 stages to reach validation
            if stages_completed < 8:
                self.log_test("V2ValidationSystem", False, f"Only {stages_completed} stages completed")
                return False
                
            # Check if articles were generated and validated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("V2ValidationSystem", False, "No articles to validate")
                return False
                
            self.log_test("V2ValidationSystem", True, f"Validation system working, {stages_completed} stages completed")
            return True
            
        except Exception as e:
            self.log_test("V2ValidationSystem", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_success_rate_measurement(self):
        """Test 9: Measure overall pipeline success rate"""
        try:
            # Test with comprehensive content to measure full pipeline success
            comprehensive_content = """
            # Enterprise Software Integration Platform
            
            ## Executive Summary
            This comprehensive platform enables seamless integration between enterprise software systems, providing real-time data synchronization, automated workflow management, and advanced analytics capabilities.
            
            ## System Architecture
            
            ### Core Components
            The platform consists of several interconnected components:
            
            #### Integration Engine
            - Real-time data processing capabilities
            - Support for multiple data formats (JSON, XML, CSV, EDI)
            - Scalable microservices architecture
            - Built-in error handling and retry mechanisms
            
            #### Workflow Orchestrator
            - Visual workflow designer
            - Conditional logic and branching
            - Scheduled and event-driven execution
            - Comprehensive audit logging
            
            #### Analytics Dashboard
            - Real-time performance metrics
            - Custom report generation
            - Data visualization tools
            - Predictive analytics capabilities
            
            ## Implementation Guide
            
            ### Prerequisites
            Before implementing the platform, ensure the following requirements are met:
            
            1. **Infrastructure Requirements**
               - Kubernetes cluster (v1.20+)
               - PostgreSQL database (v13+)
               - Redis cache (v6+)
               - Load balancer with SSL termination
            
            2. **Security Requirements**
               - SSL certificates for all endpoints
               - OAuth 2.0 / SAML integration
               - Network segmentation
               - Regular security audits
            
            3. **Monitoring Requirements**
               - Prometheus metrics collection
               - Grafana dashboards
               - ELK stack for log aggregation
               - Alert manager configuration
            
            ### Installation Process
            
            #### Step 1: Environment Setup
            ```bash
            # Create namespace
            kubectl create namespace integration-platform
            
            # Apply configuration
            kubectl apply -f config/
            
            # Deploy services
            helm install platform ./charts/integration-platform
            ```
            
            #### Step 2: Database Configuration
            ```sql
            -- Create database
            CREATE DATABASE integration_platform;
            
            -- Create user
            CREATE USER platform_user WITH PASSWORD 'secure_password';
            
            -- Grant permissions
            GRANT ALL PRIVILEGES ON DATABASE integration_platform TO platform_user;
            ```
            
            #### Step 3: Service Configuration
            Update the configuration files with your environment-specific settings:
            
            ```yaml
            # config/application.yml
            server:
              port: 8080
              ssl:
                enabled: true
                key-store: /etc/ssl/keystore.p12
                key-store-password: ${SSL_KEYSTORE_PASSWORD}
            
            database:
              url: jdbc:postgresql://postgres:5432/integration_platform
              username: platform_user
              password: ${DB_PASSWORD}
            
            redis:
              host: redis
              port: 6379
              password: ${REDIS_PASSWORD}
            ```
            
            ## Configuration Management
            
            ### Environment Variables
            The platform uses environment variables for configuration:
            
            | Variable | Description | Required |
            |----------|-------------|----------|
            | DB_PASSWORD | Database password | Yes |
            | REDIS_PASSWORD | Redis password | Yes |
            | SSL_KEYSTORE_PASSWORD | SSL keystore password | Yes |
            | OAUTH_CLIENT_ID | OAuth client ID | Yes |
            | OAUTH_CLIENT_SECRET | OAuth client secret | Yes |
            
            ### Feature Flags
            Enable or disable features using configuration flags:
            
            ```json
            {
              "features": {
                "advanced_analytics": true,
                "real_time_sync": true,
                "workflow_designer": true,
                "api_rate_limiting": true,
                "audit_logging": true
              }
            }
            ```
            
            ## API Reference
            
            ### Authentication Endpoints
            
            #### POST /api/auth/login
            Authenticate user and obtain access token.
            
            **Request:**
            ```json
            {
              "username": "user@example.com",
              "password": "secure_password"
            }
            ```
            
            **Response:**
            ```json
            {
              "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
              "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
              "expires_in": 3600
            }
            ```
            
            ### Integration Endpoints
            
            #### GET /api/integrations
            List all configured integrations.
            
            **Response:**
            ```json
            {
              "integrations": [
                {
                  "id": "salesforce-crm",
                  "name": "Salesforce CRM Integration",
                  "status": "active",
                  "last_sync": "2024-01-15T10:30:00Z"
                }
              ]
            }
            ```
            
            #### POST /api/integrations/{id}/sync
            Trigger manual synchronization for specific integration.
            
            ## Troubleshooting
            
            ### Common Issues
            
            #### Connection Timeouts
            **Symptoms:** Integration fails with timeout errors
            **Solution:** 
            1. Check network connectivity
            2. Verify firewall rules
            3. Increase timeout values in configuration
            
            #### Memory Issues
            **Symptoms:** Out of memory errors in logs
            **Solution:**
            1. Increase JVM heap size
            2. Optimize query performance
            3. Implement data pagination
            
            #### Authentication Failures
            **Symptoms:** 401 Unauthorized responses
            **Solution:**
            1. Verify OAuth configuration
            2. Check token expiration
            3. Validate client credentials
            
            ### Performance Optimization
            
            #### Database Optimization
            - Create appropriate indexes
            - Optimize query performance
            - Implement connection pooling
            - Regular maintenance tasks
            
            #### Caching Strategy
            - Implement Redis caching
            - Cache frequently accessed data
            - Set appropriate TTL values
            - Monitor cache hit rates
            
            ## Monitoring and Alerting
            
            ### Key Metrics
            Monitor these critical metrics:
            
            - **Throughput:** Messages processed per second
            - **Latency:** Average processing time
            - **Error Rate:** Percentage of failed operations
            - **Resource Usage:** CPU, memory, disk utilization
            
            ### Alert Configuration
            Set up alerts for:
            
            ```yaml
            alerts:
              - name: high_error_rate
                condition: error_rate > 5%
                duration: 5m
                severity: critical
              
              - name: high_latency
                condition: avg_latency > 10s
                duration: 2m
                severity: warning
            ```
            
            ## Security Considerations
            
            ### Data Encryption
            - All data encrypted in transit using TLS 1.3
            - Sensitive data encrypted at rest using AES-256
            - Regular key rotation policies
            
            ### Access Control
            - Role-based access control (RBAC)
            - Multi-factor authentication required
            - Regular access reviews and audits
            
            ### Compliance
            - GDPR compliance for EU data
            - SOC 2 Type II certification
            - Regular security assessments
            
            ## Conclusion
            
            This enterprise integration platform provides a robust, scalable solution for connecting disparate software systems. With proper implementation and monitoring, it enables organizations to achieve seamless data flow and improved operational efficiency.
            
            For additional support and documentation, visit our knowledge base or contact the support team.
            """
            
            payload = {
                "content": comprehensive_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=300)
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                self.log_test("Pipeline Success Rate Measurement", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                error_msg = data.get("message", "Unknown error")
                self.log_test("Pipeline Success Rate Measurement", False, f"Processing failed: {error_msg}")
                return False
                
            # Analyze pipeline completion
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            total_stages = 17  # Expected total stages in V2 pipeline
            
            success_rate = (stages_completed / total_stages) * 100
            
            # Check articles generated
            articles = data.get("articles", [])
            
            # Check for stage errors
            stage_errors = processing_info.get("stage_errors", [])
            critical_errors = len([err for err in stage_errors if err.get("severity") == "critical"])
            
            self.log_test("Pipeline Success Rate Measurement", True, 
                         f"Success rate: {success_rate:.1f}% ({stages_completed}/{total_stages} stages), "
                         f"{len(articles)} articles, {critical_errors} critical errors, {processing_time:.1f}s")
            
            # Store detailed results for analysis
            self.stage_results = {
                "stages_completed": stages_completed,
                "total_stages": total_stages,
                "success_rate": success_rate,
                "articles_generated": len(articles),
                "critical_errors": critical_errors,
                "processing_time": processing_time,
                "stage_errors": stage_errors
            }
            
            return True
            
        except Exception as e:
            self.log_test("Pipeline Success Rate Measurement", False, f"Exception: {str(e)}")
            return False
    
    def test_remaining_v2_implementations_needed(self):
        """Test 10: Identify remaining V2 implementations needed for 100% success"""
        try:
            # Analyze stage errors from previous test
            if not self.stage_results:
                self.log_test("Remaining V2 Implementations Analysis", False, "No stage results available")
                return False
                
            stage_errors = self.stage_results.get("stage_errors", [])
            stages_completed = self.stage_results.get("stages_completed", 0)
            
            # Identify missing implementations
            missing_implementations = []
            
            # Check for specific method errors
            for error in stage_errors:
                error_msg = error.get("message", "")
                if "has no attribute" in error_msg:
                    missing_implementations.append(error_msg)
            
            # Expected V2 classes and their key methods
            expected_implementations = {
                "V2MultiDimensionalAnalyzer": "analyze_normalized_document",
                "V2GlobalOutlinePlanner": "create_global_outline", 
                "V2PerArticleOutlinePlanner": "create_per_article_outlines",
                "V2PrewriteSystem": "extract_prewrite_data",
                "V2ArticleGenerator": "generate",
                "V2StyleProcessor": "process_style",
                "V2ValidationSystem": "validate_content",
                "V2RelatedLinksSystem": "generate_related_links",
                "V2GapFillingSystem": "fill_gaps",
                "V2EvidenceTaggingSystem": "tag_evidence",
                "V2CodeNormalizationSystem": "normalize_code_blocks",
                "V2CrossArticleQASystem": "perform_cross_article_qa",
                "V2AdaptiveAdjustmentSystem": "adjust_article_balance",
                "V2PublishingSystem": "publish_v2_content",
                "V2VersioningSystem": "create_version",
                "V2ReviewSystem": "enqueue_for_review"
            }
            
            # Calculate implementation progress
            total_expected = len(expected_implementations)
            implemented_count = max(0, stages_completed - 1)  # Subtract 1 for content extraction
            implementation_rate = (implemented_count / total_expected) * 100
            
            details = f"Implementation rate: {implementation_rate:.1f}% ({implemented_count}/{total_expected} classes), "
            details += f"Missing implementations: {len(missing_implementations)}"
            
            if missing_implementations:
                details += f", Errors: {missing_implementations[:3]}"  # Show first 3 errors
            
            self.log_test("Remaining V2 Implementations Analysis", True, details)
            return True
            
        except Exception as e:
            self.log_test("Remaining V2 Implementations Analysis", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all KE-PR5 Pipeline Orchestrator success rate tests"""
        print("🎯 KE-PR5 PIPELINE ORCHESTRATOR SUCCESS RATE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("Focus: Measuring current success rate vs previous 16.7%")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_engine_availability,
            self.test_v2_multidimensional_analyzer,
            self.test_v2_global_outline_planner,
            self.test_v2_per_article_outline_planner,
            self.test_v2_prewrite_system,
            self.test_v2_article_generator,
            self.test_v2_style_processor,
            self.test_v2_validation_system,
            self.test_pipeline_success_rate_measurement,
            self.test_remaining_v2_implementations_needed
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
        print("🎯 KE-PR5 PIPELINE ORCHESTRATOR SUCCESS RATE SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Test Success Rate: {success_rate:.1f}%")
        print()
        
        # Pipeline success rate analysis
        if self.stage_results:
            pipeline_success = self.stage_results.get("success_rate", 0)
            stages_completed = self.stage_results.get("stages_completed", 0)
            articles_generated = self.stage_results.get("articles_generated", 0)
            
            print("📊 PIPELINE SUCCESS RATE ANALYSIS:")
            print(f"Current Pipeline Success Rate: {pipeline_success:.1f}%")
            print(f"Previous Success Rate: 16.7%")
            
            if pipeline_success > 16.7:
                improvement = pipeline_success - 16.7
                print(f"✅ IMPROVEMENT: +{improvement:.1f}% increase from baseline")
            else:
                print(f"❌ NO IMPROVEMENT: Still at or below 16.7% baseline")
            
            print(f"Stages Completed: {stages_completed}/17")
            print(f"Articles Generated: {articles_generated}")
            print()
        
        # Overall assessment
        if success_rate >= 80:
            print("🎉 KE-PR5 PIPELINE ORCHESTRATOR: EXCELLENT - Major improvements achieved!")
        elif success_rate >= 60:
            print("✅ KE-PR5 PIPELINE ORCHESTRATOR: GOOD - Significant progress made")
        elif success_rate >= 40:
            print("⚠️ KE-PR5 PIPELINE ORCHESTRATOR: PARTIAL - Some improvements detected")
        else:
            print("❌ KE-PR5 PIPELINE ORCHESTRATOR: NEEDS ATTENTION - Limited progress")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = KE_PR5_PipelineSuccessRateTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 60 else 1)