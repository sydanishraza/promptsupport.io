#!/usr/bin/env python3
"""
KE-PR5 Pipeline Orchestrator Diagnostic Test
Comprehensive diagnosis to identify which V2 stage classes have missing method implementations
preventing 100% success rate.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://promptsupport-3.preview.emergentagent.com/api"

class KE_PR5_DiagnosticTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.v2_stage_status = {}
        self.missing_methods = []
        self.pipeline_failures = []
        
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
        
    def test_pipeline_orchestrator_availability(self):
        """Test 1: Verify Pipeline Orchestrator is available and operational"""
        try:
            response = requests.get(f"{self.backend_url}/engine", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Pipeline Orchestrator Availability", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Check if pipeline orchestrator is mentioned
            engine_message = data.get("message", "").lower()
            has_pipeline = "pipeline" in engine_message or "orchestrator" in engine_message
            
            # Check for V2 pipeline features
            features = data.get("features", [])
            pipeline_features = [f for f in features if "pipeline" in f.lower() or "orchestrat" in f.lower()]
            
            if not has_pipeline and not pipeline_features:
                self.log_test("Pipeline Orchestrator Availability", False, "No pipeline orchestrator detected")
                return False
                
            self.log_test("Pipeline Orchestrator Availability", True, 
                         f"Pipeline orchestrator available, features: {pipeline_features}")
            return True
            
        except Exception as e:
            self.log_test("Pipeline Orchestrator Availability", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_stage_class_availability(self):
        """Test 2: Check which V2 stage classes are available vs missing"""
        try:
            # Test with minimal content to trigger stage loading
            test_content = "# Test Content\nThis is a test to check V2 stage class availability."
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=60)
            
            if response.status_code != 200:
                self.log_test("V2 Stage Class Availability", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            
            # Analyze the response for stage information
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            stage_errors = processing_info.get("stage_errors", [])
            
            # Expected V2 stages (17 total)
            expected_stages = [
                "V2MultiDimensionalAnalyzer", "V2GlobalOutlinePlanner", "V2PerArticleOutlinePlanner",
                "V2PrewriteSystem", "V2GapFillingSystem", "V2EvidenceTaggingSystem", 
                "V2CodeNormalizationSystem", "V2ArticleGenerator", "V2StyleProcessor",
                "V2RelatedLinksSystem", "V2ValidationSystem", "V2PublishingSystem",
                "V2CrossArticleQASystem", "V2AdaptiveAdjustmentSystem", "V2MediaManager",
                "V2VersioningSystem", "V2ReviewSystem"
            ]
            
            # Analyze stage errors for missing methods
            missing_method_errors = []
            attribute_errors = []
            
            for error in stage_errors:
                error_msg = error.get("message", "")
                stage_name = error.get("stage", "unknown")
                
                if "AttributeError" in error_msg or "has no attribute" in error_msg:
                    attribute_errors.append({
                        "stage": stage_name,
                        "error": error_msg,
                        "severity": error.get("severity", "unknown")
                    })
                    
                if "method not found" in error_msg or "missing method" in error_msg:
                    missing_method_errors.append({
                        "stage": stage_name,
                        "error": error_msg,
                        "severity": error.get("severity", "unknown")
                    })
            
            # Store results for analysis
            self.v2_stage_status = {
                "stages_completed": stages_completed,
                "total_expected": 17,
                "completion_rate": (stages_completed / 17) * 100,
                "attribute_errors": attribute_errors,
                "missing_method_errors": missing_method_errors,
                "stage_errors": stage_errors
            }
            
            success_rate = (stages_completed / 17) * 100
            
            if success_rate < 100:
                self.log_test("V2 Stage Class Availability", False, 
                             f"Incomplete pipeline: {stages_completed}/17 stages ({success_rate:.1f}%)")
                return False
            else:
                self.log_test("V2 Stage Class Availability", True, 
                             f"All 17 V2 stages available ({success_rate:.1f}%)")
                return True
                
        except Exception as e:
            self.log_test("V2 Stage Class Availability", False, f"Exception: {str(e)}")
            return False
    
    def test_v2_class_method_availability(self):
        """Test 3: Check which V2 class methods are missing vs implemented"""
        try:
            # Expected methods for each V2 class based on pipeline usage
            expected_methods = {
                'V2ContentExtractor': ['extract_raw_text'],
                'V2MultiDimensionalAnalyzer': ['analyze_normalized_document'],
                'V2GlobalOutlinePlanner': ['create_global_outline'],
                'V2PerArticleOutlinePlanner': ['create_per_article_outlines'],
                'V2PrewriteSystem': ['extract_prewrite_data'],
                'V2ArticleGenerator': ['generate_article'],
                'V2StyleProcessor': ['process_style'],
                'V2RelatedLinksSystem': ['generate_related_links'],
                'V2GapFillingSystem': ['fill_gaps'],
                'V2EvidenceTaggingSystem': ['tag_evidence'],
                'V2CodeNormalizationSystem': ['normalize_code_blocks'],
                'V2ValidationSystem': ['validate_content'],
                'V2CrossArticleQASystem': ['perform_cross_article_qa'],
                'V2AdaptiveAdjustmentSystem': ['adjust_article_balance'],
                'V2PublishingSystem': ['publish_v2_content'],
                'V2VersioningSystem': ['create_version'],
                'V2ReviewSystem': ['enqueue_for_review']
            }
            
            # Check method availability by importing and inspecting classes
            missing_methods = {}
            placeholder_classes = []
            
            try:
                # Import V2 classes to check their methods
                import sys
                import os
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)
                
                from engine.v2.analyzer import V2MultiDimensionalAnalyzer
                from engine.v2.outline import V2GlobalOutlinePlanner, V2PerArticleOutlinePlanner
                from engine.v2.prewrite import V2PrewriteSystem
                from engine.v2.generator import V2ArticleGenerator
                from engine.v2.style import V2StyleProcessor
                from engine.v2.related import V2RelatedLinksSystem
                from engine.v2.gaps import V2GapFillingSystem
                from engine.v2.evidence import V2EvidenceTaggingSystem
                from engine.v2.code_norm import V2CodeNormalizationSystem
                from engine.v2.validate import V2ValidationSystem
                from engine.v2.crossqa import V2CrossArticleQASystem
                from engine.v2.adapt import V2AdaptiveAdjustmentSystem
                from engine.v2.publish import V2PublishingSystem
                from engine.v2.versioning import V2VersioningSystem
                from engine.v2.review import V2ReviewSystem
                from engine.v2.extractor import V2ContentExtractor
                
                # Check each class for expected methods
                v2_classes = {
                    'V2ContentExtractor': V2ContentExtractor,
                    'V2MultiDimensionalAnalyzer': V2MultiDimensionalAnalyzer,
                    'V2GlobalOutlinePlanner': V2GlobalOutlinePlanner,
                    'V2PerArticleOutlinePlanner': V2PerArticleOutlinePlanner,
                    'V2PrewriteSystem': V2PrewriteSystem,
                    'V2ArticleGenerator': V2ArticleGenerator,
                    'V2StyleProcessor': V2StyleProcessor,
                    'V2RelatedLinksSystem': V2RelatedLinksSystem,
                    'V2GapFillingSystem': V2GapFillingSystem,
                    'V2EvidenceTaggingSystem': V2EvidenceTaggingSystem,
                    'V2CodeNormalizationSystem': V2CodeNormalizationSystem,
                    'V2ValidationSystem': V2ValidationSystem,
                    'V2CrossArticleQASystem': V2CrossArticleQASystem,
                    'V2AdaptiveAdjustmentSystem': V2AdaptiveAdjustmentSystem,
                    'V2PublishingSystem': V2PublishingSystem,
                    'V2VersioningSystem': V2VersioningSystem,
                    'V2ReviewSystem': V2ReviewSystem
                }
                
                for class_name, class_obj in v2_classes.items():
                    expected_methods_for_class = expected_methods.get(class_name, [])
                    class_missing_methods = []
                    
                    # Check if class is just a placeholder
                    instance = class_obj()
                    class_methods = [method for method in dir(instance) if not method.startswith('_')]
                    
                    # Check for expected methods
                    for method_name in expected_methods_for_class:
                        if not hasattr(instance, method_name):
                            class_missing_methods.append(method_name)
                        else:
                            # Check if method is just a placeholder (returns None or raises NotImplementedError)
                            method = getattr(instance, method_name)
                            if callable(method):
                                try:
                                    # Try to inspect the method source to see if it's a placeholder
                                    import inspect
                                    source = inspect.getsource(method)
                                    if 'pass' in source or 'NotImplementedError' in source or 'TODO' in source:
                                        class_missing_methods.append(f"{method_name} (placeholder)")
                                except:
                                    # If we can't inspect, assume it's implemented
                                    pass
                    
                    if class_missing_methods:
                        missing_methods[class_name] = class_missing_methods
                    
                    # Check if entire class is placeholder
                    if len(class_methods) <= 2:  # Only __init__ and maybe one other method
                        placeholder_classes.append(class_name)
                
                # Store results for analysis
                self.missing_methods = missing_methods
                self.placeholder_classes = placeholder_classes
                
                total_expected_methods = sum(len(methods) for methods in expected_methods.values())
                total_missing_methods = sum(len(methods) for methods in missing_methods.values())
                implementation_rate = ((total_expected_methods - total_missing_methods) / total_expected_methods) * 100
                
                if total_missing_methods == 0:
                    self.log_test("V2 Class Method Availability", True, 
                                 f"All methods implemented ({implementation_rate:.1f}%)")
                    return True
                else:
                    self.log_test("V2 Class Method Availability", False, 
                                 f"Missing {total_missing_methods}/{total_expected_methods} methods ({implementation_rate:.1f}% implemented)")
                    return False
                    
            except ImportError as import_error:
                self.log_test("V2 Class Method Availability", False, f"Import error: {import_error}")
                return False
                
        except Exception as e:
            self.log_test("V2 Class Method Availability", False, f"Exception: {str(e)}")
            return False
    
    def test_specific_v2_stage_methods(self):
        """Test 4: Test specific V2 stage methods to identify missing implementations"""
        try:
            # Test with content designed to trigger specific stage methods
            comprehensive_content = """
            # Comprehensive V2 Stage Method Testing
            
            ## Multi-Dimensional Analysis Test
            This section tests the V2MultiDimensionalAnalyzer with complex content analysis requirements.
            
            ## Outline Planning Test
            This tests both global and per-article outline planning with hierarchical content structure.
            
            ### Prewrite System Test
            Testing prewrite data extraction with various content types and formats.
            
            ## Gap Filling System Test
            Content with intentional gaps to test the V2GapFillingSystem functionality.
            
            ## Evidence Tagging Test
            Claims and statements that require evidence tagging and validation.
            
            ## Code Normalization Test
            ```javascript
            function testCode() {
                console.log("Testing code normalization");
                return true;
            }
            ```
            
            ```python
            def another_test():
                print("Multiple code blocks for normalization")
                return "success"
            ```
            
            ## Article Generation Test
            Complex content structure for comprehensive article generation testing.
            
            ## Style Processing Test
            Content requiring Woolf-aligned technical writing style processing and structural linting.
            
            ## Related Links Test
            Content with multiple topics for related links generation testing.
            
            ## Validation Test
            Content requiring comprehensive validation including technical accuracy and completeness.
            
            ## Publishing Test
            Content ready for V2 publishing system with complete metadata and structure.
            
            ## Cross-Article QA Test
            Content for cross-article quality assurance and consistency checking.
            
            ## Adaptive Adjustment Test
            Content requiring balance adjustments and optimization.
            
            ## Media Processing Test
            Content with media references for V2MediaManager testing.
            
            ## Versioning Test
            Content for version management and tracking system testing.
            
            ## Review System Test
            Content for human-in-the-loop review system testing and queue management.
            """
            
            payload = {
                "content": comprehensive_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=180)
            
            if response.status_code != 200:
                self.log_test("Specific V2 Stage Methods", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            stage_errors = processing_info.get("stage_errors", [])
            
            # Analyze specific method failures
            method_failures = {}
            critical_failures = []
            
            for error in stage_errors:
                stage_name = error.get("stage", "unknown")
                error_msg = error.get("message", "")
                severity = error.get("severity", "unknown")
                
                if stage_name not in method_failures:
                    method_failures[stage_name] = []
                    
                method_failures[stage_name].append({
                    "message": error_msg,
                    "severity": severity
                })
                
                if severity == "critical":
                    critical_failures.append({
                        "stage": stage_name,
                        "error": error_msg
                    })
            
            # Store detailed analysis
            self.missing_methods = method_failures
            self.pipeline_failures = critical_failures
            
            success_rate = (stages_completed / 17) * 100
            
            if critical_failures:
                self.log_test("Specific V2 Stage Methods", False, 
                             f"Critical method failures in {len(critical_failures)} stages")
                return False
            elif success_rate < 100:
                self.log_test("Specific V2 Stage Methods", False, 
                             f"Method issues: {stages_completed}/17 stages completed ({success_rate:.1f}%)")
                return False
            else:
                self.log_test("Specific V2 Stage Methods", True, 
                             f"All stage methods working ({success_rate:.1f}%)")
                return True
                
        except Exception as e:
            self.log_test("Specific V2 Stage Methods", False, f"Exception: {str(e)}")
            return False
    
    def test_pipeline_execution_flow(self):
        """Test 5: Test complete pipeline execution flow to identify bottlenecks"""
        try:
            # Test pipeline flow with different content types
            test_cases = [
                {
                    "name": "Simple Content",
                    "content": "# Simple Test\nBasic content for pipeline flow testing.",
                    "expected_stages": 17
                },
                {
                    "name": "Complex Content", 
                    "content": """
                    # Complex Pipeline Flow Test
                    
                    ## Introduction
                    This is a comprehensive test of the pipeline execution flow.
                    
                    ### Code Example
                    ```python
                    def pipeline_test():
                        return "testing"
                    ```
                    
                    ## Multiple Sections
                    Testing various content types and structures.
                    """,
                    "expected_stages": 17
                },
                {
                    "name": "Minimal Content",
                    "content": "Test",
                    "expected_stages": 17
                }
            ]
            
            flow_results = []
            
            for test_case in test_cases:
                payload = {
                    "content": test_case["content"],
                    "content_type": "markdown", 
                    "processing_mode": "v2_only"
                }
                
                start_time = time.time()
                response = requests.post(f"{self.backend_url}/content/process", 
                                       json=payload, timeout=120)
                processing_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    processing_info = data.get("processing_info", {})
                    stages_completed = processing_info.get("stages_completed", 0)
                    stage_errors = processing_info.get("stage_errors", [])
                    
                    flow_results.append({
                        "name": test_case["name"],
                        "stages_completed": stages_completed,
                        "expected_stages": test_case["expected_stages"],
                        "processing_time": processing_time,
                        "error_count": len(stage_errors),
                        "success": stages_completed == test_case["expected_stages"]
                    })
                else:
                    flow_results.append({
                        "name": test_case["name"],
                        "stages_completed": 0,
                        "expected_stages": test_case["expected_stages"],
                        "processing_time": processing_time,
                        "error_count": 1,
                        "success": False
                    })
            
            # Analyze flow results
            successful_flows = [r for r in flow_results if r["success"]]
            success_rate = len(successful_flows) / len(flow_results) * 100
            
            if success_rate < 100:
                failed_cases = [r["name"] for r in flow_results if not r["success"]]
                self.log_test("Pipeline Execution Flow", False, 
                             f"Flow issues in: {failed_cases} ({success_rate:.1f}% success)")
                return False
            else:
                avg_time = sum(r["processing_time"] for r in flow_results) / len(flow_results)
                self.log_test("Pipeline Execution Flow", True, 
                             f"All flows successful, avg time: {avg_time:.1f}s")
                return True
                
        except Exception as e:
            self.log_test("Pipeline Execution Flow", False, f"Exception: {str(e)}")
            return False
    
    def test_stage_by_stage_execution(self):
        """Test 6: Analyze stage-by-stage execution to pinpoint failure points"""
        try:
            # Test content designed to progress through all stages
            test_content = """
            # Stage-by-Stage Execution Analysis
            
            ## Comprehensive Content for All Stages
            This content is designed to trigger every stage of the V2 pipeline for detailed analysis.
            
            ### Analysis Requirements (Stage 1)
            Multi-dimensional content analysis with various content types and complexity levels.
            
            ### Outline Planning (Stages 2-3)
            Global and per-article outline planning with hierarchical structure and dependencies.
            
            ### Prewrite Processing (Stage 4)
            Prewrite data extraction with metadata, context, and structural information.
            
            ### Gap Identification (Stage 5)
            Content gaps that need to be filled for completeness and accuracy.
            
            ### Evidence Requirements (Stage 6)
            Claims and statements requiring evidence tagging and validation.
            
            ### Code Processing (Stage 7)
            ```javascript
            // Code normalization testing
            function stageTest() {
                console.log("Stage 7: Code Normalization");
                return {
                    stage: 7,
                    status: "processing",
                    normalized: true
                };
            }
            ```
            
            ### Article Generation (Stage 8)
            Comprehensive article generation with proper structure and formatting.
            
            ### Style Processing (Stage 9)
            Woolf-aligned technical writing style and structural linting requirements.
            
            ### Related Content (Stage 10)
            Related links generation and cross-referencing system testing.
            
            ### Validation (Stage 11)
            Content validation including technical accuracy and completeness checks.
            
            ### Publishing (Stage 12)
            V2 publishing system with metadata and content library integration.
            
            ### Quality Assurance (Stage 13)
            Cross-article QA and consistency checking across content.
            
            ### Optimization (Stage 14)
            Adaptive adjustment and balance optimization for content quality.
            
            ### Media Processing (Stage 15)
            Media management and processing for enhanced content delivery.
            
            ### Version Management (Stage 16)
            Version tracking and management system for content lifecycle.
            
            ### Review System (Stage 17)
            Human-in-the-loop review system and quality control processes.
            """
            
            payload = {
                "content": test_content,
                "content_type": "markdown",
                "processing_mode": "v2_only"
            }
            
            response = requests.post(f"{self.backend_url}/content/process", 
                                   json=payload, timeout=180)
            
            if response.status_code != 200:
                self.log_test("Stage-by-Stage Execution", False, f"HTTP {response.status_code}")
                return False
                
            data = response.json()
            processing_info = data.get("processing_info", {})
            stages_completed = processing_info.get("stages_completed", 0)
            stage_errors = processing_info.get("stage_errors", [])
            
            # Analyze where pipeline stops/fails
            stage_analysis = {
                "completed_stages": stages_completed,
                "total_stages": 17,
                "completion_percentage": (stages_completed / 17) * 100,
                "failed_at_stage": 17 - stages_completed + 1 if stages_completed < 17 else None,
                "error_stages": []
            }
            
            # Identify which stages have errors
            for error in stage_errors:
                stage_info = {
                    "stage": error.get("stage", "unknown"),
                    "message": error.get("message", ""),
                    "severity": error.get("severity", "unknown")
                }
                stage_analysis["error_stages"].append(stage_info)
            
            # Store detailed stage analysis
            self.stage_analysis = stage_analysis
            
            if stages_completed == 17:
                self.log_test("Stage-by-Stage Execution", True, 
                             f"All 17 stages completed successfully")
                return True
            else:
                failed_stage = stage_analysis["failed_at_stage"]
                self.log_test("Stage-by-Stage Execution", False, 
                             f"Pipeline stopped at stage {failed_stage} ({stages_completed}/17 completed)")
                return False
                
        except Exception as e:
            self.log_test("Stage-by-Stage Execution", False, f"Exception: {str(e)}")
            return False
    
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        print("\n" + "=" * 80)
        print("🔍 KE-PR5 PIPELINE ORCHESTRATOR DIAGNOSTIC REPORT")
        print("=" * 80)
        
        # Overall status
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"\n📊 OVERALL PIPELINE STATUS: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests} tests passed)")
        
        # V2 Stage Status Analysis
        if hasattr(self, 'v2_stage_status') and self.v2_stage_status:
            stage_status = self.v2_stage_status
            print(f"\n🔧 V2 STAGE COMPLETION ANALYSIS:")
            stages_completed = stage_status.get('stages_completed', 0)
            completion_rate = stage_status.get('completion_rate', 0)
            print(f"   Stages Completed: {stages_completed}/17 ({completion_rate:.1f}%)")
            
            attribute_errors = stage_status.get('attribute_errors', [])
            missing_method_errors = stage_status.get('missing_method_errors', [])
            
            if attribute_errors:
                print(f"\n❌ ATTRIBUTE ERRORS DETECTED ({len(attribute_errors)}):")
                for error in attribute_errors:
                    print(f"   • Stage: {error['stage']}")
                    print(f"     Error: {error['error']}")
                    print(f"     Severity: {error['severity']}")
            
            if missing_method_errors:
                print(f"\n❌ MISSING METHOD ERRORS ({len(missing_method_errors)}):")
                for error in missing_method_errors:
                    print(f"   • Stage: {error['stage']}")
                    print(f"     Error: {error['error']}")
                    print(f"     Severity: {error['severity']}")
        
        # Missing Methods Analysis
        if self.missing_methods:
            print(f"\n🚫 MISSING METHOD IMPLEMENTATIONS:")
            for stage, methods in self.missing_methods.items():
                print(f"   • {stage}:")
                for method in methods:
                    print(f"     - {method}")
        
        # Placeholder Classes
        if hasattr(self, 'placeholder_classes') and self.placeholder_classes:
            print(f"\n⚠️ PLACEHOLDER CLASSES DETECTED ({len(self.placeholder_classes)}):")
            for class_name in self.placeholder_classes:
                print(f"   • {class_name}: Needs full implementation")
        
        # Pipeline Failures
        if self.pipeline_failures:
            print(f"\n💥 CRITICAL PIPELINE FAILURES ({len(self.pipeline_failures)}):")
            for failure in self.pipeline_failures:
                print(f"   • Stage: {failure['stage']}")
                print(f"     Error: {failure['error']}")
        
        # Stage-by-Stage Analysis
        if hasattr(self, 'stage_analysis'):
            analysis = self.stage_analysis
            print(f"\n📈 STAGE-BY-STAGE EXECUTION ANALYSIS:")
            print(f"   Completion: {analysis['completed_stages']}/17 stages ({analysis['completion_percentage']:.1f}%)")
            
            if analysis['failed_at_stage']:
                print(f"   ⚠️ Pipeline stopped at Stage {analysis['failed_at_stage']}")
            
            if analysis['error_stages']:
                print(f"   🔍 Stages with errors:")
                for stage_error in analysis['error_stages']:
                    print(f"     • {stage_error['stage']}: {stage_error['message']} ({stage_error['severity']})")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS FOR 100% SUCCESS RATE:")
        
        if success_rate == 100:
            print("   ✅ Pipeline is already achieving 100% success rate!")
            print("   ✅ All V2 stage classes have complete method implementations")
            print("   ✅ No missing methods or critical failures detected")
        else:
            print("   🔧 REQUIRED FIXES:")
            
            if hasattr(self, 'v2_stage_status') and self.v2_stage_status.get('attribute_errors'):
                print("   1. Fix AttributeError issues in V2 stage classes:")
                for error in self.v2_stage_status['attribute_errors']:
                    print(f"      - {error['stage']}: {error['error']}")
            
            if self.missing_methods:
                print("   2. Implement missing methods in V2 stage classes:")
                for stage, errors in self.missing_methods.items():
                    print(f"      - {stage}: {len(errors)} method issues")
            
            if self.pipeline_failures:
                print("   3. Resolve critical pipeline failures:")
                for failure in self.pipeline_failures:
                    print(f"      - {failure['stage']}: {failure['error']}")
            
            if hasattr(self, 'stage_analysis') and self.stage_analysis['failed_at_stage']:
                failed_stage = self.stage_analysis['failed_at_stage']
                print(f"   4. Fix Stage {failed_stage} implementation to allow pipeline continuation")
        
        print(f"\n🎯 PATH TO 100% SUCCESS:")
        print("   1. Review and fix all identified AttributeError issues")
        print("   2. Implement missing methods in V2 stage classes")
        print("   3. Resolve critical failures preventing stage completion")
        print("   4. Test pipeline execution with comprehensive content")
        print("   5. Verify all 17 stages complete successfully")
        
        return success_rate
    
    def run_all_tests(self):
        """Run all diagnostic tests"""
        print("🔍 KE-PR5 PIPELINE ORCHESTRATOR DIAGNOSTIC TESTING")
        print("=" * 80)
        print("Comprehensive diagnosis to identify V2 stage classes with missing method implementations")
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print()
        
        # Run all diagnostic tests
        tests = [
            self.test_pipeline_orchestrator_availability,
            self.test_v2_stage_class_availability,
            self.test_v2_class_method_availability,
            self.test_specific_v2_stage_methods,
            self.test_pipeline_execution_flow,
            self.test_stage_by_stage_execution
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace("test_", "").replace("_", " ").title()
                self.log_test(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(2)
        
        # Generate comprehensive diagnostic report
        success_rate = self.generate_diagnostic_report()
        
        return success_rate

if __name__ == "__main__":
    tester = KE_PR5_DiagnosticTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 85 else 1)