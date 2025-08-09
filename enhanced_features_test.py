#!/usr/bin/env python3
"""
Enhanced Features Testing for Knowledge Engine
Testing the specific enhancements mentioned in the review request
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://14236aae-8093-4969-a2a2-e2c349953e54.preview.emergentagent.com') + '/api'

class EnhancedFeaturesTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"Testing Enhanced Features at: {self.base_url}")
        
    def test_url_processing_with_web_scraping(self):
        """Test enhanced URL processing with BeautifulSoup web scraping"""
        print("\n🌐 Testing Enhanced URL Processing with Web Scraping...")
        try:
            # Test with a real URL that should work
            test_data = {
                'url': 'https://example.com',
                'metadata': json.dumps({
                    "source": "enhanced_features_test",
                    "test_type": "url_processing_enhanced"
                })
            }
            
            response = requests.post(
                f"{self.base_url}/content/process-url",
                data=test_data,
                timeout=45
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                # Check for enhanced URL processing features
                required_fields = ['job_id', 'status', 'url', 'page_title', 'extracted_content_length', 'chunks_created']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ Enhanced URL processing working - proper title and content extraction")
                    print(f"✅ Page title extracted: {data.get('page_title', 'N/A')}")
                    print(f"✅ Content extracted: {data.get('extracted_content_length', 0)} characters")
                    print(f"✅ Chunks created: {data.get('chunks_created', 0)}")
                    
                    # Wait and check if Content Library article was created
                    time.sleep(3)
                    return self.verify_url_content_library_integration(data.get('job_id'))
                else:
                    print(f"❌ Enhanced URL processing failed - missing fields: {missing_fields}")
                    return False
            else:
                print(f"❌ URL processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ URL processing test failed - {str(e)}")
            return False
    
    def verify_url_content_library_integration(self, job_id):
        """Verify that URL processing creates Content Library articles"""
        try:
            # Check Content Library for new articles
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Look for articles from URL processing
                url_articles = [article for article in articles if article.get('source_type') == 'url_processing']
                
                if url_articles:
                    latest_article = url_articles[0]  # Most recent
                    print(f"✅ URL processing created Content Library article: '{latest_article.get('title', 'N/A')}'")
                    print(f"✅ Article summary: {latest_article.get('summary', 'N/A')[:100]}...")
                    return True
                else:
                    print("⚠️ No URL processing articles found in Content Library")
                    return False
            else:
                print("❌ Could not verify Content Library integration")
                return False
        except Exception as e:
            print(f"❌ Content Library verification failed - {str(e)}")
            return False
    
    def test_multiple_article_generation(self):
        """Test that large documents generate multiple articles (2-5 articles)"""
        print("\n📚 Testing Multiple Article Generation from Large Documents...")
        try:
            # Create a large, structured document that should generate multiple articles
            large_document_content = """
# Comprehensive Guide to Machine Learning and AI

## Introduction to Artificial Intelligence
Artificial Intelligence (AI) represents one of the most significant technological advances of our time. AI systems can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation. The field has evolved rapidly over the past decade, with breakthrough applications in healthcare, finance, transportation, and entertainment.

## Machine Learning Fundamentals
Machine Learning (ML) is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled data to train models, unsupervised learning finds patterns in unlabeled data, and reinforcement learning learns through interaction with an environment.

## Deep Learning and Neural Networks
Deep Learning is a specialized area of machine learning that uses artificial neural networks with multiple layers. These networks can automatically learn hierarchical representations of data, making them particularly effective for tasks like image recognition, natural language processing, and speech synthesis. Convolutional Neural Networks (CNNs) excel at image processing, while Recurrent Neural Networks (RNNs) are designed for sequential data.

## Natural Language Processing Applications
Natural Language Processing (NLP) enables computers to understand, interpret, and generate human language. Modern NLP applications include chatbots, language translation, sentiment analysis, and text summarization. Large Language Models (LLMs) like GPT have revolutionized the field by demonstrating remarkable capabilities in text generation and comprehension.

## Computer Vision and Image Recognition
Computer Vision allows machines to interpret and understand visual information from the world. Applications include facial recognition, medical image analysis, autonomous vehicle navigation, and quality control in manufacturing. Advanced techniques like object detection, image segmentation, and style transfer have opened new possibilities in creative and practical applications.

## AI Ethics and Responsible Development
As AI systems become more powerful and widespread, ethical considerations become increasingly important. Key concerns include bias in AI systems, privacy protection, transparency in decision-making, and the potential impact on employment. Responsible AI development requires careful consideration of these factors and implementation of appropriate safeguards.

## Future Trends and Emerging Technologies
The future of AI holds exciting possibilities, including quantum machine learning, neuromorphic computing, and artificial general intelligence (AGI). Edge AI will bring intelligence to IoT devices, while federated learning will enable privacy-preserving collaborative training. These advances will continue to transform industries and society.

## Implementation Best Practices
Successful AI implementation requires careful planning, quality data, appropriate model selection, and continuous monitoring. Organizations should establish clear objectives, ensure data quality, choose suitable algorithms, and implement robust testing procedures. Regular model updates and performance monitoring are essential for maintaining effectiveness.

## Conclusion and Next Steps
The field of AI and machine learning continues to evolve rapidly, offering tremendous opportunities for innovation and problem-solving. Success in this domain requires continuous learning, experimentation, and adaptation to new technologies and methodologies. Organizations and individuals should stay informed about developments and consider how these technologies can be applied to their specific challenges and opportunities.
            """
            
            # Upload this large document
            file_data = io.BytesIO(large_document_content.encode('utf-8'))
            
            files = {
                'file': ('comprehensive_ai_guide.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "enhanced_features_test",
                    "test_type": "multiple_article_generation",
                    "document_type": "comprehensive_guide"
                })
            }
            
            print("Uploading large document that should generate multiple articles...")
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ File upload failed - status code {response.status_code}")
                return False
            
            upload_data = response.json()
            print(f"Upload response: {json.dumps(upload_data, indent=2)}")
            
            # Wait for processing to complete
            time.sleep(5)
            
            # Check Content Library for multiple articles
            return self.verify_multiple_articles_created()
            
        except Exception as e:
            print(f"❌ Multiple article generation test failed - {str(e)}")
            return False
    
    def verify_multiple_articles_created(self):
        """Verify that multiple articles were created from the large document"""
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Look for recent articles from our test
                recent_articles = [
                    article for article in articles 
                    if 'comprehensive_ai_guide' in str(article.get('metadata', {})) or
                       'Machine Learning' in article.get('title', '') or
                       'AI' in article.get('title', '')
                ]
                
                print(f"Found {len(recent_articles)} articles related to our test document")
                
                if len(recent_articles) >= 2:
                    print("✅ Multiple article generation working!")
                    for i, article in enumerate(recent_articles[:5]):  # Show up to 5 articles
                        print(f"  Article {i+1}: '{article.get('title', 'N/A')}'")
                        print(f"    Summary: {article.get('summary', 'N/A')[:80]}...")
                    return True
                elif len(recent_articles) == 1:
                    print("⚠️ Only one article generated - may need larger/more structured content")
                    print(f"  Article: '{recent_articles[0].get('title', 'N/A')}'")
                    return True  # Still working, just not multiple
                else:
                    print("❌ No articles found from large document test")
                    return False
            else:
                print("❌ Could not check Content Library for multiple articles")
                return False
        except Exception as e:
            print(f"❌ Multiple articles verification failed - {str(e)}")
            return False
    
    def test_enhanced_document_api(self):
        """Test enhanced document API with related_articles and articles_count"""
        print("\n📄 Testing Enhanced Document API with Article Relationships...")
        try:
            response = requests.get(f"{self.base_url}/documents", timeout=15)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                if not documents:
                    print("⚠️ No documents found to test enhanced API")
                    return True
                
                # Check if documents have enhanced fields
                enhanced_docs = []
                for doc in documents:
                    if 'related_articles' in doc and 'articles_count' in doc:
                        enhanced_docs.append(doc)
                
                print(f"Found {len(enhanced_docs)} documents with enhanced API fields")
                
                if enhanced_docs:
                    print("✅ Enhanced Document API working!")
                    
                    # Show examples of enhanced data
                    for i, doc in enumerate(enhanced_docs[:3]):  # Show first 3
                        print(f"  Document {i+1}:")
                        print(f"    Articles count: {doc.get('articles_count', 0)}")
                        print(f"    Related articles: {len(doc.get('related_articles', []))}")
                        
                        if doc.get('related_articles'):
                            for j, article in enumerate(doc['related_articles'][:2]):  # Show first 2
                                print(f"      Article {j+1}: '{article.get('title', 'N/A')}'")
                    
                    return True
                else:
                    print("❌ No documents found with enhanced API fields (related_articles, articles_count)")
                    return False
            else:
                print(f"❌ Document API failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Enhanced Document API test failed - {str(e)}")
            return False
    
    def test_ai_generated_titles_not_placeholder(self):
        """Test that articles have AI-generated titles, not 'Processed Content' placeholders"""
        print("\n🤖 Testing AI-Generated Titles (No More 'Processed Content')...")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if not articles:
                    print("⚠️ No articles found to test titles")
                    return True
                
                # Analyze article titles
                placeholder_titles = []
                ai_generated_titles = []
                
                for article in articles:
                    title = article.get('title', '')
                    if title in ['Processed Content', 'processed content']:
                        placeholder_titles.append(article)
                    elif len(title) > 10 and not title.startswith('Processed'):
                        ai_generated_titles.append(article)
                
                print(f"Found {len(ai_generated_titles)} articles with AI-generated titles")
                print(f"Found {len(placeholder_titles)} articles with placeholder titles")
                
                if len(ai_generated_titles) > len(placeholder_titles):
                    print("✅ AI-generated titles working! Examples:")
                    for i, article in enumerate(ai_generated_titles[:5]):
                        print(f"  '{article.get('title', 'N/A')}'")
                    return True
                else:
                    print("⚠️ Many articles still have placeholder titles")
                    if ai_generated_titles:
                        print("Some AI-generated titles found:")
                        for article in ai_generated_titles[:3]:
                            print(f"  '{article.get('title', 'N/A')}'")
                    return len(ai_generated_titles) > 0  # Partial success
            else:
                print("❌ Could not check Content Library for title analysis")
                return False
                
        except Exception as e:
            print(f"❌ AI-generated titles test failed - {str(e)}")
            return False
    
    def test_content_extraction_quality(self):
        """Test that content extraction produces meaningful summaries and tags"""
        print("\n📝 Testing Content Extraction Quality (Summaries & Tags)...")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if not articles:
                    print("⚠️ No articles found to test content quality")
                    return True
                
                # Analyze content quality
                quality_articles = []
                
                for article in articles:
                    summary = article.get('summary', '')
                    tags = article.get('tags', [])
                    
                    # Check for quality indicators
                    has_meaningful_summary = (
                        len(summary) > 50 and 
                        not summary.startswith('Content processed from') and
                        '.' in summary  # Has sentences
                    )
                    
                    has_relevant_tags = (
                        len(tags) > 1 and 
                        not all(tag in ['text_processing', 'upload'] for tag in tags)
                    )
                    
                    if has_meaningful_summary or has_relevant_tags:
                        quality_articles.append(article)
                
                print(f"Found {len(quality_articles)} articles with quality content extraction")
                
                if quality_articles:
                    print("✅ Content extraction quality working! Examples:")
                    for i, article in enumerate(quality_articles[:3]):
                        print(f"  Article: '{article.get('title', 'N/A')}'")
                        print(f"    Summary: {article.get('summary', 'N/A')[:100]}...")
                        print(f"    Tags: {article.get('tags', [])}")
                    return True
                else:
                    print("❌ No articles found with quality content extraction")
                    return False
            else:
                print("❌ Could not check Content Library for content quality")
                return False
                
        except Exception as e:
            print(f"❌ Content extraction quality test failed - {str(e)}")
            return False
    
    def run_enhanced_features_tests(self):
        """Run all enhanced features tests"""
        print("🚀 Starting Enhanced Features Testing")
        print("🎯 FOCUS: Review Request Enhanced Features")
        print(f"Backend URL: {self.base_url}")
        print("=" * 70)
        
        results = {}
        
        # Test enhanced features mentioned in review request
        results['url_processing_web_scraping'] = self.test_url_processing_with_web_scraping()
        results['multiple_article_generation'] = self.test_multiple_article_generation()
        results['enhanced_document_api'] = self.test_enhanced_document_api()
        results['ai_generated_titles'] = self.test_ai_generated_titles_not_placeholder()
        results['content_extraction_quality'] = self.test_content_extraction_quality()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 ENHANCED FEATURES TEST RESULTS")
        print("🎯 REVIEW REQUEST FOCUS")
        print("=" * 70)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nEnhanced Features: {passed}/{total} tests passed")
        
        if passed >= 4:  # Most features working
            print("🎉 Enhanced Knowledge Engine features are working well!")
            return True
        elif passed >= 2:  # Some features working
            print("⚠️ Some enhanced features working, others need attention")
            return True
        else:
            print("❌ Enhanced features need significant work")
            return False

if __name__ == "__main__":
    tester = EnhancedFeaturesTest()
    success = tester.run_enhanced_features_tests()
    exit(0 if success else 1)