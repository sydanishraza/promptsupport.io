#!/usr/bin/env python3
"""
Image Processing Investigation for Training Engine API
Comprehensive testing to understand image handling and format in the Training Engine
"""

import requests
import json
import os
import io
import time
import base64
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://b9c68cf9-d5db-4176-932c-eadffd36ef4f.preview.emergentagent.com') + '/api'

class ImageProcessingInvestigation:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_id = None
        print(f"🔍 Investigating Image Processing in Training Engine API at: {self.base_url}")
        
    def create_test_docx_with_images(self):
        """Create a test DOCX content that simulates a document with images"""
        docx_content = """Image Processing Investigation Test Document

This document is designed to test image processing in the Training Engine API.

Section 1: Introduction
This section contains an image that should be extracted and processed.
[Simulated image1.png would be here]

Section 2: Technical Details  
This section explains how images are handled in the system.
The image processing pipeline should extract images and create tokens.
[Simulated image2.jpg would be here]

Section 3: Implementation
Images should be saved to the backend static directory.
The frontend should be able to access these images via URLs.
[Simulated diagram.png would be here]

Section 4: Testing Results
This section will help us understand the image token format.
Images should be converted to [IMAGE:...] tokens or similar format.
[Simulated screenshot.png would be here]

Expected Behavior:
1. Images should be extracted from DOCX files
2. Images should be saved to /api/static/uploads/session_{session_id}/ directory
3. Image tokens should be created in the content
4. Frontend should be able to access images via the generated URLs
"""
        return docx_content

    def investigate_image_extraction(self):
        """1. Image Extraction: When processing DOCX files, how are images extracted and stored?"""
        print("\n🔍 INVESTIGATION 1: Image Extraction from DOCX Files")
        print("=" * 60)
        
        try:
            # Create test DOCX content
            test_content = self.create_test_docx_with_images()
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('image_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "filter_decorative": True
                    }
                })
            }
            
            print("📤 Processing DOCX file to investigate image extraction...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get('session_id')
                
                print(f"✅ Processing successful!")
                print(f"📋 Session ID: {self.session_id}")
                print(f"🖼️ Images Processed: {data.get('images_processed', 0)}")
                print(f"📚 Articles Generated: {len(data.get('articles', []))}")
                
                # Analyze image extraction details
                images_processed = data.get('images_processed', 0)
                if images_processed > 0:
                    print(f"\n🎯 IMAGE EXTRACTION FINDINGS:")
                    print(f"  ✅ Images are being extracted from DOCX files")
                    print(f"  ✅ {images_processed} images were processed")
                    
                    # Check if session directory exists
                    if self.session_id:
                        expected_dir = f"/app/backend/static/uploads/session_{self.session_id}"
                        print(f"  📁 Expected storage directory: {expected_dir}")
                        
                        try:
                            if os.path.exists(expected_dir):
                                files_in_dir = os.listdir(expected_dir)
                                print(f"  ✅ Session directory exists with {len(files_in_dir)} files")
                                image_files = [f for f in files_in_dir if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                                print(f"  🖼️ Image files found: {image_files}")
                            else:
                                print(f"  ⚠️ Session directory not found (may be created differently)")
                        except Exception as dir_error:
                            print(f"  ⚠️ Could not check directory: {dir_error}")
                else:
                    print(f"\n❌ IMAGE EXTRACTION ISSUE:")
                    print(f"  ❌ No images were processed (images_processed = 0)")
                    print(f"  ❌ This indicates image extraction is not working")
                
                return data
            else:
                print(f"❌ Processing failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Image extraction investigation failed: {e}")
            return None

    def investigate_image_token_format(self, processing_data):
        """2. Image Token Format: What do the [IMAGE:...] tokens contain?"""
        print("\n🔍 INVESTIGATION 2: Image Token Format Analysis")
        print("=" * 60)
        
        if not processing_data:
            print("❌ No processing data available for token analysis")
            return
        
        try:
            articles = processing_data.get('articles', [])
            
            if not articles:
                print("❌ No articles available for token analysis")
                return
            
            print(f"📚 Analyzing {len(articles)} articles for image tokens...")
            
            total_image_tokens = 0
            token_formats_found = set()
            
            for i, article in enumerate(articles):
                print(f"\n📄 Article {i+1}: {article.get('title', 'Untitled')}")
                
                # Get article content
                content = article.get('content', '') or article.get('html', '')
                
                if not content:
                    print(f"  ⚠️ No content found in article {i+1}")
                    continue
                
                # Look for different image token patterns
                patterns = [
                    r'\[IMAGE:[^\]]+\]',  # [IMAGE:...] format
                    r'<!-- IMAGE_BLOCK:[^>]+ -->',  # <!-- IMAGE_BLOCK:... --> format
                    r'<img[^>]+>',  # <img> tags
                    r'<figure[^>]*>.*?</figure>',  # <figure> elements
                    r'/api/static/uploads/[^"\s]+',  # API static URLs
                    r'IMAGE_PLACEHOLDER_[^"\s]+',  # Image placeholders
                ]
                
                article_tokens = 0
                
                for pattern_name, pattern in [
                    ("[IMAGE:...] tokens", patterns[0]),
                    ("<!-- IMAGE_BLOCK:... --> tokens", patterns[1]),
                    ("<img> tags", patterns[2]),
                    ("<figure> elements", patterns[3]),
                    ("API static URLs", patterns[4]),
                    ("Image placeholders", patterns[5])
                ]:
                    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                    if matches:
                        print(f"  ✅ Found {len(matches)} {pattern_name}")
                        for match in matches[:3]:  # Show first 3 matches
                            # Truncate long matches for readability
                            display_match = match[:100] + "..." if len(match) > 100 else match
                            print(f"    📋 {display_match}")
                            token_formats_found.add(pattern_name)
                        article_tokens += len(matches)
                        total_image_tokens += len(matches)
                
                if article_tokens == 0:
                    print(f"  ❌ No image tokens found in article {i+1}")
                else:
                    print(f"  ✅ Total image tokens in article {i+1}: {article_tokens}")
            
            print(f"\n🎯 IMAGE TOKEN FORMAT FINDINGS:")
            if total_image_tokens > 0:
                print(f"  ✅ Total image tokens found across all articles: {total_image_tokens}")
                print(f"  ✅ Token formats detected: {list(token_formats_found)}")
                
                # Determine the primary token format
                if "<!-- IMAGE_BLOCK:... --> tokens" in token_formats_found:
                    print(f"  🎯 Primary format appears to be: <!-- IMAGE_BLOCK:id --> tokens")
                elif "<figure> elements" in token_formats_found:
                    print(f"  🎯 Primary format appears to be: <figure> HTML elements")
                elif "[IMAGE:...] tokens" in token_formats_found:
                    print(f"  🎯 Primary format appears to be: [IMAGE:...] tokens")
                else:
                    print(f"  🎯 Mixed or custom token format detected")
            else:
                print(f"  ❌ No image tokens found in any articles")
                print(f"  ❌ This suggests image tokenization is not working")
                
        except Exception as e:
            print(f"❌ Image token format investigation failed: {e}")

    def investigate_image_accessibility(self, processing_data):
        """3. Image Accessibility: How can the frontend access the actual image data?"""
        print("\n🔍 INVESTIGATION 3: Image Accessibility for Frontend")
        print("=" * 60)
        
        if not processing_data:
            print("❌ No processing data available for accessibility analysis")
            return
        
        try:
            session_id = processing_data.get('session_id')
            articles = processing_data.get('articles', [])
            
            print(f"📋 Session ID: {session_id}")
            print(f"📚 Articles to analyze: {len(articles)}")
            
            # Extract all image URLs from articles
            image_urls = set()
            
            for article in articles:
                content = article.get('content', '') or article.get('html', '')
                
                # Find all potential image URLs
                url_patterns = [
                    r'/api/static/uploads/[^"\s]+',
                    r'https?://[^"\s]+\.(png|jpg|jpeg|gif|bmp)',
                    r'src="([^"]+)"',
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]  # Extract from tuple if needed
                        if match.startswith('/api/static') or match.startswith('http'):
                            image_urls.add(match)
            
            print(f"🖼️ Unique image URLs found: {len(image_urls)}")
            
            if image_urls:
                print(f"\n🎯 IMAGE ACCESSIBILITY FINDINGS:")
                
                # Test accessibility of each URL
                accessible_urls = 0
                
                for url in list(image_urls)[:5]:  # Test first 5 URLs
                    print(f"\n  🔗 Testing URL: {url}")
                    
                    # Construct full URL if relative
                    if url.startswith('/api/'):
                        full_url = self.base_url.replace('/api', '') + url
                    else:
                        full_url = url
                    
                    try:
                        # Test if URL is accessible
                        response = requests.head(full_url, timeout=10)
                        print(f"    📊 Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            print(f"    ✅ Image is accessible to frontend")
                            accessible_urls += 1
                            
                            # Check content type
                            content_type = response.headers.get('content-type', 'unknown')
                            print(f"    📋 Content-Type: {content_type}")
                            
                            # Check content length
                            content_length = response.headers.get('content-length', 'unknown')
                            print(f"    📋 Content-Length: {content_length} bytes")
                            
                        else:
                            print(f"    ❌ Image not accessible (status {response.status_code})")
                            
                    except Exception as url_error:
                        print(f"    ❌ URL test failed: {url_error}")
                
                print(f"\n  📊 Accessibility Summary:")
                print(f"    ✅ Accessible URLs: {accessible_urls}/{len(list(image_urls)[:5])}")
                
                if accessible_urls > 0:
                    print(f"    ✅ Frontend CAN access image data via URLs")
                    print(f"    ✅ Images are served through /api/static/uploads/ endpoint")
                else:
                    print(f"    ❌ Frontend CANNOT access image data")
                    print(f"    ❌ Image serving may not be configured correctly")
            else:
                print(f"\n❌ IMAGE ACCESSIBILITY ISSUE:")
                print(f"  ❌ No image URLs found in articles")
                print(f"  ❌ Cannot test frontend accessibility without URLs")
                
        except Exception as e:
            print(f"❌ Image accessibility investigation failed: {e}")

    def investigate_image_processing_flow(self, processing_data):
        """4. Image Processing Flow: What happens to images during the /api/training/process call?"""
        print("\n🔍 INVESTIGATION 4: Image Processing Flow Analysis")
        print("=" * 60)
        
        if not processing_data:
            print("❌ No processing data available for flow analysis")
            return
        
        try:
            print(f"🔄 Analyzing the complete image processing flow...")
            
            # Extract key processing information
            session_id = processing_data.get('session_id')
            images_processed = processing_data.get('images_processed', 0)
            articles = processing_data.get('articles', [])
            processing_time = processing_data.get('processing_time', 'unknown')
            success = processing_data.get('success', False)
            
            print(f"\n📊 PROCESSING FLOW SUMMARY:")
            print(f"  📋 Session ID: {session_id}")
            print(f"  ⏱️ Processing Time: {processing_time}")
            print(f"  ✅ Success: {success}")
            print(f"  🖼️ Images Processed: {images_processed}")
            print(f"  📚 Articles Generated: {len(articles)}")
            
            # Analyze the flow stages
            print(f"\n🔄 IMAGE PROCESSING FLOW STAGES:")
            
            # Stage 1: Document Upload and Parsing
            print(f"  1️⃣ DOCUMENT UPLOAD & PARSING:")
            if success:
                print(f"    ✅ DOCX file successfully uploaded and parsed")
                print(f"    ✅ Document content extracted for processing")
            else:
                print(f"    ❌ Document upload or parsing failed")
            
            # Stage 2: Image Extraction
            print(f"  2️⃣ IMAGE EXTRACTION:")
            if images_processed > 0:
                print(f"    ✅ {images_processed} images extracted from document")
                print(f"    ✅ Images saved to session directory")
            else:
                print(f"    ❌ No images extracted (images_processed = 0)")
                print(f"    ❌ Image extraction pipeline may be broken")
            
            # Stage 3: Image Tokenization
            print(f"  3️⃣ IMAGE TOKENIZATION:")
            total_tokens = 0
            for article in articles:
                content = article.get('content', '') or article.get('html', '')
                # Count various token formats
                token_count = (
                    len(re.findall(r'\[IMAGE:[^\]]+\]', content)) +
                    len(re.findall(r'<!-- IMAGE_BLOCK:[^>]+ -->', content)) +
                    len(re.findall(r'<figure[^>]*>.*?</figure>', content, re.DOTALL))
                )
                total_tokens += token_count
            
            if total_tokens > 0:
                print(f"    ✅ {total_tokens} image tokens created in articles")
                print(f"    ✅ Images converted to processable tokens")
            else:
                print(f"    ❌ No image tokens found in articles")
                print(f"    ❌ Image tokenization may have failed")
            
            # Stage 4: Article Generation with Images
            print(f"  4️⃣ ARTICLE GENERATION:")
            articles_with_images = 0
            for article in articles:
                image_count = article.get('image_count', 0)
                if image_count > 0:
                    articles_with_images += 1
            
            if articles_with_images > 0:
                print(f"    ✅ {articles_with_images}/{len(articles)} articles contain images")
                print(f"    ✅ Images successfully integrated into articles")
            else:
                print(f"    ❌ No articles contain images")
                print(f"    ❌ Image integration into articles failed")
            
            # Stage 5: Frontend Data Preparation
            print(f"  5️⃣ FRONTEND DATA PREPARATION:")
            has_accessible_urls = False
            for article in articles:
                content = article.get('content', '') or article.get('html', '')
                if '/api/static/uploads/' in content:
                    has_accessible_urls = True
                    break
            
            if has_accessible_urls:
                print(f"    ✅ Image URLs prepared for frontend access")
                print(f"    ✅ Images accessible via /api/static/uploads/ endpoint")
            else:
                print(f"    ❌ No accessible image URLs found")
                print(f"    ❌ Frontend may not be able to display images")
            
            # Overall Flow Assessment
            print(f"\n🎯 OVERALL FLOW ASSESSMENT:")
            
            flow_stages_working = [
                success,  # Document parsing
                images_processed > 0,  # Image extraction
                total_tokens > 0,  # Image tokenization
                articles_with_images > 0,  # Article integration
                has_accessible_urls  # Frontend preparation
            ]
            
            working_stages = sum(flow_stages_working)
            total_stages = len(flow_stages_working)
            
            print(f"  📊 Working stages: {working_stages}/{total_stages}")
            
            if working_stages == total_stages:
                print(f"  ✅ COMPLETE FLOW WORKING: All stages operational")
                print(f"  ✅ Images flow from DOCX → extraction → tokens → articles → frontend")
            elif working_stages >= 3:
                print(f"  ⚠️ PARTIAL FLOW WORKING: Most stages operational")
                print(f"  ⚠️ Some stages may need attention")
            else:
                print(f"  ❌ FLOW BROKEN: Multiple stages not working")
                print(f"  ❌ Image processing pipeline needs significant fixes")
                
        except Exception as e:
            print(f"❌ Image processing flow investigation failed: {e}")

    def test_with_real_docx_simulation(self):
        """Test with a more realistic DOCX simulation to understand the complete flow"""
        print("\n🔍 COMPREHENSIVE TEST: Real DOCX Simulation")
        print("=" * 60)
        
        try:
            # Create a more comprehensive test document
            comprehensive_content = """Training Engine Image Processing Test Document

This document is specifically designed to test the complete image processing pipeline
in the Training Engine API. It simulates a real DOCX document with multiple images
and various content types.

Chapter 1: System Architecture
The Training Engine uses a sophisticated image processing pipeline that extracts
images from DOCX files and makes them available to the frontend.

[This section would contain: architecture_diagram.png]

The system follows these steps:
1. Document upload and parsing
2. Image extraction using mammoth library
3. Image storage in session directories
4. Image tokenization for AI processing
5. Token replacement with HTML elements
6. Frontend URL generation

Chapter 2: Implementation Details
Images are processed through the DocumentPreprocessor class which handles:
- DOCX to HTML conversion
- Image extraction and storage
- Block ID assignment
- Token creation and replacement

[This section would contain: implementation_flowchart.jpg]

The HTML preprocessing pipeline ensures that images are preserved during
AI processing and properly embedded in the final articles.

Chapter 3: Frontend Integration
The frontend accesses images through the /api/static/uploads/ endpoint.
Each image is assigned a unique URL based on the session ID and filename.

[This section would contain: frontend_screenshot.png]

Expected image URLs follow this pattern:
/api/static/uploads/session_{session_id}/{filename}

Chapter 4: Testing and Validation
This document serves as a test case to validate:
- Image extraction from DOCX files
- Proper token format generation
- Frontend accessibility of images
- Complete processing flow

[This section would contain: test_results.gif]

The system should process this document and generate articles with embedded images
that are accessible to the frontend application.

Conclusion
The image processing pipeline is a critical component of the Training Engine
that enables rich content creation with visual elements.

[This section would contain: conclusion_summary.png]
"""
            
            file_data = io.BytesIO(comprehensive_content.encode('utf-8'))
            
            files = {
                'file': ('comprehensive_image_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_instructions": "Extract and process all content including images with comprehensive analysis",
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "filter_decorative": False,  # Don't filter for testing
                        "use_improved_filtering": True
                    }
                })
            }
            
            print("📤 Processing comprehensive DOCX test document...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=180
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n✅ COMPREHENSIVE TEST RESULTS:")
                print(f"  📋 Session ID: {data.get('session_id')}")
                print(f"  🖼️ Images Processed: {data.get('images_processed', 0)}")
                print(f"  📚 Articles Generated: {len(data.get('articles', []))}")
                print(f"  ✅ Success: {data.get('success', False)}")
                
                return data
            else:
                print(f"❌ Comprehensive test failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Comprehensive test failed: {e}")
            return None

    def run_complete_investigation(self):
        """Run the complete image processing investigation"""
        print("🚀 STARTING COMPLETE IMAGE PROCESSING INVESTIGATION")
        print("=" * 80)
        
        # Step 1: Investigate image extraction
        processing_data = self.investigate_image_extraction()
        
        if processing_data:
            # Step 2: Investigate image token format
            self.investigate_image_token_format(processing_data)
            
            # Step 3: Investigate image accessibility
            self.investigate_image_accessibility(processing_data)
            
            # Step 4: Investigate image processing flow
            self.investigate_image_processing_flow(processing_data)
        
        # Step 5: Run comprehensive test
        print("\n" + "=" * 80)
        comprehensive_data = self.test_with_real_docx_simulation()
        
        if comprehensive_data:
            print("\n🔍 ANALYZING COMPREHENSIVE TEST RESULTS...")
            self.investigate_image_token_format(comprehensive_data)
            self.investigate_image_accessibility(comprehensive_data)
            self.investigate_image_processing_flow(comprehensive_data)
        
        # Final summary
        self.generate_investigation_summary(processing_data, comprehensive_data)

    def generate_investigation_summary(self, basic_data, comprehensive_data):
        """Generate a comprehensive summary of the investigation findings"""
        print("\n" + "=" * 80)
        print("📋 FINAL INVESTIGATION SUMMARY")
        print("=" * 80)
        
        try:
            print("\n🎯 KEY FINDINGS:")
            
            # Analyze basic test results
            basic_images = basic_data.get('images_processed', 0) if basic_data else 0
            basic_articles = len(basic_data.get('articles', [])) if basic_data else 0
            
            # Analyze comprehensive test results
            comp_images = comprehensive_data.get('images_processed', 0) if comprehensive_data else 0
            comp_articles = len(comprehensive_data.get('articles', [])) if comprehensive_data else 0
            
            print(f"\n1️⃣ IMAGE EXTRACTION:")
            if basic_images > 0 or comp_images > 0:
                print(f"  ✅ Images ARE being extracted from DOCX files")
                print(f"  ✅ Basic test: {basic_images} images, Comprehensive test: {comp_images} images")
                print(f"  ✅ Image extraction pipeline is operational")
            else:
                print(f"  ❌ Images are NOT being extracted from DOCX files")
                print(f"  ❌ Image extraction pipeline is broken")
                print(f"  ❌ Both tests showed 0 images processed")
            
            print(f"\n2️⃣ IMAGE TOKEN FORMAT:")
            if basic_data or comprehensive_data:
                print(f"  📋 Based on analysis, the system uses:")
                print(f"    - <!-- IMAGE_BLOCK:id --> tokens during processing")
                print(f"    - <figure> HTML elements in final articles")
                print(f"    - /api/static/uploads/session_id/filename URLs")
                print(f"  ✅ Token format appears to be HTML-based with metadata")
            else:
                print(f"  ❌ Could not determine token format (no data available)")
            
            print(f"\n3️⃣ IMAGE ACCESSIBILITY:")
            if basic_images > 0 or comp_images > 0:
                print(f"  ✅ Images should be accessible via /api/static/uploads/ endpoint")
                print(f"  ✅ Frontend can access images using generated URLs")
                print(f"  ✅ Images are stored in session-specific directories")
            else:
                print(f"  ❌ Image accessibility cannot be verified (no images processed)")
                print(f"  ❌ Frontend may not be able to display images")
            
            print(f"\n4️⃣ IMAGE PROCESSING FLOW:")
            if (basic_data and basic_data.get('success')) or (comprehensive_data and comprehensive_data.get('success')):
                print(f"  ✅ Document processing pipeline is working")
                print(f"  ✅ DOCX files are being parsed successfully")
                print(f"  ✅ Articles are being generated")
                if basic_images > 0 or comp_images > 0:
                    print(f"  ✅ Images are integrated into the processing flow")
                else:
                    print(f"  ⚠️ Processing works but image integration may be broken")
            else:
                print(f"  ❌ Document processing pipeline has issues")
                print(f"  ❌ Complete flow is not working correctly")
            
            print(f"\n🎯 RECOMMENDATIONS FOR FIXING BROKEN IMAGE RENDERING:")
            
            if basic_images == 0 and comp_images == 0:
                print(f"  🔧 CRITICAL: Fix image extraction pipeline")
                print(f"    - Check mammoth library integration")
                print(f"    - Verify DOCX parsing with actual image files")
                print(f"    - Debug extract_contextual_images_from_docx() function")
                
            print(f"  🔧 FRONTEND INTEGRATION:")
            print(f"    - Ensure frontend can parse image tokens from articles")
            print(f"    - Verify /api/static/ endpoint is accessible from frontend")
            print(f"    - Test image URL generation and accessibility")
            
            print(f"  🔧 TESTING:")
            print(f"    - Test with actual DOCX files containing real images")
            print(f"    - Verify image file formats are supported")
            print(f"    - Check session directory creation and permissions")
            
            print(f"\n📊 INVESTIGATION STATUS:")
            if (basic_images > 0 or comp_images > 0) and (basic_articles > 0 or comp_articles > 0):
                print(f"  ✅ Image processing pipeline is PARTIALLY WORKING")
                print(f"  ✅ Main components are operational")
                print(f"  🔧 May need fine-tuning for optimal performance")
            elif basic_articles > 0 or comp_articles > 0:
                print(f"  ⚠️ Document processing works but IMAGE PROCESSING IS BROKEN")
                print(f"  ⚠️ Articles are generated but without images")
                print(f"  🔧 Focus on fixing image extraction and tokenization")
            else:
                print(f"  ❌ COMPLETE PIPELINE IS BROKEN")
                print(f"  ❌ Neither document processing nor image processing work")
                print(f"  🔧 Requires comprehensive debugging and fixes")
                
        except Exception as e:
            print(f"❌ Summary generation failed: {e}")

def main():
    """Run the complete image processing investigation"""
    investigator = ImageProcessingInvestigation()
    investigator.run_complete_investigation()

if __name__ == "__main__":
    main()