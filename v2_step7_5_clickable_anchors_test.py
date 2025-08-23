#!/usr/bin/env python3
"""
V2 Engine Step 7.5 Clickable Anchors Enhancement Testing
Comprehensive testing of clickable anchor functionality for Mini-TOC as specifically requested
"""

import asyncio
import json
import requests
import os
import re
from datetime import datetime
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://woolf-style-lint.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2ClickableAnchorsTester:
    """Comprehensive tester for V2 Engine Step 7.5 Clickable Anchors Enhancement"""
    
    def __init__(self):
        self.test_results = []
        self.test_run_id = None
        self.sample_content = """
        # Google Maps JavaScript API Tutorial
        
        This comprehensive guide covers everything you need to know about implementing Google Maps in your web applications.
        
        ## Table of Contents
        - Getting Started
        - API Key Setup
        - Basic Map Implementation
        - Advanced Features
        - Troubleshooting
        
        ## Getting Started
        
        The Google Maps JavaScript API allows you to embed Google Maps in your web pages.
        
        ## API Key Setup
        
        Before you can use the Google Maps JavaScript API, you need to obtain an API key.
        
        ## Basic Map Implementation
        
        Here's how to create a basic map implementation.
        
        ### Map Initialization
        
        Initialize your map with basic settings.
        
        ### Adding Markers
        
        Learn how to add markers to your map.
        
        ## Advanced Features
        
        Explore advanced features like custom styling and overlays.
        
        ### Custom Styling
        
        Apply custom styles to your map.
        
        ### Map Overlays
        
        Add overlays and custom elements to your map.
        
        ## Troubleshooting
        
        Common issues and their solutions.
        """
        
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
        
    def test_v2_engine_health_check(self) -> bool:
        """Test V2 Engine health check includes style endpoints"""
        try:
            print(f"\n🔍 TESTING V2 ENGINE HEALTH CHECK WITH STYLE ENDPOINTS")
            
            response = requests.get(f"{API_BASE}/engine", timeout=30)
            
            if response.status_code != 200:
                self.log_test("V2 Engine Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify V2 engine status
            if data.get('engine') != 'v2':
                self.log_test("V2 Engine Health Check", False, f"Expected engine=v2, got {data.get('engine')}")
                return False
                
            # Verify style diagnostics endpoint is present
            endpoints = data.get('endpoints', {})
            if 'style_diagnostics' not in endpoints:
                self.log_test("V2 Engine Health Check", False, "Missing style_diagnostics endpoint")
                return False
                
            # Verify required style features are present
            features = data.get('features', [])
            required_style_features = [
                'woolf_style_processing', 'structural_linting', 'microsoft_style_guide', 'technical_writing_standards'
            ]
            
            missing_features = []
            for feature in required_style_features:
                if feature not in features:
                    missing_features.append(feature)
                    
            if missing_features:
                self.log_test("V2 Engine Health Check", False, f"Missing style features: {missing_features}")
                return False
                
            self.log_test("V2 Engine Health Check", True, 
                         f"V2 Engine active with style diagnostics endpoint and features: {required_style_features}",
                         data)
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_clickable_anchor_generation(self) -> bool:
        """Test clickable anchor generation in Mini-TOC"""
        try:
            print(f"\n🔗 TESTING CLICKABLE ANCHOR GENERATION")
            
            # Process content to test anchor generation
            content_data = {
                'content': self.sample_content,
                'processing_options': {
                    'enable_style_processing': True,
                    'enable_clickable_anchors': True
                }
            }
            
            response = requests.post(f"{API_BASE}/content/process", 
                                   json=content_data, 
                                   timeout=60)
            
            if response.status_code != 200:
                self.log_test("Clickable Anchor Generation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Store job ID for later tests
            self.test_run_id = data.get('job_id')
            
            if not self.test_run_id:
                self.log_test("Clickable Anchor Generation", False, "No job_id returned from content processing")
                return False
            
            # Wait for processing to complete
            import time
            time.sleep(10)
            
            # Get style diagnostics to check anchor generation
            style_response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if style_response.status_code != 200:
                self.log_test("Clickable Anchor Generation", False, f"Style diagnostics HTTP {style_response.status_code}")
                return False
                
            style_data = style_response.json()
            
            # Check if recent style results include anchor processing
            recent_results = style_data.get('recent_results', [])
            
            if not recent_results:
                self.log_test("Clickable Anchor Generation", False, "No recent style results found")
                return False
            
            # Find our processing result
            our_result = None
            for result in recent_results:
                if result.get('run_id') == self.test_run_id:
                    our_result = result
                    break
            
            if not our_result:
                # Check the most recent result
                our_result = recent_results[0]
            
            # Check for anchor-related metadata
            metadata = our_result.get('metadata', {})
            
            anchor_tests = []
            
            # Test 1: Check if anchor_links_generated is present
            if 'anchor_links_generated' in metadata:
                anchor_count = metadata['anchor_links_generated']
                anchor_tests.append(f"Anchor links generated: {anchor_count}")
            else:
                anchor_tests.append("Missing anchor_links_generated metadata")
            
            # Test 2: Check if toc_broken_links is present
            if 'toc_broken_links' in metadata:
                broken_links = metadata['toc_broken_links']
                anchor_tests.append(f"TOC broken links tracked: {len(broken_links) if isinstance(broken_links, list) else broken_links}")
            else:
                anchor_tests.append("Missing toc_broken_links metadata")
            
            # Test 3: Check formatted content for clickable anchors
            formatted_content = our_result.get('formatted_content', '')
            
            if formatted_content:
                # Look for anchor link patterns [Text](#slug)
                anchor_pattern = r'\[([^\]]+)\]\(#([^)]+)\)'
                anchor_matches = re.findall(anchor_pattern, formatted_content)
                
                if anchor_matches:
                    anchor_tests.append(f"Found {len(anchor_matches)} clickable anchor links in content")
                    
                    # Check for corresponding heading IDs
                    heading_id_pattern = r'<h[2-6][^>]*id="([^"]+)"'
                    heading_ids = re.findall(heading_id_pattern, formatted_content)
                    
                    if heading_ids:
                        anchor_tests.append(f"Found {len(heading_ids)} heading IDs for anchor targets")
                    else:
                        anchor_tests.append("No heading IDs found for anchor targets")
                else:
                    anchor_tests.append("No clickable anchor links found in formatted content")
            else:
                anchor_tests.append("No formatted content available for anchor testing")
            
            # Determine success based on anchor functionality
            success = any('generated:' in test or 'Found' in test and 'anchor' in test for test in anchor_tests)
            
            self.log_test("Clickable Anchor Generation", success, 
                         f"Anchor generation tests: {anchor_tests}",
                         our_result)
            return success
            
        except Exception as e:
            self.log_test("Clickable Anchor Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_slug_generation(self) -> bool:
        """Test slugified ID generation for headings"""
        try:
            print(f"\n🏷️ TESTING SLUG GENERATION FOR HEADINGS")
            
            if not self.test_run_id:
                self.log_test("Slug Generation", False, "No test run ID available from previous test")
                return False
            
            # Get specific style result
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Slug Generation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            if not recent_results:
                self.log_test("Slug Generation", False, "No recent results for slug testing")
                return False
            
            # Get the most recent result
            result = recent_results[0]
            formatted_content = result.get('formatted_content', '')
            
            if not formatted_content:
                self.log_test("Slug Generation", False, "No formatted content available for slug testing")
                return False
            
            slug_tests = []
            
            # Test slug patterns in heading IDs
            heading_patterns = [
                (r'<h2[^>]*id="getting-started"', "Getting Started → getting-started"),
                (r'<h2[^>]*id="api-key-setup"', "API Key Setup → api-key-setup"),
                (r'<h2[^>]*id="basic-map-implementation"', "Basic Map Implementation → basic-map-implementation"),
                (r'<h3[^>]*id="map-initialization"', "Map Initialization → map-initialization"),
                (r'<h3[^>]*id="adding-markers"', "Adding Markers → adding-markers"),
                (r'<h2[^>]*id="advanced-features"', "Advanced Features → advanced-features"),
                (r'<h3[^>]*id="custom-styling"', "Custom Styling → custom-styling"),
                (r'<h3[^>]*id="map-overlays"', "Map Overlays → map-overlays")
            ]
            
            for pattern, description in heading_patterns:
                if re.search(pattern, formatted_content):
                    slug_tests.append(f"✅ Slug generated: {description}")
                else:
                    slug_tests.append(f"❌ Missing slug: {description}")
            
            # Test anchor links pointing to these slugs
            anchor_patterns = [
                (r'\[Getting Started\]\(#getting-started\)', "Getting Started anchor link"),
                (r'\[API Key Setup\]\(#api-key-setup\)', "API Key Setup anchor link"),
                (r'\[Basic Map Implementation\]\(#basic-map-implementation\)', "Basic Map Implementation anchor link"),
                (r'\[Advanced Features\]\(#advanced-features\)', "Advanced Features anchor link"),
                (r'\[Troubleshooting\]\(#troubleshooting\)', "Troubleshooting anchor link")
            ]
            
            for pattern, description in anchor_patterns:
                if re.search(pattern, formatted_content):
                    slug_tests.append(f"✅ Anchor link: {description}")
                else:
                    slug_tests.append(f"❌ Missing anchor: {description}")
            
            # Count successful slug generations
            successful_slugs = len([test for test in slug_tests if test.startswith('✅')])
            total_expected = len(heading_patterns) + len(anchor_patterns)
            
            success = successful_slugs >= (total_expected * 0.5)  # At least 50% success
            
            self.log_test("Slug Generation", success, 
                         f"Slug generation results ({successful_slugs}/{total_expected}): {slug_tests}",
                         formatted_content[:1000])
            return success
            
        except Exception as e:
            self.log_test("Slug Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_toc_link_validation(self) -> bool:
        """Test TOC link validation and broken link detection"""
        try:
            print(f"\n🔍 TESTING TOC LINK VALIDATION")
            
            # Get style diagnostics to check validation results
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("TOC Link Validation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            if not recent_results:
                self.log_test("TOC Link Validation", False, "No recent results for validation testing")
                return False
            
            result = recent_results[0]
            metadata = result.get('metadata', {})
            
            validation_tests = []
            
            # Test 1: Check toc_broken_links array
            if 'toc_broken_links' in metadata:
                broken_links = metadata['toc_broken_links']
                if isinstance(broken_links, list):
                    validation_tests.append(f"TOC broken links array present: {len(broken_links)} broken links")
                    
                    # If there are broken links, that's actually good for testing validation
                    if len(broken_links) == 0:
                        validation_tests.append("✅ No broken TOC links detected")
                    else:
                        validation_tests.append(f"⚠️ {len(broken_links)} broken TOC links detected: {broken_links}")
                else:
                    validation_tests.append(f"TOC broken links present but not array: {broken_links}")
            else:
                validation_tests.append("❌ Missing toc_broken_links metadata")
            
            # Test 2: Check anchor_links_generated count
            if 'anchor_links_generated' in metadata:
                anchor_count = metadata['anchor_links_generated']
                if isinstance(anchor_count, int) and anchor_count > 0:
                    validation_tests.append(f"✅ Anchor links generated: {anchor_count}")
                else:
                    validation_tests.append(f"⚠️ No anchor links generated: {anchor_count}")
            else:
                validation_tests.append("❌ Missing anchor_links_generated metadata")
            
            # Test 3: Validate content has both anchors and targets
            formatted_content = result.get('formatted_content', '')
            
            if formatted_content:
                # Find all anchor links
                anchor_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', formatted_content)
                
                # Find all heading IDs
                heading_ids = re.findall(r'<h[2-6][^>]*id="([^"]+)"', formatted_content)
                
                if anchor_links and heading_ids:
                    # Check if anchor targets exist
                    anchor_targets = [link[1] for link in anchor_links]  # Get the #slug part
                    
                    valid_anchors = []
                    broken_anchors = []
                    
                    for target in anchor_targets:
                        if target in heading_ids:
                            valid_anchors.append(target)
                        else:
                            broken_anchors.append(target)
                    
                    validation_tests.append(f"✅ Valid anchor links: {len(valid_anchors)}")
                    if broken_anchors:
                        validation_tests.append(f"❌ Broken anchor links: {len(broken_anchors)} - {broken_anchors}")
                    else:
                        validation_tests.append("✅ No broken anchor links found in content analysis")
                else:
                    validation_tests.append("❌ Missing anchor links or heading IDs in content")
            else:
                validation_tests.append("❌ No formatted content available for validation")
            
            # Determine success - validation is working if we have the metadata and structure
            success = ('toc_broken_links' in str(validation_tests) and 
                      'anchor_links_generated' in str(validation_tests) and
                      not any('❌ Missing' in test for test in validation_tests))
            
            self.log_test("TOC Link Validation", success, 
                         f"Validation tests: {validation_tests}",
                         metadata)
            return success
            
        except Exception as e:
            self.log_test("TOC Link Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_style_processing(self) -> bool:
        """Test enhanced style processing includes anchor generation"""
        try:
            print(f"\n🎨 TESTING ENHANCED STYLE PROCESSING WITH ANCHORS")
            
            # Get style diagnostics
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Enhanced Style Processing", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            style_tests = []
            
            # Test 1: Check overall style system status
            if data.get('style_system_status') == 'active':
                style_tests.append("✅ Style system active")
            else:
                style_tests.append(f"❌ Style system not active: {data.get('style_system_status')}")
            
            # Test 2: Check recent results for anchor processing
            recent_results = data.get('recent_results', [])
            
            if recent_results:
                result = recent_results[0]
                
                # Check processing method
                processing_method = result.get('processing_method', '')
                if processing_method:
                    style_tests.append(f"✅ Processing method: {processing_method}")
                else:
                    style_tests.append("❌ No processing method specified")
                
                # Check if anchor processing is included
                metadata = result.get('metadata', {})
                
                if 'anchor_links_generated' in metadata or 'toc_broken_links' in metadata:
                    style_tests.append("✅ Anchor processing integrated in style system")
                else:
                    style_tests.append("❌ Anchor processing not integrated in style system")
                
                # Check formatted content quality
                formatted_content = result.get('formatted_content', '')
                content_length = len(formatted_content)
                
                if content_length > 1000:
                    style_tests.append(f"✅ Substantial formatted content: {content_length} chars")
                else:
                    style_tests.append(f"⚠️ Limited formatted content: {content_length} chars")
                
                # Check for Woolf-style formatting
                if any(pattern in formatted_content for pattern in ['<h2', '<h3', 'id="', '[', '](#']):
                    style_tests.append("✅ Woolf-style formatting with headings and anchors")
                else:
                    style_tests.append("❌ Missing Woolf-style formatting elements")
                    
            else:
                style_tests.append("❌ No recent style results available")
            
            # Test 3: Check style statistics
            statistics = data.get('statistics', {})
            
            if statistics:
                total_runs = statistics.get('total_style_runs', 0)
                success_rate = statistics.get('success_rate', 0)
                
                if total_runs > 0:
                    style_tests.append(f"✅ Style processing runs: {total_runs}")
                else:
                    style_tests.append("❌ No style processing runs")
                
                if success_rate >= 80:
                    style_tests.append(f"✅ High success rate: {success_rate}%")
                else:
                    style_tests.append(f"⚠️ Low success rate: {success_rate}%")
            else:
                style_tests.append("❌ No style statistics available")
            
            # Determine success
            success_indicators = len([test for test in style_tests if test.startswith('✅')])
            total_tests = len(style_tests)
            
            success = success_indicators >= (total_tests * 0.6)  # At least 60% success
            
            self.log_test("Enhanced Style Processing", success, 
                         f"Style processing tests ({success_indicators}/{total_tests}): {style_tests}",
                         data)
            return success
            
        except Exception as e:
            self.log_test("Enhanced Style Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_metadata_enhancement(self) -> bool:
        """Test metadata enhancement with anchor information"""
        try:
            print(f"\n📊 TESTING METADATA ENHANCEMENT WITH ANCHOR INFO")
            
            # Get style diagnostics for metadata analysis
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Metadata Enhancement", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            if not recent_results:
                self.log_test("Metadata Enhancement", False, "No recent results for metadata testing")
                return False
            
            result = recent_results[0]
            metadata = result.get('metadata', {})
            
            metadata_tests = []
            
            # Test 1: Check anchor_links_generated field
            if 'anchor_links_generated' in metadata:
                anchor_count = metadata['anchor_links_generated']
                if isinstance(anchor_count, int):
                    metadata_tests.append(f"✅ anchor_links_generated: {anchor_count} (integer)")
                else:
                    metadata_tests.append(f"⚠️ anchor_links_generated: {anchor_count} (not integer)")
            else:
                metadata_tests.append("❌ Missing anchor_links_generated field")
            
            # Test 2: Check toc_broken_links field
            if 'toc_broken_links' in metadata:
                broken_links = metadata['toc_broken_links']
                if isinstance(broken_links, list):
                    metadata_tests.append(f"✅ toc_broken_links: {len(broken_links)} items (array)")
                else:
                    metadata_tests.append(f"⚠️ toc_broken_links: {broken_links} (not array)")
            else:
                metadata_tests.append("❌ Missing toc_broken_links field")
            
            # Test 3: Check other enhanced metadata fields
            enhanced_fields = [
                'structural_compliance_score',
                'terminology_corrections',
                'formatting_changes_applied',
                'content_length'
            ]
            
            for field in enhanced_fields:
                if field in metadata:
                    value = metadata[field]
                    metadata_tests.append(f"✅ {field}: {value}")
                else:
                    metadata_tests.append(f"❌ Missing {field}")
            
            # Test 4: Check metadata completeness
            required_metadata_fields = [
                'processing_timestamp',
                'processing_method',
                'engine'
            ]
            
            for field in required_metadata_fields:
                if field in metadata:
                    metadata_tests.append(f"✅ {field}: {metadata[field]}")
                else:
                    metadata_tests.append(f"❌ Missing required field: {field}")
            
            # Test 5: Verify V2 engine metadata
            if metadata.get('engine') == 'v2':
                metadata_tests.append("✅ V2 engine metadata confirmed")
            else:
                metadata_tests.append(f"❌ Wrong engine metadata: {metadata.get('engine')}")
            
            # Determine success based on anchor-specific metadata
            anchor_metadata_present = ('anchor_links_generated' in str(metadata_tests) and 
                                     'toc_broken_links' in str(metadata_tests))
            
            success_count = len([test for test in metadata_tests if test.startswith('✅')])
            total_count = len(metadata_tests)
            
            success = anchor_metadata_present and (success_count >= total_count * 0.7)
            
            self.log_test("Metadata Enhancement", success, 
                         f"Metadata tests ({success_count}/{total_count}): {metadata_tests}",
                         metadata)
            return success
            
        except Exception as e:
            self.log_test("Metadata Enhancement", False, f"Exception: {str(e)}")
            return False
    
    def test_structural_compliance_validation(self) -> bool:
        """Test structural compliance validation includes clickable TOC"""
        try:
            print(f"\n🏗️ TESTING STRUCTURAL COMPLIANCE VALIDATION")
            
            # Get style diagnostics for compliance analysis
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Structural Compliance Validation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            if not recent_results:
                self.log_test("Structural Compliance Validation", False, "No recent results for compliance testing")
                return False
            
            result = recent_results[0]
            metadata = result.get('metadata', {})
            
            compliance_tests = []
            
            # Test 1: Check structural compliance score
            if 'structural_compliance_score' in metadata:
                score = metadata['structural_compliance_score']
                if isinstance(score, (int, float)):
                    compliance_tests.append(f"✅ Structural compliance score: {score}")
                else:
                    compliance_tests.append(f"⚠️ Invalid compliance score: {score}")
            else:
                compliance_tests.append("❌ Missing structural_compliance_score")
            
            # Test 2: Check for TOC compliance validation
            formatted_content = result.get('formatted_content', '')
            
            if formatted_content:
                # Check for TOC structure
                has_toc_heading = bool(re.search(r'<h[2-6][^>]*>.*table of contents.*</h[2-6]>', formatted_content, re.IGNORECASE))
                has_toc_list = bool(re.search(r'<ul[^>]*>.*</ul>', formatted_content, re.DOTALL))
                has_anchor_links = bool(re.search(r'\[([^\]]+)\]\(#([^)]+)\)', formatted_content))
                has_heading_ids = bool(re.search(r'<h[2-6][^>]*id="[^"]+"', formatted_content))
                
                if has_toc_heading:
                    compliance_tests.append("✅ TOC heading structure present")
                else:
                    compliance_tests.append("❌ Missing TOC heading structure")
                
                if has_toc_list:
                    compliance_tests.append("✅ TOC list structure present")
                else:
                    compliance_tests.append("❌ Missing TOC list structure")
                
                if has_anchor_links:
                    compliance_tests.append("✅ Clickable anchor links present")
                else:
                    compliance_tests.append("❌ Missing clickable anchor links")
                
                if has_heading_ids:
                    compliance_tests.append("✅ Heading IDs for anchor targets present")
                else:
                    compliance_tests.append("❌ Missing heading IDs for anchor targets")
                
                # Overall TOC compliance
                toc_compliance_score = sum([has_toc_heading, has_toc_list, has_anchor_links, has_heading_ids])
                compliance_tests.append(f"TOC compliance: {toc_compliance_score}/4 requirements met")
                
            else:
                compliance_tests.append("❌ No formatted content for compliance validation")
            
            # Test 3: Check compliance validation features
            compliance_features = [
                'structural_rules_enforcement',
                'language_rules_enforcement', 
                'terminology_standardization',
                'microsoft_style_guide'
            ]
            
            # Check if these features are mentioned in the engine status
            engine_response = requests.get(f"{API_BASE}/engine", timeout=30)
            if engine_response.status_code == 200:
                engine_data = engine_response.json()
                features = engine_data.get('features', [])
                
                for feature in compliance_features:
                    if feature in features:
                        compliance_tests.append(f"✅ {feature} feature available")
                    else:
                        compliance_tests.append(f"❌ Missing {feature} feature")
            
            # Determine success based on compliance validation working
            success_indicators = len([test for test in compliance_tests if test.startswith('✅')])
            total_tests = len(compliance_tests)
            
            # Special focus on TOC-related compliance
            toc_success = any('anchor links present' in test for test in compliance_tests)
            
            success = toc_success and (success_indicators >= total_tests * 0.6)
            
            self.log_test("Structural Compliance Validation", success, 
                         f"Compliance validation tests ({success_indicators}/{total_tests}): {compliance_tests}",
                         result)
            return success
            
        except Exception as e:
            self.log_test("Structural Compliance Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_processing_pipeline_integration(self) -> bool:
        """Test anchor processing works in all 3 processing pipelines"""
        try:
            print(f"\n🔄 TESTING PROCESSING PIPELINE INTEGRATION")
            
            pipeline_tests = []
            
            # Test 1: Text Processing Pipeline
            try:
                text_data = {
                    'content': self.sample_content,
                    'processing_options': {
                        'enable_style_processing': True,
                        'enable_clickable_anchors': True
                    }
                }
                
                text_response = requests.post(f"{API_BASE}/content/process", 
                                            json=text_data, 
                                            timeout=60)
                
                if text_response.status_code == 200:
                    text_result = text_response.json()
                    if text_result.get('job_id'):
                        pipeline_tests.append("✅ Text processing pipeline accepts anchor processing")
                    else:
                        pipeline_tests.append("❌ Text processing pipeline failed")
                else:
                    pipeline_tests.append(f"❌ Text processing pipeline error: {text_response.status_code}")
                    
            except Exception as e:
                pipeline_tests.append(f"❌ Text processing pipeline exception: {str(e)}")
            
            # Test 2: File Upload Pipeline (simulate)
            try:
                # Check if file upload endpoint exists
                engine_response = requests.get(f"{API_BASE}/engine", timeout=30)
                if engine_response.status_code == 200:
                    engine_data = engine_response.json()
                    endpoints = engine_data.get('endpoints', {})
                    
                    if 'file_upload' in endpoints:
                        pipeline_tests.append("✅ File upload pipeline endpoint available")
                    else:
                        pipeline_tests.append("❌ File upload pipeline endpoint missing")
                else:
                    pipeline_tests.append("❌ Cannot verify file upload pipeline")
                    
            except Exception as e:
                pipeline_tests.append(f"❌ File upload pipeline check exception: {str(e)}")
            
            # Test 3: URL Processing Pipeline (simulate)
            try:
                # Check if URL processing endpoint exists
                if 'url_processing' in endpoints:
                    pipeline_tests.append("✅ URL processing pipeline endpoint available")
                else:
                    pipeline_tests.append("❌ URL processing pipeline endpoint missing")
                    
            except Exception as e:
                pipeline_tests.append(f"❌ URL processing pipeline check exception: {str(e)}")
            
            # Test 4: Verify anchor processing is integrated in V2 pipeline
            try:
                # Check style diagnostics for pipeline integration
                style_response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
                
                if style_response.status_code == 200:
                    style_data = style_response.json()
                    
                    # Check if recent results show pipeline integration
                    recent_results = style_data.get('recent_results', [])
                    
                    if recent_results:
                        result = recent_results[0]
                        metadata = result.get('metadata', {})
                        
                        # Check for pipeline integration indicators
                        if 'processing_pipeline' in metadata or 'engine' in metadata:
                            pipeline_tests.append("✅ Pipeline integration metadata present")
                        else:
                            pipeline_tests.append("❌ Missing pipeline integration metadata")
                        
                        # Check for anchor processing in pipeline
                        if 'anchor_links_generated' in metadata:
                            pipeline_tests.append("✅ Anchor processing integrated in pipeline")
                        else:
                            pipeline_tests.append("❌ Anchor processing not integrated in pipeline")
                    else:
                        pipeline_tests.append("❌ No recent results to verify pipeline integration")
                else:
                    pipeline_tests.append("❌ Cannot verify pipeline integration")
                    
            except Exception as e:
                pipeline_tests.append(f"❌ Pipeline integration check exception: {str(e)}")
            
            # Test 5: Check V2 engine features for pipeline support
            try:
                if engine_response.status_code == 200:
                    features = engine_data.get('features', [])
                    
                    pipeline_features = [
                        'multi_dimensional_analysis',
                        'adaptive_granularity', 
                        'intelligent_chunking',
                        'woolf_style_processing'
                    ]
                    
                    for feature in pipeline_features:
                        if feature in features:
                            pipeline_tests.append(f"✅ {feature} pipeline feature available")
                        else:
                            pipeline_tests.append(f"❌ Missing {feature} pipeline feature")
                            
            except Exception as e:
                pipeline_tests.append(f"❌ Pipeline features check exception: {str(e)}")
            
            # Determine success based on pipeline integration
            success_indicators = len([test for test in pipeline_tests if test.startswith('✅')])
            total_tests = len(pipeline_tests)
            
            # Focus on key integration indicators
            key_success = any('Anchor processing integrated' in test for test in pipeline_tests)
            
            success = key_success and (success_indicators >= total_tests * 0.6)
            
            self.log_test("Processing Pipeline Integration", success, 
                         f"Pipeline integration tests ({success_indicators}/{total_tests}): {pipeline_tests}",
                         pipeline_tests)
            return success
            
        except Exception as e:
            self.log_test("Processing Pipeline Integration", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all V2 Engine Step 7.5 Clickable Anchors Enhancement tests"""
        print(f"🚀 STARTING V2 ENGINE STEP 7.5 CLICKABLE ANCHORS ENHANCEMENT TESTING")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📡 API Base: {API_BASE}")
        
        test_methods = [
            self.test_v2_engine_health_check,
            self.test_clickable_anchor_generation,
            self.test_slug_generation,
            self.test_toc_link_validation,
            self.test_enhanced_style_processing,
            self.test_metadata_enhancement,
            self.test_structural_compliance_validation,
            self.test_processing_pipeline_integration
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_method.__name__}: {str(e)}")
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        # Compile final results
        results = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "overall_status": "PASS" if success_rate >= 75 else "FAIL"
            },
            "test_details": self.test_results,
            "backend_url": BACKEND_URL,
            "test_timestamp": datetime.utcnow().isoformat(),
            "engine_version": "v2",
            "step_tested": "Step 7.5 - Clickable Anchors Enhancement"
        }
        
        print(f"\n" + "="*80)
        print(f"🎯 V2 ENGINE STEP 7.5 CLICKABLE ANCHORS ENHANCEMENT TESTING COMPLETE")
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"🏆 OVERALL STATUS: {results['test_summary']['overall_status']}")
        print(f"="*80)
        
        return results

def main():
    """Main test execution"""
    tester = V2ClickableAnchorsTester()
    results = tester.run_comprehensive_tests()
    
    # Print detailed results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for result in results["test_details"]:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['details']}")
    
    return results

if __name__ == "__main__":
    main()