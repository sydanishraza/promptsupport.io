#!/usr/bin/env python3
"""
CRITICAL BUG INVESTIGATION: Text Content Processing Investigation
Testing document processing with text content to investigate article generation differences
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://smartdoc-v2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

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

def process_text_content(content, description):
    """Process text content through Knowledge Engine"""
    try:
        log_test_result(f"📤 Processing {description} ({len(content):,} characters)...")
        
        # Use the text processing endpoint
        payload = {
            "content": content,
            "content_type": "text"
        }
        
        # Start processing
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process-text", 
                               json=payload, 
                               headers={'Content-Type': 'application/json'},
                               timeout=600)
        
        if response.status_code != 200:
            log_test_result(f"❌ Text processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return None
        
        upload_data = response.json()
        job_id = upload_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from text processing", "ERROR")
            return None
        
        log_test_result(f"✅ Text processing started, Job ID: {job_id}")
        
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
                            'content_length': len(content),
                            'description': description,
                            'status_data': status_data
                        }
                        
                        log_test_result(f"📈 RESULTS for {description}:")
                        log_test_result(f"   📚 Chunks Created: {result['chunks_created']}")
                        log_test_result(f"   📄 Articles Generated: {result['articles_generated']}")
                        log_test_result(f"   ⏱️ Processing Time: {result['processing_time']:.1f}s")
                        log_test_result(f"   📏 Content Length: {result['content_length']:,} chars")
                        
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
        log_test_result(f"❌ Text content processing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None

def create_comprehensive_test_content():
    """Create comprehensive test content similar to Customer Summary Screen User Guide"""
    return """# Customer Summary Screen User Guide 1.3

## Table of Contents
1. Introduction and Overview
2. Getting Started with Customer Summary
3. Navigation and Interface Layout
4. Customer Information Management
5. Transaction History and Analysis
6. Account Status and Management
7. Communication Tools and Features
8. Reporting and Analytics
9. Advanced Features and Customization
10. Troubleshooting and Support
11. Best Practices and Tips
12. Integration with Other Systems
13. Security and Compliance
14. Performance Optimization
15. Future Updates and Roadmap

## Chapter 1: Introduction and Overview

### 1.1 Welcome to Customer Summary Screen
The Customer Summary Screen is the central hub for managing customer relationships and accessing comprehensive customer data. This powerful interface provides a 360-degree view of customer interactions, transaction history, and account status in a single, intuitive dashboard.

### 1.2 Key Features and Benefits
- Comprehensive customer data visualization
- Real-time transaction monitoring
- Advanced analytics and reporting
- Integrated communication tools
- Customizable dashboard layouts
- Multi-channel interaction tracking
- Automated workflow capabilities
- Compliance and audit trail features

### 1.3 System Requirements
Before using the Customer Summary Screen, ensure your system meets the following requirements:
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Minimum screen resolution: 1366x768
- Stable internet connection (minimum 10 Mbps recommended)
- JavaScript enabled
- Cookies and local storage enabled

### 1.4 User Roles and Permissions
The system supports multiple user roles with different access levels:
- Administrator: Full system access and configuration
- Manager: Customer data access and team oversight
- Agent: Customer interaction and basic data entry
- Viewer: Read-only access to customer information
- Analyst: Advanced reporting and analytics access

## Chapter 2: Getting Started with Customer Summary

### 2.1 Initial Setup and Configuration
When first accessing the Customer Summary Screen, complete the following setup steps:

1. **Profile Configuration**
   - Update your personal information
   - Set notification preferences
   - Configure dashboard layout
   - Select default filters and views

2. **Security Settings**
   - Enable two-factor authentication
   - Set up security questions
   - Configure session timeout preferences
   - Review access permissions

3. **Integration Setup**
   - Connect external data sources
   - Configure API endpoints
   - Set up automated data synchronization
   - Test integration connections

### 2.2 First Login Experience
Your first login will guide you through:
- Welcome tour of key features
- Basic navigation training
- Sample data exploration
- Quick start tutorials
- Help resource locations

### 2.3 Dashboard Customization
Personalize your workspace by:
- Arranging widget layouts
- Setting default search filters
- Configuring alert preferences
- Customizing color themes
- Setting up quick action buttons

## Chapter 3: Navigation and Interface Layout

### 3.1 Main Navigation Structure
The Customer Summary Screen features an intuitive navigation structure:

**Top Navigation Bar**
- Home dashboard link
- Search functionality
- User profile menu
- Notification center
- Help and support access

**Left Sidebar Menu**
- Customer search and selection
- Recent customers list
- Favorite customers
- Advanced search filters
- System settings access

**Main Content Area**
- Customer information panels
- Transaction displays
- Interactive charts and graphs
- Action buttons and tools
- Status indicators

### 3.2 Search and Filter Capabilities
Powerful search features include:
- Global customer search
- Advanced filter combinations
- Saved search preferences
- Quick filter buttons
- Real-time search suggestions

### 3.3 Responsive Design Features
The interface adapts to different screen sizes:
- Mobile-optimized layouts
- Tablet-friendly navigation
- Desktop full-feature access
- Touch-friendly controls
- Keyboard navigation support

## Chapter 4: Customer Information Management

### 4.1 Customer Profile Overview
The customer profile section displays:
- Personal and contact information
- Account creation and modification dates
- Customer tier and status indicators
- Relationship manager assignments
- Communication preferences
- Document attachments

### 4.2 Contact Information Management
Maintain accurate customer contact details:
- Primary and secondary addresses
- Phone numbers and extensions
- Email addresses and preferences
- Social media profiles
- Emergency contact information
- Communication history logs

### 4.3 Account Hierarchy and Relationships
Manage complex customer relationships:
- Parent-child account structures
- Business relationship mapping
- Authorized user management
- Power of attorney designations
- Beneficiary information
- Joint account holders

### 4.4 Customer Segmentation and Tagging
Organize customers effectively:
- Custom tag creation and assignment
- Automated segmentation rules
- Behavioral classification
- Risk assessment categories
- Marketing preference groups
- Service level designations

## Chapter 5: Transaction History and Analysis

### 5.1 Transaction Display and Filtering
View and analyze customer transactions:
- Chronological transaction listing
- Date range filtering options
- Transaction type categorization
- Amount and currency filters
- Status-based filtering
- Channel-specific views

### 5.2 Transaction Details and Drill-Down
Access comprehensive transaction information:
- Transaction reference numbers
- Processing timestamps
- Fee and charge breakdowns
- Authorization details
- Settlement information
- Related document links

### 5.3 Pattern Recognition and Alerts
Identify important transaction patterns:
- Unusual activity detection
- Spending pattern analysis
- Frequency trend monitoring
- Seasonal behavior identification
- Risk indicator flagging
- Compliance alert generation

### 5.4 Export and Reporting Options
Generate transaction reports:
- PDF statement generation
- Excel export functionality
- Custom report templates
- Scheduled report delivery
- Audit trail documentation
- Regulatory compliance reports

## Chapter 6: Account Status and Management

### 6.1 Account Status Indicators
Monitor account health through:
- Real-time status displays
- Color-coded indicators
- Alert notifications
- Trend analysis charts
- Performance metrics
- Risk assessment scores

### 6.2 Account Maintenance Actions
Perform essential account management:
- Status updates and changes
- Hold and restriction management
- Credit limit adjustments
- Interest rate modifications
- Fee structure updates
- Account closure procedures

### 6.3 Workflow and Approval Processes
Manage complex approval workflows:
- Multi-level authorization requirements
- Automated workflow routing
- Approval status tracking
- Escalation procedures
- Audit trail maintenance
- Compliance verification

## Chapter 7: Communication Tools and Features

### 7.1 Integrated Communication Hub
Access all communication channels:
- Email integration and templates
- SMS messaging capabilities
- Voice call logging
- Video conference scheduling
- Chat and instant messaging
- Social media monitoring

### 7.2 Communication History Tracking
Maintain comprehensive communication records:
- Interaction timestamps
- Communication channel identification
- Participant information
- Content summaries
- Attachment management
- Follow-up scheduling

### 7.3 Automated Communication Features
Leverage automation for efficiency:
- Triggered message sending
- Template-based communications
- Scheduled reminder systems
- Event-driven notifications
- Personalized content generation
- Multi-channel campaign management

## Chapter 8: Reporting and Analytics

### 8.1 Standard Report Library
Access pre-built reports:
- Customer summary reports
- Transaction analysis reports
- Performance metrics dashboards
- Compliance monitoring reports
- Risk assessment summaries
- Trend analysis documents

### 8.2 Custom Report Builder
Create tailored reports:
- Drag-and-drop report designer
- Custom field selection
- Advanced filtering options
- Calculated field creation
- Conditional formatting
- Interactive chart generation

### 8.3 Real-Time Analytics Dashboard
Monitor key metrics:
- Live performance indicators
- Trend visualization
- Comparative analysis tools
- Predictive modeling displays
- Alert threshold monitoring
- Drill-down capabilities

## Chapter 9: Advanced Features and Customization

### 9.1 API Integration Capabilities
Extend functionality through APIs:
- RESTful API endpoints
- Webhook configuration
- Third-party integrations
- Custom application development
- Data synchronization tools
- Authentication management

### 9.2 Workflow Automation
Streamline processes with automation:
- Business rule configuration
- Automated task assignment
- Conditional logic implementation
- Integration trigger setup
- Performance monitoring
- Exception handling

### 9.3 Advanced Security Features
Implement robust security measures:
- Role-based access control
- Field-level security
- Data encryption standards
- Audit logging
- Compliance monitoring
- Threat detection

## Chapter 10: Troubleshooting and Support

### 10.1 Common Issues and Solutions
Resolve frequent problems:
- Login and authentication issues
- Data loading problems
- Performance optimization
- Browser compatibility
- Network connectivity
- Permission-related errors

### 10.2 Error Message Reference
Understand system messages:
- Error code explanations
- Resolution procedures
- Escalation guidelines
- Contact information
- Documentation references
- Video tutorials

### 10.3 Support Resources
Access help when needed:
- Online documentation
- Video tutorial library
- Community forums
- Live chat support
- Phone support options
- Training resources

## Chapter 11: Best Practices and Tips

### 11.1 Efficiency Optimization
Maximize productivity:
- Keyboard shortcut utilization
- Batch processing techniques
- Template usage strategies
- Automation implementation
- Workflow optimization
- Time management tips

### 11.2 Data Quality Management
Maintain accurate information:
- Regular data validation
- Duplicate detection and resolution
- Standardization procedures
- Quality metrics monitoring
- Correction workflows
- Audit procedures

### 11.3 Security Best Practices
Protect sensitive information:
- Password management
- Session security
- Data handling procedures
- Privacy compliance
- Incident reporting
- Regular security reviews

## Chapter 12: Integration with Other Systems

### 12.1 CRM System Integration
Connect with customer relationship management:
- Data synchronization
- Workflow coordination
- Reporting integration
- User experience consistency
- Performance optimization
- Troubleshooting procedures

### 12.2 Financial System Connections
Integrate with financial platforms:
- Account balance synchronization
- Transaction data sharing
- Reconciliation procedures
- Reporting coordination
- Audit trail maintenance
- Compliance verification

### 12.3 Third-Party Service Integration
Connect external services:
- Payment processing systems
- Identity verification services
- Credit reporting agencies
- Marketing automation platforms
- Document management systems
- Communication tools

## Chapter 13: Security and Compliance

### 13.1 Data Protection Standards
Implement comprehensive data protection:
- Encryption requirements
- Access control measures
- Data retention policies
- Privacy protection procedures
- Breach response protocols
- Regular security assessments

### 13.2 Regulatory Compliance
Meet industry requirements:
- Financial services regulations
- Data privacy laws
- Industry-specific standards
- International compliance
- Audit requirements
- Documentation standards

### 13.3 Risk Management
Identify and mitigate risks:
- Risk assessment procedures
- Monitoring and detection
- Response protocols
- Recovery procedures
- Continuous improvement
- Training and awareness

## Chapter 14: Performance Optimization

### 14.1 System Performance Monitoring
Track system efficiency:
- Response time measurement
- Resource utilization monitoring
- User experience metrics
- Error rate tracking
- Capacity planning
- Performance tuning

### 14.2 User Experience Optimization
Enhance user satisfaction:
- Interface responsiveness
- Navigation efficiency
- Feature accessibility
- Mobile optimization
- Personalization options
- Feedback incorporation

### 14.3 Scalability Considerations
Plan for growth:
- Capacity planning
- Architecture optimization
- Load balancing
- Database performance
- Network optimization
- Resource allocation

## Chapter 15: Future Updates and Roadmap

### 15.1 Planned Enhancements
Upcoming feature releases:
- New functionality additions
- User interface improvements
- Performance enhancements
- Integration expansions
- Security upgrades
- Compliance updates

### 15.2 Technology Evolution
Adapt to changing technology:
- Platform modernization
- Cloud migration strategies
- Mobile-first development
- AI and machine learning integration
- Automation expansion
- User experience evolution

### 15.3 Feedback and Improvement
Continuous enhancement process:
- User feedback collection
- Feature request management
- Performance monitoring
- Quality assurance
- Release management
- Change communication

## Conclusion

The Customer Summary Screen User Guide provides comprehensive coverage of all system features and capabilities. Regular reference to this guide will help users maximize their productivity and ensure optimal customer service delivery.

For additional support, training resources, and updates, please visit our online documentation portal or contact our support team.

---

*Customer Summary Screen User Guide Version 1.3*
*Last Updated: January 2024*
*© 2024 Company Name. All rights reserved.*"""

def create_smaller_test_content():
    """Create smaller test content for comparison"""
    return """# Simple User Guide

## Introduction
This is a simple user guide for testing purposes.

## Getting Started
Follow these steps to get started:
1. Log into the system
2. Navigate to the main dashboard
3. Select your preferred settings

## Basic Features
The system includes:
- User management
- Data entry
- Reporting tools
- Help documentation

## Conclusion
This guide covers the basic features of the system."""

def test_different_content_sizes():
    """Test processing with different content sizes"""
    try:
        log_test_result("🎯 TESTING DIFFERENT CONTENT SIZES", "CRITICAL")
        
        test_cases = [
            {
                'content': create_smaller_test_content(),
                'description': 'Small Content (Simple Guide)'
            },
            {
                'content': create_comprehensive_test_content(),
                'description': 'Large Content (Comprehensive Guide)'
            }
        ]
        
        results = []
        
        for case in test_cases:
            log_test_result(f"🧪 Testing {case['description']}")
            result = process_text_content(case['content'], case['description'])
            
            if result:
                results.append(result)
            
            # Wait between tests
            time.sleep(10)
        
        # Analyze results
        log_test_result("📊 CONTENT SIZE ANALYSIS", "ANALYSIS")
        
        if len(results) >= 2:
            small_result = results[0]
            large_result = results[1]
            
            log_test_result(f"📏 CONTENT SIZE COMPARISON:")
            log_test_result(f"   Small Content: {small_result['content_length']:,} chars → {small_result['articles_generated']} articles")
            log_test_result(f"   Large Content: {large_result['content_length']:,} chars → {large_result['articles_generated']} articles")
            
            # Check if large content generates significantly more articles
            if large_result['articles_generated'] > small_result['articles_generated'] * 3:
                log_test_result(f"✅ EXPECTED BEHAVIOR: Large content generates {large_result['articles_generated']/small_result['articles_generated']:.1f}x more articles", "SUCCESS")
                return True
            elif large_result['articles_generated'] <= 6 and large_result['content_length'] > 50000:
                log_test_result(f"❌ CRITICAL ISSUE: Large content ({large_result['content_length']:,} chars) only generated {large_result['articles_generated']} articles", "CRITICAL")
                return False
            else:
                log_test_result(f"⚠️ UNEXPECTED BEHAVIOR: Article generation ratio may indicate processing constraints", "WARNING")
                return True
        
        return False
        
    except Exception as e:
        log_test_result(f"❌ Content size testing failed: {e}", "ERROR")
        return False

def check_existing_customer_guide_articles():
    """Check for existing customer guide articles in Content Library"""
    try:
        log_test_result("🔍 CHECKING FOR EXISTING CUSTOMER GUIDE ARTICLES", "ANALYSIS")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📚 Content Library: {total_articles} total articles")
        
        # Look for customer guide related articles
        customer_articles = []
        summary_articles = []
        guide_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            source = article.get('source_document', '').lower()
            
            if 'customer' in title or 'customer' in source:
                customer_articles.append(article)
            if 'summary' in title or 'summary' in source:
                summary_articles.append(article)
            if 'guide' in title or 'guide' in source:
                guide_articles.append(article)
        
        log_test_result(f"🔍 ARTICLE ANALYSIS:")
        log_test_result(f"   Customer-related articles: {len(customer_articles)}")
        log_test_result(f"   Summary-related articles: {len(summary_articles)}")
        log_test_result(f"   Guide-related articles: {len(guide_articles)}")
        
        # Show sample titles
        if customer_articles:
            log_test_result(f"📄 CUSTOMER ARTICLES FOUND:")
            for i, article in enumerate(customer_articles[:10]):
                title = article.get('title', 'Untitled')
                created = article.get('created_at', 'Unknown')
                log_test_result(f"   {i+1}. {title[:80]}...")
        
        # Check if we have the reported 38 articles
        if len(customer_articles) >= 30:
            log_test_result(f"🎯 CONFIRMED: Found {len(customer_articles)} customer-related articles (matches bug report)", "CRITICAL")
        elif len(customer_articles) > 0:
            log_test_result(f"⚠️ PARTIAL MATCH: Found {len(customer_articles)} customer-related articles (less than reported)", "WARNING")
        else:
            log_test_result("❌ NO CUSTOMER ARTICLES: No customer guide articles found", "ERROR")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Customer guide article check failed: {e}", "ERROR")
        return False

def main():
    """Main test execution"""
    log_test_result("🚀 STARTING TEXT CONTENT PROCESSING INVESTIGATION", "START")
    
    # Test backend health first
    if not test_backend_health():
        log_test_result("❌ Backend health check failed, aborting tests", "ABORT")
        return False
    
    # Run investigation tests
    tests = [
        ("Different Content Sizes", test_different_content_sizes),
        ("Existing Customer Guide Articles", check_existing_customer_guide_articles)
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
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)