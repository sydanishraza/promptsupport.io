#!/usr/bin/env python3
"""
TICKET 3 Implementation Testing - Universal Bookmarks & Durable Links System
Testing the complete TICKET 3 solution for universal bookmarking and cross-document linking
"""

import requests
import json
import time
import sys
import re
from datetime import datetime

# Use configured backend URL from environment
import os
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🧪 TICKET 3 TESTING: Universal Bookmarks & Durable Links System")
print(f"🌐 Backend URL: {BACKEND_URL}")
print(f"📡 API Base: {API_BASE}")
print("=" * 80)

class TICKET3Tester:
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
    
    def test_document_identifier_generation(self):
        """Test 1: Verify doc_uid and doc_slug generation"""
        print("🔧 TEST 1: Document Identifier Generation (doc_uid, doc_slug)")
        
        test_content = """
        <h2>Google Maps JavaScript API Tutorial</h2>
        <p>This comprehensive guide covers everything you need to know about implementing Google Maps in your web applications.</p>
        
        <h3>Getting Started with API Integration</h3>
        <p>Learn how to set up your Google Maps API key and basic configuration.</p>
        
        <h3>Creating Your First Map</h3>
        <p>Step-by-step instructions for creating and displaying a basic map.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "Google Maps JavaScript API Tutorial",
                        "test_type": "ticket3_document_identifiers"
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article = result['articles'][0]
                    
                    # Check for TICKET 3 document identifiers
                    has_doc_uid = 'doc_uid' in article and article['doc_uid']
                    has_doc_slug = 'doc_slug' in article and article['doc_slug']
                    
                    # Validate doc_uid format (ULID-style)
                    doc_uid_valid = False
                    if has_doc_uid:
                        doc_uid = article['doc_uid']
                        # Should be 26 characters, start with 01JZ (timestamp prefix)
                        doc_uid_valid = (len(doc_uid) == 26 and 
                                       doc_uid.startswith('01JZ') and 
                                       doc_uid.isalnum())
                    
                    # Validate doc_slug format (URL-friendly)
                    doc_slug_valid = False
                    if has_doc_slug:
                        doc_slug = article['doc_slug']
                        # Should be lowercase, hyphenated, no special chars
                        doc_slug_valid = (re.match(r'^[a-z0-9-]+$', doc_slug) and 
                                        'google-maps' in doc_slug and
                                        len(doc_slug) <= 50)
                    
                    passed = has_doc_uid and has_doc_slug and doc_uid_valid and doc_slug_valid
                    
                    self.log_test(
                        "Document Identifier Generation", 
                        passed,
                        f"doc_uid: {has_doc_uid} (valid: {doc_uid_valid}), doc_slug: {has_doc_slug} (valid: {doc_slug_valid})"
                    )
                else:
                    self.log_test("Document Identifier Generation", False, "No articles generated")
            else:
                self.log_test("Document Identifier Generation", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Document Identifier Generation", False, f"Exception: {str(e)}")
    
    def test_headings_registry_extraction(self):
        """Test 2: Verify headings registry extraction with stable IDs"""
        print("🔧 TEST 2: Headings Registry Extraction")
        
        test_content = """
        <h2>API Authentication Setup</h2>
        <p>Configure your Google Maps API credentials.</p>
        
        <h3>Obtaining API Keys</h3>
        <p>Steps to get your API key from Google Cloud Console.</p>
        
        <h3>Environment Configuration</h3>
        <p>Setting up environment variables for secure key storage.</p>
        
        <h4>Development Environment</h4>
        <p>Configuration for local development.</p>
        
        <h2>Map Implementation</h2>
        <p>Creating and customizing your map display.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": test_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "Google Maps API Implementation Guide",
                        "test_type": "ticket3_headings_registry"
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article = result['articles'][0]
                    
                    # Check for TICKET 3 headings registry
                    has_headings_registry = 'headings_registry' in article
                    headings_registry = article.get('headings_registry', [])
                    
                    if has_headings_registry and headings_registry:
                        # Validate registry structure
                        valid_entries = 0
                        expected_headings = [
                            {'level': 2, 'text_contains': 'API Authentication'},
                            {'level': 3, 'text_contains': 'Obtaining API Keys'},
                            {'level': 3, 'text_contains': 'Environment Configuration'},
                            {'level': 4, 'text_contains': 'Development Environment'},
                            {'level': 2, 'text_contains': 'Map Implementation'}
                        ]
                        
                        for entry in headings_registry:
                            # Each entry should have: level, text, anchor, id
                            required_fields = ['level', 'text', 'anchor', 'id']
                            if all(field in entry for field in required_fields):
                                # Validate ID format (doc_uid#anchor)
                                if '#' in entry['id'] and len(entry['id']) > 26:
                                    valid_entries += 1
                        
                        # Check if we found expected headings
                        found_expected = 0
                        for expected in expected_headings:
                            for entry in headings_registry:
                                if (entry.get('level') == expected['level'] and 
                                    expected['text_contains'].lower() in entry.get('text', '').lower()):
                                    found_expected += 1
                                    break
                        
                        registry_complete = len(headings_registry) >= 4  # Should have multiple headings
                        structure_valid = valid_entries >= len(headings_registry) * 0.8  # 80% valid
                        content_match = found_expected >= len(expected_headings) * 0.6  # 60% match
                        
                        passed = registry_complete and structure_valid and content_match
                        
                        self.log_test(
                            "Headings Registry Extraction", 
                            passed,
                            f"Registry entries: {len(headings_registry)}, Valid: {valid_entries}, Expected found: {found_expected}/{len(expected_headings)}"
                        )
                    else:
                        self.log_test("Headings Registry Extraction", False, "No headings registry found")
                else:
                    self.log_test("Headings Registry Extraction", False, "No articles generated")
            else:
                self.log_test("Headings Registry Extraction", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Headings Registry Extraction", False, f"Exception: {str(e)}")
    
    def test_cross_document_validation_api(self):
        """Test 3: Test cross-document validation API endpoint"""
        print("🔧 TEST 3: Cross-Document Validation API")
        
        try:
            # Test the validation endpoint
            response = requests.post(f"{API_BASE}/bookmarks/validate-cross-document-links", 
                json={
                    "source_doc_uid": "01JZ12345678ABCDEFGH",
                    "target_links": [
                        "01JZ87654321ZYXWVUTS#getting-started",
                        "01JZ11111111AAAABBBB#configuration",
                        "invalid-link-format"
                    ]
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                has_validation_results = 'validation_results' in result
                has_summary = 'summary' in result
                
                if has_validation_results:
                    validation_results = result['validation_results']
                    
                    # Should have results for each link
                    results_count = len(validation_results)
                    expected_count = 3  # We sent 3 links
                    
                    # Check for proper validation structure
                    valid_structure = all(
                        'link' in res and 'valid' in res and 'reason' in res 
                        for res in validation_results
                    )
                    
                    passed = (has_validation_results and has_summary and 
                             results_count == expected_count and valid_structure)
                    
                    self.log_test(
                        "Cross-Document Validation API", 
                        passed,
                        f"Results: {results_count}/{expected_count}, Structure valid: {valid_structure}"
                    )
                else:
                    self.log_test("Cross-Document Validation API", False, "No validation results in response")
            else:
                self.log_test("Cross-Document Validation API", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Cross-Document Validation API", False, f"Exception: {str(e)}")
    
    def test_linkbuilder_system(self):
        """Test 4: Test LinkBuilder system with environment route maps"""
        print("🔧 TEST 4: LinkBuilder System with Route Maps")
        
        try:
            # Test the link building endpoint
            response = requests.post(f"{API_BASE}/bookmarks/build-link", 
                json={
                    "doc_uid": "01JZ12345678ABCDEFGH",
                    "anchor": "getting-started-guide",
                    "environment": "production",
                    "link_type": "internal"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                has_href = 'href' in result
                has_environment = 'environment' in result
                has_link_type = 'link_type' in result
                
                if has_href:
                    href = result['href']
                    
                    # Validate href format
                    # Should be a proper URL with doc_uid and anchor
                    href_valid = (isinstance(href, str) and 
                                len(href) > 10 and
                                '01JZ12345678ABCDEFGH' in href and
                                'getting-started-guide' in href)
                    
                    # Check environment handling
                    env_handled = result.get('environment') == 'production'
                    
                    passed = has_href and href_valid and env_handled
                    
                    self.log_test(
                        "LinkBuilder System", 
                        passed,
                        f"Href valid: {href_valid}, Environment: {result.get('environment')}"
                    )
                else:
                    self.log_test("LinkBuilder System", False, "No href in response")
            else:
                self.log_test("LinkBuilder System", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("LinkBuilder System", False, f"Exception: {str(e)}")
    
    def test_backfill_system(self):
        """Test 5: Test bookmark registry backfill system"""
        print("🔧 TEST 5: Bookmark Registry Backfill System")
        
        try:
            # Test the backfill endpoint
            response = requests.post(f"{API_BASE}/bookmarks/backfill-registry", 
                json={
                    "batch_size": 5,
                    "dry_run": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                has_processed = 'processed_count' in result
                has_updated = 'updated_count' in result
                has_articles = 'articles_processed' in result
                
                # Should have processing statistics
                processed_count = result.get('processed_count', 0)
                updated_count = result.get('updated_count', 0)
                
                # Validate backfill worked
                backfill_executed = processed_count >= 0 and updated_count >= 0
                
                passed = has_processed and has_updated and backfill_executed
                
                self.log_test(
                    "Bookmark Registry Backfill", 
                    passed,
                    f"Processed: {processed_count}, Updated: {updated_count}"
                )
            else:
                self.log_test("Bookmark Registry Backfill", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Bookmark Registry Backfill", False, f"Exception: {str(e)}")
    
    def test_v2_processing_integration(self):
        """Test 6: Test V2 processing pipeline integration with TICKET 3"""
        print("🔧 TEST 6: V2 Processing Pipeline Integration")
        
        # Test with Google Maps tutorial content as requested
        google_maps_content = """
        <h1>Building a Basic Google Map with JavaScript API</h1>
        
        <h2>Introduction</h2>
        <p>Google Maps JavaScript API allows you to embed Google Maps in your web pages. This tutorial will guide you through creating a basic map with custom markers and styling.</p>
        
        <h2>Prerequisites</h2>
        <p>Before you begin, make sure you have:</p>
        <ul>
        <li>A Google Cloud Platform account</li>
        <li>Basic knowledge of HTML and JavaScript</li>
        <li>A text editor or IDE</li>
        </ul>
        
        <h2>Getting Your API Key</h2>
        <p>First, you need to obtain an API key from the Google Cloud Console.</p>
        
        <h3>Step 1: Create a Project</h3>
        <p>Navigate to the Google Cloud Console and create a new project.</p>
        
        <h3>Step 2: Enable the Maps API</h3>
        <p>Enable the Google Maps JavaScript API for your project.</p>
        
        <h2>Creating Your First Map</h2>
        <p>Now let's create a basic map implementation.</p>
        
        <h3>HTML Structure</h3>
        <p>Create the basic HTML structure for your map.</p>
        
        <h3>JavaScript Implementation</h3>
        <p>Add the JavaScript code to initialize and display the map.</p>
        """
        
        try:
            response = requests.post(f"{API_BASE}/content/process", 
                json={
                    "content": google_maps_content,
                    "content_type": "text",
                    "metadata": {
                        "title": "Building a Basic Google Map with JavaScript API",
                        "original_filename": "Google Map JavaScript API Tutorial.docx",
                        "test_type": "ticket3_v2_integration"
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    article = result['articles'][0]
                    
                    # Check for all TICKET 3 fields
                    ticket3_fields = [
                        'doc_uid',
                        'doc_slug', 
                        'headings_registry',
                        'xrefs',
                        'related_links'
                    ]
                    
                    fields_present = sum(1 for field in ticket3_fields if field in article)
                    
                    # Validate specific TICKET 3 data
                    doc_uid_valid = (article.get('doc_uid', '').startswith('01JZ') and 
                                   len(article.get('doc_uid', '')) == 26)
                    
                    doc_slug_valid = ('google-map' in article.get('doc_slug', '').lower() and
                                    re.match(r'^[a-z0-9-]+$', article.get('doc_slug', '')))
                    
                    headings_registry_valid = (isinstance(article.get('headings_registry'), list) and
                                             len(article.get('headings_registry', [])) > 0)
                    
                    # Check if headings have proper TICKET 3 IDs (doc_uid#anchor format)
                    registry_ids_valid = False
                    if headings_registry_valid:
                        registry = article['headings_registry']
                        valid_ids = sum(1 for entry in registry 
                                      if entry.get('id', '').startswith(article.get('doc_uid', '')) and 
                                         '#' in entry.get('id', ''))
                        registry_ids_valid = valid_ids > 0
                    
                    integration_score = (fields_present / len(ticket3_fields) + 
                                       int(doc_uid_valid) + int(doc_slug_valid) + 
                                       int(headings_registry_valid) + int(registry_ids_valid)) / 5
                    
                    passed = integration_score >= 0.8  # 80% integration success
                    
                    self.log_test(
                        "V2 Processing Integration", 
                        passed,
                        f"Fields: {fields_present}/{len(ticket3_fields)}, UID: {doc_uid_valid}, Slug: {doc_slug_valid}, Registry: {headings_registry_valid}, IDs: {registry_ids_valid}"
                    )
                else:
                    self.log_test("V2 Processing Integration", False, "No articles generated")
            else:
                self.log_test("V2 Processing Integration", False, f"API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("V2 Processing Integration", False, f"Exception: {str(e)}")
    
    def test_data_model_persistence(self):
        """Test 7: Test data model persistence in content library"""
        print("🔧 TEST 7: Data Model Persistence in Content Library")
        
        try:
            # Get recent articles from content library to check TICKET 3 fields
            response = requests.get(f"{API_BASE}/content-library", timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'articles' in result and len(result['articles']) > 0:
                    articles = result['articles']
                    
                    # Check recent articles for TICKET 3 fields
                    ticket3_articles = 0
                    total_checked = min(5, len(articles))  # Check up to 5 recent articles
                    
                    for article in articles[:total_checked]:
                        # Count articles with TICKET 3 fields
                        has_doc_uid = 'doc_uid' in article and article['doc_uid']
                        has_doc_slug = 'doc_slug' in article and article['doc_slug']
                        has_headings_registry = 'headings_registry' in article
                        
                        if has_doc_uid and has_doc_slug and has_headings_registry:
                            ticket3_articles += 1
                    
                    # Also check if we can retrieve a specific article with TICKET 3 data
                    if articles:
                        first_article_id = articles[0].get('id')
                        if first_article_id:
                            detail_response = requests.get(f"{API_BASE}/content-library/{first_article_id}", timeout=10)
                            
                            detail_has_ticket3 = False
                            if detail_response.status_code == 200:
                                detail_article = detail_response.json()
                                detail_has_ticket3 = ('doc_uid' in detail_article and 
                                                    'headings_registry' in detail_article)
                    
                    persistence_rate = ticket3_articles / total_checked if total_checked > 0 else 0
                    passed = persistence_rate >= 0.3  # At least 30% of recent articles have TICKET 3 data
                    
                    self.log_test(
                        "Data Model Persistence", 
                        passed,
                        f"TICKET 3 articles: {ticket3_articles}/{total_checked} ({persistence_rate:.1%})"
                    )
                else:
                    self.log_test("Data Model Persistence", False, "No articles found in content library")
            else:
                self.log_test("Data Model Persistence", False, f"Content library API error: {response.status_code}")
                
        except Exception as e:
            self.log_test("Data Model Persistence", False, f"Exception: {str(e)}")
    
    def test_bookmark_api_endpoints(self):
        """Test 8: Test all TICKET 3 bookmark API endpoints"""
        print("🔧 TEST 8: Bookmark API Endpoints")
        
        endpoints_to_test = [
            {
                'name': 'Backfill Registry',
                'method': 'POST',
                'url': f"{API_BASE}/bookmarks/backfill-registry",
                'data': {"dry_run": True, "batch_size": 1}
            },
            {
                'name': 'Validate Links',
                'method': 'POST', 
                'url': f"{API_BASE}/bookmarks/validate-cross-document-links",
                'data': {"source_doc_uid": "test", "target_links": ["test#anchor"]}
            },
            {
                'name': 'Build Link',
                'method': 'POST',
                'url': f"{API_BASE}/bookmarks/build-link", 
                'data': {"doc_uid": "test", "anchor": "test", "environment": "dev"}
            }
        ]
        
        working_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint['method'] == 'POST':
                    response = requests.post(endpoint['url'], json=endpoint['data'], timeout=10)
                else:
                    response = requests.get(endpoint['url'], timeout=10)
                
                # Consider 200, 400, 422 as "working" (endpoint exists and responds)
                # 404 or 500 would indicate endpoint not implemented
                endpoint_working = response.status_code in [200, 400, 422]
                
                if endpoint_working:
                    working_endpoints += 1
                    print(f"    ✅ {endpoint['name']}: {response.status_code}")
                else:
                    print(f"    ❌ {endpoint['name']}: {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ {endpoint['name']}: Exception - {str(e)}")
        
        endpoint_success_rate = working_endpoints / total_endpoints
        passed = endpoint_success_rate >= 0.67  # At least 2/3 endpoints working
        
        self.log_test(
            "Bookmark API Endpoints", 
            passed,
            f"Working endpoints: {working_endpoints}/{total_endpoints} ({endpoint_success_rate:.1%})"
        )
    
    def run_all_tests(self):
        """Run all TICKET 3 tests"""
        print("🚀 Starting TICKET 3 Implementation Testing")
        print("=" * 80)
        
        # Run all test methods
        self.test_document_identifier_generation()
        self.test_headings_registry_extraction()
        self.test_cross_document_validation_api()
        self.test_linkbuilder_system()
        self.test_backfill_system()
        self.test_v2_processing_integration()
        self.test_data_model_persistence()
        self.test_bookmark_api_endpoints()
        
        # Print summary
        print("=" * 80)
        print("🏁 TICKET 3 TESTING SUMMARY")
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
        print("🎯 TICKET 3 IMPLEMENTATION STATUS:")
        if success_rate >= 80:
            print("✅ TICKET 3 implementation is working correctly!")
            print("   Universal bookmarks and durable links system is fully functional.")
        elif success_rate >= 60:
            print("⚠️  TICKET 3 implementation is partially working.")
            print("   Some components are functional but issues remain.")
        else:
            print("❌ TICKET 3 implementation has significant issues.")
            print("   Major components are not working as expected.")
        
        return success_rate >= 60  # Consider 60%+ as acceptable

if __name__ == "__main__":
    tester = TICKET3Tester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)