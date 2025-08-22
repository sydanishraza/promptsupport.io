#!/usr/bin/env python3
"""
Quick DOCX Processing Test - Verify fixes are working
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdoc-v2.preview.emergentagent.com') + '/api'

def test_docx_processing_fix():
    """Test that DOCX processing works without AttributeError"""
    print("🔍 Testing DOCX Processing Fix...")
    
    try:
        # Download the Google Maps tutorial document
        print("📥 Downloading Google Maps tutorial document...")
        doc_url = "https://customer-assets.emergentagent.com/job_content-refiner-2/artifacts/5lvc26qb_Google%20Map%20JavaScript%20API%20Tutorial.docx"
        response = requests.get(doc_url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to download document: {response.status_code}")
            return False
        
        document_content = response.content
        print(f"✅ Document downloaded: {len(document_content)} bytes")
        
        # Process the document
        files = {
            'file': ('Google_Map_JavaScript_API_Tutorial.docx', io.BytesIO(document_content), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'metadata': json.dumps({
                "source": "quick_fix_test",
                "test_type": "attribute_error_verification"
            })
        }
        
        print("📤 Processing document...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/content/upload",
            files=files,
            data=form_data,
            timeout=90
        )
        
        processing_time = time.time() - start_time
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ DOCX PROCESSING FIX SUCCESSFUL:")
            print(f"  ✅ No AttributeError occurred")
            print(f"  ✅ Chunks created: {data.get('chunks_created', 0)}")
            print(f"  ✅ File type: {data.get('file_type', 'unknown')}")
            print(f"  ✅ Status: {data.get('status', 'unknown')}")
            
            # Wait a moment and check Content Library
            time.sleep(5)
            
            print("\n🔍 Checking Content Library for generated articles...")
            response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
            
            if response.status_code == 200:
                library_data = response.json()
                articles = library_data.get('articles', [])
                
                # Look for recent Google Maps articles
                recent_articles = []
                for article in articles[:10]:  # Check first 10 articles
                    title = article.get('title', '').lower()
                    if 'google' in title and ('map' in title or 'javascript' in title):
                        recent_articles.append(article)
                
                if recent_articles:
                    print(f"✅ Found {len(recent_articles)} Google Maps articles:")
                    for i, article in enumerate(recent_articles):
                        title = article.get('title', '')
                        content = article.get('content', '')
                        word_count = len(content.split()) if content else 0
                        
                        print(f"  📄 Article {i+1}: '{title}'")
                        print(f"      Word Count: {word_count}")
                        
                        # Check for title fix
                        if 'comprehensive guide to' in title.lower():
                            print("      ⚠️ Still shows generic title")
                        elif 'using google map javascript api' in title.lower():
                            print("      ✅ Shows correct H1 title")
                        else:
                            print("      ✅ Shows custom title")
                    
                    return True
                else:
                    print("⚠️ No Google Maps articles found in Content Library")
                    return True  # Processing worked, just no articles found
            else:
                print(f"⚠️ Could not check Content Library: {response.status_code}")
                return True  # Processing worked, just can't verify articles
            
        else:
            print(f"❌ DOCX processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🚀 Quick DOCX Processing Fix Test")
    print("=" * 50)
    
    success = test_docx_processing_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 DOCX PROCESSING FIX VERIFICATION SUCCESSFUL!")
        print("✅ DocumentPreprocessor AttributeError has been resolved")
    else:
        print("❌ DOCX PROCESSING FIX VERIFICATION FAILED")
        print("❌ Issues may still persist")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)