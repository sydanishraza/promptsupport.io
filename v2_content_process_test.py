#!/usr/bin/env python3
"""
V2 Content Processing Test
Focus: Testing V2 content processing to trigger style processing and Mini-TOC anchor generation
"""

import requests
import json
import sys
import time
from datetime import datetime

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

def test_v2_content_processing():
    """Test V2 content processing to generate style results"""
    print_test_header("V2 Content Processing - Trigger Style Processing")
    
    try:
        # Create test content with Mini-TOC structure
        test_content = """# Code Normalization in JavaScript: A Practical Example

This article provides an overview of code normalization in JavaScript, illustrating its importance through a practical example.

## Table of Contents
- Introduction to Code Normalization
- Understanding the Code Example
- Benefits of Code Normalization
- Best Practices for Code Normalization

## Introduction to Code Normalization

Code normalization is a crucial practice in software development that involves standardizing code to improve its structure and readability.

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
        
        # Test V2 content processing
        payload = {
            "content": test_content,
            "engine": "v2",
            "enable_style_processing": True
        }
        
        print_info("Triggering V2 content processing...")
        response = requests.post(
            f"{BACKEND_URL}/content/process",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        print_info(f"POST /api/content/process - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            status = data.get('status', 'unknown')
            engine = data.get('engine', 'unknown')
            
            print_success(f"V2 content processing triggered - Job ID: {job_id}")
            print_info(f"Status: {status}")
            print_info(f"Engine: {engine}")
            
            return job_id
        else:
            print_error(f"V2 content processing failed: {response.status_code}")
            try:
                error_data = response.json()
                print_error(f"Error details: {error_data}")
            except:
                print_error(f"Raw response: {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Error in V2 content processing: {e}")
        return None

def check_job_status(job_id):
    """Check V2 processing job status"""
    print_test_header(f"Check V2 Processing Job Status - {job_id}")
    
    try:
        response = requests.get(f"{BACKEND_URL}/job-status/{job_id}", timeout=30)
        print_info(f"GET /api/job-status/{job_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            engine = data.get('engine', 'unknown')
            progress = data.get('progress', {})
            
            print_info(f"Job status: {status}")
            print_info(f"Engine: {engine}")
            
            if progress:
                print_info(f"Progress: {progress}")
            
            return status == 'completed'
        else:
            print_error(f"Failed to check job status: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error checking job status: {e}")
        return False

def wait_for_processing_completion(job_id, max_wait_time=60):
    """Wait for V2 processing to complete"""
    print_test_header(f"Wait for V2 Processing Completion - {job_id}")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        print_info(f"Checking job status... (elapsed: {int(time.time() - start_time)}s)")
        
        if check_job_status(job_id):
            print_success("✓ V2 processing completed successfully")
            return True
        
        print_info("Processing still in progress, waiting 10 seconds...")
        time.sleep(10)
    
    print_error(f"✗ Processing did not complete within {max_wait_time} seconds")
    return False

def test_style_diagnostics_after_v2():
    """Test style diagnostics after V2 processing"""
    print_test_header("Style Diagnostics After V2 Processing")
    
    try:
        response = requests.get(f"{BACKEND_URL}/style/diagnostics", timeout=30)
        print_info(f"GET /api/style/diagnostics - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            system_status = data.get('system_status', 'unknown')
            engine = data.get('engine', 'unknown')
            recent_results = data.get('recent_results', [])
            
            print_info(f"System status: {system_status}")
            print_info(f"Engine: {engine}")
            print_info(f"Recent results count: {len(recent_results)}")
            
            if recent_results:
                print_success("✓ Found recent style processing results")
                
                # Analyze the most recent result
                latest = recent_results[0]
                style_id = latest.get('style_id')
                style_status = latest.get('style_status')
                timestamp = latest.get('timestamp')
                
                print_info(f"Latest style ID: {style_id}")
                print_info(f"Latest status: {style_status}")
                print_info(f"Timestamp: {timestamp}")
                
                # Check for anchor-related fields
                anchor_links = latest.get('anchor_links_generated', 0)
                toc_broken_links = latest.get('toc_broken_links', [])
                
                print_info(f"Anchor links generated: {anchor_links}")
                print_info(f"TOC broken links: {len(toc_broken_links) if isinstance(toc_broken_links, list) else toc_broken_links}")
                
                if anchor_links > 0:
                    print_success("✓ Anchor links are being generated")
                else:
                    print_error("✗ No anchor links generated")
                
                if isinstance(toc_broken_links, list) and len(toc_broken_links) == 0:
                    print_success("✓ No broken TOC links")
                else:
                    print_error(f"✗ Broken TOC links found: {toc_broken_links}")
                
                return style_id
            else:
                print_error("✗ No recent style processing results")
                return None
        else:
            print_error(f"Failed to access style diagnostics: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error testing style diagnostics: {e}")
        return None

def test_detailed_style_result(style_id):
    """Test detailed style result analysis"""
    print_test_header(f"Detailed Style Result Analysis - {style_id}")
    
    try:
        response = requests.get(f"{BACKEND_URL}/style/diagnostics/{style_id}", timeout=30)
        print_info(f"GET /api/style/diagnostics/{style_id} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            style_result = data.get('style_result', {})
            analysis = data.get('analysis', {})
            
            print_success("✓ Detailed style result accessible")
            
            # Check style result details
            article_title = style_result.get('article_title', 'Unknown')
            style_status = style_result.get('style_status', 'unknown')
            anchor_links_generated = style_result.get('anchor_links_generated', 0)
            toc_broken_links = style_result.get('toc_broken_links', [])
            
            print_info(f"Article title: {article_title}")
            print_info(f"Style status: {style_status}")
            print_info(f"Anchor links generated: {anchor_links_generated}")
            print_info(f"TOC broken links: {len(toc_broken_links) if isinstance(toc_broken_links, list) else toc_broken_links}")
            
            # Check structural compliance
            structural_compliance = analysis.get('structural_compliance', {})
            if structural_compliance:
                has_mini_toc = structural_compliance.get('has_mini_toc', False)
                toc_anchor_count = structural_compliance.get('toc_anchor_count', 0)
                compliance_score = structural_compliance.get('compliance_score', 0)
                
                print_info(f"Has Mini-TOC: {has_mini_toc}")
                print_info(f"TOC anchor count: {toc_anchor_count}")
                print_info(f"Compliance score: {compliance_score}")
                
                if has_mini_toc:
                    print_success("✓ Mini-TOC structure detected")
                else:
                    print_error("✗ No Mini-TOC structure")
                
                if toc_anchor_count > 0:
                    print_success(f"✓ TOC anchors present: {toc_anchor_count}")
                else:
                    print_error("✗ No TOC anchors found")
            
            # Success criteria
            success_indicators = 0
            total_indicators = 4
            
            if style_status == 'success':
                success_indicators += 1
                print_success("✓ Style processing successful")
            else:
                print_error(f"✗ Style processing status: {style_status}")
            
            if anchor_links_generated > 0:
                success_indicators += 1
                print_success("✓ Anchor links generated")
            else:
                print_error("✗ No anchor links generated")
            
            if isinstance(toc_broken_links, list) and len(toc_broken_links) == 0:
                success_indicators += 1
                print_success("✓ No broken TOC links")
            else:
                print_error("✗ Broken TOC links present")
            
            if structural_compliance.get('has_mini_toc', False):
                success_indicators += 1
                print_success("✓ Mini-TOC structure present")
            else:
                print_error("✗ No Mini-TOC structure")
            
            success_rate = (success_indicators / total_indicators) * 100
            print_info(f"Style processing success rate: {success_rate:.1f}% ({success_indicators}/{total_indicators})")
            
            return success_rate >= 75
        else:
            print_error(f"Failed to get detailed style result: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error testing detailed style result: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting V2 Content Processing and Style Test")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    test_results = {
        'v2_content_processing': False,
        'processing_completion': False,
        'style_diagnostics': False,
        'detailed_style_analysis': False
    }
    
    # Test 1: Trigger V2 Content Processing
    print_info("\n🎯 GOAL: Trigger V2 content processing with style processing enabled")
    job_id = test_v2_content_processing()
    test_results['v2_content_processing'] = job_id is not None
    
    if job_id:
        # Test 2: Wait for Processing Completion
        print_info("\n🎯 GOAL: Wait for V2 processing to complete")
        processing_complete = wait_for_processing_completion(job_id)
        test_results['processing_completion'] = processing_complete
        
        if processing_complete:
            # Test 3: Check Style Diagnostics
            print_info("\n🎯 GOAL: Check style diagnostics after V2 processing")
            style_id = test_style_diagnostics_after_v2()
            test_results['style_diagnostics'] = style_id is not None
            
            if style_id:
                # Test 4: Detailed Style Analysis
                print_info("\n🎯 GOAL: Analyze detailed style processing results")
                detailed_analysis_ok = test_detailed_style_result(style_id)
                test_results['detailed_style_analysis'] = detailed_analysis_ok
    
    # Final Summary
    print_test_header("V2 CONTENT PROCESSING AND STYLE TEST SUMMARY")
    
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
    
    if test_results['v2_content_processing']:
        print_success("✓ V2 content processing can be triggered")
    else:
        print_error("✗ V2 content processing trigger failed")
    
    if test_results['processing_completion']:
        print_success("✓ V2 processing completes successfully")
    else:
        print_error("✗ V2 processing completion issues")
    
    if test_results['style_diagnostics']:
        print_success("✓ Style processing generates results")
    else:
        print_error("✗ Style processing may not be generating results")
    
    if test_results['detailed_style_analysis']:
        print_success("✓ Style processing includes Mini-TOC anchor generation")
    else:
        print_error("✗ Mini-TOC anchor generation may not be working")
    
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