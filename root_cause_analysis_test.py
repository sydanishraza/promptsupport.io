#!/usr/bin/env python3
"""
Root-Cause Analysis Test for Google Maps V2 Processing
Analyzing the specific fixes requested in the review
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime

# Configuration
BACKEND_URL = 'https://content-pipeline-5.preview.emergentagent.com'
API_BASE = f"{BACKEND_URL}/api"

def analyze_article_fixes(article):
    """Analyze article for the 4 specific root-cause fixes"""
    content = article.get('content', '')
    title = article.get('title', 'Unknown')
    
    print(f"\n🔍 ANALYZING: {title}")
    print(f"📅 Created: {article.get('created_at', 'Unknown')}")
    print(f"🔧 Engine: {article.get('engine', 'Unknown')}")
    
    # Fix 1: No H1 in content body (removed from line 7223)
    h1_elements = re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE | re.DOTALL)
    h1_count = len(h1_elements)
    
    print(f"\n1️⃣ H1 REMOVAL FIX:")
    if h1_count == 0:
        print(f"   ✅ SUCCESS: No H1 elements in content body")
        h1_fix = True
    else:
        print(f"   ❌ FAILED: Found {h1_count} H1 elements in content body")
        for i, h1 in enumerate(h1_elements):
            print(f"      H1 #{i+1}: {h1[:100]}...")
        h1_fix = False
    
    # Fix 2: Clickable Mini-TOC links with proper anchor format
    toc_anchor_links = re.findall(r'<a href="#([^"]+)"[^>]*>([^<]+)</a>', content)
    markdown_toc_links = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
    
    all_toc_links = toc_anchor_links + [(text, anchor) for text, anchor in markdown_toc_links]
    
    print(f"\n2️⃣ CLICKABLE MINI-TOC LINKS FIX:")
    if len(all_toc_links) >= 3:
        print(f"   ✅ SUCCESS: Found {len(all_toc_links)} clickable TOC links")
        for i, (anchor_or_text, text_or_anchor) in enumerate(all_toc_links[:3]):
            print(f"      Link #{i+1}: {anchor_or_text} -> #{text_or_anchor}")
        toc_fix = True
    else:
        print(f"   ❌ FAILED: Found only {len(all_toc_links)} TOC links (expected ≥3)")
        toc_fix = False
    
    # Fix 3: Proper list type detection (OL for procedural content)
    ol_lists = re.findall(r'<ol[^>]*>.*?</ol>', content, re.IGNORECASE | re.DOTALL)
    ul_lists = re.findall(r'<ul[^>]*>.*?</ul>', content, re.IGNORECASE | re.DOTALL)
    
    # Check for procedural indicators
    procedural_indicators = ['step', 'first', 'second', 'third', 'then', 'next', 'finally', 'go to', 'create', 'enable']
    has_procedural = any(indicator in content.lower() for indicator in procedural_indicators)
    
    print(f"\n3️⃣ LIST TYPE DETECTION FIX:")
    print(f"   📊 Found: {len(ol_lists)} OL lists, {len(ul_lists)} UL lists")
    print(f"   📝 Procedural content detected: {has_procedural}")
    
    if has_procedural and len(ol_lists) > 0:
        print(f"   ✅ SUCCESS: Found {len(ol_lists)} ordered lists for procedural content")
        list_fix = True
    elif not has_procedural:
        print(f"   ℹ️  NO PROCEDURAL CONTENT: List type detection not applicable")
        list_fix = True
    else:
        print(f"   ❌ FAILED: Procedural content found but no ordered lists")
        list_fix = False
    
    # Fix 4: Code block consolidation via new _consolidate_code_blocks method
    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', content, re.IGNORECASE | re.DOTALL)
    code_elements = re.findall(r'<code[^>]*>.*?</code>', content, re.IGNORECASE | re.DOTALL)
    
    total_code = len(code_blocks) + len(code_elements)
    
    print(f"\n4️⃣ CODE BLOCK CONSOLIDATION FIX:")
    print(f"   📊 Found: {len(code_blocks)} <pre> blocks, {len(code_elements)} <code> elements")
    
    if total_code > 0:
        # Check for consolidation (fewer, larger blocks vs many fragments)
        avg_length = sum(len(block) for block in code_blocks + code_elements) / total_code
        
        # Look for signs of consolidation
        consolidated_indicators = 0
        if len(code_blocks) > 0:  # Has proper code blocks
            consolidated_indicators += 1
        if avg_length > 100:  # Blocks are substantial
            consolidated_indicators += 1
        if total_code <= 10:  # Not too fragmented
            consolidated_indicators += 1
            
        if consolidated_indicators >= 2:
            print(f"   ✅ SUCCESS: Code blocks appear consolidated (avg length: {avg_length:.0f} chars)")
            code_fix = True
        else:
            print(f"   ⚠️  PARTIAL: Code blocks may be fragmented (avg length: {avg_length:.0f} chars)")
            code_fix = False
    else:
        print(f"   ℹ️  NO CODE BLOCKS: Consolidation not applicable")
        code_fix = True
    
    # Overall assessment
    fixes = [h1_fix, toc_fix, list_fix, code_fix]
    success_count = sum(fixes)
    success_rate = (success_count / len(fixes)) * 100
    
    print(f"\n📊 OVERALL ASSESSMENT:")
    print(f"   ✅ Fixes working: {success_count}/4 ({success_rate:.1f}%)")
    print(f"   🎯 H1 removal: {'✅' if h1_fix else '❌'}")
    print(f"   🔗 TOC links: {'✅' if toc_fix else '❌'}")
    print(f"   📝 List types: {'✅' if list_fix else '❌'}")
    print(f"   💻 Code consolidation: {'✅' if code_fix else '❌'}")
    
    return {
        'success_rate': success_rate,
        'h1_fix': h1_fix,
        'toc_fix': toc_fix,
        'list_fix': list_fix,
        'code_fix': code_fix,
        'fixes_working': success_count,
        'total_fixes': len(fixes)
    }

async def main():
    """Main analysis function"""
    print("🚀 ROOT-CAUSE ANALYSIS TEST FOR GOOGLE MAPS V2 PROCESSING")
    print("=" * 80)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get all articles
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    print(f"📚 Found {len(articles)} articles in content library")
                    
                    # Analyze each article
                    results = []
                    for i, article in enumerate(articles):
                        result = analyze_article_fixes(article)
                        result['article_title'] = article.get('title', f'Article {i+1}')
                        result['article_id'] = article.get('id', 'unknown')
                        result['engine'] = article.get('engine', 'unknown')
                        result['created_at'] = article.get('created_at', 'unknown')
                        results.append(result)
                    
                    # Summary analysis
                    print(f"\n{'='*80}")
                    print("📈 SUMMARY ANALYSIS")
                    print(f"{'='*80}")
                    
                    total_articles = len(results)
                    avg_success_rate = sum(r['success_rate'] for r in results) / total_articles if total_articles > 0 else 0
                    
                    h1_working = sum(1 for r in results if r['h1_fix'])
                    toc_working = sum(1 for r in results if r['toc_fix'])
                    list_working = sum(1 for r in results if r['list_fix'])
                    code_working = sum(1 for r in results if r['code_fix'])
                    
                    print(f"🎯 Overall Success Rate: {avg_success_rate:.1f}%")
                    print(f"📊 Fix Success Rates:")
                    print(f"   H1 Removal: {h1_working}/{total_articles} ({h1_working/total_articles*100:.1f}%)")
                    print(f"   TOC Links: {toc_working}/{total_articles} ({toc_working/total_articles*100:.1f}%)")
                    print(f"   List Types: {list_working}/{total_articles} ({list_working/total_articles*100:.1f}%)")
                    print(f"   Code Consolidation: {code_working}/{total_articles} ({code_working/total_articles*100:.1f}%)")
                    
                    # Identify best performing article
                    best_article = max(results, key=lambda x: x['success_rate'])
                    print(f"\n🏆 BEST PERFORMING ARTICLE:")
                    print(f"   Title: {best_article['article_title']}")
                    print(f"   Success Rate: {best_article['success_rate']:.1f}%")
                    print(f"   Engine: {best_article['engine']}")
                    
                    # Root-cause analysis conclusion
                    print(f"\n🔍 ROOT-CAUSE ANALYSIS CONCLUSION:")
                    if avg_success_rate >= 75:
                        print(f"   ✅ ROOT-CAUSE FIXES ARE WORKING ({avg_success_rate:.1f}% success)")
                        print(f"   🎉 The V2 processing pipeline successfully implements the fixes")
                    elif avg_success_rate >= 50:
                        print(f"   ⚠️  ROOT-CAUSE FIXES PARTIALLY WORKING ({avg_success_rate:.1f}% success)")
                        print(f"   🔧 Some fixes are implemented but improvements needed")
                    else:
                        print(f"   ❌ ROOT-CAUSE FIXES NOT WORKING ({avg_success_rate:.1f}% success)")
                        print(f"   🚨 Significant issues remain with the V2 processing pipeline")
                    
                    return avg_success_rate >= 50
                    
                else:
                    print(f"❌ Failed to access content library: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error in root-cause analysis: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)