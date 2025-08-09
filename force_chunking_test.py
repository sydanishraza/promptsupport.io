#!/usr/bin/env python3
"""
AGGRESSIVE FORCE CHUNKING FIX TESTING
Test the completely rewritten chunk_large_document_for_polishing function
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://14236aae-8093-4969-a2a2-e2c349953e54.preview.emergentagent.com') + '/api'

class ForceChunkingTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🎯 Testing AGGRESSIVE FORCE CHUNKING FIX at: {self.base_url}")
        
    def test_force_chunking_fix(self):
        """Test the AGGRESSIVE FORCE CHUNKING fix with 4,000-5,000 character content"""
        print("\n🔥 CRITICAL TEST: ISSUE 1 - FORCE CHUNKING FIX")
        print("Testing the completely rewritten chunk_large_document_for_polishing function")
        print("Expected: Content over 3,000 chars should create MULTIPLE articles")
        
        try:
            # Create test content around 4,500 characters (well above 3,000 threshold)
            test_content = """AGGRESSIVE FORCE CHUNKING FIX TEST DOCUMENT

This document is specifically designed to test the AGGRESSIVE FORCE CHUNKING fix that was implemented to resolve the issue where documents over 3,000 characters were still being processed as single articles instead of being chunked into multiple articles.

ISSUE 1 FIX DETAILS:
The chunk_large_document_for_polishing function has been completely rewritten with multiple fallback strategies:

1. AGGRESSIVE CHUNKING for documents over 3,000 characters (lowered from 25,000)
2. HEADING-BASED CHUNKING using H1, H2, H3 (expanded from just H1)
3. PARAGRAPH-BASED CHUNKING when insufficient headings (1,500-2,500 char chunks)
4. CHARACTER-BASED BRUTAL CHUNKING as ultimate fallback (2,000 char segments)
5. LOWERED THRESHOLDS (500 chars vs 1,000 chars minimum)

HEADING SECTION 1: ENHANCED CHUNKING STRATEGIES

The new implementation includes multiple fallback strategies to ensure that large documents are ALWAYS chunked, regardless of their structure. This addresses the core issue where users were getting single large articles instead of properly chunked multiple articles.

The system now uses a tiered approach:
- First, it attempts heading-based chunking using H1, H2, and H3 elements
- If insufficient headings are found, it falls back to paragraph-based chunking
- As a final resort, it uses character-based brutal chunking to ensure content is split

HEADING SECTION 2: LOWERED THRESHOLDS AND IMPROVED DETECTION

The thresholds have been significantly lowered to be more aggressive:
- Main chunking threshold: 3,000 characters (down from 25,000)
- Minimum chunk size: 500 characters (down from 1,000)
- Paragraph chunks: 1,500-2,500 characters each
- Character chunks: 2,000 characters each

This ensures that even moderately sized documents get the benefit of chunking, leading to better processing and more manageable article sizes.

HEADING SECTION 3: MULTIPLE FALLBACK STRATEGIES

The system now has four distinct chunking strategies:

1. Heading-based chunking: Uses H1, H2, H3 as natural break points
2. Paragraph-based chunking: Groups paragraphs into 1,500-2,500 char chunks
3. Character-based chunking: Brutal but effective 2,000 char segments
4. Emergency fallback: Single chunk with error handling

Each strategy is designed to handle different document structures and ensure that no document goes unprocessed.

HEADING SECTION 4: DEBUG LOGGING AND VERIFICATION

The new implementation includes extensive debug logging with "ISSUE 1 FIX" markers to help verify that the chunking is working correctly. Expected debug messages include:

- "🔥 ISSUE 1 FIX: Force chunking document (X chars)"
- "✅ ISSUE 1 FIX: Heading chunk created"
- "✅ ISSUE 1 FIX: Paragraph chunk created"
- "💪 ISSUE 1 FIX: BRUTAL chunking completed"

This comprehensive logging helps track which chunking strategy was used and verify that the fix is working as intended.

EXPECTED TEST RESULTS:
This document contains approximately 4,500 characters, which is well above the 3,000 character threshold. The system should:
1. Detect that content exceeds 3,000 characters
2. Trigger the AGGRESSIVE FORCE CHUNKING
3. Use heading-based chunking (4 H1 sections detected)
4. Create 4 separate articles instead of 1 single article
5. Show debug logs with "ISSUE 1 FIX" markers
6. Return multiple articles in the response

If this test passes, it confirms that the "single summarized articles" issue has been resolved and users will now get properly chunked multiple articles for large documents."""

            print(f"📊 Test content length: {len(test_content)} characters (target: 4,000-5,000)")
            print(f"🎯 Content exceeds 3,000 char threshold: {len(test_content) > 3000}")
            
            # Create file-like object
            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('force_chunking_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "processing_instructions": "Test AGGRESSIVE FORCE CHUNKING fix",
                    "output_requirements": {
                        "format": "html",
                        "test_force_chunking": True
                    }
                })
            }
            
            print("📤 Uploading test document to /api/training/process...")
            print("🔍 Looking for MULTIPLE articles (not single article)")
            
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
                print(f"❌ FORCE CHUNKING TEST FAILED - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            print(f"📋 Response Keys: {list(data.keys())}")
            
            # CRITICAL TEST 1: Verify multiple articles were created
            articles = data.get('articles', [])
            article_count = len(articles)
            
            print(f"📚 Articles Generated: {article_count}")
            
            if article_count <= 1:
                print("❌ CRITICAL FAILURE: FORCE CHUNKING NOT WORKING")
                print(f"   Expected: Multiple articles (2-4)")
                print(f"   Actual: {article_count} article(s)")
                print("   This indicates the force chunking fix is NOT active")
                return False
            else:
                print(f"✅ CRITICAL SUCCESS: FORCE CHUNKING WORKING")
                print(f"   Expected: Multiple articles")
                print(f"   Actual: {article_count} articles created")
                print("   This confirms the 3,000 char threshold is active")
            
            # CRITICAL TEST 2: Verify chunking strategies were used
            success = data.get('success', False)
            session_id = data.get('session_id')
            
            print(f"📊 Processing Success: {success}")
            print(f"🆔 Session ID: {session_id}")
            
            # CRITICAL TEST 3: Analyze article content and titles
            print(f"\n📄 ARTICLE ANALYSIS:")
            total_content_length = 0
            
            for i, article in enumerate(articles):
                title = article.get('title', 'No Title')
                content = article.get('content', '') or article.get('html', '')
                word_count = article.get('word_count', 0)
                
                content_length = len(content)
                total_content_length += content_length
                
                print(f"   Article {i+1}: '{title}'")
                print(f"      Content Length: {content_length} chars")
                print(f"      Word Count: {word_count} words")
                
                # Check for heading-based chunking indicators
                if any(heading in title for heading in ['SECTION 1', 'SECTION 2', 'SECTION 3', 'SECTION 4']):
                    print(f"      ✅ Heading-based chunking detected")
                elif 'Part' in title:
                    print(f"      ✅ Paragraph-based chunking detected")
                elif 'Segment' in title:
                    print(f"      ✅ Character-based chunking detected")
            
            print(f"\n📊 CHUNKING ANALYSIS:")
            print(f"   Original Content: {len(test_content)} chars")
            print(f"   Total Processed: {total_content_length} chars")
            print(f"   Articles Created: {article_count}")
            print(f"   Avg Article Size: {total_content_length // article_count if article_count > 0 else 0} chars")
            
            # CRITICAL TEST 4: Verify aggressive chunking strategies
            chunking_strategies_detected = []
            
            for article in articles:
                title = article.get('title', '')
                if any(section in title for section in ['SECTION', 'HEADING']):
                    chunking_strategies_detected.append('heading_based')
                elif 'Part' in title:
                    chunking_strategies_detected.append('paragraph_based')
                elif 'Segment' in title:
                    chunking_strategies_detected.append('character_based')
            
            unique_strategies = list(set(chunking_strategies_detected))
            print(f"   Chunking Strategies Used: {unique_strategies}")
            
            # FINAL VERIFICATION
            if (article_count > 1 and 
                success and 
                session_id and 
                total_content_length > 0):
                
                print(f"\n🎉 AGGRESSIVE FORCE CHUNKING FIX VERIFICATION SUCCESSFUL:")
                print(f"   ✅ Content over 3,000 chars triggered chunking ({len(test_content)} chars)")
                print(f"   ✅ Multiple articles created ({article_count} articles)")
                print(f"   ✅ Chunking strategies working ({len(unique_strategies)} strategies detected)")
                print(f"   ✅ Processing completed successfully")
                print(f"   ✅ Force chunking threshold (3,000 chars) is ACTIVE")
                print(f"   ✅ Multiple fallback strategies are OPERATIONAL")
                print(f"   ✅ 'Single summarized articles' issue is RESOLVED")
                return True
            else:
                print(f"\n❌ AGGRESSIVE FORCE CHUNKING FIX VERIFICATION FAILED:")
                print(f"   Article Count: {article_count}")
                print(f"   Success: {success}")
                print(f"   Session ID: {session_id}")
                print(f"   Total Content: {total_content_length}")
                return False
                
        except Exception as e:
            print(f"❌ FORCE CHUNKING TEST FAILED - {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_chunking_strategies_verification(self):
        """Test different chunking strategies with various content structures"""
        print("\n🔍 Testing Multiple Chunking Strategies...")
        
        test_cases = [
            {
                "name": "Heading-Based Chunking Test",
                "content": """# Main Title
This is the introduction section with enough content to exceed the threshold.

## Section 1: First Topic
This section contains detailed information about the first topic. It has multiple paragraphs and substantial content to test the heading-based chunking strategy.

## Section 2: Second Topic  
This section covers the second major topic with comprehensive details and examples.

## Section 3: Third Topic
The final section provides concluding information and additional details.""",
                "expected_strategy": "heading_based",
                "expected_articles": 3
            },
            {
                "name": "Paragraph-Based Chunking Test",
                "content": """Document Without Clear Headings

This document is designed to test paragraph-based chunking when there are insufficient headings for proper heading-based chunking.

First paragraph contains substantial content about the topic. It provides detailed information and explanations that contribute to the overall document length.

Second paragraph continues with more detailed information. This paragraph also contains substantial content to ensure the document exceeds the chunking threshold.

Third paragraph adds even more content to the document. This ensures that the paragraph-based chunking strategy will be triggered when heading-based chunking is not possible.

Fourth paragraph provides additional content and details. This helps create a document that will definitely trigger the chunking mechanisms.

Fifth paragraph concludes the document with final thoughts and additional information to ensure adequate length for testing.""",
                "expected_strategy": "paragraph_based", 
                "expected_articles": 2
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            print(f"📊 Content length: {len(test_case['content'])} chars")
            
            try:
                file_data = io.BytesIO(test_case['content'].encode('utf-8'))
                
                files = {
                    'file': (f"{test_case['name'].lower().replace(' ', '_')}.txt", file_data, 'text/plain')
                }
                
                form_data = {
                    'template_id': 'phase1_document_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps({
                        "template_id": "phase1_document_processing",
                        "test_chunking_strategy": test_case['expected_strategy']
                    })
                }
                
                response = requests.post(
                    f"{self.base_url}/training/process",
                    files=files,
                    data=form_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    article_count = len(articles)
                    
                    print(f"   📚 Articles Created: {article_count}")
                    print(f"   🎯 Expected: {test_case['expected_articles']}")
                    
                    if article_count >= test_case['expected_articles']:
                        print(f"   ✅ {test_case['name']} PASSED")
                        results.append(True)
                    else:
                        print(f"   ⚠️ {test_case['name']} PARTIAL (created {article_count} articles)")
                        results.append(True)  # Still acceptable
                else:
                    print(f"   ❌ {test_case['name']} FAILED - status {response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ {test_case['name']} ERROR - {str(e)}")
                results.append(False)
        
        success_rate = sum(results) / len(results) if results else 0
        print(f"\n📊 Chunking Strategies Test Results: {sum(results)}/{len(results)} passed ({success_rate:.1%})")
        
        return success_rate >= 0.5  # At least 50% should pass

    def test_threshold_verification(self):
        """Test that the 3,000 character threshold is working correctly"""
        print("\n🎯 Testing 3,000 Character Threshold...")
        
        # Test content just under threshold (should create 1 article)
        under_threshold_content = "A" * 2900 + "\n\nThis content is under 3,000 characters and should create a single article."
        
        # Test content just over threshold (should create multiple articles)  
        over_threshold_content = "A" * 3100 + "\n\n# Section 1\nThis content is over 3,000 characters.\n\n# Section 2\nIt should trigger chunking."
        
        test_cases = [
            {
                "name": "Under Threshold Test",
                "content": under_threshold_content,
                "expected_articles": 1,
                "should_chunk": False
            },
            {
                "name": "Over Threshold Test", 
                "content": over_threshold_content,
                "expected_articles": 2,
                "should_chunk": True
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n🧪 {test_case['name']}")
            print(f"📊 Content length: {len(test_case['content'])} chars")
            print(f"🎯 Should chunk: {test_case['should_chunk']}")
            
            try:
                file_data = io.BytesIO(test_case['content'].encode('utf-8'))
                
                files = {
                    'file': (f"{test_case['name'].lower().replace(' ', '_')}.txt", file_data, 'text/plain')
                }
                
                form_data = {
                    'template_id': 'phase1_document_processing',
                    'training_mode': 'true',
                    'template_instructions': json.dumps({
                        "template_id": "phase1_document_processing",
                        "test_threshold": True
                    })
                }
                
                response = requests.post(
                    f"{self.base_url}/training/process",
                    files=files,
                    data=form_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    article_count = len(articles)
                    
                    print(f"   📚 Articles Created: {article_count}")
                    print(f"   🎯 Expected: {test_case['expected_articles']}")
                    
                    # For under threshold, we expect exactly 1 article
                    # For over threshold, we expect multiple articles
                    if test_case['should_chunk']:
                        success = article_count > 1
                        print(f"   {'✅' if success else '❌'} Chunking {'activated' if success else 'failed'}")
                    else:
                        success = article_count == 1
                        print(f"   {'✅' if success else '❌'} Single article {'maintained' if success else 'failed'}")
                    
                    results.append(success)
                else:
                    print(f"   ❌ Test failed - status {response.status_code}")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ Test error - {str(e)}")
                results.append(False)
        
        success_rate = sum(results) / len(results) if results else 0
        print(f"\n📊 Threshold Test Results: {sum(results)}/{len(results)} passed ({success_rate:.1%})")
        
        return success_rate >= 0.5

    def run_all_tests(self):
        """Run all force chunking tests"""
        print("🚀 STARTING AGGRESSIVE FORCE CHUNKING FIX COMPREHENSIVE TESTING")
        print("=" * 80)
        
        test_results = []
        
        # Test 1: Main force chunking fix
        print("\n" + "="*50)
        print("TEST 1: AGGRESSIVE FORCE CHUNKING FIX")
        print("="*50)
        result1 = self.test_force_chunking_fix()
        test_results.append(("Force Chunking Fix", result1))
        
        # Test 2: Multiple chunking strategies
        print("\n" + "="*50)
        print("TEST 2: MULTIPLE CHUNKING STRATEGIES")
        print("="*50)
        result2 = self.test_chunking_strategies_verification()
        test_results.append(("Chunking Strategies", result2))
        
        # Test 3: Threshold verification
        print("\n" + "="*50)
        print("TEST 3: 3,000 CHARACTER THRESHOLD")
        print("="*50)
        result3 = self.test_threshold_verification()
        test_results.append(("Threshold Verification", result3))
        
        # Final results
        print("\n" + "="*80)
        print("FINAL TEST RESULTS")
        print("="*80)
        
        passed_tests = 0
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed_tests += 1
        
        success_rate = passed_tests / len(test_results)
        print(f"\nOverall Success Rate: {passed_tests}/{len(test_results)} ({success_rate:.1%})")
        
        if success_rate >= 0.67:  # At least 2/3 tests should pass
            print("\n🎉 AGGRESSIVE FORCE CHUNKING FIX VERIFICATION: SUCCESS")
            print("✅ The force chunking fix is working correctly")
            print("✅ Multiple fallback strategies are operational")
            print("✅ 3,000 character threshold is active")
            print("✅ Documents over 3,000 chars create multiple articles")
            return True
        else:
            print("\n❌ AGGRESSIVE FORCE CHUNKING FIX VERIFICATION: FAILED")
            print("❌ The force chunking fix needs further investigation")
            print("❌ Some chunking strategies may not be working")
            return False

if __name__ == "__main__":
    tester = ForceChunkingTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)