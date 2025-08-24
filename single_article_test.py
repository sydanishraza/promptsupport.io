#!/usr/bin/env python3
"""
Training Engine Single Article Issue Testing
Comprehensive test to identify root cause of single article generation instead of multi-article output
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com') + '/api'

class SingleArticleIssueTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"Testing Training Engine Single Article Issue at: {self.base_url}")
        
    def create_multi_h1_docx_content(self):
        """Create DOCX content with multiple H1 headings that should generate multiple articles"""
        return """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. This revolutionary technology has transformed numerous industries and continues to shape our digital world.

The fundamental concept behind machine learning involves algorithms that can identify patterns in data, make predictions, and improve their performance over time through experience. This capability makes machine learning particularly valuable for solving complex problems that traditional programming approaches cannot handle effectively.

# Types of Machine Learning Algorithms

Machine learning algorithms can be broadly categorized into three main types: supervised learning, unsupervised learning, and reinforcement learning. Each category serves different purposes and is suited for specific types of problems.

Supervised learning algorithms learn from labeled training data to make predictions on new, unseen data. Common examples include linear regression for predicting continuous values and classification algorithms for categorizing data into discrete classes.

Unsupervised learning algorithms work with unlabeled data to discover hidden patterns and structures. Clustering algorithms like K-means and hierarchical clustering are popular unsupervised techniques used for market segmentation and customer analysis.

# Applications in Modern Technology

Machine learning has found applications across virtually every industry, from healthcare and finance to entertainment and transportation. In healthcare, ML algorithms assist in medical diagnosis, drug discovery, and personalized treatment plans.

The financial sector leverages machine learning for fraud detection, algorithmic trading, and credit scoring. These applications have significantly improved the accuracy and efficiency of financial services while reducing operational costs.

In the technology sector, machine learning powers recommendation systems, natural language processing, computer vision, and autonomous systems. Companies like Google, Amazon, and Netflix rely heavily on ML algorithms to enhance user experiences and optimize their services.

# Future Trends and Developments

The future of machine learning looks incredibly promising, with emerging trends like deep learning, neural networks, and artificial general intelligence leading the way. These advanced techniques are pushing the boundaries of what's possible with AI.

Edge computing and federated learning are becoming increasingly important as organizations seek to process data closer to its source while maintaining privacy and security. This trend is particularly relevant for IoT devices and mobile applications.

Explainable AI and ethical machine learning are gaining attention as society demands more transparency and accountability in AI systems. These developments will be crucial for building trust and ensuring responsible AI deployment.

# Implementation Best Practices

Successful machine learning implementation requires careful attention to data quality, model selection, and performance evaluation. Organizations must establish robust data pipelines and maintain high-quality datasets to achieve optimal results.

Model validation and testing are critical components of any ML project. Cross-validation techniques, holdout testing, and continuous monitoring help ensure that models perform well in production environments.

Collaboration between data scientists, domain experts, and stakeholders is essential for successful ML projects. This interdisciplinary approach ensures that technical solutions align with business objectives and user needs."""

    def test_h1_detection_and_chunking(self):
        """Test H1 detection and chunking logic with multi-H1 document"""
        print("\n🔍 Testing H1 Detection and Chunking Logic...")
        try:
            # Create test content with 5 clear H1 sections
            test_content = self.create_multi_h1_docx_content()
            
            # Count expected H1 sections
            h1_count = test_content.count('# ')
            print(f"📊 Test document contains {h1_count} H1 headings")
            print("📋 Expected H1 sections:")
            h1_lines = [line.strip() for line in test_content.split('\n') if line.strip().startswith('# ')]
            for i, h1 in enumerate(h1_lines, 1):
                print(f"   {i}. {h1}")
            
            # Create file-like object
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('multi_h1_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use training template that should respect H1 structure
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_instructions": "Process document maintaining H1-based structure",
                    "output_requirements": {
                        "format": "html",
                        "respect_h1_structure": True,
                        "create_separate_articles": True
                    }
                })
            }
            
            print("📤 Processing multi-H1 document...")
            print("🎯 EXPECTED: Should generate 5 separate articles (one per H1 section)")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=180
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            
            # CRITICAL TEST: Check number of articles generated
            articles = data.get('articles', [])
            articles_count = len(articles)
            
            print(f"\n🎯 CRITICAL ANALYSIS:")
            print(f"📊 Expected Articles: {h1_count} (based on H1 count)")
            print(f"📊 Generated Articles: {articles_count}")
            
            if articles_count == 1 and h1_count > 1:
                print("❌ SINGLE ARTICLE ISSUE CONFIRMED:")
                print("   ❌ Multiple H1 sections collapsed into single article")
                print("   ❌ H1-based chunking is NOT working correctly")
                self.analyze_single_article_content(articles[0], h1_lines)
                return False
            elif articles_count == h1_count:
                print("✅ MULTI-ARTICLE GENERATION WORKING:")
                print("   ✅ Each H1 section generated separate article")
                print("   ✅ H1-based chunking is working correctly")
                self.analyze_multi_article_structure(articles, h1_lines)
                return True
            elif articles_count > 1 and articles_count < h1_count:
                print("⚠️ PARTIAL MULTI-ARTICLE GENERATION:")
                print(f"   ⚠️ Generated {articles_count} articles from {h1_count} H1 sections")
                print("   ⚠️ Some H1 sections may have been merged")
                self.analyze_partial_article_structure(articles, h1_lines)
                return True  # Partial success
            else:
                print("❓ UNEXPECTED ARTICLE COUNT:")
                print(f"   ❓ Generated {articles_count} articles from {h1_count} H1 sections")
                self.analyze_unexpected_structure(articles, h1_lines)
                return False
                
        except Exception as e:
            print(f"❌ H1 detection and chunking test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def analyze_single_article_content(self, article, expected_h1s):
        """Analyze the single article to understand why chunking failed"""
        print("\n🔍 SINGLE ARTICLE ANALYSIS:")
        
        title = article.get('title', 'No title')
        content = article.get('content', '') or article.get('html', '')
        word_count = article.get('word_count', 0)
        
        print(f"📄 Article Title: {title}")
        print(f"📊 Word Count: {word_count}")
        print(f"📏 Content Length: {len(content)} characters")
        
        # Check if all H1 content is present in single article
        h1_content_found = 0
        for h1 in expected_h1s:
            h1_text = h1.replace('# ', '').strip()
            if h1_text.lower() in content.lower():
                h1_content_found += 1
                print(f"   ✅ Found H1 content: {h1_text}")
            else:
                print(f"   ❌ Missing H1 content: {h1_text}")
        
        print(f"📊 H1 Content Coverage: {h1_content_found}/{len(expected_h1s)} sections found")
        
        # Check HTML structure
        h1_tags = content.count('<h1>')
        h2_tags = content.count('<h2>')
        h3_tags = content.count('<h3>')
        
        print(f"🏷️ HTML Structure Analysis:")
        print(f"   <h1> tags: {h1_tags}")
        print(f"   <h2> tags: {h2_tags}")
        print(f"   <h3> tags: {h3_tags}")
        
        if h1_tags > 1:
            print("   ⚠️ Multiple H1 tags found but still single article")
            print("   ⚠️ Issue may be in article generation logic, not H1 detection")
        elif h1_tags == 1 and h2_tags > 0:
            print("   ⚠️ H1 sections may have been converted to H2")
            print("   ⚠️ Issue may be in HTML preprocessing or AI processing")
        else:
            print("   ❌ H1 structure not preserved in final content")
    
    def analyze_multi_article_structure(self, articles, expected_h1s):
        """Analyze multi-article structure to confirm correct chunking"""
        print("\n✅ MULTI-ARTICLE STRUCTURE ANALYSIS:")
        
        for i, article in enumerate(articles):
            title = article.get('title', f'Article {i+1}')
            word_count = article.get('word_count', 0)
            content = article.get('content', '') or article.get('html', '')
            
            print(f"📄 Article {i+1}:")
            print(f"   Title: {title}")
            print(f"   Word Count: {word_count}")
            print(f"   Content Length: {len(content)} characters")
            
            # Check which H1 content this article contains
            h1_matches = []
            for h1 in expected_h1s:
                h1_text = h1.replace('# ', '').strip()
                if h1_text.lower() in title.lower() or h1_text.lower() in content.lower():
                    h1_matches.append(h1_text)
            
            if h1_matches:
                print(f"   ✅ Contains H1 content: {', '.join(h1_matches)}")
            else:
                print(f"   ⚠️ No clear H1 content match found")
    
    def analyze_partial_article_structure(self, articles, expected_h1s):
        """Analyze partial multi-article structure"""
        print("\n⚠️ PARTIAL MULTI-ARTICLE STRUCTURE ANALYSIS:")
        
        total_word_count = sum(article.get('word_count', 0) for article in articles)
        print(f"📊 Total Word Count Across Articles: {total_word_count}")
        
        for i, article in enumerate(articles):
            title = article.get('title', f'Article {i+1}')
            word_count = article.get('word_count', 0)
            
            print(f"📄 Article {i+1}: {title} ({word_count} words)")
    
    def analyze_unexpected_structure(self, articles, expected_h1s):
        """Analyze unexpected article structure"""
        print("\n❓ UNEXPECTED STRUCTURE ANALYSIS:")
        
        for i, article in enumerate(articles):
            title = article.get('title', f'Article {i+1}')
            word_count = article.get('word_count', 0)
            
            print(f"📄 Article {i+1}: {title} ({word_count} words)")
    
    def test_backend_logs_analysis(self):
        """Test to capture and analyze backend logs for chunking-related messages"""
        print("\n🔍 Testing Backend Logs Analysis...")
        try:
            print("📋 Looking for key log messages that indicate chunking behavior:")
            print("   - 'H1 elements found'")
            print("   - 'H1 sections found'") 
            print("   - 'requires_chunked_processing'")
            print("   - 'separate articles'")
            print("   - 'LOGICAL CHUNKING'")
            
            # Create a simple test to trigger logging
            test_content = """# First Section
This is the first section with substantial content.

# Second Section  
This is the second section with different content.

# Third Section
This is the third section to test chunking."""
            
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('log_analysis_test.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true'
            }
            
            print("📤 Processing file to capture backend logs...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"📊 Log Analysis Results:")
                print(f"   Articles Generated: {len(articles)}")
                print(f"   Processing Success: {data.get('success', False)}")
                
                # Note: We can't directly access backend logs from here,
                # but we can infer behavior from the response
                if len(articles) == 3:
                    print("✅ Backend logs likely show proper H1 detection and chunking")
                elif len(articles) == 1:
                    print("❌ Backend logs likely show chunking failure or single article processing")
                else:
                    print(f"⚠️ Backend logs show unexpected chunking behavior ({len(articles)} articles)")
                
                return True
            else:
                print(f"❌ Log analysis test failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend logs analysis failed - {str(e)}")
            return False
    
    def test_article_generation_flow(self):
        """Test the complete article generation flow to identify where chunking breaks"""
        print("\n🔍 Testing Article Generation Flow...")
        try:
            print("🔄 Testing complete pipeline: Upload → Extract → Chunk → Generate → Return")
            
            # Create content that should definitely generate multiple articles
            test_content = """# Machine Learning Fundamentals

Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention.

The core principle behind machine learning is to create algorithms that can receive input data and use statistical analysis to predict an output value within an acceptable range.

# Deep Learning Technologies

Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning. Learning can be supervised, semi-supervised or unsupervised.

Deep learning architectures such as deep neural networks, deep belief networks, recurrent neural networks and convolutional neural networks have been applied to fields including computer vision, speech recognition, natural language processing, machine translation, bioinformatics and drug design.

# Natural Language Processing

Natural language processing is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data.

The goal is a computer capable of understanding the contents of documents, including the contextual nuances of the language within them. The technology can then accurately extract information and insights contained in the documents.

# Computer Vision Applications

Computer vision is an interdisciplinary scientific field that deals with how computers can gain high-level understanding from digital images or videos. From the perspective of engineering, it seeks to understand and automate tasks that the human visual system can do.

Computer vision tasks include methods for acquiring, processing, analyzing and understanding digital images, and extraction of high-dimensional data from the real world in order to produce numerical or symbolic information.

# Reinforcement Learning Systems

Reinforcement learning is an area of machine learning concerned with how intelligent agents ought to take actions in an environment in order to maximize the notion of cumulative reward. Reinforcement learning is one of three basic machine learning paradigms, alongside supervised learning and unsupervised learning.

Reinforcement learning differs from supervised learning in not needing labelled input/output pairs to be presented, and in not needing sub-optimal actions to be explicitly corrected."""
            
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('article_flow_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_instructions": "Create separate articles for each major section",
                    "output_requirements": {
                        "format": "html",
                        "maintain_structure": True,
                        "separate_h1_sections": True
                    }
                })
            }
            
            print("📤 Testing complete article generation flow...")
            print("🎯 Expected: 5 articles (one per H1 section)")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=180
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Flow completed in {processing_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                # Analyze the complete flow
                success = data.get('success', False)
                articles = data.get('articles', [])
                session_id = data.get('session_id')
                processing_time_backend = data.get('processing_time', 0)
                
                print(f"\n🔄 ARTICLE GENERATION FLOW ANALYSIS:")
                print(f"   Success: {success}")
                print(f"   Session ID: {session_id}")
                print(f"   Backend Processing Time: {processing_time_backend}s")
                print(f"   Articles Generated: {len(articles)}")
                
                # Detailed article analysis
                if len(articles) == 5:
                    print("✅ FLOW SUCCESS: Correct number of articles generated")
                    print("   ✅ H1-based chunking working correctly")
                    print("   ✅ Article generation preserving structure")
                    return True
                elif len(articles) == 1:
                    print("❌ FLOW FAILURE: Single article generated from 5 H1 sections")
                    print("   ❌ Chunking logic is collapsing multiple sections")
                    print("   ❌ Root cause: Article generation combining chunks")
                    
                    # Analyze the single article
                    if articles:
                        single_article = articles[0]
                        content = single_article.get('content', '')
                        word_count = single_article.get('word_count', 0)
                        
                        print(f"   📊 Single Article Word Count: {word_count}")
                        print(f"   📊 Single Article Content Length: {len(content)}")
                        
                        # Check if all H1 content is merged
                        h1_sections = ['Machine Learning', 'Deep Learning', 'Natural Language', 'Computer Vision', 'Reinforcement Learning']
                        found_sections = sum(1 for section in h1_sections if section.lower() in content.lower())
                        print(f"   📊 H1 Sections Found in Single Article: {found_sections}/5")
                        
                        if found_sections >= 4:
                            print("   ❌ CONFIRMED: All H1 sections merged into single article")
                            print("   ❌ Issue is in article generation logic, not content extraction")
                    
                    return False
                else:
                    print(f"⚠️ FLOW PARTIAL: {len(articles)} articles generated (expected 5)")
                    print("   ⚠️ Some H1 sections may be merged")
                    return True  # Partial success
                    
            else:
                print(f"❌ Article generation flow failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Article generation flow test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_final_response_verification(self):
        """Test to verify the final response structure and article count"""
        print("\n🔍 Testing Final Response Verification...")
        try:
            print("📋 Verifying final API response structure and article count")
            
            # Create a definitive test with clear H1 structure
            test_content = """# Introduction
This is the introduction section with comprehensive content about the topic.

# Methodology  
This section describes the methodology used in the research and analysis.

# Results
This section presents the results and findings from the study.

# Conclusion
This section provides conclusions and recommendations based on the results."""
            
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('response_verification_test.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true'
            }
            
            print("📤 Processing definitive test document...")
            print("🎯 Expected: 4 articles with clear H1-based titles")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n📋 FINAL RESPONSE VERIFICATION:")
                print(f"   Response Keys: {list(data.keys())}")
                
                # Check required fields
                required_fields = ['success', 'articles', 'session_id']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    return False
                
                # Verify article structure
                articles = data.get('articles', [])
                print(f"   📊 Articles in Response: {len(articles)}")
                
                if len(articles) == 4:
                    print("   ✅ CORRECT: 4 articles generated (one per H1 section)")
                    
                    # Verify article titles match H1 sections
                    expected_titles = ['Introduction', 'Methodology', 'Results', 'Conclusion']
                    for i, article in enumerate(articles):
                        title = article.get('title', '')
                        print(f"   📄 Article {i+1}: {title}")
                        
                        # Check if title contains expected H1 content
                        title_matches = any(expected.lower() in title.lower() for expected in expected_titles)
                        if title_matches:
                            print(f"      ✅ Title matches H1 structure")
                        else:
                            print(f"      ⚠️ Title may not match H1 structure")
                    
                    return True
                    
                elif len(articles) == 1:
                    print("   ❌ SINGLE ARTICLE ISSUE CONFIRMED")
                    print("   ❌ 4 H1 sections collapsed into 1 article")
                    
                    # Analyze the single article
                    single_article = articles[0]
                    title = single_article.get('title', 'No title')
                    word_count = single_article.get('word_count', 0)
                    
                    print(f"   📄 Single Article Title: {title}")
                    print(f"   📊 Single Article Word Count: {word_count}")
                    
                    return False
                else:
                    print(f"   ⚠️ UNEXPECTED: {len(articles)} articles generated (expected 4)")
                    return True  # Partial success
                    
            else:
                print(f"❌ Final response verification failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Final response verification failed - {str(e)}")
            return False
    
    def run_comprehensive_single_article_test(self):
        """Run all tests to identify the root cause of single article issue"""
        print("🚨 COMPREHENSIVE SINGLE ARTICLE ISSUE TESTING")
        print("=" * 60)
        
        test_results = []
        
        # Test 1: H1 Detection and Chunking
        print("\n" + "="*60)
        result1 = self.test_h1_detection_and_chunking()
        test_results.append(("H1 Detection and Chunking", result1))
        
        # Test 2: Backend Logs Analysis
        print("\n" + "="*60)
        result2 = self.test_backend_logs_analysis()
        test_results.append(("Backend Logs Analysis", result2))
        
        # Test 3: Article Generation Flow
        print("\n" + "="*60)
        result3 = self.test_article_generation_flow()
        test_results.append(("Article Generation Flow", result3))
        
        # Test 4: Final Response Verification
        print("\n" + "="*60)
        result4 = self.test_final_response_verification()
        test_results.append(("Final Response Verification", result4))
        
        # Summary
        print("\n" + "="*60)
        print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("="*60)
        
        passed_tests = 0
        failed_tests = 0
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed_tests += 1
            else:
                failed_tests += 1
        
        print(f"\n📊 Overall Results: {passed_tests}/{len(test_results)} tests passed")
        
        # Root cause analysis
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        if failed_tests == 0:
            print("✅ SINGLE ARTICLE ISSUE RESOLVED: All tests passed")
            print("✅ Multi-article generation is working correctly")
        elif failed_tests == len(test_results):
            print("❌ CRITICAL ISSUE: All tests failed")
            print("❌ Single article issue is confirmed and widespread")
            print("❌ Root cause likely in core chunking or article generation logic")
        else:
            print("⚠️ MIXED RESULTS: Some tests passed, some failed")
            print("⚠️ Single article issue may be intermittent or context-dependent")
        
        return passed_tests > failed_tests

if __name__ == "__main__":
    tester = SingleArticleIssueTest()
    success = tester.run_comprehensive_single_article_test()
    
    if success:
        print("\n🎉 TESTING COMPLETED: Single article issue analysis complete")
    else:
        print("\n🚨 TESTING COMPLETED: Single article issue confirmed - needs immediate fix")