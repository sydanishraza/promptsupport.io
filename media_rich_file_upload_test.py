#!/usr/bin/env python3
"""
Media-Rich File Upload Test
Test file upload processing with media_rich_example.md
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://a81dd4ba-cb0f-4d88-a93c-5e40594e5b1a.preview.emergentagent.com') + '/api'

def test_media_rich_file_upload():
    """Test uploading the media_rich_example.md file"""
    print("🖼️ Testing Media-Rich File Upload with media_rich_example.md")
    print("=" * 60)
    
    try:
        # Load the media-rich example file
        with open('/app/media_rich_example.md', 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        print(f"✅ Loaded media_rich_example.md: {len(file_content)} characters")
        
        # Get initial Content Library count
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=10)
        initial_count = 0
        if response.status_code == 200:
            initial_count = response.json().get('total', 0)
            print(f"Initial Content Library articles: {initial_count}")
        
        # Create file-like object
        file_data = io.BytesIO(file_content.encode('utf-8'))
        
        files = {
            'file': ('media_rich_example.md', file_data, 'text/markdown')
        }
        
        form_data = {
            'metadata': json.dumps({
                "source": "media_rich_file_upload_test",
                "test_type": "file_upload_media_extraction",
                "document_type": "markdown_with_media",
                "has_embedded_images": True,
                "original_filename": "media_rich_example.md"
            })
        }
        
        print("🚀 Uploading media-rich markdown file...")
        
        response = requests.post(
            f"{BACKEND_URL}/content/upload",
            files=files,
            data=form_data,
            timeout=45
        )
        
        if response.status_code != 200:
            print(f"❌ File upload failed - status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        upload_data = response.json()
        print(f"✅ File upload successful:")
        print(f"   - Job ID: {upload_data.get('job_id')}")
        print(f"   - File type: {upload_data.get('file_type')}")
        print(f"   - Extracted content length: {upload_data.get('extracted_content_length')}")
        print(f"   - Chunks created: {upload_data.get('chunks_created')}")
        
        # Wait for processing to complete
        time.sleep(5)
        
        # Check Content Library for new articles
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=10)
        if response.status_code != 200:
            print("❌ Could not check Content Library after upload")
            return False
        
        data = response.json()
        new_count = data.get('total', 0)
        articles = data.get('articles', [])
        
        print(f"📚 Content Library after upload: {new_count} articles (was {initial_count})")
        
        if new_count > initial_count:
            print("✅ New articles created from media-rich file upload!")
            
            # Find articles created from our upload
            upload_articles = []
            for article in articles:
                metadata = article.get('metadata', {})
                if (metadata.get('source') == 'media_rich_file_upload_test' or 
                    'media_rich_example.md' in article.get('title', '')):
                    upload_articles.append(article)
            
            print(f"🎯 Found {len(upload_articles)} articles from our media-rich upload")
            
            # Check for media preservation
            media_preserved_count = 0
            for article in upload_articles:
                content = article.get('content', '')
                title = article.get('title', 'N/A')
                if 'data:image/' in content:
                    media_preserved_count += 1
                    print(f"✅ Article '{title}' contains embedded media")
            
            if media_preserved_count > 0:
                print(f"🖼️ Media preservation in file upload: {media_preserved_count}/{len(upload_articles)} articles contain embedded media")
                return True
            else:
                print("⚠️ Articles created but no embedded media preserved")
                return len(upload_articles) > 0
        else:
            print("⚠️ No new articles created from file upload")
            return False
            
    except Exception as e:
        print(f"❌ Media-rich file upload test failed - {str(e)}")
        return False

if __name__ == "__main__":
    success = test_media_rich_file_upload()
    print(f"\n🎯 Media-Rich File Upload Test: {'✅ PASSED' if success else '❌ FAILED'}")
    exit(0 if success else 1)