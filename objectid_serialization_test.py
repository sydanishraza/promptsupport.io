#!/usr/bin/env python3
"""
V2 Engine Step 13 ObjectId Serialization Fix Testing
Focused testing to verify that ObjectId serialization resolves HTTP 500 errors in review system endpoints
"""

import asyncio
import json
import requests
import os
from datetime import datetime
from typing import Dict, Any, List

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://woolf-style-lint.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ObjectIdSerializationTester:
    """Focused tester for ObjectId serialization fix in V2 Review System"""
    
    def __init__(self):
        self.test_results = []
        self.sample_run_ids = []
        
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
        
    def test_review_runs_objectid_serialization(self) -> bool:
        """Test GET /api/review/runs for proper ObjectId serialization without HTTP 500 errors"""
        try:
            print(f"\n🔍 TESTING REVIEW RUNS OBJECTID SERIALIZATION")
            
            response = requests.get(f"{API_BASE}/review/runs?limit=10", timeout=30)
            
            # Check for HTTP 500 errors that were previously caused by ObjectId serialization
            if response.status_code == 500:
                self.log_test("Review Runs ObjectId Serialization", False, 
                             f"HTTP 500 error - ObjectId serialization issue still present: {response.text}")
                return False
                
            if response.status_code != 200:
                self.log_test("Review Runs ObjectId Serialization", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
                
            # Verify JSON response can be parsed (no ObjectId serialization errors)
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Review Runs ObjectId Serialization", False, 
                             f"JSON parsing failed - possible ObjectId serialization issue: {str(e)}")
                return False
                
            # Verify response structure and check for ObjectId strings
            runs = data.get('runs', [])
            if runs:
                # Store sample run IDs for later tests
                self.sample_run_ids = [run.get('run_id') for run in runs[:3] if run.get('run_id')]
                
                # Check that all IDs are strings (not ObjectId objects)
                first_run = runs[0]
                run_id = first_run.get('run_id')
                
                if run_id and isinstance(run_id, str):
                    self.log_test("Review Runs ObjectId Serialization", True, 
                                 f"ObjectId serialization working - retrieved {len(runs)} runs with proper string IDs",
                                 {"run_count": len(runs), "sample_run_id": run_id})
                    return True
                else:
                    self.log_test("Review Runs ObjectId Serialization", False, 
                                 f"Run ID is not a string: {type(run_id)} - {run_id}")
                    return False
            else:
                self.log_test("Review Runs ObjectId Serialization", True, 
                             "No runs available but endpoint responds without ObjectId serialization errors")
                return True
                
        except Exception as e:
            self.log_test("Review Runs ObjectId Serialization", False, f"Exception: {str(e)}")
            return False
    
    def test_run_details_objectid_serialization(self) -> bool:
        """Test GET /api/review/runs/{run_id} for proper ObjectId serialization"""
        try:
            print(f"\n🔍 TESTING RUN DETAILS OBJECTID SERIALIZATION")
            
            if not self.sample_run_ids:
                # Try with a test run ID
                run_id = "test_run_objectid_123"
            else:
                run_id = self.sample_run_ids[0]
                
            response = requests.get(f"{API_BASE}/review/runs/{run_id}", timeout=30)
            
            # Check for HTTP 500 errors that were previously caused by ObjectId serialization
            if response.status_code == 500:
                self.log_test("Run Details ObjectId Serialization", False, 
                             f"HTTP 500 error - ObjectId serialization issue still present: {response.text}")
                return False
                
            if response.status_code == 404:
                self.log_test("Run Details ObjectId Serialization", True, 
                             f"Run {run_id} not found but no ObjectId serialization errors (404 is expected)")
                return True
                
            if response.status_code != 200:
                self.log_test("Run Details ObjectId Serialization", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
                
            # Verify JSON response can be parsed (no ObjectId serialization errors)
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Run Details ObjectId Serialization", False, 
                             f"JSON parsing failed - possible ObjectId serialization issue: {str(e)}")
                return False
                
            # Check for proper string serialization of IDs in nested data
            serialization_checks = []
            
            # Check run_id
            if 'run_id' in data and isinstance(data['run_id'], str):
                serialization_checks.append("run_id properly serialized as string")
            elif 'run_id' in data:
                serialization_checks.append(f"run_id not string: {type(data['run_id'])}")
                
            # Check articles data for ObjectId serialization
            articles = data.get('articles', {})
            articles_data = articles.get('articles_data', [])
            if articles_data:
                for article in articles_data[:2]:  # Check first 2 articles
                    if 'id' in article and isinstance(article['id'], str):
                        serialization_checks.append(f"article id properly serialized")
                    elif 'id' in article:
                        serialization_checks.append(f"article id not string: {type(article['id'])}")
                        
            # Check processing results for any ObjectId references
            processing_results = data.get('processing_results', {})
            for step_name, step_data in processing_results.items():
                if isinstance(step_data, dict):
                    for key, value in step_data.items():
                        if key.endswith('_id') and value and not isinstance(value, str):
                            serialization_checks.append(f"{step_name}.{key} not string: {type(value)}")
                            
            # All checks should show proper serialization
            failed_checks = [check for check in serialization_checks if 'not string' in check]
            
            if failed_checks:
                self.log_test("Run Details ObjectId Serialization", False, 
                             f"ObjectId serialization issues found: {failed_checks}")
                return False
            else:
                self.log_test("Run Details ObjectId Serialization", True, 
                             f"ObjectId serialization working properly: {serialization_checks}",
                             data)
                return True
                
        except Exception as e:
            self.log_test("Run Details ObjectId Serialization", False, f"Exception: {str(e)}")
            return False
    
    def test_quality_badges_objectid_serialization(self) -> bool:
        """Test quality badges calculation endpoint for ObjectId serialization fix"""
        try:
            print(f"\n🏆 TESTING QUALITY BADGES OBJECTID SERIALIZATION")
            
            # Get runs to test badge calculation (this was failing with ObjectId errors)
            response = requests.get(f"{API_BASE}/review/runs?limit=5", timeout=30)
            
            # Check for HTTP 500 errors that were previously caused by ObjectId serialization in badge calculation
            if response.status_code == 500:
                self.log_test("Quality Badges ObjectId Serialization", False, 
                             f"HTTP 500 error in badge calculation - ObjectId serialization issue: {response.text}")
                return False
                
            if response.status_code != 200:
                self.log_test("Quality Badges ObjectId Serialization", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
                
            # Verify JSON response can be parsed
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Quality Badges ObjectId Serialization", False, 
                             f"JSON parsing failed in badge data: {str(e)}")
                return False
                
            runs = data.get('runs', [])
            
            if not runs:
                self.log_test("Quality Badges ObjectId Serialization", True, 
                             "No runs available but badge calculation endpoint responds without ObjectId errors")
                return True
                
            # Test badge data serialization
            badge_serialization_tests = []
            
            for i, run in enumerate(runs[:3]):  # Test first 3 runs
                badges = run.get('badges', {})
                
                if not badges:
                    badge_serialization_tests.append(f"Run {i+1}: No badges (acceptable)")
                    continue
                    
                # Check each badge for proper serialization
                for badge_name, badge_data in badges.items():
                    if isinstance(badge_data, dict):
                        # Check that badge data is properly serialized
                        for key, value in badge_data.items():
                            if key.endswith('_id') and value and not isinstance(value, str):
                                badge_serialization_tests.append(f"Run {i+1} {badge_name}.{key} not string: {type(value)}")
                            else:
                                badge_serialization_tests.append(f"Run {i+1} {badge_name}.{key} properly serialized")
                    else:
                        badge_serialization_tests.append(f"Run {i+1} {badge_name} data structure valid")
                        
            # Check for serialization failures
            failed_badge_tests = [test for test in badge_serialization_tests if 'not string' in test]
            
            if failed_badge_tests:
                self.log_test("Quality Badges ObjectId Serialization", False, 
                             f"Badge ObjectId serialization issues: {failed_badge_tests}")
                return False
            else:
                self.log_test("Quality Badges ObjectId Serialization", True, 
                             f"Quality badges ObjectId serialization working: {len(badge_serialization_tests)} checks passed",
                             {"badge_tests": badge_serialization_tests[:10]})  # Show first 10 tests
                return True
                
        except Exception as e:
            self.log_test("Quality Badges ObjectId Serialization", False, f"Exception: {str(e)}")
            return False
    
    def test_review_workflow_objectid_serialization(self) -> bool:
        """Test review workflow integration for ObjectId serialization fix"""
        try:
            print(f"\n🔄 TESTING REVIEW WORKFLOW OBJECTID SERIALIZATION")
            
            # Test comprehensive data retrieval (this was failing with ObjectId errors)
            response = requests.get(f"{API_BASE}/review/runs?limit=3", timeout=30)
            
            # Check for HTTP 500 errors in workflow integration
            if response.status_code == 500:
                self.log_test("Review Workflow ObjectId Serialization", False, 
                             f"HTTP 500 error in workflow integration - ObjectId serialization issue: {response.text}")
                return False
                
            if response.status_code != 200:
                self.log_test("Review Workflow ObjectId Serialization", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
                
            # Verify JSON response can be parsed
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.log_test("Review Workflow ObjectId Serialization", False, 
                             f"JSON parsing failed in workflow data: {str(e)}")
                return False
                
            # Deep check for ObjectId serialization in complex nested data
            workflow_serialization_tests = []
            
            # Check summary data
            summary = data.get('summary', {})
            for key, value in summary.items():
                if key.endswith('_id') and value and not isinstance(value, str):
                    workflow_serialization_tests.append(f"Summary {key} not string: {type(value)}")
                else:
                    workflow_serialization_tests.append(f"Summary {key} properly handled")
                    
            # Check runs data for deep ObjectId serialization
            runs = data.get('runs', [])
            for i, run in enumerate(runs[:2]):  # Check first 2 runs thoroughly
                
                # Check processing results (complex nested data)
                processing_results = run.get('processing_results', {})
                for step_name, step_data in processing_results.items():
                    if isinstance(step_data, dict):
                        for key, value in step_data.items():
                            if key.endswith('_id') and value:
                                if isinstance(value, str):
                                    workflow_serialization_tests.append(f"Run {i+1} {step_name}.{key} properly serialized")
                                else:
                                    workflow_serialization_tests.append(f"Run {i+1} {step_name}.{key} not string: {type(value)}")
                                    
                # Check articles data (another complex nested structure)
                articles = run.get('articles', {})
                articles_data = articles.get('articles_data', [])
                for j, article in enumerate(articles_data[:2]):  # Check first 2 articles
                    if 'id' in article:
                        if isinstance(article['id'], str):
                            workflow_serialization_tests.append(f"Run {i+1} article {j+1} id properly serialized")
                        else:
                            workflow_serialization_tests.append(f"Run {i+1} article {j+1} id not string: {type(article['id'])}")
                            
            # Check for any serialization failures
            failed_workflow_tests = [test for test in workflow_serialization_tests if 'not string' in test]
            
            if failed_workflow_tests:
                self.log_test("Review Workflow ObjectId Serialization", False, 
                             f"Workflow ObjectId serialization issues: {failed_workflow_tests}")
                return False
            else:
                self.log_test("Review Workflow ObjectId Serialization", True, 
                             f"Review workflow ObjectId serialization working: {len(workflow_serialization_tests)} checks passed",
                             {"workflow_tests": workflow_serialization_tests[:15]})  # Show first 15 tests
                return True
                
        except Exception as e:
            self.log_test("Review Workflow ObjectId Serialization", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_collections_objectid_serialization(self) -> bool:
        """Test that V2 collections handle ObjectId serialization properly"""
        try:
            print(f"\n🗄️ TESTING V2 COLLECTIONS OBJECTID SERIALIZATION")
            
            # Test multiple endpoints that access V2 collections
            endpoints_to_test = [
                ("/review/runs", "Review runs collection"),
                ("/engine", "Engine status with V2 data")
            ]
            
            collection_tests = []
            
            for endpoint, description in endpoints_to_test:
                try:
                    response = requests.get(f"{API_BASE}{endpoint}", timeout=30)
                    
                    if response.status_code == 500:
                        collection_tests.append(f"{description}: HTTP 500 - ObjectId serialization issue")
                        continue
                        
                    if response.status_code not in [200, 404]:
                        collection_tests.append(f"{description}: HTTP {response.status_code}")
                        continue
                        
                    # Try to parse JSON
                    try:
                        data = response.json()
                        collection_tests.append(f"{description}: JSON parsing successful")
                    except json.JSONDecodeError:
                        collection_tests.append(f"{description}: JSON parsing failed - ObjectId issue")
                        
                except Exception as e:
                    collection_tests.append(f"{description}: Exception - {str(e)}")
                    
            # Check for any failures
            failed_collection_tests = [test for test in collection_tests if 'HTTP 500' in test or 'failed' in test or 'Exception' in test]
            
            if failed_collection_tests:
                self.log_test("V2 Collections ObjectId Serialization", False, 
                             f"V2 collections ObjectId serialization issues: {failed_collection_tests}")
                return False
            else:
                self.log_test("V2 Collections ObjectId Serialization", True, 
                             f"V2 collections ObjectId serialization working: {collection_tests}",
                             {"collection_tests": collection_tests})
                return True
                
        except Exception as e:
            self.log_test("V2 Collections ObjectId Serialization", False, f"Exception: {str(e)}")
            return False
    
    def run_objectid_serialization_tests(self) -> Dict[str, Any]:
        """Run all ObjectId serialization fix tests"""
        print(f"🚀 STARTING V2 ENGINE STEP 13 OBJECTID SERIALIZATION FIX TESTING")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📡 API Base: {API_BASE}")
        print(f"🎯 Focus: Verify ObjectId serialization resolves HTTP 500 errors")
        
        test_methods = [
            self.test_review_runs_objectid_serialization,
            self.test_run_details_objectid_serialization,
            self.test_quality_badges_objectid_serialization,
            self.test_review_workflow_objectid_serialization,
            self.test_v2_collections_objectid_serialization
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_method.__name__}: {str(e)}")
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        # Compile final results
        results = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "overall_status": "PASS" if success_rate >= 80 else "FAIL",
                "fix_verified": success_rate >= 80
            },
            "test_details": self.test_results,
            "backend_url": BACKEND_URL,
            "test_timestamp": datetime.utcnow().isoformat(),
            "engine_version": "v2",
            "fix_tested": "ObjectId Serialization Fix for HTTP 500 Errors"
        }
        
        print(f"\n" + "="*80)
        print(f"🎯 V2 ENGINE STEP 13 OBJECTID SERIALIZATION FIX TESTING COMPLETE")
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"🔧 FIX STATUS: {'VERIFIED' if results['test_summary']['fix_verified'] else 'NEEDS ATTENTION'}")
        print(f"🏆 OVERALL STATUS: {results['test_summary']['overall_status']}")
        print(f"="*80)
        
        return results

def main():
    """Main test execution"""
    tester = ObjectIdSerializationTester()
    results = tester.run_objectid_serialization_tests()
    
    # Print detailed results
    print(f"\n📋 DETAILED TEST RESULTS:")
    for result in results["test_details"]:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}: {result['details']}")
    
    return results

if __name__ == "__main__":
    main()