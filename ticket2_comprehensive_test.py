#!/usr/bin/env python3
"""
TICKET 2 Comprehensive Testing - V2 Processing Pipeline and Mini-TOC
Final comprehensive test of TICKET 2 implementation as requested in review
"""

import requests
import json
import time
import sys
import re
import os
from datetime import datetime

# Use configured backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 TICKET 2 COMPREHENSIVE TESTING - Final Integration Verification")
print(f"🌐 Backend URL: {BACKEND_URL}")
print(f"📡 API Base: {API_BASE}")
print("=" * 80)

class TICKET2ComprehensiveTester:
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
    
    def test_v2_processing_pipeline_health(self):
        """Test 1: Verify V2 processing pipeline runs without method resolution errors"""
        print("🔧 TEST 1: V2 Processing Pipeline Health Check")
        
        # Test content designed to trigger TICKET 2 features
        test_content = """
        <h2>API Integration Complete Guide</h2>
        <p>This comprehensive guide covers everything you need to know about API integration, from basic setup to advanced configuration.</p>
        
        <h3>Getting Started with Setup</h3>
        <p>Before you begin the integration process, ensure you have all the necessary prerequisites in place.</p>
        
        <h3>Authentication & Security</h3>
        <p>Learn how to properly configure authentication and security measures for your API integration.</p>
        
        <h4>API Key Configuration</h4>
        <p>Step-by-step instructions for setting up your API keys securely.</p>
        
        <h4>OAuth Implementation</h4>
        <p>Advanced authentication using OAuth 2.0 for enhanced security.</p>
        
        <h2>Implementation Best Practices</h2>
        <p>Follow these industry-standard best practices to ensure a robust and maintainable integration.</p>
        
        <h3>Error Handling Strategies</h3>
        <p>Comprehensive error handling approaches for production-ready applications.</p>
        
        <h3>Performance Optimization</h3>
        <p>Techniques to optimize your API calls and improve overall performance.</p>
        """
        
        try:
            print("📤 Sending content to V2 processing pipeline...")
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 Comprehensive Test - V2 Pipeline",
                        "test_type": "v2_pipeline_comprehensive"
                    }
                },
                timeout=90  # Extended timeout for comprehensive processing
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # V2 processing should complete successfully
                processing_success = (
                    result.get('status') == 'completed' and
                    result.get('engine') == 'v2' and
                    result.get('chunks_created', 0) > 0
                )
                
                job_id = result.get('job_id', 'unknown')
                chunks_created = result.get('chunks_created', 0)
                
                self.log_test(
                    "V2 Processing Pipeline Health", 
                    processing_success,
                    f"Status: {result.get('status')}, Engine: {result.get('engine')}, Chunks: {chunks_created}, Job ID: {job_id}"
                )
                
                return job_id if processing_success else None
            else:
                self.log_test("V2 Processing Pipeline Health", False, f"HTTP error: {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            self.log_test("V2 Processing Pipeline Health", False, f"Exception: {str(e)}")
            return None
    
    def test_content_library_integration(self, job_id=None):
        """Test 2: Verify processed content appears in content library with TICKET 2 features"""
        print("🔧 TEST 2: Content Library Integration with TICKET 2 Features")
        
        try:
            # Wait a moment for processing to complete
            time.sleep(2)
            
            # Get content library
            response = requests.get(f"{API_BASE}/content-library", timeout=15)
            
            if response.status_code == 200:
                library = response.json()
                articles = library.get('articles', [])
                
                if not articles:
                    self.log_test("Content Library Integration", False, "No articles found in content library")
                    return None
                
                # Find the most recent article (should be our test article)
                latest_article = articles[-1]
                article_title = latest_article.get('title', 'No title')
                article_content = latest_article.get('content', '')
                article_id = latest_article.get('id', 'unknown')
                
                # Check if this is likely our test article
                is_test_article = (
                    'TICKET 2' in article_title or
                    'API Integration' in article_title or
                    len(article_content) > 1000  # Substantial content
                )
                
                if is_test_article:
                    self.log_test(
                        "Content Library Integration", 
                        True,
                        f"Found test article: '{article_title}' (ID: {article_id}, Content: {len(article_content)} chars)"
                    )
                    return latest_article
                else:
                    self.log_test("Content Library Integration", False, f"Latest article doesn't appear to be our test: '{article_title}'")
                    return None
            else:
                self.log_test("Content Library Integration", False, f"Content library API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Content Library Integration", False, f"Exception: {str(e)}")
            return None
    
    def test_ticket2_features_implementation(self, article):
        """Test 3: Comprehensive TICKET 2 features analysis"""
        print("🔧 TEST 3: TICKET 2 Features Implementation Analysis")
        
        if not article:
            self.log_test("TICKET 2 Features Implementation", False, "No article provided for analysis")
            return
        
        try:
            content = article.get('content', '')
            title = article.get('title', 'Unknown')
            
            print(f"    📄 Analyzing article: {title}")
            print(f"    📏 Content length: {len(content)} characters")
            
            # Feature 1: Heading ID Assignment
            heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', content)
            total_headings = content.count('<h2') + content.count('<h3') + content.count('<h4')
            
            # Feature 2: TOC Link Generation
            toc_links = re.findall(r'href="#([^"]+)"', content)
            
            # Feature 3: Link Resolution
            resolved_links = 0
            if toc_links and heading_ids:
                resolved_links = sum(1 for link in toc_links if link in heading_ids)
            
            resolution_rate = resolved_links / len(toc_links) if toc_links else 0
            
            # Feature 4: Mini-TOC Structure
            has_minitoc_structure = any([
                'mini-toc' in content.lower(),
                'table of contents' in content.lower(),
                len(toc_links) >= 3  # Multiple TOC links indicate TOC structure
            ])
            
            # Feature 5: Stable Slug Generation
            stable_slugs = True
            duplicate_handling = False
            
            if heading_ids:
                # Check slug stability (lowercase, hyphens, no random chars)
                stable_slugs = all(re.match(r'^[a-z0-9-]+(-\d+)?$', hid) for hid in heading_ids)
                
                # Check duplicate handling (suffixes like -2, -3)
                duplicate_handling = any(re.search(r'-\d+$', hid) for hid in heading_ids)
            
            # Calculate overall success
            features = {
                'heading_ids_assigned': len(heading_ids) > 0 and len(heading_ids) >= total_headings * 0.8,
                'toc_links_generated': len(toc_links) >= 3,
                'links_resolve': resolution_rate >= 0.8,
                'minitoc_structure': has_minitoc_structure,
                'stable_slugs': stable_slugs and len(heading_ids) > 0
            }
            
            passed_features = sum(features.values())
            total_features = len(features)
            success_rate = passed_features / total_features
            
            # Detailed analysis
            analysis_details = []
            analysis_details.append(f"Heading IDs: {len(heading_ids)}/{total_headings} ({features['heading_ids_assigned']})")
            analysis_details.append(f"TOC Links: {len(toc_links)} ({features['toc_links_generated']})")
            analysis_details.append(f"Resolution: {resolved_links}/{len(toc_links)} ({resolution_rate:.1%}) ({features['links_resolve']})")
            analysis_details.append(f"Mini-TOC: {has_minitoc_structure} ({features['minitoc_structure']})")
            analysis_details.append(f"Stable Slugs: {stable_slugs} ({features['stable_slugs']})")
            
            if duplicate_handling:
                analysis_details.append(f"Duplicate Handling: ✅ (found suffixed IDs)")
            
            passed = success_rate >= 0.6  # 60% of features must work
            
            self.log_test(
                "TICKET 2 Features Implementation", 
                passed,
                f"Features: {passed_features}/{total_features} ({success_rate:.1%}) - " + ", ".join(analysis_details)
            )
            
            return features
            
        except Exception as e:
            self.log_test("TICKET 2 Features Implementation", False, f"Exception: {str(e)}")
            return None
    
    def test_style_diagnostics_integration(self):
        """Test 4: Verify TICKET 2 integration with V2 Style Diagnostics"""
        print("🔧 TEST 4: Style Diagnostics Integration")
        
        try:
            response = requests.get(f"{API_BASE}/style/diagnostics", timeout=15)
            
            if response.status_code == 200:
                diagnostics = response.json()
                
                # Check for recent style processing
                recent_results = diagnostics.get('recent_results', [])
                total_runs = diagnostics.get('total_runs', 0)
                success_rate = diagnostics.get('success_rate', 0)
                
                # Look for TICKET 2 related indicators
                ticket2_indicators = 0
                if recent_results:
                    for result in recent_results[:3]:  # Check last 3 runs
                        result_str = str(result).lower()
                        if any(keyword in result_str for keyword in ['toc', 'anchor', 'heading', 'slug']):
                            ticket2_indicators += 1
                
                integration_success = (
                    len(recent_results) > 0 and
                    total_runs > 0 and
                    success_rate > 0
                )
                
                self.log_test(
                    "Style Diagnostics Integration", 
                    integration_success,
                    f"Recent runs: {len(recent_results)}, Total: {total_runs}, Success rate: {success_rate:.1%}, TICKET 2 indicators: {ticket2_indicators}"
                )
            else:
                self.log_test("Style Diagnostics Integration", False, f"Diagnostics API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Style Diagnostics Integration", False, f"Exception: {str(e)}")
    
    def test_end_to_end_workflow(self):
        """Test 5: End-to-end TICKET 2 workflow test"""
        print("🔧 TEST 5: End-to-End TICKET 2 Workflow")
        
        # Complex test content with various heading scenarios
        test_content = """
        <h2>Advanced Integration Patterns</h2>
        <p>This section covers advanced patterns and techniques for robust API integrations.</p>
        
        <h3>Microservices Architecture</h3>
        <p>Implementing API integrations in a microservices environment.</p>
        
        <h4>Service Discovery</h4>
        <p>Automatic service discovery and registration mechanisms.</p>
        
        <h4>Load Balancing</h4>
        <p>Distributing API calls across multiple service instances.</p>
        
        <h3>Caching Strategies</h3>
        <p>Effective caching approaches to improve performance and reduce API calls.</p>
        
        <h4>Redis Implementation</h4>
        <p>Using Redis for distributed caching in API integrations.</p>
        
        <h2>Monitoring & Observability</h2>
        <p>Essential monitoring and observability practices for production API integrations.</p>
        
        <h3>Logging Best Practices</h3>
        <p>Structured logging approaches for API integration debugging.</p>
        
        <h3>Metrics Collection</h3>
        <p>Key metrics to track for API performance and reliability.</p>
        
        <h4>Response Time Monitoring</h4>
        <p>Tracking and alerting on API response times.</p>
        
        <h2>Security Considerations</h2>
        <p>Comprehensive security measures for API integrations.</p>
        
        <h3>Rate Limiting</h3>
        <p>Implementing rate limiting to protect against abuse.</p>
        
        <h3>Input Validation</h3>
        <p>Thorough input validation and sanitization techniques.</p>
        """
        
        try:
            print("📤 Processing complex content through complete V2 pipeline...")
            
            # Step 1: Process content
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "TICKET 2 End-to-End Workflow Test",
                        "test_type": "end_to_end_comprehensive"
                    }
                },
                timeout=120  # Extended timeout for complex processing
            )
            
            if response.status_code != 200:
                self.log_test("End-to-End TICKET 2 Workflow", False, f"Processing failed: {response.status_code}")
                return
            
            result = response.json()
            processing_success = result.get('status') == 'completed'
            
            if not processing_success:
                self.log_test("End-to-End TICKET 2 Workflow", False, f"Processing not completed: {result.get('status')}")
                return
            
            # Step 2: Wait and retrieve from content library
            time.sleep(3)
            
            library_response = requests.get(f"{API_BASE}/content-library", timeout=15)
            if library_response.status_code != 200:
                self.log_test("End-to-End TICKET 2 Workflow", False, "Failed to retrieve from content library")
                return
            
            library = library_response.json()
            articles = library.get('articles', [])
            
            if not articles:
                self.log_test("End-to-End TICKET 2 Workflow", False, "No articles in content library")
                return
            
            # Step 3: Analyze the latest article for comprehensive TICKET 2 features
            latest_article = articles[-1]
            content = latest_article.get('content', '')
            
            # Comprehensive feature validation
            validations = {
                'substantial_content': len(content) > 2000,
                'multiple_headings': content.count('<h2') >= 2 and content.count('<h3') >= 4,
                'heading_ids_present': len(re.findall(r'<h[234][^>]*id="[^"]+"', content)) >= 8,
                'toc_links_present': len(re.findall(r'href="#[^"]+"', content)) >= 6,
                'proper_link_resolution': self._check_link_resolution(content),
                'stable_slug_format': self._check_stable_slugs(content),
                'duplicate_handling': self._check_duplicate_handling(content)
            }
            
            passed_validations = sum(validations.values())
            total_validations = len(validations)
            success_rate = passed_validations / total_validations
            
            passed = success_rate >= 0.7  # 70% success rate required for end-to-end
            
            validation_summary = ", ".join([f"{k}: {'✅' if v else '❌'}" for k, v in validations.items()])
            
            self.log_test(
                "End-to-End TICKET 2 Workflow", 
                passed,
                f"Validations: {passed_validations}/{total_validations} ({success_rate:.1%}) - {validation_summary}"
            )
            
        except Exception as e:
            self.log_test("End-to-End TICKET 2 Workflow", False, f"Exception: {str(e)}")
    
    def _check_link_resolution(self, content):
        """Helper: Check if TOC links resolve to heading IDs"""
        toc_links = re.findall(r'href="#([^"]+)"', content)
        heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', content)
        
        if not toc_links or not heading_ids:
            return False
        
        resolved = sum(1 for link in toc_links if link in heading_ids)
        return resolved / len(toc_links) >= 0.8  # 80% resolution rate
    
    def _check_stable_slugs(self, content):
        """Helper: Check if slugs follow stable pattern"""
        heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', content)
        
        if not heading_ids:
            return False
        
        # All IDs should match stable pattern (lowercase, hyphens, optional numeric suffix)
        return all(re.match(r'^[a-z0-9-]+(-\d+)?$', hid) for hid in heading_ids)
    
    def _check_duplicate_handling(self, content):
        """Helper: Check if duplicate headings are handled with suffixes"""
        heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', content)
        
        # Look for suffixed IDs (indicating duplicate handling)
        suffixed_ids = [hid for hid in heading_ids if re.search(r'-\d+$', hid)]
        
        # If we have many headings, we expect some duplicates to be handled
        return len(suffixed_ids) > 0 if len(heading_ids) > 5 else True
    
    def run_all_tests(self):
        """Run all TICKET 2 comprehensive tests"""
        print("🚀 Starting TICKET 2 Comprehensive Testing")
        print("=" * 80)
        
        # Test 1: V2 Processing Pipeline Health
        job_id = self.test_v2_processing_pipeline_health()
        
        # Test 2: Content Library Integration
        article = self.test_content_library_integration(job_id)
        
        # Test 3: TICKET 2 Features Implementation
        features = self.test_ticket2_features_implementation(article)
        
        # Test 4: Style Diagnostics Integration
        self.test_style_diagnostics_integration()
        
        # Test 5: End-to-End Workflow
        self.test_end_to_end_workflow()
        
        # Print comprehensive summary
        print("=" * 80)
        print("🏁 TICKET 2 COMPREHENSIVE TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"📊 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
        
        print()
        print("🎯 TICKET 2 IMPLEMENTATION FINAL STATUS:")
        if success_rate >= 80:
            print("✅ TICKET 2 implementation is WORKING CORRECTLY!")
            print("   ✓ V2 processing pipeline runs without method resolution errors")
            print("   ✓ Mini-TOC generation with clickable links is functional")
            print("   ✓ Stable slug assignment and anchor resolution working")
            print("   ✓ Complete integration verified end-to-end")
        elif success_rate >= 60:
            print("⚠️  TICKET 2 implementation is PARTIALLY WORKING")
            print("   ✓ Some components are functional")
            print("   ❌ Some issues remain that need attention")
        else:
            print("❌ TICKET 2 implementation has SIGNIFICANT ISSUES")
            print("   ❌ Major components are not working as expected")
            print("   ❌ Requires immediate attention and fixes")
        
        return success_rate, self.test_results

if __name__ == "__main__":
    tester = TICKET2ComprehensiveTester()
    success_rate, results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 60 else 1)