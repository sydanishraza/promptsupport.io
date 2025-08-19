#!/usr/bin/env python3
"""
CRITICAL BUG INVESTIGATION: Knowledge Engine Processing Investigation
Testing the Knowledge Engine with different content types and sizes to investigate article generation differences
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://smartchunk.preview.emergentagent.com"
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

def process_text_content_via_knowledge_engine(content, description):
    """Process text content through Knowledge Engine using correct endpoint"""
    try:
        log_test_result(f"📤 Processing {description} ({len(content):,} characters)...")
        
        # Use the correct content processing endpoint
        payload = {
            "content": content,
            "content_type": "text",
            "metadata": {
                "source": "test_investigation",
                "description": description
            }
        }
        
        # Start processing
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/process", 
                               json=payload, 
                               headers={'Content-Type': 'application/json'},
                               timeout=600)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return None
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        chunks_created = process_data.get('chunks_created', 0)
        
        if not job_id:
            log_test_result("❌ No job_id received from content processing", "ERROR")
            return None
        
        processing_time = time.time() - start_time
        log_test_result(f"✅ Content processing completed, Job ID: {job_id}")
        log_test_result(f"📊 Processing Results: {chunks_created} chunks created in {processing_time:.1f}s")
        
        # Get job details for more information
        try:
            job_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
            if job_response.status_code == 200:
                job_data = job_response.json()
                log_test_result(f"📋 Job Status: {job_data.get('status', 'unknown')}")
            else:
                log_test_result(f"⚠️ Could not retrieve job details: {job_response.status_code}")
        except Exception as e:
            log_test_result(f"⚠️ Error retrieving job details: {e}")
        
        result = {
            'job_id': job_id,
            'processing_time': processing_time,
            'chunks_created': chunks_created,
            'content_length': len(content),
            'description': description,
            'status': 'completed'
        }
        
        return result
        
    except Exception as e:
        log_test_result(f"❌ Content processing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None

def create_customer_summary_guide_content():
    """Create content similar to Customer Summary Screen User Guide"""
    return """# Customer Summary Screen User Guide 1.3

## Table of Contents
1. Introduction and System Overview
2. Getting Started with Customer Management
3. Navigation and User Interface
4. Customer Information Management
5. Transaction History and Analysis
6. Account Status and Operations
7. Communication Tools and Features
8. Reporting and Analytics Dashboard
9. Advanced Features and Customization
10. Troubleshooting and Support
11. Best Practices and Guidelines
12. System Integration Capabilities
13. Security and Compliance Features
14. Performance Optimization Tips
15. Future Updates and Roadmap

## Chapter 1: Introduction and System Overview

### 1.1 Welcome to Customer Summary Screen
The Customer Summary Screen serves as the central command center for comprehensive customer relationship management. This sophisticated platform provides a unified view of customer interactions, transaction histories, account statuses, and communication records, all integrated into a single, intuitive interface designed for maximum efficiency and user experience.

### 1.2 Core System Capabilities
Our platform delivers enterprise-grade functionality including:
- Real-time customer data aggregation and visualization
- Advanced transaction monitoring and analysis capabilities
- Integrated multi-channel communication management
- Comprehensive reporting and analytics dashboard
- Customizable workflow automation and business rules
- Advanced security features and compliance monitoring
- Scalable architecture supporting high-volume operations
- Mobile-responsive design for anywhere access

### 1.3 Technical Architecture and Requirements
The system is built on modern cloud-native architecture with the following technical specifications:
- Microservices-based architecture for scalability and reliability
- RESTful API design for seamless integration capabilities
- Real-time data synchronization across all system components
- Advanced caching mechanisms for optimal performance
- Comprehensive audit logging and data lineage tracking
- Enterprise-grade security with multi-factor authentication
- Disaster recovery and business continuity features

### 1.4 User Roles and Permission Management
The platform supports sophisticated role-based access control with granular permissions:
- System Administrator: Complete system configuration and user management
- Department Manager: Team oversight and advanced reporting access
- Customer Service Agent: Customer interaction and data entry capabilities
- Data Analyst: Advanced analytics and reporting functionality
- Compliance Officer: Audit trail access and regulatory reporting
- Read-Only User: View-only access to customer information

## Chapter 2: Getting Started with Customer Management

### 2.1 Initial System Setup and Configuration
Upon first access to the Customer Summary Screen, users must complete a comprehensive setup process:

**Personal Profile Configuration**
- Complete user profile information including contact details and preferences
- Configure notification settings for alerts, reminders, and system updates
- Set up personalized dashboard layouts and widget arrangements
- Establish default search filters and view preferences
- Configure time zone and localization settings

**Security and Authentication Setup**
- Enable multi-factor authentication for enhanced security
- Configure security questions and backup authentication methods
- Set up session timeout preferences and security policies
- Review and acknowledge data handling and privacy policies
- Configure password policies and update schedules

**System Integration and Data Sources**
- Connect external data sources and third-party systems
- Configure API endpoints and authentication credentials
- Set up automated data synchronization schedules
- Test integration connections and data flow validation
- Configure error handling and notification procedures

### 2.2 Dashboard Customization and Personalization
The system offers extensive customization capabilities:
- Drag-and-drop widget arrangement for optimal workflow
- Custom color themes and branding options
- Configurable quick action buttons and shortcuts
- Personalized search filters and saved queries
- Custom alert thresholds and notification preferences

### 2.3 First-Time User Experience and Training
New users receive comprehensive onboarding support:
- Interactive system tour highlighting key features and capabilities
- Step-by-step tutorials for common tasks and workflows
- Sample data exploration with guided exercises
- Video training library covering advanced features
- Access to user community forums and knowledge base

## Chapter 3: Navigation and User Interface

### 3.1 Main Navigation Architecture
The Customer Summary Screen features an intuitive, hierarchical navigation structure designed for efficiency:

**Primary Navigation Header**
- Global search functionality with advanced filtering capabilities
- User profile menu with settings and preferences access
- Notification center with real-time alerts and updates
- Help and support resources including documentation and tutorials
- Quick access to frequently used features and tools

**Secondary Navigation Sidebar**
- Customer search and selection with auto-complete functionality
- Recently accessed customers list with quick access
- Favorite customers bookmark system for frequent contacts
- Advanced search filters with saved query capabilities
- System settings and configuration access

**Main Content Display Area**
- Dynamic customer information panels with real-time updates
- Interactive transaction displays with drill-down capabilities
- Comprehensive charts and graphs with customizable views
- Context-sensitive action buttons and workflow tools
- Status indicators and alert notifications

### 3.2 Advanced Search and Filtering Capabilities
The platform provides powerful search functionality:
- Global customer search across all data fields
- Boolean search operators for complex queries
- Advanced filter combinations with logical operators
- Saved search templates for recurring queries
- Real-time search suggestions and auto-completion
- Search result ranking and relevance scoring

### 3.3 Responsive Design and Multi-Device Support
The interface adapts seamlessly across different platforms:
- Mobile-optimized layouts for smartphone access
- Tablet-friendly navigation with touch-optimized controls
- Desktop full-feature access with keyboard shortcuts
- Cross-browser compatibility and performance optimization
- Offline capability for critical functions

## Chapter 4: Customer Information Management

### 4.1 Comprehensive Customer Profile Management
The customer profile section provides a complete view of customer information:
- Personal and business contact information with validation
- Account creation dates and modification history tracking
- Customer tier classification and status indicators
- Relationship manager assignments and contact information
- Communication preferences and channel selections
- Document attachments and file management system

### 4.2 Contact Information and Communication Management
Maintain accurate and up-to-date customer contact details:
- Primary and secondary address management with validation
- Multiple phone numbers with type classification and extensions
- Email address management with preference settings
- Social media profile integration and monitoring
- Emergency contact information and relationship mapping
- Communication history logging and interaction tracking

### 4.3 Account Hierarchy and Relationship Mapping
Manage complex customer relationship structures:
- Parent-child account hierarchies with visual mapping
- Business relationship diagrams and organizational charts
- Authorized user management with permission levels
- Power of attorney designations and legal documentation
- Beneficiary information and inheritance planning
- Joint account holder management and responsibilities

### 4.4 Customer Segmentation and Advanced Tagging
Organize and categorize customers effectively:
- Custom tag creation with hierarchical organization
- Automated segmentation rules based on behavior and demographics
- Behavioral classification using machine learning algorithms
- Risk assessment categories with scoring models
- Marketing preference groups and campaign targeting
- Service level designations and priority classifications

## Chapter 5: Transaction History and Analysis

### 5.1 Transaction Display and Advanced Filtering
View and analyze customer transactions with sophisticated tools:
- Chronological transaction listing with pagination
- Flexible date range filtering with preset options
- Transaction type categorization and classification
- Amount and currency filters with range selections
- Status-based filtering with multiple criteria
- Channel-specific views and source identification

### 5.2 Transaction Details and Comprehensive Drill-Down
Access detailed transaction information:
- Unique transaction reference numbers and identifiers
- Precise processing timestamps with timezone information
- Detailed fee and charge breakdowns with explanations
- Authorization details and approval workflows
- Settlement information and clearing processes
- Related document links and supporting materials

### 5.3 Pattern Recognition and Intelligent Alerts
Identify important transaction patterns using advanced analytics:
- Unusual activity detection using machine learning
- Spending pattern analysis with trend identification
- Frequency trend monitoring and seasonal adjustments
- Behavioral pattern recognition and anomaly detection
- Risk indicator flagging with severity levels
- Compliance alert generation and regulatory monitoring

### 5.4 Export and Comprehensive Reporting Options
Generate detailed transaction reports:
- PDF statement generation with customizable templates
- Excel export functionality with data formatting
- Custom report templates with drag-and-drop design
- Scheduled report delivery via email or secure portal
- Audit trail documentation with digital signatures
- Regulatory compliance reports with certification

## Chapter 6: Account Status and Management

### 6.1 Real-Time Account Status Monitoring
Monitor account health through comprehensive indicators:
- Real-time status displays with color-coded alerts
- Dynamic indicator systems with threshold monitoring
- Automated alert notifications with escalation procedures
- Trend analysis charts with predictive modeling
- Performance metrics dashboards with KPI tracking
- Risk assessment scores with contributing factor analysis

### 6.2 Account Maintenance and Operations
Perform essential account management functions:
- Status updates and change management workflows
- Hold and restriction management with approval processes
- Credit limit adjustments with risk assessment
- Interest rate modifications with market analysis
- Fee structure updates with customer notification
- Account closure procedures with compliance verification

### 6.3 Workflow Management and Approval Processes
Manage complex approval workflows:
- Multi-level authorization requirements with role-based routing
- Automated workflow routing with business rule engine
- Approval status tracking with real-time updates
- Escalation procedures with timeout management
- Comprehensive audit trail maintenance
- Compliance verification and regulatory reporting

## Chapter 7: Communication Tools and Features

### 7.1 Integrated Multi-Channel Communication Hub
Access all communication channels from a unified interface:
- Email integration with template management and automation
- SMS messaging capabilities with delivery confirmation
- Voice call logging with recording and transcription
- Video conference scheduling with calendar integration
- Chat and instant messaging with presence indicators
- Social media monitoring and engagement tracking

### 7.2 Communication History and Interaction Tracking
Maintain comprehensive communication records:
- Detailed interaction timestamps with duration tracking
- Communication channel identification and classification
- Participant information and role identification
- Content summaries with keyword extraction
- Attachment management with version control
- Follow-up scheduling with automated reminders

### 7.3 Automated Communication and Campaign Management
Leverage automation for enhanced efficiency:
- Triggered message sending based on customer behavior
- Template-based communications with personalization
- Scheduled reminder systems with escalation procedures
- Event-driven notifications with customizable triggers
- Personalized content generation using AI
- Multi-channel campaign management with analytics

## Chapter 8: Reporting and Analytics Dashboard

### 8.1 Standard Report Library and Templates
Access comprehensive pre-built reporting capabilities:
- Customer summary reports with executive dashboards
- Transaction analysis reports with trend identification
- Performance metrics dashboards with real-time updates
- Compliance monitoring reports with regulatory alignment
- Risk assessment summaries with scoring models
- Trend analysis documents with predictive insights

### 8.2 Custom Report Builder and Design Tools
Create tailored reports using advanced tools:
- Intuitive drag-and-drop report designer interface
- Custom field selection with data validation
- Advanced filtering options with logical operators
- Calculated field creation with formula builder
- Conditional formatting with visual indicators
- Interactive chart generation with drill-down capabilities

### 8.3 Real-Time Analytics and Business Intelligence
Monitor key metrics with advanced analytics:
- Live performance indicators with threshold monitoring
- Dynamic trend visualization with predictive modeling
- Comparative analysis tools with benchmarking
- Predictive modeling displays with confidence intervals
- Alert threshold monitoring with automated notifications
- Advanced drill-down capabilities with root cause analysis

## Chapter 9: Advanced Features and Customization

### 9.1 API Integration and Development Capabilities
Extend functionality through comprehensive APIs:
- RESTful API endpoints with comprehensive documentation
- Webhook configuration for real-time event notifications
- Third-party integrations with popular business applications
- Custom application development with SDK support
- Data synchronization tools with conflict resolution
- Authentication management with OAuth 2.0 support

### 9.2 Workflow Automation and Business Rules
Streamline processes with intelligent automation:
- Business rule configuration with visual designer
- Automated task assignment with load balancing
- Conditional logic implementation with decision trees
- Integration trigger setup with event monitoring
- Performance monitoring with optimization recommendations
- Exception handling with escalation procedures

### 9.3 Advanced Security and Compliance Features
Implement comprehensive security measures:
- Role-based access control with granular permissions
- Field-level security with data classification
- Advanced data encryption standards with key management
- Comprehensive audit logging with tamper protection
- Compliance monitoring with regulatory reporting
- Threat detection with behavioral analysis

## Chapter 10: Troubleshooting and Support

### 10.1 Common Issues and Resolution Procedures
Resolve frequent problems with detailed guidance:
- Login and authentication troubleshooting with step-by-step solutions
- Data loading problems with performance optimization
- Browser compatibility issues with recommended settings
- Network connectivity troubleshooting with diagnostic tools
- Permission-related errors with access management
- Performance optimization with system tuning

### 10.2 Error Message Reference and Diagnostic Tools
Understand system messages and diagnostic information:
- Comprehensive error code explanations with context
- Step-by-step resolution procedures with screenshots
- Escalation guidelines with contact information
- Diagnostic tools with automated problem detection
- Log analysis with pattern recognition
- Performance monitoring with bottleneck identification

### 10.3 Support Resources and Training Materials
Access comprehensive help when needed:
- Extensive online documentation with search capabilities
- Video tutorial library with step-by-step instructions
- Active community forums with expert moderation
- Live chat support with technical specialists
- Phone support options with priority queuing
- Training resources with certification programs

## Chapter 11: Best Practices and Guidelines

### 11.1 Efficiency Optimization and Productivity Tips
Maximize productivity with proven strategies:
- Keyboard shortcut utilization with customizable mappings
- Batch processing techniques with automation tools
- Template usage strategies with best practices
- Workflow optimization with process improvement
- Time management tips with productivity metrics
- Performance monitoring with efficiency tracking

### 11.2 Data Quality Management and Governance
Maintain accurate and reliable information:
- Regular data validation with automated checks
- Duplicate detection and resolution procedures
- Data standardization procedures with quality metrics
- Quality metrics monitoring with trend analysis
- Correction workflows with approval processes
- Audit procedures with compliance verification

### 11.3 Security Best Practices and Risk Management
Protect sensitive information with comprehensive security:
- Password management with policy enforcement
- Session security with timeout management
- Data handling procedures with classification
- Privacy compliance with regulatory requirements
- Incident reporting with escalation procedures
- Regular security reviews with vulnerability assessment

## Chapter 12: System Integration Capabilities

### 12.1 CRM System Integration and Data Synchronization
Connect with customer relationship management systems:
- Bidirectional data synchronization with conflict resolution
- Workflow coordination with process automation
- Reporting integration with unified dashboards
- User experience consistency with single sign-on
- Performance optimization with caching strategies
- Troubleshooting procedures with diagnostic tools

### 12.2 Financial System Connections and Data Management
Integrate with financial platforms and services:
- Real-time account balance synchronization
- Transaction data sharing with reconciliation
- Automated reconciliation procedures with exception handling
- Reporting coordination with consolidated views
- Audit trail maintenance with compliance verification
- Regulatory reporting with automated generation

### 12.3 Third-Party Service Integration and API Management
Connect external services and applications:
- Payment processing systems with secure tokenization
- Identity verification services with fraud detection
- Credit reporting agencies with automated updates
- Marketing automation platforms with campaign integration
- Document management systems with version control
- Communication tools with unified messaging

## Chapter 13: Security and Compliance Features

### 13.1 Data Protection Standards and Implementation
Implement comprehensive data protection measures:
- Advanced encryption requirements with key management
- Access control measures with role-based permissions
- Data retention policies with automated lifecycle management
- Privacy protection procedures with consent management
- Breach response protocols with incident management
- Regular security assessments with vulnerability scanning

### 13.2 Regulatory Compliance and Reporting
Meet industry requirements and standards:
- Financial services regulations with automated compliance
- Data privacy laws with consent management
- Industry-specific standards with certification
- International compliance with multi-jurisdiction support
- Audit requirements with automated documentation
- Documentation standards with version control

### 13.3 Risk Management and Monitoring
Identify and mitigate operational risks:
- Comprehensive risk assessment procedures
- Continuous monitoring and detection systems
- Incident response protocols with escalation
- Recovery procedures with business continuity
- Continuous improvement with lessons learned
- Training and awareness programs with certification

## Chapter 14: Performance Optimization

### 14.1 System Performance Monitoring and Tuning
Track and optimize system efficiency:
- Response time measurement with performance baselines
- Resource utilization monitoring with capacity planning
- User experience metrics with satisfaction tracking
- Error rate tracking with root cause analysis
- Capacity planning with growth projections
- Performance tuning with optimization recommendations

### 14.2 User Experience Optimization and Enhancement
Enhance user satisfaction and productivity:
- Interface responsiveness with performance optimization
- Navigation efficiency with usability testing
- Feature accessibility with compliance standards
- Mobile optimization with responsive design
- Personalization options with user preferences
- Feedback incorporation with continuous improvement

### 14.3 Scalability Considerations and Planning
Plan for future growth and expansion:
- Capacity planning with demand forecasting
- Architecture optimization with scalability patterns
- Load balancing with high availability
- Database performance with optimization strategies
- Network optimization with content delivery
- Resource allocation with cost optimization

## Chapter 15: Future Updates and Roadmap

### 15.1 Planned Enhancements and Feature Releases
Upcoming improvements and new capabilities:
- New functionality additions with user feedback integration
- User interface improvements with modern design principles
- Performance enhancements with optimization strategies
- Integration expansions with popular business applications
- Security upgrades with latest threat protection
- Compliance updates with regulatory changes

### 15.2 Technology Evolution and Innovation
Adapt to changing technology landscape:
- Platform modernization with cloud-native architecture
- Cloud migration strategies with minimal disruption
- Mobile-first development with responsive design
- AI and machine learning integration with intelligent automation
- Automation expansion with workflow optimization
- User experience evolution with emerging technologies

### 15.3 Feedback and Continuous Improvement
Ongoing enhancement process:
- User feedback collection with multiple channels
- Feature request management with prioritization
- Performance monitoring with continuous optimization
- Quality assurance with comprehensive testing
- Release management with controlled deployment
- Change communication with stakeholder engagement

## Conclusion and Next Steps

The Customer Summary Screen User Guide provides comprehensive coverage of all system features, capabilities, and best practices. This extensive documentation serves as both a learning resource for new users and a reference guide for experienced professionals.

Regular reference to this guide will help users maximize their productivity, ensure optimal customer service delivery, and maintain compliance with organizational policies and regulatory requirements.

For additional support, advanced training resources, system updates, and community engagement, please visit our comprehensive online documentation portal or contact our dedicated support team.

---

*Customer Summary Screen User Guide Version 1.3*
*Last Updated: January 2024*
*© 2024 Company Name. All rights reserved.*
*Document Classification: Internal Use Only*
*Total Pages: 85 | Word Count: Approximately 15,000 words*"""

def create_simple_test_content():
    """Create simple test content for comparison"""
    return """# Simple Test Guide

## Introduction
This is a basic test document to compare processing results.

## Getting Started
Follow these simple steps:
1. Access the system
2. Navigate to the main area
3. Complete your tasks

## Basic Features
The system includes:
- User management
- Data entry
- Basic reporting
- Help documentation

## Troubleshooting
Common issues:
- Login problems
- Data loading issues
- Performance concerns

## Conclusion
This simple guide covers basic system usage."""

def create_medium_test_content():
    """Create medium-sized test content"""
    return """# Medium Test Documentation

## Chapter 1: Introduction
This document provides comprehensive information about system usage and best practices.

### 1.1 Overview
The system is designed to handle various business processes efficiently.

### 1.2 Key Features
- Advanced user management
- Comprehensive data processing
- Detailed reporting capabilities
- Integration with external systems

## Chapter 2: Getting Started
This chapter covers initial setup and configuration.

### 2.1 System Requirements
- Modern web browser
- Stable internet connection
- Appropriate user permissions
- Basic computer skills

### 2.2 Initial Setup
1. Create user account
2. Configure preferences
3. Set up integrations
4. Test functionality

## Chapter 3: Core Features
Detailed explanation of main system capabilities.

### 3.1 User Management
- Create and manage user accounts
- Assign roles and permissions
- Monitor user activity
- Generate user reports

### 3.2 Data Processing
- Import data from various sources
- Process and validate information
- Generate insights and analytics
- Export results in multiple formats

## Chapter 4: Advanced Features
Explore sophisticated system capabilities.

### 4.1 Automation
- Set up automated workflows
- Configure business rules
- Monitor process execution
- Handle exceptions and errors

### 4.2 Integration
- Connect with external systems
- Configure API endpoints
- Manage data synchronization
- Monitor integration health

## Chapter 5: Reporting and Analytics
Generate comprehensive reports and insights.

### 5.1 Standard Reports
- User activity reports
- System performance metrics
- Data quality assessments
- Compliance documentation

### 5.2 Custom Analytics
- Create custom dashboards
- Design specific reports
- Set up automated delivery
- Configure alert thresholds

## Chapter 6: Troubleshooting
Resolve common issues and problems.

### 6.1 Common Problems
- Authentication issues
- Data loading problems
- Performance concerns
- Integration failures

### 6.2 Support Resources
- Online documentation
- Video tutorials
- Community forums
- Technical support

## Conclusion
This documentation provides comprehensive coverage of system features and capabilities."""

def test_different_content_sizes_with_knowledge_engine():
    """Test processing with different content sizes using Knowledge Engine"""
    try:
        log_test_result("🎯 TESTING DIFFERENT CONTENT SIZES WITH KNOWLEDGE ENGINE", "CRITICAL")
        
        test_cases = [
            {
                'content': create_simple_test_content(),
                'description': 'Small Content (Simple Guide)',
                'expected_articles': '1-2'
            },
            {
                'content': create_medium_test_content(),
                'description': 'Medium Content (Documentation)',
                'expected_articles': '3-6'
            },
            {
                'content': create_customer_summary_guide_content(),
                'description': 'Large Content (Customer Summary Guide)',
                'expected_articles': '15-30+'
            }
        ]
        
        results = []
        
        for case in test_cases:
            log_test_result(f"🧪 Testing {case['description']}")
            log_test_result(f"   Content length: {len(case['content']):,} characters")
            log_test_result(f"   Expected articles: {case['expected_articles']}")
            
            result = process_text_content_via_knowledge_engine(case['content'], case['description'])
            
            if result:
                results.append(result)
            
            # Wait between tests
            time.sleep(15)
        
        # Analyze results
        log_test_result("📊 CONTENT SIZE PROCESSING ANALYSIS", "ANALYSIS")
        
        if len(results) >= 2:
            for result in results:
                log_test_result(f"📄 {result['description']}:")
                log_test_result(f"   Content: {result['content_length']:,} chars")
                log_test_result(f"   Chunks: {result['chunks_created']}")
                log_test_result(f"   Processing time: {result['processing_time']:.1f}s")
            
            # Check for processing inconsistencies
            chunk_counts = [r['chunks_created'] for r in results]
            content_lengths = [r['content_length'] for r in results]
            
            # Calculate chunks per character ratio
            ratios = []
            for i, result in enumerate(results):
                if result['content_length'] > 0:
                    ratio = result['chunks_created'] / result['content_length'] * 1000  # chunks per 1000 chars
                    ratios.append(ratio)
                    log_test_result(f"   {result['description']}: {ratio:.3f} chunks per 1000 chars")
            
            # Check for significant differences in processing efficiency
            if len(ratios) >= 2:
                max_ratio = max(ratios)
                min_ratio = min(ratios)
                
                if max_ratio > 0 and min_ratio > 0:
                    ratio_difference = max_ratio / min_ratio
                    
                    if ratio_difference > 2.0:  # More than 2x difference
                        log_test_result(f"🚨 PROCESSING INCONSISTENCY DETECTED:", "CRITICAL")
                        log_test_result(f"   Ratio difference: {ratio_difference:.1f}x")
                        log_test_result(f"   This suggests different processing paths for different content sizes")
                        return False
                    else:
                        log_test_result(f"✅ CONSISTENT PROCESSING: Ratio difference within acceptable range ({ratio_difference:.1f}x)", "SUCCESS")
                        return True
                else:
                    log_test_result("⚠️ Cannot calculate processing ratios (zero chunks created)", "WARNING")
                    return False
            else:
                log_test_result("⚠️ Insufficient data for ratio analysis", "WARNING")
                return False
        else:
            log_test_result("❌ Insufficient results for analysis", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ Content size testing failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def check_content_library_for_recent_articles():
    """Check Content Library for recently created articles"""
    try:
        log_test_result("🔍 CHECKING CONTENT LIBRARY FOR RECENT ARTICLES", "ANALYSIS")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📚 Content Library: {total_articles} total articles")
        
        # Analyze articles by creation time and source
        recent_articles = []
        customer_articles = []
        test_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            source = article.get('source_document', '').lower()
            created_at = article.get('created_at', '')
            
            # Look for recent articles (created today)
            if created_at and '2025-08-17' in created_at:
                recent_articles.append(article)
            
            # Look for customer-related articles
            if 'customer' in title or 'customer' in source:
                customer_articles.append(article)
            
            # Look for test-related articles
            if 'test' in title or 'test' in source:
                test_articles.append(article)
        
        log_test_result(f"📊 ARTICLE ANALYSIS:")
        log_test_result(f"   Recent articles (today): {len(recent_articles)}")
        log_test_result(f"   Customer-related articles: {len(customer_articles)}")
        log_test_result(f"   Test-related articles: {len(test_articles)}")
        
        # Show recent articles
        if recent_articles:
            log_test_result(f"📄 RECENT ARTICLES CREATED TODAY:")
            for i, article in enumerate(recent_articles[:10]):
                title = article.get('title', 'Untitled')
                created = article.get('created_at', 'Unknown')
                source = article.get('source_document', 'Unknown')
                log_test_result(f"   {i+1}. {title[:60]}... (Source: {source})")
        
        # Check for the reported customer guide articles
        if len(customer_articles) >= 30:
            log_test_result(f"🎯 CONFIRMED: Found {len(customer_articles)} customer-related articles", "CRITICAL")
            log_test_result("   This matches the bug report of 38 articles for Customer Summary Screen User Guide")
        elif len(customer_articles) > 0:
            log_test_result(f"⚠️ PARTIAL MATCH: Found {len(customer_articles)} customer-related articles", "WARNING")
        else:
            log_test_result("❌ NO CUSTOMER ARTICLES: No customer guide articles found", "ERROR")
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Content Library analysis failed: {e}", "ERROR")
        return False

def main():
    """Main test execution"""
    log_test_result("🚀 STARTING KNOWLEDGE ENGINE PROCESSING INVESTIGATION", "START")
    
    # Test backend health first
    if not test_backend_health():
        log_test_result("❌ Backend health check failed, aborting tests", "ABORT")
        return False
    
    # Run investigation tests
    tests = [
        ("Different Content Sizes with Knowledge Engine", test_different_content_sizes_with_knowledge_engine),
        ("Content Library Recent Articles Analysis", check_content_library_for_recent_articles)
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
    
    if passed_tests < total_tests:
        log_test_result("🚨 CRITICAL ISSUES DETECTED IN KNOWLEDGE ENGINE PROCESSING", "CRITICAL")
        log_test_result("   Investigation reveals inconsistent article generation across document types", "CRITICAL")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)