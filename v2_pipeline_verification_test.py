#!/usr/bin/env python3
"""
V2 Pipeline Verification Test
Verify all V2 processing steps executed correctly
"""

import asyncio
import aiohttp
import json
import os
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

async def test_v2_pipeline_verification():
    """Verify all V2 processing steps executed correctly"""
    print_test_header("V2 Pipeline Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Verifying V2 processing pipeline steps...")
            
            # Check V2 diagnostics endpoints
            v2_endpoints = [
                ('/style/diagnostics', 'Woolf Style Processing'),
                ('/related-links/diagnostics', 'Related Links Generation'), 
                ('/gap-filling/diagnostics', 'Gap Filling System'),
                ('/evidence-tagging/diagnostics', 'Evidence Tagging'),
                ('/code-normalization/diagnostics', 'Code Normalization')
            ]
            
            pipeline_results = []
            
            for endpoint, step_name in v2_endpoints:
                try:
                    print_info(f"Checking {step_name}...")
                    async with session.get(f"{API_BASE}{endpoint}") as response:
                        if response.status == 200:
                            diagnostics = await response.json()
                            
                            # Check for V2 engine confirmation
                            engine = diagnostics.get('engine', 'unknown')
                            system_status = diagnostics.get('system_status', 'unknown')
                            
                            # Check for processing results
                            recent_results = diagnostics.get('recent_results', [])
                            total_runs = diagnostics.get('total_runs', 0)
                            success_rate = diagnostics.get('success_rate', 0)
                            
                            if engine.lower() == 'v2' and system_status == 'active':
                                print_success(f"✅ {step_name}: V2 engine active, {total_runs} runs, {success_rate}% success")
                                pipeline_results.append((step_name, True, f"Active with {total_runs} runs"))
                            else:
                                print_error(f"❌ {step_name}: engine={engine}, status={system_status}")
                                pipeline_results.append((step_name, False, f"engine={engine}, status={system_status}"))
                        else:
                            print_error(f"❌ {step_name}: HTTP {response.status}")
                            pipeline_results.append((step_name, False, f"HTTP {response.status}"))
                            
                except Exception as e:
                    print_error(f"❌ {step_name}: Error - {e}")
                    pipeline_results.append((step_name, False, f"Error: {e}"))
            
            # Calculate success rate
            successful_steps = sum(1 for _, success, _ in pipeline_results if success)
            total_steps = len(pipeline_results)
            success_rate = (successful_steps / total_steps) * 100 if total_steps > 0 else 0
            
            print_info(f"V2 pipeline verification: {successful_steps}/{total_steps} steps verified ({success_rate:.1f}%)")
            
            # Show detailed results
            for step_name, success, details in pipeline_results:
                status = "✅ PASS" if success else "❌ FAIL"
                print_info(f"{status} - {step_name}: {details}")
            
            return success_rate >= 60, pipeline_results
                
    except Exception as e:
        print_error(f"Error verifying V2 pipeline: {e}")
        return False, []

async def test_database_verification():
    """Verify database storage in MongoDB content_library collection"""
    print_test_header("Database Verification")
    
    try:
        async with aiohttp.ClientSession() as session:
            print_info("Verifying database storage in content_library collection...")
            
            async with session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', []) if isinstance(data, dict) else data
                    
                    print_success(f"Database accessible - {len(articles)} articles in content_library")
                    
                    # Look for recently created Google Maps API articles
                    google_maps_articles = []
                    for article in articles:
                        title = article.get('title', '').lower()
                        if any(keyword in title for keyword in ['google', 'map', 'javascript', 'api']):
                            google_maps_articles.append(article)
                    
                    if google_maps_articles:
                        print_success(f"Found {len(google_maps_articles)} Google Maps API articles in database")
                        
                        # Check article metadata for V2 processing indicators
                        v2_processed = 0
                        for article in google_maps_articles:
                            article_str = str(article).lower()
                            if any(indicator in article_str for indicator in ['v2', 'engine']):
                                v2_processed += 1
                        
                        print_info(f"Articles with V2 processing indicators: {v2_processed}")
                        
                        # Show article details
                        for i, article in enumerate(google_maps_articles):
                            title = article.get('title', 'Untitled')
                            created_at = article.get('created_at', 'Unknown')
                            content_length = len(str(article.get('content', '')))
                            print_info(f"  {i+1}. {title}")
                            print_info(f"     Created: {created_at}")
                            print_info(f"     Content: {content_length} chars")
                        
                        return True, google_maps_articles
                    else:
                        print_warning("No Google Maps API articles found in database")
                        return False, []
                        
                else:
                    print_error(f"Failed to access database - Status: {response.status}")
                    return False, []
                    
    except Exception as e:
        print_error(f"Error verifying database: {e}")
        return False, []

async def run_v2_verification():
    """Run V2 verification tests"""
    print_test_header("V2 Engine Processing Verification")
    print_info(f"Backend URL: {BACKEND_URL}")
    print_info(f"Test Time: {datetime.now().isoformat()}")
    print_info("Focus: Verify V2 pipeline execution and database storage")
    
    # Test results tracking
    test_results = []
    
    # Test 1: V2 Pipeline Verification
    success, pipeline_results = await test_v2_pipeline_verification()
    test_results.append(("V2 Pipeline Verification", success))
    
    # Test 2: Database Verification
    success, db_articles = await test_database_verification()
    test_results.append(("Database Verification", success))
    
    # Final Results Summary
    print_test_header("Verification Results Summary")
    
    passed_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print_info(f"Tests Passed: {passed_tests}/{total_tests}")
    print_info(f"Success Rate: {success_rate:.1f}%")
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print_info(f"{status} - {test_name}")
    
    # Overall assessment
    if success_rate >= 80:
        print_success(f"🎉 V2 VERIFICATION PASSED - {success_rate:.1f}% SUCCESS RATE")
        print_success("V2 Engine pipeline executed correctly!")
    elif success_rate >= 60:
        print_info(f"⚠️ V2 VERIFICATION PARTIAL - {success_rate:.1f}% SUCCESS RATE")
        print_info("Some V2 functionality verified, but improvements needed.")
    else:
        print_error(f"❌ V2 VERIFICATION FAILED - {success_rate:.1f}% SUCCESS RATE")
        print_error("Significant issues with V2 pipeline execution.")
    
    return success_rate >= 60

if __name__ == "__main__":
    print("🚀 Starting V2 Pipeline Verification...")
    
    try:
        success = asyncio.run(run_v2_verification())
        
        if success:
            print("\n🎯 V2 VERIFICATION COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n💥 V2 VERIFICATION COMPLETED WITH ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)