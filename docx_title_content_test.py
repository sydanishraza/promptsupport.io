#!/usr/bin/env python3
"""
DOCX Processing Title and Content Quality Test
Testing the specific Google Map JavaScript API Tutorial document to identify:
1. Title generation issues (expected: "Using Google Map Javascript API")
2. Content quality issues (summarization vs enhancement)
3. Root cause analysis of title and content problems
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://14236aae-8093-4969-a2a2-e2c349953e54.preview.emergentagent.com"
TEST_FILE = "/app/Google_Map_JavaScript_API_Tutorial.docx"

def test_docx_title_and_content_issues():
    """Test the specific Google Maps tutorial document for title and content issues"""
    
    print("🎯 DOCX PROCESSING TITLE AND CONTENT QUALITY TEST")
    print("=" * 60)
    print(f"Testing file: {TEST_FILE}")
    print(f"Expected title: 'Using Google Map Javascript API' (from H1)")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Check if test file exists
    if not os.path.exists(TEST_FILE):
        print(f"❌ Test file not found: {TEST_FILE}")
        return False
    
    file_size = os.path.getsize(TEST_FILE)
    print(f"📊 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    print()
    
    try:
        # Test 1: Upload and process the document
        print("🔄 TEST 1: DOCX Processing Pipeline")
        print("-" * 40)
        
        with open(TEST_FILE, 'rb') as f:
            files = {'file': ('Google_Map_JavaScript_API_Tutorial.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            
            print("📤 Uploading DOCX file...")
            start_time = time.time()
            
            response = requests.post(
                f"{BACKEND_URL}/api/content/upload",
                files=files,
                timeout=300  # 5 minute timeout for large files
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing time: {processing_time:.2f} seconds")
            
            if response.status_code != 200:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            result = response.json()
            print(f"✅ Upload successful")
            print(f"📋 Response keys: {list(result.keys())}")
            
            # Analyze the response structure
            if 'status' in result:
                print(f"📊 Status: {result['status']}")
            
            if 'articles_created' in result:
                articles_count = result['articles_created']
                print(f"📄 Articles created: {articles_count}")
            elif 'chunks_created' in result:
                articles_count = result['chunks_created']
                print(f"📄 Chunks created: {articles_count}")
            else:
                print("⚠️ No article/chunk count found in response")
                articles_count = 0
            
            print()
            
            # Test 2: Examine generated articles for title issues
            print("🔍 TEST 2: TITLE GENERATION ANALYSIS")
            print("-" * 40)
            
            # Get articles from Content Library
            content_response = requests.get(f"{BACKEND_URL}/api/content-library")
            
            if content_response.status_code == 200:
                content_data = content_response.json()
                articles = content_data.get('articles', [])
                
                print(f"📚 Total articles in Content Library: {len(articles)}")
                
                # Find recently created articles (last 5 minutes)
                recent_cutoff = datetime.now().timestamp() - 300  # 5 minutes ago
                recent_articles = []
                
                for article in articles:
                    # Check if article was created recently
                    created_at = article.get('created_at', '')
                    if created_at:
                        try:
                            # Handle different datetime formats
                            if 'T' in created_at:
                                article_time = datetime.fromisoformat(created_at.replace('Z', '+00:00')).timestamp()
                            else:
                                article_time = datetime.fromisoformat(created_at).timestamp()
                            
                            if article_time > recent_cutoff:
                                recent_articles.append(article)
                        except:
                            # If we can't parse the date, include it anyway for analysis
                            recent_articles.append(article)
                
                print(f"📝 Recent articles (last 5 min): {len(recent_articles)}")
                
                # Analyze titles of recent articles
                print("\n🏷️ TITLE ANALYSIS:")
                expected_title_keywords = ["google", "map", "javascript", "api"]
                
                for i, article in enumerate(recent_articles[:5]):  # Check first 5 recent articles
                    title = article.get('title', 'No title')
                    content_length = len(article.get('content', ''))
                    word_count = article.get('word_count', 0)
                    
                    print(f"\nArticle {i+1}:")
                    print(f"  📋 Title: '{title}'")
                    print(f"  📊 Content length: {content_length:,} characters")
                    print(f"  📝 Word count: {word_count}")
                    
                    # Check if title matches expected pattern
                    title_lower = title.lower()
                    matching_keywords = sum(1 for keyword in expected_title_keywords if keyword in title_lower)
                    
                    if "comprehensive guide" in title_lower:
                        print(f"  ❌ ISSUE: Title contains 'Comprehensive Guide' (generic generation)")
                    elif matching_keywords >= 3:
                        print(f"  ✅ Title contains relevant keywords ({matching_keywords}/4)")
                    else:
                        print(f"  ⚠️ Title may not match source content ({matching_keywords}/4 keywords)")
                    
                    # Check for expected title
                    if "using google map javascript api" in title_lower:
                        print(f"  ✅ PERFECT: Title matches expected 'Using Google Map Javascript API'")
                    
                print()
                
                # Test 3: Content Quality Analysis
                print("📖 TEST 3: CONTENT QUALITY ANALYSIS")
                print("-" * 40)
                
                for i, article in enumerate(recent_articles[:3]):  # Analyze first 3 articles
                    content = article.get('content', '')
                    title = article.get('title', 'No title')
                    
                    print(f"\nArticle {i+1}: {title[:50]}...")
                    
                    # Analyze content characteristics
                    content_lines = content.split('\n')
                    non_empty_lines = [line.strip() for line in content_lines if line.strip()]
                    
                    # Count HTML elements
                    h1_count = content.count('<h1>')
                    h2_count = content.count('<h2>')
                    h3_count = content.count('<h3>')
                    p_count = content.count('<p>')
                    
                    print(f"  📊 Structure: {h1_count} H1, {h2_count} H2, {h3_count} H3, {p_count} paragraphs")
                    print(f"  📝 Non-empty lines: {len(non_empty_lines)}")
                    
                    # Check for technical content indicators
                    technical_indicators = [
                        'javascript', 'api', 'function', 'code', 'example', 
                        'implementation', 'tutorial', 'step', 'method'
                    ]
                    
                    content_lower = content.lower()
                    found_indicators = [indicator for indicator in technical_indicators if indicator in content_lower]
                    
                    print(f"  🔧 Technical indicators: {len(found_indicators)}/9 ({', '.join(found_indicators[:5])})")
                    
                    # Check for summarization vs enhancement indicators
                    summarization_indicators = [
                        'in summary', 'to summarize', 'in conclusion', 'overview of',
                        'brief introduction', 'quick guide', 'simplified'
                    ]
                    
                    enhancement_indicators = [
                        'detailed explanation', 'comprehensive', 'step-by-step',
                        'in-depth', 'thorough', 'extensive', 'complete guide'
                    ]
                    
                    summarization_count = sum(1 for indicator in summarization_indicators if indicator in content_lower)
                    enhancement_count = sum(1 for indicator in enhancement_indicators if indicator in content_lower)
                    
                    print(f"  📉 Summarization indicators: {summarization_count}")
                    print(f"  📈 Enhancement indicators: {enhancement_count}")
                    
                    if summarization_count > enhancement_count:
                        print(f"  ❌ ISSUE: Content appears to be summarized rather than enhanced")
                    elif enhancement_count > 0:
                        print(f"  ✅ Content shows enhancement characteristics")
                    else:
                        print(f"  ⚠️ Content quality unclear")
                    
                    # Sample content preview
                    content_preview = content[:500] + "..." if len(content) > 500 else content
                    print(f"  📄 Content preview: {content_preview}")
                
            else:
                print(f"❌ Failed to get Content Library: {content_response.status_code}")
            
            print()
            
            # Test 4: Backend Processing Analysis
            print("🔧 TEST 4: BACKEND PROCESSING ANALYSIS")
            print("-" * 40)
            
            # Check backend logs for processing details
            print("📋 Processing details from response:")
            for key, value in result.items():
                if key not in ['status', 'articles_created', 'chunks_created']:
                    print(f"  {key}: {value}")
            
            # Test 5: Root Cause Investigation
            print("\n🔍 TEST 5: ROOT CAUSE INVESTIGATION")
            print("-" * 40)
            
            print("Investigating potential issues:")
            
            # Check if HTML preprocessing pipeline is being used
            if 'processing_approach' in result:
                approach = result['processing_approach']
                print(f"  📋 Processing approach: {approach}")
                
                if 'simplified' in approach.lower():
                    print(f"  ❌ ISSUE: Using simplified processing instead of comprehensive")
                elif 'html_preprocessing' in approach.lower():
                    print(f"  ✅ Using HTML preprocessing pipeline")
                else:
                    print(f"  ⚠️ Processing approach unclear")
            
            # Check for title generation method
            if articles_count > 0:
                print(f"  📊 Generated {articles_count} articles from document")
                
                if articles_count == 1:
                    print(f"  ⚠️ Single article generated - may indicate summarization")
                else:
                    print(f"  ✅ Multiple articles generated - indicates proper chunking")
            
            print()
            print("🎯 SUMMARY OF FINDINGS:")
            print("-" * 40)
            
            # Provide summary based on analysis
            issues_found = []
            
            if recent_articles:
                sample_title = recent_articles[0].get('title', '')
                if 'comprehensive guide' in sample_title.lower():
                    issues_found.append("Generic 'Comprehensive Guide' titles being generated")
                
                sample_content = recent_articles[0].get('content', '')
                if len(sample_content) < 2000:
                    issues_found.append("Content appears to be summarized (short length)")
            
            if issues_found:
                print("❌ ISSUES IDENTIFIED:")
                for issue in issues_found:
                    print(f"  - {issue}")
            else:
                print("✅ No major issues identified in this test")
            
            return True
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - document may be too large or processing is slow")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_docx_title_and_content_issues()
    
    if success:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")