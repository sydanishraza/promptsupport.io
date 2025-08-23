#!/usr/bin/env python3
"""
Large Document Cross-Reference Test
Upload a larger document to force multiple article generation and test cross-references
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://woolf-style-lint.preview.emergentagent.com') + '/api'

def test_large_document_cross_references():
    """Test cross-references with a large document that should generate multiple articles"""
    print("🔍 LARGE DOCUMENT CROSS-REFERENCE TEST")
    print("=" * 60)
    
    # Create a large test document with multiple detailed sections
    large_content = """
# Complete Guide to API Integration

## Introduction to API Integration
API integration is a fundamental aspect of modern web development that enables different software systems to communicate and share data effectively. This comprehensive guide will walk you through every aspect of API integration, from basic concepts to advanced implementation techniques.

Understanding APIs is crucial for developers who want to build scalable, interconnected applications. APIs serve as bridges between different software components, allowing them to exchange information seamlessly. Whether you're working with REST APIs, GraphQL endpoints, or webhook integrations, the principles covered in this guide will help you master the art of API integration.

The modern web ecosystem relies heavily on API integrations to provide rich, dynamic user experiences. From social media integrations to payment processing, APIs power the interconnected web we use every day.

## Prerequisites and Setup Requirements

Before diving into API integration, you need to ensure your development environment is properly configured. This section covers all the essential prerequisites and setup steps required for successful API integration.

### Development Environment Setup
Setting up your development environment is the first critical step in any API integration project. You'll need to install the necessary tools, configure your IDE, and prepare your project structure for optimal development workflow.

Start by installing Node.js and npm if you're working with JavaScript, or Python and pip for Python-based integrations. Ensure you have a reliable code editor with API testing capabilities, such as Visual Studio Code with REST Client extension or Postman for API testing.

### API Key Management
Proper API key management is essential for secure integrations. Never hardcode API keys directly in your source code. Instead, use environment variables or secure configuration files that are excluded from version control.

Create a dedicated configuration file for your API credentials and use a robust key management system. Consider using services like AWS Secrets Manager or Azure Key Vault for production environments.

## Core API Integration Concepts

Understanding the fundamental concepts of API integration is crucial for building robust, maintainable integrations. This section explores the key principles that govern how APIs work and how to integrate them effectively.

### REST API Fundamentals
REST (Representational State Transfer) is the most common architectural style for web APIs. REST APIs use standard HTTP methods (GET, POST, PUT, DELETE) to perform operations on resources identified by URLs.

When working with REST APIs, you'll encounter several key concepts: resources, HTTP methods, status codes, and request/response formats. Each resource in a REST API is identified by a unique URL, and you interact with these resources using standard HTTP methods.

Understanding HTTP status codes is crucial for proper error handling. Status codes in the 200 range indicate success, 400 range indicates client errors, and 500 range indicates server errors.

### Authentication and Authorization
Most APIs require some form of authentication to ensure that only authorized users can access protected resources. Common authentication methods include API keys, OAuth 2.0, and JWT tokens.

API key authentication is the simplest form, where you include a secret key in your requests. OAuth 2.0 is more complex but provides better security for user-facing applications. JWT tokens offer a stateless authentication mechanism that's particularly useful for microservices architectures.

## Implementation Strategies and Best Practices

Implementing API integrations requires careful planning and adherence to best practices. This section covers proven strategies for building reliable, scalable API integrations.

### Error Handling and Retry Logic
Robust error handling is essential for production API integrations. Networks are unreliable, and APIs can experience temporary outages or rate limiting. Your integration code must handle these scenarios gracefully.

Implement exponential backoff retry logic for transient errors. This means waiting progressively longer between retry attempts to avoid overwhelming the API server. Set reasonable timeout values and maximum retry limits to prevent infinite loops.

Log all API interactions, including request details, response codes, and error messages. This logging will be invaluable for debugging issues in production environments.

### Rate Limiting and Throttling
Most APIs implement rate limiting to prevent abuse and ensure fair usage among all clients. Understanding and respecting these limits is crucial for maintaining a good relationship with API providers.

Implement client-side rate limiting to stay within the API's limits. Use techniques like token bucket algorithms or sliding window counters to track your request rate. When you hit rate limits, implement proper backoff strategies.

### Caching Strategies
Effective caching can significantly improve the performance of your API integrations while reducing the load on API servers. Implement caching at multiple levels: in-memory caching for frequently accessed data, database caching for persistent storage, and HTTP caching using standard cache headers.

Consider the freshness requirements of your data when designing caching strategies. Some data can be cached for hours or days, while other data requires real-time updates.

## Advanced Integration Techniques

Once you've mastered the basics, you can explore advanced techniques that will make your integrations more robust and efficient.

### Webhook Integration
Webhooks provide a way for APIs to push data to your application in real-time, rather than requiring you to poll for updates. This is more efficient and provides better user experiences for time-sensitive data.

When implementing webhook endpoints, ensure they're secure, idempotent, and can handle high volumes of requests. Implement proper authentication for incoming webhook requests and use message queues for processing webhook payloads asynchronously.

### GraphQL Integration
GraphQL offers a more flexible alternative to REST APIs, allowing clients to request exactly the data they need. This can reduce over-fetching and improve performance, especially for mobile applications.

When integrating with GraphQL APIs, take advantage of features like query batching, caching, and real-time subscriptions. Use tools like Apollo Client or Relay to manage GraphQL integrations effectively.

## Testing and Monitoring

Comprehensive testing and monitoring are essential for maintaining reliable API integrations in production environments.

### Integration Testing Strategies
Develop comprehensive test suites that cover both happy path scenarios and edge cases. Use tools like Postman, Insomnia, or custom test scripts to automate API testing.

Implement contract testing to ensure your integrations remain compatible as APIs evolve. Tools like Pact can help you maintain contracts between API consumers and providers.

### Monitoring and Alerting
Set up monitoring for your API integrations to detect issues before they impact users. Monitor key metrics like response times, error rates, and throughput.

Implement alerting for critical failures and performance degradation. Use tools like Datadog, New Relic, or custom monitoring solutions to track the health of your integrations.

## Troubleshooting Common Issues

Even with careful planning and implementation, you'll encounter issues with API integrations. This section covers common problems and their solutions.

### Authentication Failures
Authentication issues are among the most common problems in API integrations. Common causes include expired tokens, incorrect credentials, and misconfigured authentication headers.

Always implement proper token refresh logic for OAuth-based integrations. Store refresh tokens securely and handle token expiration gracefully.

### Network and Connectivity Issues
Network problems can cause intermittent failures in API integrations. Implement proper timeout handling and retry logic to handle these issues gracefully.

Use connection pooling and keep-alive connections to improve performance and reliability. Monitor network metrics to identify connectivity patterns and issues.

### Data Format and Validation Errors
APIs may return data in unexpected formats or with validation errors. Implement robust data validation and transformation logic to handle these scenarios.

Use schema validation libraries to ensure incoming data matches your expectations. Implement fallback strategies for handling malformed or incomplete data.

## Security Considerations

Security should be a primary concern in all API integrations. This section covers essential security practices.

### Secure Communication
Always use HTTPS for API communications to encrypt data in transit. Validate SSL certificates and implement certificate pinning for critical integrations.

### Input Validation and Sanitization
Validate and sanitize all data received from APIs before processing or storing it. This prevents injection attacks and data corruption issues.

### Secrets Management
Use proper secrets management practices for storing API keys, tokens, and other sensitive information. Never commit secrets to version control systems.

## Performance Optimization

Optimizing the performance of your API integrations is crucial for providing good user experiences and minimizing resource usage.

### Connection Management
Use connection pooling and persistent connections to reduce the overhead of establishing new connections for each request. Configure appropriate connection timeouts and pool sizes.

### Batch Processing
When possible, use batch APIs to process multiple operations in a single request. This reduces network overhead and improves throughput.

### Asynchronous Processing
Implement asynchronous processing for non-critical API operations. Use message queues and background workers to handle time-consuming operations without blocking user interactions.

## Conclusion and Next Steps

API integration is a complex but essential skill for modern developers. By following the practices and techniques outlined in this guide, you'll be well-equipped to build robust, scalable API integrations.

Continue learning by exploring specific API documentation, experimenting with different integration patterns, and staying up-to-date with evolving API standards and best practices.

Remember that good API integration is an iterative process. Start with simple implementations and gradually add complexity as your understanding and requirements grow.
"""
    
    try:
        print(f"📤 Uploading large document ({len(large_content)} characters)...")
        
        # Upload large content
        files = {
            'file': ('large_api_guide.txt', large_content, 'text/plain')
        }
        
        response = requests.post(f"{BACKEND_URL}/content/upload", files=files, timeout=180)
        print(f"Upload Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"✅ Upload successful, Job ID: {job_id}")
            
            # Wait longer for processing due to large content
            print("⏳ Waiting for processing to complete (large document)...")
            time.sleep(45)  # Give more time for large document processing
            
            # Check job status
            job_response = requests.get(f"{BACKEND_URL}/jobs/{job_id}", timeout=10)
            if job_response.status_code == 200:
                job_data = job_response.json()
                print(f"Job Status: {job_data.get('status')}")
                print(f"Chunks Created: {job_data.get('chunks_created', 0)}")
                
                # Get Content Library articles
                print("\n🔍 Checking Content Library for generated articles...")
                library_response = requests.get(f"{BACKEND_URL}/content-library?limit=50", timeout=30)
                
                if library_response.status_code == 200:
                    library_data = library_response.json()
                    all_articles = library_data.get('articles', [])
                    
                    # Find articles from our job (check recent articles since source_job_id might be missing)
                    recent_articles = all_articles[:10]  # Check last 10 articles
                    print(f"📚 Checking last 10 articles for our content...")
                    
                    # Look for articles that might be from our job based on content/timing
                    potential_job_articles = []
                    for article in recent_articles:
                        title = article.get('title', '')
                        content = article.get('content', '')
                        created_at = article.get('created_at', '')
                        
                        # Check if this might be from our upload based on content keywords
                        if any(keyword in title.lower() or keyword in content.lower() 
                               for keyword in ['api integration', 'authentication', 'webhook', 'rest api']):
                            potential_job_articles.append(article)
                    
                    print(f"📄 Found {len(potential_job_articles)} potential articles from our upload")
                    
                    if len(potential_job_articles) > 1:
                        print(f"✅ Multiple articles found - analyzing cross-references...")
                        
                        # Analyze each article for cross-references
                        articles_with_cross_refs = 0
                        cross_ref_details = []
                        
                        for i, article in enumerate(potential_job_articles):
                            title = article.get('title', f'Article {i+1}')[:60]
                            content = article.get('content', '')
                            article_id = article.get('id')
                            
                            print(f"\n📄 Article {i+1}: {title}")
                            print(f"  - ID: {article_id}")
                            print(f"  - Content length: {len(content)} chars")
                            
                            # Check for cross-reference indicators
                            has_related_links = 'related-links' in content
                            has_procedural_nav = 'Procedural Navigation' in content
                            has_related_articles = 'Related Articles' in content
                            has_cross_ref_links = 'href="/content-library/article/' in content
                            has_hr_separator = '<hr>' in content
                            
                            print(f"  - Has related-links div: {has_related_links}")
                            print(f"  - Has procedural navigation: {has_procedural_nav}")
                            print(f"  - Has related articles section: {has_related_articles}")
                            print(f"  - Has cross-reference links: {has_cross_ref_links}")
                            print(f"  - Has HR separator: {has_hr_separator}")
                            
                            cross_ref_found = any([has_related_links, has_procedural_nav, has_related_articles, has_cross_ref_links])
                            
                            if cross_ref_found:
                                articles_with_cross_refs += 1
                                
                                # Extract cross-reference section for analysis
                                cross_ref_section = ""
                                if has_related_links:
                                    start_idx = content.find('<div class="related-links">')
                                    if start_idx != -1:
                                        end_idx = content.find('</div>', start_idx)
                                        if end_idx != -1:
                                            cross_ref_section = content[start_idx:end_idx + 6]
                                
                                cross_ref_details.append({
                                    'title': title,
                                    'id': article_id,
                                    'has_links': cross_ref_found,
                                    'section_preview': cross_ref_section[:200] + '...' if cross_ref_section else 'No section found'
                                })
                        
                        # Final analysis
                        print(f"\n📊 CROSS-REFERENCE ANALYSIS RESULTS:")
                        print(f"  - Total potential articles: {len(potential_job_articles)}")
                        print(f"  - Articles WITH cross-references: {articles_with_cross_refs}")
                        print(f"  - Articles WITHOUT cross-references: {len(potential_job_articles) - articles_with_cross_refs}")
                        
                        if articles_with_cross_refs > 0:
                            success_rate = (articles_with_cross_refs / len(potential_job_articles)) * 100
                            print(f"  - Success rate: {success_rate:.1f}%")
                            
                            print(f"\n✅ CROSS-REFERENCE EXAMPLES FOUND:")
                            for detail in cross_ref_details:
                                if detail['has_links']:
                                    print(f"  - {detail['title']}")
                                    print(f"    Section: {detail['section_preview']}")
                            
                            if success_rate >= 50:
                                print(f"\n🎉 CROSS-REFERENCES ARE WORKING!")
                                print(f"   add_related_links_to_articles function is working and saving to database")
                                return {
                                    'issue_confirmed': False,
                                    'cross_references_working': True,
                                    'success_rate': success_rate,
                                    'articles_with_cross_refs': articles_with_cross_refs,
                                    'total_articles': len(potential_job_articles)
                                }
                            else:
                                print(f"\n⚠️ PARTIAL SUCCESS - Some cross-references found but not consistent")
                                return {
                                    'issue_confirmed': True,
                                    'cross_references_working': 'partial',
                                    'success_rate': success_rate,
                                    'articles_with_cross_refs': articles_with_cross_refs,
                                    'total_articles': len(potential_job_articles)
                                }
                        else:
                            print(f"\n❌ NO CROSS-REFERENCES FOUND")
                            print(f"   add_related_links_to_articles function is NOT working or NOT saving to database")
                            return {
                                'issue_confirmed': True,
                                'cross_references_working': False,
                                'success_rate': 0,
                                'articles_with_cross_refs': 0,
                                'total_articles': len(potential_job_articles)
                            }
                    else:
                        print(f"⚠️ Only {len(potential_job_articles)} potential article(s) found")
                        return {
                            'issue_confirmed': True,
                            'root_cause': 'insufficient_articles_generated',
                            'articles_found': len(potential_job_articles)
                        }
                else:
                    print(f"❌ Failed to get Content Library: {library_response.status_code}")
            else:
                print(f"❌ Failed to get job status: {job_response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            if response.text:
                print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return {'issue_confirmed': True, 'root_cause': 'test_execution_error', 'error': str(e)}

if __name__ == "__main__":
    result = test_large_document_cross_references()
    print(f"\n🎯 FINAL TEST RESULT:")
    print(json.dumps(result, indent=2))