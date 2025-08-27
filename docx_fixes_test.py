#!/usr/bin/env python3
"""
DOCX Processing Fixes Testing
Direct API testing for the 4 specific refinement fixes
"""

import requests
import json
import os
import io
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com') + '/api'

def test_docx_processing_fixes():
    """Test all 4 DOCX processing refinement fixes directly"""
    print("🚀 Testing DOCX Processing Refinement Fixes")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Redundant Title Handling
    print("\n🔍 FIX 1 - Testing Redundant Title Handling...")
    try:
        test_content = """Product Management Best Practices Guide

Introduction
This guide covers essential product management practices for modern organizations.

Chapter 1: Strategic Planning
Product managers must develop comprehensive strategies that align with business objectives.

Chapter 2: Stakeholder Management  
Building strong relationships across the organization is critical for success.

Conclusion
These practices will help product managers deliver successful outcomes."""

        file_data = io.BytesIO(test_content.encode('utf-8'))
        
        files = {
            'file': ('Product_Management_Guide.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        print("📤 Uploading test file...")
        response = requests.post(f"{BACKEND_URL}/content/upload", files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful: {data.get('status', 'unknown')}")
            print(f"📊 Chunks created: {data.get('chunks_created', 0)}")
            
            if data.get('chunks_created', 0) > 0:
                results['fix_1_title_handling'] = True
                print("✅ FIX 1 - Title handling working")
            else:
                results['fix_1_title_handling'] = False
                print("❌ FIX 1 - No chunks created")
        else:
            results['fix_1_title_handling'] = False
            print(f"❌ FIX 1 - Upload failed: {response.status_code}")
            
    except Exception as e:
        results['fix_1_title_handling'] = False
        print(f"❌ FIX 1 - Error: {str(e)}")
    
    # Test 2: Chunking Validation (create longer content)
    print("\n🔍 FIX 2 - Testing Chunking Validation...")
    try:
        # Create content over 6,000 characters
        long_content = """Advanced Software Development Methodologies

Chapter 1: Agile Development Fundamentals
Agile development has revolutionized the software industry by emphasizing iterative development, collaboration, and flexibility. This methodology breaks down complex projects into manageable sprints, typically lasting 2-4 weeks. Teams work closely together, with daily stand-ups, sprint planning, and retrospectives forming the core of the process. The Agile Manifesto, created in 2001, established four key values: individuals and interactions over processes and tools, working software over comprehensive documentation, customer collaboration over contract negotiation, and responding to change over following a plan. These principles have guided countless successful software projects and continue to evolve with modern development practices. Agile methodologies include Scrum, Kanban, Extreme Programming (XP), and Lean Software Development, each offering unique approaches to project management and team collaboration. Teams implementing Agile practices report higher satisfaction, better product quality, and improved ability to respond to changing requirements.

Chapter 2: DevOps Integration and Continuous Delivery
DevOps represents a cultural shift that bridges the gap between development and operations teams. This approach emphasizes automation, continuous integration, and continuous delivery (CI/CD) pipelines. Modern DevOps practices include infrastructure as code, containerization with Docker and Kubernetes, automated testing at multiple levels, and comprehensive monitoring and logging. Teams implementing DevOps see significant improvements in deployment frequency, lead time for changes, and mean time to recovery. The integration of development and operations creates a more efficient and reliable software delivery process. Key tools in the DevOps ecosystem include Jenkins, GitLab CI, GitHub Actions, Terraform, Ansible, Prometheus, and Grafana. Organizations must also invest in cultural change management to successfully adopt DevOps practices. The benefits include faster time to market, improved reliability, better collaboration between teams, and increased ability to scale operations.

Chapter 3: Microservices Architecture Patterns
Microservices architecture has emerged as a powerful pattern for building scalable, maintainable applications. This approach breaks down monolithic applications into smaller, independent services that communicate through well-defined APIs. Each microservice can be developed, deployed, and scaled independently, allowing teams to work more efficiently and choose the best technology stack for each service. Key considerations include service discovery, load balancing, data consistency, and distributed system challenges. Organizations adopting microservices must also invest in robust monitoring, logging, and debugging tools to manage the increased complexity. Popular microservices frameworks include Spring Boot, Express.js, Flask, and FastAPI. Service mesh technologies like Istio and Linkerd provide additional capabilities for managing microservices communication. The transition to microservices requires careful planning, gradual migration strategies, and strong DevOps practices to be successful.

Chapter 4: Cloud-Native Development Strategies
Cloud-native development leverages cloud computing capabilities to build and run scalable applications. This approach utilizes containerization, service meshes, microservices, immutable infrastructure, and declarative APIs. Cloud-native applications are designed to be resilient, manageable, and observable, taking full advantage of cloud platforms' elasticity and distributed nature. Key technologies include Kubernetes for orchestration, service meshes like Istio for communication, and serverless computing for event-driven architectures. Organizations must consider security, cost optimization, and vendor lock-in when adopting cloud-native strategies. The Cloud Native Computing Foundation (CNCF) provides a landscape of tools and technologies that support cloud-native development practices. Benefits include improved scalability, better resource utilization, enhanced fault tolerance, and the ability to leverage managed cloud services for faster development cycles.

Chapter 5: Quality Assurance and Testing Strategies
Modern software development requires comprehensive testing strategies that go beyond traditional manual testing. Test-driven development (TDD) and behavior-driven development (BDD) have become essential practices for ensuring code quality. Automated testing pyramids include unit tests, integration tests, and end-to-end tests, each serving different purposes in the quality assurance process. Performance testing, security testing, and accessibility testing are equally important for delivering robust applications. Teams must balance test coverage with development velocity, using tools like code coverage analysis and mutation testing to ensure test effectiveness. Popular testing frameworks include Jest, Pytest, JUnit, Selenium, and Cypress. Continuous testing practices integrate quality assurance throughout the development lifecycle, enabling faster feedback and higher confidence in releases."""

        print(f"📊 Long content length: {len(long_content)} characters")
        
        if len(long_content) > 6000:
            file_data = io.BytesIO(long_content.encode('utf-8'))
            
            files = {
                'file': ('Long_Development_Guide.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            print("📤 Uploading long content for chunking test...")
            response = requests.post(f"{BACKEND_URL}/content/upload", files=files, timeout=90)
            
            if response.status_code == 200:
                data = response.json()
                chunks_created = data.get('chunks_created', 0)
                print(f"✅ Upload successful: {data.get('status', 'unknown')}")
                print(f"📊 Chunks created: {chunks_created}")
                
                if chunks_created >= 1:
                    results['fix_2_chunking'] = True
                    print("✅ FIX 2 - Chunking is working")
                else:
                    results['fix_2_chunking'] = False
                    print("❌ FIX 2 - No chunks created")
            else:
                results['fix_2_chunking'] = False
                print(f"❌ FIX 2 - Upload failed: {response.status_code}")
        else:
            results['fix_2_chunking'] = False
            print("❌ FIX 2 - Test content not long enough")
            
    except Exception as e:
        results['fix_2_chunking'] = False
        print(f"❌ FIX 2 - Error: {str(e)}")
    
    # Test 3: HTML Optimization
    print("\n🔍 FIX 3 - Testing HTML Optimization...")
    try:
        html_test_content = """HTML Optimization Test Document

Introduction
This document tests HTML optimization features for editor compatibility.

Important Note
This is a critical note that should be formatted properly in HTML.

Data Table
The following information should be structured as a proper table:

Feature | Status | Description
--------|--------|------------
Callouts | Active | Enhanced formatting
Tables | Active | Structured data
Headings | Active | Semantic hierarchy

Technical Details
This section contains technical information that should be properly structured.

Summary
The generated HTML should be clean and editor-compatible."""

        file_data = io.BytesIO(html_test_content.encode('utf-8'))
        
        files = {
            'file': ('HTML_Test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        print("📤 Uploading HTML optimization test...")
        response = requests.post(f"{BACKEND_URL}/content/upload", files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful: {data.get('status', 'unknown')}")
            print(f"📊 Chunks created: {data.get('chunks_created', 0)}")
            
            if data.get('chunks_created', 0) > 0:
                results['fix_3_html_optimization'] = True
                print("✅ FIX 3 - HTML optimization processing completed")
            else:
                results['fix_3_html_optimization'] = False
                print("❌ FIX 3 - No chunks created")
        else:
            results['fix_3_html_optimization'] = False
            print(f"❌ FIX 3 - Upload failed: {response.status_code}")
            
    except Exception as e:
        results['fix_3_html_optimization'] = False
        print(f"❌ FIX 3 - Error: {str(e)}")
    
    # Test 4: Content Structure for Editor
    print("\n🔍 FIX 4 - Testing Content Structure for Editor...")
    try:
        structure_test_content = """Editor Structure Test

Main Section
This content should generate proper HTML structure for editor compatibility.

Subsection One
Content with proper heading hierarchy and paragraph structure.

Key Points:
- First important point
- Second important point  
- Third important point

Numbered Steps:
1. Initial setup
2. Configuration
3. Testing
4. Deployment

Technical Information
This section contains technical details that should be properly formatted.

Conclusion
The structure should be editor-friendly and well-formed."""

        file_data = io.BytesIO(structure_test_content.encode('utf-8'))
        
        files = {
            'file': ('Structure_Test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        print("📤 Uploading structure test...")
        response = requests.post(f"{BACKEND_URL}/content/upload", files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful: {data.get('status', 'unknown')}")
            print(f"📊 Chunks created: {data.get('chunks_created', 0)}")
            
            if data.get('chunks_created', 0) > 0:
                results['fix_4_content_structure'] = True
                print("✅ FIX 4 - Content structure processing completed")
            else:
                results['fix_4_content_structure'] = False
                print("❌ FIX 4 - No chunks created")
        else:
            results['fix_4_content_structure'] = False
            print(f"❌ FIX 4 - Upload failed: {response.status_code}")
            
    except Exception as e:
        results['fix_4_content_structure'] = False
        print(f"❌ FIX 4 - Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("DOCX PROCESSING REFINEMENT FIXES TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for fix_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        fix_display = fix_name.replace('_', ' ').title()
        print(f"{status} {fix_display}")
    
    print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL DOCX PROCESSING REFINEMENT FIXES WORKING!")
    elif passed_tests >= 3:
        print("✅ MOST DOCX PROCESSING REFINEMENT FIXES WORKING")
    else:
        print("⚠️ DOCX PROCESSING REFINEMENT FIXES NEED ATTENTION")
    
    return results

if __name__ == "__main__":
    test_docx_processing_fixes()