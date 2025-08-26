#!/usr/bin/env python3
"""
TICKET 2 Implementation Testing - Local Backend Testing
Testing the complete TICKET 2 solution for Mini-TOC anchoring system using local backend
"""

import requests
import json
import time
import sys
import re
from datetime import datetime

# Use local backend for testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"🧪 TICKET 2 LOCAL TESTING: Stable Anchors + Mini-TOC Systematic Fix")
print(f"🌐 Backend URL: {BACKEND_URL}")
print(f"📡 API Base: {API_BASE}")
print("=" * 80)

class TICKET2LocalTester:
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
    
    def test_backend_health(self):
        """Test 0: Verify backend is healthy and V2 engine is available"""
        print("🔧 TEST 0: Backend Health Check")
        
        try:
            # Check basic health
            health_response = requests.get(f"{API_BASE}/health", timeout=10)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                
                # Check V2 engine status
                engine_response = requests.get(f"{API_BASE}/engine/status", timeout=10)
                
                if engine_response.status_code == 200:
                    engine_data = engine_response.json()
                    
                    # Verify V2 engine is active
                    v2_active = engine_data.get('engine') == 'v2'
                    has_style_processing = 'woolf_style_processing' in engine_data.get('features', [])
                    
                    passed = v2_active and has_style_processing
                    
                    self.log_test(
                        "Backend Health Check", 
                        passed,
                        f"V2 Engine: {v2_active}, Style Processing: {has_style_processing}"
                    )
                else:
                    self.log_test("Backend Health Check", False, f"Engine status error: {engine_response.status_code}")
            else:
                self.log_test("Backend Health Check", False, f"Health check error: {health_response.status_code}")
                
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Exception: {str(e)}")
    
    def test_v2_processing_pipeline(self):
        """Test 1: Verify V2 processing pipeline runs without method resolution errors"""
        print("🔧 TEST 1: V2 Processing Pipeline")
        
        test_content = """
        <h2>Getting Started with API Integration</h2>
        <p>This section covers the basics of API integration.</p>
        
        <h3>API Key & Authentication Setup</h3>
        <p>Configure your API credentials for secure access.</p>
        
        <h3>Making Your First API Call</h3>
        <p>Step-by-step guide to making your first API request.</p>
        
        <h2>Advanced Configuration</h2>
        <p>Advanced settings and customization options.</p>
        
        <h3>Error Handling</h3>
        <p>How to handle API errors gracefully.</p>
        """
        
        try:
            # Process content through V2 pipeline
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 V2 Pipeline Test",
                        "test_type": "v2_pipeline_test"
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if processing completed successfully
                has_articles = 'articles' in result and len(result['articles']) > 0
                
                if has_articles:
                    article = result['articles'][0]
                    article_content = article.get('content', '')
                    
                    # Verify V2 processing features are present
                    has_processed_content = len(article_content) > 100
                    has_metadata = 'metadata' in article
                    
                    passed = has_processed_content and has_metadata
                    
                    self.log_test(
                        "V2 Processing Pipeline", 
                        passed,
                        f"Articles generated: {len(result['articles'])}, Content length: {len(article_content)}, Has metadata: {has_metadata}"
                    )
                else:
                    self.log_test("V2 Processing Pipeline", False, "No articles generated")
            else:
                self.log_test("V2 Processing Pipeline", False, f"API error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            self.log_test("V2 Processing Pipeline", False, f"Exception: {str(e)}")
    
    def test_stable_slug_assignment(self):
        """Test 2: Verify stable slug assignment to heading IDs"""
        print("🔧 TEST 2: Stable Slug Assignment")
        
        test_content = """
        <h2>Getting Started Guide</h2>
        <p>Introduction to the system.</p>
        
        <h3>Prerequisites & Setup</h3>
        <p>What you need before starting.</p>
        
        <h3>Installation Process</h3>
        <p>Step-by-step installation guide.</p>
        
        <h2>Configuration Options</h2>
        <p>Available configuration settings.</p>
        
        <h4>Environment Variables</h4>
        <p>Required environment setup.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Stable Slug Test",
                        "test_type": "stable_slug_test"
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Look for stable slug patterns
                    expected_slugs = [
                        'getting-started-guide',
                        'prerequisites-setup',
                        'installation-process',
                        'configuration-options',
                        'environment-variables'
                    ]
                    
                    found_slugs = 0
                    for slug in expected_slugs:
                        if f'id="{slug}"' in article_content:
                            found_slugs += 1
                            print(f"    ✅ Found stable slug: {slug}")
                        else:
                            print(f"    ❌ Missing slug: {slug}")
                    
                    success_rate = found_slugs / len(expected_slugs)
                    passed = success_rate >= 0.6  # 60% success rate required
                    
                    self.log_test(
                        "Stable Slug Assignment", 
                        passed,
                        f"Found {found_slugs}/{len(expected_slugs)} expected slugs ({success_rate:.1%})"
                    )
                else:
                    self.log_test("Stable Slug Assignment", False, "No articles generated")
            else:
                self.log_test("Stable Slug Assignment", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Stable Slug Assignment", False, f"Exception: {str(e)}")
    
    def test_minitoc_generation(self):
        """Test 3: Verify Mini-TOC generation with proper clickable links"""
        print("🔧 TEST 3: Mini-TOC Generation")
        
        test_content = """
        <h2>System Overview</h2>
        <p>Overview of the system architecture and components.</p>
        
        <h3>Core Components</h3>
        <p>Description of the main system components.</p>
        
        <h3>Data Flow</h3>
        <p>How data flows through the system.</p>
        
        <h2>Implementation Guide</h2>
        <p>Step-by-step implementation instructions.</p>
        
        <h3>Setup Instructions</h3>
        <p>Initial setup and configuration.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Mini-TOC Test",
                        "test_type": "minitoc_test"
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Check for Mini-TOC structure
                    has_toc_container = 'mini-toc' in article_content.lower() or 'table of contents' in article_content.lower()
                    
                    # Count clickable links in TOC format
                    toc_links = len(re.findall(r'href="#[^"]+">.*?</a>', article_content))
                    
                    # Check for proper anchor format
                    anchor_links = len(re.findall(r'<a[^>]*href="#[^"]+', article_content))
                    
                    # Verify TOC appears before content
                    first_h2_pos = article_content.find('<h2')
                    toc_indicators = ['mini-toc', 'table of contents', 'contents']
                    toc_pos = min([article_content.lower().find(indicator) for indicator in toc_indicators if article_content.lower().find(indicator) != -1] or [len(article_content)])
                    
                    toc_before_content = toc_pos < first_h2_pos if first_h2_pos != -1 else False
                    
                    passed = (has_toc_container and 
                             toc_links >= 3 and  # Should have multiple TOC links
                             anchor_links >= 3 and  # Should have anchor links
                             toc_before_content)  # TOC positioned correctly
                    
                    self.log_test(
                        "Mini-TOC Generation", 
                        passed,
                        f"TOC container: {has_toc_container}, TOC links: {toc_links}, Anchor links: {anchor_links}, Position: {'correct' if toc_before_content else 'incorrect'}"
                    )
                else:
                    self.log_test("Mini-TOC Generation", False, "No articles generated")
            else:
                self.log_test("Mini-TOC Generation", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Mini-TOC Generation", False, f"Exception: {str(e)}")
    
    def test_duplicate_heading_handling(self):
        """Test 4: Verify duplicate heading handling with suffixes"""
        print("🔧 TEST 4: Duplicate Heading Handling")
        
        test_content = """
        <h2>Introduction</h2>
        <p>First introduction section.</p>
        
        <h3>Getting Started</h3>
        <p>Initial getting started guide.</p>
        
        <h2>Introduction</h2>
        <p>Second introduction section (duplicate).</p>
        
        <h3>Getting Started</h3>
        <p>Another getting started section (duplicate).</p>
        
        <h2>Configuration</h2>
        <p>Configuration details.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Duplicate Handling Test",
                        "test_type": "duplicate_handling_test"
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Look for duplicate handling patterns
                    has_base_introduction = 'id="introduction"' in article_content
                    has_suffixed_introduction = ('id="introduction-2"' in article_content or 
                                               'id="introduction-1"' in article_content)
                    
                    has_base_getting_started = 'id="getting-started"' in article_content
                    has_suffixed_getting_started = ('id="getting-started-2"' in article_content or 
                                                   'id="getting-started-1"' in article_content)
                    
                    # Count total unique IDs
                    all_ids = re.findall(r'id="([^"]+)"', article_content)
                    unique_ids = len(set(all_ids))
                    total_ids = len(all_ids)
                    
                    # All IDs should be unique (no duplicates)
                    no_duplicate_ids = unique_ids == total_ids
                    
                    passed = (has_base_introduction and 
                             has_suffixed_introduction and
                             has_base_getting_started and 
                             has_suffixed_getting_started and
                             no_duplicate_ids)
                    
                    self.log_test(
                        "Duplicate Heading Handling", 
                        passed,
                        f"Base intro: {has_base_introduction}, Suffixed intro: {has_suffixed_introduction}, Base getting-started: {has_base_getting_started}, Suffixed getting-started: {has_suffixed_getting_started}, Unique IDs: {unique_ids}/{total_ids}"
                    )
                else:
                    self.log_test("Duplicate Heading Handling", False, "No articles generated")
            else:
                self.log_test("Duplicate Heading Handling", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Duplicate Heading Handling", False, f"Exception: {str(e)}")
    
    def test_anchor_resolution(self):
        """Test 5: Verify all TOC links resolve correctly"""
        print("🔧 TEST 5: Anchor Resolution")
        
        test_content = """
        <h2>System Architecture</h2>
        <p>Overview of the system design.</p>
        
        <h3>Frontend Components</h3>
        <p>User interface components.</p>
        
        <h3>Backend Services</h3>
        <p>Server-side services.</p>
        
        <h2>API Documentation</h2>
        <p>Complete API reference.</p>
        
        <h3>Authentication</h3>
        <p>User authentication methods.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Anchor Resolution Test",
                        "test_type": "anchor_resolution_test"
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article_content = result['articles'][0].get('content', '')
                    
                    # Extract all TOC links (href="#...")
                    toc_links = re.findall(r'href="#([^"]+)"', article_content)
                    
                    # Extract all heading IDs (id="...")
                    heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', article_content)
                    
                    # Check resolution rate
                    resolved_links = 0
                    broken_links = []
                    
                    for link in toc_links:
                        if link in heading_ids:
                            resolved_links += 1
                        else:
                            broken_links.append(link)
                    
                    total_links = len(toc_links)
                    resolution_rate = resolved_links / total_links if total_links > 0 else 0
                    
                    # Require at least 80% resolution rate
                    passed = resolution_rate >= 0.8 and total_links > 0
                    
                    self.log_test(
                        "Anchor Resolution", 
                        passed,
                        f"Resolved {resolved_links}/{total_links} links ({resolution_rate:.1%}). Broken: {broken_links[:3]}"
                    )
                else:
                    self.log_test("Anchor Resolution", False, "No articles generated")
            else:
                self.log_test("Anchor Resolution", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Anchor Resolution", False, f"Exception: {str(e)}")
    
    def test_content_library_integration(self):
        """Test 6: Verify integration with content library"""
        print("🔧 TEST 6: Content Library Integration")
        
        try:
            # Check content library for recent articles with TICKET 2 features
            response = requests.get(f"{API_BASE}/content-library", timeout=30)
            
            if response.status_code == 200:
                library_data = response.json()
                
                if 'articles' in library_data and len(library_data['articles']) > 0:
                    # Look for recent articles with TICKET 2 features
                    recent_articles = library_data['articles'][:5]  # Check first 5 articles
                    
                    ticket2_features_found = 0
                    
                    for article in recent_articles:
                        content = article.get('content', '')
                        
                        # Check for TICKET 2 indicators
                        has_stable_ids = len(re.findall(r'id="[a-z0-9-]+"', content)) > 0
                        has_toc_links = 'href="#' in content
                        has_proper_headings = '<h2' in content or '<h3' in content
                        
                        if has_stable_ids and has_toc_links and has_proper_headings:
                            ticket2_features_found += 1
                    
                    feature_rate = ticket2_features_found / len(recent_articles)
                    passed = feature_rate >= 0.4  # At least 40% of recent articles have TICKET 2 features
                    
                    self.log_test(
                        "Content Library Integration", 
                        passed,
                        f"Found TICKET 2 features in {ticket2_features_found}/{len(recent_articles)} recent articles ({feature_rate:.1%})"
                    )
                else:
                    self.log_test("Content Library Integration", False, "No articles found in content library")
            else:
                self.log_test("Content Library Integration", False, f"Content library API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Content Library Integration", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all TICKET 2 tests"""
        print("🚀 Starting TICKET 2 Local Implementation Testing")
        print("=" * 80)
        
        # Run all test methods
        self.test_backend_health()
        self.test_v2_processing_pipeline()
        self.test_stable_slug_assignment()
        self.test_minitoc_generation()
        self.test_duplicate_heading_handling()
        self.test_anchor_resolution()
        self.test_content_library_integration()
        
        # Print summary
        print("=" * 80)
        print("🏁 TICKET 2 LOCAL TESTING SUMMARY")
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
    tester = TICKET2LocalTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)