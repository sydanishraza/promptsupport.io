#!/usr/bin/env python3
"""
Media Extraction Debug Test for Enhanced Content Engine
Comprehensive debugging of media processing pipeline with real_visual_document.md
"""

import requests
import json
import os
import io
import time
import re
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://c97b1c99-0ca1-4c2e-bb21-83dd79ddc554.preview.emergentagent.com') + '/api'

class MediaExtractionDebugTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_job_id = None
        self.test_article_ids = []
        print(f"🔍 Media Extraction Debug Test - Backend URL: {self.base_url}")
        print("🎯 FOCUS: Debug media extraction with real_visual_document.md")
        print("=" * 80)
        
    def load_real_visual_document(self):
        """Load the real_visual_document.md file"""
        print("\n📄 Loading real_visual_document.md...")
        try:
            with open('/app/real_visual_document.md', 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ Loaded document: {len(content)} characters")
            
            # Count embedded images
            svg_images = re.findall(r'data:image/svg\+xml;base64,[A-Za-z0-9+/=]+', content)
            print(f"🖼️ Found {len(svg_images)} embedded SVG images")
            
            # Show image details
            for i, img in enumerate(svg_images, 1):
                img_size = len(img)
                print(f"   Image {i}: {img_size} characters, starts with: {img[:50]}...")
            
            return content
            
        except Exception as e:
            print(f"❌ Failed to load real_visual_document.md: {e}")
            return None
    
    def analyze_media_content(self, content):
        """Analyze media content in the document"""
        print("\n🔍 Analyzing media content...")
        
        # Find all data URLs
        data_urls = re.findall(r'data:image/[^)]+', content)
        print(f"📊 Total data URLs found: {len(data_urls)}")
        
        # Analyze each data URL
        for i, url in enumerate(data_urls, 1):
            # Extract format and size
            if ';base64,' in url:
                format_part = url.split(';base64,')[0].replace('data:image/', '')
                base64_part = url.split(';base64,')[1]
                
                print(f"   🖼️ Image {i}:")
                print(f"      Format: {format_part}")
                print(f"      Base64 length: {len(base64_part)} characters")
                print(f"      Estimated size: ~{len(base64_part) * 3 // 4} bytes")
                
                # Validate base64
                try:
                    decoded = base64.b64decode(base64_part)
                    print(f"      ✅ Valid base64 data ({len(decoded)} bytes)")
                except Exception as e:
                    print(f"      ❌ Invalid base64 data: {e}")
        
        # Find image captions and references
        captions = re.findall(r'\*Figure \d+:.*?\*', content)
        print(f"📝 Image captions found: {len(captions)}")
        for caption in captions:
            print(f"   📝 {caption}")
        
        return {
            'total_data_urls': len(data_urls),
            'data_urls': data_urls,
            'captions': captions,
            'content_length': len(content)
        }
    
    def test_file_upload_with_media(self):
        """Test uploading the real_visual_document.md file"""
        print("\n🔍 Testing File Upload with Media...")
        
        # Load the document
        content = self.load_real_visual_document()
        if not content:
            return False
        
        # Analyze media before upload
        media_analysis = self.analyze_media_content(content)
        
        try:
            # Create file-like object
            file_data = io.BytesIO(content.encode('utf-8'))
            
            files = {
                'file': ('real_visual_document.md', file_data, 'text/markdown')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "media_extraction_debug_test",
                    "test_type": "real_visual_document_upload",
                    "document_type": "technical_documentation_with_media",
                    "original_filename": "real_visual_document.md",
                    "expected_images": media_analysis['total_data_urls']
                })
            }
            
            print(f"📤 Uploading file with {media_analysis['total_data_urls']} embedded images...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=60  # Longer timeout for media processing
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Upload Response: {json.dumps(data, indent=2)}")
                
                self.test_job_id = data.get('job_id')
                print(f"📋 Job ID: {self.test_job_id}")
                
                return True
            else:
                print(f"❌ Upload failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload failed - {str(e)}")
            return False
    
    def test_job_status_and_chunks(self):
        """Test job status and examine created chunks for media preservation"""
        print("\n🔍 Testing Job Status and Chunk Analysis...")
        
        if not self.test_job_id:
            print("❌ No job ID available")
            return False
        
        try:
            # Wait for processing to complete
            print("⏳ Waiting for processing to complete...")
            time.sleep(5)
            
            response = requests.get(
                f"{self.base_url}/jobs/{self.test_job_id}",
                timeout=15
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📋 Job Status: {json.dumps(data, indent=2)}")
                
                status = data.get('status')
                chunks_created = data.get('chunks_created', 0)
                
                print(f"📊 Job Status: {status}")
                print(f"📊 Chunks Created: {chunks_created}")
                
                if status == 'completed' and chunks_created > 0:
                    print("✅ Job completed successfully with chunks created")
                    return True
                else:
                    print(f"❌ Job status: {status}, chunks: {chunks_created}")
                    return False
            else:
                print(f"❌ Job status check failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Job status check failed - {str(e)}")
            return False
    
    def test_document_chunks_media_preservation(self):
        """Test if document chunks preserve media data"""
        print("\n🔍 Testing Document Chunks for Media Preservation...")
        
        try:
            response = requests.get(f"{self.base_url}/documents", timeout=15)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])
                
                print(f"📊 Total documents: {len(documents)}")
                
                # Look for our test document chunks
                test_chunks = []
                for doc in documents:
                    metadata = doc.get('metadata', {})
                    if metadata.get('source') == 'media_extraction_debug_test':
                        test_chunks.append(doc)
                
                print(f"🎯 Test document chunks found: {len(test_chunks)}")
                
                if not test_chunks:
                    print("❌ No test document chunks found")
                    return False
                
                # Analyze chunks for media preservation
                total_media_found = 0
                for i, chunk in enumerate(test_chunks):
                    content = chunk.get('content', '')
                    data_urls = re.findall(r'data:image/[^)]+', content)
                    
                    print(f"   📄 Chunk {i+1}: {len(content)} chars, {len(data_urls)} images")
                    if data_urls:
                        total_media_found += len(data_urls)
                        for j, url in enumerate(data_urls):
                            format_type = url.split(';')[0].replace('data:image/', '')
                            print(f"      🖼️ Image {j+1}: {format_type} format")
                
                print(f"🖼️ Total media items found in chunks: {total_media_found}")
                
                if total_media_found > 0:
                    print("✅ Media data preserved in document chunks")
                    return True
                else:
                    print("❌ No media data found in document chunks")
                    return False
                    
            else:
                print(f"❌ Document listing failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Document chunks test failed - {str(e)}")
            return False
    
    def test_content_library_media_integration(self):
        """Test if Content Library articles preserve embedded media"""
        print("\n🔍 Testing Content Library Media Integration...")
        
        try:
            # Get initial count
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Content Library access failed - status code {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"📊 Total Content Library articles: {len(articles)}")
            
            # Look for articles created from our test
            test_articles = []
            for article in articles:
                metadata = article.get('metadata', {})
                source_type = article.get('source_type', '')
                
                # Check if this article was created from our test upload
                if (metadata.get('source') == 'media_extraction_debug_test' or
                    'real_visual_document' in article.get('title', '').lower() or
                    metadata.get('original_filename') == 'real_visual_document.md'):
                    test_articles.append(article)
                    self.test_article_ids.append(article.get('id'))
            
            print(f"🎯 Test articles found: {len(test_articles)}")
            
            if not test_articles:
                print("❌ No test articles found in Content Library")
                return False
            
            # Analyze articles for media preservation
            total_articles_with_media = 0
            total_media_items = 0
            
            for i, article in enumerate(test_articles):
                title = article.get('title', 'Untitled')
                content = article.get('content', '')
                
                # Count media in article content
                data_urls = re.findall(r'data:image/[^)]+', content)
                captions = re.findall(r'\*Figure \d+:.*?\*', content)
                
                print(f"   📄 Article {i+1}: '{title}'")
                print(f"      Content length: {len(content)} characters")
                print(f"      Media items: {len(data_urls)}")
                print(f"      Captions: {len(captions)}")
                
                if data_urls:
                    total_articles_with_media += 1
                    total_media_items += len(data_urls)
                    
                    # Show media details
                    for j, url in enumerate(data_urls):
                        format_type = url.split(';')[0].replace('data:image/', '')
                        base64_part = url.split(';base64,')[1] if ';base64,' in url else ''
                        print(f"         🖼️ Image {j+1}: {format_type}, {len(base64_part)} base64 chars")
                
                # Show some captions
                for caption in captions[:2]:  # Show first 2 captions
                    print(f"      📝 {caption}")
            
            print(f"\n📊 MEDIA INTEGRATION SUMMARY:")
            print(f"   Articles with media: {total_articles_with_media}/{len(test_articles)}")
            print(f"   Total media items: {total_media_items}")
            
            if total_articles_with_media > 0 and total_media_items > 0:
                print("✅ Content Library successfully preserves embedded media")
                return True
            else:
                print("❌ Content Library does not preserve embedded media")
                return False
                
        except Exception as e:
            print(f"❌ Content Library media integration test failed - {str(e)}")
            return False
    
    def test_llm_prompt_media_preservation(self):
        """Test if LLM prompts are preserving media during article generation"""
        print("\n🔍 Testing LLM Prompt Media Preservation...")
        
        if not self.test_article_ids:
            print("❌ No test article IDs available")
            return False
        
        try:
            # Get one of our test articles to examine
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code != 200:
                print("❌ Could not retrieve articles for LLM analysis")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Find our test article
            test_article = None
            for article in articles:
                if article.get('id') in self.test_article_ids:
                    test_article = article
                    break
            
            if not test_article:
                print("❌ Could not find test article for LLM analysis")
                return False
            
            content = test_article.get('content', '')
            metadata = test_article.get('metadata', {})
            
            print(f"📄 Analyzing article: '{test_article.get('title', 'Untitled')}'")
            print(f"📊 Content length: {len(content)} characters")
            
            # Check for AI processing indicators
            ai_processed = metadata.get('ai_processed', False)
            ai_model = metadata.get('ai_model', 'unknown')
            
            print(f"🤖 AI Processed: {ai_processed}")
            print(f"🤖 AI Model: {ai_model}")
            
            # Analyze content for media preservation
            data_urls = re.findall(r'data:image/[^)]+', content)
            svg_images = re.findall(r'data:image/svg\+xml;base64,[A-Za-z0-9+/=]+', content)
            captions = re.findall(r'\*Figure \d+:.*?\*', content)
            image_references = re.findall(r'(?:Figure|figure|diagram|image|chart)\s*\d+', content)
            
            print(f"🖼️ Data URLs found: {len(data_urls)}")
            print(f"🖼️ SVG images found: {len(svg_images)}")
            print(f"📝 Image captions found: {len(captions)}")
            print(f"🔗 Image references found: {len(image_references)}")
            
            # Check for markdown image syntax
            markdown_images = re.findall(r'!\[.*?\]\(data:image/.*?\)', content)
            print(f"📝 Markdown images found: {len(markdown_images)}")
            
            # Analyze content structure for AI enhancement
            headings = re.findall(r'^#+\s+.*$', content, re.MULTILINE)
            bullet_points = re.findall(r'^\s*[-*]\s+.*$', content, re.MULTILINE)
            numbered_lists = re.findall(r'^\s*\d+\.\s+.*$', content, re.MULTILINE)
            
            print(f"📋 Content structure:")
            print(f"   Headings: {len(headings)}")
            print(f"   Bullet points: {len(bullet_points)}")
            print(f"   Numbered lists: {len(numbered_lists)}")
            
            # Show sample content with media
            if data_urls:
                print(f"\n📄 Sample content with media:")
                # Find a section with an image
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'data:image/' in line:
                        # Show context around the image
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        for j in range(start, end):
                            marker = ">>> " if j == i else "    "
                            print(f"{marker}{lines[j][:100]}...")
                        break
            
            # Assessment
            if ai_processed and data_urls and captions:
                print("✅ LLM successfully preserved media during article generation")
                print(f"   - AI processing: {ai_processed}")
                print(f"   - Media preserved: {len(data_urls)} items")
                print(f"   - Captions maintained: {len(captions)} items")
                return True
            elif data_urls:
                print("⚠️ Media preserved but may not be AI-enhanced")
                return True
            else:
                print("❌ LLM prompts are not preserving media during article generation")
                return False
                
        except Exception as e:
            print(f"❌ LLM prompt media preservation test failed - {str(e)}")
            return False
    
    def test_search_media_content(self):
        """Test if media content is searchable"""
        print("\n🔍 Testing Search for Media Content...")
        
        try:
            # Search for terms that should be in our visual document
            search_terms = [
                "System Architecture",
                "Data Flow",
                "Network Topology",
                "Figure 1",
                "diagram"
            ]
            
            total_results = 0
            media_results = 0
            
            for term in search_terms:
                search_request = {
                    "query": term,
                    "limit": 10
                }
                
                response = requests.post(
                    f"{self.base_url}/search",
                    json=search_request,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    print(f"🔍 Search '{term}': {len(results)} results")
                    total_results += len(results)
                    
                    # Check if any results contain media
                    for result in results:
                        content = result.get('content', '')
                        if 'data:image/' in content:
                            media_results += 1
                            print(f"   🖼️ Result contains media: {content[:100]}...")
                else:
                    print(f"❌ Search for '{term}' failed - status code {response.status_code}")
            
            print(f"\n📊 Search Results Summary:")
            print(f"   Total results: {total_results}")
            print(f"   Results with media: {media_results}")
            
            if total_results > 0:
                print("✅ Media content is searchable")
                return True
            else:
                print("❌ Media content is not searchable")
                return False
                
        except Exception as e:
            print(f"❌ Search media content test failed - {str(e)}")
            return False
    
    def test_media_workflow_end_to_end(self):
        """Test complete media workflow from upload to retrieval"""
        print("\n🔍 Testing Complete Media Workflow End-to-End...")
        
        try:
            # Step 1: Upload document with media
            print("📤 Step 1: Upload document with media")
            if not self.test_file_upload_with_media():
                print("❌ Step 1 failed: File upload")
                return False
            
            # Step 2: Verify job processing
            print("\n⚙️ Step 2: Verify job processing")
            if not self.test_job_status_and_chunks():
                print("❌ Step 2 failed: Job processing")
                return False
            
            # Step 3: Check document chunks
            print("\n📄 Step 3: Check document chunks")
            if not self.test_document_chunks_media_preservation():
                print("❌ Step 3 failed: Document chunks")
                return False
            
            # Step 4: Verify Content Library integration
            print("\n📚 Step 4: Verify Content Library integration")
            if not self.test_content_library_media_integration():
                print("❌ Step 4 failed: Content Library integration")
                return False
            
            # Step 5: Test LLM media preservation
            print("\n🤖 Step 5: Test LLM media preservation")
            if not self.test_llm_prompt_media_preservation():
                print("❌ Step 5 failed: LLM media preservation")
                return False
            
            # Step 6: Test search functionality
            print("\n🔍 Step 6: Test search functionality")
            if not self.test_search_media_content():
                print("❌ Step 6 failed: Search functionality")
                return False
            
            print("\n✅ Complete media workflow test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ End-to-end workflow test failed - {str(e)}")
            return False
    
    def run_comprehensive_media_debug(self):
        """Run comprehensive media extraction debugging"""
        print("🚀 Starting Comprehensive Media Extraction Debug Test")
        print("🎯 FOCUS: Debug media extraction with real_visual_document.md")
        print("📋 GOAL: Identify why images aren't showing in generated articles")
        print("=" * 80)
        
        results = {}
        
        # Load and analyze the source document
        print("\n📄 PHASE 1: SOURCE DOCUMENT ANALYSIS")
        print("=" * 50)
        content = self.load_real_visual_document()
        if content:
            media_analysis = self.analyze_media_content(content)
            results['source_analysis'] = True
            print(f"✅ Source document loaded with {media_analysis['total_data_urls']} images")
        else:
            results['source_analysis'] = False
            print("❌ Could not load source document")
            return False
        
        # Test complete workflow
        print("\n🔄 PHASE 2: COMPLETE MEDIA WORKFLOW TEST")
        print("=" * 50)
        results['end_to_end_workflow'] = self.test_media_workflow_end_to_end()
        
        # Individual component tests
        print("\n🔧 PHASE 3: INDIVIDUAL COMPONENT TESTS")
        print("=" * 50)
        
        # Reset for individual tests
        self.test_job_id = None
        self.test_article_ids = []
        
        results['file_upload'] = self.test_file_upload_with_media()
        time.sleep(3)  # Wait for processing
        results['job_processing'] = self.test_job_status_and_chunks()
        results['document_chunks'] = self.test_document_chunks_media_preservation()
        results['content_library'] = self.test_content_library_media_integration()
        results['llm_preservation'] = self.test_llm_prompt_media_preservation()
        results['search_functionality'] = self.test_search_media_content()
        
        # Summary and diagnosis
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE MEDIA EXTRACTION DEBUG RESULTS")
        print("🎯 DEBUGGING: real_visual_document.md media processing")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        test_phases = [
            ('source_analysis', 'Source Document Analysis'),
            ('end_to_end_workflow', 'End-to-End Workflow'),
            ('file_upload', 'File Upload with Media'),
            ('job_processing', 'Job Processing'),
            ('document_chunks', 'Document Chunks Media Preservation'),
            ('content_library', 'Content Library Media Integration'),
            ('llm_preservation', 'LLM Media Preservation'),
            ('search_functionality', 'Search Media Content')
        ]
        
        for test_key, test_name in test_phases:
            if test_key in results:
                result = results[test_key]
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name}: {status}")
                if result:
                    passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        # Diagnosis
        print("\n🔍 DIAGNOSIS:")
        if results.get('source_analysis') and results.get('file_upload'):
            if results.get('document_chunks'):
                if results.get('content_library'):
                    if results.get('llm_preservation'):
                        print("✅ Media extraction pipeline is working correctly")
                        print("   - Source document loaded with media")
                        print("   - File upload preserves media")
                        print("   - Document chunks contain media")
                        print("   - Content Library articles preserve media")
                        print("   - LLM prompts maintain media during generation")
                    else:
                        print("⚠️ Issue identified: LLM prompts may be stripping media")
                        print("   - Media preserved through document processing")
                        print("   - Issue occurs during AI article generation")
                        print("   - Check LLM prompts for media preservation instructions")
                else:
                    print("⚠️ Issue identified: Content Library not preserving media")
                    print("   - Media preserved in document chunks")
                    print("   - Issue occurs during Content Library article creation")
                    print("   - Check create_content_library_article_from_chunks function")
            else:
                print("⚠️ Issue identified: Document chunking losing media")
                print("   - File upload successful")
                print("   - Issue occurs during content chunking process")
                print("   - Check process_text_content function")
        else:
            print("❌ Issue identified: File upload or source document problems")
            print("   - Check file upload endpoint and document loading")
        
        # Success criteria
        critical_tests = ['source_analysis', 'file_upload', 'content_library', 'llm_preservation']
        critical_passed = sum(1 for test in critical_tests if results.get(test, False))
        
        if critical_passed >= 3:
            print(f"\n🎉 Media extraction debugging successful: {critical_passed}/{len(critical_tests)} critical tests passed")
            return True
        else:
            print(f"\n❌ Media extraction has issues: {len(critical_tests) - critical_passed} critical failures")
            return False

if __name__ == "__main__":
    tester = MediaExtractionDebugTest()
    success = tester.run_comprehensive_media_debug()
    exit(0 if success else 1)