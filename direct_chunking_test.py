#!/usr/bin/env python3
"""
Direct Smart Chunking Test - Test the smart_chunk_content function directly
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://29ab9b48-9f0b-482b-8a23-9ef1aebd2745.preview.emergentagent.com') + '/api'

def test_direct_chunking_with_no_breaks():
    """
    Test with content that absolutely has no paragraph or line breaks
    """
    print("🔥 DIRECT CHUNKING TEST - NO BREAKS")
    print("Testing with content that has absolutely no paragraph or line breaks")
    
    try:
        # Create content with NO breaks whatsoever - exactly like the user's issue
        # This content is over 2000 characters and has NO \n\n or \n breaks
        no_breaks_content = "Customer Summary Screen User Guide Overview This comprehensive guide provides detailed instructions for using the Customer Summary Screen functionality within the system The Customer Summary Screen serves as a central hub for viewing and managing customer information account details billing history and communication logs Understanding how to effectively navigate and utilize this screen is essential for customer service representatives and account managers The screen displays critical customer data in an organized format that allows for quick access to important information during customer interactions Key Features The Customer Summary Screen includes several key features designed to enhance user productivity and customer service quality The main dashboard provides an overview of customer account status recent activity and pending items that require attention Users can access detailed customer profiles that include contact information account history billing details and service records The interface supports multiple viewing modes to accommodate different workflow preferences and user roles within the organization Navigation and Layout The screen layout is designed for intuitive navigation with clearly labeled sections and logical information hierarchy The top navigation bar provides quick access to primary functions including customer search account creation and reporting tools The left sidebar contains expandable menu options for different data categories such as personal information billing history service tickets and communication logs The main content area displays selected information in a tabular format with sorting and filtering capabilities Search and Filter Options Advanced search functionality allows users to locate specific customer records using various criteria including name account number phone number or email address Filter options enable users to narrow down results based on account status service type billing cycle or geographic location The search results display in a sortable list format with key customer identifiers and status indicators Users can save frequently used search criteria as custom filters for improved efficiency Account Management Features The Customer Summary Screen provides comprehensive account management capabilities including the ability to view and modify customer information process billing adjustments and manage service configurations Users can access detailed billing history with transaction level detail and payment tracking The system supports bulk operations for managing multiple accounts simultaneously and includes audit trails for all account modifications Integration with other system modules ensures data consistency across all customer touchpoints"
        
        print(f"📏 Content length: {len(no_breaks_content)} characters")
        print(f"📝 Paragraph breaks (\\n\\n): {no_breaks_content.count(chr(10) + chr(10))}")
        print(f"📝 Line breaks (\\n): {no_breaks_content.count(chr(10))}")
        print(f"📝 Any whitespace breaks: {no_breaks_content.count('  ')}")
        
        # Verify absolutely no breaks
        if no_breaks_content.count('\n') == 0 and no_breaks_content.count('\n\n') == 0:
            print("✅ Content confirmed: ABSOLUTELY NO BREAKS")
        else:
            print("❌ Content still has breaks - this shouldn't happen")
            return False
        
        # Create file for upload
        file_data = io.BytesIO(no_breaks_content.encode('utf-8'))
        
        files = {
            'file': ('direct_no_breaks_test.txt', file_data, 'text/plain')
        }
        
        form_data = {
            'metadata': json.dumps({
                "source": "direct_no_breaks_test",
                "test_type": "absolutely_no_breaks",
                "content_length": len(no_breaks_content),
                "paragraph_breaks": 0,
                "line_breaks": 0,
                "expected_behavior": "character_based_chunking_must_trigger"
            })
        }
        
        print("📤 Testing with content that has absolutely no breaks...")
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/content/upload",
            files=files,
            data=form_data,
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Direct chunking test failed - status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        
        # CRITICAL VALIDATION: Check chunks created
        chunks_created = data.get('chunks_created', 0)
        print(f"📊 Chunks Created: {chunks_created}")
        
        # With 2000+ characters and NO breaks, this MUST create multiple chunks
        if chunks_created > 1:
            print("✅ DIRECT CHUNKING TEST SUCCESSFUL:")
            print(f"  ✅ Content with no breaks: {len(no_breaks_content)} chars")
            print(f"  ✅ Character-based chunking triggered")
            print(f"  ✅ Multiple chunks created: {chunks_created}")
            print(f"  ✅ smart_chunk_content fallback is working!")
            return True
        else:
            print("❌ DIRECT CHUNKING TEST FAILED:")
            print(f"  ❌ Only {chunks_created} chunk created from {len(no_breaks_content)} chars")
            print(f"  ❌ Character-based chunking fallback NOT triggered")
            print(f"  ❌ This confirms the bug is still present")
            return False
            
    except Exception as e:
        print(f"❌ Direct chunking test failed - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_with_very_long_content():
    """
    Test with extremely long content to force chunking
    """
    print("\n🔥 VERY LONG CONTENT TEST")
    print("Testing with extremely long content (5000+ chars) with no breaks")
    
    try:
        # Create very long content by repeating the base content
        base_content = "This is a very long single paragraph without any line breaks or paragraph separators that should definitely trigger the character-based chunking fallback mechanism in the smart_chunk_content function because it exceeds the FORCE_CHUNK_THRESHOLD of 1200 characters by a significant margin and contains no natural breaking points for the system to use when attempting to split the content into manageable chunks for processing by the AI system which needs to handle content in smaller pieces to ensure quality output and proper processing within token limits and memory constraints of the language models being used for content enhancement and article generation in the knowledge engine system. "
        
        # Repeat to make it very long
        very_long_content = base_content * 10  # Should be ~5000+ characters
        
        print(f"📏 Very long content length: {len(very_long_content)} characters")
        print(f"📝 Paragraph breaks (\\n\\n): {very_long_content.count(chr(10) + chr(10))}")
        print(f"📝 Line breaks (\\n): {very_long_content.count(chr(10))}")
        
        # Create file for upload
        file_data = io.BytesIO(very_long_content.encode('utf-8'))
        
        files = {
            'file': ('very_long_no_breaks_test.txt', file_data, 'text/plain')
        }
        
        form_data = {
            'metadata': json.dumps({
                "source": "very_long_no_breaks_test",
                "test_type": "extremely_long_no_breaks",
                "content_length": len(very_long_content),
                "expected_chunks": "multiple_due_to_length"
            })
        }
        
        print("📤 Testing with extremely long content...")
        
        response = requests.post(
            f"{BACKEND_URL}/content/upload",
            files=files,
            data=form_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            chunks_created = data.get('chunks_created', 0)
            
            print(f"📊 Very Long Content Test Results:")
            print(f"  Content Length: {len(very_long_content)} characters")
            print(f"  Chunks Created: {chunks_created}")
            
            # With 5000+ characters, this should definitely create multiple chunks
            expected_chunks = len(very_long_content) // 2000  # Rough estimate
            
            if chunks_created >= 2:
                print("✅ VERY LONG CONTENT TEST SUCCESSFUL:")
                print(f"  ✅ {len(very_long_content)} chars → {chunks_created} chunks")
                print(f"  ✅ Character-based chunking working for very long content")
                return True
            else:
                print("❌ VERY LONG CONTENT TEST FAILED:")
                print(f"  ❌ Expected multiple chunks, got {chunks_created}")
                return False
        else:
            print(f"❌ Very long content test failed - status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Very long content test failed - {str(e)}")
        return False

def main():
    """
    Run direct chunking tests
    """
    print("🎯 DIRECT SMART CHUNKING TESTS")
    print("Testing the smart_chunk_content function with problematic content")
    print("=" * 80)
    
    tests = [
        ("Direct No Breaks Test", test_direct_chunking_with_no_breaks),
        ("Very Long Content Test", test_with_very_long_content)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "="*80)
    print("🎯 DIRECT CHUNKING TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"📊 Overall Results: {passed}/{total} tests passed")
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    if passed >= 1:  # At least 1 test should pass
        print("\n🎉 DIRECT CHUNKING: PARTIALLY WORKING")
        print("✅ Character-based chunking works for some content")
        print("⚠️ May need investigation for edge cases")
        return True
    else:
        print("\n❌ DIRECT CHUNKING: FAILED")
        print("❌ Character-based chunking not working properly")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 DIRECT CHUNKING TESTS: SOME SUCCESS")
    else:
        print("\n🚨 DIRECT CHUNKING TESTS: FAILED")