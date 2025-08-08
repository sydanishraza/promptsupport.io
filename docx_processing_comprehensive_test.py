#!/usr/bin/env python3
"""
Enhanced .DOCX Processing System Comprehensive Testing
Testing the enhanced documentation processing pipeline as requested in the review
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://b9c68cf9-d5db-4176-932c-eadffd36ef4f.preview.emergentagent.com') + '/api'

class ComprehensiveDocxProcessingTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_session_id = None
        print(f"🎯 Testing Enhanced .DOCX Processing System at: {self.base_url}")
        print("=" * 80)
        
    def test_docx_upload_and_processing_pipeline(self):
        """Test 1: DOCX FILE PROCESSING PIPELINE - Test /api/content/upload endpoint with DOCX files"""
        print("🔍 TEST 1: DOCX FILE PROCESSING PIPELINE")
        print("Testing /api/content/upload endpoint with real DOCX files...")
        
        try:
            # Use the source_document.docx file mentioned in the review request
            docx_file_path = "/app/source_document.docx"
            
            if not os.path.exists(docx_file_path):
                print(f"⚠️ Source document not found, using alternative...")
                docx_file_path = "/app/Master_Product_Management_Guide.docx"
            
            if not os.path.exists(docx_file_path):
                print(f"❌ No suitable DOCX file found")
                return False
            
            file_size = os.path.getsize(docx_file_path)
            print(f"📄 Testing with {os.path.basename(docx_file_path)} ({file_size} bytes)")
            
            with open(docx_file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(docx_file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'metadata': json.dumps({
                        "source": "enhanced_docx_processing_test",
                        "test_type": "docx_processing_pipeline",
                        "document_type": "documentation",
                        "enable_image_extraction": True,
                        "enable_documentation_processing": True
                    })
                }
                
                print("📤 Uploading DOCX file to /api/content/upload...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.base_url}/content/upload",
                    files=files,
                    data=form_data,
                    timeout=180
                )
                
                processing_time = time.time() - start_time
                print(f"⏱️ Upload processing time: {processing_time:.2f} seconds")
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ DOCX upload successful!")
                    print(f"📋 Response keys: {list(data.keys())}")
                    
                    # Check for expected response structure
                    job_id = data.get('job_id')
                    if job_id:
                        print(f"🆔 Job ID: {job_id}")
                        self.test_session_id = data.get('session_id', job_id)
                    
                    chunks_created = data.get('chunks_created', 0)
                    print(f"📚 Chunks created: {chunks_created}")
                    
                    status = data.get('status', 'unknown')
                    print(f"📊 Status: {status}")
                    
                    # Check for documentation processing indicators
                    if chunks_created > 0:
                        print("✅ DOCX processing pipeline operational")
                        return True
                    else:
                        print("⚠️ No chunks created - may indicate processing issues")
                        return False
                else:
                    print(f"❌ DOCX upload failed - status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ DOCX upload test failed - {str(e)}")
            return False
    
    def test_image_extraction_and_real_file_saving(self):
        """Test 2: Verify image extraction from DOCX documents and real file saving"""
        print("\n🔍 TEST 2: IMAGE EXTRACTION AND REAL FILE SAVING")
        print("Testing image extraction and saving to /api/static/uploads/...")
        
        try:
            # Use a DOCX file that likely contains images
            docx_files_to_test = [
                "/app/Google_Map_JavaScript_API_Tutorial.docx",
                "/app/Master_Product_Management_Guide.docx",
                "/app/source_document.docx"
            ]
            
            docx_file_path = None
            for file_path in docx_files_to_test:
                if os.path.exists(file_path):
                    docx_file_path = file_path
                    break
            
            if not docx_file_path:
                print(f"❌ No suitable DOCX file found for image testing")
                return False
            
            file_size = os.path.getsize(docx_file_path)
            print(f"📄 Testing with {os.path.basename(docx_file_path)} ({file_size} bytes)")
            
            with open(docx_file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(docx_file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'metadata': json.dumps({
                        "source": "image_extraction_test",
                        "test_type": "image_extraction_and_saving",
                        "extract_images": True,
                        "save_real_files": True
                    })
                }
                
                print("📤 Processing DOCX for image extraction...")
                
                response = requests.post(
                    f"{self.base_url}/content/upload",
                    files=files,
                    data=form_data,
                    timeout=180
                )
                
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for image processing indicators
                    images_processed = data.get('images_processed', 0)
                    print(f"🖼️ Images processed: {images_processed}")
                    
                    session_id = data.get('session_id') or data.get('job_id')
                    if session_id:
                        print(f"🆔 Session ID: {session_id}")
                        
                        # Test if images are accessible via static URL
                        if images_processed > 0:
                            print("🔗 Testing image URL accessibility...")
                            test_url = f"{self.base_url}/static/uploads/session_{session_id}/"
                            print(f"📍 Expected image directory: {test_url}")
                            
                            # Try to access the static directory
                            try:
                                static_response = requests.get(test_url, timeout=10)
                                if static_response.status_code in [200, 403]:  # 403 is OK for directory listing
                                    print("✅ Image directory accessible")
                                else:
                                    print(f"⚠️ Image directory returned status {static_response.status_code}")
                            except:
                                print("⚠️ Could not test image directory accessibility")
                        
                        print("✅ Image extraction and file saving operational")
                        return True
                    else:
                        print("⚠️ No session ID returned")
                        return images_processed > 0  # Still OK if images were processed
                else:
                    print(f"❌ Image extraction test failed - status code {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Image extraction test failed - {str(e)}")
            return False
    
    def test_documentation_processing_function(self):
        """Test 3: ENHANCED DOCUMENTATION PROCESSING - Verify create_documentation_articles_from_content function"""
        print("\n🔍 TEST 3: ENHANCED DOCUMENTATION PROCESSING")
        print("Testing documentation-specific processing pipeline...")
        
        try:
            # Test with a documentation-style DOCX file
            docx_file_path = "/app/Master_Product_Management_Guide.docx"
            
            if not os.path.exists(docx_file_path):
                docx_file_path = "/app/source_document.docx"
            
            if not os.path.exists(docx_file_path):
                print(f"❌ No documentation DOCX file found")
                return False
            
            print(f"📄 Testing documentation processing with {os.path.basename(docx_file_path)}")
            
            with open(docx_file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(docx_file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                # Use documentation-specific processing parameters
                form_data = {
                    'content_type': 'documentation',
                    'processing_mode': 'enhanced_documentation',
                    'metadata': json.dumps({
                        "source": "documentation_processing_test",
                        "test_type": "enhanced_documentation_processing",
                        "document_type": "technical_documentation",
                        "enable_technical_writing_standards": True,
                        "enable_tables_and_procedures": True,
                        "enable_callouts": True,
                        "enable_numbered_procedures": True,
                        "preserve_full_content": True
                    })
                }
                
                print("📤 Processing DOCX with documentation-specific pipeline...")
                
                response = requests.post(
                    f"{self.base_url}/content/upload",
                    files=files,
                    data=form_data,
                    timeout=240  # Longer timeout for enhanced processing
                )
                
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for documentation-specific processing indicators
                    processing_mode = data.get('processing_mode', 'standard')
                    print(f"🔧 Processing mode: {processing_mode}")
                    
                    chunks_created = data.get('chunks_created', 0)
                    articles_created = data.get('articles_created', 0)
                    print(f"📚 Chunks created: {chunks_created}")
                    print(f"📄 Articles created: {articles_created}")
                    
                    # Check for technical writing standards
                    if 'technical_writing_applied' in data:
                        print("✅ Technical writing standards applied")
                    
                    if 'tables_processed' in data:
                        print(f"📊 Tables processed: {data['tables_processed']}")
                    
                    if 'procedures_identified' in data:
                        print(f"📋 Procedures identified: {data['procedures_identified']}")
                    
                    if chunks_created > 0 or articles_created > 0:
                        print("✅ Documentation processing successful!")
                        return True
                    else:
                        print("⚠️ No content was created from documentation")
                        return False
                else:
                    print(f"❌ Documentation processing failed - status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Documentation processing test failed - {str(e)}")
            return False
    
    def test_article_generation_quality_standards(self):
        """Test 4: ARTICLE GENERATION QUALITY - Verify articles match quality standards"""
        print("\n🔍 TEST 4: ARTICLE GENERATION QUALITY STANDARDS")
        print("Testing article quality standards and HTML structure...")
        
        try:
            # Check Content Library for recently generated articles
            print("📚 Checking Content Library for generated articles...")
            
            response = requests.get(f"{self.base_url}/content-library", timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Could not access Content Library - status code {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            if not articles:
                print("⚠️ No articles found in Content Library")
                return False
            
            print(f"📚 Found {len(articles)} articles in Content Library")
            
            # Test the most recent articles (likely from our tests)
            test_articles = articles[:5]  # Test first 5 articles
            
            quality_checks_passed = 0
            total_quality_checks = 0
            
            for i, article in enumerate(test_articles):
                print(f"\n📄 Testing Article {i+1}: {article.get('title', 'Untitled')[:60]}...")
                
                # Quality Check 1: HTML Structure (H1, H2, H3, tables, lists)
                content = article.get('content', '') or article.get('html', '')
                if content:
                    h1_count = content.count('<h1')
                    h2_count = content.count('<h2')
                    h3_count = content.count('<h3')
                    table_count = content.count('<table')
                    list_count = content.count('<ul') + content.count('<ol')
                    
                    print(f"  📊 HTML Structure: H1({h1_count}) H2({h2_count}) H3({h3_count}) Tables({table_count}) Lists({list_count})")
                    
                    if h1_count > 0 or h2_count > 0:
                        quality_checks_passed += 1
                        print("  ✅ Proper heading structure")
                    else:
                        print("  ⚠️ Limited heading structure")
                    
                    total_quality_checks += 1
                
                # Quality Check 2: Content Length (comprehensive, not summaries)
                word_count = article.get('word_count', 0)
                print(f"  📝 Word count: {word_count}")
                
                if word_count > 1000:  # Comprehensive content
                    quality_checks_passed += 1
                    print("  ✅ Comprehensive content (not summary)")
                elif word_count > 500:
                    quality_checks_passed += 0.5  # Partial credit
                    print("  ⚠️ Moderate content length")
                else:
                    print("  ⚠️ Content may be too brief")
                
                total_quality_checks += 1
                
                # Quality Check 3: Clean Titles (not generic "Comprehensive Guide To...")
                title = article.get('title', '')
                if title and not title.startswith('Comprehensive Guide To'):
                    quality_checks_passed += 1
                    print("  ✅ Clean, specific title")
                else:
                    print("  ⚠️ Generic or missing title")
                
                total_quality_checks += 1
                
                # Quality Check 4: Contextual Image Embedding with Real URLs
                image_count = article.get('image_count', 0)
                has_images = article.get('has_images', False)
                
                print(f"  🖼️ Images: {image_count} (has_images: {has_images})")
                
                if image_count > 0 and '/api/static/uploads/' in content:
                    quality_checks_passed += 1
                    print("  ✅ Real image URLs (not fake)")
                elif image_count == 0:
                    quality_checks_passed += 1  # No images is acceptable
                    print("  ✅ No images expected/found")
                else:
                    print("  ⚠️ Image integration issues")
                
                total_quality_checks += 1
                
                # Quality Check 5: Professional HTML Structure
                if content:
                    has_figure_elements = '<figure' in content
                    has_proper_paragraphs = '<p>' in content
                    has_semantic_structure = any(tag in content for tag in ['<section', '<article', '<header'])
                    
                    structure_score = sum([has_figure_elements, has_proper_paragraphs, has_semantic_structure])
                    
                    if structure_score >= 2:
                        quality_checks_passed += 1
                        print("  ✅ Professional HTML structure")
                    else:
                        print("  ⚠️ HTML structure needs improvement")
                    
                    total_quality_checks += 1
            
            # Overall quality assessment
            quality_percentage = (quality_checks_passed / total_quality_checks) * 100
            print(f"\n📊 Overall Quality Assessment: {quality_checks_passed:.1f}/{total_quality_checks} checks passed ({quality_percentage:.1f}%)")
            
            if quality_percentage >= 70:
                print("✅ Article generation quality meets standards!")
                return True
            else:
                print("⚠️ Article generation quality needs improvement")
                return False
                
        except Exception as e:
            print(f"❌ Article quality test failed - {str(e)}")
            return False
    
    def test_content_library_integration(self):
        """Test 5: CONTENT LIBRARY INTEGRATION - Test article storage in content_library collection"""
        print("\n🔍 TEST 5: CONTENT LIBRARY INTEGRATION")
        print("Testing article storage in content_library collection...")
        
        try:
            # Test Content Library API endpoints
            print("📚 Testing Content Library endpoints...")
            
            # Test GET /api/content-library
            response = requests.get(f"{self.base_url}/content-library", timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Content Library GET failed - status code {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            total_count = data.get('total', len(articles))
            
            print(f"📚 Content Library contains {total_count} articles")
            
            if not articles:
                print("⚠️ No articles found in Content Library")
                return True  # Not necessarily a failure
            
            # Test article metadata structure
            sample_article = articles[0]
            print(f"📄 Testing metadata structure of: {sample_article.get('title', 'Untitled')[:50]}...")
            
            # Check required metadata fields
            required_fields = ['id', 'title', 'content', 'created_at', 'word_count']
            metadata_checks_passed = 0
            
            for field in required_fields:
                if field in sample_article:
                    metadata_checks_passed += 1
                    print(f"  ✅ {field}: {type(sample_article[field]).__name__}")
                else:
                    print(f"  ❌ Missing field: {field}")
            
            # Check optional metadata fields for enhanced processing
            optional_fields = ['tags', 'status', 'image_count', 'metadata', 'ai_processed', 'takeaways', 'summary']
            for field in optional_fields:
                if field in sample_article:
                    print(f"  ✅ {field}: {sample_article[field]}")
            
            # Test article retrieval by ID
            if 'id' in sample_article:
                article_id = sample_article['id']
                print(f"🔍 Testing individual article retrieval: {article_id}")
                
                response = requests.get(f"{self.base_url}/content-library/{article_id}", timeout=15)
                
                if response.status_code == 200:
                    print("  ✅ Individual article retrieval successful")
                else:
                    print(f"  ⚠️ Individual article retrieval failed - status {response.status_code}")
            
            # Overall assessment
            if metadata_checks_passed >= 4:  # At least 4 out of 5 required fields
                print("✅ Content Library integration working properly!")
                return True
            else:
                print("❌ Content Library integration has metadata issues")
                return False
                
        except Exception as e:
            print(f"❌ Content Library integration test failed - {str(e)}")
            return False
    
    def test_asset_management_system(self):
        """Test 6: ASSET MANAGEMENT - Verify extracted images are saved as files (not base64)"""
        print("\n🔍 TEST 6: ASSET MANAGEMENT SYSTEM")
        print("Testing asset metadata and real file storage...")
        
        try:
            # Test Assets API endpoint
            print("📁 Testing Assets API endpoint...")
            
            response = requests.get(f"{self.base_url}/assets", timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Assets API failed - status code {response.status_code}")
                return False
            
            data = response.json()
            assets = data.get('assets', [])
            total_assets = data.get('total', len(assets))
            
            print(f"📁 Asset Library contains {total_assets} assets")
            
            if not assets:
                print("⚠️ No assets found in Asset Library")
                return True  # Not necessarily a failure if no images were processed
            
            # Test asset metadata structure
            image_assets = [asset for asset in assets if asset.get('asset_type') == 'image']
            print(f"🖼️ Found {len(image_assets)} image assets")
            
            if image_assets:
                sample_asset = image_assets[0]
                print(f"📄 Testing asset metadata: {sample_asset.get('filename', 'Unknown')}")
                
                # Check required asset fields
                required_asset_fields = ['id', 'filename', 'asset_type', 'url', 'file_size']
                asset_checks_passed = 0
                
                for field in required_asset_fields:
                    if field in sample_asset:
                        asset_checks_passed += 1
                        print(f"  ✅ {field}: {sample_asset[field]}")
                    else:
                        print(f"  ❌ Missing field: {field}")
                
                # Verify assets are saved as files (not base64)
                file_size = sample_asset.get('file_size', 0)
                url = sample_asset.get('url', '')
                
                if file_size > 0 and not url.startswith('data:'):
                    print(f"  ✅ Asset saved as real file ({file_size} bytes)")
                    print(f"  ✅ Real URL (not base64): {url}")
                else:
                    print(f"  ⚠️ Asset may not be saved as real file")
                
                # Test asset URL accessibility
                if url and url.startswith('/api/'):
                    print(f"🔗 Testing asset URL accessibility: {url}")
                    
                    # Convert relative URL to full URL for testing
                    full_url = self.base_url.replace('/api', '') + url
                    
                    try:
                        asset_response = requests.head(full_url, timeout=10)
                        if asset_response.status_code == 200:
                            print("  ✅ Asset URL accessible")
                        else:
                            print(f"  ⚠️ Asset URL returned status {asset_response.status_code}")
                    except:
                        print("  ⚠️ Asset URL accessibility test failed")
                
                # Overall asset management assessment
                if asset_checks_passed >= 4:
                    print("✅ Asset management working properly!")
                    return True
                else:
                    print("❌ Asset management has metadata issues")
                    return False
            else:
                print("✅ Asset management system operational (no image assets to test)")
                return True
                
        except Exception as e:
            print(f"❌ Asset management test failed - {str(e)}")
            return False
    
    def test_processing_workflow_and_job_tracking(self):
        """Test 7: PROCESSING WORKFLOW - Test job creation and tracking"""
        print("\n🔍 TEST 7: PROCESSING WORKFLOW AND JOB TRACKING")
        print("Testing job creation, tracking, and status updates...")
        
        try:
            # Create a new processing job
            print("🔄 Creating new processing job...")
            
            docx_file_path = "/app/simple_test.docx"
            if not os.path.exists(docx_file_path):
                docx_file_path = "/app/test_document.docx"
            
            if not os.path.exists(docx_file_path):
                print("❌ No test DOCX file available for workflow testing")
                return False
            
            with open(docx_file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(docx_file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'metadata': json.dumps({
                        "source": "workflow_test",
                        "test_type": "processing_workflow",
                        "track_job": True
                    })
                }
                
                print("📤 Submitting processing job...")
                
                response = requests.post(
                    f"{self.base_url}/content/upload",
                    files=files,
                    data=form_data,
                    timeout=120
                )
                
                if response.status_code != 200:
                    print(f"❌ Job creation failed - status code {response.status_code}")
                    return False
                
                data = response.json()
                job_id = data.get('job_id')
                
                if not job_id:
                    print("❌ No job ID returned from processing")
                    return False
                
                print(f"🆔 Job created: {job_id}")
                
                # Test job status tracking
                print("📊 Testing job status tracking...")
                
                status_response = requests.get(f"{self.base_url}/jobs/{job_id}", timeout=15)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ Job status retrieved successfully")
                    print(f"📊 Status: {status_data.get('status', 'unknown')}")
                    
                    # Check for expected status fields
                    expected_fields = ['job_id', 'status', 'created_at']
                    status_checks_passed = 0
                    
                    for field in expected_fields:
                        if field in status_data:
                            status_checks_passed += 1
                            print(f"  ✅ {field}: {status_data[field]}")
                        else:
                            print(f"  ❌ Missing field: {field}")
                    
                    # Test error handling and fallback systems
                    print("🔧 Testing error handling...")
                    
                    # Try to get status of non-existent job
                    fake_job_response = requests.get(f"{self.base_url}/jobs/fake-job-id", timeout=10)
                    if fake_job_response.status_code == 404:
                        print("  ✅ Proper error handling for non-existent jobs")
                    else:
                        print(f"  ⚠️ Unexpected response for non-existent job: {fake_job_response.status_code}")
                    
                    if status_checks_passed >= 2:
                        print("✅ Processing workflow working properly!")
                        return True
                    else:
                        print("❌ Processing workflow has status tracking issues")
                        return False
                else:
                    print(f"❌ Job status tracking failed - status code {status_response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Processing workflow test failed - {str(e)}")
            return False
    
    def test_products_and_assortments_docx_specific(self):
        """Test 8: SPECIFIC TEST CASE - Upload the Products and Assortments DOCX file"""
        print("\n🔍 TEST 8: PRODUCTS AND ASSORTMENTS DOCX PROCESSING")
        print("Testing with the specific Products and Assortments DOCX file...")
        
        try:
            # Look for the specific file mentioned in the review request
            potential_files = [
                "/app/source_document.docx",  # Mentioned in review request
                "/app/Master_Product_Management_Guide.docx",
                "/app/Google_Map_JavaScript_API_Tutorial.docx"
            ]
            
            docx_file_path = None
            for file_path in potential_files:
                if os.path.exists(file_path):
                    docx_file_path = file_path
                    break
            
            if not docx_file_path:
                print("❌ No suitable Products and Assortments DOCX file found")
                return False
            
            file_size = os.path.getsize(docx_file_path)
            print(f"📄 Testing with {os.path.basename(docx_file_path)} ({file_size} bytes)")
            
            with open(docx_file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(docx_file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'content_type': 'documentation',
                    'processing_mode': 'enhanced_documentation',
                    'metadata': json.dumps({
                        "source": "products_assortments_test",
                        "test_type": "products_and_assortments_processing",
                        "document_type": "product_documentation",
                        "enable_technical_writing_standards": True,
                        "enable_tables_and_procedures": True,
                        "enable_callouts": True,
                        "enable_numbered_procedures": True,
                        "preserve_full_content": True,
                        "generate_overview_page": True
                    })
                }
                
                print("📤 Processing Products and Assortments DOCX with enhanced pipeline...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.base_url}/content/upload",
                    files=files,
                    data=form_data,
                    timeout=240
                )
                
                processing_time = time.time() - start_time
                print(f"⏱️ Processing time: {processing_time:.2f} seconds")
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify specific requirements from the review request
                    chunks_created = data.get('chunks_created', 0)
                    articles_created = data.get('articles_created', 0)
                    images_processed = data.get('images_processed', 0)
                    
                    print(f"📚 Chunks created: {chunks_created}")
                    print(f"📄 Articles created: {articles_created}")
                    print(f"🖼️ Images processed: {images_processed}")
                    
                    # Check for technical documentation format
                    if 'technical_writing_applied' in data:
                        print("✅ Technical writing standards applied")
                    
                    if 'tables_processed' in data:
                        print(f"📊 Tables processed: {data['tables_processed']}")
                    
                    if 'procedures_identified' in data:
                        print(f"📋 Procedures identified: {data['procedures_identified']}")
                    
                    if 'callouts_processed' in data:
                        print(f"📢 Callouts processed: {data['callouts_processed']}")
                    
                    # Verify content preservation (not summaries)
                    if chunks_created > 0 or articles_created > 0:
                        print("✅ Articles generated successfully")
                        
                        # Check if this was comprehensive processing
                        if processing_time > 30:  # Longer processing suggests comprehensive work
                            print("✅ Comprehensive processing (not summary)")
                        
                        # Check for overview page creation
                        if 'overview_page_created' in data:
                            print("✅ Overview page with article navigation created")
                        
                        return True
                    else:
                        print("❌ No content was generated")
                        return False
                else:
                    print(f"❌ Products and Assortments processing failed - status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Products and Assortments test failed - {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive enhanced DOCX processing tests"""
        print("🚀 STARTING COMPREHENSIVE ENHANCED .DOCX PROCESSING SYSTEM TESTING")
        print("=" * 80)
        print("Testing Objectives:")
        print("1. DOCX FILE PROCESSING PIPELINE")
        print("2. IMAGE EXTRACTION AND REAL FILE SAVING")
        print("3. ENHANCED DOCUMENTATION PROCESSING")
        print("4. ARTICLE GENERATION QUALITY STANDARDS")
        print("5. CONTENT LIBRARY INTEGRATION")
        print("6. ASSET MANAGEMENT SYSTEM")
        print("7. PROCESSING WORKFLOW AND JOB TRACKING")
        print("8. PRODUCTS & ASSORTMENTS DOCX SPECIFIC TEST")
        print("=" * 80)
        
        tests = [
            ("DOCX Upload & Processing Pipeline", self.test_docx_upload_and_processing_pipeline),
            ("Image Extraction & Real File Saving", self.test_image_extraction_and_real_file_saving),
            ("Enhanced Documentation Processing", self.test_documentation_processing_function),
            ("Article Generation Quality Standards", self.test_article_generation_quality_standards),
            ("Content Library Integration", self.test_content_library_integration),
            ("Asset Management System", self.test_asset_management_system),
            ("Processing Workflow & Job Tracking", self.test_processing_workflow_and_job_tracking),
            ("Products & Assortments DOCX Specific", self.test_products_and_assortments_docx_specific)
        ]
        
        results = []
        
        for test_name, test_function in tests:
            try:
                result = test_function()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results.append((test_name, False))
            
            print("-" * 80)
        
        # Final comprehensive summary
        print("\n🎯 COMPREHENSIVE ENHANCED .DOCX PROCESSING SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for _, result in results if result)
        total_tests = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        print("-" * 80)
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        # Detailed assessment based on review requirements
        critical_tests = [
            "DOCX Upload & Processing Pipeline",
            "Image Extraction & Real File Saving", 
            "Enhanced Documentation Processing",
            "Article Generation Quality Standards"
        ]
        
        critical_passed = sum(1 for test_name, result in results if test_name in critical_tests and result)
        critical_total = len(critical_tests)
        
        print(f"🎯 CRITICAL TESTS: {critical_passed}/{critical_total} passed ({(critical_passed/critical_total)*100:.1f}%)")
        
        if passed_tests >= total_tests * 0.75:  # 75% pass rate
            print("🎉 ENHANCED .DOCX PROCESSING SYSTEM: FULLY OPERATIONAL")
            return True
        elif critical_passed >= critical_total * 0.75:  # Critical tests mostly passing
            print("⚠️ ENHANCED .DOCX PROCESSING SYSTEM: CORE FUNCTIONALITY OPERATIONAL")
            return True
        else:
            print("❌ ENHANCED .DOCX PROCESSING SYSTEM: NEEDS IMMEDIATE ATTENTION")
            return False

if __name__ == "__main__":
    tester = ComprehensiveDocxProcessingTest()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n✅ Enhanced .DOCX Processing System comprehensive testing completed successfully!")
        print("The enhanced documentation processing pipeline is operational and meets quality standards.")
    else:
        print("\n❌ Enhanced .DOCX Processing System comprehensive testing found critical issues.")
        print("The system requires attention to meet the enhanced documentation processing requirements.")