#!/usr/bin/env python3
"""
CRITICAL BUG INVESTIGATION: Document Type Processing Inconsistency
Testing why only one document gets comprehensive processing while others are limited to 5 articles

INVESTIGATION FOCUS:
- Test different document types (DOCX vs PDF) with similar content
- Analyze processing path differences
- Check ultra-large document detection consistency
- Find hidden processing constraints
- Test outline generation across document types
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import tempfile
import io

# Backend URL from frontend .env
BACKEND_URL = "https://smartdoc-v2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def create_test_content(content_type="technical_manual", size="large"):
    """Create test content simulating different document types"""
    
    if content_type == "technical_manual":
        content = """# Technical Implementation Manual
        
## Chapter 1: System Overview
This comprehensive technical manual covers advanced system implementation procedures and best practices for enterprise-level deployment.

### 1.1 Architecture Overview
The system architecture follows a microservices pattern with distributed components across multiple layers including presentation, business logic, data access, and infrastructure layers.

### 1.2 Core Components
- Authentication Service: Handles user authentication and authorization
- Data Processing Engine: Manages data transformation and validation
- API Gateway: Routes requests and handles load balancing
- Database Layer: Persistent storage with replication
- Monitoring System: Real-time system health monitoring

### 1.3 Security Framework
Security is implemented at multiple levels including network security, application security, data encryption, and access controls.

## Chapter 2: Installation and Setup
This chapter provides detailed installation procedures for different environments.

### 2.1 Prerequisites
Before beginning installation, ensure the following prerequisites are met:
- Operating System: Linux Ubuntu 20.04 or higher
- Memory: Minimum 16GB RAM, recommended 32GB
- Storage: Minimum 500GB SSD storage
- Network: High-speed internet connection
- Database: PostgreSQL 13 or higher

### 2.2 Environment Preparation
Prepare the environment by installing required dependencies and configuring system settings.

### 2.3 Installation Steps
1. Download the installation package from the official repository
2. Extract the package to the target directory
3. Run the installation script with appropriate permissions
4. Configure environment variables and system paths
5. Initialize the database schema and seed data
6. Start the application services in the correct order
7. Verify installation by running health checks

## Chapter 3: Configuration Management
Configuration management is critical for proper system operation.

### 3.1 Configuration Files
The system uses multiple configuration files for different components:
- application.yml: Main application configuration
- database.properties: Database connection settings
- security.conf: Security policies and rules
- logging.properties: Logging configuration

### 3.2 Environment-Specific Settings
Different environments require specific configuration adjustments:
- Development: Debug logging, local database connections
- Staging: Production-like settings with test data
- Production: Optimized performance settings, secure connections

### 3.3 Configuration Validation
Always validate configuration changes before deployment to prevent system failures.

## Chapter 4: API Documentation
The system provides comprehensive REST APIs for integration.

### 4.1 Authentication APIs
- POST /api/auth/login: User authentication
- POST /api/auth/logout: User logout
- GET /api/auth/profile: User profile information
- PUT /api/auth/profile: Update user profile

### 4.2 Data Management APIs
- GET /api/data: Retrieve data records
- POST /api/data: Create new data record
- PUT /api/data/{id}: Update existing record
- DELETE /api/data/{id}: Delete data record

### 4.3 System Management APIs
- GET /api/system/health: System health check
- GET /api/system/metrics: Performance metrics
- POST /api/system/backup: Initiate system backup
- GET /api/system/logs: Retrieve system logs

## Chapter 5: Troubleshooting Guide
Common issues and their solutions.

### 5.1 Connection Issues
If experiencing connection problems:
1. Check network connectivity
2. Verify firewall settings
3. Confirm service status
4. Review error logs

### 5.2 Performance Issues
For performance problems:
1. Monitor system resources
2. Check database performance
3. Review application logs
4. Analyze network latency

### 5.3 Data Issues
When encountering data problems:
1. Verify data integrity
2. Check backup status
3. Review data validation rules
4. Confirm user permissions

## Chapter 6: Advanced Features
Advanced functionality for power users.

### 6.1 Custom Integrations
The system supports custom integrations through:
- Webhook endpoints
- Custom API extensions
- Plugin architecture
- Event-driven processing

### 6.2 Scalability Options
Scale the system using:
- Horizontal scaling with load balancers
- Vertical scaling with resource upgrades
- Database sharding for large datasets
- Caching strategies for performance

### 6.3 Monitoring and Alerting
Implement comprehensive monitoring:
- Real-time dashboards
- Automated alerting rules
- Performance metrics collection
- Log aggregation and analysis

## Chapter 7: Maintenance Procedures
Regular maintenance ensures optimal performance.

### 7.1 Backup Procedures
- Daily automated backups
- Weekly full system backups
- Monthly backup verification
- Disaster recovery testing

### 7.2 Update Procedures
- Security patch management
- Feature update deployment
- Database schema migrations
- Configuration updates

### 7.3 Performance Optimization
- Regular performance audits
- Database optimization
- Cache management
- Resource utilization analysis

## Conclusion
This manual provides comprehensive coverage of system implementation, configuration, and maintenance procedures for successful enterprise deployment."""

    elif content_type == "user_guide":
        content = """# User Guide: Customer Summary Screen

## Introduction
Welcome to the Customer Summary Screen User Guide. This comprehensive guide will help you navigate and utilize all features of the customer summary interface.

## Getting Started
The Customer Summary Screen is your central hub for viewing customer information, transaction history, and account details.

### Accessing the Screen
1. Log into the system using your credentials
2. Navigate to the Customers section
3. Select a customer from the list
4. The Customer Summary Screen will display

### Screen Layout
The screen is divided into several key sections:
- Customer Information Panel
- Transaction History
- Account Status
- Quick Actions Menu
- Related Documents

## Customer Information Panel
This panel displays essential customer details including contact information, account status, and key metrics.

### Personal Information
- Full name and contact details
- Account creation date
- Last activity timestamp
- Customer tier and status

### Account Metrics
- Total transaction volume
- Average transaction amount
- Account balance
- Credit limit and utilization

## Transaction History
View detailed transaction records with filtering and search capabilities.

### Viewing Transactions
- Transactions are displayed in chronological order
- Use date filters to narrow results
- Search by transaction type or amount
- Export data for external analysis

### Transaction Details
Each transaction shows:
- Date and time
- Transaction type
- Amount and currency
- Status and reference number
- Associated fees or charges

## Account Management
Manage customer accounts directly from the summary screen.

### Status Changes
- Update account status
- Modify credit limits
- Apply holds or restrictions
- Process account closures

### Document Management
- Upload customer documents
- View existing files
- Generate reports
- Send communications

## Quick Actions
Perform common tasks quickly using the actions menu.

### Available Actions
- Process payments
- Generate statements
- Schedule callbacks
- Create support tickets
- Update contact information

## Reporting Features
Generate various reports for customer analysis.

### Standard Reports
- Account summary report
- Transaction history report
- Activity analysis report
- Compliance documentation

### Custom Reports
- Create custom report templates
- Schedule automated reports
- Export in multiple formats
- Share with team members

## Troubleshooting
Common issues and solutions for the Customer Summary Screen.

### Display Issues
If information is not displaying correctly:
1. Refresh the browser
2. Clear cache and cookies
3. Check internet connection
4. Contact technical support

### Performance Issues
For slow loading times:
1. Close unnecessary browser tabs
2. Check system resources
3. Verify network speed
4. Report persistent issues

## Best Practices
Recommendations for optimal use of the Customer Summary Screen.

### Data Accuracy
- Verify customer information regularly
- Update contact details promptly
- Maintain accurate transaction records
- Document all customer interactions

### Security Considerations
- Log out when finished
- Don't share login credentials
- Report suspicious activity
- Follow data protection policies

## Advanced Features
Explore advanced functionality for power users.

### Customization Options
- Personalize screen layout
- Configure default filters
- Set up automated alerts
- Create custom workflows

### Integration Capabilities
- Connect with external systems
- Import/export data
- API access for developers
- Third-party tool integration

## Support and Training
Resources for additional help and training.

### Help Resources
- Online documentation
- Video tutorials
- FAQ section
- User community forums

### Training Options
- Live training sessions
- Self-paced courses
- Certification programs
- Advanced workshops

## Conclusion
The Customer Summary Screen provides comprehensive tools for effective customer management. Regular use of this guide will help maximize your productivity and ensure optimal customer service."""

    elif content_type == "api_documentation":
        content = """# API Integration Documentation

## Overview
This comprehensive API documentation provides detailed information for integrating with our platform services.

## Authentication
All API requests require proper authentication using API keys or OAuth tokens.

### API Key Authentication
Include your API key in the request header:
```
Authorization: Bearer YOUR_API_KEY
```

### OAuth 2.0 Authentication
For OAuth authentication, follow the standard OAuth 2.0 flow:
1. Redirect user to authorization endpoint
2. Receive authorization code
3. Exchange code for access token
4. Use access token for API requests

## Base URL
All API endpoints are relative to the base URL:
```
https://api.example.com/v1
```

## Rate Limiting
API requests are subject to rate limiting:
- 1000 requests per hour for standard accounts
- 5000 requests per hour for premium accounts
- Rate limit headers included in responses

## Data Formats
The API supports JSON format for both requests and responses.

### Request Format
```json
{
  "data": {
    "attribute1": "value1",
    "attribute2": "value2"
  }
}
```

### Response Format
```json
{
  "success": true,
  "data": {
    "id": "12345",
    "attributes": {}
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## User Management Endpoints

### Create User
Create a new user account.

**Endpoint:** `POST /users`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_12345",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Get User
Retrieve user information by ID.

**Endpoint:** `GET /users/{user_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_12345",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Update User
Update user information.

**Endpoint:** `PUT /users/{user_id}`

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

### Delete User
Delete a user account.

**Endpoint:** `DELETE /users/{user_id}`

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

## Data Management Endpoints

### List Records
Retrieve a list of data records with pagination.

**Endpoint:** `GET /data`

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Records per page (default: 20, max: 100)
- `sort`: Sort field and direction (e.g., "created_at:desc")
- `filter`: Filter criteria

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "record_12345",
      "title": "Sample Record",
      "content": "Record content",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "pages": 8
  }
}
```

### Create Record
Create a new data record.

**Endpoint:** `POST /data`

**Request Body:**
```json
{
  "title": "New Record",
  "content": "Record content",
  "category": "general",
  "tags": ["tag1", "tag2"]
}
```

### Get Record
Retrieve a specific data record.

**Endpoint:** `GET /data/{record_id}`

### Update Record
Update an existing data record.

**Endpoint:** `PUT /data/{record_id}`

### Delete Record
Delete a data record.

**Endpoint:** `DELETE /data/{record_id}`

## File Upload Endpoints

### Upload File
Upload a file to the system.

**Endpoint:** `POST /files`

**Request:** Multipart form data with file

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "file_12345",
    "filename": "document.pdf",
    "size": 1024000,
    "mime_type": "application/pdf",
    "url": "https://cdn.example.com/files/document.pdf"
  }
}
```

### Get File
Retrieve file information.

**Endpoint:** `GET /files/{file_id}`

### Delete File
Delete a file from the system.

**Endpoint:** `DELETE /files/{file_id}`

## Webhook Configuration

### Create Webhook
Set up a webhook endpoint for event notifications.

**Endpoint:** `POST /webhooks`

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["user.created", "data.updated"],
  "secret": "webhook_secret"
}
```

### List Webhooks
Get all configured webhooks.

**Endpoint:** `GET /webhooks`

### Update Webhook
Modify webhook configuration.

**Endpoint:** `PUT /webhooks/{webhook_id}`

### Delete Webhook
Remove a webhook configuration.

**Endpoint:** `DELETE /webhooks/{webhook_id}`

## Error Handling
The API uses standard HTTP status codes and provides detailed error messages.

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### Common Error Codes
- 400: Bad Request - Invalid input data
- 401: Unauthorized - Invalid or missing authentication
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Resource not found
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - Server error

## SDK and Libraries
Official SDKs are available for popular programming languages:
- JavaScript/Node.js
- Python
- PHP
- Ruby
- Java
- C#

## Testing
Use our sandbox environment for testing:
- Base URL: https://sandbox-api.example.com/v1
- Test API keys provided in developer dashboard
- No rate limiting in sandbox

## Support
For API support and questions:
- Documentation: https://docs.example.com
- Support email: api-support@example.com
- Developer forum: https://forum.example.com
- Status page: https://status.example.com

## Changelog
Track API changes and updates:
- Version 1.3: Added webhook support
- Version 1.2: Enhanced error handling
- Version 1.1: Added file upload endpoints
- Version 1.0: Initial API release"""

    # Adjust content size based on parameter
    if size == "small":
        # Return first 2000 characters
        return content[:2000]
    elif size == "medium":
        # Return first 5000 characters
        return content[:5000]
    else:  # large
        # Return full content
        return content

def create_test_docx_file(content, filename):
    """Create a test DOCX file with given content"""
    try:
        # For testing purposes, create a simple text file with .docx extension
        # In a real scenario, you'd use python-docx to create proper DOCX files
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        log_test_result(f"❌ Error creating test DOCX file: {e}", "ERROR")
        return None

def create_test_pdf_file(content, filename):
    """Create a test PDF file with given content"""
    try:
        # For testing purposes, create a simple text file with .pdf extension
        # In a real scenario, you'd use reportlab or similar to create proper PDF files
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        log_test_result(f"❌ Error creating test PDF file: {e}", "ERROR")
        return None

def test_backend_health():
    """Test backend health and connectivity"""
    try:
        log_test_result("Testing backend health check...")
        response = requests.get(f"{API_BASE}/health", timeout=30)
        
        if response.status_code == 200:
            log_test_result("✅ Backend health check PASSED", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ Backend health check FAILED: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend health check FAILED: {e}", "ERROR")
        return False

def process_document_and_analyze(file_path, file_type, content_description):
    """Process a document and analyze the results"""
    try:
        log_test_result(f"📤 Processing {content_description} ({file_type})...")
        
        # Determine MIME type
        mime_types = {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pdf': 'application/pdf'
        }
        
        mime_type = mime_types.get(file_type.lower(), 'application/octet-stream')
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, mime_type)}
            
            # Start processing
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=600)
            
            if response.status_code != 200:
                log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                log_test_result(f"Response: {response.text[:500]}")
                return None
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if not job_id:
                log_test_result("❌ No job_id received from upload", "ERROR")
                return None
            
            log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing progress...")
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return None
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Extract metrics
                        result = {
                            'job_id': job_id,
                            'processing_time': processing_time,
                            'chunks_created': status_data.get('chunks_created', 0),
                            'articles_generated': status_data.get('articles_generated', 0),
                            'file_type': file_type,
                            'content_description': content_description,
                            'status_data': status_data
                        }
                        
                        log_test_result(f"📈 RESULTS for {content_description}:")
                        log_test_result(f"   📚 Chunks Created: {result['chunks_created']}")
                        log_test_result(f"   📄 Articles Generated: {result['articles_generated']}")
                        log_test_result(f"   ⏱️ Processing Time: {result['processing_time']:.1f}s")
                        
                        return result
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return None
                    
                    # Continue monitoring
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Document processing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None

def test_document_type_processing_differences():
    """
    CRITICAL TEST: Compare processing results across different document types
    """
    try:
        log_test_result("🎯 STARTING DOCUMENT TYPE PROCESSING INVESTIGATION", "CRITICAL")
        
        # Test scenarios
        test_scenarios = [
            {
                'content_type': 'technical_manual',
                'size': 'large',
                'file_type': 'docx',
                'description': 'Large Technical Manual (DOCX)'
            },
            {
                'content_type': 'technical_manual', 
                'size': 'large',
                'file_type': 'pdf',
                'description': 'Large Technical Manual (PDF)'
            },
            {
                'content_type': 'user_guide',
                'size': 'large', 
                'file_type': 'docx',
                'description': 'User Guide (DOCX)'
            },
            {
                'content_type': 'user_guide',
                'size': 'large',
                'file_type': 'pdf', 
                'description': 'User Guide (PDF)'
            },
            {
                'content_type': 'api_documentation',
                'size': 'large',
                'file_type': 'docx',
                'description': 'API Documentation (DOCX)'
            },
            {
                'content_type': 'api_documentation',
                'size': 'large',
                'file_type': 'pdf',
                'description': 'API Documentation (PDF)'
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            log_test_result(f"🧪 Testing scenario: {scenario['description']}")
            
            # Create test content
            content = create_test_content(scenario['content_type'], scenario['size'])
            
            # Create test file
            if scenario['file_type'] == 'docx':
                file_path = create_test_docx_file(content, f"test_{scenario['content_type']}.docx")
            else:
                file_path = create_test_pdf_file(content, f"test_{scenario['content_type']}.pdf")
            
            if not file_path:
                log_test_result(f"❌ Failed to create test file for {scenario['description']}", "ERROR")
                continue
            
            # Process document
            result = process_document_and_analyze(file_path, scenario['file_type'], scenario['description'])
            
            if result:
                result.update(scenario)
                results.append(result)
            
            # Clean up test file
            try:
                os.unlink(file_path)
            except:
                pass
            
            # Wait between tests to avoid overwhelming the system
            time.sleep(10)
        
        # Analyze results
        log_test_result("📊 ANALYSIS OF DOCUMENT TYPE PROCESSING DIFFERENCES", "ANALYSIS")
        
        if not results:
            log_test_result("❌ No results to analyze", "ERROR")
            return False
        
        # Group by file type
        docx_results = [r for r in results if r['file_type'] == 'docx']
        pdf_results = [r for r in results if r['file_type'] == 'pdf']
        
        log_test_result(f"📄 DOCX Results ({len(docx_results)} tests):")
        for result in docx_results:
            log_test_result(f"   {result['description']}: {result['articles_generated']} articles")
        
        log_test_result(f"📄 PDF Results ({len(pdf_results)} tests):")
        for result in pdf_results:
            log_test_result(f"   {result['description']}: {result['articles_generated']} articles")
        
        # Calculate averages
        if docx_results:
            docx_avg = sum(r['articles_generated'] for r in docx_results) / len(docx_results)
            log_test_result(f"📊 DOCX Average Articles: {docx_avg:.1f}")
        
        if pdf_results:
            pdf_avg = sum(r['articles_generated'] for r in pdf_results) / len(pdf_results)
            log_test_result(f"📊 PDF Average Articles: {pdf_avg:.1f}")
        
        # Check for inconsistencies
        all_article_counts = [r['articles_generated'] for r in results]
        min_articles = min(all_article_counts)
        max_articles = max(all_article_counts)
        
        if max_articles > min_articles * 2:  # Significant difference
            log_test_result(f"🚨 CRITICAL INCONSISTENCY DETECTED:", "CRITICAL")
            log_test_result(f"   Minimum articles generated: {min_articles}")
            log_test_result(f"   Maximum articles generated: {max_articles}")
            log_test_result(f"   Ratio: {max_articles/min_articles:.1f}x difference")
            
            # Find which scenarios produced different results
            high_performers = [r for r in results if r['articles_generated'] == max_articles]
            low_performers = [r for r in results if r['articles_generated'] == min_articles]
            
            log_test_result(f"🔍 HIGH PERFORMERS ({max_articles} articles):")
            for r in high_performers:
                log_test_result(f"   - {r['description']} ({r['file_type'].upper()})")
            
            log_test_result(f"🔍 LOW PERFORMERS ({min_articles} articles):")
            for r in low_performers:
                log_test_result(f"   - {r['description']} ({r['file_type'].upper()})")
            
            return False
        else:
            log_test_result(f"✅ CONSISTENT PROCESSING: Article counts within acceptable range ({min_articles}-{max_articles})", "SUCCESS")
            return True
    
    except Exception as e:
        log_test_result(f"❌ Document type investigation failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_ultra_large_detection_consistency():
    """Test if ultra-large document detection works consistently across document types"""
    try:
        log_test_result("🔍 TESTING ULTRA-LARGE DOCUMENT DETECTION CONSISTENCY", "CRITICAL")
        
        # Create very large content to trigger ultra-large detection
        large_content = create_test_content("technical_manual", "large")
        # Multiply content to make it ultra-large
        ultra_large_content = large_content * 10  # Make it 10x larger
        
        log_test_result(f"📏 Created ultra-large content: {len(ultra_large_content):,} characters")
        
        # Test with both DOCX and PDF
        test_cases = [
            {'type': 'docx', 'description': 'Ultra-Large DOCX'},
            {'type': 'pdf', 'description': 'Ultra-Large PDF'}
        ]
        
        results = []
        
        for case in test_cases:
            log_test_result(f"🧪 Testing {case['description']}")
            
            # Create test file
            if case['type'] == 'docx':
                file_path = create_test_docx_file(ultra_large_content, "ultra_large_test.docx")
            else:
                file_path = create_test_pdf_file(ultra_large_content, "ultra_large_test.pdf")
            
            if not file_path:
                continue
            
            # Process and analyze
            result = process_document_and_analyze(file_path, case['type'], case['description'])
            
            if result:
                results.append(result)
            
            # Clean up
            try:
                os.unlink(file_path)
            except:
                pass
            
            time.sleep(10)
        
        # Analyze ultra-large detection consistency
        if len(results) >= 2:
            docx_result = next((r for r in results if r['file_type'] == 'docx'), None)
            pdf_result = next((r for r in results if r['file_type'] == 'pdf'), None)
            
            if docx_result and pdf_result:
                docx_articles = docx_result['articles_generated']
                pdf_articles = pdf_result['articles_generated']
                
                log_test_result(f"📊 ULTRA-LARGE DETECTION RESULTS:")
                log_test_result(f"   DOCX: {docx_articles} articles")
                log_test_result(f"   PDF: {pdf_articles} articles")
                
                if abs(docx_articles - pdf_articles) <= 2:  # Allow small variance
                    log_test_result("✅ ULTRA-LARGE DETECTION CONSISTENT", "SUCCESS")
                    return True
                else:
                    log_test_result(f"❌ ULTRA-LARGE DETECTION INCONSISTENT: {abs(docx_articles - pdf_articles)} article difference", "ERROR")
                    return False
        
        log_test_result("⚠️ Insufficient results for ultra-large detection analysis", "WARNING")
        return False
        
    except Exception as e:
        log_test_result(f"❌ Ultra-large detection test failed: {e}", "ERROR")
        return False

def check_content_library_for_processing_patterns():
    """Check Content Library for patterns in article generation"""
    try:
        log_test_result("🔍 ANALYZING CONTENT LIBRARY FOR PROCESSING PATTERNS", "ANALYSIS")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📚 Content Library Analysis: {total_articles} total articles")
        
        # Analyze articles by source document type
        docx_articles = []
        pdf_articles = []
        other_articles = []
        
        for article in articles:
            source = article.get('source_document', '').lower()
            title = article.get('title', '').lower()
            
            if '.docx' in source or 'docx' in title:
                docx_articles.append(article)
            elif '.pdf' in source or 'pdf' in title:
                pdf_articles.append(article)
            else:
                other_articles.append(article)
        
        log_test_result(f"📊 ARTICLE DISTRIBUTION BY SOURCE TYPE:")
        log_test_result(f"   DOCX-sourced articles: {len(docx_articles)}")
        log_test_result(f"   PDF-sourced articles: {len(pdf_articles)}")
        log_test_result(f"   Other-sourced articles: {len(other_articles)}")
        
        # Look for specific patterns mentioned in the bug report
        customer_guide_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            source = article.get('source_document', '').lower()
            
            if 'customer' in title or 'customer' in source:
                customer_guide_articles.append(article)
        
        if customer_guide_articles:
            log_test_result(f"🎯 CUSTOMER GUIDE ARTICLES FOUND: {len(customer_guide_articles)}")
            
            # Show details of customer guide articles
            for i, article in enumerate(customer_guide_articles[:10]):  # Show first 10
                title = article.get('title', 'Untitled')
                created = article.get('created_at', 'Unknown')
                log_test_result(f"   {i+1}. {title[:60]}... (Created: {created})")
            
            if len(customer_guide_articles) > 30:
                log_test_result(f"🚨 CONFIRMED: Customer guide generated {len(customer_guide_articles)} articles (matches bug report)", "CRITICAL")
            else:
                log_test_result(f"⚠️ Customer guide articles: {len(customer_guide_articles)} (less than reported 38)", "WARNING")
        else:
            log_test_result("❌ No customer guide articles found in Content Library", "ERROR")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Content Library analysis failed: {e}", "ERROR")
        return False

def main():
    """Main test execution"""
    log_test_result("🚀 STARTING CRITICAL BUG INVESTIGATION: Document Type Processing Inconsistency", "START")
    
    # Test backend health first
    if not test_backend_health():
        log_test_result("❌ Backend health check failed, aborting tests", "ABORT")
        return False
    
    # Run investigation tests
    tests = [
        ("Document Type Processing Differences", test_document_type_processing_differences),
        ("Ultra-Large Detection Consistency", test_ultra_large_detection_consistency),
        ("Content Library Pattern Analysis", check_content_library_for_processing_patterns)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        log_test_result(f"🧪 Running test: {test_name}")
        try:
            result = test_func()
            results[test_name] = result
            status = "PASSED" if result else "FAILED"
            log_test_result(f"📋 Test '{test_name}': {status}")
        except Exception as e:
            log_test_result(f"❌ Test '{test_name}' crashed: {e}", "ERROR")
            results[test_name] = False
    
    # Final summary
    log_test_result("📊 FINAL INVESTIGATION SUMMARY", "SUMMARY")
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    log_test_result(f"Tests Passed: {passed_tests}/{total_tests}")
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        log_test_result("🎉 ALL INVESTIGATION TESTS PASSED", "SUCCESS")
        return True
    else:
        log_test_result("🚨 INVESTIGATION REVEALED CRITICAL ISSUES", "CRITICAL")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)