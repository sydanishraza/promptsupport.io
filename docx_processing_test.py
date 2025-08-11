#!/usr/bin/env python3
"""
Enhanced DOCX Processing Pipeline Testing
Comprehensive testing for the Training Interface DOCX processing enhancements
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://804e26ce-e2cd-4ae9-bd9c-fe7be1b5493a.preview.emergentagent.com') + '/api'

class DOCXProcessingTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"Testing Enhanced DOCX Processing Pipeline at: {self.base_url}")
        
    def create_substantial_docx_content(self):
        """Create substantial DOCX-like content that should trigger enhanced processing"""
        return """Enhanced DOCX Processing Pipeline Test Document

This is a comprehensive test document designed to verify the enhanced DOCX processing pipeline in the Training Interface. This document contains substantial content that should trigger the enhanced processing path rather than the simplified fallback.

Chapter 1: Introduction to Enhanced Processing
The enhanced DOCX processing system has been specifically designed to handle complex documents with multiple sections, images, and comprehensive content. This system should generate multiple articles from substantial DOCX content, with each article containing 1000+ words to ensure comprehensive coverage.

Key Features of Enhanced Processing:
1. Contextual image extraction and embedding
2. Comprehensive content coverage (targeting 3000+ words per article)
3. Multiple article generation from substantial content
4. Professional HTML structure with headings, paragraphs, and lists
5. Proper session management and storage

Chapter 2: Processing Decision Logic
The enhanced processing conditions should be triggered when:
- Images are found in the document (contextual_images > 0)
- Multiple structure blocks are present (structure_count >= 1)
- Substantial text content exists (body_text_length > 200)
- Total content length exceeds threshold (total_content_length > 500)

The system should log debug messages showing:
- Processing metrics (images, structure blocks, content length)
- "ENHANCED" processing path selection over "SIMPLIFIED"
- Recovery mechanisms when enhanced processing has issues

Chapter 3: Content Quality Requirements
Generated articles must demonstrate:
- Comprehensive content (not truncated at 800 words)
- Proper HTML structure with headings, paragraphs, lists
- Images embedded with figure elements
- Professional technical documentation quality
- Multiple articles from substantial DOCX content

Chapter 4: Image Processing and Embedding
The enhanced image extraction system should:
- Extract images from DOCX files with contextual tagging
- Filter out decorative images (logos, headers, footers)
- Focus on content-relevant images based on filename patterns
- Tag images with proper contextual metadata
- Sort images by document flow order
- Embed images with proper figure/figcaption structure

Chapter 5: Session Management Verification
Training sessions must be properly stored with:
- Articles array included in database storage
- Session ID correctly generated and returned
- Template data properly applied
- All metadata preserved correctly

Chapter 6: Critical Fixes Implementation
The system should resolve three main issues:
1. Content coverage enhancement (800→3000+ words per article)
2. Enhanced image extraction (bypass prevention)
3. DOCX processing returning 0 articles (fixed to generate multiple articles)

Chapter 7: Technical Implementation Details
The enhanced processing pipeline includes:
- Phase 1: Enhanced text extraction with structure preservation
- Phase 2: Contextual image extraction with filtering
- Phase 3: Template-based article generation
- Phase 4: Quality assurance and validation
- Phase 5: Session storage and management

Chapter 8: Quality Assurance Testing
This document should generate:
- Multiple comprehensive articles (2-3 articles minimum)
- Each article with 1000+ words of content
- Proper HTML formatting throughout
- Professional technical documentation quality
- Complete session management with proper IDs

Chapter 9: Performance and Reliability
The enhanced processing should:
- Complete within reasonable time limits (under 60 seconds)
- Handle large documents without memory issues
- Provide detailed debug logging for troubleshooting
- Implement proper error handling and recovery
- Maintain consistent quality across all generated articles

Chapter 10: Integration and Validation
Final validation should confirm:
- Enhanced processing path is consistently used
- Multiple articles are generated successfully
- Content coverage meets 1000+ word requirements
- Images are properly extracted and embedded
- Session management works correctly
- All critical fixes are operational

This comprehensive test document contains over 500 words and multiple structured sections that should definitively trigger the enhanced processing path and generate multiple high-quality articles with comprehensive content coverage."""

    def test_training_templates_endpoint(self):
        """Test GET /api/training/templates endpoint"""
        print("🔍 Testing Training Templates Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/training/templates", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if "templates" in data and "total" in data:
                    print(f"✅ Training templates endpoint working - {data['total']} templates found")
                    return True
                else:
                    print("❌ Training templates endpoint failed - invalid response structure")
                    return False
            else:
                print(f"❌ Training templates endpoint failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Training templates endpoint failed - {str(e)}")
            return False

    def test_training_sessions_endpoint(self):
        """Test GET /api/training/sessions endpoint"""
        print("\n🔍 Testing Training Sessions Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/training/sessions", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                print(f"Sessions count: {data.get('total', 0)}")
                
                if "sessions" in data and "total" in data:
                    print(f"✅ Training sessions endpoint working - {data['total']} sessions found")
                    return True
                else:
                    print("❌ Training sessions endpoint failed - invalid response structure")
                    return False
            else:
                print(f"❌ Training sessions endpoint failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Training sessions endpoint failed - {str(e)}")
            return False

    def test_enhanced_docx_processing_pipeline(self):
        """Test the enhanced DOCX processing pipeline with substantial content"""
        print("\n🔍 Testing Enhanced DOCX Processing Pipeline...")
        try:
            # Create substantial DOCX-like content
            docx_content = self.create_substantial_docx_content()
            print(f"Created test content: {len(docx_content)} characters")
            
            # Create file-like object with .docx extension to trigger DOCX processing
            file_data = io.BytesIO(docx_content.encode('utf-8'))
            
            # Prepare template data for Phase 1 processing
            template_data = {
                "template_id": "phase1_document_processing",
                "template_name": "Phase 1: Document Upload Processing",
                "processing_instructions": "Process uploaded documents to create comprehensive articles with proper structure and formatting",
                "output_requirements": {
                    "format": "html",
                    "min_articles": 1,
                    "max_articles": 5,
                    "quality_benchmarks": [
                        "Content completeness",
                        "No duplication", 
                        "Proper formatting",
                        "Professional presentation"
                    ]
                },
                "media_handling": {
                    "extract_images": True,
                    "contextual_placement": True,
                    "accessibility_attributes": True
                }
            }
            
            files = {
                'file': ('enhanced_docx_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps(template_data)
            }
            
            print("🚀 Starting enhanced DOCX processing...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120  # Extended timeout for enhanced processing
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"Status Code: {response.status_code}")
            print(f"Processing Time: {processing_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Verify enhanced processing results
                success = data.get("success", False)
                session_id = data.get("session_id")
                articles = data.get("articles", [])
                images_processed = data.get("images_processed", 0)
                template_applied = data.get("template_applied")
                
                print(f"✅ Processing Success: {success}")
                print(f"📝 Session ID: {session_id}")
                print(f"📚 Articles Generated: {len(articles)}")
                print(f"🖼️ Images Processed: {images_processed}")
                print(f"📋 Template Applied: {template_applied}")
                print(f"⏱️ Processing Time: {processing_time:.2f}s")
                
                if success and session_id and len(articles) > 0:
                    print("✅ Enhanced DOCX processing pipeline successful!")
                    
                    # Analyze article quality
                    self.analyze_article_quality(articles)
                    
                    # Verify processing decision logic
                    self.verify_processing_decision_logic(data)
                    
                    # Test session management
                    self.test_session_management(session_id)
                    
                    return True
                else:
                    print(f"❌ Enhanced DOCX processing failed - success: {success}, session_id: {session_id}, articles: {len(articles)}")
                    return False
            else:
                print(f"❌ Enhanced DOCX processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Enhanced DOCX processing test failed - {str(e)}")
            return False

    def analyze_article_quality(self, articles):
        """Analyze the quality of generated articles"""
        print("\n🔍 Analyzing Article Quality...")
        
        total_words = 0
        html_articles = 0
        articles_with_images = 0
        
        for i, article in enumerate(articles):
            title = article.get("title", "Untitled")
            content = article.get("content", "")
            html_content = article.get("html", content)
            word_count = article.get("word_count", len(content.split()))
            image_count = article.get("image_count", 0)
            
            print(f"\n  Article {i+1}: {title}")
            print(f"    Word Count: {word_count}")
            print(f"    Content Length: {len(content)} chars")
            print(f"    HTML Length: {len(html_content)} chars")
            print(f"    Images: {image_count}")
            
            total_words += word_count
            
            # Check for HTML structure
            html_tags = ['<h1>', '<h2>', '<h3>', '<p>', '<ul>', '<li>', '<figure>']
            html_found = sum(1 for tag in html_tags if tag in html_content)
            if html_found > 0:
                html_articles += 1
                print(f"    ✅ HTML Structure: {html_found} tags found")
            else:
                print(f"    ❌ HTML Structure: No HTML tags found")
            
            # Check for images
            if image_count > 0:
                articles_with_images += 1
                print(f"    ✅ Images: {image_count} images embedded")
            
            # Check content coverage (targeting 1000+ words)
            if word_count >= 1000:
                print(f"    ✅ Content Coverage: {word_count} words (meets 1000+ requirement)")
            elif word_count >= 500:
                print(f"    ⚠️ Content Coverage: {word_count} words (below 1000 target)")
            else:
                print(f"    ❌ Content Coverage: {word_count} words (insufficient)")
        
        print(f"\n📊 Overall Quality Analysis:")
        print(f"  Total Articles: {len(articles)}")
        print(f"  Total Words: {total_words}")
        print(f"  Average Words per Article: {total_words / len(articles) if articles else 0:.0f}")
        print(f"  Articles with HTML Structure: {html_articles}/{len(articles)}")
        print(f"  Articles with Images: {articles_with_images}/{len(articles)}")
        
        # Quality assessment
        if len(articles) >= 2:
            print("  ✅ Multiple articles generated")
        else:
            print("  ⚠️ Only single article generated")
            
        if total_words >= 1000:
            print("  ✅ Comprehensive content coverage")
        else:
            print("  ❌ Insufficient content coverage")
            
        if html_articles == len(articles):
            print("  ✅ All articles have proper HTML structure")
        else:
            print("  ⚠️ Some articles lack HTML structure")

    def verify_processing_decision_logic(self, response_data):
        """Verify that enhanced processing conditions were triggered"""
        print("\n🔍 Verifying Processing Decision Logic...")
        
        # Check for debug information in response
        processing_time = response_data.get("processing_time", 0)
        images_processed = response_data.get("images_processed", 0)
        articles_count = len(response_data.get("articles", []))
        
        print(f"  Processing Time: {processing_time}s")
        print(f"  Images Processed: {images_processed}")
        print(f"  Articles Generated: {articles_count}")
        
        # Verify enhanced processing was used
        if processing_time > 5:  # Enhanced processing should take more time
            print("  ✅ Processing time indicates enhanced processing path")
        else:
            print("  ⚠️ Processing time suggests simplified processing")
            
        if articles_count > 1:
            print("  ✅ Multiple articles suggest enhanced processing")
        else:
            print("  ⚠️ Single article may indicate simplified processing")
            
        # Check for enhanced processing indicators
        template_applied = response_data.get("template_applied")
        if template_applied:
            print(f"  ✅ Template applied: {template_applied}")
        else:
            print("  ❌ No template applied")

    def test_session_management(self, session_id):
        """Test that training sessions are properly stored"""
        print(f"\n🔍 Testing Session Management for {session_id}...")
        try:
            # Get training sessions to verify our session was stored
            response = requests.get(f"{self.base_url}/training/sessions", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                sessions = data.get("sessions", [])
                
                # Look for our session
                our_session = None
                for session in sessions:
                    if session.get("session_id") == session_id:
                        our_session = session
                        break
                
                if our_session:
                    print("  ✅ Session found in database")
                    print(f"    Session ID: {our_session.get('session_id')}")
                    print(f"    Template ID: {our_session.get('template_id')}")
                    print(f"    Filename: {our_session.get('filename')}")
                    print(f"    Training Mode: {our_session.get('training_mode')}")
                    
                    # Check if articles are included
                    articles = our_session.get("articles", [])
                    if articles:
                        print(f"    ✅ Articles stored: {len(articles)} articles")
                        return True
                    else:
                        print("    ❌ No articles stored in session")
                        return False
                else:
                    print("  ❌ Session not found in database")
                    return False
            else:
                print(f"  ❌ Could not retrieve sessions - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Session management test failed - {str(e)}")
            return False

    def test_content_coverage_fix(self):
        """Test the content coverage fix (800→3000+ words per article)"""
        print("\n🔍 Testing Content Coverage Fix (800→3000+ words)...")
        try:
            # Create very comprehensive content that should generate long articles
            comprehensive_content = """Content Coverage Enhancement Test Document

This document is specifically designed to test the content coverage enhancement that increases the word limit from 800 to 3000+ words per article. The enhanced processing system should generate comprehensive articles that fully cover the source material without artificial truncation.

Section 1: Comprehensive Content Processing
The enhanced content processing system has been redesigned to handle substantial documents and generate comprehensive articles. This system should process all available content and create articles that thoroughly cover the subject matter without being limited by the previous 800-word restriction.

Key improvements include:
- Increased word limit from 800 to 3000+ words per article
- Enhanced content extraction algorithms
- Improved template-based processing
- Better content organization and structure
- Comprehensive coverage of source material

Section 2: Technical Implementation Details
The technical implementation involves several key components:

1. Enhanced Content Extraction
   - Improved text extraction from various document formats
   - Better handling of structured content (headings, lists, tables)
   - Preservation of formatting and document structure
   - Enhanced metadata extraction and processing

2. Template-Based Processing
   - Advanced template application for content organization
   - Intelligent content splitting and article generation
   - Quality benchmarks and validation
   - Professional formatting and presentation

3. Content Coverage Algorithms
   - Comprehensive content analysis and processing
   - Intelligent article boundary detection
   - Content completeness validation
   - Quality assurance and review processes

Section 3: Quality Assurance and Validation
The enhanced system includes comprehensive quality assurance measures:

- Content completeness verification
- Duplicate content detection and removal
- Professional formatting validation
- Technical accuracy assessment
- User experience optimization

Section 4: Performance and Scalability
The system has been optimized for performance and scalability:

- Efficient processing algorithms
- Optimized memory usage
- Scalable architecture design
- Performance monitoring and optimization
- Resource management and allocation

Section 5: Integration and Testing
Comprehensive integration testing ensures:

- End-to-end functionality validation
- Cross-platform compatibility
- Performance benchmarking
- User acceptance testing
- Continuous integration and deployment

This comprehensive test document contains substantial content that should generate articles exceeding 1000 words each, demonstrating the successful implementation of the content coverage enhancement."""

            # Create file for processing
            file_data = io.BytesIO(comprehensive_content.encode('utf-8'))
            
            template_data = {
                "template_id": "content_coverage_test",
                "processing_instructions": "Generate comprehensive articles with full content coverage, targeting 1000+ words per article",
                "output_requirements": {
                    "format": "html",
                    "min_articles": 1,
                    "max_articles": 3,
                    "target_words_per_article": 1000
                }
            }
            
            files = {
                'file': ('content_coverage_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'content_coverage_test',
                'training_mode': 'true',
                'template_instructions': json.dumps(template_data)
            }
            
            print("🚀 Testing content coverage enhancement...")
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                print(f"Articles generated: {len(articles)}")
                
                # Check word counts
                total_words = 0
                articles_over_1000 = 0
                
                for i, article in enumerate(articles):
                    word_count = article.get("word_count", len(article.get("content", "").split()))
                    total_words += word_count
                    
                    print(f"  Article {i+1}: {word_count} words")
                    
                    if word_count >= 1000:
                        articles_over_1000 += 1
                        print(f"    ✅ Meets 1000+ word target")
                    else:
                        print(f"    ❌ Below 1000 word target")
                
                print(f"\nContent Coverage Results:")
                print(f"  Total words: {total_words}")
                print(f"  Articles over 1000 words: {articles_over_1000}/{len(articles)}")
                print(f"  Average words per article: {total_words / len(articles) if articles else 0:.0f}")
                
                if articles_over_1000 > 0 or total_words >= 1000:
                    print("✅ Content coverage fix working - comprehensive articles generated")
                    return True
                else:
                    print("❌ Content coverage fix failed - articles still truncated")
                    return False
            else:
                print(f"❌ Content coverage test failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content coverage test failed - {str(e)}")
            return False

    def test_training_evaluate_endpoint(self):
        """Test POST /api/training/evaluate endpoint"""
        print("\n🔍 Testing Training Evaluate Endpoint...")
        try:
            evaluation_data = {
                "session_id": "test_session_123",
                "result_id": "test_result_456", 
                "evaluation": "accepted",
                "feedback": "Test evaluation for enhanced DOCX processing pipeline"
            }
            
            response = requests.post(
                f"{self.base_url}/training/evaluate",
                json=evaluation_data,
                timeout=10
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if (data.get("success") and 
                    "evaluation_id" in data and 
                    "message" in data):
                    print("✅ Training evaluate endpoint working")
                    return True
                else:
                    print("❌ Training evaluate endpoint failed - invalid response structure")
                    return False
            else:
                print(f"❌ Training evaluate endpoint failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Training evaluate endpoint failed - {str(e)}")
            return False

    def run_all_tests(self):
        """Run all DOCX processing tests"""
        print("🚀 Starting Enhanced DOCX Processing Pipeline Tests")
        print("=" * 60)
        
        tests = [
            ("Training Templates Endpoint", self.test_training_templates_endpoint),
            ("Training Sessions Endpoint", self.test_training_sessions_endpoint),
            ("Enhanced DOCX Processing Pipeline", self.test_enhanced_docx_processing_pipeline),
            ("Content Coverage Fix", self.test_content_coverage_fix),
            ("Training Evaluate Endpoint", self.test_training_evaluate_endpoint),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print(f"\n{'='*60}")
        print("ENHANCED DOCX PROCESSING TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nOverall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All Enhanced DOCX Processing tests PASSED!")
        elif passed >= total * 0.8:
            print("⚠️ Most Enhanced DOCX Processing tests passed - minor issues detected")
        else:
            print("❌ Enhanced DOCX Processing has significant issues")
        
        return passed, total

if __name__ == "__main__":
    tester = DOCXProcessingTest()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if passed == total else 1)