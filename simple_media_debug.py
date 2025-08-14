#!/usr/bin/env python3
"""
Simple Media Debug Test for real_visual_document.md
"""

import requests
import json
import os
import re
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdocs-23.preview.emergentagent.com') + '/api'

def main():
    print("🔍 SIMPLE MEDIA DEBUG TEST")
    print("🎯 Testing real_visual_document.md processing")
    print("=" * 60)
    
    # Step 1: Load and analyze source document
    print("\n📄 Step 1: Loading real_visual_document.md...")
    try:
        with open('/app/real_visual_document.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Document loaded: {len(content)} characters")
        
        # Count embedded images
        svg_images = re.findall(r'data:image/svg\+xml;base64,[A-Za-z0-9+/=]+', content)
        print(f"🖼️ Found {len(svg_images)} embedded SVG images")
        
        # Show first image details
        if svg_images:
            first_image = svg_images[0]
            print(f"   First image: {len(first_image)} chars")
            print(f"   Preview: {first_image[:80]}...")
        
    except Exception as e:
        print(f"❌ Failed to load document: {e}")
        return False
    
    # Step 2: Check current Content Library state
    print("\n📚 Step 2: Checking current Content Library state...")
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            initial_count = len(articles)
            
            print(f"✅ Content Library accessible: {initial_count} articles")
            
            # Check for articles with media
            articles_with_media = 0
            total_media_items = 0
            
            for article in articles[:10]:  # Check first 10 articles
                article_content = article.get('content', '')
                media_count = len(re.findall(r'data:image/', article_content))
                if media_count > 0:
                    articles_with_media += 1
                    total_media_items += media_count
            
            print(f"🖼️ Articles with media: {articles_with_media}/10 (checked)")
            print(f"🖼️ Total media items found: {total_media_items}")
            
            # Show sample article with media
            for article in articles[:5]:
                article_content = article.get('content', '')
                if 'data:image/' in article_content:
                    title = article.get('title', 'Untitled')
                    media_count = len(re.findall(r'data:image/', article_content))
                    print(f"   📄 '{title}': {media_count} images")
                    break
            
        else:
            print(f"❌ Content Library not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Content Library check failed: {e}")
        return False
    
    # Step 3: Test simple text processing with media
    print("\n⚙️ Step 3: Testing text processing with media...")
    try:
        # Use a smaller portion of the document for testing
        test_content = content[:2000]  # First 2000 characters
        
        # Count media in test content
        test_media = re.findall(r'data:image/svg\+xml;base64,[A-Za-z0-9+/=]+', test_content)
        print(f"📤 Processing {len(test_content)} chars with {len(test_media)} images")
        
        process_request = {
            "content": test_content,
            "content_type": "text",
            "metadata": {
                "source": "simple_media_debug_test",
                "test_type": "media_extraction_debug",
                "original_filename": "real_visual_document_sample.md"
            }
        }
        
        response = requests.post(
            f"{BACKEND_URL}/content/process",
            json=process_request,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Processing successful: {data.get('chunks_created', 0)} chunks")
            job_id = data.get('job_id')
            
            # Wait and check job status
            time.sleep(3)
            
            if job_id:
                job_response = requests.get(f"{BACKEND_URL}/jobs/{job_id}", timeout=10)
                if job_response.status_code == 200:
                    job_data = job_response.json()
                    print(f"📋 Job status: {job_data.get('status')}")
                    print(f"📋 Chunks created: {job_data.get('chunks_created', 0)}")
            
        else:
            print(f"❌ Processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Text processing failed: {e}")
        return False
    
    # Step 4: Check if new Content Library articles were created
    print("\n📚 Step 4: Checking for new Content Library articles...")
    try:
        time.sleep(5)  # Wait for article creation
        
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            new_count = len(articles)
            
            print(f"📊 Content Library articles: {new_count} (was {initial_count})")
            
            if new_count > initial_count:
                print("✅ New articles created!")
                
                # Check the newest articles for media
                for article in articles[:3]:  # Check first 3 (newest)
                    title = article.get('title', 'Untitled')
                    content = article.get('content', '')
                    metadata = article.get('metadata', {})
                    
                    if metadata.get('source') == 'simple_media_debug_test':
                        media_count = len(re.findall(r'data:image/', content))
                        print(f"   🎯 Test article: '{title}'")
                        print(f"      Content length: {len(content)} chars")
                        print(f"      Media items: {media_count}")
                        
                        if media_count > 0:
                            print("      ✅ Media preserved in article!")
                            # Show sample media
                            media_match = re.search(r'data:image/[^)]+', content)
                            if media_match:
                                media_url = media_match.group(0)
                                print(f"      🖼️ Sample: {media_url[:60]}...")
                        else:
                            print("      ❌ No media found in article")
                        
                        return media_count > 0
            else:
                print("⚠️ No new articles created")
                return False
                
        else:
            print(f"❌ Could not check updated Content Library: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Content Library check failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Simple Media Debug Test")
    success = main()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ MEDIA EXTRACTION TEST PASSED")
        print("🖼️ Images are being preserved in generated articles")
    else:
        print("❌ MEDIA EXTRACTION TEST FAILED")
        print("🖼️ Images are NOT being preserved in generated articles")
    print("=" * 60)
    
    exit(0 if success else 1)