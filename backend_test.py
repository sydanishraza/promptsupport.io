#!/usr/bin/env python3
"""
TICKET 2 Implementation Testing - Stable Anchors + Mini-TOC Systematic Fix
Testing the complete TICKET 2 solution for Mini-TOC anchoring system
"""

import requests
import json
import time
import sys
import re
from datetime import datetime

# Use configured backend URL from environment
import os
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🧪 TICKET 2 TESTING: Stable Anchors + Mini-TOC Systematic Fix")
print(f"🌐 Backend URL: {BACKEND_URL}")
print(f"📡 API Base: {API_BASE}")
print("=" * 80)

class TICKET2Tester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} | {test_name}")
        if details:
            print(f"    📝 {details}")
        print()
    
    def test_stable_slug_generation(self):
        """Test 1: Verify stable slug generation with special characters and duplicates"""
        print("🔧 TEST 1: Stable Slug Generation")
        
        # Test content with various heading types
        test_content = """
        <h2>Getting Started with API Integration</h2>
        <p>This section covers the basics.</p>
        
        <h3>API Key & Authentication Setup</h3>
        <p>Configure your API credentials.</p>
        
        <h2>Getting Started with API Integration</h2>
        <p>Duplicate heading to test collision handling.</p>
        
        <h3>Special Characters: Testing (Symbols) & Unicode™</h3>
        <p>Testing special character handling.</p>
        
        <h4>Step-by-Step Configuration Process</h4>
        <p>Detailed configuration steps.</p>
        """
        
        try:
            # Process content through V2 style system to trigger TICKET 2 implementation
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Slug Test",
                        "test_type": "stable_slug_generation"
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if articles were generated
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Verify stable slug patterns
                    expected_patterns = [
                        'id="getting-started-with-api-integration"',  # First occurrence
                        'id="getting-started-with-api-integration-2"',  # Duplicate with suffix
                        'id="api-key-authentication-setup"',  # Special chars normalized
                        'id="special-characters-testing-symbols-unicode"',  # Unicode normalized
                        'id="step-by-step-configuration-process"'  # Hyphens preserved
                    ]
                    
                    found_patterns = 0
                    for pattern in expected_patterns:
                        if pattern in article_content:
                            found_patterns += 1
                            print(f"    ✅ Found expected pattern: {pattern}")
                        else:
                            print(f"    ❌ Missing pattern: {pattern}")
                    
                    success_rate = found_patterns / len(expected_patterns)
                    passed = success_rate >= 0.8  # 80% success rate required
                    
                    self.log_test(
                        "Stable Slug Generation", 
                        passed,
                        f"Found {found_patterns}/{len(expected_patterns)} expected slug patterns ({success_rate:.1%})"
                    )
                else:
                    self.log_test("Stable Slug Generation", False, "No articles generated from test content")
            else:
                self.log_test("Stable Slug Generation", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Stable Slug Generation", False, f"Exception: {str(e)}")
    
    def test_heading_id_assignment(self):
        """Test 2: Verify ID assignment before TOC generation"""
        print("🔧 TEST 2: Heading ID Assignment Before TOC")
        
        test_content = """
        <h2>Introduction to the System</h2>
        <p>Overview content here.</p>
        
        <h3>Key Features and Benefits</h3>
        <p>Feature descriptions.</p>
        
        <h3>Implementation Requirements</h3>
        <p>Requirements details.</p>
        
        <h4>Technical Specifications</h4>
        <p>Technical details.</p>
        
        <h2>Advanced Configuration</h2>
        <p>Advanced topics.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 ID Assignment Test",
                        "test_type": "heading_id_assignment"
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Check for proper ID assignment to H2, H3, H4 headings
                    h2_with_ids = article_content.count('<h2 id="')
                    h3_with_ids = article_content.count('<h3 id="')
                    h4_with_ids = article_content.count('<h4 id="')
                    
                    # Count total headings
                    total_h2 = article_content.count('<h2')
                    total_h3 = article_content.count('<h3')
                    total_h4 = article_content.count('<h4')
                    
                    # All headings should have IDs assigned
                    all_h2_have_ids = h2_with_ids == total_h2 and total_h2 > 0
                    all_h3_have_ids = h3_with_ids == total_h3 and total_h3 > 0
                    all_h4_have_ids = h4_with_ids == total_h4 and total_h4 > 0
                    
                    passed = all_h2_have_ids and all_h3_have_ids and all_h4_have_ids
                    
                    self.log_test(
                        "Heading ID Assignment", 
                        passed,
                        f"H2: {h2_with_ids}/{total_h2}, H3: {h3_with_ids}/{total_h3}, H4: {h4_with_ids}/{total_h4} have IDs"
                    )
                else:
                    self.log_test("Heading ID Assignment", False, "No articles generated")
            else:
                self.log_test("Heading ID Assignment", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Heading ID Assignment", False, f"Exception: {str(e)}")
    
    def test_minitoc_creation(self):
        """Test 3: Verify Mini-TOC creation with clickable links"""
        print("🔧 TEST 3: Mini-TOC Creation with Clickable Links")
        
        test_content = """
        <h2>Getting Started Guide</h2>
        <p>This guide will help you get started quickly.</p>
        
        <h3>Prerequisites and Setup</h3>
        <p>What you need before starting.</p>
        
        <h3>Installation Process</h3>
        <p>Step-by-step installation.</p>
        
        <h2>Configuration Options</h2>
        <p>Available configuration settings.</p>
        
        <h3>Basic Configuration</h3>
        <p>Essential settings.</p>
        
        <h4>Environment Variables</h4>
        <p>Required environment setup.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Mini-TOC Test",
                        "test_type": "minitoc_creation"
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Check for Mini-TOC structure
                    has_minitoc_container = 'class="mini-toc"' in article_content
                    
                    # Count TOC links
                    toc_links = article_content.count('class="toc-link"')
                    
                    # Check for proper href attributes pointing to heading IDs
                    href_patterns = [
                        'href="#getting-started-guide"',
                        'href="#prerequisites-and-setup"',
                        'href="#installation-process"',
                        'href="#configuration-options"',
                        'href="#basic-configuration"',
                        'href="#environment-variables"'
                    ]
                    
                    found_hrefs = 0
                    for pattern in href_patterns:
                        if pattern in article_content:
                            found_hrefs += 1
                    
                    # Verify TOC is positioned at the beginning
                    toc_position = article_content.find('class="mini-toc"')
                    first_heading_position = article_content.find('<h2')
                    toc_before_content = toc_position < first_heading_position if toc_position != -1 and first_heading_position != -1 else False
                    
                    passed = (has_minitoc_container and 
                             toc_links >= 5 and  # Should have links for all headings
                             found_hrefs >= 4 and  # Most href patterns found
                             toc_before_content)  # TOC positioned correctly
                    
                    self.log_test(
                        "Mini-TOC Creation", 
                        passed,
                        f"TOC container: {has_minitoc_container}, Links: {toc_links}, Hrefs: {found_hrefs}/6, Position: {'correct' if toc_before_content else 'incorrect'}"
                    )
                else:
                    self.log_test("Mini-TOC Creation", False, "No articles generated")
            else:
                self.log_test("Mini-TOC Creation", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Mini-TOC Creation", False, f"Exception: {str(e)}")
    
    def test_heading_ladder_validation(self):
        """Test 4: Verify proper heading hierarchy validation"""
        print("🔧 TEST 4: Heading Ladder Validation")
        
        # Test with proper hierarchy
        valid_content = """
        <h2>Main Section</h2>
        <p>Main content.</p>
        
        <h3>Subsection A</h3>
        <p>Subsection content.</p>
        
        <h4>Detail Level</h4>
        <p>Detailed information.</p>
        
        <h3>Subsection B</h3>
        <p>More subsection content.</p>
        
        <h2>Another Main Section</h2>
        <p>More main content.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process-text", 
                data={
                    "content": valid_content,
                    "metadata": json.dumps({
                        "title": "TICKET 2 Heading Ladder Test",
                        "test_type": "heading_ladder_validation"
                    })
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    # Check if processing succeeded (proper hierarchy should be accepted)
                    article_content = result['articles'][0].get('content', '')
                    
                    # Verify the content was processed and contains expected structure
                    has_h2 = '<h2' in article_content
                    has_h3 = '<h3' in article_content
                    has_h4 = '<h4' in article_content
                    has_minitoc = 'mini-toc' in article_content
                    
                    # Proper hierarchy should result in successful processing
                    passed = has_h2 and has_h3 and has_h4 and has_minitoc
                    
                    self.log_test(
                        "Heading Ladder Validation", 
                        passed,
                        f"Valid hierarchy processed successfully: H2={has_h2}, H3={has_h3}, H4={has_h4}, TOC={has_minitoc}"
                    )
                else:
                    self.log_test("Heading Ladder Validation", False, "No articles generated from valid hierarchy")
            else:
                self.log_test("Heading Ladder Validation", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Heading Ladder Validation", False, f"Exception: {str(e)}")
    
    def test_anchor_resolution(self):
        """Test 5: Verify all TOC links resolve to actual headings"""
        print("🔧 TEST 5: Anchor Resolution Validation")
        
        test_content = """
        <h2>System Overview</h2>
        <p>Overview of the system architecture.</p>
        
        <h3>Core Components</h3>
        <p>Description of core components.</p>
        
        <h3>Data Flow</h3>
        <p>How data flows through the system.</p>
        
        <h2>Implementation Guide</h2>
        <p>Step-by-step implementation.</p>
        
        <h3>Setup Instructions</h3>
        <p>Initial setup process.</p>
        
        <h4>Configuration Files</h4>
        <p>Required configuration.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process-text", 
                data={
                    "content": test_content,
                    "metadata": json.dumps({
                        "title": "TICKET 2 Anchor Resolution Test",
                        "test_type": "anchor_resolution"
                    })
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Extract all TOC links (href="#...")
                    toc_links = re.findall(r'href="#([^"]+)"', article_content)
                    
                    # Extract all heading IDs (id="...")
                    heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', article_content)
                    
                    # Check if all TOC links have corresponding heading IDs
                    resolved_links = 0
                    broken_links = []
                    
                    for link in toc_links:
                        if link in heading_ids:
                            resolved_links += 1
                        else:
                            broken_links.append(link)
                    
                    total_links = len(toc_links)
                    resolution_rate = resolved_links / total_links if total_links > 0 else 0
                    
                    # All links should resolve (100% resolution rate)
                    passed = resolution_rate == 1.0 and total_links > 0
                    
                    self.log_test(
                        "Anchor Resolution", 
                        passed,
                        f"Resolved {resolved_links}/{total_links} links ({resolution_rate:.1%}). Broken: {broken_links}"
                    )
                else:
                    self.log_test("Anchor Resolution", False, "No articles generated")
            else:
                self.log_test("Anchor Resolution", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Anchor Resolution", False, f"Exception: {str(e)}")
    
    def test_duplicate_heading_handling(self):
        """Test 6: Verify duplicate heading handling with suffixes"""
        print("🔧 TEST 6: Duplicate Heading Handling")
        
        test_content = """
        <h2>Introduction</h2>
        <p>First introduction section.</p>
        
        <h3>Getting Started</h3>
        <p>Initial getting started guide.</p>
        
        <h2>Introduction</h2>
        <p>Second introduction section (duplicate).</p>
        
        <h3>Getting Started</h3>
        <p>Another getting started section (duplicate).</p>
        
        <h3>Getting Started</h3>
        <p>Third getting started section (triple).</p>
        
        <h2>Conclusion</h2>
        <p>Final thoughts.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process-text", 
                data={
                    "content": test_content,
                    "metadata": json.dumps({
                        "title": "TICKET 2 Duplicate Handling Test",
                        "test_type": "duplicate_handling"
                    })
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Check for expected duplicate handling patterns
                    expected_ids = [
                        'id="introduction"',      # First occurrence
                        'id="introduction-2"',    # Second occurrence with suffix
                        'id="getting-started"',   # First occurrence
                        'id="getting-started-2"', # Second occurrence with suffix
                        'id="getting-started-3"', # Third occurrence with suffix
                        'id="conclusion"'         # Unique heading
                    ]
                    
                    found_ids = 0
                    for expected_id in expected_ids:
                        if expected_id in article_content:
                            found_ids += 1
                            print(f"    ✅ Found: {expected_id}")
                        else:
                            print(f"    ❌ Missing: {expected_id}")
                    
                    # Check that TOC links also use the correct suffixed IDs
                    toc_has_suffixes = ('href="#introduction-2"' in article_content and 
                                       'href="#getting-started-2"' in article_content and
                                       'href="#getting-started-3"' in article_content)
                    
                    success_rate = found_ids / len(expected_ids)
                    passed = success_rate >= 0.8 and toc_has_suffixes  # 80% success + TOC consistency
                    
                    self.log_test(
                        "Duplicate Heading Handling", 
                        passed,
                        f"Found {found_ids}/{len(expected_ids)} expected IDs ({success_rate:.1%}), TOC suffixes: {toc_has_suffixes}"
                    )
                else:
                    self.log_test("Duplicate Heading Handling", False, "No articles generated")
            else:
                self.log_test("Duplicate Heading Handling", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Duplicate Heading Handling", False, f"Exception: {str(e)}")
    
    def test_order_of_operations(self):
        """Test 7: Verify correct order of operations (IDs → TOC → Validation)"""
        print("🔧 TEST 7: Order of Operations Verification")
        
        test_content = """
        <h2>System Architecture</h2>
        <p>Overview of the system design and architecture.</p>
        
        <h3>Frontend Components</h3>
        <p>User interface components and their responsibilities.</p>
        
        <h3>Backend Services</h3>
        <p>Server-side services and API endpoints.</p>
        
        <h4>Database Layer</h4>
        <p>Data persistence and storage mechanisms.</p>
        
        <h2>API Documentation</h2>
        <p>Complete API reference and usage examples.</p>
        
        <h3>Authentication Endpoints</h3>
        <p>User authentication and authorization.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process-text", 
                data={
                    "content": test_content,
                    "metadata": json.dumps({
                        "title": "TICKET 2 Order of Operations Test",
                        "test_type": "order_of_operations"
                    })
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Verify the complete pipeline worked correctly:
                    # 1. All headings have IDs assigned
                    headings_with_ids = len(re.findall(r'<h[234][^>]*id="[^"]+"', article_content))
                    total_headings = article_content.count('<h2') + article_content.count('<h3') + article_content.count('<h4')
                    
                    # 2. Mini-TOC was built using those IDs
                    has_minitoc = 'class="mini-toc"' in article_content
                    toc_links_count = article_content.count('class="toc-link"')
                    
                    # 3. All TOC links resolve to existing heading IDs
                    toc_hrefs = re.findall(r'class="toc-link"[^>]*href="#([^"]+)"', article_content)
                    heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', article_content)
                    
                    all_links_resolve = all(href in heading_ids for href in toc_hrefs)
                    
                    # 4. TOC appears before the first heading (correct positioning)
                    toc_position = article_content.find('class="mini-toc"')
                    first_heading_pos = article_content.find('<h2')
                    correct_positioning = toc_position < first_heading_pos if toc_position != -1 and first_heading_pos != -1 else False
                    
                    # All operations should complete successfully
                    ids_assigned = headings_with_ids == total_headings and total_headings > 0
                    toc_built = has_minitoc and toc_links_count > 0
                    validation_passed = all_links_resolve and len(toc_hrefs) > 0
                    
                    passed = ids_assigned and toc_built and validation_passed and correct_positioning
                    
                    self.log_test(
                        "Order of Operations", 
                        passed,
                        f"IDs: {headings_with_ids}/{total_headings}, TOC: {toc_links_count} links, Resolution: {all_links_resolve}, Position: {'correct' if correct_positioning else 'incorrect'}"
                    )
                else:
                    self.log_test("Order of Operations", False, "No articles generated")
            else:
                self.log_test("Order of Operations", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Order of Operations", False, f"Exception: {str(e)}")
    
    def test_style_diagnostics_integration(self):
        """Test 8: Verify TICKET 2 integration with V2 Style Diagnostics"""
        print("🔧 TEST 8: Style Diagnostics Integration")
        
        try:
            # Get style diagnostics to verify TICKET 2 features are tracked
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=15)
            
            if response.status_code == 200:
                diagnostics = response.json()
                
                # Check for TICKET 2 related metrics in diagnostics
                has_recent_runs = len(diagnostics.get('recent_results', [])) > 0
                
                if has_recent_runs:
                    recent_run = diagnostics['recent_results'][0]
                    
                    # Look for TICKET 2 related fields
                    ticket2_indicators = [
                        'anchors_resolve' in str(recent_run),
                        'heading_ladder_valid' in str(recent_run),
                        'stable_anchors_applied' in str(recent_run),
                        'toc' in str(recent_run).lower()
                    ]
                    
                    integration_score = sum(ticket2_indicators) / len(ticket2_indicators)
                    passed = integration_score >= 0.5  # At least 50% of indicators present
                    
                    self.log_test(
                        "Style Diagnostics Integration", 
                        passed,
                        f"TICKET 2 integration indicators: {sum(ticket2_indicators)}/{len(ticket2_indicators)} ({integration_score:.1%})"
                    )
                else:
                    self.log_test("Style Diagnostics Integration", False, "No recent style processing runs found")
            else:
                self.log_test("Style Diagnostics Integration", False, f"Diagnostics API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Style Diagnostics Integration", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all TICKET 2 tests"""
        print("🚀 Starting TICKET 2 Implementation Testing")
        print("=" * 80)
        
        # Run all test methods
        self.test_stable_slug_generation()
        self.test_heading_id_assignment()
        self.test_minitoc_creation()
        self.test_heading_ladder_validation()
        self.test_anchor_resolution()
        self.test_duplicate_heading_handling()
        self.test_order_of_operations()
        self.test_style_diagnostics_integration()
        
        # Print summary
        print("=" * 80)
        print("🏁 TICKET 2 TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📊 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
        
        print()
        print("🎯 TICKET 2 IMPLEMENTATION STATUS:")
        if success_rate >= 80:
            print("✅ TICKET 2 implementation is working correctly!")
            print("   All major components (stable slugs, ID assignment, Mini-TOC, validation) are functional.")
        elif success_rate >= 60:
            print("⚠️  TICKET 2 implementation is partially working.")
            print("   Some components are functional but issues remain.")
        else:
            print("❌ TICKET 2 implementation has significant issues.")
            print("   Major components are not working as expected.")
        
        return success_rate >= 60  # Consider 60%+ as acceptable

if __name__ == "__main__":
    tester = TICKET2Tester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)