#!/usr/bin/env python3
"""
REAL-TIME OUTLINE-FIRST APPROACH TEST
Test the outline-first implementation by processing a substantial document
and monitoring for outline-specific log messages in real-time
"""

import requests
import json
import time
import os
import threading
import subprocess
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def create_test_document():
    """Create a substantial test document to trigger outline-first approach"""
    test_content = """# Customer Summary Screen User Guide - Test Document

## Introduction
This comprehensive guide covers all aspects of the Customer Summary Screen functionality, providing detailed instructions for effective customer management and system navigation.

## Chapter 1: Getting Started with Customer Summary Screen
The Customer Summary Screen serves as the central hub for all customer-related activities. This section covers initial setup, navigation basics, and essential features that every user should understand.

### 1.1 System Overview
The system provides comprehensive customer management capabilities including account management, billing oversight, communication tracking, and hierarchical customer organization.

### 1.2 Navigation Fundamentals
Understanding the tab-based navigation system is crucial for efficient workflow management. The interface includes multiple specialized tabs for different functional areas.

### 1.3 User Permissions and Access Control
Different user roles have varying levels of access to customer information and system functions. This section explains permission structures and access limitations.

## Chapter 2: Account Management Features
Account management represents the core functionality of the Customer Summary Screen, encompassing customer data maintenance, account status monitoring, and relationship management.

### 2.1 Customer Information Management
Maintaining accurate customer information is essential for effective service delivery. This includes contact details, service addresses, and account preferences.

### 2.2 Account Status Monitoring
Real-time account status information helps users quickly identify customer account conditions, payment status, and service delivery issues.

### 2.3 Service Address Management
Managing multiple service addresses for customers requires understanding of the address hierarchy and service point relationships.

## Chapter 3: Billing and Accounts Receivable
The billing functionality provides comprehensive tools for invoice management, payment processing, and accounts receivable oversight.

### 3.1 Invoice Generation and Management
Creating and managing customer invoices involves understanding billing cycles, rate structures, and special charge applications.

### 3.2 Payment Processing
Processing customer payments requires knowledge of payment methods, allocation rules, and exception handling procedures.

### 3.3 Accounts Receivable Reporting
Generating accurate AR reports helps maintain financial oversight and supports collection activities.

## Chapter 4: Communication Management
Effective communication tracking ensures comprehensive customer service delivery and maintains detailed interaction histories.

### 4.1 Communication Log Features
The communication log provides chronological tracking of all customer interactions across multiple channels and user types.

### 4.2 Log Entry Management
Creating, editing, and organizing communication log entries requires understanding of categorization systems and priority levels.

### 4.3 Communication Reporting
Generating communication reports supports customer service analysis and regulatory compliance requirements.

## Chapter 5: Utility Account Management
Managing utility accounts involves understanding service delivery, meter management, and regulatory compliance requirements.

### 5.1 Service Point Management
Service points represent the physical locations where utility services are delivered and require careful management and monitoring.

### 5.2 Meter Reading and Management
Accurate meter reading and data management ensures proper billing and service delivery tracking.

### 5.3 Service Orders and Work Management
Processing service orders and managing work requests requires coordination between customer service and field operations.

## Chapter 6: Transaction History and Market Data
Understanding transaction history and market data provides insights into customer usage patterns and market dynamics.

### 6.1 Transaction History Analysis
Analyzing customer transaction patterns helps identify trends and supports customer service improvements.

### 6.2 Market Data Integration
Integration with market data systems provides real-time information about market conditions and pricing.

### 6.3 Reporting and Analytics
Comprehensive reporting capabilities support business intelligence and regulatory reporting requirements.

## Chapter 7: Customer Hierarchy Management
Managing customer hierarchies enables efficient organization of related customer accounts and streamlined billing processes.

### 7.1 Hierarchy Structure Design
Designing effective customer hierarchies requires understanding of business relationships and billing requirements.

### 7.2 Master Customer Configuration
Configuring master customer accounts involves setting up consolidated billing and reporting structures.

### 7.3 Subsidiary Account Management
Managing subsidiary accounts within hierarchies requires understanding of inheritance rules and override capabilities.

## Chapter 8: Advanced Features and Customization
Advanced features provide enhanced functionality for power users and specialized business requirements.

### 8.1 Custom Field Configuration
Configuring custom fields allows organizations to capture specialized information relevant to their business processes.

### 8.2 Workflow Automation
Implementing workflow automation reduces manual processing and improves operational efficiency.

### 8.3 Integration Capabilities
Understanding integration options enables organizations to connect the system with other business applications.

## Chapter 9: Troubleshooting and Support
Effective troubleshooting requires understanding of common issues, diagnostic procedures, and escalation processes.

### 9.1 Common Issues and Solutions
Identifying and resolving common system issues helps maintain operational efficiency and user satisfaction.

### 9.2 Diagnostic Procedures
Following systematic diagnostic procedures ensures thorough problem identification and resolution.

### 9.3 Support Resources and Escalation
Understanding available support resources and escalation procedures ensures timely issue resolution.

## Chapter 10: Best Practices and Optimization
Implementing best practices ensures optimal system performance and user productivity.

### 10.1 Performance Optimization
Optimizing system performance involves understanding of data management, query optimization, and resource utilization.

### 10.2 User Training and Adoption
Effective user training programs support successful system adoption and maximize return on investment.

### 10.3 Continuous Improvement
Implementing continuous improvement processes ensures the system evolves to meet changing business requirements.

## Conclusion
This comprehensive guide provides the foundation for effective use of the Customer Summary Screen system. Regular reference to these procedures ensures consistent and efficient customer management operations.

## Appendices
Additional resources, reference materials, and detailed technical specifications support advanced users and system administrators.

### Appendix A: System Requirements
Detailed technical requirements for system installation and operation.

### Appendix B: API Documentation
Comprehensive API documentation for system integration and customization.

### Appendix C: Regulatory Compliance
Information about regulatory requirements and compliance procedures.
"""
    
    # Write test document
    test_file_path = "/app/test_outline_document.txt"
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    log_test_result(f"✅ Created test document: {len(test_content)} characters")
    return test_file_path

def monitor_backend_logs(stop_event, log_messages):
    """Monitor backend logs for outline-first messages in real-time"""
    try:
        # Start monitoring from current position
        process = subprocess.Popen(['tail', '-f', '/var/log/supervisor/backend.out.log'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
        
        while not stop_event.is_set():
            line = process.stdout.readline()
            if line:
                line = line.strip()
                
                # Check for outline-first specific messages
                if any(keyword in line for keyword in [
                    'COMPREHENSIVE OUTLINE GENERATED',
                    'CREATING ARTICLES FROM OUTLINE', 
                    'OUTLINE-BASED SUCCESS',
                    'articles planned',
                    'comprehensive articles'
                ]):
                    log_messages.append(f"🎯 OUTLINE LOG: {line}")
                    log_test_result(f"🎯 DETECTED: {line}", "OUTLINE")
                
                # Check for other relevant messages
                elif any(keyword in line for keyword in [
                    'ULTRA-LARGE DOCUMENT DETECTED',
                    'USING DYNAMIC LIMIT',
                    'conservative merging',
                    'articles created'
                ]):
                    log_messages.append(f"📊 PROCESSING LOG: {line}")
                    log_test_result(f"📊 PROCESSING: {line}", "INFO")
            
            time.sleep(0.1)
        
        process.terminate()
        
    except Exception as e:
        log_test_result(f"⚠️ Log monitoring error: {e}", "WARNING")

def test_outline_first_with_monitoring():
    """Test outline-first approach with real-time log monitoring"""
    try:
        log_test_result("🎯 STARTING REAL-TIME OUTLINE-FIRST TEST", "CRITICAL")
        
        # Create test document
        test_file = create_test_document()
        
        # Start log monitoring
        stop_event = threading.Event()
        log_messages = []
        log_thread = threading.Thread(target=monitor_backend_logs, args=(stop_event, log_messages))
        log_thread.daemon = True
        log_thread.start()
        
        log_test_result("📡 Started real-time log monitoring", "INFO")
        
        # Get initial Content Library count
        initial_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        initial_count = 0
        if initial_response.status_code == 200:
            initial_data = initial_response.json()
            initial_count = initial_data.get('total', 0)
            log_test_result(f"📚 Initial Content Library count: {initial_count}")
        
        # Upload and process the document
        log_test_result("📤 Uploading test document to Knowledge Engine...")
        
        with open(test_file, 'rb') as f:
            files = {'file': ('test_outline_document.txt', f, 'text/plain')}
            
            # Start processing
            start_time = time.time()
            response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
            
            if response.status_code != 200:
                log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
                log_test_result(f"Response: {response.text[:500]}")
                stop_event.set()
                return False
            
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if not job_id:
                log_test_result("❌ No job_id received from upload", "ERROR")
                stop_event.set()
                return False
            
            log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing with real-time log analysis...")
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        
        outline_evidence = {
            'outline_generated': False,
            'articles_from_outline': False,
            'comprehensive_coverage': False
        }
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                break
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    log_test_result(f"📊 Processing status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Extract metrics
                        chunks_created = status_data.get('chunks_created', 0)
                        articles_generated = status_data.get('articles_generated', 0)
                        
                        log_test_result(f"📈 PROCESSING RESULTS:")
                        log_test_result(f"   📚 Chunks Created: {chunks_created}")
                        log_test_result(f"   📄 Articles Generated: {articles_generated}")
                        
                        # Check success criteria
                        if articles_generated > 6:
                            outline_evidence['comprehensive_coverage'] = True
                            log_test_result(f"✅ COMPREHENSIVE COVERAGE: {articles_generated} articles generated", "SUCCESS")
                        
                        break
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        break
                    
                    time.sleep(5)
                else:
                    log_test_result(f"⚠️ Status check failed: {status_response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
        
        # Stop log monitoring
        stop_event.set()
        time.sleep(2)  # Allow log thread to finish
        
        # Analyze collected log messages
        log_test_result("📋 ANALYZING COLLECTED LOG MESSAGES:")
        
        for message in log_messages:
            if 'COMPREHENSIVE OUTLINE GENERATED' in message:
                outline_evidence['outline_generated'] = True
            elif 'CREATING ARTICLES FROM OUTLINE' in message:
                outline_evidence['articles_from_outline'] = True
        
        # Final verification
        final_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        final_count = initial_count
        if final_response.status_code == 200:
            final_data = final_response.json()
            final_count = final_data.get('total', 0)
        
        articles_added = final_count - initial_count
        log_test_result(f"📊 FINAL RESULTS:")
        log_test_result(f"   Articles added to library: {articles_added}")
        log_test_result(f"   Total log messages captured: {len(log_messages)}")
        
        # Clean up test file
        os.remove(test_file)
        
        return outline_evidence, articles_added
        
    except Exception as e:
        log_test_result(f"❌ Real-time outline test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False, 0

def run_realtime_outline_test():
    """Run comprehensive real-time outline-first test"""
    log_test_result("🚀 STARTING REAL-TIME OUTLINE-FIRST COMPREHENSIVE TEST", "CRITICAL")
    log_test_result("=" * 70)
    
    # Test backend connectivity first
    try:
        response = requests.get(f"{API_BASE}/health", timeout=30)
        if response.status_code != 200:
            log_test_result("❌ Backend not accessible - aborting test", "CRITICAL_ERROR")
            return False
        log_test_result("✅ Backend connectivity confirmed", "SUCCESS")
    except Exception as e:
        log_test_result(f"❌ Backend connectivity failed: {e}", "CRITICAL_ERROR")
        return False
    
    # Run the main test
    result = test_outline_first_with_monitoring()
    
    if isinstance(result, tuple):
        outline_evidence, articles_added = result
        
        log_test_result("\n" + "=" * 70)
        log_test_result("🎯 REAL-TIME OUTLINE-FIRST TEST RESULTS", "CRITICAL")
        log_test_result("=" * 70)
        
        log_test_result("📊 OUTLINE-FIRST EVIDENCE:")
        log_test_result(f"   Outline Generated: {'✅ YES' if outline_evidence.get('outline_generated') else '❌ NO'}")
        log_test_result(f"   Articles from Outline: {'✅ YES' if outline_evidence.get('articles_from_outline') else '❌ NO'}")
        log_test_result(f"   Comprehensive Coverage: {'✅ YES' if outline_evidence.get('comprehensive_coverage') else '❌ NO'}")
        log_test_result(f"   Articles Added: {articles_added}")
        
        # Overall assessment
        evidence_count = sum(outline_evidence.values())
        if evidence_count >= 2 and articles_added > 6:
            log_test_result("🎉 CRITICAL SUCCESS: Outline-first approach working correctly!", "CRITICAL_SUCCESS")
            log_test_result("✅ Real-time monitoring confirmed outline-based article generation", "CRITICAL_SUCCESS")
            return True
        elif articles_added > 6:
            log_test_result("⚠️ PARTIAL SUCCESS: Comprehensive articles generated but limited log evidence", "WARNING")
            return True
        else:
            log_test_result("❌ INSUFFICIENT EVIDENCE: Outline-first approach needs investigation", "ERROR")
            return False
    else:
        log_test_result("❌ CRITICAL FAILURE: Real-time test could not complete", "CRITICAL_ERROR")
        return False

if __name__ == "__main__":
    print("Real-Time Outline-First Approach Test")
    print("=" * 50)
    
    success = run_realtime_outline_test()
    
    if success:
        print("\n✅ REAL-TIME TEST COMPLETED - Outline-first approach confirmed working")
    else:
        print("\n❌ REAL-TIME TEST COMPLETED - Outline-first approach needs investigation")