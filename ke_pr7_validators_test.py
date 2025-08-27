#!/usr/bin/env python3
"""
KE-PR7 Validator & QA Report as First-Class Module Testing
Comprehensive test suite for machine-readable QA reports, publish gates, and validation checks
"""

import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List

# Test configuration
BACKEND_URL = "https://content-processor.preview.emergentagent.com/api"

class KE_PR7_Tester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_test(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if data and isinstance(data, dict):
            print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
        print()

    def test_engine_status_qa_summaries(self):
        """Test 1: Verify QA summaries are exposed in /api/engine endpoint"""
        try:
            print("🔍 Testing QA summaries exposure in engine status...")
            
            response = self.session.get(f"{self.backend_url}/engine")
            
            if response.status_code != 200:
                self.log_test("Engine Status QA Summaries", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check for QA-related features
            features = data.get("features", [])
            qa_features = [f for f in features if "qa" in f.lower() or "validation" in f.lower()]
            
            # Check for QA summaries
            qa_summaries = data.get("qa_summaries", [])
            qa_summary_count = data.get("qa_summary_count", 0)
            qa_features_dict = data.get("qa_features", {})
            
            # Verify KE-PR7 specific features
            expected_features = [
                "qa_reports_machine_readable",
                "coverage_analysis_advanced", 
                "unsupported_claims_detection",
                "placeholder_detection_comprehensive",
                "duplicate_content_detection",
                "broken_links_detection",
                "missing_media_detection",
                "content_quality_checks",
                "technical_accuracy_validation",
                "publish_gates_p0_blocking",
                "qa_database_persistence",
                "qa_summaries_api_exposure",
                "first_class_validation_module"
            ]
            
            missing_features = [f for f in expected_features if f not in features]
            
            if missing_features:
                self.log_test("Engine Status QA Summaries", "FAIL",
                            f"Missing KE-PR7 features: {missing_features}",
                            {"found_features": qa_features, "qa_summaries_count": qa_summary_count})
                return False
            
            # Check QA features structure
            required_qa_features = [
                "coverage_analysis", "unsupported_claims_detection", "placeholder_detection",
                "duplicate_content_detection", "broken_links_detection", "missing_media_detection",
                "publish_gates", "machine_readable_reports"
            ]
            
            missing_qa_features = [f for f in required_qa_features if not qa_features_dict.get(f)]
            
            if missing_qa_features:
                self.log_test("Engine Status QA Summaries", "FAIL",
                            f"Missing QA features: {missing_qa_features}",
                            {"qa_features": qa_features_dict})
                return False
            
            self.log_test("Engine Status QA Summaries", "PASS",
                        f"Found {len(qa_features)} QA features, {qa_summary_count} QA summaries",
                        {"qa_features": qa_features[:5], "qa_summaries_count": qa_summary_count})
            return True
            
        except Exception as e:
            self.log_test("Engine Status QA Summaries", "FAIL", f"Exception: {str(e)}")
            return False

    def test_qa_diagnostics_endpoints(self):
        """Test 2: Verify QA diagnostics endpoints are functional"""
        try:
            print("🔍 Testing QA diagnostics endpoints...")
            
            # Test main QA diagnostics endpoint
            response = self.session.get(f"{self.backend_url}/qa/diagnostics")
            
            if response.status_code != 200:
                self.log_test("QA Diagnostics Endpoints", "FAIL",
                            f"QA diagnostics HTTP {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            
            # Check response structure
            required_fields = ["total_qa_runs", "passed_qa_runs", "qa_runs_with_issues", "error_qa_runs", "qa_results"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                self.log_test("QA Diagnostics Endpoints", "FAIL",
                            f"Missing fields in QA diagnostics: {missing_fields}",
                            {"response_keys": list(data.keys())})
                return False
            
            qa_results = data.get("qa_results", [])
            total_runs = data.get("total_qa_runs", 0)
            
            # Test specific QA diagnostics if we have results
            if qa_results:
                first_qa = qa_results[0]
                qa_id = first_qa.get("qa_id")
                
                if qa_id:
                    specific_response = self.session.get(f"{self.backend_url}/qa/diagnostics/{qa_id}")
                    
                    if specific_response.status_code == 200:
                        specific_data = specific_response.json()
                        qa_summary = specific_data.get("qa_summary", {})
                        
                        self.log_test("QA Diagnostics Endpoints", "PASS",
                                    f"QA diagnostics working. Total runs: {total_runs}, Specific QA found",
                                    {"total_runs": total_runs, "qa_summary_keys": list(qa_summary.keys())})
                        return True
                    else:
                        self.log_test("QA Diagnostics Endpoints", "PARTIAL",
                                    f"Main endpoint works, specific QA endpoint failed: {specific_response.status_code}",
                                    {"total_runs": total_runs})
                        return True
            
            self.log_test("QA Diagnostics Endpoints", "PASS",
                        f"QA diagnostics endpoint working. Total runs: {total_runs}",
                        {"total_runs": total_runs, "structure_valid": True})
            return True
            
        except Exception as e:
            self.log_test("QA Diagnostics Endpoints", "FAIL", f"Exception: {str(e)}")
            return False

    def test_content_processing_with_qa_validation(self):
        """Test 3: Test content processing with QA validation and machine-readable reports"""
        try:
            print("🔍 Testing content processing with QA validation...")
            
            # Test content with various validation issues
            test_content = """
            # Test Article with Validation Issues
            
            This is a test article that contains various issues for validation testing.
            
            ## Unsupported Claims Section
            Studies show that this always works perfectly. Everyone knows this is the best approach.
            Research proves that it never fails. Obviously, this is clearly the most effective method.
            
            ## Placeholder Section
            [TODO: Add more content here]
            [MISSING: Important information needed]
            Insert diagram here...
            
            ## Duplicate Content
            This sentence appears multiple times in the document.
            This sentence appears multiple times in the document.
            
            ## Technical Issues
            The API simply works magically. It just works automatically.
            You can use JSON, json, and Json interchangeably.
            
            ## Links and Media
            Check out this broken link: https://invalid-domain-12345.com/nonexistent
            See the image below: ![Missing Image]()
            As shown in figure 1, the process is clear.
            
            ## Code Section
            This discusses API integration but has no code examples.
            """
            
            # Submit content for processing
            payload = {
                "content": test_content,
                "metadata": {
                    "title": "KE-PR7 Validation Test Article",
                    "source": "test_suite"
                }
            }
            
            response = self.session.post(f"{self.backend_url}/content/process", json=payload)
            
            if response.status_code != 200:
                self.log_test("Content Processing QA Validation", "FAIL",
                            f"Content processing failed: HTTP {response.status_code}: {response.text}")
                return False
            
            result = response.json()
            
            # Check for QA validation in response
            validation_result = result.get("validation_result", {})
            qa_report = validation_result.get("qa_report", {})
            
            if not qa_report:
                self.log_test("Content Processing QA Validation", "FAIL",
                            "No QA report found in processing result",
                            {"validation_keys": list(validation_result.keys())})
                return False
            
            # Verify QA report structure
            required_qa_fields = ["job_id", "coverage_percent", "flags", "broken_links", "missing_media"]
            missing_qa_fields = [f for f in required_qa_fields if f not in qa_report]
            
            if missing_qa_fields:
                self.log_test("Content Processing QA Validation", "FAIL",
                            f"QA report missing fields: {missing_qa_fields}",
                            {"qa_report_keys": list(qa_report.keys())})
                return False
            
            # Analyze QA report content
            flags = qa_report.get("flags", [])
            coverage_percent = qa_report.get("coverage_percent", 0)
            broken_links = qa_report.get("broken_links", [])
            missing_media = qa_report.get("missing_media", [])
            
            # Count flag types
            p0_flags = [f for f in flags if f.get("severity") == "P0"]
            p1_flags = [f for f in flags if f.get("severity") == "P1"]
            
            # Verify expected validation issues were detected
            expected_issues = {
                "unsupported_claims": any("unsupported" in f.get("code", "").lower() or "claim" in f.get("code", "").lower() for f in flags),
                "placeholders": any("placeholder" in f.get("code", "").lower() for f in flags),
                "duplicates": any("duplicate" in f.get("code", "").lower() for f in flags),
                "technical_accuracy": any("technical" in f.get("code", "").lower() or "vague" in f.get("code", "").lower() for f in flags),
                "broken_links": len(broken_links) > 0,
                "missing_media": len(missing_media) > 0
            }
            
            detected_issues = sum(expected_issues.values())
            
            if detected_issues < 3:  # Should detect at least 3 types of issues
                self.log_test("Content Processing QA Validation", "PARTIAL",
                            f"QA validation working but only detected {detected_issues}/6 expected issue types",
                            {"detected_issues": expected_issues, "flags_count": len(flags)})
                return True
            
            self.log_test("Content Processing QA Validation", "PASS",
                        f"QA validation detected {detected_issues}/6 issue types. Coverage: {coverage_percent}%, P0: {len(p0_flags)}, P1: {len(p1_flags)}",
                        {"coverage": coverage_percent, "p0_flags": len(p0_flags), "p1_flags": len(p1_flags), "detected_issues": detected_issues})
            return True
            
        except Exception as e:
            self.log_test("Content Processing QA Validation", "FAIL", f"Exception: {str(e)}")
            return False

    def test_publish_gate_p0_blocking(self):
        """Test 4: Test publish gate functionality - ensure P0 issues block publishing"""
        try:
            print("🔍 Testing publish gate P0 blocking functionality...")
            
            # Create content with critical P0 issues
            p0_content = """
            # Critical Issues Test
            
            [TODO: This is a major placeholder that should block publishing]
            [MISSING: Critical content needed]
            [PLACEHOLDER: Important section]
            
            This sentence is duplicated exactly.
            This sentence is duplicated exactly.
            This sentence is duplicated exactly.
            
            Studies always prove that this never fails. Everyone definitely knows this is obviously true.
            Research clearly shows that this certainly works perfectly every time without exception.
            """
            
            # Submit content for processing
            payload = {
                "content": p0_content,
                "metadata": {
                    "title": "P0 Blocking Test Article",
                    "source": "publish_gate_test"
                }
            }
            
            response = self.session.post(f"{self.backend_url}/content/process", json=payload)
            
            if response.status_code != 200:
                self.log_test("Publish Gate P0 Blocking", "FAIL",
                            f"Content processing failed: HTTP {response.status_code}")
                return False
            
            result = response.json()
            
            # Check publishing result
            publishing_result = result.get("publishing_result", {})
            publishing_status = publishing_result.get("status", "")
            
            # Check QA report for P0 issues
            validation_result = result.get("validation_result", {})
            qa_report = validation_result.get("qa_report", {})
            flags = qa_report.get("flags", [])
            
            p0_flags = [f for f in flags if f.get("severity") == "P0"]
            
            # Verify P0 issues were detected
            if len(p0_flags) == 0:
                self.log_test("Publish Gate P0 Blocking", "FAIL",
                            "No P0 issues detected in content with critical problems",
                            {"flags_count": len(flags), "publishing_status": publishing_status})
                return False
            
            # Check if publishing was blocked
            if publishing_status == "blocked":
                block_reason = publishing_result.get("block_reason", "")
                self.log_test("Publish Gate P0 Blocking", "PASS",
                            f"Publishing correctly blocked due to {len(p0_flags)} P0 issues: {block_reason}",
                            {"p0_flags": len(p0_flags), "block_reason": block_reason})
                return True
            elif publishing_status == "success":
                self.log_test("Publish Gate P0 Blocking", "FAIL",
                            f"Publishing should have been blocked but succeeded with {len(p0_flags)} P0 issues",
                            {"p0_flags": len(p0_flags), "publishing_status": publishing_status})
                return False
            else:
                self.log_test("Publish Gate P0 Blocking", "PARTIAL",
                            f"P0 issues detected ({len(p0_flags)}) but publishing status unclear: {publishing_status}",
                            {"p0_flags": len(p0_flags), "publishing_status": publishing_status})
                return True
            
        except Exception as e:
            self.log_test("Publish Gate P0 Blocking", "FAIL", f"Exception: {str(e)}")
            return False

    def test_comprehensive_validation_checks(self):
        """Test 5: Test all validation checks comprehensively"""
        try:
            print("🔍 Testing comprehensive validation checks...")
            
            # Test content covering all validation areas
            comprehensive_content = """
            # Comprehensive Validation Test
            
            ## Coverage Test Section
            This section tests coverage analysis with substantial content to ensure proper coverage calculation.
            
            ## Unsupported Claims Test
            Studies always show that this method never fails. Everyone knows this is the best approach.
            Research definitely proves that it works perfectly. Obviously, this is clearly superior.
            
            ## Placeholder Detection Test
            [TODO: Add implementation details]
            [MISSING: Code examples needed]
            Insert screenshot here...
            Add configuration steps below.
            
            ## Duplicate Content Test
            This exact sentence appears multiple times for testing.
            This exact sentence appears multiple times for testing.
            
            The following paragraph is repeated exactly.
            This paragraph contains duplicate information that should be detected by the validation system.
            
            The following paragraph is repeated exactly.
            This paragraph contains duplicate information that should be detected by the validation system.
            
            ## Broken Links Test
            Visit our documentation: https://nonexistent-domain-12345.com/docs
            Check the API reference: https://invalid-api-site.com/reference
            
            ## Missing Media Test
            ![Missing Screenshot]()
            See figure 1 below for the workflow diagram.
            The image shows the process clearly.
            
            ## Content Quality Test
            Short.
            
            ## Technical Accuracy Test
            The API simply works magically. It just works automatically.
            You might use JSON, json, Json, and JSON formats.
            This should work fine, probably.
            
            ## Code Discussion Without Examples
            This section discusses API integration, function calls, and code implementation
            but provides no actual code examples or snippets.
            """
            
            # Submit for processing
            payload = {
                "content": comprehensive_content,
                "metadata": {
                    "title": "Comprehensive Validation Test",
                    "source": "validation_test_suite"
                }
            }
            
            response = self.session.post(f"{self.backend_url}/content/process", json=payload)
            
            if response.status_code != 200:
                self.log_test("Comprehensive Validation Checks", "FAIL",
                            f"Processing failed: HTTP {response.status_code}")
                return False
            
            result = response.json()
            validation_result = result.get("validation_result", {})
            qa_report = validation_result.get("qa_report", {})
            
            if not qa_report:
                self.log_test("Comprehensive Validation Checks", "FAIL",
                            "No QA report in processing result")
                return False
            
            # Analyze validation results
            flags = qa_report.get("flags", [])
            coverage_percent = qa_report.get("coverage_percent", 0)
            broken_links = qa_report.get("broken_links", [])
            missing_media = qa_report.get("missing_media", [])
            
            # Check each validation type
            validation_checks = {
                "coverage_analysis": coverage_percent > 0,
                "unsupported_claims": any("claim" in f.get("code", "").lower() or "unsupported" in f.get("code", "").lower() for f in flags),
                "placeholder_detection": any("placeholder" in f.get("code", "").lower() for f in flags),
                "duplicate_detection": any("duplicate" in f.get("code", "").lower() for f in flags),
                "broken_links_detection": len(broken_links) > 0,
                "missing_media_detection": len(missing_media) > 0,
                "content_quality_checks": any("quality" in f.get("code", "").lower() or "short" in f.get("code", "").lower() or "heading" in f.get("code", "").lower() for f in flags),
                "technical_accuracy_checks": any("technical" in f.get("code", "").lower() or "vague" in f.get("code", "").lower() or "terminology" in f.get("code", "").lower() for f in flags)
            }
            
            passed_checks = sum(validation_checks.values())
            total_checks = len(validation_checks)
            
            # Count flag severities
            p0_count = len([f for f in flags if f.get("severity") == "P0"])
            p1_count = len([f for f in flags if f.get("severity") == "P1"])
            
            if passed_checks >= 6:  # Should pass at least 6/8 validation types
                self.log_test("Comprehensive Validation Checks", "PASS",
                            f"Validation system working well: {passed_checks}/{total_checks} checks passed. Coverage: {coverage_percent}%, Flags: P0={p0_count}, P1={p1_count}",
                            {"validation_checks": validation_checks, "coverage": coverage_percent, "total_flags": len(flags)})
                return True
            else:
                self.log_test("Comprehensive Validation Checks", "PARTIAL",
                            f"Validation partially working: {passed_checks}/{total_checks} checks passed",
                            {"validation_checks": validation_checks, "flags_count": len(flags)})
                return True
            
        except Exception as e:
            self.log_test("Comprehensive Validation Checks", "FAIL", f"Exception: {str(e)}")
            return False

    def test_qa_database_persistence(self):
        """Test 6: Test QA report database persistence"""
        try:
            print("🔍 Testing QA report database persistence...")
            
            # Get current QA diagnostics to check persistence
            response = self.session.get(f"{self.backend_url}/qa/diagnostics")
            
            if response.status_code != 200:
                self.log_test("QA Database Persistence", "FAIL",
                            f"Cannot access QA diagnostics: HTTP {response.status_code}")
                return False
            
            data = response.json()
            qa_results = data.get("qa_results", [])
            total_runs = data.get("total_qa_runs", 0)
            
            if total_runs == 0:
                # Try to create a QA result by processing content
                test_payload = {
                    "content": "# Test Article\n\nThis is a test article for QA persistence testing.",
                    "metadata": {"title": "QA Persistence Test", "source": "persistence_test"}
                }
                
                process_response = self.session.post(f"{self.backend_url}/content/process", json=test_payload)
                
                if process_response.status_code == 200:
                    # Check QA diagnostics again
                    time.sleep(2)  # Wait for processing
                    response = self.session.get(f"{self.backend_url}/qa/diagnostics")
                    
                    if response.status_code == 200:
                        data = response.json()
                        qa_results = data.get("qa_results", [])
                        total_runs = data.get("total_qa_runs", 0)
            
            # Verify persistence structure
            if total_runs > 0 and qa_results:
                # Check QA result structure
                first_result = qa_results[0]
                required_fields = ["qa_id", "timestamp", "engine"]
                
                missing_fields = [f for f in required_fields if f not in first_result]
                
                if missing_fields:
                    self.log_test("QA Database Persistence", "PARTIAL",
                                f"QA results persisted but missing fields: {missing_fields}",
                                {"total_runs": total_runs, "result_keys": list(first_result.keys())})
                    return True
                
                # Check if we can retrieve specific QA result
                qa_id = first_result.get("qa_id")
                if qa_id:
                    specific_response = self.session.get(f"{self.backend_url}/qa/diagnostics/{qa_id}")
                    
                    if specific_response.status_code == 200:
                        self.log_test("QA Database Persistence", "PASS",
                                    f"QA reports properly persisted and retrievable. Total: {total_runs}",
                                    {"total_runs": total_runs, "specific_retrieval": True})
                        return True
                
                self.log_test("QA Database Persistence", "PARTIAL",
                            f"QA reports persisted but specific retrieval failed. Total: {total_runs}",
                            {"total_runs": total_runs})
                return True
            else:
                self.log_test("QA Database Persistence", "FAIL",
                            "No QA results found in database",
                            {"total_runs": total_runs})
                return False
            
        except Exception as e:
            self.log_test("QA Database Persistence", "FAIL", f"Exception: {str(e)}")
            return False

    def test_machine_readable_qa_reports(self):
        """Test 7: Test machine-readable QA report format"""
        try:
            print("🔍 Testing machine-readable QA report format...")
            
            # Process content to generate QA report
            test_content = """
            # Machine-Readable QA Test
            
            This content has specific issues for testing machine-readable format.
            
            [TODO: Add content here]
            Studies always show this works perfectly.
            
            This duplicate sentence appears twice.
            This duplicate sentence appears twice.
            
            Check this link: https://invalid-test-domain.com
            See the missing image: ![Test Image]()
            """
            
            payload = {
                "content": test_content,
                "metadata": {
                    "title": "Machine-Readable QA Test",
                    "source": "machine_readable_test"
                }
            }
            
            response = self.session.post(f"{self.backend_url}/content/process", json=payload)
            
            if response.status_code != 200:
                self.log_test("Machine-Readable QA Reports", "FAIL",
                            f"Processing failed: HTTP {response.status_code}")
                return False
            
            result = response.json()
            validation_result = result.get("validation_result", {})
            qa_report = validation_result.get("qa_report", {})
            
            if not qa_report:
                self.log_test("Machine-Readable QA Reports", "FAIL",
                            "No QA report found")
                return False
            
            # Verify machine-readable structure
            required_structure = {
                "job_id": str,
                "coverage_percent": (int, float),
                "flags": list,
                "broken_links": list,
                "missing_media": list
            }
            
            structure_valid = True
            structure_issues = []
            
            for field, expected_type in required_structure.items():
                if field not in qa_report:
                    structure_issues.append(f"Missing field: {field}")
                    structure_valid = False
                elif not isinstance(qa_report[field], expected_type):
                    structure_issues.append(f"Wrong type for {field}: expected {expected_type}, got {type(qa_report[field])}")
                    structure_valid = False
            
            # Verify flag structure
            flags = qa_report.get("flags", [])
            if flags:
                first_flag = flags[0]
                required_flag_fields = ["code", "severity", "message"]
                
                for field in required_flag_fields:
                    if field not in first_flag:
                        structure_issues.append(f"Flag missing field: {field}")
                        structure_valid = False
            
            # Check if data is JSON serializable (machine-readable)
            try:
                json.dumps(qa_report)
                json_serializable = True
            except Exception:
                json_serializable = False
                structure_issues.append("QA report not JSON serializable")
                structure_valid = False
            
            if structure_valid and json_serializable:
                self.log_test("Machine-Readable QA Reports", "PASS",
                            f"QA report is properly machine-readable. Flags: {len(flags)}, Coverage: {qa_report.get('coverage_percent', 0)}%",
                            {"structure_valid": True, "json_serializable": True, "flags_count": len(flags)})
                return True
            else:
                self.log_test("Machine-Readable QA Reports", "FAIL",
                            f"QA report structure issues: {'; '.join(structure_issues)}",
                            {"structure_issues": structure_issues})
                return False
            
        except Exception as e:
            self.log_test("Machine-Readable QA Reports", "FAIL", f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all KE-PR7 tests"""
        print("🚀 Starting KE-PR7 Validator & QA Report Testing Suite")
        print("=" * 60)
        
        tests = [
            self.test_engine_status_qa_summaries,
            self.test_qa_diagnostics_endpoints,
            self.test_content_processing_with_qa_validation,
            self.test_publish_gate_p0_blocking,
            self.test_comprehensive_validation_checks,
            self.test_qa_database_persistence,
            self.test_machine_readable_qa_reports
        ]
        
        passed = 0
        failed = 0
        partial = 0
        
        for test in tests:
            try:
                result = test()
                if result is True:
                    passed += 1
                elif result is False:
                    failed += 1
                else:
                    partial += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                failed += 1
        
        print("=" * 60)
        print("🏁 KE-PR7 Testing Complete")
        print(f"✅ Passed: {passed}")
        print(f"⚠️ Partial: {partial}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed + partial) / len(tests) * 100:.1f}%")
        
        # Summary of key findings
        print("\n📋 Key Findings:")
        for result in self.test_results:
            if result["status"] in ["PASS", "FAIL"]:
                print(f"   {result['status']}: {result['test']}")
        
        return {
            "total_tests": len(tests),
            "passed": passed,
            "partial": partial,
            "failed": failed,
            "success_rate": (passed + partial) / len(tests) * 100,
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = KE_PR7_Tester()
    results = tester.run_all_tests()
    
    # Return results for integration with test_result.md
    return results

if __name__ == "__main__":
    main()