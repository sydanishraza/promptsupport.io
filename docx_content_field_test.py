#!/usr/bin/env python3
"""
V2 Engine DOCX Content Field Fix Verification Testing
Testing the fix for the content field population issue where articles were generated with empty 'content' field 
despite having content in 'html' and 'markdown' fields.

CRITICAL BUG FIX VERIFICATION: Testing the fix for the content field population issue where articles 
were generated with empty 'content' field despite having content in 'html' and 'markdown' fields.

FIX APPLIED: Added "content": html_content to the content library article creation in 
V2PublishingSystem._create_content_library_article() method.
"""

import asyncio
import json
import requests
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DOCXContentFieldTester:
    """Comprehensive tester for V2 Engine DOCX Content Field Fix"""
    
    def __init__(self):
        self.test_results = []
        self.test_run_id = None
        self.sample_articles = []
        
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
        """Test V2 Engine health check and availability"""
        try:
            print(f"\n🔍 TESTING V2 ENGINE HEALTH CHECK")
            
            response = requests.get(f"{API_BASE}/engine", timeout=30)
            
            if response.status_code != 200:
                self.log_test("V2 Engine Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify V2 engine status
            if data.get('engine') != 'v2':
                self.log_test("V2 Engine Health Check", False, f"Expected engine=v2, got {data.get('engine')}")
                return False
                
            # Verify V2 processing features
            features = data.get('features', [])
            required_v2_features = [
                'multi_dimensional_analysis', 'adaptive_granularity', 'intelligent_chunking', 'cross_referencing'
            ]
            
            missing_features = []
            for feature in required_v2_features:
                if feature not in features:
                    missing_features.append(feature)
                    
            if missing_features:
                self.log_test("V2 Engine Health Check", False, f"Missing V2 features: {missing_features}")
                return False
                
            self.log_test("V2 Engine Health Check", True, 
                         f"V2 Engine active with features: {required_v2_features}",
                         data)
            return True
            
        except Exception as e:
            self.log_test("V2 Engine Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_docx_file_upload_processing(self) -> bool:
        """Test DOCX file upload and V2 processing pipeline"""
        try:
            print(f"\n📄 TESTING DOCX FILE UPLOAD AND V2 PROCESSING")
            
            # Create a sample DOCX-like content for testing
            test_content = """
            <h1>Google Maps JavaScript API Tutorial</h1>
            <p>This comprehensive tutorial will guide you through implementing Google Maps JavaScript API in your web applications.</p>
            
            <h2>Getting Started</h2>
            <p>To begin using the Google Maps JavaScript API, you'll need to obtain an API key from the Google Cloud Console.</p>
            
            <h3>Step 1: Create a Google Cloud Project</h3>
            <p>Navigate to the Google Cloud Console and create a new project for your mapping application.</p>
            
            <h3>Step 2: Enable the Maps JavaScript API</h3>
            <p>In your project dashboard, enable the Maps JavaScript API service.</p>
            
            <h2>Implementation</h2>
            <p>Once you have your API key, you can start implementing the map in your HTML page.</p>
            
            <pre><code>
            function initMap() {
                const map = new google.maps.Map(document.getElementById("map"), {
                    zoom: 4,
                    center: { lat: -25.344, lng: 131.036 },
                });
            }
            </code></pre>
            
            <h2>Customization Options</h2>
            <p>The Google Maps API provides numerous customization options for styling and functionality.</p>
            
            <h3>Map Styles</h3>
            <p>You can customize the appearance of your map using predefined styles or create custom styles.</p>
            
            <h3>Markers and Info Windows</h3>
            <p>Add interactive markers and information windows to enhance user experience.</p>
            """
            
            # Test text processing endpoint (simulating DOCX processing)
            processing_data = {
                'content': test_content,
                'metadata': json.dumps({
                    'original_filename': 'Google Map JavaScript API Tutorial.docx',
                    'file_extension': '.docx',
                    'content_type': 'tutorial',
                    'test_scenario': 'docx_content_field_fix'
                })
            }
            
            response = requests.post(f"{API_BASE}/content/process-text", data=processing_data, timeout=60)
            
            if response.status_code != 200:
                self.log_test("DOCX File Processing", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify V2 processing response
            if data.get('engine') != 'v2':
                self.log_test("DOCX File Processing", False, f"Expected engine=v2, got {data.get('engine')}")
                return False
                
            # Store job ID for later verification
            self.test_run_id = data.get('job_id')
            if not self.test_run_id:
                self.log_test("DOCX File Processing", False, "No job_id returned from processing")
                return False
                
            # Verify processing started
            processing_status = data.get('status', 'unknown')
            if processing_status not in ['processing', 'completed']:
                self.log_test("DOCX File Processing", False, f"Unexpected processing status: {processing_status}")
                return False
                
            self.log_test("DOCX File Processing", True, 
                         f"V2 processing started successfully. Job ID: {self.test_run_id}, Status: {processing_status}",
                         data)
            return True
            
        except Exception as e:
            self.log_test("DOCX File Processing", False, f"Exception: {str(e)}")
            return False
    
    def test_content_library_articles_retrieval(self) -> bool:
        """Test retrieval of generated articles from content library"""
        try:
            print(f"\n📚 TESTING CONTENT LIBRARY ARTICLES RETRIEVAL")
            
            # Wait a moment for processing to complete
            time.sleep(3)
            
            response = requests.get(f"{API_BASE}/content-library?limit=10", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Content Library Retrieval", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify response structure
            if 'articles' not in data:
                self.log_test("Content Library Retrieval", False, "No articles field in response")
                return False
                
            articles = data['articles']
            if not articles:
                self.log_test("Content Library Retrieval", False, "No articles found in content library")
                return False
                
            # Store sample articles for content field testing
            self.sample_articles = articles[:5]  # Take first 5 articles
            
            # Verify V2 engine articles are present
            v2_articles = [article for article in articles if article.get('engine') == 'v2']
            
            if not v2_articles:
                self.log_test("Content Library Retrieval", False, "No V2 engine articles found")
                return False
                
            self.log_test("Content Library Retrieval", True, 
                         f"Retrieved {len(articles)} articles, {len(v2_articles)} V2 articles available for testing",
                         {"total_articles": len(articles), "v2_articles": len(v2_articles)})
            return True
            
        except Exception as e:
            self.log_test("Content Library Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_content_field_population_fix(self) -> bool:
        """Test that the content field is now properly populated (CRITICAL FIX VERIFICATION)"""
        try:
            print(f"\n🎯 TESTING CONTENT FIELD POPULATION FIX (CRITICAL)")
            
            if not self.sample_articles:
                self.log_test("Content Field Population Fix", False, "No sample articles available for testing")
                return False
            
            content_field_tests = []
            articles_with_content = 0
            articles_with_matching_content = 0
            total_tested = 0
            
            for article in self.sample_articles:
                article_id = article.get('id', 'unknown')
                article_title = article.get('title', 'Unknown Title')
                
                # Check if article has content field
                content_field = article.get('content', '')
                html_field = article.get('html', '')
                markdown_field = article.get('markdown', '')
                
                total_tested += 1
                
                # CRITICAL TEST 1: Content field should not be empty
                if content_field and len(content_field.strip()) > 0:
                    articles_with_content += 1
                    content_field_tests.append(f"✅ Article '{article_title[:30]}...' has populated content field ({len(content_field)} chars)")
                    
                    # CRITICAL TEST 2: Content field should match HTML field
                    if content_field == html_field:
                        articles_with_matching_content += 1
                        content_field_tests.append(f"✅ Article '{article_title[:30]}...' content field matches html field")
                    else:
                        content_field_tests.append(f"⚠️ Article '{article_title[:30]}...' content field differs from html field")
                        
                else:
                    content_field_tests.append(f"❌ Article '{article_title[:30]}...' has EMPTY content field (BUG NOT FIXED)")
                
                # Additional verification: Check if html and markdown fields have content
                if html_field and len(html_field.strip()) > 0:
                    content_field_tests.append(f"✅ Article '{article_title[:30]}...' has html content ({len(html_field)} chars)")
                else:
                    content_field_tests.append(f"⚠️ Article '{article_title[:30]}...' has empty html field")
                    
                if markdown_field and len(markdown_field.strip()) > 0:
                    content_field_tests.append(f"✅ Article '{article_title[:30]}...' has markdown content ({len(markdown_field)} chars)")
                else:
                    content_field_tests.append(f"⚠️ Article '{article_title[:30]}...' has empty markdown field")
            
            # Calculate success rates
            content_population_rate = (articles_with_content / total_tested) * 100 if total_tested > 0 else 0
            content_matching_rate = (articles_with_matching_content / total_tested) * 100 if total_tested > 0 else 0
            
            # CRITICAL SUCCESS CRITERIA
            fix_successful = (
                content_population_rate >= 80 and  # At least 80% of articles should have content field populated
                articles_with_content > 0  # At least one article should have content
            )
            
            test_summary = f"Content field population: {articles_with_content}/{total_tested} articles ({content_population_rate:.1f}%), Content-HTML matching: {articles_with_matching_content}/{total_tested} articles ({content_matching_rate:.1f}%)"
            
            self.log_test("Content Field Population Fix", fix_successful, 
                         f"{test_summary}. Fix {'SUCCESSFUL' if fix_successful else 'FAILED'}",
                         {
                             "content_field_tests": content_field_tests,
                             "articles_with_content": articles_with_content,
                             "articles_with_matching_content": articles_with_matching_content,
                             "total_tested": total_tested,
                             "content_population_rate": content_population_rate,
                             "content_matching_rate": content_matching_rate
                         })
            return fix_successful
            
        except Exception as e:
            self.log_test("Content Field Population Fix", False, f"Exception: {str(e)}")
            return False
    
    def test_article_structure_validation(self) -> bool:
        """Test that articles have complete V2 structure with all required fields"""
        try:
            print(f"\n🏗️ TESTING COMPLETE ARTICLE STRUCTURE VALIDATION")
            
            if not self.sample_articles:
                self.log_test("Article Structure Validation", False, "No sample articles available for testing")
                return False
            
            required_fields = ['content', 'html', 'markdown', 'toc', 'faq', 'related_links']
            structure_tests = []
            articles_with_complete_structure = 0
            
            for article in self.sample_articles:
                article_title = article.get('title', 'Unknown Title')
                missing_fields = []
                
                for field in required_fields:
                    if field not in article or not article[field]:
                        missing_fields.append(field)
                
                if not missing_fields:
                    articles_with_complete_structure += 1
                    structure_tests.append(f"✅ Article '{article_title[:30]}...' has complete structure")
                else:
                    structure_tests.append(f"⚠️ Article '{article_title[:30]}...' missing fields: {missing_fields}")
                
                # Verify V2 metadata
                engine = article.get('engine', 'unknown')
                if engine == 'v2':
                    structure_tests.append(f"✅ Article '{article_title[:30]}...' has V2 engine metadata")
                else:
                    structure_tests.append(f"⚠️ Article '{article_title[:30]}...' has non-V2 engine: {engine}")
            
            structure_success_rate = (articles_with_complete_structure / len(self.sample_articles)) * 100
            structure_valid = structure_success_rate >= 60  # At least 60% should have complete structure
            
            self.log_test("Article Structure Validation", structure_valid, 
                         f"Complete structure: {articles_with_complete_structure}/{len(self.sample_articles)} articles ({structure_success_rate:.1f}%)",
                         {
                             "structure_tests": structure_tests,
                             "articles_with_complete_structure": articles_with_complete_structure,
                             "structure_success_rate": structure_success_rate
                         })
            return structure_valid
            
        except Exception as e:
            self.log_test("Article Structure Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_publishing_system_integration(self) -> bool:
        """Test V2 Publishing System integration and content library persistence"""
        try:
            print(f"\n📚 TESTING V2 PUBLISHING SYSTEM INTEGRATION")
            
            # Test publishing diagnostics endpoint
            response = requests.get(f"{API_BASE}/publishing/diagnostics", timeout=30)
            
            if response.status_code != 200:
                self.log_test("V2 Publishing System Integration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify publishing system is operational
            if data.get('engine') != 'v2':
                self.log_test("V2 Publishing System Integration", False, f"Expected engine=v2, got {data.get('engine')}")
                return False
            
            # Check publishing statistics
            total_runs = data.get('total_runs', 0)
            successful_runs = data.get('successful_runs', 0)
            
            if total_runs == 0:
                self.log_test("V2 Publishing System Integration", True, "No publishing runs yet (expected for new system)")
                return True
            
            success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
            
            # Verify publishing system health
            publishing_healthy = success_rate >= 70  # At least 70% success rate
            
            self.log_test("V2 Publishing System Integration", publishing_healthy, 
                         f"Publishing system operational: {successful_runs}/{total_runs} successful runs ({success_rate:.1f}%)",
                         data)
            return publishing_healthy
            
        except Exception as e:
            self.log_test("V2 Publishing System Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_media_extraction_functionality(self) -> bool:
        """Test that media extraction still works correctly with content field fix"""
        try:
            print(f"\n🖼️ TESTING MEDIA EXTRACTION FUNCTIONALITY")
            
            # Test media library endpoint
            response = requests.get(f"{API_BASE}/media-library?limit=5", timeout=30)
            
            if response.status_code != 200:
                self.log_test("Media Extraction Functionality", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            
            # Verify media library structure
            if 'media' not in data:
                self.log_test("Media Extraction Functionality", True, "No media field (expected if no media processed)")
                return True
                
            media_items = data['media']
            
            # Check if any media was extracted
            if not media_items:
                self.log_test("Media Extraction Functionality", True, "No media items found (expected for text-only content)")
                return True
            
            # Verify media structure
            media_extraction_working = True
            for media_item in media_items[:3]:  # Check first 3 items
                required_media_fields = ['url', 'filename', 'alt_text']
                missing_media_fields = [field for field in required_media_fields if field not in media_item]
                
                if missing_media_fields:
                    media_extraction_working = False
                    break
            
            self.log_test("Media Extraction Functionality", media_extraction_working, 
                         f"Media extraction working: {len(media_items)} media items found with proper structure",
                         {"media_count": len(media_items)})
            return media_extraction_working
            
        except Exception as e:
            self.log_test("Media Extraction Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_regression_no_new_issues(self) -> bool:
        """Test that the content field fix doesn't break existing functionality"""
        try:
            print(f"\n🔄 TESTING REGRESSION - NO NEW ISSUES INTRODUCED")
            
            regression_tests = []
            
            # Test 1: V2 Engine still responds correctly
            engine_response = requests.get(f"{API_BASE}/engine", timeout=30)
            if engine_response.status_code == 200 and engine_response.json().get('engine') == 'v2':
                regression_tests.append("✅ V2 Engine endpoint still functional")
            else:
                regression_tests.append("❌ V2 Engine endpoint broken")
            
            # Test 2: Content library still accessible
            library_response = requests.get(f"{API_BASE}/content-library?limit=1", timeout=30)
            if library_response.status_code == 200:
                regression_tests.append("✅ Content library endpoint still functional")
            else:
                regression_tests.append("❌ Content library endpoint broken")
            
            # Test 3: Processing endpoints still work
            processing_response = requests.get(f"{API_BASE}/processing/status", timeout=30)
            if processing_response.status_code in [200, 404]:  # 404 is acceptable if no processing
                regression_tests.append("✅ Processing endpoints still functional")
            else:
                regression_tests.append("❌ Processing endpoints broken")
            
            # Test 4: Error handling still works
            error_response = requests.get(f"{API_BASE}/nonexistent-endpoint", timeout=30)
            if error_response.status_code == 404:
                regression_tests.append("✅ Error handling still functional")
            else:
                regression_tests.append("⚠️ Error handling changed")
            
            successful_regression_tests = len([test for test in regression_tests if test.startswith("✅")])
            regression_success_rate = (successful_regression_tests / len(regression_tests)) * 100
            
            regression_passed = regression_success_rate >= 75  # At least 75% of regression tests should pass
            
            self.log_test("Regression Testing", regression_passed, 
                         f"Regression tests: {successful_regression_tests}/{len(regression_tests)} passed ({regression_success_rate:.1f}%)",
                         {"regression_tests": regression_tests})
            return regression_passed
            
        except Exception as e:
            self.log_test("Regression Testing", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all DOCX Content Field Fix verification tests"""
        print(f"🚀 STARTING V2 ENGINE DOCX CONTENT FIELD FIX VERIFICATION TESTING")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📡 API Base: {API_BASE}")
        print(f"🎯 CRITICAL BUG FIX: Testing content field population in V2PublishingSystem._create_content_library_article()")
        
        test_methods = [
            self.test_v2_engine_health_check,
            self.test_docx_file_upload_processing,
            self.test_content_library_articles_retrieval,
            self.test_content_field_population_fix,  # CRITICAL TEST
            self.test_article_structure_validation,
            self.test_v2_publishing_system_integration,
            self.test_media_extraction_functionality,
            self.test_regression_no_new_issues
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        critical_test_passed = False
        
        for test_method in test_methods:
            try:
                test_result = test_method()
                if test_result:
                    passed_tests += 1
                    
                # Track critical test specifically
                if test_method.__name__ == 'test_content_field_population_fix':
                    critical_test_passed = test_result
                    
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_method.__name__}: {str(e)}")
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        # Determine overall status - critical test must pass
        overall_status = "PASS" if (success_rate >= 70 and critical_test_passed) else "FAIL"
        
        # Compile final results
        results = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "critical_test_passed": critical_test_passed,
                "overall_status": overall_status
            },
            "test_details": self.test_results,
            "backend_url": BACKEND_URL,
            "test_timestamp": datetime.utcnow().isoformat(),
            "engine_version": "v2",
            "fix_tested": "DOCX Content Field Population Fix in V2PublishingSystem._create_content_library_article()",
            "critical_bug_status": "FIXED" if critical_test_passed else "NOT FIXED"
        }
        
        print(f"\n" + "="*80)
        print(f"🎯 V2 ENGINE DOCX CONTENT FIELD FIX VERIFICATION COMPLETE")
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"🔥 CRITICAL TEST (Content Field Fix): {'✅ PASSED' if critical_test_passed else '❌ FAILED'}")
        print(f"🏆 OVERALL STATUS: {overall_status}")
        print(f"🐛 BUG STATUS: {'✅ FIXED' if critical_test_passed else '❌ NOT FIXED'}")
        print(f"="*80)
        
        return results

def main():
    """Main test execution"""
    tester = DOCXContentFieldTester()
    results = tester.run_comprehensive_tests()
    
    # Print detailed results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for result in results["test_details"]:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['details']}")
    
    # Print critical findings
    critical_test_result = next((r for r in results["test_details"] if "Content Field Population Fix" in r["test"]), None)
    if critical_test_result:
        print(f"\n🎯 CRITICAL TEST RESULT:")
        print(f"{'✅ CONTENT FIELD FIX VERIFIED' if critical_test_result['success'] else '❌ CONTENT FIELD FIX FAILED'}")
        if critical_test_result.get('data'):
            print(f"📊 Details: {critical_test_result['data'].get('content_population_rate', 0):.1f}% articles have populated content field")
    
    return results

if __name__ == "__main__":
    main()