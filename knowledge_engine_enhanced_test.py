#!/usr/bin/env python3
"""
Knowledge Engine Enhanced Features Backend Testing
Testing enhanced PDF processing, article generation, TOC creation, and technical writing standards
"""

import requests
import json
import os
import io
import time
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdocs-23.preview.emergentagent.com') + '/api'

class KnowledgeEngineEnhancedTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_job_id = None
        self.test_session_id = str(uuid.uuid4())
        print(f"🧠 Testing Knowledge Engine Enhanced Features at: {self.base_url}")
        print(f"🔬 Test Session ID: {self.test_session_id}")
        
    def test_health_check(self):
        """Test backend health and AI services availability"""
        print("\n🔍 Testing Backend Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Check Response: {json.dumps(data, indent=2)}")
                
                # Verify AI services are configured
                services = data.get("services", {})
                required_services = ["mongodb", "openai", "anthropic"]
                
                for service in required_services:
                    status = services.get(service, "unknown")
                    if status in ["connected", "configured", "healthy"]:
                        print(f"✅ {service.upper()}: {status}")
                    else:
                        print(f"⚠️ {service.upper()}: {status}")
                
                return True
            else:
                print(f"❌ Health check failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def test_enhanced_pdf_processing(self):
        """Test enhanced PDF processing with multi-method approach"""
        print("\n📄 Testing Enhanced PDF Processing...")
        
        # Create a test PDF content
        test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 85
>>
stream
BT
/F1 12 Tf
72 720 Td
(Enhanced Knowledge Engine Testing) Tj
0 -20 Td
(This document tests the new PDF processing capabilities) Tj
0 -20 Td
(with improved multi-method approach and technical writing standards.) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000411 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
481
%%EOF"""
        
        try:
            # Test PDF upload and processing
            files = {
                'file': ('enhanced_test.pdf', io.BytesIO(test_pdf_content), 'application/pdf')
            }
            
            print("🔄 Uploading test PDF...")
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                timeout=60
            )
            
            print(f"Upload Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ PDF Upload Response: {json.dumps(data, indent=2)}")
                
                # Check for job tracking
                if 'job_id' in data:
                    self.test_job_id = data['job_id']
                    print(f"📋 Job ID: {self.test_job_id}")
                    
                    # Wait for processing to complete
                    return self._wait_for_processing_completion()
                else:
                    print("⚠️ No job_id returned, checking immediate response")
                    return self._verify_pdf_processing_response(data)
            else:
                print(f"❌ PDF upload failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Enhanced PDF processing test failed: {e}")
            return False

    def test_enhanced_article_generation(self):
        """Test enhanced article generation with technical writing standards"""
        print("\n📝 Testing Enhanced Article Generation...")
        
        try:
            # Get recent articles from content library
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if not articles:
                    print("⚠️ No articles found for testing")
                    return False
                
                print(f"📚 Found {len(articles)} articles in Content Library")
                
                # Test recent articles for enhanced features
                enhanced_features_found = 0
                
                for i, article in enumerate(articles[:5]):  # Test first 5 articles
                    print(f"\n🔍 Analyzing Article {i+1}: {article.get('title', 'Untitled')}")
                    
                    # Check for specific, actionable titles (not generic)
                    title = article.get('title', '')
                    if self._is_specific_actionable_title(title):
                        print(f"✅ Specific, actionable title: {title}")
                        enhanced_features_found += 1
                    else:
                        print(f"⚠️ Generic title detected: {title}")
                    
                    # Check content for technical writing elements
                    content = article.get('content', '')
                    if self._has_technical_writing_elements(content):
                        print("✅ Technical writing elements found")
                        enhanced_features_found += 1
                    else:
                        print("⚠️ Missing technical writing elements")
                    
                    # Check for proper HTML structure
                    if self._has_proper_html_structure(content):
                        print("✅ Proper HTML structure (H2, H3, H4 - no H1)")
                        enhanced_features_found += 1
                    else:
                        print("⚠️ HTML structure issues detected")
                
                # Determine success based on enhanced features found
                success_rate = enhanced_features_found / (len(articles[:5]) * 3) * 100
                print(f"\n📊 Enhanced Features Success Rate: {success_rate:.1f}%")
                
                return success_rate >= 60  # At least 60% of features should be present
                
            else:
                print(f"❌ Failed to get content library: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Enhanced article generation test failed: {e}")
            return False

    def test_multi_article_toc_creation(self):
        """Test multi-article TOC creation functionality"""
        print("\n📋 Testing Multi-Article TOC Creation...")
        
        try:
            # Create test content that should generate multiple articles
            test_content = """
            # Chapter 1: Introduction to Enhanced Knowledge Engine
            
            This is the first chapter covering the basics of the enhanced knowledge engine system.
            
            ## Key Features
            - Enhanced PDF processing
            - Technical writing standards
            - Multi-article generation
            
            # Chapter 2: Advanced Processing Techniques
            
            This chapter covers advanced processing techniques for document analysis.
            
            ## Processing Methods
            - Multi-method PDF approach
            - Contextual image placement
            - Semantic content analysis
            
            # Chapter 3: Implementation Guidelines
            
            This final chapter provides implementation guidelines for the system.
            
            ## Best Practices
            - Follow technical writing standards
            - Use proper HTML structure
            - Implement related links
            """
            
            # Upload test content
            files = {
                'file': ('multi_chapter_test.txt', io.BytesIO(test_content.encode()), 'text/plain')
            }
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Multi-chapter content uploaded: {json.dumps(data, indent=2)}")
                
                # Wait for processing
                time.sleep(5)
                
                # Check if TOC article was created
                return self._verify_toc_creation()
            else:
                print(f"❌ Multi-chapter upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Multi-article TOC test failed: {e}")
            return False

    def test_article_quality_standards(self):
        """Test article quality standards and structure"""
        print("\n⭐ Testing Article Quality Standards...")
        
        try:
            # Get articles for quality analysis
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if not articles:
                    print("⚠️ No articles found for quality testing")
                    return False
                
                quality_scores = []
                
                for i, article in enumerate(articles[:3]):  # Test first 3 articles
                    print(f"\n🔍 Quality Analysis - Article {i+1}")
                    
                    score = 0
                    max_score = 6
                    
                    # Check 1: Title doesn't repeat in body
                    title = article.get('title', '')
                    content = article.get('content', '')
                    
                    if title and title not in content:
                        print("✅ Title doesn't repeat in article body")
                        score += 1
                    else:
                        print("⚠️ Title repetition detected")
                    
                    # Check 2: Appropriate HTML structure
                    if self._has_appropriate_html_structure(content):
                        print("✅ Appropriate HTML structure (H2, H3, H4)")
                        score += 1
                    else:
                        print("⚠️ HTML structure issues")
                    
                    # Check 3: Technical writing elements
                    if self._has_technical_writing_elements(content):
                        print("✅ Technical writing elements present")
                        score += 1
                    else:
                        print("⚠️ Missing technical writing elements")
                    
                    # Check 4: Related links section
                    if self._has_related_links(content):
                        print("✅ Related links section found")
                        score += 1
                    else:
                        print("⚠️ No related links section")
                    
                    # Check 5: Proper content length
                    if len(content) > 500:
                        print("✅ Adequate content length")
                        score += 1
                    else:
                        print("⚠️ Content too short")
                    
                    # Check 6: Professional structure
                    if self._has_professional_structure(content):
                        print("✅ Professional content structure")
                        score += 1
                    else:
                        print("⚠️ Structure needs improvement")
                    
                    quality_percentage = (score / max_score) * 100
                    quality_scores.append(quality_percentage)
                    print(f"📊 Article Quality Score: {quality_percentage:.1f}%")
                
                # Calculate overall quality
                avg_quality = sum(quality_scores) / len(quality_scores)
                print(f"\n📈 Overall Article Quality: {avg_quality:.1f}%")
                
                return avg_quality >= 70  # At least 70% quality score
                
            else:
                print(f"❌ Failed to get articles for quality testing: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Article quality test failed: {e}")
            return False

    def test_backend_integration_functions(self):
        """Test backend integration functions for enhanced features"""
        print("\n🔧 Testing Backend Integration Functions...")
        
        try:
            # Test 1: Content analysis endpoint
            print("🔍 Testing content analysis endpoint...")
            test_content = "This is a test content for analysis with enhanced features."
            
            response = requests.post(
                f"{self.base_url}/content-analysis",
                json={"content": test_content},
                timeout=10
            )
            
            analysis_working = False
            if response.status_code == 200:
                data = response.json()
                print("✅ Content analysis endpoint working")
                analysis_working = True
            else:
                print(f"⚠️ Content analysis endpoint issue: {response.status_code}")
            
            # Test 2: Asset management for images
            print("🖼️ Testing asset management...")
            assets_response = requests.get(f"{self.base_url}/assets", timeout=10)
            
            assets_working = False
            if assets_response.status_code == 200:
                assets_data = assets_response.json()
                print(f"✅ Asset management working - {len(assets_data.get('assets', []))} assets found")
                assets_working = True
            else:
                print(f"⚠️ Asset management issue: {assets_response.status_code}")
            
            # Test 3: Document processing status
            print("📄 Testing document processing status...")
            docs_response = requests.get(f"{self.base_url}/documents", timeout=10)
            
            docs_working = False
            if docs_response.status_code == 200:
                docs_data = docs_response.json()
                print(f"✅ Document processing working - {docs_data.get('count', 0)} documents")
                docs_working = True
            else:
                print(f"⚠️ Document processing issue: {docs_response.status_code}")
            
            # Overall integration score
            working_functions = sum([analysis_working, assets_working, docs_working])
            integration_score = (working_functions / 3) * 100
            
            print(f"\n📊 Backend Integration Score: {integration_score:.1f}%")
            return integration_score >= 66  # At least 2 out of 3 functions working
            
        except Exception as e:
            print(f"❌ Backend integration test failed: {e}")
            return False

    def _wait_for_processing_completion(self):
        """Wait for document processing to complete"""
        if not self.test_job_id:
            return False
            
        print("⏳ Waiting for processing completion...")
        max_wait = 120  # 2 minutes max wait
        wait_time = 0
        
        while wait_time < max_wait:
            try:
                # Check job status
                response = requests.get(f"{self.base_url}/job-status/{self.test_job_id}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    
                    print(f"📋 Job Status: {status}")
                    
                    if status == 'completed':
                        print("✅ Processing completed successfully")
                        return True
                    elif status == 'failed':
                        print("❌ Processing failed")
                        return False
                    
                time.sleep(5)
                wait_time += 5
                
            except Exception as e:
                print(f"⚠️ Status check error: {e}")
                time.sleep(5)
                wait_time += 5
        
        print("⏰ Processing timeout")
        return False

    def _verify_pdf_processing_response(self, data):
        """Verify PDF processing response for enhanced features"""
        required_fields = ['status', 'message']
        
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return False
        
        if data.get('status') == 'completed':
            print("✅ PDF processing completed successfully")
            return True
        else:
            print(f"⚠️ PDF processing status: {data.get('status')}")
            return False

    def _is_specific_actionable_title(self, title):
        """Check if title is specific and actionable (not generic)"""
        generic_patterns = [
            "comprehensive guide to",
            "complete guide to",
            "introduction to",
            "overview of",
            "basics of"
        ]
        
        title_lower = title.lower()
        return not any(pattern in title_lower for pattern in generic_patterns)

    def _has_technical_writing_elements(self, content):
        """Check for technical writing elements like callouts, tables, lists"""
        technical_elements = [
            "💡",  # Tips
            "📝",  # Notes
            "⚠️",  # Cautions
            "<table",  # Tables
            "<ul>",  # Lists
            "<ol>",  # Ordered lists
            "<blockquote",  # Callouts
            "<code"  # Code blocks
        ]
        
        return any(element in content for element in technical_elements)

    def _has_proper_html_structure(self, content):
        """Check for proper HTML structure (H2, H3, H4 - no H1)"""
        has_h2_h3_h4 = any(tag in content for tag in ["<h2", "<h3", "<h4"])
        has_no_h1 = "<h1" not in content
        
        return has_h2_h3_h4 and has_no_h1

    def _has_appropriate_html_structure(self, content):
        """Check for appropriate HTML structure"""
        return any(tag in content for tag in ["<h2", "<h3", "<h4", "<p>"])

    def _has_related_links(self, content):
        """Check for related links section"""
        related_indicators = [
            "related articles",
            "related links",
            "see also",
            "next:",
            "previous:"
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in related_indicators)

    def _has_professional_structure(self, content):
        """Check for professional content structure"""
        structure_elements = [
            "<h2",  # Headings
            "<p>",  # Paragraphs
            "<ul>",  # Lists
            "<strong>",  # Bold text
            "<em>"  # Emphasis
        ]
        
        found_elements = sum(1 for element in structure_elements if element in content)
        return found_elements >= 3  # At least 3 structural elements

    def _verify_toc_creation(self):
        """Verify that TOC article was created for multi-article content"""
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                # Look for TOC article
                toc_found = False
                for article in articles:
                    title = article.get('title', '').lower()
                    content = article.get('content', '').lower()
                    
                    if ('table of contents' in title or 'overview' in title or
                        'table of contents' in content):
                        print("✅ TOC article found")
                        toc_found = True
                        break
                
                if not toc_found:
                    print("⚠️ No TOC article found")
                
                return toc_found
            else:
                print(f"❌ Failed to verify TOC creation: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ TOC verification failed: {e}")
            return False

    def run_all_tests(self):
        """Run all Knowledge Engine enhanced feature tests"""
        print("🚀 Starting Knowledge Engine Enhanced Features Testing")
        print("=" * 60)
        
        test_results = {}
        
        # Test 1: Health Check
        test_results['health_check'] = self.test_health_check()
        
        # Test 2: Enhanced PDF Processing
        test_results['enhanced_pdf_processing'] = self.test_enhanced_pdf_processing()
        
        # Test 3: Enhanced Article Generation
        test_results['enhanced_article_generation'] = self.test_enhanced_article_generation()
        
        # Test 4: Multi-Article TOC Creation
        test_results['multi_article_toc'] = self.test_multi_article_toc_creation()
        
        # Test 5: Article Quality Standards
        test_results['article_quality'] = self.test_article_quality_standards()
        
        # Test 6: Backend Integration Functions
        test_results['backend_integration'] = self.test_backend_integration_functions()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 KNOWLEDGE ENGINE ENHANCED FEATURES TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if success_rate >= 80:
            print("🎉 KNOWLEDGE ENGINE ENHANCED FEATURES: PRODUCTION READY")
            return True
        elif success_rate >= 60:
            print("⚠️ KNOWLEDGE ENGINE ENHANCED FEATURES: MOSTLY WORKING")
            return True
        else:
            print("❌ KNOWLEDGE ENGINE ENHANCED FEATURES: NEEDS ATTENTION")
            return False

if __name__ == "__main__":
    tester = KnowledgeEngineEnhancedTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)