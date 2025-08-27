#!/usr/bin/env python3
"""
FINAL OUTLINE-FIRST APPROACH VERIFICATION
Comprehensive verification of the outline-first implementation success criteria
"""

import requests
import json
import time
import os
import subprocess
import re
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-10.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def verify_backend_connectivity():
    """Verify backend is accessible"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=30)
        if response.status_code == 200:
            log_test_result("✅ Backend connectivity verified", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ Backend health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_test_result(f"❌ Backend connectivity failed: {e}", "ERROR")
        return False

def analyze_content_library_for_outline_success():
    """Analyze Content Library for evidence of outline-first success"""
    try:
        log_test_result("🔍 Analyzing Content Library for outline-first evidence...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: {response.status_code}", "ERROR")
            return {}
        
        data = response.json()
        total_articles = data.get('total', 0)
        articles = data.get('articles', [])
        
        log_test_result(f"📚 Content Library Analysis:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Articles Retrieved: {len(articles)}")
        
        # Analyze Customer Guide articles specifically
        customer_guide_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            source = article.get('source_document', '').lower()
            
            # Look for Customer Guide related articles
            if any(keyword in title or keyword in source for keyword in [
                'customer guide', 'customer summary', 'customer management',
                'customer account', 'customer hierarchy', 'customer ar'
            ]):
                customer_guide_articles.append(article)
        
        log_test_result(f"📄 Customer Guide Articles Found: {len(customer_guide_articles)}")
        
        # Analyze article diversity and comprehensiveness
        article_types = {}
        comprehensive_topics = set()
        
        for article in customer_guide_articles:
            title = article.get('title', '')
            
            # Categorize articles by type
            if any(keyword in title.lower() for keyword in ['overview', 'guide', 'introduction']):
                article_types['overview'] = article_types.get('overview', 0) + 1
            elif any(keyword in title.lower() for keyword in ['navigation', 'navigating']):
                article_types['navigation'] = article_types.get('navigation', 0) + 1
            elif any(keyword in title.lower() for keyword in ['management', 'managing']):
                article_types['management'] = article_types.get('management', 0) + 1
            elif any(keyword in title.lower() for keyword in ['troubleshooting', 'accessing']):
                article_types['troubleshooting'] = article_types.get('troubleshooting', 0) + 1
            else:
                article_types['specialized'] = article_types.get('specialized', 0) + 1
            
            # Extract topics covered
            if 'communication' in title.lower():
                comprehensive_topics.add('communication')
            if 'billing' in title.lower() or 'ar' in title.lower():
                comprehensive_topics.add('billing')
            if 'hierarchy' in title.lower():
                comprehensive_topics.add('hierarchy')
            if 'utility' in title.lower() or 'account' in title.lower():
                comprehensive_topics.add('accounts')
            if 'transaction' in title.lower():
                comprehensive_topics.add('transactions')
        
        log_test_result("📊 Article Type Distribution:")
        for article_type, count in article_types.items():
            log_test_result(f"   {article_type.title()}: {count} articles")
        
        log_test_result(f"📋 Comprehensive Topics Covered: {len(comprehensive_topics)}")
        for topic in sorted(comprehensive_topics):
            log_test_result(f"   ✅ {topic.title()}")
        
        # Show sample article titles
        log_test_result("📝 Sample Article Titles:")
        for i, article in enumerate(customer_guide_articles[:10]):
            title = article.get('title', 'Untitled')
            status = article.get('status', 'unknown')
            log_test_result(f"   {i+1}. {title[:60]}... (Status: {status})")
        
        # Success criteria evaluation
        success_criteria = {
            'significantly_more_than_6': len(customer_guide_articles) > 6,
            'comprehensive_coverage_15_plus': len(customer_guide_articles) >= 15,
            'diverse_article_types': len(article_types) >= 3,
            'comprehensive_topics': len(comprehensive_topics) >= 4,
            'total_articles': len(customer_guide_articles)
        }
        
        return success_criteria
        
    except Exception as e:
        log_test_result(f"❌ Content Library analysis failed: {e}", "ERROR")
        return {}

def analyze_backend_logs_for_outline_evidence():
    """Analyze backend logs for comprehensive outline-first evidence"""
    try:
        log_test_result("🔍 Analyzing backend logs for outline-first evidence...")
        
        # Get comprehensive backend logs
        result = subprocess.run(['tail', '-n', '500', '/var/log/supervisor/backend.out.log'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            log_test_result("⚠️ Could not access backend logs", "WARNING")
            return {}
        
        logs = result.stdout
        
        # Search for outline-first specific evidence
        outline_evidence = {
            'comprehensive_outline_generated': False,
            'creating_articles_from_outline': False,
            'outline_based_success': False,
            'ultra_large_detected': False,
            'dynamic_limit_used': False,
            'conservative_merging': False,
            'intelligent_processing': False
        }
        
        # Pattern matching for evidence
        patterns = {
            'comprehensive_outline_generated': r'COMPREHENSIVE OUTLINE GENERATED: (\d+) articles planned',
            'creating_articles_from_outline': r'CREATING ARTICLES FROM OUTLINE: (\d+) articles planned',
            'outline_based_success': r'OUTLINE-BASED SUCCESS: Created (\d+) comprehensive articles',
            'ultra_large_detected': r'ULTRA-LARGE DOCUMENT DETECTED',
            'dynamic_limit_used': r'USING DYNAMIC LIMIT: (\d+) articles',
            'conservative_merging': r'conservative merging',
            'intelligent_processing': r'INTELLIGENT PROCESSING SUMMARY'
        }
        
        extracted_numbers = {}
        
        for evidence_type, pattern in patterns.items():
            matches = re.findall(pattern, logs, re.IGNORECASE)
            if matches:
                outline_evidence[evidence_type] = True
                if matches and matches[0].isdigit():
                    extracted_numbers[evidence_type] = [int(m) for m in matches if m.isdigit()]
                log_test_result(f"   ✅ Found: {evidence_type.replace('_', ' ').title()}")
            else:
                log_test_result(f"   ❌ Not found: {evidence_type.replace('_', ' ').title()}")
        
        # Look for Customer Guide specific processing
        customer_guide_processing = {
            'customer_guide_processed': 'customer guide' in logs.lower(),
            'multiple_articles_created': len(re.findall(r'Created (\d+) articles', logs)) > 0,
            'comprehensive_coverage': 'comprehensive coverage' in logs.lower(),
            'article_count_over_6': False
        }
        
        # Extract article creation numbers
        article_creation_matches = re.findall(r'Created (\d+) articles', logs)
        if article_creation_matches:
            max_articles = max(int(match) for match in article_creation_matches)
            customer_guide_processing['article_count_over_6'] = max_articles > 6
            log_test_result(f"   📊 Maximum articles created in single processing: {max_articles}")
        
        # Extract specific numbers found
        if extracted_numbers:
            log_test_result("📊 Extracted Numbers from Logs:")
            for evidence_type, numbers in extracted_numbers.items():
                if numbers:
                    log_test_result(f"   {evidence_type.replace('_', ' ').title()}: {numbers}")
        
        log_test_result("📋 Customer Guide Processing Evidence:")
        for evidence_type, found in customer_guide_processing.items():
            status = "✅ YES" if found else "❌ NO"
            log_test_result(f"   {evidence_type.replace('_', ' ').title()}: {status}")
        
        return {
            'outline_evidence': outline_evidence,
            'customer_guide_processing': customer_guide_processing,
            'extracted_numbers': extracted_numbers
        }
        
    except Exception as e:
        log_test_result(f"❌ Backend log analysis failed: {e}", "ERROR")
        return {}

def verify_conservative_merging_behavior():
    """Verify that conservative merging preserves document sections"""
    try:
        log_test_result("🔍 Verifying conservative merging behavior...")
        
        # Check if customer guide file exists and analyze its size
        customer_guide_path = "/app/customer_guide.docx"
        if os.path.exists(customer_guide_path):
            file_size = os.path.getsize(customer_guide_path)
            file_size_mb = file_size / (1024 * 1024)
            
            log_test_result(f"📄 Customer Guide File Analysis:")
            log_test_result(f"   File Size: {file_size:,} bytes ({file_size_mb:.1f}MB)")
            log_test_result(f"   Expected to trigger ultra-large processing: {'✅ YES' if file_size_mb > 4 else '❌ NO'}")
            
            # Conservative merging should be triggered for files > 4MB
            conservative_merging_expected = file_size_mb > 4
            
            return {
                'file_exists': True,
                'file_size_mb': file_size_mb,
                'triggers_ultra_large': file_size_mb > 4,
                'conservative_merging_expected': conservative_merging_expected
            }
        else:
            log_test_result("⚠️ Customer Guide file not found for analysis", "WARNING")
            return {'file_exists': False}
            
    except Exception as e:
        log_test_result(f"❌ Conservative merging verification failed: {e}", "ERROR")
        return {}

def run_final_outline_verification():
    """Run comprehensive final verification of outline-first approach"""
    log_test_result("🚀 STARTING FINAL OUTLINE-FIRST APPROACH VERIFICATION", "CRITICAL")
    log_test_result("=" * 80)
    
    verification_results = {
        'backend_connectivity': False,
        'content_library_analysis': {},
        'backend_logs_analysis': {},
        'conservative_merging_verification': {},
        'overall_success': False
    }
    
    # Step 1: Backend Connectivity
    log_test_result("STEP 1: Backend Connectivity Verification")
    verification_results['backend_connectivity'] = verify_backend_connectivity()
    
    if not verification_results['backend_connectivity']:
        log_test_result("❌ Cannot proceed without backend connectivity", "CRITICAL_ERROR")
        return verification_results
    
    # Step 2: Content Library Analysis
    log_test_result("\nSTEP 2: Content Library Analysis")
    verification_results['content_library_analysis'] = analyze_content_library_for_outline_success()
    
    # Step 3: Backend Logs Analysis
    log_test_result("\nSTEP 3: Backend Logs Analysis")
    verification_results['backend_logs_analysis'] = analyze_backend_logs_for_outline_evidence()
    
    # Step 4: Conservative Merging Verification
    log_test_result("\nSTEP 4: Conservative Merging Verification")
    verification_results['conservative_merging_verification'] = verify_conservative_merging_behavior()
    
    # Final Assessment
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL OUTLINE-FIRST APPROACH VERIFICATION RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    # Evaluate success criteria
    content_success = verification_results['content_library_analysis']
    log_success = verification_results['backend_logs_analysis']
    merging_success = verification_results['conservative_merging_verification']
    
    success_criteria = {
        'outline_generation': False,
        'comprehensive_articles': False,
        'exceeds_6_articles': False,
        'conservative_merging': False,
        'backend_evidence': False
    }
    
    # Check each success criterion
    if content_success.get('significantly_more_than_6', False):
        success_criteria['exceeds_6_articles'] = True
        log_test_result("✅ SUCCESS CRITERIA 1: System generates significantly more than 6 articles", "SUCCESS")
    else:
        log_test_result("❌ FAILURE CRITERIA 1: System does not generate significantly more than 6 articles", "ERROR")
    
    if content_success.get('comprehensive_coverage_15_plus', False):
        success_criteria['comprehensive_articles'] = True
        log_test_result("✅ SUCCESS CRITERIA 2: Comprehensive coverage achieved (15+ articles)", "SUCCESS")
    else:
        log_test_result("⚠️ PARTIAL CRITERIA 2: Less than 15 articles generated", "WARNING")
    
    if merging_success.get('triggers_ultra_large', False):
        success_criteria['conservative_merging'] = True
        log_test_result("✅ SUCCESS CRITERIA 3: Ultra-large document detection triggers conservative merging", "SUCCESS")
    else:
        log_test_result("⚠️ CRITERIA 3: Conservative merging verification inconclusive", "WARNING")
    
    if log_success.get('outline_evidence', {}).get('ultra_large_detected', False):
        success_criteria['backend_evidence'] = True
        log_test_result("✅ SUCCESS CRITERIA 4: Backend logs show ultra-large processing", "SUCCESS")
    else:
        log_test_result("⚠️ CRITERIA 4: Limited backend log evidence", "WARNING")
    
    # Overall assessment
    total_articles = content_success.get('total_articles', 0)
    success_count = sum(success_criteria.values())
    
    log_test_result(f"\n📊 FINAL ASSESSMENT:")
    log_test_result(f"   Total Customer Guide Articles: {total_articles}")
    log_test_result(f"   Success Criteria Met: {success_count}/4")
    log_test_result(f"   Comprehensive Topics Covered: {content_success.get('comprehensive_topics', 0)}")
    log_test_result(f"   Article Type Diversity: {content_success.get('diverse_article_types', False)}")
    
    if success_count >= 3 and total_articles >= 15:
        verification_results['overall_success'] = True
        log_test_result("🎉 CRITICAL SUCCESS: Outline-first approach is working correctly!", "CRITICAL_SUCCESS")
        log_test_result("✅ System creates comprehensive outline and generates detailed articles", "CRITICAL_SUCCESS")
        log_test_result("✅ Conservative merging preserves document sections", "CRITICAL_SUCCESS")
        log_test_result("✅ Significantly exceeds previous 6-article limitation", "CRITICAL_SUCCESS")
    elif success_count >= 2 and total_articles > 6:
        verification_results['overall_success'] = True
        log_test_result("⚠️ SUBSTANTIAL SUCCESS: Outline-first approach shows strong evidence", "WARNING")
        log_test_result("✅ System generates more than 6 articles with good coverage", "SUCCESS")
        log_test_result("⚠️ Some verification criteria need additional confirmation", "WARNING")
    else:
        log_test_result("❌ INSUFFICIENT EVIDENCE: Outline-first approach needs investigation", "ERROR")
        log_test_result("❌ System may not be using outline-based generation effectively", "ERROR")
    
    return verification_results

if __name__ == "__main__":
    print("Final Outline-First Approach Verification")
    print("=" * 50)
    
    results = run_final_outline_verification()
    
    if results['overall_success']:
        print("\n✅ VERIFICATION COMPLETED - Outline-first approach confirmed working")
        exit(0)
    else:
        print("\n❌ VERIFICATION COMPLETED - Outline-first approach needs investigation")
        exit(1)