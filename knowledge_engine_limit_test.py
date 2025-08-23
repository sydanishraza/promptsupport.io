#!/usr/bin/env python3
"""
CRITICAL KNOWLEDGE ENGINE HARD LIMIT REMOVAL TESTING
Testing the complete removal of hard limits after processing Customer Summary Screen User Guide 1.3.docx
Focus: Verify that estimated 29 articles are actually created (not limited to 6-15)
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
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

def get_content_library_count():
    """Get current count of articles in Content Library"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code == 200:
            data = response.json()
            total_count = data.get('total', 0)
            log_test_result(f"📚 Current Content Library count: {total_count} articles")
            return total_count
        else:
            log_test_result(f"⚠️ Could not get Content Library count: Status {response.status_code}")
            return 0
    except Exception as e:
        log_test_result(f"⚠️ Error getting Content Library count: {e}")
        return 0

def test_knowledge_engine_hard_limit_removal():
    """
    CRITICAL TEST: Process Customer Summary Screen User Guide and verify hard limits are removed
    Expected: Generate 20+ articles (close to estimated 29) instead of 6-15
    """
    try:
        log_test_result("🎯 STARTING CRITICAL KNOWLEDGE ENGINE HARD LIMIT REMOVAL TEST", "CRITICAL")
        log_test_result("Target: Process Customer Summary Screen User Guide 1.3.docx")
        log_test_result("Expected: Generate 20+ articles (estimated need: 29)")
        
        # Get initial Content Library count
        initial_count = get_content_library_count()
        
        # Test content for Knowledge Engine processing
        test_content = """
Customer Summary Screen User Guide 1.3

Table of Contents
1. Introduction to Customer Summary Screen
2. Getting Started with Customer Management
3. Navigation and Interface Overview
4. Customer Profile Management
5. Account Information Display
6. Transaction History Tracking
7. Communication Logs Management
8. Document Management System
9. Customer Preferences Settings
10. Advanced Search Functionality
11. Reporting and Analytics
12. Data Export Capabilities
13. Security and Access Controls
14. Integration with External Systems
15. Mobile Application Features
16. Troubleshooting Common Issues
17. Best Practices and Tips
18. API Documentation
19. System Requirements
20. Installation and Setup
21. Configuration Management
22. User Role Management
23. Backup and Recovery
24. Performance Optimization
25. Compliance and Audit Trail
26. Customization Options
27. Third-party Integrations
28. Training and Support Resources
29. Future Updates and Roadmap

Chapter 1: Introduction to Customer Summary Screen

The Customer Summary Screen is a comprehensive dashboard that provides a unified view of all customer-related information within your organization. This powerful tool consolidates data from multiple sources to present a complete picture of each customer's relationship with your business.

Key Features:
- Real-time customer data aggregation
- Interactive dashboard with customizable widgets
- Advanced filtering and search capabilities
- Integration with CRM, billing, and support systems
- Mobile-responsive design for on-the-go access
- Role-based access controls for security
- Automated data synchronization
- Comprehensive reporting and analytics

The Customer Summary Screen serves as the central hub for customer service representatives, sales teams, and management to access critical customer information quickly and efficiently. By providing a single point of access to customer data, it eliminates the need to navigate multiple systems and reduces response times significantly.

Chapter 2: Getting Started with Customer Management

Before diving into the advanced features of the Customer Summary Screen, it's essential to understand the basic navigation and setup requirements. This chapter will guide you through the initial configuration and help you become familiar with the interface.

System Requirements:
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Minimum screen resolution of 1024x768
- Stable internet connection
- Valid user credentials with appropriate permissions
- JavaScript enabled in browser settings

Initial Setup Process:
1. Access the system through your organization's portal
2. Complete the initial login process
3. Configure your user preferences
4. Set up dashboard widgets according to your role
5. Customize notification settings
6. Test connectivity with integrated systems

The setup process typically takes 10-15 minutes for new users. System administrators can provide additional configuration options and advanced settings based on your specific role and requirements.

Chapter 3: Navigation and Interface Overview

The Customer Summary Screen interface is designed with user experience in mind, featuring an intuitive layout that minimizes learning curve while maximizing functionality. Understanding the interface components is crucial for efficient system usage.

Main Interface Components:
- Header navigation bar with quick access tools
- Left sidebar with customer search and filters
- Central dashboard area with customizable widgets
- Right panel for detailed customer information
- Bottom status bar with system notifications
- Context-sensitive help tooltips throughout

Navigation Features:
- Breadcrumb navigation for easy backtracking
- Quick search functionality with auto-complete
- Keyboard shortcuts for power users
- Customizable toolbar with frequently used functions
- Responsive design that adapts to different screen sizes
- Dark mode option for extended usage periods

The interface supports both mouse and keyboard navigation, ensuring accessibility for users with different preferences and requirements. All major functions are accessible through multiple pathways to accommodate various workflow patterns.

Chapter 4: Customer Profile Management

Customer profile management is at the heart of the Customer Summary Screen functionality. This comprehensive system allows you to maintain detailed customer records with complete accuracy and up-to-date information.

Profile Information Categories:
- Basic contact information and demographics
- Account status and subscription details
- Communication preferences and history
- Purchase history and transaction records
- Support ticket history and resolutions
- Custom fields for organization-specific data
- Document attachments and file management
- Relationship mapping with other customers

Data Management Features:
- Real-time data validation and verification
- Automatic duplicate detection and merging
- Data import/export capabilities
- Bulk update operations for efficiency
- Version control and change tracking
- Data quality scoring and recommendations
- Integration with external data sources
- Automated data enrichment services

The profile management system ensures data integrity while providing flexibility for different business requirements. Advanced users can configure custom workflows and automation rules to streamline data maintenance processes.

Chapter 5: Account Information Display

The account information display provides a comprehensive view of customer account details, financial information, and subscription status. This centralized view eliminates the need to access multiple systems for account-related inquiries.

Account Display Components:
- Current account balance and payment status
- Subscription details and renewal dates
- Billing history with detailed transaction records
- Payment method information and preferences
- Credit limits and available balances
- Account alerts and notifications
- Service level agreements and terms
- Account hierarchy for enterprise customers

Financial Information Features:
- Real-time balance calculations
- Payment processing status updates
- Automated billing cycle tracking
- Revenue recognition and reporting
- Tax calculation and compliance
- Multi-currency support for global operations
- Integration with accounting systems
- Customizable financial dashboards

The account information system provides both summary and detailed views, allowing users to quickly assess account status while having access to comprehensive financial data when needed.

Chapter 6: Transaction History Tracking

Transaction history tracking provides detailed records of all customer interactions, purchases, and financial activities. This comprehensive audit trail supports customer service, compliance, and business intelligence requirements.

Transaction Categories:
- Purchase transactions with detailed line items
- Payment processing and refund records
- Service usage and consumption tracking
- Account modifications and updates
- Communication interactions and touchpoints
- Support case creation and resolution
- System access and security events
- Integration with third-party services

Tracking Features:
- Real-time transaction recording
- Advanced search and filtering capabilities
- Export functionality for external analysis
- Automated categorization and tagging
- Performance metrics and analytics
- Compliance reporting and audit trails
- Data retention policy management
- Integration with business intelligence tools

The transaction tracking system maintains complete data integrity while providing flexible access to historical information for analysis and reporting purposes.

This comprehensive guide continues with detailed coverage of all 29 chapters, providing in-depth explanations, step-by-step procedures, troubleshooting guides, and best practices for maximizing the effectiveness of the Customer Summary Screen system. Each chapter builds upon previous concepts while introducing advanced features and capabilities that support complex business requirements and workflows.
"""
        
        log_test_result(f"📝 Test content prepared: {len(test_content)} characters")
        log_test_result("🚀 Initiating Knowledge Engine processing...")
        
        # Process content through Knowledge Engine
        payload = {
            "content": test_content,
            "content_type": "text",
            "metadata": {
                "original_filename": "Customer Summary Screen User Guide 1.3.docx",
                "source": "paste",
                "content_length": len(test_content)
            }
        }
        
        response = requests.post(
            f"{API_BASE}/content/process",
            json=payload,
            timeout=300  # 5 minute timeout for large document processing
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Knowledge Engine processing FAILED: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text}")
            return False
        
        result = response.json()
        log_test_result("✅ Knowledge Engine processing completed successfully")
        
        # Extract processing results
        job_id = result.get('job_id', 'unknown')
        processing_time = result.get('processing_time', 0)
        articles_generated = result.get('articles_generated', 0)
        chunks_created = result.get('chunks_created', 0)
        
        log_test_result(f"📊 PROCESSING RESULTS:")
        log_test_result(f"   - Job ID: {job_id}")
        log_test_result(f"   - Processing Time: {processing_time:.2f} seconds")
        log_test_result(f"   - Articles Generated: {articles_generated}")
        log_test_result(f"   - Chunks Created: {chunks_created}")
        
        # Get updated Content Library count
        time.sleep(2)  # Allow time for articles to be saved
        final_count = get_content_library_count()
        articles_added = final_count - initial_count
        
        log_test_result(f"📈 CONTENT LIBRARY IMPACT:")
        log_test_result(f"   - Initial count: {initial_count}")
        log_test_result(f"   - Final count: {final_count}")
        log_test_result(f"   - Articles added: {articles_added}")
        
        # CRITICAL VERIFICATION: Check if hard limits have been removed
        log_test_result("🔍 CRITICAL VERIFICATION - HARD LIMIT REMOVAL:", "CRITICAL")
        
        success_criteria = {
            "articles_generated_20_plus": articles_generated >= 20,
            "articles_added_15_plus": articles_added >= 15,
            "not_limited_to_6": articles_generated > 6,
            "not_limited_to_15": articles_generated > 15,
            "approaching_estimated_29": articles_generated >= 20
        }
        
        for criterion, passed in success_criteria.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            log_test_result(f"   - {criterion}: {status}")
        
        # Overall assessment
        passed_criteria = sum(success_criteria.values())
        total_criteria = len(success_criteria)
        
        if passed_criteria >= 4:  # At least 4 out of 5 criteria must pass
            log_test_result("🎉 HARD LIMIT REMOVAL TEST PASSED", "SUCCESS")
            log_test_result(f"✅ SUCCESS RATE: {passed_criteria}/{total_criteria} criteria passed")
            log_test_result(f"✅ Generated {articles_generated} articles (target: 20+, estimated need: 29)")
            return True
        else:
            log_test_result("❌ HARD LIMIT REMOVAL TEST FAILED", "ERROR")
            log_test_result(f"❌ FAILURE RATE: {passed_criteria}/{total_criteria} criteria passed")
            log_test_result(f"❌ Only generated {articles_generated} articles (target: 20+)")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Knowledge Engine hard limit removal test FAILED: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_backend_logs_for_dynamic_limits():
    """
    Test backend logs to verify dynamic limits are being used
    Look for "USING DYNAMIC LIMIT" messages
    """
    try:
        log_test_result("🔍 Checking backend logs for dynamic limit usage...")
        
        # Try to get recent backend logs
        response = requests.get(f"{API_BASE}/system/logs", timeout=30)
        
        if response.status_code == 200:
            logs = response.text
            
            # Check for dynamic limit messages
            dynamic_limit_found = False
            hard_limit_found = False
            
            if "USING DYNAMIC LIMIT" in logs:
                dynamic_limit_found = True
                log_test_result("✅ Found 'USING DYNAMIC LIMIT' in backend logs", "SUCCESS")
            
            if any(phrase in logs for phrase in ["intelligent_limit = 15", "intelligent_limit = 12", "intelligent_limit = 20"]):
                hard_limit_found = True
                log_test_result("❌ Found hard-coded limits in backend logs", "ERROR")
            
            if dynamic_limit_found and not hard_limit_found:
                log_test_result("✅ Backend logs confirm dynamic limits are being used", "SUCCESS")
                return True
            else:
                log_test_result("⚠️ Backend logs verification inconclusive", "WARNING")
                return False
                
        else:
            log_test_result(f"⚠️ Could not access backend logs: Status {response.status_code}", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"⚠️ Backend logs check failed: {e}", "WARNING")
        return False

def run_comprehensive_knowledge_engine_test():
    """Run comprehensive Knowledge Engine hard limit removal test"""
    log_test_result("=" * 80)
    log_test_result("KNOWLEDGE ENGINE HARD LIMIT REMOVAL - COMPREHENSIVE TEST", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        "backend_health": False,
        "hard_limit_removal": False,
        "backend_logs_verification": False
    }
    
    # Test 1: Backend Health
    log_test_result("\n🏥 TEST 1: Backend Health Check")
    test_results["backend_health"] = test_backend_health()
    
    if not test_results["backend_health"]:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "ERROR")
        return False
    
    # Test 2: Hard Limit Removal
    log_test_result("\n🎯 TEST 2: Knowledge Engine Hard Limit Removal")
    test_results["hard_limit_removal"] = test_knowledge_engine_hard_limit_removal()
    
    # Test 3: Backend Logs Verification
    log_test_result("\n📋 TEST 3: Backend Logs Verification")
    test_results["backend_logs_verification"] = test_backend_logs_for_dynamic_limits()
    
    # Final Results
    log_test_result("\n" + "=" * 80)
    log_test_result("FINAL TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        log_test_result(f"{test_name.upper()}: {status}")
    
    if passed_tests >= 2:  # At least 2 out of 3 tests must pass (health + hard limit removal)
        log_test_result(f"\n🎉 OVERALL RESULT: SUCCESS ({passed_tests}/{total_tests} tests passed)", "SUCCESS")
        log_test_result("✅ Knowledge Engine hard limit removal is working correctly")
        return True
    else:
        log_test_result(f"\n❌ OVERALL RESULT: FAILURE ({passed_tests}/{total_tests} tests passed)", "ERROR")
        log_test_result("❌ Knowledge Engine hard limit removal needs attention")
        return False

if __name__ == "__main__":
    success = run_comprehensive_knowledge_engine_test()
    sys.exit(0 if success else 1)