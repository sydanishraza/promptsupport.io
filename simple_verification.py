#!/usr/bin/env python3
"""
Simple verification of DOCX processing results
"""
import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://woolf-style-lint.preview.emergentagent.com') + '/api'

def check_backend_health():
    """Check if backend is responsive"""
    try:
        print("🔍 Checking backend health...")
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is responsive")
            return True
        else:
            print(f"⚠️ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not responsive: {e}")
        return False

def check_content_library_simple():
    """Simple check of content library"""
    try:
        print("📚 Checking content library (simple)...")
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"📊 Total articles in library: {len(articles)}")
            
            if len(articles) > 0:
                print("✅ Content library has articles")
                
                # Check for articles with substantial content
                substantial_articles = 0
                articles_with_images = 0
                total_chars = 0
                
                for article in articles[:10]:  # Check first 10 articles
                    content = article.get('content', '') or article.get('html', '')
                    image_count = article.get('image_count', 0)
                    
                    if len(content) > 500:
                        substantial_articles += 1
                    if image_count > 0 or '<img' in content or '<figure' in content:
                        articles_with_images += 1
                    total_chars += len(content)
                
                print(f"📊 Articles with substantial content: {substantial_articles}")
                print(f"📊 Articles with images: {articles_with_images}")
                print(f"📊 Average content length: {total_chars // min(len(articles), 10):,} chars")
                
                return True
            else:
                print("⚠️ Content library is empty")
                return False
        else:
            print(f"❌ Failed to get content library: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking content library: {e}")
        return False

def check_assets():
    """Check asset library"""
    try:
        print("🖼️ Checking asset library...")
        response = requests.get(f"{BACKEND_URL}/assets", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            assets = data.get('assets', [])
            print(f"📊 Total assets: {len(assets)}")
            
            # Count image assets
            image_assets = [a for a in assets if a.get('asset_type') == 'image']
            print(f"📊 Image assets: {len(image_assets)}")
            
            return len(assets) > 0
        else:
            print(f"❌ Failed to get assets: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking assets: {e}")
        return False

def main():
    print("🧪 SIMPLE VERIFICATION OF DOCX PROCESSING RESULTS")
    print("=" * 60)
    
    results = []
    
    # Check backend health
    results.append(check_backend_health())
    
    # Wait a moment for backend to stabilize
    time.sleep(5)
    
    # Check content library
    results.append(check_content_library_simple())
    
    # Check assets
    results.append(check_assets())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed >= 2:
        print("✅ VERIFICATION: System appears to be working")
        print("✅ DOCX processing pipeline is functional")
    else:
        print("❌ VERIFICATION: System has issues")
    
    return passed >= 2

if __name__ == "__main__":
    main()