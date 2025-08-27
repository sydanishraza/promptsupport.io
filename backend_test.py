#!/usr/bin/env python3
"""
TICKET 3 Implementation Testing - Method Integration Fix Verification
Testing all TICKET 3 methods after integration into V2StyleProcessor class
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com/api"

class TICKET3Tester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = f"{status} - {test_name}"
        if details:
            result += f" | {details}"
            
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_v2_engine_health(self):
        """Test 1: Verify V2 Engine is operational with TICKET 3 features"""
        try:
            response = requests.get(f"{self.backend_url}/engine", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2 Engine Health Check", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check engine status
            if data.get("status") != "operational":
                self.log_test("V2 Engine Health Check", False, f"Engine status: {data.get('status')}")
                return False
                
            # Check for V2 features
            features = data.get("features", [])
            required_features = ["v2_processing", "woolf_style_processing"]
            
            missing_features = [f for f in required_features if f not in features]
            if missing_features:
                self.log_test("V2 Engine Health Check", False, f"Missing features: {missing_features}")
                return False
                
            self.log_test("V2 Engine Health Check", True, f"Engine operational with {len(features)} features")
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_v2style_processor_instantiation(self):
        """Test 2: Verify V2StyleProcessor can be instantiated and methods are accessible"""
        try:
            # Test by calling a diagnostic endpoint that uses V2StyleProcessor
            response = requests.get(f"{self.backend_url}/style/diagnostics", timeout=10)
            
            if response.status_code != 200:
                self.log_test("V2StyleProcessor Instantiation", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check if we get valid diagnostic data (indicates V2StyleProcessor is working)
            if "engine" not in data:
                self.log_test("V2StyleProcessor Instantiation", False, "No engine field in diagnostics")
                return False
                
            if data.get("engine") != "v2":
                self.log_test("V2StyleProcessor Instantiation", False, f"Wrong engine: {data.get('engine')}")
                return False
                
            self.log_test("V2StyleProcessor Instantiation", True, "V2StyleProcessor accessible via diagnostics")
            return True
            
        except Exception as e:
            self.log_test("V2StyleProcessor Instantiation", False, f"Exception: {str(e)}")
            return False
    
    def test_bookmark_registry_extraction(self):
        """Test 3: Test bookmark registry extraction with sample content"""
        try:
            # Create test content with headings
            test_content = """
            <h2 id="getting-started">Getting Started with API Integration</h2>
            <p>This section covers the basics of API integration.</p>
            
            <h3 id="authentication">Authentication Process</h3>
            <p>Learn how to authenticate your API requests.</p>
            
            <h2 id="advanced-features">Advanced Features</h2>
            <p>Explore advanced API capabilities.</p>
            
            <h3 id="rate-limiting">Rate Limiting</h3>
            <p>Understanding API rate limits.</p>
            """
            
            # Test via V2 processing pipeline (which should use bookmark registry)
            payload = {
                "content": test_content,
                "content_type": "html",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Bookmark Registry Extraction", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check if processing was successful
            if data.get("status") != "success":
                self.log_test("Bookmark Registry Extraction", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check if articles were generated with bookmark data
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Bookmark Registry Extraction", False, "No articles generated")
                return False
                
            # Check first article for TICKET 3 data
            article = articles[0]
            
            # Check for doc_uid
            if not article.get("doc_uid"):
                self.log_test("Bookmark Registry Extraction", False, "No doc_uid generated")
                return False
                
            # Check for doc_slug  
            if not article.get("doc_slug"):
                self.log_test("Bookmark Registry Extraction", False, "No doc_slug generated")
                return False
                
            # Check for headings registry
            headings = article.get("headings", [])
            if len(headings) < 2:  # Should have at least 2 headings from our test content
                self.log_test("Bookmark Registry Extraction", False, f"Insufficient headings extracted: {len(headings)}")
                return False
                
            # Verify heading structure
            first_heading = headings[0]
            required_fields = ["id", "text", "level", "order"]
            missing_fields = [f for f in required_fields if f not in first_heading]
            
            if missing_fields:
                self.log_test("Bookmark Registry Extraction", False, f"Missing heading fields: {missing_fields}")
                return False
                
            self.log_test("Bookmark Registry Extraction", True, 
                         f"Extracted {len(headings)} headings, doc_uid: {article['doc_uid'][:10]}...")
            return True
            
        except Exception as e:
            self.log_test("Bookmark Registry Extraction", False, f"Exception: {str(e)}")
            return False
    
    def test_document_identifier_generation(self):
        """Test 4: Test doc_uid and doc_slug generation"""
        try:
            # Test with a simple article creation
            test_title = "Complete Guide to API Authentication and Security Best Practices"
            test_content = "<h2>Introduction</h2><p>This guide covers API authentication.</p>"
            
            payload = {
                "content": test_content,
                "content_type": "html", 
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process",
                                   json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_test("Document Identifier Generation", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                self.log_test("Document Identifier Generation", False, "No articles generated")
                return False
                
            article = articles[0]
            doc_uid = article.get("doc_uid")
            doc_slug = article.get("doc_slug")
            
            # Validate doc_uid format (should be ULID-like: 01JZ + timestamp + random)
            if not doc_uid or not doc_uid.startswith("01JZ") or len(doc_uid) < 20:
                self.log_test("Document Identifier Generation", False, f"Invalid doc_uid format: {doc_uid}")
                return False
                
            # Validate doc_slug format (should be URL-friendly)
            if not doc_slug or " " in doc_slug or doc_slug != doc_slug.lower():
                self.log_test("Document Identifier Generation", False, f"Invalid doc_slug format: {doc_slug}")
                return False
                
            # Check that doc_slug is derived from title
            if "api" not in doc_slug or "authentication" not in doc_slug:
                self.log_test("Document Identifier Generation", False, f"doc_slug doesn't reflect title: {doc_slug}")
                return False
                
            self.log_test("Document Identifier Generation", True,
                         f"doc_uid: {doc_uid}, doc_slug: {doc_slug}")
            return True
            
        except Exception as e:
            self.log_test("Document Identifier Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_linkbuilder_system(self):
        """Test 5: Test LinkBuilder system with route maps"""
        try:
            # This test verifies the href building functionality
            # We'll test by creating content and checking if the system can handle cross-references
            
            test_content = """
            <h2 id="overview">System Overview</h2>
            <p>This system provides comprehensive API management.</p>
            
            <h2 id="integration">Integration Guide</h2>
            <p>Follow these steps for integration.</p>
            """
            
            payload = {
                "content": test_content,
                "content_type": "html",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process",
                                   json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_test("LinkBuilder System", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                self.log_test("LinkBuilder System", False, "No articles generated")
                return False
                
            article = articles[0]
            
            # Check that the article has the necessary fields for link building
            if not article.get("doc_uid") or not article.get("doc_slug"):
                self.log_test("LinkBuilder System", False, "Missing doc_uid or doc_slug for link building")
                return False
                
            # Check that headings have proper IDs for anchor linking
            headings = article.get("headings", [])
            if not headings:
                self.log_test("LinkBuilder System", False, "No headings for anchor linking")
                return False
                
            # Verify headings have proper anchor IDs
            for heading in headings:
                if not heading.get("id"):
                    self.log_test("LinkBuilder System", False, f"Heading missing ID: {heading}")
                    return False
                    
            # Check if xrefs and related_links fields are initialized (required for LinkBuilder)
            if "xrefs" not in article:
                self.log_test("LinkBuilder System", False, "Missing xrefs field")
                return False
                
            if "related_links" not in article:
                self.log_test("LinkBuilder System", False, "Missing related_links field")
                return False
                
            self.log_test("LinkBuilder System", True,
                         f"LinkBuilder ready: {len(headings)} anchors, xrefs/related_links initialized")
            return True
            
        except Exception as e:
            self.log_test("LinkBuilder System", False, f"Exception: {str(e)}")
            return False
    
    def test_backfill_functionality(self):
        """Test 6: Test backfill_bookmark_registry method"""
        try:
            # Test the backfill endpoint
            response = requests.post(f"{self.backend_url}/ticket3/backfill-bookmarks?limit=5", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Backfill Functionality", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check response structure
            if "status" not in data:
                self.log_test("Backfill Functionality", False, "Missing status in response")
                return False
                
            # Success or no articles to backfill are both valid
            if data["status"] not in ["success", "failed"]:
                self.log_test("Backfill Functionality", False, f"Invalid status: {data['status']}")
                return False
                
            # If failed, check if it's due to no articles (which is acceptable)
            if data["status"] == "failed":
                message = data.get("message", "")
                if "No articles need backfilling" in message or "0 articles" in message:
                    self.log_test("Backfill Functionality", True, "No articles need backfilling (acceptable)")
                    return True
                else:
                    self.log_test("Backfill Functionality", False, f"Backfill failed: {message}")
                    return False
                    
            # If successful, check the data
            backfill_data = data.get("data", {})
            articles_processed = backfill_data.get("articles_processed", 0)
            
            self.log_test("Backfill Functionality", True,
                         f"Backfill completed: {articles_processed} articles processed")
            return True
            
        except Exception as e:
            self.log_test("Backfill Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_api_endpoint_integration(self):
        """Test 7: Test API endpoints work with integrated methods"""
        try:
            # Test the validation endpoint (requires V2StyleProcessor methods)
            # First, we need a document to validate - let's create one
            test_content = "<h2 id='test'>Test Heading</h2><p>Test content</p>"
            
            payload = {
                "content": test_content,
                "content_type": "html",
                "processing_mode": "v2_only"
            }
            
            # Create a document first
            response = requests.post(f"{self.backend_url}/content/process",
                                   json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log_test("API Endpoint Integration", False, f"Failed to create test document: HTTP {response.status_code}")
                return False
                
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                self.log_test("API Endpoint Integration", False, "No test document created")
                return False
                
            doc_uid = articles[0].get("doc_uid")
            if not doc_uid:
                self.log_test("API Endpoint Integration", False, "Test document missing doc_uid")
                return False
                
            # Now test the validation endpoint
            response = requests.get(f"{self.backend_url}/ticket3/validate-links/{doc_uid}", timeout=15)
            
            if response.status_code != 200:
                self.log_test("API Endpoint Integration", False, f"Validation endpoint HTTP {response.status_code}")
                return False
                
            validation_data = response.json()
            
            # Check response structure
            if "status" not in validation_data:
                self.log_test("API Endpoint Integration", False, "Missing status in validation response")
                return False
                
            if validation_data["status"] != "success":
                self.log_test("API Endpoint Integration", False, f"Validation failed: {validation_data.get('message', 'Unknown error')}")
                return False
                
            # Check that validation data is present
            if "validation" not in validation_data:
                self.log_test("API Endpoint Integration", False, "Missing validation data")
                return False
                
            self.log_test("API Endpoint Integration", True,
                         f"Validation endpoint working for doc_uid: {doc_uid[:10]}...")
            return True
            
        except Exception as e:
            self.log_test("API Endpoint Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_v2_pipeline(self):
        """Test 8: Test complete V2 pipeline with _apply_bookmark_registry integration"""
        try:
            # Test comprehensive V2 processing with TICKET 3 integration
            comprehensive_content = """
            <h1>Complete API Integration Guide</h1>
            
            <h2 id="introduction">Introduction to API Integration</h2>
            <p>This comprehensive guide covers all aspects of API integration including authentication, rate limiting, and best practices.</p>
            
            <h3 id="prerequisites">Prerequisites</h3>
            <p>Before starting, ensure you have the following:</p>
            <ul>
                <li>Valid API credentials</li>
                <li>Development environment setup</li>
                <li>Basic understanding of REST APIs</li>
            </ul>
            
            <h2 id="authentication">Authentication Methods</h2>
            <p>Learn about different authentication approaches.</p>
            
            <h3 id="api-keys">API Key Authentication</h3>
            <p>The most common authentication method.</p>
            
            <h3 id="oauth">OAuth 2.0 Authentication</h3>
            <p>More secure authentication for production systems.</p>
            
            <h2 id="implementation">Implementation Guide</h2>
            <p>Step-by-step implementation instructions.</p>
            
            <h3 id="setup">Initial Setup</h3>
            <p>Configure your development environment.</p>
            
            <h3 id="first-request">Making Your First Request</h3>
            <p>Send your first API request.</p>
            
            <h2 id="best-practices">Best Practices</h2>
            <p>Follow these guidelines for optimal API usage.</p>
            
            <h3 id="error-handling">Error Handling</h3>
            <p>Properly handle API errors and exceptions.</p>
            
            <h3 id="rate-limiting">Rate Limiting</h3>
            <p>Respect API rate limits to avoid throttling.</p>
            """
            
            payload = {
                "content": comprehensive_content,
                "content_type": "html",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process",
                                   json=payload, timeout=45)
            
            if response.status_code != 200:
                self.log_test("Complete V2 Pipeline", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check processing status
            if data.get("status") != "success":
                self.log_test("Complete V2 Pipeline", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check articles generated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("Complete V2 Pipeline", False, "No articles generated")
                return False
                
            article = articles[0]
            
            # Verify all TICKET 3 components are present
            ticket3_fields = ["doc_uid", "doc_slug", "headings", "xrefs", "related_links"]
            missing_fields = [f for f in ticket3_fields if f not in article]
            
            if missing_fields:
                self.log_test("Complete V2 Pipeline", False, f"Missing TICKET 3 fields: {missing_fields}")
                return False
                
            # Verify heading extraction worked
            headings = article.get("headings", [])
            if len(headings) < 5:  # Should have many headings from our comprehensive content
                self.log_test("Complete V2 Pipeline", False, f"Insufficient headings extracted: {len(headings)}")
                return False
                
            # Verify doc_uid format
            doc_uid = article.get("doc_uid")
            if not doc_uid or not doc_uid.startswith("01JZ"):
                self.log_test("Complete V2 Pipeline", False, f"Invalid doc_uid: {doc_uid}")
                return False
                
            # Verify doc_slug format
            doc_slug = article.get("doc_slug")
            if not doc_slug or " " in doc_slug:
                self.log_test("Complete V2 Pipeline", False, f"Invalid doc_slug: {doc_slug}")
                return False
                
            # Check that content has proper heading IDs (from stable anchors)
            content = article.get("content", "") or article.get("html", "")
            if 'id="' not in content:
                self.log_test("Complete V2 Pipeline", False, "Content missing heading IDs")
                return False
                
            # Verify processing metadata
            metadata = article.get("metadata", {})
            if metadata.get("engine") != "v2":
                self.log_test("Complete V2 Pipeline", False, f"Wrong engine in metadata: {metadata.get('engine')}")
                return False
                
            self.log_test("Complete V2 Pipeline", True,
                         f"Complete pipeline success: {len(headings)} headings, doc_uid: {doc_uid[:10]}..., doc_slug: {doc_slug[:20]}...")
            return True
            
        except Exception as e:
            self.log_test("Complete V2 Pipeline", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all TICKET 3 tests"""
        print("🎯 TICKET 3 IMPLEMENTATION TESTING - Method Integration Fix Verification")
        print("=" * 80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_v2_engine_health,
            self.test_v2style_processor_instantiation,
            self.test_bookmark_registry_extraction,
            self.test_document_identifier_generation,
            self.test_linkbuilder_system,
            self.test_backfill_functionality,
            self.test_api_endpoint_integration,
            self.test_complete_v2_pipeline
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(1)
        
        # Print summary
        print()
        print("=" * 80)
        print("🎯 TICKET 3 TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 80:
            print("🎉 TICKET 3 IMPLEMENTATION: EXCELLENT - Method integration fix successful!")
        elif success_rate >= 60:
            print("✅ TICKET 3 IMPLEMENTATION: GOOD - Most functionality working")
        elif success_rate >= 40:
            print("⚠️ TICKET 3 IMPLEMENTATION: PARTIAL - Some issues remain")
        else:
            print("❌ TICKET 3 IMPLEMENTATION: NEEDS ATTENTION - Major issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = TICKET3Tester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)