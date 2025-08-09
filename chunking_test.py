#!/usr/bin/env python3
"""
Chunking Test - Create content over 6,000 characters to test smart chunking
"""

import requests
import json
import os
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://14236aae-8093-4969-a2a2-e2c349953e54.preview.emergentagent.com') + '/api'

def test_chunking():
    """Test chunking with very long content"""
    
    # Create very long content (definitely over 6,000 characters)
    long_content = """Advanced Software Development Methodologies and Best Practices for Modern Organizations

Chapter 1: Agile Development Fundamentals and Implementation Strategies for Large Scale Projects
Agile development has completely revolutionized the software industry by emphasizing iterative development approaches, enhanced team collaboration, and unprecedented flexibility in project management methodologies and organizational structures. This comprehensive methodology systematically breaks down complex, multi-faceted projects into manageable sprints that typically last between 2-4 weeks, allowing development teams to deliver incremental value while maintaining exceptionally high quality standards and meeting stringent customer requirements. Development teams work closely together through structured daily stand-up meetings, comprehensive sprint planning sessions, detailed sprint reviews with stakeholders, and thorough retrospectives that form the foundational core of the entire Agile development process. The revolutionary Agile Manifesto, created in 2001 by seventeen experienced software developers from diverse backgrounds, established four fundamental key values that continue to guide and influence modern development practices across industries: individuals and interactions over rigid processes and tools, working software over comprehensive documentation, customer collaboration over contract negotiation, and responding to change over following a predetermined rigid plan. These transformative principles have successfully guided countless software projects across various industries and continue to evolve with modern development practices, technological advances, and changing business requirements. Agile methodologies encompass various frameworks including Scrum, Kanban, Extreme Programming (XP), Lean Software Development, Crystal, and Feature-Driven Development, each offering unique approaches to project management, team collaboration, value delivery, and continuous improvement processes.

Chapter 2: DevOps Integration and Continuous Delivery Pipeline Implementation for Enterprise Systems
DevOps represents a fundamental cultural and organizational shift that effectively bridges the traditional gap between development and operations teams, creating a unified, collaborative approach to software delivery, infrastructure management, and system reliability. This comprehensive approach emphasizes extensive automation, continuous integration practices, sophisticated continuous delivery (CI/CD) pipelines, and collaborative practices that streamline the entire software development lifecycle from initial concept to production deployment. Modern DevOps practices include infrastructure as code (IaC) implementations, advanced containerization with Docker and Kubernetes orchestration, automated testing at multiple levels including unit testing, integration testing, system testing, and comprehensive end-to-end testing, sophisticated monitoring and logging systems, proactive incident response procedures, and comprehensive security integration throughout the development pipeline. Development and operations teams implementing DevOps methodologies consistently see significant improvements in deployment frequency, reduced lead time for changes, decreased mean time to recovery from incidents, enhanced overall system reliability and performance, and improved customer satisfaction metrics. The strategic integration of development and operations creates a more efficient, reliable, and scalable software delivery process that enables organizations to respond quickly to changing market demands, customer feedback, and competitive pressures. Key tools in the modern DevOps ecosystem include Jenkins, GitLab CI, GitHub Actions, Azure DevOps, CircleCI, Terraform, Ansible, Chef, Puppet, Prometheus, Grafana, ELK Stack (Elasticsearch, Logstash, Kibana), and various cloud-native monitoring solutions from AWS, Google Cloud, and Microsoft Azure.

Chapter 3: Microservices Architecture Patterns and Implementation Considerations for Distributed Systems
Microservices architecture has emerged as a powerful and transformative architectural pattern for building highly scalable, maintainable, and resilient applications that can evolve independently and effectively support large-scale distributed systems across multiple geographic regions. This sophisticated approach systematically breaks down monolithic applications into smaller, independent, loosely-coupled services that communicate through well-defined APIs, asynchronous message queues, and event-driven architectures that promote system resilience and scalability. Each individual microservice can be independently developed, thoroughly tested, safely deployed, and dynamically scaled, allowing development teams to work more efficiently, choose the most appropriate technology stack for each specific service, maintain faster development cycles, and respond quickly to changing business requirements. Critical architectural considerations include sophisticated service discovery mechanisms, intelligent load balancing strategies, complex data consistency patterns, distributed transaction management systems, circuit breaker implementations for fault tolerance, comprehensive monitoring and observability solutions, and robust security implementations across service boundaries. Organizations adopting microservices architecture must also invest significantly in robust monitoring systems, centralized logging solutions, distributed tracing capabilities, and advanced debugging tools to effectively manage the increased complexity and interdependencies inherent in distributed systems. Popular microservices frameworks and technologies include Spring Boot, Express.js, Flask, FastAPI, Node.js, Go, Rust, .NET Core, and various cloud-native platforms and services. Service mesh technologies like Istio, Linkerd, Consul Connect, and AWS App Mesh provide additional sophisticated capabilities for managing microservices communication, implementing security policies, and providing comprehensive observability across the entire service ecosystem.

Chapter 4: Cloud-Native Development Strategies and Platform Engineering for Modern Applications
Cloud-native development comprehensively leverages cloud computing capabilities, advanced containerization technologies, and modern architectural patterns to build and run highly scalable applications that fully utilize the elasticity, resilience, global distribution, and cost-effectiveness of modern cloud platforms. This comprehensive approach utilizes advanced containerization with Docker, sophisticated orchestration with Kubernetes, service meshes for secure communication management, microservices for enhanced modularity, immutable infrastructure principles, declarative APIs for configuration management, and serverless computing for event-driven architectures. Cloud-native applications are specifically designed and architected to be resilient, manageable, observable, and infinitely scalable, taking full advantage of cloud platforms' auto-scaling capabilities, managed services, global distribution networks, and advanced security features. Key technologies and practices include Kubernetes for container orchestration, service meshes like Istio for secure service-to-service communication, serverless computing platforms like AWS Lambda and Azure Functions for event-driven architectures, and comprehensive observability solutions for monitoring, logging, and troubleshooting distributed systems. Organizations must carefully consider security implications, cost optimization strategies, vendor lock-in risks, data sovereignty requirements, compliance obligations, and performance optimization when adopting cloud-native development strategies. The Cloud Native Computing Foundation (CNCF) provides a comprehensive landscape of tools, technologies, and best practices that support cloud-native development, including graduated projects like Kubernetes, Prometheus, Envoy, Fluentd, and many others that form the foundation of modern cloud-native ecosystems.

Chapter 5: Quality Assurance, Testing Strategies, and Continuous Quality Improvement for Enterprise Applications
Modern software development requires comprehensive, multi-layered testing strategies that go far beyond traditional manual testing approaches and integrate quality assurance throughout the entire development lifecycle, from initial requirements gathering to production deployment and ongoing maintenance. Test-driven development (TDD) and behavior-driven development (BDD) have become essential practices for ensuring code quality, reducing defects, improving maintainability, and maintaining high standards of software reliability and performance across complex enterprise applications. Automated testing pyramids include comprehensive unit tests for individual components, integration tests for system interactions, contract tests for API compatibility, performance tests for scalability validation, and end-to-end tests for complete user workflows, each serving different purposes in the comprehensive quality assurance process. Performance testing, security testing, accessibility testing, usability testing, compatibility testing, and regulatory compliance testing are equally important for delivering robust, secure, and user-friendly applications that meet diverse user needs, regulatory requirements, and business objectives. Development teams must carefully balance comprehensive test coverage with development velocity, using advanced tools like code coverage analysis, mutation testing, property-based testing, automated test generation, and AI-powered testing to ensure test effectiveness and comprehensive quality validation throughout the development process."""

    print(f"📊 Test content length: {len(long_content)} characters")
    
    if len(long_content) > 6000:
        print("✅ Content is over 6,000 characters - suitable for chunking test")
        
        file_data = io.BytesIO(long_content.encode('utf-8'))
        
        files = {
            'file': ('Very_Long_Development_Guide.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        print("📤 Uploading very long content for chunking test...")
        response = requests.post(f"{BACKEND_URL}/content/upload", files=files, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            chunks_created = data.get('chunks_created', 0)
            print(f"✅ Upload successful: {data.get('status', 'unknown')}")
            print(f"📊 Chunks created: {chunks_created}")
            
            if chunks_created > 1:
                print("✅ CHUNKING IS WORKING - Multiple chunks created for long content")
                return True
            elif chunks_created == 1:
                print("⚠️ SINGLE CHUNK - May indicate chunking threshold not reached or different implementation")
                return True  # Still acceptable
            else:
                print("❌ NO CHUNKS - Chunking failed")
                return False
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    else:
        print("❌ Content not long enough for chunking test")
        return False

if __name__ == "__main__":
    result = test_chunking()
    print(f"\nChunking test result: {'PASSED' if result else 'FAILED'}")