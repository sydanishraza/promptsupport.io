#!/usr/bin/env python3
"""
Quick PDF Processing Status Check
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://docai-promptsupport.preview.emergentagent.com') + '/api'

def check_system_status():
    """Check if the system is responsive"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is responsive")
            return True
        else:
            print(f"⚠️ Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not responsive: {e}")
        return False

def check_content_library():
    """Check current content library status"""
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"📚 Content Library: {len(articles)} total articles")
            
            # Look for recent PDF-related articles
            pdf_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                if 'whisk' in title or 'studio' in title or 'integration' in title:
                    pdf_articles.append(article)
            
            if pdf_articles:
                print(f"🎯 Found {len(pdf_articles)} potential PDF articles:")
                for i, article in enumerate(pdf_articles[:3]):  # Show first 3
                    print(f"   {i+1}. {article.get('title', 'Untitled')}")
                    print(f"      Created: {article.get('created_at', 'Unknown')}")
                    print(f"      Words: {article.get('word_count', 'Unknown')}")
            else:
                print("⚠️ No PDF-related articles found yet")
            
            return True
        else:
            print(f"❌ Content Library check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Content Library check failed: {e}")
        return False

def check_asset_library():
    """Check current asset library status"""
    try:
        response = requests.get(f"{BACKEND_URL}/assets", timeout=15)
        if response.status_code == 200:
            data = response.json()
            assets = data.get('assets', [])
            print(f"📎 Asset Library: {len(assets)} total assets")
            
            # Look for recent assets
            recent_assets = []
            for asset in assets:
                filename = asset.get('filename', '').lower()
                if 'whisk' in filename or 'studio' in filename or asset.get('asset_type') == 'image':
                    recent_assets.append(asset)
            
            if recent_assets:
                print(f"🖼️ Found {len(recent_assets)} potential PDF assets")
            else:
                print("⚠️ No PDF-related assets found")
            
            return True
        else:
            print(f"❌ Asset Library check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Asset Library check failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 QUICK PDF PROCESSING STATUS CHECK")
    print("="*50)
    
    # Check system components
    system_ok = check_system_status()
    content_ok = check_content_library()
    assets_ok = check_asset_library()
    
    print("\n📊 SUMMARY:")
    if system_ok and content_ok and assets_ok:
        print("✅ System is operational - PDF processing may be ongoing in background")
    else:
        print("❌ System has connectivity issues - PDF processing likely failed")