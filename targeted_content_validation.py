#!/usr/bin/env python3
"""
TARGETED CONTENT LIBRARY VALIDATION
Focus on specific issues and provide detailed analysis
"""

import requests
import json
from bs4 import BeautifulSoup
import re

# Backend URL
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def analyze_content_library_issues():
    """Analyze specific Content Library issues in detail"""
    try:
        print("🔍 TARGETED CONTENT LIBRARY VALIDATION")
        print("=" * 60)
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Content Library access failed: {response.status_code}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"📚 Analyzing {len(articles)} articles")
        print()
        
        # Detailed analysis of each article
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            article_type = article.get('article_type', 'unknown')
            
            print(f"📄 ARTICLE {i}: {title[:60]}...")
            print(f"   Type: {article_type}")
            print(f"   Content length: {len(content)} characters")
            
            # Check for HTML document structure wrapping
            if content.startswith('```html') or '<!DOCTYPE html>' in content:
                print("   ❌ ISSUE: Content wrapped in HTML document structure")
                print("   🔧 NEEDS FIX: clean_article_html_content() not working properly")
            else:
                print("   ✅ GOOD: Clean semantic HTML content")
            
            # Parse content for detailed analysis
            if content.startswith('```html'):
                # Extract content from code block
                actual_content = content.replace('```html\n', '').replace('\n```', '')
                soup = BeautifulSoup(actual_content, 'html.parser')
            else:
                soup = BeautifulSoup(content, 'html.parser')
            
            # Check for text duplication
            duplications_found = 0
            list_items = soup.find_all('li')
            for li in list_items:
                text = li.get_text().strip()
                if text:
                    sentences = re.split(r'[.!?]+', text)
                    for j in range(len(sentences) - 1):
                        sentence1 = sentences[j].strip()
                        sentence2 = sentences[j + 1].strip()
                        if sentence1 and sentence2 and sentence1 == sentence2:
                            duplications_found += 1
                            print(f"   ❌ DUPLICATION: '{sentence1[:50]}...'")
            
            if duplications_found == 0:
                print("   ✅ GOOD: No text duplications found")
            
            # Check code blocks
            code_blocks = soup.find_all(['pre', 'code'])
            empty_code_blocks = 0
            working_code_blocks = 0
            
            for block in code_blocks:
                code_text = block.get_text().strip()
                if not code_text:
                    empty_code_blocks += 1
                else:
                    working_code_blocks += 1
            
            if empty_code_blocks > 0:
                print(f"   ❌ ISSUE: {empty_code_blocks} empty code blocks")
            else:
                print(f"   ✅ GOOD: {working_code_blocks} working code blocks")
            
            # Check ordered lists
            ordered_lists = soup.find_all('ol')
            fragmented_lists = 0
            proper_lists = 0
            
            for ol in ordered_lists:
                list_items = ol.find_all('li', recursive=False)
                if len(list_items) == 1:
                    fragmented_lists += 1
                else:
                    proper_lists += 1
            
            if fragmented_lists > 0:
                print(f"   ❌ ISSUE: {fragmented_lists} fragmented lists")
            else:
                print(f"   ✅ GOOD: {proper_lists} properly structured lists")
            
            # Check WYSIWYG features
            wysiwyg_features = []
            if soup.find_all(['div', 'ul'], class_=re.compile(r'toc|table-of-contents')):
                wysiwyg_features.append('Mini-TOC')
            if soup.find_all('div', class_=re.compile(r'callout')):
                wysiwyg_features.append('Callouts')
            if soup.find_all('a', href=re.compile(r'^#')):
                wysiwyg_features.append('Anchor links')
            
            if wysiwyg_features:
                print(f"   ✅ WYSIWYG FEATURES: {', '.join(wysiwyg_features)}")
            else:
                print("   ⚠️  No WYSIWYG features detected")
            
            print()
        
        # Summary
        print("=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)
        
        # Count issues
        html_wrapper_issues = sum(1 for a in articles if a.get('content', '').startswith('```html') or '<!DOCTYPE html>' in a.get('content', ''))
        
        print(f"📊 CRITICAL ISSUES ANALYSIS:")
        print(f"   Articles with HTML wrapper issues: {html_wrapper_issues}/{len(articles)}")
        
        if html_wrapper_issues == 0:
            print("✅ HTML WRAPPER CLEANING: WORKING")
        else:
            print("❌ HTML WRAPPER CLEANING: NEEDS ATTENTION")
            print("🔧 RECOMMENDATION: Fix clean_article_html_content() function")
        
        # Overall assessment
        if html_wrapper_issues == 0:
            print("\n🎉 MAJOR FIXES ARE WORKING!")
            print("✅ Content is properly cleaned for WYSIWYG editors")
            return True
        else:
            print(f"\n❌ CRITICAL ISSUES REMAIN: {html_wrapper_issues} articles need fixing")
            print("❌ Content is not properly cleaned for WYSIWYG editors")
            return False
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = analyze_content_library_issues()
    
    if success:
        print("\n🎉 VALIDATION PASSED: Content Library fixes are working!")
    else:
        print("\n❌ VALIDATION FAILED: Content Library issues remain")