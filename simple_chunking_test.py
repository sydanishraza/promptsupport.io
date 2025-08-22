#!/usr/bin/env python3
"""
Simple test to verify the AGGRESSIVE FORCE CHUNKING fix
"""

import requests
import json
import os
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdoc-v2.preview.emergentagent.com') + '/api'

def test_force_chunking():
    """Simple test of force chunking with clear H1 structure"""
    print("🔥 Testing AGGRESSIVE FORCE CHUNKING FIX")
    
    # Create content with clear H1 structure and over 4,000 characters
    content = """# Introduction to Force Chunking Test

This document tests the AGGRESSIVE FORCE CHUNKING fix that should create multiple articles for content over 3,000 characters. """ + "A" * 800 + """

# Section 1: First Major Topic

This is the first major section of the document. It contains substantial content to ensure the document exceeds the 3,000 character threshold for force chunking. """ + "B" * 800 + """

# Section 2: Second Major Topic  

This is the second major section with additional comprehensive content. The system should detect these H1 headings and use them as natural break points for creating separate articles. """ + "C" * 800 + """

# Section 3: Third Major Topic

This is the third section that provides even more content to ensure we have a substantial document that definitely exceeds the chunking threshold. """ + "D" * 800 + """

# Section 4: Final Major Topic

This final section completes our test document with additional content to ensure comprehensive testing of the force chunking functionality. """ + "E" * 800

    print(f"📊 Content length: {len(content)} characters")
    print(f"🎯 H1 sections: 5 (Introduction + 4 sections)")
    print(f"🔥 Should create 5 separate articles")
    
    try:
        file_data = io.BytesIO(content.encode('utf-8'))
        
        files = {
            'file': ('simple_chunking_test.txt', file_data, 'text/plain')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true',
            'template_instructions': json.dumps({
                "template_id": "phase1_document_processing"
            })
        }
        
        print("📤 Processing test document...")
        
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=90
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"📚 Articles Created: {len(articles)}")
            
            for i, article in enumerate(articles):
                title = article.get('title', 'No Title')
                content_len = len(article.get('content', ''))
                print(f"   Article {i+1}: '{title}' ({content_len} chars)")
            
            if len(articles) > 1:
                print("✅ FORCE CHUNKING IS WORKING - Multiple articles created")
                return True
            else:
                print("❌ FORCE CHUNKING NOT WORKING - Only single article created")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_force_chunking()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")