#!/usr/bin/env python3
"""
TOC Coordination Analysis
Analyze articles with toc-link class for ID coordination
"""

import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def analyze_toc_coordination():
    """Analyze TOC coordination in articles with toc-link class"""
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🔍 Analyzing TOC coordination in articles with toc-link class...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    print(f"📚 Found {len(articles)} articles in content library")
                    
                    # Filter articles with toc-link class
                    toc_articles = []
                    for article in articles:
                        content = article.get('content', article.get('html', ''))
                        if 'toc-link' in content:
                            toc_articles.append(article)
                    
                    print(f"🔗 Found {len(toc_articles)} articles with toc-link class")
                    
                    total_toc_links = 0
                    total_coordinated_links = 0
                    
                    for i, article in enumerate(toc_articles[:8]):  # Analyze first 8 TOC articles
                        content = article.get('content', article.get('html', ''))
                        title = article.get('title', 'Untitled')
                        
                        print(f"\n📄 Article {i+1}: {title[:60]}...")
                        
                        # Extract TOC links with toc-link class
                        toc_links = re.findall(r'<a[^>]*class="toc-link"[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                        
                        # Also check for any other anchor links
                        all_anchor_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                        
                        # Extract heading IDs
                        heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"', content)
                        
                        print(f"   🔗 TOC links (toc-link class): {len(toc_links)}")
                        print(f"   🔗 All anchor links: {len(all_anchor_links)}")
                        print(f"   🏷️  Heading IDs: {len(heading_ids)}")
                        
                        if heading_ids:
                            print(f"   📋 Heading IDs found: {heading_ids[:6]}")
                        
                        # Analyze coordination for toc-link class links
                        coordinated_toc = 0
                        for j, (target_id, link_text) in enumerate(toc_links[:5]):
                            total_toc_links += 1
                            if target_id in heading_ids:
                                total_coordinated_links += 1
                                coordinated_toc += 1
                                print(f"   ✅ TOC {j+1}: '{link_text[:30]}' -> #{target_id} (COORDINATED)")
                            else:
                                print(f"   ❌ TOC {j+1}: '{link_text[:30]}' -> #{target_id} (BROKEN)")
                        
                        # Count remaining TOC links
                        for target_id, _ in toc_links[5:]:
                            total_toc_links += 1
                            if target_id in heading_ids:
                                total_coordinated_links += 1
                                coordinated_toc += 1
                        
                        # Analyze all anchor links for comparison
                        coordinated_all = 0
                        for target_id, _ in all_anchor_links:
                            if target_id in heading_ids:
                                coordinated_all += 1
                        
                        toc_rate = (coordinated_toc / len(toc_links)) * 100 if toc_links else 0
                        all_rate = (coordinated_all / len(all_anchor_links)) * 100 if all_anchor_links else 0
                        
                        print(f"   📊 TOC coordination rate: {toc_rate:.1f}% ({coordinated_toc}/{len(toc_links)})")
                        print(f"   📊 All anchor coordination rate: {all_rate:.1f}% ({coordinated_all}/{len(all_anchor_links)})")
                        
                        # Check for section-style IDs
                        section_ids = [hid for hid in heading_ids if hid.startswith('section')]
                        if section_ids:
                            print(f"   🔢 Section-style IDs: {section_ids}")
                    
                    # Overall statistics
                    overall_rate = (total_coordinated_links / total_toc_links) * 100 if total_toc_links > 0 else 0
                    
                    print(f"\n{'='*80}")
                    print(f"📊 TOC COORDINATION ANALYSIS RESULTS")
                    print(f"{'='*80}")
                    print(f"Articles with TOC links: {len(toc_articles)}")
                    print(f"Articles analyzed: {min(8, len(toc_articles))}")
                    print(f"Total TOC links: {total_toc_links}")
                    print(f"Coordinated TOC links: {total_coordinated_links}")
                    print(f"Overall TOC coordination rate: {overall_rate:.1f}%")
                    
                    # Assessment
                    if overall_rate >= 90:
                        print(f"🎉 EXCELLENT - Target achieved! ({overall_rate:.1f}%)")
                        status = "TARGET_ACHIEVED"
                    elif overall_rate >= 70:
                        print(f"✅ GOOD - Significant improvement ({overall_rate:.1f}%)")
                        status = "SIGNIFICANT_IMPROVEMENT"
                    elif overall_rate >= 50:
                        print(f"⚠️ MODERATE - Some improvement ({overall_rate:.1f}%)")
                        status = "MODERATE_IMPROVEMENT"
                    elif overall_rate >= 20:
                        print(f"⚠️ LOW - Needs improvement ({overall_rate:.1f}%)")
                        status = "NEEDS_IMPROVEMENT"
                    else:
                        print(f"❌ CRITICAL - Major issues ({overall_rate:.1f}%)")
                        status = "CRITICAL_ISSUES"
                    
                    return overall_rate, status
                else:
                    print(f"❌ Failed to access content library - Status: {response.status}")
                    return 0, "ERROR"
                    
    except Exception as e:
        print(f"❌ Error analyzing TOC coordination: {e}")
        return 0, "ERROR"

if __name__ == "__main__":
    print("🚀 Starting TOC Coordination Analysis...")
    
    try:
        rate, status = asyncio.run(analyze_toc_coordination())
        print(f"\n🎯 Analysis completed")
        print(f"📊 Current TOC coordination rate: {rate:.1f}%")
        print(f"📈 Status: {status}")
        
        if status == "TARGET_ACHIEVED":
            print("🎉 The ID coordination fix has achieved the 90%+ target!")
        elif status in ["SIGNIFICANT_IMPROVEMENT", "MODERATE_IMPROVEMENT"]:
            print("✅ The ID coordination fix shows improvement but may need further refinement")
        else:
            print("❌ The ID coordination fix needs significant work to reach the target")
        
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")