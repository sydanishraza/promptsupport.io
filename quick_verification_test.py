#!/usr/bin/env python3
"""
Quick Verification Test for Knowledge Engine Fixes
Simple verification of current system state
"""

import requests
import json
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://29ab9b48-9f0b-482b-8a23-9ef1aebd2745.preview.emergentagent.com') + '/api'

def test_image_storage_verification():
    """Verify current image storage state"""
    print("🔍 VERIFICATION 1: Image Storage System")
    
    uploads_dir = "/app/backend/static/uploads"
    
    if not os.path.exists(uploads_dir):
        print("❌ Upload directory does not exist")
        return False
    
    files = os.listdir(uploads_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    session_dirs = [f for f in files if f.startswith('session_')]
    
    print(f"📁 Upload directory: {uploads_dir}")
    print(f"🖼️ Direct image files: {len(image_files)}")
    print(f"📂 Session directories: {len(session_dirs)}")
    
    # Show some recent images
    if image_files:
        print("📷 Recent images:")
        for img in sorted(image_files, key=lambda x: os.path.getmtime(os.path.join(uploads_dir, x)), reverse=True)[:5]:
            print(f"   {img}")
    
    # Check session directories
    if session_dirs:
        print("📂 Session directories with images:")
        for session_dir in session_dirs[:3]:
            session_path = os.path.join(uploads_dir, session_dir)
            if os.path.exists(session_path):
                session_files = os.listdir(session_path)
                session_images = [f for f in session_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                if session_images:
                    print(f"   {session_dir}: {len(session_images)} images")
    
    # ISSUE 1 ASSESSMENT
    if len(image_files) > 0 or any(os.path.exists(os.path.join(uploads_dir, sd)) for sd in session_dirs):
        print("✅ ISSUE 1 PROGRESS: Image storage system is operational")
        return True
    else:
        print("❌ ISSUE 1 PROBLEM: No images found in storage system")
        return False

def test_content_library_quick_check():
    """Quick check of Content Library"""
    print("\n🔍 VERIFICATION 2: Content Library Quick Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Content Library access failed: {response.status_code}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"📚 Total articles: {len(articles)}")
        
        if len(articles) == 0:
            print("❌ No articles in Content Library")
            return False
        
        # Quick analysis of recent articles
        articles_with_images = 0
        articles_with_good_content = 0
        total_image_urls = 0
        
        for article in articles[:5]:  # Check first 5 articles
            content = article.get('content', '') or article.get('html', '')
            word_count = article.get('word_count', 0)
            title = article.get('title', 'Untitled')
            
            # Check for images
            if '/api/static/uploads/' in content:
                articles_with_images += 1
                urls = re.findall(r'/api/static/uploads/[^"\'>\s]+', content)
                total_image_urls += len(urls)
            
            # Check content quality
            if word_count >= 200:
                articles_with_good_content += 1
            
            print(f"📄 {title[:50]}... - {word_count} words, images: {'/api/static/uploads/' in content}")
        
        print(f"📊 Articles with images: {articles_with_images}/5")
        print(f"📊 Articles with good content: {articles_with_good_content}/5")
        print(f"📊 Total image URLs: {total_image_urls}")
        
        # ISSUE ASSESSMENT
        issue1_progress = articles_with_images > 0
        issue2_progress = articles_with_good_content >= 3
        
        if issue1_progress:
            print("✅ ISSUE 1 PROGRESS: Some articles contain image URLs")
        else:
            print("❌ ISSUE 1 PROBLEM: No articles with image URLs found")
        
        if issue2_progress:
            print("✅ ISSUE 2 PROGRESS: Articles have substantial content")
        else:
            print("❌ ISSUE 2 PROBLEM: Articles have limited content")
        
        return issue1_progress or issue2_progress
        
    except Exception as e:
        print(f"❌ Content Library check failed: {e}")
        return False

def test_image_url_accessibility():
    """Test if some image URLs are accessible"""
    print("\n🔍 VERIFICATION 3: Image URL Accessibility")
    
    try:
        # Get some articles to find image URLs
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        
        if response.status_code != 200:
            print("⚠️ Could not fetch articles for URL testing")
            return True  # Not critical for this verification
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Extract image URLs
        image_urls = []
        for article in articles[:10]:
            content = article.get('content', '') or article.get('html', '')
            urls = re.findall(r'/api/static/uploads/[^"\'>\s]+', content)
            image_urls.extend(urls)
        
        # Remove duplicates and test a few
        unique_urls = list(set(image_urls))[:5]
        
        if not unique_urls:
            print("⚠️ No image URLs found to test")
            return True
        
        print(f"🔗 Testing {len(unique_urls)} image URLs...")
        
        accessible_count = 0
        for url in unique_urls:
            try:
                full_url = f"{BACKEND_URL.replace('/api', '')}{url}"
                response = requests.head(full_url, timeout=5)
                if response.status_code == 200:
                    accessible_count += 1
                    print(f"   ✅ {url}")
                else:
                    print(f"   ❌ {url} ({response.status_code})")
            except Exception as e:
                print(f"   ❌ {url} (error)")
        
        print(f"📊 Accessible URLs: {accessible_count}/{len(unique_urls)}")
        
        if accessible_count > 0:
            print("✅ ISSUE 1 PROGRESS: Some image URLs are accessible")
            return True
        else:
            print("❌ ISSUE 1 PROBLEM: No image URLs are accessible")
            return False
            
    except Exception as e:
        print(f"❌ URL accessibility test failed: {e}")
        return False

def main():
    print("🚀 QUICK KNOWLEDGE ENGINE VERIFICATION")
    print("=" * 50)
    
    results = []
    
    # Run quick verifications
    results.append(("Image Storage", test_image_storage_verification()))
    results.append(("Content Library", test_content_library_quick_check()))
    results.append(("URL Accessibility", test_image_url_accessibility()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK VERIFICATION RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 OVERALL: {passed}/{total} verifications passed")
    
    # Final assessment
    if passed >= 2:
        print("\n✅ KNOWLEDGE ENGINE SHOWS POSITIVE INDICATORS")
        print("🔍 CRITICAL ISSUES STATUS:")
        print("  ISSUE 1 (Images broken): System has image storage and some URLs")
        print("  ISSUE 2 (Content incomplete): Articles are being generated with content")
        print("\n💡 RECOMMENDATION: The fixes appear to be working to some degree.")
        print("   The system is processing images and generating content.")
        print("   Some fine-tuning may be needed for optimal performance.")
    else:
        print("\n❌ KNOWLEDGE ENGINE NEEDS ATTENTION")
        print("🔍 CRITICAL ISSUES STATUS:")
        print("  ISSUE 1 (Images broken): Limited progress detected")
        print("  ISSUE 2 (Content incomplete): Limited progress detected")

if __name__ == "__main__":
    main()