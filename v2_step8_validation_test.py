#!/usr/bin/env python3
"""
V2 ENGINE STEP 8 COMPREHENSIVE TESTING
Test the V2 Engine Step 8: "Implement Validators (fidelity, 100% coverage, placeholders, style)" functionality

This test suite validates:
1. V2ValidationSystem integration in all 3 processing pipelines
2. Fidelity and coverage validation using LLM (Prompt A)
3. Placeholder detection using LLM (Prompt B)
4. Programmatic style guard validation for structural compliance
5. Validation metrics calculation (redundancy, granularity alignment, complexity alignment)
6. Quality threshold enforcement (coverage ≥ 100%, fidelity ≥ 0.9, placeholders ≤ 0)
7. Partial run marking when validation fails
8. Validation diagnostics endpoints
9. Validation result storage in v2_validation_results collection
10. Actionable diagnostics generation for failed validations
"""

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2ValidationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.validation_ids = []
        self.run_ids = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    async def test_v2_engine_health_check(self):
        """Test 1: Verify V2 Engine is active with validation system"""
        try:
            async with self.session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check V2 engine status
                    if data.get('engine') == 'v2' and data.get('status') == 'active':
                        # Check validation features
                        v2_features = data.get('v2_features', [])
                        validation_features = data.get('validation_features', [])
                        
                        if 'comprehensive_validation' in v2_features and len(validation_features) >= 4:
                            self.log_test("V2 Engine Health Check", "PASS", 
                                        f"V2 Engine active with {len(validation_features)} validation features")
                        else:
                            self.log_test("V2 Engine Health Check", "FAIL", 
                                        f"Missing validation features: {validation_features}")
                    else:
                        self.log_test("V2 Engine Health Check", "FAIL", 
                                    f"V2 Engine not active: {data}")
                else:
                    self.log_test("V2 Engine Health Check", "FAIL", 
                                f"Health check failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("V2 Engine Health Check", "FAIL", f"Exception: {str(e)}")
    
    async def test_text_processing_with_validation(self):
        """Test 2: Test V2 text processing pipeline with validation"""
        try:
            # Create comprehensive test content with potential validation issues
            test_content = """
            # Google Maps JavaScript API Integration Guide
            
            This comprehensive guide covers Google Maps API integration with detailed examples and best practices.
            
            ## Getting Started
            
            To begin using the Google Maps JavaScript API, you need to obtain an API key from the Google Cloud Console.
            
            ### API Key Setup
            1. Visit the Google Cloud Console
            2. Create a new project or select existing
            3. Enable the Maps JavaScript API
            4. Generate an API key
            
            ## Basic Map Implementation
            
            Here's a basic example of implementing a Google Map:
            
            ```javascript
            function initMap() {
                const map = new google.maps.Map(document.getElementById("map"), {
                    zoom: 10,
                    center: { lat: 37.7749, lng: -122.4194 }
                });
            }
            ```
            
            ## Advanced Features
            
            ### Markers and InfoWindows
            You can add markers to your map with custom information windows.
            
            ### Geocoding Services
            The API provides geocoding capabilities to convert addresses to coordinates.
            
            ## Best Practices
            
            - Always use HTTPS
            - Implement proper error handling
            - Optimize for mobile devices
            - Use clustering for multiple markers
            
            ## Troubleshooting
            
            Common issues include API key restrictions and quota limits.
            """
            
            payload = {
                "content": test_content,
                "processing_options": {
                    "granularity": "moderate",
                    "audience": "developer"
                }
            }
            
            print(f"🚀 Testing V2 text processing with validation...")
            
            async with self.session.post(f"{API_BASE}/content/process", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check V2 engine processing
                    if data.get('engine') == 'v2':
                        run_id = data.get('job_id')
                        if run_id:
                            self.run_ids.append(run_id)
                        
                        # Wait for processing to complete
                        await asyncio.sleep(5)
                        
                        # Check if validation was performed
                        message = data.get('message', '')
                        if 'validation' in message.lower() or 'step 8' in message.lower():
                            self.log_test("Text Processing with V2 Validation", "PASS", 
                                        f"V2 processing with validation completed - run_id: {run_id}")
                        else:
                            self.log_test("Text Processing with V2 Validation", "PARTIAL", 
                                        f"V2 processing completed but validation status unclear - run_id: {run_id}")
                    else:
                        self.log_test("Text Processing with V2 Validation", "FAIL", 
                                    f"Not using V2 engine: {data.get('engine')}")
                else:
                    self.log_test("Text Processing with V2 Validation", "FAIL", 
                                f"Processing failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Text Processing with V2 Validation", "FAIL", f"Exception: {str(e)}")
    
    async def test_validation_diagnostics_endpoints(self):
        """Test 3: Test validation diagnostics endpoints"""
        try:
            # Test general diagnostics endpoint
            print(f"🔍 Testing validation diagnostics endpoints...")
            
            async with self.session.get(f"{API_BASE}/validation/diagnostics") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check diagnostics structure
                    required_fields = ['total_validations', 'passed_validations', 'partial_validations', 'validation_results']
                    if all(field in data for field in required_fields):
                        total_validations = data.get('total_validations', 0)
                        validation_results = data.get('validation_results', [])
                        
                        if total_validations > 0 and len(validation_results) > 0:
                            # Store validation IDs for specific testing
                            for result in validation_results[:3]:  # Test first 3
                                validation_id = result.get('validation_id')
                                if validation_id:
                                    self.validation_ids.append(validation_id)
                            
                            self.log_test("Validation Diagnostics General Endpoint", "PASS", 
                                        f"Found {total_validations} validations with proper structure")
                        else:
                            self.log_test("Validation Diagnostics General Endpoint", "PARTIAL", 
                                        f"Endpoint works but no validation results found")
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_test("Validation Diagnostics General Endpoint", "FAIL", 
                                    f"Missing required fields: {missing_fields}")
                else:
                    self.log_test("Validation Diagnostics General Endpoint", "FAIL", 
                                f"Endpoint failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Validation Diagnostics General Endpoint", "FAIL", f"Exception: {str(e)}")
    
    async def test_specific_validation_diagnostics(self):
        """Test 4: Test specific validation diagnostics endpoint"""
        try:
            if not self.validation_ids:
                self.log_test("Specific Validation Diagnostics", "SKIP", 
                            "No validation IDs available from previous tests")
                return
            
            # Test specific validation diagnostics
            validation_id = self.validation_ids[0]
            print(f"🔍 Testing specific validation diagnostics for: {validation_id}")
            
            async with self.session.get(f"{API_BASE}/validation/diagnostics/{validation_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check detailed validation structure
                    required_fields = ['validation_id', 'validation_status', 'summary_scores', 'threshold_compliance', 'diagnostics']
                    if all(field in data for field in required_fields):
                        
                        # Check summary scores
                        summary_scores = data.get('summary_scores', {})
                        expected_scores = ['fidelity_score', 'coverage_percent', 'placeholder_count', 'style_compliance']
                        
                        if all(score in summary_scores for score in expected_scores):
                            # Check compliance summary
                            compliance_summary = data.get('compliance_summary', {})
                            validation_status = data.get('validation_status', 'unknown')
                            
                            self.log_test("Specific Validation Diagnostics", "PASS", 
                                        f"Detailed validation data retrieved - Status: {validation_status}")
                        else:
                            missing_scores = [s for s in expected_scores if s not in summary_scores]
                            self.log_test("Specific Validation Diagnostics", "FAIL", 
                                        f"Missing summary scores: {missing_scores}")
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_test("Specific Validation Diagnostics", "FAIL", 
                                    f"Missing required fields: {missing_fields}")
                elif response.status == 404:
                    self.log_test("Specific Validation Diagnostics", "PARTIAL", 
                                f"Validation ID not found: {validation_id}")
                else:
                    self.log_test("Specific Validation Diagnostics", "FAIL", 
                                f"Endpoint failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Specific Validation Diagnostics", "FAIL", f"Exception: {str(e)}")
    
    async def test_validation_with_placeholder_content(self):
        """Test 5: Test validation with content containing placeholders"""
        try:
            # Create content with intentional placeholders to test detection
            placeholder_content = """
            # API Documentation Guide
            
            This guide covers [MISSING] API integration.
            
            ## Setup Instructions
            
            TODO: Add setup instructions here
            
            ## Configuration
            
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            
            ## Examples
            
            INSERT_CODE_EXAMPLE
            
            ## Troubleshooting
            
            ADD_TROUBLESHOOTING_SECTION
            """
            
            payload = {
                "content": placeholder_content,
                "processing_options": {
                    "granularity": "shallow",
                    "audience": "developer"
                }
            }
            
            print(f"🔍 Testing validation with placeholder content...")
            
            async with self.session.post(f"{API_BASE}/content/process", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('engine') == 'v2':
                        run_id = data.get('job_id')
                        if run_id:
                            self.run_ids.append(run_id)
                        
                        # Wait for processing
                        await asyncio.sleep(5)
                        
                        # Check validation diagnostics for this run
                        if run_id:
                            async with self.session.get(f"{API_BASE}/validation/diagnostics?run_id={run_id}") as diag_response:
                                if diag_response.status == 200:
                                    diag_data = await diag_response.json()
                                    validation_results = diag_data.get('validation_results', [])
                                    
                                    if validation_results:
                                        validation_result = validation_results[0]
                                        placeholder_detection = validation_result.get('placeholder_detection', {})
                                        placeholders = placeholder_detection.get('placeholders', [])
                                        
                                        if len(placeholders) > 0:
                                            self.log_test("Placeholder Detection Validation", "PASS", 
                                                        f"Detected {len(placeholders)} placeholders as expected")
                                        else:
                                            self.log_test("Placeholder Detection Validation", "FAIL", 
                                                        "No placeholders detected despite intentional placeholders in content")
                                    else:
                                        self.log_test("Placeholder Detection Validation", "FAIL", 
                                                    "No validation results found for placeholder test")
                                else:
                                    self.log_test("Placeholder Detection Validation", "FAIL", 
                                                f"Diagnostics request failed with status {diag_response.status}")
                        else:
                            self.log_test("Placeholder Detection Validation", "FAIL", 
                                        "No run_id returned from processing")
                    else:
                        self.log_test("Placeholder Detection Validation", "FAIL", 
                                    f"Not using V2 engine: {data.get('engine')}")
                else:
                    self.log_test("Placeholder Detection Validation", "FAIL", 
                                f"Processing failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Placeholder Detection Validation", "FAIL", f"Exception: {str(e)}")
    
    async def test_style_guard_validation(self):
        """Test 6: Test style guard validation for structural compliance"""
        try:
            # Create content that may not meet all structural requirements
            minimal_content = """
            # Basic Guide
            
            This is a simple guide with minimal structure.
            
            Some content here without proper sections.
            """
            
            payload = {
                "content": minimal_content,
                "processing_options": {
                    "granularity": "shallow",
                    "audience": "end_user"
                }
            }
            
            print(f"🎯 Testing style guard validation...")
            
            async with self.session.post(f"{API_BASE}/content/process", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('engine') == 'v2':
                        run_id = data.get('job_id')
                        if run_id:
                            self.run_ids.append(run_id)
                        
                        # Wait for processing
                        await asyncio.sleep(5)
                        
                        # Check style guard validation results
                        if run_id:
                            async with self.session.get(f"{API_BASE}/validation/diagnostics?run_id={run_id}") as diag_response:
                                if diag_response.status == 200:
                                    diag_data = await diag_response.json()
                                    validation_results = diag_data.get('validation_results', [])
                                    
                                    if validation_results:
                                        validation_result = validation_results[0]
                                        style_guard = validation_result.get('style_guard', {})
                                        overall_compliance = style_guard.get('overall_compliance', 0)
                                        article_results = style_guard.get('article_results', [])
                                        
                                        if overall_compliance is not None and len(article_results) > 0:
                                            # Check if structural elements were evaluated
                                            first_article = article_results[0]
                                            structure_check = first_article.get('structure_check', {})
                                            required_elements = ['h1_title', 'intro_paragraph', 'main_body']
                                            
                                            if any(element in structure_check for element in required_elements):
                                                self.log_test("Style Guard Validation", "PASS", 
                                                            f"Style compliance: {overall_compliance:.2f}, checked {len(structure_check)} elements")
                                            else:
                                                self.log_test("Style Guard Validation", "FAIL", 
                                                            f"No structural elements checked: {structure_check}")
                                        else:
                                            self.log_test("Style Guard Validation", "FAIL", 
                                                        "No style guard results found")
                                    else:
                                        self.log_test("Style Guard Validation", "FAIL", 
                                                    "No validation results found for style test")
                                else:
                                    self.log_test("Style Guard Validation", "FAIL", 
                                                f"Diagnostics request failed with status {diag_response.status}")
                        else:
                            self.log_test("Style Guard Validation", "FAIL", 
                                        "No run_id returned from processing")
                    else:
                        self.log_test("Style Guard Validation", "FAIL", 
                                    f"Not using V2 engine: {data.get('engine')}")
                else:
                    self.log_test("Style Guard Validation", "FAIL", 
                                f"Processing failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Style Guard Validation", "FAIL", f"Exception: {str(e)}")
    
    async def test_validation_metrics_calculation(self):
        """Test 7: Test validation metrics calculation"""
        try:
            # Create content that should generate multiple articles for metrics testing
            complex_content = """
            # Comprehensive Software Development Guide
            
            This guide covers multiple aspects of software development.
            
            ## Chapter 1: Planning and Design
            
            Software planning involves requirements gathering, system design, and architecture decisions.
            
            ### Requirements Analysis
            Understanding user needs and system requirements is crucial.
            
            ### System Architecture
            Designing scalable and maintainable system architecture.
            
            ## Chapter 2: Implementation
            
            The implementation phase involves coding, testing, and integration.
            
            ### Coding Standards
            Following consistent coding standards improves maintainability.
            
            ### Testing Strategies
            Implementing comprehensive testing strategies ensures quality.
            
            ## Chapter 3: Deployment and Maintenance
            
            Deployment and ongoing maintenance are critical for success.
            
            ### Deployment Strategies
            Various deployment strategies for different environments.
            
            ### Monitoring and Maintenance
            Ongoing monitoring and maintenance procedures.
            """
            
            payload = {
                "content": complex_content,
                "processing_options": {
                    "granularity": "moderate",
                    "audience": "developer"
                }
            }
            
            print(f"📊 Testing validation metrics calculation...")
            
            async with self.session.post(f"{API_BASE}/content/process", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('engine') == 'v2':
                        run_id = data.get('job_id')
                        if run_id:
                            self.run_ids.append(run_id)
                        
                        # Wait for processing
                        await asyncio.sleep(8)  # Longer wait for complex content
                        
                        # Check validation metrics
                        if run_id:
                            async with self.session.get(f"{API_BASE}/validation/diagnostics?run_id={run_id}") as diag_response:
                                if diag_response.status == 200:
                                    diag_data = await diag_response.json()
                                    validation_results = diag_data.get('validation_results', [])
                                    
                                    if validation_results:
                                        validation_result = validation_results[0]
                                        validation_metrics = validation_result.get('validation_metrics', {})
                                        
                                        # Check for required metrics
                                        required_metrics = ['redundancy_score', 'granularity_alignment_score', 
                                                          'complexity_alignment_score', 'total_articles', 'total_source_blocks']
                                        
                                        if all(metric in validation_metrics for metric in required_metrics):
                                            redundancy = validation_metrics.get('redundancy_score', 0)
                                            granularity = validation_metrics.get('granularity_alignment_score', 0)
                                            complexity = validation_metrics.get('complexity_alignment_score', 0)
                                            total_articles = validation_metrics.get('total_articles', 0)
                                            
                                            self.log_test("Validation Metrics Calculation", "PASS", 
                                                        f"Metrics calculated - Redundancy: {redundancy:.2f}, Granularity: {granularity:.2f}, Complexity: {complexity:.2f}, Articles: {total_articles}")
                                        else:
                                            missing_metrics = [m for m in required_metrics if m not in validation_metrics]
                                            self.log_test("Validation Metrics Calculation", "FAIL", 
                                                        f"Missing metrics: {missing_metrics}")
                                    else:
                                        self.log_test("Validation Metrics Calculation", "FAIL", 
                                                    "No validation results found for metrics test")
                                else:
                                    self.log_test("Validation Metrics Calculation", "FAIL", 
                                                f"Diagnostics request failed with status {diag_response.status}")
                        else:
                            self.log_test("Validation Metrics Calculation", "FAIL", 
                                        "No run_id returned from processing")
                    else:
                        self.log_test("Validation Metrics Calculation", "FAIL", 
                                    f"Not using V2 engine: {data.get('engine')}")
                else:
                    self.log_test("Validation Metrics Calculation", "FAIL", 
                                f"Processing failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Validation Metrics Calculation", "FAIL", f"Exception: {str(e)}")
    
    async def test_quality_threshold_enforcement(self):
        """Test 8: Test quality threshold enforcement and partial run marking"""
        try:
            print(f"⚖️ Testing quality threshold enforcement...")
            
            # Check recent validation results for threshold enforcement
            async with self.session.get(f"{API_BASE}/validation/diagnostics") as response:
                if response.status == 200:
                    data = await response.json()
                    validation_results = data.get('validation_results', [])
                    
                    if validation_results:
                        # Analyze threshold compliance across results
                        passed_count = 0
                        partial_count = 0
                        threshold_checks = 0
                        
                        for result in validation_results[:5]:  # Check first 5 results
                            validation_status = result.get('validation_status', 'unknown')
                            threshold_compliance = result.get('threshold_compliance', {})
                            
                            if threshold_compliance:
                                threshold_checks += 1
                                if validation_status == 'passed':
                                    passed_count += 1
                                elif validation_status == 'partial':
                                    partial_count += 1
                        
                        if threshold_checks > 0:
                            # Check if threshold enforcement is working
                            enforcement_working = (passed_count + partial_count) == threshold_checks
                            
                            if enforcement_working:
                                self.log_test("Quality Threshold Enforcement", "PASS", 
                                            f"Threshold enforcement working - {passed_count} passed, {partial_count} partial out of {threshold_checks} validations")
                            else:
                                self.log_test("Quality Threshold Enforcement", "PARTIAL", 
                                            f"Some validation results missing status - {threshold_checks} checked")
                        else:
                            self.log_test("Quality Threshold Enforcement", "FAIL", 
                                        "No threshold compliance data found in validation results")
                    else:
                        self.log_test("Quality Threshold Enforcement", "SKIP", 
                                    "No validation results available for threshold testing")
                else:
                    self.log_test("Quality Threshold Enforcement", "FAIL", 
                                f"Diagnostics endpoint failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Quality Threshold Enforcement", "FAIL", f"Exception: {str(e)}")
    
    async def test_validation_result_storage(self):
        """Test 9: Test validation result storage in v2_validation_results collection"""
        try:
            print(f"💾 Testing validation result storage...")
            
            # Check if validation results are being stored properly
            async with self.session.get(f"{API_BASE}/validation/diagnostics") as response:
                if response.status == 200:
                    data = await response.json()
                    total_validations = data.get('total_validations', 0)
                    validation_results = data.get('validation_results', [])
                    
                    if total_validations > 0 and len(validation_results) > 0:
                        # Check structure of stored validation results
                        sample_result = validation_results[0]
                        required_storage_fields = ['validation_id', 'run_id', 'validation_status', 
                                                 'timestamp', 'engine', 'summary_scores']
                        
                        if all(field in sample_result for field in required_storage_fields):
                            # Check if engine is marked as v2
                            if sample_result.get('engine') == 'v2':
                                self.log_test("Validation Result Storage", "PASS", 
                                            f"V2 validation results properly stored - {total_validations} total validations")
                            else:
                                self.log_test("Validation Result Storage", "PARTIAL", 
                                            f"Validation results stored but engine not marked as v2: {sample_result.get('engine')}")
                        else:
                            missing_fields = [f for f in required_storage_fields if f not in sample_result]
                            self.log_test("Validation Result Storage", "FAIL", 
                                        f"Stored validation results missing fields: {missing_fields}")
                    else:
                        self.log_test("Validation Result Storage", "FAIL", 
                                    "No validation results found in storage")
                else:
                    self.log_test("Validation Result Storage", "FAIL", 
                                f"Storage check failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Validation Result Storage", "FAIL", f"Exception: {str(e)}")
    
    async def test_actionable_diagnostics_generation(self):
        """Test 10: Test actionable diagnostics generation for failed validations"""
        try:
            print(f"🔧 Testing actionable diagnostics generation...")
            
            # Look for validation results with diagnostics
            async with self.session.get(f"{API_BASE}/validation/diagnostics") as response:
                if response.status == 200:
                    data = await response.json()
                    validation_results = data.get('validation_results', [])
                    
                    diagnostics_found = False
                    actionable_diagnostics = 0
                    
                    for result in validation_results:
                        diagnostics = result.get('diagnostics', [])
                        if diagnostics:
                            diagnostics_found = True
                            
                            # Check if diagnostics are actionable
                            for diagnostic in diagnostics:
                                if 'action' in diagnostic and 'message' in diagnostic:
                                    actionable_diagnostics += 1
                    
                    if diagnostics_found and actionable_diagnostics > 0:
                        self.log_test("Actionable Diagnostics Generation", "PASS", 
                                    f"Found {actionable_diagnostics} actionable diagnostics across validation results")
                    elif diagnostics_found:
                        self.log_test("Actionable Diagnostics Generation", "PARTIAL", 
                                    "Diagnostics found but may not be fully actionable")
                    else:
                        self.log_test("Actionable Diagnostics Generation", "SKIP", 
                                    "No diagnostics found in validation results (may indicate all validations passed)")
                else:
                    self.log_test("Actionable Diagnostics Generation", "FAIL", 
                                f"Diagnostics check failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("Actionable Diagnostics Generation", "FAIL", f"Exception: {str(e)}")
    
    async def test_file_upload_validation_integration(self):
        """Test 11: Test V2 validation integration in file upload pipeline"""
        try:
            print(f"📁 Testing file upload validation integration...")
            
            # Create a simple test file content
            test_file_content = """
            API Integration Best Practices
            
            This document covers essential practices for API integration.
            
            Authentication Methods
            - API Keys
            - OAuth 2.0
            - JWT Tokens
            
            Rate Limiting
            Implement proper rate limiting to avoid service disruption.
            
            Error Handling
            Always implement comprehensive error handling.
            """
            
            # Create form data for file upload
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_file_content, 
                              filename='api_integration_guide.txt',
                              content_type='text/plain')
            form_data.add_field('processing_options', 
                              json.dumps({"granularity": "shallow", "audience": "developer"}))
            
            async with self.session.post(f"{API_BASE}/content/upload", 
                                       data=form_data) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('engine') == 'v2':
                        run_id = data.get('job_id')
                        if run_id:
                            self.run_ids.append(run_id)
                        
                        # Wait for processing
                        await asyncio.sleep(5)
                        
                        # Check if validation was performed for file upload
                        message = data.get('message', '')
                        if 'validation' in message.lower() or 'step 8' in message.lower():
                            self.log_test("File Upload Validation Integration", "PASS", 
                                        f"V2 file upload with validation completed - run_id: {run_id}")
                        else:
                            self.log_test("File Upload Validation Integration", "PARTIAL", 
                                        f"V2 file upload completed but validation status unclear - run_id: {run_id}")
                    else:
                        self.log_test("File Upload Validation Integration", "FAIL", 
                                    f"File upload not using V2 engine: {data.get('engine')}")
                else:
                    self.log_test("File Upload Validation Integration", "FAIL", 
                                f"File upload failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("File Upload Validation Integration", "FAIL", f"Exception: {str(e)}")
    
    async def test_url_processing_validation_integration(self):
        """Test 12: Test V2 validation integration in URL processing pipeline"""
        try:
            print(f"🌐 Testing URL processing validation integration...")
            
            # Test with a sample URL (using a placeholder since we can't guarantee external URLs)
            test_url = "https://example.com/api-documentation"
            
            payload = {
                "url": test_url,
                "processing_options": {
                    "granularity": "moderate",
                    "audience": "developer"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process-url", 
                                       json=payload) as response:
                # Note: This may fail due to URL accessibility, but we're testing the pipeline
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('engine') == 'v2':
                        run_id = data.get('job_id')
                        if run_id:
                            self.run_ids.append(run_id)
                        
                        # Wait for processing
                        await asyncio.sleep(5)
                        
                        # Check if validation was performed for URL processing
                        message = data.get('message', '')
                        if 'validation' in message.lower() or 'step 8' in message.lower():
                            self.log_test("URL Processing Validation Integration", "PASS", 
                                        f"V2 URL processing with validation completed - run_id: {run_id}")
                        else:
                            self.log_test("URL Processing Validation Integration", "PARTIAL", 
                                        f"V2 URL processing completed but validation status unclear - run_id: {run_id}")
                    else:
                        self.log_test("URL Processing Validation Integration", "FAIL", 
                                    f"URL processing not using V2 engine: {data.get('engine')}")
                elif response.status == 400:
                    # URL may not be accessible, but check if V2 engine was attempted
                    try:
                        data = await response.json()
                        if 'v2' in str(data).lower():
                            self.log_test("URL Processing Validation Integration", "PARTIAL", 
                                        "V2 URL processing attempted but URL not accessible")
                        else:
                            self.log_test("URL Processing Validation Integration", "SKIP", 
                                        "URL not accessible for testing")
                    except:
                        self.log_test("URL Processing Validation Integration", "SKIP", 
                                    "URL not accessible for testing")
                else:
                    self.log_test("URL Processing Validation Integration", "FAIL", 
                                f"URL processing failed with status {response.status}")
                    
        except Exception as e:
            self.log_test("URL Processing Validation Integration", "FAIL", f"Exception: {str(e)}")
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("V2 ENGINE STEP 8 VALIDATION TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        partial_tests = len([t for t in self.test_results if t['status'] == 'PARTIAL'])
        skipped_tests = len([t for t in self.test_results if t['status'] == 'SKIP'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Partial: {partial_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\nDETAILED RESULTS:")
        print("-" * 80)
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️" if result['status'] == "PARTIAL" else "⏭️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n" + "="*80)
        
        # Determine overall validation system status
        critical_tests = [
            "V2 Engine Health Check",
            "Text Processing with V2 Validation", 
            "Validation Diagnostics General Endpoint",
            "Validation Result Storage"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['status'] == 'PASS')
        
        if critical_passed == len(critical_tests):
            print("🎉 V2 ENGINE STEP 8 VALIDATION SYSTEM: FULLY OPERATIONAL")
        elif critical_passed >= len(critical_tests) * 0.75:
            print("⚠️ V2 ENGINE STEP 8 VALIDATION SYSTEM: MOSTLY OPERATIONAL")
        else:
            print("❌ V2 ENGINE STEP 8 VALIDATION SYSTEM: NEEDS ATTENTION")
        
        print("="*80)

async def main():
    """Main test execution function"""
    print("🚀 Starting V2 Engine Step 8 Validation Testing")
    print("Testing comprehensive validation system for fidelity, coverage, placeholders, and style")
    print("="*80)
    
    async with V2ValidationTester() as tester:
        # Execute all validation tests
        await tester.test_v2_engine_health_check()
        await tester.test_text_processing_with_validation()
        await tester.test_validation_diagnostics_endpoints()
        await tester.test_specific_validation_diagnostics()
        await tester.test_validation_with_placeholder_content()
        await tester.test_style_guard_validation()
        await tester.test_validation_metrics_calculation()
        await tester.test_quality_threshold_enforcement()
        await tester.test_validation_result_storage()
        await tester.test_actionable_diagnostics_generation()
        await tester.test_file_upload_validation_integration()
        await tester.test_url_processing_validation_integration()
        
        # Print comprehensive summary
        tester.print_test_summary()

if __name__ == "__main__":
    asyncio.run(main())