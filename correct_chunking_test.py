#!/usr/bin/env python3
"""
DOCX Chunking Threshold Fix - Correct Test
Test with proper text content to verify chunking threshold
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-pipeline-4.preview.emergentagent.com') + '/api'

def test_chunking_with_text_file():
    """Test chunking threshold with a proper text file"""
    print("🎯 DOCX CHUNKING THRESHOLD FIX - CORRECT TEST")
    print("=" * 60)
    
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

The testing confirms that the "single_article_simplified" issue has been resolved and users receive the enhanced processing experience they expect.

Additional content to ensure we are well over the 1500 character threshold. This extra content helps verify that the chunking logic is working correctly and that documents with substantial content are properly split into multiple articles rather than processed as single comprehensive documents."""

    content_length = len(test_content)
    print(f"📏 Test content length: {content_length} characters")
    print(f"🎯 Expected: Multiple chunks (content > 1500)")
    
    if content_length <= 1500:
        print("❌ Test content is not long enough!")
        return False
    
    try:
        # Test with text file (not fake DOCX)
        print("\n🔍 Testing with proper text file...")
        
        file_data = io.BytesIO(test_content.encode('utf-8'))
        files = {
            'file': ('chunking_threshold_test.txt', file_data, 'text/plain')
        }
        
        form_data = {
            'metadata': json.dumps({
                "test_type": "chunking_threshold_verification",
                "content_length": content_length,
                "expected_behavior": "multiple_articles"
            })
        }
        
        print("📤 Uploading test file...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/content/upload",
            files=files,
            data=form_data,
            timeout=120
        )
        
        processing_time = time.time() - start_time
        print(f"⏱️ Processing time: {processing_time:.2f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response: {json.dumps(data, indent=2)}")
            
            # Check the key metrics
            extracted_length = data.get('extracted_content_length', 0)
            chunks_created = data.get('chunks_created', 0)
            
            print(f"\n🎯 CHUNKING ANALYSIS:")
            print(f"   Original content: {content_length} characters")
            print(f"   Extracted content: {extracted_length} characters")
            print(f"   Chunks created: {chunks_created}")
            
            # Verify content extraction
            if extracted_length < content_length * 0.8:  # Should extract at least 80% of content
                print("⚠️ Content extraction may have issues")
                print(f"   Expected ~{content_length}, got {extracted_length}")
            else:
                print("✅ Content extraction looks good")
            
            # Verify chunking
            if extracted_length > 1500 and chunks_created > 1:
                print("✅ CHUNKING THRESHOLD FIX IS WORKING!")
                print("   Content > 1500 chars resulted in multiple chunks")
                return True
            elif extracted_length > 1500 and chunks_created == 1:
                print("❌ CHUNKING THRESHOLD FIX NOT WORKING")
                print("   Content > 1500 chars but only 1 chunk created")
                return False
            elif extracted_length <= 1500:
                print("⚠️ CONTENT EXTRACTION ISSUE")
                print("   Extracted content too small to test chunking properly")
                return False
            else:
                print("⚠️ UNEXPECTED RESULT")
                return False
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_small_content():
    """Test with content under 1500 characters to verify single article behavior"""
    print("\n🔍 Testing with small content (< 1500 chars)...")
    
    small_content = """Small Content Test

This is a small document that should remain as a single article because it's under the 1500 character threshold.

The system should:
- Detect content length under 1500 characters
- Create only 1 chunk
- Use single article processing

This test verifies that the threshold logic works in both directions."""

    content_length = len(small_content)
    print(f"📏 Small content length: {content_length} characters")
    
    try:
        file_data = io.BytesIO(small_content.encode('utf-8'))
        files = {
            'file': ('small_content_test.txt', file_data, 'text/plain')
        }
        
        form_data = {
            'metadata': json.dumps({
                "test_type": "small_content_verification",
                "content_length": content_length
            })
        }
        
        response = requests.post(
            f"{BACKEND_URL}/content/upload",
            files=files,
            data=form_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            chunks_created = data.get('chunks_created', 0)
            extracted_length = data.get('extracted_content_length', 0)
            
            print(f"   Extracted: {extracted_length} chars, Chunks: {chunks_created}")
            
            if chunks_created == 1:
                print("✅ Small content correctly processed as single article")
                return True
            else:
                print(f"⚠️ Small content created {chunks_created} chunks (expected 1)")
                return False
        else:
            print(f"❌ Small content test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Small content test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 DOCX CHUNKING THRESHOLD FIX - COMPREHENSIVE VERIFICATION")
    print("=" * 70)
    print("OBJECTIVE: Verify threshold lowered from 3000 to 1500 characters")
    print("EXPECTED: Multiple articles for content > 1500, single for < 1500")
    print("=" * 70)
    
    # Run tests
    large_test_result = test_chunking_with_text_file()
    small_test_result = test_small_content()
    
    # Final assessment
    print(f"\n{'='*70}")
    print("🎯 FINAL CHUNKING THRESHOLD FIX VERIFICATION:")
    print(f"{'='*70}")
    print(f"   Large content test (>1500): {'✅ PASSED' if large_test_result else '❌ FAILED'}")
    print(f"   Small content test (<1500): {'✅ PASSED' if small_test_result else '❌ FAILED'}")
    
    if large_test_result and small_test_result:
        print("\n🎉 CHUNKING THRESHOLD FIX VERIFICATION: SUCCESS")
        print("✅ System correctly handles both large and small content")
        print("✅ Threshold of 1500 characters is working as expected")
        print("✅ Multiple articles generated for content > 1500 chars")
        print("✅ Single articles generated for content < 1500 chars")
    elif large_test_result:
        print("\n⚠️ CHUNKING THRESHOLD FIX VERIFICATION: PARTIAL SUCCESS")
        print("✅ Large content chunking is working")
        print("⚠️ Small content behavior needs verification")
    else:
        print("\n❌ CHUNKING THRESHOLD FIX VERIFICATION: NEEDS ATTENTION")
        print("❌ Large content chunking is not working as expected")
        print("❌ Threshold fix may not be properly implemented")
    
    print(f"{'='*70}")
    
    success = large_test_result and small_test_result
    exit(0 if success else 1)