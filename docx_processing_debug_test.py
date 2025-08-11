#!/usr/bin/env python3
"""
DOCX Processing Debug Test
Test the specific DOCX processing pipeline that was failing according to test_result.md
"""

import requests
import json
import os
import io
import time
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://29ab9b48-9f0b-482b-8a23-9ef1aebd2745.preview.emergentagent.com') + '/api'

class DOCXProcessingDebugTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🎯 Testing DOCX Processing Pipeline at: {self.base_url}")
        print("🔍 DEBUGGING DOCX PROCESSING ISSUES:")
        print("1. Test /api/content/upload endpoint with DOCX")
        print("2. Test /api/training/process endpoint with DOCX")
        print("3. Check for HTML preprocessing pipeline errors")
        print("4. Verify comprehensive vs simplified processing")
        print("5. Capture exact error messages and stack traces")
        
    def test_content_upload_docx(self):
        """Test /api/content/upload with DOCX file"""
        print("\n🔍 STEP 1: Testing /api/content/upload with DOCX...")
        try:
            # Create a substantial DOCX file that should trigger comprehensive processing
            test_docx_content = """Products and Assortments Management Guide

# Chapter 1: Product Management Overview

Product management is a critical business function that involves planning, developing, and marketing products throughout their lifecycle.

## 1.1 Product Strategy
A well-defined product strategy serves as the foundation for all product decisions. It should align with the company's overall business objectives and market positioning.

Key components of product strategy include:
- Market analysis and customer segmentation
- Competitive landscape assessment
- Value proposition definition
- Product roadmap development

## 1.2 Product Development Process
The product development process typically follows these stages:

1. **Ideation and Concept Development**
   - Market research and customer feedback
   - Brainstorming and idea generation
   - Concept validation and feasibility analysis

2. **Design and Prototyping**
   - Technical specifications
   - User experience design
   - Prototype development and testing

3. **Development and Testing**
   - Agile development methodologies
   - Quality assurance and testing
   - Performance optimization

4. **Launch and Marketing**
   - Go-to-market strategy
   - Marketing campaigns
   - Sales enablement

# Chapter 2: Assortment Planning

Assortment planning is the process of selecting the right mix of products to offer customers at the right time and in the right quantities.

## 2.1 Assortment Strategy
Effective assortment strategy considers multiple factors:

- Customer preferences and buying behavior
- Seasonal trends and market dynamics
- Inventory management and supply chain constraints
- Profitability and margin optimization

## 2.2 Category Management
Category management involves organizing products into logical groups and optimizing the performance of each category.

Key principles include:
- Customer-centric category definitions
- Data-driven decision making
- Cross-functional collaboration
- Continuous performance monitoring

## 2.3 Inventory Optimization
Balancing inventory levels to meet customer demand while minimizing costs requires sophisticated planning and forecasting.

Techniques include:
- Demand forecasting models
- Safety stock calculations
- Reorder point optimization
- ABC analysis for prioritization

# Chapter 3: Performance Measurement

Measuring the success of product and assortment strategies requires comprehensive metrics and analytics.

## 3.1 Key Performance Indicators
Important KPIs for product management include:
- Revenue and profitability metrics
- Market share and competitive position
- Customer satisfaction and retention
- Inventory turnover and efficiency

## 3.2 Analytics and Reporting
Modern product management relies on data analytics to drive decisions:
- Sales performance analysis
- Customer behavior insights
- Market trend identification
- Predictive modeling

This comprehensive guide provides the foundation for effective product and assortment management in today's competitive marketplace."""

            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('products_assortments_guide.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "docx_debug_test",
                    "test_type": "content_upload_docx",
                    "document_type": "comprehensive_guide"
                })
            }
            
            print("📤 Uploading DOCX file to /api/content/upload...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=120
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📋 Response Keys: {list(data.keys())}")
                
                success = data.get('success', False)
                status = data.get('status', 'unknown')
                chunks_created = data.get('chunks_created', 0)
                job_id = data.get('job_id', 'none')
                
                print(f"✅ Success: {success}")
                print(f"📊 Status: {status}")
                print(f"📊 Chunks Created: {chunks_created}")
                print(f"📊 Job ID: {job_id}")
                
                if success and chunks_created > 0:
                    print("✅ STEP 1 PASSED: /api/content/upload with DOCX successful")
                    return True, data
                else:
                    print("❌ STEP 1 FAILED: /api/content/upload processing failed")
                    error = data.get('error', 'Unknown error')
                    print(f"Error: {error}")
                    return False, data
            else:
                print(f"❌ STEP 1 FAILED: HTTP error {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ STEP 1 FAILED: Exception during content upload test - {str(e)}")
            traceback.print_exc()
            return False, {}
    
    def test_training_process_docx(self):
        """Test /api/training/process with DOCX file"""
        print("\n🔍 STEP 2: Testing /api/training/process with DOCX...")
        try:
            # Create the same substantial DOCX file
            test_docx_content = """Products and Assortments Management Guide

# Chapter 1: Product Management Overview

Product management is a critical business function that involves planning, developing, and marketing products throughout their lifecycle.

## 1.1 Product Strategy
A well-defined product strategy serves as the foundation for all product decisions. It should align with the company's overall business objectives and market positioning.

Key components of product strategy include:
- Market analysis and customer segmentation
- Competitive landscape assessment
- Value proposition definition
- Product roadmap development

## 1.2 Product Development Process
The product development process typically follows these stages:

1. **Ideation and Concept Development**
   - Market research and customer feedback
   - Brainstorming and idea generation
   - Concept validation and feasibility analysis

2. **Design and Prototyping**
   - Technical specifications
   - User experience design
   - Prototype development and testing

3. **Development and Testing**
   - Agile development methodologies
   - Quality assurance and testing
   - Performance optimization

4. **Launch and Marketing**
   - Go-to-market strategy
   - Marketing campaigns
   - Sales enablement

# Chapter 2: Assortment Planning

Assortment planning is the process of selecting the right mix of products to offer customers at the right time and in the right quantities.

## 2.1 Assortment Strategy
Effective assortment strategy considers multiple factors:

- Customer preferences and buying behavior
- Seasonal trends and market dynamics
- Inventory management and supply chain constraints
- Profitability and margin optimization

## 2.2 Category Management
Category management involves organizing products into logical groups and optimizing the performance of each category.

Key principles include:
- Customer-centric category definitions
- Data-driven decision making
- Cross-functional collaboration
- Continuous performance monitoring

## 2.3 Inventory Optimization
Balancing inventory levels to meet customer demand while minimizing costs requires sophisticated planning and forecasting.

Techniques include:
- Demand forecasting models
- Safety stock calculations
- Reorder point optimization
- ABC analysis for prioritization

# Chapter 3: Performance Measurement

Measuring the success of product and assortment strategies requires comprehensive metrics and analytics.

## 3.1 Key Performance Indicators
Important KPIs for product management include:
- Revenue and profitability metrics
- Market share and competitive position
- Customer satisfaction and retention
- Inventory turnover and efficiency

## 3.2 Analytics and Reporting
Modern product management relies on data analytics to drive decisions:
- Sales performance analysis
- Customer behavior insights
- Market trend identification
- Predictive modeling

This comprehensive guide provides the foundation for effective product and assortment management in today's competitive marketplace."""

            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('products_assortments_training.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use comprehensive processing template
            form_data = {
                'template_id': 'comprehensive_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "comprehensive_processing",
                    "processing_approach": "comprehensive",
                    "output_requirements": {
                        "format": "html",
                        "min_word_count": 800,
                        "max_word_count": 1500,
                        "quality_benchmarks": ["content_completeness", "proper_formatting"]
                    },
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True
                    }
                })
            }
            
            print("📤 Processing DOCX file with /api/training/process...")
            print("🎯 Using comprehensive processing approach...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=180  # Extended timeout for comprehensive processing
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📋 Response Keys: {list(data.keys())}")
                
                success = data.get('success', False)
                session_id = data.get('session_id', 'none')
                articles = data.get('articles', [])
                images_processed = data.get('images_processed', 0)
                processing_time_reported = data.get('processing_time', 0)
                
                print(f"✅ Success: {success}")
                print(f"📊 Session ID: {session_id}")
                print(f"📊 Articles Generated: {len(articles)}")
                print(f"📊 Images Processed: {images_processed}")
                print(f"📊 Processing Time: {processing_time_reported}s")
                
                if success and len(articles) > 0:
                    print("✅ STEP 2 PASSED: /api/training/process with DOCX successful")
                    
                    # Analyze article quality
                    total_words = 0
                    for i, article in enumerate(articles):
                        word_count = article.get('word_count', 0)
                        title = article.get('title', f'Article {i+1}')
                        total_words += word_count
                        print(f"📄 {title}: {word_count} words")
                    
                    avg_words = total_words / len(articles) if articles else 0
                    print(f"📊 Average words per article: {avg_words:.0f}")
                    
                    if avg_words >= 800:
                        print("✅ COMPREHENSIVE PROCESSING: Articles meet word count requirements")
                    else:
                        print("⚠️ SIMPLIFIED PROCESSING: Articles below comprehensive word count")
                        print("🎯 This indicates fallback to simplified processing occurred")
                    
                    return True, data
                else:
                    print("❌ STEP 2 FAILED: /api/training/process processing failed")
                    error = data.get('error', 'Unknown error')
                    print(f"Error: {error}")
                    
                    # Check for specific HTML preprocessing errors
                    if 'AttributeError' in error and 'DocumentPreprocessor' in error:
                        print("🎯 CRITICAL ERROR: DocumentPreprocessor AttributeError detected")
                        print("🎯 This confirms the HTML preprocessing pipeline is failing")
                    
                    return False, data
            else:
                print(f"❌ STEP 2 FAILED: HTTP error {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ STEP 2 FAILED: Exception during training process test - {str(e)}")
            traceback.print_exc()
            return False, {}
    
    def test_html_preprocessing_specific(self):
        """Test HTML preprocessing pipeline specifically"""
        print("\n🔍 STEP 3: Testing HTML Preprocessing Pipeline Specifically...")
        try:
            # Create a DOCX file that should definitely trigger HTML preprocessing
            test_docx_content = """HTML Preprocessing Pipeline Test

This document is specifically designed to trigger the HTML preprocessing pipeline
that was mentioned as failing in the test_result.md file.

According to the review request, the system should:
1. Use process_with_html_preprocessing_pipeline function
2. Create DocumentPreprocessor instance
3. Call preprocess_document method
4. Process HTML chunks with _assign_block_ids_to_chunk
5. Tokenize images with _tokenize_images_in_chunk

If the HTML preprocessing pipeline fails, the system falls back to:
- create_multiple_articles_from_content() (simplified processing)
- This generates short articles (~387 words) instead of comprehensive ones

Expected behavior with working HTML preprocessing:
- Articles should be 800-1500 words (comprehensive)
- Should use create_comprehensive_articles_from_docx_content()
- Should have proper HTML structure with data-block-id attributes

Let's test if the HTML preprocessing pipeline is actually working or if it's
falling back to simplified processing due to DocumentPreprocessor errors."""

            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('html_preprocessing_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Force HTML preprocessing pipeline
            form_data = {
                'template_id': 'html_preprocessing_test',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "html_preprocessing_test",
                    "processing_approach": "html_preprocessing_pipeline",
                    "force_html_preprocessing": True,
                    "output_requirements": {
                        "format": "html",
                        "use_html_preprocessing": True,
                        "min_word_count": 800
                    },
                    "media_handling": {
                        "extract_images": True,
                        "use_html_tokenization": True,
                        "contextual_placement": True
                    }
                })
            }
            
            print("📤 Testing HTML preprocessing pipeline specifically...")
            print("🎯 Forcing HTML preprocessing approach...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📋 Response Keys: {list(data.keys())}")
                
                success = data.get('success', False)
                articles = data.get('articles', [])
                error = data.get('error', '')
                
                print(f"✅ Success: {success}")
                print(f"📊 Articles Generated: {len(articles)}")
                
                if error:
                    print(f"❌ Error: {error}")
                    
                    # Check for HTML preprocessing specific errors
                    if 'AttributeError' in error:
                        print("🎯 ATTRIBUTEERROR DETECTED in HTML preprocessing")
                        
                        if 'DocumentPreprocessor' in error and 'has no attribute' in error:
                            print("🎯 CONFIRMED: DocumentPreprocessor missing method")
                            
                            # Extract the specific missing method
                            import re
                            match = re.search(r"'DocumentPreprocessor' object has no attribute '([^']+)'", error)
                            if match:
                                missing_method = match.group(1)
                                print(f"🎯 MISSING METHOD: {missing_method}")
                                print(f"🔧 FIX NEEDED: Add {missing_method} to DocumentPreprocessor class")
                        
                        return False, data
                
                if success and len(articles) > 0:
                    print("✅ STEP 3 PASSED: HTML preprocessing pipeline working")
                    
                    # Check if comprehensive processing was used
                    total_words = sum(article.get('word_count', 0) for article in articles)
                    avg_words = total_words / len(articles) if articles else 0
                    
                    print(f"📊 Average words per article: {avg_words:.0f}")
                    
                    if avg_words >= 800:
                        print("✅ COMPREHENSIVE PROCESSING: HTML preprocessing pipeline working")
                    else:
                        print("⚠️ SIMPLIFIED FALLBACK: HTML preprocessing may have failed")
                        print("🎯 System fell back to simplified processing")
                    
                    return True, data
                else:
                    print("❌ STEP 3 FAILED: HTML preprocessing pipeline failed")
                    return False, data
            else:
                print(f"❌ STEP 3 FAILED: HTTP error {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ STEP 3 FAILED: Exception during HTML preprocessing test - {str(e)}")
            traceback.print_exc()
            return False, {}
    
    def test_backend_logs_analysis(self):
        """Analyze backend logs for DocumentPreprocessor errors"""
        print("\n🔍 STEP 4: Analyzing Backend Logs for DocumentPreprocessor Errors...")
        try:
            print("📋 Checking backend logs for DocumentPreprocessor-related errors...")
            
            # Try to trigger processing and then check logs
            test_content = """Backend Log Analysis Test

This test is designed to trigger DOCX processing and then analyze the backend logs
for any DocumentPreprocessor-related errors.

According to the review request, the error should be:
"AttributeError: DocumentPreprocessor object has no attribute _assign_block_ids_to_chunk"

Let's see if we can capture this error in the logs."""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('log_analysis_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'log_analysis_test',
                'training_mode': 'true'
            }
            
            print("📤 Processing file to generate logs...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=60
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                error = data.get('error', '')
                
                print(f"✅ Success: {success}")
                
                if error:
                    print(f"❌ Error in response: {error}")
                    
                    if 'AttributeError' in error and 'DocumentPreprocessor' in error:
                        print("🎯 STEP 4 SUCCESS: DocumentPreprocessor AttributeError captured")
                        print("🎯 CONFIRMED: HTML preprocessing pipeline is failing")
                        return True, data
                
                print("✅ STEP 4 PASSED: No DocumentPreprocessor errors in logs")
                print("🎯 This suggests the methods exist and are working")
                return True, data
            else:
                print(f"❌ STEP 4 FAILED: HTTP error {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ STEP 4 FAILED: Exception during log analysis - {str(e)}")
            return False, {}
    
    def test_comprehensive_vs_simplified_processing(self):
        """Test to determine if comprehensive or simplified processing is being used"""
        print("\n🔍 STEP 5: Testing Comprehensive vs Simplified Processing...")
        try:
            print("🎯 Testing to determine which processing path is being used...")
            
            # Create a substantial document that should trigger comprehensive processing
            test_docx_content = """Comprehensive vs Simplified Processing Test

# Chapter 1: Introduction
This document tests whether the system uses comprehensive processing (800-1500 words per article) 
or falls back to simplified processing (~387 words per article).

## 1.1 Comprehensive Processing Indicators
If comprehensive processing is working:
- Articles should be 800-1500 words each
- Should use create_comprehensive_articles_from_docx_content()
- HTML preprocessing pipeline should be active
- DocumentPreprocessor methods should work correctly

## 1.2 Simplified Processing Indicators  
If simplified processing is being used:
- Articles will be ~387 words each
- Uses create_multiple_articles_from_content()
- HTML preprocessing pipeline failed
- System fell back due to DocumentPreprocessor errors

# Chapter 2: Test Content
This chapter provides substantial content to test the processing approach.

## 2.1 Content Analysis
The system should analyze this content and determine the appropriate processing approach.
If HTML preprocessing is working, it should create comprehensive articles with proper structure.

## 2.2 Expected Results
Based on the content length and structure, we expect:
- Multiple articles (one per chapter)
- Each article should be comprehensive (800+ words)
- Proper HTML structure with headings and paragraphs
- Professional formatting and presentation

# Chapter 3: Conclusion
This test will help determine if the DocumentPreprocessor issues are causing
the system to fall back to simplified processing instead of using the intended
comprehensive processing approach.

The results will show whether the HTML preprocessing pipeline is working correctly
or if there are indeed missing methods in the DocumentPreprocessor class."""

            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('comprehensive_vs_simplified_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'comprehensive_test',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "comprehensive_test",
                    "processing_approach": "comprehensive",
                    "output_requirements": {
                        "format": "html",
                        "target_word_count": 1200,
                        "quality_benchmarks": ["comprehensive_content", "proper_structure"]
                    }
                })
            }
            
            print("📤 Processing with comprehensive processing requirements...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                articles = data.get('articles', [])
                
                print(f"✅ Success: {success}")
                print(f"📊 Articles Generated: {len(articles)}")
                
                if success and len(articles) > 0:
                    # Analyze word counts to determine processing type
                    word_counts = []
                    for i, article in enumerate(articles):
                        word_count = article.get('word_count', 0)
                        title = article.get('title', f'Article {i+1}')
                        word_counts.append(word_count)
                        print(f"📄 {title}: {word_count} words")
                    
                    avg_words = sum(word_counts) / len(word_counts)
                    print(f"📊 Average words per article: {avg_words:.0f}")
                    
                    # Determine processing type based on word count
                    if avg_words >= 800:
                        print("✅ COMPREHENSIVE PROCESSING DETECTED")
                        print("🎯 HTML preprocessing pipeline is working correctly")
                        print("🎯 DocumentPreprocessor methods are functional")
                        processing_type = "comprehensive"
                    elif 300 <= avg_words <= 500:
                        print("⚠️ SIMPLIFIED PROCESSING DETECTED")
                        print("🎯 System fell back to simplified processing")
                        print("🎯 This suggests HTML preprocessing pipeline failed")
                        print("🎯 Possible DocumentPreprocessor method issues")
                        processing_type = "simplified"
                    else:
                        print("❓ UNKNOWN PROCESSING TYPE")
                        print(f"🎯 Unexpected word count range: {avg_words:.0f}")
                        processing_type = "unknown"
                    
                    print(f"✅ STEP 5 PASSED: Processing type identified as {processing_type}")
                    return True, {"processing_type": processing_type, "avg_words": avg_words, "data": data}
                else:
                    print("❌ STEP 5 FAILED: No articles generated")
                    return False, {}
            else:
                print(f"❌ STEP 5 FAILED: HTTP error {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ STEP 5 FAILED: Exception during processing type test - {str(e)}")
            return False, {}
    
    def run_all_tests(self):
        """Run all DOCX processing debug tests"""
        print("🎯 STARTING DOCX PROCESSING DEBUG TESTING")
        print("=" * 60)
        
        results = []
        test_data = []
        
        # Run all test steps
        result1, data1 = self.test_content_upload_docx()
        results.append(result1)
        test_data.append(data1)
        
        result2, data2 = self.test_training_process_docx()
        results.append(result2)
        test_data.append(data2)
        
        result3, data3 = self.test_html_preprocessing_specific()
        results.append(result3)
        test_data.append(data3)
        
        result4, data4 = self.test_backend_logs_analysis()
        results.append(result4)
        test_data.append(data4)
        
        result5, data5 = self.test_comprehensive_vs_simplified_processing()
        results.append(result5)
        test_data.append(data5)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 DOCX PROCESSING DEBUG TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"📊 Tests Passed: {passed}/{total}")
        
        test_names = [
            "/api/content/upload with DOCX",
            "/api/training/process with DOCX",
            "HTML Preprocessing Pipeline",
            "Backend Logs Analysis",
            "Comprehensive vs Simplified Processing"
        ]
        
        for i, (test_name, result) in enumerate(zip(test_names, results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i+1}. {test_name}: {status}")
        
        # Analyze results for root cause
        print("\n🎯 ROOT CAUSE ANALYSIS:")
        
        # Check if we detected simplified processing
        if result5 and isinstance(data5, dict) and data5.get('processing_type') == 'simplified':
            print("❌ CRITICAL ISSUE IDENTIFIED:")
            print("- System is using SIMPLIFIED processing instead of COMPREHENSIVE")
            print("- Average word count is ~387 words (should be 800-1500)")
            print("- This confirms HTML preprocessing pipeline is failing")
            print("- System falls back to create_multiple_articles_from_content()")
            print("\n🔧 REQUIRED INVESTIGATION:")
            print("1. Check if DocumentPreprocessor methods exist but have errors")
            print("2. Verify HTML preprocessing pipeline is being triggered")
            print("3. Check for silent failures in DocumentPreprocessor")
            print("4. Ensure comprehensive processing functions are called")
        elif result5 and isinstance(data5, dict) and data5.get('processing_type') == 'comprehensive':
            print("✅ SYSTEM WORKING CORRECTLY:")
            print("- Comprehensive processing is being used")
            print("- HTML preprocessing pipeline is functional")
            print("- DocumentPreprocessor methods are working")
            print("- Articles meet 800-1500 word requirements")
        else:
            print("❓ INCONCLUSIVE RESULTS:")
            print("- Unable to determine processing type definitively")
            print("- May need more specific testing")
        
        return passed >= 3  # At least 3 out of 5 tests should pass

if __name__ == "__main__":
    tester = DOCXProcessingDebugTest()
    success = tester.run_all_tests()
    
    if not success:
        print("\n❌ DOCX PROCESSING DEBUG TESTING FAILED")
        sys.exit(1)
    else:
        print("\n✅ DOCX PROCESSING DEBUG TESTING COMPLETED")
        sys.exit(0)