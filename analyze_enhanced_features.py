#!/usr/bin/env python3
"""
ENHANCED FEATURES ANALYSIS - Real Code Path Fixes Verification
Analyze existing articles for enhanced content generation features.
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

# Backend URL from frontend .env
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def get_content_library_articles():
    """Get all articles from Content Library"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            log_test_result(f"📚 Retrieved {len(articles)} articles from Content Library")
            return articles
        else:
            log_test_result(f"❌ Content Library retrieval failed: Status {response.status_code}", "ERROR")
            return []
            
    except Exception as e:
        log_test_result(f"❌ Content Library retrieval failed: {e}", "ERROR")
        return []

def analyze_enhanced_features(article):
    """Analyze a single article for all enhanced features"""
    try:
        article_id = article.get('id', 'unknown')
        title = article.get('title', 'Untitled')
        content = article.get('content', '')
        
        if not content or len(content.strip()) < 100:
            return {
                'article_id': article_id,
                'title': title,
                'has_content': False,
                'content_length': len(content),
                'features': {}
            }
        
        # Parse HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Feature 1: Mini-TOC with anchor links
        toc_elements = soup.find_all(['div', 'ul', 'nav'], class_=re.compile(r'toc|table-of-contents|mini-toc', re.I))
        anchor_links = soup.find_all('a', href=re.compile(r'^#'))
        has_mini_toc = len(toc_elements) > 0 or len(anchor_links) > 0
        
        # Feature 2: Enhanced Code Blocks with syntax highlighting
        code_blocks = soup.find_all(['pre', 'code'])
        enhanced_code_blocks = []
        for block in code_blocks:
            # Check for language classes or syntax highlighting
            classes = block.get('class', [])
            if any('language-' in str(cls) or 'hljs' in str(cls) or 'highlight' in str(cls) for cls in classes):
                enhanced_code_blocks.append(block)
        
        has_enhanced_code_blocks = len(enhanced_code_blocks) > 0
        
        # Feature 3: Proper Heading Hierarchy (no H1 in body content)
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        h4_tags = soup.find_all('h4')
        proper_heading_hierarchy = len(h1_tags) == 0 and len(h2_tags) > 0
        
        # Feature 4: Enhanced List Rendering with hierarchical CSS classes
        lists = soup.find_all(['ul', 'ol'])
        enhanced_lists = []
        for lst in lists:
            classes = lst.get('class', [])
            if any('doc-list' in str(cls) or 'enhanced-list' in str(cls) or 'hierarchical' in str(cls) for cls in classes):
                enhanced_lists.append(lst)
        
        has_enhanced_lists = len(enhanced_lists) > 0
        
        # Feature 5: Contextual Cross-References within article content
        internal_links = soup.find_all('a', href=re.compile(r'/content-library/article/'))
        has_cross_references = len(internal_links) > 0
        
        # Feature 6: Simple Related Links list (not categorized divs)
        related_sections = soup.find_all(['div', 'section'], class_=re.compile(r'related|cross-ref', re.I))
        related_lists = soup.find_all('ul', class_=re.compile(r'related|cross-ref', re.I))
        # Check for simple list structure (not categorized divs)
        simple_related_links = False
        for section in related_sections:
            # Look for simple ul/li structure without nested category divs
            lists_in_section = section.find_all('ul')
            if lists_in_section and not section.find_all('div', class_=re.compile(r'category|group', re.I)):
                simple_related_links = True
                break
        
        has_simple_related_links = simple_related_links or len(related_lists) > 0
        
        # Feature 7: Callouts and Enhanced Formatting
        callouts = soup.find_all(['div', 'blockquote', 'aside'], class_=re.compile(r'callout|alert|note|warning|tip|info', re.I))
        enhanced_formatting_elements = soup.find_all(['strong', 'em', 'mark', 'blockquote', 'code'])
        has_callouts = len(callouts) > 0
        has_enhanced_formatting = len(enhanced_formatting_elements) > 0
        
        return {
            'article_id': article_id,
            'title': title,
            'has_content': True,
            'content_length': len(content),
            'features': {
                'mini_toc': {
                    'present': has_mini_toc,
                    'toc_elements': len(toc_elements),
                    'anchor_links': len(anchor_links)
                },
                'enhanced_code_blocks': {
                    'present': has_enhanced_code_blocks,
                    'total_code_blocks': len(code_blocks),
                    'enhanced_blocks': len(enhanced_code_blocks)
                },
                'proper_heading_hierarchy': {
                    'present': proper_heading_hierarchy,
                    'h1_count': len(h1_tags),
                    'h2_count': len(h2_tags),
                    'h3_count': len(h3_tags),
                    'h4_count': len(h4_tags)
                },
                'enhanced_lists': {
                    'present': has_enhanced_lists,
                    'total_lists': len(lists),
                    'enhanced_lists': len(enhanced_lists)
                },
                'cross_references': {
                    'present': has_cross_references,
                    'internal_links': len(internal_links)
                },
                'simple_related_links': {
                    'present': has_simple_related_links,
                    'related_sections': len(related_sections),
                    'related_lists': len(related_lists)
                },
                'callouts': {
                    'present': has_callouts,
                    'callout_count': len(callouts)
                },
                'enhanced_formatting': {
                    'present': has_enhanced_formatting,
                    'formatting_elements': len(enhanced_formatting_elements)
                }
            }
        }
        
    except Exception as e:
        log_test_result(f"❌ Article analysis failed for {article.get('title', 'Unknown')}: {e}", "ERROR")
        return {
            'article_id': article.get('id', 'unknown'),
            'title': article.get('title', 'Unknown'),
            'has_content': False,
            'features': {},
            'error': str(e)
        }

def analyze_recent_articles_for_enhanced_features():
    """Analyze recent articles for enhanced features"""
    try:
        log_test_result("🎯 ANALYZING RECENT ARTICLES FOR ENHANCED FEATURES", "CRITICAL")
        
        # Get all articles from Content Library
        all_articles = get_content_library_articles()
        
        if not all_articles:
            log_test_result("❌ No articles found in Content Library", "ERROR")
            return False
        
        # Analyze most recent 20 articles
        recent_articles = all_articles[-20:] if len(all_articles) > 20 else all_articles
        
        log_test_result(f"🔍 ANALYZING {len(recent_articles)} RECENT ARTICLES FOR ENHANCED FEATURES")
        log_test_result("=" * 70)
        
        feature_analysis_results = []
        articles_with_content = 0
        
        for article in recent_articles:
            analysis = analyze_enhanced_features(article)
            feature_analysis_results.append(analysis)
            if analysis.get('has_content', False):
                articles_with_content += 1
        
        log_test_result(f"📊 Articles with content for analysis: {articles_with_content}/{len(recent_articles)}")
        
        # Compile and report results
        return compile_feature_analysis_results(feature_analysis_results)
        
    except Exception as e:
        log_test_result(f"❌ Enhanced features analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def compile_feature_analysis_results(feature_analysis_results):
    """Compile comprehensive results for all enhanced features"""
    try:
        log_test_result("\n📊 COMPILING ENHANCED FEATURES ANALYSIS RESULTS", "CRITICAL")
        log_test_result("=" * 70)
        
        # Filter articles with content
        articles_with_content = [a for a in feature_analysis_results if a.get('has_content', False)]
        
        if not articles_with_content:
            log_test_result("❌ No articles with content found for feature analysis", "ERROR")
            return False
        
        log_test_result(f"🎯 ENHANCED FEATURES ANALYSIS ({len(articles_with_content)} articles with content):")
        log_test_result("=" * 70)
        
        # Initialize feature statistics
        feature_stats = {
            'mini_toc': {'present': 0, 'total': 0, 'details': []},
            'enhanced_code_blocks': {'present': 0, 'total': 0, 'details': []},
            'proper_heading_hierarchy': {'present': 0, 'total': 0, 'details': []},
            'enhanced_lists': {'present': 0, 'total': 0, 'details': []},
            'cross_references': {'present': 0, 'total': 0, 'details': []},
            'simple_related_links': {'present': 0, 'total': 0, 'details': []},
            'callouts': {'present': 0, 'total': 0, 'details': []},
            'enhanced_formatting': {'present': 0, 'total': 0, 'details': []}
        }
        
        # Analyze each article
        for analysis in articles_with_content:
            features = analysis.get('features', {})
            article_title = analysis.get('title', 'Unknown')[:50]
            
            for feature_name in feature_stats.keys():
                if feature_name in features:
                    feature_stats[feature_name]['total'] += 1
                    feature_data = features[feature_name]
                    
                    if feature_data.get('present', False):
                        feature_stats[feature_name]['present'] += 1
                        feature_stats[feature_name]['details'].append({
                            'title': article_title,
                            'data': feature_data
                        })
        
        # Calculate and report results for each feature
        critical_features_passed = 0
        total_critical_features = len(feature_stats)
        
        for feature_name, stats in feature_stats.items():
            if stats['total'] > 0:
                success_rate = (stats['present'] / stats['total']) * 100
                feature_display_name = feature_name.replace('_', ' ').title()
                status = "✅ PASSED" if success_rate >= 30 else "❌ FAILED"
                
                log_test_result(f"{status} {feature_display_name}: {stats['present']}/{stats['total']} articles ({success_rate:.1f}%)")
                
                # Detailed reporting for key features
                if feature_name == 'enhanced_code_blocks' and stats['details']:
                    total_code_blocks = sum(d['data'].get('total_code_blocks', 0) for d in stats['details'])
                    enhanced_blocks = sum(d['data'].get('enhanced_blocks', 0) for d in stats['details'])
                    log_test_result(f"   📋 Code Blocks Detail: {enhanced_blocks}/{total_code_blocks} blocks enhanced")
                
                elif feature_name == 'proper_heading_hierarchy' and stats['details']:
                    total_h1 = sum(d['data'].get('h1_count', 0) for d in stats['details'])
                    total_h2 = sum(d['data'].get('h2_count', 0) for d in stats['details'])
                    log_test_result(f"   📋 Heading Detail: {total_h1} H1 tags (should be 0), {total_h2} H2 tags")
                
                elif feature_name == 'cross_references' and stats['details']:
                    total_links = sum(d['data'].get('internal_links', 0) for d in stats['details'])
                    log_test_result(f"   📋 Cross-References Detail: {total_links} internal links found")
                
                # Show sample articles with this feature
                if stats['details'] and len(stats['details']) > 0:
                    sample_titles = [d['title'] for d in stats['details'][:3]]
                    log_test_result(f"   📄 Sample articles: {', '.join(sample_titles)}")
                
                if success_rate >= 30:
                    critical_features_passed += 1
        
        # Overall Assessment
        log_test_result(f"\n🎯 OVERALL REAL CODE PATH FIXES ASSESSMENT:")
        log_test_result("=" * 70)
        
        overall_success_rate = (critical_features_passed / total_critical_features) * 100
        
        log_test_result(f"Critical Features Passed: {critical_features_passed}/{total_critical_features}")
        log_test_result(f"Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Success criteria assessment
        if overall_success_rate >= 70:
            log_test_result("🎉 CRITICAL SUCCESS: Real code path fixes are working correctly!", "CRITICAL_SUCCESS")
            log_test_result("✅ Enhanced content generation features are operational", "CRITICAL_SUCCESS")
            return True
        elif overall_success_rate >= 50:
            log_test_result("⚠️ PARTIAL SUCCESS: Most real code path fixes working, some improvements needed", "WARNING")
            return True
        else:
            log_test_result("❌ CRITICAL FAILURE: Real code path fixes need significant attention", "CRITICAL_ERROR")
            log_test_result("❌ Enhanced content generation features are not working properly", "CRITICAL_ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ Results compilation failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Enhanced Features Analysis - Real Code Path Fixes Verification")
    print("=" * 70)
    
    success = analyze_recent_articles_for_enhanced_features()
    
    print(f"\nFinal Result: {'SUCCESS' if success else 'FAILURE'}")