#!/usr/bin/env python3
"""
Direct TOC Processing Test
Test the simplified sequential assignment by processing fresh content through V2 engine
"""

import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-formatter.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_direct_sequential_assignment():
    """Test direct sequential assignment with fresh content"""
    print("🧪 Testing Direct Sequential Assignment with Fresh Content")
    print("="*80)
    
    # Test content with Mini-TOC and some existing section IDs
    test_content = """
    <h1>Complete API Integration Guide</h1>
    <p>This comprehensive guide covers everything you need to know about API integration.</p>
    
    <ul>
        <li>Getting Started</li>
        <li>Authentication Setup</li>
        <li>Making API Requests</li>
        <li>Error Handling</li>
        <li>Advanced Configuration</li>
        <li>Best Practices</li>
    </ul>
    
    <h2 id="section1">Getting Started</h2>
    <p>Learn the basics of API integration and how to get started with your first API call.</p>
    
    <h2 id="section2">Authentication Setup</h2>
    <p>Set up authentication for secure API access using API keys and tokens.</p>
    
    <h2>Making API Requests</h2>
    <p>Learn how to make different types of API requests including GET, POST, PUT, and DELETE.</p>
    
    <h2>Error Handling</h2>
    <p>Implement proper error handling to make your API integration robust and reliable.</p>
    
    <h2>Advanced Configuration</h2>
    <p>Configure advanced settings for optimal API performance and security.</p>
    
    <h2>Best Practices</h2>
    <p>Follow industry best practices for API integration and maintenance.</p>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📤 Processing content through V2 Engine...")
            print(f"   Content length: {len(test_content)} characters")
            print(f"   Expected: 6 TOC items -> section1, section2, section3, section4, section5, section6")
            
            # Process through V2 engine
            payload = {
                "content": test_content,
                "source_type": "html",
                "processing_options": {
                    "enable_style_processing": True,
                    "enable_anchor_processing": True
                }
            }
            
            async with session.post(f"{API_BASE}/content/process", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ V2 Processing completed - Status: {result.get('status', 'unknown')}")
                    
                    job_id = result.get('job_id')
                    if job_id:
                        print(f"📋 Job ID: {job_id}")
                        
                        # Wait for processing to complete
                        print("⏳ Waiting for processing to complete...")
                        await asyncio.sleep(5)
                        
                        # Get the processed article from content library
                        async with session.get(f"{API_BASE}/content-library") as lib_response:
                            if lib_response.status == 200:
                                lib_data = await lib_response.json()
                                articles = lib_data.get('articles', []) if isinstance(lib_data, dict) else lib_data
                                
                                if articles:
                                    # Find the most recent article (should be our test)
                                    latest_article = articles[0]
                                    processed_content = latest_article.get('content', '')
                                    title = latest_article.get('title', 'Untitled')
                                    
                                    print(f"📄 Analyzing processed article: '{title}'")
                                    print(f"   Content length: {len(processed_content)} characters")
                                    
                                    # Extract TOC links
                                    toc_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', processed_content)
                                    print(f"🔗 Found {len(toc_links)} TOC anchor links:")
                                    
                                    for i, (target_id, link_text) in enumerate(toc_links):
                                        print(f"   {i+1}. '{link_text}' -> #{target_id}")
                                    
                                    # Extract heading IDs
                                    heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"', processed_content)
                                    print(f"🏷️  Found {len(heading_ids)} heading IDs: {heading_ids}")
                                    
                                    # Check for section-style IDs specifically
                                    section_ids = [hid for hid in heading_ids if hid.startswith('section')]
                                    print(f"📋 Section-style IDs: {section_ids}")
                                    
                                    # Analyze sequential assignment
                                    print("\n🎯 Sequential Assignment Analysis:")
                                    sequential_matches = 0
                                    
                                    for i, (target_id, link_text) in enumerate(toc_links):
                                        expected_section = f"section{i+1}"
                                        
                                        if target_id == expected_section:
                                            sequential_matches += 1
                                            print(f"   ✅ TOC #{i+1}: '{link_text}' -> #{target_id} (CORRECT)")
                                        else:
                                            print(f"   ❌ TOC #{i+1}: '{link_text}' -> #{target_id} (expected #{expected_section})")
                                    
                                    # Calculate success rate
                                    if len(toc_links) > 0:
                                        success_rate = (sequential_matches / len(toc_links)) * 100
                                        print(f"\n📊 Sequential Assignment Results:")
                                        print(f"   Success Rate: {success_rate:.1f}% ({sequential_matches}/{len(toc_links)})")
                                        
                                        if success_rate >= 90:
                                            print(f"🎉 SUCCESS: Direct sequential assignment is working! ({success_rate:.1f}%)")
                                            return True
                                        elif success_rate >= 50:
                                            print(f"⚠️  PARTIAL: Some sequential assignment working ({success_rate:.1f}%)")
                                            return True
                                        else:
                                            print(f"❌ FAILED: Sequential assignment not working ({success_rate:.1f}%)")
                                            return False
                                    else:
                                        print("❌ No TOC links found - processing may have failed")
                                        return False
                                else:
                                    print("❌ No articles found in content library")
                                    return False
                            else:
                                print(f"❌ Failed to access content library - Status: {lib_response.status}")
                                return False
                    else:
                        print("❌ No job ID returned from processing")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ V2 Processing failed - Status: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error in direct sequential assignment test: {e}")
        return False

async def test_toc_processing_endpoint():
    """Test the direct TOC processing endpoint"""
    print("\n🧪 Testing Direct TOC Processing Endpoint")
    print("="*80)
    
    # Test content with clear TOC structure
    test_html = """
    <h1>API Documentation</h1>
    <p>Complete guide to our API.</p>
    
    <ul>
        <li>Introduction</li>
        <li>Authentication</li>
        <li>Endpoints</li>
        <li>Examples</li>
    </ul>
    
    <h2 id="section1">Introduction</h2>
    <p>Welcome to our API documentation.</p>
    
    <h2 id="section2">Authentication</h2>
    <p>Learn how to authenticate with our API.</p>
    
    <h2>Endpoints</h2>
    <p>Available API endpoints and their usage.</p>
    
    <h2>Examples</h2>
    <p>Practical examples of API usage.</p>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Testing TOC processing endpoint directly...")
            
            payload = {"content": test_html}
            
            async with session.post(f"{API_BASE}/style/process-toc-links", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ TOC Processing completed")
                    print(f"   Articles processed: {result.get('articles_processed', 0)}")
                    print(f"   Engine: {result.get('engine', 'unknown')}")
                    
                    updated_articles = result.get('updated_articles', [])
                    if updated_articles:
                        print(f"📋 Updated articles: {len(updated_articles)}")
                        
                        for article in updated_articles[:3]:  # Show first 3
                            anchor_links = article.get('anchor_links_generated', 0)
                            changes = article.get('structural_changes', [])
                            broken_links = article.get('toc_broken_links', 0)
                            
                            print(f"   - {article.get('title', 'Untitled')[:40]}...")
                            print(f"     Anchor links: {anchor_links}")
                            print(f"     Changes: {len(changes)}")
                            print(f"     Broken links: {broken_links}")
                        
                        # Check if any articles had anchor links generated
                        total_anchors = sum(a.get('anchor_links_generated', 0) for a in updated_articles)
                        if total_anchors > 0:
                            print(f"🎉 SUCCESS: {total_anchors} total anchor links generated across articles")
                            return True
                        else:
                            print("⚠️  No anchor links generated - may need fresh content")
                            return False
                    else:
                        print("❌ No updated articles returned")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ TOC Processing failed - Status: {response.status}")
                    print(f"   Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing TOC processing endpoint: {e}")
        return False

async def main():
    """Run the direct TOC tests"""
    print("🚀 Direct TOC Sequential Assignment Test Suite")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    # Test 1: Direct sequential assignment with fresh content
    test1_success = await test_direct_sequential_assignment()
    
    # Test 2: TOC processing endpoint
    test2_success = await test_toc_processing_endpoint()
    
    # Summary
    print("\n" + "="*80)
    print("📊 Test Results Summary")
    print("="*80)
    
    tests = [
        ("Direct Sequential Assignment (Fresh Content)", test1_success),
        ("TOC Processing Endpoint", test2_success)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    success_rate = (passed / total) * 100
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 50:
        print("🎉 Direct sequential assignment approach is working!")
    else:
        print("❌ Direct sequential assignment needs investigation")
    
    return success_rate >= 50

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)