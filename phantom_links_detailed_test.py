#!/usr/bin/env python3
"""
DETAILED PHANTOM LINKS ANALYSIS
Detailed analysis of the phantom links issue found in hub articles
"""

import requests
import json
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdoc-v2.preview.emergentagent.com') + '/api'

def analyze_phantom_links():
    """Analyze phantom links in detail"""
    print("🔍 DETAILED PHANTOM LINKS ANALYSIS")
    print("=" * 60)
    
    try:
        # Get all articles from Content Library
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Could not fetch Content Library - status code {response.status_code}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"📚 Analyzing {len(articles)} articles for phantom links...")
        
        # Look for hub articles that might contain phantom links
        hub_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '')
            
            # Identify hub articles by title patterns or content length
            if (any(keyword in title for keyword in ['guide', 'overview', 'integration', 'step-by-step']) and
                len(content) > 3000):  # Substantial content suggesting it's a hub article
                hub_articles.append(article)
        
        print(f"🎯 Found {len(hub_articles)} potential hub articles")
        
        total_phantom_links = 0
        total_working_links = 0
        
        for i, article in enumerate(hub_articles):
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            article_id = article.get('id')
            
            print(f"\n📄 Article {i+1}: {title}")
            print(f"   ID: {article_id}")
            print(f"   Content Length: {len(content)} characters")
            
            # Find all anchor links (#section-name)
            anchor_links = re.findall(r'href=["\']#([^"\']*)["\']', content)
            phantom_count = len(anchor_links)
            total_phantom_links += phantom_count
            
            print(f"   🔗 Phantom anchor links found: {phantom_count}")
            
            if phantom_count > 0:
                print("   📋 Sample phantom links:")
                for link in anchor_links[:5]:  # Show first 5
                    print(f"      - #{link}")
                
                if phantom_count > 5:
                    print(f"      ... and {phantom_count - 5} more")
            
            # Find Content Library links
            content_library_links = re.findall(r'href=["\'][^"\']*content-library[^"\']*["\']', content)
            api_article_links = re.findall(r'href=["\'][^"\']*article/[^"\']*["\']', content)
            
            working_count = len(content_library_links) + len(api_article_links)
            total_working_links += working_count
            
            print(f"   ✅ Working Content Library links: {working_count}")
            
            # Analyze the type of phantom links
            if phantom_count > 0:
                # Categorize phantom links
                setup_links = [link for link in anchor_links if any(keyword in link.lower() for keyword in ['setup', 'start', 'account', 'key'])]
                implementation_links = [link for link in anchor_links if any(keyword in link.lower() for keyword in ['implement', 'sync', 'api', 'integration'])]
                troubleshooting_links = [link for link in anchor_links if any(keyword in link.lower() for keyword in ['trouble', 'error', 'debug', 'problem'])]
                
                print(f"   📊 Link categories:")
                print(f"      Setup-related: {len(setup_links)}")
                print(f"      Implementation-related: {len(implementation_links)}")
                print(f"      Troubleshooting-related: {len(troubleshooting_links)}")
                print(f"      Other: {phantom_count - len(setup_links) - len(implementation_links) - len(troubleshooting_links)}")
        
        print(f"\n📊 OVERALL PHANTOM LINKS ANALYSIS:")
        print(f"   Total hub articles analyzed: {len(hub_articles)}")
        print(f"   Total phantom anchor links: {total_phantom_links}")
        print(f"   Total working Content Library links: {total_working_links}")
        print(f"   Phantom to working ratio: {total_phantom_links}:{total_working_links}")
        
        # Determine severity
        if total_phantom_links > 20:
            severity = "CRITICAL"
            print(f"🚨 {severity}: High number of phantom links detected")
        elif total_phantom_links > 10:
            severity = "HIGH"
            print(f"⚠️ {severity}: Moderate number of phantom links detected")
        elif total_phantom_links > 0:
            severity = "MEDIUM"
            print(f"⚠️ {severity}: Some phantom links detected")
        else:
            severity = "NONE"
            print(f"✅ {severity}: No phantom links detected")
        
        print(f"\n🎯 PHANTOM LINKS ISSUE STATUS:")
        if total_phantom_links == 0:
            print("✅ RESOLVED: No phantom links found")
            print("✅ Hub articles contain only working links to real articles")
            return True
        else:
            print("❌ NOT RESOLVED: Phantom links still present")
            print("❌ Hub articles contain links to non-existent content sections")
            print("❌ Users will encounter broken navigation when clicking these links")
            
            # Provide specific recommendations
            print(f"\n💡 RECOMMENDATIONS:")
            print("1. Replace phantom anchor links with real Content Library article links")
            print("2. Create actual articles for the sections referenced by phantom links")
            print("3. Update hub article generation to use actual article IDs instead of anchor links")
            print("4. Implement link validation to prevent phantom links in generated content")
            
            return False
        
    except Exception as e:
        print(f"❌ Phantom links analysis failed - {str(e)}")
        return False

if __name__ == "__main__":
    success = analyze_phantom_links()
    exit(0 if success else 1)