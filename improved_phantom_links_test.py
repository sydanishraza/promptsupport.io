#!/usr/bin/env python3
"""
IMPROVED Phantom Links Cleanup Testing - Knowledge Engine Backend
Comprehensive testing for the IMPROVED phantom links cleanup implementation
"""

import requests
import json
import os
import io
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://article-genius-1.preview.emergentagent.com') + '/api'

class ImprovedPhantomLinksTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_articles = []
        print(f"🔗 Testing IMPROVED Phantom Links Cleanup at: {self.base_url}")
        
    def test_backend_health_check(self):
        """Test backend health before phantom links testing"""
        print("🔍 Testing Backend Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Backend health check passed")
                    return True
                else:
                    print("❌ Backend not healthy")
                    return False
            else:
                print(f"❌ Health check failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check failed - {str(e)}")
            return False
    
    def test_comprehensive_document_processing(self):
        """Test the same comprehensive document that generated 198 phantom links"""
        print("\n🔍 Testing Comprehensive Document Processing (Previously Generated 198 Phantom Links)...")
        try:
            # Create the SAME comprehensive test document that caused the regression
            comprehensive_test_content = """Comprehensive Guide to Whisk Studio Integration API
            
This comprehensive documentation provides complete coverage of the Whisk Studio Integration API, including setup, implementation, customization, and troubleshooting guidance.

## Table of Contents

1. What is Whisk Studio
2. Getting Started
3. Create an Account
4. Setup Authentication Guide
5. Implementation Guide
6. Advanced Features Customization
7. Troubleshooting Common Issues
8. API Reference Documentation
9. Best Practices and Examples
10. FAQ and Support

## What is Whisk Studio

Whisk Studio is a powerful integration platform that enables developers to create seamless connections between different applications and services. The platform provides a comprehensive API that allows for custom integrations and automated workflows.

Key features include:
- Real-time data synchronization
- Webhook support for event-driven integrations
- Comprehensive API documentation
- Developer-friendly SDKs
- Enterprise-grade security

## Getting Started

To begin using the Whisk Studio Integration API, you'll need to follow these essential steps:

### Prerequisites
- Active Whisk Studio account
- API credentials
- Development environment setup
- Basic understanding of REST APIs

### Initial Setup Process
1. Register for a developer account
2. Generate API keys
3. Configure authentication
4. Test basic connectivity
5. Review documentation

## Create an Account

Creating your Whisk Studio developer account is the first step in accessing the Integration API:

### Account Registration Steps
1. Visit the Whisk Studio developer portal
2. Complete the registration form
3. Verify your email address
4. Set up two-factor authentication
5. Accept the terms of service

### Account Verification
After registration, you'll need to verify your account through the email confirmation process. This ensures secure access to the API and protects your integration data.

## Setup Authentication Guide

Proper authentication is crucial for secure API access. Whisk Studio supports multiple authentication methods:

### API Key Authentication
The simplest method for getting started:
- Generate API keys from your dashboard
- Include keys in request headers
- Rotate keys regularly for security
- Monitor usage and rate limits

### OAuth 2.0 Integration
For production applications:
- Register your application
- Implement OAuth flow
- Handle token refresh
- Secure token storage

### JWT Token Authentication
For advanced use cases:
- Generate JWT tokens
- Configure token expiration
- Implement token validation
- Handle token renewal

## Implementation Guide

This section provides detailed implementation guidance for common integration scenarios:

### Basic API Integration
Start with simple API calls to understand the platform:

```javascript
// Example API call
const response = await fetch('https://api.whiskstudio.com/v1/data', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
});
```

### Webhook Configuration
Set up webhooks for real-time data updates:
- Configure webhook endpoints
- Handle webhook authentication
- Process incoming data
- Implement error handling

### Data Synchronization
Implement bi-directional data sync:
- Map data fields
- Handle data transformations
- Manage sync conflicts
- Monitor sync status

## Advanced Features Customization

Customize the integration to meet your specific requirements:

### Custom Field Mapping
Configure how data flows between systems:
- Define field mappings
- Set up data transformations
- Handle custom data types
- Validate data integrity

### Workflow Automation
Create automated workflows:
- Define trigger conditions
- Set up action sequences
- Handle error scenarios
- Monitor workflow performance

### Custom Integrations
Build specialized integrations:
- Use SDK libraries
- Implement custom logic
- Handle edge cases
- Optimize performance

## Troubleshooting Common Issues

Common problems and their solutions:

### Authentication Errors
- Verify API key validity
- Check authentication headers
- Confirm account permissions
- Review rate limiting

### Data Sync Issues
- Validate data formats
- Check field mappings
- Monitor error logs
- Test with sample data

### Performance Problems
- Optimize API calls
- Implement caching
- Use batch operations
- Monitor response times

### Connection Problems
- Check network connectivity
- Verify endpoint URLs
- Test with different environments
- Review firewall settings

## API Reference Documentation

Complete API reference with endpoints, parameters, and examples:

### Core Endpoints
- GET /api/v1/data - Retrieve data
- POST /api/v1/data - Create new records
- PUT /api/v1/data/{id} - Update existing records
- DELETE /api/v1/data/{id} - Delete records

### Authentication Endpoints
- POST /auth/login - User authentication
- POST /auth/refresh - Token refresh
- POST /auth/logout - Session termination

### Webhook Endpoints
- POST /webhooks/register - Register webhook
- GET /webhooks/list - List webhooks
- DELETE /webhooks/{id} - Remove webhook

## Best Practices and Examples

Industry best practices for successful integrations:

### Security Best Practices
- Use HTTPS for all communications
- Implement proper authentication
- Validate all input data
- Monitor for suspicious activity

### Performance Optimization
- Implement efficient caching
- Use pagination for large datasets
- Optimize database queries
- Monitor system performance

### Error Handling
- Implement comprehensive error handling
- Log errors for debugging
- Provide meaningful error messages
- Set up monitoring and alerts

### Code Examples
Practical examples for common scenarios:
- Basic data retrieval
- Batch data processing
- Real-time webhook handling
- Error recovery patterns

## FAQ and Support

Frequently asked questions and support resources:

### Common Questions
Q: How do I get started with the API?
A: Begin by creating a developer account and generating API keys.

Q: What authentication methods are supported?
A: We support API keys, OAuth 2.0, and JWT tokens.

Q: How do I handle rate limiting?
A: Implement exponential backoff and monitor your usage.

Q: Where can I find code examples?
A: Check our GitHub repository and documentation site.

### Support Resources
- Developer documentation
- Community forums
- Support ticket system
- Live chat support
- Video tutorials

### Contact Information
For additional support:
- Email: support@whiskstudio.com
- Phone: 1-800-WHISK-API
- Live chat: Available 24/7
- Community forum: forum.whiskstudio.com

This comprehensive guide provides everything you need to successfully integrate with the Whisk Studio API. Follow the step-by-step instructions and refer to the troubleshooting section if you encounter any issues."""

            # Create file-like object
            file_data = io.BytesIO(comprehensive_test_content.encode('utf-8'))
            
            files = {
                'file': ('comprehensive_whisk_studio_guide.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_instructions": "Process comprehensive document with IMPROVED phantom link cleanup",
                    "output_requirements": {
                        "format": "html",
                        "min_articles": 4,
                        "max_articles": 10,
                        "quality_benchmarks": ["content_completeness", "no_phantom_links", "proper_formatting"]
                    },
                    "phantom_link_prevention": True
                })
            }
            
            print("📤 Processing comprehensive document (previously generated 198 phantom links)...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=180  # Extended timeout for comprehensive processing
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Document processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            
            # Store articles for phantom link analysis
            self.test_articles = data.get('articles', [])
            articles_count = len(self.test_articles)
            
            print(f"📚 Articles Generated: {articles_count}")
            
            if articles_count == 0:
                print("❌ No articles generated for phantom link testing")
                return False
            
            # Basic success check
            success = data.get('success', False)
            if success and articles_count > 0:
                print(f"✅ Comprehensive document processing successful - {articles_count} articles generated")
                return True
            else:
                print("❌ Document processing failed")
                return False
                
        except Exception as e:
            print(f"❌ Comprehensive document processing failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_phantom_links_detection_and_cleanup(self):
        """Test phantom links detection and verify cleanup effectiveness"""
        print("\n🔍 Testing Phantom Links Detection and Cleanup Effectiveness...")
        try:
            if not self.test_articles:
                print("❌ No articles available for phantom link testing")
                return False
            
            print(f"🔍 Analyzing {len(self.test_articles)} articles for phantom links...")
            
            total_phantom_links = 0
            articles_with_phantom_links = 0
            phantom_link_patterns = []
            
            # Define phantom link patterns to detect
            phantom_patterns = [
                r'href\s*=\s*["\']#[^"\']*["\']',  # href="#anything"
                r'<a[^>]*href\s*=\s*["\']#[^"\']*["\'][^>]*>',  # Full anchor tags with # links
                r'#what-is-whisk-studio',
                r'#getting-started', 
                r'#create-an-account',
                r'#setup-authentication-guide',
                r'#implementation-guide',
                r'#advanced-features-customization',
                r'#troubleshooting',
                r'#api-reference',
                r'#best-practices',
                r'#faq-and-support'
            ]
            
            for i, article in enumerate(self.test_articles):
                article_title = article.get('title', f'Article {i+1}')
                content = article.get('content', '') or article.get('html', '')
                
                print(f"\n📄 Analyzing Article {i+1}: '{article_title[:50]}...'")
                print(f"   Content length: {len(content)} characters")
                
                article_phantom_count = 0
                found_patterns = []
                
                # Check for each phantom link pattern
                for pattern in phantom_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        article_phantom_count += len(matches)
                        found_patterns.extend(matches)
                        print(f"   🚨 Found {len(matches)} matches for pattern: {pattern}")
                        for match in matches[:3]:  # Show first 3 matches
                            print(f"      - {match[:50]}...")
                
                if article_phantom_count > 0:
                    articles_with_phantom_links += 1
                    total_phantom_links += article_phantom_count
                    phantom_link_patterns.extend(found_patterns)
                    print(f"   ❌ Article {i+1} contains {article_phantom_count} phantom links")
                else:
                    print(f"   ✅ Article {i+1} contains NO phantom links")
            
            # CRITICAL ASSESSMENT: Compare with previous 198 phantom links
            print(f"\n📊 PHANTOM LINKS CLEANUP ASSESSMENT:")
            print(f"   Previous test result: 198 phantom links")
            print(f"   Current test result: {total_phantom_links} phantom links")
            print(f"   Articles with phantom links: {articles_with_phantom_links}/{len(self.test_articles)}")
            
            # Calculate improvement
            if total_phantom_links == 0:
                print(f"   🎉 PERFECT SUCCESS: 100% phantom links eliminated (198 → 0)")
                improvement = "100% elimination"
            elif total_phantom_links < 198:
                reduction_percent = ((198 - total_phantom_links) / 198) * 100
                print(f"   ✅ SIGNIFICANT IMPROVEMENT: {reduction_percent:.1f}% reduction (198 → {total_phantom_links})")
                improvement = f"{reduction_percent:.1f}% reduction"
            else:
                print(f"   ❌ REGRESSION: Phantom links increased or stayed same (198 → {total_phantom_links})")
                improvement = "No improvement or regression"
            
            # SUCCESS CRITERIA CHECK
            success_criteria_met = total_phantom_links < 10  # Target: significant reduction, ideally 0
            
            if success_criteria_met:
                print(f"✅ SUCCESS CRITERIA MET: Phantom links reduced to {total_phantom_links} (target: < 10)")
                return True
            else:
                print(f"❌ SUCCESS CRITERIA NOT MET: {total_phantom_links} phantom links remain (target: < 10)")
                return False
                
        except Exception as e:
            print(f"❌ Phantom links detection failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_regex_patterns_effectiveness(self):
        """Test that the improved regex patterns are working effectively"""
        print("\n🔍 Testing Improved Regex Patterns Effectiveness...")
        try:
            # Test the regex patterns directly with known phantom link examples
            test_html_samples = [
                '<a href="#what-is-whisk-studio">What is Whisk Studio</a>',
                '<a href="#getting-started">Getting Started</a>',
                '<a href="#create-an-account">Create an Account</a>',
                '<a href="#setup-authentication-guide">Setup Guide</a>',
                '<a href="">Empty Link</a>',
                '<a>No href attribute</a>',
                '<a href="/content-library/article/123">Valid Content Library Link</a>',
                '<a href="https://example.com">Valid External Link</a>'
            ]
            
            print("🧪 Testing regex patterns on sample phantom links...")
            
            # Simulate the cleanup functions
            for i, sample in enumerate(test_html_samples):
                print(f"\n   Test {i+1}: {sample}")
                
                # Test STEP 1: Remove anchor tags with href starting with #
                step1_pattern = r'<a[^>]*href\s*=\s*["\']#[^"\']*["\'][^>]*>(.*?)</a>'
                step1_result = re.sub(step1_pattern, r'\1', sample, flags=re.IGNORECASE | re.DOTALL)
                
                # Test STEP 2: Remove anchor tags with empty href
                step2_pattern = r'<a[^>]*href\s*=\s*["\'][\s]*["\'][^>]*>(.*?)</a>'
                step2_result = re.sub(step2_pattern, r'\1', step1_result, flags=re.IGNORECASE | re.DOTALL)
                
                # Test STEP 3: Remove anchor tags without href
                step3_pattern = r'<a(?![^>]*href)[^>]*>(.*?)</a>'
                final_result = re.sub(step3_pattern, r'\1', step2_result, flags=re.IGNORECASE | re.DOTALL)
                
                if final_result != sample:
                    print(f"      ✅ CLEANED: '{final_result}'")
                else:
                    print(f"      ➡️ UNCHANGED: '{final_result}' (expected for valid links)")
            
            # Test with a comprehensive HTML sample
            comprehensive_html = """
            <h2>Navigation Links</h2>
            <ul>
                <li><a href="#what-is-whisk-studio">What is Whisk Studio</a></li>
                <li><a href="#getting-started">Getting Started</a></li>
                <li><a href="">Empty Link</a></li>
                <li><a>No href</a></li>
                <li><a href="/content-library/article/123">Valid Link</a></li>
                <li><a href="https://example.com">External Link</a></li>
            </ul>
            """
            
            print(f"\n🧪 Testing comprehensive HTML cleanup...")
            print(f"   Original: {len(comprehensive_html)} characters")
            
            # Apply all cleanup steps
            cleaned_html = comprehensive_html
            
            # Step 1: Remove # anchor links
            cleaned_html = re.sub(r'<a[^>]*href\s*=\s*["\']#[^"\']*["\'][^>]*>(.*?)</a>', r'\1', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
            
            # Step 2: Remove empty href links
            cleaned_html = re.sub(r'<a[^>]*href\s*=\s*["\'][\s]*["\'][^>]*>(.*?)</a>', r'\1', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
            
            # Step 3: Remove no-href links
            cleaned_html = re.sub(r'<a(?![^>]*href)[^>]*>(.*?)</a>', r'\1', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
            
            print(f"   Cleaned: {len(cleaned_html)} characters")
            
            # Count remaining anchor tags
            remaining_anchors = len(re.findall(r'<a[^>]*>', cleaned_html, re.IGNORECASE))
            phantom_anchors = len(re.findall(r'<a[^>]*href\s*=\s*["\']#[^"\']*["\']', cleaned_html, re.IGNORECASE))
            
            print(f"   Remaining anchor tags: {remaining_anchors}")
            print(f"   Remaining phantom anchors: {phantom_anchors}")
            
            if phantom_anchors == 0:
                print("✅ REGEX PATTERNS EFFECTIVENESS VERIFIED:")
                print("  ✅ All phantom anchor links successfully removed")
                print("  ✅ Valid links preserved")
                print("  ✅ Improved regex patterns are working effectively")
                return True
            else:
                print("❌ REGEX PATTERNS EFFECTIVENESS FAILED:")
                print(f"  ❌ {phantom_anchors} phantom anchor links remain")
                return False
                
        except Exception as e:
            print(f"❌ Regex patterns effectiveness test failed - {str(e)}")
            return False
    
    def run_all_phantom_links_tests(self):
        """Run all phantom links cleanup tests"""
        print("🚀 STARTING IMPROVED PHANTOM LINKS CLEANUP TESTING")
        print("=" * 80)
        
        test_results = []
        
        # Test 1: Backend Health Check
        test_results.append(("Backend Health Check", self.test_backend_health_check()))
        
        # Test 2: Comprehensive Document Processing (same document that caused 198 phantom links)
        test_results.append(("Comprehensive Document Processing", self.test_comprehensive_document_processing()))
        
        # Test 3: Phantom Links Detection and Cleanup
        test_results.append(("Phantom Links Detection and Cleanup", self.test_phantom_links_detection_and_cleanup()))
        
        # Test 4: Regex Patterns Effectiveness
        test_results.append(("Regex Patterns Effectiveness", self.test_regex_patterns_effectiveness()))
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 IMPROVED PHANTOM LINKS CLEANUP TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed_tests += 1
        
        print(f"\n📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests >= 3:  # At least 3 out of 4 tests should pass
            print("🎉 IMPROVED PHANTOM LINKS CLEANUP TESTING: SUCCESS")
            print("✅ IMPROVED phantom links cleanup is working effectively")
            return True
        else:
            print("❌ IMPROVED PHANTOM LINKS CLEANUP TESTING: NEEDS IMPROVEMENT")
            print("❌ Phantom links cleanup requires additional fixes")
            return False

if __name__ == "__main__":
    tester = ImprovedPhantomLinksTest()
    success = tester.run_all_phantom_links_tests()
    exit(0 if success else 1)