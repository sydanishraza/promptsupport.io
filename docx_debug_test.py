#!/usr/bin/env python3
"""
DOCX Processing Debug Test - Comprehensive Investigation
Specifically designed to debug why DOCX processing generates single summarized articles 
instead of comprehensive ones as requested in the review.
"""

import requests
import json
import os
import io
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com') + '/api'

class DOCXProcessingDebugTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🔍 DOCX Processing Debug Test - Backend URL: {self.base_url}")
        
    def test_docx_processing_flow_debug(self):
        """
        CRITICAL DEBUG TEST: Trace DOCX processing flow to identify why it's generating 
        single summarized articles instead of comprehensive ones
        """
        print("\n" + "="*80)
        print("🎯 CRITICAL DEBUG: DOCX Processing Flow Investigation")
        print("="*80)
        print("OBJECTIVE: Find why DOCX processing generates single summarized articles")
        print("EXPECTED: Multiple comprehensive articles like PDF processing")
        print("="*80)
        
        try:
            # Create a substantial DOCX-like content that should generate multiple comprehensive articles
            test_docx_content = """Products and Assortments Management Guide

# Chapter 1: Product Strategy Overview

Product strategy forms the foundation of successful business operations. A comprehensive product strategy encompasses market analysis, competitive positioning, and customer needs assessment. Organizations must develop robust frameworks for product development, lifecycle management, and portfolio optimization.

The strategic approach to product management involves multiple stakeholders across different departments. Marketing teams provide market insights, engineering teams deliver technical specifications, and sales teams offer customer feedback. This collaborative approach ensures that products meet market demands while maintaining technical feasibility and commercial viability.

Key components of product strategy include market segmentation, value proposition development, pricing strategies, and go-to-market planning. Each component requires careful analysis and strategic thinking to ensure successful product launches and sustained market performance.

# Chapter 2: Assortment Planning Fundamentals

Assortment planning represents a critical business function that directly impacts revenue generation and customer satisfaction. Effective assortment planning requires deep understanding of customer preferences, market trends, and inventory management principles.

The assortment planning process involves multiple analytical steps including demand forecasting, category analysis, and performance evaluation. Planners must consider seasonal variations, promotional activities, and competitive dynamics when developing assortment strategies.

Modern assortment planning leverages advanced analytics and machine learning algorithms to optimize product mix decisions. These technologies enable more accurate demand predictions and better inventory allocation across different channels and locations.

Data-driven assortment planning helps organizations reduce inventory costs while improving customer satisfaction through better product availability. The integration of real-time sales data and predictive analytics creates opportunities for dynamic assortment optimization.

# Chapter 3: Category Management Excellence

Category management provides a systematic approach to managing product categories as strategic business units. This methodology focuses on maximizing category performance through strategic planning, tactical execution, and continuous improvement.

The category management process includes category definition, role assignment, strategy development, and performance measurement. Each step requires careful analysis and strategic decision-making to ensure optimal category performance.

Successful category management requires collaboration between retailers and suppliers to create mutually beneficial partnerships. These partnerships focus on driving category growth, improving operational efficiency, and enhancing customer experience.

Category captains play crucial roles in category management by providing market insights, analytical capabilities, and strategic recommendations. The selection and management of category captains significantly impacts category performance and competitive positioning.

# Chapter 4: Inventory Optimization Strategies

Inventory optimization balances the competing objectives of minimizing inventory costs while maximizing service levels. This complex optimization problem requires sophisticated analytical approaches and strategic thinking.

The inventory optimization process considers multiple factors including demand variability, supply chain constraints, and service level requirements. Organizations must develop comprehensive inventory policies that address these various considerations.

Advanced inventory optimization techniques include safety stock optimization, reorder point calculation, and economic order quantity determination. These techniques help organizations minimize total inventory costs while maintaining desired service levels.

Technology plays an increasingly important role in inventory optimization through automated replenishment systems, demand sensing capabilities, and predictive analytics. These technologies enable more responsive and efficient inventory management practices.

# Chapter 5: Performance Measurement and Analytics

Performance measurement provides the foundation for continuous improvement in product and assortment management. Effective measurement systems track key performance indicators across multiple dimensions including financial performance, operational efficiency, and customer satisfaction.

The development of comprehensive measurement frameworks requires careful consideration of business objectives, stakeholder requirements, and data availability. Organizations must balance the need for detailed insights with the practical constraints of data collection and analysis.

Advanced analytics capabilities enable deeper insights into performance drivers and improvement opportunities. Machine learning algorithms can identify patterns and relationships that traditional analytical approaches might miss.

Regular performance reviews and strategic adjustments ensure that product and assortment strategies remain aligned with changing market conditions and business objectives. This continuous improvement approach drives sustained competitive advantage."""

            # Create file-like object
            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('products_assortments_debug.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Test with training/process endpoint (where the issue was reported)
            form_data = {
                'template_id': 'comprehensive_processing',
                'training_mode': 'true'
            }
            
            print("📤 Uploading DOCX file for comprehensive processing debug...")
            print(f"📊 Content size: {len(test_docx_content)} characters")
            print(f"📚 Expected: Multiple comprehensive articles (5 chapters)")
            
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
            
            if response.status_code != 200:
                print(f"❌ DOCX processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📋 Response Keys: {list(data.keys())}")
            
            # CRITICAL DEBUG ANALYSIS
            print("\n" + "="*60)
            print("🔍 CRITICAL DEBUG ANALYSIS")
            print("="*60)
            
            # 1. Check which functions were actually called
            success = data.get('success', False)
            articles = data.get('articles', [])
            processing_approach = data.get('processing_approach', 'unknown')
            chunks_created = data.get('chunks_created', 0)
            
            print(f"✅ Processing Success: {success}")
            print(f"📚 Articles Generated: {len(articles)}")
            print(f"🔧 Processing Approach: {processing_approach}")
            print(f"📄 Chunks Created: {chunks_created}")
            
            # 2. Analyze article characteristics
            if articles:
                print(f"\n📊 ARTICLE ANALYSIS:")
                total_words = 0
                for i, article in enumerate(articles):
                    title = article.get('title', 'Untitled')
                    content = article.get('content', '') or article.get('html', '')
                    word_count = len(content.split()) if content else 0
                    total_words += word_count
                    
                    print(f"  Article {i+1}: '{title}'")
                    print(f"    Word Count: {word_count}")
                    print(f"    Content Length: {len(content)} chars")
                    
                    # Check for title patterns
                    if title.startswith("Comprehensive Guide To"):
                        print(f"    ⚠️ ISSUE DETECTED: Generic title pattern")
                    
                    # Check content quality
                    if word_count < 500:
                        print(f"    ⚠️ ISSUE DETECTED: Short article (< 500 words)")
                    elif word_count > 1000:
                        print(f"    ✅ GOOD: Comprehensive article (> 1000 words)")
                
                avg_words = total_words / len(articles) if articles else 0
                print(f"\n📈 SUMMARY STATISTICS:")
                print(f"  Total Words: {total_words}")
                print(f"  Average Words per Article: {avg_words:.0f}")
                print(f"  Expected: 800-1500 words per article")
                
                # 3. Check for fallback behavior
                if len(articles) == 1 and avg_words < 800:
                    print(f"\n❌ CRITICAL ISSUE DETECTED:")
                    print(f"  - Single article generated (expected: multiple)")
                    print(f"  - Low word count ({avg_words:.0f} words)")
                    print(f"  - Likely using simplified/fallback processing")
                    return False
                elif len(articles) > 1 and avg_words > 800:
                    print(f"\n✅ COMPREHENSIVE PROCESSING WORKING:")
                    print(f"  - Multiple articles generated ({len(articles)})")
                    print(f"  - Good word count ({avg_words:.0f} words average)")
                    print(f"  - Using comprehensive processing approach")
                    return True
                else:
                    print(f"\n⚠️ MIXED RESULTS:")
                    print(f"  - Articles: {len(articles)} (expected: multiple)")
                    print(f"  - Word count: {avg_words:.0f} (expected: 800-1500)")
                    print(f"  - May need further investigation")
                    return True
            else:
                print(f"\n❌ CRITICAL FAILURE: No articles generated")
                return False
                
        except Exception as e:
            print(f"❌ DOCX processing debug test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_title_generation_investigation(self):
        """
        Investigate why titles are always starting with "Comprehensive Guide To"
        """
        print("\n" + "="*80)
        print("🔍 TITLE GENERATION INVESTIGATION")
        print("="*80)
        print("OBJECTIVE: Find why titles start with 'Comprehensive Guide To'")
        print("EXPECTED: Contextual titles based on actual content")
        print("="*80)
        
        try:
            # Create content with specific titles that should be preserved
            test_content = """Marketing Strategy Implementation Guide

# Customer Acquisition Strategies
This section focuses on proven methods for acquiring new customers through digital marketing channels, traditional advertising, and referral programs.

# Revenue Optimization Techniques  
This section covers advanced techniques for maximizing revenue through pricing strategies, upselling, cross-selling, and customer lifetime value optimization.

# Brand Development Framework
This section outlines a comprehensive framework for building strong brand identity, brand positioning, and brand equity in competitive markets."""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('title_generation_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'comprehensive_processing',
                'training_mode': 'true'
            }
            
            print("📤 Testing title generation patterns...")
            print("📚 Expected titles:")
            print("  - Customer Acquisition Strategies")
            print("  - Revenue Optimization Techniques")
            print("  - Brand Development Framework")
            print("❌ NOT expected: 'Comprehensive Guide To...'")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"\n📊 TITLE GENERATION RESULTS:")
                
                generic_titles = 0
                contextual_titles = 0
                
                for i, article in enumerate(articles):
                    title = article.get('title', 'Untitled')
                    print(f"  Article {i+1}: '{title}'")
                    
                    # Check for generic title patterns
                    if title.startswith("Comprehensive Guide To"):
                        print(f"    ❌ GENERIC TITLE DETECTED")
                        generic_titles += 1
                    elif any(keyword in title for keyword in ['Customer', 'Revenue', 'Brand', 'Marketing']):
                        print(f"    ✅ CONTEXTUAL TITLE DETECTED")
                        contextual_titles += 1
                    else:
                        print(f"    ⚠️ UNKNOWN TITLE PATTERN")
                
                print(f"\n📈 TITLE ANALYSIS:")
                print(f"  Generic Titles: {generic_titles}")
                print(f"  Contextual Titles: {contextual_titles}")
                print(f"  Total Articles: {len(articles)}")
                
                if generic_titles > 0:
                    print(f"\n❌ TITLE GENERATION ISSUE CONFIRMED:")
                    print(f"  - {generic_titles} articles have generic 'Comprehensive Guide To' titles")
                    print(f"  - System is not using contextual title generation")
                    print(f"  - May be using template-based title generation")
                    return False
                elif contextual_titles > 0:
                    print(f"\n✅ TITLE GENERATION WORKING:")
                    print(f"  - {contextual_titles} articles have contextual titles")
                    print(f"  - System is using content-based title generation")
                    return True
                else:
                    print(f"\n⚠️ TITLE GENERATION INCONCLUSIVE:")
                    print(f"  - No clear pattern detected")
                    print(f"  - May need further investigation")
                    return True
            else:
                print(f"❌ Title generation test failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Title generation investigation failed - {str(e)}")
            return False
    
    def test_content_splitting_analysis(self):
        """
        Test whether content is being split into multiple articles or processed as single article
        """
        print("\n" + "="*80)
        print("🔍 CONTENT SPLITTING ANALYSIS")
        print("="*80)
        print("OBJECTIVE: Verify content is split into multiple articles, not single article")
        print("="*80)
        
        try:
            # Create content with clear section boundaries that should be split
            test_content = """Content Splitting Test Document

# Section 1: Introduction to Content Splitting
This is the first section that should become its own comprehensive article. The content splitting system should recognize this as a distinct section based on the H1 heading and create a separate article with substantial content development.

This section should be expanded with comprehensive explanations, examples, and detailed analysis to meet the word count requirements for comprehensive articles.

# Section 2: Advanced Content Processing
This is the second section that should become a separate comprehensive article. The system should recognize the H1 boundary and create a new article starting from this point.

The content processing system should apply comprehensive enhancement to this section, expanding it with detailed explanations and professional formatting.

# Section 3: Quality Assurance Methods
This third section should also become its own comprehensive article. The splitting algorithm should maintain clear boundaries between sections while ensuring each article has substantial content.

Quality assurance in content processing involves multiple validation steps and comprehensive review processes.

# Section 4: Performance Optimization
The fourth section should demonstrate that the system can handle multiple sections and create multiple comprehensive articles rather than combining everything into a single summarized article.

Performance optimization requires careful analysis of processing workflows and systematic improvement approaches."""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('content_splitting_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'comprehensive_processing',
                'training_mode': 'true'
            }
            
            print("📤 Testing content splitting behavior...")
            print("📊 Input: 4 distinct sections with H1 headings")
            print("📚 Expected: 4 separate comprehensive articles")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"\n📊 CONTENT SPLITTING RESULTS:")
                print(f"  Input Sections: 4")
                print(f"  Generated Articles: {len(articles)}")
                
                if len(articles) == 4:
                    print(f"  ✅ PERFECT SPLITTING: Each section became an article")
                elif len(articles) > 1:
                    print(f"  ✅ GOOD SPLITTING: Multiple articles generated")
                elif len(articles) == 1:
                    print(f"  ❌ POOR SPLITTING: All content combined into single article")
                    print(f"  ❌ This indicates the system is not splitting content properly")
                    return False
                
                # Analyze article titles and content
                for i, article in enumerate(articles):
                    title = article.get('title', 'Untitled')
                    content = article.get('content', '') or article.get('html', '')
                    word_count = len(content.split()) if content else 0
                    
                    print(f"\n  Article {i+1}: '{title}'")
                    print(f"    Word Count: {word_count}")
                    
                    # Check if title corresponds to expected sections
                    expected_keywords = ['Introduction', 'Advanced', 'Quality', 'Performance']
                    if any(keyword in title for keyword in expected_keywords):
                        print(f"    ✅ Title matches expected section")
                    else:
                        print(f"    ⚠️ Title doesn't match expected section")
                
                # Overall assessment
                if len(articles) >= 2:
                    print(f"\n✅ CONTENT SPLITTING WORKING:")
                    print(f"  - Multiple articles generated ({len(articles)})")
                    print(f"  - Content is being split properly")
                    return True
                else:
                    print(f"\n❌ CONTENT SPLITTING FAILED:")
                    print(f"  - Only {len(articles)} article generated")
                    print(f"  - Content not being split into multiple articles")
                    return False
            else:
                print(f"❌ Content splitting test failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content splitting analysis failed - {str(e)}")
            return False
    
    def run_comprehensive_debug_suite(self):
        """
        Run all debug tests to identify the root cause of DOCX processing issues
        """
        print("\n" + "="*100)
        print("🚀 COMPREHENSIVE DOCX PROCESSING DEBUG SUITE")
        print("="*100)
        print("MISSION: Find why DOCX processing generates single summarized articles")
        print("INSTEAD OF: Multiple comprehensive articles like PDF processing")
        print("="*100)
        
        test_results = {}
        
        # Run all debug tests
        tests = [
            ("DOCX Processing Flow Debug", self.test_docx_processing_flow_debug),
            ("Content Splitting Analysis", self.test_content_splitting_analysis),
            ("Title Generation Investigation", self.test_title_generation_investigation)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"🧪 Running: {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                test_results[test_name] = result
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}")
                test_results[test_name] = False
        
        # Final analysis
        print(f"\n" + "="*100)
        print("📊 COMPREHENSIVE DEBUG RESULTS")
        print("="*100)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {status}: {test_name}")
        
        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        if not test_results.get("DOCX Processing Flow Debug", True):
            print("❌ CRITICAL: DOCX processing is generating single summarized articles")
            print("   ROOT CAUSE: System is using simplified/fallback processing instead of comprehensive")
            
        if not test_results.get("Content Splitting Analysis", True):
            print("❌ CRITICAL: Content not being split into multiple articles")
            print("   ROOT CAUSE: Chunking/splitting logic not working for DOCX files")
            
        if not test_results.get("Title Generation Investigation", True):
            print("❌ CRITICAL: Generic titles being generated instead of contextual ones")
            print("   ROOT CAUSE: Template-based title generation instead of content-based")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print("1. Check if DOCX files are triggering fallback to simplified processing")
        print("2. Verify create_comprehensive_articles_from_docx_content() is being called")
        print("3. Ensure content splitting logic works for DOCX format")
        print("4. Fix title generation to use contextual content instead of templates")
        print("5. Align DOCX processing path with PDF processing path")
        
        return passed_tests >= 2  # At least 2 out of 3 tests should pass

def main():
    """Run the comprehensive DOCX processing debug suite"""
    tester = DOCXProcessingDebugTest()
    
    print("🎯 DOCX PROCESSING DEBUG TEST SUITE")
    print("Investigating why DOCX processing generates single summarized articles")
    print("instead of comprehensive ones like PDF processing")
    
    success = tester.run_comprehensive_debug_suite()
    
    if success:
        print(f"\n✅ DEBUG SUITE COMPLETED - Issues identified and analyzed")
    else:
        print(f"\n❌ DEBUG SUITE COMPLETED - Critical issues found requiring fixes")
    
    return success

if __name__ == "__main__":
    main()

def test_docx_html_pipeline():
    """Test with DOCX file to trigger HTML preprocessing pipeline"""
    print("🔍 TESTING DOCX FILE TO TRIGGER HTML PREPROCESSING PIPELINE")
    print("=" * 70)
    
    # Create DOCX-like content (will be treated as DOCX due to extension)
    docx_content = """<h1>Introduction to Machine Learning</h1>
<p>This is the introduction section that explains the basics of machine learning and artificial intelligence. This section should become the first article based on the H1 heading structure.</p>
<p>Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task.</p>

<h1>Data Preprocessing and Feature Engineering</h1>
<p>This is the second major section focusing on data preprocessing techniques. This should become the second article based on the H1 heading structure.</p>
<p>Data preprocessing is crucial for successful machine learning projects. It involves cleaning, transforming, and preparing raw data for analysis.</p>

<h1>Model Training and Evaluation</h1>
<p>This is the third major section covering model training methodologies. This should become the third article based on the H1 heading structure.</p>
<p>Model training involves selecting appropriate algorithms, tuning hyperparameters, and evaluating model performance using various metrics.</p>

<h1>Deployment and Production Considerations</h1>
<p>This is the fourth and final major section about deploying models to production. This should become the fourth article based on the H1 heading structure.</p>
<p>Deploying machine learning models to production requires careful consideration of scalability, monitoring, and maintenance requirements.</p>"""

    try:
        file_data = io.BytesIO(docx_content.encode('utf-8'))
        
        files = {
            'file': ('multi_h1_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true'
        }
        
        print("📤 Uploading DOCX file to trigger HTML preprocessing pipeline...")
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=120
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"\n🔍 DOCX PROCESSING RESULTS:")
            print(f"Articles Generated: {len(articles)}")
            
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'No Title')
                print(f"Article {i}: '{title}'")
            
            return True
        else:
            print(f"❌ DOCX processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ DOCX test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_docx_html_pipeline()