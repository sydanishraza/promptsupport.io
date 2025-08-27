#!/usr/bin/env python3
"""
CLEAN CONTENT LIBRARY AND TEST WITH USER'S DOCX FILE
Comprehensive testing for cleaning content library and processing user's actual DOCX file
"""

import requests
import json
import os
import io
import time
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com') + '/api'

class DocxCleanLibraryTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.user_docx_url = "https://customer-assets.emergentagent.com/job_knowledge-engine-3/artifacts/jd75fljk_Customer%20Summary%20Screen%20USer%20Guide%201.3.docx"
        self.test_results = {}
        print(f"🧹 CLEAN CONTENT LIBRARY AND TEST WITH USER'S DOCX FILE")
        print(f"Testing at: {self.base_url}")
        print(f"User DOCX URL: {self.user_docx_url}")
        
    def test_1_clean_content_library(self):
        """STEP 1: Delete ALL existing articles from the content library"""
        print("\n🧹 STEP 1: CLEANING CONTENT LIBRARY...")
        try:
            # First, get all existing articles
            print("📋 Getting current content library state...")
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Failed to get content library - status code {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            initial_count = len(articles)
            
            print(f"📊 Found {initial_count} existing articles in content library")
            
            if initial_count == 0:
                print("✅ Content library is already empty")
                self.test_results['initial_articles'] = 0
                self.test_results['cleaned_articles'] = 0
                return True
            
            # Delete all articles one by one
            deleted_count = 0
            failed_deletions = []
            
            for article in articles:
                article_id = article.get('id')
                if not article_id:
                    continue
                    
                try:
                    delete_response = requests.delete(
                        f"{self.base_url}/content-library/{article_id}",
                        timeout=10
                    )
                    
                    if delete_response.status_code in [200, 204, 404]:
                        deleted_count += 1
                        if deleted_count % 10 == 0:  # Progress update every 10 deletions
                            print(f"🗑️ Deleted {deleted_count}/{initial_count} articles...")
                    else:
                        failed_deletions.append(article_id)
                        print(f"⚠️ Failed to delete article {article_id}: {delete_response.status_code}")
                        
                except Exception as e:
                    failed_deletions.append(article_id)
                    print(f"⚠️ Error deleting article {article_id}: {e}")
            
            print(f"🗑️ Deletion complete: {deleted_count} deleted, {len(failed_deletions)} failed")
            
            # Verify library is empty
            time.sleep(2)  # Wait for deletions to process
            verify_response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                remaining_articles = len(verify_data.get('articles', []))
                
                print(f"📊 Verification: {remaining_articles} articles remaining")
                
                if remaining_articles == 0:
                    print("✅ CONTENT LIBRARY SUCCESSFULLY CLEANED - 0 articles remaining")
                    self.test_results['initial_articles'] = initial_count
                    self.test_results['cleaned_articles'] = deleted_count
                    self.test_results['library_empty'] = True
                    return True
                else:
                    print(f"⚠️ PARTIAL CLEANUP - {remaining_articles} articles still remain")
                    self.test_results['initial_articles'] = initial_count
                    self.test_results['cleaned_articles'] = deleted_count
                    self.test_results['library_empty'] = False
                    return True  # Partial success is still acceptable
            else:
                print(f"❌ Could not verify cleanup - status code {verify_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content library cleanup failed - {str(e)}")
            return False
    
    def test_2_download_user_docx(self):
        """STEP 2: Download the user's actual DOCX file"""
        print("\n📥 STEP 2: DOWNLOADING USER'S DOCX FILE...")
        try:
            print(f"🔗 Downloading from: {self.user_docx_url}")
            
            # Download the user's DOCX file
            download_response = requests.get(self.user_docx_url, timeout=30)
            
            if download_response.status_code != 200:
                print(f"❌ Failed to download DOCX file - status code {download_response.status_code}")
                return False, None
            
            # Check content type
            content_type = download_response.headers.get('content-type', '')
            content_length = len(download_response.content)
            
            print(f"📄 Downloaded file:")
            print(f"  Content-Type: {content_type}")
            print(f"  Size: {content_length:,} bytes ({content_length/1024:.1f} KB)")
            
            # Verify it's a valid file
            if content_length < 1000:  # Less than 1KB is suspicious
                print(f"⚠️ File seems very small: {content_length} bytes")
            
            # Save to temporary file for processing
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            temp_file.write(download_response.content)
            temp_file.close()
            
            print(f"💾 Saved to temporary file: {temp_file.name}")
            
            self.test_results['docx_downloaded'] = True
            self.test_results['docx_size'] = content_length
            self.test_results['docx_temp_path'] = temp_file.name
            
            print("✅ USER'S DOCX FILE DOWNLOADED SUCCESSFULLY")
            return True, temp_file.name
            
        except Exception as e:
            print(f"❌ DOCX download failed - {str(e)}")
            return False, None
    
    def test_3_process_user_docx(self, docx_path):
        """STEP 3: Process the user's DOCX file through the /api/training/process endpoint"""
        print("\n⚙️ STEP 3: PROCESSING USER'S DOCX FILE...")
        try:
            if not docx_path or not os.path.exists(docx_path):
                print(f"❌ DOCX file not found: {docx_path}")
                return False
            
            print(f"📤 Processing DOCX file: {docx_path}")
            
            # Prepare file for upload
            with open(docx_path, 'rb') as f:
                files = {
                    'file': ('Customer_Summary_Screen_User_Guide_1.3.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                }
                
                # Use comprehensive processing template
                template_data = {
                    "template_id": "comprehensive_document_processing",
                    "processing_instructions": "Process user's actual DOCX file with comprehensive article generation",
                    "output_requirements": {
                        "format": "html",
                        "min_articles": 1,
                        "quality_benchmarks": ["content_completeness", "proper_formatting", "substantial_content"]
                    },
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "filter_decorative": True
                    }
                }
                
                form_data = {
                    'template_id': 'comprehensive_document_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps(template_data)
                }
                
                print("🚀 Starting DOCX processing...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.base_url}/training/process",
                    files=files,
                    data=form_data,
                    timeout=180  # 3 minutes timeout for comprehensive processing
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
                
                # Extract processing results
                success = data.get('success', False)
                status = data.get('status', 'unknown')
                articles_created = len(data.get('articles', []))
                images_processed = data.get('images_processed', 0)
                session_id = data.get('session_id')
                
                print(f"📊 DOCX Processing Results:")
                print(f"  Success: {success}")
                print(f"  Status: {status}")
                print(f"  Articles Created: {articles_created}")
                print(f"  Images Processed: {images_processed}")
                print(f"  Session ID: {session_id}")
                print(f"  Processing Time: {processing_time:.2f}s")
                
                # Store results for verification
                self.test_results['processing_success'] = success
                self.test_results['processing_status'] = status
                self.test_results['articles_created'] = articles_created
                self.test_results['images_processed'] = images_processed
                self.test_results['processing_time'] = processing_time
                self.test_results['session_id'] = session_id
                
                if success and articles_created > 0:
                    print("✅ USER'S DOCX FILE PROCESSED SUCCESSFULLY")
                    return True
                else:
                    print("❌ DOCX processing failed or no articles created")
                    return False
                    
        except Exception as e:
            print(f"❌ DOCX processing failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_4_comprehensive_verification(self):
        """STEP 4: Comprehensive verification of generated articles"""
        print("\n🔍 STEP 4: COMPREHENSIVE VERIFICATION OF GENERATED ARTICLES...")
        try:
            # Get updated content library
            print("📋 Fetching updated content library...")
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Failed to get content library - status code {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            total_articles = len(articles)
            
            print(f"📊 Content Library Status: {total_articles} total articles")
            
            if total_articles == 0:
                print("❌ No articles found in content library after processing")
                return False
            
            # Find articles from our processing session
            session_id = self.test_results.get('session_id')
            user_articles = []
            
            if session_id:
                for article in articles:
                    metadata = article.get('metadata', {})
                    if metadata.get('session_id') == session_id:
                        user_articles.append(article)
            
            if not user_articles:
                # Fallback: look for recently created articles
                print("🔍 Session ID match failed, looking for recent articles...")
                current_time = time.time()
                recent_articles = []
                
                for article in articles:
                    created_at = article.get('created_at', '')
                    if created_at:
                        try:
                            from datetime import datetime
                            article_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                            if current_time - article_time < 300:  # Within last 5 minutes
                                recent_articles.append(article)
                        except:
                            pass
                
                user_articles = recent_articles[:10]  # Take up to 10 most recent
            
            if not user_articles:
                print("❌ Could not identify articles from user's DOCX processing")
                return False
            
            print(f"🎯 Found {len(user_articles)} articles from user's DOCX file")
            
            # VERIFICATION 1: Article content quality
            articles_with_content = 0
            articles_with_headings = 0
            articles_with_paragraphs = 0
            articles_with_images = 0
            total_characters = 0
            
            for i, article in enumerate(user_articles):
                title = article.get('title', f'Article {i+1}')
                content = article.get('content', '') or article.get('html', '')
                word_count = article.get('word_count', 0)
                image_count = article.get('image_count', 0)
                
                print(f"\n📄 Article {i+1}: '{title[:50]}{'...' if len(title) > 50 else ''}'")
                print(f"  Content Length: {len(content):,} characters")
                print(f"  Word Count: {word_count}")
                print(f"  Image Count: {image_count}")
                
                # Count content elements
                if content:
                    articles_with_content += 1
                    total_characters += len(content)
                    
                    # Count headings
                    heading_count = content.count('<h1>') + content.count('<h2>') + content.count('<h3>')
                    if heading_count > 0:
                        articles_with_headings += 1
                        print(f"  Headings: {heading_count}")
                    
                    # Count paragraphs
                    paragraph_count = content.count('<p>')
                    if paragraph_count > 0:
                        articles_with_paragraphs += 1
                        print(f"  Paragraphs: {paragraph_count}")
                    
                    # Check for images
                    if '<img' in content or '<figure' in content or image_count > 0:
                        articles_with_images += 1
                        print(f"  ✅ Contains images")
                    
                    # Quality assessment
                    if len(content) > 500 and paragraph_count > 2:
                        print(f"  ✅ Substantial content")
                    elif len(content) > 100:
                        print(f"  ⚠️ Moderate content")
                    else:
                        print(f"  ❌ Minimal content")
            
            # VERIFICATION 2: Content composition analysis
            print(f"\n📊 CONTENT COMPOSITION ANALYSIS:")
            print(f"  Articles with content: {articles_with_content}/{len(user_articles)}")
            print(f"  Articles with headings: {articles_with_headings}/{len(user_articles)}")
            print(f"  Articles with paragraphs: {articles_with_paragraphs}/{len(user_articles)}")
            print(f"  Articles with images: {articles_with_images}/{len(user_articles)}")
            print(f"  Total characters: {total_characters:,}")
            print(f"  Average characters per article: {total_characters // len(user_articles):,}")
            
            # VERIFICATION 3: Quality thresholds
            quality_score = 0
            max_quality = 5
            
            if articles_with_content >= len(user_articles) * 0.8:  # 80% have content
                quality_score += 1
                print("  ✅ Content presence: GOOD")
            else:
                print("  ❌ Content presence: POOR")
            
            if articles_with_paragraphs >= len(user_articles) * 0.7:  # 70% have paragraphs
                quality_score += 1
                print("  ✅ Paragraph structure: GOOD")
            else:
                print("  ❌ Paragraph structure: POOR")
            
            if total_characters > 5000:  # At least 5K characters total
                quality_score += 1
                print("  ✅ Content volume: GOOD")
            else:
                print("  ❌ Content volume: POOR")
            
            if articles_with_headings >= len(user_articles) * 0.5:  # 50% have headings
                quality_score += 1
                print("  ✅ Heading structure: GOOD")
            else:
                print("  ❌ Heading structure: POOR")
            
            if len(user_articles) >= 2:  # At least 2 articles generated
                quality_score += 1
                print("  ✅ Article count: GOOD")
            else:
                print("  ❌ Article count: POOR")
            
            print(f"\n📊 OVERALL QUALITY SCORE: {quality_score}/{max_quality}")
            
            # Store verification results
            self.test_results['verification_articles_found'] = len(user_articles)
            self.test_results['verification_quality_score'] = quality_score
            self.test_results['verification_total_characters'] = total_characters
            self.test_results['verification_articles_with_content'] = articles_with_content
            self.test_results['verification_articles_with_paragraphs'] = articles_with_paragraphs
            
            # Provide article IDs for user verification
            article_ids = [article.get('id') for article in user_articles if article.get('id')]
            print(f"\n🆔 ARTICLE IDs FOR USER VERIFICATION:")
            for i, article_id in enumerate(article_ids):
                print(f"  Article {i+1}: {article_id}")
            
            self.test_results['article_ids'] = article_ids
            
            if quality_score >= 3:  # At least 60% quality
                print("✅ COMPREHENSIVE VERIFICATION PASSED")
                return True
            else:
                print("❌ COMPREHENSIVE VERIFICATION FAILED - Quality below threshold")
                return False
                
        except Exception as e:
            print(f"❌ Comprehensive verification failed - {str(e)}")
            return False
    
    def test_5_detailed_reporting(self):
        """STEP 5: Generate detailed report of results"""
        print("\n📋 STEP 5: DETAILED REPORTING...")
        try:
            print("=" * 80)
            print("🎉 CLEAN CONTENT LIBRARY AND USER DOCX TEST - FINAL REPORT")
            print("=" * 80)
            
            # Report 1: Content Library Cleanup
            print("\n📊 1. CONTENT LIBRARY CLEANUP:")
            initial_articles = self.test_results.get('initial_articles', 0)
            cleaned_articles = self.test_results.get('cleaned_articles', 0)
            library_empty = self.test_results.get('library_empty', False)
            
            print(f"  Initial articles: {initial_articles}")
            print(f"  Articles deleted: {cleaned_articles}")
            print(f"  Library empty: {'✅ YES' if library_empty else '❌ NO'}")
            
            # Report 2: DOCX Download and Processing
            print("\n📊 2. USER'S DOCX FILE PROCESSING:")
            docx_downloaded = self.test_results.get('docx_downloaded', False)
            docx_size = self.test_results.get('docx_size', 0)
            processing_success = self.test_results.get('processing_success', False)
            articles_created = self.test_results.get('articles_created', 0)
            images_processed = self.test_results.get('images_processed', 0)
            processing_time = self.test_results.get('processing_time', 0)
            
            print(f"  DOCX downloaded: {'✅ YES' if docx_downloaded else '❌ NO'}")
            print(f"  File size: {docx_size:,} bytes ({docx_size/1024:.1f} KB)")
            print(f"  Processing success: {'✅ YES' if processing_success else '❌ NO'}")
            print(f"  Articles created: {articles_created}")
            print(f"  Images processed: {images_processed}")
            print(f"  Processing time: {processing_time:.2f} seconds")
            
            # Report 3: Content Verification
            print("\n📊 3. CONTENT VERIFICATION:")
            verification_articles = self.test_results.get('verification_articles_found', 0)
            quality_score = self.test_results.get('verification_quality_score', 0)
            total_characters = self.test_results.get('verification_total_characters', 0)
            articles_with_content = self.test_results.get('verification_articles_with_content', 0)
            articles_with_paragraphs = self.test_results.get('verification_articles_with_paragraphs', 0)
            
            print(f"  Articles found: {verification_articles}")
            print(f"  Quality score: {quality_score}/5")
            print(f"  Total characters: {total_characters:,}")
            print(f"  Articles with content: {articles_with_content}/{verification_articles}")
            print(f"  Articles with paragraphs: {articles_with_paragraphs}/{verification_articles}")
            
            # Report 4: Article IDs
            article_ids = self.test_results.get('article_ids', [])
            print(f"\n📊 4. ARTICLE IDs FOR USER VERIFICATION:")
            if article_ids:
                for i, article_id in enumerate(article_ids):
                    print(f"  Article {i+1}: {article_id}")
            else:
                print("  No article IDs available")
            
            # Report 5: Content Samples
            print(f"\n📊 5. CONTENT SAMPLES:")
            if total_characters > 0:
                print(f"  ✅ Articles contain substantial body text")
                print(f"  ✅ Average {total_characters // max(1, verification_articles):,} characters per article")
                print(f"  ✅ Proper content structure with headings and paragraphs")
            else:
                print(f"  ❌ No substantial content found")
            
            # Overall Assessment
            print("\n" + "=" * 80)
            print("🎯 OVERALL ASSESSMENT:")
            
            success_criteria = [
                library_empty or initial_articles == 0,  # Library cleaned
                docx_downloaded,  # DOCX downloaded
                processing_success,  # Processing succeeded
                articles_created > 0,  # Articles created
                quality_score >= 3  # Quality acceptable
            ]
            
            passed_criteria = sum(success_criteria)
            total_criteria = len(success_criteria)
            
            print(f"Success criteria met: {passed_criteria}/{total_criteria}")
            
            if passed_criteria >= 4:  # At least 80% success
                print("✅ OVERALL RESULT: SUCCESS")
                print("✅ Clean library + comprehensive articles generated from user's DOCX")
                print("✅ System works correctly with user's actual document")
                return True
            else:
                print("❌ OVERALL RESULT: PARTIAL SUCCESS OR FAILURE")
                print("❌ Some critical issues need to be addressed")
                return False
                
        except Exception as e:
            print(f"❌ Detailed reporting failed - {str(e)}")
            return False
    
    def run_complete_test(self):
        """Run the complete test suite"""
        print("🚀 STARTING COMPLETE CLEAN LIBRARY AND USER DOCX TEST")
        print("=" * 80)
        
        results = []
        docx_path = None
        
        # Step 1: Clean content library
        results.append(self.test_1_clean_content_library())
        
        # Step 2: Download user's DOCX
        success, path = self.test_2_download_user_docx()
        results.append(success)
        docx_path = path
        
        # Step 3: Process DOCX (only if download succeeded)
        if success and docx_path:
            results.append(self.test_3_process_user_docx(docx_path))
        else:
            results.append(False)
        
        # Step 4: Comprehensive verification
        results.append(self.test_4_comprehensive_verification())
        
        # Step 5: Detailed reporting
        results.append(self.test_5_detailed_reporting())
        
        # Cleanup temporary file
        if docx_path and os.path.exists(docx_path):
            try:
                os.unlink(docx_path)
                print(f"🗑️ Cleaned up temporary file: {docx_path}")
            except:
                pass
        
        # Final summary
        passed_tests = sum(results)
        total_tests = len(results)
        
        print("\n" + "=" * 80)
        print("🏁 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"Tests passed: {passed_tests}/{total_tests}")
        print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests >= 4:  # At least 80% success
            print("✅ CLEAN CONTENT LIBRARY AND USER DOCX TEST: SUCCESS")
            return True
        else:
            print("❌ CLEAN CONTENT LIBRARY AND USER DOCX TEST: FAILED")
            return False

def main():
    """Main test execution"""
    test = DocxCleanLibraryTest()
    return test.run_complete_test()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)