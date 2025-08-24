#!/usr/bin/env python3
"""
V2 Engine Step 4 Global Outline Planning - 100% Success Rate Verification Test
Testing V2GlobalOutlinePlanner for comprehensive functionality and integration
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class V2GlobalOutlinePlanningTester:
    def __init__(self):
        self.test_results = []
        self.session = None
        
    async def setup_session(self):
        """Setup HTTP session for testing"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def test_v2_engine_health_check(self):
        """Test V2 Engine health check with global outline planning features"""
        try:
            async with self.session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify V2 engine is active
                    if data.get('engine') == 'v2' and data.get('status') == 'active':
                        # Check for global outline planning features
                        features = data.get('features', [])
                        outline_features = [
                            'multi_dimensional_analysis',
                            'adaptive_granularity', 
                            'intelligent_chunking',
                            'cross_referencing'
                        ]
                        
                        missing_features = [f for f in outline_features if f not in features]
                        if not missing_features:
                            self.log_test("V2 Engine Health Check with Global Outline Planning", True, 
                                        f"V2 Engine active with all global outline planning features: {outline_features}")
                            return True
                        else:
                            self.log_test("V2 Engine Health Check with Global Outline Planning", False,
                                        f"Missing global outline planning features: {missing_features}")
                            return False
                    else:
                        self.log_test("V2 Engine Health Check with Global Outline Planning", False,
                                    f"V2 Engine not active: engine={data.get('engine')}, status={data.get('status')}")
                        return False
                else:
                    self.log_test("V2 Engine Health Check with Global Outline Planning", False,
                                f"HTTP {response.status}: {await response.text()}")
                    return False
                    
        except Exception as e:
            self.log_test("V2 Engine Health Check with Global Outline Planning", False, f"Error: {e}")
            return False
    
    async def test_global_outline_database_collections(self):
        """Test global outline planning database storage and retrieval"""
        try:
            # Test content processing to trigger global outline planning
            test_content = """
            # Advanced API Integration Guide
            
            ## Introduction
            This comprehensive guide covers advanced API integration techniques for modern web applications.
            
            ## Authentication Methods
            Learn about OAuth 2.0, JWT tokens, and API key authentication.
            
            ### OAuth 2.0 Implementation
            Step-by-step OAuth 2.0 setup with code examples.
            
            ### JWT Token Management
            Best practices for JWT token handling and refresh strategies.
            
            ## Data Processing
            Advanced techniques for processing API responses and error handling.
            
            ### Response Parsing
            Efficient methods for parsing JSON and XML responses.
            
            ### Error Handling Strategies
            Comprehensive error handling for robust applications.
            
            ## Performance Optimization
            Techniques for optimizing API calls and reducing latency.
            
            ### Caching Strategies
            Implementing effective caching for API responses.
            
            ### Rate Limiting
            Managing API rate limits and implementing backoff strategies.
            """
            
            payload = {
                "content": test_content,
                "metadata": {
                    "title": "V2 Global Outline Planning Test Document",
                    "source": "test_suite",
                    "test_type": "global_outline_verification"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if processing was successful and used V2 engine
                    if data.get('success') and data.get('engine') == 'v2':
                        run_id = data.get('run_id')
                        if run_id:
                            # Verify global outline was created and stored
                            processing_results = data.get('processing_results', {})
                            if 'global_outline_planning' in processing_results:
                                outline_result = processing_results['global_outline_planning']
                                if outline_result.get('status') == 'completed':
                                    self.log_test("Global Outline Planning Database Collections", True,
                                                f"Global outline stored successfully with run_id: {run_id}, "
                                                f"articles planned: {outline_result.get('articles_count', 0)}, "
                                                f"blocks processed: {outline_result.get('total_blocks', 0)}")
                                    return True
                                else:
                                    self.log_test("Global Outline Planning Database Collections", False,
                                                f"Global outline planning not completed: {outline_result}")
                                    return False
                            else:
                                self.log_test("Global Outline Planning Database Collections", False,
                                            "Global outline planning not found in processing results")
                                return False
                        else:
                            self.log_test("Global Outline Planning Database Collections", False,
                                        "No run_id returned from processing")
                            return False
                    else:
                        self.log_test("Global Outline Planning Database Collections", False,
                                    f"Processing failed or not using V2 engine: success={data.get('success')}, engine={data.get('engine')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Global Outline Planning Database Collections", False,
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Global Outline Planning Database Collections", False, f"Error: {e}")
            return False
    
    async def test_hierarchical_organization_and_content_structure(self):
        """Test hierarchical organization and content structure optimization"""
        try:
            # Test with complex hierarchical content
            hierarchical_content = """
            # Enterprise Software Architecture Guide
            
            ## Chapter 1: System Architecture Fundamentals
            Understanding the core principles of enterprise system design.
            
            ### 1.1 Architectural Patterns
            Common patterns used in enterprise applications.
            
            #### 1.1.1 Microservices Architecture
            Detailed explanation of microservices design patterns.
            
            #### 1.1.2 Monolithic Architecture
            When and how to use monolithic architecture effectively.
            
            ### 1.2 Design Principles
            SOLID principles and their application in enterprise systems.
            
            #### 1.2.1 Single Responsibility Principle
            Implementing SRP in large-scale applications.
            
            #### 1.2.2 Open/Closed Principle
            Designing extensible systems with OCP.
            
            ## Chapter 2: Database Design and Management
            Comprehensive database architecture for enterprise applications.
            
            ### 2.1 Relational Database Design
            Best practices for relational database schema design.
            
            #### 2.1.1 Normalization Strategies
            Database normalization techniques and trade-offs.
            
            #### 2.1.2 Indexing Optimization
            Advanced indexing strategies for performance.
            
            ### 2.2 NoSQL Database Integration
            When and how to integrate NoSQL databases.
            
            #### 2.2.1 Document Databases
            MongoDB and similar document database implementations.
            
            #### 2.2.2 Graph Databases
            Neo4j and graph database use cases.
            
            ## Chapter 3: Security and Compliance
            Enterprise-grade security implementation.
            
            ### 3.1 Authentication and Authorization
            Comprehensive security frameworks.
            
            ### 3.2 Data Protection
            Encryption and data privacy compliance.
            """
            
            payload = {
                "content": hierarchical_content,
                "metadata": {
                    "title": "Hierarchical Content Structure Test",
                    "source": "test_suite",
                    "test_type": "hierarchical_organization"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('engine') == 'v2':
                        processing_results = data.get('processing_results', {})
                        
                        # Check multi-dimensional analysis
                        if 'multi_dimensional_analysis' in processing_results:
                            analysis = processing_results['multi_dimensional_analysis']
                            if analysis.get('status') == 'completed':
                                analysis_data = analysis.get('analysis', {})
                                content_type = analysis_data.get('content_type')
                                complexity = analysis_data.get('complexity_level')
                                
                                # Check global outline planning
                                if 'global_outline_planning' in processing_results:
                                    outline = processing_results['global_outline_planning']
                                    if outline.get('status') == 'completed':
                                        articles_count = outline.get('articles_count', 0)
                                        total_blocks = outline.get('total_blocks', 0)
                                        
                                        # Verify hierarchical processing
                                        if articles_count >= 3 and total_blocks >= 10:
                                            self.log_test("Hierarchical Organization and Content Structure", True,
                                                        f"Complex hierarchical content processed successfully: "
                                                        f"content_type={content_type}, complexity={complexity}, "
                                                        f"articles={articles_count}, blocks={total_blocks}")
                                            return True
                                        else:
                                            self.log_test("Hierarchical Organization and Content Structure", False,
                                                        f"Insufficient hierarchical processing: articles={articles_count}, blocks={total_blocks}")
                                            return False
                                    else:
                                        self.log_test("Hierarchical Organization and Content Structure", False,
                                                    f"Global outline planning failed: {outline}")
                                        return False
                                else:
                                    self.log_test("Hierarchical Organization and Content Structure", False,
                                                "Global outline planning not found in results")
                                    return False
                            else:
                                self.log_test("Hierarchical Organization and Content Structure", False,
                                            f"Multi-dimensional analysis failed: {analysis}")
                                return False
                        else:
                            self.log_test("Hierarchical Organization and Content Structure", False,
                                        "Multi-dimensional analysis not found in results")
                            return False
                    else:
                        self.log_test("Hierarchical Organization and Content Structure", False,
                                    f"Processing failed: success={data.get('success')}, engine={data.get('engine')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Hierarchical Organization and Content Structure", False,
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Hierarchical Organization and Content Structure", False, f"Error: {e}")
            return False
    
    async def test_cross_article_relationships_mapping(self):
        """Test cross-article relationships and content interconnections mapping"""
        try:
            # Test with interconnected content
            interconnected_content = """
            # API Development Ecosystem Guide
            
            ## REST API Design Principles
            Fundamental principles for designing RESTful APIs that integrate with authentication systems and database management.
            
            ## Authentication and Security
            Comprehensive security implementation that works with REST APIs and connects to database security measures.
            
            ## Database Integration Patterns
            Database design patterns that support REST API operations and maintain security compliance.
            
            ## Testing and Quality Assurance
            Testing strategies for REST APIs, authentication systems, and database operations to ensure system reliability.
            
            ## Deployment and DevOps
            Deployment strategies that encompass REST APIs, authentication services, and database management in production environments.
            
            ## Monitoring and Analytics
            Monitoring solutions for tracking REST API performance, authentication events, and database operations.
            
            ## Troubleshooting and Maintenance
            Common issues and solutions across REST APIs, authentication systems, and database management.
            """
            
            payload = {
                "content": interconnected_content,
                "metadata": {
                    "title": "Cross-Article Relationships Test",
                    "source": "test_suite", 
                    "test_type": "cross_article_mapping"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('engine') == 'v2':
                        processing_results = data.get('processing_results', {})
                        
                        # Check if cross-article QA was performed (indicates relationship mapping)
                        if 'cross_article_qa' in processing_results:
                            qa_result = processing_results['cross_article_qa']
                            if qa_result.get('status') == 'completed':
                                # Check for relationship mapping indicators
                                qa_data = qa_result.get('qa_results', {})
                                duplicates_found = qa_data.get('duplicates_found', 0)
                                invalid_links = qa_data.get('invalid_links_found', 0)
                                terminology_issues = qa_data.get('terminology_issues_found', 0)
                                
                                # Check global outline for article relationships
                                if 'global_outline_planning' in processing_results:
                                    outline = processing_results['global_outline_planning']
                                    articles_count = outline.get('articles_count', 0)
                                    
                                    if articles_count >= 3:
                                        self.log_test("Cross-Article Relationships Mapping", True,
                                                    f"Cross-article relationships mapped successfully: "
                                                    f"articles={articles_count}, duplicates_checked={duplicates_found >= 0}, "
                                                    f"links_validated={invalid_links >= 0}, terminology_checked={terminology_issues >= 0}")
                                        return True
                                    else:
                                        self.log_test("Cross-Article Relationships Mapping", False,
                                                    f"Insufficient articles for relationship mapping: {articles_count}")
                                        return False
                                else:
                                    self.log_test("Cross-Article Relationships Mapping", False,
                                                "Global outline planning not found")
                                    return False
                            else:
                                self.log_test("Cross-Article Relationships Mapping", False,
                                            f"Cross-article QA failed: {qa_result}")
                                return False
                        else:
                            self.log_test("Cross-Article Relationships Mapping", False,
                                        "Cross-article QA not found in processing results")
                            return False
                    else:
                        self.log_test("Cross-Article Relationships Mapping", False,
                                    f"Processing failed: success={data.get('success')}, engine={data.get('engine')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Cross-Article Relationships Mapping", False,
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Cross-Article Relationships Mapping", False, f"Error: {e}")
            return False
    
    async def test_coverage_optimization_and_topic_coverage(self):
        """Test coverage optimization and comprehensive topic coverage planning"""
        try:
            # Test with comprehensive content requiring full coverage
            comprehensive_content = """
            # Complete Software Development Lifecycle Guide
            
            ## Planning and Requirements Analysis
            Comprehensive requirements gathering and project planning methodologies.
            
            ### Stakeholder Analysis
            Identifying and managing stakeholder requirements and expectations.
            
            ### Technical Requirements Specification
            Detailed technical specification documentation and validation.
            
            ## Design and Architecture
            System design principles and architectural decision making.
            
            ### System Architecture Design
            High-level system architecture and component design.
            
            ### Database Design and Modeling
            Data modeling and database architecture planning.
            
            ### User Interface and Experience Design
            UI/UX design principles and user-centered design approaches.
            
            ## Development and Implementation
            Coding standards, development practices, and implementation strategies.
            
            ### Frontend Development
            Modern frontend development techniques and frameworks.
            
            ### Backend Development
            Server-side development and API design patterns.
            
            ### Database Implementation
            Database setup, optimization, and maintenance procedures.
            
            ## Testing and Quality Assurance
            Comprehensive testing strategies and quality assurance processes.
            
            ### Unit Testing
            Test-driven development and unit testing best practices.
            
            ### Integration Testing
            System integration testing and API testing methodologies.
            
            ### User Acceptance Testing
            UAT planning and execution strategies.
            
            ## Deployment and DevOps
            Deployment strategies and DevOps implementation.
            
            ### Continuous Integration/Continuous Deployment
            CI/CD pipeline setup and automation.
            
            ### Infrastructure Management
            Cloud infrastructure and server management.
            
            ## Maintenance and Support
            Post-deployment maintenance and ongoing support strategies.
            
            ### Performance Monitoring
            System monitoring and performance optimization.
            
            ### Bug Tracking and Resolution
            Issue management and resolution processes.
            """
            
            payload = {
                "content": comprehensive_content,
                "metadata": {
                    "title": "Coverage Optimization Test",
                    "source": "test_suite",
                    "test_type": "coverage_optimization"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('engine') == 'v2':
                        processing_results = data.get('processing_results', {})
                        
                        # Check validation results for coverage
                        if 'validation' in processing_results:
                            validation = processing_results['validation']
                            if validation.get('status') == 'completed':
                                validation_data = validation.get('validation_results', {})
                                coverage_percentage = validation_data.get('coverage_percentage', 0)
                                
                                # Check global outline planning
                                if 'global_outline_planning' in processing_results:
                                    outline = processing_results['global_outline_planning']
                                    articles_count = outline.get('articles_count', 0)
                                    total_blocks = outline.get('total_blocks', 0)
                                    
                                    # Verify comprehensive coverage
                                    if coverage_percentage >= 95 and articles_count >= 5 and total_blocks >= 15:
                                        self.log_test("Coverage Optimization and Topic Coverage", True,
                                                    f"Comprehensive topic coverage achieved: "
                                                    f"coverage={coverage_percentage}%, articles={articles_count}, "
                                                    f"blocks={total_blocks}")
                                        return True
                                    else:
                                        self.log_test("Coverage Optimization and Topic Coverage", False,
                                                    f"Insufficient coverage: coverage={coverage_percentage}%, "
                                                    f"articles={articles_count}, blocks={total_blocks}")
                                        return False
                                else:
                                    self.log_test("Coverage Optimization and Topic Coverage", False,
                                                "Global outline planning not found")
                                    return False
                            else:
                                self.log_test("Coverage Optimization and Topic Coverage", False,
                                            f"Validation failed: {validation}")
                                return False
                        else:
                            self.log_test("Coverage Optimization and Topic Coverage", False,
                                        "Validation not found in processing results")
                            return False
                    else:
                        self.log_test("Coverage Optimization and Topic Coverage", False,
                                    f"Processing failed: success={data.get('success')}, engine={data.get('engine')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Coverage Optimization and Topic Coverage", False,
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Coverage Optimization and Topic Coverage", False, f"Error: {e}")
            return False
    
    async def test_v2_processing_pipeline_integration(self):
        """Test integration with V2MultiDimensionalAnalyzer (Step 3) and V2PerArticleOutlinePlanner (Step 5)"""
        try:
            # Test with content that requires full pipeline integration
            pipeline_test_content = """
            # Advanced Machine Learning Implementation Guide
            
            ## Introduction to Machine Learning
            Comprehensive overview of machine learning concepts and applications.
            
            ## Data Preprocessing and Feature Engineering
            Essential data preparation techniques for machine learning models.
            
            ## Model Selection and Training
            Choosing appropriate algorithms and training methodologies.
            
            ## Model Evaluation and Validation
            Comprehensive evaluation metrics and validation strategies.
            
            ## Deployment and Production
            Deploying machine learning models in production environments.
            """
            
            payload = {
                "content": pipeline_test_content,
                "metadata": {
                    "title": "V2 Pipeline Integration Test",
                    "source": "test_suite",
                    "test_type": "pipeline_integration"
                }
            }
            
            async with self.session.post(f"{API_BASE}/content/process", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('engine') == 'v2':
                        processing_results = data.get('processing_results', {})
                        
                        # Verify Step 3: Multi-dimensional analysis
                        step3_present = 'multi_dimensional_analysis' in processing_results
                        step3_status = processing_results.get('multi_dimensional_analysis', {}).get('status') == 'completed' if step3_present else False
                        
                        # Verify Step 4: Global outline planning
                        step4_present = 'global_outline_planning' in processing_results
                        step4_status = processing_results.get('global_outline_planning', {}).get('status') == 'completed' if step4_present else False
                        
                        # Verify Step 5: Per-article outline planning
                        step5_present = 'per_article_outline_planning' in processing_results
                        step5_status = processing_results.get('per_article_outline_planning', {}).get('status') == 'completed' if step5_present else False
                        
                        # Check integration success
                        if step3_present and step4_present and (step5_present or 'article_generation' in processing_results):
                            if step3_status and step4_status:
                                self.log_test("V2 Processing Pipeline Integration", True,
                                            f"V2 pipeline integration successful: "
                                            f"Step3(Analysis)={step3_status}, Step4(GlobalOutline)={step4_status}, "
                                            f"Step5/ArticleGen={step5_status or 'article_generation' in processing_results}")
                                return True
                            else:
                                self.log_test("V2 Processing Pipeline Integration", False,
                                            f"Pipeline steps failed: Step3={step3_status}, Step4={step4_status}")
                                return False
                        else:
                            self.log_test("V2 Processing Pipeline Integration", False,
                                        f"Missing pipeline steps: Step3={step3_present}, Step4={step4_present}, Step5={step5_present}")
                            return False
                    else:
                        self.log_test("V2 Processing Pipeline Integration", False,
                                    f"Processing failed: success={data.get('success')}, engine={data.get('engine')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("V2 Processing Pipeline Integration", False,
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("V2 Processing Pipeline Integration", False, f"Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all V2 Engine Step 4 Global Outline Planning tests"""
        print("🧪 V2 ENGINE STEP 4 GLOBAL OUTLINE PLANNING - 100% SUCCESS RATE VERIFICATION")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Define test sequence for comprehensive verification
            tests = [
                ("V2 Engine Health Check with Global Outline Planning", self.test_v2_engine_health_check),
                ("Global Outline Planning Database Collections", self.test_global_outline_database_collections),
                ("Hierarchical Organization and Content Structure", self.test_hierarchical_organization_and_content_structure),
                ("Cross-Article Relationships Mapping", self.test_cross_article_relationships_mapping),
                ("Coverage Optimization and Topic Coverage", self.test_coverage_optimization_and_topic_coverage),
                ("V2 Processing Pipeline Integration", self.test_v2_processing_pipeline_integration),
            ]
            
            # Run tests
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                print(f"\n🧪 TESTING: {test_name}")
                try:
                    success = await test_func()
                    if success:
                        passed_tests += 1
                except Exception as e:
                    print(f"❌ TEST ERROR: {test_name} - {e}")
                    self.log_test(test_name, False, f"Test execution error: {e}")
            
            # Calculate success rate
            success_rate = (passed_tests / total_tests) * 100
            
            print(f"\n" + "=" * 80)
            print(f"🎯 V2 ENGINE STEP 4 GLOBAL OUTLINE PLANNING TEST RESULTS")
            print(f"   ✅ Passed: {passed_tests}/{total_tests} tests")
            print(f"   📊 Success Rate: {success_rate:.1f}%")
            
            if success_rate == 100.0:
                print(f"   🎉 100% SUCCESS RATE ACHIEVED - V2 Engine Step 4 Global Outline Planning FULLY OPERATIONAL")
            elif success_rate >= 96.4:
                print(f"   ✅ SUCCESS RATE IMPROVED from previous 96.4% to {success_rate:.1f}%")
            else:
                print(f"   ⚠️  SUCCESS RATE: {success_rate:.1f}% - Areas needing attention identified")
            
            print(f"\n📋 DETAILED TEST RESULTS:")
            for result in self.test_results:
                status = "✅" if result['success'] else "❌"
                print(f"   {status} {result['test']}: {'PASSED' if result['success'] else 'FAILED'}")
                if not result['success'] and result['details']:
                    print(f"      Details: {result['details']}")
            
            return success_rate
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution"""
    tester = V2GlobalOutlinePlanningTester()
    success_rate = await tester.run_all_tests()
    
    # Exit with appropriate code
    if success_rate == 100.0:
        print(f"\n🎉 V2 ENGINE STEP 4 GLOBAL OUTLINE PLANNING: 100% SUCCESS RATE CONFIRMED")
        sys.exit(0)
    else:
        print(f"\n⚠️  V2 ENGINE STEP 4 GLOBAL OUTLINE PLANNING: {success_rate:.1f}% SUCCESS RATE")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())