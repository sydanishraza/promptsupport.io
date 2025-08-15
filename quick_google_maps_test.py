#!/usr/bin/env python3
"""
Quick Google Maps DOCX Image Processing Test
Based on backend logs analysis
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://docai-promptsupport.preview.emergentagent.com') + '/api'

def test_google_maps_docx_quick():
    """Quick test of Google Maps DOCX processing based on backend logs"""
    print("🗺️ QUICK GOOGLE MAPS DOCX IMAGE PROCESSING TEST")
    print("=" * 60)
    
    docx_file_path = '/app/Google_Map_JavaScript_API_Tutorial.docx'
    
    # Verify file exists
    if not os.path.exists(docx_file_path):
        print("❌ Google Maps DOCX file not found")
        return False
    
    file_size = os.path.getsize(docx_file_path)
    print(f"📄 File: {docx_file_path}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    try:
        with open(docx_file_path, 'rb') as docx_file:
            files = {
                'file': ('Google_Map_JavaScript_API_Tutorial.docx', docx_file, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            form_data = {
                'template_id': 'phase1_document_processing',
                'training_mode': 'true'
            }
            
            print("📤 Processing Google Maps DOCX...")
            start_time = time.time()
            
            response = requests.post(
                f"{BACKEND_URL}/training/process",
                files=files,
                data=form_data,
                timeout=300
            )
            
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing Time: {processing_time:.2f} seconds")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Key metrics
                success = data.get('success', False)
                images_processed = data.get('images_processed', 0)
                articles = data.get('articles', [])
                session_id = data.get('session_id')
                
                print(f"\n📋 RESULTS:")
                print(f"  ✅ Success: {success}")
                print(f"  🖼️ Images Processed: {images_processed}")
                print(f"  📚 Articles Generated: {len(articles)}")
                print(f"  🆔 Session ID: {session_id}")
                
                # Detailed analysis
                if articles:
                    article = articles[0]
                    title = article.get('title', 'Untitled')
                    word_count = article.get('word_count', 0)
                    content = article.get('content', '') or article.get('html', '')
                    
                    print(f"\n📄 FIRST ARTICLE:")
                    print(f"  Title: {title}")
                    print(f"  Word Count: {word_count:,}")
                    print(f"  Content Length: {len(content):,} characters")
                    
                    # Check for images in content
                    figure_count = content.count('<figure')
                    img_count = content.count('<img')
                    api_static_count = content.count('/api/static/uploads/')
                    
                    print(f"  HTML Images: {figure_count} figures, {img_count} img tags")
                    print(f"  Image URLs: {api_static_count} /api/static/uploads/ references")
                    
                    # Check for Google Maps content
                    maps_keywords = ['google', 'map', 'javascript', 'api']
                    content_lower = content.lower()
                    found_keywords = [kw for kw in maps_keywords if kw in content_lower]
                    print(f"  Maps Keywords: {found_keywords}")
                
                # Test results analysis
                print(f"\n🔍 ANALYSIS:")
                
                if success:
                    print("  ✅ DOCX Processing Pipeline: WORKING")
                else:
                    print("  ❌ DOCX Processing Pipeline: FAILED")
                
                if processing_time < 180:
                    print(f"  ✅ Backend Processing Time: ACCEPTABLE ({processing_time:.1f}s)")
                else:
                    print(f"  ⚠️ Backend Processing Time: SLOW ({processing_time:.1f}s)")
                
                if images_processed > 0:
                    print(f"  ✅ Image Detection and Extraction: WORKING ({images_processed} images)")
                else:
                    print("  ❌ Image Detection and Extraction: FAILED (0 images)")
                
                if figure_count > 0 or img_count > 0:
                    print(f"  ✅ Image Tokenization: WORKING ({figure_count + img_count} embedded)")
                else:
                    print("  ❌ Image Tokenization: FAILED (no embedded images)")
                
                # Overall assessment
                critical_issues = []
                if images_processed == 0:
                    critical_issues.append("No images detected/extracted from DOCX")
                if figure_count == 0 and img_count == 0:
                    critical_issues.append("No images embedded in final articles")
                if not success:
                    critical_issues.append("Processing pipeline failed")
                
                print(f"\n🎯 CRITICAL ISSUES IDENTIFIED:")
                if critical_issues:
                    for issue in critical_issues:
                        print(f"  ❌ {issue}")
                else:
                    print("  ✅ No critical issues found")
                
                return len(critical_issues) == 0
                
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_maps_docx_quick()
    if success:
        print("\n✅ OVERALL: Google Maps DOCX processing working correctly")
    else:
        print("\n❌ OVERALL: Google Maps DOCX processing has critical issues")