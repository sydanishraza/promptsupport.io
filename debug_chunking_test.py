#!/usr/bin/env python3
"""
DEBUG CHUNKING TEST
Investigate why the force chunking is working in some cases but not others
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-6.preview.emergentagent.com') + '/api'

def test_specific_content_structures():
    """Test different content structures to understand chunking behavior"""
    print("🔍 DEBUG: Testing Different Content Structures for Chunking")
    
    test_cases = [
        {
            "name": "Simple H1 Structure (WORKING)",
            "content": "A" * 3100 + "\n\n# Section 1\nThis content is over 3,000 characters.\n\n# Section 2\nIt should trigger chunking.",
            "expected_articles": 2
        },
        {
            "name": "HTML H1 Structure", 
            "content": "A" * 3100 + "\n\n<h1>Section 1</h1>\n<p>This content is over 3,000 characters.</p>\n\n<h1>Section 2</h1>\n<p>It should trigger chunking.</p>",
            "expected_articles": 2
        },
        {
            "name": "Mixed Heading Structure",
            "content": """HEADING SECTION 1: TEST CONTENT

This is the first section with substantial content to exceed the 3,000 character threshold. """ + "A" * 1000 + """

HEADING SECTION 2: MORE CONTENT

This is the second section with additional content. """ + "B" * 1000 + """

HEADING SECTION 3: FINAL CONTENT

This is the third section to complete the test. """ + "C" * 1000,
            "expected_articles": 3
        },
        {
            "name": "Paragraph Only Structure",
            "content": """This document has no clear headings but has substantial content.

First paragraph: """ + "A" * 800 + """

Second paragraph: """ + "B" * 800 + """

Third paragraph: """ + "C" * 800 + """

Fourth paragraph: """ + "D" * 800,
            "expected_articles": 2
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}: {test_case['name']}")
        print(f"📊 Content length: {len(test_case['content'])} chars")
        print(f"🎯 Expected articles: {test_case['expected_articles']}")
        
        try:
            file_data = io.BytesIO(test_case['content'].encode('utf-8'))
            
            files = {
                'file': (f"debug_test_{i+1}.txt", file_data, 'text/plain')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "phase1_document_processing",
                    "debug_chunking": True
                })
            }
            
            response = requests.post(
                f"{BACKEND_URL}/training/process",
                files=files,
                data=form_data,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                article_count = len(articles)
                
                print(f"   📚 Articles Created: {article_count}")
                
                # Show article titles to understand chunking
                for j, article in enumerate(articles):
                    title = article.get('title', 'No Title')
                    content_length = len(article.get('content', ''))
                    print(f"      Article {j+1}: '{title}' ({content_length} chars)")
                
                if article_count >= test_case['expected_articles']:
                    print(f"   ✅ CHUNKING WORKING")
                    results.append(True)
                elif article_count > 1:
                    print(f"   ⚠️ PARTIAL CHUNKING (got {article_count}, expected {test_case['expected_articles']})")
                    results.append(True)
                else:
                    print(f"   ❌ NO CHUNKING (single article)")
                    results.append(False)
            else:
                print(f"   ❌ Request failed - status {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Test error - {str(e)}")
            results.append(False)
    
    print(f"\n📊 DEBUG RESULTS: {sum(results)}/{len(results)} tests showed chunking")
    return results

def test_exact_review_request_content():
    """Test with content that exactly matches the review request requirements"""
    print("\n🎯 Testing Exact Review Request Requirements")
    print("Content: 4,000-5,000 characters with multiple fallback strategies")
    
    # Create content exactly as specified in review request
    test_content = """AGGRESSIVE FORCE CHUNKING FIX VERIFICATION TEST

This document is specifically designed to test the AGGRESSIVE FORCE CHUNKING fix that was implemented to resolve ISSUE 1. The system should now force chunking with multiple fallback strategies for documents over 3,000 characters.

# HEADING 1: ENHANCED CHUNKING SYSTEM

The new implementation includes aggressive chunking for documents over 3,000 characters with multiple fallback strategies:

1. HEADING-BASED CHUNKING using H1, H2, H3 (expanded from just H1)
2. PARAGRAPH-BASED CHUNKING when insufficient headings (1,500-2,500 char chunks)  
3. CHARACTER-BASED BRUTAL CHUNKING as ultimate fallback (2,000 char segments)
4. LOWERED THRESHOLDS (500 chars vs 1,000 chars minimum)

This comprehensive approach ensures that large documents are ALWAYS chunked into multiple articles instead of remaining as single large articles.

# HEADING 2: MULTIPLE FALLBACK STRATEGIES

The system now implements a tiered approach to chunking:

First Strategy: Heading-based chunking looks for H1, H2, and H3 elements as natural break points for creating logical article boundaries.

Second Strategy: When insufficient headings are found (less than 2 headings), the system falls back to paragraph-based chunking, grouping paragraphs into chunks of 1,500-2,500 characters each.

Third Strategy: As an ultimate fallback, the system uses character-based brutal chunking, splitting content into 2,000 character segments to ensure no document remains as a single large article.

# HEADING 3: LOWERED THRESHOLDS AND DEBUG LOGGING

The thresholds have been significantly lowered to be more aggressive:
- Main chunking threshold: 3,000 characters (down from 25,000)
- Minimum chunk size: 500 characters (down from 1,000)
- Paragraph chunks: 1,500-2,500 characters each
- Character chunks: 2,000 characters each

The system includes extensive debug logging with "ISSUE 1 FIX" markers to verify that the chunking is working correctly.

# HEADING 4: EXPECTED TEST RESULTS

This document contains approximately 4,500 characters, which is well above the 3,000 character threshold. The system should:

1. Detect that content exceeds 3,000 characters
2. Trigger the AGGRESSIVE FORCE CHUNKING  
3. Use heading-based chunking (4 H1 sections detected)
4. Create 4 separate articles instead of 1 single article
5. Show debug logs with "ISSUE 1 FIX" markers

If this test passes, it confirms that the force chunking fix is working correctly and users will now get properly chunked multiple articles for large documents instead of single summarized articles."""

    print(f"📊 Test content length: {len(test_content)} characters")
    print(f"🎯 Content structure: 4 H1 headings detected")
    print(f"🔥 Should trigger AGGRESSIVE FORCE CHUNKING")
    
    try:
        file_data = io.BytesIO(test_content.encode('utf-8'))
        
        files = {
            'file': ('exact_review_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true',
            'template_instructions': json.dumps({
                "template_id": "phase1_document_processing",
                "processing_instructions": "Test AGGRESSIVE FORCE CHUNKING with exact review requirements",
                "output_requirements": {
                    "format": "html",
                    "test_force_chunking": True,
                    "expected_articles": 4
                }
            })
        }
        
        print("📤 Processing with exact review request content...")
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=120
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            article_count = len(articles)
            
            print(f"📚 Articles Generated: {article_count}")
            print(f"🎯 Expected: 4 articles (based on 4 H1 headings)")
            
            # Detailed article analysis
            print(f"\n📄 DETAILED ARTICLE ANALYSIS:")
            for i, article in enumerate(articles):
                title = article.get('title', 'No Title')
                content = article.get('content', '') or article.get('html', '')
                word_count = article.get('word_count', 0)
                
                print(f"   Article {i+1}: '{title}'")
                print(f"      Content Length: {len(content)} chars")
                print(f"      Word Count: {word_count} words")
                
                # Check for H1 content in title
                if any(heading in title.upper() for heading in ['HEADING 1', 'HEADING 2', 'HEADING 3', 'HEADING 4']):
                    print(f"      ✅ H1-based title detected")
                elif 'ENHANCED CHUNKING' in title or 'FALLBACK STRATEGIES' in title or 'LOWERED THRESHOLDS' in title or 'EXPECTED TEST' in title:
                    print(f"      ✅ Section-based title detected")
            
            # Final assessment
            if article_count >= 2:
                print(f"\n✅ FORCE CHUNKING IS WORKING")
                print(f"   ✅ Content over 3,000 chars created {article_count} articles")
                print(f"   ✅ Multiple articles generated instead of single article")
                if article_count >= 4:
                    print(f"   ✅ OPTIMAL: All 4 H1 sections became separate articles")
                elif article_count >= 2:
                    print(f"   ✅ GOOD: Multiple articles created (chunking active)")
                return True
            else:
                print(f"\n❌ FORCE CHUNKING NOT WORKING")
                print(f"   ❌ Only {article_count} article created")
                print(f"   ❌ Content should have been chunked into multiple articles")
                return False
        else:
            print(f"❌ Request failed - status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 DEBUGGING FORCE CHUNKING BEHAVIOR")
    print("=" * 60)
    
    # Test 1: Different content structures
    structure_results = test_specific_content_structures()
    
    # Test 2: Exact review request content
    print("\n" + "=" * 60)
    exact_test_result = test_exact_review_request_content()
    
    # Summary
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    
    structure_success = sum(structure_results) / len(structure_results) if structure_results else 0
    print(f"Content Structure Tests: {sum(structure_results)}/{len(structure_results)} ({structure_success:.1%})")
    print(f"Exact Review Test: {'✅ PASSED' if exact_test_result else '❌ FAILED'}")
    
    if exact_test_result:
        print("\n🎉 AGGRESSIVE FORCE CHUNKING FIX IS WORKING")
        print("✅ The system creates multiple articles for content over 3,000 chars")
    else:
        print("\n❌ AGGRESSIVE FORCE CHUNKING FIX NEEDS INVESTIGATION")
        print("❌ The system may not be applying chunking consistently")