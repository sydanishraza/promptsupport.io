#!/usr/bin/env python3
"""
Cross-References Debug Test
Focused testing to debug why cross-references are not working in articles
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://content-engine-6.preview.emergentagent.com') + '/api'

class CrossReferencesDebugTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🔍 Cross-References Debug Test - Backend URL: {self.base_url}")
        
    def test_content_library_articles(self):
        """Get articles from Content Library to analyze cross-reference structure"""
        print("\n🔍 STEP 1: Analyzing Content Library Articles for Cross-References")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=30)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                total = data.get('total', 0)
                
                print(f"✅ Found {total} articles in Content Library")
                
                # Analyze articles for cross-references
                articles_with_links = 0
                articles_without_links = 0
                cross_ref_examples = []
                
                for i, article in enumerate(articles[:10]):  # Check first 10 articles
                    article_id = article.get('id')
                    title = article.get('title', 'Untitled')[:50]
                    content = article.get('content', '')
                    
                    # Check for related-links div
                    has_related_links = 'related-links' in content
                    has_cross_refs = 'Related Articles' in content or 'Procedural Navigation' in content
                    
                    if has_related_links or has_cross_refs:
                        articles_with_links += 1
                        # Extract cross-reference section for analysis
                        if 'related-links' in content:
                            start_idx = content.find('<div class="related-links">')
                            if start_idx != -1:
                                end_idx = content.find('</div>', start_idx)
                                if end_idx != -1:
                                    cross_ref_section = content[start_idx:end_idx + 6]
                                    cross_ref_examples.append({
                                        'title': title,
                                        'id': article_id,
                                        'cross_ref_html': cross_ref_section[:500] + '...' if len(cross_ref_section) > 500 else cross_ref_section
                                    })
                    else:
                        articles_without_links += 1
                    
                    print(f"  Article {i+1}: {title}")
                    print(f"    - Has related-links div: {has_related_links}")
                    print(f"    - Has cross-references: {has_cross_refs}")
                    print(f"    - Content length: {len(content)} chars")
                
                print(f"\n📊 CROSS-REFERENCE ANALYSIS RESULTS:")
                print(f"  - Articles WITH cross-references: {articles_with_links}")
                print(f"  - Articles WITHOUT cross-references: {articles_without_links}")
                print(f"  - Cross-reference success rate: {(articles_with_links/(articles_with_links+articles_without_links)*100):.1f}%")
                
                # Show examples of cross-references found
                if cross_ref_examples:
                    print(f"\n✅ CROSS-REFERENCE EXAMPLES FOUND:")
                    for example in cross_ref_examples[:3]:
                        print(f"  Article: {example['title']}")
                        print(f"  Cross-ref HTML: {example['cross_ref_html']}")
                        print()
                else:
                    print(f"\n❌ NO CROSS-REFERENCES FOUND IN ANY ARTICLES")
                
                return {
                    'total_articles': total,
                    'articles_with_links': articles_with_links,
                    'articles_without_links': articles_without_links,
                    'cross_ref_examples': cross_ref_examples
                }
            else:
                print(f"❌ Failed to get Content Library: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error analyzing Content Library: {e}")
            return None
    
    def test_upload_and_debug_cross_references(self):
        """Upload a test document and debug cross-reference generation step by step"""
        print("\n🔍 STEP 2: Upload Test Document and Debug Cross-Reference Generation")
        
        # Create a test document with multiple sections to trigger cross-references
        test_content = """
        # Introduction to API Integration
        This is the introduction section that explains the basics.
        
        # Setup and Configuration
        This section covers the setup process and configuration steps.
        
        # Implementation Guide
        This section provides detailed implementation instructions.
        
        # Troubleshooting
        This section covers common issues and solutions.
        """
        
        try:
            # Upload test content
            files = {
                'file': ('test_cross_ref_doc.txt', test_content, 'text/plain')
            }
            
            print("📤 Uploading test document...")
            response = requests.post(f"{self.base_url}/content/upload", files=files, timeout=120)
            print(f"Upload Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get('job_id')
                print(f"✅ Upload successful, Job ID: {job_id}")
                
                # Monitor processing with detailed logging
                print("🔄 Monitoring processing for cross-reference generation...")
                max_attempts = 30
                attempt = 0
                
                while attempt < max_attempts:
                    time.sleep(2)
                    attempt += 1
                    
                    status_response = requests.get(f"{self.base_url}/jobs/{job_id}", timeout=10)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status')
                        
                        print(f"  Attempt {attempt}: Status = {status}")
                        
                        if status == 'completed':
                            print("✅ Processing completed!")
                            
                            # Get the generated articles
                            articles = status_data.get('articles', [])
                            print(f"📄 Generated {len(articles)} articles")
                            
                            # Debug cross-reference generation
                            return self.debug_generated_articles(articles, job_id)
                            
                        elif status == 'failed':
                            error = status_data.get('error', 'Unknown error')
                            print(f"❌ Processing failed: {error}")
                            return None
                    else:
                        print(f"  Status check failed: {status_response.status_code}")
                
                print("⏰ Processing timeout - checking final status...")
                return None
            else:
                print(f"❌ Upload failed: {response.status_code}")
                if response.text:
                    print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error in upload and debug: {e}")
            return None
    
    def debug_generated_articles(self, articles, job_id):
        """Debug the generated articles for cross-reference functionality"""
        print(f"\n🔍 STEP 3: Debugging Generated Articles for Cross-References")
        
        cross_ref_debug = {
            'total_articles': len(articles),
            'articles_with_cross_refs': 0,
            'articles_without_cross_refs': 0,
            'cross_ref_details': [],
            'function_call_evidence': []
        }
        
        for i, article in enumerate(articles):
            article_id = article.get('id')
            title = article.get('title', f'Article {i+1}')
            content = article.get('content', '')
            
            print(f"\n📄 Article {i+1}: {title}")
            print(f"  - ID: {article_id}")
            print(f"  - Content length: {len(content)} chars")
            
            # Check for cross-reference indicators
            has_related_links_div = 'related-links' in content
            has_procedural_nav = 'Procedural Navigation' in content
            has_related_articles = 'Related Articles' in content
            has_external_resources = 'External Resources' in content
            has_hr_separator = '<hr>' in content
            
            print(f"  - Has related-links div: {has_related_links_div}")
            print(f"  - Has procedural navigation: {has_procedural_nav}")
            print(f"  - Has related articles section: {has_related_articles}")
            print(f"  - Has external resources: {has_external_resources}")
            print(f"  - Has HR separator: {has_hr_separator}")
            
            # Look for specific cross-reference patterns
            cross_ref_patterns = [
                'Previous:',
                'Next:',
                'Back to Table of Contents',
                'Related in This Guide',
                'Related Articles',
                'External Resources',
                'href="/content-library/article/',
                '<a href="#article-'
            ]
            
            found_patterns = []
            for pattern in cross_ref_patterns:
                if pattern in content:
                    found_patterns.append(pattern)
            
            print(f"  - Cross-ref patterns found: {found_patterns}")
            
            # Extract cross-reference section if it exists
            cross_ref_section = ""
            if has_related_links_div:
                start_idx = content.find('<div class="related-links">')
                if start_idx != -1:
                    end_idx = content.find('</div>', start_idx)
                    if end_idx != -1:
                        cross_ref_section = content[start_idx:end_idx + 6]
            
            if found_patterns or has_related_links_div:
                cross_ref_debug['articles_with_cross_refs'] += 1
                cross_ref_debug['cross_ref_details'].append({
                    'article_id': article_id,
                    'title': title,
                    'patterns_found': found_patterns,
                    'cross_ref_section': cross_ref_section[:300] + '...' if len(cross_ref_section) > 300 else cross_ref_section
                })
            else:
                cross_ref_debug['articles_without_cross_refs'] += 1
        
        # Check if articles were saved to Content Library with cross-references
        print(f"\n🔍 STEP 4: Verifying Cross-References in Content Library")
        time.sleep(2)  # Wait for database save
        
        # Get updated Content Library to see if cross-references persisted
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=30)
            if response.status_code == 200:
                data = response.json()
                library_articles = data.get('articles', [])
                
                # Find articles from our job
                job_articles = [art for art in library_articles if art.get('source_job_id') == job_id]
                print(f"📚 Found {len(job_articles)} articles from job {job_id} in Content Library")
                
                for article in job_articles:
                    content = article.get('content', '')
                    title = article.get('title', 'Untitled')
                    has_cross_refs = 'related-links' in content
                    print(f"  - {title}: Cross-refs in library = {has_cross_refs}")
                    
                    if has_cross_refs:
                        cross_ref_debug['function_call_evidence'].append(f"add_related_links_to_articles successfully added links to: {title}")
                    else:
                        cross_ref_debug['function_call_evidence'].append(f"add_related_links_to_articles did NOT add links to: {title}")
        
        except Exception as e:
            print(f"⚠️ Could not verify Content Library persistence: {e}")
        
        # Print debug summary
        print(f"\n📊 CROSS-REFERENCE DEBUG SUMMARY:")
        print(f"  - Total articles generated: {cross_ref_debug['total_articles']}")
        print(f"  - Articles WITH cross-references: {cross_ref_debug['articles_with_cross_refs']}")
        print(f"  - Articles WITHOUT cross-references: {cross_ref_debug['articles_without_cross_refs']}")
        
        if cross_ref_debug['articles_with_cross_refs'] > 0:
            print(f"✅ Cross-reference generation is WORKING")
            print(f"  Success rate: {(cross_ref_debug['articles_with_cross_refs']/cross_ref_debug['total_articles']*100):.1f}%")
        else:
            print(f"❌ Cross-reference generation is NOT WORKING")
            print(f"  0 cross-references found in {cross_ref_debug['total_articles']} articles")
        
        # Show function call evidence
        if cross_ref_debug['function_call_evidence']:
            print(f"\n🔍 FUNCTION CALL EVIDENCE:")
            for evidence in cross_ref_debug['function_call_evidence']:
                print(f"  - {evidence}")
        
        return cross_ref_debug
    
    def test_backend_logs_for_cross_references(self):
        """Check backend logs for add_related_links_to_articles function calls"""
        print(f"\n🔍 STEP 5: Checking Backend Logs for Cross-Reference Function Calls")
        
        # This would require access to backend logs, which we can't directly access
        # But we can infer from the API responses and article content
        print("ℹ️ Backend log analysis would require direct server access")
        print("   Using article content analysis as proxy for function call verification")
        
        return True
    
    def run_comprehensive_debug(self):
        """Run comprehensive cross-reference debugging"""
        print("🚀 Starting Comprehensive Cross-Reference Debug Test")
        print("=" * 60)
        
        # Step 1: Analyze existing articles
        library_analysis = self.test_content_library_articles()
        
        # Step 2: Upload test document and debug generation
        generation_debug = self.test_upload_and_debug_cross_references()
        
        # Step 3: Check backend logs (limited)
        self.test_backend_logs_for_cross_references()
        
        # Final analysis
        print("\n" + "=" * 60)
        print("🎯 FINAL CROSS-REFERENCE DEBUG ANALYSIS")
        print("=" * 60)
        
        if library_analysis:
            existing_success_rate = (library_analysis['articles_with_links'] / 
                                   (library_analysis['articles_with_links'] + library_analysis['articles_without_links']) * 100)
            print(f"📚 Existing Content Library:")
            print(f"  - Cross-reference success rate: {existing_success_rate:.1f}%")
            print(f"  - Articles with cross-refs: {library_analysis['articles_with_links']}")
            print(f"  - Articles without cross-refs: {library_analysis['articles_without_links']}")
        
        if generation_debug:
            new_success_rate = (generation_debug['articles_with_cross_refs'] / 
                              generation_debug['total_articles'] * 100) if generation_debug['total_articles'] > 0 else 0
            print(f"🆕 New Article Generation:")
            print(f"  - Cross-reference success rate: {new_success_rate:.1f}%")
            print(f"  - Articles with cross-refs: {generation_debug['articles_with_cross_refs']}")
            print(f"  - Articles without cross-refs: {generation_debug['articles_without_cross_refs']}")
        
        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        if library_analysis and library_analysis['articles_with_links'] > 0:
            print("✅ add_related_links_to_articles function IS working for some articles")
            print("   Issue may be: inconsistent execution, specific content types, or timing")
        elif generation_debug and generation_debug['articles_with_cross_refs'] > 0:
            print("✅ add_related_links_to_articles function IS working for new articles")
            print("   Issue may be: older articles don't have cross-references")
        else:
            print("❌ add_related_links_to_articles function is NOT working")
            print("   Possible causes:")
            print("   - Function not being called during article processing")
            print("   - Function called but not adding links due to logic issues")
            print("   - Links added but not persisted to database")
            print("   - Links added but not displayed in frontend")
        
        return {
            'library_analysis': library_analysis,
            'generation_debug': generation_debug
        }

if __name__ == "__main__":
    tester = CrossReferencesDebugTest()
    results = tester.run_comprehensive_debug()