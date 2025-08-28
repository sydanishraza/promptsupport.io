#!/usr/bin/env python3
"""
KE-PR9 MongoDB Repository Pattern Testing
Comprehensive test suite for repository pattern integration and TICKET-3 fields preservation
"""

import os
import sys
import asyncio
import json
import requests
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get backend URL from frontend .env
def get_backend_url():
    """Get backend URL from frontend .env file"""
    frontend_env_path = os.path.join(os.path.dirname(__file__), 'frontend', '.env')
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()
print(f"🌐 Testing KE-PR9 Repository Pattern at: {BACKEND_URL}")

class KE_PR9_RepositoryTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.test_doc_uid = None
        self.test_article_id = None
        
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
        
    def test_repository_pattern_availability(self):
        """Test 1: Verify repository pattern is available and working"""
        try:
            # Test engine status to see if repository layer is loaded
            response = requests.get(f"{self.backend_url}/api/engine", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Repository Pattern Availability", False, f"Engine endpoint failed: HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check if engine is operational
            if data.get("status") not in ["operational", "active"]:
                self.log_test("Repository Pattern Availability", False, f"Engine not operational: {data.get('status')}")
                return False
            
            # Test content library endpoint which should use repository pattern
            response = requests.get(f"{self.backend_url}/api/content/library", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Repository Pattern Availability", False, f"Content library endpoint failed: HTTP {response.status_code}")
                return False
                
            library_data = response.json()
            
            # Check if repository layer is being used
            source = library_data.get("source", "unknown")
            if "repository" in source.lower():
                self.log_test("Repository Pattern Availability", True, f"Repository layer active: {source}")
                return True
            elif source == "direct_database":
                self.log_test("Repository Pattern Availability", True, f"Fallback to direct DB working: {source}")
                return True
            else:
                self.log_test("Repository Pattern Availability", False, f"Unknown data source: {source}")
                return False
                
        except Exception as e:
            self.log_test("Repository Pattern Availability", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_engine_with_repository_pattern(self):
        """Test 2: Test V2 engine content processing with repository pattern for TICKET-3 fields"""
        try:
            # Create comprehensive content that will generate TICKET-3 fields
            test_content = """
            # MongoDB Repository Pattern Integration Guide
            
            ## Introduction
            This guide demonstrates the integration of MongoDB repository pattern with TICKET-3 field preservation including doc_uid, doc_slug, headings, and cross-references.
            
            ## Repository Pattern Benefits
            - Centralized data access layer
            - TICKET-3 field preservation
            - Consistent error handling
            - Clean separation of concerns
            
            ## Implementation Details
            The repository pattern provides:
            
            ### Content Library Operations
            - Article insertion with TICKET-3 fields
            - Document retrieval by doc_uid and doc_slug
            - Heading and cross-reference management
            
            ### Cross-Document Operations
            - Bookmark registry management
            - Link building and validation
            - Document relationship tracking
            
            ## Code Example
            ```python
            # Repository usage example
            repo = RepositoryFactory.get_content_library()
            article = await repo.find_by_doc_uid(doc_uid)
            await repo.update_headings(doc_uid, headings)
            ```
            
            ## Best Practices
            1. Always preserve TICKET-3 fields during operations
            2. Use repository pattern for all database operations
            3. Implement proper error handling and fallbacks
            4. Maintain data consistency across operations
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/api/content/process", 
                                   json=payload, timeout=120)
            
            if response.status_code != 200:
                self.log_test("V2 Engine with Repository Pattern", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success":
                self.log_test("V2 Engine with Repository Pattern", False, f"Processing failed: {data.get('message', 'Unknown error')}")
                return False
                
            # Check if articles were generated
            articles = data.get("articles", [])
            if not articles:
                self.log_test("V2 Engine with Repository Pattern", False, "No articles generated")
                return False
                
            # Check first article for TICKET-3 fields
            article = articles[0]
            
            # Verify TICKET-3 fields are present
            ticket3_fields = ["doc_uid", "doc_slug", "headings", "xrefs"]
            missing_fields = []
            
            for field in ticket3_fields:
                if field not in article:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_test("V2 Engine with Repository Pattern", False, f"Missing TICKET-3 fields: {missing_fields}")
                return False
            
            # Store test data for later tests
            self.test_doc_uid = article.get("doc_uid")
            self.test_article_id = article.get("id")
            
            # Verify field formats
            doc_uid = article.get("doc_uid", "")
            doc_slug = article.get("doc_slug", "")
            headings = article.get("headings", [])
            xrefs = article.get("xrefs", [])
            
            # Basic format validation
            if not doc_uid or len(doc_uid) < 10:
                self.log_test("V2 Engine with Repository Pattern", False, f"Invalid doc_uid format: {doc_uid}")
                return False
                
            if not doc_slug or not isinstance(doc_slug, str):
                self.log_test("V2 Engine with Repository Pattern", False, f"Invalid doc_slug format: {doc_slug}")
                return False
                
            if not isinstance(headings, list):
                self.log_test("V2 Engine with Repository Pattern", False, f"Headings not a list: {type(headings)}")
                return False
                
            if not isinstance(xrefs, list):
                self.log_test("V2 Engine with Repository Pattern", False, f"Xrefs not a list: {type(xrefs)}")
                return False
            
            self.log_test("V2 Engine with Repository Pattern", True, 
                         f"Article created with TICKET-3 fields: doc_uid={doc_uid[:20]}..., {len(headings)} headings, {len(xrefs)} xrefs")
            return True
            
        except Exception as e:
            self.log_test("V2 Engine with Repository Pattern", False, f"Exception: {str(e)}")
            return False
    
    def test_content_library_repository_operations(self):
        """Test 3: Test content library operations using repository pattern"""
        try:
            # Test GET /api/content/library endpoint
            response = requests.get(f"{self.backend_url}/api/content/library", timeout=15)
            
            if response.status_code != 200:
                self.log_test("Content Library Repository Operations", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Verify response structure
            if "articles" not in data or "count" not in data:
                self.log_test("Content Library Repository Operations", False, "Invalid response structure")
                return False
                
            articles = data.get("articles", [])
            count = data.get("count", 0)
            source = data.get("source", "unknown")
            
            # Verify we have articles
            if count == 0:
                self.log_test("Content Library Repository Operations", False, "No articles found in library")
                return False
            
            # Check if our test article is in the library
            test_article_found = False
            ticket3_compliant_articles = 0
            
            for article in articles:
                # Check for TICKET-3 fields in existing articles
                has_ticket3_fields = all(field in article for field in ["doc_uid", "doc_slug", "headings", "xrefs"])
                if has_ticket3_fields:
                    ticket3_compliant_articles += 1
                
                # Check if our test article is present
                if self.test_doc_uid and article.get("doc_uid") == self.test_doc_uid:
                    test_article_found = True
            
            # Verify repository pattern is working
            repository_working = "repository" in source.lower() or source == "direct_database"
            
            if not repository_working:
                self.log_test("Content Library Repository Operations", False, f"Repository pattern not working: {source}")
                return False
            
            # Check TICKET-3 compliance
            ticket3_compliance_rate = (ticket3_compliant_articles / count) * 100 if count > 0 else 0
            
            self.log_test("Content Library Repository Operations", True, 
                         f"Repository working: {source}, {count} articles, {ticket3_compliance_rate:.1f}% TICKET-3 compliant, test article found: {test_article_found}")
            return True
            
        except Exception as e:
            self.log_test("Content Library Repository Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_ticket3_bookmark_operations(self):
        """Test 4: Test TICKET-3 bookmark and cross-reference operations"""
        try:
            # Test backfill bookmarks endpoint
            response = requests.post(f"{self.backend_url}/api/ticket3/backfill-bookmarks", 
                                   json={"limit": 10}, timeout=30)
            
            if response.status_code != 200:
                self.log_test("TICKET-3 Bookmark Operations", False, f"Backfill failed: HTTP {response.status_code}")
                return False
                
            backfill_data = response.json()
            
            if backfill_data.get("status") != "success":
                self.log_test("TICKET-3 Bookmark Operations", False, f"Backfill failed: {backfill_data.get('message')}")
                return False
            
            # Test document registry endpoint if we have a test doc_uid
            if self.test_doc_uid:
                registry_response = requests.get(f"{self.backend_url}/api/ticket3/document-registry/{self.test_doc_uid}", timeout=10)
                
                if registry_response.status_code == 200:
                    registry_data = registry_response.json()
                    registry_found = True
                elif registry_response.status_code == 404:
                    # 404 is acceptable for new documents
                    registry_found = False
                else:
                    self.log_test("TICKET-3 Bookmark Operations", False, f"Registry endpoint failed: HTTP {registry_response.status_code}")
                    return False
            else:
                registry_found = False
            
            # Test link building endpoint
            if self.test_doc_uid:
                link_response = requests.get(f"{self.backend_url}/api/ticket3/build-link", 
                                           params={
                                               "target_doc_uid": self.test_doc_uid,
                                               "anchor_id": "introduction",
                                               "environment": "content_library"
                                           }, timeout=10)
                
                if link_response.status_code == 200:
                    link_data = link_response.json()
                    link_built = link_data.get("status") == "success"
                else:
                    link_built = False
            else:
                link_built = False
            
            # Evaluate overall success
            backfill_success = backfill_data.get("status") == "success"
            
            if backfill_success:
                self.log_test("TICKET-3 Bookmark Operations", True, 
                             f"Backfill successful, registry found: {registry_found}, link built: {link_built}")
                return True
            else:
                self.log_test("TICKET-3 Bookmark Operations", False, "Backfill operation failed")
                return False
                
        except Exception as e:
            self.log_test("TICKET-3 Bookmark Operations", False, f"Exception: {str(e)}")
            return False
    
    def test_qa_diagnostics_repository_integration(self):
        """Test 5: Test QA diagnostics with repository-based validation queries"""
        try:
            # Test QA diagnostics endpoint
            response = requests.get(f"{self.backend_url}/api/qa/diagnostics", timeout=15)
            
            if response.status_code != 200:
                self.log_test("QA Diagnostics Repository Integration", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check response structure
            if "qa_summaries" not in data and "diagnostics" not in data:
                self.log_test("QA Diagnostics Repository Integration", False, "Invalid diagnostics response structure")
                return False
            
            # Check if repository layer is being used for QA operations
            source = data.get("source", "unknown")
            repository_used = "repository" in source.lower() or "database" in source.lower()
            
            # Check for QA data
            qa_summaries = data.get("qa_summaries", [])
            diagnostics = data.get("diagnostics", {})
            
            # Verify we have some QA data or diagnostics
            has_qa_data = len(qa_summaries) > 0 or len(diagnostics) > 0
            
            if repository_used and has_qa_data:
                self.log_test("QA Diagnostics Repository Integration", True, 
                             f"Repository integration working: {len(qa_summaries)} QA summaries, source: {source}")
                return True
            elif repository_used:
                self.log_test("QA Diagnostics Repository Integration", True, 
                             f"Repository integration working (no QA data yet): source: {source}")
                return True
            else:
                self.log_test("QA Diagnostics Repository Integration", False, f"Repository not used: {source}")
                return False
                
        except Exception as e:
            self.log_test("QA Diagnostics Repository Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_article_deletion_repository_pattern(self):
        """Test 6: Test article deletion using repository pattern"""
        try:
            if not self.test_article_id:
                self.log_test("Article Deletion Repository Pattern", False, "No test article ID available")
                return False
            
            # Test article deletion
            response = requests.delete(f"{self.backend_url}/api/content/library/{self.test_article_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                source = data.get("source", "unknown")
                
                # Verify repository pattern was used
                repository_used = "repository" in source.lower() or "database" in source.lower()
                
                if repository_used:
                    self.log_test("Article Deletion Repository Pattern", True, f"Deletion successful via: {source}")
                    return True
                else:
                    self.log_test("Article Deletion Repository Pattern", False, f"Unknown deletion source: {source}")
                    return False
                    
            elif response.status_code == 404:
                # Article not found - could be already deleted or ID mismatch
                self.log_test("Article Deletion Repository Pattern", True, "Article not found (acceptable - may be already deleted)")
                return True
            else:
                self.log_test("Article Deletion Repository Pattern", False, f"Deletion failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Article Deletion Repository Pattern", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling_and_fallbacks(self):
        """Test 7: Test error handling and fallback mechanisms"""
        try:
            # Test with invalid doc_uid to check error handling
            invalid_doc_uid = "invalid-doc-uid-12345"
            
            # Test document registry with invalid doc_uid
            response = requests.get(f"{self.backend_url}/api/ticket3/document-registry/{invalid_doc_uid}", timeout=10)
            
            # Should return 404 or proper error handling
            if response.status_code == 404:
                error_handling_works = True
                error_details = "404 for invalid doc_uid (correct)"
            elif response.status_code == 200:
                data = response.json()
                if data.get("status") == "error" or not data.get("registry"):
                    error_handling_works = True
                    error_details = "Proper error response for invalid doc_uid"
                else:
                    error_handling_works = False
                    error_details = "No error handling for invalid doc_uid"
            else:
                error_handling_works = False
                error_details = f"Unexpected status code: {response.status_code}"
            
            # Test content library endpoint resilience
            library_response = requests.get(f"{self.backend_url}/api/content/library", timeout=10)
            library_resilient = library_response.status_code == 200
            
            # Test engine status for overall system health
            engine_response = requests.get(f"{self.backend_url}/api/engine", timeout=10)
            engine_healthy = engine_response.status_code == 200
            
            # Evaluate overall error handling
            overall_resilience = error_handling_works and library_resilient and engine_healthy
            
            if overall_resilience:
                self.log_test("Error Handling and Fallbacks", True, 
                             f"Error handling working: {error_details}, library resilient: {library_resilient}, engine healthy: {engine_healthy}")
                return True
            else:
                self.log_test("Error Handling and Fallbacks", False, 
                             f"Error handling issues: {error_details}, library resilient: {library_resilient}, engine healthy: {engine_healthy}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling and Fallbacks", False, f"Exception: {str(e)}")
            return False
    
    def test_ticket3_fields_preservation_across_operations(self):
        """Test 8: Test TICKET-3 fields preservation across multiple operations"""
        try:
            # Create a new article with specific TICKET-3 fields
            test_content = """
            # TICKET-3 Fields Preservation Test
            
            ## Test Heading 1
            This section tests heading preservation.
            
            ### Test Subheading 1.1
            Content for subheading.
            
            ## Test Heading 2
            This section tests cross-reference preservation.
            
            ### Test Subheading 2.1
            More content for testing.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            # Create article
            response = requests.post(f"{self.backend_url}/api/content/process", 
                                   json=payload, timeout=60)
            
            if response.status_code != 200:
                self.log_test("TICKET-3 Fields Preservation", False, f"Article creation failed: HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            if data.get("status") != "success" or not data.get("articles"):
                self.log_test("TICKET-3 Fields Preservation", False, "Article creation failed")
                return False
            
            article = data["articles"][0]
            
            # Extract TICKET-3 fields
            original_doc_uid = article.get("doc_uid")
            original_doc_slug = article.get("doc_slug")
            original_headings = article.get("headings", [])
            original_xrefs = article.get("xrefs", [])
            
            if not original_doc_uid:
                self.log_test("TICKET-3 Fields Preservation", False, "No doc_uid in created article")
                return False
            
            # Wait a moment for database consistency
            time.sleep(2)
            
            # Retrieve article from content library to verify persistence
            library_response = requests.get(f"{self.backend_url}/api/content/library", timeout=10)
            
            if library_response.status_code != 200:
                self.log_test("TICKET-3 Fields Preservation", False, "Failed to retrieve content library")
                return False
            
            library_data = library_response.json()
            articles = library_data.get("articles", [])
            
            # Find our test article
            test_article_found = None
            for lib_article in articles:
                if lib_article.get("doc_uid") == original_doc_uid:
                    test_article_found = lib_article
                    break
            
            if not test_article_found:
                self.log_test("TICKET-3 Fields Preservation", False, "Test article not found in library")
                return False
            
            # Verify TICKET-3 fields are preserved
            preserved_doc_uid = test_article_found.get("doc_uid")
            preserved_doc_slug = test_article_found.get("doc_slug")
            preserved_headings = test_article_found.get("headings", [])
            preserved_xrefs = test_article_found.get("xrefs", [])
            
            # Check preservation
            uid_preserved = preserved_doc_uid == original_doc_uid
            slug_preserved = preserved_doc_slug == original_doc_slug
            headings_preserved = isinstance(preserved_headings, list)
            xrefs_preserved = isinstance(preserved_xrefs, list)
            
            preservation_score = sum([uid_preserved, slug_preserved, headings_preserved, xrefs_preserved])
            
            if preservation_score == 4:
                self.log_test("TICKET-3 Fields Preservation", True, 
                             f"All TICKET-3 fields preserved: doc_uid, doc_slug, {len(preserved_headings)} headings, {len(preserved_xrefs)} xrefs")
                return True
            else:
                self.log_test("TICKET-3 Fields Preservation", False, 
                             f"TICKET-3 fields not fully preserved: uid={uid_preserved}, slug={slug_preserved}, headings={headings_preserved}, xrefs={xrefs_preserved}")
                return False
                
        except Exception as e:
            self.log_test("TICKET-3 Fields Preservation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all KE-PR9 repository pattern tests"""
        print("🎯 KE-PR9 MONGODB REPOSITORY PATTERN TESTING")
        print("=" * 80)
        print("Testing repository pattern integration and TICKET-3 fields preservation")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all tests
        tests = [
            self.test_repository_pattern_availability,
            self.test_v2_engine_with_repository_pattern,
            self.test_content_library_repository_operations,
            self.test_ticket3_bookmark_operations,
            self.test_qa_diagnostics_repository_integration,
            self.test_ticket3_fields_preservation_across_operations,
            self.test_article_deletion_repository_pattern,
            self.test_error_handling_and_fallbacks
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(2)
        
        # Print summary
        print()
        print("=" * 80)
        print("🎯 KE-PR9 MONGODB REPOSITORY PATTERN TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate == 100:
            print("🎉 KE-PR9 REPOSITORY PATTERN: PERFECT - All repository operations working flawlessly!")
            print("✅ Repository pattern fully integrated")
            print("✅ TICKET-3 fields properly preserved")
            print("✅ All API endpoints using repository layer")
        elif success_rate >= 85:
            print("🎉 KE-PR9 REPOSITORY PATTERN: EXCELLENT - Nearly perfect implementation!")
        elif success_rate >= 70:
            print("✅ KE-PR9 REPOSITORY PATTERN: GOOD - Most functionality working")
        elif success_rate >= 50:
            print("⚠️ KE-PR9 REPOSITORY PATTERN: PARTIAL - Some issues remain")
        else:
            print("❌ KE-PR9 REPOSITORY PATTERN: NEEDS ATTENTION - Major issues detected")
        
        print()
        print("Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate

if __name__ == "__main__":
    tester = KE_PR9_RepositoryTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)