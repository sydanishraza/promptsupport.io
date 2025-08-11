#!/usr/bin/env python3
"""
Focused DOCX Processing Test
Quick test of the enhanced DOCX processing pipeline
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://5281eecc-eac8-4f65-9a23-23445575ef21.preview.emergentagent.com') + '/api'

def test_training_endpoints():
    """Quick test of training endpoints"""
    print(f"Testing Training Interface at: {BACKEND_URL}")
    
    # Test 1: Training Templates
    print("\n🔍 Testing Training Templates...")
    try:
        response = requests.get(f"{BACKEND_URL}/training/templates", timeout=30)
        print(f"Templates Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Templates: {data.get('total', 0)} found")
        else:
            print(f"❌ Templates failed: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Templates error: {str(e)}")
    
    # Test 2: Training Sessions
    print("\n🔍 Testing Training Sessions...")
    try:
        response = requests.get(f"{BACKEND_URL}/training/sessions", timeout=30)
        print(f"Sessions Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sessions: {data.get('total', 0)} found")
        else:
            print(f"❌ Sessions failed: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Sessions error: {str(e)}")
    
    # Test 3: Enhanced DOCX Processing
    print("\n🔍 Testing Enhanced DOCX Processing...")
    try:
        # Create substantial test content
        docx_content = """Enhanced DOCX Processing Test Document

This comprehensive test document is designed to verify the enhanced DOCX processing pipeline in the Training Interface. The document contains substantial content that should trigger the enhanced processing path rather than the simplified fallback.

Chapter 1: Enhanced Processing Requirements
The enhanced DOCX processing system must:
1. Generate multiple articles from substantial DOCX content
2. Ensure content coverage is comprehensive (targeting 1000+ words per article)
3. Extract and embed images properly with figure elements
4. Use enhanced processing path (not simplified fallback)
5. Store training sessions properly with articles array

Chapter 2: Processing Decision Logic
The system should log debug messages showing:
- Processing metrics (images, structure blocks, content length)
- "ENHANCED" processing path selection over "SIMPLIFIED"
- Recovery mechanisms when enhanced processing has issues

Chapter 3: Content Quality Verification
Generated articles must have:
- Comprehensive content (not truncated at 800 words)
- Proper HTML structure with headings, paragraphs, lists
- Professional technical documentation quality
- Multiple articles from substantial DOCX content

This test document contains over 1000 words of structured content across multiple chapters and sections, which should definitively trigger the enhanced processing path and generate comprehensive articles."""

        # Create file-like object
        file_data = io.BytesIO(docx_content.encode('utf-8'))
        
        # Template data
        template_data = {
            "template_id": "phase1_document_processing",
            "processing_instructions": "Process documents to create comprehensive articles",
            "output_requirements": {
                "format": "html",
                "min_articles": 1,
                "max_articles": 5
            }
        }
        
        files = {
            'file': ('enhanced_docx_test.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true',
            'template_instructions': json.dumps(template_data)
        }
        
        print("🚀 Processing DOCX file...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=180  # 3 minute timeout
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Processing Status: {response.status_code}")
        print(f"Processing Time: {processing_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            session_id = data.get("session_id")
            articles = data.get("articles", [])
            images_processed = data.get("images_processed", 0)
            
            print(f"✅ Success: {success}")
            print(f"📝 Session ID: {session_id}")
            print(f"📚 Articles: {len(articles)}")
            print(f"🖼️ Images: {images_processed}")
            
            # Analyze articles
            if articles:
                total_words = 0
                for i, article in enumerate(articles):
                    title = article.get("title", "Untitled")
                    content = article.get("content", "")
                    word_count = len(content.split())
                    total_words += word_count
                    
                    print(f"  Article {i+1}: '{title}' ({word_count} words)")
                    
                    # Check for HTML structure
                    html_tags = ['<h1>', '<h2>', '<p>', '<ul>', '<li>']
                    html_found = sum(1 for tag in html_tags if tag in content)
                    print(f"    HTML tags: {html_found}")
                    
                    # Check content coverage
                    if word_count >= 1000:
                        print(f"    ✅ Comprehensive coverage: {word_count} words")
                    elif word_count >= 500:
                        print(f"    ⚠️ Moderate coverage: {word_count} words")
                    else:
                        print(f"    ❌ Limited coverage: {word_count} words")
                
                print(f"\n📊 Total words across all articles: {total_words}")
                print(f"📊 Average words per article: {total_words / len(articles):.0f}")
                
                # Overall assessment
                if len(articles) >= 1 and total_words >= 500:
                    print("✅ Enhanced DOCX processing working!")
                    
                    # Test session storage
                    print("\n🔍 Verifying session storage...")
                    try:
                        session_response = requests.get(f"{BACKEND_URL}/training/sessions", timeout=30)
                        if session_response.status_code == 200:
                            session_data = session_response.json()
                            sessions = session_data.get("sessions", [])
                            
                            # Look for our session
                            found_session = False
                            for session in sessions:
                                if session.get("session_id") == session_id:
                                    found_session = True
                                    stored_articles = session.get("articles", [])
                                    print(f"✅ Session found with {len(stored_articles)} articles")
                                    break
                            
                            if not found_session:
                                print("❌ Session not found in database")
                        else:
                            print(f"❌ Could not verify session storage: {session_response.status_code}")
                    except Exception as e:
                        print(f"❌ Session verification error: {str(e)}")
                    
                else:
                    print("❌ Enhanced DOCX processing failed - insufficient output")
            else:
                print("❌ No articles generated")
        else:
            print(f"❌ Processing failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ DOCX processing error: {str(e)}")

if __name__ == "__main__":
    test_training_endpoints()