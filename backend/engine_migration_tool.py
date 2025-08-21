#!/usr/bin/env python3
"""
Engine Migration Tool
Helps users migrate between different engine versions and compare results
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from server import db
from refined_engine import refined_engine
from refined_engine_v2 import advanced_refined_engine

@dataclass
class MigrationResult:
    """Results from engine migration/comparison"""
    source_engine: str
    target_engine: str
    articles_migrated: int
    migration_time: float
    success: bool
    error: Optional[str] = None

class EngineMigrationTool:
    """Tool for migrating content between engine versions"""
    
    def __init__(self):
        self.name = "Engine Migration Tool v1.0"
        
    async def compare_engines(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Compare results from different engines on the same content"""
        try:
            print(f"🔄 COMPARING ENGINES: Processing same content with different engines")
            
            results = {}
            
            # Test with Refined Engine v2.0
            try:
                print(f"🆕 Testing with Refined Engine v2.0...")
                refined_articles = await refined_engine.process_content(content, {
                    **metadata,
                    "comparison_test": True,
                    "engine_version": "refined_2.0"
                })
                
                results['refined_2.0'] = {
                    'success': True,
                    'articles_count': len(refined_articles),
                    'articles': refined_articles,
                    'total_content_length': sum(len(a['content']) for a in refined_articles),
                    'processing_approach': refined_articles[0].get('metadata', {}).get('processing_approach', 'unknown') if refined_articles else 'none'
                }
                print(f"✅ Refined v2.0: {len(refined_articles)} articles created")
                
            except Exception as e:
                results['refined_2.0'] = {'success': False, 'error': str(e)}
                print(f"❌ Refined v2.0 failed: {e}")
            
            # Test with Advanced Engine v2.1
            try:
                print(f"🚀 Testing with Advanced Engine v2.1...")
                advanced_articles = await advanced_refined_engine.process_content(content, {
                    **metadata,
                    "comparison_test": True,
                    "engine_version": "advanced_2.1"
                })
                
                results['advanced_2.1'] = {
                    'success': True,
                    'articles_count': len(advanced_articles),
                    'articles': advanced_articles,
                    'total_content_length': sum(len(a['content']) for a in advanced_articles),
                    'processing_approach': advanced_articles[0].get('metadata', {}).get('processing_approach', 'unknown') if advanced_articles else 'none',
                    'content_type': advanced_articles[0].get('metadata', {}).get('content_type', 'unknown') if advanced_articles else 'none',
                    'confidence_avg': sum(
                        a.get('metadata', {}).get('analysis_confidence', 0.0) 
                        for a in advanced_articles
                    ) / max(1, len(advanced_articles))
                }
                print(f"✅ Advanced v2.1: {len(advanced_articles)} articles created")
                
            except Exception as e:
                results['advanced_2.1'] = {'success': False, 'error': str(e)}
                print(f"❌ Advanced v2.1 failed: {e}")
            
            # Generate comparison analysis
            comparison = self.analyze_engine_comparison(results, content)
            
            return {
                'comparison_timestamp': datetime.utcnow().isoformat(),
                'content_analyzed': {
                    'length': len(content),
                    'word_count': len(content.split()),
                    'original_filename': metadata.get('original_filename', 'Unknown')
                },
                'engine_results': results,
                'comparison_analysis': comparison,
                'recommendation': self.generate_engine_recommendation(results, comparison)
            }
            
        except Exception as e:
            print(f"❌ Engine comparison error: {e}")
            return {
                'error': f"Comparison failed: {str(e)}",
                'comparison_timestamp': datetime.utcnow().isoformat()
            }

    def analyze_engine_comparison(self, results: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Analyze the differences between engine results"""
        try:
            analysis = {
                'engines_tested': list(results.keys()),
                'successful_engines': [k for k, v in results.items() if v.get('success', False)],
                'failed_engines': [k for k, v in results.items() if not v.get('success', False)]
            }
            
            # Compare successful engines
            successful = {k: v for k, v in results.items() if v.get('success', False)}
            
            if len(successful) >= 2:
                # Article count comparison
                article_counts = {k: v['articles_count'] for k, v in successful.items()}
                analysis['article_count_comparison'] = article_counts
                
                # Content length comparison
                content_lengths = {k: v['total_content_length'] for k, v in successful.items()}
                analysis['content_length_comparison'] = content_lengths
                
                # Processing approach comparison
                approaches = {k: v['processing_approach'] for k, v in successful.items()}
                analysis['approach_comparison'] = approaches
                
                # Quality indicators
                quality_scores = {}
                for engine, result in successful.items():
                    score = 0.0
                    
                    # Content richness (length relative to source)
                    if result['total_content_length'] > len(content) * 0.8:
                        score += 0.3
                    
                    # Article count appropriateness
                    if 1 <= result['articles_count'] <= 3:  # Good range for most content
                        score += 0.2
                    
                    # Advanced features (for v2.1)
                    if engine == 'advanced_2.1':
                        confidence = result.get('confidence_avg', 0.0)
                        score += confidence * 0.3
                        
                        if result.get('content_type') != 'unknown':
                            score += 0.2
                    
                    quality_scores[engine] = min(1.0, score)
                
                analysis['quality_comparison'] = quality_scores
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing comparison: {e}")
            return {'error': f"Analysis failed: {str(e)}"}

    def generate_engine_recommendation(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendation for which engine to use"""
        try:
            successful = analysis.get('successful_engines', [])
            
            if not successful:
                return {
                    'recommendation': 'none',
                    'reason': 'No engines processed successfully',
                    'confidence': 0.0
                }
            
            if len(successful) == 1:
                return {
                    'recommendation': successful[0],
                    'reason': f'Only {successful[0]} processed successfully',
                    'confidence': 0.7
                }
            
            # Compare quality scores
            quality_scores = analysis.get('quality_comparison', {})
            
            if quality_scores:
                best_engine = max(quality_scores.items(), key=lambda x: x[1])
                
                # Generate detailed reasoning
                reasons = []
                
                if 'advanced_2.1' in successful and 'refined_2.0' in successful:
                    advanced_quality = quality_scores.get('advanced_2.1', 0.0)
                    refined_quality = quality_scores.get('refined_2.0', 0.0)
                    
                    if advanced_quality > refined_quality + 0.1:
                        reasons.append("Advanced Engine v2.1 shows superior content analysis and processing")
                        if 'advanced_2.1' in results and results['advanced_2.1'].get('confidence_avg', 0) > 0.8:
                            reasons.append("High confidence scores indicate accurate content classification")
                        
                    elif refined_quality > advanced_quality + 0.1:
                        reasons.append("Refined Engine v2.0 provides sufficient quality with simpler processing")
                        
                    else:
                        reasons.append("Both engines show similar quality - choose based on features needed")
                
                # Feature-based recommendations
                if best_engine[0] == 'advanced_2.1':
                    reasons.append("Advanced features available: enhanced analysis, batch processing, analytics")
                
                return {
                    'recommendation': best_engine[0],
                    'reason': '; '.join(reasons) if reasons else f'Highest quality score: {best_engine[1]:.2f}',
                    'confidence': min(1.0, best_engine[1] + 0.3),
                    'quality_scores': quality_scores
                }
            
            # Fallback recommendation
            return {
                'recommendation': 'advanced_2.1' if 'advanced_2.1' in successful else successful[0],
                'reason': 'Defaulting to most advanced available engine',
                'confidence': 0.6
            }
            
        except Exception as e:
            print(f"❌ Error generating recommendation: {e}")
            return {
                'recommendation': 'unknown',
                'reason': f'Recommendation failed: {str(e)}',
                'confidence': 0.0
            }

    async def migrate_articles_to_engine(self, article_ids: List[str], target_engine: str) -> Dict[str, Any]:
        """Migrate existing articles to a different engine (reprocess with new engine)"""
        try:
            print(f"🔄 MIGRATING ARTICLES: {len(article_ids)} articles to {target_engine}")
            
            results = {
                'migrated_articles': [],
                'failed_migrations': [],
                'total_attempted': len(article_ids),
                'migration_timestamp': datetime.utcnow().isoformat()
            }
            
            for article_id in article_ids:
                try:
                    # Fetch original article
                    article = await db.content_library.find_one({"id": article_id})
                    
                    if not article:
                        results['failed_migrations'].append({
                            'article_id': article_id,
                            'error': 'Article not found'
                        })
                        continue
                    
                    # Extract original content (we can't get source content, so use existing)
                    # This is a limitation - ideally we'd store source content for migrations
                    content = self.extract_text_from_html(article.get('content', ''))
                    
                    if len(content) < 100:
                        results['failed_migrations'].append({
                            'article_id': article_id,
                            'error': 'Insufficient content for reprocessing'
                        })
                        continue
                    
                    # Prepare metadata for reprocessing
                    migration_metadata = {
                        'original_filename': article.get('source_document', 'Migrated Article'),
                        'migration_source': article.get('metadata', {}).get('engine_version', 'unknown'),
                        'migration_target': target_engine,
                        'original_article_id': article_id,
                        'migration_timestamp': datetime.utcnow().isoformat()
                    }
                    
                    # Process with target engine
                    new_articles = []
                    if target_engine == 'refined_2.0':
                        new_articles = await refined_engine.process_content(content, migration_metadata)
                    elif target_engine == 'advanced_2.1':
                        new_articles = await advanced_refined_engine.process_content(content, migration_metadata)
                    else:
                        results['failed_migrations'].append({
                            'article_id': article_id,
                            'error': f'Unknown target engine: {target_engine}'
                        })
                        continue
                    
                    if new_articles:
                        # Mark original as migrated (don't delete, just flag)
                        await db.content_library.update_one(
                            {"id": article_id},
                            {"$set": {
                                "status": "migrated",
                                "migration_info": {
                                    "migrated_to_engine": target_engine,
                                    "migration_timestamp": datetime.utcnow().isoformat(),
                                    "new_article_ids": [a['id'] for a in new_articles]
                                }
                            }}
                        )
                        
                        results['migrated_articles'].append({
                            'original_id': article_id,
                            'original_title': article.get('title', 'Unknown'),
                            'new_articles': [
                                {
                                    'id': a['id'],
                                    'title': a['title'],
                                    'type': a['article_type']
                                } for a in new_articles
                            ],
                            'new_count': len(new_articles)
                        })
                        
                        print(f"✅ Migrated article {article_id}: {len(new_articles)} new articles")
                    else:
                        results['failed_migrations'].append({
                            'article_id': article_id,
                            'error': 'Target engine failed to generate articles'
                        })
                        
                except Exception as migration_error:
                    results['failed_migrations'].append({
                        'article_id': article_id,
                        'error': str(migration_error)
                    })
                    print(f"❌ Failed to migrate article {article_id}: {migration_error}")
            
            results['success_count'] = len(results['migrated_articles'])
            results['failure_count'] = len(results['failed_migrations'])
            results['success_rate'] = (results['success_count'] / max(1, results['total_attempted'])) * 100
            
            print(f"🎉 MIGRATION COMPLETE: {results['success_count']}/{results['total_attempted']} articles migrated ({results['success_rate']:.1f}% success rate)")
            
            return results
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            return {
                'error': f"Migration failed: {str(e)}",
                'migration_timestamp': datetime.utcnow().isoformat()
            }

    def extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML content for reprocessing"""
        try:
            import re
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html_content)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return html_content

    async def get_engine_statistics(self) -> Dict[str, Any]:
        """Get statistics about articles created by different engines"""
        try:
            print(f"📊 GATHERING ENGINE STATISTICS")
            
            # Count articles by engine
            total_articles = await db.content_library.count_documents({})
            
            refined_articles = await db.content_library.count_documents({
                "metadata.refined_engine": True
            })
            
            advanced_articles = await db.content_library.count_documents({
                "metadata.advanced_refined_engine": True
            })
            
            legacy_articles = total_articles - refined_articles - advanced_articles
            
            # Get processing approaches
            approach_pipeline = [
                {"$match": {"metadata.processing_approach": {"$exists": True}}},
                {"$group": {"_id": "$metadata.processing_approach", "count": {"$sum": 1}}}
            ]
            
            approach_stats = {}
            async for doc in db.content_library.aggregate(approach_pipeline):
                approach_stats[doc['_id']] = doc['count']
            
            # Get content types (for advanced engine)
            content_type_pipeline = [
                {"$match": {"metadata.content_type": {"$exists": True}}},
                {"$group": {"_id": "$metadata.content_type", "count": {"$sum": 1}}}
            ]
            
            content_type_stats = {}
            async for doc in db.content_library.aggregate(content_type_pipeline):
                content_type_stats[doc['_id']] = doc['count']
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'total_articles': total_articles,
                'engine_distribution': {
                    'legacy_engine': legacy_articles,
                    'refined_2.0': refined_articles,
                    'advanced_2.1': advanced_articles
                },
                'engine_percentages': {
                    'legacy_engine': (legacy_articles / max(1, total_articles)) * 100,
                    'refined_2.0': (refined_articles / max(1, total_articles)) * 100,
                    'advanced_2.1': (advanced_articles / max(1, total_articles)) * 100
                },
                'processing_approaches': approach_stats,
                'content_types': content_type_stats,
                'migration_candidates': {
                    'legacy_articles': legacy_articles,
                    'refined_upgradeable': refined_articles  # Could be upgraded to advanced
                }
            }
            
        except Exception as e:
            print(f"❌ Error getting engine statistics: {e}")
            return {
                'error': f"Statistics failed: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            }


# Global instance
migration_tool = EngineMigrationTool()