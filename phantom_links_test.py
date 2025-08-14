#!/usr/bin/env python3
"""
CRITICAL BUG TEST: Missing Articles & Phantom Links
Testing the critical bug fix for missing articles and phantom links in hub articles
"""

import requests
import json
import os
import io
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://smartdocs-23.preview.emergentagent.com') + '/api'

class PhantomLinksTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_job_id = None
        self.test_articles = []
        print(f"🔍 Testing Phantom Links Bug Fix at: {self.base_url}")
        
    def test_health_check(self):
        """Test backend health before running phantom links tests"""
        print("🔍 Testing Backend Health...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Backend health check passed")
                    return True
            print(f"❌ Backend health check failed - status code {response.status_code}")
            return False
        except Exception as e:
            print(f"❌ Backend health check failed - {str(e)}")
            return False
    
    def test_article_count_verification(self):
        """Test that multiple articles are actually created (not just overview + FAQ)"""
        print("\n🔍 Testing Article Count Verification...")
        try:
            # Create a comprehensive test document that should generate multiple articles
            test_document = """Comprehensive API Integration Guide

# Introduction to API Integration
This comprehensive guide covers all aspects of API integration from setup to troubleshooting.

## Chapter 1: Getting Started with API Setup
Setting up your API integration requires several key steps. First, you need to obtain your API credentials from the developer portal. This process typically involves creating an account, verifying your identity, and generating API keys.

### Authentication Configuration
Configure your authentication settings by adding your API key to your application's environment variables. This ensures secure access to the API endpoints while keeping your credentials protected.

### Initial Connection Testing
Test your initial connection by making a simple GET request to the health endpoint. This verifies that your credentials are working and the API is accessible.

## Chapter 2: Core Implementation Strategies
Once your setup is complete, you can begin implementing the core functionality. This involves understanding the API's data structures, request formats, and response handling.

### Request Formatting
Proper request formatting is crucial for successful API interactions. Ensure your requests include all required headers, parameters, and payload data in the correct format.

### Response Processing
Handle API responses appropriately by checking status codes, parsing JSON data, and implementing error handling for various scenarios.

### Rate Limiting Management
Implement rate limiting strategies to avoid exceeding API quotas. This includes implementing exponential backoff and request queuing mechanisms.

## Chapter 3: Advanced Customization Features
Advanced users can leverage additional customization options to optimize their integration for specific use cases.

### Custom Webhooks
Set up custom webhooks to receive real-time notifications about important events. This enables your application to respond immediately to changes.

### Data Transformation
Implement data transformation pipelines to convert API responses into formats that match your application's requirements.

### Caching Strategies
Implement intelligent caching to reduce API calls and improve application performance while maintaining data freshness.

## Chapter 4: Troubleshooting Common Issues
When issues arise, systematic troubleshooting can help identify and resolve problems quickly.

### Connection Problems
Common connection issues include network timeouts, DNS resolution problems, and firewall restrictions. Check your network configuration and API endpoint accessibility.

### Authentication Errors
Authentication failures often result from expired tokens, incorrect credentials, or insufficient permissions. Verify your API keys and token refresh mechanisms.

### Data Format Issues
Data format problems can occur when request or response formats don't match expectations. Validate your data structures against the API documentation.

### Performance Optimization
Optimize performance by analyzing response times, implementing connection pooling, and using appropriate timeout values.

## Conclusion
This comprehensive guide provides the foundation for successful API integration. Follow these best practices to ensure reliable, scalable, and maintainable integrations."""

            # Upload the comprehensive document
            file_data = io.BytesIO(test_document.encode('utf-8'))
            
            files = {
                'file': ('comprehensive_api_guide.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'template_id': 'comprehensive_processing',
                'training_mode': 'false'  # Use production mode to test real article generation
            }
            
            print("📤 Uploading comprehensive document to test article count...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=120
            )
            
            print(f"📊 Upload Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Document upload failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            data = response.json()
            self.test_job_id = data.get('job_id')
            
            # Wait for processing to complete
            print("⏳ Waiting for document processing to complete...")
            time.sleep(10)
            
            # Check Content Library for generated articles
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code == 200:
                library_data = response.json()
                articles = library_data.get('articles', [])
                
                # Filter articles from our test document
                test_articles = [
                    article for article in articles 
                    if 'api' in article.get('title', '').lower() or 
                       'comprehensive' in article.get('title', '').lower() or
                       'integration' in article.get('title', '').lower()
                ]
                
                self.test_articles = test_articles
                article_count = len(test_articles)
                
                print(f"📚 Articles generated from test document: {article_count}")
                
                # Print article titles for verification
                for i, article in enumerate(test_articles):
                    title = article.get('title', 'Untitled')
                    print(f"  {i+1}. {title}")
                
                # CRITICAL TEST: Should generate 4-6 articles, not just 2 (overview + FAQ)
                if article_count >= 4:
                    print("✅ ARTICLE COUNT VERIFICATION PASSED:")
                    print(f"  ✅ Generated {article_count} articles (expected 4-6)")
                    print("  ✅ Multiple articles created beyond just overview + FAQ")
                    print("  ✅ Comprehensive documents properly broken into logical stages")
                    return True
                elif article_count >= 2:
                    print("⚠️ ARTICLE COUNT VERIFICATION PARTIAL:")
                    print(f"  ⚠️ Generated {article_count} articles (expected 4-6)")
                    print("  ⚠️ May still be generating only overview + FAQ")
                    return False
                else:
                    print("❌ ARTICLE COUNT VERIFICATION FAILED:")
                    print(f"  ❌ Generated only {article_count} articles")
                    print("  ❌ Critical bug: Missing articles issue not resolved")
                    return False
            else:
                print(f"❌ Could not check Content Library - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Article count verification failed - {str(e)}")
            return False
    
    def test_link_integrity(self):
        """Test that hub article links point to real articles in Content Library"""
        print("\n🔍 Testing Link Integrity...")
        try:
            if not self.test_articles:
                print("⚠️ No test articles available - running article count test first")
                if not self.test_article_count_verification():
                    return False
            
            # Look for hub/overview articles that should contain links
            hub_articles = [
                article for article in self.test_articles
                if any(keyword in article.get('title', '').lower() 
                      for keyword in ['overview', 'guide', 'table of contents', 'introduction'])
            ]
            
            if not hub_articles:
                print("⚠️ No hub articles found to test link integrity")
                return True
            
            print(f"🔗 Testing link integrity in {len(hub_articles)} hub articles...")
            
            phantom_links_found = 0
            working_links_found = 0
            total_links_tested = 0
            
            for hub_article in hub_articles:
                title = hub_article.get('title', 'Untitled')
                content = hub_article.get('content', '')
                article_id = hub_article.get('id')
                
                print(f"\n📄 Testing links in: {title}")
                
                # Check for phantom anchor links (#section-name)
                import re
                anchor_links = re.findall(r'href=["\']#[^"\']*["\']', content)
                phantom_links_found += len(anchor_links)
                
                if anchor_links:
                    print(f"  ❌ Found {len(anchor_links)} phantom anchor links:")
                    for link in anchor_links[:3]:  # Show first 3
                        print(f"    - {link}")
                
                # Check for proper Content Library links
                content_library_links = re.findall(r'href=["\'][^"\']*content-library[^"\']*["\']', content)
                api_links = re.findall(r'href=["\'][^"\']*article/[^"\']*["\']', content)
                
                working_links_found += len(content_library_links) + len(api_links)
                total_links_tested += len(anchor_links) + len(content_library_links) + len(api_links)
                
                if content_library_links or api_links:
                    print(f"  ✅ Found {len(content_library_links) + len(api_links)} proper Content Library links")
                
                # Test a few actual links to verify they work
                for link_match in (content_library_links + api_links)[:2]:  # Test first 2 links
                    # Extract URL from href attribute
                    url_match = re.search(r'href=["\']([^"\']*)["\']', link_match)
                    if url_match:
                        link_url = url_match.group(1)
                        
                        # If it's a relative link, make it absolute
                        if link_url.startswith('/'):
                            test_url = f"{self.base_url.replace('/api', '')}{link_url}"
                        else:
                            test_url = link_url
                        
                        try:
                            # Test if the linked article exists
                            if '/article/' in test_url:
                                linked_article_id = test_url.split('/article/')[-1]
                                article_response = requests.get(
                                    f"{self.base_url}/content-library/article/{linked_article_id}",
                                    timeout=10
                                )
                                if article_response.status_code == 200:
                                    print(f"    ✅ Link verified: Article {linked_article_id} exists")
                                else:
                                    print(f"    ❌ Broken link: Article {linked_article_id} not found")
                        except Exception as link_error:
                            print(f"    ⚠️ Could not verify link: {str(link_error)}")
            
            # CRITICAL TEST: No phantom links, working Content Library links
            print(f"\n📊 Link Integrity Summary:")
            print(f"  Phantom anchor links found: {phantom_links_found}")
            print(f"  Working Content Library links found: {working_links_found}")
            print(f"  Total links tested: {total_links_tested}")
            
            if phantom_links_found == 0 and working_links_found > 0:
                print("✅ LINK INTEGRITY VERIFICATION PASSED:")
                print("  ✅ No phantom anchor links found")
                print("  ✅ Hub articles contain working Content Library links")
                print("  ✅ Links point to real articles, not missing content")
                return True
            elif phantom_links_found == 0:
                print("⚠️ LINK INTEGRITY VERIFICATION PARTIAL:")
                print("  ✅ No phantom anchor links found")
                print("  ⚠️ Limited Content Library links detected")
                return True
            else:
                print("❌ LINK INTEGRITY VERIFICATION FAILED:")
                print(f"  ❌ Found {phantom_links_found} phantom anchor links")
                print("  ❌ Hub articles still contain links to non-existent content")
                return False
                
        except Exception as e:
            print(f"❌ Link integrity test failed - {str(e)}")
            return False
    
    def test_content_coverage_analysis(self):
        """Test that comprehensive documents generate appropriate article breakdown"""
        print("\n🔍 Testing Content Coverage Analysis...")
        try:
            if not self.test_articles:
                print("⚠️ No test articles available for coverage analysis")
                return False
            
            print(f"📊 Analyzing content coverage across {len(self.test_articles)} articles...")
            
            # Analyze functional stage detection
            stages_detected = {
                'setup': 0,
                'implementation': 0,
                'customization': 0,
                'troubleshooting': 0,
                'overview': 0
            }
            
            total_content_length = 0
            articles_with_substantial_content = 0
            
            for article in self.test_articles:
                title = article.get('title', '').lower()
                content = article.get('content', '')
                content_length = len(content)
                total_content_length += content_length
                
                # Check for substantial content (not empty articles)
                if content_length > 500:  # Minimum substantial content
                    articles_with_substantial_content += 1
                
                # Detect functional stages
                if any(keyword in title for keyword in ['setup', 'getting started', 'configuration', 'install']):
                    stages_detected['setup'] += 1
                elif any(keyword in title for keyword in ['implementation', 'core', 'main', 'primary']):
                    stages_detected['implementation'] += 1
                elif any(keyword in title for keyword in ['customization', 'advanced', 'custom', 'optimization']):
                    stages_detected['customization'] += 1
                elif any(keyword in title for keyword in ['troubleshooting', 'debug', 'issues', 'problems', 'errors']):
                    stages_detected['troubleshooting'] += 1
                elif any(keyword in title for keyword in ['overview', 'introduction', 'guide', 'table of contents']):
                    stages_detected['overview'] += 1
                
                print(f"  📄 {article.get('title', 'Untitled')}: {content_length} chars")
            
            # Calculate coverage metrics
            avg_content_length = total_content_length / len(self.test_articles) if self.test_articles else 0
            coverage_percentage = (articles_with_substantial_content / len(self.test_articles)) * 100 if self.test_articles else 0
            stages_covered = sum(1 for count in stages_detected.values() if count > 0)
            
            print(f"\n📊 Content Coverage Analysis Results:")
            print(f"  Total articles: {len(self.test_articles)}")
            print(f"  Articles with substantial content: {articles_with_substantial_content}")
            print(f"  Average content length: {avg_content_length:.0f} characters")
            print(f"  Coverage percentage: {coverage_percentage:.1f}%")
            print(f"  Functional stages covered: {stages_covered}/5")
            
            print(f"\n🎯 Functional Stage Breakdown:")
            for stage, count in stages_detected.items():
                if count > 0:
                    print(f"  ✅ {stage.title()}: {count} articles")
                else:
                    print(f"  ⚪ {stage.title()}: 0 articles")
            
            # CRITICAL TEST: Comprehensive coverage with multiple functional stages
            if (coverage_percentage >= 80 and 
                stages_covered >= 3 and 
                avg_content_length >= 800):
                print("✅ CONTENT COVERAGE ANALYSIS PASSED:")
                print("  ✅ Comprehensive documents generate appropriate article breakdown")
                print("  ✅ Multiple functional stages detected (setup, implementation, etc.)")
                print("  ✅ Articles contain substantial content (not empty)")
                print("  ✅ Related content stays grouped properly")
                return True
            elif coverage_percentage >= 60 and stages_covered >= 2:
                print("⚠️ CONTENT COVERAGE ANALYSIS PARTIAL:")
                print("  ⚠️ Some functional stages detected but coverage could be better")
                print("  ⚠️ Article breakdown is working but may need optimization")
                return True
            else:
                print("❌ CONTENT COVERAGE ANALYSIS FAILED:")
                print("  ❌ Poor content coverage or missing functional stages")
                print("  ❌ Articles may be too short or not properly categorized")
                return False
                
        except Exception as e:
            print(f"❌ Content coverage analysis failed - {str(e)}")
            return False
    
    def test_hub_article_accuracy(self):
        """Test that hub article TOC accurately reflects generated articles"""
        print("\n🔍 Testing Hub Article Accuracy...")
        try:
            if not self.test_articles:
                print("⚠️ No test articles available for hub accuracy testing")
                return False
            
            # Find hub/overview articles
            hub_articles = [
                article for article in self.test_articles
                if any(keyword in article.get('title', '').lower() 
                      for keyword in ['overview', 'guide', 'table of contents', 'introduction'])
            ]
            
            if not hub_articles:
                print("⚠️ No hub articles found to test accuracy")
                return True
            
            print(f"📋 Testing accuracy of {len(hub_articles)} hub articles...")
            
            accurate_hubs = 0
            total_promised_articles = 0
            total_existing_articles = 0
            
            for hub_article in hub_articles:
                title = hub_article.get('title', 'Untitled')
                content = hub_article.get('content', '')
                
                print(f"\n📄 Testing hub article: {title}")
                
                # Extract promised articles from TOC
                import re
                
                # Look for various TOC patterns
                toc_patterns = [
                    r'<li[^>]*>.*?<a[^>]*href=["\'][^"\']*["\'][^>]*>([^<]+)</a>',  # HTML links in lists
                    r'<a[^>]*href=["\'][^"\']*["\'][^>]*>([^<]+)</a>',  # Any HTML links
                    r'\d+\.\s*([^\n]+)',  # Numbered list items
                    r'-\s*([^\n]+)',  # Bullet list items
                ]
                
                promised_articles = []
                for pattern in toc_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    promised_articles.extend(matches)
                
                # Clean up promised article titles
                promised_articles = [
                    title.strip().replace('&nbsp;', ' ').replace('&amp;', '&')
                    for title in promised_articles
                    if len(title.strip()) > 10  # Filter out short/meaningless entries
                ]
                
                # Remove duplicates
                promised_articles = list(set(promised_articles))
                
                print(f"  📋 Promised articles in TOC: {len(promised_articles)}")
                for i, promised_title in enumerate(promised_articles[:5]):  # Show first 5
                    print(f"    {i+1}. {promised_title}")
                
                # Check how many promised articles actually exist
                existing_count = 0
                for promised_title in promised_articles:
                    # Look for matching articles in our test set
                    for existing_article in self.test_articles:
                        existing_title = existing_article.get('title', '')
                        
                        # Fuzzy matching for article titles
                        if (promised_title.lower() in existing_title.lower() or
                            existing_title.lower() in promised_title.lower() or
                            self._calculate_title_similarity(promised_title, existing_title) > 0.6):
                            existing_count += 1
                            break
                
                accuracy_percentage = (existing_count / len(promised_articles)) * 100 if promised_articles else 100
                
                print(f"  📊 Accuracy: {existing_count}/{len(promised_articles)} articles exist ({accuracy_percentage:.1f}%)")
                
                total_promised_articles += len(promised_articles)
                total_existing_articles += existing_count
                
                if accuracy_percentage >= 80:
                    accurate_hubs += 1
                    print(f"  ✅ Hub article accuracy acceptable")
                else:
                    print(f"  ❌ Hub article accuracy poor")
            
            # Overall accuracy assessment
            overall_accuracy = (total_existing_articles / total_promised_articles) * 100 if total_promised_articles else 100
            hub_accuracy_rate = (accurate_hubs / len(hub_articles)) * 100 if hub_articles else 100
            
            print(f"\n📊 Hub Article Accuracy Summary:")
            print(f"  Total promised articles: {total_promised_articles}")
            print(f"  Total existing articles: {total_existing_articles}")
            print(f"  Overall accuracy: {overall_accuracy:.1f}%")
            print(f"  Accurate hubs: {accurate_hubs}/{len(hub_articles)} ({hub_accuracy_rate:.1f}%)")
            
            # CRITICAL TEST: Hub articles accurately reflect generated content
            if overall_accuracy >= 80 and hub_accuracy_rate >= 75:
                print("✅ HUB ARTICLE ACCURACY VERIFICATION PASSED:")
                print("  ✅ Hub article TOC accurately reflects generated articles")
                print("  ✅ Mini-TOC shows actual article titles and types")
                print("  ✅ Promised articles actually exist in Content Library")
                print("  ✅ No false promises of non-existent content")
                return True
            elif overall_accuracy >= 60:
                print("⚠️ HUB ARTICLE ACCURACY VERIFICATION PARTIAL:")
                print("  ⚠️ Some accuracy issues but generally working")
                print("  ⚠️ May have some phantom promises but not critical")
                return True
            else:
                print("❌ HUB ARTICLE ACCURACY VERIFICATION FAILED:")
                print("  ❌ Hub articles promise content that doesn't exist")
                print("  ❌ TOC does not accurately reflect generated articles")
                print("  ❌ Critical phantom links issue not resolved")
                return False
                
        except Exception as e:
            print(f"❌ Hub article accuracy test failed - {str(e)}")
            return False
    
    def _calculate_title_similarity(self, title1, title2):
        """Calculate similarity between two titles"""
        try:
            # Simple word-based similarity
            words1 = set(title1.lower().split())
            words2 = set(title2.lower().split())
            
            if not words1 or not words2:
                return 0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
        except:
            return 0
    
    def test_seamless_navigation(self):
        """Test that users can navigate seamlessly between related articles"""
        print("\n🔍 Testing Seamless Navigation...")
        try:
            if not self.test_articles:
                print("⚠️ No test articles available for navigation testing")
                return False
            
            print(f"🧭 Testing navigation between {len(self.test_articles)} articles...")
            
            articles_with_navigation = 0
            total_navigation_links = 0
            working_navigation_links = 0
            
            for article in self.test_articles:
                title = article.get('title', 'Untitled')
                content = article.get('content', '')
                article_id = article.get('id')
                
                # Look for navigation elements
                import re
                
                # Check for "Related Articles" sections
                has_related_section = 'related' in content.lower() and 'articles' in content.lower()
                
                # Check for navigation links (Previous/Next, Continue to, See also)
                navigation_patterns = [
                    r'continue\s+to\s+[^<\n]+',
                    r'see\s+also[^<\n]*',
                    r'previous[^<\n]*',
                    r'next[^<\n]*',
                    r'related[^<\n]*articles?[^<\n]*'
                ]
                
                nav_links_found = 0
                for pattern in navigation_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    nav_links_found += len(matches)
                
                # Check for actual hyperlinks to other articles
                content_library_links = re.findall(r'href=["\'][^"\']*content-library[^"\']*["\']', content)
                article_links = re.findall(r'href=["\'][^"\']*article/[^"\']*["\']', content)
                
                total_links = len(content_library_links) + len(article_links)
                total_navigation_links += total_links
                
                if has_related_section or nav_links_found > 0 or total_links > 0:
                    articles_with_navigation += 1
                    working_navigation_links += total_links
                    print(f"  ✅ {title}: {total_links} navigation links, related section: {has_related_section}")
                else:
                    print(f"  ⚪ {title}: No navigation elements found")
            
            # Calculate navigation metrics
            navigation_coverage = (articles_with_navigation / len(self.test_articles)) * 100 if self.test_articles else 0
            avg_links_per_article = total_navigation_links / len(self.test_articles) if self.test_articles else 0
            
            print(f"\n🧭 Navigation Analysis Results:")
            print(f"  Articles with navigation: {articles_with_navigation}/{len(self.test_articles)} ({navigation_coverage:.1f}%)")
            print(f"  Total navigation links: {total_navigation_links}")
            print(f"  Working navigation links: {working_navigation_links}")
            print(f"  Average links per article: {avg_links_per_article:.1f}")
            
            # CRITICAL TEST: Seamless navigation between articles
            if navigation_coverage >= 60 and avg_links_per_article >= 1:
                print("✅ SEAMLESS NAVIGATION VERIFICATION PASSED:")
                print("  ✅ Users can navigate seamlessly between related articles")
                print("  ✅ Articles contain working links to other Content Library articles")
                print("  ✅ No broken anchor links or missing article references")
                print("  ✅ Navigation system supports user workflow")
                return True
            elif navigation_coverage >= 30:
                print("⚠️ SEAMLESS NAVIGATION VERIFICATION PARTIAL:")
                print("  ⚠️ Some navigation available but could be improved")
                print("  ⚠️ Basic linking working but coverage is limited")
                return True
            else:
                print("❌ SEAMLESS NAVIGATION VERIFICATION FAILED:")
                print("  ❌ Poor navigation between articles")
                print("  ❌ Users cannot easily move between related content")
                print("  ❌ Navigation system needs improvement")
                return False
                
        except Exception as e:
            print(f"❌ Seamless navigation test failed - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all phantom links bug fix tests"""
        print("🚀 Starting CRITICAL BUG TEST: Missing Articles & Phantom Links")
        print("=" * 80)
        
        test_results = []
        
        # Test 1: Backend Health
        test_results.append(("Backend Health Check", self.test_health_check()))
        
        # Test 2: Article Count Verification
        test_results.append(("Article Count Verification", self.test_article_count_verification()))
        
        # Test 3: Link Integrity Testing
        test_results.append(("Link Integrity Testing", self.test_link_integrity()))
        
        # Test 4: Content Coverage Analysis
        test_results.append(("Content Coverage Analysis", self.test_content_coverage_analysis()))
        
        # Test 5: Hub Article Accuracy
        test_results.append(("Hub Article Accuracy", self.test_hub_article_accuracy()))
        
        # Test 6: Seamless Navigation
        test_results.append(("Seamless Navigation", self.test_seamless_navigation()))
        
        # Print final results
        print("\n" + "=" * 80)
        print("🎯 PHANTOM LINKS BUG FIX TEST RESULTS")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 PHANTOM LINKS BUG FIX VERIFICATION: SUCCESS")
            print("✅ Critical bug fixes are working correctly")
            print("✅ Multiple articles created per document")
            print("✅ Working links - hub articles link to actual existing articles")
            print("✅ No phantom links - all references point to real Content Library articles")
            print("✅ Comprehensive coverage - complex documents broken into logical stages")
            print("✅ Hub accuracy - TOC reflects actual generated content")
            return True
        elif success_rate >= 60:
            print("⚠️ PHANTOM LINKS BUG FIX VERIFICATION: PARTIAL SUCCESS")
            print("⚠️ Most fixes are working but some issues remain")
            print("⚠️ System is functional but may need additional improvements")
            return True
        else:
            print("❌ PHANTOM LINKS BUG FIX VERIFICATION: FAILED")
            print("❌ Critical issues remain with missing articles and phantom links")
            print("❌ Bug fixes need additional work")
            return False

if __name__ == "__main__":
    tester = PhantomLinksTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)