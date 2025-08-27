#!/usr/bin/env python3
"""
WYSIWYG TEMPLATE INTEGRATION ANALYSIS
Analyze existing articles for WYSIWYG template integration features
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def analyze_wysiwyg_features():
    """Analyze existing articles for WYSIWYG template integration features"""
    try:
        log_test_result("🎯 ANALYZING EXISTING ARTICLES FOR WYSIWYG FEATURES", "CRITICAL")
        
        # Get articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=60)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📚 Found {total_articles} total articles, analyzing {len(articles)} articles...")
        
        if not articles:
            log_test_result("❌ No articles found for analysis", "ERROR")
            return False
        
        # WYSIWYG features to analyze
        wysiwyg_features = {
            'article_body_wrapper': 0,
            'enhanced_code_blocks': 0,
            'line_numbers_code': 0,
            'expandable_sections': 0,
            'contextual_callouts': 0,
            'copy_functionality': 0,
            'heading_ids': 0,
            'mini_toc_structure': 0,
            'interactive_elements': 0
        }
        
        # Template contamination patterns
        contamination_patterns = [
            r'what are the main benefits',
            r'getting started guide.*generic',
            r'this is an overview of',
            r'main content from',
            r'related links:.*#article-',
            r'frequently asked questions.*generic',
            r'placeholder.*content',
            r'template.*example',
            r'sample.*text.*here',
            r'lorem ipsum',
            r'#what-is-.*-studio',
            r'#getting-started',
            r'#create-an-account'
        ]
        
        clean_articles = 0
        contaminated_articles = 0
        articles_with_wysiwyg = 0
        
        for i, article in enumerate(articles):
            article_title = article.get('title', 'Untitled')
            article_content = article.get('content', '')
            
            log_test_result(f"📄 Article {i+1}: {article_title[:60]}...")
            log_test_result(f"   Content length: {len(article_content)} characters")
            
            # Check for template contamination
            contamination_count = 0
            found_patterns = []
            
            for pattern in contamination_patterns:
                matches = re.findall(pattern, article_content.lower())
                if matches:
                    contamination_count += len(matches)
                    found_patterns.append(pattern)
            
            if contamination_count > 0:
                log_test_result(f"   ❌ CONTAMINATION: {contamination_count} instances found", "WARNING")
                contaminated_articles += 1
                for pattern in found_patterns[:3]:  # Show first 3 patterns
                    log_test_result(f"      Pattern: {pattern}", "WARNING")
            else:
                log_test_result(f"   ✅ CLEAN: No template contamination", "SUCCESS")
                clean_articles += 1
            
            # Parse HTML content for WYSIWYG features
            if article_content:
                soup = BeautifulSoup(article_content, 'html.parser')
                article_wysiwyg_count = 0
                
                # Check for article-body wrapper
                if soup.find('div', class_='article-body'):
                    wysiwyg_features['article_body_wrapper'] += 1
                    article_wysiwyg_count += 1
                    log_test_result(f"   ✅ Found article-body wrapper", "SUCCESS")
                
                # Check for enhanced code blocks with line numbers
                code_blocks_with_line_numbers = soup.find_all('pre', class_='line-numbers')
                if code_blocks_with_line_numbers:
                    wysiwyg_features['enhanced_code_blocks'] += len(code_blocks_with_line_numbers)
                    wysiwyg_features['line_numbers_code'] += len(code_blocks_with_line_numbers)
                    article_wysiwyg_count += len(code_blocks_with_line_numbers)
                    log_test_result(f"   ✅ Found {len(code_blocks_with_line_numbers)} enhanced code blocks with line numbers", "SUCCESS")
                
                # Check for expandable sections
                expandable_sections = soup.find_all(['div', 'section'], class_=re.compile(r'expandable|collapsible|faq-item|accordion'))
                if expandable_sections:
                    wysiwyg_features['expandable_sections'] += len(expandable_sections)
                    article_wysiwyg_count += len(expandable_sections)
                    log_test_result(f"   ✅ Found {len(expandable_sections)} expandable sections", "SUCCESS")
                
                # Check for contextual callouts
                callouts = soup.find_all(['div', 'aside'], class_=re.compile(r'callout|note|tip|warning|info|alert'))
                if callouts:
                    wysiwyg_features['contextual_callouts'] += len(callouts)
                    article_wysiwyg_count += len(callouts)
                    log_test_result(f"   ✅ Found {len(callouts)} contextual callouts", "SUCCESS")
                
                # Check for copy functionality
                copy_elements = soup.find_all(['button', 'span'], class_=re.compile(r'copy|clipboard'))
                if copy_elements:
                    wysiwyg_features['copy_functionality'] += len(copy_elements)
                    article_wysiwyg_count += len(copy_elements)
                    log_test_result(f"   ✅ Found {len(copy_elements)} copy functionality elements", "SUCCESS")
                
                # Check for heading IDs (for navigation)
                headings_with_ids = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], id=True)
                if headings_with_ids:
                    wysiwyg_features['heading_ids'] += len(headings_with_ids)
                    article_wysiwyg_count += len(headings_with_ids)
                    log_test_result(f"   ✅ Found {len(headings_with_ids)} headings with IDs", "SUCCESS")
                
                # Check for mini-TOC structure
                toc_elements = soup.find_all(['ul', 'ol'], class_=re.compile(r'toc|table-of-contents'))
                if toc_elements:
                    wysiwyg_features['mini_toc_structure'] += len(toc_elements)
                    article_wysiwyg_count += len(toc_elements)
                    log_test_result(f"   ✅ Found {len(toc_elements)} TOC structures", "SUCCESS")
                
                # Check for interactive elements
                interactive_elements = soup.find_all(['button', 'a'], class_=True) or \
                                     soup.find_all(attrs={'data-action': True})
                if interactive_elements:
                    wysiwyg_features['interactive_elements'] += len(interactive_elements)
                    article_wysiwyg_count += len(interactive_elements)
                    log_test_result(f"   ✅ Found {len(interactive_elements)} interactive elements", "SUCCESS")
                
                if article_wysiwyg_count > 0:
                    articles_with_wysiwyg += 1
                    log_test_result(f"   🎉 Article has {article_wysiwyg_count} WYSIWYG features", "SUCCESS")
                else:
                    log_test_result(f"   ⚠️ Article has no WYSIWYG features", "WARNING")
        
        # Final assessment
        log_test_result("\n" + "=" * 80)
        log_test_result("🎯 WYSIWYG TEMPLATE INTEGRATION ANALYSIS RESULTS", "CRITICAL")
        log_test_result("=" * 80)
        
        # Content cleanliness assessment
        log_test_result(f"📊 CONTENT CLEANLINESS:")
        log_test_result(f"   ✅ Clean articles: {clean_articles}/{len(articles)} ({clean_articles/len(articles)*100:.1f}%)")
        log_test_result(f"   ❌ Contaminated articles: {contaminated_articles}/{len(articles)} ({contaminated_articles/len(articles)*100:.1f}%)")
        
        # WYSIWYG features summary
        total_wysiwyg_features = sum(wysiwyg_features.values())
        log_test_result(f"\n📊 WYSIWYG FEATURES SUMMARY:")
        for feature, count in wysiwyg_features.items():
            log_test_result(f"   {feature.replace('_', ' ').title()}: {count}")
        
        log_test_result(f"\n📈 OVERALL WYSIWYG INTEGRATION:")
        log_test_result(f"   Total WYSIWYG features found: {total_wysiwyg_features}")
        log_test_result(f"   Articles with WYSIWYG features: {articles_with_wysiwyg}/{len(articles)} ({articles_with_wysiwyg/len(articles)*100:.1f}%)")
        
        # Success criteria assessment
        success_criteria = {
            'clean_content': clean_articles >= len(articles) * 0.8,  # 80% clean
            'wysiwyg_features': total_wysiwyg_features >= 5,  # At least 5 WYSIWYG features
            'feature_coverage': articles_with_wysiwyg >= len(articles) * 0.3,  # 30% of articles have features
            'no_major_contamination': contaminated_articles <= len(articles) * 0.2  # Less than 20% contaminated
        }
        
        passed_criteria = sum(success_criteria.values())
        total_criteria = len(success_criteria)
        
        log_test_result(f"\n🎯 SUCCESS CRITERIA ASSESSMENT:")
        for criterion, passed in success_criteria.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            log_test_result(f"   {criterion.replace('_', ' ').title()}: {status}")
        
        log_test_result(f"\nOVERALL RESULT: {passed_criteria}/{total_criteria} criteria passed")
        
        if passed_criteria >= 3:
            log_test_result("🎉 WYSIWYG TEMPLATE INTEGRATION ANALYSIS: MOSTLY SUCCESSFUL", "CRITICAL_SUCCESS")
            log_test_result("✅ System shows good progress toward WYSIWYG integration", "CRITICAL_SUCCESS")
            return True
        else:
            log_test_result("❌ WYSIWYG TEMPLATE INTEGRATION ANALYSIS: NEEDS IMPROVEMENT", "CRITICAL_ERROR")
            log_test_result("❌ System needs more work on WYSIWYG template integration", "CRITICAL_ERROR")
            return False
    
    except Exception as e:
        log_test_result(f"❌ WYSIWYG analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("WYSIWYG Template Integration Analysis")
    print("=" * 50)
    
    success = analyze_wysiwyg_features()
    
    if success:
        exit(0)
    else:
        exit(1)