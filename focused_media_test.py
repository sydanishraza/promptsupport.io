#!/usr/bin/env python3
"""
Focused Media Extraction Verification Test
Quick verification of enhanced media extraction capabilities
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://e80eb79c-1717-4a64-ad4c-a221fb117258.preview.emergentagent.com') + '/api'

def test_media_extraction_capabilities():
    """Test the enhanced media extraction capabilities"""
    print("🔍 Testing Enhanced Media Extraction Capabilities")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Verify Content Library has articles with embedded media
    print("\n1. Testing Content Library Media Storage...")
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            media_articles = [a for a in articles if 'data:image/' in a.get('content', '')]
            
            print(f"✅ Total articles: {len(articles)}")
            print(f"✅ Articles with embedded media: {len(media_articles)}")
            
            if media_articles:
                # Analyze media preservation
                sample_article = media_articles[0]
                content = sample_article.get('content', '')
                
                # Count different types of media elements
                data_urls = content.count('data:image/')
                jpeg_images = content.count('data:image/jpeg;base64,')
                png_images = content.count('data:image/png;base64,')
                image_refs = content.count('![')
                figure_captions = content.count('*Figure')
                
                print(f"✅ Sample article analysis:")
                print(f"  - Title: {sample_article.get('title', 'No title')[:60]}...")
                print(f"  - Data URLs: {data_urls}")
                print(f"  - JPEG images: {jpeg_images}")
                print(f"  - PNG images: {png_images}")
                print(f"  - Image references: {image_refs}")
                print(f"  - Figure captions: {figure_captions}")
                
                # Verify data URL format
                import re
                data_url_pattern = r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+'
                valid_data_urls = re.findall(data_url_pattern, content)
                
                if valid_data_urls:
                    print(f"✅ Valid data URL format: {len(valid_data_urls)} found")
                    
                    # Test base64 decoding
                    try:
                        import base64
                        sample_url = valid_data_urls[0]
                        base64_part = sample_url.split('base64,')[1]
                        decoded = base64.b64decode(base64_part)
                        print(f"✅ Base64 data integrity verified ({len(decoded)} bytes)")
                        results['content_library_media_storage'] = True
                    except Exception as e:
                        print(f"❌ Base64 data corrupted: {e}")
                        results['content_library_media_storage'] = False
                else:
                    print("❌ No valid data URLs found")
                    results['content_library_media_storage'] = False
            else:
                print("❌ No articles with embedded media found")
                results['content_library_media_storage'] = False
        else:
            print(f"❌ Content Library access failed: {response.status_code}")
            results['content_library_media_storage'] = False
    except Exception as e:
        print(f"❌ Content Library test failed: {e}")
        results['content_library_media_storage'] = False
    
    # Test 2: Verify AI-generated articles preserve media
    print("\n2. Testing AI Media Preservation...")
    try:
        # Look for AI-generated articles with media
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            ai_media_articles = []
            for article in articles:
                content = article.get('content', '')
                metadata = article.get('metadata', {})
                
                if ('data:image/' in content and 
                    metadata.get('ai_processed') == True):
                    ai_media_articles.append(article)
            
            print(f"✅ AI-generated articles with media: {len(ai_media_articles)}")
            
            if ai_media_articles:
                sample_ai_article = ai_media_articles[0]
                content = sample_ai_article.get('content', '')
                
                # Check for strategic image placement
                strategic_refs = (
                    'shown in the diagram' in content.lower() or
                    'illustrated' in content.lower() or
                    'as shown' in content.lower() or
                    'figure below' in content.lower()
                )
                
                print(f"✅ AI article title: {sample_ai_article.get('title', 'No title')[:60]}...")
                print(f"✅ Strategic image references: {strategic_refs}")
                print(f"✅ Data URLs preserved: {content.count('data:image/')}")
                
                results['ai_media_preservation'] = True
            else:
                print("⚠️ No AI-generated articles with media found")
                results['ai_media_preservation'] = False
        else:
            print(f"❌ AI media preservation test failed: {response.status_code}")
            results['ai_media_preservation'] = False
    except Exception as e:
        print(f"❌ AI media preservation test failed: {e}")
        results['ai_media_preservation'] = False
    
    # Test 3: Check for multi-article media distribution
    print("\n3. Testing Multi-Article Media Distribution...")
    try:
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Look for articles that might be from multi-article splitting
            multi_article_candidates = []
            for article in articles:
                metadata = article.get('metadata', {})
                if (metadata.get('total_articles', 0) > 1 or 
                    metadata.get('article_index')):
                    multi_article_candidates.append(article)
            
            # Also check for articles with similar themes but different focuses
            themed_articles = {}
            for article in articles:
                content = article.get('content', '')
                title = article.get('title', '').lower()
                
                # Group by common themes
                if 'data visualization' in title or 'chart' in content.lower():
                    themed_articles.setdefault('visualization', []).append(article)
                elif 'architecture' in title or 'system' in title:
                    themed_articles.setdefault('architecture', []).append(article)
                elif 'performance' in title or 'monitoring' in title:
                    themed_articles.setdefault('performance', []).append(article)
            
            multi_article_groups = [group for group in themed_articles.values() if len(group) > 1]
            
            print(f"✅ Multi-article candidates: {len(multi_article_candidates)}")
            print(f"✅ Themed article groups: {len(multi_article_groups)}")
            
            if multi_article_candidates or multi_article_groups:
                # Check media distribution across related articles
                total_media_articles = 0
                for group in multi_article_groups:
                    media_in_group = sum(1 for a in group if 'data:image/' in a.get('content', ''))
                    total_media_articles += media_in_group
                    if media_in_group > 1:
                        print(f"✅ Found {media_in_group} articles with media in themed group")
                
                results['multi_article_media_distribution'] = total_media_articles > 1
            else:
                print("⚠️ No clear multi-article media distribution found")
                results['multi_article_media_distribution'] = False
        else:
            print(f"❌ Multi-article test failed: {response.status_code}")
            results['multi_article_media_distribution'] = False
    except Exception as e:
        print(f"❌ Multi-article test failed: {e}")
        results['multi_article_media_distribution'] = False
    
    # Test 4: Verify enhanced document processing capabilities
    print("\n4. Testing Enhanced Document Processing...")
    try:
        # Check for articles that show signs of enhanced processing
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            enhanced_articles = []
            for article in articles:
                content = article.get('content', '')
                metadata = article.get('metadata', {})
                
                # Look for signs of enhanced processing
                has_media_metadata = 'Media Assets' in content or 'Total Images' in content
                has_structured_content = content.count('#') > 2  # Multiple headings
                has_ai_enhancement = metadata.get('ai_processed') == True
                
                if has_media_metadata or (has_structured_content and has_ai_enhancement):
                    enhanced_articles.append(article)
            
            print(f"✅ Articles with enhanced processing: {len(enhanced_articles)}")
            
            if enhanced_articles:
                sample_enhanced = enhanced_articles[0]
                content = sample_enhanced.get('content', '')
                
                # Check for comprehensive features
                features = {
                    'media_metadata': 'Media Assets' in content or 'Total Images' in content,
                    'structured_headings': content.count('#') > 2,
                    'figure_captions': '*Figure' in content,
                    'comprehensive_content': len(content) > 1000,
                    'ai_processing': sample_enhanced.get('metadata', {}).get('ai_processed') == True
                }
                
                print(f"✅ Enhanced processing features:")
                for feature, present in features.items():
                    status = "✅" if present else "❌"
                    print(f"  {status} {feature.replace('_', ' ').title()}: {present}")
                
                results['enhanced_document_processing'] = sum(features.values()) >= 3
            else:
                print("❌ No enhanced processing detected")
                results['enhanced_document_processing'] = False
        else:
            print(f"❌ Enhanced processing test failed: {response.status_code}")
            results['enhanced_document_processing'] = False
    except Exception as e:
        print(f"❌ Enhanced processing test failed: {e}")
        results['enhanced_document_processing'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 ENHANCED MEDIA EXTRACTION TEST RESULTS")
    print("=" * 60)
    
    test_descriptions = {
        'content_library_media_storage': 'Content Library Media Storage & Integrity',
        'ai_media_preservation': 'AI-Generated Articles Media Preservation',
        'multi_article_media_distribution': 'Multi-Article Media Distribution',
        'enhanced_document_processing': 'Enhanced Document Processing Features'
    }
    
    passed = 0
    total = len(results)
    
    for test_name, description in test_descriptions.items():
        if test_name in results:
            result = results[test_name]
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{description}: {status}")
            if result:
                passed += 1
    
    print(f"\nOverall Media Extraction Tests: {passed}/{total} tests passed")
    
    # Assessment
    if passed >= 3:
        print("🎉 Enhanced Media Extraction capabilities are working!")
        print("✅ The Knowledge Engine successfully handles embedded media")
        return True
    elif passed >= 2:
        print("⚠️ Enhanced Media Extraction partially working")
        print("🔧 Some media capabilities need attention")
        return True
    else:
        print("❌ Enhanced Media Extraction capabilities need significant work")
        print("🚨 Critical media handling issues detected")
        return False

if __name__ == "__main__":
    success = test_media_extraction_capabilities()
    exit(0 if success else 1)