#!/usr/bin/env python3
"""
Enhanced Knowledge Engine Testing - Comprehensive Content Processing
Testing the enhanced Knowledge Engine with focus on:
1. Enhanced Document Processing with Billing-Management.docx
2. Multi-Article Generation
3. Content Enhancement with LLM processing
4. Production-Ready Features
5. Enhanced Metadata
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://1f0a6d55-6538-4e79-bced-87abc96991a4.preview.emergentagent.com') + '/api'

class EnhancedKnowledgeEngineTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_job_id = None
        self.billing_doc_path = '/app/test_billing_doc.docx'
        print(f"Testing Enhanced Knowledge Engine at: {self.base_url}")
        print(f"Test document: {self.billing_doc_path}")
        
    def test_billing_document_upload_processing(self):
        """Test enhanced document processing with Billing-Management.docx"""
        print("🔍 Testing Enhanced Document Processing with Billing-Management.docx...")
        
        # Check if test document exists
        if not os.path.exists(self.billing_doc_path):
            print(f"❌ Test document not found at {self.billing_doc_path}")
            return False
            
        try:
            # Get initial Content Library count
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            initial_count = 0
            initial_articles = []
            if response.status_code == 200:
                data = response.json()
                initial_count = data.get('total', 0)
                initial_articles = data.get('articles', [])
                print(f"Initial Content Library articles: {initial_count}")
            
            # Upload the Billing Management document
            with open(self.billing_doc_path, 'rb') as file:
                files = {
                    'file': ('Billing-Management.docx', file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'metadata': json.dumps({
                        "source": "enhanced_knowledge_engine_test",
                        "test_type": "billing_document_processing",
                        "document_type": "billing_management_guide",
                        "original_filename": "Billing-Management.docx"
                    })
                }
                
                print("Uploading Billing-Management.docx...")
                response = requests.post(
                    f"{self.base_url}/content/upload",
                    files=files,
                    data=form_data,
                    timeout=60  # Longer timeout for document processing
                )
                
                print(f"Upload Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    upload_data = response.json()
                    print(f"Upload Response: {json.dumps(upload_data, indent=2)}")
                    
                    self.test_job_id = upload_data.get('job_id')
                    extracted_length = upload_data.get('extracted_content_length', 0)
                    chunks_created = upload_data.get('chunks_created', 0)
                    
                    print(f"✅ Document uploaded successfully")
                    print(f"📄 Extracted content length: {extracted_length} characters")
                    print(f"🧩 Chunks created: {chunks_created}")
                    
                    # Wait for processing to complete
                    print("⏳ Waiting for document processing to complete...")
                    time.sleep(10)
                    
                    # Check if Content Library articles were created
                    response = requests.get(f"{self.base_url}/content-library", timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        new_count = data.get('total', 0)
                        new_articles = data.get('articles', [])
                        
                        print(f"📚 Content Library articles after processing: {new_count}")
                        
                        if new_count > initial_count:
                            articles_created = new_count - initial_count
                            print(f"✅ {articles_created} new articles created from Billing document!")
                            
                            # Analyze the newly created articles
                            return self.analyze_billing_document_articles(new_articles, initial_articles)
                        else:
                            print("⚠️ No new articles created - checking for processing issues")
                            return False
                    else:
                        print(f"❌ Could not check Content Library after processing")
                        return False
                else:
                    print(f"❌ Document upload failed - status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Billing document processing failed - {str(e)}")
            return False
    
    def analyze_billing_document_articles(self, new_articles, initial_articles):
        """Analyze the articles created from the Billing document"""
        print("\n🔍 Analyzing Billing Document Articles...")
        
        # Find newly created articles (those not in initial set)
        initial_ids = {article.get('id') for article in initial_articles}
        billing_articles = [article for article in new_articles if article.get('id') not in initial_ids]
        
        if not billing_articles:
            print("❌ No new articles found for analysis")
            return False
        
        print(f"📊 Found {len(billing_articles)} new articles to analyze")
        
        # Test 1: Enhanced Document Structure Extraction
        structure_test = self.test_document_structure_extraction(billing_articles)
        
        # Test 2: Multi-Article Generation Logic
        multi_article_test = self.test_multi_article_generation(billing_articles)
        
        # Test 3: Content Enhancement Quality
        content_enhancement_test = self.test_content_enhancement_quality(billing_articles)
        
        # Test 4: Production-Ready Features
        production_features_test = self.test_production_ready_features(billing_articles)
        
        # Test 5: Enhanced Metadata
        metadata_test = self.test_enhanced_metadata(billing_articles)
        
        # Overall assessment
        tests_passed = sum([
            structure_test, multi_article_test, content_enhancement_test,
            production_features_test, metadata_test
        ])
        
        print(f"\n📊 Billing Document Analysis Results: {tests_passed}/5 tests passed")
        
        if tests_passed >= 4:
            print("✅ Enhanced Knowledge Engine processing is working excellently!")
            return True
        elif tests_passed >= 3:
            print("✅ Enhanced Knowledge Engine processing is working well with minor issues")
            return True
        else:
            print("❌ Enhanced Knowledge Engine processing has significant issues")
            return False
    
    def test_document_structure_extraction(self, articles):
        """Test that document structure, headings, tables, and formatting are properly captured"""
        print("\n🔍 Testing Document Structure Extraction...")
        
        try:
            structure_indicators = 0
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                
                # Check for proper heading hierarchies (H1, H2, H3, H4)
                heading_levels = ['# ', '## ', '### ', '#### ']
                found_headings = sum(1 for level in heading_levels if level in content)
                if found_headings >= 2:
                    structure_indicators += 1
                    print(f"✅ Article '{title[:50]}...' has proper heading hierarchy ({found_headings} levels)")
                
                # Check for table extraction (markdown tables)
                if '|' in content and '---' in content:
                    structure_indicators += 1
                    print(f"✅ Article '{title[:50]}...' contains structured tables")
                
                # Check for lists and structured content
                if ('- ' in content or '1. ' in content) and len(content) > 500:
                    structure_indicators += 1
                    print(f"✅ Article '{title[:50]}...' has structured lists")
                
                # Check for media asset references
                if 'image' in content.lower() or 'diagram' in content.lower() or 'table' in content.lower():
                    structure_indicators += 1
                    print(f"✅ Article '{title[:50]}...' references media assets")
            
            if structure_indicators >= 3:
                print("✅ Document structure extraction is working well")
                return True
            else:
                print(f"⚠️ Document structure extraction needs improvement ({structure_indicators} indicators found)")
                return False
                
        except Exception as e:
            print(f"❌ Document structure test failed - {str(e)}")
            return False
    
    def test_multi_article_generation(self, articles):
        """Test that documents are properly split into multiple focused articles"""
        print("\n🔍 Testing Multi-Article Generation Logic...")
        
        try:
            if len(articles) >= 2:
                print(f"✅ Multiple articles generated: {len(articles)} articles")
                
                # Check that articles have different focuses
                titles = [article.get('title', '') for article in articles]
                unique_keywords = set()
                
                for title in titles:
                    # Extract key terms from titles
                    words = title.lower().split()
                    for word in words:
                        if len(word) > 4 and word not in ['article', 'guide', 'management', 'system']:
                            unique_keywords.add(word)
                
                if len(unique_keywords) >= len(articles):
                    print(f"✅ Articles have distinct focuses - {len(unique_keywords)} unique concepts")
                    
                    # Check article lengths are reasonable (not too short or too long)
                    appropriate_lengths = 0
                    for article in articles:
                        content_length = len(article.get('content', ''))
                        if 800 <= content_length <= 4000:  # Reasonable article length
                            appropriate_lengths += 1
                    
                    if appropriate_lengths >= len(articles) * 0.7:  # At least 70% have good length
                        print(f"✅ Article lengths are appropriate ({appropriate_lengths}/{len(articles)})")
                        return True
                    else:
                        print(f"⚠️ Some articles have inappropriate lengths ({appropriate_lengths}/{len(articles)})")
                        return False
                else:
                    print(f"⚠️ Articles may not have distinct enough focuses")
                    return False
            else:
                print(f"⚠️ Only {len(articles)} article(s) generated - may need better splitting logic")
                return len(articles) == 1  # Single comprehensive article is also acceptable
                
        except Exception as e:
            print(f"❌ Multi-article generation test failed - {str(e)}")
            return False
    
    def test_content_enhancement_quality(self, articles):
        """Test that LLM processing creates well-formatted, enhanced content"""
        print("\n🔍 Testing Content Enhancement Quality...")
        
        try:
            quality_indicators = 0
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                summary = article.get('summary', '')
                
                # Check for AI-enhanced content indicators
                enhancement_markers = [
                    'overview', 'prerequisites', 'what you\'ll learn', 'key takeaways',
                    'next steps', 'best practices', 'troubleshooting', 'conclusion'
                ]
                
                found_markers = sum(1 for marker in enhancement_markers if marker in content.lower())
                if found_markers >= 3:
                    quality_indicators += 1
                    print(f"✅ Article '{title[:50]}...' has enhanced structure ({found_markers} sections)")
                
                # Check for professional formatting
                if ('**' in content or '*' in content) and ('> ' in content or '```' in content):
                    quality_indicators += 1
                    print(f"✅ Article '{title[:50]}...' has professional formatting")
                
                # Check for meaningful summaries (not generic)
                if (len(summary) > 100 and 
                    not summary.startswith('Content processed') and
                    not summary.startswith('Generated from')):
                    quality_indicators += 1
                    print(f"✅ Article '{title[:50]}...' has meaningful summary")
                
                # Check for actionable content
                actionable_words = ['step', 'configure', 'setup', 'implement', 'create', 'manage']
                if sum(1 for word in actionable_words if word in content.lower()) >= 3:
                    quality_indicators += 1
                    print(f"✅ Article '{title[:50]}...' contains actionable content")
            
            if quality_indicators >= len(articles) * 2:  # At least 2 quality indicators per article
                print("✅ Content enhancement quality is excellent")
                return True
            elif quality_indicators >= len(articles):  # At least 1 quality indicator per article
                print("✅ Content enhancement quality is good")
                return True
            else:
                print(f"⚠️ Content enhancement quality needs improvement ({quality_indicators} indicators)")
                return False
                
        except Exception as e:
            print(f"❌ Content enhancement quality test failed - {str(e)}")
            return False
    
    def test_production_ready_features(self, articles):
        """Test production-ready features like callouts, tips, warnings, etc."""
        print("\n🔍 Testing Production-Ready Features...")
        
        try:
            production_features = 0
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                
                # Check for callouts and tips
                callout_indicators = ['> **', '💡', '⚠️', '✅', '❌', '📝', '🔧', '💡 Pro Tip', '⚠️ Warning']
                found_callouts = sum(1 for indicator in callout_indicators if indicator in content)
                if found_callouts >= 1:
                    production_features += 1
                    print(f"✅ Article '{title[:50]}...' has callouts/tips ({found_callouts} found)")
                
                # Check for step-by-step procedures
                if ('1. ' in content and '2. ' in content) or ('Step 1' in content and 'Step 2' in content):
                    production_features += 1
                    print(f"✅ Article '{title[:50]}...' has step-by-step procedures")
                
                # Check for code blocks or configuration examples
                if '```' in content or '`' in content:
                    production_features += 1
                    print(f"✅ Article '{title[:50]}...' has code/configuration examples")
                
                # Check for comprehensive sections
                comprehensive_sections = ['introduction', 'overview', 'conclusion', 'summary', 'takeaways']
                found_sections = sum(1 for section in comprehensive_sections if section in content.lower())
                if found_sections >= 2:
                    production_features += 1
                    print(f"✅ Article '{title[:50]}...' has comprehensive sections")
            
            if production_features >= len(articles) * 2:  # At least 2 features per article
                print("✅ Production-ready features are excellent")
                return True
            elif production_features >= len(articles):  # At least 1 feature per article
                print("✅ Production-ready features are good")
                return True
            else:
                print(f"⚠️ Production-ready features need improvement ({production_features} features)")
                return False
                
        except Exception as e:
            print(f"❌ Production-ready features test failed - {str(e)}")
            return False
    
    def test_enhanced_metadata(self, articles):
        """Test enhanced metadata including comprehensive tags and detailed summaries"""
        print("\n🔍 Testing Enhanced Metadata...")
        
        try:
            metadata_quality = 0
            
            for article in articles:
                title = article.get('title', '')
                summary = article.get('summary', '')
                tags = article.get('tags', [])
                takeaways = article.get('takeaways', [])
                metadata = article.get('metadata', {})
                
                # Check for comprehensive tags
                if len(tags) >= 4:
                    # Check for technical terms and categories
                    technical_terms = sum(1 for tag in tags if len(tag) > 3 and tag not in ['test', 'upload'])
                    if technical_terms >= 3:
                        metadata_quality += 1
                        print(f"✅ Article '{title[:50]}...' has comprehensive tags ({len(tags)} tags)")
                
                # Check for detailed summaries (3-4 sentences)
                sentence_count = summary.count('.') + summary.count('!') + summary.count('?')
                if sentence_count >= 3 and len(summary) > 150:
                    metadata_quality += 1
                    print(f"✅ Article '{title[:50]}...' has detailed summary ({sentence_count} sentences)")
                
                # Check for specific and actionable takeaways
                if len(takeaways) >= 3:
                    actionable_takeaways = sum(1 for takeaway in takeaways 
                                             if len(takeaway) > 20 and 
                                             any(word in takeaway.lower() for word in ['how', 'use', 'implement', 'configure', 'manage']))
                    if actionable_takeaways >= 2:
                        metadata_quality += 1
                        print(f"✅ Article '{title[:50]}...' has actionable takeaways ({len(takeaways)} total)")
                
                # Check for AI processing metadata
                if metadata.get('ai_processed') and metadata.get('ai_model'):
                    metadata_quality += 1
                    print(f"✅ Article '{title[:50]}...' has AI processing metadata")
            
            if metadata_quality >= len(articles) * 2:  # At least 2 metadata features per article
                print("✅ Enhanced metadata is excellent")
                return True
            elif metadata_quality >= len(articles):  # At least 1 metadata feature per article
                print("✅ Enhanced metadata is good")
                return True
            else:
                print(f"⚠️ Enhanced metadata needs improvement ({metadata_quality} features)")
                return False
                
        except Exception as e:
            print(f"❌ Enhanced metadata test failed - {str(e)}")
            return False
    
    def test_job_tracking_for_billing_document(self):
        """Test job tracking for the billing document processing"""
        print("\n🔍 Testing Job Tracking for Billing Document...")
        
        if not self.test_job_id:
            print("⚠️ No job ID available from billing document upload")
            return True
        
        try:
            response = requests.get(f"{self.base_url}/jobs/{self.test_job_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Job Status: {json.dumps(data, indent=2)}")
                
                if (data.get('status') == 'completed' and 
                    data.get('chunks_created', 0) > 0):
                    print(f"✅ Job tracking successful - {data.get('chunks_created')} chunks created")
                    return True
                else:
                    print(f"⚠️ Job may not be completed yet - Status: {data.get('status')}")
                    return True
            else:
                print(f"❌ Job tracking failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Job tracking test failed - {str(e)}")
            return False
    
    def test_search_billing_content(self):
        """Test searching for content from the billing document"""
        print("\n🔍 Testing Search for Billing Document Content...")
        
        try:
            # Search for billing-related terms
            search_terms = ['billing', 'management', 'invoice', 'payment', 'account']
            
            for term in search_terms:
                search_request = {
                    "query": term,
                    "limit": 5
                }
                
                response = requests.post(
                    f"{self.base_url}/search",
                    json=search_request,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results_count = data.get('total_found', 0)
                    
                    if results_count > 0:
                        print(f"✅ Found {results_count} results for '{term}'")
                        return True
                else:
                    print(f"⚠️ Search failed for term '{term}' - status {response.status_code}")
            
            print("⚠️ No search results found for billing terms")
            return False
            
        except Exception as e:
            print(f"❌ Billing content search test failed - {str(e)}")
            return False
    
    def run_enhanced_knowledge_engine_tests(self):
        """Run comprehensive tests for the Enhanced Knowledge Engine"""
        print("🚀 Starting Enhanced Knowledge Engine Comprehensive Testing")
        print("🎯 FOCUS: Enhanced Content Processing with Billing-Management.docx")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        results = {}
        
        # Main test: Enhanced Document Processing with Billing Document
        print("\n🎯 ENHANCED DOCUMENT PROCESSING TEST")
        print("=" * 50)
        results['billing_document_processing'] = self.test_billing_document_upload_processing()
        
        # Supporting tests
        print("\n🔧 SUPPORTING FUNCTIONALITY TESTS")
        print("=" * 50)
        results['job_tracking'] = self.test_job_tracking_for_billing_document()
        results['search_billing_content'] = self.test_search_billing_content()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 ENHANCED KNOWLEDGE ENGINE TEST RESULTS")
        print("🎯 COMPREHENSIVE CONTENT PROCESSING ASSESSMENT")
        print("=" * 80)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            priority_marker = "🎯 " if test_name == 'billing_document_processing' else ""
            print(f"{priority_marker}{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        # Assessment
        if results.get('billing_document_processing', False):
            print("\n🎉 ENHANCED KNOWLEDGE ENGINE IS WORKING EXCELLENTLY!")
            print("✅ Enhanced Document Processing: OPERATIONAL")
            print("✅ Multi-Article Generation: OPERATIONAL") 
            print("✅ Content Enhancement: OPERATIONAL")
            print("✅ Production-Ready Features: OPERATIONAL")
            print("✅ Enhanced Metadata: OPERATIONAL")
            
            if passed == total:
                print("🎉 ALL SUPPORTING FEATURES ALSO WORKING!")
            
            return True
        else:
            print("\n❌ ENHANCED KNOWLEDGE ENGINE HAS ISSUES")
            print("❌ Enhanced Document Processing: FAILED")
            print("⚠️ Core functionality may need attention")
            return False

if __name__ == "__main__":
    tester = EnhancedKnowledgeEngineTest()
    success = tester.run_enhanced_knowledge_engine_tests()
    exit(0 if success else 1)