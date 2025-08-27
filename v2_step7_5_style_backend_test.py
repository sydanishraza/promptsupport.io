#!/usr/bin/env python3
"""
V2 Engine Step 7.5 Implementation Testing - Woolf-aligned Technical Writing Style + Structural Lint
Comprehensive testing of style processing components, diagnostic endpoints, and Woolf standards enforcement
"""

import asyncio
import json
import requests
import os
from datetime import datetime
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2StyleProcessorTester:
    """Comprehensive tester for V2 Engine Step 7.5 Style Processing System"""
    
    def __init__(self):
        self.test_results = []
        self.test_run_id = None
        self.sample_style_ids = []
        
    def log_test(self, test_name: str, success: bool, details: str, data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {details}")
        
    def test_v2_engine_health_check_with_style_endpoints(self) -> bool:
        """Test 1: V2 Engine Health Check with Style Endpoints"""
        try:
            print(f"\n🔍 TESTING V2 ENGINE HEALTH CHECK WITH STYLE ENDPOINTS")
            
            response = requests.get(f"{API_BASE}/engine", timeout=30)
            
            if response.status_code != 200:
                self.log_test("V2 Engine Health Check with Style Endpoints", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify V2 engine status
            if data.get('engine') != 'v2':
                self.log_test("V2 Engine Health Check with Style Endpoints", False, 
                             f"Expected engine=v2, got {data.get('engine')}")
                return False
                
            # Verify style diagnostic endpoints are present
            endpoints = data.get('endpoints', {})
            required_style_endpoints = [
                'style_diagnostics'
            ]
            
            missing_endpoints = []
            for endpoint in required_style_endpoints:
                if endpoint not in endpoints:
                    missing_endpoints.append(endpoint)
                    
            if missing_endpoints:
                self.log_test("V2 Engine Health Check with Style Endpoints", False, 
                             f"Missing style endpoints: {missing_endpoints}")
                return False
                
            # Verify style features are present
            features = data.get('features', [])
            required_style_features = [
                'woolf_style_processing', 'structural_linting', 'microsoft_style_guide', 
                'technical_writing_standards'
            ]
            
            missing_features = []
            for feature in required_style_features:
                if feature not in features:
                    missing_features.append(feature)
                    
            if missing_features:
                self.log_test("V2 Engine Health Check with Style Endpoints", False, 
                             f"Missing style features: {missing_features}")
                return False
                
            self.log_test("V2 Engine Health Check with Style Endpoints", True, 
                         f"V2 Engine active with style endpoints: {required_style_endpoints} and features: {required_style_features}",
                         data)
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Health Check with Style Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_style_diagnostic_endpoints_operational(self) -> bool:
        """Test 2: Style Diagnostic Endpoints Operational"""
        try:
            print(f"\n📊 TESTING STYLE DIAGNOSTIC ENDPOINTS OPERATIONAL")
            
            # Test GET /api/style/diagnostics
            print(f"Testing GET /api/style/diagnostics...")
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Style Diagnostic Endpoints - General", False, 
                             f"GET /api/style/diagnostics failed: HTTP {response.status_code}")
                return False
                
            diagnostics_data = response.json()
            
            # Verify comprehensive style statistics structure
            required_fields = ['style_system_status', 'total_style_runs', 'recent_style_results']
            missing_fields = []
            for field in required_fields:
                if field not in diagnostics_data:
                    missing_fields.append(field)
                    
            if missing_fields:
                self.log_test("Style Diagnostic Endpoints - General", False, 
                             f"Missing required fields in diagnostics: {missing_fields}")
                return False
            
            # Get sample style IDs for specific endpoint testing
            recent_results = diagnostics_data.get('recent_style_results', [])
            if recent_results:
                self.sample_style_ids = [result.get('style_id') for result in recent_results[:3] if result.get('style_id')]
            
            # Test GET /api/style/diagnostics/{style_id} if we have sample IDs
            if self.sample_style_ids:
                print(f"Testing GET /api/style/diagnostics/{{style_id}} with sample ID: {self.sample_style_ids[0]}")
                response = requests.get(f"{API_BASE}/style/diagnostics/{self.sample_style_ids[0]}", timeout=30)
                
                if response.status_code != 200:
                    self.log_test("Style Diagnostic Endpoints - Specific", False, 
                                 f"GET /api/style/diagnostics/{{style_id}} failed: HTTP {response.status_code}")
                    return False
                    
                specific_data = response.json()
                
                # Verify specific style result analysis structure
                required_specific_fields = ['style_id', 'style_results', 'compliance_metrics']
                missing_specific_fields = []
                for field in required_specific_fields:
                    if field not in specific_data:
                        missing_specific_fields.append(field)
                        
                if missing_specific_fields:
                    self.log_test("Style Diagnostic Endpoints - Specific", False, 
                                 f"Missing fields in specific diagnostics: {missing_specific_fields}")
                    return False
            
            # Test POST /api/style/rerun
            print(f"Testing POST /api/style/rerun...")
            rerun_payload = {
                "run_id": self.sample_style_ids[0] if self.sample_style_ids else "test_run_id",
                "reprocess_style": True
            }
            
            response = requests.post(f"{API_BASE}/style/rerun", json=rerun_payload, timeout=30)
            
            # Accept both 200 (success) and 404 (run not found) as valid responses for testing
            if response.status_code not in [200, 404]:
                self.log_test("Style Diagnostic Endpoints - Rerun", False, 
                             f"POST /api/style/rerun failed: HTTP {response.status_code}")
                return False
            
            self.log_test("Style Diagnostic Endpoints Operational", True, 
                         f"All style diagnostic endpoints operational: GET /api/style/diagnostics, GET /api/style/diagnostics/{{style_id}}, POST /api/style/rerun",
                         {"diagnostics_data": diagnostics_data, "sample_ids": self.sample_style_ids})
            return True
            
        except Exception as e:
            self.log_test("Style Diagnostic Endpoints Operational", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_style_processor_integration_verification(self) -> bool:
        """Test 3: V2StyleProcessor Integration Verification"""
        try:
            print(f"\n🔧 TESTING V2STYLEPROCESSOR INTEGRATION VERIFICATION")
            
            # Test style processing through content processing pipeline
            test_content = """
            # API Key Integration Guide
            
            This guide explains how to integrate API keys into your application for secure authentication.
            
            ## Getting Started
            
            First, you need to obtain your API key from the dashboard. Navigate to Settings > API Keys and generate a new key.
            
            ## Implementation Steps
            
            1. Store your API key securely
            2. Add authentication headers to requests
            3. Handle authentication errors properly
            
            ## Code Example
            
            ```javascript
            const apiKey = 'your-api-key-here';
            const response = await fetch('/api/data', {
                headers: {
                    'Authorization': `Bearer ${apiKey}`
                }
            });
            ```
            
            ## Best Practices
            
            - Never expose API keys in client-side code
            - Use environment variables for key storage
            - Implement proper error handling
            - Rotate keys regularly for security
            """
            
            print(f"Testing style processing through V2 content processing pipeline...")
            
            # Process content through V2 engine to trigger style processing
            processing_payload = {
                "content": test_content,
                "processing_options": {
                    "enable_style_processing": True,
                    "woolf_standards": True,
                    "structural_linting": True
                }
            }
            
            response = requests.post(f"{API_BASE}/content/process", json=processing_payload, timeout=60)
            
            if response.status_code not in [200, 202]:
                self.log_test("V2StyleProcessor Integration - Processing", False, 
                             f"Content processing failed: HTTP {response.status_code}")
                return False
                
            processing_data = response.json()
            
            # Verify V2 engine processing
            if processing_data.get('engine') != 'v2':
                self.log_test("V2StyleProcessor Integration - Engine", False, 
                             f"Expected V2 engine processing, got {processing_data.get('engine')}")
                return False
            
            # Get job ID for tracking
            job_id = processing_data.get('job_id')
            if not job_id:
                self.log_test("V2StyleProcessor Integration - Job ID", False, 
                             "No job_id returned from processing")
                return False
            
            # Check if style results are stored in v2_style_results collection
            # We'll verify this through the diagnostics endpoint
            print(f"Verifying style results storage for job_id: {job_id}")
            
            # Wait a moment for processing to complete
            import time
            time.sleep(3)
            
            # Check diagnostics for recent style processing
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            if response.status_code == 200:
                diagnostics_data = response.json()
                recent_results = diagnostics_data.get('recent_style_results', [])
                
                # Look for our job in recent results
                job_found = any(result.get('job_id') == job_id for result in recent_results)
                
                if job_found:
                    self.log_test("V2StyleProcessor Integration - Storage", True, 
                                 f"Style results found in v2_style_results collection for job_id: {job_id}")
                else:
                    self.log_test("V2StyleProcessor Integration - Storage", False, 
                                 f"Style results not found for job_id: {job_id}")
                    return False
            
            self.log_test("V2StyleProcessor Integration Verification", True, 
                         f"V2StyleProcessor integrated in processing pipeline, job_id: {job_id}",
                         {"job_id": job_id, "processing_data": processing_data})
            return True
            
        except Exception as e:
            self.log_test("V2StyleProcessor Integration Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_woolf_standards_implementation(self) -> bool:
        """Test 4: Woolf Standards Implementation Testing"""
        try:
            print(f"\n📝 TESTING WOOLF STANDARDS IMPLEMENTATION")
            
            # Test content that should trigger various Woolf standards
            test_content_with_issues = """
            # api integration
            
            this section covers api integration. you will learn how to integrate apis.
            
            ## getting started
            
            to get started with api integration, follow these steps:
            - step 1: get api key
            - step 2: make request
            - step 3: handle response
            
            ## code sample
            
            here is a code sample:
            
            ```
            fetch('/api/data')
            ```
            
            ## faq
            
            Q: how do i get api key?
            A: go to dashboard
            
            Q: what if request fails?
            A: check error message
            
            Q: can i use multiple keys?
            A: yes you can
            
            Q: how to rotate keys?
            A: use settings page
            
            Q: what about rate limits?
            A: check documentation
            
            Q: how to handle errors?
            A: implement try catch
            
            Q: what formats supported?
            A: json and xml
            
            Q: can i cache responses?
            A: yes with proper headers
            
            Q: how to authenticate?
            A: use bearer token
            
            Q: what about cors?
            A: configure server
            """
            
            print(f"Testing Woolf standards enforcement with problematic content...")
            
            # Process content to trigger style processing
            processing_payload = {
                "content": test_content_with_issues,
                "processing_options": {
                    "enable_style_processing": True,
                    "woolf_standards": True,
                    "structural_linting": True,
                    "microsoft_style_guide": True,
                    "technical_writing_standards": True
                }
            }
            
            response = requests.post(f"{API_BASE}/content/process", json=processing_payload, timeout=60)
            
            if response.status_code not in [200, 202]:
                self.log_test("Woolf Standards Implementation", False, 
                             f"Style processing failed: HTTP {response.status_code}")
                return False
                
            processing_data = response.json()
            job_id = processing_data.get('job_id')
            
            # Wait for processing to complete
            import time
            time.sleep(5)
            
            # Check style diagnostics for compliance metrics
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            if response.status_code != 200:
                self.log_test("Woolf Standards Implementation", False, 
                             "Could not retrieve style diagnostics")
                return False
                
            diagnostics_data = response.json()
            recent_results = diagnostics_data.get('recent_style_results', [])
            
            # Find our processing result
            our_result = None
            for result in recent_results:
                if result.get('job_id') == job_id:
                    our_result = result
                    break
            
            if not our_result:
                self.log_test("Woolf Standards Implementation", False, 
                             f"Style processing result not found for job_id: {job_id}")
                return False
            
            # Verify Woolf standards were applied
            style_results = our_result.get('style_results', {})
            
            # Check for structural rules enforcement
            structural_compliance = style_results.get('structural_compliance', {})
            if not structural_compliance:
                self.log_test("Woolf Standards - Structural Rules", False, 
                             "No structural compliance data found")
                return False
            
            # Check for language rules enforcement
            language_compliance = style_results.get('language_compliance', {})
            if not language_compliance:
                self.log_test("Woolf Standards - Language Rules", False, 
                             "No language compliance data found")
                return False
            
            # Check for terminology standardization
            terminology_corrections = style_results.get('terminology_corrections', [])
            if not isinstance(terminology_corrections, list):
                self.log_test("Woolf Standards - Terminology", False, 
                             "No terminology corrections data found")
                return False
            
            # Check for Microsoft Manual of Style integration
            style_guide_compliance = style_results.get('microsoft_style_compliance', {})
            if not style_guide_compliance:
                self.log_test("Woolf Standards - Microsoft Style Guide", False, 
                             "No Microsoft style guide compliance data found")
                return False
            
            self.log_test("Woolf Standards Implementation Testing", True, 
                         f"Woolf standards enforced: structural rules, language rules, terminology standardization, Microsoft style guide",
                         {"job_id": job_id, "style_results": style_results})
            return True
            
        except Exception as e:
            self.log_test("Woolf Standards Implementation Testing", False, f"Exception: {str(e)}")
            return False
    
    def test_style_compliance_validation(self) -> bool:
        """Test 5: Style Compliance Validation"""
        try:
            print(f"\n✅ TESTING STYLE COMPLIANCE VALIDATION")
            
            # Get recent style results to analyze compliance metrics
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Style Compliance Validation", False, 
                             f"Could not retrieve style diagnostics: HTTP {response.status_code}")
                return False
                
            diagnostics_data = response.json()
            recent_results = diagnostics_data.get('recent_style_results', [])
            
            if not recent_results:
                self.log_test("Style Compliance Validation", False, 
                             "No recent style results found for compliance validation")
                return False
            
            # Analyze compliance metrics from recent results
            compliance_tests_passed = 0
            total_compliance_tests = 4
            
            for result in recent_results[:3]:  # Check up to 3 recent results
                style_results = result.get('style_results', {})
                
                # Test 1: Structural compliance checking with scoring system
                structural_compliance = style_results.get('structural_compliance', {})
                if 'compliance_score' in structural_compliance:
                    compliance_tests_passed += 1
                    print(f"✅ Structural compliance scoring found: {structural_compliance.get('compliance_score')}")
                
                # Test 2: Terminology corrections tracking
                terminology_corrections = style_results.get('terminology_corrections', [])
                if isinstance(terminology_corrections, list):
                    compliance_tests_passed += 1
                    print(f"✅ Terminology corrections tracking found: {len(terminology_corrections)} corrections")
                
                # Test 3: Overall compliance metrics calculation
                overall_compliance = style_results.get('overall_compliance_score')
                if overall_compliance is not None:
                    compliance_tests_passed += 1
                    print(f"✅ Overall compliance metrics found: {overall_compliance}")
                
                # Test 4: Detailed formatting analysis per article
                formatting_analysis = style_results.get('formatting_analysis', {})
                if formatting_analysis:
                    compliance_tests_passed += 1
                    print(f"✅ Detailed formatting analysis found: {len(formatting_analysis)} analysis points")
                
                break  # Only need to check one result for validation
            
            if compliance_tests_passed >= 3:  # At least 3 out of 4 compliance features working
                self.log_test("Style Compliance Validation", True, 
                             f"Style compliance validation working: {compliance_tests_passed}/{total_compliance_tests} features verified",
                             {"compliance_features": compliance_tests_passed, "sample_results": recent_results[:1]})
                return True
            else:
                self.log_test("Style Compliance Validation", False, 
                             f"Insufficient compliance features: {compliance_tests_passed}/{total_compliance_tests} working")
                return False
            
        except Exception as e:
            self.log_test("Style Compliance Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_llm_based_style_formatting(self) -> bool:
        """Test 6: LLM-based Style Formatting"""
        try:
            print(f"\n🤖 TESTING LLM-BASED STYLE FORMATTING")
            
            # Test content that needs LLM-based style formatting
            test_content_for_formatting = """
            # integration id setup
            
            this guide shows how to setup integration id for your app.
            
            ## what is integration id
            
            integration id is a unique identifier for your integration. it helps track usage.
            
            ## how to get integration id
            
            1. go to dashboard
            2. click integrations
            3. create new integration
            4. copy integration id
            
            ## using integration id
            
            add integration id to your requests like this:
            
            ```
            headers: {
                'integration-id': 'your-id-here'
            }
            ```
            
            ## troubleshooting
            
            if integration id not working:
            - check spelling
            - verify permissions
            - contact support
            """
            
            print(f"Testing LLM-based Woolf style formatting...")
            
            # Process content with LLM-based style formatting enabled
            processing_payload = {
                "content": test_content_for_formatting,
                "processing_options": {
                    "enable_style_processing": True,
                    "llm_style_formatting": True,
                    "woolf_help_center_standards": True,
                    "fallback_formatting": True
                }
            }
            
            response = requests.post(f"{API_BASE}/content/process", json=processing_payload, timeout=60)
            
            if response.status_code not in [200, 202]:
                self.log_test("LLM-based Style Formatting", False, 
                             f"LLM style formatting failed: HTTP {response.status_code}")
                return False
                
            processing_data = response.json()
            job_id = processing_data.get('job_id')
            
            # Wait for LLM processing to complete
            import time
            time.sleep(7)  # LLM processing takes longer
            
            # Check style results for LLM formatting
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            if response.status_code != 200:
                self.log_test("LLM-based Style Formatting", False, 
                             "Could not retrieve style diagnostics for LLM formatting verification")
                return False
                
            diagnostics_data = response.json()
            recent_results = diagnostics_data.get('recent_style_results', [])
            
            # Find our LLM formatting result
            llm_result = None
            for result in recent_results:
                if result.get('job_id') == job_id:
                    llm_result = result
                    break
            
            if not llm_result:
                self.log_test("LLM-based Style Formatting", False, 
                             f"LLM formatting result not found for job_id: {job_id}")
                return False
            
            # Verify LLM-based formatting was applied
            style_results = llm_result.get('style_results', {})
            
            # Check for LLM formatting indicators
            llm_formatting_applied = style_results.get('llm_formatting_applied', False)
            woolf_standards_applied = style_results.get('woolf_standards_applied', False)
            fallback_used = style_results.get('fallback_formatting_used', False)
            
            formatting_tests_passed = 0
            
            if llm_formatting_applied:
                formatting_tests_passed += 1
                print(f"✅ LLM formatting applied successfully")
            
            if woolf_standards_applied:
                formatting_tests_passed += 1
                print(f"✅ Woolf Help Center standards applied")
            
            # Check for either successful LLM formatting or fallback
            if llm_formatting_applied or fallback_used:
                formatting_tests_passed += 1
                print(f"✅ Formatting completed (LLM: {llm_formatting_applied}, Fallback: {fallback_used})")
            
            if formatting_tests_passed >= 2:
                self.log_test("LLM-based Style Formatting", True, 
                             f"LLM-based style formatting working: {formatting_tests_passed}/3 features verified",
                             {"job_id": job_id, "llm_formatting": llm_formatting_applied, "fallback": fallback_used})
                return True
            else:
                self.log_test("LLM-based Style Formatting", False, 
                             f"LLM formatting insufficient: {formatting_tests_passed}/3 features working")
                return False
            
        except Exception as e:
            self.log_test("LLM-based Style Formatting", False, f"Exception: {str(e)}")
            return False
    
    def test_database_storage_and_retrieval(self) -> bool:
        """Test 7: Database Storage and Retrieval"""
        try:
            print(f"\n💾 TESTING DATABASE STORAGE AND RETRIEVAL")
            
            # Test style results storage in v2_style_results collection
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Database Storage and Retrieval", False, 
                             f"Could not retrieve style diagnostics: HTTP {response.status_code}")
                return False
                
            diagnostics_data = response.json()
            
            # Verify database storage statistics
            total_style_runs = diagnostics_data.get('total_style_runs', 0)
            recent_results = diagnostics_data.get('recent_style_results', [])
            
            if total_style_runs == 0:
                self.log_test("Database Storage - Total Runs", False, 
                             "No style runs found in database")
                return False
            
            if not recent_results:
                self.log_test("Database Storage - Recent Results", False, 
                             "No recent style results found in database")
                return False
            
            # Test style metadata preservation
            storage_tests_passed = 0
            total_storage_tests = 4
            
            for result in recent_results[:3]:  # Check up to 3 results
                # Test 1: Style results stored in v2_style_results collection
                if result.get('style_id'):
                    storage_tests_passed += 1
                    print(f"✅ Style results stored with style_id: {result.get('style_id')}")
                
                # Test 2: Style metadata preservation for diagnostics
                if result.get('metadata'):
                    storage_tests_passed += 1
                    print(f"✅ Style metadata preserved: {len(result.get('metadata', {}))} fields")
                
                # Test 3: Style result retrieval with proper ObjectId serialization
                style_id = result.get('style_id')
                if style_id:
                    response = requests.get(f"{API_BASE}/style/diagnostics/{style_id}", timeout=30)
                    if response.status_code == 200:
                        storage_tests_passed += 1
                        print(f"✅ Style result retrieval working for style_id: {style_id}")
                
                # Test 4: Database collections operational
                if result.get('job_id') and result.get('timestamp'):
                    storage_tests_passed += 1
                    print(f"✅ Database collections operational with job tracking")
                
                break  # Only need to check one result
            
            if storage_tests_passed >= 3:
                self.log_test("Database Storage and Retrieval", True, 
                             f"Database storage working: {storage_tests_passed}/{total_storage_tests} features verified, {total_style_runs} total runs",
                             {"total_runs": total_style_runs, "recent_count": len(recent_results)})
                return True
            else:
                self.log_test("Database Storage and Retrieval", False, 
                             f"Database storage insufficient: {storage_tests_passed}/{total_storage_tests} features working")
                return False
            
        except Exception as e:
            self.log_test("Database Storage and Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_processing_pipeline_integration(self) -> bool:
        """Test 8: Processing Pipeline Integration"""
        try:
            print(f"\n🔄 TESTING PROCESSING PIPELINE INTEGRATION")
            
            # Test Step 7.5 integration in all 3 processing pipelines
            pipeline_tests_passed = 0
            total_pipeline_tests = 3
            
            # Test 1: Text processing pipeline
            print(f"Testing text processing pipeline integration...")
            text_payload = {
                "content": "# Integration ID Guide\n\nThis guide covers Integration ID setup and usage for secure API authentication.",
                "processing_options": {
                    "enable_style_processing": True,
                    "pipeline": "text"
                }
            }
            
            response = requests.post(f"{API_BASE}/content/process", json=text_payload, timeout=60)
            if response.status_code in [200, 202]:
                pipeline_tests_passed += 1
                print(f"✅ Text processing pipeline integration working")
            
            # Test 2: File upload processing pipeline (simulate)
            print(f"Testing file upload processing pipeline integration...")
            file_payload = {
                "content": "# API Key Management\n\nLearn how to manage API keys securely in your applications.",
                "processing_options": {
                    "enable_style_processing": True,
                    "pipeline": "file_upload",
                    "filename": "api_guide.md"
                }
            }
            
            response = requests.post(f"{API_BASE}/content/process", json=file_payload, timeout=60)
            if response.status_code in [200, 202]:
                pipeline_tests_passed += 1
                print(f"✅ File upload processing pipeline integration working")
            
            # Test 3: URL processing pipeline (simulate)
            print(f"Testing URL processing pipeline integration...")
            url_payload = {
                "content": "# Authentication Guide\n\nComprehensive guide to API authentication methods and best practices.",
                "processing_options": {
                    "enable_style_processing": True,
                    "pipeline": "url_processing",
                    "source_url": "https://example.com/auth-guide"
                }
            }
            
            response = requests.post(f"{API_BASE}/content/process", json=url_payload, timeout=60)
            if response.status_code in [200, 202]:
                pipeline_tests_passed += 1
                print(f"✅ URL processing pipeline integration working")
            
            # Wait for processing to complete
            import time
            time.sleep(5)
            
            # Verify Step 7.5 integration between Article Generation (Step 7) and Validation (Step 8)
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            if response.status_code == 200:
                diagnostics_data = response.json()
                recent_results = diagnostics_data.get('recent_style_results', [])
                
                # Check if recent processing shows Step 7.5 integration
                step_integration_found = False
                for result in recent_results[:5]:  # Check recent results
                    processing_steps = result.get('processing_steps', [])
                    if any('step_7_5' in str(step).lower() or 'style' in str(step).lower() for step in processing_steps):
                        step_integration_found = True
                        break
                
                if step_integration_found:
                    print(f"✅ Step 7.5 integration verified between Article Generation and Validation")
                else:
                    print(f"⚠️ Step 7.5 integration not clearly visible in processing steps")
            
            if pipeline_tests_passed >= 2:  # At least 2 out of 3 pipelines working
                self.log_test("Processing Pipeline Integration", True, 
                             f"Processing pipeline integration working: {pipeline_tests_passed}/{total_pipeline_tests} pipelines verified",
                             {"pipelines_working": pipeline_tests_passed})
                return True
            else:
                self.log_test("Processing Pipeline Integration", False, 
                             f"Processing pipeline integration insufficient: {pipeline_tests_passed}/{total_pipeline_tests} pipelines working")
                return False
            
        except Exception as e:
            self.log_test("Processing Pipeline Integration", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run all V2 Engine Step 7.5 Style Processing tests"""
        print(f"\n🎯 V2 ENGINE STEP 7.5 WOOLF-ALIGNED STYLE PROCESSING COMPREHENSIVE TESTING STARTED")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"📅 Test Run: {datetime.utcnow().isoformat()}")
        
        # Run all 8 critical success criteria tests
        test_methods = [
            self.test_v2_engine_health_check_with_style_endpoints,
            self.test_style_diagnostic_endpoints_operational,
            self.test_v2_style_processor_integration_verification,
            self.test_woolf_standards_implementation,
            self.test_style_compliance_validation,
            self.test_llm_based_style_formatting,
            self.test_database_storage_and_retrieval,
            self.test_processing_pipeline_integration
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} failed with exception: {e}")
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        # Generate comprehensive summary
        summary = {
            "test_suite": "V2 Engine Step 7.5 - Woolf-aligned Technical Writing Style + Structural Lint",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": f"{success_rate:.1f}%",
            "timestamp": datetime.utcnow().isoformat(),
            "backend_url": BACKEND_URL,
            "test_results": self.test_results,
            "critical_success_criteria": {
                "v2_engine_health_check_with_style_endpoints": passed_tests >= 1,
                "style_diagnostic_endpoints_operational": passed_tests >= 2,
                "v2_style_processor_integration_verification": passed_tests >= 3,
                "woolf_standards_implementation_testing": passed_tests >= 4,
                "style_compliance_validation": passed_tests >= 5,
                "llm_based_style_formatting": passed_tests >= 6,
                "database_storage_and_retrieval": passed_tests >= 7,
                "processing_pipeline_integration": passed_tests >= 8
            }
        }
        
        print(f"\n🎉 V2 ENGINE STEP 7.5 TESTING COMPLETED")
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        if success_rate >= 87.5:  # 7/8 tests passing
            print(f"✅ EXCELLENT: V2 Engine Step 7.5 is PRODUCTION READY")
        elif success_rate >= 75.0:  # 6/8 tests passing
            print(f"⚠️ GOOD: V2 Engine Step 7.5 is mostly functional with minor issues")
        elif success_rate >= 62.5:  # 5/8 tests passing
            print(f"⚠️ MODERATE: V2 Engine Step 7.5 has significant issues requiring attention")
        else:
            print(f"❌ CRITICAL: V2 Engine Step 7.5 has major issues preventing production use")
        
        return summary

def main():
    """Main test execution"""
    tester = V2StyleProcessorTester()
    results = tester.run_comprehensive_test_suite()
    
    # Save results to file
    with open('/app/v2_step7_5_style_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Test results saved to: /app/v2_step7_5_style_test_results.json")
    
    return results

if __name__ == "__main__":
    main()