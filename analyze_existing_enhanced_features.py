#!/usr/bin/env python3
"""
Analyze Existing Articles for Enhanced Features
Tests the ensure_enhanced_features() function by analyzing existing Content Library articles
"""

import requests
import json
import re
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://woolf-style-lint.preview.emergentagent.com') + '/api'

class ExistingEnhancedFeaturesAnalyzer:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {
            "mini_toc_present": {"passed": 0, "total": 0, "percentage": 0, "details": []},
            "enhanced_code_blocks": {"passed": 0, "total": 0, "percentage": 0, "details": []},
            "callouts_present": {"passed": 0, "total": 0, "percentage": 0, "details": []},
            "enhanced_list_classes": {"passed": 0, "total": 0, "percentage": 0, "details": []},
            "cross_references": {"passed": 0, "total": 0, "percentage": 0, "details": []},
            "anchor_ids_on_headings": {"passed": 0, "total": 0, "percentage": 0, "details": []}
        }
        print(f"🔍 ANALYZING EXISTING ARTICLES FOR ENHANCED FEATURES at: {self.base_url}")
        
    def get_content_library_articles(self):
        """Get all articles from Content Library"""
        try:
            response = requests.get(f"{self.base_url}/content-library")
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                print(f"📚 Retrieved {len(articles)} articles from Content Library")
                return articles
            else:
                print(f"❌ Failed to retrieve Content Library: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error retrieving articles: {e}")
            return []
    
    def analyze_mini_toc(self, content: str, title: str) -> bool:
        """Test 1: Mini-TOC present at start"""
        self.test_results["mini_toc_present"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for mini-toc class
        mini_toc = soup.find('div', class_='mini-toc')
        
        # Look for TOC-like structures at the beginning
        first_1000_chars = content[:1000].lower()
        toc_indicators = [
            'contents', 'table of contents', 'mini-toc', 'toc-list',
            '📋 contents', '📋 table of contents', '📋'
        ]
        
        has_toc_indicators = any(indicator in first_1000_chars for indicator in toc_indicators)
        
        # Look for anchor links in lists (TOC navigation)
        anchor_links = soup.find_all('a', href=re.compile(r'^#'))
        
        # Check for list with navigation structure
        toc_lists = soup.find_all('ul', class_=re.compile(r'toc'))
        
        passed = bool(mini_toc or (has_toc_indicators and len(anchor_links) > 0) or toc_lists)
        
        if passed:
            self.test_results["mini_toc_present"]["passed"] += 1
            
        detail = {
            "title": title[:50] + "..." if len(title) > 50 else title,
            "passed": passed,
            "mini_toc_div": bool(mini_toc),
            "toc_indicators": has_toc_indicators,
            "anchor_links": len(anchor_links),
            "toc_lists": len(toc_lists)
        }
        self.test_results["mini_toc_present"]["details"].append(detail)
        
        return passed
    
    def analyze_enhanced_code_blocks(self, content: str, title: str) -> bool:
        """Test 2: Enhanced Code Blocks with copy buttons"""
        self.test_results["enhanced_code_blocks"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for enhanced code block containers
        code_containers = soup.find_all('div', class_='code-block-container')
        copy_buttons = soup.find_all('button', class_='copy-code-btn')
        code_headers = soup.find_all('div', class_='code-header')
        
        # Count total code blocks
        all_code_blocks = soup.find_all('pre')
        total_code_blocks = len(all_code_blocks)
        enhanced_code_blocks = len(code_containers)
        
        # If there are code blocks, they should be enhanced
        if total_code_blocks > 0:
            passed = enhanced_code_blocks > 0 and len(copy_buttons) > 0
        else:
            passed = True  # No code blocks to enhance
            
        if passed:
            self.test_results["enhanced_code_blocks"]["passed"] += 1
            
        detail = {
            "title": title[:50] + "..." if len(title) > 50 else title,
            "passed": passed,
            "total_code_blocks": total_code_blocks,
            "enhanced_containers": enhanced_code_blocks,
            "copy_buttons": len(copy_buttons),
            "code_headers": len(code_headers)
        }
        self.test_results["enhanced_code_blocks"]["details"].append(detail)
        
        return passed
    
    def analyze_callouts(self, content: str, title: str) -> bool:
        """Test 3: Callouts present"""
        self.test_results["callouts_present"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for callout elements
        callouts = soup.find_all('div', class_=re.compile(r'callout'))
        callout_tips = soup.find_all('div', class_='callout-tip')
        callout_titles = soup.find_all('div', class_='callout-title')
        callout_content = soup.find_all('div', class_='callout-content')
        
        # Look for callout-like visual indicators
        callout_emojis = re.findall(r'(💡|⚠️|📝|🔥|⭐|🎯|📋)', content)
        
        passed = len(callouts) > 0 or len(callout_emojis) > 2
        
        if passed:
            self.test_results["callouts_present"]["passed"] += 1
            
        detail = {
            "title": title[:50] + "..." if len(title) > 50 else title,
            "passed": passed,
            "callout_divs": len(callouts),
            "callout_tips": len(callout_tips),
            "callout_titles": len(callout_titles),
            "visual_indicators": len(callout_emojis)
        }
        self.test_results["callouts_present"]["details"].append(detail)
        
        return passed
    
    def analyze_enhanced_list_classes(self, content: str, title: str) -> bool:
        """Test 4: Enhanced List Classes"""
        self.test_results["enhanced_list_classes"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all lists
        ordered_lists = soup.find_all('ol')
        unordered_lists = soup.find_all('ul')
        total_lists = len(ordered_lists) + len(unordered_lists)
        
        # Find lists with enhanced classes
        doc_list_ordered = soup.find_all('ol', class_=re.compile(r'doc-list.*ordered'))
        doc_list_unordered = soup.find_all('ul', class_=re.compile(r'doc-list.*unordered'))
        doc_list_any = soup.find_all(['ol', 'ul'], class_=re.compile(r'doc-list'))
        
        enhanced_lists = len(doc_list_any)
        
        if total_lists > 0:
            enhancement_ratio = enhanced_lists / total_lists
            passed = enhancement_ratio >= 0.5  # At least 50% of lists should have enhanced classes
        else:
            passed = True  # No lists to enhance
            enhancement_ratio = 1.0
            
        if passed:
            self.test_results["enhanced_list_classes"]["passed"] += 1
            
        detail = {
            "title": title[:50] + "..." if len(title) > 50 else title,
            "passed": passed,
            "total_lists": total_lists,
            "enhanced_lists": enhanced_lists,
            "enhancement_ratio": enhancement_ratio,
            "doc_list_ordered": len(doc_list_ordered),
            "doc_list_unordered": len(doc_list_unordered)
        }
        self.test_results["enhanced_list_classes"]["details"].append(detail)
        
        return passed
    
    def analyze_cross_references(self, content: str, title: str) -> bool:
        """Test 5: Cross-References"""
        self.test_results["cross_references"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for cross-reference elements
        cross_ref_links = soup.find_all('a', class_='cross-ref')
        see_also_sections = soup.find_all(class_='see-also')
        
        # Look for cross-reference patterns in text
        cross_ref_patterns = re.findall(r'(see also|refer to|check out|learn more|cross-ref)', content.lower())
        
        # Look for anchor links (internal navigation)
        anchor_links = soup.find_all('a', href=re.compile(r'^#'))
        
        # Look for related links sections
        related_links = soup.find_all(class_='related-links')
        
        passed = (len(cross_ref_links) > 0 or len(see_also_sections) > 0 or 
                 len(cross_ref_patterns) > 0 or len(anchor_links) > 0 or len(related_links) > 0)
        
        if passed:
            self.test_results["cross_references"]["passed"] += 1
            
        detail = {
            "title": title[:50] + "..." if len(title) > 50 else title,
            "passed": passed,
            "cross_ref_links": len(cross_ref_links),
            "see_also_sections": len(see_also_sections),
            "cross_ref_patterns": len(cross_ref_patterns),
            "anchor_links": len(anchor_links),
            "related_links": len(related_links)
        }
        self.test_results["cross_references"]["details"].append(detail)
        
        return passed
    
    def analyze_anchor_ids_on_headings(self, content: str, title: str) -> bool:
        """Test 6: Anchor IDs on headings"""
        self.test_results["anchor_ids_on_headings"]["total"] += 1
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all H2 headings
        h2_headings = soup.find_all('h2')
        h2_with_ids = soup.find_all('h2', id=True)
        
        # Also check H3 headings
        h3_headings = soup.find_all('h3')
        h3_with_ids = soup.find_all('h3', id=True)
        
        total_headings = len(h2_headings) + len(h3_headings)
        headings_with_ids = len(h2_with_ids) + len(h3_with_ids)
        
        if total_headings > 0:
            id_ratio = headings_with_ids / total_headings
            passed = id_ratio >= 0.3  # At least 30% of headings should have IDs
        else:
            passed = True  # No headings to enhance
            id_ratio = 1.0
            
        if passed:
            self.test_results["anchor_ids_on_headings"]["passed"] += 1
            
        # Sample some IDs
        sample_ids = [h.get('id') for h in h2_with_ids[:2] if h.get('id')]
        
        detail = {
            "title": title[:50] + "..." if len(title) > 50 else title,
            "passed": passed,
            "total_h2_headings": len(h2_headings),
            "h2_with_ids": len(h2_with_ids),
            "total_h3_headings": len(h3_headings),
            "h3_with_ids": len(h3_with_ids),
            "id_ratio": id_ratio,
            "sample_ids": sample_ids
        }
        self.test_results["anchor_ids_on_headings"]["details"].append(detail)
        
        return passed
    
    def analyze_article(self, article):
        """Analyze a single article for all enhanced features"""
        title = article.get('title', 'Untitled')
        content = article.get('content', '')
        
        if not content or len(content) < 100:
            return  # Skip articles with no content
        
        print(f"\n🔍 Analyzing: {title[:60]}{'...' if len(title) > 60 else ''}")
        print(f"   Content length: {len(content)} characters")
        
        # Run all tests
        self.analyze_mini_toc(content, title)
        self.analyze_enhanced_code_blocks(content, title)
        self.analyze_callouts(content, title)
        self.analyze_enhanced_list_classes(content, title)
        self.analyze_cross_references(content, title)
        self.analyze_anchor_ids_on_headings(content, title)
    
    def run_analysis(self):
        """Run comprehensive analysis of existing articles"""
        print("🔥 STARTING ENHANCED FEATURES ANALYSIS OF EXISTING ARTICLES")
        print("=" * 80)
        print("Analyzing Content Library articles for ensure_enhanced_features() compliance")
        print("=" * 80)
        
        # Get articles from Content Library
        articles = self.get_content_library_articles()
        
        if not articles:
            print("❌ No articles found to analyze")
            return
        
        # Analyze a sample of articles (limit to 10 for performance)
        sample_articles = articles[:10]
        print(f"📊 Analyzing {len(sample_articles)} sample articles...")
        
        for article in sample_articles:
            self.analyze_article(article)
        
        # Generate report
        self.generate_detailed_report()
    
    def generate_detailed_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "=" * 80)
        print("🎯 ENHANCED FEATURES ANALYSIS RESULTS")
        print("=" * 80)
        
        # Calculate percentages
        for feature_name, results in self.test_results.items():
            if results["total"] > 0:
                results["percentage"] = (results["passed"] / results["total"]) * 100
            else:
                results["percentage"] = 0
        
        # Display summary results
        print("\n📊 SUMMARY RESULTS:")
        
        overall_passed = 0
        overall_total = 0
        
        for feature_name, results in self.test_results.items():
            passed = results["passed"]
            total = results["total"]
            percentage = results["percentage"]
            
            overall_passed += passed
            overall_total += total
            
            status_icon = "✅" if percentage >= 90 else "⚠️" if percentage >= 70 else "❌"
            feature_display = feature_name.replace('_', ' ').title()
            
            print(f"{status_icon} {feature_display}: {passed}/{total} ({percentage:.1f}%)")
        
        overall_percentage = (overall_passed / max(1, overall_total)) * 100
        
        print(f"\n🏆 OVERALL ENHANCED FEATURES COMPLIANCE")
        print(f"   Tests Passed: {overall_passed}/{overall_total}")
        print(f"   Success Rate: {overall_percentage:.1f}%")
        
        # Show detailed results for each feature
        print("\n📋 DETAILED FEATURE ANALYSIS:")
        
        for feature_name, results in self.test_results.items():
            feature_display = feature_name.replace('_', ' ').title()
            print(f"\n🔍 {feature_display} ({results['passed']}/{results['total']} - {results['percentage']:.1f}%)")
            
            # Show some examples
            passed_examples = [d for d in results['details'] if d['passed']]
            failed_examples = [d for d in results['details'] if not d['passed']]
            
            if passed_examples:
                print(f"   ✅ Working examples:")
                for example in passed_examples[:3]:
                    print(f"      - {example['title']}")
            
            if failed_examples:
                print(f"   ❌ Failed examples:")
                for example in failed_examples[:3]:
                    print(f"      - {example['title']}")
        
        # Determine final status
        if overall_percentage >= 95:
            status = "✅ EXCELLENT - Enhanced features working at near 100% compliance!"
            recommendation = "The ensure_enhanced_features() function is working excellently."
        elif overall_percentage >= 85:
            status = "✅ VERY GOOD - Enhanced features working very well"
            recommendation = "Minor improvements could achieve perfect compliance."
        elif overall_percentage >= 70:
            status = "⚠️ GOOD - Most enhanced features working"
            recommendation = "Some enhanced features need attention for better compliance."
        elif overall_percentage >= 50:
            status = "⚠️ PARTIAL - Enhanced features partially working"
            recommendation = "Significant improvements needed in ensure_enhanced_features() function."
        else:
            status = "❌ CRITICAL - Enhanced features not working properly"
            recommendation = "Major fixes required in ensure_enhanced_features() implementation."
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        print(f"   Status: {status}")
        print(f"   Recommendation: {recommendation}")
        
        print("\n" + "=" * 80)
        print("🔍 ENHANCED FEATURES ANALYSIS COMPLETE")
        print("=" * 80)
        
        return overall_percentage

def main():
    """Main analysis execution"""
    analyzer = ExistingEnhancedFeaturesAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()