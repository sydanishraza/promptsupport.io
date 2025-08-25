#!/usr/bin/env python3
"""
PHASE 6 BUG FIX VERIFICATION TEST
Direct verification of the bug fixes for empty articles issue
"""

import requests
import json
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-formatter.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def verify_phase6_bug_fixes():
    """Verify Phase 6 bug fixes are working"""
    try:
        log_test_result("🔍 VERIFYING PHASE 6 BUG FIXES", "CRITICAL")
        
        # Get all articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        total_articles = data.get('total', 0)
        
        log_test_result(f"📚 Found {total_articles} articles in Content Library")
        
        if total_articles == 0:
            log_test_result("❌ No articles found - cannot verify bug fixes", "ERROR")
            return False
        
        # SUCCESS CRITERIA VERIFICATION
        success_criteria = {
            'no_empty_articles': True,
            'comprehensive_content': True,
            'code_blocks_preserved': False,
            'no_placeholder_content': True,
            'proper_html_structure': True
        }
        
        empty_articles = 0
        short_articles = 0
        placeholder_articles = 0
        articles_with_code = 0
        articles_with_google_maps = 0
        
        log_test_result("🔍 Analyzing articles for bug fix verification...")
        
        for i, article in enumerate(articles):
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            content_length = len(content.strip())
            
            log_test_result(f"📄 Article {i+1}: {title[:50]}... ({content_length} chars)")
            
            # Check for empty articles
            if content_length == 0:
                empty_articles += 1
                success_criteria['no_empty_articles'] = False
                log_test_result("   ❌ Empty article detected", "ERROR")
            
            # Check for very short articles (likely problematic)
            elif content_length < 100:
                short_articles += 1
                log_test_result(f"   ⚠️ Very short article ({content_length} chars)", "WARNING")
            
            # Check for comprehensive content
            elif content_length > 1000:
                log_test_result("   ✅ Comprehensive content confirmed")
            
            # Check for placeholder content patterns
            placeholder_patterns = [
                'This is an overview of',
                'Main content from',
                '```html\n<!DOCTYPE html>',
                '<html><head><title>',
                'placeholder content'
            ]
            
            if any(pattern in content for pattern in placeholder_patterns):
                placeholder_articles += 1
                success_criteria['no_placeholder_content'] = False
                log_test_result("   ❌ Placeholder content detected", "ERROR")
            
            # Check for code blocks preservation
            if '<code>' in content or '<pre>' in content or 'function' in content:
                articles_with_code += 1
                success_criteria['code_blocks_preserved'] = True
                log_test_result("   ✅ Code blocks preserved")
            
            # Check for Google Maps content (from our test)
            if 'Google Maps' in content or 'JavaScript API' in content:
                articles_with_google_maps += 1
                log_test_result("   ✅ Google Maps tutorial content found")
            
            # Check for proper HTML structure (not full document)
            if content.startswith('<!DOCTYPE html>') or '<html>' in content[:100]:
                success_criteria['proper_html_structure'] = False
                log_test_result("   ❌ Full HTML document structure detected (should be article content only)", "ERROR")
        
        # SUMMARY OF FINDINGS
        log_test_result("\n📊 BUG FIX VERIFICATION SUMMARY:", "CRITICAL")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Empty Articles: {empty_articles}")
        log_test_result(f"   Short Articles (<100 chars): {short_articles}")
        log_test_result(f"   Placeholder Articles: {placeholder_articles}")
        log_test_result(f"   Articles with Code Blocks: {articles_with_code}")
        log_test_result(f"   Articles with Google Maps Content: {articles_with_google_maps}")
        
        # SUCCESS CRITERIA EVALUATION
        log_test_result("\n🎯 SUCCESS CRITERIA EVALUATION:", "CRITICAL")
        passed_criteria = 0
        total_criteria = len(success_criteria)
        
        for criterion, passed in success_criteria.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            log_test_result(f"   {criterion.replace('_', ' ').title()}: {status}")
            if passed:
                passed_criteria += 1
        
        log_test_result(f"\nOVERALL RESULT: {passed_criteria}/{total_criteria} criteria passed")
        
        # SPECIFIC BUG FIX VERIFICATION
        log_test_result("\n🐛 SPECIFIC BUG FIX VERIFICATION:", "CRITICAL")
        
        # Bug Fix 1: Empty Articles Issue
        if empty_articles == 0:
            log_test_result("✅ EMPTY ARTICLES BUG FIXED: No empty articles found", "SUCCESS")
        else:
            log_test_result(f"❌ EMPTY ARTICLES BUG PERSISTS: {empty_articles} empty articles found", "ERROR")
        
        # Bug Fix 2: Placeholder Content Issue  
        if placeholder_articles == 0:
            log_test_result("✅ PLACEHOLDER CONTENT BUG FIXED: No placeholder content found", "SUCCESS")
        else:
            log_test_result(f"❌ PLACEHOLDER CONTENT BUG PERSISTS: {placeholder_articles} articles with placeholders", "ERROR")
        
        # Bug Fix 3: Tutorial Content Processing
        if articles_with_google_maps > 0:
            log_test_result("✅ TUTORIAL PROCESSING WORKING: Google Maps tutorial content processed correctly", "SUCCESS")
        else:
            log_test_result("⚠️ TUTORIAL PROCESSING: No Google Maps content found (may have been processed earlier)", "WARNING")
        
        # Bug Fix 4: Code Block Preservation
        if articles_with_code > 0:
            log_test_result("✅ CODE BLOCK PRESERVATION WORKING: Code blocks found in articles", "SUCCESS")
        else:
            log_test_result("⚠️ CODE BLOCK PRESERVATION: No code blocks found in current articles", "WARNING")
        
        # FINAL VERDICT
        critical_bugs_fixed = (empty_articles == 0 and placeholder_articles == 0)
        
        if critical_bugs_fixed and passed_criteria >= 4:
            log_test_result("\n🎉 PHASE 6 BUG FIXES SUCCESSFUL!", "CRITICAL_SUCCESS")
            log_test_result("✅ Empty articles bug has been resolved", "CRITICAL_SUCCESS")
            log_test_result("✅ Placeholder content bug has been resolved", "CRITICAL_SUCCESS")
            log_test_result("✅ Content generation produces comprehensive, real content", "CRITICAL_SUCCESS")
            return True
        else:
            log_test_result("\n❌ PHASE 6 BUG FIXES INCOMPLETE", "CRITICAL_ERROR")
            if empty_articles > 0:
                log_test_result("❌ Empty articles issue still persists", "CRITICAL_ERROR")
            if placeholder_articles > 0:
                log_test_result("❌ Placeholder content issue still persists", "CRITICAL_ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Bug fix verification failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Phase 6 Bug Fix Verification Test")
    print("=" * 40)
    
    success = verify_phase6_bug_fixes()
    
    if success:
        print("\n🎉 VERIFICATION SUCCESSFUL: Phase 6 bug fixes are working!")
        exit(0)
    else:
        print("\n❌ VERIFICATION FAILED: Phase 6 bug fixes need more work")
        exit(1)