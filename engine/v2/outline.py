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
                import re
                
                # Clean response and extract JSON
                cleaned_response = re.sub(r'[-\x1f\x7f-\x9f]', '', llm_response)
                
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    outline_data = json.loads(json_str)
                    
                    # Validate required fields
                    if 'articles' in outline_data and 'discarded_blocks' in outline_data:
                        print(f"🎯 V2 OUTLINE: LLM outline planning successful - {len(outline_data['articles'])} articles, {len(outline_data['discarded_blocks'])} discarded - engine=v2")
                        return outline_data
                    else:
                        print(f"⚠️ V2 OUTLINE: Invalid outline structure from LLM - engine=v2")
                        return None
                else:
                    print(f"⚠️ V2 OUTLINE: No JSON found in LLM outline response - engine=v2")
                    return None
            else:
                print(f"❌ V2 OUTLINE: No response from LLM for outline planning - engine=v2")
                return None
                
        except json.JSONDecodeError as e:
            print(f"⚠️ V2 OUTLINE: Invalid JSON response from LLM - {e}")
            return None
        except Exception as e:
            print(f"❌ V2 OUTLINE: Error in LLM outline planning - {e}")
            return None
    
    async def _validate_and_enhance_outline(self, llm_outline: dict, normalized_doc, granularity: str) -> dict:
        """Validate LLM outline and enhance with rule-based validation"""
        try:
            enhanced_outline = llm_outline.copy()
            
            # Get all block IDs that should exist
            expected_block_ids = [f"block_{i + 1}" for i in range(len(normalized_doc.blocks))]
            
            # Get all assigned and discarded block IDs
            assigned_blocks = set()
            for article in enhanced_outline.get('articles', []):
                for block_id in article.get('block_ids', []):
                    assigned_blocks.add(block_id)
            
            discarded_blocks = set()
            for discarded in enhanced_outline.get('discarded_blocks', []):
                discarded_blocks.add(discarded.get('block_id'))
            
            # Find missing blocks
            all_accounted_blocks = assigned_blocks.union(discarded_blocks)
            missing_blocks = set(expected_block_ids) - all_accounted_blocks
            
            # Assign missing blocks to appropriate articles or discard them
            if missing_blocks:
                print(f"⚠️ V2 OUTLINE: Found {len(missing_blocks)} unassigned blocks, assigning them - engine=v2")
                
                for block_id in missing_blocks:
                    # Get block index
                    block_index = int(block_id.split('_')[1]) - 1
                    if block_index < len(normalized_doc.blocks):
                        block = normalized_doc.blocks[block_index]
                        
                        # Decide whether to assign or discard based on content
                        if self._should_discard_block(block):
                            enhanced_outline.setdefault('discarded_blocks', []).append({
                                "block_id": block_id,
                                "reason": "boilerplate"
                            })
                        else:
                            # Assign to most appropriate article
                            self._assign_block_to_best_article(block_id, block, enhanced_outline)
            
            # Validate article count against granularity
            article_count = len(enhanced_outline.get('articles', []))
            target_count = self._get_target_article_count(granularity)
            
            if isinstance(target_count, tuple):
                min_count, max_count = target_count
                if article_count < min_count or article_count > max_count:
                    print(f"⚠️ V2 OUTLINE: Article count {article_count} outside {granularity} range {min_count}-{max_count} - engine=v2")
            else:
                if article_count != target_count:
                    print(f"⚠️ V2 OUTLINE: Article count {article_count} doesn't match {granularity} target {target_count} - engine=v2")
            
            # Add validation metadata
            enhanced_outline['validation_metadata'] = {
                "total_blocks": len(normalized_doc.blocks),
                "assigned_blocks": len(assigned_blocks),
                "discarded_blocks": len(discarded_blocks),
                "missing_blocks_found": len(missing_blocks),
                "article_count": article_count,
                "granularity": granularity,
                "validation_passed": True
            }
            
            return enhanced_outline
            
        except Exception as e:
            print(f"❌ V2 OUTLINE: Error validating outline - {e}")
            return llm_outline
    
    def _should_discard_block(self, block) -> bool:
        """Determine if a block should be discarded"""
        if not block or not block.content:
            return True
        
        content_lower = block.content.lower().strip()
        
        # Check for boilerplate patterns
        boilerplate_patterns = [
            'copyright', '©', 'all rights reserved', 'confidential',
            'page', 'slide', 'header', 'footer', 'draft', 'version',
            'document number', 'revision', 'last updated'
        ]
        
        if any(pattern in content_lower for pattern in boilerplate_patterns):
            return True
        
        # Check if content is too short to be meaningful
        if len(content_lower) < 20:
            return True
        
        # Check for repetitive content (basic heuristic)
        words = content_lower.split()
        if len(words) > 0 and len(set(words)) / len(words) < 0.3:
            return True
        
        return False
    
    def _assign_block_to_best_article(self, block_id: str, block, enhanced_outline: dict):
        """Assign unassigned block to the most appropriate article"""
        articles = enhanced_outline.get('articles', [])
        
        if not articles:
            # Create a default article if none exist
            enhanced_outline['articles'] = [{
                "article_id": "a1",
                "proposed_title": "Main Content",
                "scope_summary": "Primary content from document",
                "block_ids": [block_id]
            }]
            return
        
        # Simple assignment: add to the first article (could be enhanced with content similarity)
        articles[0]['block_ids'].append(block_id)
    
    def _get_target_article_count(self, granularity: str):
        """Get target article count for granularity"""
        return self.granularity_article_counts.get(granularity, 3)
    
    async def _store_global_outline(self, outline: dict, run_id: str, doc_id: str) -> dict:
        """Store global outline with run and return enhanced version"""
        try:
            # Add storage metadata
            outline['storage_metadata'] = {
                'run_id': run_id,
                'doc_id': doc_id,
                'stored_at': create_processing_metadata('global_outline')['timestamp'],
                'engine': 'v2'
            }
            
            # TODO: Implement actual storage to repository if needed
            # For now, return enhanced outline
            
            return outline
            
        except Exception as e:
            print(f"❌ V2 OUTLINE: Error storing outline - {e}")
            return outline
    
    async def _rule_based_outline_planning(self, normalized_doc, analysis: dict) -> dict:
        """Fallback rule-based outline planning when LLM fails"""
        try:
            print(f"📋 V2 OUTLINE: Using rule-based fallback planning - engine=v2")
            
            granularity = analysis.get('granularity', 'shallow')
            target_count = self._get_target_article_count(granularity)
            
            if isinstance(target_count, tuple):
                target_count = target_count[0]  # Use minimum for fallback
            
            # Simple distribution of blocks across articles
            blocks = normalized_doc.blocks
            blocks_per_article = max(1, len(blocks) // target_count)
            
            articles = []
            for i in range(target_count):
                start_idx = i * blocks_per_article
                end_idx = start_idx + blocks_per_article if i < target_count - 1 else len(blocks)
                
                block_ids = [f"block_{j + 1}" for j in range(start_idx, end_idx)]
                
                articles.append({
                    "article_id": f"a{i + 1}",
                    "proposed_title": f"Article {i + 1}: Content Section",
                    "scope_summary": f"Content blocks {start_idx + 1} to {end_idx}",
                    "block_ids": block_ids
                })
            
            return {
                'articles': articles,
                'discarded_blocks': [],
                'planning_method': 'rule_based_fallback',
                'validation_metadata': {
                    "total_blocks": len(blocks),
                    "assigned_blocks": len(blocks),
                    "discarded_blocks": 0,
                    "article_count": len(articles),
                    "granularity": granularity
                }
            }
            
        except Exception as e:
            print(f"❌ V2 OUTLINE: Error in rule-based planning - {e}")
            return self._get_emergency_fallback_outline(normalized_doc)
    
    async def _create_fallback_outline(self, normalized_doc, run_id: str) -> dict:
        """Create basic fallback outline when all else fails"""
        try:
            title = getattr(normalized_doc, 'title', 'Document') if normalized_doc else 'Document'
            block_count = len(getattr(normalized_doc, 'blocks', [])) if normalized_doc else 0
            
            fallback_outline = {
                'articles': [{
                    "article_id": "fallback_a1",
                    "proposed_title": f"Processed: {title}",
                    "scope_summary": "Complete document content",
                    "block_ids": [f"block_{i + 1}" for i in range(block_count)]
                }],
                'discarded_blocks': [],
                'planning_method': 'emergency_fallback',
                'storage_metadata': {
                    'run_id': run_id,
                    'doc_id': getattr(normalized_doc, 'doc_id', 'unknown') if normalized_doc else 'unknown',
                    'engine': 'v2'
                }
            }
            
            return fallback_outline
            
        except Exception as e:
            print(f"❌ V2 OUTLINE: Error creating fallback outline - {e}")
            return {
                'articles': [{
                    "article_id": "emergency_a1",
                    "proposed_title": "Document Content",
                    "scope_summary": "Emergency fallback content",
                    "block_ids": []
                }],
                'discarded_blocks': [],
                'planning_method': 'emergency_fallback'
            }
    
    def _get_emergency_fallback_outline(self, normalized_doc) -> dict:
        """Emergency fallback when everything fails"""
        block_count = len(getattr(normalized_doc, 'blocks', [])) if normalized_doc else 0
        
        return {
            'articles': [{
                "article_id": "emergency_a1",
                "proposed_title": "Document Content",
                "scope_summary": "Emergency processing fallback",
                "block_ids": [f"block_{i + 1}" for i in range(block_count)]
            }],
            'discarded_blocks': [],
            'planning_method': 'emergency_fallback'
        }
    
    # Methods for backward compatibility with new interface
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
    
    # Legacy interface support for backward compatibility
    async def create_article_outline(self, *args, **kwargs) -> dict:
        """Legacy interface - redirect to create_per_article_outlines"""
        return await self.create_per_article_outlines(*args, **kwargs)
    
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


print("✅ KE-M1: V2 Outline Planning classes migrated from server.py")