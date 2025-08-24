#!/usr/bin/env python3
"""
Focused Cross-Reference Test
Test to verify the specific issue with cross-references not being saved to database
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-pipeline-5.preview.emergentagent.com') + '/api'

def test_cross_reference_database_persistence():
    """Test if cross-references are being saved to database after generation"""
    print("🔍 FOCUSED TEST: Cross-Reference Database Persistence Issue")
    print("=" * 60)
    
    # Create test content that will generate multiple articles
    test_content = """
# Introduction to API Integration
This is the introduction section that explains the basics of API integration.
It covers fundamental concepts and provides an overview of what you'll learn.

# Setup and Configuration
This section covers the setup process and configuration steps needed.
You'll learn how to configure your environment and prepare for integration.

# Implementation Guide  
This section provides detailed implementation instructions and code examples.
Follow these steps to successfully implement the API integration.

# Advanced Features
This section covers advanced features and customization options.
Learn how to extend the basic implementation with advanced capabilities.

# Troubleshooting
This section covers common issues and solutions you might encounter.
Use this guide to resolve problems and optimize your implementation.
"""
    
    try:
        print("📤 Uploading test document with multiple sections...")
        
        # Upload test content
        files = {
            'file': ('cross_ref_test.txt', test_content, 'text/plain')
        }
        
        response = requests.post(f"{BACKEND_URL}/content/upload", files=files, timeout=120)
        print(f"Upload Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"✅ Upload successful, Job ID: {job_id}")
            
            # Wait for processing to complete
            print("⏳ Waiting for processing to complete...")
            time.sleep(30)  # Give enough time for processing
            
            # Check job status
            job_response = requests.get(f"{BACKEND_URL}/jobs/{job_id}", timeout=10)
            if job_response.status_code == 200:
                job_data = job_response.json()
                print(f"Job Status: {job_data.get('status')}")
                print(f"Chunks Created: {job_data.get('chunks_created', 0)}")
                
                # Get Content Library articles to check for cross-references
                print("\n🔍 Checking Content Library for generated articles...")
                library_response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
                
                if library_response.status_code == 200:
                    library_data = library_response.json()
                    all_articles = library_data.get('articles', [])
                    
                    # Find articles from our job
                    job_articles = [art for art in all_articles if art.get('source_job_id') == job_id]
                    print(f"📚 Found {len(job_articles)} articles from job {job_id}")
                    
                    if len(job_articles) > 1:
                        print(f"✅ Multiple articles generated - cross-references should be added")
                        
                        # Analyze each article for cross-references
                        articles_with_cross_refs = 0
                        articles_without_cross_refs = 0
                        
                        for i, article in enumerate(job_articles):
                            title = article.get('title', f'Article {i+1}')[:50]
                            content = article.get('content', '')
                            
                            # Check for cross-reference indicators
                            has_related_links = 'related-links' in content
                            has_procedural_nav = 'Procedural Navigation' in content
                            has_related_articles = 'Related Articles' in content
                            has_cross_ref_links = 'href="/content-library/article/' in content
                            
                            print(f"\n📄 Article {i+1}: {title}")
                            print(f"  - Has related-links div: {has_related_links}")
                            print(f"  - Has procedural navigation: {has_procedural_nav}")
                            print(f"  - Has related articles section: {has_related_articles}")
                            print(f"  - Has cross-reference links: {has_cross_ref_links}")
                            
                            if has_related_links or has_procedural_nav or has_related_articles:
                                articles_with_cross_refs += 1
                                
                                # Extract and show cross-reference section
                                if has_related_links:
                                    start_idx = content.find('<div class="related-links">')
                                    if start_idx != -1:
                                        end_idx = content.find('</div>', start_idx)
                                        if end_idx != -1:
                                            cross_ref_section = content[start_idx:end_idx + 6]
                                            print(f"  - Cross-ref section: {cross_ref_section[:200]}...")
                            else:
                                articles_without_cross_refs += 1
                        
                        # Final analysis
                        print(f"\n📊 CROSS-REFERENCE ANALYSIS:")
                        print(f"  - Total articles: {len(job_articles)}")
                        print(f"  - Articles WITH cross-references: {articles_with_cross_refs}")
                        print(f"  - Articles WITHOUT cross-references: {articles_without_cross_refs}")
                        
                        if articles_with_cross_refs > 0:
                            success_rate = (articles_with_cross_refs / len(job_articles)) * 100
                            print(f"  - Success rate: {success_rate:.1f}%")
                            
                            if success_rate == 100:
                                print("✅ CROSS-REFERENCES ARE WORKING PERFECTLY")
                                print("   add_related_links_to_articles function is working and saving to database")
                            else:
                                print("⚠️ PARTIAL SUCCESS - Some articles have cross-references")
                                print("   add_related_links_to_articles function is working but not consistently")
                        else:
                            print("❌ CRITICAL ISSUE CONFIRMED")
                            print("   add_related_links_to_articles function is NOT working or NOT saving to database")
                            print("\n🔍 ROOT CAUSE ANALYSIS:")
                            print("   1. Function may be called but updated articles not saved to database")
                            print("   2. Function may have logic errors preventing link generation")
                            print("   3. Function may be throwing exceptions during execution")
                            
                            return {
                                'issue_confirmed': True,
                                'root_cause': 'cross_references_not_persisted_to_database',
                                'articles_generated': len(job_articles),
                                'articles_with_cross_refs': articles_with_cross_refs
                            }
                    else:
                        print("⚠️ Only one article generated - cross-references not expected")
                        return {
                            'issue_confirmed': False,
                            'root_cause': 'single_article_generated',
                            'articles_generated': len(job_articles)
                        }
                else:
                    print(f"❌ Failed to get Content Library: {library_response.status_code}")
            else:
                print(f"❌ Failed to get job status: {job_response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            if response.text:
                print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return {'issue_confirmed': True, 'root_cause': 'test_execution_error', 'error': str(e)}

if __name__ == "__main__":
    result = test_cross_reference_database_persistence()
    print(f"\n🎯 TEST RESULT: {result}")