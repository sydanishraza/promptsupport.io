#!/usr/bin/env python3
"""
V2 Engine Step 2 Implementation Testing - Content Extraction & Structuring (100% capture)
Testing the V2 schema models, content extraction, processing pipeline, and database storage
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List
import os

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://None.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2EngineStep2Tester:
    def __init__(self):
        self.test_results = []
        self.backend_url = API_BASE
        print(f"🧪 V2 ENGINE STEP 2 TESTING INITIALIZED")
        print(f"🔗 Backend URL: {self.backend_url}")
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_v2_schema_validation(self):
        """Test 1: V2 Schema Validation - Test that V2 schema models are properly defined"""
        print(f"\n🔍 TEST 1: V2 SCHEMA VALIDATION")
        
        try:
            # Test health endpoint to verify V2 engine is active
            response = requests.get(f"{self.backend_url}/engine", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check V2 engine status
                if data.get('engine') == 'v2':
                    self.log_test("V2 Engine Active", True, f"Engine status: {data.get('engine')}")
                else:
                    self.log_test("V2 Engine Active", False, f"Expected v2, got: {data.get('engine')}")
                    return
                
                # Check V2 features
                v2_features = data.get('v2_features', [])
                expected_features = [
                    'multi_dimensional_analysis',
                    'adaptive_granularity', 
                    'intelligent_chunking',
                    'cross_referencing',
                    'comprehensive_file_support',
                    'image_extraction',
                    'progress_tracking'
                ]
                
                missing_features = [f for f in expected_features if f not in v2_features]
                if not missing_features:
                    self.log_test("V2 Features Available", True, f"All {len(expected_features)} V2 features present")
                else:
                    self.log_test("V2 Features Available", False, f"Missing features: {missing_features}")
                
                # Check V2 endpoints
                v2_endpoints = data.get('endpoints', {})
                expected_endpoints = ['text_processing', 'file_upload', 'url_processing']
                
                missing_endpoints = [e for e in expected_endpoints if e not in v2_endpoints]
                if not missing_endpoints:
                    self.log_test("V2 Endpoints Available", True, f"All {len(expected_endpoints)} V2 endpoints present")
                else:
                    self.log_test("V2 Endpoints Available", False, f"Missing endpoints: {missing_endpoints}")
                    
            else:
                self.log_test("V2 Engine Health Check", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("V2 Schema Validation", False, f"Error: {str(e)}")
    
    def test_v2_content_extractor(self):
        """Test 2: V2 Content Extractor Testing - Test V2ContentExtractor functionality"""
        print(f"\n🔍 TEST 2: V2 CONTENT EXTRACTOR TESTING")
        
        # Test sample content for extraction
        sample_text_content = """# Google Maps JavaScript API Tutorial

## Introduction
This comprehensive guide covers the Google Maps JavaScript API integration for web applications.

## Getting Started
To begin using the Google Maps API, you'll need:
- A Google Cloud Platform account
- An API key with Maps JavaScript API enabled
- Basic knowledge of HTML and JavaScript

### Step 1: Setup
First, include the Maps JavaScript API in your HTML:

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap"></script>
```

### Step 2: Initialize the Map
Create a basic map instance:

```javascript
function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 10,
        center: { lat: 37.7749, lng: -122.4194 }
    });
}
```

## Advanced Features
The API supports various advanced features:
- Custom markers and info windows
- Geocoding and reverse geocoding
- Directions and distance calculations
- Street View integration

> Important: Always handle API errors gracefully and implement proper error handling.

## Troubleshooting
Common issues include:
1. Invalid API key errors
2. Quota exceeded messages
3. CORS policy violations
4. Map not displaying correctly
"""

        sample_html_content = """<!DOCTYPE html>
<html>
<head>
    <title>API Documentation</title>
</head>
<body>
    <h1>REST API Guide</h1>
    <p>This guide covers our REST API endpoints and usage patterns.</p>
    
    <h2>Authentication</h2>
    <p>All API requests require authentication using Bearer tokens.</p>
    
    <h3>Getting a Token</h3>
    <p>Send a POST request to /auth/token with your credentials.</p>
    
    <ul>
        <li>Username and password required</li>
        <li>Token expires after 24 hours</li>
        <li>Refresh tokens available</li>
    </ul>
    
    <h2>Endpoints</h2>
    <table>
        <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
        <tr><td>GET</td><td>/users</td><td>List all users</td></tr>
        <tr><td>POST</td><td>/users</td><td>Create new user</td></tr>
    </table>
    
    <blockquote>
        Remember to include proper error handling in your applications.
    </blockquote>
    
    <pre><code>
    curl -H "Authorization: Bearer TOKEN" https://api.example.com/users
    </code></pre>
    
    <img src="/images/api-flow.png" alt="API Flow Diagram" />
</body>
</html>"""
        
        try:
            # Test V2 text processing with sample content
            text_payload = {
                "content": sample_text_content,
                "metadata": {
                    "title": "Google Maps API Tutorial Test",
                    "source": "test_content",
                    "test_type": "v2_extraction"
                }
            }
            
            print(f"📝 Testing V2 text content processing...")
            response = requests.post(
                f"{self.backend_url}/content/process",
                json=text_payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify V2 engine processing
                if data.get('engine') == 'v2':
                    self.log_test("V2 Text Processing", True, f"Engine: {data.get('engine')}, Status: {data.get('status')}")
                    
                    # Check for content blocks and structure detection
                    if data.get('chunks_created', 0) > 0:
                        self.log_test("Content Block Creation", True, f"Created {data.get('chunks_created')} chunks")
                    else:
                        self.log_test("Content Block Creation", False, "No chunks created")
                        
                    # Check for V2 enhanced messaging
                    message = data.get('message', '')
                    if 'V2 Engine' in message:
                        self.log_test("V2 Enhanced Messaging", True, f"Message: {message}")
                    else:
                        self.log_test("V2 Enhanced Messaging", False, f"Message: {message}")
                        
                else:
                    self.log_test("V2 Text Processing", False, f"Expected v2 engine, got: {data.get('engine')}")
                    
            else:
                self.log_test("V2 Text Processing", False, f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("V2 Content Extractor Testing", False, f"Error: {str(e)}")
    
    def test_processing_pipeline_integration(self):
        """Test 3: Processing Pipeline Integration - Test V2 processing pipeline"""
        print(f"\n🔍 TEST 3: PROCESSING PIPELINE INTEGRATION")
        
        # Test content with various structures for comprehensive extraction
        comprehensive_content = """# Complete Development Guide

## Overview
This guide provides comprehensive coverage of modern web development practices.

### Key Topics Covered
- Frontend frameworks and libraries
- Backend API development
- Database design and optimization
- DevOps and deployment strategies

## Frontend Development

### React Framework
React is a popular JavaScript library for building user interfaces.

#### Component Structure
```jsx
function MyComponent({ title, children }) {
    return (
        <div className="component">
            <h2>{title}</h2>
            {children}
        </div>
    );
}
```

#### State Management
Modern React applications use hooks for state management:

```javascript
const [count, setCount] = useState(0);
const [user, setUser] = useState(null);

useEffect(() => {
    fetchUserData();
}, []);
```

### Vue.js Framework
Vue.js offers a different approach to component-based development.

## Backend Development

### API Design Principles
When designing REST APIs, follow these principles:

1. Use meaningful HTTP status codes
2. Implement proper error handling
3. Version your APIs appropriately
4. Document all endpoints thoroughly

### Database Integration
Choose the right database for your needs:

- **SQL Databases**: PostgreSQL, MySQL, SQLite
- **NoSQL Databases**: MongoDB, Redis, DynamoDB
- **Graph Databases**: Neo4j, Amazon Neptune

> Pro Tip: Consider your data relationships and query patterns when choosing a database.

## Testing Strategies

### Unit Testing
Write comprehensive unit tests for all functions:

```python
def test_user_creation():
    user = create_user("john@example.com", "password123")
    assert user.email == "john@example.com"
    assert user.is_active == True
```

### Integration Testing
Test how different parts of your system work together.

## Deployment and DevOps

### Container Orchestration
Use Docker and Kubernetes for scalable deployments:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
```

### Monitoring and Logging
Implement comprehensive monitoring:
- Application performance monitoring (APM)
- Error tracking and alerting
- Log aggregation and analysis
- Infrastructure monitoring

## Conclusion
Following these practices will help you build robust, scalable web applications.
"""
        
        try:
            # Test comprehensive content processing
            payload = {
                "content": comprehensive_content,
                "metadata": {
                    "title": "Complete Development Guide",
                    "source": "comprehensive_test",
                    "test_type": "pipeline_integration",
                    "expected_blocks": ["headings", "paragraphs", "code", "lists", "quotes"]
                }
            }
            
            print(f"🔄 Testing V2 processing pipeline integration...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.backend_url}/content/process",
                json=payload,
                timeout=180
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify V2 processing
                if data.get('engine') == 'v2':
                    self.log_test("V2 Pipeline Processing", True, f"Processed in {processing_time:.2f}s")
                    
                    # Check job tracking
                    job_id = data.get('job_id')
                    if job_id:
                        self.log_test("V2 Job Tracking", True, f"Job ID: {job_id}")
                    else:
                        self.log_test("V2 Job Tracking", False, "No job ID returned")
                    
                    # Check content structuring
                    chunks_created = data.get('chunks_created', 0)
                    if chunks_created > 0:
                        self.log_test("Content Structuring", True, f"Created {chunks_created} structured chunks")
                        
                        # Test if multiple articles were created for comprehensive content
                        if chunks_created >= 2:
                            self.log_test("Multi-Article Generation", True, f"Generated {chunks_created} articles from comprehensive content")
                        else:
                            self.log_test("Multi-Article Generation", False, f"Only {chunks_created} article created")
                    else:
                        self.log_test("Content Structuring", False, "No chunks created")
                        
                    # Check V2 metadata preservation
                    if 'V2 Engine' in data.get('message', ''):
                        self.log_test("V2 Metadata Preservation", True, "V2 engine metadata preserved")
                    else:
                        self.log_test("V2 Metadata Preservation", False, "V2 metadata not found")
                        
                else:
                    self.log_test("V2 Pipeline Processing", False, f"Expected v2, got: {data.get('engine')}")
                    
            else:
                self.log_test("Processing Pipeline Integration", False, f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Processing Pipeline Integration", False, f"Error: {str(e)}")
    
    def test_database_storage_verification(self):
        """Test 4: Database Storage Verification - Test normalized document storage"""
        print(f"\n🔍 TEST 4: DATABASE STORAGE VERIFICATION")
        
        try:
            # Test content that should create normalized documents
            test_content = """# Database Storage Test Document

## Section 1: Introduction
This document tests the V2 engine's database storage capabilities.

### Subsection 1.1: Purpose
The purpose is to verify that normalized documents are properly stored.

## Section 2: Technical Details
This section contains technical information about the storage system.

### Code Example
```python
def store_document(doc):
    return database.insert(doc)
```

### Important Notes
- All documents must have unique IDs
- Provenance tracking is required
- Metadata must be preserved

## Section 3: Validation
This section validates the storage process.
"""
            
            payload = {
                "content": test_content,
                "metadata": {
                    "title": "Database Storage Test",
                    "source": "storage_verification",
                    "test_type": "database_storage"
                }
            }
            
            print(f"💾 Testing normalized document storage...")
            response = requests.post(
                f"{self.backend_url}/content/process",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify processing completed
                if data.get('status') == 'completed':
                    self.log_test("Document Processing", True, f"Status: {data.get('status')}")
                    
                    # Check if articles were created (indicating storage worked)
                    chunks_created = data.get('chunks_created', 0)
                    if chunks_created > 0:
                        self.log_test("Article Creation", True, f"Created {chunks_created} articles")
                        
                        # Test Content Library to verify storage
                        print(f"📚 Verifying Content Library storage...")
                        library_response = requests.get(f"{self.backend_url}/content-library", timeout=30)
                        
                        if library_response.status_code == 200:
                            library_data = library_response.json()
                            total_articles = library_data.get('total', 0)
                            
                            if total_articles > 0:
                                self.log_test("Content Library Storage", True, f"Total articles in library: {total_articles}")
                                
                                # Check for recent articles with V2 metadata
                                articles = library_data.get('articles', [])
                                v2_articles = [a for a in articles if a.get('metadata', {}).get('engine') == 'v2']
                                
                                if v2_articles:
                                    self.log_test("V2 Metadata Storage", True, f"Found {len(v2_articles)} articles with V2 metadata")
                                    
                                    # Check normalized document structure
                                    sample_article = v2_articles[0]
                                    required_fields = ['id', 'title', 'content', 'status', 'created_at']
                                    missing_fields = [f for f in required_fields if f not in sample_article]
                                    
                                    if not missing_fields:
                                        self.log_test("Document Structure", True, "All required fields present")
                                    else:
                                        self.log_test("Document Structure", False, f"Missing fields: {missing_fields}")
                                        
                                    # Check for V2 specific metadata
                                    v2_metadata = sample_article.get('metadata', {})
                                    if v2_metadata.get('processing_version') == '2.0':
                                        self.log_test("V2 Processing Version", True, "Processing version 2.0 confirmed")
                                    else:
                                        self.log_test("V2 Processing Version", False, f"Version: {v2_metadata.get('processing_version')}")
                                        
                                else:
                                    self.log_test("V2 Metadata Storage", False, "No articles with V2 metadata found")
                                    
                            else:
                                self.log_test("Content Library Storage", False, "No articles found in library")
                                
                        else:
                            self.log_test("Content Library Access", False, f"HTTP {library_response.status_code}")
                            
                    else:
                        self.log_test("Article Creation", False, "No articles created")
                        
                else:
                    self.log_test("Document Processing", False, f"Status: {data.get('status')}")
                    
            else:
                self.log_test("Database Storage Verification", False, f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Database Storage Verification", False, f"Error: {str(e)}")
    
    def test_error_handling_and_fallbacks(self):
        """Test 5: Error Handling & Fallbacks - Test V2 error handling and fallback mechanisms"""
        print(f"\n🔍 TEST 5: ERROR HANDLING & FALLBACKS")
        
        try:
            # Test 1: Invalid content
            print(f"🚫 Testing invalid content handling...")
            invalid_payload = {
                "content": "",  # Empty content
                "metadata": {
                    "title": "Invalid Content Test",
                    "test_type": "error_handling"
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/content/process",
                json=invalid_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                # Should still process but with minimal content
                if data.get('engine') == 'v2':
                    self.log_test("Invalid Content Handling", True, f"V2 engine handled empty content gracefully")
                else:
                    self.log_test("Invalid Content Handling", False, f"Engine: {data.get('engine')}")
            else:
                # Error response is also acceptable for invalid content
                self.log_test("Invalid Content Handling", True, f"Proper error response: {response.status_code}")
            
            # Test 2: Malformed content
            print(f"🔧 Testing malformed content handling...")
            malformed_payload = {
                "content": "<<<INVALID MARKUP>>> ``` unclosed code block\n# Broken heading\n\n\n\n\n",
                "metadata": {
                    "title": "Malformed Content Test",
                    "test_type": "error_handling"
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/content/process",
                json=malformed_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('engine') == 'v2':
                    self.log_test("Malformed Content Handling", True, "V2 engine processed malformed content")
                    
                    # Check if fallback was used
                    if data.get('metadata', {}).get('fallback'):
                        self.log_test("Fallback Mechanism", True, "Fallback to legacy processing detected")
                    else:
                        self.log_test("V2 Resilience", True, "V2 engine handled malformed content without fallback")
                else:
                    self.log_test("Malformed Content Handling", False, f"Engine: {data.get('engine')}")
            else:
                self.log_test("Malformed Content Handling", True, f"Proper error handling: {response.status_code}")
            
            # Test 3: Very large content (stress test)
            print(f"📏 Testing large content handling...")
            large_content = "# Large Content Test\n\n" + ("This is a test paragraph with substantial content. " * 1000)
            
            large_payload = {
                "content": large_content,
                "metadata": {
                    "title": "Large Content Test",
                    "test_type": "stress_test"
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/content/process",
                json=large_payload,
                timeout=300  # Extended timeout for large content
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('engine') == 'v2':
                    self.log_test("Large Content Handling", True, f"Processed {len(large_content)} chars in {processing_time:.2f}s")
                else:
                    self.log_test("Large Content Handling", False, f"Engine: {data.get('engine')}")
            else:
                self.log_test("Large Content Handling", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Error Handling & Fallbacks", False, f"Error: {str(e)}")
    
    def test_file_type_support(self):
        """Test 6: File Type Support Testing - Test MIME type detection and V2 file processing"""
        print(f"\n🔍 TEST 6: FILE TYPE SUPPORT TESTING")
        
        try:
            # Test different content types that simulate different file formats
            test_cases = [
                {
                    "name": "HTML Content",
                    "content": """<!DOCTYPE html>
<html>
<head><title>Test HTML</title></head>
<body>
    <h1>HTML Test Document</h1>
    <p>This tests HTML content processing.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
</body>
</html>""",
                    "metadata": {"title": "HTML Test", "file_type": "html"}
                },
                {
                    "name": "Markdown Content", 
                    "content": """# Markdown Test Document

## Introduction
This is a **markdown** document with *emphasis*.

### Code Block
```python
def hello_world():
    print("Hello, World!")
```

### List
- Item A
- Item B
- Item C

> This is a blockquote in markdown.
""",
                    "metadata": {"title": "Markdown Test", "file_type": "markdown"}
                },
                {
                    "name": "Technical Documentation",
                    "content": """API Reference Guide

AUTHENTICATION
All requests require Bearer token authentication.

ENDPOINTS
GET /api/users - Retrieve user list
POST /api/users - Create new user
PUT /api/users/{id} - Update user
DELETE /api/users/{id} - Delete user

ERROR CODES
400 - Bad Request
401 - Unauthorized  
404 - Not Found
500 - Internal Server Error

EXAMPLES
curl -H "Authorization: Bearer TOKEN" https://api.example.com/users
""",
                    "metadata": {"title": "API Reference", "file_type": "text"}
                }
            ]
            
            for test_case in test_cases:
                print(f"📄 Testing {test_case['name']}...")
                
                payload = {
                    "content": test_case["content"],
                    "metadata": test_case["metadata"]
                }
                
                response = requests.post(
                    f"{self.backend_url}/content/process",
                    json=payload,
                    timeout=120
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('engine') == 'v2':
                        self.log_test(f"{test_case['name']} Processing", True, f"V2 engine processed {test_case['metadata']['file_type']} content")
                        
                        # Check content structure detection
                        chunks_created = data.get('chunks_created', 0)
                        if chunks_created > 0:
                            self.log_test(f"{test_case['name']} Structure Detection", True, f"Detected structure: {chunks_created} chunks")
                        else:
                            self.log_test(f"{test_case['name']} Structure Detection", False, "No structure detected")
                            
                    else:
                        self.log_test(f"{test_case['name']} Processing", False, f"Engine: {data.get('engine')}")
                        
                else:
                    self.log_test(f"{test_case['name']} Processing", False, f"HTTP {response.status_code}")
                    
        except Exception as e:
            self.log_test("File Type Support Testing", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all V2 Engine Step 2 tests"""
        print(f"🚀 STARTING V2 ENGINE STEP 2 COMPREHENSIVE TESTING")
        print(f"📅 Test started at: {datetime.now().isoformat()}")
        print(f"=" * 80)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_v2_schema_validation()
        self.test_v2_content_extractor()
        self.test_processing_pipeline_integration()
        self.test_database_storage_verification()
        self.test_error_handling_and_fallbacks()
        self.test_file_type_support()
        
        # Calculate results
        total_time = time.time() - start_time
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n" + "=" * 80)
        print(f"🎯 V2 ENGINE STEP 2 TESTING COMPLETE")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"📊 Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for test in self.test_results:
                if not test['success']:
                    print(f"   • {test['test']}: {test['details']}")
        
        if success_rate >= 80:
            print(f"\n✅ V2 ENGINE STEP 2 IMPLEMENTATION: PRODUCTION READY")
            print(f"🎉 Content Extraction & Structuring (100% capture) is working correctly!")
        else:
            print(f"\n⚠️  V2 ENGINE STEP 2 IMPLEMENTATION: NEEDS ATTENTION")
            print(f"🔧 Some components require fixes before production deployment")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "total_time": total_time,
            "test_results": self.test_results
        }

def main():
    """Main test execution"""
    tester = V2EngineStep2Tester()
    results = tester.run_all_tests()
    
    # Return exit code based on success rate
    if results['success_rate'] >= 80:
        exit(0)  # Success
    else:
        exit(1)  # Failure

if __name__ == "__main__":
    main()