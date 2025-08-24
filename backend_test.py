#!/usr/bin/env python3
"""
V2 Engine Code Normalization System Comprehensive Testing
Testing V2 Engine Code Normalization System to verify Prism-ready HTML generation
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://content-pipeline-5.preview.emergentagent.com/api"

class V2RelatedLinksSystemTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        self.test_results["total_tests"] += 1
        if passed:
            self.test_results["passed_tests"] += 1
            status = "✅ PASSED"
        else:
            self.test_results["failed_tests"] += 1
            status = "❌ FAILED"
            
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
            
        self.test_results["test_details"].append({
            "test_name": test_name,
            "status": "passed" if passed else "failed",
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_v2_engine_health_check(self):
        """Test V2 Engine health check with related links endpoints"""
        try:
            print("\n🔍 TESTING: V2 Engine Health Check with Related Links Endpoints")
            
            response = requests.get(f"{self.backend_url}/engine")
            
            if response.status_code == 200:
                engine_data = response.json()
                
                # Check engine status
                engine_status = engine_data.get('engine')
                if engine_status == 'v2':
                    self.log_test("V2 Engine Status Check", True, f"Engine status: {engine_status}")
                else:
                    self.log_test("V2 Engine Status Check", False, f"Expected 'v2', got: {engine_status}")
                    return False
                
                # Check related links endpoints
                endpoints = engine_data.get('endpoints', {})
                required_endpoints = [
                    'related_links_diagnostics'
                ]
                
                missing_endpoints = []
                for endpoint in required_endpoints:
                    if endpoint not in endpoints:
                        missing_endpoints.append(endpoint)
                
                if not missing_endpoints:
                    self.log_test("Related Links Endpoints Check", True, f"All required endpoints present: {required_endpoints}")
                else:
                    self.log_test("Related Links Endpoints Check", False, f"Missing endpoints: {missing_endpoints}")
                    return False
                
                # Check related links features
                features = engine_data.get('features', [])
                required_features = [
                    'content_library_indexing',
                    'similarity_matching',
                    'internal_links_discovery',
                    'external_links_extraction'
                ]
                
                missing_features = []
                for feature in required_features:
                    if feature not in features:
                        missing_features.append(feature)
                
                if not missing_features:
                    self.log_test("Related Links Features Check", True, f"All required features present: {required_features}")
                else:
                    self.log_test("Related Links Features Check", False, f"Missing features: {missing_features}")
                    return False
                
                return True
            else:
                self.log_test("V2 Engine Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("V2 Engine Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_seed_articles_creation(self):
        """Test seed articles creation for similarity testing"""
        try:
            print("\n🌱 TESTING: Seed Articles Creation")
            
            response = requests.post(f"{self.backend_url}/seed/create-test-articles")
            
            if response.status_code == 200:
                seed_data = response.json()
                
                # Check seed creation status
                status = seed_data.get('status')
                if status == 'success':
                    self.log_test("Seed Articles Creation Status", True, f"Status: {status}")
                else:
                    self.log_test("Seed Articles Creation Status", False, f"Expected 'success', got: {status}")
                    return False
                
                # Check articles created
                articles_created = seed_data.get('articles_created', 0)
                if articles_created >= 5:
                    self.log_test("Seed Articles Count", True, f"Created {articles_created} articles")
                else:
                    self.log_test("Seed Articles Count", False, f"Expected >= 5 articles, got: {articles_created}")
                    return False
                
                # Check article titles
                article_titles = seed_data.get('article_titles', [])
                expected_titles = [
                    'Integration Process',
                    'API Integration', 
                    'Getting Started',
                    'Error Handling',
                    'Whisk Studio'
                ]
                
                found_titles = 0
                for expected in expected_titles:
                    for actual in article_titles:
                        if expected.lower() in actual.lower():
                            found_titles += 1
                            break
                
                if found_titles >= 4:
                    self.log_test("Seed Articles Titles Check", True, f"Found {found_titles}/5 expected titles")
                else:
                    self.log_test("Seed Articles Titles Check", False, f"Only found {found_titles}/5 expected titles")
                    return False
                
                return True
            else:
                self.log_test("Seed Articles Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Seed Articles Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_content_library_indexing(self):
        """Test content library indexing functionality"""
        try:
            print("\n🔍 TESTING: Content Library Indexing")
            
            response = requests.get(f"{self.backend_url}/related-links/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                
                # Check content library status
                content_library_status = diagnostics_data.get('content_library_status', {})
                
                # Check indexing enabled
                indexing_enabled = content_library_status.get('indexing_enabled')
                if indexing_enabled:
                    self.log_test("Content Library Indexing Enabled", True, "Indexing is enabled")
                else:
                    self.log_test("Content Library Indexing Enabled", False, "Indexing is not enabled")
                    return False
                
                # Check similarity method
                similarity_method = content_library_status.get('similarity_method')
                if similarity_method == 'keyword_and_semantic':
                    self.log_test("Similarity Method Check", True, f"Method: {similarity_method}")
                else:
                    self.log_test("Similarity Method Check", False, f"Expected 'keyword_and_semantic', got: {similarity_method}")
                    return False
                
                # Check articles indexed
                articles_indexed = content_library_status.get('articles_indexed', 0)
                if articles_indexed >= 5:
                    self.log_test("Articles Indexed Count", True, f"Indexed {articles_indexed} articles")
                else:
                    self.log_test("Articles Indexed Count", False, f"Expected >= 5 articles, got: {articles_indexed}")
                    return False
                
                # Check last index update
                last_update = content_library_status.get('last_index_update')
                if last_update:
                    self.log_test("Index Update Timestamp", True, f"Last update: {last_update}")
                else:
                    self.log_test("Index Update Timestamp", False, "No index update timestamp found")
                    return False
                
                return True
            else:
                self.log_test("Content Library Indexing", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Content Library Indexing", False, f"Exception: {str(e)}")
            return False
    
    def test_related_links_diagnostics(self):
        """Test related links diagnostic endpoints"""
        try:
            print("\n📊 TESTING: Related Links Diagnostic Endpoints")
            
            # Test main diagnostics endpoint
            response = requests.get(f"{self.backend_url}/related-links/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                
                # Check system status
                system_status = diagnostics_data.get('related_links_system_status')
                if system_status == 'active':
                    self.log_test("Related Links System Status", True, f"Status: {system_status}")
                else:
                    self.log_test("Related Links System Status", False, f"Expected 'active', got: {system_status}")
                    return False
                
                # Check engine
                engine = diagnostics_data.get('engine')
                if engine == 'v2':
                    self.log_test("Related Links Engine Check", True, f"Engine: {engine}")
                else:
                    self.log_test("Related Links Engine Check", False, f"Expected 'v2', got: {engine}")
                    return False
                
                # Check summary statistics
                summary = diagnostics_data.get('related_links_summary', {})
                total_runs = summary.get('total_related_links_runs', 0)
                
                if total_runs >= 0:
                    self.log_test("Related Links Summary Statistics", True, f"Total runs: {total_runs}")
                else:
                    self.log_test("Related Links Summary Statistics", False, "No summary statistics found")
                    return False
                
                # Check recent results structure
                recent_results = diagnostics_data.get('recent_related_links_results', [])
                if isinstance(recent_results, list):
                    self.log_test("Recent Results Structure", True, f"Found {len(recent_results)} recent results")
                else:
                    self.log_test("Recent Results Structure", False, "Recent results not in list format")
                    return False
                
                return True
            else:
                self.log_test("Related Links Diagnostics", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Related Links Diagnostics", False, f"Exception: {str(e)}")
            return False
    
    def test_content_processing_with_related_links(self):
        """Test content processing with related links generation (Step 7.7)"""
        try:
            print("\n🔗 TESTING: Content Processing with Related Links Generation")
            
            # Test content for processing
            test_content = """
            # Google Maps JavaScript API Integration Guide
            
            This comprehensive guide covers Google Maps API integration with JavaScript applications.
            
            ## Getting Started with Maps API
            Learn how to set up your development environment and obtain API keys.
            
            ## Authentication and API Keys
            Secure your API integration with proper authentication methods.
            
            ## Error Handling Best Practices
            Implement robust error handling for production applications.
            """
            
            # Process content through V2 engine
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json={"content": test_content})
            
            if response.status_code == 200:
                process_data = response.json()
                
                # Check processing status
                status = process_data.get('status')
                if status == 'completed':
                    self.log_test("Content Processing Status", True, f"Status: {status}")
                else:
                    self.log_test("Content Processing Status", False, f"Expected 'completed', got: {status}")
                    return False
                
                # Check engine confirmation
                engine = process_data.get('engine')
                if engine == 'v2':
                    self.log_test("Processing Engine Check", True, f"Engine: {engine}")
                else:
                    self.log_test("Processing Engine Check", False, f"Expected 'v2', got: {engine}")
                    return False
                
                # Check job ID for further testing
                job_id = process_data.get('job_id')
                if job_id:
                    self.log_test("Job ID Generation", True, f"Job ID: {job_id}")
                    
                    # Wait a moment for processing to complete
                    time.sleep(2)
                    
                    # Check if related links were generated
                    return self.verify_related_links_generation(job_id)
                else:
                    self.log_test("Job ID Generation", False, "No job ID returned")
                    return False
                
            else:
                self.log_test("Content Processing", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Content Processing with Related Links", False, f"Exception: {str(e)}")
            return False
    
    def verify_related_links_generation(self, job_id):
        """Verify related links were generated for processed content"""
        try:
            print(f"\n🔍 VERIFYING: Related Links Generation for Job {job_id}")
            
            # Check diagnostics for recent related links results
            response = requests.get(f"{self.backend_url}/related-links/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                recent_results = diagnostics_data.get('recent_related_links_results', [])
                
                # Look for results from our job
                job_results = [r for r in recent_results if r.get('run_id') == job_id]
                
                if job_results:
                    result = job_results[0]
                    
                    # Check related links status
                    status = result.get('related_links_status')
                    if status == 'success':
                        self.log_test("Related Links Generation Status", True, f"Status: {status}")
                    else:
                        self.log_test("Related Links Generation Status", False, f"Expected 'success', got: {status}")
                        return False
                    
                    # Check links counts
                    internal_count = result.get('internal_links_count', 0)
                    external_count = result.get('external_links_count', 0)
                    total_count = result.get('total_links_count', 0)
                    
                    if total_count >= 3:
                        self.log_test("Related Links Count Check", True, f"Total: {total_count} (Internal: {internal_count}, External: {external_count})")
                    else:
                        self.log_test("Related Links Count Check", False, f"Expected >= 3 links, got: {total_count}")
                        return False
                    
                    # Test specific result endpoint
                    related_links_id = result.get('related_links_id')
                    if related_links_id:
                        return self.test_specific_related_links_result(related_links_id)
                    else:
                        self.log_test("Related Links ID Check", False, "No related links ID found")
                        return False
                else:
                    self.log_test("Related Links Generation Verification", False, f"No related links results found for job {job_id}")
                    return False
            else:
                self.log_test("Related Links Verification", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Related Links Generation Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_specific_related_links_result(self, related_links_id):
        """Test specific related links result endpoint"""
        try:
            print(f"\n🔍 TESTING: Specific Related Links Result - {related_links_id}")
            
            response = requests.get(f"{self.backend_url}/related-links/diagnostics/{related_links_id}")
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Check engine
                engine = result_data.get('engine')
                if engine == 'v2':
                    self.log_test("Specific Result Engine Check", True, f"Engine: {engine}")
                else:
                    self.log_test("Specific Result Engine Check", False, f"Expected 'v2', got: {engine}")
                    return False
                
                # Check result structure
                related_links_result = result_data.get('related_links_result', {})
                if related_links_result:
                    self.log_test("Related Links Result Structure", True, "Result structure present")
                else:
                    self.log_test("Related Links Result Structure", False, "No result structure found")
                    return False
                
                # Check analysis section
                analysis = result_data.get('analysis', {})
                if analysis:
                    self.log_test("Related Links Analysis Section", True, "Analysis section present")
                    
                    # Check processing summary
                    processing_summary = analysis.get('processing_summary', {})
                    if processing_summary:
                        self.log_test("Processing Summary", True, "Processing summary present")
                    else:
                        self.log_test("Processing Summary", False, "No processing summary found")
                        return False
                    
                    # Check related links breakdown
                    links_breakdown = analysis.get('related_links_breakdown', [])
                    if isinstance(links_breakdown, list):
                        self.log_test("Related Links Breakdown", True, f"Found {len(links_breakdown)} links in breakdown")
                    else:
                        self.log_test("Related Links Breakdown", False, "Links breakdown not in list format")
                        return False
                else:
                    self.log_test("Related Links Analysis Section", False, "No analysis section found")
                    return False
                
                return True
            else:
                self.log_test("Specific Related Links Result", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Specific Related Links Result", False, f"Exception: {str(e)}")
            return False
    
    def test_related_links_rerun(self):
        """Test related links rerun functionality"""
        try:
            print("\n🔄 TESTING: Related Links Rerun Functionality")
            
            # First, get a recent run ID from diagnostics
            response = requests.get(f"{self.backend_url}/related-links/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                recent_results = diagnostics_data.get('recent_related_links_results', [])
                
                if recent_results:
                    # Use the most recent run ID
                    run_id = recent_results[0].get('run_id')
                    
                    if run_id:
                        # Test rerun endpoint
                        rerun_response = requests.post(f"{self.backend_url}/related-links/rerun",
                                                     json={"run_id": run_id})
                        
                        if rerun_response.status_code == 200:
                            rerun_data = rerun_response.json()
                            
                            # Check rerun status
                            status = rerun_data.get('status')
                            if status == 'completed':
                                self.log_test("Related Links Rerun Status", True, f"Status: {status}")
                            else:
                                self.log_test("Related Links Rerun Status", False, f"Expected 'completed', got: {status}")
                                return False
                            
                            # Check engine
                            engine = rerun_data.get('engine')
                            if engine == 'v2':
                                self.log_test("Rerun Engine Check", True, f"Engine: {engine}")
                            else:
                                self.log_test("Rerun Engine Check", False, f"Expected 'v2', got: {engine}")
                                return False
                            
                            # Check rerun results
                            articles_processed = rerun_data.get('articles_processed', 0)
                            if articles_processed > 0:
                                self.log_test("Rerun Articles Processed", True, f"Processed {articles_processed} articles")
                            else:
                                self.log_test("Rerun Articles Processed", False, f"No articles processed in rerun")
                                return False
                            
                            return True
                        else:
                            self.log_test("Related Links Rerun", False, f"HTTP {rerun_response.status_code}: {rerun_response.text}")
                            return False
                    else:
                        self.log_test("Related Links Rerun", False, "No run ID found for rerun test")
                        return False
                else:
                    self.log_test("Related Links Rerun", False, "No recent results found for rerun test")
                    return False
            else:
                self.log_test("Related Links Rerun Setup", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Related Links Rerun", False, f"Exception: {str(e)}")
            return False
    
    def test_database_storage_and_retrieval(self):
        """Test database storage and retrieval of related links results"""
        try:
            print("\n💾 TESTING: Database Storage and Retrieval")
            
            response = requests.get(f"{self.backend_url}/related-links/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                
                # Check recent results for database storage verification
                recent_results = diagnostics_data.get('recent_related_links_results', [])
                
                if recent_results:
                    self.log_test("Database Storage Verification", True, f"Found {len(recent_results)} stored results")
                    
                    # Check result structure for proper data preservation
                    first_result = recent_results[0]
                    required_fields = [
                        'related_links_id',
                        'run_id', 
                        'article_title',
                        'related_links_status',
                        'timestamp'
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in first_result:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        self.log_test("Database Result Structure", True, f"All required fields present: {required_fields}")
                    else:
                        self.log_test("Database Result Structure", False, f"Missing fields: {missing_fields}")
                        return False
                    
                    # Check ObjectId serialization (no ObjectId objects in response)
                    result_str = json.dumps(first_result)
                    if 'ObjectId' not in result_str:
                        self.log_test("ObjectId Serialization", True, "No ObjectId serialization issues")
                    else:
                        self.log_test("ObjectId Serialization", False, "ObjectId serialization issues detected")
                        return False
                    
                    return True
                else:
                    self.log_test("Database Storage Verification", False, "No stored results found")
                    return False
            else:
                self.log_test("Database Storage and Retrieval", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Database Storage and Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_engine_status_integration(self):
        """Test related links integration in engine status"""
        try:
            print("\n⚙️ TESTING: Engine Status Integration")
            
            response = requests.get(f"{self.backend_url}/engine")
            
            if response.status_code == 200:
                engine_data = response.json()
                
                # Check engine message includes related links
                message = engine_data.get('message', '').lower()
                if 'related links' in message or 'related_links' in message:
                    self.log_test("Engine Message Integration", True, "Related links mentioned in engine message")
                else:
                    self.log_test("Engine Message Integration", False, "Related links not mentioned in engine message")
                    return False
                
                # Check features include related links capabilities
                features = engine_data.get('features', [])
                related_features = [f for f in features if 'related' in f.lower() or 'link' in f.lower()]
                
                if related_features:
                    self.log_test("Related Links Features Integration", True, f"Found related features: {related_features}")
                else:
                    self.log_test("Related Links Features Integration", False, "No related links features found")
                    return False
                
                # Check endpoints include related links diagnostics
                endpoints = engine_data.get('endpoints', {})
                if 'related_links_diagnostics' in endpoints:
                    self.log_test("Related Links Endpoints Integration", True, "Related links diagnostics endpoint present")
                else:
                    self.log_test("Related Links Endpoints Integration", False, "Related links diagnostics endpoint missing")
                    return False
                
                return True
            else:
                self.log_test("Engine Status Integration", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Engine Status Integration", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all V2 Engine Related Links System tests"""
        print("🚀 STARTING V2 ENGINE RELATED LINKS SYSTEM COMPREHENSIVE TESTING")
        print("=" * 80)
        
        # Test sequence based on review requirements
        test_sequence = [
            ("V2 Engine Health Check", self.test_v2_engine_health_check),
            ("Seed Articles Creation", self.test_seed_articles_creation),
            ("Content Library Indexing", self.test_content_library_indexing),
            ("Related Links Diagnostics", self.test_related_links_diagnostics),
            ("Content Processing with Related Links", self.test_content_processing_with_related_links),
            ("Related Links Rerun", self.test_related_links_rerun),
            ("Database Storage and Retrieval", self.test_database_storage_and_retrieval),
            ("Engine Status Integration", self.test_engine_status_integration)
        ]
        
        for test_name, test_function in test_sequence:
            try:
                print(f"\n{'='*60}")
                print(f"🧪 RUNNING: {test_name}")
                print(f"{'='*60}")
                
                success = test_function()
                
                if not success:
                    print(f"⚠️ Test '{test_name}' failed - continuing with remaining tests")
                    
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                self.log_test(test_name, False, f"Critical error: {str(e)}")
        
        # Print final summary
        self.print_test_summary()
        
        return self.test_results
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 V2 ENGINE RELATED LINKS SYSTEM TESTING SUMMARY")
        print("="*80)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed} ✅")
        print(f"   Failed: {failed} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"🎉 EXCELLENT: Related Links System is working well!")
        elif success_rate >= 60:
            print(f"⚠️ GOOD: Related Links System is mostly functional with some issues")
        else:
            print(f"❌ NEEDS ATTENTION: Related Links System has significant issues")
        
        # Print failed tests details
        if failed > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for test in self.test_results["test_details"]:
                if test["status"] == "failed":
                    print(f"   • {test['test_name']}: {test['details']}")
        
        print("\n" + "="*80)

def main():
    """Main testing function"""
    print("🔗 V2 ENGINE RELATED LINKS SYSTEM COMPREHENSIVE TESTING")
    print("Testing content library indexing, similarity matching, and related links generation")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*80)
    
    tester = V2RelatedLinksSystemTester()
    results = tester.run_comprehensive_tests()
    
    # Return appropriate exit code
    if results["failed_tests"] == 0:
        print("✅ ALL TESTS PASSED - Related Links System is fully operational!")
        sys.exit(0)
    else:
        print(f"❌ {results['failed_tests']} TESTS FAILED - Related Links System needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()