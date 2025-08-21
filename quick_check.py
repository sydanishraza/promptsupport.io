#!/usr/bin/env python3
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-6.preview.emergentagent.com') + '/api'

try:
    print("🔍 Checking content library...")
    response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        print(f"📊 Total articles: {len(articles)}")
        
        # Look for recent articles (last 10 minutes)
        import time
        current_time = time.time()
        recent_articles = []
        
        for article in articles:
            created_at = article.get('created_at', '')
            if created_at:
                try:
                    from datetime import datetime
                    article_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                    if current_time - article_time < 600:  # Within last 10 minutes
                        recent_articles.append(article)
                except:
                    pass
        
        print(f"📊 Recent articles (last 10 min): {len(recent_articles)}")
        
        if recent_articles:
            print("🎯 Recent articles found:")
            for i, article in enumerate(recent_articles[:5]):
                title = article.get('title', 'No title')[:50]
                content_len = len(article.get('content', ''))
                image_count = article.get('image_count', 0)
                print(f"  {i+1}. {title} ({content_len} chars, {image_count} images)")
    else:
        print(f"❌ Failed to get content library: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")