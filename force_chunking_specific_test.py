#!/usr/bin/env python3
"""
Force Chunking Specific Test
Testing ISSUE 1: Force chunking at 3,000 character threshold with properly sized content
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://docai-promptsupport.preview.emergentagent.com') + '/api'

def create_large_test_content():
    """Create content that's definitely over 3,000 characters"""
    
    base_content = """FORCE CHUNKING TEST DOCUMENT - COMPREHENSIVE TESTING

This document is specifically designed to test the FORCE CHUNKING FIX where the polish_article_content threshold was lowered from 25,000 to 3,000 characters. This content is designed to be approximately 4,500-5,000 characters long, which should definitively trigger the force chunking mechanism.

SECTION 1: INTRODUCTION TO FORCE CHUNKING SYSTEM
The force chunking system represents a critical improvement in document processing efficiency. When documents exceed the 3,000 character threshold, the system automatically activates chunking mode to split the content into multiple, more manageable articles. This ensures better readability, improved processing performance, and enhanced user experience. The system should detect that this document exceeds 3,000 characters and automatically create multiple articles instead of trying to process it as a single large article that would be difficult to read and navigate.

SECTION 2: TECHNICAL IMPLEMENTATION DETAILS AND ARCHITECTURE
The polish_article_content function has been significantly updated to implement this new threshold. Previously, the system would only chunk documents that exceeded 25,000 characters, which meant that medium-sized documents were processed as single, unwieldy articles. The new implementation checks if content length exceeds 3,000 characters, and when this threshold is exceeded, the system activates force chunking mode and calls the chunk_large_document_for_polishing function to split the content into logical sections based on heading structure and content flow. Each section becomes a separate article, ensuring optimal processing and user experience while maintaining the logical structure and flow of the original document.

SECTION 3: EXPECTED BEHAVIOR VERIFICATION AND TESTING METHODOLOGY
When this document is processed through the /api/training/process endpoint, the system should demonstrate the following behavior patterns: First, it should detect that the content length exceeds 3,000 characters. Second, it should activate force chunking mode automatically. Third, it should split the content into multiple logical articles based on section boundaries and heading structures. Fourth, it should return multiple articles instead of one large article. Fifth, each article should have appropriate titles and content that maintains the logical flow and structure of the original document while being more digestible for readers.

SECTION 4: QUALITY ASSURANCE TESTING AND VALIDATION PROCEDURES
This section ensures we have sufficient content to definitively exceed the 3,000 character threshold for comprehensive testing. The total character count of this document should be approximately 4,500-5,000 characters, which is well above the new 3,000 character force chunking threshold. This guarantees that the chunking mechanism will be triggered during testing, allowing us to validate that the implementation works correctly and produces the expected results. The content is structured with clear section boundaries to facilitate logical chunking while maintaining readability and coherence across the generated articles.

SECTION 5: PERFORMANCE IMPLICATIONS AND USER EXPERIENCE BENEFITS
The force chunking fix represents a significant improvement in document processing efficiency and user experience. By lowering the threshold from 25,000 to 3,000 characters, the system can now handle medium-sized documents more effectively, creating multiple focused articles instead of unwieldy single articles that are difficult to read and navigate. This improvement benefits users by providing more digestible content chunks, better navigation, improved readability, and enhanced overall user experience when working with processed documents.

SECTION 6: CONCLUSION AND VALIDATION SUMMARY
This test document validates that the force chunking implementation works correctly and produces the expected results. The document structure, content length, and section organization are specifically designed to trigger the chunking mechanism and demonstrate its effectiveness. When processed, this document should generate multiple articles that maintain the logical flow and structure while being more manageable and user-friendly than a single large article would be."""

    print(f"📊 Generated content length: {len(base_content)} characters")
    
    # If still not long enough, add more content
    if len(base_content) < 4000:
        additional_content = """

SECTION 7: ADDITIONAL TESTING CONTENT FOR THRESHOLD VALIDATION
This additional section ensures that we have sufficient content to definitively exceed the 3,000 character threshold. The force chunking system is designed to handle documents of various sizes and structures, and this comprehensive test validates its effectiveness across different content types and lengths. The system should demonstrate consistent behavior when processing documents that exceed the threshold, regardless of the specific content structure or formatting used in the original document.

SECTION 8: COMPREHENSIVE VALIDATION AND FINAL TESTING
This final section completes our comprehensive test document, ensuring that we have created content that will definitively trigger the force chunking mechanism. The total character count should now be well above 4,000 characters, providing a clear test case for validating the 3,000 character threshold implementation. This thorough testing approach ensures that we can confidently verify the fix is working as expected and producing the desired results for users."""
        
        base_content += additional_content
    
    print(f"📊 Final content length: {len(base_content)} characters")
    return base_content

def test_force_chunking_with_large_content():
    """Test force chunking with content definitely over 3,000 characters"""
    print("🔥 TESTING FORCE CHUNKING WITH LARGE CONTENT")
    print("=" * 60)
    
    # Create large content
    test_content = create_large_test_content()
    
    if len(test_content) <= 3000:
        print(f"❌ ERROR: Test content is only {len(test_content)} chars, cannot test chunking")
        return False
    else:
        print(f"✅ Test content is {len(test_content)} chars - should trigger FORCE CHUNKING")
    
    try:
        # Create file-like object
        file_data = io.BytesIO(test_content.encode('utf-8'))
        
        files = {
            'file': ('large_force_chunking_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'comprehensive_processing',
            'training_mode': 'true',
            'template_instructions': json.dumps({
                "template_id": "comprehensive_processing",
                "processing_instructions": "Test force chunking with large content over 3,000 characters"
            })
        }
        
        print("📤 Uploading large test document to /api/training/process...")
        
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
        
        if response.status_code != 200:
            print(f"❌ FORCE CHUNKING TEST FAILED - status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        print(f"📋 Response Keys: {list(data.keys())}")
        
        # Check for chunking indicators
        articles = data.get('articles', [])
        chunks_created = data.get('chunks_created', 0)
        success = data.get('success', False)
        
        print(f"📚 Articles Generated: {len(articles)}")
        print(f"🔄 Chunks Created: {chunks_created}")
        print(f"✅ Success: {success}")
        
        # CRITICAL TEST: Multiple articles should be created for content > 3,000 chars
        if len(articles) > 1:
            print("🎉 FORCE CHUNKING FIX VERIFIED: CHUNKING IS WORKING!")
            print(f"  ✅ Content over 3,000 chars ({len(test_content)}) created {len(articles)} articles")
            print(f"  ✅ Force chunking threshold of 3,000 chars is active")
            
            # Show article details
            total_content_length = 0
            for i, article in enumerate(articles):
                title = article.get('title', 'Untitled')
                content_length = len(article.get('content', ''))
                total_content_length += content_length
                print(f"  📄 Article {i+1}: '{title}' ({content_length} chars)")
            
            print(f"  📊 Total content across articles: {total_content_length} chars")
            return True
            
        elif len(articles) == 1:
            print("❌ FORCE CHUNKING FIX FAILED: Only 1 article created")
            print("❌ Force chunking did NOT activate despite content > 3,000 chars")
            print("❌ System may still be using old 25,000 char threshold")
            
            # Show the single article details
            article = articles[0]
            title = article.get('title', 'Untitled')
            content_length = len(article.get('content', ''))
            print(f"  📄 Single Article: '{title}' ({content_length} chars)")
            print(f"  📊 Original content: {len(test_content)} chars")
            
            return False
        else:
            print("❌ FORCE CHUNKING FIX FAILED: No articles created")
            return False
            
    except Exception as e:
        print(f"❌ Force chunking test failed - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 FORCE CHUNKING SPECIFIC TEST")
    print("=" * 60)
    print("Testing ISSUE 1: Force chunking threshold lowered to 3,000 characters")
    print("=" * 60)
    
    result = test_force_chunking_with_large_content()
    
    print("\n" + "=" * 60)
    print("🎯 FORCE CHUNKING TEST RESULTS")
    print("=" * 60)
    
    if result:
        print("🎉 FORCE CHUNKING FIX IS WORKING CORRECTLY!")
        print("  ✅ Content over 3,000 characters triggers multiple articles")
        print("  ✅ Force chunking threshold of 3,000 chars is active")
    else:
        print("❌ FORCE CHUNKING FIX NEEDS ATTENTION")
        print("  ❌ Content over 3,000 characters did not trigger chunking")
        print("  ❌ System may still be using old threshold or chunking is disabled")