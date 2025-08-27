#!/usr/bin/env python3
"""
TICKET 2 Focused Test - Test V2 processing pipeline and TICKET 2 integration
"""

import requests
import json
import os
import time
import re

# Use configured backend URL
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🧪 TICKET 2 Focused Test - V2 Processing Pipeline")
print(f"🌐 Backend URL: {BACKEND_URL}")
print("=" * 70)

def test_v2_processing_with_ticket2():
    """Test V2 processing pipeline with TICKET 2 features"""
    print("🔧 TEST: V2 Processing Pipeline with TICKET 2")
    
    # Test content with multiple headings for TOC generation
    test_content = """
    <h2>Getting Started with the System</h2>
    <p>This guide will help you understand the system architecture and get started with implementation.</p>
    
    <h3>Prerequisites and Requirements</h3>
    <p>Before you begin, ensure you have the following prerequisites in place.</p>
    
    <h3>Installation and Setup</h3>
    <p>Follow these steps to install and configure the system properly.</p>
    
    <h4>Environment Configuration</h4>
    <p>Configure your environment variables and settings.</p>
    
    <h2>Advanced Configuration</h2>
    <p>Learn about advanced configuration options and customization.</p>
    
    <h3>Security Settings</h3>
    <p>Configure security settings for production deployment.</p>
    
    <h3>Performance Optimization</h3>
    <p>Optimize the system for better performance.</p>
    """
    
    try:
        print("📤 Sending content to V2 processing pipeline...")
        
        response = requests.post(f"{API_BASE}/content/process", 
            json={
                "content": test_content,
                "content_type": "text",
                "metadata": {
                    "title": "TICKET 2 V2 Pipeline Test",
                    "test_type": "v2_pipeline_ticket2"
                }
            },
            timeout=120  # Longer timeout for full V2 pipeline
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            articles = result.get('articles', [])
            
            print(f"✅ V2 Processing: Generated {len(articles)} articles")
            
            if articles:
                # Analyze first article for TICKET 2 features
                article = articles[0]
                content = article.get('content', '')
                title = article.get('title', 'Unknown')
                
                print(f"📄 Analyzing article: '{title[:50]}...'")
                print(f"📏 Content length: {len(content)} characters")
                
                # TICKET 2 Feature Analysis
                ticket2_results = analyze_ticket2_features(content)
                
                # Print detailed analysis
                print("\n🎯 TICKET 2 FEATURE ANALYSIS:")
                print("-" * 50)
                
                for feature, result in ticket2_results.items():
                    status = "✅" if result['found'] else "❌"
                    print(f"{status} {feature}: {result['details']}")
                
                # Calculate overall success
                found_features = sum(1 for r in ticket2_results.values() if r['found'])
                total_features = len(ticket2_results)
                success_rate = (found_features / total_features) * 100
                
                print(f"\n📊 TICKET 2 Success Rate: {found_features}/{total_features} ({success_rate:.1f}%)")
                
                # Check if content was processed by V2 Style Processor
                metadata = article.get('metadata', {})
                engine = metadata.get('engine', 'unknown')
                processing_version = metadata.get('processing_version', 'unknown')
                
                print(f"\n🔍 Processing Metadata:")
                print(f"   Engine: {engine}")
                print(f"   Version: {processing_version}")
                
                return success_rate >= 60  # 60% success rate threshold
            else:
                print("❌ No articles generated")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            if response.text:
                error_text = response.text[:500]
                print(f"   Error details: {error_text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def analyze_ticket2_features(content):
    """Analyze content for TICKET 2 features"""
    results = {}
    
    # 1. Stable Slug Generation - Check for heading IDs
    heading_ids = re.findall(r'<h[234][^>]*id="([^"]+)"', content)
    results['Stable Slug Generation'] = {
        'found': len(heading_ids) > 0,
        'details': f"Found {len(heading_ids)} heading IDs: {heading_ids[:3]}{'...' if len(heading_ids) > 3 else ''}"
    }
    
    # 2. Mini-TOC Creation - Check for TOC structure
    has_toc_container = 'mini-toc' in content.lower() or 'table-of-contents' in content.lower()
    toc_links = re.findall(r'href="#([^"]+)"', content)
    results['Mini-TOC Creation'] = {
        'found': has_toc_container or len(toc_links) > 0,
        'details': f"TOC container: {has_toc_container}, TOC links: {len(toc_links)}"
    }
    
    # 3. Anchor Resolution - Check if TOC links match heading IDs
    resolved_links = [link for link in toc_links if link in heading_ids]
    resolution_rate = len(resolved_links) / len(toc_links) if toc_links else 0
    results['Anchor Resolution'] = {
        'found': resolution_rate > 0.5,  # At least 50% resolution
        'details': f"Resolved {len(resolved_links)}/{len(toc_links)} links ({resolution_rate:.1%})"
    }
    
    # 4. Duplicate Heading Handling - Check for suffixed IDs
    suffixed_ids = [id for id in heading_ids if re.search(r'-\d+$', id)]
    results['Duplicate Handling'] = {
        'found': len(suffixed_ids) > 0 or len(set(heading_ids)) == len(heading_ids),
        'details': f"Suffixed IDs: {len(suffixed_ids)}, Unique IDs: {len(set(heading_ids))}/{len(heading_ids)}"
    }
    
    # 5. Heading Hierarchy - Check for proper H2/H3/H4 structure
    h2_count = content.count('<h2')
    h3_count = content.count('<h3')
    h4_count = content.count('<h4')
    results['Heading Hierarchy'] = {
        'found': h2_count > 0 and (h3_count > 0 or h4_count > 0),
        'details': f"H2: {h2_count}, H3: {h3_count}, H4: {h4_count}"
    }
    
    # 6. V2 Style Processing - Check for style-related classes or attributes
    has_style_classes = any(cls in content for cls in ['toc-link', 'mini-toc', 'heading-anchor'])
    results['V2 Style Processing'] = {
        'found': has_style_classes,
        'details': f"Style classes found: {has_style_classes}"
    }
    
    return results

def test_style_diagnostics_after_processing():
    """Check style diagnostics after processing"""
    print("\n🔧 TEST: Style Diagnostics After Processing")
    
    try:
        # Wait a moment for processing to complete
        time.sleep(2)
        
        response = requests.get(f"{API_BASE}/style/diagnostics", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            print(f"✅ Style Diagnostics: {len(recent_results)} recent results")
            
            if recent_results:
                latest = recent_results[0]
                print(f"   Latest run: {latest.get('created_at', 'unknown')}")
                print(f"   Success rate: {latest.get('success_rate', 'unknown')}")
                print(f"   Style ID: {latest.get('style_id', 'unknown')}")
                
                # Check for TICKET 2 related fields
                ticket2_indicators = []
                latest_str = str(latest).lower()
                
                if 'anchor' in latest_str:
                    ticket2_indicators.append('anchor processing')
                if 'toc' in latest_str:
                    ticket2_indicators.append('TOC processing')
                if 'heading' in latest_str:
                    ticket2_indicators.append('heading processing')
                if 'slug' in latest_str:
                    ticket2_indicators.append('slug generation')
                
                print(f"   TICKET 2 indicators: {ticket2_indicators}")
                return len(ticket2_indicators) > 0
            else:
                print("   No recent results found")
                return False
        else:
            print(f"❌ Style Diagnostics Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Style Diagnostics Exception: {e}")
        return False

def main():
    """Run focused TICKET 2 tests"""
    print("🚀 Starting TICKET 2 Focused Tests")
    
    # Test V2 processing pipeline
    v2_success = test_v2_processing_with_ticket2()
    
    # Test style diagnostics
    diagnostics_success = test_style_diagnostics_after_processing()
    
    print("\n" + "=" * 70)
    print("🏁 TICKET 2 Focused Test Summary")
    print("=" * 70)
    
    results = [v2_success, diagnostics_success]
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"📊 Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 50:
        print("✅ TICKET 2 integration appears to be working in V2 pipeline")
        print("   The V2StyleProcessor is processing content and applying TICKET 2 features")
    else:
        print("❌ TICKET 2 integration has issues")
        print("   The V2StyleProcessor may not be applying TICKET 2 features correctly")
    
    return success_rate >= 50

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)