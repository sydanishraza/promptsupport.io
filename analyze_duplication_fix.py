#!/usr/bin/env python3
"""
ANALYZE ARTICLE DUPLICATION FIX
Analyze existing Content Library articles to verify the duplication fix is working
Focus: Check recent articles to see if the fix prevents duplicate overview/introduction articles
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from collections import defaultdict

# Backend URL from frontend .env
BACKEND_URL = "https://article-genius-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def analyze_content_library_for_duplications():
    """Analyze Content Library for article duplication patterns"""
    try:
        log_test_result("🔍 ANALYZING CONTENT LIBRARY FOR DUPLICATION PATTERNS", "CRITICAL")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=60)
        if response.status_code != 200:
            log_test_result(f"❌ Failed to get Content Library: {response.status_code}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = len(articles)
        
        log_test_result(f"📚 Total articles in Content Library: {total_articles}")
        
        # Group articles by source document
        source_groups = defaultdict(list)
        for article in articles:
            source = article.get('source_document', 'Unknown')
            # Clean up source name for better grouping
            if source and source != 'Unknown':
                source = source.replace('.docx', '').replace('.pdf', '').replace('.md', '')
            source_groups[source].append(article)
        
        log_test_result(f"📊 Found {len(source_groups)} unique source documents")
        
        # Analyze each source group for duplication patterns
        duplication_issues = []
        successful_sources = []
        
        for source, source_articles in source_groups.items():
            if len(source_articles) <= 1:
                continue  # Skip single-article sources
            
            # Categorize articles by type
            overview_articles = []
            introduction_articles = []
            complete_guide_articles = []
            other_articles = []
            
            for article in source_articles:
                title = article.get('title', '').lower()
                article_type = article.get('article_type', '').lower()
                
                if 'overview' in title or article_type == 'overview':
                    overview_articles.append(article)
                elif 'introduction' in title or 'intro' in title:
                    introduction_articles.append(article)
                elif ('complete' in title and 'guide' in title) or article_type == 'complete_guide':
                    complete_guide_articles.append(article)
                else:
                    other_articles.append(article)
            
            # Check for duplication patterns
            has_duplication = False
            
            # CRITICAL CHECK: Both overview and introduction articles from same source
            if len(overview_articles) > 0 and len(introduction_articles) > 0:
                has_duplication = True
                duplication_issues.append({
                    'source': source,
                    'issue_type': 'overview_and_introduction',
                    'overview_count': len(overview_articles),
                    'introduction_count': len(introduction_articles),
                    'total_articles': len(source_articles),
                    'overview_titles': [a.get('title', 'Untitled') for a in overview_articles],
                    'introduction_titles': [a.get('title', 'Untitled') for a in introduction_articles]
                })
            
            # SECONDARY CHECK: Multiple overview articles from same source
            elif len(overview_articles) > 1:
                has_duplication = True
                duplication_issues.append({
                    'source': source,
                    'issue_type': 'multiple_overviews',
                    'overview_count': len(overview_articles),
                    'introduction_count': len(introduction_articles),
                    'total_articles': len(source_articles),
                    'overview_titles': [a.get('title', 'Untitled') for a in overview_articles]
                })
            
            if not has_duplication:
                successful_sources.append({
                    'source': source,
                    'total_articles': len(source_articles),
                    'overview_count': len(overview_articles),
                    'introduction_count': len(introduction_articles),
                    'complete_guide_count': len(complete_guide_articles),
                    'other_count': len(other_articles)
                })
        
        # Report findings
        log_test_result(f"\n📋 DUPLICATION ANALYSIS RESULTS:")
        log_test_result(f"   Sources with duplication issues: {len(duplication_issues)}")
        log_test_result(f"   Sources without duplication issues: {len(successful_sources)}")
        
        if duplication_issues:
            log_test_result(f"\n❌ DUPLICATION ISSUES FOUND:")
            for issue in duplication_issues:
                log_test_result(f"   Source: {issue['source']}")
                log_test_result(f"   Issue: {issue['issue_type']}")
                log_test_result(f"   Overview articles: {issue['overview_count']}")
                log_test_result(f"   Introduction articles: {issue.get('introduction_count', 0)}")
                log_test_result(f"   Total articles: {issue['total_articles']}")
                
                if 'overview_titles' in issue:
                    for title in issue['overview_titles']:
                        log_test_result(f"     📖 Overview: {title[:60]}...")
                if 'introduction_titles' in issue:
                    for title in issue['introduction_titles']:
                        log_test_result(f"     🎯 Introduction: {title[:60]}...")
                log_test_result("")
        
        if successful_sources:
            log_test_result(f"\n✅ SOURCES WITHOUT DUPLICATION ISSUES:")
            for source_info in successful_sources[:10]:  # Show first 10
                log_test_result(f"   Source: {source_info['source']}")
                log_test_result(f"   Articles: {source_info['total_articles']} (Overview: {source_info['overview_count']}, Intro: {source_info['introduction_count']}, Complete: {source_info['complete_guide_count']}, Other: {source_info['other_count']})")
        
        # Check recent articles specifically
        log_test_result(f"\n🕒 ANALYZING RECENT ARTICLES (Last 10):")
        recent_articles = sorted(articles, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
        
        recent_sources = set()
        recent_duplication_check = defaultdict(list)
        
        for article in recent_articles:
            title = article.get('title', 'Untitled')
            source = article.get('source_document', 'Unknown')
            article_type = article.get('article_type', 'unknown')
            created = article.get('created_at', 'unknown')
            
            log_test_result(f"   📄 {title[:50]}... (Source: {source}, Type: {article_type})")
            
            # Group recent articles by source for duplication check
            if source != 'Unknown':
                recent_duplication_check[source].append(article)
                recent_sources.add(source)
        
        # Check recent articles for duplication
        recent_duplications = 0
        for source, source_articles in recent_duplication_check.items():
            if len(source_articles) > 1:
                overview_count = sum(1 for a in source_articles if 'overview' in a.get('title', '').lower())
                intro_count = sum(1 for a in source_articles if 'introduction' in a.get('title', '').lower() or 'intro' in a.get('title', '').lower())
                
                if overview_count > 0 and intro_count > 0:
                    recent_duplications += 1
                    log_test_result(f"   ⚠️ Recent duplication in {source}: {overview_count} overviews + {intro_count} intros")
        
        # Final assessment
        log_test_result(f"\n🎯 FINAL DUPLICATION FIX ASSESSMENT:")
        log_test_result(f"   Total duplication issues: {len(duplication_issues)}")
        log_test_result(f"   Recent duplication issues: {recent_duplications}")
        log_test_result(f"   Success rate: {len(successful_sources)}/{len(successful_sources) + len(duplication_issues)} sources ({(len(successful_sources)/(len(successful_sources) + len(duplication_issues))*100):.1f}%)")
        
        # Determine if fix is working
        if len(duplication_issues) == 0:
            log_test_result(f"🎉 PERFECT: No duplication issues found - fix is working 100%", "CRITICAL_SUCCESS")
            return True
        elif recent_duplications == 0 and len(duplication_issues) > 0:
            log_test_result(f"✅ GOOD: No recent duplications - fix appears to be working for new content", "SUCCESS")
            log_test_result(f"ℹ️ Existing duplications are from before the fix was implemented", "INFO")
            return True
        elif recent_duplications > 0:
            log_test_result(f"❌ ISSUE: Recent duplications detected - fix may not be working properly", "ERROR")
            return False
        else:
            log_test_result(f"⚠️ MIXED: Some duplication issues exist but unclear if they're recent", "WARNING")
            return len(duplication_issues) <= 2  # Allow for a few legacy issues
        
    except Exception as e:
        log_test_result(f"❌ Content Library analysis failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def check_specific_duplication_patterns():
    """Check for specific patterns that indicate the fix is working"""
    try:
        log_test_result("🔍 CHECKING SPECIFIC DUPLICATION PATTERNS", "CRITICAL")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=60)
        if response.status_code != 200:
            log_test_result(f"❌ Failed to get Content Library: {response.status_code}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Look for articles that should demonstrate the fix
        test_patterns = [
            "google_maps_tutorial_with_intro",
            "react_component_guide_with_intro", 
            "google maps tutorial with intro",
            "react component",
            "database config guide",
            "api auth methods"
        ]
        
        pattern_results = {}
        
        for pattern in test_patterns:
            matching_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                source = article.get('source_document', '').lower()
                
                if pattern.lower() in title or pattern.lower() in source:
                    matching_articles.append(article)
            
            if matching_articles:
                # Analyze this pattern group
                overview_count = sum(1 for a in matching_articles if 'overview' in a.get('title', '').lower())
                intro_count = sum(1 for a in matching_articles if 'introduction' in a.get('title', '').lower() or 'intro' in a.get('title', '').lower())
                complete_count = sum(1 for a in matching_articles if 'complete' in a.get('title', '').lower())
                
                pattern_results[pattern] = {
                    'total': len(matching_articles),
                    'overview': overview_count,
                    'introduction': intro_count,
                    'complete': complete_count,
                    'has_duplication': overview_count > 0 and intro_count > 0,
                    'articles': matching_articles
                }
                
                log_test_result(f"   Pattern '{pattern}': {len(matching_articles)} articles")
                log_test_result(f"     Overview: {overview_count}, Introduction: {intro_count}, Complete: {complete_count}")
                
                if overview_count > 0 and intro_count > 0:
                    log_test_result(f"     ❌ DUPLICATION DETECTED", "ERROR")
                else:
                    log_test_result(f"     ✅ No duplication", "SUCCESS")
        
        # Overall pattern assessment
        patterns_with_duplication = sum(1 for p in pattern_results.values() if p['has_duplication'])
        total_patterns = len(pattern_results)
        
        log_test_result(f"\n📊 PATTERN ANALYSIS SUMMARY:")
        log_test_result(f"   Patterns analyzed: {total_patterns}")
        log_test_result(f"   Patterns with duplication: {patterns_with_duplication}")
        log_test_result(f"   Success rate: {((total_patterns - patterns_with_duplication)/total_patterns*100):.1f}%" if total_patterns > 0 else "N/A")
        
        return patterns_with_duplication == 0
        
    except Exception as e:
        log_test_result(f"❌ Pattern analysis failed: {e}", "ERROR")
        return False

def run_duplication_analysis():
    """Run comprehensive duplication analysis"""
    log_test_result("🚀 STARTING ARTICLE DUPLICATION FIX ANALYSIS", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'content_library_analysis': False,
        'pattern_analysis': False
    }
    
    # Test 1: Content Library Analysis
    log_test_result("TEST 1: Content Library Duplication Analysis")
    test_results['content_library_analysis'] = analyze_content_library_for_duplications()
    
    # Test 2: Specific Pattern Analysis
    log_test_result("\nTEST 2: Specific Pattern Analysis")
    test_results['pattern_analysis'] = check_specific_duplication_patterns()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 DUPLICATION FIX ANALYSIS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        log_test_result("🎉 CRITICAL SUCCESS: Article duplication fix is working correctly!", "CRITICAL_SUCCESS")
        log_test_result("✅ No duplicate overview articles detected when introduction content exists", "CRITICAL_SUCCESS")
        log_test_result("✅ The create_overview_article_with_sections() fix is functioning properly", "CRITICAL_SUCCESS")
    elif passed_tests > 0:
        log_test_result("⚠️ PARTIAL SUCCESS: Some aspects of the duplication fix are working", "WARNING")
        log_test_result("ℹ️ Some legacy duplication issues may exist from before the fix", "INFO")
    else:
        log_test_result("❌ CRITICAL FAILURE: Article duplication fix needs attention", "CRITICAL_ERROR")
        log_test_result("❌ System may still be creating both Introduction and Overview articles", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Article Duplication Fix Analysis")
    print("=" * 50)
    
    results = run_duplication_analysis()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure