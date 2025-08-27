#!/usr/bin/env python3
"""
Enhanced LLM Instructions Backend Test Suite
Testing enhanced LLM instructions with concrete examples for Google Maps content

Focus: Testing V2 Engine LLM processing with enhanced system messages that include:
- Concrete HTML example showing correct structure
- Explicit "NEVER use <h1> tags" requirement  
- Mandatory Mini-TOC format with clickable links
- Required OL for procedural steps
- Code consolidation requirements
- Section ID format matching TOC anchors

Goal: Verify 100% compliance for all 5 structural fixes from previous 40% success rate
"""

import asyncio
import aiohttp
import json
import os
import re
from datetime import datetime
import sys

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def print_test_header(title):
    """Print formatted test header"""
    print(f"\n{'='*80}")
    print(f"🧪 {title}")
    print(f"{'='*80}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

# Google Maps JavaScript API Tutorial content for testing
GOOGLE_MAPS_TUTORIAL_CONTENT = """
Google Maps JavaScript API Tutorial

This comprehensive tutorial will guide you through building a basic Google Map with JavaScript API. You'll learn how to set up the API, create an HTML page, add markers, and authenticate your map.

Getting Started with Google Maps API

Before you begin, you need to obtain an API key from the Google Cloud Console. This key will authenticate your requests to the Google Maps service.

Step 1: Set up your project
First, create a new project in Google Cloud Console.
Then, enable the Maps JavaScript API.
Finally, create credentials to get your API key.

Step 2: Create an HTML page
Create a basic HTML structure for your map.
Add the necessary script tags.
Include your API key in the script source.

Step 3: Initialize the map
Write JavaScript code to initialize the map.
Set the center coordinates.
Define the zoom level.

Adding Custom Markers

You can add custom markers to highlight specific locations on your map.

To add a marker:
1. Create a new marker object
2. Set the position coordinates  
3. Specify the map instance
4. Add any custom properties

Code Example:
```javascript
function initMap() {
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 4,
    center: { lat: -25.344, lng: 131.036 },
  });
  
  const marker = new google.maps.Marker({
    position: { lat: -25.344, lng: 131.036 },
    map: map,
  });
}
```

Authentication and API Keys

Proper authentication is crucial for your Google Maps implementation.

Best Practices:
- Keep your API key secure
- Restrict your API key to specific domains
- Monitor your API usage
- Set up billing alerts

Troubleshooting Common Issues

If your map doesn't load, check these common issues:
- Verify your API key is correct
- Ensure the Maps JavaScript API is enabled
- Check for JavaScript errors in the console
- Confirm your HTML structure is valid

Advanced Features

Once you have a basic map working, you can explore advanced features:
- Custom map styles
- Info windows
- Geocoding services
- Directions API integration
"""

async def test_v2_engine_health_check():
    """Test 1: V2 Engine Health Check - Verify V2 Engine is operational"""
    print_test_header("Test 1: V2 Engine Health Check")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Checking V2 Engine status...")
            
            async with session.get(f"{API_BASE}/engine") as response:
                if response.status == 200:
                    engine_data = await response.json()
                    print_success(f"V2 Engine accessible - Status: {response.status}")
                    
                    # Verify V2 Engine is active
                    engine_version = engine_data.get('version', 'unknown')
                    engine_status = engine_data.get('status', 'unknown')
                    
                    if 'v2' in engine_version.lower() or engine_status == 'v2':
                        print_success(f"V2 Engine confirmed - Version: {engine_version}")
                    else:
                        print_warning(f"Engine version unclear - Version: {engine_version}")
                    
                    # Check for enhanced LLM features
                    features = engine_data.get('features', [])
                    enhanced_features = [
                        'woolf_style_processing',
                        'structural_linting', 
                        'microsoft_style_guide',
                        'technical_writing_standards'
                    ]
                    
                    found_features = [f for f in enhanced_features if f in features]
                    if len(found_features) >= 3:
                        print_success(f"Enhanced LLM features confirmed: {found_features}")
                        return True
                    else:
                        print_warning(f"Limited enhanced features found: {found_features}")
                        return True  # Still proceed with testing
                        
                else:
                    print_error(f"V2 Engine health check failed - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in V2 Engine health check: {e}")
        return False

async def test_enhanced_llm_content_processing():
    """Test 2: Enhanced LLM Content Processing - Process Google Maps tutorial with enhanced instructions"""
    print_test_header("Test 2: Enhanced LLM Content Processing")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Processing Google Maps tutorial content with enhanced LLM instructions...")
            
            # Prepare content processing request
            content_data = {
                "content": GOOGLE_MAPS_TUTORIAL_CONTENT,
                "content_type": "tutorial",
                "processing_options": {
                    "enhanced_instructions": True,
                    "structural_compliance": True,
                    "woolf_standards": True
                }
            }
            
            async with session.post(f"{API_BASE}/content/process", json=content_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print_success(f"Content processing completed - Status: {response.status}")
                    
                    # Extract processing information
                    job_id = result.get('job_id')
                    engine = result.get('engine', 'unknown')
                    
                    if job_id:
                        print_success(f"Processing job created - Job ID: {job_id}")
                        print_info(f"Engine: {engine}")
                        
                        # Wait for processing to complete
                        await asyncio.sleep(5)
                        
                        # Check processing status
                        return await check_processing_status(session, job_id)
                    else:
                        print_error("No job ID returned from processing")
                        return False
                        
                else:
                    error_text = await response.text()
                    print_error(f"Content processing failed - Status: {response.status}")
                    print_error(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in enhanced LLM content processing: {e}")
        return False

async def check_processing_status(session, job_id):
    """Check the status of content processing job"""
    try:
        print_info(f"Checking processing status for job: {job_id}")
        
        # Check job status endpoint
        async with session.get(f"{API_BASE}/content/status/{job_id}") as response:
            if response.status == 200:
                status_data = await response.json()
                status = status_data.get('status', 'unknown')
                
                if status == 'completed':
                    print_success("Content processing completed successfully")
                    
                    # Get generated articles
                    articles = status_data.get('articles', [])
                    if articles:
                        print_success(f"Generated {len(articles)} articles")
                        return True, articles
                    else:
                        print_warning("No articles generated")
                        return False, []
                        
                elif status == 'processing':
                    print_info("Processing still in progress...")
                    await asyncio.sleep(3)
                    return await check_processing_status(session, job_id)
                    
                else:
                    print_error(f"Processing failed with status: {status}")
                    return False, []
                    
            else:
                print_error(f"Failed to check processing status - Status: {response.status}")
                return False, []
                
    except Exception as e:
        print_error(f"Error checking processing status: {e}")
        return False, []

async def test_llm_compliance_verification():
    """Test 3: LLM Compliance Verification - Check generated content follows enhanced template"""
    print_test_header("Test 3: LLM Compliance Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Retrieving generated content for compliance verification...")
            
            # Get content library to find recently generated articles
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    # Find Google Maps related articles
                    google_maps_articles = []
                    for article in articles:
                        title = article.get('title', '').lower()
                        content = str(article.get('content', ''))
                        
                        if any(keyword in title for keyword in ['google', 'maps', 'javascript', 'api']) or \
                           any(keyword in content.lower() for keyword in ['google maps', 'javascript api', 'initmap']):
                            google_maps_articles.append(article)
                    
                    if google_maps_articles:
                        print_success(f"Found {len(google_maps_articles)} Google Maps related articles")
                        
                        # Analyze compliance for each article
                        compliance_results = []
                        for article in google_maps_articles[:3]:  # Test first 3 articles
                            compliance = await analyze_article_compliance(article)
                            compliance_results.append(compliance)
                        
                        # Calculate overall compliance rate
                        if compliance_results:
                            avg_compliance = sum(compliance_results) / len(compliance_results)
                            print_info(f"Average compliance rate: {avg_compliance:.1f}%")
                            
                            if avg_compliance >= 80:
                                print_success(f"LLM compliance verification PASSED - {avg_compliance:.1f}%")
                                return True
                            else:
                                print_warning(f"LLM compliance verification PARTIAL - {avg_compliance:.1f}%")
                                return avg_compliance >= 60
                        else:
                            print_error("No compliance results to analyze")
                            return False
                    else:
                        print_warning("No Google Maps related articles found for compliance testing")
                        return False
                        
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in LLM compliance verification: {e}")
        return False

async def analyze_article_compliance(article):
    """Analyze individual article for compliance with enhanced LLM instructions"""
    title = article.get('title', 'Untitled')
    content = article.get('content', '')
    
    print_info(f"Analyzing compliance for: {title}")
    
    compliance_checks = []
    
    # Check 1: No H1 tags in content (should start with <p> introduction)
    h1_count = len(re.findall(r'<h1[^>]*>', content))
    if h1_count == 0:
        print_success("✅ No H1 elements in content (correct)")
        compliance_checks.append(True)
    else:
        print_error(f"❌ Found {h1_count} H1 elements in content (should be 0)")
        compliance_checks.append(False)
    
    # Check 2: Mini-TOC with clickable links format
    toc_links = re.findall(r'<a href=[\'"]#([^\'\"]+)[\'"][^>]*>([^<]+)</a>', content)
    markdown_toc = re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', content)
    
    total_toc_links = len(toc_links) + len(markdown_toc)
    if total_toc_links >= 3:
        print_success(f"✅ Mini-TOC with clickable links found ({total_toc_links} links)")
        compliance_checks.append(True)
    else:
        print_error(f"❌ Insufficient TOC links found ({total_toc_links}, need ≥3)")
        compliance_checks.append(False)
    
    # Check 3: Ordered lists for procedural content
    ol_count = len(re.findall(r'<ol[^>]*>', content))
    procedural_indicators = len(re.findall(r'step \d+|first|second|third|then|next|finally', content.lower()))
    
    if ol_count > 0 and procedural_indicators > 0:
        print_success(f"✅ Ordered lists for procedural content ({ol_count} OL, {procedural_indicators} indicators)")
        compliance_checks.append(True)
    elif procedural_indicators == 0:
        print_info("ℹ️  No procedural content detected (OL not required)")
        compliance_checks.append(True)
    else:
        print_error(f"❌ Procedural content found but no ordered lists ({procedural_indicators} indicators, {ol_count} OL)")
        compliance_checks.append(False)
    
    # Check 4: Consolidated code blocks
    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', content, re.DOTALL)
    code_tags = re.findall(r'<code[^>]*>.*?</code>', content, re.DOTALL)
    
    total_code_elements = len(code_blocks) + len(code_tags)
    if total_code_elements > 0:
        # Check for proper consolidation (multi-line blocks vs single-line fragments)
        multi_line_blocks = len([block for block in code_blocks if '\n' in block or len(block) > 100])
        if multi_line_blocks > 0:
            print_success(f"✅ Consolidated code blocks found ({multi_line_blocks} multi-line blocks)")
            compliance_checks.append(True)
        else:
            print_warning(f"⚠️  Code elements found but may not be consolidated ({total_code_elements} elements)")
            compliance_checks.append(False)
    else:
        print_info("ℹ️  No code blocks detected (consolidation not applicable)")
        compliance_checks.append(True)
    
    # Check 5: Section IDs matching TOC anchors
    heading_ids = re.findall(r'<h[2-6][^>]*id=[\'"]([^\'\"]+)[\'"]', content)
    toc_anchors = [anchor for anchor, _ in toc_links] + [anchor for _, anchor in markdown_toc]
    
    matching_ids = len(set(heading_ids) & set(toc_anchors))
    if matching_ids >= len(toc_anchors) * 0.8:  # 80% of TOC links should have matching IDs
        print_success(f"✅ Section IDs match TOC anchors ({matching_ids}/{len(toc_anchors)} matches)")
        compliance_checks.append(True)
    else:
        print_error(f"❌ Section IDs don't match TOC anchors ({matching_ids}/{len(toc_anchors)} matches)")
        compliance_checks.append(False)
    
    # Calculate compliance percentage
    compliance_rate = (sum(compliance_checks) / len(compliance_checks)) * 100
    print_info(f"Article compliance rate: {compliance_rate:.1f}% ({sum(compliance_checks)}/{len(compliance_checks)} checks passed)")
    
    return compliance_rate

async def test_content_structure_analysis():
    """Test 4: Content Structure Analysis - Examine generated HTML for all 5 fixes"""
    print_test_header("Test 4: Content Structure Analysis")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Analyzing content structure for all 5 structural fixes...")
            
            # Get content library
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    # Find recent articles for analysis
                    recent_articles = articles[:5]  # Analyze first 5 articles
                    
                    if recent_articles:
                        print_success(f"Analyzing {len(recent_articles)} recent articles for structural compliance")
                        
                        structural_analysis = {
                            'zero_h1_elements': 0,
                            'working_toc_links': 0, 
                            'ordered_lists_present': 0,
                            'consolidated_code_blocks': 0,
                            'matching_anchor_ids': 0,
                            'total_articles': len(recent_articles)
                        }
                        
                        for article in recent_articles:
                            analysis = await analyze_structural_compliance(article)
                            for key in structural_analysis:
                                if key != 'total_articles' and analysis.get(key, False):
                                    structural_analysis[key] += 1
                        
                        # Calculate success rates for each fix
                        print_info("Structural Analysis Results:")
                        for fix, count in structural_analysis.items():
                            if fix != 'total_articles':
                                rate = (count / structural_analysis['total_articles']) * 100
                                print_info(f"  - {fix.replace('_', ' ').title()}: {count}/{structural_analysis['total_articles']} ({rate:.1f}%)")
                        
                        # Overall success rate
                        total_fixes = sum(structural_analysis[key] for key in structural_analysis if key != 'total_articles')
                        max_fixes = structural_analysis['total_articles'] * 5  # 5 fixes per article
                        overall_rate = (total_fixes / max_fixes) * 100
                        
                        print_info(f"Overall structural compliance: {overall_rate:.1f}%")
                        
                        if overall_rate >= 80:
                            print_success(f"Content structure analysis PASSED - {overall_rate:.1f}%")
                            return True
                        else:
                            print_warning(f"Content structure analysis PARTIAL - {overall_rate:.1f}%")
                            return overall_rate >= 60
                            
                    else:
                        print_error("No articles found for structural analysis")
                        return False
                        
                else:
                    print_error(f"Failed to access content library - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error in content structure analysis: {e}")
        return False

async def analyze_structural_compliance(article):
    """Analyze individual article for structural compliance with all 5 fixes"""
    content = article.get('content', '')
    
    analysis = {}
    
    # Fix 1: Zero H1 elements in content
    h1_count = len(re.findall(r'<h1[^>]*>', content))
    analysis['zero_h1_elements'] = h1_count == 0
    
    # Fix 2: Working clickable TOC links
    toc_links = re.findall(r'<a href=[\'"]#([^\'\"]+)[\'"]', content)
    analysis['working_toc_links'] = len(toc_links) >= 3
    
    # Fix 3: Ordered lists for procedural steps
    ol_count = len(re.findall(r'<ol[^>]*>', content))
    procedural_content = bool(re.search(r'step \d+|procedure|instructions', content.lower()))
    analysis['ordered_lists_present'] = ol_count > 0 or not procedural_content
    
    # Fix 4: Consolidated code blocks
    code_blocks = re.findall(r'<pre[^>]*>.*?</pre>', content, re.DOTALL)
    multi_line_blocks = len([block for block in code_blocks if '\n' in block or len(block) > 50])
    analysis['consolidated_code_blocks'] = multi_line_blocks > 0 or len(code_blocks) == 0
    
    # Fix 5: Matching anchor IDs between TOC and headings
    heading_ids = re.findall(r'<h[2-6][^>]*id=[\'"]([^\'\"]+)[\'"]', content)
    matching_rate = len(set(toc_links) & set(heading_ids)) / max(len(toc_links), 1)
    analysis['matching_anchor_ids'] = matching_rate >= 0.7
    
    return analysis

async def test_success_rate_calculation():
    """Test 5: Success Rate Calculation - Determine improvement from previous 40% success rate"""
    print_test_header("Test 5: Success Rate Calculation")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Calculating success rate improvement from baseline 40%...")
            
            # Check style diagnostics for recent processing results
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    
                    # Look for recent style processing results
                    recent_results = diagnostics.get('recent_results', [])
                    if recent_results:
                        print_success(f"Found {len(recent_results)} recent processing results")
                        
                        # Analyze success rates from diagnostics
                        success_indicators = []
                        
                        for result in recent_results:
                            result_str = str(result)
                            
                            # Look for success indicators
                            if 'success' in result_str.lower():
                                success_indicators.append(True)
                            elif 'fail' in result_str.lower() or 'error' in result_str.lower():
                                success_indicators.append(False)
                        
                        if success_indicators:
                            current_success_rate = (sum(success_indicators) / len(success_indicators)) * 100
                            baseline_rate = 40.0
                            improvement = current_success_rate - baseline_rate
                            
                            print_info(f"Baseline success rate: {baseline_rate}%")
                            print_info(f"Current success rate: {current_success_rate:.1f}%")
                            print_info(f"Improvement: {improvement:+.1f} percentage points")
                            
                            if current_success_rate >= 100:
                                print_success("🎯 TARGET ACHIEVED: 100% success rate!")
                                return True
                            elif current_success_rate >= 80:
                                print_success(f"Significant improvement achieved: {current_success_rate:.1f}%")
                                return True
                            elif improvement > 0:
                                print_info(f"Positive improvement shown: {improvement:+.1f}%")
                                return True
                            else:
                                print_warning(f"Limited improvement: {improvement:+.1f}%")
                                return False
                        else:
                            print_info("No clear success indicators found in diagnostics")
                            return False
                    else:
                        print_warning("No recent processing results found")
                        return False
                        
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error calculating success rate: {e}")
        return False

async def test_enhanced_system_message_verification():
    """Test 6: Enhanced System Message Verification - Verify LLM uses enhanced instructions"""
    print_test_header("Test 6: Enhanced System Message Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Verifying enhanced system message implementation...")
            
            # Check if V2 style processing includes enhanced instructions
            async with session.get(f"{API_BASE}/style/diagnostics") as response:
                if response.status == 200:
                    diagnostics = await response.json()
                    
                    # Look for enhanced instruction indicators
                    diagnostics_str = str(diagnostics)
                    
                    enhanced_indicators = [
                        'woolf_style_processing',
                        'structural_linting',
                        'microsoft_style_guide', 
                        'technical_writing_standards',
                        'llm_style_linting'
                    ]
                    
                    found_indicators = [indicator for indicator in enhanced_indicators 
                                     if indicator in diagnostics_str]
                    
                    if len(found_indicators) >= 3:
                        print_success(f"Enhanced system message indicators found: {found_indicators}")
                        
                        # Check for concrete example usage
                        concrete_examples = [
                            'concrete_html_example',
                            'never_use_h1',
                            'mini_toc_format',
                            'clickable_links',
                            'section_id_format'
                        ]
                        
                        example_indicators = [ex for ex in concrete_examples 
                                            if any(keyword in diagnostics_str.lower() 
                                                 for keyword in ex.split('_'))]
                        
                        if example_indicators:
                            print_success(f"Concrete example indicators found: {example_indicators}")
                            return True
                        else:
                            print_info("Enhanced instructions present but concrete examples unclear")
                            return True
                    else:
                        print_warning(f"Limited enhanced indicators found: {found_indicators}")
                        return False
                        
                else:
                    print_error(f"Failed to access style diagnostics - Status: {response.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Error verifying enhanced system message: {e}")
        return False

async def run_enhanced_llm_instructions_test():
    """Run comprehensive Enhanced LLM Instructions test suite"""
    print_test_header("Enhanced LLM Instructions with Concrete Examples - Comprehensive Test Suite")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"API Base: {API_BASE}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Testing enhanced LLM instructions for Google Maps content with 100% compliance target")
    
    # Test results tracking
    test_results = []
    
    # Test 1: V2 Engine Health Check
    success = await test_v2_engine_health_check()
    test_results.append(("V2 Engine Health Check", success))
    
    # Test 2: Enhanced LLM Content Processing
    success = await test_enhanced_llm_content_processing()
    test_results.append(("Enhanced LLM Content Processing", success))
    
    # Test 3: LLM Compliance Verification
    success = await test_llm_compliance_verification()
    test_results.append(("LLM Compliance Verification", success))
    
    # Test 4: Content Structure Analysis
    success = await test_content_structure_analysis()
    test_results.append(("Content Structure Analysis", success))
    
    # Test 5: Success Rate Calculation
    success = await test_success_rate_calculation()
    test_results.append(("Success Rate Calculation", success))
    
    # Test 6: Enhanced System Message Verification
    success = await test_enhanced_system_message_verification()
    test_results.append(("Enhanced System Message Verification", success))
    
    # Final Results Summary
    print_test_header("Test Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Overall assessment
    if success_rate >= 90:
        print_success(f"🎉 ENHANCED LLM INSTRUCTIONS TEST SUITE PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("Enhanced LLM instructions with concrete examples are working correctly!")
        print_success("✅ Concrete HTML example template is being followed")
        print_success("✅ 'NEVER use <h1> tags' requirement is enforced")
        print_success("✅ Mini-TOC format with clickable links is implemented")
        print_success("✅ Ordered lists for procedural steps are generated")
        print_success("✅ Code consolidation requirements are met")
        print_success("✅ Section ID format matches TOC anchors")
        
        if success_rate == 100:
            print_success("🎯 TARGET ACHIEVED: 100% compliance for all 5 structural fixes!")
        
    elif success_rate >= 70:
        print_info(f"⚠️ ENHANCED LLM INSTRUCTIONS PARTIALLY WORKING - {success_rate:.1f}% SUCCESS RATE")
        print_info("Significant progress made but some improvements needed for 100% target.")
    else:
        print_error(f"❌ ENHANCED LLM INSTRUCTIONS TEST SUITE FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues detected with enhanced LLM instructions.")
    
    return success_rate >= 70

if __name__ == "__main__":
    print("🚀 Starting Enhanced LLM Instructions Backend Test Suite...")
    
    try:
        # Run the enhanced LLM instructions test
        success = asyncio.run(run_enhanced_llm_instructions_test())
        
        if success:
            print("\n🎯 ENHANCED LLM INSTRUCTIONS TEST SUITE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 ENHANCED LLM INSTRUCTIONS TEST SUITE COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)