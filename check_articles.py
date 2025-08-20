#!/usr/bin/env python3
import requests
import json

response = requests.get("https://article-genius-1.preview.emergentagent.com/api/content-library")
data = response.json()

for i, article in enumerate(data['articles']):
    print(f'Article {i+1}: {article["title"]}')
    content = article['content']
    if '```html' in content:
        print(f'  ❌ HAS HTML WRAPPER')
        print(f'  Content start: {repr(content[:100])}')
    else:
        print(f'  ✅ Clean')
    print()