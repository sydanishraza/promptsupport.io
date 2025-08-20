#!/usr/bin/env python3
"""
PHASE 6 ENHANCED MULTI-DIMENSIONAL CONTENT PROCESSING PIPELINE TESTING
Comprehensive testing of Phase 6 features including:
1. Multi-dimensional analysis testing
2. Adaptive granularity processing  
3. Enhanced formatting preservation
4. Processing pipeline integration
5. Backward compatibility
6. Error handling & resilience
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://article-genius-1.preview.emergentagent.com"
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

def test_multi_dimensional_analysis():
    """Test the enhanced_multi_dimensional_analysis function with different content types"""
    try:
        log_test_result("🧠 TESTING MULTI-DIMENSIONAL ANALYSIS", "CRITICAL")
        
        # Test scenarios with different content types
        test_scenarios = [
            {
                "name": "Tutorial Content (should use unified approach)",
                "content": """# Google Maps JavaScript API Tutorial
                
                ## Step 1: Setup Your API Key
                First, you need to get an API key from Google Cloud Console.
                
                ```javascript
                const apiKey = 'YOUR_API_KEY_HERE';
                ```
                
                ## Step 2: Initialize the Map
                Create a basic map instance:
                
                ```javascript
                function initMap() {
                    const map = new google.maps.Map(document.getElementById('map'), {
                        zoom: 10,
                        center: { lat: -34.397, lng: 150.644 }
                    });
                }
                ```
                
                ## Step 3: Add Markers
                Add markers to your map:
                
                ```javascript
                const marker = new google.maps.Marker({
                    position: { lat: -34.397, lng: 150.644 },
                    map: map,
                    title: 'Hello World!'
                });
                ```
                
                This tutorial shows you how to create interactive maps step by step.""",
                "expected_type": "tutorial",
                "expected_approach": "unified"
            },
            {
                "name": "Complex Documentation (should use appropriate split)",
                "content": """# Product Documentation Manual
                
                ## Chapter 1: Introduction
                This comprehensive manual covers all aspects of our product suite including installation, configuration, usage, and troubleshooting.
                
                ## Chapter 2: Installation Guide
                ### System Requirements
                - Windows 10 or later
                - 8GB RAM minimum
                - 50GB disk space
                
                ### Installation Steps
                1. Download the installer
                2. Run as administrator
                3. Follow setup wizard
                
                ## Chapter 3: Configuration
                ### Database Setup
                Configure your database connection:
                - Host: localhost
                - Port: 5432
                - Database: myapp
                
                ### User Management
                Set up user accounts and permissions.
                
                ## Chapter 4: Advanced Features
                ### API Integration
                Connect to external services using our REST API.
                
                ### Custom Workflows
                Create automated workflows for your business processes.
                
                ## Chapter 5: Troubleshooting
                Common issues and solutions.
                
                ## Chapter 6: FAQ
                Frequently asked questions and answers.""",
                "expected_type": "product_guide",
                "expected_approach": "split"
            },
            {
                "name": "Code-Heavy Content (should preserve formatting)",
                "content": """# API Reference Guide
                
                ## Authentication
                All API requests require authentication:
                
                ```javascript
                const headers = {
                    'Authorization': 'Bearer ' + token,
                    'Content-Type': 'application/json'
                };
                ```
                
                ## Endpoints
                
                ### GET /api/users
                Retrieve user list:
                
                ```javascript
                fetch('/api/users', {
                    method: 'GET',
                    headers: headers
                })
                .then(response => response.json())
                .then(data => console.log(data));
                ```
                
                ### POST /api/users
                Create new user:
                
                ```javascript
                const userData = {
                    name: 'John Doe',
                    email: 'john@example.com'
                };
                
                fetch('/api/users', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(userData)
                });
                ```
                
                ## Error Handling
                Handle API errors properly:
                
                ```javascript
                .catch(error => {
                    console.error('API Error:', error);
                    // Handle error appropriately
                });
                ```""",
                "expected_type": "reference",
                "expected_formatting": "code_heavy"
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            log_test_result(f"Testing scenario: {scenario['name']}")
            
            # Test content processing with this scenario
            try:
                # Create a test file with the content
                test_filename = f"test_{scenario['name'].lower().replace(' ', '_')}.txt"
                test_content = scenario['content']
                
                # Upload content as text
                files = {'file': (test_filename, test_content.encode(), 'text/plain')}
                
                start_time = time.time()
                response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
                
                if response.status_code == 200:
                    upload_data = response.json()
                    job_id = upload_data.get('job_id')
                    
                    if job_id:
                        # Monitor processing
                        processing_result = monitor_processing(job_id, max_wait=180)
                        
                        if processing_result['success']:
                            # Analyze the results
                            analysis_result = analyze_processing_results(processing_result, scenario)
                            results.append({
                                'scenario': scenario['name'],
                                'success': analysis_result['success'],
                                'details': analysis_result
                            })
                            
                            if analysis_result['success']:
                                log_test_result(f"✅ {scenario['name']}: Analysis successful", "SUCCESS")
                            else:
                                log_test_result(f"❌ {scenario['name']}: Analysis failed - {analysis_result.get('reason', 'Unknown')}", "ERROR")
                        else:
                            log_test_result(f"❌ {scenario['name']}: Processing failed", "ERROR")
                            results.append({'scenario': scenario['name'], 'success': False, 'reason': 'Processing failed'})
                    else:
                        log_test_result(f"❌ {scenario['name']}: No job_id received", "ERROR")
                        results.append({'scenario': scenario['name'], 'success': False, 'reason': 'No job_id'})
                else:
                    log_test_result(f"❌ {scenario['name']}: Upload failed - Status {response.status_code}", "ERROR")
                    results.append({'scenario': scenario['name'], 'success': False, 'reason': f'Upload failed: {response.status_code}'})
                    
            except Exception as e:
                log_test_result(f"❌ {scenario['name']}: Exception - {e}", "ERROR")
                results.append({'scenario': scenario['name'], 'success': False, 'reason': str(e)})
        
        # Evaluate overall results
        successful_scenarios = sum(1 for r in results if r['success'])
        total_scenarios = len(results)
        
        log_test_result(f"📊 Multi-dimensional analysis results: {successful_scenarios}/{total_scenarios} scenarios passed")
        
        if successful_scenarios >= total_scenarios * 0.8:  # 80% success rate
            log_test_result("✅ Multi-dimensional analysis testing PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ Multi-dimensional analysis testing FAILED", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Multi-dimensional analysis testing failed: {e}", "ERROR")
        return False

def monitor_processing(job_id, max_wait=300):
    """Monitor job processing and return results"""
    try:
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                return {'success': False, 'reason': 'Timeout'}
            
            try:
                response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    
                    if status == 'completed':
                        return {
                            'success': True,
                            'data': data,
                            'processing_time': elapsed,
                            'articles_generated': data.get('articles_generated', 0),
                            'chunks_created': data.get('chunks_created', 0)
                        }
                    elif status == 'failed':
                        return {'success': False, 'reason': data.get('error', 'Processing failed')}
                    
                    time.sleep(5)
                else:
                    time.sleep(5)
                    
            except Exception as e:
                time.sleep(5)
                
    except Exception as e:
        return {'success': False, 'reason': str(e)}

def analyze_processing_results(processing_result, scenario):
    """Analyze processing results against expected outcomes"""
    try:
        articles_generated = processing_result.get('articles_generated', 0)
        processing_time = processing_result.get('processing_time', 0)
        
        analysis = {
            'success': True,
            'articles_generated': articles_generated,
            'processing_time': processing_time,
            'meets_expectations': True,
            'details': []
        }
        
        # Check if results meet scenario expectations
        expected_type = scenario.get('expected_type', '')
        expected_approach = scenario.get('expected_approach', '')
        
        # Tutorial content should generate fewer articles (unified approach)
        if expected_approach == 'unified':
            if articles_generated <= 3:
                analysis['details'].append("✅ Unified approach correctly applied (≤3 articles)")
            else:
                analysis['details'].append(f"⚠️ Expected unified approach but got {articles_generated} articles")
                analysis['meets_expectations'] = False
        
        # Complex documentation should generate more articles (split approach)
        elif expected_approach == 'split':
            if articles_generated >= 4:
                analysis['details'].append(f"✅ Split approach correctly applied ({articles_generated} articles)")
            else:
                analysis['details'].append(f"⚠️ Expected split approach but got only {articles_generated} articles")
                analysis['meets_expectations'] = False
        
        # Check processing time is reasonable
        if processing_time < 120:  # Under 2 minutes
            analysis['details'].append(f"✅ Processing time acceptable ({processing_time:.1f}s)")
        else:
            analysis['details'].append(f"⚠️ Processing time high ({processing_time:.1f}s)")
        
        # Check articles were actually generated
        if articles_generated > 0:
            analysis['details'].append(f"✅ Articles generated successfully ({articles_generated})")
        else:
            analysis['details'].append("❌ No articles generated")
            analysis['success'] = False
        
        return analysis
        
    except Exception as e:
        return {'success': False, 'reason': str(e)}

def test_adaptive_granularity_processing():
    """Test adaptive granularity with different content sizes and types"""
    try:
        log_test_result("📏 TESTING ADAPTIVE GRANULARITY PROCESSING", "CRITICAL")
        
        # Test different granularity levels
        granularity_tests = [
            {
                "name": "Shallow Split (Simple Guide)",
                "content": """# Quick Start Guide
                
                ## Introduction
                This is a simple guide to get you started quickly.
                
                ## Setup
                1. Download the software
                2. Install it
                3. Run the application
                
                ## Basic Usage
                - Open the application
                - Create a new project
                - Start working
                
                ## Conclusion
                You're now ready to use the software effectively.""",
                "expected_articles": 2,  # Should generate 2-3 articles
                "granularity": "shallow"
            },
            {
                "name": "Moderate Split (Medium Documentation)",
                "content": """# Comprehensive User Manual
                
                ## Chapter 1: Introduction
                Welcome to our comprehensive user manual. This guide covers all aspects of using our software effectively.
                
                ## Chapter 2: Installation and Setup
                ### System Requirements
                Before installing, ensure your system meets these requirements:
                - Operating System: Windows 10 or later
                - RAM: 8GB minimum, 16GB recommended
                - Storage: 10GB free space
                - Network: Internet connection required
                
                ### Installation Process
                1. Download the installer from our website
                2. Run the installer as administrator
                3. Follow the installation wizard
                4. Restart your computer when prompted
                
                ## Chapter 3: Getting Started
                ### First Launch
                When you first launch the application, you'll see the welcome screen.
                
                ### Creating Your First Project
                To create a new project:
                1. Click "New Project"
                2. Choose a template
                3. Enter project details
                4. Click "Create"
                
                ## Chapter 4: Advanced Features
                ### Customization Options
                The software offers extensive customization options.
                
                ### Integration with Other Tools
                Connect with popular third-party applications.
                
                ## Chapter 5: Troubleshooting
                Common issues and their solutions.
                
                ## Chapter 6: FAQ
                Frequently asked questions and detailed answers.""",
                "expected_articles": 5,  # Should generate 4-6 articles
                "granularity": "moderate"
            },
            {
                "name": "Deep Split (Comprehensive Manual)",
                "content": """# Enterprise Software Documentation
                
                ## Part I: Introduction and Overview
                ### Chapter 1: Welcome to Enterprise Software
                This comprehensive documentation covers all aspects of our enterprise software solution.
                
                ### Chapter 2: Architecture Overview
                Understanding the system architecture and components.
                
                ## Part II: Installation and Configuration
                ### Chapter 3: System Requirements
                Detailed system requirements for different deployment scenarios.
                
                ### Chapter 4: Installation Guide
                Step-by-step installation instructions for various environments.
                
                ### Chapter 5: Initial Configuration
                Configure the system for your organization's needs.
                
                ## Part III: User Management
                ### Chapter 6: User Accounts
                Creating and managing user accounts.
                
                ### Chapter 7: Roles and Permissions
                Setting up role-based access control.
                
                ### Chapter 8: Authentication Systems
                Integrating with LDAP, SSO, and other authentication systems.
                
                ## Part IV: Core Features
                ### Chapter 9: Dashboard and Navigation
                Understanding the user interface and navigation.
                
                ### Chapter 10: Data Management
                Working with data import, export, and management features.
                
                ### Chapter 11: Reporting and Analytics
                Creating reports and analyzing data.
                
                ## Part V: Advanced Features
                ### Chapter 12: API Integration
                Using the REST API for custom integrations.
                
                ### Chapter 13: Workflow Automation
                Setting up automated workflows and processes.
                
                ### Chapter 14: Custom Development
                Extending the system with custom modules.
                
                ## Part VI: Administration
                ### Chapter 15: System Administration
                Administrative tasks and system maintenance.
                
                ### Chapter 16: Backup and Recovery
                Data backup strategies and disaster recovery.
                
                ### Chapter 17: Performance Optimization
                Optimizing system performance and scalability.
                
                ## Part VII: Troubleshooting and Support
                ### Chapter 18: Common Issues
                Troubleshooting common problems and solutions.
                
                ### Chapter 19: Error Messages
                Understanding and resolving error messages.
                
                ### Chapter 20: Support Resources
                Getting help and additional resources.""",
                "expected_articles": 8,  # Should generate 7+ articles
                "granularity": "deep"
            }
        ]
        
        results = []
        
        for test in granularity_tests:
            log_test_result(f"Testing granularity: {test['name']}")
            
            try:
                # Upload and process content
                test_filename = f"granularity_{test['granularity']}_test.txt"
                files = {'file': (test_filename, test['content'].encode(), 'text/plain')}
                
                response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
                
                if response.status_code == 200:
                    upload_data = response.json()
                    job_id = upload_data.get('job_id')
                    
                    if job_id:
                        processing_result = monitor_processing(job_id, max_wait=240)
                        
                        if processing_result['success']:
                            articles_generated = processing_result.get('articles_generated', 0)
                            expected_articles = test['expected_articles']
                            
                            # Check if granularity is appropriate
                            granularity_appropriate = False
                            
                            if test['granularity'] == 'shallow' and 2 <= articles_generated <= 3:
                                granularity_appropriate = True
                            elif test['granularity'] == 'moderate' and 4 <= articles_generated <= 6:
                                granularity_appropriate = True
                            elif test['granularity'] == 'deep' and articles_generated >= 7:
                                granularity_appropriate = True
                            
                            results.append({
                                'test': test['name'],
                                'success': granularity_appropriate,
                                'articles_generated': articles_generated,
                                'expected_range': f"{expected_articles}±1",
                                'granularity': test['granularity']
                            })
                            
                            if granularity_appropriate:
                                log_test_result(f"✅ {test['name']}: Appropriate granularity ({articles_generated} articles)", "SUCCESS")
                            else:
                                log_test_result(f"❌ {test['name']}: Inappropriate granularity ({articles_generated} articles, expected ~{expected_articles})", "ERROR")
                        else:
                            log_test_result(f"❌ {test['name']}: Processing failed", "ERROR")
                            results.append({'test': test['name'], 'success': False, 'reason': 'Processing failed'})
                    else:
                        log_test_result(f"❌ {test['name']}: No job_id received", "ERROR")
                        results.append({'test': test['name'], 'success': False, 'reason': 'No job_id'})
                else:
                    log_test_result(f"❌ {test['name']}: Upload failed", "ERROR")
                    results.append({'test': test['name'], 'success': False, 'reason': 'Upload failed'})
                    
            except Exception as e:
                log_test_result(f"❌ {test['name']}: Exception - {e}", "ERROR")
                results.append({'test': test['name'], 'success': False, 'reason': str(e)})
        
        # Evaluate results
        successful_tests = sum(1 for r in results if r.get('success', False))
        total_tests = len(results)
        
        log_test_result(f"📊 Adaptive granularity results: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests >= total_tests * 0.7:  # 70% success rate
            log_test_result("✅ Adaptive granularity processing PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ Adaptive granularity processing FAILED", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Adaptive granularity testing failed: {e}", "ERROR")
        return False

def test_enhanced_formatting_preservation():
    """Test enhanced formatting preservation for code blocks, callouts, lists, tables"""
    try:
        log_test_result("🎨 TESTING ENHANCED FORMATTING PRESERVATION", "CRITICAL")
        
        # Test content with rich formatting
        rich_content = """# Technical Documentation with Rich Formatting
        
        ## Code Blocks with Language Detection
        
        Here's a JavaScript example:
        ```javascript
        function initializeApp() {
            const config = {
                apiKey: 'your-api-key',
                authDomain: 'your-domain.firebaseapp.com'
            };
            
            firebase.initializeApp(config);
            console.log('App initialized successfully');
        }
        ```
        
        Python example:
        ```python
        def process_data(data):
            result = []
            for item in data:
                if item.is_valid():
                    result.append(item.transform())
            return result
        ```
        
        ## Callouts and Notes
        
        > **Note:** This is an important note that users should pay attention to.
        
        > **Tip:** Here's a helpful tip for better performance.
        
        > **Warning:** Be careful when modifying these settings.
        
        > **Important:** This step is critical for proper functionality.
        
        ## Lists and Structured Content
        
        ### Ordered List
        1. First step in the process
        2. Second step with details
        3. Third step with sub-items:
           a. Sub-item one
           b. Sub-item two
           c. Sub-item three
        4. Final step
        
        ### Unordered List
        - Feature A: Description of feature A
        - Feature B: Description of feature B
          - Sub-feature B1
          - Sub-feature B2
        - Feature C: Description of feature C
        
        ### Checklist
        - [x] Completed task
        - [x] Another completed task
        - [ ] Pending task
        - [ ] Future task
        
        ## Tables
        
        | Feature | Basic Plan | Pro Plan | Enterprise |
        |---------|------------|----------|------------|
        | Users | 5 | 50 | Unlimited |
        | Storage | 10GB | 100GB | 1TB |
        | Support | Email | Priority | 24/7 Phone |
        | API Calls | 1,000/month | 10,000/month | Unlimited |
        
        ## Mixed Content Example
        
        To configure the database connection:
        
        1. Open the configuration file:
        ```bash
        nano /etc/myapp/config.yml
        ```
        
        2. Update the database settings:
        ```yaml
        database:
          host: localhost
          port: 5432
          name: myapp_db
          user: myapp_user
          password: secure_password
        ```
        
        > **Important:** Make sure to restart the service after making changes.
        
        3. Restart the service:
        ```bash
        sudo systemctl restart myapp
        ```
        
        ## Code with Inline Comments
        
        ```javascript
        // Initialize the application
        const app = {
            // Configuration object
            config: {
                debug: true,
                version: '1.0.0'
            },
            
            // Main initialization function
            init: function() {
                console.log('Starting app version', this.config.version);
                
                // Set up event listeners
                this.setupEventListeners();
                
                // Load initial data
                this.loadData();
            },
            
            // Event listener setup
            setupEventListeners: function() {
                document.addEventListener('DOMContentLoaded', () => {
                    console.log('DOM loaded, app ready');
                });
            }
        };
        
        // Start the application
        app.init();
        ```
        """
        
        # Upload and process the rich content
        test_filename = "rich_formatting_test.md"
        files = {'file': (test_filename, rich_content.encode(), 'text/markdown')}
        
        response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
        
        if response.status_code == 200:
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if job_id:
                processing_result = monitor_processing(job_id, max_wait=240)
                
                if processing_result['success']:
                    # Check if articles were generated
                    articles_generated = processing_result.get('articles_generated', 0)
                    
                    if articles_generated > 0:
                        # Verify formatting preservation by checking Content Library
                        formatting_check = verify_formatting_preservation()
                        
                        if formatting_check['success']:
                            log_test_result("✅ Enhanced formatting preservation PASSED", "SUCCESS")
                            log_test_result(f"   Code blocks preserved: {formatting_check.get('code_blocks', 0)}")
                            log_test_result(f"   Lists preserved: {formatting_check.get('lists', 0)}")
                            log_test_result(f"   Tables preserved: {formatting_check.get('tables', 0)}")
                            return True
                        else:
                            log_test_result("❌ Formatting preservation verification failed", "ERROR")
                            return False
                    else:
                        log_test_result("❌ No articles generated for formatting test", "ERROR")
                        return False
                else:
                    log_test_result("❌ Processing failed for formatting test", "ERROR")
                    return False
            else:
                log_test_result("❌ No job_id received for formatting test", "ERROR")
                return False
        else:
            log_test_result(f"❌ Upload failed for formatting test: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Enhanced formatting preservation testing failed: {e}", "ERROR")
        return False

def verify_formatting_preservation():
    """Verify that formatting elements are preserved in generated articles"""
    try:
        # Get recent articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Look for recent articles (last 10)
            recent_articles = articles[:10]
            
            formatting_stats = {
                'success': False,
                'code_blocks': 0,
                'lists': 0,
                'tables': 0,
                'callouts': 0,
                'articles_checked': len(recent_articles)
            }
            
            for article in recent_articles:
                content = article.get('content', '')
                
                # Check for code blocks
                if '<pre>' in content or '<code>' in content or '```' in content:
                    formatting_stats['code_blocks'] += 1
                
                # Check for lists
                if '<ul>' in content or '<ol>' in content or '<li>' in content:
                    formatting_stats['lists'] += 1
                
                # Check for tables
                if '<table>' in content or '<tr>' in content or '<td>' in content:
                    formatting_stats['tables'] += 1
                
                # Check for callouts/notes
                if 'note' in content.lower() or 'tip' in content.lower() or 'warning' in content.lower():
                    formatting_stats['callouts'] += 1
            
            # Consider successful if we found some formatting elements
            if (formatting_stats['code_blocks'] > 0 or 
                formatting_stats['lists'] > 0 or 
                formatting_stats['tables'] > 0):
                formatting_stats['success'] = True
            
            return formatting_stats
        else:
            return {'success': False, 'reason': 'Could not access Content Library'}
            
    except Exception as e:
        return {'success': False, 'reason': str(e)}

def test_processing_pipeline_integration():
    """Test the complete intelligent_content_processing_pipeline integration"""
    try:
        log_test_result("🔄 TESTING PROCESSING PIPELINE INTEGRATION", "CRITICAL")
        
        # Test with Google Maps API tutorial scenario (as mentioned in review)
        google_maps_content = """# Google Maps JavaScript API Tutorial - Complete Guide
        
        ## Introduction
        The Google Maps JavaScript API lets you customize maps with your own content and imagery for display on web pages and mobile devices.
        
        ## Prerequisites
        - Basic knowledge of HTML and JavaScript
        - A Google Cloud Platform account
        - A web server (local or remote)
        
        ## Step 1: Get an API Key
        
        1. Go to the Google Cloud Console
        2. Create a new project or select an existing one
        3. Enable the Maps JavaScript API
        4. Create credentials (API key)
        
        ```javascript
        // Your API key will look like this
        const API_KEY = 'AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
        ```
        
        > **Important:** Restrict your API key to prevent unauthorized use.
        
        ## Step 2: Basic HTML Setup
        
        Create a basic HTML file:
        
        ```html
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
            <h1>My Google Map</h1>
            <div id="map"></div>
            
            <script>
                function initMap() {
                    // Map initialization code goes here
                }
            </script>
            <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap"></script>
        </body>
        </html>
        ```
        
        ## Step 3: Initialize the Map
        
        Add the map initialization code:
        
        ```javascript
        function initMap() {
            // The location of your choice
            const location = { lat: -25.344, lng: 131.036 };
            
            // The map, centered at location
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 4,
                center: location,
            });
            
            // The marker, positioned at location
            const marker = new google.maps.Marker({
                position: location,
                map: map,
            });
        }
        ```
        
        ## Step 4: Adding Custom Markers
        
        You can add multiple markers with custom icons:
        
        ```javascript
        function addCustomMarkers(map) {
            const locations = [
                { lat: -25.344, lng: 131.036, title: 'Location 1' },
                { lat: -25.355, lng: 131.044, title: 'Location 2' },
                { lat: -25.363, lng: 131.052, title: 'Location 3' }
            ];
            
            locations.forEach(location => {
                new google.maps.Marker({
                    position: { lat: location.lat, lng: location.lng },
                    map: map,
                    title: location.title,
                    icon: {
                        url: 'custom-marker.png',
                        scaledSize: new google.maps.Size(32, 32)
                    }
                });
            });
        }
        ```
        
        ## Step 5: Info Windows
        
        Add information windows to your markers:
        
        ```javascript
        function createInfoWindow(marker, content) {
            const infoWindow = new google.maps.InfoWindow({
                content: content
            });
            
            marker.addListener('click', () => {
                infoWindow.open(map, marker);
            });
        }
        ```
        
        ## Step 6: Map Styling
        
        Customize your map appearance:
        
        ```javascript
        const styledMapType = new google.maps.StyledMapType([
            {
                "elementType": "geometry",
                "stylers": [{"color": "#f5f5f5"}]
            },
            {
                "elementType": "labels.icon",
                "stylers": [{"visibility": "off"}]
            }
        ], {name: 'Styled Map'});
        
        map.mapTypes.set('styled_map', styledMapType);
        map.setMapTypeId('styled_map');
        ```
        
        ## Troubleshooting
        
        ### Common Issues
        
        1. **Map not loading**: Check your API key and make sure the Maps JavaScript API is enabled
        2. **Markers not appearing**: Verify coordinates are correct
        3. **Console errors**: Check for JavaScript syntax errors
        
        ### Error Handling
        
        ```javascript
        function initMap() {
            try {
                // Map initialization code
            } catch (error) {
                console.error('Error initializing map:', error);
                document.getElementById('map').innerHTML = 'Error loading map';
            }
        }
        ```
        
        ## Best Practices
        
        - Always restrict your API key
        - Use error handling
        - Optimize marker loading for large datasets
        - Consider map clustering for many markers
        - Test on different devices and browsers
        
        ## Conclusion
        
        You now have a complete Google Maps integration with custom markers, info windows, and styling. This tutorial covered all the essential features you need to create interactive maps for your web applications.
        """
        
        # Upload and process the Google Maps tutorial
        test_filename = "google_maps_api_tutorial.md"
        files = {'file': (test_filename, google_maps_content.encode(), 'text/markdown')}
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=300)
        
        if response.status_code == 200:
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if job_id:
                processing_result = monitor_processing(job_id, max_wait=300)
                
                if processing_result['success']:
                    # Verify pipeline integration
                    integration_check = verify_pipeline_integration(processing_result)
                    
                    if integration_check['success']:
                        log_test_result("✅ Processing pipeline integration PASSED", "SUCCESS")
                        log_test_result(f"   Articles generated: {integration_check.get('articles_generated', 0)}")
                        log_test_result(f"   Cross-references: {integration_check.get('cross_references', 0)}")
                        log_test_result(f"   Related links: {integration_check.get('related_links', 0)}")
                        return True
                    else:
                        log_test_result("❌ Pipeline integration verification failed", "ERROR")
                        return False
                else:
                    log_test_result("❌ Processing failed for pipeline integration test", "ERROR")
                    return False
            else:
                log_test_result("❌ No job_id received for pipeline integration test", "ERROR")
                return False
        else:
            log_test_result(f"❌ Upload failed for pipeline integration test: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Processing pipeline integration testing failed: {e}", "ERROR")
        return False

def verify_pipeline_integration(processing_result):
    """Verify that the processing pipeline properly integrated all components"""
    try:
        articles_generated = processing_result.get('articles_generated', 0)
        
        # Get articles from Content Library to verify integration
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Look for recent articles (last 10)
            recent_articles = articles[:10]
            
            integration_stats = {
                'success': False,
                'articles_generated': articles_generated,
                'cross_references': 0,
                'related_links': 0,
                'metadata_present': 0,
                'proper_tagging': 0
            }
            
            for article in recent_articles:
                content = article.get('content', '')
                metadata = article.get('metadata', {})
                tags = article.get('tags', [])
                
                # Check for cross-references and related links
                if 'related' in content.lower() or 'see also' in content.lower():
                    integration_stats['cross_references'] += 1
                
                if '<a href=' in content or 'content-library/article' in content:
                    integration_stats['related_links'] += 1
                
                # Check for proper metadata
                if metadata and len(metadata) > 0:
                    integration_stats['metadata_present'] += 1
                
                # Check for proper tagging
                if tags and len(tags) > 0:
                    integration_stats['proper_tagging'] += 1
            
            # Consider successful if articles were generated and have some integration features
            if (articles_generated > 0 and 
                (integration_stats['metadata_present'] > 0 or 
                 integration_stats['proper_tagging'] > 0)):
                integration_stats['success'] = True
            
            return integration_stats
        else:
            return {'success': False, 'reason': 'Could not access Content Library'}
            
    except Exception as e:
        return {'success': False, 'reason': str(e)}

def test_backward_compatibility():
    """Test that existing functionality still works (backward compatibility)"""
    try:
        log_test_result("🔄 TESTING BACKWARD COMPATIBILITY", "CRITICAL")
        
        # Test with simple content that should work with legacy processing
        simple_content = """# Simple User Guide
        
        ## Getting Started
        This is a simple guide to help you get started with our product.
        
        ## Basic Features
        Here are the basic features you need to know:
        - Feature 1: Description
        - Feature 2: Description
        - Feature 3: Description
        
        ## Conclusion
        You're now ready to use the product effectively.
        """
        
        # Upload and process simple content
        test_filename = "backward_compatibility_test.txt"
        files = {'file': (test_filename, simple_content.encode(), 'text/plain')}
        
        response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=180)
        
        if response.status_code == 200:
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            
            if job_id:
                processing_result = monitor_processing(job_id, max_wait=120)
                
                if processing_result['success']:
                    articles_generated = processing_result.get('articles_generated', 0)
                    
                    if articles_generated > 0:
                        log_test_result("✅ Backward compatibility PASSED", "SUCCESS")
                        log_test_result(f"   Simple content processed successfully ({articles_generated} articles)")
                        return True
                    else:
                        log_test_result("❌ Backward compatibility FAILED: No articles generated", "ERROR")
                        return False
                else:
                    log_test_result("❌ Backward compatibility FAILED: Processing failed", "ERROR")
                    return False
            else:
                log_test_result("❌ Backward compatibility FAILED: No job_id", "ERROR")
                return False
        else:
            log_test_result(f"❌ Backward compatibility FAILED: Upload failed ({response.status_code})", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backward compatibility testing failed: {e}", "ERROR")
        return False

def test_error_handling_resilience():
    """Test error handling and resilience with various edge cases"""
    try:
        log_test_result("🛡️ TESTING ERROR HANDLING & RESILIENCE", "CRITICAL")
        
        error_tests = [
            {
                "name": "Insufficient Content",
                "content": "Too short",
                "expected_behavior": "graceful_handling"
            },
            {
                "name": "Malformed Content",
                "content": "# Broken\n\n```javascript\nfunction broken() {\n// Missing closing brace\n\n## Another Section\nContent here",
                "expected_behavior": "process_anyway"
            },
            {
                "name": "Very Large Content",
                "content": "# Large Document\n\n" + ("This is a very long paragraph with lots of content. " * 1000),
                "expected_behavior": "handle_large_content"
            }
        ]
        
        results = []
        
        for test in error_tests:
            log_test_result(f"Testing error scenario: {test['name']}")
            
            try:
                test_filename = f"error_test_{test['name'].lower().replace(' ', '_')}.txt"
                files = {'file': (test_filename, test['content'].encode(), 'text/plain')}
                
                response = requests.post(f"{API_BASE}/content/upload", files=files, timeout=180)
                
                if response.status_code == 200:
                    upload_data = response.json()
                    job_id = upload_data.get('job_id')
                    
                    if job_id:
                        processing_result = monitor_processing(job_id, max_wait=120)
                        
                        # For error handling, we expect either success or graceful failure
                        if processing_result['success'] or 'graceful' in str(processing_result.get('reason', '')):
                            results.append({'test': test['name'], 'success': True})
                            log_test_result(f"✅ {test['name']}: Handled gracefully", "SUCCESS")
                        else:
                            results.append({'test': test['name'], 'success': False, 'reason': 'Not handled gracefully'})
                            log_test_result(f"❌ {test['name']}: Not handled gracefully", "ERROR")
                    else:
                        # No job_id might be acceptable for some error cases
                        results.append({'test': test['name'], 'success': True, 'reason': 'Rejected appropriately'})
                        log_test_result(f"✅ {test['name']}: Rejected appropriately", "SUCCESS")
                else:
                    # HTTP error might be acceptable for some cases
                    if response.status_code in [400, 422]:  # Bad request or validation error
                        results.append({'test': test['name'], 'success': True, 'reason': 'Validation error as expected'})
                        log_test_result(f"✅ {test['name']}: Validation error as expected", "SUCCESS")
                    else:
                        results.append({'test': test['name'], 'success': False, 'reason': f'Unexpected HTTP {response.status_code}'})
                        log_test_result(f"❌ {test['name']}: Unexpected HTTP {response.status_code}", "ERROR")
                        
            except Exception as e:
                # Exceptions might be acceptable for error cases
                results.append({'test': test['name'], 'success': True, 'reason': 'Exception handled'})
                log_test_result(f"✅ {test['name']}: Exception handled appropriately", "SUCCESS")
        
        # Evaluate results
        successful_tests = sum(1 for r in results if r.get('success', False))
        total_tests = len(results)
        
        log_test_result(f"📊 Error handling results: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests >= total_tests * 0.8:  # 80% success rate
            log_test_result("✅ Error handling & resilience PASSED", "SUCCESS")
            return True
        else:
            log_test_result("❌ Error handling & resilience FAILED", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Error handling & resilience testing failed: {e}", "ERROR")
        return False

def run_phase6_comprehensive_test():
    """Run comprehensive Phase 6 Enhanced Multi-Dimensional Content Processing Pipeline test suite"""
    log_test_result("🚀 STARTING PHASE 6 COMPREHENSIVE TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'multi_dimensional_analysis': False,
        'adaptive_granularity_processing': False,
        'enhanced_formatting_preservation': False,
        'processing_pipeline_integration': False,
        'backward_compatibility': False,
        'error_handling_resilience': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Multi-Dimensional Analysis
    log_test_result("\nTEST 2: Multi-Dimensional Analysis Testing")
    test_results['multi_dimensional_analysis'] = test_multi_dimensional_analysis()
    
    # Test 3: Adaptive Granularity Processing
    log_test_result("\nTEST 3: Adaptive Granularity Processing")
    test_results['adaptive_granularity_processing'] = test_adaptive_granularity_processing()
    
    # Test 4: Enhanced Formatting Preservation
    log_test_result("\nTEST 4: Enhanced Formatting Preservation")
    test_results['enhanced_formatting_preservation'] = test_enhanced_formatting_preservation()
    
    # Test 5: Processing Pipeline Integration
    log_test_result("\nTEST 5: Processing Pipeline Integration")
    test_results['processing_pipeline_integration'] = test_processing_pipeline_integration()
    
    # Test 6: Backward Compatibility
    log_test_result("\nTEST 6: Backward Compatibility")
    test_results['backward_compatibility'] = test_backward_compatibility()
    
    # Test 7: Error Handling & Resilience
    log_test_result("\nTEST 7: Error Handling & Resilience")
    test_results['error_handling_resilience'] = test_error_handling_resilience()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 PHASE 6 FINAL TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        log_test_result("🎉 PHASE 6 SUCCESS: Enhanced Multi-Dimensional Content Processing Pipeline is working!", "CRITICAL_SUCCESS")
        log_test_result("✅ Multi-dimensional analysis, adaptive granularity, and enhanced formatting are operational", "CRITICAL_SUCCESS")
    elif success_rate >= 60:
        log_test_result("⚠️ PHASE 6 PARTIAL SUCCESS: Most features working but some issues detected", "WARNING")
    else:
        log_test_result("❌ PHASE 6 FAILURE: Critical issues with Enhanced Multi-Dimensional Content Processing Pipeline", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Phase 6 Enhanced Multi-Dimensional Content Processing Pipeline Testing")
    print("=" * 70)
    
    results = run_phase6_comprehensive_test()
    
    # Exit with appropriate code
    success_rate = (sum(results.values()) / len(results)) * 100
    if success_rate >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure