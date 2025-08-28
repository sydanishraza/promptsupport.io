"""
KE-M1: V2 Outline Planning System - Complete Implementation Migration
Migrated from server.py - Global and per-article outline planning with LLM intelligence
"""

from typing import Dict, Any, List, Optional
from ..llm.client import get_llm_client
from ..llm.prompts import ARTICLE_OUTLINE_PROMPT
from ._utils import generate_run_id, create_processing_metadata
import json

class V2GlobalOutlinePlanner:
    """V2 Engine: Global outline planning with 100% block assignment and granularity compliance"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.granularity_article_counts = {
            "unified": 1,
            "shallow": 3,
            "moderate": (4, 6),  # Range for moderate
            "deep": 7  # Minimum for deep
        }
        
        self.discard_reasons = ["duplicate", "boilerplate", "junk"]
    
    async def create_global_outline(self, normalized_doc=None, analysis: dict = None, run_id: str = None, **kwargs) -> dict:
        """V2 Engine: Create comprehensive global outline with 100% block coverage
        
        Supports both new interface (analysis_result) and legacy interface (normalized_doc, analysis)
        """
        try:
            # Handle both new and legacy interfaces
            if normalized_doc is None and analysis is None:
                # New interface - extract from kwargs
                analysis_result = kwargs.get('analysis_result', {})
                return await self._create_global_outline_new(analysis_result)
            else:
                # Legacy interface - use normalized_doc and analysis
                return await self._create_global_outline_legacy(normalized_doc, analysis, run_id)
                
        except Exception as e:
            print(f"❌ V2 GLOBAL OUTLINE: Error creating outline - {e}")
            return await self._create_fallback_outline(normalized_doc, run_id or generate_run_id())
    
    async def _create_global_outline_new(self, analysis_result: dict) -> dict:
        """Create global outline structure from analysis results (new interface)"""
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
    
    async def _create_global_outline_legacy(self, normalized_doc, analysis: dict, run_id: str) -> dict:
        """Create comprehensive global outline with 100% block coverage (legacy interface)"""
        try:
            print(f"📋 V2 OUTLINE: Creating global outline for {normalized_doc.title} - engine=v2")
            
            granularity = analysis.get('granularity', 'shallow')
            content_type = analysis.get('content_type', 'conceptual')
            audience = analysis.get('audience', 'end_user')
            
            # Create document preview with block details for LLM analysis
            doc_preview_with_blocks = self._create_detailed_block_preview(normalized_doc, analysis)
            
            # Perform LLM-based outline planning
            outline_result = await self._perform_llm_outline_planning(doc_preview_with_blocks, analysis)
            
            if outline_result:
                # Validate and enhance outline
                validated_outline = await self._validate_and_enhance_outline(outline_result, normalized_doc, granularity)
                
                # Store outline with run
                stored_outline = await self._store_global_outline(validated_outline, run_id, normalized_doc.doc_id)
                
                print(f"✅ V2 OUTLINE: Global outline created - {len(validated_outline.get('articles', []))} articles, {len(validated_outline.get('discarded_blocks', []))} discarded blocks - engine=v2")
                return stored_outline
            else:
                # Fallback to rule-based outline planning
                print(f"🔄 V2 OUTLINE: LLM planning failed, using rule-based fallback - engine=v2")
                fallback_outline = await self._rule_based_outline_planning(normalized_doc, analysis)
                return await self._store_global_outline(fallback_outline, run_id, normalized_doc.doc_id)
                
        except Exception as e:
            print(f"❌ V2 OUTLINE: Error creating global outline - {e} - engine=v2")
            # Create basic fallback outline
            return await self._create_fallback_outline(normalized_doc, run_id)
    
    def _create_detailed_block_preview(self, normalized_doc, analysis: dict) -> str:
        """Create detailed preview with all blocks for LLM outline planning"""
        try:
            preview_parts = []
            
            # Document and analysis metadata
            preview_parts.append(f"DOCUMENT: {normalized_doc.title}")
            preview_parts.append(f"ANALYSIS: {analysis}")
            preview_parts.append(f"TOTAL_BLOCKS: {len(normalized_doc.blocks)}")
            preview_parts.append(f"GRANULARITY: {analysis.get('granularity', 'shallow')}")
            preview_parts.append(f"CONTENT_TYPE: {analysis.get('content_type', 'conceptual')}")
            preview_parts.append(f"AUDIENCE: {analysis.get('audience', 'end_user')}")
            
            # Detailed block listing
            preview_parts.append("\nALL BLOCKS (must be assigned or discarded):")
            
            for i, block in enumerate(normalized_doc.blocks):
                # Create unique block ID
                block_id = f"block_{i + 1}"
                
                # Get block preview (first 150 chars)
                content_preview = block.content[:150] + "..." if len(block.content) > 150 else block.content
                
                # Add block details
                block_info = f"ID:{block_id} | TYPE:{block.block_type}"
                if hasattr(block, 'level') and block.level:
                    block_info += f" | LEVEL:{block.level}"
                
                block_info += f" | CONTENT: {content_preview}"
                
                # Add source information if available
                if hasattr(block, 'source_pointer') and block.source_pointer:
                    if hasattr(block.source_pointer, 'page_number') and block.source_pointer.page_number:
                        block_info += f" | PAGE:{block.source_pointer.page_number}"
                    if hasattr(block.source_pointer, 'slide_number') and block.source_pointer.slide_number:
                        block_info += f" | SLIDE:{block.source_pointer.slide_number}"
                
                preview_parts.append(block_info)
            
            # Add media information
            if normalized_doc.media:
                preview_parts.append(f"\nMEDIA_ASSETS: {len(normalized_doc.media)} items")
                for i, media in enumerate(normalized_doc.media[:5]):  # Show first 5 media items
                    media_info = f"MEDIA_{i+1}: {media.media_type} - {media.alt_text or 'No alt text'}"
                    preview_parts.append(media_info)
            
            return "\n".join(preview_parts)
            
        except Exception as e:
            print(f"❌ V2 OUTLINE: Error creating detailed block preview - {e}")
            return f"DOCUMENT: {normalized_doc.title}\nTOTAL_BLOCKS: {len(normalized_doc.blocks)}\nERROR: Could not create detailed preview"
    
    async def _perform_llm_outline_planning(self, doc_preview_with_blocks: str, analysis: dict) -> dict:
        """Perform LLM-based outline planning using specified prompt format"""
        try:
            granularity = analysis.get('granularity', 'shallow')
            
            # Article count guidance based on granularity
            if granularity == 'unified':
                count_guidance = "Create exactly 1 comprehensive article"
            elif granularity == 'shallow':
                count_guidance = "Create exactly 3 articles"
            elif granularity == 'moderate':
                count_guidance = "Create 4-6 articles (optimal range)"
            else:  # deep
                count_guidance = "Create 7 or more articles for detailed coverage"
            
            system_message = """You are a documentation planner. Split the source into articles and assign all blocks.

Your task is to create a comprehensive outline that assigns every single block to exactly one article OR explicitly discards it with a justified reason.

CRITICAL REQUIREMENTS:
1. Follow the granularity guidance for article count
2. EVERY block_id must be accounted for - either assigned to an article or discarded
3. Discarded blocks must have valid reasons: duplicate, boilerplate, or junk
4. Articles should have logical scope and coherent content flow
5. Proposed titles must be descriptive and specific to article content

ARTICLE ASSIGNMENT STRATEGY:
- Group related blocks by topic, function, or logical sequence
- Ensure articles have balanced content (avoid very small or very large articles)
- Consider content type and audience when grouping blocks
- Maintain document flow and logical progression

DISCARD CRITERIA:
- duplicate: Block content repeats information from other blocks
- boilerplate: Generic headers, footers, disclaimers, template text
- junk: Meaningless content, formatting artifacts, empty sections"""

            user_message = f"""Plan articles for this document based on the analysis and block details.

{count_guidance}

<normalized_docs_preview>
{doc_preview_with_blocks}
</normalized_docs_preview>

Requirements:
- Follow analysis.granularity for article count
- Assign each block_id to exactly one article, OR discard with a reason
- Return only JSON with articles[] and discarded_blocks[]

Return ONLY JSON in this exact format:
{{
  "articles": [
    {{
      "article_id": "a1",
      "proposed_title": "Specific descriptive title",
      "scope_summary": "Brief summary of what this article covers",
      "block_ids": ["block_1", "block_2", "block_3"]
    }}
  ],
  "discarded_blocks": [
    {{
      "block_id": "block_x",
      "reason": "duplicate|boilerplate|junk"
    }}
  ]
}}"""

            # Use centralized LLM client
            llm_response = await self.llm_client.complete(
                system_message=system_message,
                user_message=user_message,
                temperature=0.3,
                max_tokens=4000
            )
            
            if llm_response:
                # Parse JSON response
                outline_result = json.loads(llm_response)
                print(f"✅ V2 OUTLINE: LLM outline planning successful - {len(outline_result.get('articles', []))} articles")
                return outline_result
            else:
                print("⚠️ V2 OUTLINE: No response from LLM")
                return None
                
        except json.JSONDecodeError as e:
            print(f"⚠️ V2 OUTLINE: Invalid JSON response from LLM - {e}")
            return None
        except Exception as e:
            print(f"❌ V2 OUTLINE: Error in LLM outline planning - {e}")
            return None
    
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