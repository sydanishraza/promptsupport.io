#!/usr/bin/env python3
"""
TICKET 2 Analysis Test - Analyze existing articles for TICKET 2 implementation
"""

import requests
import json
import re
from datetime import datetime

# Use local backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 TICKET 2 ANALYSIS TEST")
print(f"🌐 Backend URL: {BACKEND_URL}")
print("=" * 80)

class TICKET2Analyzer:
    def __init__(self):
        self.analysis_results = []
        
    def analyze_article_content(self, article_id, title, content):
        """Analyze a single article for TICKET 2 implementation"""
        print(f"\n📄 Analyzing: {title}")
        print(f"   ID: {article_id}")
        
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
        
        analysis = {
            'article_id': article_id,
            'title': title,
            'toc_links_count': len(toc_links),
            'heading_ids_count': len(heading_ids),
            'has_minitoc': has_minitoc,
            'coordination_rate': coordination_rate,
            'coordinated_links': len(coordinated_links),
            'broken_links': len(toc_links) - len(coordinated_links),
            'descriptive_toc_count': len(descriptive_toc),
            'descriptive_headings_count': len(descriptive_headings),
            'section_style_toc_count': len(section_style_toc),
            'section_style_headings_count': len(section_style_headings),
            'toc_links': toc_links[:5],  # First 5 for analysis
            'heading_ids': heading_ids[:5],  # First 5 for analysis
            'coordinated_links': coordinated_links[:5],
            'ticket2_score': 0
        }
        
        # Calculate TICKET 2 implementation score
        score_components = [
            has_minitoc,  # Has Mini-TOC
            coordination_rate >= 0.8,  # Good coordination
            len(descriptive_toc) / len(toc_links) >= 0.8 if toc_links else False,  # Descriptive TOC
            len(descriptive_headings) / len(heading_ids) >= 0.8 if heading_ids else False,  # Descriptive headings
            len(section_style_toc) == 0,  # No old section-style TOC
            len(section_style_headings) == 0  # No old section-style headings
        ]
        
        analysis['ticket2_score'] = sum(score_components) / len(score_components)
        
        print(f"   📊 TOC Links: {len(toc_links)}, Heading IDs: {len(heading_ids)}")
        print(f"   🔗 Coordination: {len(coordinated_links)}/{len(toc_links)} ({coordination_rate:.1%})")
        print(f"   📝 Descriptive format: TOC={len(descriptive_toc)}/{len(toc_links)}, Headings={len(descriptive_headings)}/{len(heading_ids)}")
        print(f"   ⚠️  Section-style format: TOC={len(section_style_toc)}, Headings={len(section_style_headings)}")
        print(f"   🎯 TICKET 2 Score: {analysis['ticket2_score']:.1%}")
        
        self.analysis_results.append(analysis)
        return analysis
    
    def analyze_content_library(self):
        """Analyze all articles in content library for TICKET 2 implementation"""
        print("🔍 Fetching content library...")
        
        try:
            response = requests.get(f"{API_BASE}/content-library", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                print(f"📚 Found {len(articles)} articles in content library")
                
                # Analyze first 10 articles for detailed analysis
                for i, article in enumerate(articles[:10]):
                    article_id = article.get('id', 'unknown')
                    title = article.get('title', 'Untitled')
                    content = article.get('content', '') or article.get('html', '')
                    
                    self.analyze_article_content(article_id, title, content)
                
                # Summary analysis
                self.print_summary_analysis()
                
            else:
                print(f"❌ Failed to fetch content library: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error analyzing content library: {str(e)}")
    
    def print_summary_analysis(self):
        """Print summary of TICKET 2 analysis"""
        print("\n" + "=" * 80)
        print("📊 TICKET 2 IMPLEMENTATION ANALYSIS SUMMARY")
        print("=" * 80)
        
        if not self.analysis_results:
            print("❌ No articles analyzed")
            return
        
        # Overall statistics
        total_articles = len(self.analysis_results)
        articles_with_toc = sum(1 for a in self.analysis_results if a['has_minitoc'])
        articles_with_good_coordination = sum(1 for a in self.analysis_results if a['coordination_rate'] >= 0.8)
        articles_with_descriptive_format = sum(1 for a in self.analysis_results if a['descriptive_toc_count'] > 0 and a['section_style_toc_count'] == 0)
        articles_fully_working = sum(1 for a in self.analysis_results if a['ticket2_score'] >= 0.8)
        
        avg_coordination = sum(a['coordination_rate'] for a in self.analysis_results) / total_articles
        avg_ticket2_score = sum(a['ticket2_score'] for a in self.analysis_results) / total_articles
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"   Total articles analyzed: {total_articles}")
        print(f"   Articles with Mini-TOC: {articles_with_toc}/{total_articles} ({articles_with_toc/total_articles:.1%})")
        print(f"   Articles with good coordination (≥80%): {articles_with_good_coordination}/{total_articles} ({articles_with_good_coordination/total_articles:.1%})")
        print(f"   Articles with descriptive format: {articles_with_descriptive_format}/{total_articles} ({articles_with_descriptive_format/total_articles:.1%})")
        print(f"   Articles fully working (≥80% TICKET 2 score): {articles_fully_working}/{total_articles} ({articles_fully_working/total_articles:.1%})")
        print(f"   Average coordination rate: {avg_coordination:.1%}")
        print(f"   Average TICKET 2 score: {avg_ticket2_score:.1%}")
        
        print(f"\n🎯 TICKET 2 IMPLEMENTATION STATUS:")
        if avg_ticket2_score >= 0.8:
            print("✅ TICKET 2 implementation is WORKING CORRECTLY!")
            print("   Stable anchor system with descriptive slugs is functional.")
            print("   Mini-TOC with clickable navigation is operational.")
            print("   ID coordination between TOC links and headings is successful.")
        elif avg_ticket2_score >= 0.6:
            print("⚠️  TICKET 2 implementation is PARTIALLY WORKING.")
            print("   Some components are functional but improvements needed.")
        else:
            print("❌ TICKET 2 implementation has SIGNIFICANT ISSUES.")
            print("   Major components are not working as expected.")
        
        # Detailed breakdown
        print(f"\n📋 DETAILED BREAKDOWN:")
        for result in self.analysis_results:
            status = "✅" if result['ticket2_score'] >= 0.8 else "⚠️" if result['ticket2_score'] >= 0.6 else "❌"
            print(f"{status} {result['title'][:50]}... | Score: {result['ticket2_score']:.1%} | Coord: {result['coordination_rate']:.1%}")
        
        # Identify issues
        print(f"\n🔍 IDENTIFIED ISSUES:")
        coordination_issues = [a for a in self.analysis_results if a['coordination_rate'] < 0.8]
        format_issues = [a for a in self.analysis_results if a['section_style_toc_count'] > 0 or a['section_style_headings_count'] > 0]
        
        if coordination_issues:
            print(f"   🔗 {len(coordination_issues)} articles have coordination issues (TOC links don't match heading IDs)")
        if format_issues:
            print(f"   📝 {len(format_issues)} articles still use old section-style format (section1, section2, etc.)")
        if not coordination_issues and not format_issues:
            print("   🎉 No major issues identified!")
        
        return avg_ticket2_score >= 0.6

if __name__ == "__main__":
    analyzer = TICKET2Analyzer()
    analyzer.analyze_content_library()