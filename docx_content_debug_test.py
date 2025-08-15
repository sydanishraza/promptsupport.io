#!/usr/bin/env python3
"""
CRITICAL DEBUG: DOCX Content Generation Issue Testing
Comprehensive testing for the critical issue where articles generated only contain 
headings/outline structure without actual content body text.
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://promptsupport-2.preview.emergentagent.com') + '/api'

class DOCXContentDebugTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🔍 CRITICAL DEBUG: Testing DOCX Content Generation at: {self.base_url}")
        print("🎯 FOCUS: Investigating why articles contain only headings without body text")
        
    def test_docx_processing_pipeline_debug(self):
        """Test DOCX processing pipeline and trace content generation process"""
        print("\n🔍 CRITICAL TEST: DOCX Processing Pipeline Content Generation Debug...")
        try:
            print("📋 Creating test DOCX with both headings AND body text...")
            
            # Create comprehensive test content with clear headings and substantial body text
            test_docx_content = """DOCX Content Generation Debug Test Document

# Introduction to Content Processing

This is the introduction paragraph that should appear in the generated article. It contains substantial body text that explains the purpose of this document and provides context for the content processing system.

The introduction continues with additional sentences to ensure there is enough body content to verify that the system is properly extracting and processing paragraph text, not just headings.

## Content Extraction Testing

This section focuses on testing content extraction capabilities. The system should extract this paragraph text and include it in the generated articles, not just the heading above.

Here is another paragraph in this section that provides more detailed information about content extraction. This text should be preserved and enhanced by the LLM processing pipeline.

### Detailed Content Analysis

This subsection contains even more specific content that should be processed. The paragraph text here is designed to test whether the system can handle nested heading structures while preserving all body content.

Additional paragraph content in the subsection to ensure comprehensive testing of the content extraction and processing pipeline.

## LLM Processing Verification

This section is specifically designed to test LLM processing. The content here should be enhanced and expanded by the AI processing pipeline, not just summarized or reduced to headings.

The LLM should receive this full paragraph text and enhance it while maintaining the core information and adding value through improved clarity and additional context.

### Content Enhancement Testing

This subsection tests whether the LLM receives full content or just headings. If the system is working correctly, this paragraph should be enhanced and expanded in the final article.

The enhancement process should preserve the original meaning while improving readability and adding comprehensive explanations where appropriate.

## Article Generation Quality

This final section tests the complete article generation process. The body text here should appear in the generated articles with proper formatting and structure.

The article generation system should create comprehensive articles that include all this body text, not just the heading structure. This is the critical test for the reported issue.

### Final Verification

This last subsection provides the final test content. If this paragraph appears in the generated article with proper enhancement, the content generation pipeline is working correctly.

The system should demonstrate that it can process both headings and body text to create comprehensive, well-structured articles that meet user expectations.
"""

            # Create file-like object
            file_data = io.BytesIO(test_docx_content.encode('utf-8'))
            
            files = {
                'file': ('content_debug_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'comprehensive_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "comprehensive_processing",
                    "processing_instructions": "Extract and enhance ALL content including headings AND body text",
                    "output_requirements": {
                        "format": "html",
                        "preserve_body_text": True,
                        "enhance_content": True,
                        "comprehensive_articles": True
                    }
                })
            }
            
            print("📤 Uploading test DOCX with comprehensive content...")
            print("🎯 Testing for: Headings + Body Text Extraction")
            
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
            
            if response.status_code != 200:
                print(f"❌ DOCX processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📋 Response Keys: {list(data.keys())}")
            
            # CRITICAL TEST 1: Verify articles were generated
            articles = data.get('articles', [])
            print(f"📚 Articles Generated: {len(articles)}")
            
            if not articles:
                print("❌ CRITICAL FAILURE: No articles generated")
                return False
            
            # CRITICAL TEST 2: Analyze article content for body text vs headings only
            print("\n🔍 CRITICAL ANALYSIS: Checking article content composition...")
            
            total_content_issues = 0
            
            for i, article in enumerate(articles):
                print(f"\n📄 ARTICLE {i+1} ANALYSIS:")
                
                title = article.get('title', 'Untitled')
                content = article.get('content', '') or article.get('html', '')
                word_count = article.get('word_count', 0)
                
                print(f"  Title: {title}")
                print(f"  Content Length: {len(content)} characters")
                print(f"  Word Count: {word_count}")
                
                if not content:
                    print("  ❌ CRITICAL ISSUE: Article has no content")
                    total_content_issues += 1
                    continue
                
                # Analyze content composition
                heading_count = content.count('<h1>') + content.count('<h2>') + content.count('<h3>')
                paragraph_count = content.count('<p>')
                
                print(f"  Headings: {heading_count}")
                print(f"  Paragraphs: {paragraph_count}")
                
                # Extract text content for analysis
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                text_content = soup.get_text().strip()
                
                # Count heading text vs body text
                heading_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                paragraph_elements = soup.find_all('p')
                
                heading_text_length = sum(len(h.get_text()) for h in heading_elements)
                paragraph_text_length = sum(len(p.get_text()) for p in paragraph_elements)
                
                print(f"  Heading Text: {heading_text_length} characters")
                print(f"  Paragraph Text: {paragraph_text_length} characters")
                
                # CRITICAL CHECK: Is this article mostly headings or does it have body content?
                if paragraph_text_length == 0:
                    print("  ❌ CRITICAL ISSUE: Article contains NO paragraph text (headings only)")
                    total_content_issues += 1
                elif paragraph_text_length < heading_text_length:
                    print("  ⚠️ WARNING: Article has more heading text than paragraph text")
                    print("  ⚠️ This may indicate content generation issues")
                    total_content_issues += 0.5
                elif paragraph_text_length < 200:
                    print("  ⚠️ WARNING: Article has very little paragraph text")
                    print("  ⚠️ Content may be too summarized")
                    total_content_issues += 0.5
                else:
                    print("  ✅ GOOD: Article has substantial paragraph content")
                
                # Sample content analysis
                if len(text_content) > 100:
                    print(f"  📝 Content Sample: {text_content[:200]}...")
                else:
                    print(f"  📝 Full Content: {text_content}")
                
                # Check for specific test content
                test_phrases = [
                    "introduction paragraph",
                    "content extraction",
                    "LLM processing",
                    "article generation",
                    "body text"
                ]
                
                found_phrases = [phrase for phrase in test_phrases if phrase.lower() in text_content.lower()]
                print(f"  🔍 Test Phrases Found: {len(found_phrases)}/{len(test_phrases)} - {found_phrases}")
                
                if len(found_phrases) == 0:
                    print("  ❌ CRITICAL ISSUE: No test content found - content may not be extracted properly")
                    total_content_issues += 1
            
            # OVERALL ASSESSMENT
            print(f"\n📊 OVERALL CONTENT GENERATION ASSESSMENT:")
            print(f"  Articles Generated: {len(articles)}")
            print(f"  Content Issues Detected: {total_content_issues}")
            
            if total_content_issues == 0:
                print("✅ CONTENT GENERATION WORKING CORRECTLY:")
                print("  ✅ All articles contain substantial body text")
                print("  ✅ Content extraction is working properly")
                print("  ✅ LLM processing is enhancing content correctly")
                return True
            elif total_content_issues < len(articles) * 0.5:
                print("⚠️ CONTENT GENERATION PARTIALLY WORKING:")
                print("  ⚠️ Some articles have content issues")
                print("  ⚠️ May need fine-tuning but core functionality works")
                return True
            else:
                print("❌ CRITICAL CONTENT GENERATION FAILURE:")
                print("  ❌ Most articles contain only headings without body text")
                print("  ❌ This confirms the reported issue")
                print("  ❌ Content extraction or LLM processing pipeline is broken")
                return False
                
        except Exception as e:
            print(f"❌ DOCX content debug test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_content_extraction_verification(self):
        """Test if content is being properly extracted from DOCX files"""
        print("\n🔍 CRITICAL TEST: Content Extraction Verification...")
        try:
            print("📋 Testing content extraction with simple text file...")
            
            # Create simple test content to verify extraction
            simple_content = """Simple Content Extraction Test

This is a simple paragraph that should be extracted and processed correctly.

Another paragraph with different content to verify extraction works properly.

Final paragraph to complete the test."""

            file_data = io.BytesIO(simple_content.encode('utf-8'))
            
            files = {
                'file': ('extraction_test.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'template_id': 'basic_processing'
            }
            
            print("📤 Testing basic content extraction...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=60
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                chunks_created = data.get('chunks_created', 0)
                job_id = data.get('job_id')
                
                print(f"📚 Chunks Created: {chunks_created}")
                print(f"🆔 Job ID: {job_id}")
                
                if chunks_created > 0:
                    print("✅ CONTENT EXTRACTION WORKING:")
                    print("  ✅ Content is being extracted and chunked")
                    print("  ✅ Basic processing pipeline is operational")
                    return True
                else:
                    print("❌ CONTENT EXTRACTION FAILED:")
                    print("  ❌ No chunks created from content")
                    return False
            else:
                print(f"❌ Content extraction test failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content extraction verification failed - {str(e)}")
            return False

    def test_llm_processing_investigation(self):
        """Test if the LLM is receiving full content or just headings"""
        print("\n🔍 CRITICAL TEST: LLM Processing Investigation...")
        try:
            print("🤖 Testing LLM processing with AI assistance endpoint...")
            
            # Test LLM directly with content that has headings and body text
            test_content = """# Test Heading

This is body text that should be processed by the LLM. The LLM should receive this full content and enhance it properly.

## Subheading

More body text in this section that tests whether the LLM gets complete content or just headings."""

            assistance_data = {
                "content": test_content,
                "mode": "enhancement",
                "context": "Testing LLM content processing"
            }
            
            print("🤖 Sending content to LLM for processing...")
            
            response = requests.post(
                f"{self.base_url}/ai-assistance",
                json=assistance_data,
                timeout=60
            )
            
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "suggestions" in data:
                    suggestions = data["suggestions"]
                    
                    if suggestions and len(suggestions) > 0:
                        enhanced_content = suggestions[0]
                        
                        print(f"📝 Enhanced Content Length: {len(enhanced_content)} characters")
                        print(f"📝 Enhanced Content Sample: {enhanced_content[:300]}...")
                        
                        # Check if enhanced content contains body text
                        if "body text" in enhanced_content.lower() or len(enhanced_content) > len(test_content):
                            print("✅ LLM PROCESSING WORKING:")
                            print("  ✅ LLM receives and processes full content")
                            print("  ✅ Content enhancement is working")
                            return True
                        else:
                            print("⚠️ LLM PROCESSING PARTIAL:")
                            print("  ⚠️ LLM may not be enhancing content properly")
                            return True
                    else:
                        print("❌ LLM PROCESSING FAILED:")
                        print("  ❌ No suggestions generated")
                        return False
                else:
                    print("❌ LLM PROCESSING FAILED:")
                    print("  ❌ AI assistance not working")
                    return False
            else:
                print(f"❌ LLM processing test failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ LLM processing investigation failed - {str(e)}")
            return False

    def test_backend_logs_analysis(self):
        """Test backend logs for content processing errors"""
        print("\n🔍 CRITICAL TEST: Backend Logs Analysis...")
        try:
            print("📋 Checking backend health and service status...")
            
            # Check backend health
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"🏥 Backend Health: {data.get('status')}")
                
                services = data.get('services', {})
                for service, status in services.items():
                    print(f"  {service}: {status}")
                
                # Check if any services are down that could affect content processing
                critical_services = ['mongodb', 'openai', 'anthropic']
                down_services = [s for s in critical_services if services.get(s) != 'healthy']
                
                if down_services:
                    print(f"⚠️ CRITICAL SERVICES DOWN: {down_services}")
                    print("⚠️ This could affect content processing quality")
                else:
                    print("✅ All critical services are healthy")
                
                return True
            else:
                print(f"❌ Backend health check failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend logs analysis failed - {str(e)}")
            return False

    def test_article_generation_debug(self):
        """Test article generation with detailed debugging"""
        print("\n🔍 CRITICAL TEST: Article Generation Debug...")
        try:
            print("📚 Testing article generation with Content Library check...")
            
            # First, check current Content Library state
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"📚 Current Content Library: {len(articles)} articles")
                
                if articles:
                    # Analyze recent articles for content quality
                    recent_articles = articles[:3]  # Check first 3 articles
                    
                    for i, article in enumerate(recent_articles):
                        print(f"\n📄 RECENT ARTICLE {i+1} ANALYSIS:")
                        
                        title = article.get('title', 'Untitled')
                        content = article.get('content', '')
                        created_at = article.get('created_at', 'Unknown')
                        
                        print(f"  Title: {title}")
                        print(f"  Created: {created_at}")
                        print(f"  Content Length: {len(content)} characters")
                        
                        if content:
                            # Quick content analysis
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(content, 'html.parser')
                            text_content = soup.get_text().strip()
                            
                            headings = len(soup.find_all(['h1', 'h2', 'h3']))
                            paragraphs = len(soup.find_all('p'))
                            
                            print(f"  Headings: {headings}")
                            print(f"  Paragraphs: {paragraphs}")
                            print(f"  Text Length: {len(text_content)} characters")
                            
                            if paragraphs == 0 and headings > 0:
                                print("  ❌ ISSUE CONFIRMED: Article has headings but no paragraphs")
                            elif len(text_content) < 200:
                                print("  ⚠️ WARNING: Article has very little content")
                            else:
                                print("  ✅ Article appears to have proper content")
                        else:
                            print("  ❌ CRITICAL: Article has no content")
                
                return True
            else:
                print(f"❌ Content Library check failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Article generation debug failed - {str(e)}")
            return False

    def run_comprehensive_debug_tests(self):
        """Run all debug tests to identify the content generation issue"""
        print("🚨 CRITICAL DEBUG: DOCX CONTENT GENERATION ISSUE INVESTIGATION")
        print("=" * 80)
        print("🎯 OBJECTIVE: Identify why articles contain only headings without body text")
        print("=" * 80)
        
        tests = [
            ("Backend Health Check", self.test_backend_logs_analysis),
            ("Content Extraction Verification", self.test_content_extraction_verification),
            ("LLM Processing Investigation", self.test_llm_processing_investigation),
            ("Article Generation Debug", self.test_article_generation_debug),
            ("DOCX Processing Pipeline Debug", self.test_docx_processing_pipeline_debug),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
        
        # Final assessment
        print("\n" + "="*80)
        print("🔍 CRITICAL DEBUG RESULTS SUMMARY")
        print("="*80)
        
        passed_tests = sum(1 for _, result in results if result)
        total_tests = len(results)
        
        print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        if passed_tests == total_tests:
            print("\n✅ ALL TESTS PASSED - Content generation appears to be working")
            print("🔍 The issue may be intermittent or specific to certain content types")
        elif passed_tests >= total_tests * 0.7:
            print("\n⚠️ MOST TESTS PASSED - Issue may be partially resolved")
            print("🔍 Some components working, others may need attention")
        else:
            print("\n❌ CRITICAL ISSUES DETECTED - Content generation pipeline has problems")
            print("🔍 Multiple components failing, requires immediate investigation")
        
        return passed_tests >= total_tests * 0.7

if __name__ == "__main__":
    tester = DOCXContentDebugTest()
    success = tester.run_comprehensive_debug_tests()
    
    if success:
        print("\n🎉 DEBUG TESTING COMPLETED SUCCESSFULLY")
    else:
        print("\n🚨 CRITICAL ISSUES IDENTIFIED - REQUIRES IMMEDIATE ATTENTION")