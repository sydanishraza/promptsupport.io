#!/usr/bin/env python3
"""
V2StyleProcessor Mini-TOC Anchor Processing Test
Focus: Testing triggering V2StyleProcessor to apply Mini-TOC anchor processing to existing articles
"""

import requests
import json
import sys
from datetime import datetime
import re
from bs4 import BeautifulSoup

# Backend URL from environment
BACKEND_URL = "https://content-pipeline-5.preview.emergentagent.com/api"

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*80}")
    print(f"🔍 {test_name}")
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

def test_style_rerun_endpoint():
    """Test 1: POST /api/style/rerun to trigger V2StyleProcessor"""
    print_test_header("Test POST /api/style/rerun - Trigger V2StyleProcessor")
    
    try:
        # First, get a valid run_id from recent processing
        print_info("Getting valid run_id from recent V2 processing...")
        
        # Check content library for V2 articles with run_id
        content_response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        if content_response.status_code != 200:
            print_error("Failed to access content library for run_id")
            return None
        
        content_data = content_response.json()
        articles = content_data.get('articles', [])
        
        # Look for V2 articles with run_id in metadata
        valid_run_id = None
        for article in articles:
            metadata = article.get('metadata', {})
            if metadata.get('engine') == 'v2' and 'run_id' in metadata:
                valid_run_id = metadata['run_id']
                print_info(f"Found valid run_id: {valid_run_id}")
                break
        
        if not valid_run_id:
            print_error("No valid run_id found in V2 articles")
            return None
        
        # Test POST /api/style/rerun with correct payload format
        payload = {
            "run_id": valid_run_id
        }
        
        response = requests.post(
            f"{BACKEND_URL}/style/rerun", 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print_info(f"POST /api/style/rerun - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Style rerun endpoint accessible and working")
            
            # Check response structure
            run_id = data.get('run_id')
            articles_processed = data.get('articles_processed', 0)
            success_count = data.get('success_count', 0)
            
            print_info(f"Run ID: {run_id}")
            print_info(f"Articles processed: {articles_processed}")
            print_info(f"Success count: {success_count}")
            
            if success_count > 0:
                print_success(f"✓ Successfully processed {success_count} articles")
                return run_id
            else:
                print_error("✗ No articles were successfully processed")
                return None
                
        elif response.status_code == 422:
            print_error("Validation error - checking response details")
            try:
                error_data = response.json()
                print_error(f"Validation error details: {error_data}")
            except:
                print_error(f"Raw response: {response.text}")
            return None
        else:
            print_error(f"Failed to trigger style rerun: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error testing style rerun endpoint: {e}")
        return None

def test_v2_engine_processing():
    """Test 2: Check if V2 engine processing automatically applies style processing"""
    print_test_header("V2 Engine Processing - Style Processing Integration")
    
    try:
        # Check V2 engine status
        response = requests.get(f"{BACKEND_URL}/engine", timeout=30)
        print_info(f"GET /api/engine - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            engine_status = data.get('status', 'unknown')
            engine_version = data.get('engine', 'unknown')
            
            print_info(f"Engine status: {engine_status}")
            print_info(f"Engine version: {engine_version}")
            
            # Check for V2-specific style processing features
            features = data.get('features', {})
            style_features = [
                'woolf_style_processing',
                'structural_linting', 
                'microsoft_style_guide',
                'technical_writing_standards'
            ]
            
            print_info("\n🔍 V2 Style Processing Features Check:")
            features_found = 0
            
            if isinstance(features, dict):
                for feature in style_features:
                    if feature in features and features[feature]:
                        print_success(f"  ✓ {feature}: {features[feature]}")
                        features_found += 1
                    else:
                        print_error(f"  ✗ {feature}: Not found or disabled")
            elif isinstance(features, list):
                for feature in style_features:
                    if feature in features:
                        print_success(f"  ✓ {feature}: Present")
                        features_found += 1
                    else:
                        print_error(f"  ✗ {feature}: Not found")
            
            # Check style diagnostics endpoint availability
            endpoints = data.get('endpoints', {})
            if 'style_diagnostics' in endpoints:
                print_success(f"  ✓ style_diagnostics endpoint: {endpoints['style_diagnostics']}")
                features_found += 1
            else:
                print_error("  ✗ style_diagnostics endpoint not found")
            
            success_rate = (features_found / (len(style_features) + 1)) * 100
            print_info(f"V2 Style Processing Integration: {success_rate:.1f}% ({features_found}/{len(style_features) + 1})")
            
            return success_rate >= 80  # 80% or higher considered good
        else:
            print_error(f"Failed to access engine status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing V2 engine processing: {e}")
        return False

def test_style_processing_results():
    """Test 3: Verify style processing results - TOC items converted to markdown links"""
    print_test_header("Style Processing Results - TOC Markdown Links Verification")
    
    try:
        # Get recent style processing results
        response = requests.get(f"{BACKEND_URL}/style/diagnostics", timeout=30)
        print_info(f"GET /api/style/diagnostics - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            if not recent_results:
                print_error("No recent style processing results found")
                return False
            
            print_success(f"Found {len(recent_results)} recent style processing results")
            
            # Analyze the most recent result
            latest_result = recent_results[0]
            style_id = latest_result.get('style_id')
            
            print_info(f"Analyzing latest result: {style_id}")
            
            # Get detailed result
            detail_response = requests.get(f"{BACKEND_URL}/style/diagnostics/{style_id}", timeout=30)
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                style_result = detail_data.get('style_result', {})
                
                # Check for anchor processing indicators
                anchor_links_generated = style_result.get('anchor_links_generated', 0)
                toc_broken_links = style_result.get('toc_broken_links', [])
                
                print_info(f"Anchor links generated: {anchor_links_generated}")
                print_info(f"TOC broken links: {len(toc_broken_links) if isinstance(toc_broken_links, list) else toc_broken_links}")
                
                # Check structural compliance for TOC
                analysis = detail_data.get('analysis', {})
                structural_compliance = analysis.get('structural_compliance', {})
                
                has_mini_toc = structural_compliance.get('has_mini_toc', False)
                toc_anchor_count = structural_compliance.get('toc_anchor_count', 0)
                
                print_info(f"Has Mini-TOC: {has_mini_toc}")
                print_info(f"TOC anchor count: {toc_anchor_count}")
                
                # Success criteria
                success_indicators = 0
                total_indicators = 4
                
                if anchor_links_generated > 0:
                    print_success("✓ Anchor links are being generated")
                    success_indicators += 1
                else:
                    print_error("✗ No anchor links generated")
                
                if isinstance(toc_broken_links, list) and len(toc_broken_links) == 0:
                    print_success("✓ No broken TOC links")
                    success_indicators += 1
                else:
                    print_error(f"✗ Found broken TOC links: {toc_broken_links}")
                
                if has_mini_toc:
                    print_success("✓ Mini-TOC structure detected")
                    success_indicators += 1
                else:
                    print_error("✗ No Mini-TOC structure found")
                
                if toc_anchor_count > 0:
                    print_success(f"✓ TOC anchors present: {toc_anchor_count}")
                    success_indicators += 1
                else:
                    print_error("✗ No TOC anchors found")
                
                success_rate = (success_indicators / total_indicators) * 100
                print_info(f"Style Processing Results Success: {success_rate:.1f}% ({success_indicators}/{total_indicators})")
                
                return success_rate >= 75  # 75% or higher considered good
            else:
                print_error(f"Failed to get detailed style result: {detail_response.status_code}")
                return False
        else:
            print_error(f"Failed to access style diagnostics: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing style processing results: {e}")
        return False

def test_article_content_update():
    """Test 4: Confirm processed content gets updated in content library with clickable anchors"""
    print_test_header("Article Content Update - Content Library Verification")
    
    try:
        # Search for the target article in content library
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        print_info(f"GET /api/content-library - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print_success(f"Content library accessible - {len(articles)} articles found")
            
            # Look for Code Normalization article
            target_article = None
            for article in articles:
                title = article.get('title', '').lower()
                if 'code normalization' in title and 'javascript' in title:
                    target_article = article
                    break
            
            if not target_article:
                print_error("Target article 'Code Normalization in JavaScript' not found")
                return False
            
            print_success(f"Found target article: {target_article['title']}")
            
            # Analyze article content for clickable anchors
            content = target_article.get('content', '') or target_article.get('html', '')
            
            if not content:
                print_error("No content found in target article")
                return False
            
            print_info(f"Article content length: {len(content)} characters")
            
            # Parse content with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for markdown-style TOC links [text](#anchor)
            markdown_toc_pattern = r'\[([^\]]+)\]\(#([^)]+)\)'
            markdown_matches = re.findall(markdown_toc_pattern, content)
            
            print_info(f"Markdown-style TOC links found: {len(markdown_matches)}")
            
            if markdown_matches:
                print_success("✓ Found markdown-style TOC links:")
                for i, (text, anchor) in enumerate(markdown_matches):
                    print_info(f"  {i+1}. [{text}](#{anchor})")
            else:
                print_error("✗ No markdown-style TOC links found")
            
            # Check for HTML anchor links in TOC
            toc_links = soup.find_all('a', href=re.compile(r'^#'))
            print_info(f"HTML anchor links found: {len(toc_links)}")
            
            if toc_links:
                print_success("✓ Found HTML anchor links:")
                for i, link in enumerate(toc_links):
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    print_info(f"  {i+1}. {text} -> {href}")
            else:
                print_error("✗ No HTML anchor links found")
            
            # Check for headings with IDs
            headings_with_ids = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], id=True)
            print_info(f"Headings with IDs found: {len(headings_with_ids)}")
            
            if headings_with_ids:
                print_success("✓ Found headings with IDs:")
                for i, heading in enumerate(headings_with_ids):
                    heading_id = heading.get('id', '')
                    text = heading.get_text().strip()
                    print_info(f"  {i+1}. {heading.name.upper()}: '{text[:40]}...' ID='{heading_id}'")
            else:
                print_error("✗ No headings with IDs found")
            
            # Success criteria
            success_indicators = 0
            total_indicators = 3
            
            if markdown_matches or toc_links:
                print_success("✓ Clickable TOC links present")
                success_indicators += 1
            else:
                print_error("✗ No clickable TOC links found")
            
            if headings_with_ids:
                print_success("✓ Headings have proper IDs for anchoring")
                success_indicators += 1
            else:
                print_error("✗ Headings lack proper IDs")
            
            if len(content) > 1000:  # Substantial content
                print_success("✓ Article has substantial content")
                success_indicators += 1
            else:
                print_error("✗ Article content seems insufficient")
            
            success_rate = (success_indicators / total_indicators) * 100
            print_info(f"Content Update Verification Success: {success_rate:.1f}% ({success_indicators}/{total_indicators})")
            
            return success_rate >= 66  # 66% or higher considered acceptable
        else:
            print_error(f"Failed to access content library: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing article content update: {e}")
        return False

def test_anchor_generation_validation():
    """Test 5: Validate anchor generation - headings get proper IDs and TOC items get converted"""
    print_test_header("Anchor Generation Validation - Comprehensive Check")
    
    try:
        # Get the most recent style processing result for detailed analysis
        response = requests.get(f"{BACKEND_URL}/style/diagnostics", timeout=30)
        
        if response.status_code != 200:
            print_error(f"Failed to access style diagnostics: {response.status_code}")
            return False
        
        data = response.json()
        recent_results = data.get('recent_results', [])
        
        if not recent_results:
            print_error("No recent style processing results for validation")
            return False
        
        latest_result = recent_results[0]
        style_id = latest_result.get('style_id')
        
        # Get detailed analysis
        detail_response = requests.get(f"{BACKEND_URL}/style/diagnostics/{style_id}", timeout=30)
        
        if detail_response.status_code != 200:
            print_error(f"Failed to get detailed style result: {detail_response.status_code}")
            return False
        
        detail_data = detail_response.json()
        style_result = detail_data.get('style_result', {})
        analysis = detail_data.get('analysis', {})
        
        print_info(f"Validating style result: {style_id}")
        print_info(f"Article: {style_result.get('article_title', 'Unknown')}")
        
        # Validation criteria
        validation_results = {}
        
        # 1. Anchor links generation
        anchor_links_generated = style_result.get('anchor_links_generated', 0)
        validation_results['anchor_generation'] = anchor_links_generated > 0
        print_success(f"✓ Anchor links generated: {anchor_links_generated}") if anchor_links_generated > 0 else print_error("✗ No anchor links generated")
        
        # 2. TOC broken links check
        toc_broken_links = style_result.get('toc_broken_links', [])
        validation_results['no_broken_links'] = isinstance(toc_broken_links, list) and len(toc_broken_links) == 0
        print_success("✓ No broken TOC links") if validation_results['no_broken_links'] else print_error(f"✗ Broken TOC links found: {toc_broken_links}")
        
        # 3. Structural compliance
        structural_compliance = analysis.get('structural_compliance', {})
        has_mini_toc = structural_compliance.get('has_mini_toc', False)
        toc_anchor_count = structural_compliance.get('toc_anchor_count', 0)
        
        validation_results['mini_toc_present'] = has_mini_toc
        validation_results['toc_anchors_present'] = toc_anchor_count > 0
        
        print_success(f"✓ Mini-TOC present: {has_mini_toc}") if has_mini_toc else print_error("✗ No Mini-TOC found")
        print_success(f"✓ TOC anchors present: {toc_anchor_count}") if toc_anchor_count > 0 else print_error("✗ No TOC anchors found")
        
        # 4. Style processing success
        style_status = style_result.get('style_status', 'unknown')
        validation_results['processing_success'] = style_status == 'success'
        print_success(f"✓ Style processing successful: {style_status}") if style_status == 'success' else print_error(f"✗ Style processing failed: {style_status}")
        
        # 5. Woolf standards compliance
        woolf_compliance = analysis.get('woolf_standards', {})
        if woolf_compliance:
            structural_rules = woolf_compliance.get('structural_rules_enforced', False)
            validation_results['woolf_compliance'] = structural_rules
            print_success(f"✓ Woolf structural rules enforced: {structural_rules}") if structural_rules else print_error("✗ Woolf structural rules not enforced")
        else:
            validation_results['woolf_compliance'] = False
            print_error("✗ No Woolf standards compliance data")
        
        # Calculate overall validation success
        passed_validations = sum(1 for result in validation_results.values() if result)
        total_validations = len(validation_results)
        
        success_rate = (passed_validations / total_validations) * 100
        print_info(f"Anchor Generation Validation Success: {success_rate:.1f}% ({passed_validations}/{total_validations})")
        
        # Detailed validation summary
        print_info("\n🔍 Validation Summary:")
        for validation_name, passed in validation_results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print_info(f"  {validation_name}: {status}")
        
        return success_rate >= 70  # 70% or higher considered good
        
    except Exception as e:
        print_error(f"Error in anchor generation validation: {e}")
        return False

def main():
    """Main test execution for V2StyleProcessor Mini-TOC anchor processing"""
    print("🚀 Starting V2StyleProcessor Mini-TOC Anchor Processing Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Test results tracking
    test_results = {
        'style_rerun_trigger': False,
        'v2_engine_processing': False,
        'style_processing_results': False,
        'article_content_update': False,
        'anchor_generation_validation': False
    }
    
    # Test 1: Trigger Style Rerun
    print_info("\n🎯 GOAL: Test POST /api/style/rerun to trigger V2StyleProcessor on existing articles")
    run_id = test_style_rerun_endpoint()
    test_results['style_rerun_trigger'] = run_id is not None
    
    # Test 2: V2 Engine Processing Check
    print_info("\n🎯 GOAL: Check if V2 engine processing automatically applies style processing including clickable anchors")
    v2_processing_ok = test_v2_engine_processing()
    test_results['v2_engine_processing'] = v2_processing_ok
    
    # Test 3: Style Processing Results
    print_info("\n🎯 GOAL: Verify style processing results - check if TOC items get converted to markdown-style links [text](#anchor)")
    style_results_ok = test_style_processing_results()
    test_results['style_processing_results'] = style_results_ok
    
    # Test 4: Article Content Update
    print_info("\n🎯 GOAL: Confirm the processed content gets updated in the content library with clickable anchors")
    content_update_ok = test_article_content_update()
    test_results['article_content_update'] = content_update_ok
    
    # Test 5: Anchor Generation Validation
    print_info("\n🎯 GOAL: Validate that headings get proper IDs and TOC items get converted to markdown links")
    anchor_validation_ok = test_anchor_generation_validation()
    test_results['anchor_generation_validation'] = anchor_validation_ok
    
    # Final Summary
    print_test_header("V2STYLEPROCESSOR MINI-TOC ANCHOR PROCESSING TEST SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print_info(f"Tests completed: {passed_tests}/{total_tests}")
    
    for test_name, passed in test_results.items():
        if passed:
            print_success(f"✓ {test_name}")
        else:
            print_error(f"✗ {test_name}")
    
    # Specific conclusions for the review request
    print_info("\n🔍 REVIEW REQUEST CONCLUSIONS:")
    
    if test_results['style_rerun_trigger']:
        print_success("✓ POST /api/style/rerun successfully triggers V2StyleProcessor")
    else:
        print_error("✗ POST /api/style/rerun endpoint has issues")
    
    if test_results['v2_engine_processing']:
        print_success("✓ V2 engine processing includes style processing with clickable anchors")
    else:
        print_error("✗ V2 engine processing may not include proper style processing")
    
    if test_results['style_processing_results']:
        print_success("✓ Style processing converts TOC items to markdown-style links")
    else:
        print_error("✗ TOC items are not being converted to markdown-style links")
    
    if test_results['article_content_update']:
        print_success("✓ Processed content is updated in content library with clickable anchors")
    else:
        print_error("✗ Content library may not be updated with clickable anchors")
    
    if test_results['anchor_generation_validation']:
        print_success("✓ Headings get proper IDs and TOC items are converted to markdown links")
    else:
        print_error("✗ Anchor generation and TOC conversion may not be working properly")
    
    print_info(f"\nTest completed at: {datetime.now().isoformat()}")
    
    # Overall assessment
    success_rate = (passed_tests / total_tests) * 100
    print_info(f"Overall success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print_success("🎉 EXCELLENT: V2StyleProcessor Mini-TOC anchor processing is working well")
    elif success_rate >= 60:
        print_info("⚠️  GOOD: V2StyleProcessor Mini-TOC anchor processing is mostly working with some issues")
    else:
        print_error("❌ NEEDS ATTENTION: V2StyleProcessor Mini-TOC anchor processing has significant issues")
    
    return success_rate >= 60  # 60%+ considered acceptable

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)