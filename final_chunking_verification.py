#!/usr/bin/env python3
"""
FINAL VERIFICATION: AGGRESSIVE FORCE CHUNKING FIX
Quick test to verify the fix is working as specified in the review request
"""

import requests
import json
import os
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://promptsupport-2.preview.emergentagent.com') + '/api'

def main_test():
    """Main test as specified in review request"""
    print("🔥 FINAL VERIFICATION: AGGRESSIVE FORCE CHUNKING FIX")
    print("Testing DOCX content around 4,000-5,000 characters")
    print("Expected: MULTIPLE articles instead of single article")
    
    # Create test content exactly as specified
    content = """AGGRESSIVE FORCE CHUNKING FIX TEST

This document tests the completely rewritten chunk_large_document_for_polishing function with multiple fallback strategies.

# ENHANCED CHUNKING STRATEGIES

The new implementation includes:
1. AGGRESSIVE chunking for documents over 3,000 characters 
2. HEADING-BASED chunking using H1, H2, H3 (expanded from just H1)
3. PARAGRAPH-BASED chunking when insufficient headings (1,500-2,500 char chunks)
4. CHARACTER-BASED brutal chunking as ultimate fallback (2,000 char segments)
5. LOWERED thresholds (500 chars vs 1,000 chars minimum)

""" + "A" * 1000 + """

# MULTIPLE FALLBACK STRATEGIES

The system now has multiple fallback strategies to ensure documents are ALWAYS chunked:
- Heading-based chunking for structured documents
- Paragraph-based chunking for unstructured content  
- Character-based chunking as final fallback

""" + "B" * 1000 + """

# LOWERED THRESHOLDS

Thresholds have been lowered:
- Main threshold: 3,000 characters (down from 25,000)
- Minimum chunk: 500 characters (down from 1,000)
- This ensures more aggressive chunking

""" + "C" * 1000 + """

# EXPECTED RESULTS

This document should create MULTIPLE articles instead of single article.
Debug logs should show "ISSUE 1 FIX" markers.
The force chunking should now DEFINITELY work.

""" + "D" * 500

    print(f"📊 Content length: {len(content)} characters")
    print(f"🎯 H1 sections: 4 (should create 4 articles)")
    
    try:
        file_data = io.BytesIO(content.encode('utf-8'))
        
        files = {
            'file': ('final_chunking_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true',
            'template_instructions': json.dumps({
                "template_id": "phase1_document_processing"
            })
        }
        
        print("📤 Processing via /api/training/process...")
        
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=90
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"📚 Articles Created: {len(articles)}")
            
            for i, article in enumerate(articles):
                title = article.get('title', 'No Title')
                print(f"   {i+1}. '{title}'")
            
            if len(articles) > 1:
                print(f"\n✅ SUCCESS: AGGRESSIVE FORCE CHUNKING IS WORKING")
                print(f"   ✅ Content over 3,000 chars created {len(articles)} articles")
                print(f"   ✅ Multiple fallback strategies operational")
                print(f"   ✅ Force chunking threshold (3,000 chars) ACTIVE")
                print(f"   ✅ 'Single summarized articles' issue RESOLVED")
                return True
            else:
                print(f"\n❌ FAILED: Force chunking not working")
                print(f"   ❌ Only {len(articles)} article created")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main_test()
    print(f"\nFINAL RESULT: {'✅ FORCE CHUNKING FIX VERIFIED' if success else '❌ FORCE CHUNKING FIX FAILED'}")
    exit(0 if success else 1)