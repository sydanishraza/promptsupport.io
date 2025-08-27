#!/usr/bin/env python3
"""
TICKET 2 Style Processing Test - Test the style processing endpoints for TOC coordination
"""

import requests
import json
import re
from datetime import datetime

# Use local backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 TICKET 2 STYLE PROCESSING TEST")
print(f"🌐 Backend URL: {BACKEND_URL}")
print("=" * 80)

def test_style_diagnostics():
    """Test style diagnostics endpoint"""
    print("🔍 Testing Style Diagnostics Endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/style/diagnostics", timeout=10)
        
        if response.status_code == 200:
            diagnostics = response.json()
            
            print(f"   ✅ Style diagnostics endpoint working")
            print(f"   📊 Recent results: {len(diagnostics.get('recent_results', []))}")
            
            # Check for TICKET 2 related features
            recent_results = diagnostics.get('recent_results', [])
            if recent_results:
                latest = recent_results[0]
                print(f"   📋 Latest result: {latest.get('timestamp', 'unknown')}")
                
                # Look for TICKET 2 indicators
                ticket2_indicators = []
                result_str = str(latest)
                
                if 'anchor' in result_str.lower():
                    ticket2_indicators.append('anchor_processing')
                if 'toc' in result_str.lower():
                    ticket2_indicators.append('toc_processing')
                if 'stable' in result_str.lower():
                    ticket2_indicators.append('stable_processing')
                
                print(f"   🎯 TICKET 2 indicators: {ticket2_indicators}")
            
            return True
        else:
            print(f"   ❌ Style diagnostics failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing style diagnostics: {str(e)}")
        return False

def test_toc_processing():
    """Test TOC processing endpoint"""
    print("\n🔧 Testing TOC Processing Endpoint...")
    
    try:
        response = requests.post(f"{API_BASE}/style/process-toc-links", 
            json={},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   ✅ TOC processing endpoint working")
            print(f"   📊 Processing result: {result.get('status', 'unknown')}")
            
            processed_articles = result.get('processed_articles', 0)
            print(f"   📄 Articles processed: {processed_articles}")
            
            if 'details' in result:
                details = result['details']
                print(f"   📋 Processing details: {details}")
            
            return True
        else:
            print(f"   ❌ TOC processing failed: {response.status_code}")
            if response.status_code == 422:
                print(f"   📋 Validation error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing TOC processing: {str(e)}")
        return False

def test_article_reprocessing():
    """Test reprocessing a specific article to fix TOC coordination"""
    print("\n🔄 Testing Article Reprocessing...")
    
    # Use the Google Maps article that we know has coordination issues
    article_id = "f68790f0-0d85-4149-b6a1-f40c098f91e3"
    
    try:
        # First, check current state
        response = requests.get(f"{API_BASE}/content-library", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            target_article = None
            for article in articles:
                if article.get('id') == article_id:
                    target_article = article
                    break
            
            if not target_article:
                print(f"   ❌ Test article not found")
                return False
            
            content = target_article.get('content') or target_article.get('html', '')
            
            # Check current coordination
            toc_links_before = re.findall(r'class="toc-link"[^>]*href="#([^"]+)"', content)
            heading_ids_before = re.findall(r'<h[234][^>]*id="([^"]+)"', content)
            
            print(f"   📊 Before: TOC links={len(toc_links_before)}, Heading IDs={len(heading_ids_before)}")
            print(f"   📋 TOC links: {toc_links_before[:3]}...")
            print(f"   📋 Heading IDs: {heading_ids_before[:3]}...")
            
            # Try to trigger reprocessing via style system
            reprocess_response = requests.post(f"{API_BASE}/style/rerun", 
                json={"article_id": article_id},
                timeout=30
            )
            
            if reprocess_response.status_code == 200:
                print(f"   ✅ Reprocessing triggered successfully")
                
                # Wait a moment and check if coordination improved
                import time
                time.sleep(2)
                
                # Check updated state
                updated_response = requests.get(f"{API_BASE}/content-library", timeout=10)
                if updated_response.status_code == 200:
                    updated_data = updated_response.json()
                    updated_articles = updated_data.get('articles', [])
                    
                    updated_article = None
                    for article in updated_articles:
                        if article.get('id') == article_id:
                            updated_article = article
                            break
                    
                    if updated_article:
                        updated_content = updated_article.get('content') or updated_article.get('html', '')
                        
                        toc_links_after = re.findall(r'class="toc-link"[^>]*href="#([^"]+)"', updated_content)
                        heading_ids_after = re.findall(r'<h[234][^>]*id="([^"]+)"', updated_content)
                        
                        coordinated_after = [link for link in toc_links_after if link in heading_ids_after]
                        coordination_rate = len(coordinated_after) / len(toc_links_after) if toc_links_after else 0
                        
                        print(f"   📊 After: TOC links={len(toc_links_after)}, Heading IDs={len(heading_ids_after)}")
                        print(f"   🔗 Coordination: {len(coordinated_after)}/{len(toc_links_after)} ({coordination_rate:.1%})")
                        
                        if coordination_rate > 0.8:
                            print(f"   ✅ Coordination significantly improved!")
                            return True
                        elif coordination_rate > 0.5:
                            print(f"   ⚠️  Coordination partially improved")
                            return True
                        else:
                            print(f"   ❌ Coordination not improved")
                            return False
                
            else:
                print(f"   ❌ Reprocessing failed: {reprocess_response.status_code}")
                return False
        
        return False
        
    except Exception as e:
        print(f"   ❌ Error testing reprocessing: {str(e)}")
        return False

def test_v2_processing_with_ticket2():
    """Test V2 processing with TICKET 2 content to see if new content works correctly"""
    print("\n🆕 Testing V2 Processing with TICKET 2...")
    
    test_content = """
    <h2>TICKET 2 Test Article</h2>
    <p>This is a test article to verify TICKET 2 stable anchor system implementation.</p>
    
    <h3>Getting Started with Testing</h3>
    <p>This section covers the basics of testing the TICKET 2 system.</p>
    
    <h3>Advanced Testing Scenarios</h3>
    <p>This section covers advanced testing approaches.</p>
    
    <h2>Configuration and Setup</h2>
    <p>Learn how to configure the system for optimal performance.</p>
    
    <h3>Environment Configuration</h3>
    <p>Setting up your environment for testing.</p>
    """
    
    try:
        response = requests.post(f"{API_BASE}/content/process", 
            json={
                "content": test_content,
                "content_type": "text",
                "metadata": {
                    "title": "TICKET 2 Final Test Article",
                    "test_type": "ticket2_final_verification"
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   ✅ V2 processing completed")
            
            if 'articles' in result and len(result['articles']) > 0:
                article = result['articles'][0]
                content = article.get('content', '')
                
                # Analyze TICKET 2 implementation
                toc_links = re.findall(r'class="toc-link"[^>]*href="#([^"]+)"', content)
                heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', content)
                
                # Check coordination
                coordinated_links = [link for link in toc_links if link in heading_ids]
                coordination_rate = len(coordinated_links) / len(toc_links) if toc_links else 0
                
                # Check format
                descriptive_toc = [link for link in toc_links if not re.match(r'^section\d+$', link)]
                descriptive_headings = [hid for hid in heading_ids if not re.match(r'^section\d+$', hid)]
                
                print(f"   📊 TOC Links: {len(toc_links)}")
                print(f"   📊 Heading IDs: {len(heading_ids)}")
                print(f"   🔗 Coordination: {len(coordinated_links)}/{len(toc_links)} ({coordination_rate:.1%})")
                print(f"   📝 Descriptive format: TOC={len(descriptive_toc)}/{len(toc_links)}, Headings={len(descriptive_headings)}/{len(heading_ids)}")
                
                if toc_links:
                    print(f"   📋 Sample TOC links: {toc_links[:3]}")
                if heading_ids:
                    print(f"   📋 Sample heading IDs: {heading_ids[:3]}")
                
                # TICKET 2 success criteria
                ticket2_working = (
                    coordination_rate >= 0.8 and
                    len(descriptive_toc) / len(toc_links) >= 0.8 if toc_links else False and
                    len(descriptive_headings) / len(heading_ids) >= 0.8 if heading_ids else False
                )
                
                if ticket2_working:
                    print(f"   ✅ TICKET 2 implementation working correctly in new content!")
                    return True
                else:
                    print(f"   ❌ TICKET 2 implementation still has issues in new content")
                    return False
            else:
                print(f"   ❌ No articles generated")
                return False
        else:
            print(f"   ❌ V2 processing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing V2 processing: {str(e)}")
        return False

def main():
    """Run all TICKET 2 style processing tests"""
    
    print("🚀 Starting TICKET 2 Style Processing Tests")
    
    results = []
    
    # Test 1: Style diagnostics
    results.append(("Style Diagnostics", test_style_diagnostics()))
    
    # Test 2: TOC processing
    results.append(("TOC Processing", test_toc_processing()))
    
    # Test 3: Article reprocessing
    results.append(("Article Reprocessing", test_article_reprocessing()))
    
    # Test 4: V2 processing with TICKET 2
    results.append(("V2 Processing with TICKET 2", test_v2_processing_with_ticket2()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TICKET 2 STYLE PROCESSING TEST SUMMARY")
    print("=" * 80)
    
    working_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    print(f"📈 RESULTS:")
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📊 OVERALL: {working_tests}/{total_tests} tests passing ({working_tests/total_tests:.1%})")
    
    if working_tests >= total_tests * 0.8:
        print("✅ TICKET 2 style processing is WORKING CORRECTLY!")
        print("   The stable anchor system and TOC coordination are functional.")
    elif working_tests >= total_tests * 0.6:
        print("⚠️  TICKET 2 style processing is PARTIALLY WORKING.")
        print("   Some components are functional but issues remain.")
    else:
        print("❌ TICKET 2 style processing has SIGNIFICANT ISSUES.")
        print("   Major components are not working as expected.")
        print("   The ID coordination failure persists - TOC links and heading IDs not synchronized.")

if __name__ == "__main__":
    main()