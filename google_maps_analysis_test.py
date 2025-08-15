#!/usr/bin/env python3
"""
Backend Test Suite for Google Maps DOCX Articles Duplication Analysis
Testing the Enhanced Knowledge Engine Anti-Duplicate System
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import List, Dict, Any
import re
from collections import Counter
import difflib

# Get backend URL from environment
BACKEND_URL = "https://promptsupport-2.preview.emergentagent.com/api"

class GoogleMapsArticleAnalyzer:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def test_backend_health(self):
        """Test if backend is accessible"""
        try:
            print("🔍 Testing backend health...")
            response = self.session.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ Backend health check passed: {response.status_code}")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend health check error: {e}")
            return False
    
    def get_all_articles(self) -> List[Dict]:
        """Retrieve all articles from content library"""
        try:
            print("📚 Fetching all articles from Content Library...")
            response = self.session.get(f"{self.backend_url}/content-library", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                total = data.get('total', len(articles))
                print(f"✅ Retrieved {len(articles)} articles (total: {total})")
                return articles
            else:
                print(f"❌ Failed to fetch articles: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error fetching articles: {e}")
            return []
    
    def find_google_maps_articles(self, articles: List[Dict]) -> List[Dict]:
        """Find articles related to Google Maps from DOCX processing"""
        print("🗺️ Searching for Google Maps related articles...")
        
        google_maps_keywords = [
            'google maps', 'maps api', 'google map', 'javascript api',
            'geocoding', 'marker', 'coordinates', 'maps platform',
            'google.maps', 'map api', 'mapping', 'location'
        ]
        
        google_maps_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            tags = article.get('tags', [])
            source_doc = article.get('source_document', '').lower()
            
            # Check if article is from DOCX processing
            is_docx_source = (
                'docx' in source_doc or
                any('docx' in tag.lower() for tag in tags) or
                article.get('processing_metadata', {}).get('source_type') == 'docx'
            )
            
            # Check for Google Maps keywords
            has_maps_content = any(
                keyword in title or keyword in content 
                for keyword in google_maps_keywords
            )
            
            if has_maps_content and is_docx_source:
                google_maps_articles.append(article)
                print(f"📍 Found Google Maps article: '{article.get('title', 'Untitled')}'")
        
        print(f"✅ Found {len(google_maps_articles)} Google Maps articles from DOCX processing")
        return google_maps_articles
    
    def analyze_title_similarity(self, articles: List[Dict]) -> Dict:
        """Analyze title similarity and redundancy"""
        print("🔍 Analyzing title similarity...")
        
        titles = [article.get('title', '') for article in articles]
        title_analysis = {
            'total_articles': len(articles),
            'unique_titles': len(set(titles)),
            'duplicate_titles': [],
            'similar_titles': [],
            'title_patterns': {}
        }
        
        # Find exact duplicates
        title_counts = Counter(titles)
        for title, count in title_counts.items():
            if count > 1:
                title_analysis['duplicate_titles'].append({
                    'title': title,
                    'count': count
                })
        
        # Find similar titles (using difflib)
        for i, title1 in enumerate(titles):
            for j, title2 in enumerate(titles[i+1:], i+1):
                similarity = difflib.SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
                if similarity > 0.7:  # 70% similarity threshold
                    title_analysis['similar_titles'].append({
                        'title1': title1,
                        'title2': title2,
                        'similarity': similarity,
                        'article1_id': articles[i].get('id'),
                        'article2_id': articles[j].get('id')
                    })
        
        # Analyze title patterns
        common_words = []
        for title in titles:
            words = re.findall(r'\b\w+\b', title.lower())
            common_words.extend(words)
        
        word_counts = Counter(common_words)
        title_analysis['title_patterns'] = dict(word_counts.most_common(10))
        
        return title_analysis
    
    def analyze_content_overlap(self, articles: List[Dict]) -> Dict:
        """Analyze content overlap and redundancy"""
        print("📝 Analyzing content overlap...")
        
        content_analysis = {
            'total_articles': len(articles),
            'content_overlaps': [],
            'common_sections': [],
            'duplicate_content_percentage': 0
        }
        
        # Extract content for comparison
        article_contents = []
        for article in articles:
            content = article.get('content', '')
            # Remove HTML tags for better comparison
            clean_content = re.sub(r'<[^>]+>', '', content)
            article_contents.append({
                'id': article.get('id'),
                'title': article.get('title'),
                'content': clean_content,
                'word_count': len(clean_content.split())
            })
        
        # Compare content similarity
        overlapping_pairs = 0
        total_pairs = 0
        
        for i, content1 in enumerate(article_contents):
            for j, content2 in enumerate(article_contents[i+1:], i+1):
                total_pairs += 1
                
                # Calculate content similarity
                similarity = difflib.SequenceMatcher(
                    None, 
                    content1['content'].lower(), 
                    content2['content'].lower()
                ).ratio()
                
                if similarity > 0.3:  # 30% similarity threshold
                    overlapping_pairs += 1
                    content_analysis['content_overlaps'].append({
                        'article1': {
                            'id': content1['id'],
                            'title': content1['title'],
                            'word_count': content1['word_count']
                        },
                        'article2': {
                            'id': content2['id'],
                            'title': content2['title'],
                            'word_count': content2['word_count']
                        },
                        'similarity': similarity
                    })
        
        if total_pairs > 0:
            content_analysis['duplicate_content_percentage'] = (overlapping_pairs / total_pairs) * 100
        
        return content_analysis
    
    def analyze_chunking_system(self, articles: List[Dict]) -> Dict:
        """Analyze how the chunking system created these articles"""
        print("⚙️ Analyzing chunking system behavior...")
        
        chunking_analysis = {
            'total_articles': len(articles),
            'source_documents': {},
            'article_sizes': [],
            'chunking_patterns': {},
            'over_chunking_indicators': []
        }
        
        # Group articles by source document
        for article in articles:
            source_doc = article.get('source_document', 'unknown')
            if source_doc not in chunking_analysis['source_documents']:
                chunking_analysis['source_documents'][source_doc] = []
            
            chunking_analysis['source_documents'][source_doc].append({
                'id': article.get('id'),
                'title': article.get('title'),
                'word_count': len(article.get('content', '').split()),
                'char_count': len(article.get('content', ''))
            })
        
        # Analyze article sizes
        for article in articles:
            content = article.get('content', '')
            word_count = len(content.split())
            char_count = len(content)
            
            chunking_analysis['article_sizes'].append({
                'id': article.get('id'),
                'title': article.get('title'),
                'word_count': word_count,
                'char_count': char_count
            })
        
        # Identify potential over-chunking
        for source_doc, doc_articles in chunking_analysis['source_documents'].items():
            if len(doc_articles) > 10:  # More than 10 articles from one document
                avg_size = sum(a['word_count'] for a in doc_articles) / len(doc_articles)
                if avg_size < 200:  # Average less than 200 words
                    chunking_analysis['over_chunking_indicators'].append({
                        'source_document': source_doc,
                        'article_count': len(doc_articles),
                        'average_word_count': avg_size,
                        'issue': 'Potential over-chunking - too many small articles'
                    })
        
        return chunking_analysis
    
    def assess_content_quality(self, articles: List[Dict]) -> Dict:
        """Assess the quality and uniqueness of each article"""
        print("⭐ Assessing content quality...")
        
        quality_analysis = {
            'total_articles': len(articles),
            'quality_scores': [],
            'unique_value_articles': [],
            'redundant_articles': [],
            'optimal_article_count_estimate': 0
        }
        
        for article in articles:
            content = article.get('content', '')
            title = article.get('title', '')
            
            # Calculate quality metrics
            word_count = len(content.split())
            char_count = len(content)
            has_headings = bool(re.search(r'<h[1-6]>', content))
            has_lists = bool(re.search(r'<[uo]l>', content))
            has_code = bool(re.search(r'<code>|<pre>', content))
            
            # Quality score calculation
            quality_score = 0
            if word_count > 100: quality_score += 1
            if word_count > 300: quality_score += 1
            if has_headings: quality_score += 1
            if has_lists: quality_score += 1
            if has_code: quality_score += 1
            if len(title) > 10: quality_score += 1
            
            quality_analysis['quality_scores'].append({
                'id': article.get('id'),
                'title': title,
                'word_count': word_count,
                'char_count': char_count,
                'quality_score': quality_score,
                'has_headings': has_headings,
                'has_lists': has_lists,
                'has_code': has_code
            })
        
        # Identify unique value vs redundant articles
        high_quality_articles = [a for a in quality_analysis['quality_scores'] if a['quality_score'] >= 4]
        low_quality_articles = [a for a in quality_analysis['quality_scores'] if a['quality_score'] < 3]
        
        quality_analysis['unique_value_articles'] = high_quality_articles
        quality_analysis['redundant_articles'] = low_quality_articles
        
        # Estimate optimal article count
        unique_topics = set()
        for article in articles:
            title_words = set(re.findall(r'\b\w+\b', article.get('title', '').lower()))
            unique_topics.update(title_words)
        
        # Rough estimate: 1 article per 3-5 unique topic words
        quality_analysis['optimal_article_count_estimate'] = max(3, len(unique_topics) // 4)
        
        return quality_analysis
    
    def generate_recommendations(self, title_analysis: Dict, content_analysis: Dict, 
                               chunking_analysis: Dict, quality_analysis: Dict) -> Dict:
        """Generate recommendations for chunking improvements"""
        print("💡 Generating recommendations...")
        
        recommendations = {
            'current_issues': [],
            'chunking_improvements': [],
            'optimal_parameters': {},
            'merge_suggestions': [],
            'elimination_suggestions': []
        }
        
        # Identify current issues
        if title_analysis['duplicate_titles']:
            recommendations['current_issues'].append(
                f"Found {len(title_analysis['duplicate_titles'])} duplicate titles"
            )
        
        if content_analysis['duplicate_content_percentage'] > 50:
            recommendations['current_issues'].append(
                f"High content overlap: {content_analysis['duplicate_content_percentage']:.1f}%"
            )
        
        if chunking_analysis['over_chunking_indicators']:
            recommendations['current_issues'].append(
                f"Over-chunking detected in {len(chunking_analysis['over_chunking_indicators'])} documents"
            )
        
        # Chunking improvements
        avg_article_size = sum(a['word_count'] for a in quality_analysis['quality_scores']) / len(quality_analysis['quality_scores'])
        
        if avg_article_size < 200:
            recommendations['chunking_improvements'].append(
                "Increase minimum chunk size to reduce over-chunking"
            )
        
        if content_analysis['duplicate_content_percentage'] > 30:
            recommendations['chunking_improvements'].append(
                "Implement better content deduplication before chunking"
            )
        
        # Optimal parameters
        recommendations['optimal_parameters'] = {
            'min_chunk_size': max(300, int(avg_article_size * 1.5)),
            'max_chunk_size': max(800, int(avg_article_size * 3)),
            'similarity_threshold': 0.7,
            'recommended_article_count': quality_analysis['optimal_article_count_estimate']
        }
        
        # Merge suggestions
        for overlap in content_analysis['content_overlaps']:
            if overlap['similarity'] > 0.7:
                recommendations['merge_suggestions'].append({
                    'article1_title': overlap['article1']['title'],
                    'article2_title': overlap['article2']['title'],
                    'reason': f"High content similarity ({overlap['similarity']:.1%})"
                })
        
        # Elimination suggestions
        for article in quality_analysis['redundant_articles']:
            if article['quality_score'] < 2 and article['word_count'] < 100:
                recommendations['elimination_suggestions'].append({
                    'title': article['title'],
                    'reason': f"Low quality (score: {article['quality_score']}) and short content ({article['word_count']} words)"
                })
        
        return recommendations
    
    def run_comprehensive_analysis(self):
        """Run the complete Google Maps DOCX articles analysis"""
        print("🚀 Starting comprehensive Google Maps DOCX articles duplication analysis...")
        print("=" * 80)
        
        # Test backend health
        if not self.test_backend_health():
            print("❌ Backend not accessible. Aborting analysis.")
            return False
        
        # Get all articles
        all_articles = self.get_all_articles()
        if not all_articles:
            print("❌ No articles found. Aborting analysis.")
            return False
        
        # Find Google Maps articles
        google_maps_articles = self.find_google_maps_articles(all_articles)
        if not google_maps_articles:
            print("⚠️ No Google Maps articles found from DOCX processing.")
            print("📊 Analyzing all articles for general duplication patterns...")
            google_maps_articles = all_articles[:15]  # Analyze first 15 articles as sample
        
        print(f"\n📊 ANALYSIS RESULTS FOR {len(google_maps_articles)} ARTICLES")
        print("=" * 80)
        
        # Run analyses
        title_analysis = self.analyze_title_similarity(google_maps_articles)
        content_analysis = self.analyze_content_overlap(google_maps_articles)
        chunking_analysis = self.analyze_chunking_system(google_maps_articles)
        quality_analysis = self.assess_content_quality(google_maps_articles)
        recommendations = self.generate_recommendations(
            title_analysis, content_analysis, chunking_analysis, quality_analysis
        )
        
        # Print detailed results
        self.print_analysis_results(
            title_analysis, content_analysis, chunking_analysis, 
            quality_analysis, recommendations
        )
        
        return True
    
    def print_analysis_results(self, title_analysis, content_analysis, 
                             chunking_analysis, quality_analysis, recommendations):
        """Print comprehensive analysis results"""
        
        print("\n1. 📋 TITLE ANALYSIS")
        print("-" * 40)
        print(f"Total Articles: {title_analysis['total_articles']}")
        print(f"Unique Titles: {title_analysis['unique_titles']}")
        print(f"Duplicate Titles: {len(title_analysis['duplicate_titles'])}")
        
        if title_analysis['duplicate_titles']:
            print("\nDuplicate Titles Found:")
            for dup in title_analysis['duplicate_titles']:
                print(f"  • '{dup['title']}' appears {dup['count']} times")
        
        if title_analysis['similar_titles']:
            print(f"\nSimilar Titles: {len(title_analysis['similar_titles'])}")
            for sim in title_analysis['similar_titles'][:5]:  # Show first 5
                print(f"  • {sim['similarity']:.1%} similarity:")
                print(f"    - '{sim['title1']}'")
                print(f"    - '{sim['title2']}'")
        
        print("\n2. 📝 CONTENT OVERLAP ANALYSIS")
        print("-" * 40)
        print(f"Total Articles: {content_analysis['total_articles']}")
        print(f"Content Overlaps Found: {len(content_analysis['content_overlaps'])}")
        print(f"Duplicate Content Percentage: {content_analysis['duplicate_content_percentage']:.1f}%")
        
        if content_analysis['content_overlaps']:
            print("\nTop Content Overlaps:")
            sorted_overlaps = sorted(content_analysis['content_overlaps'], 
                                   key=lambda x: x['similarity'], reverse=True)
            for overlap in sorted_overlaps[:3]:  # Show top 3
                print(f"  • {overlap['similarity']:.1%} similarity:")
                print(f"    - '{overlap['article1']['title']}' ({overlap['article1']['word_count']} words)")
                print(f"    - '{overlap['article2']['title']}' ({overlap['article2']['word_count']} words)")
        
        print("\n3. ⚙️ CHUNKING SYSTEM ANALYSIS")
        print("-" * 40)
        print(f"Total Articles: {chunking_analysis['total_articles']}")
        print(f"Source Documents: {len(chunking_analysis['source_documents'])}")
        
        for source_doc, articles in chunking_analysis['source_documents'].items():
            if len(articles) > 1:
                avg_words = sum(a['word_count'] for a in articles) / len(articles)
                print(f"  • '{source_doc}': {len(articles)} articles (avg: {avg_words:.0f} words)")
        
        if chunking_analysis['over_chunking_indicators']:
            print("\nOver-chunking Issues:")
            for issue in chunking_analysis['over_chunking_indicators']:
                print(f"  • {issue['source_document']}: {issue['article_count']} articles, avg {issue['average_word_count']:.0f} words")
        
        print("\n4. ⭐ CONTENT QUALITY ASSESSMENT")
        print("-" * 40)
        print(f"Total Articles: {quality_analysis['total_articles']}")
        print(f"High Quality Articles: {len(quality_analysis['unique_value_articles'])}")
        print(f"Low Quality Articles: {len(quality_analysis['redundant_articles'])}")
        print(f"Optimal Article Count Estimate: {quality_analysis['optimal_article_count_estimate']}")
        
        # Quality distribution
        quality_scores = [a['quality_score'] for a in quality_analysis['quality_scores']]
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"Average Quality Score: {avg_quality:.1f}/6")
        
        avg_words = sum(a['word_count'] for a in quality_analysis['quality_scores']) / len(quality_analysis['quality_scores'])
        print(f"Average Word Count: {avg_words:.0f} words")
        
        print("\n5. 💡 RECOMMENDATIONS")
        print("-" * 40)
        
        if recommendations['current_issues']:
            print("Current Issues:")
            for issue in recommendations['current_issues']:
                print(f"  ❌ {issue}")
        
        if recommendations['chunking_improvements']:
            print("\nChunking Improvements:")
            for improvement in recommendations['chunking_improvements']:
                print(f"  🔧 {improvement}")
        
        print("\nOptimal Parameters:")
        params = recommendations['optimal_parameters']
        print(f"  • Min Chunk Size: {params['min_chunk_size']} words")
        print(f"  • Max Chunk Size: {params['max_chunk_size']} words")
        print(f"  • Similarity Threshold: {params['similarity_threshold']}")
        print(f"  • Recommended Article Count: {params['recommended_article_count']}")
        
        if recommendations['merge_suggestions']:
            print(f"\nMerge Suggestions ({len(recommendations['merge_suggestions'])}):")
            for merge in recommendations['merge_suggestions'][:3]:  # Show first 3
                print(f"  🔗 Merge: '{merge['article1_title']}' + '{merge['article2_title']}'")
                print(f"     Reason: {merge['reason']}")
        
        if recommendations['elimination_suggestions']:
            print(f"\nElimination Suggestions ({len(recommendations['elimination_suggestions'])}):")
            for elim in recommendations['elimination_suggestions'][:3]:  # Show first 3
                print(f"  🗑️ Remove: '{elim['title']}'")
                print(f"     Reason: {elim['reason']}")
        
        print("\n" + "=" * 80)
        print("✅ COMPREHENSIVE ANALYSIS COMPLETED")
        print("=" * 80)

def main():
    """Main function to run the analysis"""
    analyzer = GoogleMapsArticleAnalyzer()
    
    try:
        success = analyzer.run_comprehensive_analysis()
        if success:
            print("\n🎉 Analysis completed successfully!")
            return True
        else:
            print("\n❌ Analysis failed!")
            return False
    except Exception as e:
        print(f"\n💥 Analysis crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)