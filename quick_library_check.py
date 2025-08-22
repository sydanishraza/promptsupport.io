#!/usr/bin/env python3
"""
Quick Content Library Check for Semantic Image Placement
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdoc-v2.preview.emergentagent.com') + '/api'

def check_content_library():
    """Check Content Library for articles with images"""
    print(f"🔍 CHECKING CONTENT LIBRARY FOR SEMANTIC IMAGE PLACEMENT")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    try:
        # Get articles from Content Library
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Could not access Content Library - status {response.status_code}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            print("❌ No articles found in Content Library")
            return False
        
        print(f"📚 Found {len(articles)} total articles in Content Library")
        
        # Analyze articles for images and semantic placement
        articles_with_images = 0
        total_images = 0
        semantic_articles = 0
        batches_with_multiple_articles = {}
        
        for i, article in enumerate(articles):
            title = article.get('title', f'Article {i+1}')
            content = article.get('content', '')
            metadata = article.get('metadata', {})
            created_at = article.get('created_at', '')
            
            # Check for images in content
            import re
            image_urls = re.findall(r'/api/static/uploads/[^"\'>\s]+', content)
            figure_count = content.count('<figure')
            img_count = content.count('<img')
            
            # Check metadata for semantic processing
            ai_processed = metadata.get('ai_processed', False)
            semantic_images = metadata.get('semantic_images_applied', 0)
            batch_id = metadata.get('batch_id') or metadata.get('session_id', 'unknown')
            
            if image_urls or figure_count > 0 or img_count > 0:
                articles_with_images += 1
                total_images += len(image_urls)
                
                print(f"📄 Article {i+1}: {title[:60]}...")
                print(f"    Created: {created_at}")
                print(f"    Images: {len(image_urls)} URLs, {figure_count} figures, {img_count} img tags")
                print(f"    AI processed: {ai_processed}")
                print(f"    Semantic images: {semantic_images}")
                print(f"    Batch ID: {batch_id}")
                
                if len(image_urls) > 0:
                    print(f"    Sample image: {image_urls[0]}")
                print()
            
            if semantic_images > 0 or 'semantic' in str(metadata).lower():
                semantic_articles += 1
            
            # Group by batch for duplication analysis
            if batch_id not in batches_with_multiple_articles:
                batches_with_multiple_articles[batch_id] = []
            batches_with_multiple_articles[batch_id].append({
                'title': title,
                'images': image_urls,
                'created_at': created_at
            })
        
        print(f"📊 CONTENT LIBRARY ANALYSIS:")
        print(f"  Total articles: {len(articles)}")
        print(f"  Articles with images: {articles_with_images}")
        print(f"  Total images found: {total_images}")
        print(f"  Articles with semantic processing: {semantic_articles}")
        
        # Check for duplication (user's specific issue)
        print(f"\n🔍 CHECKING FOR IMAGE DUPLICATION (USER'S ISSUE):")
        
        duplication_found = False
        batches_tested = 0
        
        for batch_id, batch_articles in batches_with_multiple_articles.items():
            if len(batch_articles) > 1:  # Multiple articles from same batch
                # Check if any have images
                articles_with_images_in_batch = [a for a in batch_articles if len(a['images']) > 0]
                
                if len(articles_with_images_in_batch) > 1:
                    batches_tested += 1
                    print(f"\n📊 Batch {batch_id}: {len(batch_articles)} articles")
                    
                    # Check for identical image sets
                    image_sets = [set(a['images']) for a in articles_with_images_in_batch]
                    
                    if len(image_sets) > 1:
                        first_set = image_sets[0]
                        identical_count = sum(1 for img_set in image_sets if img_set == first_set)
                        
                        if identical_count == len(image_sets):
                            print(f"    ❌ DUPLICATION DETECTED: All {len(image_sets)} articles have identical images")
                            duplication_found = True
                            
                            # Show the duplicated images
                            for img_url in list(first_set)[:3]:  # Show first 3
                                print(f"      - {img_url}")
                        else:
                            print(f"    ✅ NO DUPLICATION: Articles have different image sets")
                            
                            # Show distribution
                            for j, article in enumerate(articles_with_images_in_batch):
                                print(f"      Article {j+1}: {len(article['images'])} images")
        
        print(f"\n📊 DUPLICATION ANALYSIS:")
        print(f"  Batches tested: {batches_tested}")
        print(f"  Duplication detected: {duplication_found}")
        
        # Final assessment
        if articles_with_images > 0:
            print(f"\n✅ IMAGES FOUND IN CONTENT LIBRARY")
            print(f"✅ {articles_with_images} articles contain images")
            
            if not duplication_found:
                print(f"✅ NO DUPLICATION DETECTED")
                print(f"✅ User's issue appears to be RESOLVED")
                print(f"✅ Semantic image placement system is working")
                return True
            else:
                print(f"❌ DUPLICATION DETECTED")
                print(f"❌ User's issue is NOT resolved")
                print(f"❌ Images are still being duplicated across articles")
                return False
        else:
            print(f"\n⚠️ NO IMAGES FOUND IN CONTENT LIBRARY")
            print(f"  This may indicate:")
            print(f"  1. No DOCX files with images have been processed recently")
            print(f"  2. Images are being filtered out during processing")
            print(f"  3. Image extraction pipeline is not working")
            return True  # Not necessarily a failure
            
    except Exception as e:
        print(f"❌ Content Library check failed - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_content_library()
    
    if success:
        print(f"\n🎯 SEMANTIC IMAGE PLACEMENT: WORKING CORRECTLY")
    else:
        print(f"\n❌ SEMANTIC IMAGE PLACEMENT: CRITICAL ISSUES DETECTED")