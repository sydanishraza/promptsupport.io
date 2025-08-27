#!/usr/bin/env python3
"""
TICKET 2 Specific Article Test - Check specific articles for TICKET 2 implementation
"""

import requests
import json
import re
from datetime import datetime

# Use local backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 TICKET 2 SPECIFIC ARTICLE TEST")
print(f"🌐 Backend URL: {BACKEND_URL}")
print("=" * 80)

def analyze_specific_article(article_id, title):
    """Analyze a specific article for TICKET 2 implementation"""
    print(f"\n📄 Analyzing: {title}")
    print(f"   ID: {article_id}")
    
    try:
        # Get content library to find the article
        response = requests.get(f"{API_BASE}/content-library", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Find the specific article
            target_article = None
            for article in articles:
                if article.get('id') == article_id:
                    target_article = article
                    break
            
            if not target_article:
                print(f"   ❌ Article not found")
                return False
            
            # Get content from different possible fields
            content = (target_article.get('content') or 
                      target_article.get('html') or 
                      target_article.get('markdown') or '')
            
            if not content:
                print(f"   ❌ No content found")
                return False
            
            print(f"   📝 Content length: {len(content)} characters")
            
            # Show first part of content for debugging
            print(f"   📋 Content preview: {content[:200]}...")
            
            # Extract TOC links
            toc_links = re.findall(r'class="toc-link"[^>]*href="#([^"]+)"', content)
            
            # Extract heading IDs
            heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', content)
            
            # Check for Mini-TOC structure
            has_minitoc = 'toc-link' in content
            
            # Check ID format (descriptive vs section-style)
            descriptive_toc = [link for link in toc_links if not re.match(r'^section\d+$', link)]
            descriptive_headings = [hid for hid in heading_ids if not re.match(r'^section\d+$', hid)]
            
            # Check coordination
            coordinated_links = [link for link in toc_links if link in heading_ids]
            coordination_rate = len(coordinated_links) / len(toc_links) if toc_links else 0
            
            # Check for old section-style IDs
            section_style_toc = [link for link in toc_links if re.match(r'^section\d+$', link)]
            section_style_headings = [hid for hid in heading_ids if re.match(r'^section\d+$', hid)]
            
            print(f"   📊 TOC Links: {len(toc_links)}")
            if toc_links:
                print(f"      TOC Links: {toc_links}")
            
            print(f"   📊 Heading IDs: {len(heading_ids)}")
            if heading_ids:
                print(f"      Heading IDs: {heading_ids}")
            
            print(f"   🔗 Coordination: {len(coordinated_links)}/{len(toc_links)} ({coordination_rate:.1%})")
            print(f"   📝 Descriptive format: TOC={len(descriptive_toc)}/{len(toc_links)}, Headings={len(descriptive_headings)}/{len(heading_ids)}")
            print(f"   ⚠️  Section-style format: TOC={len(section_style_toc)}, Headings={len(section_style_headings)}")
            
            # Calculate TICKET 2 implementation score
            score_components = [
                has_minitoc,  # Has Mini-TOC
                coordination_rate >= 0.8,  # Good coordination
                len(descriptive_toc) / len(toc_links) >= 0.8 if toc_links else False,  # Descriptive TOC
                len(descriptive_headings) / len(heading_ids) >= 0.8 if heading_ids else False,  # Descriptive headings
                len(section_style_toc) == 0,  # No old section-style TOC
                len(section_style_headings) == 0  # No old section-style headings
            ]
            
            ticket2_score = sum(score_components) / len(score_components)
            print(f"   🎯 TICKET 2 Score: {ticket2_score:.1%}")
            
            # Detailed analysis
            if coordinated_links:
                print(f"   ✅ Coordinated links: {coordinated_links}")
            
            broken_links = [link for link in toc_links if link not in heading_ids]
            if broken_links:
                print(f"   ❌ Broken links: {broken_links}")
            
            return ticket2_score >= 0.6
            
        else:
            print(f"   ❌ Failed to fetch content library: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error analyzing article: {str(e)}")
        return False

def main():
    """Test specific articles known to have TICKET 2 implementation"""
    
    # Articles to test based on what we saw in the content library
    test_articles = [
        ("f68790f0-0d85-4149-b6a1-f40c098f91e3", "Using Google Map Javascript API"),
        ("4cab81d4-26ed-4e3b-881d-17cc02b39462", "Introduction to Products"),
        ("4363f921-8e19-4889-acb7-13f13e6d58b3", "Introduction to Salesforce Products")
    ]
    
    results = []
    
    for article_id, title in test_articles:
        result = analyze_specific_article(article_id, title)
        results.append((title, result))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TICKET 2 SPECIFIC ARTICLE TEST SUMMARY")
    print("=" * 80)
    
    working_articles = sum(1 for _, result in results if result)
    total_articles = len(results)
    
    print(f"📈 RESULTS:")
    for title, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {title}")
    
    print(f"\n📊 OVERALL: {working_articles}/{total_articles} articles working ({working_articles/total_articles:.1%})")
    
    if working_articles >= total_articles * 0.8:
        print("✅ TICKET 2 implementation is WORKING CORRECTLY!")
    elif working_articles >= total_articles * 0.6:
        print("⚠️  TICKET 2 implementation is PARTIALLY WORKING.")
    else:
        print("❌ TICKET 2 implementation has SIGNIFICANT ISSUES.")

if __name__ == "__main__":
    main()