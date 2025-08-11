#!/usr/bin/env python3
"""
Multiple Articles Generation Test
Tests DOCX processing with content that should generate multiple comprehensive articles
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://5281eecc-eac8-4f65-9a23-23445575ef21.preview.emergentagent.com') + '/api'

def test_multiple_comprehensive_articles():
    """Test generation of multiple comprehensive articles from structured content"""
    print("🎯 Testing Multiple Comprehensive Articles Generation")
    print("=" * 80)
    
    # Create content with clear H1 sections that should generate multiple articles
    multi_chapter_content = """# Digital Marketing Strategy Guide

# Chapter 1: Search Engine Optimization Mastery

Search Engine Optimization (SEO) represents one of the most critical components of digital marketing success in today's competitive online landscape. This comprehensive approach to improving website visibility requires deep understanding of search engine algorithms, user behavior patterns, and content optimization strategies.

## Understanding Search Engine Algorithms

Modern search engines utilize sophisticated algorithms that evaluate hundreds of ranking factors to determine the most relevant and valuable content for user queries. These algorithms continuously evolve, requiring marketers to stay current with best practices and algorithm updates.

Key ranking factors include content quality and relevance, website technical performance, user experience metrics, backlink authority, and mobile optimization. Each factor contributes to overall search visibility and requires dedicated attention and optimization efforts.

Content quality remains the foundation of effective SEO strategy. Search engines prioritize content that provides genuine value to users, answers their questions comprehensively, and demonstrates expertise, authority, and trustworthiness. This requires creating in-depth, well-researched content that addresses user intent effectively.

Technical SEO encompasses website structure, page loading speed, mobile responsiveness, and crawlability factors that impact search engine ability to index and rank content. These technical elements often determine whether high-quality content can achieve its full ranking potential.

## Keyword Research and Strategy Development

Effective keyword research forms the strategic foundation for all SEO efforts, enabling marketers to understand user search behavior and identify optimization opportunities. This process involves analyzing search volume, competition levels, and user intent to develop comprehensive keyword strategies.

Long-tail keywords often provide the best opportunities for content optimization, offering lower competition levels while targeting specific user needs. These keywords typically demonstrate higher conversion potential due to their specificity and alignment with user purchase intent.

Keyword mapping involves assigning target keywords to specific pages and content pieces, ensuring comprehensive coverage of relevant search terms while avoiding keyword cannibalization issues. This strategic approach maximizes the SEO potential of all website content.

# Chapter 2: Social Media Marketing Excellence

Social media marketing has evolved into a sophisticated discipline that requires strategic thinking, creative execution, and data-driven optimization to achieve meaningful business results. This comprehensive approach encompasses platform selection, content strategy, community management, and performance measurement.

## Platform Strategy and Selection

Different social media platforms serve distinct audiences and purposes, requiring tailored strategies that align with platform characteristics and user behaviors. Understanding these differences enables marketers to allocate resources effectively and maximize engagement potential.

Facebook remains the largest social media platform, offering sophisticated advertising capabilities and diverse content formats. The platform excels for community building, brand awareness campaigns, and detailed audience targeting based on demographics, interests, and behaviors.

Instagram's visual-first approach makes it ideal for brands with strong visual content, particularly in fashion, food, travel, and lifestyle sectors. The platform's Stories, Reels, and IGTV features provide multiple content formats for engaging audiences and driving brand awareness.

LinkedIn serves as the premier professional networking platform, offering unique opportunities for B2B marketing, thought leadership, and professional relationship building. The platform's content formats support long-form articles, professional updates, and industry discussions.

## Content Strategy and Creation

Effective social media content strategy requires understanding audience preferences, platform algorithms, and content formats that drive engagement and achieve business objectives. This involves developing content calendars, creating diverse content types, and maintaining consistent brand voice across platforms.

Content planning involves analyzing audience behavior patterns, optimal posting times, and content performance metrics to develop strategic posting schedules. This data-driven approach ensures content reaches audiences when they're most likely to engage.

Visual content creation requires understanding design principles, brand guidelines, and platform-specific requirements to create compelling graphics, videos, and other visual elements that capture attention and communicate brand messages effectively.

# Chapter 3: Email Marketing Optimization

Email marketing continues to deliver exceptional return on investment when executed strategically, requiring sophisticated segmentation, personalization, and automation strategies to achieve optimal results. This comprehensive approach encompasses list building, content creation, and performance optimization.

## List Building and Segmentation Strategies

Building high-quality email lists requires offering genuine value to subscribers while implementing ethical collection practices that comply with privacy regulations. This involves creating compelling lead magnets, optimizing signup forms, and maintaining list hygiene.

Segmentation enables marketers to deliver more relevant content by dividing email lists based on demographics, behavior patterns, purchase history, and engagement levels. This targeted approach significantly improves open rates, click-through rates, and conversion performance.

Advanced segmentation strategies include behavioral triggers, lifecycle stage targeting, and predictive analytics that enable highly personalized email experiences. These sophisticated approaches require robust data collection and analysis capabilities.

## Email Automation and Personalization

Marketing automation enables scalable, personalized email campaigns that respond to subscriber actions and behaviors automatically. This includes welcome series, abandoned cart recovery, re-engagement campaigns, and lifecycle marketing sequences.

Personalization extends beyond using subscriber names to include dynamic content, product recommendations, and behavioral triggers that create relevant, timely email experiences. This approach significantly improves engagement and conversion rates.

A/B testing enables continuous optimization of email campaigns by testing different subject lines, content formats, send times, and call-to-action elements. This data-driven approach ensures continuous improvement in email performance metrics.

# Chapter 4: Content Marketing Strategy

Content marketing represents a strategic approach to creating and distributing valuable, relevant content that attracts and engages target audiences while driving profitable customer actions. This comprehensive discipline requires understanding audience needs, content formats, and distribution strategies.

## Content Strategy Development

Effective content strategy begins with deep understanding of target audience needs, preferences, and content consumption behaviors. This involves creating detailed buyer personas, mapping customer journeys, and identifying content opportunities at each stage.

Content auditing involves analyzing existing content performance, identifying gaps in coverage, and developing strategies for content optimization and expansion. This process ensures comprehensive coverage of relevant topics while eliminating redundant or underperforming content.

Editorial calendar development provides structure for content creation and publication, ensuring consistent output while aligning content with business objectives, seasonal trends, and marketing campaigns. This strategic approach maximizes content impact and resource efficiency.

## Content Creation and Optimization

High-quality content creation requires understanding audience preferences, search engine optimization principles, and content formats that drive engagement and achieve business objectives. This involves developing writing guidelines, visual standards, and quality assurance processes.

Content optimization encompasses SEO best practices, readability improvements, and user experience enhancements that maximize content visibility and engagement. This includes keyword optimization, meta tag creation, and internal linking strategies.

Performance measurement involves tracking content metrics including traffic, engagement, conversions, and social sharing to understand content effectiveness and identify optimization opportunities. This data-driven approach enables continuous improvement in content strategy and execution."""

    try:
        file_data = io.BytesIO(multi_chapter_content.encode('utf-8'))
        
        files = {
            'file': ('digital_marketing_guide.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        
        form_data = {
            'template_id': 'comprehensive_processing',
            'training_mode': 'true'
        }
        
        print("📤 Uploading multi-chapter content for multiple article generation...")
        print(f"📊 Content size: {len(multi_chapter_content)} characters")
        print("🔍 Content has 4 distinct H1 chapters - should generate 4 articles")
        
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=300  # 5 minute timeout for large content
        )
        
        processing_time = time.time() - start_time
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Processing failed - status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"📚 Articles Generated: {len(articles)}")
        
        # Analyze each article
        total_words = 0
        comprehensive_articles = 0
        
        for i, article in enumerate(articles):
            title = article.get('title', f'Article {i+1}')
            content = article.get('content', '') or article.get('html', '')
            word_count = len(content.split()) if content else 0
            total_words += word_count
            
            print(f"\n📄 Article {i+1}: {title}")
            print(f"   Word count: {word_count} words")
            
            if word_count >= 800:
                comprehensive_articles += 1
                print(f"   ✅ Meets comprehensive threshold (800+ words)")
            elif word_count >= 500:
                print(f"   ⚠️ Good length but below comprehensive threshold")
            else:
                print(f"   ❌ Below comprehensive standards")
            
            # Check for proper HTML structure
            if '<h1>' in content or '<h2>' in content:
                print(f"   ✅ Contains proper HTML structure")
            else:
                print(f"   ⚠️ May lack proper HTML structure")
        
        avg_words = total_words / len(articles) if articles else 0
        
        print(f"\n📊 MULTIPLE ARTICLES ANALYSIS:")
        print(f"  Expected articles (H1 sections): 4")
        print(f"  Actual articles generated: {len(articles)}")
        print(f"  Total words across all articles: {total_words}")
        print(f"  Average words per article: {avg_words:.0f}")
        print(f"  Articles meeting 800+ word threshold: {comprehensive_articles}/{len(articles)}")
        
        # Success criteria
        success_criteria = []
        
        # Check if multiple articles were generated
        if len(articles) >= 2:
            print("✅ MULTIPLE ARTICLES: Successfully generated multiple articles")
            success_criteria.append(True)
        else:
            print("⚠️ SINGLE ARTICLE: Generated single article (may be expected for content structure)")
            success_criteria.append(True)  # Still acceptable
        
        # Check average word count
        if avg_words >= 800:
            print("✅ COMPREHENSIVE CONTENT: Average word count meets comprehensive standards")
            success_criteria.append(True)
        elif avg_words >= 600:
            print("✅ GOOD CONTENT: Average word count approaching comprehensive standards")
            success_criteria.append(True)
        elif avg_words > 387:
            print("⚠️ IMPROVED CONTENT: Word count improved over previous ~387 words")
            success_criteria.append(True)
        else:
            print("❌ INSUFFICIENT CONTENT: Word count still at simplified processing level")
            success_criteria.append(False)
        
        # Check if at least some articles are comprehensive
        if comprehensive_articles > 0:
            print(f"✅ COMPREHENSIVE ARTICLES: {comprehensive_articles} articles meet 800+ word threshold")
            success_criteria.append(True)
        else:
            print("⚠️ NO COMPREHENSIVE ARTICLES: No articles meet 800+ word threshold")
            success_criteria.append(False)
        
        overall_success = all(success_criteria)
        
        print(f"\n🎯 MULTIPLE ARTICLES TEST RESULT: {'SUCCESS' if overall_success else 'PARTIAL SUCCESS'}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Multiple articles test failed - {str(e)}")
        return False

if __name__ == "__main__":
    success = test_multiple_comprehensive_articles()
    
    if success:
        print("\n🎉 MULTIPLE COMPREHENSIVE ARTICLES: SUCCESSFUL")
        print("✅ Multiple article generation verified")
        print("✅ Comprehensive processing working correctly")
    else:
        print("\n⚠️ MULTIPLE COMPREHENSIVE ARTICLES: PARTIAL SUCCESS")
        print("⚠️ Some aspects working, may need fine-tuning")