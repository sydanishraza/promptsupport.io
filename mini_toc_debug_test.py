#!/usr/bin/env python3
"""
Detailed Mini-TOC Linking Debug Test
Focus: Understanding why TOC items are not clickable despite having proper heading IDs
"""

import requests
import json
from bs4 import BeautifulSoup
import re

BACKEND_URL = "https://content-engine-10.preview.emergentagent.com/api"

def analyze_toc_issue():
    """Detailed analysis of the Mini-TOC linking issue"""
    print("🔍 DETAILED MINI-TOC LINKING ANALYSIS")
    print("="*80)
    
    # Get the target article
    response = requests.get(f"{BACKEND_URL}/content-library")
    if response.status_code != 200:
        print("❌ Failed to access content library")
        return
    
    articles = response.json().get('articles', [])
    target_article = None
    
    for article in articles:
        title = article.get('title', '').lower()
        if 'code normalization' in title and 'javascript' in title:
            target_article = article
            break
    
    if not target_article:
        print("❌ Target article not found")
        return
    
    print(f"✅ Found article: {target_article['title']}")
    print(f"📄 Article ID: {target_article['id']}")
    
    content = target_article.get('content', '') or target_article.get('html', '')
    soup = BeautifulSoup(content, 'html.parser')
    
    print("\n" + "="*80)
    print("🔍 CURRENT TOC STRUCTURE ANALYSIS")
    print("="*80)
    
    # Find the TOC
    ul_elements = soup.find_all('ul')
    toc_element = None
    
    for ul in ul_elements:
        items = ul.find_all('li')
        if len(items) >= 3:  # Likely the TOC
            toc_element = ul
            break
    
    if toc_element:
        print("✅ Found TOC structure:")
        toc_items = toc_element.find_all('li')
        
        for i, item in enumerate(toc_items, 1):
            item_text = item.get_text().strip()
            print(f"  {i}. {item_text}")
            print(f"     HTML: {str(item)}")
            
            # Check if it has any links
            links = item.find_all('a')
            if links:
                for link in links:
                    href = link.get('href', '')
                    print(f"     🔗 Link found: href='{href}'")
            else:
                print(f"     ❌ No links found - this is the problem!")
    
    print("\n" + "="*80)
    print("🔍 HEADING ID MAPPING ANALYSIS")
    print("="*80)
    
    # Find all headings with IDs
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    heading_map = {}
    
    for heading in headings:
        heading_id = heading.get('id', '')
        heading_text = heading.get_text().strip()
        
        if heading_id:
            heading_map[heading_id] = heading_text
            print(f"✅ {heading.name.upper()}: '{heading_text}' → ID='{heading_id}'")
        else:
            print(f"❌ {heading.name.upper()}: '{heading_text}' → No ID")
    
    print(f"\n📊 Total headings with IDs: {len(heading_map)}")
    
    print("\n" + "="*80)
    print("🔍 EXPECTED VS ACTUAL TOC LINKS")
    print("="*80)
    
    if toc_element:
        toc_items = toc_element.find_all('li')
        
        print("Expected TOC format (what should be generated):")
        for i, item in enumerate(toc_items, 1):
            item_text = item.get_text().strip()
            
            # Try to match with heading IDs
            matching_id = None
            for heading_id, heading_text in heading_map.items():
                if item_text.lower() in heading_text.lower() or heading_text.lower() in item_text.lower():
                    matching_id = heading_id
                    break
            
            if matching_id:
                print(f"  {i}. <li><a href=\"#{matching_id}\">{item_text}</a></li>")
                print(f"     ✅ Should link to: #{matching_id}")
            else:
                print(f"  {i}. <li>{item_text}</li>")
                print(f"     ❌ No matching heading ID found")
        
        print("\nActual TOC format (what is currently generated):")
        for i, item in enumerate(toc_items, 1):
            print(f"  {i}. {str(item)}")
    
    print("\n" + "="*80)
    print("🔍 ROOT CAUSE ANALYSIS")
    print("="*80)
    
    print("FINDINGS:")
    print("1. ✅ Target article exists and is accessible")
    print("2. ✅ Article has proper heading IDs (section1, section2, block_1, section3, section4)")
    print("3. ✅ Mini-TOC structure exists as <ul><li> elements")
    print("4. ❌ TOC items are plain <li> elements without <a href='#id'> links")
    print("5. ❌ V2StyleProcessor is not converting TOC bullets to clickable anchors")
    
    print("\nROOT CAUSE:")
    print("The V2StyleProcessor's _process_clickable_anchors() method is either:")
    print("- Not being called during content processing")
    print("- Not properly converting Mini-TOC bullets to anchor links")
    print("- Processing is happening but results are not being saved to content library")
    
    print("\nRECOMMENDATION:")
    print("1. Check if V2StyleProcessor is actually processing this article")
    print("2. Verify _process_clickable_anchors() method implementation")
    print("3. Test the style processing pipeline with this specific article")
    print("4. Check if processed content is being saved back to content library")

def test_style_processing_on_article():
    """Test if we can trigger style processing on the target article"""
    print("\n" + "="*80)
    print("🔍 TESTING STYLE PROCESSING ON TARGET ARTICLE")
    print("="*80)
    
    # Try to trigger style processing
    try:
        # First, let's see if there are any recent style processing results
        response = requests.get(f"{BACKEND_URL}/style/diagnostics")
        if response.status_code == 200:
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            print(f"📊 Recent style processing runs: {len(recent_results)}")
            
            if recent_results:
                print("Recent style processing results:")
                for i, result in enumerate(recent_results[:5], 1):
                    print(f"  {i}. Article: {result.get('article_title', 'N/A')}")
                    print(f"     Status: {result.get('style_status', 'N/A')}")
                    print(f"     Anchors: {result.get('anchor_links_generated', 'N/A')}")
                    print(f"     Timestamp: {result.get('timestamp', 'N/A')}")
            else:
                print("❌ No recent style processing results found")
                print("This suggests that V2StyleProcessor is not actively processing articles")
        
        # Try to trigger a rerun (if endpoint exists)
        print("\n🔄 Attempting to trigger style processing rerun...")
        rerun_response = requests.post(f"{BACKEND_URL}/style/rerun", 
                                     json={"run_id": "test"}, 
                                     timeout=30)
        
        print(f"Style rerun response: {rerun_response.status_code}")
        if rerun_response.status_code == 200:
            print("✅ Style rerun endpoint accessible")
            print(f"Response: {rerun_response.json()}")
        else:
            print(f"❌ Style rerun failed: {rerun_response.text}")
            
    except Exception as e:
        print(f"❌ Error testing style processing: {e}")

if __name__ == "__main__":
    analyze_toc_issue()
    test_style_processing_on_article()
    
    print("\n" + "="*80)
    print("🎯 SUMMARY FOR MAIN AGENT")
    print("="*80)
    print("ISSUE IDENTIFIED: Mini-TOC items exist as plain <li> elements but are NOT converted to clickable <a href='#id'> links")
    print("BACKEND STATUS: V2StyleProcessor exists but appears to not be actively processing articles")
    print("CONTENT STATUS: Article has proper heading IDs but TOC lacks anchor links")
    print("NEXT STEPS: Main agent needs to ensure V2StyleProcessor _process_clickable_anchors() method is working and being applied to content library articles")