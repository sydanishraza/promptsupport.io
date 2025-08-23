#!/usr/bin/env python3
"""
Refined Engine v2.0 Detailed Analysis
Analyzes the refined engine articles in detail
"""

import requests
import json

BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com/api"

def analyze_refined_engine_articles():
    """Analyze refined engine articles in detail"""
    print("🔍 DETAILED REFINED ENGINE v2.0 ANALYSIS")
    print("=" * 60)
    
    try:
        # Get all articles from Content Library
        response = requests.get(f"{BACKEND_URL}/content-library", timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to fetch Content Library: {response.status_code}")
            return
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"📚 Total Articles in Library: {len(articles)}")
        
        # Find refined engine articles
        refined_articles = []
        for article in articles:
            metadata = article.get('metadata', {})
            if metadata.get('refined_engine') == True:
                refined_articles.append(article)
        
        print(f"🆕 Refined Engine Articles Found: {len(refined_articles)}")
        
        if not refined_articles:
            print("❌ No refined engine articles found!")
            return
        
        # Analyze each refined engine article
        for i, article in enumerate(refined_articles):
            print(f"\n📄 REFINED ARTICLE {i+1}: {article.get('title', 'No title')}")
            print("-" * 50)
            
            # Basic metadata
            metadata = article.get('metadata', {})
            print(f"🔧 Engine Version: {metadata.get('engine_version', 'Unknown')}")
            print(f"🎯 Processing Approach: {metadata.get('processing_approach', 'Unknown')}")
            print(f"📊 Content Type: {metadata.get('content_type', 'Unknown')}")
            print(f"🎨 WYSIWYG Enhanced: {metadata.get('wysiwyg_enhanced', False)}")
            print(f"🔒 Source Fidelity: {metadata.get('source_fidelity', 'Unknown')}")
            
            # Content analysis
            content = article.get('content', '')
            print(f"📏 Content Length: {len(content)} characters")
            
            # Check WYSIWYG enhancements
            wysiwyg_features = {
                'article_body_wrapper': '<div class="article-body">' in content,
                'enhanced_code_blocks': 'class="line-numbers"' in content,
                'heading_ids': 'id="h_' in content,
                'mini_toc': 'mini-toc' in content,
                'expandable_sections': 'class="expandable"' in content,
                'contextual_notes': 'class="note"' in content
            }
            
            print(f"\n🎨 WYSIWYG FEATURES ANALYSIS:")
            wysiwyg_count = 0
            for feature, present in wysiwyg_features.items():
                status = "✅" if present else "❌"
                print(f"   {status} {feature.replace('_', ' ').title()}")
                if present:
                    wysiwyg_count += 1
            
            print(f"   📊 WYSIWYG Score: {wysiwyg_count}/6 features ({(wysiwyg_count/6)*100:.1f}%)")
            
            # Check content validation
            print(f"\n🔍 CONTENT VALIDATION:")
            has_headings = '<h2' in content or '<h3' in content
            has_paragraphs = '<p>' in content
            has_structure = '<div class="article-body">' in content
            substantial_content = len(content.replace('<', '').replace('>', '')) > 500
            
            validation_score = sum([has_headings, has_paragraphs, has_structure, substantial_content])
            print(f"   ✅ Has Headings: {has_headings}")
            print(f"   ✅ Has Paragraphs: {has_paragraphs}")
            print(f"   ✅ Has Structure: {has_structure}")
            print(f"   ✅ Substantial Content: {substantial_content}")
            print(f"   📊 Validation Score: {validation_score}/4 ({(validation_score/4)*100:.1f}%)")
            
            # Check multi-dimensional analysis metrics
            metrics = metadata.get('metrics', {})
            if metrics:
                print(f"\n📊 MULTI-DIMENSIONAL ANALYSIS METRICS:")
                print(f"   📝 Word Count: {metrics.get('word_count', 0)}")
                print(f"   📋 Heading Count: {metrics.get('heading_count', 0)}")
                print(f"   💻 Code Blocks: {metrics.get('code_blocks', 0)}")
                print(f"   📝 List Items: {metrics.get('list_items', 0)}")
                print(f"   🔢 Code Density: {metrics.get('code_density', 0):.2f}")
            
            # Check granularity decision
            print(f"\n🎯 GRANULARITY DECISION ANALYSIS:")
            approach = metadata.get('processing_approach', 'unknown')
            content_type = metadata.get('content_type', 'unknown')
            
            # For tutorials and short content, should default to unified
            if content_type == 'tutorial' and approach == 'unified':
                print(f"   ✅ Correct: Tutorial content using unified approach")
            elif content_type == 'reference' and approach == 'unified':
                print(f"   ✅ Acceptable: Reference content using unified approach")
            elif approach == 'moderate':
                print(f"   ✅ Acceptable: Using moderate split approach")
            else:
                print(f"   ⚠️ Approach: {approach} for {content_type} content")
            
            # Check source fidelity
            print(f"\n🔒 SOURCE FIDELITY CHECK:")
            fidelity = metadata.get('source_fidelity', 'unknown')
            if fidelity == 'strict':
                print(f"   ✅ Strict source fidelity maintained")
            else:
                print(f"   ⚠️ Source fidelity: {fidelity}")
        
        # Overall assessment
        print(f"\n" + "=" * 60)
        print("🎯 REFINED ENGINE v2.0 OVERALL ASSESSMENT")
        print("=" * 60)
        
        # Calculate overall scores
        total_wysiwyg_score = 0
        total_validation_score = 0
        correct_granularity = 0
        strict_fidelity = 0
        
        for article in refined_articles:
            content = article.get('content', '')
            metadata = article.get('metadata', {})
            
            # WYSIWYG score
            wysiwyg_features = [
                '<div class="article-body">' in content,
                'class="line-numbers"' in content,
                'id="h_' in content,
                'mini-toc' in content,
                'class="expandable"' in content,
                'class="note"' in content
            ]
            total_wysiwyg_score += sum(wysiwyg_features)
            
            # Validation score
            validation_features = [
                '<h2' in content or '<h3' in content,
                '<p>' in content,
                '<div class="article-body">' in content,
                len(content.replace('<', '').replace('>', '')) > 500
            ]
            total_validation_score += sum(validation_features)
            
            # Granularity check
            approach = metadata.get('processing_approach', '')
            content_type = metadata.get('content_type', '')
            if (content_type == 'tutorial' and approach == 'unified') or approach in ['unified', 'moderate']:
                correct_granularity += 1
            
            # Fidelity check
            if metadata.get('source_fidelity') == 'strict':
                strict_fidelity += 1
        
        # Calculate percentages
        max_wysiwyg = len(refined_articles) * 6
        max_validation = len(refined_articles) * 4
        
        wysiwyg_percentage = (total_wysiwyg_score / max_wysiwyg) * 100 if max_wysiwyg > 0 else 0
        validation_percentage = (total_validation_score / max_validation) * 100 if max_validation > 0 else 0
        granularity_percentage = (correct_granularity / len(refined_articles)) * 100 if refined_articles else 0
        fidelity_percentage = (strict_fidelity / len(refined_articles)) * 100 if refined_articles else 0
        
        print(f"🎨 WYSIWYG Enhancements: {wysiwyg_percentage:.1f}% ({total_wysiwyg_score}/{max_wysiwyg})")
        print(f"🔍 Content Validation: {validation_percentage:.1f}% ({total_validation_score}/{max_validation})")
        print(f"🎯 Granularity Decision: {granularity_percentage:.1f}% ({correct_granularity}/{len(refined_articles)})")
        print(f"🔒 Source Fidelity: {fidelity_percentage:.1f}% ({strict_fidelity}/{len(refined_articles)})")
        
        # Overall score
        overall_score = (wysiwyg_percentage + validation_percentage + granularity_percentage + fidelity_percentage) / 4
        print(f"\n📊 OVERALL REFINED ENGINE SCORE: {overall_score:.1f}%")
        
        if overall_score >= 80:
            print("🎉 REFINED ENGINE v2.0: EXCELLENT - PRODUCTION READY")
        elif overall_score >= 70:
            print("✅ REFINED ENGINE v2.0: GOOD - PRODUCTION READY")
        elif overall_score >= 60:
            print("⚠️ REFINED ENGINE v2.0: ACCEPTABLE - MINOR IMPROVEMENTS NEEDED")
        else:
            print("❌ REFINED ENGINE v2.0: NEEDS SIGNIFICANT IMPROVEMENTS")
        
        return {
            'wysiwyg_score': wysiwyg_percentage,
            'validation_score': validation_percentage,
            'granularity_score': granularity_percentage,
            'fidelity_score': fidelity_percentage,
            'overall_score': overall_score,
            'articles_analyzed': len(refined_articles)
        }
        
    except Exception as e:
        print(f"❌ ERROR in analysis: {e}")
        return None

if __name__ == "__main__":
    results = analyze_refined_engine_articles()
    if results:
        print(f"\n🎯 Analysis complete: {results['articles_analyzed']} articles analyzed")
        print(f"📊 Overall Score: {results['overall_score']:.1f}%")