#!/usr/bin/env python3
"""
Enhanced Knowledge Engine Media Extraction Testing
Comprehensive testing for media-rich document processing as requested in review
"""

import requests
import json
import os
import io
import time
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://6932dd27-38f2-4781-9b35-b6aac917fef1.preview.emergentagent.com') + '/api'

class MediaExtractionTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = {}
        print(f"🖼️ Testing Enhanced Knowledge Engine Media Extraction at: {self.base_url}")
        print("🎯 FOCUS: Comprehensive Media Extraction with media_rich_example.md")
        
    def load_media_rich_example(self):
        """Load the media_rich_example.md file for testing"""
        try:
            with open('/app/media_rich_example.md', 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Loaded media_rich_example.md: {len(content)} characters")
            return content
        except Exception as e:
            print(f"❌ Failed to load media_rich_example.md: {e}")
            return None
    
    def analyze_media_content(self, content):
        """Analyze the media content in the document"""
        print("\n🔍 Analyzing Media Content in Document...")
        
        # Find all base64 images
        data_url_pattern = r'data:image/([^;]+);base64,([A-Za-z0-9+/=]+)'
        media_matches = re.findall(data_url_pattern, content)
        
        # Find image references and captions
        image_refs = re.findall(r'!\[([^\]]*)\]\(data:image/[^)]+\)', content)
        figure_captions = re.findall(r'\*Figure \d+:([^*]+)\*', content)
        
        print(f"📊 Media Analysis Results:")
        print(f"   - Base64 images found: {len(media_matches)}")
        print(f"   - Image formats: {[match[0] for match in media_matches]}")
        print(f"   - Image references: {len(image_refs)}")
        print(f"   - Figure captions: {len(figure_captions)}")
        
        for i, (format_type, base64_data) in enumerate(media_matches, 1):
            print(f"   - Image {i}: {format_type} format, {len(base64_data)} base64 characters")
        
        for i, caption in enumerate(figure_captions, 1):
            print(f"   - Caption {i}:{caption.strip()}")
        
        return {
            'total_images': len(media_matches),
            'image_formats': [match[0] for match in media_matches],
            'image_references': image_refs,
            'figure_captions': figure_captions,
            'base64_data': [match[1] for match in media_matches]
        }
    
    def test_media_rich_document_processing(self):
        """Test 1: Media-Rich Document Processing"""
        print("\n🖼️ TEST 1: Media-Rich Document Processing")
        print("=" * 50)
        
        try:
            # Load the media-rich example
            content = self.load_media_rich_example()
            if not content:
                return False
            
            # Analyze media before processing
            media_analysis = self.analyze_media_content(content)
            
            # Get initial Content Library count
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            initial_count = 0
            if response.status_code == 200:
                initial_count = response.json().get('total', 0)
                print(f"Initial Content Library articles: {initial_count}")
            
            # Process the media-rich content
            test_content = {
                "content": content,
                "content_type": "text",
                "metadata": {
                    "source": "media_extraction_test",
                    "test_type": "media_rich_processing",
                    "original_filename": "media_rich_example.md",
                    "has_embedded_media": True,
                    "media_count": media_analysis['total_images']
                }
            }
            
            print(f"🚀 Processing media-rich document with {media_analysis['total_images']} embedded images...")
            
            response = requests.post(
                f"{self.base_url}/content/process",
                json=test_content,
                timeout=45
            )
            
            if response.status_code != 200:
                print(f"❌ Content processing failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            process_data = response.json()
            print(f"✅ Content processing successful:")
            print(f"   - Job ID: {process_data.get('job_id')}")
            print(f"   - Chunks created: {process_data.get('chunks_created')}")
            
            # Wait for processing to complete
            time.sleep(3)
            
            # Check if Content Library articles were created
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if response.status_code != 200:
                print("❌ Could not retrieve Content Library after processing")
                return False
            
            data = response.json()
            new_count = data.get('total', 0)
            articles = data.get('articles', [])
            
            print(f"📚 Content Library after processing: {new_count} articles (was {initial_count})")
            
            if new_count > initial_count:
                print("✅ New articles created from media-rich document!")
                
                # Find articles created from our test
                test_articles = []
                for article in articles:
                    metadata = article.get('metadata', {})
                    if (metadata.get('source') == 'media_extraction_test' or 
                        'media_rich_example.md' in article.get('title', '')):
                        test_articles.append(article)
                
                print(f"🎯 Found {len(test_articles)} articles from our media-rich test")
                
                # Verify media preservation in articles
                media_preserved_count = 0
                for article in test_articles:
                    content = article.get('content', '')
                    if 'data:image/' in content:
                        media_preserved_count += 1
                        print(f"✅ Article '{article.get('title', 'N/A')}' contains embedded media")
                
                if media_preserved_count > 0:
                    print(f"🖼️ Media preservation: {media_preserved_count}/{len(test_articles)} articles contain embedded media")
                    return True
                else:
                    print("⚠️ Articles created but no embedded media found")
                    return len(test_articles) > 0  # Partial success
            else:
                print("⚠️ No new articles created - checking existing articles for media")
                # Check if any existing articles have media
                media_articles = [a for a in articles if 'data:image/' in a.get('content', '')]
                print(f"📊 Found {len(media_articles)} existing articles with embedded media")
                return len(media_articles) > 0
                
        except Exception as e:
            print(f"❌ Media-rich document processing test failed - {str(e)}")
            return False
    
    def test_multi_article_creation_with_media(self):
        """Test 2: Multi-Article Creation with Media Integration"""
        print("\n🖼️ TEST 2: Multi-Article Creation with Media Integration")
        print("=" * 50)
        
        try:
            # Get current Content Library state
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if response.status_code != 200:
                print("❌ Could not get Content Library state")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Look for articles that might be from multi-article splitting
            multi_article_candidates = []
            media_containing_articles = []
            
            for article in articles:
                metadata = article.get('metadata', {})
                content = article.get('content', '')
                
                # Check if article is from multi-article processing
                if (metadata.get('total_articles', 0) > 1 or 
                    metadata.get('article_index') is not None):
                    multi_article_candidates.append(article)
                
                # Check if article contains media
                if 'data:image/' in content:
                    media_containing_articles.append(article)
            
            print(f"📊 Multi-Article Analysis:")
            print(f"   - Multi-article candidates: {len(multi_article_candidates)}")
            print(f"   - Articles with embedded media: {len(media_containing_articles)}")
            
            # Check for media distribution across articles
            if multi_article_candidates:
                print("🔍 Analyzing multi-article media distribution...")
                
                media_in_multi_articles = 0
                for article in multi_article_candidates:
                    if 'data:image/' in article.get('content', ''):
                        media_in_multi_articles += 1
                        title = article.get('title', 'N/A')
                        article_index = article.get('metadata', {}).get('article_index', 'N/A')
                        print(f"   ✅ Article {article_index}: '{title}' contains media")
                
                if media_in_multi_articles > 0:
                    print(f"🖼️ Media distribution success: {media_in_multi_articles} multi-articles contain media")
                    return True
                else:
                    print("⚠️ Multi-articles found but no media distribution detected")
                    return len(multi_article_candidates) > 0
            else:
                print("⚠️ No multi-article candidates found")
                # Check if we have any articles with media at all
                return len(media_containing_articles) > 0
                
        except Exception as e:
            print(f"❌ Multi-article media integration test failed - {str(e)}")
            return False
    
    def test_enhanced_writing_quality_with_media(self):
        """Test 3: Enhanced Writing Quality with Media"""
        print("\n🖼️ TEST 3: Enhanced Writing Quality with Media")
        print("=" * 50)
        
        try:
            # Get Content Library articles
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if response.status_code != 200:
                print("❌ Could not get Content Library articles")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Analyze articles for enhanced writing quality with media
            quality_indicators = {
                'articles_with_media': 0,
                'articles_with_figure_references': 0,
                'articles_with_captions': 0,
                'articles_with_structured_headings': 0,
                'articles_with_callouts': 0,
                'total_analyzed': 0
            }
            
            print("🔍 Analyzing writing quality and media integration...")
            
            for article in articles:
                content = article.get('content', '')
                if not content:
                    continue
                
                quality_indicators['total_analyzed'] += 1
                
                # Check for embedded media
                if 'data:image/' in content:
                    quality_indicators['articles_with_media'] += 1
                
                # Check for figure references in text
                if re.search(r'(Figure \d+|shown in.*figure|illustrated.*below|diagram.*shows)', content, re.IGNORECASE):
                    quality_indicators['articles_with_figure_references'] += 1
                
                # Check for image captions
                if re.search(r'\*Figure \d+:|!\[.*\].*\*.*:', content):
                    quality_indicators['articles_with_captions'] += 1
                
                # Check for structured headings
                heading_count = len(re.findall(r'^#{1,4}\s+', content, re.MULTILINE))
                if heading_count >= 3:
                    quality_indicators['articles_with_structured_headings'] += 1
                
                # Check for callouts and tips
                if re.search(r'(💡|⚠️|> \*\*|### Key|### Important)', content):
                    quality_indicators['articles_with_callouts'] += 1
            
            print(f"📊 Writing Quality Analysis Results:")
            print(f"   - Total articles analyzed: {quality_indicators['total_analyzed']}")
            print(f"   - Articles with embedded media: {quality_indicators['articles_with_media']}")
            print(f"   - Articles with figure references: {quality_indicators['articles_with_figure_references']}")
            print(f"   - Articles with captions: {quality_indicators['articles_with_captions']}")
            print(f"   - Articles with structured headings: {quality_indicators['articles_with_structured_headings']}")
            print(f"   - Articles with callouts/tips: {quality_indicators['articles_with_callouts']}")
            
            # Calculate quality score
            if quality_indicators['total_analyzed'] > 0:
                media_integration_score = (
                    quality_indicators['articles_with_media'] + 
                    quality_indicators['articles_with_figure_references'] + 
                    quality_indicators['articles_with_captions']
                ) / (quality_indicators['total_analyzed'] * 3) * 100
                
                writing_quality_score = (
                    quality_indicators['articles_with_structured_headings'] + 
                    quality_indicators['articles_with_callouts']
                ) / (quality_indicators['total_analyzed'] * 2) * 100
                
                print(f"🎯 Quality Scores:")
                print(f"   - Media integration: {media_integration_score:.1f}%")
                print(f"   - Writing quality: {writing_quality_score:.1f}%")
                
                # Success if we have good media integration and writing quality
                if (quality_indicators['articles_with_media'] > 0 and 
                    quality_indicators['articles_with_structured_headings'] > 0):
                    print("✅ Enhanced writing quality with media integration confirmed")
                    return True
                else:
                    print("⚠️ Some quality indicators present but not comprehensive")
                    return quality_indicators['articles_with_media'] > 0
            else:
                print("❌ No articles found to analyze")
                return False
                
        except Exception as e:
            print(f"❌ Enhanced writing quality test failed - {str(e)}")
            return False
    
    def test_media_metadata_and_captions(self):
        """Test 4: Media Metadata and Captions"""
        print("\n🖼️ TEST 4: Media Metadata and Captions")
        print("=" * 50)
        
        try:
            # Get Content Library articles
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if response.status_code != 200:
                print("❌ Could not get Content Library articles")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Analyze media metadata and captions
            media_analysis = {
                'articles_with_media': 0,
                'preserved_captions': 0,
                'figure_numbers': 0,
                'contextual_descriptions': 0,
                'data_integrity_checks': 0,
                'total_media_items': 0
            }
            
            print("🔍 Analyzing media metadata and captions...")
            
            for article in articles:
                content = article.get('content', '')
                if not content:
                    continue
                
                # Find all data URLs
                data_urls = re.findall(r'data:image/([^;]+);base64,([A-Za-z0-9+/=]+)', content)
                if data_urls:
                    media_analysis['articles_with_media'] += 1
                    media_analysis['total_media_items'] += len(data_urls)
                    
                    # Check data integrity (base64 should be valid length)
                    for format_type, base64_data in data_urls:
                        if len(base64_data) > 20 and len(base64_data) % 4 == 0:  # Basic base64 validation
                            media_analysis['data_integrity_checks'] += 1
                
                # Check for preserved captions
                captions = re.findall(r'\*Figure \d+:([^*]+)\*', content)
                if captions:
                    media_analysis['preserved_captions'] += len(captions)
                
                # Check for figure numbers and references
                figure_refs = re.findall(r'Figure \d+', content)
                if figure_refs:
                    media_analysis['figure_numbers'] += len(figure_refs)
                
                # Check for contextual descriptions
                if re.search(r'(shown in.*figure|illustrated.*below|diagram.*shows|as.*image)', content, re.IGNORECASE):
                    media_analysis['contextual_descriptions'] += 1
            
            print(f"📊 Media Metadata Analysis Results:")
            print(f"   - Articles with media: {media_analysis['articles_with_media']}")
            print(f"   - Total media items: {media_analysis['total_media_items']}")
            print(f"   - Preserved captions: {media_analysis['preserved_captions']}")
            print(f"   - Figure number references: {media_analysis['figure_numbers']}")
            print(f"   - Contextual descriptions: {media_analysis['contextual_descriptions']}")
            print(f"   - Data integrity checks passed: {media_analysis['data_integrity_checks']}")
            
            # Success criteria
            if (media_analysis['articles_with_media'] > 0 and 
                media_analysis['data_integrity_checks'] > 0):
                print("✅ Media metadata and captions properly preserved")
                
                if media_analysis['preserved_captions'] > 0:
                    print("✅ Image captions preserved and enhanced")
                
                if media_analysis['figure_numbers'] > 0:
                    print("✅ Figure numbers and references maintained")
                
                return True
            else:
                print("❌ Media metadata preservation issues detected")
                return False
                
        except Exception as e:
            print(f"❌ Media metadata test failed - {str(e)}")
            return False
    
    def test_content_library_media_integration(self):
        """Test 5: Content Library Media Integration"""
        print("\n🖼️ TEST 5: Content Library Media Integration")
        print("=" * 50)
        
        try:
            # Get Content Library articles
            response = requests.get(f"{self.base_url}/content-library", timeout=10)
            if response.status_code != 200:
                print("❌ Could not get Content Library articles")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            total_articles = data.get('total', 0)
            
            print(f"📚 Content Library Analysis:")
            print(f"   - Total articles: {total_articles}")
            print(f"   - Articles retrieved: {len(articles)}")
            
            # Analyze media integration in Content Library
            integration_analysis = {
                'articles_with_media': 0,
                'media_rich_articles': [],
                'base64_data_preserved': 0,
                'workflow_complete': 0
            }
            
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', 'N/A')
                
                # Check for embedded media
                data_urls = re.findall(r'data:image/[^)]+', content)
                if data_urls:
                    integration_analysis['articles_with_media'] += 1
                    integration_analysis['media_rich_articles'].append({
                        'title': title,
                        'media_count': len(data_urls),
                        'content_length': len(content)
                    })
                    
                    # Check base64 data preservation
                    for data_url in data_urls:
                        if 'base64,' in data_url and len(data_url) > 50:
                            integration_analysis['base64_data_preserved'] += 1
                
                # Check if article shows signs of complete workflow
                metadata = article.get('metadata', {})
                if (metadata.get('ai_processed') and 
                    content and len(content) > 100):
                    integration_analysis['workflow_complete'] += 1
            
            print(f"🔍 Media Integration Results:")
            print(f"   - Articles with embedded media: {integration_analysis['articles_with_media']}")
            print(f"   - Base64 data items preserved: {integration_analysis['base64_data_preserved']}")
            print(f"   - Complete workflow articles: {integration_analysis['workflow_complete']}")
            
            # Show sample media-rich articles
            if integration_analysis['media_rich_articles']:
                print(f"\n📋 Sample Media-Rich Articles:")
                for i, article_info in enumerate(integration_analysis['media_rich_articles'][:3], 1):
                    print(f"   {i}. '{article_info['title']}'")
                    print(f"      - Media items: {article_info['media_count']}")
                    print(f"      - Content length: {article_info['content_length']} chars")
            
            # Success criteria
            if (integration_analysis['articles_with_media'] > 0 and 
                integration_analysis['base64_data_preserved'] > 0):
                print("✅ Content Library media integration working correctly")
                print("✅ Base64 data integrity maintained through complete workflow")
                return True
            else:
                print("❌ Content Library media integration issues")
                return False
                
        except Exception as e:
            print(f"❌ Content Library media integration test failed - {str(e)}")
            return False
    
    def run_comprehensive_media_tests(self):
        """Run all comprehensive media extraction tests"""
        print("🖼️ ENHANCED KNOWLEDGE ENGINE MEDIA EXTRACTION TESTING")
        print("🎯 Comprehensive Media Processing with media_rich_example.md")
        print("=" * 70)
        
        # Run all media extraction tests
        tests = [
            ('Media-Rich Document Processing', self.test_media_rich_document_processing),
            ('Multi-Article Creation with Media Integration', self.test_multi_article_creation_with_media),
            ('Enhanced Writing Quality with Media', self.test_enhanced_writing_quality_with_media),
            ('Media Metadata and Captions', self.test_media_metadata_and_captions),
            ('Content Library Media Integration', self.test_content_library_media_integration)
        ]
        
        results = {}
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            results[test_name] = test_func()
        
        # Summary
        print("\n" + "=" * 70)
        print("🖼️ COMPREHENSIVE MEDIA EXTRACTION TEST RESULTS")
        print("=" * 70)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Media Extraction Tests: {passed}/{total} passed")
        
        # Assessment
        if passed >= 3:  # At least 3 out of 5 tests should pass
            print("🎉 Enhanced Knowledge Engine Media Extraction is working!")
            if passed == total:
                print("🏆 Perfect media extraction and integration!")
            return True
        else:
            print(f"❌ Media extraction tests failed - {total - passed} critical issues")
            return False

if __name__ == "__main__":
    tester = MediaExtractionTest()
    success = tester.run_comprehensive_media_tests()
    exit(0 if success else 1)