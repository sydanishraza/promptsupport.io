#!/usr/bin/env python3
"""
Detailed investigation of empty code blocks
"""

import requests
import json
from bs4 import BeautifulSoup

# Backend URL
BACKEND_URL = "https://smartdoc-v2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def investigate_empty_code_blocks():
    """Investigate empty code blocks in detail"""
    try:
        # Get articles
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Content Library access failed: Status {response.status_code}")
            return
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"📚 Investigating {len(articles)} articles for empty code blocks...")
        
        for article in articles:
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            
            if not content:
                continue
                
            print(f"\n🔍 Analyzing article: {title}")
            
            # Parse HTML content
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all code blocks
            code_blocks = soup.find_all(['pre', 'code'])
            
            print(f"   Found {len(code_blocks)} code blocks")
            
            for i, code_block in enumerate(code_blocks):
                code_text = code_block.get_text().strip()
                
                print(f"   Code block {i+1}: {len(code_text)} characters")
                
                # Check if code block is empty or contains only whitespace
                if not code_text or len(code_text) < 10:
                    print(f"   ❌ EMPTY CODE BLOCK FOUND:")
                    print(f"      HTML: {str(code_block)[:200]}...")
                    print(f"      Text: '{code_text}'")
                    print(f"      Length: {len(code_text)}")
                else:
                    print(f"   ✅ Code block has content: {code_text[:50]}...")
                    
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_empty_code_blocks()