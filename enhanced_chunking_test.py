#!/usr/bin/env python3
"""
Enhanced DOCX Chunking Fix Testing
Test the enhanced chunking fix that should detect H2 structure and create multiple articles
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

class EnhancedChunkingTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"Testing Enhanced DOCX Chunking at: {self.base_url}")
        
    def test_clear_content_library(self):
        """Clear the current content library (1 article currently)"""
        print("🧹 Testing Content Library Cleanup...")
        try:
            # First, get current articles
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                current_count = len(articles)
                print(f"📊 Current Content Library: {current_count} articles")
                
                if current_count == 0:
                    print("✅ Content Library already empty")
                    return True
                
                # Delete all articles
                deleted_count = 0
                for article in articles:
                    article_id = article.get('id')
                    if article_id:
                        try:
                            delete_response = requests.delete(f"{self.base_url}/content-library/{article_id}", timeout=10)
                            if delete_response.status_code in [200, 204]:
                                deleted_count += 1
                                print(f"🗑️ Deleted article: {article.get('title', 'Unknown')}")
                            else:
                                print(f"⚠️ Failed to delete article {article_id}: {delete_response.status_code}")
                        except Exception as e:
                            print(f"⚠️ Error deleting article {article_id}: {e}")
                
                print(f"✅ Content Library cleanup complete: {deleted_count}/{current_count} articles deleted")
                return True
            else:
                print(f"❌ Failed to get content library - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content library cleanup failed - {str(e)}")
            return False
    
    def test_download_user_docx_file(self):
        """Download the user's DOCX file for testing"""
        print("📥 Testing User's DOCX File Download...")
        try:
            docx_url = "https://customer-assets.emergentagent.com/job_knowledge-engine-3/artifacts/jd75fljk_Customer%20Summary%20Screen%20USer%20Guide%201.3.docx"
            
            print(f"🔗 Downloading from: {docx_url}")
            
            response = requests.get(docx_url, timeout=30)
            
            if response.status_code == 200:
                file_size = len(response.content)
                print(f"✅ Successfully downloaded DOCX file: {file_size} bytes ({file_size/1024/1024:.1f} MB)")
                
                # Verify it's a valid DOCX file
                content_type = response.headers.get('content-type', '')
                if 'application' in content_type or file_size > 1000000:  # At least 1MB
                    print(f"✅ File appears to be valid DOCX format")
                    return response.content
                else:
                    print(f"⚠️ File may not be DOCX format: {content_type}")
                    return response.content  # Still try to process
            else:
                print(f"❌ Failed to download DOCX file - status code {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ DOCX file download failed - {str(e)}")
            return None
    
    def test_enhanced_chunking_processing(self, docx_content):
        """Test the enhanced chunking with the user's DOCX file"""
        print("🎯 Testing Enhanced DOCX Chunking Fix...")
        try:
            print("🔍 CRITICAL TEST: Enhanced H1 AND H2 Detection for chunking")
            print("📊 Expected: Multiple articles based on H2 headings (common in user guides)")
            print("🖼️ Expected: 204 images properly extracted")
            print("📄 Expected: Each article with substantial content, not just headings")
            
            # Create file upload
            files = {
                'file': ('Customer_Summary_Screen_User_Guide_1.3.docx', docx_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Add required form data for training/process endpoint
            form_data = {
                'template_id': 'enhanced_chunking_test',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "enhanced_chunking_test",
                    "processing_instructions": "Test enhanced H1 AND H2 detection for chunking",
                    "output_requirements": {
                        "format": "html",
                        "min_articles": 2,
                        "max_articles": 10,
                        "quality_benchmarks": ["content_completeness", "proper_chunking", "h2_detection"]
                    },
                    "media_handling": {
                        "extract_images": True,
                        "contextual_placement": True,
                        "filter_decorative": True
                    }
                })
            }
            
            # Use training/process endpoint as specified in the review
            print("📤 Processing user's DOCX file with enhanced chunking...")
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=300  # 5 minutes for large file processing
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Enhanced chunking processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📋 Processing Response Keys: {list(data.keys())}")
            
            return self._verify_enhanced_chunking_results(data, processing_time)
            
        except Exception as e:
            print(f"❌ Enhanced chunking processing failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _verify_enhanced_chunking_results(self, data, processing_time):
        """Verify the enhanced chunking results meet expectations"""
        print("\n🔍 ENHANCED CHUNKING VERIFICATION:")
        
        # Test 1: Processing Success
        success = data.get('success', False) or data.get('status') == 'completed'
        print(f"✅ Processing Success: {success}")
        
        if not success:
            print("❌ CRITICAL FAILURE: Processing did not complete successfully")
            return False
        
        # Test 2: Multiple Articles Created (Key Enhancement)
        articles_created = data.get('chunks_created', 0) or len(data.get('articles', []))
        print(f"📚 Articles Created: {articles_created}")
        
        if articles_created <= 1:
            print("❌ CRITICAL FAILURE: Enhanced chunking should create MULTIPLE articles")
            print("❌ This indicates H2 detection is not working properly")
            return False
        else:
            print(f"✅ ENHANCED CHUNKING SUCCESS: {articles_created} articles created (> 1)")
            print("✅ H2-based chunking is working correctly")
        
        # Test 3: Image Extraction (204 images expected)
        images_processed = data.get('images_processed', 0)
        print(f"🖼️ Images Processed: {images_processed}")
        
        if images_processed >= 200:
            print(f"✅ EXCELLENT: {images_processed} images processed (close to expected 204)")
        elif images_processed >= 100:
            print(f"✅ GOOD: {images_processed} images processed (substantial extraction)")
        elif images_processed > 0:
            print(f"⚠️ PARTIAL: {images_processed} images processed (some extraction working)")
        else:
            print("❌ FAILURE: No images processed")
        
        # Test 4: Article Quality (substantial content)
        articles = data.get('articles', [])
        if articles:
            print(f"\n📄 ARTICLE QUALITY VERIFICATION:")
            
            total_content_length = 0
            articles_with_substantial_content = 0
            
            for i, article in enumerate(articles):
                title = article.get('title', f'Article {i+1}')
                content = article.get('content', '') or article.get('html', '')
                word_count = len(content.split()) if content else 0
                char_count = len(content) if content else 0
                
                print(f"  📄 Article {i+1}: '{title[:50]}...'")
                print(f"     📊 {word_count} words, {char_count} characters")
                
                total_content_length += char_count
                
                # Check for substantial content (not just headings)
                if char_count > 500:  # At least 500 characters
                    articles_with_substantial_content += 1
                    print(f"     ✅ Substantial content")
                else:
                    print(f"     ⚠️ Limited content")
            
            avg_content_length = total_content_length / len(articles)
            print(f"\n📊 CONTENT QUALITY SUMMARY:")
            print(f"   📄 {articles_with_substantial_content}/{len(articles)} articles have substantial content")
            print(f"   📊 Average article length: {avg_content_length:.0f} characters")
            
            if articles_with_substantial_content >= len(articles) * 0.7:  # 70% threshold
                print("✅ CONTENT QUALITY: Excellent - most articles have substantial content")
            elif articles_with_substantial_content >= len(articles) * 0.5:  # 50% threshold
                print("✅ CONTENT QUALITY: Good - many articles have substantial content")
            else:
                print("⚠️ CONTENT QUALITY: Needs improvement - few articles have substantial content")
        
        # Test 5: Debug Log Analysis
        session_id = data.get('session_id')
        if session_id:
            print(f"📋 Session ID: {session_id}")
        
        # Test 6: Overall Assessment
        print(f"\n🎯 ENHANCED CHUNKING FIX ASSESSMENT:")
        
        success_criteria = [
            ("Processing completed successfully", success),
            ("Multiple articles created", articles_created > 1),
            ("Images extracted", images_processed > 0),
            ("Substantial content in articles", articles_with_substantial_content > 0 if articles else True)
        ]
        
        passed_criteria = sum(1 for _, passed in success_criteria if passed)
        total_criteria = len(success_criteria)
        
        print(f"📊 Success Rate: {passed_criteria}/{total_criteria} criteria passed")
        
        for criterion, passed in success_criteria:
            status = "✅" if passed else "❌"
            print(f"   {status} {criterion}")
        
        if passed_criteria >= 3:  # At least 3 out of 4 criteria
            print("🎉 ENHANCED CHUNKING FIX VERIFICATION: SUCCESS")
            print("✅ The enhanced chunking system is working correctly")
            print("✅ H2 detection and multiple article creation is operational")
            print("✅ User's issue should be resolved")
            return True
        else:
            print("❌ ENHANCED CHUNKING FIX VERIFICATION: FAILED")
            print("❌ The enhanced chunking system needs further fixes")
            return False
    
    def test_content_library_verification(self):
        """Verify the articles appear in the Content Library"""
        print("\n📚 Testing Content Library Integration...")
        try:
            # Wait a moment for articles to be saved
            time.sleep(3)
            
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                current_count = len(articles)
                
                print(f"📊 Content Library now contains: {current_count} articles")
                
                if current_count > 1:
                    print("✅ CONTENT LIBRARY INTEGRATION: SUCCESS")
                    print(f"✅ {current_count} articles successfully saved to Content Library")
                    
                    # Show sample articles
                    for i, article in enumerate(articles[:3]):  # Show first 3
                        title = article.get('title', 'Unknown')
                        created_at = article.get('created_at', 'Unknown')
                        print(f"   📄 Article {i+1}: '{title[:60]}...' ({created_at})")
                    
                    return True
                elif current_count == 1:
                    print("⚠️ CONTENT LIBRARY INTEGRATION: PARTIAL")
                    print("⚠️ Only 1 article found - enhanced chunking may not be working")
                    return False
                else:
                    print("❌ CONTENT LIBRARY INTEGRATION: FAILED")
                    print("❌ No articles found in Content Library")
                    return False
            else:
                print(f"❌ Failed to check Content Library - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Content Library verification failed - {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete enhanced chunking test suite"""
        print("🚀 ENHANCED DOCX CHUNKING FIX - COMPREHENSIVE TEST")
        print("=" * 60)
        print("🎯 Testing the enhanced chunking fix with user's actual DOCX file")
        print("📋 Expected Results:")
        print("   - Multiple articles based on H2 headings")
        print("   - 204 images properly extracted")
        print("   - Each article with substantial content")
        print("   - Debug logs showing 'ENHANCED CHUNKING: Using X major headings'")
        print("=" * 60)
        
        test_results = []
        
        # Test 1: Clear Content Library
        print("\n" + "="*50)
        print("TEST 1: CLEAR CONTENT LIBRARY")
        print("="*50)
        result1 = self.test_clear_content_library()
        test_results.append(("Clear Content Library", result1))
        
        # Test 2: Download User's DOCX File
        print("\n" + "="*50)
        print("TEST 2: DOWNLOAD USER'S DOCX FILE")
        print("="*50)
        docx_content = self.test_download_user_docx_file()
        result2 = docx_content is not None
        test_results.append(("Download User's DOCX File", result2))
        
        if not result2:
            print("❌ Cannot proceed without DOCX file")
            return False
        
        # Test 3: Enhanced Chunking Processing
        print("\n" + "="*50)
        print("TEST 3: ENHANCED CHUNKING PROCESSING")
        print("="*50)
        result3 = self.test_enhanced_chunking_processing(docx_content)
        test_results.append(("Enhanced Chunking Processing", result3))
        
        # Test 4: Content Library Verification
        print("\n" + "="*50)
        print("TEST 4: CONTENT LIBRARY VERIFICATION")
        print("="*50)
        result4 = self.test_content_library_verification()
        test_results.append(("Content Library Verification", result4))
        
        # Final Results
        print("\n" + "="*60)
        print("ENHANCED CHUNKING FIX - FINAL RESULTS")
        print("="*60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        print(f"📊 Overall Success Rate: {passed_tests}/{total_tests} tests passed")
        print()
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}: {test_name}")
        
        print()
        
        if passed_tests >= 3:  # At least 3 out of 4 tests should pass
            print("🎉 ENHANCED CHUNKING FIX VERIFICATION: OVERALL SUCCESS")
            print("✅ The enhanced chunking system is working correctly")
            print("✅ H1 AND H2 detection for chunking is operational")
            print("✅ Multiple articles are being created from H2 structure")
            print("✅ User's 'Customer Summary Screen User Guide 1.3.docx' should now process correctly")
            print("✅ The issue of single large articles should be resolved")
            return True
        else:
            print("❌ ENHANCED CHUNKING FIX VERIFICATION: OVERALL FAILURE")
            print("❌ The enhanced chunking system still has issues")
            print("❌ Further fixes may be needed")
            return False

def main():
    """Main test execution"""
    tester = EnhancedChunkingTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 RECOMMENDATION: Enhanced chunking fix is working correctly")
        exit(0)
    else:
        print("\n🎯 RECOMMENDATION: Enhanced chunking fix needs further investigation")
        exit(1)

if __name__ == "__main__":
    main()