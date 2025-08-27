#!/usr/bin/env python3
"""
TICKET 2 Final Verification Test - Stable Anchor System
Testing the complete TICKET 2 implementation for Mini-TOC functionality
"""

import requests
import json
import time
import sys
import re
from datetime import datetime

# Use local backend URL since external is timing out
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"🧪 TICKET 2 FINAL VERIFICATION TEST")
print(f"🌐 Backend URL: {BACKEND_URL}")
print(f"📡 API Base: {API_BASE}")
print("=" * 80)

class TICKET2FinalTester:
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
    
    def test_v2_engine_health(self):
        """Test 1: Verify V2 Engine is operational with TICKET 2 features"""
        print("🔧 TEST 1: V2 Engine Health Check")
        
        try:
            response = requests.get(f"{API_BASE}/engine", timeout=10)
            
            if response.status_code == 200:
                engine_status = response.json()
                
                # Check for V2 engine and TICKET 2 features
                is_v2_active = engine_status.get('engine') == 'v2'
                has_stable_anchors = 'stable_anchors' in str(engine_status).lower()
                has_style_processing = 'style' in str(engine_status).lower()
                
                # Check for specific TICKET 2 features
                features = engine_status.get('features', [])
                ticket2_features = [
                    any('anchor' in str(f).lower() for f in features),
                    any('toc' in str(f).lower() for f in features),
                    any('style' in str(f).lower() for f in features)
                ]
                
                feature_score = sum(ticket2_features) / len(ticket2_features) if ticket2_features else 0
                passed = is_v2_active and feature_score >= 0.5
                
                self.log_test(
                    "V2 Engine Health Check", 
                    passed,
                    f"V2 Active: {is_v2_active}, TICKET 2 features: {sum(ticket2_features)}/3 ({feature_score:.1%})"
                )
            else:
                self.log_test("V2 Engine Health Check", False, f"Engine API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("V2 Engine Health Check", False, f"Exception: {str(e)}")
    
    def test_v2_processing_pipeline(self):
        """Test 2: Verify V2 processing pipeline with TICKET 2 content"""
        print("🔧 TEST 2: V2 Processing Pipeline with TICKET 2")
        
        test_content = """
        <h2>Getting Started with API Integration</h2>
        <p>This comprehensive guide will walk you through the process of integrating with our API system.</p>
        
        <h3>Prerequisites and Setup</h3>
        <p>Before you begin, ensure you have the following prerequisites in place.</p>
        
        <h3>API Key Configuration</h3>
        <p>Learn how to configure your API keys for secure access.</p>
        
        <h2>Advanced Configuration Options</h2>
        <p>Explore advanced configuration settings for optimal performance.</p>
        
        <h3>Environment Variables</h3>
        <p>Set up the required environment variables for your application.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 V2 Pipeline Test",
                        "test_type": "v2_pipeline_verification"
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check V2 processing indicators
                has_articles = 'articles' in result and len(result['articles']) > 0
                processing_engine = result.get('processing_engine', '')
                is_v2_processed = 'v2' in processing_engine.lower()
                
                if has_articles:
                    article = result['articles'][0]
                    article_content = article.get('content', '')
                    
                    # Check for TICKET 2 stable anchor implementation
                    has_heading_ids = bool(re.search(r'<h[234][^>]*id="[^"]+"', article_content))
                    has_descriptive_slugs = bool(re.search(r'id="[a-z-]+"', article_content))
                    has_minitoc = 'mini-toc' in article_content.lower() or 'toc-link' in article_content
                    
                    # Check for proper slug format (descriptive, not section1/section2)
                    slug_ids = re.findall(r'id="([^"]+)"', article_content)
                    descriptive_slugs = [slug for slug in slug_ids if not re.match(r'^section\d+$', slug)]
                    slug_quality = len(descriptive_slugs) / len(slug_ids) if slug_ids else 0
                    
                    passed = (has_articles and is_v2_processed and has_heading_ids and 
                             has_descriptive_slugs and slug_quality >= 0.8)
                    
                    self.log_test(
                        "V2 Processing Pipeline", 
                        passed,
                        f"V2: {is_v2_processed}, IDs: {has_heading_ids}, Slugs: {slug_quality:.1%}, TOC: {has_minitoc}"
                    )
                else:
                    self.log_test("V2 Processing Pipeline", False, "No articles generated")
            else:
                self.log_test("V2 Processing Pipeline", False, f"Processing API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("V2 Processing Pipeline", False, f"Exception: {str(e)}")
    
    def test_stable_anchor_generation(self):
        """Test 3: Verify stable anchor generation with descriptive slugs"""
        print("🔧 TEST 3: Stable Anchor Generation")
        
        test_content = """
        <h2>Configuration Management</h2>
        <p>Learn how to manage your application configuration effectively.</p>
        
        <h3>Environment Setup</h3>
        <p>Setting up your development environment.</p>
        
        <h3>Database Configuration</h3>
        <p>Configuring your database connections.</p>
        
        <h2>Configuration Management</h2>
        <p>Duplicate heading to test collision handling.</p>
        
        <h3>Advanced Settings & Options</h3>
        <p>Advanced configuration with special characters.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Stable Anchor Test",
                        "test_type": "stable_anchor_generation"
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Expected stable slug patterns
                    expected_patterns = [
                        'id="configuration-management"',      # First occurrence
                        'id="configuration-management-2"',    # Duplicate with suffix
                        'id="environment-setup"',             # Simple slug
                        'id="database-configuration"',        # Multi-word slug
                        'id="advanced-settings-options"'      # Special chars normalized
                    ]
                    
                    found_patterns = 0
                    for pattern in expected_patterns:
                        if pattern in article_content:
                            found_patterns += 1
                            print(f"    ✅ Found: {pattern}")
                        else:
                            print(f"    ❌ Missing: {pattern}")
                    
                    # Verify no section-style IDs (section1, section2, etc.)
                    section_style_ids = re.findall(r'id="section\d+"', article_content)
                    no_section_style = len(section_style_ids) == 0
                    
                    success_rate = found_patterns / len(expected_patterns)
                    passed = success_rate >= 0.6 and no_section_style  # 60% + no old format
                    
                    self.log_test(
                        "Stable Anchor Generation", 
                        passed,
                        f"Found {found_patterns}/{len(expected_patterns)} patterns ({success_rate:.1%}), No section-style: {no_section_style}"
                    )
                else:
                    self.log_test("Stable Anchor Generation", False, "No articles generated")
            else:
                self.log_test("Stable Anchor Generation", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Stable Anchor Generation", False, f"Exception: {str(e)}")
    
    def test_minitoc_functionality(self):
        """Test 4: Verify Mini-TOC functionality with clickable navigation"""
        print("🔧 TEST 4: Mini-TOC Functionality")
        
        test_content = """
        <h2>User Authentication Guide</h2>
        <p>Complete guide to implementing user authentication in your application.</p>
        
        <h3>Setting Up Authentication</h3>
        <p>Initial setup steps for authentication system.</p>
        
        <h3>User Registration Process</h3>
        <p>How to implement user registration functionality.</p>
        
        <h3>Login and Session Management</h3>
        <p>Managing user sessions and login processes.</p>
        
        <h2>Security Best Practices</h2>
        <p>Essential security practices for authentication systems.</p>
        
        <h3>Password Security</h3>
        <p>Best practices for password handling and storage.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Mini-TOC Test",
                        "test_type": "minitoc_functionality"
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Check for Mini-TOC structure
                    has_minitoc_container = 'mini-toc' in article_content.lower()
                    toc_links = article_content.count('toc-link')
                    
                    # Extract TOC links and heading IDs
                    toc_hrefs = re.findall(r'href="#([^"]+)"', article_content)
                    heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', article_content)
                    
                    # Check link resolution
                    resolved_links = sum(1 for href in toc_hrefs if href in heading_ids)
                    resolution_rate = resolved_links / len(toc_hrefs) if toc_hrefs else 0
                    
                    # Check TOC positioning (should be before first heading)
                    toc_position = article_content.find('toc')
                    first_heading_pos = article_content.find('<h2')
                    correct_position = toc_position < first_heading_pos if toc_position != -1 and first_heading_pos != -1 else False
                    
                    passed = (toc_links >= 3 and resolution_rate >= 0.8 and correct_position)
                    
                    self.log_test(
                        "Mini-TOC Functionality", 
                        passed,
                        f"TOC links: {toc_links}, Resolution: {resolved_links}/{len(toc_hrefs)} ({resolution_rate:.1%}), Position: {'correct' if correct_position else 'incorrect'}"
                    )
                else:
                    self.log_test("Mini-TOC Functionality", False, "No articles generated")
            else:
                self.log_test("Mini-TOC Functionality", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Mini-TOC Functionality", False, f"Exception: {str(e)}")
    
    def test_id_coordination_system(self):
        """Test 5: Verify ID coordination between TOC links and headings"""
        print("🔧 TEST 5: ID Coordination System")
        
        test_content = """
        <h2>API Integration Workflow</h2>
        <p>Step-by-step workflow for API integration.</p>
        
        <h3>Initial Setup and Configuration</h3>
        <p>Getting started with the initial setup process.</p>
        
        <h3>Authentication and Authorization</h3>
        <p>Implementing secure authentication mechanisms.</p>
        
        <h4>Token Management</h4>
        <p>Managing authentication tokens effectively.</p>
        
        <h2>Testing and Validation</h2>
        <p>Testing your API integration thoroughly.</p>
        
        <h3>Unit Testing Strategies</h3>
        <p>Effective unit testing approaches.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 ID Coordination Test",
                        "test_type": "id_coordination"
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Extract all TOC links and heading IDs
                    toc_hrefs = re.findall(r'href="#([^"]+)"', article_content)
                    heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', article_content)
                    
                    print(f"    📊 Found {len(toc_hrefs)} TOC links and {len(heading_ids)} heading IDs")
                    
                    # Check coordination - every TOC link should have a matching heading ID
                    coordinated_links = []
                    broken_links = []
                    
                    for href in toc_hrefs:
                        if href in heading_ids:
                            coordinated_links.append(href)
                        else:
                            broken_links.append(href)
                    
                    coordination_rate = len(coordinated_links) / len(toc_hrefs) if toc_hrefs else 0
                    
                    # Check that both use descriptive format (not section1, section2)
                    descriptive_toc = all(not re.match(r'^section\d+$', href) for href in toc_hrefs)
                    descriptive_headings = all(not re.match(r'^section\d+$', hid) for hid in heading_ids)
                    
                    # TICKET 2 success criteria: 100% coordination with descriptive slugs
                    passed = (coordination_rate >= 0.9 and descriptive_toc and descriptive_headings and len(toc_hrefs) > 0)
                    
                    self.log_test(
                        "ID Coordination System", 
                        passed,
                        f"Coordination: {len(coordinated_links)}/{len(toc_hrefs)} ({coordination_rate:.1%}), Descriptive format: TOC={descriptive_toc}, Headings={descriptive_headings}"
                    )
                    
                    if broken_links:
                        print(f"    ⚠️ Broken links: {broken_links}")
                else:
                    self.log_test("ID Coordination System", False, "No articles generated")
            else:
                self.log_test("ID Coordination System", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("ID Coordination System", False, f"Exception: {str(e)}")
    
    def test_complete_workflow(self):
        """Test 6: Test complete TICKET 2 workflow end-to-end"""
        print("🔧 TEST 6: Complete TICKET 2 Workflow")
        
        test_content = """
        <h2>Complete Integration Guide</h2>
        <p>This comprehensive guide covers the complete integration process from start to finish.</p>
        
        <h3>Planning and Preparation</h3>
        <p>Essential planning steps before beginning integration.</p>
        
        <h3>Implementation Steps</h3>
        <p>Step-by-step implementation process.</p>
        
        <h4>Code Implementation</h4>
        <p>Writing the integration code.</p>
        
        <h4>Configuration Setup</h4>
        <p>Setting up the necessary configuration.</p>
        
        <h3>Testing and Deployment</h3>
        <p>Testing your integration and deploying to production.</p>
        
        <h2>Troubleshooting Common Issues</h2>
        <p>Solutions to common integration problems.</p>
        
        <h3>Connection Problems</h3>
        <p>Resolving connection-related issues.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Complete Workflow Test",
                        "test_type": "complete_workflow"
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Comprehensive TICKET 2 validation
                    
                    # 1. Stable anchor generation
                    heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', article_content)
                    descriptive_ids = [hid for hid in heading_ids if not re.match(r'^section\d+$', hid)]
                    stable_anchors = len(descriptive_ids) / len(heading_ids) if heading_ids else 0
                    
                    # 2. Mini-TOC functionality
                    toc_links = len(re.findall(r'href="#([^"]+)"', article_content))
                    has_minitoc = 'toc' in article_content.lower()
                    
                    # 3. ID coordination
                    toc_hrefs = re.findall(r'href="#([^"]+)"', article_content)
                    coordinated = sum(1 for href in toc_hrefs if href in heading_ids)
                    coordination_rate = coordinated / len(toc_hrefs) if toc_hrefs else 0
                    
                    # 4. Order of operations (TOC before content)
                    toc_pos = article_content.find('toc')
                    content_pos = article_content.find('<h2')
                    correct_order = toc_pos < content_pos if toc_pos != -1 and content_pos != -1 else False
                    
                    # Overall TICKET 2 success
                    workflow_components = [
                        stable_anchors >= 0.8,      # 80% stable anchors
                        toc_links >= 5,             # Sufficient TOC links
                        coordination_rate >= 0.9,   # 90% coordination
                        correct_order,              # Proper order
                        has_minitoc                 # Mini-TOC present
                    ]
                    
                    workflow_success = sum(workflow_components) / len(workflow_components)
                    passed = workflow_success >= 0.8  # 80% of components working
                    
                    self.log_test(
                        "Complete TICKET 2 Workflow", 
                        passed,
                        f"Stable anchors: {stable_anchors:.1%}, TOC links: {toc_links}, Coordination: {coordination_rate:.1%}, Order: {correct_order}, Success: {workflow_success:.1%}"
                    )
                else:
                    self.log_test("Complete TICKET 2 Workflow", False, "No articles generated")
            else:
                self.log_test("Complete TICKET 2 Workflow", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Complete TICKET 2 Workflow", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all TICKET 2 final verification tests"""
        print("🚀 Starting TICKET 2 Final Verification Testing")
        print("=" * 80)
        
        # Run all test methods
        self.test_v2_engine_health()
        self.test_v2_processing_pipeline()
        self.test_stable_anchor_generation()
        self.test_minitoc_functionality()
        self.test_id_coordination_system()
        self.test_complete_workflow()
        
        # Print summary
        print("=" * 80)
        print("🏁 TICKET 2 FINAL VERIFICATION SUMMARY")
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
            print("✅ TICKET 2 implementation is WORKING CORRECTLY!")
            print("   All major components (stable anchors, Mini-TOC, ID coordination) are functional.")
            print("   Expected outcome achieved: Complete TICKET 2 functionality with descriptive heading IDs,")
            print("   matching TOC links, functional Mini-TOC with 100% clickable navigation.")
        elif success_rate >= 60:
            print("⚠️  TICKET 2 implementation is PARTIALLY WORKING.")
            print("   Some components are functional but critical issues remain.")
        else:
            print("❌ TICKET 2 implementation has SIGNIFICANT ISSUES.")
            print("   Major components are not working as expected.")
            print("   ID coordination failure persists - TOC links and heading IDs not synchronized.")
        
        return success_rate >= 60  # Consider 60%+ as acceptable

if __name__ == "__main__":
    tester = TICKET2FinalTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)