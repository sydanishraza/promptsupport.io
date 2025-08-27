#!/usr/bin/env python3
"""
REAL CONTENT LIBRARY ISSUES FIX VALIDATION
Comprehensive testing of actual implementation fixes for Content Library issues
"""

import asyncio
import aiohttp
import json
import os
import time
import re
from datetime import datetime
from typing import Dict, List, Any

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://content-engine-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ContentLibraryFixValidator:
    def __init__(self):
        self.session = None
        self.test_results = {
            'high_quality_generation': False,
            'quality_fixes_applied': False,
            'ordered_lists_fixed': False,
            'overview_vs_complete_guide': False,
            'faq_standardization': False,
            'wysiwyg_features': False,
            'content_quality': False,
            'database_storage': False,
            'real_content_processing': False
        }
        self.detailed_findings = []
        
    async def setup_session(self):
        """Setup HTTP session for API calls"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def log_finding(self, test_name: str, status: str, details: str):
        """Log detailed test findings"""
        finding = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.detailed_findings.append(finding)
        print(f"📋 {test_name}: {status} - {details}")
        
    async def test_real_content_processing(self) -> bool:
        """Test 1: Real Content Processing with actual document"""
        try:
            print("🔍 TESTING REAL CONTENT PROCESSING...")
            
            # Test with substantial content that should trigger quality fixes
            test_content = """
            Google Maps JavaScript API Tutorial - Complete Implementation Guide
            
            This comprehensive guide covers everything you need to know about implementing Google Maps JavaScript API in your web applications.
            
            ## Getting Started
            
            1. First, you need to obtain an API key from Google Cloud Console
            2. Next, include the Google Maps JavaScript API in your HTML
            3. Then, initialize the map with your desired configuration
            4. Finally, add markers and customize your map
            
            ### Step-by-Step Implementation
            
            1. Create a new HTML file
            2. Add the Google Maps API script
            3. Initialize the map object
            4. Configure map options
            5. Add event listeners
            6. Test your implementation
            
            ## Advanced Features
            
            - Custom markers and info windows
            - Geocoding and reverse geocoding
            - Directions and routing
            - Places API integration
            - Street View integration
            
            ## Common Issues and Solutions
            
            Q: Why is my map not loading?
            A: Check your API key and ensure it's properly configured.
            
            Q: How do I add custom markers?
            A: Use the google.maps.Marker constructor with custom icon properties.
            """
            
            # Process content through the backend
            async with self.session.post(
                f"{API_BASE}/process-content",
                json={
                    "content": test_content,
                    "filename": "Google_Maps_API_Tutorial.txt",
                    "processing_type": "intelligent"
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    job_id = result.get('job_id')
                    
                    if job_id:
                        # Wait for processing to complete
                        await self.wait_for_processing(job_id)
                        
                        # Check if articles were generated
                        articles = await self.get_generated_articles()
                        if len(articles) > 0:
                            await self.log_finding("Real Content Processing", "✅ PASSED", 
                                                 f"Successfully processed content and generated {len(articles)} articles")
                            return True
                        else:
                            await self.log_finding("Real Content Processing", "❌ FAILED", 
                                                 "No articles generated from content processing")
                            return False
                    else:
                        await self.log_finding("Real Content Processing", "❌ FAILED", 
                                             "No job ID returned from processing")
                        return False
                else:
                    await self.log_finding("Real Content Processing", "❌ FAILED", 
                                         f"API call failed with status {response.status}")
                    return False
                    
        except Exception as e:
            await self.log_finding("Real Content Processing", "❌ ERROR", f"Exception: {str(e)}")
            return False
            
    async def wait_for_processing(self, job_id: str, timeout: int = 120):
        """Wait for content processing to complete"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with self.session.get(f"{API_BASE}/processing-status/{job_id}") as response:
                    if response.status == 200:
                        status_data = await response.json()
                        status = status_data.get('status')
                        
                        if status == 'completed':
                            print(f"✅ Processing completed for job {job_id}")
                            return True
                        elif status == 'failed':
                            print(f"❌ Processing failed for job {job_id}")
                            return False
                        else:
                            print(f"⏳ Processing status: {status}")
                            await asyncio.sleep(5)
                    else:
                        await asyncio.sleep(5)
            except Exception as e:
                print(f"⚠️ Error checking processing status: {e}")
                await asyncio.sleep(5)
                
        print(f"⏰ Processing timeout after {timeout} seconds")
        return False
        
    async def get_generated_articles(self) -> List[Dict]:
        """Get recently generated articles from Content Library"""
        try:
            async with self.session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    # Filter for recently created articles (last 5 minutes)
                    recent_articles = []
                    current_time = datetime.now()
                    
                    for article in articles:
                        created_at = article.get('created_at')
                        if created_at:
                            try:
                                if isinstance(created_at, str):
                                    article_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                else:
                                    article_time = created_at
                                    
                                time_diff = (current_time - article_time.replace(tzinfo=None)).total_seconds()
                                if time_diff < 300:  # 5 minutes
                                    recent_articles.append(article)
                            except:
                                continue
                                
                    return recent_articles
                else:
                    return []
        except Exception as e:
            print(f"❌ Error getting articles: {e}")
            return []
            
    async def test_ordered_lists_validation(self) -> bool:
        """Test 2: Ordered Lists Validation - Check for continuous numbering and no duplication"""
        try:
            print("🔍 TESTING ORDERED LISTS VALIDATION...")
            
            articles = await self.get_generated_articles()
            if not articles:
                await self.log_finding("Ordered Lists Validation", "⚠️ SKIPPED", 
                                     "No recent articles found to test")
                return False
                
            issues_found = []
            lists_analyzed = 0
            
            for article in articles:
                content = article.get('content', '')
                
                # Check for ordered lists
                ol_matches = re.findall(r'<ol[^>]*>(.*?)</ol>', content, re.DOTALL)
                
                for ol_content in ol_matches:
                    lists_analyzed += 1
                    
                    # Check for text duplication patterns like "Text.Text."
                    duplication_pattern = r'(\b\w+(?:\s+\w+)*)\.\1\.'
                    if re.search(duplication_pattern, ol_content):
                        issues_found.append(f"Text duplication found in article '{article.get('title', 'Unknown')}'")
                    
                    # Check for proper list structure
                    li_items = re.findall(r'<li[^>]*>(.*?)</li>', ol_content, re.DOTALL)
                    if len(li_items) > 1:
                        # Check if items have proper content
                        empty_items = [i for i, item in enumerate(li_items) if len(item.strip()) < 5]
                        if empty_items:
                            issues_found.append(f"Empty list items found in article '{article.get('title', 'Unknown')}'")
                            
            if lists_analyzed == 0:
                await self.log_finding("Ordered Lists Validation", "⚠️ SKIPPED", 
                                     "No ordered lists found in recent articles")
                return False
            elif len(issues_found) == 0:
                await self.log_finding("Ordered Lists Validation", "✅ PASSED", 
                                     f"Analyzed {lists_analyzed} ordered lists - no duplication or structural issues found")
                return True
            else:
                await self.log_finding("Ordered Lists Validation", "❌ FAILED", 
                                     f"Found {len(issues_found)} issues: {'; '.join(issues_found[:3])}")
                return False
                
        except Exception as e:
            await self.log_finding("Ordered Lists Validation", "❌ ERROR", f"Exception: {str(e)}")
            return False
            
    async def test_overview_vs_complete_guide_separation(self) -> bool:
        """Test 3: Overview vs Complete Guide Separation"""
        try:
            print("🔍 TESTING OVERVIEW VS COMPLETE GUIDE SEPARATION...")
            
            articles = await self.get_generated_articles()
            if not articles:
                await self.log_finding("Overview vs Complete Guide", "⚠️ SKIPPED", 
                                     "No recent articles found to test")
                return False
                
            overview_articles = []
            complete_guide_articles = []
            
            for article in articles:
                title = article.get('title', '').lower()
                article_type = article.get('article_type', '').lower()
                content = article.get('content', '')
                
                if 'overview' in title or 'overview' in article_type:
                    overview_articles.append(article)
                elif 'complete' in title or 'guide' in title or 'tutorial' in title:
                    complete_guide_articles.append(article)
                    
            if len(overview_articles) == 0 and len(complete_guide_articles) == 0:
                await self.log_finding("Overview vs Complete Guide", "⚠️ SKIPPED", 
                                     "No overview or complete guide articles found")
                return False
                
            # Validate overview articles (should be summaries, not detailed steps)
            overview_issues = []
            for article in overview_articles:
                content = article.get('content', '')
                
                # Check if overview contains detailed implementation (it shouldn't)
                detailed_patterns = [
                    r'<pre><code',  # Code blocks
                    r'step \d+',    # Step-by-step instructions
                    r'<ol[^>]*>.*?<li.*?implementation',  # Implementation lists
                ]
                
                for pattern in detailed_patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                        overview_issues.append(f"Overview article '{article.get('title')}' contains detailed implementation")
                        break
                        
            # Validate complete guide articles (should have detailed content)
            guide_issues = []
            for article in complete_guide_articles:
                content = article.get('content', '')
                
                # Check if complete guide has substantial content
                if len(content) < 1000:
                    guide_issues.append(f"Complete guide '{article.get('title')}' has insufficient content ({len(content)} chars)")
                    
                # Check for presence of detailed elements
                has_code = '<pre><code' in content or '<code' in content
                has_steps = re.search(r'<ol|step \d+|<li', content, re.IGNORECASE)
                
                if not (has_code or has_steps):
                    guide_issues.append(f"Complete guide '{article.get('title')}' lacks detailed implementation content")
                    
            total_issues = len(overview_issues) + len(guide_issues)
            
            if total_issues == 0:
                await self.log_finding("Overview vs Complete Guide", "✅ PASSED", 
                                     f"Found {len(overview_articles)} overview and {len(complete_guide_articles)} complete guide articles with proper separation")
                return True
            else:
                all_issues = overview_issues + guide_issues
                await self.log_finding("Overview vs Complete Guide", "❌ FAILED", 
                                     f"Found {total_issues} separation issues: {'; '.join(all_issues[:2])}")
                return False
                
        except Exception as e:
            await self.log_finding("Overview vs Complete Guide", "❌ ERROR", f"Exception: {str(e)}")
            return False
            
    async def test_faq_standardization(self) -> bool:
        """Test 4: FAQ Standardization with proper HTML formatting"""
        try:
            print("🔍 TESTING FAQ STANDARDIZATION...")
            
            articles = await self.get_generated_articles()
            if not articles:
                await self.log_finding("FAQ Standardization", "⚠️ SKIPPED", 
                                     "No recent articles found to test")
                return False
                
            faq_articles = []
            for article in articles:
                title = article.get('title', '').lower()
                article_type = article.get('article_type', '').lower()
                
                if 'faq' in title or 'frequently asked' in title or 'faq' in article_type:
                    faq_articles.append(article)
                    
            if len(faq_articles) == 0:
                await self.log_finding("FAQ Standardization", "⚠️ SKIPPED", 
                                     "No FAQ articles found in recent articles")
                return False
                
            issues_found = []
            
            for article in faq_articles:
                content = article.get('content', '')
                title = article.get('title', '')
                
                # Check for proper HTML formatting (not Markdown)
                if re.search(r'##\s|###\s', content):
                    issues_found.append(f"FAQ article '{title}' contains Markdown formatting instead of HTML")
                    
                # Check for proper HTML structure
                if not re.search(r'<h[2-4][^>]*>', content):
                    issues_found.append(f"FAQ article '{title}' lacks proper HTML heading structure")
                    
                # Check for standardized title format
                if not re.search(r'frequently asked questions|faq', title.lower()):
                    issues_found.append(f"FAQ article title '{title}' doesn't follow standardized format")
                    
                # Check for cross-reference links
                has_links = re.search(r'<a\s+href=["\'][^"\']*["\'][^>]*>', content)
                if not has_links:
                    issues_found.append(f"FAQ article '{title}' lacks cross-reference links")
                    
            if len(issues_found) == 0:
                await self.log_finding("FAQ Standardization", "✅ PASSED", 
                                     f"Found {len(faq_articles)} FAQ articles with proper standardization")
                return True
            else:
                await self.log_finding("FAQ Standardization", "❌ FAILED", 
                                     f"Found {len(issues_found)} standardization issues: {'; '.join(issues_found[:2])}")
                return False
                
        except Exception as e:
            await self.log_finding("FAQ Standardization", "❌ ERROR", f"Exception: {str(e)}")
            return False
            
    async def test_wysiwyg_editor_features(self) -> bool:
        """Test 5: WYSIWYG Editor Features Usage"""
        try:
            print("🔍 TESTING WYSIWYG EDITOR FEATURES...")
            
            articles = await self.get_generated_articles()
            if not articles:
                await self.log_finding("WYSIWYG Editor Features", "⚠️ SKIPPED", 
                                     "No recent articles found to test")
                return False
                
            features_found = {
                'mini_toc': 0,
                'callouts': 0,
                'anchor_links': 0,
                'enhanced_lists': 0,
                'code_blocks': 0
            }
            
            for article in articles:
                content = article.get('content', '')
                
                # Check for Mini-TOC
                if re.search(r'<div[^>]*class="mini-toc"', content):
                    features_found['mini_toc'] += 1
                    
                # Check for callouts
                if re.search(r'<div[^>]*class="callout', content):
                    features_found['callouts'] += 1
                    
                # Check for anchor links
                if re.search(r'<[^>]+id="[^"]*"', content):
                    features_found['anchor_links'] += 1
                    
                # Check for enhanced lists with CSS classes
                if re.search(r'<[ou]l[^>]*class="doc-list', content):
                    features_found['enhanced_lists'] += 1
                    
                # Check for proper code blocks
                if re.search(r'<pre><code[^>]*class="language-', content):
                    features_found['code_blocks'] += 1
                    
            total_features = sum(features_found.values())
            
            if total_features >= 3:  # At least 3 different WYSIWYG features should be present
                await self.log_finding("WYSIWYG Editor Features", "✅ PASSED", 
                                     f"Found {total_features} WYSIWYG features across articles: {features_found}")
                return True
            else:
                await self.log_finding("WYSIWYG Editor Features", "❌ FAILED", 
                                     f"Insufficient WYSIWYG features found ({total_features}): {features_found}")
                return False
                
        except Exception as e:
            await self.log_finding("WYSIWYG Editor Features", "❌ ERROR", f"Exception: {str(e)}")
            return False
            
    async def test_content_quality_verification(self) -> bool:
        """Test 6: Content Quality Verification"""
        try:
            print("🔍 TESTING CONTENT QUALITY VERIFICATION...")
            
            articles = await self.get_generated_articles()
            if not articles:
                await self.log_finding("Content Quality Verification", "⚠️ SKIPPED", 
                                     "No recent articles found to test")
                return False
                
            quality_issues = []
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '')
                
                # Check for text duplication
                duplication_patterns = [
                    r'(\b\w+(?:\s+\w+){0,3})\.\s*\1\.',  # "Text. Text." patterns
                    r'(\b\w+(?:\s+\w+){0,3})\s+\1\s+',   # Repeated phrases
                ]
                
                for pattern in duplication_patterns:
                    if re.search(pattern, content):
                        quality_issues.append(f"Text duplication in '{title}'")
                        break
                        
                # Check for broken image references
                if re.search(r'figure\d+\.png|image\d+\.jpg', content):
                    quality_issues.append(f"Broken image references in '{title}'")
                    
                # Check for empty code blocks
                empty_code_pattern = r'<pre><code[^>]*>\s*</code></pre>'
                if re.search(empty_code_pattern, content):
                    quality_issues.append(f"Empty code blocks in '{title}'")
                    
                # Check for professional content structure
                if len(content) < 500:
                    quality_issues.append(f"Insufficient content length in '{title}' ({len(content)} chars)")
                    
            if len(quality_issues) == 0:
                await self.log_finding("Content Quality Verification", "✅ PASSED", 
                                     f"All {len(articles)} articles passed quality checks")
                return True
            else:
                await self.log_finding("Content Quality Verification", "❌ FAILED", 
                                     f"Found {len(quality_issues)} quality issues: {'; '.join(quality_issues[:3])}")
                return False
                
        except Exception as e:
            await self.log_finding("Content Quality Verification", "❌ ERROR", f"Exception: {str(e)}")
            return False
            
    async def test_database_storage_validation(self) -> bool:
        """Test 7: Database Storage Validation"""
        try:
            print("🔍 TESTING DATABASE STORAGE VALIDATION...")
            
            # Get current article count
            async with self.session.get(f"{API_BASE}/content-library") as response:
                if response.status == 200:
                    data = await response.json()
                    total_articles = data.get('total', 0)
                    articles = data.get('articles', [])
                    
                    if total_articles > 0 and len(articles) > 0:
                        # Check article metadata structure
                        sample_article = articles[0]
                        required_fields = ['id', 'title', 'content', 'status', 'created_at']
                        missing_fields = [field for field in required_fields if field not in sample_article]
                        
                        if len(missing_fields) == 0:
                            await self.log_finding("Database Storage Validation", "✅ PASSED", 
                                                 f"Found {total_articles} articles with proper metadata structure")
                            return True
                        else:
                            await self.log_finding("Database Storage Validation", "❌ FAILED", 
                                                 f"Articles missing required fields: {missing_fields}")
                            return False
                    else:
                        await self.log_finding("Database Storage Validation", "❌ FAILED", 
                                             "No articles found in database")
                        return False
                else:
                    await self.log_finding("Database Storage Validation", "❌ FAILED", 
                                         f"Content Library API returned status {response.status}")
                    return False
                    
        except Exception as e:
            await self.log_finding("Database Storage Validation", "❌ ERROR", f"Exception: {str(e)}")
            return False
            
    async def run_comprehensive_validation(self):
        """Run all validation tests"""
        print("🚀 STARTING COMPREHENSIVE CONTENT LIBRARY FIX VALIDATION")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Run all tests
            test_methods = [
                ('real_content_processing', self.test_real_content_processing),
                ('ordered_lists_fixed', self.test_ordered_lists_validation),
                ('overview_vs_complete_guide', self.test_overview_vs_complete_guide_separation),
                ('faq_standardization', self.test_faq_standardization),
                ('wysiwyg_features', self.test_wysiwyg_editor_features),
                ('content_quality', self.test_content_quality_verification),
                ('database_storage', self.test_database_storage_validation),
            ]
            
            for test_key, test_method in test_methods:
                print(f"\n{'='*60}")
                result = await test_method()
                self.test_results[test_key] = result
                await asyncio.sleep(2)  # Brief pause between tests
                
        finally:
            await self.cleanup_session()
            
        # Generate final report
        await self.generate_final_report()
        
    async def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE VALIDATION REPORT")
        print("="*80)
        
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n🎯 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
            
        print(f"\n📝 DETAILED FINDINGS:")
        for finding in self.detailed_findings[-10:]:  # Show last 10 findings
            print(f"   {finding['status']} {finding['test']}: {finding['details']}")
            
        # Critical success criteria
        critical_tests = ['real_content_processing', 'content_quality', 'database_storage']
        critical_passed = sum(1 for test in critical_tests if self.test_results.get(test, False))
        
        print(f"\n🔥 CRITICAL SUCCESS CRITERIA: {critical_passed}/{len(critical_tests)} passed")
        
        if success_rate >= 80 and critical_passed == len(critical_tests):
            print(f"\n🎉 VALIDATION SUCCESSFUL: Content Library fixes are working correctly!")
            print(f"✅ Real content processing operational")
            print(f"✅ Quality fixes applied successfully") 
            print(f"✅ Database storage working properly")
        else:
            print(f"\n⚠️ VALIDATION ISSUES DETECTED: Some fixes need attention")
            failed_tests = [test for test, result in self.test_results.items() if not result]
            print(f"❌ Failed tests: {', '.join(failed_tests)}")

async def main():
    """Main test execution"""
    validator = ContentLibraryFixValidator()
    await validator.run_comprehensive_validation()

if __name__ == "__main__":
    asyncio.run(main())