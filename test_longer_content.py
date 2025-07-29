#!/usr/bin/env python3
"""
Test with longer content that should trigger multi-article splitting
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://2318aeda-c194-4690-b95f-460c1aa5825b.preview.emergentagent.com') + '/api'

# Extended test content that should definitely trigger multi-article splitting
EXTENDED_MULTI_SECTION_CONTENT = """# Enterprise Software Documentation

## Chapter 1: System Architecture Overview
This chapter covers the foundational architecture of our enterprise software platform, including core components, data flow patterns, and integration points that form the backbone of the system. The architecture is designed to be scalable, maintainable, and secure, providing a solid foundation for enterprise-level applications.

### Core Components
The system consists of several key components that work together to provide comprehensive functionality:

- Authentication Service: Handles user authentication, authorization, and session management
- Data Processing Engine: Manages data transformation, validation, and processing workflows
- User Interface Layer: Provides responsive web interfaces and API endpoints for client applications
- Database Management System: Ensures data integrity, backup, and recovery capabilities
- API Gateway: Routes requests, handles rate limiting, and provides security controls

### Integration Patterns
The system uses microservices architecture with event-driven communication patterns. This approach enables:

- Loose coupling between services
- Independent scaling of components
- Fault tolerance and resilience
- Technology diversity across services
- Easier maintenance and updates

### Security Architecture
Security is implemented at multiple layers including network security, application security, and data security. Key security features include:

- Multi-factor authentication
- Role-based access control
- Data encryption at rest and in transit
- Security monitoring and alerting
- Regular security audits and penetration testing

## Chapter 2: User Management and Authentication
Comprehensive guide to user management, role-based access control, and authentication mechanisms implemented throughout the platform. This chapter provides detailed information on how to configure, manage, and troubleshoot user-related functionality.

### Authentication Methods
The platform supports multiple authentication methods to accommodate different organizational requirements:

- Single Sign-On (SSO): Integration with SAML 2.0 and OpenID Connect providers
- Multi-Factor Authentication (MFA): Support for SMS, email, and authenticator apps
- OAuth 2.0/OpenID Connect: Modern authentication protocols for API access
- LDAP Integration: Connection to existing directory services
- Certificate-based authentication: For high-security environments

### User Provisioning
User accounts can be created and managed through various methods:

- Manual user creation through the admin interface
- Bulk user import from CSV files
- Automated provisioning through SCIM protocol
- Just-in-time provisioning for SSO users
- API-based user management for integration scenarios

### Role Management
Define and manage user roles with granular permissions. The role-based access control system provides:

- Hierarchical role structures
- Fine-grained permission assignments
- Dynamic role assignment based on user attributes
- Temporary role elevation for specific tasks
- Audit trails for all role changes

## Chapter 3: Data Management and Storage
This chapter covers data management strategies, storage solutions, and data governance practices implemented in the enterprise software platform.

### Database Architecture
The platform uses a hybrid database approach combining:

- Relational databases for transactional data
- NoSQL databases for document storage
- Time-series databases for metrics and logs
- In-memory caches for performance optimization
- Data warehouses for analytics and reporting

### Data Security and Compliance
Data protection measures include:

- Encryption of sensitive data fields
- Data masking for non-production environments
- Compliance with GDPR, HIPAA, and other regulations
- Data retention and deletion policies
- Regular data security assessments

### Backup and Recovery
Comprehensive backup and recovery procedures ensure data availability:

- Automated daily backups
- Point-in-time recovery capabilities
- Cross-region backup replication
- Disaster recovery testing procedures
- Recovery time and point objectives (RTO/RPO)

## Chapter 4: Performance and Monitoring
Performance optimization and system monitoring are critical for maintaining enterprise-level service quality.

### Performance Optimization
Key performance optimization strategies include:

- Database query optimization
- Caching strategies at multiple levels
- Load balancing and auto-scaling
- Content delivery network (CDN) integration
- Performance testing and benchmarking

### Monitoring and Alerting
Comprehensive monitoring covers:

- Application performance monitoring (APM)
- Infrastructure monitoring
- Log aggregation and analysis
- Custom business metrics
- Proactive alerting and incident response

### Capacity Planning
Regular capacity planning activities include:

- Resource utilization analysis
- Growth trend forecasting
- Scalability testing
- Cost optimization strategies
- Technology refresh planning"""

def test_extended_content():
    """Test the extended content that should trigger multi-article splitting"""
    print(f"🔍 Testing Extended Multi-Section Content ({len(EXTENDED_MULTI_SECTION_CONTENT)} characters)")
    
    try:
        # Get initial Content Library count
        initial_response = requests.get(f"{BACKEND_URL}/content-library", timeout=10)
        initial_count = 0
        if initial_response.status_code == 200:
            initial_count = initial_response.json().get('total', 0)
        
        print(f"Initial Content Library articles: {initial_count}")
        
        # Process the extended content
        test_content = {
            "content": EXTENDED_MULTI_SECTION_CONTENT,
            "content_type": "text",
            "metadata": {
                "source": "extended_multi_article_test",
                "test_type": "extended_splitting_logic_test",
                "original_filename": "Extended_Enterprise_Software_Documentation.md",
                "file_extension": "md"
            }
        }
        
        print("Processing extended multi-section content...")
        response = requests.post(
            f"{BACKEND_URL}/content/process",
            json=test_content,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Wait for processing
            time.sleep(10)
            
            # Check final Content Library count
            final_response = requests.get(f"{BACKEND_URL}/content-library", timeout=10)
            if final_response.status_code == 200:
                final_data = final_response.json()
                final_count = final_data.get('total', 0)
                articles = final_data.get('articles', [])
                
                print(f"Final Content Library articles: {final_count}")
                print(f"Articles created: {final_count - initial_count}")
                
                # Look for our test articles
                test_articles = [
                    article for article in articles 
                    if article.get('metadata', {}).get('source') == 'extended_multi_article_test'
                ]
                
                print(f"Test articles found: {len(test_articles)}")
                
                if len(test_articles) > 1:
                    print("✅ Extended content successfully created multiple articles!")
                    
                    for i, article in enumerate(test_articles):
                        print(f"\nArticle {i+1}:")
                        print(f"  Title: {article.get('title', 'N/A')}")
                        print(f"  Summary: {article.get('summary', 'N/A')[:100]}...")
                        print(f"  Tags: {article.get('tags', [])}")
                    
                    return True
                elif len(test_articles) == 1:
                    print("⚠️ Extended content created only 1 article")
                    print(f"Article title: {test_articles[0].get('title', 'N/A')}")
                    return False
                else:
                    print("❌ No test articles found")
                    return False
            else:
                print("❌ Could not check final Content Library state")
                return False
        else:
            print(f"❌ Content processing failed - status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Extended content test failed - {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Extended Multi-Article Content")
    print("=" * 60)
    
    success = test_extended_content()
    
    if success:
        print("\n✅ Multi-article splitting logic is working correctly!")
        print("The original test content was too short (918 chars < 1000 char threshold)")
    else:
        print("\n❌ Multi-article splitting may have issues")
        print("Need to investigate further")