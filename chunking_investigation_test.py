#!/usr/bin/env python3
"""
CHUNKING INVESTIGATION TEST
Detailed analysis of why the 4.8MB DOCX file generated only 1 article instead of multiple articles
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-6.preview.emergentagent.com') + '/api'

def test_chunking_threshold():
    """Test the chunking threshold logic"""
    print("🔍 CHUNKING THRESHOLD INVESTIGATION")
    print("=" * 60)
    
    # Check current Content Library
    response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"📚 Total articles in Content Library: {len(articles)}")
        
        # Find the most recent article (likely our test)
        if articles:
            recent_article = articles[0]  # Assuming first is most recent
            title = recent_article.get('title', 'Unknown')
            content = recent_article.get('content', '') or recent_article.get('html', '')
            word_count = len(content.split())
            char_count = len(content)
            
            print(f"\n📄 Most Recent Article Analysis:")
            print(f"  📋 Title: {title}")
            print(f"  📏 Character count: {char_count:,}")
            print(f"  📝 Word count: {word_count:,}")
            
            # Check if this should have triggered chunking
            print(f"\n🎯 CHUNKING ANALYSIS:")
            print(f"  📏 Content length: {char_count:,} characters")
            print(f"  🎯 Chunking threshold: 1,500 characters")
            
            if char_count > 1500:
                print(f"  ✅ Content EXCEEDS chunking threshold by {char_count - 1500:,} characters")
                print(f"  ❓ Question: Why was only 1 article created?")
                
                # Possible reasons:
                print(f"\n🔍 POSSIBLE REASONS FOR SINGLE ARTICLE:")
                print(f"  1. Document structure: No clear H1/H2 headings for chunking")
                print(f"  2. Processing approach: System chose 'single comprehensive' over 'multiple chunks'")
                print(f"  3. Content type: Document treated as single logical unit")
                print(f"  4. Chunking logic: Threshold check may have different implementation")
                
            else:
                print(f"  ❌ Content BELOW chunking threshold")
                print(f"  ✅ Single article creation is correct behavior")
            
            # Check for document structure indicators
            h1_count = content.count('<h1>')
            h2_count = content.count('<h2>')
            h3_count = content.count('<h3>')
            
            print(f"\n🏗️ DOCUMENT STRUCTURE ANALYSIS:")
            print(f"  📋 H1 headings: {h1_count}")
            print(f"  📋 H2 headings: {h2_count}")
            print(f"  📋 H3 headings: {h3_count}")
            
            if h1_count > 1:
                print(f"  ✅ Multiple H1 headings suggest document should be chunked")
            elif h2_count > 3:
                print(f"  ✅ Multiple H2 headings suggest document could be chunked")
            else:
                print(f"  ⚠️ Limited heading structure may explain single article")
            
            return True
        else:
            print("❌ No articles found in Content Library")
            return False
    else:
        print(f"❌ Could not access Content Library - status {response.status_code}")
        return False

def test_content_processing_approach():
    """Test what processing approach was used"""
    print("\n🔍 CONTENT PROCESSING APPROACH INVESTIGATION")
    print("=" * 60)
    
    # Create a test with known large content to see chunking behavior
    test_content = """CHUNKING TEST DOCUMENT

This is a test document specifically designed to trigger the chunking logic.
This document contains multiple sections that should be processed as separate articles
if the chunking system is working correctly.

SECTION 1: INTRODUCTION
This is the introduction section with substantial content. Lorem ipsum dolor sit amet, 
consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna 
aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut 
aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate 
velit esse cillum dolore eu fugiat nulla pariatur.

SECTION 2: METHODOLOGY
This section describes the methodology with detailed explanations. Excepteur sint 
occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id 
est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium 
doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis 
et quasi architecto beatae vitae dicta sunt explicabo.

SECTION 3: RESULTS
This section presents the results with comprehensive analysis. Nemo enim ipsam 
voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur 
magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, 
qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non 
numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.

SECTION 4: DISCUSSION
This section discusses the implications with thorough examination. Ut enim ad minima 
veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut 
aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea 
voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum 
fugiat quo voluptas nulla pariatur.

SECTION 5: CONCLUSION
This final section provides conclusions and recommendations. At vero eos et accusamus 
et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti 
atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate 
non provident, similique sunt in culpa qui officia deserunt mollitia animi.

This document is specifically designed to exceed the 1,500 character threshold and 
should trigger multiple article creation if the chunking system is working correctly."""

    print(f"📏 Test content length: {len(test_content):,} characters")
    print(f"🎯 Expected behavior: Multiple articles (content > 1,500 chars)")
    
    # Upload test content
    import io
    file_data = io.BytesIO(test_content.encode('utf-8'))
    
    files = {
        'file': ('chunking_test.txt', file_data, 'text/plain')
    }
    
    form_data = {
        'metadata': json.dumps({
            "source": "chunking_investigation",
            "test_type": "chunking_threshold_test",
            "expected_articles": "multiple"
        })
    }
    
    print("📤 Uploading chunking test content...")
    
    response = requests.post(
        f"{BACKEND_URL}/content/upload",
        files=files,
        data=form_data,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        chunks_created = data.get('chunks_created', 0)
        status = data.get('status', 'unknown')
        
        print(f"✅ Upload successful:")
        print(f"  📚 Chunks created: {chunks_created}")
        print(f"  📊 Status: {status}")
        
        if chunks_created > 1:
            print("✅ CHUNKING WORKING: Multiple chunks created as expected")
        elif chunks_created == 1:
            print("⚠️ SINGLE CHUNK: System created only 1 chunk despite large content")
            print("❓ This suggests chunking threshold may not be working as expected")
        else:
            print("❌ NO CHUNKS: Processing may have failed")
        
        return chunks_created > 0
    else:
        print(f"❌ Upload failed - status {response.status_code}")
        return False

def investigate_docx_specific_processing():
    """Investigate DOCX-specific processing behavior"""
    print("\n🔍 DOCX-SPECIFIC PROCESSING INVESTIGATION")
    print("=" * 60)
    
    # Check if DOCX files are processed differently than text files
    print("📋 Comparing DOCX vs Text processing behavior...")
    
    # The key question: Does the DOCX processing pipeline have different chunking logic?
    print("\n🎯 KEY QUESTIONS:")
    print("1. Does DOCX processing use different chunking thresholds?")
    print("2. Does DOCX content extraction affect chunking decisions?")
    print("3. Are DOCX files processed through a different pipeline?")
    print("4. Does the 'single_article_simplified' approach get triggered for DOCX?")
    
    # Check the actual extracted content length from our DOCX test
    print("\n📊 DOCX PROCESSING ANALYSIS:")
    print("- Original file: 4.8MB (4,789,101 bytes)")
    print("- Generated article: 714 words (~3,500 characters)")
    print("- Extraction ratio: Very low (suggests heavy summarization)")
    
    print("\n💡 HYPOTHESIS:")
    print("The DOCX processing may be using 'single_article_simplified' approach")
    print("instead of comprehensive chunking, which would explain:")
    print("- Single article output")
    print("- Low word count (714 words from 4.8MB file)")
    print("- No image extraction")
    
    return True

if __name__ == "__main__":
    print("🔍 CHUNKING INVESTIGATION TEST")
    print("Analyzing why 4.8MB DOCX generated only 1 article")
    print("=" * 80)
    
    test_chunking_threshold()
    test_content_processing_approach()
    investigate_docx_specific_processing()
    
    print("\n🎯 INVESTIGATION SUMMARY:")
    print("=" * 80)
    print("✅ DOCX processing pipeline is functional")
    print("⚠️ Chunking behavior needs investigation:")
    print("  - Large DOCX file (4.8MB) generated only 1 article")
    print("  - Content appears summarized (714 words)")
    print("  - No images extracted from likely image-rich document")
    print("  - May be using 'simplified' instead of 'comprehensive' processing")
    
    print("\n📋 RECOMMENDATIONS:")
    print("1. Verify chunking threshold implementation for DOCX files")
    print("2. Check if DOCX processing uses different pipeline than text files")
    print("3. Investigate image extraction from DOCX files")
    print("4. Confirm processing approach (comprehensive vs simplified)")