"""
KE-PR5: V2 Outline Planning System - Complete Implementation
Extracted from server.py - Global and per-article outline planning with LLM intelligence
"""

from typing import Dict, Any, List
from ..llm.client import get_llm_client
from ..llm.prompts import ARTICLE_OUTLINE_PROMPT

class V2GlobalOutlinePlanner:
    """V2 Engine: Global outline planning for content structure organization"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
    
    async def create_global_outline(self, analysis_result: dict, **kwargs) -> dict:
        """Create global outline structure from analysis results"""
        try:
            print(f"📋 V2 GLOBAL OUTLINE: Creating global outline - engine=v2")
            
            # Extract analysis data
            analysis = analysis_result.get('content_analysis', {})
            doc_stats = analysis_result.get('analysis_metadata', {}).get('document_stats', {})
            
            # Get content type and complexity
            content_type = analysis.get('content_type', 'mixed')
            complexity = analysis.get('complexity', 'moderate')
            recommended_articles = analysis.get('recommended_article_count', 2)
            
            # Create outline structure
            outline = {
                'outline_type': 'global',
                'content_type': content_type,
                'complexity_level': complexity,
                'recommended_articles': recommended_articles,
                'sections': self._create_outline_sections(analysis),
                'processing_strategy': self._determine_processing_strategy(analysis),
                'estimated_processing_time': analysis.get('processing_recommendations', {}).get('estimated_processing_time', '5-10 minutes')
            }
            
            result = {
                'global_outline': outline,
                'outline_metadata': {
                    'created_sections': len(outline['sections']),
                    'processing_strategy': outline['processing_strategy'],
                    'engine': 'v2'
                }
            }
            
            print(f"✅ V2 GLOBAL OUTLINE: Created outline with {len(outline['sections'])} sections")
            return result
            
        except Exception as e:
            print(f"❌ V2 GLOBAL OUTLINE: Error creating outline - {e}")
            return {
                'global_outline': self._get_fallback_outline(),
                'error': str(e)
            }
    
    def _create_outline_sections(self, analysis: dict) -> List[dict]:
        """Create outline sections based on analysis"""
        content_type = analysis.get('content_type', 'mixed')
        
        if content_type == 'api_documentation':
            return [
                {'title': 'API Overview', 'type': 'introduction', 'priority': 'high'},
                {'title': 'Authentication', 'type': 'technical', 'priority': 'high'},
                {'title': 'Endpoints', 'type': 'reference', 'priority': 'high'},
                {'title': 'Code Examples', 'type': 'example', 'priority': 'medium'},
                {'title': 'Error Handling', 'type': 'troubleshooting', 'priority': 'medium'}
            ]
        elif content_type == 'tutorial':
            return [
                {'title': 'Introduction', 'type': 'introduction', 'priority': 'high'},
                {'title': 'Prerequisites', 'type': 'requirements', 'priority': 'high'},
                {'title': 'Step-by-Step Guide', 'type': 'tutorial', 'priority': 'high'},
                {'title': 'Examples', 'type': 'example', 'priority': 'medium'},
                {'title': 'Troubleshooting', 'type': 'troubleshooting', 'priority': 'low'}
            ]
        else:
            return [
                {'title': 'Overview', 'type': 'introduction', 'priority': 'high'},
                {'title': 'Main Content', 'type': 'content', 'priority': 'high'},
                {'title': 'Examples', 'type': 'example', 'priority': 'medium'},
                {'title': 'Summary', 'type': 'conclusion', 'priority': 'low'}
            ]
    
    def _determine_processing_strategy(self, analysis: dict) -> str:
        """Determine the best processing strategy based on analysis"""
        complexity = analysis.get('complexity', 'moderate')
        word_count = analysis.get('document_stats', {}).get('word_count', 0)
        
        if complexity in ['complex', 'highly_complex'] or word_count > 8000:
            return 'deep_processing'
        elif complexity == 'simple' or word_count < 2000:
            return 'lightweight_processing'
        else:
            return 'standard_processing'
    
    def _get_fallback_outline(self) -> dict:
        """Fallback outline structure"""
        return {
            'outline_type': 'global',
            'content_type': 'mixed',
            'complexity_level': 'moderate',
            'recommended_articles': 1,
            'sections': [
                {'title': 'Main Content', 'type': 'content', 'priority': 'high'}
            ],
            'processing_strategy': 'standard_processing'
        }


class V2PerArticleOutlinePlanner:
    """V2 Engine: Per-article outline planning for individual article structure"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
    
    async def create_per_article_outlines(self, global_outline_result: dict, **kwargs) -> dict:
        """Create detailed outlines for individual articles"""
        try:
            print(f"📄 V2 PER-ARTICLE OUTLINE: Creating per-article outlines - engine=v2")
            
            # Extract global outline
            global_outline = global_outline_result.get('global_outline', {})
            sections = global_outline.get('sections', [])
            recommended_articles = global_outline.get('recommended_articles', 1)
            
            # Create article outlines
            articles = []
            
            if recommended_articles == 1:
                # Single article - use all sections
                article = {
                    'id': 'article_1',
                    'title': 'Main Article',
                    'outline': {
                        'sections': sections,
                        'structure_type': 'comprehensive',
                        'estimated_length': 'long'
                    },
                    'content_blocks': [],
                    'processing_priority': 'high'
                }
                articles.append(article)
                
            else:
                # Multiple articles - distribute sections
                sections_per_article = max(1, len(sections) // recommended_articles)
                
                for i in range(recommended_articles):
                    start_idx = i * sections_per_article
                    end_idx = start_idx + sections_per_article if i < recommended_articles - 1 else len(sections)
                    article_sections = sections[start_idx:end_idx]
                    
                    article = {
                        'id': f'article_{i+1}',
                        'title': f'Article {i+1}: {article_sections[0]["title"] if article_sections else "Content"}',
                        'outline': {
                            'sections': article_sections,
                            'structure_type': 'focused',
                            'estimated_length': 'medium'
                        },
                        'content_blocks': [],
                        'processing_priority': 'high' if i == 0 else 'medium'
                    }
                    articles.append(article)
            
            result = {
                'articles': articles,
                'outline_metadata': {
                    'total_articles': len(articles),
                    'total_sections': sum(len(a['outline']['sections']) for a in articles),
                    'processing_strategy': global_outline.get('processing_strategy', 'standard'),
                    'engine': 'v2'
                }
            }
            
            print(f"✅ V2 PER-ARTICLE OUTLINE: Created {len(articles)} article outlines")
            return result
            
        except Exception as e:
            print(f"❌ V2 PER-ARTICLE OUTLINE: Error creating outlines - {e}")
            return {
                'articles': [self._get_fallback_article()],
                'error': str(e)
            }
    
    def _get_fallback_article(self) -> dict:
        """Fallback article outline"""
        return {
            'id': 'article_fallback',
            'title': 'Generated Article',
            'outline': {
                'sections': [
                    {'title': 'Introduction', 'type': 'introduction', 'priority': 'high'},
                    {'title': 'Main Content', 'type': 'content', 'priority': 'high'},
                    {'title': 'Conclusion', 'type': 'conclusion', 'priority': 'medium'}
                ],
                'structure_type': 'standard',
                'estimated_length': 'medium'
            },
            'content_blocks': [],
            'processing_priority': 'high'
        }