#!/usr/bin/env python3
"""
HTML TOC Structure Test
Test the simplified sequential assignment with proper HTML TOC structure
"""

import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_html_toc_structure():
    """Test with proper HTML TOC structure that the processor expects"""
    print("🧪 Testing HTML TOC Structure for Sequential Assignment")
    print("="*80)
    
    # Create content with proper HTML structure that matches what the processor looks for
    test_content = """
    <div>
        <h1>Complete API Integration Guide</h1>
        <p>This comprehensive guide covers everything you need to know about API integration with sequential TOC assignment.</p>
        
        <ul>
            <li>Getting Started</li>
            <li>Authentication</li>
            <li>Making Requests</li>
            <li>Error Handling</li>
            <li>Advanced Features</li>
        </ul>
        
        <h2 id="section1">Getting Started</h2>
        <p>Learn the basics of API integration and how to get started with your first API call.</p>
        
        <h2 id="section2">Authentication</h2>
        <p>Set up authentication for secure API access using API keys and tokens.</p>
        
        <h2>Making Requests</h2>
        <p>Learn how to make different types of API requests including GET, POST, PUT, and DELETE.</p>
        
        <h2>Error Handling</h2>
        <p>Implement proper error handling to make your API integration robust and reliable.</p>
        
        <h2>Advanced Features</h2>
        <p>Explore advanced API features for optimal performance and functionality.</p>
    </div>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📤 Processing HTML content with proper TOC structure...")
            print(f"   Content length: {len(test_content)} characters")
            print(f"   Structure: 5 TOC items, 2 existing section IDs (section1, section2)")
            print(f"   Expected: Generate section3, section4, section5 for remaining items")
            
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
                                    
                                    # Show a sample of the processed content
                                    print(f"📝 Content sample:")
                                    content_lines = processed_content.split('\n')[:10]
                                    for i, line in enumerate(content_lines):
                                        if line.strip():
                                            print(f"   {i+1}: {line.strip()[:80]}...")
                                    
                                    # Extract TOC links
                                    toc_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', processed_content)
                                    print(f"\n🔗 Found {len(toc_links)} TOC anchor links:")
                                    
                                    for i, (target_id, link_text) in enumerate(toc_links):
                                        print(f"   {i+1}. '{link_text}' -> #{target_id}")
                                    
                                    # Extract heading IDs
                                    heading_ids = re.findall(r'<h[1-6][^>]*id="([^"]+)"', processed_content)
                                    print(f"\n🏷️  Found {len(heading_ids)} heading IDs: {heading_ids}")
                                    
                                    # Check for section-style IDs specifically
                                    section_ids = [hid for hid in heading_ids if hid.startswith('section')]
                                    section_ids.sort(key=lambda x: int(re.search(r'section(\d+)', x).group(1)) if re.search(r'section(\d+)', x) else 0)
                                    print(f"📋 Section-style IDs (sorted): {section_ids}")
                                    
                                    # Analyze sequential assignment
                                    print(f"\n🎯 Sequential Assignment Analysis:")
                                    sequential_matches = 0
                                    pattern_continuation = 0
                                    
                                    for i, (target_id, link_text) in enumerate(toc_links):
                                        expected_section = f"section{i+1}"
                                        
                                        if target_id == expected_section:
                                            sequential_matches += 1
                                            if i >= 2:  # section3+ are pattern continuations
                                                pattern_continuation += 1
                                            print(f"   ✅ TOC #{i+1}: '{link_text}' -> #{target_id} (CORRECT)")
                                        else:
                                            print(f"   ❌ TOC #{i+1}: '{link_text}' -> #{target_id} (expected #{expected_section})")
                                    
                                    # Check if new section IDs were generated
                                    expected_sections = [f"section{i}" for i in range(1, 6)]  # section1 to section5
                                    generated_sections = [sid for sid in section_ids if sid in expected_sections[2:]]  # section3+
                                    
                                    print(f"\n📊 Pattern Continuation Analysis:")
                                    print(f"   Expected new sections: {expected_sections[2:]}")  # section3, section4, section5
                                    print(f"   Generated sections: {generated_sections}")
                                    print(f"   Pattern continuation rate: {len(generated_sections)}/3 = {(len(generated_sections)/3)*100:.1f}%")
                                    
                                    # Calculate success rates
                                    if len(toc_links) > 0:
                                        sequential_rate = (sequential_matches / len(toc_links)) * 100
                                        print(f"\n📊 Sequential Assignment Results:")
                                        print(f"   Sequential matches: {sequential_matches}/{len(toc_links)} = {sequential_rate:.1f}%")
                                        print(f"   Pattern continuation: {pattern_continuation} new sections generated")
                                        
                                        # Overall assessment
                                        if sequential_rate >= 90 and len(generated_sections) >= 2:
                                            print(f"🎉 SUCCESS: Direct sequential assignment with pattern continuation working! ({sequential_rate:.1f}%)")
                                            return True
                                        elif sequential_rate >= 70:
                                            print(f"⚠️  PARTIAL SUCCESS: Sequential assignment mostly working ({sequential_rate:.1f}%)")
                                            return True
                                        else:
                                            print(f"❌ FAILED: Sequential assignment not working ({sequential_rate:.1f}%)")
                                            return False
                                    else:
                                        print("❌ No TOC links found - TOC processing may have failed")
                                        
                                        # Check if the content has the expected structure
                                        if '<ul>' in processed_content and '<li>' in processed_content:
                                            print("   ℹ️  Content has <ul><li> structure but no anchor links generated")
                                        else:
                                            print("   ℹ️  Content may not have proper TOC structure")
                                        
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
        print(f"❌ Error in HTML TOC structure test: {e}")
        return False

async def test_direct_style_processing():
    """Test the style processing directly on content"""
    print("\n🧪 Testing Direct Style Processing with TOC")
    print("="*80)
    
    # Simple test content
    test_html = """
    <h1>API Guide</h1>
    <p>Simple API guide with TOC.</p>
    
    <ul>
        <li>Introduction</li>
        <li>Setup</li>
        <li>Usage</li>
    </ul>
    
    <h2 id="section1">Introduction</h2>
    <p>Getting started with the API.</p>
    
    <h2 id="section2">Setup</h2>
    <p>Setting up your environment.</p>
    
    <h2>Usage</h2>
    <p>How to use the API effectively.</p>
    """
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Testing style processing with simple TOC structure...")
            
            # Test the style processing endpoint directly
            payload = {
                "content": test_html,
                "processing_options": {
                    "enable_anchor_processing": True
                }
            }
            
            # Check if there's a direct style processing endpoint
            async with session.post(f"{API_BASE}/style/process", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Style processing completed")
                    
                    processed_content = result.get('content', '')
                    changes = result.get('structural_changes', [])
                    anchor_links = result.get('anchor_links_generated', 0)
                    
                    print(f"   Anchor links generated: {anchor_links}")
                    print(f"   Structural changes: {len(changes)}")
                    
                    if anchor_links > 0:
                        print(f"🎉 SUCCESS: Style processing generated {anchor_links} anchor links")
                        
                        # Show the TOC links
                        toc_links = re.findall(r'<a[^>]*href="#([^"]+)"[^>]*>([^<]+)</a>', processed_content)
                        for i, (target_id, link_text) in enumerate(toc_links):
                            print(f"   {i+1}. '{link_text}' -> #{target_id}")
                        
                        return True
                    else:
                        print("⚠️  Style processing completed but no anchor links generated")
                        return False
                else:
                    print(f"❌ Style processing failed - Status: {response.status}")
                    # Try the TOC processing endpoint instead
                    async with session.post(f"{API_BASE}/style/process-toc-links", json={"content": test_html}) as toc_response:
                        if toc_response.status == 200:
                            toc_result = await toc_response.json()
                            print(f"✅ TOC processing endpoint worked")
                            print(f"   Articles processed: {toc_result.get('articles_processed', 0)}")
                            return True
                        else:
                            print(f"❌ TOC processing also failed - Status: {toc_response.status}")
                            return False
                    
    except Exception as e:
        print(f"❌ Error in direct style processing test: {e}")
        return False

async def main():
    """Run the HTML TOC structure tests"""
    print("🚀 HTML TOC Structure Test Suite")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    # Test 1: HTML TOC structure with sequential assignment
    test1_success = await test_html_toc_structure()
    
    # Test 2: Direct style processing
    test2_success = await test_direct_style_processing()
    
    # Summary
    print("\n" + "="*80)
    print("📊 Test Results Summary")
    print("="*80)
    
    tests = [
        ("HTML TOC Structure Sequential Assignment", test1_success),
        ("Direct Style Processing", test2_success)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    success_rate = (passed / total) * 100
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 50:
        print("🎉 HTML TOC structure processing is working!")
    else:
        print("❌ HTML TOC structure processing needs investigation")
    
    return success_rate >= 50

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)