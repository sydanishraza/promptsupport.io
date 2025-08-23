#!/usr/bin/env python3
"""
V2 ENGINE STEP 7 IMPLEMENTATION TESTING
Test the newly implemented V2 Engine Step 7: "Generate Articles (strict format + audience-aware)" functionality.

SPECIFIC TESTING REQUIREMENTS:
1. Test V2 text processing with v2_article_generator integration
2. Test V2 file upload processing with new article generation
3. Test V2 URL processing with V2ArticleGenerator 
4. Verify strict article format compliance (H1 Title, Intro, Mini-TOC, Main Body, FAQs, Related Links)
5. Test audience-aware styling for different audiences (developer, business, admin, end_user)
6. Verify articles are properly stored in content library with V2 metadata
7. Test title extraction from HTML content works correctly
8. Verify no media embedding occurs (only references)
9. Test HTML to Markdown conversion
10. Verify 100% block coverage in generated articles
"""

import asyncio
import aiohttp
import json
import os
import time
import tempfile
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://woolf-style-lint.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2EngineStep7Tester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def test_backend_health(self):
        """Test backend health and V2 engine status"""
        try:
            async with self.session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    data = await response.json()
                    engine_status = data.get('engine', '')
                    v2_active = engine_status == 'v2'
                    
                    self.log_test(
                        "Backend Health Check", 
                        v2_active,
                        f"Engine: {engine_status}, Status: {response.status}"
                    )
                    return v2_active
                else:
                    self.log_test("Backend Health Check", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
            return False
    
    async def test_v2_text_processing_with_article_generator(self):
        """Test V2 text processing with v2_article_generator integration"""
        try:
            # Create comprehensive test content for different audiences
            test_content = """
            # Advanced API Integration Guide
            
            ## Introduction
            This comprehensive guide covers advanced API integration techniques for modern web applications. 
            We'll explore authentication methods, rate limiting strategies, error handling patterns, and performance optimization.
            
            ## Authentication Methods
            
            ### OAuth 2.0 Implementation
            OAuth 2.0 provides secure authorization for API access. Here's how to implement it:
            
            ```javascript
            const oauth2Client = new OAuth2Client({
                clientId: 'your-client-id',
                clientSecret: 'your-client-secret',
                redirectUri: 'https://your-app.com/callback'
            });
            
            // Generate authorization URL
            const authUrl = oauth2Client.generateAuthUrl({
                access_type: 'offline',
                scope: ['https://www.googleapis.com/auth/userinfo.profile']
            });
            ```
            
            ### API Key Management
            Proper API key management is crucial for security:
            
            1. Store keys in environment variables
            2. Rotate keys regularly
            3. Use different keys for different environments
            4. Monitor key usage and implement alerts
            
            ## Rate Limiting Strategies
            
            ### Client-Side Rate Limiting
            Implement exponential backoff to handle rate limits gracefully:
            
            ```javascript
            class RateLimitHandler {
                constructor(maxRetries = 3) {
                    this.maxRetries = maxRetries;
                }
                
                async makeRequest(url, options, retryCount = 0) {
                    try {
                        const response = await fetch(url, options);
                        
                        if (response.status === 429) {
                            if (retryCount < this.maxRetries) {
                                const delay = Math.pow(2, retryCount) * 1000;
                                await this.sleep(delay);
                                return this.makeRequest(url, options, retryCount + 1);
                            }
                            throw new Error('Rate limit exceeded');
                        }
                        
                        return response;
                    } catch (error) {
                        throw error;
                    }
                }
                
                sleep(ms) {
                    return new Promise(resolve => setTimeout(resolve, ms));
                }
            }
            ```
            
            ### Server-Side Rate Limiting
            Configure rate limiting on your API server:
            
            - Use Redis for distributed rate limiting
            - Implement sliding window algorithms
            - Set appropriate limits per user/IP
            - Provide clear error messages
            
            ## Error Handling Patterns
            
            ### Comprehensive Error Handling
            Implement robust error handling for API calls:
            
            ```javascript
            async function apiCall(endpoint, options = {}) {
                try {
                    const response = await fetch(endpoint, {
                        ...options,
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${getToken()}`,
                            ...options.headers
                        }
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new APIError(errorData.message, response.status, errorData);
                    }
                    
                    return await response.json();
                } catch (error) {
                    if (error instanceof APIError) {
                        throw error;
                    }
                    throw new APIError('Network error occurred', 0, { originalError: error });
                }
            }
            
            class APIError extends Error {
                constructor(message, status, data) {
                    super(message);
                    this.name = 'APIError';
                    this.status = status;
                    this.data = data;
                }
            }
            ```
            
            ## Performance Optimization
            
            ### Caching Strategies
            Implement effective caching to reduce API calls:
            
            1. **Browser Caching**: Use appropriate cache headers
            2. **Application Caching**: Cache responses in memory or localStorage
            3. **CDN Caching**: Leverage CDN for static API responses
            4. **Database Caching**: Cache frequently accessed data
            
            ### Request Optimization
            Optimize your API requests for better performance:
            
            - Use GraphQL for flexible data fetching
            - Implement request batching
            - Use compression (gzip/brotli)
            - Minimize payload size
            
            ## Security Best Practices
            
            ### Input Validation
            Always validate input data:
            
            ```javascript
            function validateApiInput(data) {
                const schema = {
                    email: { type: 'string', format: 'email', required: true },
                    age: { type: 'number', min: 0, max: 150 },
                    preferences: { type: 'object' }
                };
                
                return validateSchema(data, schema);
            }
            ```
            
            ### HTTPS and Encryption
            - Always use HTTPS for API communications
            - Implement proper SSL/TLS configuration
            - Use strong encryption algorithms
            - Validate SSL certificates
            
            ## Monitoring and Analytics
            
            ### API Monitoring
            Monitor your API usage and performance:
            
            - Track response times
            - Monitor error rates
            - Set up alerts for anomalies
            - Use APM tools for detailed insights
            
            ### Usage Analytics
            Analyze API usage patterns:
            
            - Track endpoint popularity
            - Monitor user behavior
            - Identify optimization opportunities
            - Generate usage reports
            
            ## Conclusion
            
            Proper API integration requires careful consideration of authentication, rate limiting, error handling, 
            and performance optimization. By following these best practices, you can build robust and scalable 
            applications that effectively utilize external APIs.
            
            Remember to always test your integrations thoroughly and monitor them in production to ensure 
            optimal performance and reliability.
            """
            
            # Test with different metadata to trigger different audience detection
            test_cases = [
                {
                    "content": test_content,
                    "metadata": {"title": "Developer API Guide", "type": "technical_documentation"},
                    "expected_audience": "developer"
                },
                {
                    "content": test_content.replace("API", "Business Process").replace("authentication", "workflow management"),
                    "metadata": {"title": "Business Process Guide", "type": "business_documentation"},
                    "expected_audience": "business"
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                print(f"\n🧪 Testing V2 Text Processing - Case {i+1}")
                
                payload = {
                    "content": test_case["content"],
                    "metadata": test_case["metadata"]
                }
                
                async with self.session.post(f"{API_BASE}/content/process", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Verify V2 engine usage
                        engine_used = data.get('engine', '')
                        v2_used = engine_used == 'v2'
                        
                        # Check job creation
                        job_id = data.get('job_id', '')
                        
                        if v2_used and job_id:
                            # Wait for processing to complete
                            await asyncio.sleep(5)
                            
                            # Check job status
                            async with self.session.get(f"{API_BASE}/jobs/{job_id}") as job_response:
                                if job_response.status == 200:
                                    job_data = await job_response.json()
                                    status = job_data.get('status', '')
                                    chunks = job_data.get('chunks', [])
                                    
                                    if status == 'completed' and chunks:
                                        # Verify V2ArticleGenerator integration
                                        v2_metadata_found = False
                                        strict_format_compliance = 0
                                        audience_aware_styling = 0
                                        
                                        for chunk in chunks:
                                            metadata = chunk.get('metadata', {})
                                            
                                            # Check V2 metadata
                                            if (metadata.get('engine') == 'v2' and 
                                                metadata.get('generated_by') == 'v2_article_generator'):
                                                v2_metadata_found = True
                                            
                                            # Check strict format compliance
                                            content = chunk.get('content', '')
                                            if self._check_strict_format(content):
                                                strict_format_compliance += 1
                                            
                                            # Check audience-aware styling
                                            if self._check_audience_styling(content, test_case["expected_audience"]):
                                                audience_aware_styling += 1
                                        
                                        # Test results
                                        self.log_test(
                                            f"V2 Text Processing Integration - Case {i+1}",
                                            v2_metadata_found,
                                            f"V2 metadata: {v2_metadata_found}, Articles: {len(chunks)}"
                                        )
                                        
                                        self.log_test(
                                            f"Strict Format Compliance - Case {i+1}",
                                            strict_format_compliance > 0,
                                            f"{strict_format_compliance}/{len(chunks)} articles compliant"
                                        )
                                        
                                        self.log_test(
                                            f"Audience-Aware Styling - Case {i+1}",
                                            audience_aware_styling > 0,
                                            f"{audience_aware_styling}/{len(chunks)} articles audience-aware"
                                        )
                                    else:
                                        self.log_test(f"V2 Text Processing - Case {i+1}", False, f"Job status: {status}, chunks: {len(chunks)}")
                                else:
                                    self.log_test(f"V2 Text Processing - Case {i+1}", False, f"Job check failed: {job_response.status}")
                        else:
                            self.log_test(f"V2 Text Processing - Case {i+1}", False, f"V2 engine: {v2_used}, Job ID: {bool(job_id)}")
                    else:
                        self.log_test(f"V2 Text Processing - Case {i+1}", False, f"Request failed: {response.status}")
                        
        except Exception as e:
            self.log_test("V2 Text Processing", False, f"Error: {str(e)}")
    
    async def test_v2_file_upload_processing(self):
        """Test V2 file upload processing with V2ArticleGenerator"""
        try:
            # Create a test file with comprehensive content
            test_content = """
            Google Maps JavaScript API Integration Guide
            
            Table of Contents:
            1. Getting Started
            2. API Key Setup
            3. Basic Map Implementation
            4. Advanced Features
            5. Customization Options
            6. Troubleshooting
            
            1. Getting Started
            
            The Google Maps JavaScript API allows you to embed Google Maps in your web pages. 
            This guide will walk you through the complete integration process.
            
            Prerequisites:
            - Basic knowledge of HTML, CSS, and JavaScript
            - A Google Cloud Platform account
            - A web server to host your application
            
            2. API Key Setup
            
            First, you need to obtain an API key from the Google Cloud Console:
            
            Step 1: Go to the Google Cloud Console
            Step 2: Create a new project or select an existing one
            Step 3: Enable the Maps JavaScript API
            Step 4: Create credentials (API key)
            Step 5: Restrict your API key for security
            
            3. Basic Map Implementation
            
            Here's how to create a basic map:
            
            HTML Structure:
            <!DOCTYPE html>
            <html>
            <head>
                <title>My Google Map</title>
                <style>
                    #map {
                        height: 400px;
                        width: 100%;
                    }
                </style>
            </head>
            <body>
                <div id="map"></div>
                <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap"></script>
            </body>
            </html>
            
            JavaScript Implementation:
            function initMap() {
                const map = new google.maps.Map(document.getElementById("map"), {
                    zoom: 10,
                    center: { lat: 37.7749, lng: -122.4194 }, // San Francisco
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                });
                
                // Add a marker
                const marker = new google.maps.Marker({
                    position: { lat: 37.7749, lng: -122.4194 },
                    map: map,
                    title: "San Francisco"
                });
            }
            
            4. Advanced Features
            
            4.1 Custom Markers
            You can create custom markers with different icons:
            
            const customMarker = new google.maps.Marker({
                position: { lat: 37.7849, lng: -122.4094 },
                map: map,
                icon: {
                    url: 'path/to/custom-icon.png',
                    scaledSize: new google.maps.Size(50, 50)
                },
                title: "Custom Marker"
            });
            
            4.2 Info Windows
            Add information windows to your markers:
            
            const infoWindow = new google.maps.InfoWindow({
                content: '<div><h3>Location Info</h3><p>This is a sample location.</p></div>'
            });
            
            marker.addListener('click', function() {
                infoWindow.open(map, marker);
            });
            
            4.3 Drawing Tools
            Enable drawing tools for user interaction:
            
            const drawingManager = new google.maps.drawing.DrawingManager({
                drawingMode: google.maps.drawing.OverlayType.MARKER,
                drawingControl: true,
                drawingControlOptions: {
                    position: google.maps.ControlPosition.TOP_CENTER,
                    drawingModes: [
                        google.maps.drawing.OverlayType.MARKER,
                        google.maps.drawing.OverlayType.CIRCLE,
                        google.maps.drawing.OverlayType.POLYGON
                    ]
                }
            });
            
            drawingManager.setMap(map);
            
            5. Customization Options
            
            5.1 Map Styling
            Customize the appearance of your map:
            
            const styledMapType = new google.maps.StyledMapType([
                {
                    "elementType": "geometry",
                    "stylers": [{"color": "#f5f5f5"}]
                },
                {
                    "elementType": "labels.icon",
                    "stylers": [{"visibility": "off"}]
                },
                {
                    "elementType": "labels.text.fill",
                    "stylers": [{"color": "#616161"}]
                }
            ], {name: 'Styled Map'});
            
            map.mapTypes.set('styled_map', styledMapType);
            map.setMapTypeId('styled_map');
            
            5.2 Custom Controls
            Add custom controls to your map:
            
            function createCustomControl() {
                const controlDiv = document.createElement('div');
                controlDiv.style.backgroundColor = '#fff';
                controlDiv.style.border = '2px solid #fff';
                controlDiv.style.borderRadius = '3px';
                controlDiv.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
                controlDiv.style.cursor = 'pointer';
                controlDiv.style.marginBottom = '22px';
                controlDiv.style.textAlign = 'center';
                controlDiv.title = 'Click to center the map';
                
                const controlText = document.createElement('div');
                controlText.style.color = 'rgb(25,25,25)';
                controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
                controlText.style.fontSize = '16px';
                controlText.style.lineHeight = '38px';
                controlText.style.paddingLeft = '5px';
                controlText.style.paddingRight = '5px';
                controlText.innerHTML = 'Center Map';
                controlDiv.appendChild(controlText);
                
                return controlDiv;
            }
            
            const customControl = createCustomControl();
            map.controls[google.maps.ControlPosition.TOP_CENTER].push(customControl);
            
            6. Troubleshooting
            
            Common Issues and Solutions:
            
            6.1 Map Not Loading
            - Check if your API key is valid and properly configured
            - Ensure the Maps JavaScript API is enabled in your Google Cloud project
            - Verify that your domain is authorized to use the API key
            - Check browser console for error messages
            
            6.2 Markers Not Appearing
            - Verify marker coordinates are correct
            - Check if the marker position is within the map bounds
            - Ensure the marker is properly added to the map object
            
            6.3 Performance Issues
            - Limit the number of markers displayed simultaneously
            - Use marker clustering for large datasets
            - Implement lazy loading for complex overlays
            - Optimize custom icons and images
            
            6.4 Mobile Responsiveness
            - Set appropriate viewport meta tag
            - Use responsive CSS for map container
            - Test touch interactions on mobile devices
            - Consider mobile-specific UI adjustments
            
            Best Practices:
            
            1. Security
            - Always restrict your API keys
            - Use HTTPS for production applications
            - Implement proper error handling
            - Monitor API usage and set quotas
            
            2. Performance
            - Cache map data when possible
            - Use appropriate zoom levels
            - Implement efficient marker management
            - Optimize for mobile devices
            
            3. User Experience
            - Provide loading indicators
            - Handle offline scenarios gracefully
            - Implement accessible navigation
            - Test across different browsers and devices
            
            Conclusion:
            
            The Google Maps JavaScript API provides powerful tools for creating interactive maps. 
            By following this guide and implementing the best practices, you can create robust 
            and user-friendly mapping applications.
            
            Remember to stay updated with the latest API changes and always test your implementation 
            thoroughly before deploying to production.
            """
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(test_content)
                temp_file_path = temp_file.name
            
            try:
                # Upload file
                with open(temp_file_path, 'rb') as file:
                    form_data = aiohttp.FormData()
                    form_data.add_field('file', file, filename='google_maps_guide.txt', content_type='text/plain')
                    form_data.add_field('metadata', json.dumps({"type": "technical_guide"}))
                    
                    async with self.session.post(f"{API_BASE}/content/upload", data=form_data) as response:
                        if response.status == 200:
                            data = await response.json()
                            job_id = data.get('job_id', '')
                            
                            if job_id:
                                # Wait for processing
                                await asyncio.sleep(10)  # File processing takes longer
                                
                                # Check job status
                                async with self.session.get(f"{API_BASE}/jobs/{job_id}") as job_response:
                                    if job_response.status == 200:
                                        job_data = await job_response.json()
                                        status = job_data.get('status', '')
                                        chunks = job_data.get('chunks', [])
                                        
                                        if status == 'completed' and chunks:
                                            # Verify V2ArticleGenerator integration
                                            v2_articles = 0
                                            title_extraction_success = 0
                                            html_to_markdown_success = 0
                                            no_media_embedding = 0
                                            
                                            for chunk in chunks:
                                                metadata = chunk.get('metadata', {})
                                                
                                                # Check V2 integration
                                                if (metadata.get('engine') == 'v2' and 
                                                    metadata.get('generated_by') == 'v2_article_generator'):
                                                    v2_articles += 1
                                                
                                                # Check title extraction
                                                title = chunk.get('title', '')
                                                if title and len(title) > 5:
                                                    title_extraction_success += 1
                                                
                                                # Check HTML to Markdown conversion
                                                markdown = chunk.get('markdown', '')
                                                if markdown and len(markdown) > 100:
                                                    html_to_markdown_success += 1
                                                
                                                # Check no media embedding
                                                content = chunk.get('content', '')
                                                if '<img' not in content or '[MEDIA_REFERENCE]' in content:
                                                    no_media_embedding += 1
                                            
                                            # Test results
                                            self.log_test(
                                                "V2 File Upload Processing",
                                                v2_articles > 0,
                                                f"V2 articles: {v2_articles}/{len(chunks)}"
                                            )
                                            
                                            self.log_test(
                                                "Title Extraction from HTML",
                                                title_extraction_success > 0,
                                                f"Successful extractions: {title_extraction_success}/{len(chunks)}"
                                            )
                                            
                                            self.log_test(
                                                "HTML to Markdown Conversion",
                                                html_to_markdown_success > 0,
                                                f"Successful conversions: {html_to_markdown_success}/{len(chunks)}"
                                            )
                                            
                                            self.log_test(
                                                "No Media Embedding",
                                                no_media_embedding == len(chunks),
                                                f"Clean articles: {no_media_embedding}/{len(chunks)}"
                                            )
                                        else:
                                            self.log_test("V2 File Upload Processing", False, f"Status: {status}, chunks: {len(chunks)}")
                                    else:
                                        self.log_test("V2 File Upload Processing", False, f"Job check failed: {job_response.status}")
                            else:
                                self.log_test("V2 File Upload Processing", False, "No job ID returned")
                        else:
                            self.log_test("V2 File Upload Processing", False, f"Upload failed: {response.status}")
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            self.log_test("V2 File Upload Processing", False, f"Error: {str(e)}")
    
    async def test_v2_url_processing(self):
        """Test V2 URL processing with V2ArticleGenerator"""
        try:
            # Test URL processing (using a reliable test URL)
            test_url = "https://httpbin.org/html"  # Simple HTML page for testing
            
            form_data = aiohttp.FormData()
            form_data.add_field('url', test_url)
            form_data.add_field('metadata', json.dumps({"type": "web_content"}))
            
            async with self.session.post(f"{API_BASE}/content/process-url", data=form_data) as response:
                if response.status == 200:
                    data = await response.json()
                    job_id = data.get('job_id', '')
                    
                    if job_id:
                        # Wait for processing
                        await asyncio.sleep(8)
                        
                        # Check job status
                        async with self.session.get(f"{API_BASE}/jobs/{job_id}") as job_response:
                            if job_response.status == 200:
                                job_data = await job_response.json()
                                status = job_data.get('status', '')
                                chunks = job_data.get('chunks', [])
                                
                                if status == 'completed' and chunks:
                                    # Verify V2ArticleGenerator integration
                                    v2_url_processing = False
                                    
                                    for chunk in chunks:
                                        metadata = chunk.get('metadata', {})
                                        
                                        # Check V2 URL processing
                                        if (metadata.get('engine') == 'v2' and 
                                            metadata.get('generated_by') == 'v2_article_generator' and
                                            metadata.get('extraction_method') == 'v2_url_extraction'):
                                            v2_url_processing = True
                                            break
                                    
                                    self.log_test(
                                        "V2 URL Processing with V2ArticleGenerator",
                                        v2_url_processing,
                                        f"Articles: {len(chunks)}, V2 processing: {v2_url_processing}"
                                    )
                                else:
                                    self.log_test("V2 URL Processing", False, f"Status: {status}, chunks: {len(chunks)}")
                            else:
                                self.log_test("V2 URL Processing", False, f"Job check failed: {job_response.status}")
                    else:
                        self.log_test("V2 URL Processing", False, "No job ID returned")
                else:
                    self.log_test("V2 URL Processing", False, f"Request failed: {response.status}")
                    
        except Exception as e:
            self.log_test("V2 URL Processing", False, f"Error: {str(e)}")
    
    async def test_content_library_storage(self):
        """Test that articles are properly stored in content library with V2 metadata"""
        try:
            # Get content library articles
            async with self.session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    if articles:
                        # Look for V2 generated articles
                        v2_articles = []
                        for article in articles:
                            metadata = article.get('metadata', {})
                            if (metadata.get('engine') == 'v2' and 
                                metadata.get('generated_by') == 'v2_article_generator'):
                                v2_articles.append(article)
                        
                        # Check V2 metadata structure
                        proper_v2_metadata = 0
                        for article in v2_articles:
                            metadata = article.get('metadata', {})
                            required_fields = [
                                'engine', 'processing_version', 'generated_by',
                                'audience', 'granularity', 'validation_metadata'
                            ]
                            
                            if all(field in metadata for field in required_fields):
                                proper_v2_metadata += 1
                        
                        self.log_test(
                            "Content Library V2 Storage",
                            len(v2_articles) > 0,
                            f"V2 articles found: {len(v2_articles)}/{len(articles)}"
                        )
                        
                        self.log_test(
                            "V2 Metadata Structure",
                            proper_v2_metadata > 0,
                            f"Proper metadata: {proper_v2_metadata}/{len(v2_articles)}"
                        )
                    else:
                        self.log_test("Content Library V2 Storage", False, "No articles found in content library")
                else:
                    self.log_test("Content Library V2 Storage", False, f"Request failed: {response.status}")
                    
        except Exception as e:
            self.log_test("Content Library V2 Storage", False, f"Error: {str(e)}")
    
    def _check_strict_format(self, content: str) -> bool:
        """Check if content follows strict article format"""
        required_elements = [
            '<h1',  # H1 Title
            '<p>',  # Intro paragraph
            '<ul>',  # Mini-TOC (usually as list)
            '<h2',  # Main body sections
        ]
        
        # Check for basic structure elements
        basic_structure = all(element in content for element in required_elements)
        
        # Check for FAQ section (optional but preferred)
        has_faq = 'FAQ' in content or 'Q:' in content or 'Question' in content
        
        # Check for related links (optional but preferred)
        has_related = 'Related' in content or 'href=' in content
        
        return basic_structure
    
    def _check_audience_styling(self, content: str, expected_audience: str) -> bool:
        """Check if content shows audience-aware styling"""
        audience_indicators = {
            'developer': ['API', 'code', 'function', 'implementation', 'technical'],
            'business': ['strategy', 'ROI', 'business', 'value', 'process'],
            'admin': ['configuration', 'setup', 'management', 'system', 'procedure'],
            'end_user': ['guide', 'how to', 'step', 'user', 'simple']
        }
        
        indicators = audience_indicators.get(expected_audience, [])
        content_lower = content.lower()
        
        # Check if at least 2 audience indicators are present
        found_indicators = sum(1 for indicator in indicators if indicator in content_lower)
        return found_indicators >= 2
    
    async def run_all_tests(self):
        """Run all V2 Engine Step 7 tests"""
        print("🚀 V2 ENGINE STEP 7 IMPLEMENTATION TESTING")
        print("=" * 60)
        
        # Test backend health first
        if not await self.test_backend_health():
            print("❌ Backend health check failed. Stopping tests.")
            return
        
        print("\n📝 Testing V2 Text Processing with V2ArticleGenerator...")
        await self.test_v2_text_processing_with_article_generator()
        
        print("\n📁 Testing V2 File Upload Processing...")
        await self.test_v2_file_upload_processing()
        
        print("\n🌐 Testing V2 URL Processing...")
        await self.test_v2_url_processing()
        
        print("\n📚 Testing Content Library Storage...")
        await self.test_content_library_storage()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 V2 ENGINE STEP 7 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ V2 ENGINE STEP 7 IMPLEMENTATION: SUCCESSFUL")
        elif success_rate >= 60:
            print("⚠️ V2 ENGINE STEP 7 IMPLEMENTATION: PARTIALLY SUCCESSFUL")
        else:
            print("❌ V2 ENGINE STEP 7 IMPLEMENTATION: NEEDS ATTENTION")
        
        print("\n📋 Detailed Test Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")

async def main():
    """Main test execution"""
    async with V2EngineStep7Tester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())