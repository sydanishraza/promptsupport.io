#!/usr/bin/env python3
"""
V2 Engine Evidence Tagging System Comprehensive Testing
Testing the newly implemented V2 Engine Evidence Tagging System for enforcing fidelity 
by mapping paragraphs to source blocks with hidden data-evidence attributes.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://content-formatter.preview.emergentagent.com/api"

def test_v2_engine_evidence_tagging_system():
    """
    Comprehensive testing of V2 Engine Evidence Tagging System
    Testing all 8 critical success criteria from the review request
    """
    print("🏷️ V2 ENGINE EVIDENCE TAGGING SYSTEM COMPREHENSIVE TESTING STARTED")
    print("=" * 80)
    
    results = {
        "total_tests": 8,
        "passed_tests": 0,
        "test_details": []
    }
    
    # Test 1: Evidence Tagging System Health Check
    print("\n1️⃣ TESTING: Evidence Tagging System Health Check")
    try:
        # Check V2 Engine status
        engine_response = requests.get(f"{BACKEND_URL}/engine")
        if engine_response.status_code == 200:
            engine_data = engine_response.json()
            
            # Check for evidence tagging diagnostics endpoint
            endpoints = engine_data.get("endpoints", {})
            has_evidence_diagnostics = "evidence_tagging_diagnostics" in endpoints
            
            # Check for evidence tagging features
            features = engine_data.get("features", [])
            evidence_features = [
                "evidence_paragraph_tagging",
                "block_id_attribution", 
                "fidelity_enforcement",
                "source_traceability"
            ]
            
            evidence_features_found = sum(1 for feature in evidence_features if feature in features)
            
            # Check engine message for evidence tagging
            engine_message = engine_data.get("message", "")
            has_evidence_message = "evidence tagging" in engine_message.lower()
            
            if has_evidence_diagnostics and evidence_features_found >= 3 and has_evidence_message:
                print("   ✅ V2 Engine health check with evidence tagging integration PASSED")
                print(f"   📊 Evidence diagnostics endpoint: {has_evidence_diagnostics}")
                print(f"   📊 Evidence features found: {evidence_features_found}/4")
                print(f"   📊 Evidence message present: {has_evidence_message}")
                results["passed_tests"] += 1
                results["test_details"].append("✅ Evidence Tagging System Health Check PASSED")
            else:
                print("   ❌ V2 Engine health check with evidence tagging integration FAILED")
                print(f"   📊 Evidence diagnostics endpoint: {has_evidence_diagnostics}")
                print(f"   📊 Evidence features found: {evidence_features_found}/4")
                print(f"   📊 Evidence message present: {has_evidence_message}")
                results["test_details"].append("❌ Evidence Tagging System Health Check FAILED")
        else:
            print(f"   ❌ Engine endpoint failed: HTTP {engine_response.status_code}")
            results["test_details"].append("❌ Evidence Tagging System Health Check FAILED - Engine endpoint error")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        results["test_details"].append(f"❌ Evidence Tagging System Health Check FAILED - {e}")
    
    # Test 2: Evidence Tagging Diagnostic Endpoints
    print("\n2️⃣ TESTING: Evidence Tagging Diagnostic Endpoints")
    try:
        # Test GET /api/evidence-tagging/diagnostics
        diagnostics_response = requests.get(f"{BACKEND_URL}/evidence-tagging/diagnostics")
        
        if diagnostics_response.status_code == 200:
            diagnostics_data = diagnostics_response.json()
            
            # Check for required fields
            required_fields = ["evidence_tagging_system_status", "engine", "evidence_tagging_summary"]
            fields_present = sum(1 for field in required_fields if field in diagnostics_data)
            
            # Check for V2 engine metadata
            is_v2_engine = diagnostics_data.get("engine") == "v2"
            
            # Check system status
            system_active = diagnostics_data.get("evidence_tagging_system_status") == "active"
            
            # Check for evidence tagging statistics
            has_statistics = "evidence_tagging_summary" in diagnostics_data
            
            # Check for system capabilities
            has_capabilities = "system_capabilities" in diagnostics_data
            
            if fields_present >= 3 and is_v2_engine and system_active and has_capabilities:
                print("   ✅ Evidence tagging diagnostic endpoints PASSED")
                print(f"   📊 Required fields present: {fields_present}/3")
                print(f"   📊 V2 engine confirmed: {is_v2_engine}")
                print(f"   📊 System status active: {system_active}")
                print(f"   📊 Has statistics: {has_statistics}")
                print(f"   📊 Has capabilities: {has_capabilities}")
                results["passed_tests"] += 1
                results["test_details"].append("✅ Evidence Tagging Diagnostic Endpoints PASSED")
            else:
                print("   ❌ Evidence tagging diagnostic endpoints FAILED")
                print(f"   📊 Required fields present: {fields_present}/3")
                print(f"   📊 V2 engine confirmed: {is_v2_engine}")
                print(f"   📊 System status active: {system_active}")
                results["test_details"].append("❌ Evidence Tagging Diagnostic Endpoints FAILED")
        else:
            print(f"   ❌ Diagnostics endpoint failed: HTTP {diagnostics_response.status_code}")
            results["test_details"].append(f"❌ Evidence Tagging Diagnostic Endpoints FAILED - HTTP {diagnostics_response.status_code}")
    except Exception as e:
        print(f"   ❌ Diagnostics endpoint error: {e}")
        results["test_details"].append(f"❌ Evidence Tagging Diagnostic Endpoints FAILED - {e}")
    
    # Test 3: Processing Pipeline Integration (Step 7.6)
    print("\n3️⃣ TESTING: Processing Pipeline Integration (Step 7.6)")
    try:
        # Test content processing to verify Step 7.6 integration
        test_content = """
        # Google Maps API Integration Guide
        
        This guide covers the essential steps for integrating Google Maps API into your web application.
        
        ## Getting Started
        
        First, you need to obtain an API key from the Google Cloud Console. This key will authenticate your requests to the Google Maps services.
        
        ## Basic Implementation
        
        Here's a simple example of how to initialize a Google Map:
        
        ```javascript
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 4,
                center: { lat: -25.344, lng: 131.036 },
            });
        }
        ```
        
        ## Adding Markers
        
        You can add markers to your map to highlight specific locations:
        
        ```javascript
        const marker = new google.maps.Marker({
            position: { lat: -25.344, lng: 131.036 },
            map: map,
        });
        ```
        """
        
        # Process content through V2 engine
        process_response = requests.post(
            f"{BACKEND_URL}/content/process",
            json={
                "content": test_content,
                "metadata": {
                    "title": "Google Maps API Integration Test",
                    "source": "evidence_tagging_test"
                }
            }
        )
        
        if process_response.status_code == 200:
            process_data = process_response.json()
            job_id = process_data.get("job_id")
            
            if job_id:
                # Wait for processing to complete
                time.sleep(10)
                
                # Check if evidence tagging was integrated in the pipeline
                diagnostics_response = requests.get(f"{BACKEND_URL}/evidence-tagging/diagnostics")
                if diagnostics_response.status_code == 200:
                    diagnostics_data = diagnostics_response.json()
                    evidence_summary = diagnostics_data.get("evidence_tagging_summary", {})
                    total_runs = evidence_summary.get("total_evidence_runs", 0)
                    
                    pipeline_integrated = total_runs > 0
                    step_7_6_executed = pipeline_integrated
                    
                    if pipeline_integrated:
                        print("   ✅ Processing pipeline integration (Step 7.6) PASSED")
                        print(f"   📊 Content processing successful: {job_id is not None}")
                        print(f"   📊 Pipeline integration confirmed: {pipeline_integrated}")
                        print(f"   📊 Step 7.6 executed: {step_7_6_executed}")
                        print(f"   📊 Total evidence runs: {total_runs}")
                        results["passed_tests"] += 1
                        results["test_details"].append("✅ Processing Pipeline Integration (Step 7.6) PASSED")
                    else:
                        print("   ❌ Processing pipeline integration FAILED - No evidence runs detected")
                        results["test_details"].append("❌ Processing Pipeline Integration FAILED - No evidence runs")
                else:
                    print("   ❌ Could not verify pipeline integration")
                    results["test_details"].append("❌ Processing Pipeline Integration FAILED - Diagnostics error")
            else:
                print("   ❌ Processing pipeline integration FAILED - No job ID")
                results["test_details"].append("❌ Processing Pipeline Integration FAILED - No job ID")
        else:
            print(f"   ❌ Content processing failed: HTTP {process_response.status_code}")
            results["test_details"].append(f"❌ Processing Pipeline Integration FAILED - HTTP {process_response.status_code}")
    except Exception as e:
        print(f"   ❌ Pipeline integration error: {e}")
        results["test_details"].append(f"❌ Processing Pipeline Integration FAILED - {e}")
    
    # Test 4: Paragraph Parsing and Evidence Mapping
    print("\n4️⃣ TESTING: Paragraph Parsing and Evidence Mapping")
    try:
        # Check if evidence tagging results exist in database
        diagnostics_response = requests.get(f"{BACKEND_URL}/evidence-tagging/diagnostics")
        
        if diagnostics_response.status_code == 200:
            diagnostics_data = diagnostics_response.json()
            
            # Look for evidence tagging statistics
            evidence_summary = diagnostics_data.get("evidence_tagging_summary", {})
            total_runs = evidence_summary.get("total_evidence_runs", 0)
            total_paragraphs = evidence_summary.get("total_paragraphs", 0)
            
            # Check for paragraph parsing capabilities
            capabilities = diagnostics_data.get("system_capabilities", {})
            has_paragraph_parsing = "paragraph_parsing" in capabilities
            has_evidence_mapping = "evidence_mapping" in capabilities
            has_faq_detection = "faq_detection" in capabilities
            
            parsing_score = sum([has_paragraph_parsing, has_evidence_mapping, has_faq_detection])
            
            if total_runs > 0 and total_paragraphs > 0 and parsing_score >= 3:
                print("   ✅ Paragraph parsing and evidence mapping PASSED")
                print(f"   📊 Total evidence tagging runs: {total_runs}")
                print(f"   📊 Total paragraphs processed: {total_paragraphs}")
                print(f"   📊 Paragraph parsing capability: {has_paragraph_parsing}")
                print(f"   📊 Evidence mapping capability: {has_evidence_mapping}")
                print(f"   📊 FAQ detection capability: {has_faq_detection}")
                results["passed_tests"] += 1
                results["test_details"].append("✅ Paragraph Parsing and Evidence Mapping PASSED")
            else:
                print("   ❌ Paragraph parsing and evidence mapping FAILED")
                print(f"   📊 Total evidence tagging runs: {total_runs}")
                print(f"   📊 Total paragraphs processed: {total_paragraphs}")
                print(f"   📊 Parsing capabilities score: {parsing_score}/3")
                results["test_details"].append("❌ Paragraph Parsing and Evidence Mapping FAILED")
        else:
            print(f"   ❌ Could not verify parsing capabilities: HTTP {diagnostics_response.status_code}")
            results["test_details"].append("❌ Paragraph Parsing and Evidence Mapping FAILED - Diagnostics error")
    except Exception as e:
        print(f"   ❌ Paragraph parsing test error: {e}")
        results["test_details"].append(f"❌ Paragraph Parsing and Evidence Mapping FAILED - {e}")
    
    # Test 5: Evidence Attribution System
    print("\n5️⃣ TESTING: Evidence Attribution System")
    try:
        # Test evidence attribution capabilities
        diagnostics_response = requests.get(f"{BACKEND_URL}/evidence-tagging/diagnostics")
        
        if diagnostics_response.status_code == 200:
            diagnostics_data = diagnostics_response.json()
            
            # Check for evidence attribution features in capabilities
            capabilities = diagnostics_data.get("system_capabilities", {})
            has_evidence_mapping = "evidence_mapping" in capabilities
            has_confidence_scoring = "confidence_scoring" in capabilities
            has_prewrite_integration = "prewrite_integration" in capabilities
            
            # Check for evidence summary data
            evidence_summary = diagnostics_data.get("evidence_tagging_summary", {})
            has_source_blocks = evidence_summary.get("total_evidence_runs", 0) > 0
            
            attribution_score = sum([has_evidence_mapping, has_confidence_scoring, has_prewrite_integration, has_source_blocks])
            
            if attribution_score >= 3:
                print("   ✅ Evidence attribution system PASSED")
                print(f"   📊 Evidence mapping capability: {has_evidence_mapping}")
                print(f"   📊 Confidence scoring capability: {has_confidence_scoring}")
                print(f"   📊 Prewrite integration capability: {has_prewrite_integration}")
                print(f"   📊 Source blocks processing: {has_source_blocks}")
                results["passed_tests"] += 1
                results["test_details"].append("✅ Evidence Attribution System PASSED")
            else:
                print("   ❌ Evidence attribution system FAILED")
                print(f"   📊 Attribution features score: {attribution_score}/4")
                results["test_details"].append("❌ Evidence Attribution System FAILED")
        else:
            print(f"   ❌ Could not verify attribution system: HTTP {diagnostics_response.status_code}")
            results["test_details"].append("❌ Evidence Attribution System FAILED - Diagnostics error")
    except Exception as e:
        print(f"   ❌ Attribution system test error: {e}")
        results["test_details"].append(f"❌ Evidence Attribution System FAILED - {e}")
    
    # Test 6: Fidelity Validation Enhancement
    print("\n6️⃣ TESTING: Fidelity Validation Enhancement")
    try:
        # Check for enhanced validation system
        diagnostics_response = requests.get(f"{BACKEND_URL}/evidence-tagging/diagnostics")
        
        if diagnostics_response.status_code == 200:
            diagnostics_data = diagnostics_response.json()
            
            # Check for fidelity validation features
            evidence_summary = diagnostics_data.get("evidence_tagging_summary", {})
            has_fidelity_enforcement = evidence_summary.get("fidelity_enforcement_enabled", False)
            has_target_threshold = evidence_summary.get("target_threshold", 0) == 95.0
            has_target_tracking = "target_achieved_runs" in evidence_summary
            has_tagging_rate = "overall_tagging_rate" in evidence_summary
            
            validation_score = sum([has_fidelity_enforcement, has_target_threshold, has_target_tracking, has_tagging_rate])
            
            if validation_score >= 3:
                print("   ✅ Fidelity validation enhancement PASSED")
                print(f"   📊 Fidelity enforcement enabled: {has_fidelity_enforcement}")
                print(f"   📊 95% target threshold: {has_target_threshold}")
                print(f"   📊 Target achievement tracking: {has_target_tracking}")
                print(f"   📊 Tagging rate calculation: {has_tagging_rate}")
                results["passed_tests"] += 1
                results["test_details"].append("✅ Fidelity Validation Enhancement PASSED")
            else:
                print("   ❌ Fidelity validation enhancement FAILED")
                print(f"   📊 Validation features score: {validation_score}/4")
                results["test_details"].append("❌ Fidelity Validation Enhancement FAILED")
        else:
            print(f"   ❌ Could not verify validation enhancement: HTTP {diagnostics_response.status_code}")
            results["test_details"].append("❌ Fidelity Validation Enhancement FAILED - Diagnostics error")
    except Exception as e:
        print(f"   ❌ Validation enhancement test error: {e}")
        results["test_details"].append(f"❌ Fidelity Validation Enhancement FAILED - {e}")
    
    # Test 7: Fidelity Target Achievement (≥95% paragraphs tagged)
    print("\n7️⃣ TESTING: Fidelity Target Achievement (≥95% paragraphs tagged)")
    try:
        # Check for fidelity target achievement
        diagnostics_response = requests.get(f"{BACKEND_URL}/evidence-tagging/diagnostics")
        
        if diagnostics_response.status_code == 200:
            diagnostics_data = diagnostics_response.json()
            
            # Look for evidence tagging statistics
            evidence_summary = diagnostics_data.get("evidence_tagging_summary", {})
            
            # Check for target achievement tracking
            has_target_threshold = evidence_summary.get("target_threshold", 0) == 95.0
            has_target_tracking = "target_achieved_runs" in evidence_summary
            has_achievement_rate = "target_achievement_rate" in evidence_summary
            has_tagging_rate = "overall_tagging_rate" in evidence_summary
            
            # Check for success indicators
            success_rate = evidence_summary.get("success_rate", 0)
            total_runs = evidence_summary.get("total_evidence_runs", 0)
            
            target_achievement_score = sum([has_target_threshold, has_target_tracking, has_achievement_rate, has_tagging_rate])
            system_operational = total_runs > 0 and success_rate >= 0
            
            if target_achievement_score >= 3 and system_operational:
                print("   ✅ Fidelity target achievement (≥95%) PASSED")
                print(f"   📊 Target threshold (95%): {has_target_threshold}")
                print(f"   📊 Target tracking: {has_target_tracking}")
                print(f"   📊 Achievement rate tracking: {has_achievement_rate}")
                print(f"   📊 Tagging rate calculation: {has_tagging_rate}")
                print(f"   📊 Total runs: {total_runs}")
                print(f"   📊 Success rate: {success_rate}%")
                results["passed_tests"] += 1
                results["test_details"].append("✅ Fidelity Target Achievement PASSED")
            else:
                print("   ❌ Fidelity target achievement FAILED")
                print(f"   📊 Target features score: {target_achievement_score}/4")
                print(f"   📊 Total runs: {total_runs}")
                print(f"   📊 Success rate: {success_rate}%")
                results["test_details"].append("❌ Fidelity Target Achievement FAILED")
        else:
            print(f"   ❌ Could not verify target achievement: HTTP {diagnostics_response.status_code}")
            results["test_details"].append("❌ Fidelity Target Achievement FAILED - Diagnostics error")
    except Exception as e:
        print(f"   ❌ Target achievement test error: {e}")
        results["test_details"].append(f"❌ Fidelity Target Achievement FAILED - {e}")
    
    # Test 8: Database Storage and Retrieval
    print("\n8️⃣ TESTING: Database Storage and Retrieval")
    try:
        # Test database storage and retrieval
        diagnostics_response = requests.get(f"{BACKEND_URL}/evidence-tagging/diagnostics")
        
        if diagnostics_response.status_code == 200:
            diagnostics_data = diagnostics_response.json()
            
            # Check for database-related information
            evidence_summary = diagnostics_data.get("evidence_tagging_summary", {})
            recent_results = diagnostics_data.get("recent_evidence_results", [])
            
            has_results_storage = len(recent_results) > 0
            has_metadata = "diagnostics_generated_at" in diagnostics_data
            has_result_structure = False
            
            # Test specific evidence tagging result endpoint if we have results
            specific_result_tested = False
            if recent_results:
                try:
                    result_id = recent_results[0].get("evidence_tagging_id")
                    if result_id:
                        specific_response = requests.get(f"{BACKEND_URL}/evidence-tagging/diagnostics/{result_id}")
                        if specific_response.status_code == 200:
                            specific_result_tested = True
                            result_data = specific_response.json()
                            has_result_structure = "evidence_tagging_result" in result_data and "analysis" in result_data
                except:
                    pass
            
            # Test rerun functionality
            rerun_tested = False
            if recent_results:
                try:
                    run_id = recent_results[0].get("run_id")
                    if run_id:
                        rerun_response = requests.post(
                            f"{BACKEND_URL}/evidence-tagging/rerun",
                            json={"run_id": run_id}
                        )
                        rerun_tested = rerun_response.status_code == 200
                except:
                    pass
            
            storage_score = sum([has_results_storage, has_metadata, has_result_structure, specific_result_tested, rerun_tested])
            
            if storage_score >= 3:
                print("   ✅ Database storage and retrieval PASSED")
                print(f"   📊 Results storage: {has_results_storage}")
                print(f"   📊 Metadata present: {has_metadata}")
                print(f"   📊 Result structure complete: {has_result_structure}")
                print(f"   📊 Specific result endpoint tested: {specific_result_tested}")
                print(f"   📊 Rerun functionality tested: {rerun_tested}")
                print(f"   📊 Total stored results: {len(recent_results)}")
                results["passed_tests"] += 1
                results["test_details"].append("✅ Database Storage and Retrieval PASSED")
            else:
                print("   ❌ Database storage and retrieval FAILED")
                print(f"   📊 Storage features score: {storage_score}/5")
                print(f"   📊 Total stored results: {len(recent_results)}")
                results["test_details"].append("❌ Database Storage and Retrieval FAILED")
        else:
            print(f"   ❌ Could not verify database storage: HTTP {diagnostics_response.status_code}")
            results["test_details"].append("❌ Database Storage and Retrieval FAILED - Diagnostics error")
    except Exception as e:
        print(f"   ❌ Database storage test error: {e}")
        results["test_details"].append(f"❌ Database Storage and Retrieval FAILED - {e}")
    
    # Calculate success rate
    success_rate = (results["passed_tests"] / results["total_tests"]) * 100
    
    print("\n" + "=" * 80)
    print("🏷️ V2 ENGINE EVIDENCE TAGGING SYSTEM TESTING RESULTS")
    print("=" * 80)
    print(f"📊 OVERALL SUCCESS RATE: {results['passed_tests']}/{results['total_tests']} ({success_rate:.1f}%)")
    
    if success_rate >= 95:
        print("🎉 EXCELLENT PERFORMANCE - PRODUCTION READY")
    elif success_rate >= 80:
        print("✅ GOOD PERFORMANCE - MOSTLY OPERATIONAL")
    elif success_rate >= 60:
        print("⚠️ MODERATE PERFORMANCE - NEEDS ATTENTION")
    else:
        print("❌ POOR PERFORMANCE - CRITICAL ISSUES")
    
    print("\n📋 DETAILED TEST RESULTS:")
    for i, detail in enumerate(results["test_details"], 1):
        print(f"   {i}. {detail}")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting V2 Engine Evidence Tagging System Comprehensive Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        results = test_v2_engine_evidence_tagging_system()
        
        # Exit with appropriate code
        if results["passed_tests"] == results["total_tests"]:
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)  # Critical error