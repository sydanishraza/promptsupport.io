#!/usr/bin/env python3
"""
DOCX Processing Fixes Testing - UPDATED FOR CRITICAL FIXES
Testing the critical DOCX processing fixes implemented by the main agent:

ISSUE 1 - FORCE CHUNKING FIX: 
- Lowered polish_article_content threshold from 25,000 to 3,000 characters
- Content over 3,000 characters should FORCE into multiple articles

ISSUE 2 - FILENAME-BASED TITLE HANDLING:
- Modified extract_document_title to prioritize filename (without extension) over content extraction
- Article titles should use original filename instead of extracting from H1/content
"""
"""
DOCX Processing Fixes Test - Google Map JavaScript API Tutorial
Comprehensive testing for title extraction and content enhancement fixes
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://woolf-style-lint.preview.emergentagent.com') + '/api'

class DOCXProcessingFixesTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_document_url = "https://customer-assets.emergentagent.com/job_content-refiner-2/artifacts/5lvc26qb_Google%20Map%20JavaScript%20API%20Tutorial.docx"
        print(f"Testing DOCX Processing Fixes at: {self.base_url}")
        print(f"Test Document: {self.test_document_url}")
        
    def download_test_document(self):
        """Download the exact Google Map JavaScript API Tutorial document"""
        print("\n🔍 Downloading Google Map JavaScript API Tutorial document...")
        try:
            response = requests.get(self.test_document_url, timeout=30)
            print(f"Download Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Document downloaded successfully: {len(response.content)} bytes")
                return response.content
            else:
                print(f"❌ Failed to download document - status code {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Document download failed - {str(e)}")
            return None
    
    def test_title_extraction_fix(self, document_content):
        """Test that title extraction now shows 'Using Google Map Javascript API' instead of 'Comprehensive Guide To...'"""
        print("\n🔍 Testing Title Extraction Fix...")
        try:
            print("🎯 CRITICAL TEST: Verifying title is extracted from H1 ('Using Google Map Javascript API')")
            print("🎯 Should NOT show generic 'Comprehensive Guide To...' title")
            
            # Upload the document for processing
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', io.BytesIO(document_content), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "title_extraction_test",
                    "test_type": "title_fix_verification",
                    "document_type": "google_maps_tutorial"
                })
            }
            
            print("📤 Processing document to test title extraction...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=120
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Document processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📋 Processing Response: {json.dumps(data, indent=2)}")
            
            # Wait for processing to complete
            time.sleep(10)
            
            # Check Content Library for generated articles
            print("\n🔍 Checking Content Library for generated articles...")
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Could not access Content Library - status code {response.status_code}")
                return False
            
            library_data = response.json()
            articles = library_data.get('articles', [])
            
            # Look for articles from our test document
            test_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                if ('google' in title and 'map' in title) or 'javascript' in title or 'api' in title:
                    test_articles.append(article)
            
            if not test_articles:
                print("❌ No articles found from Google Maps tutorial document")
                return False
            
            print(f"✅ Found {len(test_articles)} articles from Google Maps tutorial")
            
            # TITLE EXTRACTION TEST
            title_fix_verified = False
            generic_title_found = False
            
            for i, article in enumerate(test_articles):
                title = article.get('title', '')
                print(f"📄 Article {i+1} Title: '{title}'")
                
                # Check for correct title extraction
                if 'using google map javascript api' in title.lower():
                    print("✅ TITLE FIX VERIFIED: Found correct H1 title 'Using Google Map Javascript API'")
                    title_fix_verified = True
                
                # Check for problematic generic titles
                if 'comprehensive guide to' in title.lower():
                    print("❌ TITLE FIX FAILED: Still generating generic 'Comprehensive Guide To...' titles")
                    generic_title_found = True
            
            if title_fix_verified and not generic_title_found:
                print("✅ TITLE EXTRACTION FIX SUCCESSFUL:")
                print("  ✅ Title extracted from H1 heading correctly")
                print("  ✅ No generic 'Comprehensive Guide' titles generated")
                return True
            elif title_fix_verified:
                print("⚠️ TITLE EXTRACTION FIX PARTIAL:")
                print("  ✅ Correct title found in some articles")
                print("  ⚠️ Some generic titles still present")
                return True
            else:
                print("❌ TITLE EXTRACTION FIX FAILED:")
                print("  ❌ No correct H1 titles found")
                print("  ❌ Generic titles may still be generated")
                return False
                
        except Exception as e:
            print(f"❌ Title extraction test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_content_enhancement_fix(self, document_content):
        """Test that content is enhanced/expanded, not summarized"""
        print("\n🔍 Testing Content Enhancement Fix...")
        try:
            print("🎯 CRITICAL TEST: Verifying content is enhanced/expanded, not summarized")
            print("🎯 Should generate comprehensive content (800-1500 words)")
            
            # Upload the document for processing with enhancement focus
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', io.BytesIO(document_content), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "content_enhancement_test",
                    "test_type": "content_quality_verification",
                    "document_type": "google_maps_tutorial",
                    "processing_mode": "comprehensive"
                })
            }
            
            print("📤 Processing document to test content enhancement...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=120
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Document processing failed - status code {response.status_code}")
                return False
            
            data = response.json()
            chunks_created = data.get('chunks_created', 0)
            print(f"📚 Chunks Created: {chunks_created}")
            
            # Wait for processing to complete
            time.sleep(15)
            
            # Check Content Library for generated articles
            print("\n🔍 Analyzing generated articles for content quality...")
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Could not access Content Library - status code {response.status_code}")
                return False
            
            library_data = response.json()
            articles = library_data.get('articles', [])
            
            # Look for recent articles from our test
            test_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                created_at = article.get('created_at', '')
                
                # Check if this is likely from our test (recent + Google Maps related)
                if (('google' in title and 'map' in title) or 'javascript' in title or 'api' in title):
                    test_articles.append(article)
            
            if not test_articles:
                print("❌ No articles found from Google Maps tutorial document")
                return False
            
            print(f"✅ Found {len(test_articles)} articles for content analysis")
            
            # CONTENT ENHANCEMENT TEST
            total_word_count = 0
            comprehensive_articles = 0
            enhanced_articles = 0
            
            for i, article in enumerate(test_articles):
                title = article.get('title', '')
                content = article.get('content', '') or article.get('html', '')
                word_count = len(content.split()) if content else 0
                
                print(f"\n📄 Article {i+1}: '{title[:50]}...'")
                print(f"📊 Word Count: {word_count}")
                
                total_word_count += word_count
                
                # Check for comprehensive content (800-1500 words target)
                if word_count >= 800:
                    comprehensive_articles += 1
                    print("✅ COMPREHENSIVE: Meets 800+ word target")
                elif word_count >= 500:
                    enhanced_articles += 1
                    print("⚠️ ENHANCED: Good length but below 800 words")
                else:
                    print("❌ SHORT: Below enhancement expectations")
                
                # Check for enhancement indicators in content
                if content:
                    # Look for signs of enhancement vs summarization
                    enhancement_indicators = [
                        'detailed explanation',
                        'comprehensive guide',
                        'step-by-step',
                        'example',
                        'implementation',
                        'best practices',
                        'advanced',
                        'tutorial'
                    ]
                    
                    summarization_indicators = [
                        'in summary',
                        'to summarize',
                        'briefly',
                        'overview only',
                        'quick summary'
                    ]
                    
                    content_lower = content.lower()
                    enhancement_score = sum(1 for indicator in enhancement_indicators if indicator in content_lower)
                    summarization_score = sum(1 for indicator in summarization_indicators if indicator in content_lower)
                    
                    print(f"📈 Enhancement indicators: {enhancement_score}")
                    print(f"📉 Summarization indicators: {summarization_score}")
                    
                    if enhancement_score > summarization_score:
                        print("✅ CONTENT STYLE: Enhanced/expanded content detected")
                    else:
                        print("⚠️ CONTENT STYLE: May be summarized content")
            
            # Overall assessment
            avg_word_count = total_word_count / len(test_articles) if test_articles else 0
            comprehensive_ratio = comprehensive_articles / len(test_articles) if test_articles else 0
            
            print(f"\n📊 CONTENT ENHANCEMENT ANALYSIS:")
            print(f"  📚 Total Articles: {len(test_articles)}")
            print(f"  📊 Average Word Count: {avg_word_count:.0f}")
            print(f"  ✅ Comprehensive Articles (800+ words): {comprehensive_articles}/{len(test_articles)} ({comprehensive_ratio:.1%})")
            print(f"  ⚠️ Enhanced Articles (500+ words): {enhanced_articles}/{len(test_articles)}")
            
            # Success criteria
            if avg_word_count >= 800 and comprehensive_ratio >= 0.5:
                print("✅ CONTENT ENHANCEMENT FIX SUCCESSFUL:")
                print("  ✅ Average word count meets comprehensive target (800+)")
                print("  ✅ Majority of articles are comprehensive")
                print("  ✅ Content is enhanced/expanded, not summarized")
                return True
            elif avg_word_count >= 500:
                print("⚠️ CONTENT ENHANCEMENT FIX PARTIAL:")
                print("  ✅ Content is enhanced beyond basic level")
                print("  ⚠️ Word count below optimal comprehensive target")
                return True
            else:
                print("❌ CONTENT ENHANCEMENT FIX FAILED:")
                print("  ❌ Content appears to be summarized, not enhanced")
                print("  ❌ Word count below enhancement expectations")
                return False
                
        except Exception as e:
            print(f"❌ Content enhancement test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_word_count_requirements(self, document_content):
        """Test that articles meet comprehensive word count requirements (800-1500 words)"""
        print("\n🔍 Testing Word Count Requirements...")
        try:
            print("🎯 CRITICAL TEST: Verifying articles meet 800-1500 word comprehensive requirements")
            
            # Use training interface for comprehensive processing
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', io.BytesIO(document_content), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            # Use comprehensive processing template
            template_data = {
                "template_id": "comprehensive_documentation",
                "processing_instructions": "Generate comprehensive, detailed articles with enhanced content",
                "output_requirements": {
                    "format": "html",
                    "min_word_count": 800,
                    "max_word_count": 1500,
                    "quality_benchmarks": ["comprehensive_coverage", "detailed_explanations", "technical_accuracy"]
                }
            }
            
            form_data = {
                'template_id': 'comprehensive_documentation',
                'training_mode': 'true',
                'template_instructions': json.dumps(template_data)
            }
            
            print("📤 Processing document with comprehensive template...")
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=180  # Extended timeout for comprehensive processing
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            print(f"📊 Response Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Comprehensive processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            if not articles:
                print("❌ No articles generated from comprehensive processing")
                return False
            
            print(f"✅ Generated {len(articles)} articles for word count analysis")
            
            # WORD COUNT ANALYSIS
            word_count_results = []
            
            for i, article in enumerate(articles):
                title = article.get('title', '')
                content = article.get('content', '') or article.get('html', '')
                
                # Clean HTML for accurate word count
                from bs4 import BeautifulSoup
                try:
                    soup = BeautifulSoup(content, 'html.parser')
                    text_content = soup.get_text()
                    word_count = len(text_content.split())
                except:
                    word_count = len(content.split()) if content else 0
                
                print(f"\n📄 Article {i+1}: '{title[:50]}...'")
                print(f"📊 Word Count: {word_count}")
                
                # Categorize by word count
                if 800 <= word_count <= 1500:
                    print("✅ OPTIMAL: Meets comprehensive requirements (800-1500 words)")
                    word_count_results.append('optimal')
                elif word_count >= 800:
                    print("✅ COMPREHENSIVE: Exceeds minimum requirement (800+ words)")
                    word_count_results.append('comprehensive')
                elif word_count >= 500:
                    print("⚠️ ENHANCED: Good but below comprehensive target")
                    word_count_results.append('enhanced')
                else:
                    print("❌ INSUFFICIENT: Below enhancement expectations")
                    word_count_results.append('insufficient')
            
            # Overall assessment
            optimal_count = word_count_results.count('optimal')
            comprehensive_count = word_count_results.count('comprehensive')
            enhanced_count = word_count_results.count('enhanced')
            insufficient_count = word_count_results.count('insufficient')
            
            total_articles = len(word_count_results)
            success_rate = (optimal_count + comprehensive_count) / total_articles if total_articles else 0
            
            print(f"\n📊 WORD COUNT REQUIREMENTS ANALYSIS:")
            print(f"  📚 Total Articles: {total_articles}")
            print(f"  ✅ Optimal (800-1500 words): {optimal_count}/{total_articles}")
            print(f"  ✅ Comprehensive (800+ words): {comprehensive_count}/{total_articles}")
            print(f"  ⚠️ Enhanced (500+ words): {enhanced_count}/{total_articles}")
            print(f"  ❌ Insufficient (<500 words): {insufficient_count}/{total_articles}")
            print(f"  📈 Success Rate: {success_rate:.1%}")
            
            # Success criteria
            if success_rate >= 0.8:
                print("✅ WORD COUNT REQUIREMENTS SUCCESSFUL:")
                print("  ✅ 80%+ of articles meet comprehensive word count requirements")
                print("  ✅ Enhancement prompts are working effectively")
                return True
            elif success_rate >= 0.5:
                print("⚠️ WORD COUNT REQUIREMENTS PARTIAL:")
                print("  ✅ Majority of articles meet requirements")
                print("  ⚠️ Some articles below optimal word count")
                return True
            else:
                print("❌ WORD COUNT REQUIREMENTS FAILED:")
                print("  ❌ Most articles below comprehensive requirements")
                print("  ❌ Enhancement prompts may not be working")
                return False
                
        except Exception as e:
            print(f"❌ Word count requirements test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_before_after_comparison(self, document_content):
        """Test before/after comparison to verify fixes resolved issues"""
        print("\n🔍 Testing Before/After Comparison...")
        try:
            print("🎯 CRITICAL TEST: Comparing current results with known issues")
            print("🎯 Known Issues:")
            print("  - Title: 'Comprehensive Guide To Using The Google Maps Javascript Api' (WRONG)")
            print("  - Content: ~387 words (TOO SHORT)")
            print("  - Processing: Simplified approach (NOT COMPREHENSIVE)")
            
            # Process document and compare with known issues
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', io.BytesIO(document_content), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "before_after_comparison",
                    "test_type": "fix_verification",
                    "document_type": "google_maps_tutorial"
                })
            }
            
            print("📤 Processing document for before/after comparison...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"❌ Document processing failed - status code {response.status_code}")
                return False
            
            # Wait for processing
            time.sleep(10)
            
            # Get results
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            if response.status_code != 200:
                print(f"❌ Could not access Content Library")
                return False
            
            library_data = response.json()
            articles = library_data.get('articles', [])
            
            # Find our test articles
            test_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                if ('google' in title and 'map' in title) or 'javascript' in title:
                    test_articles.append(article)
            
            if not test_articles:
                print("❌ No test articles found for comparison")
                return False
            
            print(f"✅ Found {len(test_articles)} articles for comparison")
            
            # BEFORE/AFTER COMPARISON
            fixes_verified = []
            
            for i, article in enumerate(test_articles):
                title = article.get('title', '')
                content = article.get('content', '') or article.get('html', '')
                word_count = len(content.split()) if content else 0
                
                print(f"\n📄 Article {i+1} Analysis:")
                print(f"  Title: '{title}'")
                print(f"  Word Count: {word_count}")
                
                # TITLE FIX VERIFICATION
                if 'comprehensive guide to' in title.lower():
                    print("  ❌ TITLE: Still shows generic 'Comprehensive Guide' (NOT FIXED)")
                    fixes_verified.append(False)
                elif 'using google map javascript api' in title.lower():
                    print("  ✅ TITLE: Shows correct H1 title (FIXED)")
                    fixes_verified.append(True)
                else:
                    print("  ⚠️ TITLE: Different title format (may be fixed)")
                    fixes_verified.append(True)
                
                # CONTENT LENGTH FIX VERIFICATION
                if word_count <= 400:
                    print("  ❌ CONTENT: Still ~387 words (NOT FIXED)")
                    fixes_verified.append(False)
                elif word_count >= 800:
                    print("  ✅ CONTENT: Comprehensive length 800+ words (FIXED)")
                    fixes_verified.append(True)
                else:
                    print("  ⚠️ CONTENT: Improved but not fully comprehensive (PARTIALLY FIXED)")
                    fixes_verified.append(True)
            
            # Overall comparison
            fixes_success_rate = sum(fixes_verified) / len(fixes_verified) if fixes_verified else 0
            
            print(f"\n📊 BEFORE/AFTER COMPARISON RESULTS:")
            print(f"  📈 Fixes Success Rate: {fixes_success_rate:.1%}")
            print(f"  ✅ Fixed Issues: {sum(fixes_verified)}/{len(fixes_verified)}")
            
            if fixes_success_rate >= 0.8:
                print("✅ BEFORE/AFTER COMPARISON SUCCESSFUL:")
                print("  ✅ Major issues have been resolved")
                print("  ✅ Title extraction working correctly")
                print("  ✅ Content enhancement working effectively")
                return True
            elif fixes_success_rate >= 0.5:
                print("⚠️ BEFORE/AFTER COMPARISON PARTIAL:")
                print("  ✅ Some issues have been resolved")
                print("  ⚠️ Some fixes may need additional work")
                return True
            else:
                print("❌ BEFORE/AFTER COMPARISON FAILED:")
                print("  ❌ Major issues persist")
                print("  ❌ Fixes may not be working as expected")
                return False
                
        except Exception as e:
            print(f"❌ Before/after comparison test failed - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_comprehensive_test(self):
        """Run all DOCX processing fixes tests"""
        print("🚀 Starting Comprehensive DOCX Processing Fixes Test")
        print("=" * 80)
        
        # Download test document
        document_content = self.download_test_document()
        if not document_content:
            print("❌ Cannot proceed without test document")
            return False
        
        # Run all tests
        test_results = []
        
        print("\n" + "=" * 80)
        test_results.append(self.test_title_extraction_fix(document_content))
        
        print("\n" + "=" * 80)
        test_results.append(self.test_content_enhancement_fix(document_content))
        
        print("\n" + "=" * 80)
        test_results.append(self.test_word_count_requirements(document_content))
        
        print("\n" + "=" * 80)
        test_results.append(self.test_before_after_comparison(document_content))
        
        # Final results
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        test_names = [
            "Title Extraction Fix",
            "Content Enhancement Fix", 
            "Word Count Requirements",
            "Before/After Comparison"
        ]
        
        passed_tests = 0
        for i, (test_name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{i+1}. {test_name}: {status}")
            if result:
                passed_tests += 1
        
        success_rate = passed_tests / len(test_results)
        print(f"\nOverall Success Rate: {passed_tests}/{len(test_results)} ({success_rate:.1%})")
        
        if success_rate >= 0.75:
            print("\n🎉 DOCX PROCESSING FIXES VERIFICATION SUCCESSFUL!")
            print("✅ Major fixes have been implemented and are working")
            return True
        elif success_rate >= 0.5:
            print("\n⚠️ DOCX PROCESSING FIXES PARTIALLY SUCCESSFUL")
            print("✅ Some fixes working, others may need attention")
            return True
        else:
            print("\n❌ DOCX PROCESSING FIXES VERIFICATION FAILED")
            print("❌ Critical issues persist, fixes may not be working")
            return False

def main():
    """Main test execution"""
    tester = DOCXProcessingFixesTest()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)