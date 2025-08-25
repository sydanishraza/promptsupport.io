#!/usr/bin/env python3
"""
V2StyleProcessor Trigger Test
Focus: Triggering V2 processing to generate style results and test Mini-TOC anchor functionality
"""

import requests
import json
import sys
import time
from datetime import datetime
import re
from bs4 import BeautifulSoup

# Backend URL from environment
BACKEND_URL = "https://content-formatter.preview.emergentagent.com/api"

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

def trigger_v2_processing():
    """Trigger V2 processing to generate new content with style processing"""
    print_test_header("Trigger V2 Processing - Generate Content with Style Processing")
    
    try:
        # Create a simple text content to trigger V2 processing
        test_content = """# Code Normalization in JavaScript: A Practical Example

## Table of Contents
- Introduction to Code Normalization
- Understanding the Code Example  
- Benefits of Code Normalization
- Best Practices for Code Normalization

## Introduction to Code Normalization

Code normalization is a crucial practice in JavaScript development that ensures consistency and maintainability across your codebase.

## Understanding the Code Example

Let's examine a practical example of code normalization in action.

### JavaScript Code Snippet

```javascript
function normalizeData(input) {
    return input.trim().toLowerCase();
}
```

## Benefits of Code Normalization

Code normalization provides several key benefits for development teams.

## Best Practices for Code Normalization

Following established patterns helps maintain code quality and consistency.
"""
        
        # Trigger V2 processing via text processing endpoint
        payload = {
            "content": test_content,
            "content_type": "text",
            "processing_options": {
                "engine": "v2",
                "enable_style_processing": True,
                "enable_mini_toc": True
            }
        }
        
        print_info("Triggering V2 processing with style processing enabled...")
        response = requests.post(
            f"{BACKEND_URL}/process-text",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        print_info(f"POST /api/process-text - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print_success(f"V2 processing triggered successfully - Job ID: {job_id}")
            
            # Wait for processing to complete
            print_info("Waiting for V2 processing to complete...")
            time.sleep(10)  # Give it some time to process
            
            return job_id
        else:
            print_error(f"Failed to trigger V2 processing: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error triggering V2 processing: {e}")
        return None

def check_processing_status(job_id):
    """Check the status of V2 processing job"""
    print_test_header(f"Check V2 Processing Status - Job ID: {job_id}")
    
    try:
        response = requests.get(f"{BACKEND_URL}/job-status/{job_id}", timeout=30)
        print_info(f"GET /api/job-status/{job_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            engine = data.get('engine', 'unknown')
            
            print_info(f"Job status: {status}")
            print_info(f"Engine: {engine}")
            
            if status == 'completed':
                print_success("✓ V2 processing completed successfully")
                return True
            elif status == 'processing':
                print_info("⏳ V2 processing still in progress")
                return False
            else:
                print_error(f"✗ V2 processing status: {status}")
                return False
        else:
            print_error(f"Failed to check job status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error checking processing status: {e}")
        return False

def test_style_diagnostics_after_processing():
    """Test style diagnostics after V2 processing"""
    print_test_header("Style Diagnostics After V2 Processing")
    
    try:
        response = requests.get(f"{BACKEND_URL}/style/diagnostics", timeout=30)
        print_info(f"GET /api/style/diagnostics - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recent_results = data.get('recent_results', [])
            
            print_info(f"Recent style processing results: {len(recent_results)}")
            
            if recent_results:
                latest_result = recent_results[0]
                style_id = latest_result.get('style_id')
                style_status = latest_result.get('style_status')
                timestamp = latest_result.get('timestamp')
                
                print_success(f"✓ Found recent style result: {style_id}")
                print_info(f"Status: {style_status}")
                print_info(f"Timestamp: {timestamp}")
                
                # Check for anchor-related fields
                if 'anchor_links_generated' in latest_result:
                    anchor_count = latest_result['anchor_links_generated']
                    print_success(f"✓ Anchor links generated: {anchor_count}")
                else:
                    print_error("✗ No anchor_links_generated field")
                
                if 'toc_broken_links' in latest_result:
                    broken_links = latest_result['toc_broken_links']
                    if isinstance(broken_links, list) and len(broken_links) == 0:
                        print_success("✓ No broken TOC links")
                    else:
                        print_error(f"✗ Broken TOC links: {broken_links}")
                
                return style_id
            else:
                print_error("✗ No recent style processing results found")
                return None
        else:
            print_error(f"Failed to access style diagnostics: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error testing style diagnostics: {e}")
        return None

def test_style_rerun_with_valid_id():
    """Test style rerun with a valid run_id"""
    print_test_header("Test Style Rerun with Valid Run ID")
    
    try:
        # Get recent V2 processing results to find a run_id
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        
        if response.status_code != 200:
            print_error("Failed to access content library")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Look for V2 articles with run_id
        valid_run_id = None
        for article in articles:
            metadata = article.get('metadata', {})
            if 'run_id' in metadata:
                valid_run_id = metadata['run_id']
                print_info(f"Found run_id: {valid_run_id}")
                break
        
        if not valid_run_id:
            print_error("No valid run_id found")
            return False
        
        # Test the rerun endpoint
        payload = {"run_id": valid_run_id}
        
        rerun_response = requests.post(
            f"{BACKEND_URL}/style/rerun",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print_info(f"POST /api/style/rerun - Status: {rerun_response.status_code}")
        
        if rerun_response.status_code == 200:
            rerun_data = rerun_response.json()
            print_success("✓ Style rerun triggered successfully")
            
            articles_processed = rerun_data.get('articles_processed', 0)
            success_count = rerun_data.get('success_count', 0)
            
            print_info(f"Articles processed: {articles_processed}")
            print_info(f"Success count: {success_count}")
            
            return success_count > 0
        else:
            print_error(f"Style rerun failed: {rerun_response.status_code}")
            print_error(f"Response: {rerun_response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error testing style rerun: {e}")
        return False

def analyze_target_article_content():
    """Analyze the target article content for Mini-TOC anchors"""
    print_test_header("Analyze Target Article - Mini-TOC Anchor Content")
    
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        
        if response.status_code != 200:
            print_error("Failed to access content library")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Find the target article
        target_article = None
        for article in articles:
            title = article.get('title', '').lower()
            if 'code normalization' in title and 'javascript' in title:
                target_article = article
                break
        
        if not target_article:
            print_error("Target article not found")
            return False
        
        print_success(f"Found target article: {target_article['title']}")
        
        content = target_article.get('content', '') or target_article.get('html', '')
        print_info(f"Content length: {len(content)} characters")
        
        # Show raw content sample to understand structure
        print_info("\n📄 Raw Content Sample (first 2000 chars):")
        print_info("-" * 60)
        print_info(content[:2000])
        print_info("-" * 60)
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for Mini-TOC structure
        print_info("\n🔍 Mini-TOC Structure Analysis:")
        
        # Check for various TOC patterns
        ul_elements = soup.find_all('ul')
        print_info(f"Found {len(ul_elements)} <ul> elements")
        
        for i, ul in enumerate(ul_elements):
            li_items = ul.find_all('li')
            print_info(f"  UL {i+1}: {len(li_items)} items")
            
            if len(li_items) >= 3:  # Likely a TOC
                print_info(f"    Potential TOC with {len(li_items)} items:")
                for j, li in enumerate(li_items):
                    text = li.get_text().strip()
                    links = li.find_all('a')
                    print_info(f"      {j+1}. {text[:50]}...")
                    
                    if links:
                        for link in links:
                            href = link.get('href', '')
                            print_info(f"         Link: {href}")
                    else:
                        print_info("         No links")
        
        # Check for markdown-style links in raw content
        markdown_pattern = r'\[([^\]]+)\]\(#([^)]+)\)'
        markdown_matches = re.findall(markdown_pattern, content)
        
        print_info(f"\n🔗 Markdown-style TOC links: {len(markdown_matches)}")
        for text, anchor in markdown_matches:
            print_info(f"  - [{text}](#{anchor})")
        
        # Check headings with IDs
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print_info(f"\n📋 Headings Analysis: {len(headings)} total")
        
        headings_with_ids = 0
        for heading in headings:
            heading_id = heading.get('id', '')
            text = heading.get_text().strip()
            
            if heading_id:
                print_info(f"  ✓ {heading.name}: '{text[:40]}...' ID='{heading_id}'")
                headings_with_ids += 1
            else:
                print_info(f"  ✗ {heading.name}: '{text[:40]}...' (No ID)")
        
        print_info(f"Headings with IDs: {headings_with_ids}/{len(headings)}")
        
        # Summary
        has_toc_structure = len(ul_elements) > 0
        has_markdown_links = len(markdown_matches) > 0
        has_heading_ids = headings_with_ids > 0
        
        success_indicators = sum([has_toc_structure, has_markdown_links, has_heading_ids])
        
        print_info(f"\n📊 Analysis Summary:")
        print_info(f"  TOC Structure: {'✓' if has_toc_structure else '✗'}")
        print_info(f"  Markdown Links: {'✓' if has_markdown_links else '✗'}")
        print_info(f"  Heading IDs: {'✓' if has_heading_ids else '✗'}")
        print_info(f"  Success Rate: {success_indicators}/3")
        
        return success_indicators >= 2
        
    except Exception as e:
        print_error(f"Error analyzing target article: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting V2StyleProcessor Trigger and Mini-TOC Test")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    test_results = {
        'v2_processing_trigger': False,
        'style_diagnostics_check': False,
        'style_rerun_test': False,
        'article_content_analysis': False
    }
    
    # Test 1: Trigger V2 Processing
    print_info("\n🎯 GOAL: Trigger V2 processing to generate content with style processing")
    job_id = trigger_v2_processing()
    
    if job_id:
        # Wait and check status
        time.sleep(15)  # Give more time for processing
        processing_complete = check_processing_status(job_id)
        test_results['v2_processing_trigger'] = processing_complete
    
    # Test 2: Check Style Diagnostics
    print_info("\n🎯 GOAL: Check style diagnostics after V2 processing")
    style_id = test_style_diagnostics_after_processing()
    test_results['style_diagnostics_check'] = style_id is not None
    
    # Test 3: Test Style Rerun
    print_info("\n🎯 GOAL: Test style rerun functionality")
    rerun_success = test_style_rerun_with_valid_id()
    test_results['style_rerun_test'] = rerun_success
    
    # Test 4: Analyze Target Article
    print_info("\n🎯 GOAL: Analyze target article for Mini-TOC anchor content")
    article_analysis_ok = analyze_target_article_content()
    test_results['article_content_analysis'] = article_analysis_ok
    
    # Final Summary
    print_test_header("V2STYLEPROCESSOR TRIGGER TEST SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print_info(f"Tests completed: {passed_tests}/{total_tests}")
    
    for test_name, passed in test_results.items():
        if passed:
            print_success(f"✓ {test_name}")
        else:
            print_error(f"✗ {test_name}")
    
    success_rate = (passed_tests / total_tests) * 100
    print_info(f"Overall success rate: {success_rate:.1f}%")
    
    # Conclusions
    print_info("\n🔍 CONCLUSIONS:")
    
    if test_results['v2_processing_trigger']:
        print_success("✓ V2 processing can be triggered successfully")
    else:
        print_error("✗ V2 processing trigger has issues")
    
    if test_results['style_diagnostics_check']:
        print_success("✓ Style diagnostics are accessible and working")
    else:
        print_error("✗ Style diagnostics may not be working properly")
    
    if test_results['style_rerun_test']:
        print_success("✓ Style rerun functionality is working")
    else:
        print_error("✗ Style rerun functionality has issues")
    
    if test_results['article_content_analysis']:
        print_success("✓ Target article has proper Mini-TOC anchor structure")
    else:
        print_error("✗ Target article lacks proper Mini-TOC anchor structure")
    
    print_info(f"\nTest completed at: {datetime.now().isoformat()}")
    
    return success_rate >= 50

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