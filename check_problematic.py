#!/usr/bin/env python3
import requests
import json

response = requests.get("https://content-pipeline-5.preview.emergentagent.com/api/content-library")
data = response.json()

for article in data['articles']:
    if '```html' in article['content']:
        print(f'PROBLEMATIC ARTICLE: {article["title"]}')
        print(f'ID: {article["id"]}')
        print(f'Article Type: {article.get("article_type", "unknown")}')
        print(f'Created: {article.get("created_at", "unknown")}')
        print(f'Metadata: {article.get("metadata", {})}')
        print(f'Content (first 500 chars):')
        print(repr(article["content"][:500]))
        print()