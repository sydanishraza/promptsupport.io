#!/usr/bin/env python3
"""
LARGE DOCUMENT REGRESSION TEST: Test with substantial content to reproduce 0 articles issue
"""

import requests
import json
import time
import os
import sys
import tempfile
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def create_large_test_document():
    """Create a large test document that might trigger the 0 articles issue"""
    content = """
# Comprehensive User Guide for Customer Management System

## Table of Contents
1. Introduction and Overview
2. Getting Started
3. User Account Management
4. Customer Data Management
5. Reporting and Analytics
6. Advanced Features
7. Troubleshooting
8. API Integration
9. Security and Compliance
10. Best Practices

## 1. Introduction and Overview

Welcome to the Customer Management System (CMS), a comprehensive platform designed to streamline your customer relationship management processes. This system provides powerful tools for managing customer data, tracking interactions, generating reports, and integrating with third-party applications.

### Key Features
- Centralized customer database
- Real-time analytics and reporting
- Automated workflow management
- Multi-channel communication tracking
- Advanced security features
- RESTful API for integrations
- Mobile-responsive interface
- Customizable dashboards

### System Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Minimum screen resolution: 1024x768
- JavaScript enabled

## 2. Getting Started

### Initial Setup
Before you begin using the Customer Management System, you'll need to complete the initial setup process. This involves configuring your organization's settings, creating user accounts, and importing existing customer data.

#### Step 1: Organization Configuration
1. Log in to the admin panel using your provided credentials
2. Navigate to Settings > Organization
3. Enter your organization details:
   - Company name
   - Address and contact information
   - Time zone settings
   - Currency preferences
   - Language settings

#### Step 2: User Account Creation
Create user accounts for your team members:
1. Go to Users > Add New User
2. Fill in the required information:
   - Full name
   - Email address
   - Role assignment
   - Department
   - Access permissions

#### Step 3: Data Import
If you have existing customer data, you can import it using our data import wizard:
1. Navigate to Data > Import
2. Select your data source (CSV, Excel, or API)
3. Map the fields to match our system
4. Review and confirm the import
5. Monitor the import progress

## 3. User Account Management

### Creating User Accounts
User accounts are the foundation of access control in the Customer Management System. Each user account defines what areas of the system a person can access and what actions they can perform.

#### User Roles
The system supports several predefined roles:
- **Administrator**: Full system access and configuration rights
- **Manager**: Access to all customer data and reporting features
- **Sales Representative**: Access to assigned customers and basic reporting
- **Support Agent**: Access to customer support features and ticket management
- **Viewer**: Read-only access to customer data and reports

#### Account Settings
Each user can customize their account settings:
- Profile information
- Password and security settings
- Notification preferences
- Dashboard layout
- Time zone and language preferences

### Password Management
Strong password policies are enforced to ensure system security:
- Minimum 8 characters
- Must include uppercase and lowercase letters
- Must include at least one number
- Must include at least one special character
- Passwords expire every 90 days
- Cannot reuse last 5 passwords

## 4. Customer Data Management

### Adding New Customers
Adding new customers to the system is straightforward:
1. Click the "Add Customer" button
2. Fill in the customer information form:
   - Basic contact details
   - Company information (if applicable)
   - Communication preferences
   - Tags and categories
   - Custom fields

### Customer Profiles
Each customer profile contains comprehensive information:
- Contact information and communication history
- Purchase history and transaction records
- Support tickets and resolution status
- Notes and internal comments
- Document attachments
- Relationship mapping

### Data Validation
The system includes robust data validation to ensure data quality:
- Email format validation
- Phone number formatting
- Address verification
- Duplicate detection
- Required field enforcement

## 5. Reporting and Analytics

### Standard Reports
The system includes several pre-built reports:
- Customer acquisition reports
- Sales performance metrics
- Support ticket analytics
- User activity reports
- Data quality assessments

### Custom Reports
Create custom reports tailored to your specific needs:
1. Navigate to Reports > Custom Reports
2. Select data sources and fields
3. Apply filters and grouping
4. Choose visualization options
5. Save and schedule the report

### Dashboard Analytics
Real-time dashboards provide instant insights:
- Key performance indicators (KPIs)
- Trend analysis charts
- Activity feeds
- Alert notifications
- Quick action buttons

## 6. Advanced Features

### Workflow Automation
Automate repetitive tasks with our workflow engine:
- Lead assignment rules
- Follow-up reminders
- Email notifications
- Status updates
- Escalation procedures

### Integration Capabilities
Connect with other business systems:
- CRM platforms
- Email marketing tools
- Accounting software
- Help desk systems
- E-commerce platforms

### API Access
Developers can access system data through our RESTful API:
- Authentication and authorization
- CRUD operations for all data types
- Webhook notifications
- Rate limiting and throttling
- Comprehensive documentation

## 7. Troubleshooting

### Common Issues
Here are solutions to frequently encountered problems:

#### Login Problems
- Verify username and password
- Check caps lock status
- Clear browser cache and cookies
- Try incognito/private browsing mode
- Contact administrator for password reset

#### Data Import Issues
- Verify file format compatibility
- Check field mapping accuracy
- Ensure data meets validation requirements
- Review error logs for specific issues
- Contact support for assistance

#### Performance Issues
- Check internet connection speed
- Clear browser cache
- Disable browser extensions
- Try different browser
- Report persistent issues to support

### Error Messages
Understanding common error messages:
- "Access Denied": Insufficient permissions
- "Data Validation Error": Invalid data format
- "Session Expired": Need to log in again
- "Server Error": System maintenance or technical issue

## 8. API Integration

### Authentication
All API requests require authentication:
```
Authorization: Bearer YOUR_API_TOKEN
Content-Type: application/json
```

### Endpoints
Key API endpoints include:
- GET /api/customers - Retrieve customer list
- POST /api/customers - Create new customer
- PUT /api/customers/{id} - Update customer
- DELETE /api/customers/{id} - Delete customer
- GET /api/reports - Access reports

### Rate Limits
API usage is subject to rate limits:
- 1000 requests per hour for standard accounts
- 5000 requests per hour for premium accounts
- 429 status code returned when limit exceeded

## 9. Security and Compliance

### Data Protection
We implement comprehensive security measures:
- SSL/TLS encryption for all data transmission
- AES-256 encryption for data at rest
- Regular security audits and penetration testing
- Multi-factor authentication support
- Role-based access control

### Compliance Standards
The system meets various compliance requirements:
- GDPR (General Data Protection Regulation)
- CCPA (California Consumer Privacy Act)
- SOC 2 Type II certification
- ISO 27001 compliance
- HIPAA compliance (healthcare customers)

### Backup and Recovery
Data protection through comprehensive backup:
- Daily automated backups
- Geographic redundancy
- Point-in-time recovery
- Disaster recovery procedures
- Regular backup testing

## 10. Best Practices

### Data Management
- Regularly clean and update customer data
- Use consistent naming conventions
- Implement data validation rules
- Monitor data quality metrics
- Train users on proper data entry

### User Training
- Provide comprehensive onboarding
- Regular training sessions
- Create user documentation
- Establish support procedures
- Monitor user adoption

### System Maintenance
- Regular software updates
- Performance monitoring
- Security patch management
- Capacity planning
- User feedback collection

## Conclusion

The Customer Management System provides a powerful platform for managing your customer relationships effectively. By following the guidelines and best practices outlined in this guide, you can maximize the value of the system and improve your customer management processes.

For additional support, please contact our customer service team or visit our online help center.
"""
    return content

def test_large_document_processing():
    """Test processing of a large document that might trigger the 0 articles issue"""
    try:
        log_test_result("🎯 TESTING LARGE DOCUMENT PROCESSING", "CRITICAL")
        log_test_result("Creating substantial test document...")
        
        test_content = create_large_test_document()
        log_test_result(f"📄 Created test document: {len(test_content)} characters, {len(test_content.split())} words")
        
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            log_test_result("📤 Uploading large document...")
            
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('large_customer_guide.txt', f, 'text/plain')}
                metadata = {'metadata': '{}'}
                
                start_time = time.time()
                response = requests.post(f"{API_BASE}/content/upload", 
                                       files=files, 
                                       data=metadata,
                                       timeout=600)  # 10 minute timeout
                
                if response.status_code != 200:
                    log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                    log_test_result(f"Response: {response.text[:500]}")
                    return False
                
                upload_data = response.json()
                job_id = upload_data.get('job_id')
                
                if not job_id:
                    log_test_result("❌ No job_id received from upload", "ERROR")
                    return False
                
                log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
        # Monitor processing with detailed logging
        log_test_result("⏳ Monitoring processing progress...")
        processing_start = time.time()
        max_wait_time = 600  # 10 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 Processing status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Extract critical metrics
                        chunks_created = status_data.get('chunks_created', 0)
                        articles_generated = status_data.get('articles_generated', 0)
                        
                        log_test_result(f"📈 LARGE DOCUMENT PROCESSING RESULTS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        log_test_result(f"   ⏱️ Processing Time: {processing_time:.1f} seconds")
                        log_test_result(f"   📊 Content Size: {len(test_content)} characters")
                        
                        # CRITICAL VERIFICATION: Check for 0 articles regression
                        if articles_generated == 0:
                            log_test_result(f"❌ CRITICAL REGRESSION CONFIRMED: 0 articles generated from large document", "CRITICAL_ERROR")
                            log_test_result("❌ LARGE DOCUMENT PROCESSING IS BROKEN", "CRITICAL_ERROR")
                            
                            # Try to get more details from the job status
                            if 'error' in status_data:
                                log_test_result(f"❌ Error details: {status_data['error']}", "ERROR")
                            
                            return False
                        else:
                            log_test_result(f"✅ Large document processed successfully: {articles_generated} articles generated", "SUCCESS")
                            
                            # Check if the number seems reasonable for the content size
                            expected_articles = max(5, len(test_content) // 2000)  # Rough estimate
                            if articles_generated < expected_articles // 2:
                                log_test_result(f"⚠️ Fewer articles than expected: got {articles_generated}, expected ~{expected_articles}", "WARNING")
                            
                            return True
                        
                    elif status == 'failed':
                        error_msg = status_data.get('error', 'Unknown error')
                        log_test_result(f"❌ Processing failed: {error_msg}", "ERROR")
                        
                        # Log detailed error for debugging
                        if 'traceback' in status_data:
                            log_test_result(f"❌ Traceback: {status_data['traceback'][:500]}...", "ERROR")
                        
                        return False
                    
                    # Continue monitoring
                    time.sleep(10)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Large document test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Large Document Regression Test")
    print("=" * 40)
    
    result = test_large_document_processing()
    
    if result:
        print("\n✅ Large document processing is working correctly")
        sys.exit(0)
    else:
        print("\n❌ Large document processing failed - regression confirmed")
        sys.exit(1)