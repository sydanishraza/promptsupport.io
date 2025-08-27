#!/usr/bin/env python3
"""
DOCX Chunking Debug Test - Check Backend Logs
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com') + '/api'

def test_with_larger_content():
    """Test with content well over 1500 characters"""
    print("🎯 DOCX CHUNKING DEBUG TEST")
    print("=" * 50)
    
    # Create content that's definitely over 1500 characters
    test_content = """DOCX Processing Chunking Threshold Test Document

This document is specifically designed to test the chunking threshold fix where the threshold was lowered from 3000 to 1500 characters to ensure DOCX files generate multiple articles instead of single articles with "single_article_simplified" approach.

# Chapter 1: Introduction to Enhanced Processing

The enhanced DOCX processing system has been updated to use a lower chunking threshold. This means that documents with content over 1500 characters should now be split into multiple articles rather than processed as a single comprehensive article. This change addresses user feedback about getting single large articles instead of focused, digestible content pieces.

The key improvements include:
- Lowered chunking threshold from 3000 to 1500 characters
- Enhanced processing path instead of simplified approach
- Better content structure detection
- Improved article generation metadata

# Chapter 2: Technical Implementation Details

The technical implementation involves several key components working together to ensure proper chunking behavior. The system now analyzes content length more aggressively and applies chunking logic earlier in the processing pipeline.

Key technical changes:
1. Content length detection happens before processing approach decision
2. Chunking validation occurs with the new 1500 character threshold
3. Processing metadata indicates "comprehensive_docx" not "single_article_simplified"
4. Debug logs show "Processing decision: ENHANCED vs SIMPLIFIED"

This ensures that users receive multiple focused articles that are easier to read and navigate, rather than single overwhelming documents.

# Chapter 3: Expected Results and Validation

When this document is processed, the system should:
- Detect content length exceeding 1500 characters
- Choose enhanced processing path over simplified approach
- Generate multiple articles (at least 2-3 articles)
- Show processing approach as "comprehensive_docx"
- Include proper processing metadata in each article

The validation process should confirm that articles are saved to the content library correctly and that the chunking validation passes with the new threshold requirements.

# Chapter 4: User Experience Improvements

The user experience improvements from this fix are significant. Instead of receiving one large article that might be overwhelming, users now get multiple focused articles that cover specific aspects of their document.

Benefits include:
- Better content organization
- Easier navigation between topics
- More focused article content
- Improved readability scores
- Better search and retrieval capabilities

This addresses the core user complaint about DOCX processing generating single summarized articles instead of comprehensive, well-structured content.

# Chapter 5: Quality Assurance and Testing

Quality assurance for this fix involves comprehensive testing of the chunking logic, content length calculations, and processing approach decisions. The system must consistently choose the enhanced processing path for documents over 1500 characters.

Testing scenarios include:
- Documents just over 1500 characters (should chunk)
- Documents just under 1500 characters (should remain single)
- Documents with multiple headings and sections
- Documents with various content types and structures
- Verification of processing metadata and approach indicators

The testing confirms that the "single_article_simplified" issue has been resolved and users receive the enhanced processing experience they expect."""

    content_length = len(test_content)
    print(f"📏 Test content length: {content_length} characters (should be > 1500)")
    
    if content_length <= 1500:
        print("❌ Test content is not long enough!")
        return False
    
    try:
        # Test with content/upload endpoint
        print("\n🔍 Testing with /content/upload endpoint...")
        
        file_data = io.BytesIO(test_content.encode('utf-8'))
        files = {
            'file': ('large_chunking_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'metadata': json.dumps({
                "test_type": "chunking_debug_test",
                "content_length": content_length,
                "expected_chunks": "multiple"
            })
        }
        
        print("📤 Uploading large test file...")
        response = requests.post(
            f"{BACKEND_URL}/content/upload",
            files=files,
            data=form_data,
            timeout=120
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response: {json.dumps(data, indent=2)}")
            
            chunks_created = data.get('chunks_created', 0)
            print(f"\n🎯 CHUNKING RESULTS:")
            print(f"   Content length: {content_length} characters")
            print(f"   Chunks created: {chunks_created}")
            print(f"   Expected: Multiple chunks (> 1)")
            
            if chunks_created > 1:
                print("✅ CHUNKING THRESHOLD FIX IS WORKING!")
                print("   Multiple chunks created as expected")
                return True
            else:
                print("❌ CHUNKING THRESHOLD FIX NOT WORKING")
                print("   Only single chunk created")
                
                # Check if there are any debug messages in the response
                response_str = json.dumps(data)
                if 'ISSUE 1' in response_str or 'FORCE CHUNKING' in response_str:
                    print("✅ Debug messages found in response")
                else:
                    print("⚠️ No debug messages found in response")
                
                return False
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_content_library_check():
    """Check content library for multiple articles"""
    print("\n🔍 Checking Content Library for multiple articles...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"📚 Total articles in library: {len(articles)}")
            
            # Look for recent test articles
            recent_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                if any(keyword in title for keyword in ['chunking', 'threshold', 'test', 'docx']):
                    recent_articles.append(article)
            
            print(f"📚 Test-related articles found: {len(recent_articles)}")
            
            if len(recent_articles) >= 2:
                print("✅ Multiple test articles found - chunking may be working")
                for i, article in enumerate(recent_articles[:3]):
                    print(f"   Article {i+1}: {article.get('title', 'No title')}")
                return True
            else:
                print("⚠️ Limited test articles found")
                return False
        else:
            print(f"❌ Could not access content library: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Content library check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 RUNNING DOCX CHUNKING DEBUG TESTS")
    print("=" * 60)
    
    test1_result = test_with_larger_content()
    test2_result = test_content_library_check()
    
    print(f"\n{'='*60}")
    print("🎯 FINAL RESULTS:")
    print(f"   Large content test: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"   Content library test: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result:
        print("\n🎉 CHUNKING THRESHOLD FIX IS WORKING!")
        print("   System correctly creates multiple chunks for large content")
    else:
        print("\n❌ CHUNKING THRESHOLD FIX NEEDS INVESTIGATION")
        print("   System still creating single chunks for large content")
    
    print(f"{'='*60}")