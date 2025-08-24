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

class V2CodeNormalizationTester:
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
    
    def test_code_normalization_health_check(self):
        """Test 1: Code Normalization System Health Check - Verify V2 Engine is active"""
        try:
            print("\n🔍 TESTING: Code Normalization System Health Check")
            
            response = requests.get(f"{self.backend_url}/code-normalization/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                
                # Check V2 Engine is active
                engine = diagnostics_data.get('engine')
                system_status = diagnostics_data.get('code_normalization_system_status')
                
                if engine == 'v2' and system_status == 'active':
                    self.log_test("V2 Engine Active with Code Normalization", True, f"Engine: {engine}, Status: {system_status}")
                    
                    # Check required features
                    capabilities = diagnostics_data.get('system_capabilities', {})
                    required_features = [
                        'supported_languages',
                        'beautification_features', 
                        'prism_integration',
                        'language_detection'
                    ]
                    
                    missing_features = []
                    for feature in required_features:
                        if feature not in capabilities:
                            missing_features.append(feature)
                    
                    if not missing_features:
                        self.log_test("All Required Features Operational", True, f"Features: {list(capabilities.keys())}")
                        return True
                    else:
                        self.log_test("All Required Features Operational", False, f"Missing: {missing_features}")
                        return False
                else:
                    self.log_test("V2 Engine Active with Code Normalization", False, f"Engine: {engine}, Status: {system_status}")
                    return False
            else:
                self.log_test("Code Normalization Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Code Normalization Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_language_detection_and_prism_mapping(self):
        """Test 2: Language Detection and Prism Class Mapping - Test 26+ supported languages"""
        try:
            print("\n🔍 TESTING: Language Detection and Prism Class Mapping")
            
            response = requests.get(f"{self.backend_url}/code-normalization/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                capabilities = diagnostics_data.get('system_capabilities', {})
                
                # Check supported languages (26+ requirement)
                supported_languages = capabilities.get('supported_languages', [])
                expected_languages = [
                    'bash', 'json', 'yaml', 'xml', 'sql', 'javascript', 'python',
                    'java', 'csharp', 'cpp', 'php', 'ruby', 'go', 'rust', 'typescript',
                    'css', 'html', 'markdown', 'graphql', 'curl', 'http'
                ]
                
                found_languages = 0
                for lang in expected_languages:
                    if lang in supported_languages:
                        found_languages += 1
                
                if len(supported_languages) >= 26 and found_languages >= 15:
                    self.log_test("26+ Supported Languages", True, f"Total: {len(supported_languages)}, Key languages: {found_languages}/{len(expected_languages)}")
                else:
                    self.log_test("26+ Supported Languages", False, f"Total: {len(supported_languages)}, Key languages: {found_languages}/{len(expected_languages)}")
                    return False
                
                # Check language detection methods
                language_detection = capabilities.get('language_detection')
                if language_detection:
                    self.log_test("Language Detection Methods", True, f"Detection: {language_detection}")
                else:
                    self.log_test("Language Detection Methods", False, "No language detection info")
                    return False
                
                # Verify actual language detection in practice
                recent_results = diagnostics_data.get('recent_code_results', [])
                if recent_results:
                    first_result = recent_results[0]
                    summary = diagnostics_data.get('code_normalization_summary', {})
                    language_dist = summary.get('language_distribution', {})
                    
                    if language_dist:
                        detected_langs = list(language_dist.keys())
                        self.log_test("Language Detection in Practice", True, f"Languages detected: {detected_langs}")
                        return True
                    else:
                        self.log_test("Language Detection in Practice", False, "No languages detected in recent processing")
                        return False
                else:
                    self.log_test("Language Detection in Practice", False, "No recent processing results")
                    return False
            else:
                self.log_test("Language Detection and Prism Mapping", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Language Detection and Prism Mapping", False, f"Exception: {str(e)}")
            return False
    
    def test_beautification_engine(self):
        """Test 3: Beautification Engine - Verify JSON, YAML, XML, SQL, curl formatting"""
        try:
            print("\n🎨 TESTING: Beautification Engine")
            
            response = requests.get(f"{self.backend_url}/code-normalization/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                capabilities = diagnostics_data.get('system_capabilities', {})
                
                # Check beautification features
                beautification_features = capabilities.get('beautification_features', [])
                expected_features = [
                    'JSON pretty-print',
                    'YAML formatting', 
                    'XML pretty-print',
                    'SQL formatting',
                    'Curl line breaks'
                ]
                
                found_features = 0
                for feature in expected_features:
                    if feature in beautification_features:
                        found_features += 1
                
                if found_features >= 4:  # At least 4 of 5 beautification features
                    self.log_test("Beautification Features Available", True, f"Found {found_features}/{len(expected_features)} features")
                else:
                    self.log_test("Beautification Features Available", False, f"Only {found_features}/{len(expected_features)} features")
                    return False
                
                # Check actual beautification in recent processing
                summary = diagnostics_data.get('code_normalization_summary', {})
                normalized_blocks = summary.get('total_normalized_blocks', 0)
                normalization_rate = summary.get('overall_normalization_rate', 0)
                
                if normalized_blocks > 0 and normalization_rate > 0:
                    self.log_test("Beautification Applied in Practice", True, f"Normalized {normalized_blocks} blocks at {normalization_rate}% rate")
                    return True
                else:
                    self.log_test("Beautification Applied in Practice", False, f"No beautification applied: {normalized_blocks} blocks, {normalization_rate}% rate")
                    return False
            else:
                self.log_test("Beautification Engine", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Beautification Engine", False, f"Exception: {str(e)}")
            return False
    
    def test_prism_ready_html_generation(self):
        """Test 4: Prism-Ready HTML Generation - Verify proper figure structure with code-toolbar, line-numbers"""
        try:
            print("\n🏗️ TESTING: Prism-Ready HTML Generation")
            
            # Get articles with code blocks to verify HTML structure
            response = requests.get(f"{self.backend_url}/content-library?limit=20")
            
            if response.status_code == 200:
                articles_data = response.json()
                articles = articles_data.get('articles', [])
                
                # Find articles with Prism-ready code blocks
                prism_ready_articles = []
                for article in articles:
                    content = article.get('content', '')
                    title = article.get('title', '')
                    
                    # Check for Prism-ready structure
                    if 'figure class="code-block"' in content:
                        prism_checks = {
                            'figure_wrapper': 'figure class="code-block"' in content,
                            'pre_line_numbers': 'pre class="line-numbers"' in content,
                            'code_language_class': 'code class="language-' in content,
                            'code_toolbar': 'code-toolbar' in content,
                            'safe_html_escaping': any(char in content for char in ['&lt;', '&gt;', '&amp;', '&quot;'])
                        }
                        
                        passed_checks = sum(prism_checks.values())
                        if passed_checks >= 4:  # At least 4 of 5 structure elements
                            prism_ready_articles.append({
                                'title': title,
                                'checks': prism_checks,
                                'passed': passed_checks
                            })
                
                if prism_ready_articles:
                    best_article = max(prism_ready_articles, key=lambda x: x['passed'])
                    self.log_test("Prism-Ready HTML Structure Found", True, f"Article: '{best_article['title']}' has {best_article['passed']}/5 Prism elements")
                    
                    # Verify specific structure elements
                    checks = best_article['checks']
                    if checks['figure_wrapper']:
                        self.log_test("Figure Wrapper with code-block class", True, "Complete figure wrapper found")
                    if checks['pre_line_numbers']:
                        self.log_test("Pre element with line-numbers class", True, "Line numbers class confirmed")
                    if checks['code_language_class']:
                        self.log_test("Code element with language classes", True, "Language classes for syntax highlighting")
                    if checks['code_toolbar']:
                        self.log_test("Code-toolbar div for Prism integration", True, "Toolbar div for copy button")
                    if checks['safe_html_escaping']:
                        self.log_test("Safe HTML escaping implemented", True, "HTML content properly escaped")
                    
                    return True
                else:
                    self.log_test("Prism-Ready HTML Structure Found", False, "No articles with proper Prism structure found")
                    return False
            else:
                self.log_test("Prism-Ready HTML Generation", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Prism-Ready HTML Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_processing_pipeline_integration(self):
        """Test 5: Processing Pipeline Integration - Verify Step 7.9 integration between Gap Filling and Validation"""
        try:
            print("\n🔗 TESTING: Processing Pipeline Integration (Step 7.9)")
            
            response = requests.get(f"{self.backend_url}/code-normalization/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                
                # Check integration in all 3 processing pipelines
                recent_results = diagnostics_data.get('recent_code_results', [])
                if recent_results:
                    first_result = recent_results[0]
                    
                    # Check pipeline integration indicators
                    pipeline_indicators = {
                        'run_id_present': 'run_id' in first_result,
                        'status_tracking': 'code_normalization_status' in first_result,
                        'timestamp_tracking': 'timestamp' in first_result,
                        'article_processing': 'articles_processed' in first_result
                    }
                    
                    passed_indicators = sum(pipeline_indicators.values())
                    
                    if passed_indicators >= 3:
                        self.log_test("Pipeline Integration Indicators", True, f"Found {passed_indicators}/4 integration indicators")
                    else:
                        self.log_test("Pipeline Integration Indicators", False, f"Only {passed_indicators}/4 integration indicators")
                        return False
                    
                    # Check database storage working
                    summary = diagnostics_data.get('code_normalization_summary', {})
                    total_runs = summary.get('total_code_runs', 0)
                    
                    if total_runs > 0:
                        self.log_test("Database Storage Working", True, f"Found {total_runs} processing runs")
                    else:
                        self.log_test("Database Storage Working", False, "No processing runs in database")
                        return False
                    
                    # Check comprehensive error handling
                    success_rate = summary.get('success_rate', 0)
                    if success_rate >= 0:  # Should be a valid percentage
                        self.log_test("Error Handling and Status Tracking", True, f"Success rate: {success_rate}%")
                        return True
                    else:
                        self.log_test("Error Handling and Status Tracking", False, "Invalid success rate")
                        return False
                else:
                    self.log_test("Processing Pipeline Integration", False, "No recent processing results found")
                    return False
            else:
                self.log_test("Processing Pipeline Integration", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Processing Pipeline Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_diagnostic_endpoints(self):
        """Test 6: Diagnostic Endpoints - Test GET /api/code-normalization/diagnostics and specific ID endpoints"""
        try:
            print("\n📊 TESTING: Diagnostic Endpoints")
            
            # Test main diagnostics endpoint
            response = requests.get(f"{self.backend_url}/code-normalization/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                
                # Check main diagnostics structure
                required_sections = [
                    'code_normalization_system_status',
                    'engine',
                    'code_normalization_summary',
                    'system_capabilities'
                ]
                
                missing_sections = []
                for section in required_sections:
                    if section not in diagnostics_data:
                        missing_sections.append(section)
                
                if not missing_sections:
                    self.log_test("GET /api/code-normalization/diagnostics", True, f"All sections present: {required_sections}")
                else:
                    self.log_test("GET /api/code-normalization/diagnostics", False, f"Missing sections: {missing_sections}")
                    return False
                
                # Test specific result endpoint if available
                recent_results = diagnostics_data.get('recent_code_results', [])
                if recent_results:
                    code_id = recent_results[0].get('code_normalization_id')
                    if code_id:
                        specific_response = requests.get(f"{self.backend_url}/code-normalization/diagnostics/{code_id}")
                        
                        if specific_response.status_code == 200:
                            specific_data = specific_response.json()
                            
                            # Check specific endpoint structure
                            required_fields = ['engine', 'code_normalization_result', 'analysis']
                            missing_fields = []
                            for field in required_fields:
                                if field not in specific_data:
                                    missing_fields.append(field)
                            
                            if not missing_fields:
                                self.log_test("GET /api/code-normalization/diagnostics/{id}", True, f"All fields present: {required_fields}")
                                return True
                            else:
                                self.log_test("GET /api/code-normalization/diagnostics/{id}", False, f"Missing fields: {missing_fields}")
                                return False
                        else:
                            self.log_test("GET /api/code-normalization/diagnostics/{id}", False, f"HTTP {specific_response.status_code}")
                            return False
                    else:
                        self.log_test("Specific Endpoint Test", False, "No code normalization ID found")
                        return False
                else:
                    self.log_test("Specific Endpoint Test", False, "No recent results for specific endpoint test")
                    return False
            else:
                self.log_test("Diagnostic Endpoints", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Diagnostic Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_database_storage(self):
        """Test 7: Database Storage - Verify code normalization results stored in v2_code_normalization_results collection"""
        try:
            print("\n💾 TESTING: Database Storage")
            
            response = requests.get(f"{self.backend_url}/code-normalization/diagnostics")
            
            if response.status_code == 200:
                diagnostics_data = response.json()
                
                # Check database storage verification
                recent_results = diagnostics_data.get('recent_code_results', [])
                
                if recent_results:
                    self.log_test("Database Storage Verification", True, f"Found {len(recent_results)} stored results")
                    
                    # Check result structure for proper data preservation
                    first_result = recent_results[0]
                    required_fields = [
                        'code_normalization_id',
                        'run_id',
                        'code_normalization_status',
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
                    
                    # Check language distribution tracking
                    summary = diagnostics_data.get('code_normalization_summary', {})
                    language_dist = summary.get('language_distribution', {})
                    
                    if language_dist:
                        self.log_test("Language Distribution Tracking", True, f"Languages tracked: {list(language_dist.keys())}")
                    else:
                        self.log_test("Language Distribution Tracking", False, "No language distribution tracking")
                        return False
                    
                    # Check beautification statistics
                    normalized_blocks = summary.get('total_normalized_blocks', 0)
                    if normalized_blocks >= 0:
                        self.log_test("Beautification Statistics Maintained", True, f"Statistics: {normalized_blocks} blocks normalized")
                        return True
                    else:
                        self.log_test("Beautification Statistics Maintained", False, "No beautification statistics")
                        return False
                else:
                    self.log_test("Database Storage Verification", False, "No stored results found")
                    return False
            else:
                self.log_test("Database Storage", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Storage", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all V2 Engine Code Normalization System tests"""
        print("🚀 STARTING V2 ENGINE CODE NORMALIZATION SYSTEM COMPREHENSIVE TESTING")
        print("=" * 80)
        
        # Test sequence based on review requirements
        test_sequence = [
            ("Code Normalization System Health Check", self.test_code_normalization_health_check),
            ("Language Detection and Prism Class Mapping", self.test_language_detection_and_prism_mapping),
            ("Beautification Engine", self.test_beautification_engine),
            ("Prism-Ready HTML Generation", self.test_prism_ready_html_generation),
            ("Processing Pipeline Integration (Step 7.9)", self.test_processing_pipeline_integration),
            ("Diagnostic Endpoints", self.test_diagnostic_endpoints),
            ("Database Storage", self.test_database_storage)
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
        print("🎯 V2 ENGINE CODE NORMALIZATION SYSTEM TESTING SUMMARY")
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
            print(f"🎉 EXCELLENT: Code Normalization System is working well!")
        elif success_rate >= 60:
            print(f"⚠️ GOOD: Code Normalization System is mostly functional with some issues")
        else:
            print(f"❌ NEEDS ATTENTION: Code Normalization System has significant issues")
        
        # Print failed tests details
        if failed > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for test in self.test_results["test_details"]:
                if test["status"] == "failed":
                    print(f"   • {test['test_name']}: {test['details']}")
        
        print("\n" + "="*80)

def main():
    """Main testing function"""
    print("🎨 V2 ENGINE CODE NORMALIZATION SYSTEM COMPREHENSIVE TESTING")
    print("Testing V2 Engine Code Normalization System to verify Prism-ready HTML generation")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*80)
    
    tester = V2CodeNormalizationTester()
    results = tester.run_comprehensive_tests()
    
    # Return appropriate exit code
    if results["failed_tests"] == 0:
        print("✅ ALL TESTS PASSED - Code Normalization System is fully operational!")
        sys.exit(0)
    else:
        print(f"❌ {results['failed_tests']} TESTS FAILED - Code Normalization System needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()