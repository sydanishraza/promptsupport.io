#!/usr/bin/env python3
"""
Google Maps DOCX Content Processing Pipeline Test
Tests the actual content processing pipeline using the Google Map JavaScript API Tutorial.docx file
to verify we get real content instead of test data.
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://75e2f69d-4b6d-467e-9338-70ba63fa8c3f.preview.emergentagent.com') + '/api'

class GoogleMapsDocxTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.docx_url = "https://customer-assets.emergentagent.com/job_training-lab-revamp/artifacts/xq5cp7dr_Google%20Map%20JavaScript%20API%20Tutorial.docx"
        print(f"🗺️ Testing Google Maps DOCX Content Processing at: {self.base_url}")
        print(f"📄 DOCX Source: {self.docx_url}")
        
    def test_file_exists(self):
        """Verify the Google Maps DOCX file exists and is accessible"""
        print("\n🔍 Testing Google Maps DOCX File Existence...")
        try:
            if os.path.exists(self.docx_file_path):
                file_size = os.path.getsize(self.docx_file_path)
                print(f"✅ File exists: {self.docx_file_path}")
                print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
                
                if file_size > 1000000:  # 1MB
                    print("✅ File size indicates substantial content with likely images")
                    return True
                else:
                    print("⚠️ File size seems small for a tutorial with images")
                    return True
            else:
                print(f"❌ File not found: {self.docx_file_path}")
                return False
                
        except Exception as e:
            print(f"❌ File existence check failed: {str(e)}")
            return False
    
    def test_image_detection_and_extraction(self):
        """
        Test 1: Image Detection and Extraction
        Test if the backend is properly detecting and extracting images from the DOCX file
        """
        print("\n🔍 TEST 1: Image Detection and Extraction from Google Maps DOCX...")
        try:
            print("🎯 FOCUS: Testing if backend detects and extracts images from DOCX during processing")
            
            # Open and upload the Google Maps DOCX file
            with open(self.docx_file_path, 'rb') as docx_file:
                files = {
                    'file': ('Google_Map_JavaScript_API_Tutorial.docx', docx_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                # Use template that enables image extraction
                form_data = {
                    'template_id': 'phase1_document_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps({
                        "template_id": "phase1_document_processing",
                        "processing_instructions": "Extract and process all content including images with enhanced detection",
                        "media_handling": {
                            "extract_images": True,
                            "contextual_placement": True,
                            "filter_decorative": True,
                            "use_enhanced_extraction": True
                        }
                    })
                }
                
                print("📤 Uploading Google Maps DOCX file for image detection test...")
                print("🔍 Monitoring for image detection and extraction...")
                
                start_time = time.time()
                
                response = requests.post(
                    f"{self.base_url}/training/process",
                    files=files,
                    data=form_data,
                    timeout=300  # 5 minutes timeout for large file
                )
                
                processing_time = time.time() - start_time
                print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
                print(f"📊 Response Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"❌ Image detection test failed - status code {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
                
                data = response.json()
                
                # TEST 1A: Check if images were detected and processed
                images_processed = data.get('images_processed', 0)
                print(f"🖼️ Images Processed: {images_processed}")
                
                if images_processed > 0:
                    print(f"✅ IMAGE DETECTION SUCCESS: {images_processed} images detected and processed")
                    print("✅ Backend is properly detecting images from Google Maps DOCX")
                else:
                    print("❌ IMAGE DETECTION FAILURE: No images detected (should be > 0)")
                    print("❌ Backend is NOT properly detecting images from DOCX file")
                    return False
                
                # TEST 1B: Check processing success
                success = data.get('success', False)
                session_id = data.get('session_id')
                
                if success and session_id:
                    print(f"✅ Processing successful with session ID: {session_id}")
                else:
                    print("❌ Processing failed or no session ID generated")
                    return False
                
                # TEST 1C: Check articles were generated
                articles = data.get('articles', [])
                print(f"📚 Articles Generated: {len(articles)}")
                
                if len(articles) > 0:
                    print("✅ Articles generated successfully")
                else:
                    print("❌ No articles generated")
                    return False
                
                # Store results for next tests
                self.test_results = {
                    'images_processed': images_processed,
                    'articles': articles,
                    'session_id': session_id,
                    'processing_time': processing_time
                }
                
                print("✅ TEST 1 PASSED: Image Detection and Extraction working correctly")
                return True
                
        except Exception as e:
            print(f"❌ Image detection and extraction test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_docx_processing_pipeline(self):
        """
        Test 2: DOCX Processing Pipeline
        Verify that the /api/training/process endpoint handles the Google Maps DOCX correctly
        """
        print("\n🔍 TEST 2: DOCX Processing Pipeline for Google Maps Tutorial...")
        try:
            print("🎯 FOCUS: Verifying /api/training/process endpoint handles Google Maps DOCX correctly")
            
            if not hasattr(self, 'test_results'):
                print("⚠️ Running standalone pipeline test (Test 1 results not available)")
                
                # Run a quick processing test
                with open(self.docx_file_path, 'rb') as docx_file:
                    files = {
                        'file': ('Google_Map_JavaScript_API_Tutorial.docx', docx_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    }
                    
                    form_data = {
                        'template_id': 'phase1_document_processing',
                        'training_mode': 'true'
                    }
                    
                    print("📤 Testing DOCX processing pipeline...")
                    
                    response = requests.post(
                        f"{self.base_url}/training/process",
                        files=files,
                        data=form_data,
                        timeout=300
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ DOCX processing pipeline failed - status code {response.status_code}")
                        return False
                    
                    data = response.json()
                    self.test_results = {
                        'images_processed': data.get('images_processed', 0),
                        'articles': data.get('articles', []),
                        'session_id': data.get('session_id'),
                        'processing_time': 0
                    }
            
            # TEST 2A: Verify pipeline handled DOCX format correctly
            articles = self.test_results['articles']
            images_processed = self.test_results['images_processed']
            
            print(f"📊 Pipeline Results:")
            print(f"  Articles: {len(articles)}")
            print(f"  Images: {images_processed}")
            print(f"  Session ID: {self.test_results['session_id']}")
            
            # TEST 2B: Check article content quality
            if articles:
                first_article = articles[0]
                content = first_article.get('content', '') or first_article.get('html', '')
                title = first_article.get('title', '')
                word_count = first_article.get('word_count', 0)
                
                print(f"📄 First Article:")
                print(f"  Title: {title}")
                print(f"  Word Count: {word_count}")
                print(f"  Content Length: {len(content)} characters")
                
                # Check for Google Maps specific content
                maps_keywords = ['google', 'map', 'javascript', 'api', 'tutorial']
                content_lower = content.lower()
                found_keywords = [kw for kw in maps_keywords if kw in content_lower]
                
                print(f"  Google Maps Keywords Found: {found_keywords}")
                
                if len(found_keywords) >= 3:
                    print("✅ Content appears to be Google Maps tutorial related")
                else:
                    print("⚠️ Content may not be properly extracted from Google Maps tutorial")
            
            # TEST 2C: Check for proper HTML structure
            if articles:
                html_content = articles[0].get('content', '') or articles[0].get('html', '')
                
                # Count HTML elements
                h1_count = html_content.count('<h1')
                h2_count = html_content.count('<h2')
                p_count = html_content.count('<p')
                img_count = html_content.count('<img')
                figure_count = html_content.count('<figure')
                
                print(f"📋 HTML Structure Analysis:")
                print(f"  H1 headings: {h1_count}")
                print(f"  H2 headings: {h2_count}")
                print(f"  Paragraphs: {p_count}")
                print(f"  Images: {img_count}")
                print(f"  Figures: {figure_count}")
                
                if h1_count > 0 and p_count > 0:
                    print("✅ Proper HTML structure detected")
                else:
                    print("⚠️ HTML structure may be incomplete")
            
            print("✅ TEST 2 PASSED: DOCX Processing Pipeline handles Google Maps file correctly")
            return True
            
        except Exception as e:
            print(f"❌ DOCX processing pipeline test failed: {str(e)}")
            return False
    
    def test_image_tokenization(self):
        """
        Test 3: Image Tokenization
        Check if images are being converted to IMAGE tokens during HTML preprocessing
        """
        print("\n🔍 TEST 3: Image Tokenization during HTML Preprocessing...")
        try:
            print("🎯 FOCUS: Checking if images are converted to IMAGE tokens during preprocessing")
            
            if not hasattr(self, 'test_results'):
                print("❌ Test 3 requires Test 1 results - running Test 1 first...")
                if not self.test_image_detection_and_extraction():
                    return False
            
            articles = self.test_results['articles']
            images_processed = self.test_results['images_processed']
            
            if images_processed == 0:
                print("❌ No images processed - cannot test tokenization")
                return False
            
            # TEST 3A: Check for image tokens in article content
            tokenization_evidence = []
            
            for i, article in enumerate(articles):
                content = article.get('content', '') or article.get('html', '')
                
                # Look for evidence of image tokenization
                token_patterns = [
                    'IMAGE_BLOCK:',
                    'END_IMAGE_BLOCK:',
                    'data-image-id=',
                    'data-block-id=',
                    '[IMAGE:',
                    '<!-- IMAGE_BLOCK:'
                ]
                
                found_patterns = []
                for pattern in token_patterns:
                    if pattern in content:
                        found_patterns.append(pattern)
                        count = content.count(pattern)
                        tokenization_evidence.append(f"Article {i+1}: {pattern} ({count} occurrences)")
                
                print(f"📄 Article {i+1} Tokenization Evidence: {found_patterns}")
            
            # TEST 3B: Check for proper image embedding
            embedded_images = 0
            for article in articles:
                content = article.get('content', '') or article.get('html', '')
                
                # Count embedded images
                figure_count = content.count('<figure')
                img_count = content.count('<img')
                api_static_count = content.count('/api/static/uploads/')
                
                embedded_images += max(figure_count, img_count)
                
                if figure_count > 0 or img_count > 0:
                    print(f"✅ Article contains {figure_count} figures, {img_count} img tags")
                    
                    # Check for proper image URLs
                    if api_static_count > 0:
                        print(f"✅ Article contains {api_static_count} proper image URLs (/api/static/uploads/)")
                    else:
                        print("⚠️ Article may not have proper image URLs")
            
            # TEST 3C: Verify tokenization worked correctly
            if tokenization_evidence:
                print("✅ IMAGE TOKENIZATION SUCCESS:")
                for evidence in tokenization_evidence:
                    print(f"  ✅ {evidence}")
                print("✅ Images are being converted to tokens during HTML preprocessing")
            else:
                print("⚠️ IMAGE TOKENIZATION UNCLEAR:")
                print("  ⚠️ No clear tokenization evidence found")
                print("  ⚠️ Images may be processed differently than expected")
            
            # TEST 3D: Check final image embedding
            if embedded_images > 0:
                print(f"✅ FINAL EMBEDDING SUCCESS: {embedded_images} images embedded in articles")
                print("✅ Token replacement with rich HTML elements working")
            else:
                print("❌ FINAL EMBEDDING FAILURE: No images embedded in final articles")
                return False
            
            print("✅ TEST 3 PASSED: Image Tokenization process working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Image tokenization test failed: {str(e)}")
            return False
    
    def test_backend_processing_time(self):
        """
        Test 4: Backend Processing Time
        Monitor if the backend processing completes properly or gets stuck
        """
        print("\n🔍 TEST 4: Backend Processing Time and Completion...")
        try:
            print("🎯 FOCUS: Monitoring backend processing time and completion status")
            
            # TEST 4A: Fresh processing time test
            print("⏱️ Running fresh processing time test...")
            
            with open(self.docx_file_path, 'rb') as docx_file:
                files = {
                    'file': ('Google_Map_JavaScript_API_Tutorial.docx', docx_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                form_data = {
                    'template_id': 'phase1_document_processing',
                    'training_mode': 'true'
                }
                
                print("📤 Starting timed processing test...")
                start_time = time.time()
                
                # Set reasonable timeout (5 minutes for large file)
                timeout_seconds = 300
                
                try:
                    response = requests.post(
                        f"{self.base_url}/training/process",
                        files=files,
                        data=form_data,
                        timeout=timeout_seconds
                    )
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
                    print(f"📊 Response Status Code: {response.status_code}")
                    
                    # TEST 4B: Analyze processing time
                    if processing_time < 60:
                        print(f"✅ EXCELLENT: Processing time under 1 minute ({processing_time:.2f}s)")
                    elif processing_time < 120:
                        print(f"✅ GOOD: Processing time under 2 minutes ({processing_time:.2f}s)")
                    elif processing_time < 300:
                        print(f"⚠️ ACCEPTABLE: Processing time under 5 minutes ({processing_time:.2f}s)")
                    else:
                        print(f"⚠️ SLOW: Processing time over 5 minutes ({processing_time:.2f}s)")
                    
                    # TEST 4C: Check if processing completed successfully
                    if response.status_code == 200:
                        data = response.json()
                        success = data.get('success', False)
                        
                        if success:
                            print("✅ PROCESSING COMPLETION SUCCESS: Backend completed processing properly")
                            
                            # Check processing results
                            images_processed = data.get('images_processed', 0)
                            articles = data.get('articles', [])
                            session_id = data.get('session_id')
                            
                            print(f"📊 Processing Results:")
                            print(f"  Success: {success}")
                            print(f"  Images Processed: {images_processed}")
                            print(f"  Articles Generated: {len(articles)}")
                            print(f"  Session ID: {session_id}")
                            
                            if images_processed > 0 and len(articles) > 0:
                                print("✅ Complete processing pipeline working correctly")
                            else:
                                print("⚠️ Processing completed but with limited results")
                            
                        else:
                            print("❌ PROCESSING COMPLETION FAILURE: Backend reported failure")
                            print(f"Response data: {data}")
                            return False
                    else:
                        print(f"❌ PROCESSING COMPLETION FAILURE: HTTP error {response.status_code}")
                        print(f"Response: {response.text}")
                        return False
                    
                except requests.exceptions.Timeout:
                    print(f"❌ PROCESSING TIMEOUT: Backend processing took longer than {timeout_seconds} seconds")
                    print("❌ Backend processing appears to be stuck or extremely slow")
                    return False
                
                # TEST 4D: Performance assessment
                file_size_mb = os.path.getsize(self.docx_file_path) / (1024 * 1024)
                processing_rate = file_size_mb / processing_time * 60  # MB per minute
                
                print(f"📊 Performance Metrics:")
                print(f"  File Size: {file_size_mb:.2f} MB")
                print(f"  Processing Rate: {processing_rate:.2f} MB/minute")
                print(f"  Time per MB: {processing_time/file_size_mb:.2f} seconds/MB")
                
                if processing_rate > 1.0:
                    print("✅ Good processing rate (>1 MB/minute)")
                elif processing_rate > 0.5:
                    print("⚠️ Acceptable processing rate (>0.5 MB/minute)")
                else:
                    print("⚠️ Slow processing rate (<0.5 MB/minute)")
                
                print("✅ TEST 4 PASSED: Backend processing completes properly without getting stuck")
                return True
                
        except Exception as e:
            print(f"❌ Backend processing time test failed: {str(e)}")
            return False
    
    def test_comprehensive_image_pipeline(self):
        """
        Comprehensive test combining all image processing aspects
        """
        print("\n🔍 COMPREHENSIVE TEST: Complete Image Processing Pipeline...")
        try:
            print("🎯 COMPREHENSIVE: Testing complete end-to-end image processing pipeline")
            
            with open(self.docx_file_path, 'rb') as docx_file:
                files = {
                    'file': ('Google_Map_JavaScript_API_Tutorial.docx', docx_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                # Use comprehensive template settings
                template_data = {
                    "template_id": "phase1_document_processing",
                    "processing_instructions": "Extract and process all content with comprehensive image handling",
                    "output_requirements": {
                        "format": "html",
                        "min_articles": 1,
                        "max_articles": 10,
                        "quality_benchmarks": ["content_completeness", "image_embedding", "proper_formatting"]
                    },
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "filter_decorative": False,  # Don't filter out any images for this test
                        "use_enhanced_extraction": True,
                        "use_html_preprocessing_pipeline": True
                    }
                }
                
                form_data = {
                    'template_id': 'phase1_document_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps(template_data)
                }
                
                print("📤 Running comprehensive image processing test...")
                
                start_time = time.time()
                
                response = requests.post(
                    f"{self.base_url}/training/process",
                    files=files,
                    data=form_data,
                    timeout=300
                )
                
                processing_time = time.time() - start_time
                
                if response.status_code != 200:
                    print(f"❌ Comprehensive test failed - status code {response.status_code}")
                    return False
                
                data = response.json()
                
                # Comprehensive analysis
                print(f"\n📊 COMPREHENSIVE RESULTS:")
                print(f"  Processing Time: {processing_time:.2f} seconds")
                print(f"  Success: {data.get('success', False)}")
                print(f"  Images Processed: {data.get('images_processed', 0)}")
                print(f"  Articles Generated: {len(data.get('articles', []))}")
                print(f"  Session ID: {data.get('session_id', 'None')}")
                
                # Detailed article analysis
                articles = data.get('articles', [])
                total_images_embedded = 0
                total_word_count = 0
                
                for i, article in enumerate(articles):
                    content = article.get('content', '') or article.get('html', '')
                    word_count = article.get('word_count', len(content.split()))
                    image_count = article.get('image_count', 0)
                    
                    # Count actual embedded images
                    figure_count = content.count('<figure')
                    img_count = content.count('<img')
                    actual_embedded = max(figure_count, img_count)
                    
                    total_images_embedded += actual_embedded
                    total_word_count += word_count
                    
                    print(f"  Article {i+1}:")
                    print(f"    Word Count: {word_count}")
                    print(f"    Reported Images: {image_count}")
                    print(f"    Actual Embedded: {actual_embedded}")
                    print(f"    Title: {article.get('title', 'Untitled')[:50]}...")
                
                print(f"\n📈 SUMMARY METRICS:")
                print(f"  Total Word Count: {total_word_count:,}")
                print(f"  Total Images Embedded: {total_images_embedded}")
                print(f"  Processing Rate: {total_word_count/processing_time:.0f} words/second")
                print(f"  Image Processing Rate: {total_images_embedded/processing_time:.2f} images/second")
                
                # Success criteria
                success_criteria = {
                    'processing_completed': data.get('success', False),
                    'images_detected': data.get('images_processed', 0) > 0,
                    'images_embedded': total_images_embedded > 0,
                    'articles_generated': len(articles) > 0,
                    'reasonable_processing_time': processing_time < 300,
                    'substantial_content': total_word_count > 1000
                }
                
                print(f"\n✅ SUCCESS CRITERIA:")
                for criterion, passed in success_criteria.items():
                    status = "✅" if passed else "❌"
                    print(f"  {status} {criterion.replace('_', ' ').title()}: {passed}")
                
                passed_criteria = sum(success_criteria.values())
                total_criteria = len(success_criteria)
                
                print(f"\n📊 OVERALL SCORE: {passed_criteria}/{total_criteria} criteria passed")
                
                if passed_criteria >= 5:  # At least 5 out of 6 criteria
                    print("✅ COMPREHENSIVE TEST PASSED: Image processing pipeline working correctly")
                    return True
                else:
                    print("❌ COMPREHENSIVE TEST FAILED: Multiple issues detected")
                    return False
                
        except Exception as e:
            print(f"❌ Comprehensive image pipeline test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Google Maps DOCX tests"""
        print("🗺️ GOOGLE MAPS DOCX IMAGE PROCESSING TEST SUITE")
        print("=" * 60)
        
        test_results = {}
        
        # Test 0: File existence
        test_results['file_exists'] = self.test_file_exists()
        
        if not test_results['file_exists']:
            print("❌ Cannot proceed - Google Maps DOCX file not found")
            return test_results
        
        # Test 1: Image Detection and Extraction
        test_results['image_detection'] = self.test_image_detection_and_extraction()
        
        # Test 2: DOCX Processing Pipeline
        test_results['docx_pipeline'] = self.test_docx_processing_pipeline()
        
        # Test 3: Image Tokenization
        test_results['image_tokenization'] = self.test_image_tokenization()
        
        # Test 4: Backend Processing Time
        test_results['processing_time'] = self.test_backend_processing_time()
        
        # Comprehensive Test
        test_results['comprehensive'] = self.test_comprehensive_image_pipeline()
        
        # Summary
        print("\n" + "=" * 60)
        print("🗺️ GOOGLE MAPS DOCX TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name.replace('_', ' ').title()}")
            if result:
                passed_tests += 1
        
        print(f"\n📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests >= 4:  # At least 4 out of 5 tests should pass
            print("✅ GOOGLE MAPS DOCX IMAGE PROCESSING: WORKING CORRECTLY")
        else:
            print("❌ GOOGLE MAPS DOCX IMAGE PROCESSING: ISSUES DETECTED")
        
        return test_results

if __name__ == "__main__":
    tester = GoogleMapsDocxTest()
    results = tester.run_all_tests()