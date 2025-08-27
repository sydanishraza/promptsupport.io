#!/usr/bin/env python3
"""
Simple Google Maps DOCX Test - Focus on Image Processing Issue
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com') + '/api'

def simple_test():
    """Simple test focusing on the image processing issue"""
    print("🗺️ SIMPLE GOOGLE MAPS DOCX IMAGE PROCESSING TEST")
    print("=" * 50)
    
    docx_file_path = '/app/Google_Map_JavaScript_API_Tutorial.docx'
    
    try:
        with open(docx_file_path, 'rb') as docx_file:
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', docx_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true'
            }
            
            print("📤 Processing Google Maps DOCX (simplified test)...")
            
            response = requests.post(
                f"{BACKEND_URL}/training/process",
                files=files,
                data=form_data,
                timeout=180  # 3 minutes timeout
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                images_processed = data.get('images_processed', 0)
                success = data.get('success', False)
                articles = data.get('articles', [])
                
                print(f"✅ Success: {success}")
                print(f"🖼️ Images Processed: {images_processed}")
                print(f"📚 Articles: {len(articles)}")
                
                # Key findings
                if images_processed == 0:
                    print("\n❌ CRITICAL ISSUE CONFIRMED:")
                    print("  - Google Maps DOCX contains images but 0 were processed")
                    print("  - Image detection/extraction pipeline is broken")
                    print("  - This matches the user-reported issue")
                else:
                    print(f"\n✅ Images processed successfully: {images_processed}")
                
                if articles and len(articles) > 0:
                    article = articles[0]
                    content = article.get('content', '') or article.get('html', '')
                    
                    # Check for embedded images
                    figure_count = content.count('<figure')
                    img_count = content.count('<img')
                    
                    if figure_count > 0 or img_count > 0:
                        print(f"✅ Images embedded in articles: {figure_count + img_count}")
                    else:
                        print("❌ No images embedded in articles")
                
                return images_processed > 0
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                if response.text:
                    print(f"Error: {response.text[:200]}")
                return False
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out - backend processing too slow")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = simple_test()
    print(f"\n{'✅' if success else '❌'} Test Result: {'PASSED' if success else 'FAILED'}")