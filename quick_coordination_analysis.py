#!/usr/bin/env python3
"""
Quick ID Coordination Analysis
Analyze the current state of ID coordination in existing articles
"""

import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def analyze_current_coordination():
    """Analyze current ID coordination state"""
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🔍 Analyzing current ID coordination state...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    print(f"📚 Found {len(articles)} articles in content library")
                    
                    total_toc_links = 0
                    total_coordinated_links = 0
                    articles_with_toc = 0
                    
                    for i, article in enumerate(articles[:10]):
                        content = article.get('content', article.get('html', ''))
                        title = article.get('title', 'Untitled')
                        
                        if not content:
                            continue
                            
                        # Extract TOC links
                        toc_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', content)
                        
                        if not toc_links:
                            continue
                            
                        articles_with_toc += 1
                        
                        # Extract heading IDs
                        heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"', content)
                        
                        print(f"\n📄 Article {i+1}: {title[:50]}...")
                        print(f"   TOC Links: {len(toc_links)}")
                        print(f"   Heading IDs: {len(heading_ids)}")
                        
                        # Show first few TOC links and their targets
                        coordinated_in_article = 0
                        for j, (target_id, link_text) in enumerate(toc_links[:5]):
                            total_toc_links += 1
                            if target_id in heading_ids:
                                total_coordinated_links += 1
                                coordinated_in_article += 1
                                print(f"   ✅ TOC {j+1}: '{link_text}' -> #{target_id} (COORDINATED)")
                            else:
                                print(f"   ❌ TOC {j+1}: '{link_text}' -> #{target_id} (BROKEN)")
                        
                        if len(toc_links) > 5:
                            # Count remaining links
                            for target_id, _ in toc_links[5:]:
                                total_toc_links += 1
                                if target_id in heading_ids:
                                    total_coordinated_links += 1
                                    coordinated_in_article += 1
                        
                        article_rate = (coordinated_in_article / len(toc_links)) * 100 if toc_links else 0
                        print(f"   📊 Article coordination rate: {article_rate:.1f}% ({coordinated_in_article}/{len(toc_links)})")
                        
                        # Show heading IDs
                        if heading_ids:
                            print(f"   🏷️  Heading IDs: {heading_ids[:8]}")
                    
                    # Overall statistics
                    overall_rate = (total_coordinated_links / total_toc_links) * 100 if total_toc_links > 0 else 0
                    
                    print(f"\n{'='*80}")
                    print(f"📊 OVERALL ID COORDINATION ANALYSIS")
                    print(f"{'='*80}")
                    print(f"Articles analyzed: {len(articles[:10])}")
                    print(f"Articles with TOC: {articles_with_toc}")
                    print(f"Total TOC links: {total_toc_links}")
                    print(f"Coordinated links: {total_coordinated_links}")
                    print(f"Overall coordination rate: {overall_rate:.1f}%")
                    
                    if overall_rate >= 90:
                        print(f"🎉 EXCELLENT - Target achieved ({overall_rate:.1f}%)")
                    elif overall_rate >= 70:
                        print(f"✅ GOOD - Significant improvement ({overall_rate:.1f}%)")
                    elif overall_rate >= 50:
                        print(f"⚠️ MODERATE - Some improvement ({overall_rate:.1f}%)")
                    elif overall_rate >= 20:
                        print(f"⚠️ LOW - Needs improvement ({overall_rate:.1f}%)")
                    else:
                        print(f"❌ CRITICAL - Major issues ({overall_rate:.1f}%)")
                    
                    return overall_rate
                else:
                    print(f"❌ Failed to access content library - Status: {response.status}")
                    return 0
                    
    except Exception as e:
        print(f"❌ Error analyzing coordination: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 Starting Quick ID Coordination Analysis...")
    
    try:
        rate = asyncio.run(analyze_current_coordination())
        print(f"\n🎯 Analysis completed - Current coordination rate: {rate:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")