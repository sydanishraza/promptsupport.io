#!/usr/bin/env python3
"""
QUICK ENHANCEMENT VERIFICATION
Verify that the enhanced outline-first approach features are working
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def verify_content_library_articles():
    """Verify articles in Content Library and check for enhancement features"""
    try:
        log_test_result("🔍 Verifying Content Library articles for enhancement features...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library check failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        total_articles = data.get('total', 0)
        articles = data.get('articles', [])
        
        log_test_result(f"📚 Content Library Status:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Articles Retrieved: {len(articles)}")
        
        # Look for recently created articles from our test
        recent_articles = []
        api_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            source = article.get('source_document', '').lower()
            created_at = article.get('created_at', '')
            
            # Look for API-related articles (from our test)
            if any(keyword in title for keyword in ['api', 'authentication', 'oauth', 'webhook', 'rest', 'integration']):
                api_articles.append(article)
                
            # Look for very recent articles (created in last hour)
            if created_at:
                try:
                    from datetime import datetime, timedelta
                    if isinstance(created_at, str):
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_time = created_at
                    
                    if datetime.now().replace(tzinfo=created_time.tzinfo) - created_time < timedelta(hours=1):
                        recent_articles.append(article)
                except:
                    pass
        
        log_test_result(f"✅ Found {len(api_articles)} API-related articles")
        log_test_result(f"✅ Found {len(recent_articles)} recent articles (last hour)")
        
        # Verify enhancement features
        enhancement_results = {
            'outline_based_articles': 0,
            'toc_article': False,
            'related_links': 0,
            'faq_article': False,
            'article_diversity': set(),
            'proper_metadata': 0
        }
        
        # Check articles for enhancement features
        for article in api_articles[:10]:  # Check first 10 API articles
            title = article.get('title', '').lower()
            content = article.get('content', '')
            article_type = article.get('article_type', '')
            metadata = article.get('metadata', {})
            
            # Check for outline-based metadata
            if metadata and metadata.get('outline_based'):
                enhancement_results['outline_based_articles'] += 1
            
            # Check for introductory TOC article
            if any(keyword in title for keyword in ['overview', 'table of contents', 'complete guide', 'introduction']):
                enhancement_results['toc_article'] = True
                log_test_result(f"✅ Found potential TOC article: {article.get('title', 'Untitled')[:50]}")
                
                # Check if TOC contains links to other articles
                if '/content-library/article/' in content:
                    log_test_result("✅ TOC article contains proper Content Library links")
            
            # Check for related links in articles
            if 'related-links' in content or 'Related Articles' in content:
                enhancement_results['related_links'] += 1
            
            # Check for FAQ/Troubleshooting article
            if any(keyword in title for keyword in ['faq', 'troubleshooting', 'common issues']):
                enhancement_results['faq_article'] = True
                log_test_result(f"✅ Found FAQ/Troubleshooting article: {article.get('title', 'Untitled')[:50]}")
            
            # Check article type diversity
            if article_type:
                enhancement_results['article_diversity'].add(article_type)
            
            # Check proper metadata
            if metadata:
                enhancement_results['proper_metadata'] += 1
        
        # Report results
        log_test_result(f"📊 ENHANCEMENT FEATURES VERIFICATION:")
        log_test_result(f"   Outline-based articles: {enhancement_results['outline_based_articles']}")
        log_test_result(f"   TOC article found: {'✅ YES' if enhancement_results['toc_article'] else '❌ NO'}")
        log_test_result(f"   Articles with related links: {enhancement_results['related_links']}")
        log_test_result(f"   FAQ article found: {'✅ YES' if enhancement_results['faq_article'] else '❌ NO'}")
        log_test_result(f"   Article types found: {', '.join(enhancement_results['article_diversity']) if enhancement_results['article_diversity'] else 'None'}")
        log_test_result(f"   Articles with metadata: {enhancement_results['proper_metadata']}")
        
        # Calculate success score
        success_score = 0
        if enhancement_results['outline_based_articles'] > 0:
            success_score += 1
        if enhancement_results['toc_article']:
            success_score += 1
        if enhancement_results['related_links'] > 0:
            success_score += 1
        if enhancement_results['faq_article']:
            success_score += 1
        if len(enhancement_results['article_diversity']) >= 2:
            success_score += 1
        if enhancement_results['proper_metadata'] > 0:
            success_score += 1
        
        log_test_result(f"🎯 ENHANCEMENT SUCCESS SCORE: {success_score}/6 features verified")
        
        return success_score >= 4  # At least 4 out of 6 features should be present
        
    except Exception as e:
        log_test_result(f"❌ Enhancement features verification failed: {e}", "ERROR")
        return False

def check_backend_logs_for_enhancements():
    """Check backend logs for enhancement messages"""
    try:
        log_test_result("🔍 Checking backend logs for enhancement messages...")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '500', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                
                enhancement_indicators = [
                    "ADDING COMPREHENSIVE ENHANCEMENTS",
                    "Creating introductory Table of Contents article",
                    "Generating FAQ/Troubleshooting article", 
                    "ENHANCED OUTLINE-BASED PROCESSING COMPLETE",
                    "COMPREHENSIVE OUTLINE GENERATED",
                    "outline-first approach",
                    "articles planned",
                    "CREATING ARTICLES FROM OUTLINE"
                ]
                
                found_indicators = []
                for indicator in enhancement_indicators:
                    if indicator in logs:
                        found_indicators.append(indicator)
                
                if found_indicators:
                    log_test_result(f"✅ Found {len(found_indicators)} enhancement indicators in backend logs:", "SUCCESS")
                    for indicator in found_indicators:
                        log_test_result(f"   - {indicator}")
                    return True
                else:
                    log_test_result("⚠️ No enhancement indicators found in backend logs")
                    return False
            else:
                log_test_result("⚠️ Could not access backend logs")
                return False
                
        except Exception as log_error:
            log_test_result(f"⚠️ Backend log check failed: {log_error}")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend log verification failed: {e}", "ERROR")
        return False

def main():
    """Main verification function"""
    log_test_result("🚀 STARTING QUICK ENHANCEMENT VERIFICATION", "CRITICAL")
    log_test_result("=" * 60)
    
    # Test 1: Content Library Verification
    log_test_result("TEST 1: Content Library Enhancement Features Verification")
    content_library_success = verify_content_library_articles()
    
    # Test 2: Backend Logs Check
    log_test_result("\nTEST 2: Backend Enhancement Logs Verification")
    backend_logs_success = check_backend_logs_for_enhancements()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 60)
    log_test_result("🎯 QUICK VERIFICATION RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 60)
    
    log_test_result(f"Content Library Features: {'✅ PASSED' if content_library_success else '❌ FAILED'}")
    log_test_result(f"Backend Logs Check: {'✅ PASSED' if backend_logs_success else '❌ FAILED'}")
    
    if content_library_success and backend_logs_success:
        log_test_result("🎉 VERIFICATION SUCCESS: Enhanced outline-first approach is working!", "SUCCESS")
        log_test_result("✅ Enhancement pipeline operational with key features verified", "SUCCESS")
        return True
    else:
        log_test_result("⚠️ PARTIAL SUCCESS: Some enhancement features verified", "WARNING")
        return False

if __name__ == "__main__":
    print("Quick Enhancement Verification")
    print("=" * 40)
    
    success = main()
    
    if success:
        exit(0)
    else:
        exit(1)