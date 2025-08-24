#!/usr/bin/env python3
"""
V2 Engine Step 7.5 Clickable Anchors Enhancement - Focused Testing
Testing based on actual API structure and recent style results
"""

import json
import requests
import os
import re
from datetime import datetime
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2ClickableAnchorsFocusedTester:
    """Focused tester for V2 Engine Step 7.5 Clickable Anchors Enhancement"""
    
    def __init__(self):
        self.test_results = []
        
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
        
    def test_clickable_anchor_generation_verification(self) -> bool:
        """Test clickable anchor generation using actual recent results"""
        try:
            print(f"\n🔗 TESTING CLICKABLE ANCHOR GENERATION VERIFICATION")
            
            # Get style diagnostics
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Clickable Anchor Generation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_style_results', [])
            
            if not recent_results:
                self.log_test("Clickable Anchor Generation", False, "No recent style results found")
                return False
            
            # Get the most recent result for detailed analysis
            latest_result = recent_results[0]
            style_id = latest_result.get('style_id')
            
            if not style_id:
                self.log_test("Clickable Anchor Generation", False, "No style_id found in recent results")
                return False
            
            # Get detailed style result
            detail_response = requests.get(f"{API_BASE}/style/diagnostics/{style_id}", timeout=30)
            
            if detail_response.status_code != 200:
                self.log_test("Clickable Anchor Generation", False, f"Detail HTTP {detail_response.status_code}")
                return False
                
            detail_data = detail_response.json()
            style_result = detail_data.get('style_result', {})
            style_results = style_result.get('style_results', [])
            
            if not style_results:
                self.log_test("Clickable Anchor Generation", False, "No style results in detailed response")
                return False
            
            # Analyze the first article result
            article_result = style_results[0]
            formatted_content = article_result.get('formatted_content', '')
            style_metadata = article_result.get('style_metadata', {})
            
            anchor_tests = []
            
            # Test 1: Check for clickable anchor links in TOC
            toc_anchor_pattern = r'-\s*\[([^\]]+)\]\(#([^)]+)\)'
            toc_anchors = re.findall(toc_anchor_pattern, formatted_content)
            
            if toc_anchors:
                anchor_tests.append(f"✅ Found {len(toc_anchors)} TOC anchor links: {[anchor[0] for anchor in toc_anchors]}")
            else:
                anchor_tests.append("❌ No TOC anchor links found")
            
            # Test 2: Check for heading IDs that match anchor targets
            heading_id_pattern = r"<h[2-6][^>]*id=['\"]([^'\"]+)['\"]"
            heading_ids = re.findall(heading_id_pattern, formatted_content)
            
            if heading_ids:
                anchor_tests.append(f"✅ Found {len(heading_ids)} heading IDs: {heading_ids}")
            else:
                anchor_tests.append("❌ No heading IDs found")
            
            # Test 3: Check anchor_links_generated metadata
            anchor_links_generated = style_metadata.get('anchor_links_generated', 0)
            anchor_tests.append(f"Anchor links generated metadata: {anchor_links_generated}")
            
            # Test 4: Check toc_broken_links metadata
            toc_broken_links = style_metadata.get('toc_broken_links', [])
            if isinstance(toc_broken_links, list):
                anchor_tests.append(f"✅ TOC broken links tracked: {len(toc_broken_links)} broken links")
                if toc_broken_links:
                    # Show details of broken links
                    broken_details = [f"{link.get('toc_text', 'unknown')} -> {link.get('expected_slug', 'unknown')}" for link in toc_broken_links]
                    anchor_tests.append(f"Broken link details: {broken_details}")
            else:
                anchor_tests.append(f"❌ TOC broken links not properly tracked: {toc_broken_links}")
            
            # Test 5: Validate anchor link resolution
            if toc_anchors and heading_ids:
                anchor_targets = [anchor[1] for anchor in toc_anchors]  # Get slug parts
                
                resolved_anchors = []
                unresolved_anchors = []
                
                for target in anchor_targets:
                    if target in heading_ids:
                        resolved_anchors.append(target)
                    else:
                        unresolved_anchors.append(target)
                
                if resolved_anchors:
                    anchor_tests.append(f"✅ Resolved anchor links: {len(resolved_anchors)} - {resolved_anchors}")
                
                if unresolved_anchors:
                    anchor_tests.append(f"❌ Unresolved anchor links: {len(unresolved_anchors)} - {unresolved_anchors}")
                else:
                    anchor_tests.append("✅ All anchor links properly resolved")
            
            # Test 6: Check slug generation quality
            if heading_ids:
                slug_quality_tests = []
                for heading_id in heading_ids:
                    # Check if slug follows proper format (lowercase, hyphenated)
                    if re.match(r'^[a-z0-9-]+$', heading_id):
                        slug_quality_tests.append(f"✅ Good slug: {heading_id}")
                    else:
                        slug_quality_tests.append(f"⚠️ Poor slug format: {heading_id}")
                
                anchor_tests.extend(slug_quality_tests)
            
            # Determine overall success
            success_indicators = len([test for test in anchor_tests if test.startswith('✅')])
            total_tests = len(anchor_tests)
            
            # Key success criteria
            has_toc_anchors = len(toc_anchors) > 0
            has_heading_ids = len(heading_ids) > 0
            has_broken_link_tracking = isinstance(toc_broken_links, list)
            
            success = has_toc_anchors and has_heading_ids and has_broken_link_tracking
            
            self.log_test("Clickable Anchor Generation", success, 
                         f"Anchor generation analysis ({success_indicators}/{total_tests} success indicators): {anchor_tests}",
                         {
                             'toc_anchors': toc_anchors,
                             'heading_ids': heading_ids,
                             'broken_links': toc_broken_links,
                             'formatted_content_length': len(formatted_content)
                         })
            return success
            
        except Exception as e:
            self.log_test("Clickable Anchor Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_slug_generation_patterns(self) -> bool:
        """Test slug generation patterns and quality"""
        try:
            print(f"\n🏷️ TESTING SLUG GENERATION PATTERNS")
            
            # Get recent style result
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Slug Generation Patterns", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_style_results', [])
            
            if not recent_results:
                self.log_test("Slug Generation Patterns", False, "No recent results")
                return False
            
            # Get detailed result
            style_id = recent_results[0].get('style_id')
            detail_response = requests.get(f"{API_BASE}/style/diagnostics/{style_id}", timeout=30)
            
            if detail_response.status_code != 200:
                self.log_test("Slug Generation Patterns", False, f"Detail HTTP {detail_response.status_code}")
                return False
                
            detail_data = detail_response.json()
            style_results = detail_data.get('style_result', {}).get('style_results', [])
            
            if not style_results:
                self.log_test("Slug Generation Patterns", False, "No style results")
                return False
            
            formatted_content = style_results[0].get('formatted_content', '')
            
            slug_tests = []
            
            # Test slug patterns
            heading_id_pattern = r"<h[2-6][^>]*id=['\"]([^'\"]+)['\"]"
            heading_ids = re.findall(heading_id_pattern, formatted_content)
            
            if heading_ids:
                for heading_id in heading_ids:
                    # Test slug format
                    if re.match(r'^[a-z0-9-]+$', heading_id):
                        slug_tests.append(f"✅ Valid slug format: '{heading_id}'")
                    else:
                        slug_tests.append(f"❌ Invalid slug format: '{heading_id}'")
                    
                    # Test slug characteristics
                    if '-' in heading_id:
                        slug_tests.append(f"✅ Hyphenated slug: '{heading_id}'")
                    
                    if heading_id.islower():
                        slug_tests.append(f"✅ Lowercase slug: '{heading_id}'")
                    else:
                        slug_tests.append(f"❌ Not lowercase: '{heading_id}'")
            else:
                slug_tests.append("❌ No heading IDs found for slug testing")
            
            # Test common slug transformations
            expected_transformations = [
                ("Getting Started", "getting-started"),
                ("API Key Setup", "api-key-setup"),
                ("Map Initialization", "map-initialization"),
                ("Adding Markers", "adding-markers"),
                ("Best Practices", "best-practices")
            ]
            
            for original, expected_slug in expected_transformations:
                if expected_slug in heading_ids:
                    slug_tests.append(f"✅ Correct transformation: '{original}' → '{expected_slug}'")
                else:
                    slug_tests.append(f"❌ Missing transformation: '{original}' → '{expected_slug}'")
            
            # Determine success
            valid_slugs = len([test for test in slug_tests if 'Valid slug format' in test and test.startswith('✅')])
            total_slugs = len([test for test in slug_tests if 'slug format' in test])
            
            success = valid_slugs > 0 and (valid_slugs >= total_slugs * 0.8 if total_slugs > 0 else False)
            
            self.log_test("Slug Generation Patterns", success, 
                         f"Slug pattern tests ({valid_slugs}/{total_slugs} valid): {slug_tests}",
                         heading_ids)
            return success
            
        except Exception as e:
            self.log_test("Slug Generation Patterns", False, f"Exception: {str(e)}")
            return False
    
    def test_toc_link_validation_system(self) -> bool:
        """Test TOC link validation and broken link detection system"""
        try:
            print(f"\n🔍 TESTING TOC LINK VALIDATION SYSTEM")
            
            # Get recent style result
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("TOC Link Validation", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_style_results', [])
            
            if not recent_results:
                self.log_test("TOC Link Validation", False, "No recent results")
                return False
            
            # Get detailed result
            style_id = recent_results[0].get('style_id')
            detail_response = requests.get(f"{API_BASE}/style/diagnostics/{style_id}", timeout=30)
            
            if detail_response.status_code != 200:
                self.log_test("TOC Link Validation", False, f"Detail HTTP {detail_response.status_code}")
                return False
                
            detail_data = detail_response.json()
            style_results = detail_data.get('style_result', {}).get('style_results', [])
            
            if not style_results:
                self.log_test("TOC Link Validation", False, "No style results")
                return False
            
            article_result = style_results[0]
            style_metadata = article_result.get('style_metadata', {})
            
            validation_tests = []
            
            # Test 1: Check toc_broken_links structure
            toc_broken_links = style_metadata.get('toc_broken_links', [])
            
            if isinstance(toc_broken_links, list):
                validation_tests.append(f"✅ TOC broken links is array: {len(toc_broken_links)} items")
                
                # Analyze broken link details
                for broken_link in toc_broken_links:
                    if isinstance(broken_link, dict):
                        toc_text = broken_link.get('toc_text', 'unknown')
                        expected_slug = broken_link.get('expected_slug', 'unknown')
                        reason = broken_link.get('reason', 'unknown')
                        
                        validation_tests.append(f"Broken link: '{toc_text}' → '{expected_slug}' (reason: {reason})")
                    else:
                        validation_tests.append(f"⚠️ Invalid broken link format: {broken_link}")
            else:
                validation_tests.append(f"❌ TOC broken links not array: {type(toc_broken_links)}")
            
            # Test 2: Check validation logic
            formatted_content = article_result.get('formatted_content', '')
            
            # Find TOC anchor links
            toc_anchor_pattern = r'-\s*\[([^\]]+)\]\(#([^)]+)\)'
            toc_anchors = re.findall(toc_anchor_pattern, formatted_content)
            
            # Find heading IDs
            heading_id_pattern = r"<h[2-6][^>]*id=['\"]([^'\"]+)['\"]"
            heading_ids = re.findall(heading_id_pattern, formatted_content)
            
            if toc_anchors and heading_ids:
                # Validate each TOC anchor
                for toc_text, anchor_target in toc_anchors:
                    if anchor_target in heading_ids:
                        validation_tests.append(f"✅ Valid link: '{toc_text}' → #{anchor_target}")
                    else:
                        validation_tests.append(f"❌ Broken link: '{toc_text}' → #{anchor_target} (target not found)")
                
                # Check if broken link detection matches our analysis
                our_broken_count = len([anchor for _, anchor in toc_anchors if anchor not in heading_ids])
                detected_broken_count = len(toc_broken_links)
                
                if our_broken_count == detected_broken_count:
                    validation_tests.append(f"✅ Broken link detection accurate: {detected_broken_count} broken links")
                else:
                    validation_tests.append(f"⚠️ Broken link detection mismatch: detected {detected_broken_count}, actual {our_broken_count}")
            else:
                validation_tests.append("❌ Cannot validate - missing TOC anchors or heading IDs")
            
            # Test 3: Check anchor_links_generated metadata
            anchor_links_generated = style_metadata.get('anchor_links_generated', 0)
            
            if isinstance(anchor_links_generated, int):
                validation_tests.append(f"✅ Anchor links generated count: {anchor_links_generated}")
            else:
                validation_tests.append(f"❌ Invalid anchor links generated: {anchor_links_generated}")
            
            # Determine success
            success_indicators = len([test for test in validation_tests if test.startswith('✅')])
            has_broken_link_tracking = isinstance(toc_broken_links, list)
            has_anchor_count = 'anchor_links_generated' in style_metadata
            
            success = has_broken_link_tracking and has_anchor_count and success_indicators >= 3
            
            self.log_test("TOC Link Validation", success, 
                         f"Validation system tests ({success_indicators} success indicators): {validation_tests}",
                         {
                             'broken_links': toc_broken_links,
                             'anchor_count': anchor_links_generated,
                             'toc_anchors': len(toc_anchors) if toc_anchors else 0,
                             'heading_ids': len(heading_ids) if heading_ids else 0
                         })
            return success
            
        except Exception as e:
            self.log_test("TOC Link Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_metadata_structure(self) -> bool:
        """Test enhanced metadata structure with anchor information"""
        try:
            print(f"\n📊 TESTING ENHANCED METADATA STRUCTURE")
            
            # Get recent style result
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Enhanced Metadata", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_style_results', [])
            
            if not recent_results:
                self.log_test("Enhanced Metadata", False, "No recent results")
                return False
            
            # Get detailed result
            style_id = recent_results[0].get('style_id')
            detail_response = requests.get(f"{API_BASE}/style/diagnostics/{style_id}", timeout=30)
            
            if detail_response.status_code != 200:
                self.log_test("Enhanced Metadata", False, f"Detail HTTP {detail_response.status_code}")
                return False
                
            detail_data = detail_response.json()
            style_results = detail_data.get('style_result', {}).get('style_results', [])
            
            if not style_results:
                self.log_test("Enhanced Metadata", False, "No style results")
                return False
            
            style_metadata = style_results[0].get('style_metadata', {})
            
            metadata_tests = []
            
            # Test required anchor-related metadata fields
            required_anchor_fields = [
                ('anchor_links_generated', int),
                ('toc_broken_links', list)
            ]
            
            for field_name, expected_type in required_anchor_fields:
                if field_name in style_metadata:
                    field_value = style_metadata[field_name]
                    if isinstance(field_value, expected_type):
                        metadata_tests.append(f"✅ {field_name}: {field_value} ({expected_type.__name__})")
                    else:
                        metadata_tests.append(f"❌ {field_name}: wrong type {type(field_value)} (expected {expected_type.__name__})")
                else:
                    metadata_tests.append(f"❌ Missing {field_name}")
            
            # Test other enhanced metadata fields
            other_metadata_fields = [
                'formatting_method',
                'structural_changes',
                'compliance_score',
                'woolf_standards_applied'
            ]
            
            for field_name in other_metadata_fields:
                if field_name in style_metadata:
                    field_value = style_metadata[field_name]
                    metadata_tests.append(f"✅ {field_name}: {field_value}")
                else:
                    metadata_tests.append(f"❌ Missing {field_name}")
            
            # Test structural compliance metadata
            structural_compliance = style_results[0].get('structural_compliance', {})
            
            if structural_compliance:
                compliance_fields = ['compliance_score', 'toc_anchor_count', 'has_mini_toc']
                
                for field_name in compliance_fields:
                    if field_name in structural_compliance.get('compliance_checks', {}):
                        field_value = structural_compliance['compliance_checks'][field_name]
                        metadata_tests.append(f"✅ Structural {field_name}: {field_value}")
                    else:
                        metadata_tests.append(f"❌ Missing structural {field_name}")
            else:
                metadata_tests.append("❌ Missing structural_compliance metadata")
            
            # Test metadata completeness
            total_fields_expected = len(required_anchor_fields) + len(other_metadata_fields)
            fields_present = len([test for test in metadata_tests if test.startswith('✅') and not test.startswith('✅ Structural')])
            
            completeness_score = (fields_present / total_fields_expected) * 100
            metadata_tests.append(f"Metadata completeness: {completeness_score:.1f}% ({fields_present}/{total_fields_expected})")
            
            # Determine success
            has_anchor_metadata = 'anchor_links_generated' in style_metadata and 'toc_broken_links' in style_metadata
            success_indicators = len([test for test in metadata_tests if test.startswith('✅')])
            
            success = has_anchor_metadata and completeness_score >= 70
            
            self.log_test("Enhanced Metadata", success, 
                         f"Metadata structure tests ({success_indicators} success, {completeness_score:.1f}% complete): {metadata_tests}",
                         style_metadata)
            return success
            
        except Exception as e:
            self.log_test("Enhanced Metadata", False, f"Exception: {str(e)}")
            return False
    
    def test_structural_compliance_with_anchors(self) -> bool:
        """Test structural compliance validation includes anchor requirements"""
        try:
            print(f"\n🏗️ TESTING STRUCTURAL COMPLIANCE WITH ANCHORS")
            
            # Get recent style result
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Structural Compliance", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            recent_results = data.get('recent_style_results', [])
            
            if not recent_results:
                self.log_test("Structural Compliance", False, "No recent results")
                return False
            
            # Get detailed result
            style_id = recent_results[0].get('style_id')
            detail_response = requests.get(f"{API_BASE}/style/diagnostics/{style_id}", timeout=30)
            
            if detail_response.status_code != 200:
                self.log_test("Structural Compliance", False, f"Detail HTTP {detail_response.status_code}")
                return False
                
            detail_data = detail_response.json()
            style_results = detail_data.get('style_result', {}).get('style_results', [])
            
            if not style_results:
                self.log_test("Structural Compliance", False, "No style results")
                return False
            
            structural_compliance = style_results[0].get('structural_compliance', {})
            
            compliance_tests = []
            
            # Test 1: Check compliance score
            compliance_score = structural_compliance.get('compliance_score', 0)
            if isinstance(compliance_score, (int, float)):
                compliance_tests.append(f"✅ Compliance score: {compliance_score}")
            else:
                compliance_tests.append(f"❌ Invalid compliance score: {compliance_score}")
            
            # Test 2: Check TOC-related compliance checks
            compliance_checks = structural_compliance.get('compliance_checks', {})
            
            toc_related_checks = [
                'has_mini_toc',
                'toc_anchor_count'
            ]
            
            for check_name in toc_related_checks:
                if check_name in compliance_checks:
                    check_value = compliance_checks[check_name]
                    compliance_tests.append(f"✅ {check_name}: {check_value}")
                else:
                    compliance_tests.append(f"❌ Missing {check_name} check")
            
            # Test 3: Check other structural compliance checks
            other_checks = [
                'has_h1_title',
                'intro_length_compliant',
                'paragraph_length_compliant',
                'code_blocks_tagged',
                'faq_structure_compliant'
            ]
            
            for check_name in other_checks:
                if check_name in compliance_checks:
                    check_value = compliance_checks[check_name]
                    compliance_tests.append(f"✅ {check_name}: {check_value}")
                else:
                    compliance_tests.append(f"❌ Missing {check_name} check")
            
            # Test 4: Check compliance issues and recommendations
            issues = structural_compliance.get('issues', [])
            if isinstance(issues, list):
                compliance_tests.append(f"✅ Issues tracked: {len(issues)} issues")
                for issue in issues:
                    compliance_tests.append(f"Issue: {issue}")
            else:
                compliance_tests.append(f"❌ Issues not properly tracked: {issues}")
            
            # Test 5: Check overall compliance determination
            is_compliant = structural_compliance.get('is_compliant', False)
            total_checks = structural_compliance.get('total_checks', 0)
            passed_checks = structural_compliance.get('passed_checks', 0)
            
            if total_checks > 0:
                calculated_compliance = (passed_checks / total_checks) * 100
                compliance_tests.append(f"✅ Compliance calculation: {passed_checks}/{total_checks} = {calculated_compliance:.1f}%")
            else:
                compliance_tests.append("❌ No compliance checks performed")
            
            # Determine success
            has_toc_checks = any('toc' in test.lower() for test in compliance_tests)
            has_compliance_score = compliance_score > 0
            success_indicators = len([test for test in compliance_tests if test.startswith('✅')])
            
            success = has_toc_checks and has_compliance_score and success_indicators >= 5
            
            self.log_test("Structural Compliance", success, 
                         f"Compliance tests ({success_indicators} success indicators): {compliance_tests}",
                         structural_compliance)
            return success
            
        except Exception as e:
            self.log_test("Structural Compliance", False, f"Exception: {str(e)}")
            return False
    
    def test_woolf_standards_integration(self) -> bool:
        """Test Woolf standards integration with anchor processing"""
        try:
            print(f"\n📚 TESTING WOOLF STANDARDS INTEGRATION")
            
            # Get engine status to check Woolf features
            engine_response = requests.get(f"{API_BASE}/engine", timeout=30)
            
            if engine_response.status_code != 200:
                self.log_test("Woolf Standards Integration", False, f"Engine HTTP {engine_response.status_code}")
                return False
                
            engine_data = engine_response.json()
            
            # Get style diagnostics
            style_response = requests.get(f"{API_BASE}/style/diagnostics", timeout=30)
            
            if style_response.status_code != 200:
                self.log_test("Woolf Standards Integration", False, f"Style HTTP {style_response.status_code}")
                return False
                
            style_data = style_response.json()
            
            woolf_tests = []
            
            # Test 1: Check Woolf features in engine
            woolf_features = [
                'woolf_style_processing',
                'structural_linting',
                'microsoft_style_guide',
                'technical_writing_standards'
            ]
            
            engine_features = engine_data.get('features', [])
            
            for feature in woolf_features:
                if feature in engine_features:
                    woolf_tests.append(f"✅ Engine feature: {feature}")
                else:
                    woolf_tests.append(f"❌ Missing engine feature: {feature}")
            
            # Test 2: Check Woolf standards in style diagnostics
            woolf_standards = style_data.get('woolf_standards', {})
            
            expected_standards = [
                'structural_rules_enforced',
                'language_rules_enforced',
                'terminology_standardized',
                'microsoft_style_guide_applied'
            ]
            
            for standard in expected_standards:
                if woolf_standards.get(standard) is True:
                    woolf_tests.append(f"✅ Woolf standard: {standard}")
                else:
                    woolf_tests.append(f"❌ Woolf standard not applied: {standard}")
            
            # Test 3: Check recent results for Woolf application
            recent_results = style_data.get('recent_style_results', [])
            
            if recent_results:
                # Get detailed result
                style_id = recent_results[0].get('style_id')
                detail_response = requests.get(f"{API_BASE}/style/diagnostics/{style_id}", timeout=30)
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    style_results = detail_data.get('style_result', {}).get('style_results', [])
                    
                    if style_results:
                        style_metadata = style_results[0].get('style_metadata', {})
                        
                        # Check Woolf standards applied
                        woolf_applied = style_metadata.get('woolf_standards_applied', False)
                        if woolf_applied:
                            woolf_tests.append("✅ Woolf standards applied to content")
                        else:
                            woolf_tests.append("❌ Woolf standards not applied to content")
                        
                        # Check formatting method
                        formatting_method = style_metadata.get('formatting_method', '')
                        if 'llm_style_linting' in formatting_method:
                            woolf_tests.append(f"✅ LLM-based Woolf formatting: {formatting_method}")
                        else:
                            woolf_tests.append(f"❌ Non-LLM formatting method: {formatting_method}")
                        
                        # Check structural changes include Woolf elements
                        structural_changes = style_metadata.get('structural_changes', [])
                        if structural_changes:
                            woolf_elements = ['headings', 'IDs', 'TOC', 'formatting']
                            woolf_changes = [change for change in structural_changes if any(element in change for element in woolf_elements)]
                            
                            if woolf_changes:
                                woolf_tests.append(f"✅ Woolf structural changes: {len(woolf_changes)} changes")
                            else:
                                woolf_tests.append("❌ No Woolf structural changes detected")
                        else:
                            woolf_tests.append("❌ No structural changes recorded")
            else:
                woolf_tests.append("❌ No recent results to check Woolf application")
            
            # Determine success
            engine_features_present = len([test for test in woolf_tests if 'Engine feature:' in test and test.startswith('✅')])
            standards_applied = len([test for test in woolf_tests if 'Woolf standard:' in test and test.startswith('✅')])
            content_application = any('applied to content' in test and test.startswith('✅') for test in woolf_tests)
            
            success = engine_features_present >= 3 and standards_applied >= 3 and content_application
            
            self.log_test("Woolf Standards Integration", success, 
                         f"Woolf integration tests (engine: {engine_features_present}/4, standards: {standards_applied}/4, applied: {content_application}): {woolf_tests}",
                         {
                             'engine_features': engine_features_present,
                             'standards_applied': standards_applied,
                             'content_application': content_application
                         })
            return success
            
        except Exception as e:
            self.log_test("Woolf Standards Integration", False, f"Exception: {str(e)}")
            return False
    
    def run_focused_tests(self) -> Dict[str, Any]:
        """Run focused V2 Engine Step 7.5 Clickable Anchors Enhancement tests"""
        print(f"🚀 STARTING V2 ENGINE STEP 7.5 CLICKABLE ANCHORS FOCUSED TESTING")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📡 API Base: {API_BASE}")
        
        test_methods = [
            self.test_clickable_anchor_generation_verification,
            self.test_slug_generation_patterns,
            self.test_toc_link_validation_system,
            self.test_enhanced_metadata_structure,
            self.test_structural_compliance_with_anchors,
            self.test_woolf_standards_integration
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
            "step_tested": "Step 7.5 - Clickable Anchors Enhancement (Focused)"
        }
        
        print(f"\n" + "="*80)
        print(f"🎯 V2 ENGINE STEP 7.5 CLICKABLE ANCHORS FOCUSED TESTING COMPLETE")
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"🏆 OVERALL STATUS: {results['test_summary']['overall_status']}")
        print(f"="*80)
        
        return results

def main():
    """Main test execution"""
    tester = V2ClickableAnchorsFocusedTester()
    results = tester.run_focused_tests()
    
    # Print detailed results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for result in results["test_details"]:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['details']}")
    
    return results

if __name__ == "__main__":
    main()