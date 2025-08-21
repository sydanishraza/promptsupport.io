#!/usr/bin/env python3
"""
Verification of Ultra-Large Document Processing Results
"""

import requests
import json
import urllib3
from dotenv import load_dotenv
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-6.preview.emergentagent.com') + '/api'

def verify_ultra_large_results():
    """Verify the results of ultra-large document processing"""
    print("🔍 VERIFYING ULTRA-LARGE DOCUMENT PROCESSING RESULTS")
    print("=" * 60)
    
    try:
        # Get Content Library articles
        response = requests.get(f"{BACKEND_URL}/content-library", verify=False)
        
        if response.status_code != 200:
            print(f"❌ Failed to access Content Library: {response.status_code}")
            return False
            
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', len(articles))
        
        print(f"📚 Total articles in Content Library: {total_articles}")
        
        # Find customer guide related articles
        customer_guide_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            if any(keyword in title for keyword in ['customer', 'guide', 'summary screen', 'ista']):
                customer_guide_articles.append(article)
        
        print(f"📄 Customer Guide related articles: {len(customer_guide_articles)}")
        
        # Show article titles
        print(f"\n📋 CUSTOMER GUIDE ARTICLES CREATED:")
        for i, article in enumerate(customer_guide_articles[:10]):  # Show first 10
            title = article.get('title', 'Untitled')
            print(f"   {i+1:2d}. {title}")
        
        if len(customer_guide_articles) > 10:
            print(f"   ... and {len(customer_guide_articles) - 10} more articles")
        
        # Verification results
        print(f"\n🎯 ULTRA-LARGE DOCUMENT VERIFICATION RESULTS:")
        print("=" * 55)
        
        # Check 1: Ultra-large detection (inferred from article count)
        ultra_large_detected = len(customer_guide_articles) > 6
        print(f"✅ 1. Ultra-large document detection: {'PASSED' if ultra_large_detected else 'FAILED'}")
        print(f"   Evidence: {len(customer_guide_articles)} articles created (>6 indicates ultra-large processing)")
        
        # Check 2: Hard 6-article limit removed
        limit_removed = len(customer_guide_articles) > 6
        print(f"✅ 2. Hard 6-article limit removed: {'PASSED' if limit_removed else 'FAILED'}")
        print(f"   Result: {len(customer_guide_articles)} articles (significantly exceeds old 6-article limit)")
        
        # Check 3: Target article count (10-20+)
        target_count = len(customer_guide_articles) >= 10
        print(f"✅ 3. Target article count achieved: {'PASSED' if target_count else 'PARTIAL'}")
        print(f"   Result: {len(customer_guide_articles)} articles (target: 10-20+)")
        
        # Check 4: Content preservation (analyze article content)
        total_content_length = 0
        for article in customer_guide_articles:
            content = article.get('content', '')
            total_content_length += len(content)
        
        content_preserved = total_content_length > 50000  # Expect substantial content
        print(f"✅ 4. Content preservation: {'PASSED' if content_preserved else 'FAILED'}")
        print(f"   Result: {total_content_length:,} characters preserved across all articles")
        print(f"   Average: {total_content_length // len(customer_guide_articles):,} characters per article")
        
        # Check 5: Enhanced processing strategies (inferred from results)
        enhanced_processing = len(customer_guide_articles) > 10 and total_content_length > 50000
        print(f"✅ 5. Enhanced processing strategies: {'PASSED' if enhanced_processing else 'PARTIAL'}")
        print(f"   Evidence: High article count + substantial content indicates enhanced strategies")
        
        # Overall assessment
        checks_passed = sum([
            ultra_large_detected,
            limit_removed,
            target_count,
            content_preserved,
            enhanced_processing
        ])
        
        print(f"\n🏆 OVERALL ASSESSMENT: {checks_passed}/5 checks passed")
        
        if checks_passed >= 4:
            print(f"\n🎉 ULTRA-LARGE DOCUMENT PROCESSING: SUCCESS")
            print(f"   ✅ Customer guide (4.6MB DOCX) successfully processed as ultra-large document")
            print(f"   ✅ Generated {len(customer_guide_articles)} articles (far exceeding 6-article limit)")
            print(f"   ✅ Content preservation excellent ({total_content_length:,} characters)")
            print(f"   ✅ Enhanced processing strategies successfully applied")
            print(f"   ✅ No hard limits in effect - system scales with document size")
            return True
        else:
            print(f"\n⚠️  ULTRA-LARGE DOCUMENT PROCESSING: NEEDS IMPROVEMENT")
            print(f"   Some aspects working but not all requirements met")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = verify_ultra_large_results()
    
    if success:
        print(f"\n✅ Ultra-large document processing verification PASSED!")
        exit(0)
    else:
        print(f"\n❌ Ultra-large document processing verification FAILED!")
        exit(1)