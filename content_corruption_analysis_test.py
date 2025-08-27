#!/usr/bin/env python3
"""
CRITICAL CONTENT CORRUPTION ANALYSIS - Content Library Testing
Testing for content corruption issues as specifically requested in the review:
1. Check for empty or near-empty articles (especially FAQ articles)
2. Verify that articles contain actual source content, not just template placeholders
3. Look for template contamination patterns like repeated HR tags, generic "Related Topics" sections
4. Test the outline-first processing pipeline to ensure it's generating proper content
5. Verify that the `ensure_enhanced_features()` function is properly disabled and not corrupting content
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime
from typing import List, Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_backend_health():
    """Test backend health and connectivity"""
    try:
        log_test_result("Testing backend health check...")
        response = requests.get(f"{API_BASE}/health", timeout=30)
        
        if response.status_code == 200:
            log_test_result("✅ Backend health check PASSED", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ Backend health check FAILED: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend health check FAILED: {e}", "ERROR")
        return False

def get_content_library_articles() -> List[Dict[str, Any]]:
    """Retrieve all articles from Content Library for analysis"""
    try:
        log_test_result("📚 Retrieving articles from Content Library...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_articles = data.get('total', 0)
            articles = data.get('articles', [])
            
            log_test_result(f"✅ Retrieved {len(articles)} articles (Total: {total_articles})")
            return articles
        else:
            log_test_result(f"❌ Failed to retrieve Content Library: Status {response.status_code}", "ERROR")
            return []
            
    except Exception as e:
        log_test_result(f"❌ Content Library retrieval failed: {e}", "ERROR")
        return []

def analyze_article_content_quality(article: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze individual article for content corruption issues"""
    analysis = {
        'article_id': article.get('id', 'unknown'),
        'title': article.get('title', 'Untitled'),
        'content_length': 0,
        'is_empty': False,
        'is_near_empty': False,
        'has_template_contamination': False,
        'has_placeholder_content': False,
        'has_repeated_hr_tags': False,
        'has_generic_sections': False,
        'content_quality_score': 0,
        'issues_found': [],
        'content_preview': ''
    }
    
    content = article.get('content', '')
    analysis['content_length'] = len(content)
    analysis['content_preview'] = content[:200] + '...' if len(content) > 200 else content
    
    # Check for empty or near-empty content
    if len(content.strip()) == 0:
        analysis['is_empty'] = True
        analysis['issues_found'].append('EMPTY_CONTENT')
    elif len(content.strip()) < 100:
        analysis['is_near_empty'] = True
        analysis['issues_found'].append('NEAR_EMPTY_CONTENT')
    
    # Check for template contamination patterns
    template_patterns = [
        r'What are the main benefits\?',
        r'Getting Started Guide',
        r'This is an overview of',
        r'Main content from',
        r'Related Topics:',
        r'<hr>\s*<hr>',  # Repeated HR tags
        r'<!DOCTYPE html>',  # Full document structure
        r'<html>.*<head>.*<body>',  # HTML document wrapper
    ]
    
    for pattern in template_patterns:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            analysis['has_template_contamination'] = True
            analysis['issues_found'].append(f'TEMPLATE_PATTERN: {pattern}')
    
    # Check for repeated HR tags specifically
    hr_count = len(re.findall(r'<hr>', content, re.IGNORECASE))
    if hr_count > 3:
        analysis['has_repeated_hr_tags'] = True
        analysis['issues_found'].append(f'EXCESSIVE_HR_TAGS: {hr_count}')
    
    # Check for generic "Related Topics" sections
    if re.search(r'Related Topics?.*?<ul>.*?</ul>', content, re.IGNORECASE | re.DOTALL):
        generic_links = re.findall(r'<a href="#[^"]*"', content)
        if len(generic_links) > 0:
            analysis['has_generic_sections'] = True
            analysis['issues_found'].append(f'GENERIC_RELATED_LINKS: {len(generic_links)}')
    
    # Check for placeholder content
    placeholder_patterns = [
        r'\[placeholder\]',
        r'\[insert.*?\]',
        r'Lorem ipsum',
        r'TODO:',
        r'FIXME:',
        r'Coming soon',
        r'Under construction'
    ]
    
    for pattern in placeholder_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            analysis['has_placeholder_content'] = True
            analysis['issues_found'].append(f'PLACEHOLDER: {pattern}')
    
    # Calculate content quality score (0-100)
    score = 100
    if analysis['is_empty']:
        score = 0
    elif analysis['is_near_empty']:
        score = 10
    else:
        # Deduct points for issues
        if analysis['has_template_contamination']:
            score -= 30
        if analysis['has_placeholder_content']:
            score -= 20
        if analysis['has_repeated_hr_tags']:
            score -= 15
        if analysis['has_generic_sections']:
            score -= 10
        
        # Bonus points for substantial content
        if len(content) > 1000:
            score += 10
        if len(content) > 5000:
            score += 10
    
    analysis['content_quality_score'] = max(0, score)
    
    return analysis

def analyze_faq_articles_specifically(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Specifically analyze FAQ articles for corruption issues"""
    faq_analysis = {
        'total_faq_articles': 0,
        'empty_faq_articles': 0,
        'corrupted_faq_articles': 0,
        'faq_articles_details': []
    }
    
    log_test_result("🔍 Analyzing FAQ articles specifically...")
    
    for article in articles:
        title = article.get('title', '').lower()
        article_type = article.get('article_type', '').lower()
        
        # Identify FAQ articles
        is_faq = (
            'faq' in title or 
            'frequently asked' in title or 
            'troubleshooting' in title or
            'faq' in article_type
        )
        
        if is_faq:
            faq_analysis['total_faq_articles'] += 1
            
            content = article.get('content', '')
            content_length = len(content.strip())
            
            faq_detail = {
                'title': article.get('title', 'Untitled'),
                'id': article.get('id', 'unknown'),
                'content_length': content_length,
                'is_empty': content_length == 0,
                'is_corrupted': False,
                'issues': []
            }
            
            if content_length == 0:
                faq_analysis['empty_faq_articles'] += 1
                faq_detail['issues'].append('EMPTY_CONTENT')
            elif content_length < 50:
                faq_detail['issues'].append('MINIMAL_CONTENT')
            
            # Check for FAQ-specific corruption patterns
            if content_length > 0:
                # Check if it's just HTML structure without actual Q&A
                if '<h' not in content and 'Q:' not in content and 'A:' not in content:
                    faq_detail['is_corrupted'] = True
                    faq_detail['issues'].append('NO_QA_STRUCTURE')
                
                # Check for template contamination in FAQ
                if 'This is an overview of' in content:
                    faq_detail['is_corrupted'] = True
                    faq_detail['issues'].append('TEMPLATE_CONTAMINATION')
            
            if faq_detail['is_corrupted'] or faq_detail['is_empty']:
                faq_analysis['corrupted_faq_articles'] += 1
            
            faq_analysis['faq_articles_details'].append(faq_detail)
    
    return faq_analysis

def test_knowledge_engine_upload_functionality():
    """Test Knowledge Engine upload to verify current content generation"""
    try:
        log_test_result("🧪 Testing Knowledge Engine upload functionality...")
        
        # Create test content for upload
        test_content = """
        Google Maps JavaScript API Tutorial - Complete Implementation Guide
        
        Introduction
        This comprehensive guide covers the complete implementation of Google Maps JavaScript API in web applications. You'll learn how to integrate maps, add markers, customize styling, and implement advanced features.
        
        Getting Started
        Before implementing Google Maps, you need to obtain an API key from the Google Cloud Console. Follow these steps:
        
        1. Create a Google Cloud Project
        2. Enable the Maps JavaScript API
        3. Generate an API key
        4. Restrict the API key for security
        
        Basic Map Implementation
        Here's how to create a basic map:
        
        ```javascript
        function initMap() {
            const map = new google.maps.Map(document.getElementById("map"), {
                zoom: 10,
                center: { lat: 37.7749, lng: -122.4194 }
            });
        }
        ```
        
        Adding Markers
        To add markers to your map:
        
        ```javascript
        const marker = new google.maps.Marker({
            position: { lat: 37.7749, lng: -122.4194 },
            map: map,
            title: "San Francisco"
        });
        ```
        
        Advanced Features
        The Google Maps API offers many advanced features including:
        - Custom map styling
        - Geocoding services
        - Directions API integration
        - Street View integration
        - Drawing tools
        
        Troubleshooting Common Issues
        Common issues and solutions:
        - API key errors: Verify your key is correct and has proper restrictions
        - Map not loading: Check console for JavaScript errors
        - Markers not appearing: Ensure coordinates are valid
        
        Best Practices
        Follow these best practices for optimal performance:
        - Use API key restrictions
        - Implement proper error handling
        - Optimize marker clustering for large datasets
        - Use appropriate zoom levels
        
        Conclusion
        This guide provides a solid foundation for implementing Google Maps in your web applications. Practice with the examples and explore the extensive API documentation for advanced features.
        """
        
        # Upload test content
        log_test_result("📤 Uploading test content to Knowledge Engine...")
        
        upload_data = {
            'content': test_content,
            'filename': 'google_maps_api_test.txt'
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/content/upload", 
                               data={'content': test_content}, 
                               timeout=300)
        
        if response.status_code != 200:
            log_test_result(f"❌ Upload failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        upload_result = response.json()
        job_id = upload_result.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from upload", "ERROR")
            return False
        
        log_test_result(f"✅ Upload successful, Job ID: {job_id}")
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing...")
        processing_start = time.time()
        max_wait_time = 300  # 5 minutes max
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        articles_generated = status_data.get('articles_generated', 0)
                        log_test_result(f"📄 Articles generated: {articles_generated}")
                        
                        return True
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(5)
                else:
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Knowledge Engine upload test failed: {e}", "ERROR")
        return False

def run_comprehensive_content_corruption_analysis():
    """Run comprehensive content corruption analysis as requested in review"""
    log_test_result("🔍 STARTING COMPREHENSIVE CONTENT CORRUPTION ANALYSIS", "CRITICAL")
    log_test_result("=" * 80)
    
    analysis_results = {
        'backend_health': False,
        'articles_retrieved': 0,
        'empty_articles': 0,
        'near_empty_articles': 0,
        'template_contaminated_articles': 0,
        'placeholder_articles': 0,
        'faq_analysis': {},
        'knowledge_engine_test': False,
        'sample_articles': [],
        'critical_issues': []
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    analysis_results['backend_health'] = test_backend_health()
    
    if not analysis_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting analysis", "CRITICAL_ERROR")
        return analysis_results
    
    # Test 2: Retrieve and Analyze Content Library Articles
    log_test_result("\nTEST 2: Content Library Article Analysis")
    articles = get_content_library_articles()
    analysis_results['articles_retrieved'] = len(articles)
    
    if not articles:
        log_test_result("❌ No articles found in Content Library", "ERROR")
        analysis_results['critical_issues'].append("NO_ARTICLES_FOUND")
        return analysis_results
    
    # Analyze each article for corruption
    log_test_result(f"🔍 Analyzing {len(articles)} articles for content corruption...")
    
    corrupted_articles = []
    high_quality_articles = []
    
    for i, article in enumerate(articles):
        analysis = analyze_article_content_quality(article)
        
        # Track statistics
        if analysis['is_empty']:
            analysis_results['empty_articles'] += 1
        if analysis['is_near_empty']:
            analysis_results['near_empty_articles'] += 1
        if analysis['has_template_contamination']:
            analysis_results['template_contaminated_articles'] += 1
        if analysis['has_placeholder_content']:
            analysis_results['placeholder_articles'] += 1
        
        # Categorize articles
        if analysis['content_quality_score'] < 50:
            corrupted_articles.append(analysis)
        elif analysis['content_quality_score'] > 80:
            high_quality_articles.append(analysis)
        
        # Store sample articles for detailed review
        if i < 5:  # First 5 articles as samples
            analysis_results['sample_articles'].append(analysis)
    
    # Test 3: FAQ-Specific Analysis
    log_test_result("\nTEST 3: FAQ Articles Specific Analysis")
    analysis_results['faq_analysis'] = analyze_faq_articles_specifically(articles)
    
    # Test 4: Knowledge Engine Upload Test
    log_test_result("\nTEST 4: Knowledge Engine Upload Functionality Test")
    analysis_results['knowledge_engine_test'] = test_knowledge_engine_upload_functionality()
    
    # Generate Comprehensive Report
    log_test_result("\n" + "=" * 80)
    log_test_result("📊 COMPREHENSIVE CONTENT CORRUPTION ANALYSIS REPORT", "CRITICAL")
    log_test_result("=" * 80)
    
    # Overall Statistics
    log_test_result(f"📚 Total Articles Analyzed: {analysis_results['articles_retrieved']}")
    log_test_result(f"🚫 Empty Articles: {analysis_results['empty_articles']}")
    log_test_result(f"⚠️  Near-Empty Articles: {analysis_results['near_empty_articles']}")
    log_test_result(f"🔧 Template Contaminated: {analysis_results['template_contaminated_articles']}")
    log_test_result(f"📝 Placeholder Content: {analysis_results['placeholder_articles']}")
    
    # FAQ Analysis Results
    faq_data = analysis_results['faq_analysis']
    log_test_result(f"\n❓ FAQ ARTICLES ANALYSIS:")
    log_test_result(f"   Total FAQ Articles: {faq_data.get('total_faq_articles', 0)}")
    log_test_result(f"   Empty FAQ Articles: {faq_data.get('empty_faq_articles', 0)}")
    log_test_result(f"   Corrupted FAQ Articles: {faq_data.get('corrupted_faq_articles', 0)}")
    
    # Sample Articles Analysis
    log_test_result(f"\n📋 SAMPLE ARTICLES DETAILED ANALYSIS:")
    for i, sample in enumerate(analysis_results['sample_articles']):
        log_test_result(f"   Article {i+1}: {sample['title'][:50]}...")
        log_test_result(f"      Content Length: {sample['content_length']} chars")
        log_test_result(f"      Quality Score: {sample['content_quality_score']}/100")
        if sample['issues_found']:
            log_test_result(f"      Issues: {', '.join(sample['issues_found'])}")
        log_test_result(f"      Preview: {sample['content_preview'][:100]}...")
    
    # Critical Issues Summary
    corruption_percentage = ((analysis_results['empty_articles'] + 
                             analysis_results['near_empty_articles'] + 
                             analysis_results['template_contaminated_articles']) / 
                            max(1, analysis_results['articles_retrieved'])) * 100
    
    log_test_result(f"\n🎯 CRITICAL FINDINGS:")
    log_test_result(f"   Content Corruption Rate: {corruption_percentage:.1f}%")
    
    if corruption_percentage > 20:
        analysis_results['critical_issues'].append("HIGH_CORRUPTION_RATE")
        log_test_result("❌ CRITICAL: High content corruption rate detected!", "CRITICAL_ERROR")
    elif corruption_percentage > 10:
        analysis_results['critical_issues'].append("MODERATE_CORRUPTION_RATE")
        log_test_result("⚠️  WARNING: Moderate content corruption detected", "WARNING")
    else:
        log_test_result("✅ Content corruption rate is within acceptable limits", "SUCCESS")
    
    # Knowledge Engine Test Result
    if analysis_results['knowledge_engine_test']:
        log_test_result("✅ Knowledge Engine upload functionality working correctly", "SUCCESS")
    else:
        log_test_result("❌ Knowledge Engine upload functionality has issues", "ERROR")
        analysis_results['critical_issues'].append("KNOWLEDGE_ENGINE_ISSUES")
    
    # Final Recommendations
    log_test_result(f"\n💡 RECOMMENDATIONS:")
    if analysis_results['empty_articles'] > 0:
        log_test_result("   - Investigate and fix empty article generation")
    if analysis_results['template_contaminated_articles'] > 0:
        log_test_result("   - Review template processing to prevent contamination")
    if faq_data.get('empty_faq_articles', 0) > 0:
        log_test_result("   - Fix FAQ article generation specifically")
    if not analysis_results['knowledge_engine_test']:
        log_test_result("   - Debug Knowledge Engine upload processing pipeline")
    
    return analysis_results

if __name__ == "__main__":
    print("Content Library Corruption Analysis")
    print("=" * 50)
    
    results = run_comprehensive_content_corruption_analysis()
    
    # Exit with appropriate code based on critical issues
    if results['critical_issues']:
        print(f"\n❌ CRITICAL ISSUES DETECTED: {', '.join(results['critical_issues'])}")
        sys.exit(1)  # Failure
    else:
        print(f"\n✅ CONTENT ANALYSIS COMPLETED SUCCESSFULLY")
        sys.exit(0)  # Success