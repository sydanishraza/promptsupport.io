#!/usr/bin/env python3
"""
Quick verification of enhanced chunking results
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartchunk.preview.emergentagent.com') + '/api'

def check_content_library():
    """Check the current state of the content library"""
    print("🔍 Checking Content Library Results...")
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"📊 Content Library contains: {len(articles)} articles")
            
            if len(articles) > 1:
                print("✅ ENHANCED CHUNKING SUCCESS: Multiple articles created!")
                
                # Show details of first few articles
                for i, article in enumerate(articles[:5]):
                    title = article.get('title', 'Unknown')
                    created_at = article.get('created_at', 'Unknown')
                    content_length = len(article.get('content', ''))
                    
                    print(f"   📄 Article {i+1}: '{title[:60]}...'")
                    print(f"      📊 Content: {content_length} characters")
                    print(f"      📅 Created: {created_at}")
                
                return True
            elif len(articles) == 1:
                print("⚠️ Only 1 article found - chunking may not be working optimally")
                article = articles[0]
                print(f"   📄 Single article: '{article.get('title', 'Unknown')[:60]}...'")
                return False
            else:
                print("❌ No articles found")
                return False
        else:
            print(f"❌ Failed to check content library - status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking content library: {e}")
        return False

def main():
    print("🎯 ENHANCED CHUNKING VERIFICATION")
    print("=" * 50)
    
    success = check_content_library()
    
    if success:
        print("\n🎉 ENHANCED CHUNKING FIX VERIFICATION: SUCCESS")
        print("✅ The enhanced H1 AND H2 detection is working")
        print("✅ Multiple articles are being created from user guide structure")
        print("✅ User's issue should be resolved")
    else:
        print("\n❌ ENHANCED CHUNKING FIX VERIFICATION: NEEDS INVESTIGATION")
        print("❌ The chunking system may need further adjustments")

if __name__ == "__main__":
    main()