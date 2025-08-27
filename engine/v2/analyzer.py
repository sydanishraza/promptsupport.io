"""
KE-PR4: V2 Multi-Dimensional Analyzer
Extracted from server.py - Advanced multi-dimensional content analysis
"""

import uuid
from datetime import datetime

# Import required dependencies
# TODO: These will need to be imported from appropriate locations
# from ..database import db
# from ..llm import call_llm_with_fallback


class V2MultiDimensionalAnalyzer:
    """V2 Engine: Advanced multi-dimensional content analysis for classification and granularity determination"""
    
    def __init__(self):
        self.content_types = ["tutorial", "reference", "conceptual", "compliance", "release_notes"]
        self.audiences = ["developer", "end_user", "admin", "business"]  
        self.format_signals = ["code_heavy", "table_heavy", "diagram_heavy", "narrative", "list_heavy"]
        self.complexity_levels = ["basic", "intermediate", "advanced"]
        self.granularity_levels = {
            "unified": 1,
            "shallow": 3, 
            "moderate": (4, 6),
            "deep": 7
        }
    
    async def analyze_normalized_document(self, normalized_doc, run_id: str) -> dict:
        """V2 Engine: Perform comprehensive multi-dimensional analysis of normalized document"""
        try:
            print(f"🔍 V2 ANALYSIS: Starting multi-dimensional analysis - {normalized_doc.title} - engine=v2")
            
            # Create preview of normalized document for LLM analysis
            doc_preview = self._create_document_preview(normalized_doc)
            
            # Perform LLM-based analysis using the specified prompt
            analysis_result = await self._perform_llm_analysis(doc_preview)
            
            if analysis_result:
                # Validate and enhance analysis with rule-based insights
                enhanced_analysis = await self._enhance_analysis(analysis_result, normalized_doc)
                
                # Store analysis with the run
                stored_analysis = await self._store_analysis(enhanced_analysis, run_id, normalized_doc.doc_id)
                
                print(f"✅ V2 ANALYSIS: Multi-dimensional analysis complete - {enhanced_analysis.get('granularity', 'unknown')} granularity - engine=v2")
                return stored_analysis
            else:
                # Fallback to rule-based analysis
                print(f"🔄 V2 ANALYSIS: LLM analysis failed, using rule-based fallback - engine=v2")
                fallback_analysis = await self._rule_based_analysis(normalized_doc)
                return await self._store_analysis(fallback_analysis, run_id, normalized_doc.doc_id)
                
        except Exception as e:
            print(f"❌ V2 ANALYSIS: Error in multi-dimensional analysis - {e} - engine=v2")
            # Return basic fallback analysis
            return await self._create_fallback_analysis(run_id, normalized_doc.doc_id)
    
    def _create_document_preview(self, normalized_doc) -> str:
        """Create a structured preview of the normalized document for LLM analysis"""
        try:
            preview_parts = []
            
            # Document metadata
            preview_parts.append(f"DOCUMENT: {normalized_doc.title}")
            preview_parts.append(f"FILENAME: {normalized_doc.original_filename or 'Unknown'}")
            preview_parts.append(f"WORD_COUNT: {normalized_doc.word_count}")
            preview_parts.append(f"BLOCK_COUNT: {len(normalized_doc.blocks)}")
            preview_parts.append(f"MEDIA_COUNT: {len(normalized_doc.media)}")
            
            if normalized_doc.page_count:
                preview_parts.append(f"PAGE_COUNT: {normalized_doc.page_count}")
            
            preview_parts.append("\nCONTENT STRUCTURE:")
            
            # Analyze content blocks
            block_types = {}
            code_blocks = 0
            table_blocks = 0
            list_blocks = 0 
            heading_levels = {}
            
            for block in normalized_doc.blocks[:20]:  # Limit to first 20 blocks for preview
                block_type = block.block_type
                block_types[block_type] = block_types.get(block_type, 0) + 1
                
                if block_type == 'code':
                    code_blocks += 1
                elif block_type == 'table':
                    table_blocks += 1
                elif block_type == 'list':
                    list_blocks += 1
                elif block_type == 'heading' and hasattr(block, 'level') and block.level:
                    heading_levels[block.level] = heading_levels.get(block.level, 0) + 1
                
                # Add block content preview (first 200 chars)
                content_preview = block.content[:200] + "..." if len(block.content) > 200 else block.content
                preview_parts.append(f"- {block_type.upper()}: {content_preview}")
            
            # Add structural analysis
            preview_parts.append(f"\nSTRUCTURAL ANALYSIS:")
            preview_parts.append(f"Block Types: {dict(block_types)}")
            preview_parts.append(f"Code Blocks: {code_blocks}")
            preview_parts.append(f"Table Blocks: {table_blocks}")
            preview_parts.append(f"List Blocks: {list_blocks}")
            preview_parts.append(f"Heading Levels: {dict(heading_levels)}")
            
            # Media analysis
            if normalized_doc.media:
                media_types = {}
                for media in normalized_doc.media:
                    media_type = media.media_type
                    media_types[media_type] = media_types.get(media_type, 0) + 1
                preview_parts.append(f"Media Types: {dict(media_types)}")
            
            return "\n".join(preview_parts)
            
        except Exception as e:
            print(f"❌ V2 ANALYSIS: Error creating document preview - {e}")
            return f"DOCUMENT: {normalized_doc.title}\nWORD_COUNT: {normalized_doc.word_count}\nBLOCK_COUNT: {len(normalized_doc.blocks)}"
    
    async def _perform_llm_analysis(self, doc_preview: str) -> dict:
        """Perform LLM-based analysis using the specified prompt format"""
        try:
            system_message = """You are a documentation analyst. Classify the uploaded resource for technical documentation purposes.

Analyze the content and determine:
1. content_type: tutorial (step-by-step instructions), reference (API docs, specifications), conceptual (explanatory content), compliance (policies, regulations), release_notes (updates, changelogs)
2. audience: developer (technical implementation), end_user (user guides), admin (configuration), business (strategy, planning)
3. format_signals: code_heavy (significant code blocks), table_heavy (extensive tabular data), diagram_heavy (visual elements), narrative (text-heavy explanatory), list_heavy (bullet points, enumerated items)
4. complexity: basic (simple content, <3000 chars), intermediate (moderate complexity, 3000-10000 chars), advanced (complex documentation, >10000 chars)
5. granularity: unified (keep as single article), shallow (split into 3 articles), moderate (split into 4-6 articles), deep (split into 7+ articles)

Consider content length, structure, technical depth, and audience needs when determining granularity."""

            user_message = f"""Analyze this normalized document and return classification:

<normalized_docs_preview>
{doc_preview}
</normalized_docs_preview>

Return ONLY a JSON object in this exact format:
{{
  "analysis": {{
    "content_type": "tutorial|reference|conceptual|compliance|release_notes",
    "audience": "developer|end_user|admin|business",
    "format_signals": ["code_heavy|table_heavy|diagram_heavy|narrative|list_heavy"],
    "complexity": "basic|intermediate|advanced",
    "granularity": "unified|shallow|moderate|deep"
  }}
}}"""

            print(f"🤖 V2 ANALYSIS: Sending document to LLM for multi-dimensional analysis - engine=v2")
            
            # Use existing LLM system
            # TODO: Import this from appropriate location
            # ai_response = await call_llm_with_fallback(system_message, user_message)
            ai_response = None  # Placeholder until imports are fixed
            
            if ai_response:
                # Parse JSON response
                import json
                import re
                
                # Clean response and extract JSON
                cleaned_response = re.sub(r'[-\x1f\x7f-\x9f]', '', ai_response)
                
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    analysis_data = json.loads(json_str)
                    
                    # Extract analysis object
                    if 'analysis' in analysis_data:
                        analysis = analysis_data['analysis']
                        print(f"🎯 V2 ANALYSIS: LLM analysis successful - {analysis.get('content_type')} / {analysis.get('audience')} / {analysis.get('granularity')} - engine=v2")
                        return analysis
                    else:
                        print(f"⚠️ V2 ANALYSIS: Analysis object not found in LLM response - engine=v2")
                        return None
                else:
                    print(f"⚠️ V2 ANALYSIS: No JSON found in LLM response - engine=v2")
                    return None
            else:
                print(f"❌ V2 ANALYSIS: No response from LLM - engine=v2")
                return None
                
        except Exception as e:
            print(f"❌ V2 ANALYSIS: Error in LLM analysis - {e} - engine=v2")
            return None
    
    async def _enhance_analysis(self, llm_analysis: dict, normalized_doc) -> dict:
        """Enhance LLM analysis with rule-based insights and validation"""
        try:
            enhanced = llm_analysis.copy()
            
            # Validate and enhance format signals based on actual content
            actual_signals = []
            
            # Check for code blocks
            code_count = sum(1 for block in normalized_doc.blocks if block.block_type == 'code')
            if code_count > 2 or (normalized_doc.word_count > 0 and code_count / len(normalized_doc.blocks) > 0.15):
                actual_signals.append("code_heavy")
            
            # Check for tables
            table_count = sum(1 for block in normalized_doc.blocks if block.block_type == 'table')
            if table_count > 1 or (normalized_doc.word_count > 0 and table_count / len(normalized_doc.blocks) > 0.1):
                actual_signals.append("table_heavy")
            
            # Check for lists
            list_count = sum(1 for block in normalized_doc.blocks if block.block_type == 'list')
            if list_count > 3 or (normalized_doc.word_count > 0 and list_count / len(normalized_doc.blocks) > 0.2):
                actual_signals.append("list_heavy")
            
            # Check for diagrams/media
            if len(normalized_doc.media) > 2:
                actual_signals.append("diagram_heavy")
            
            # Default to narrative if no specific signals
            if not actual_signals:
                actual_signals.append("narrative")
            
            # Enhance format signals with actual analysis
            enhanced['format_signals'] = list(set(enhanced.get('format_signals', []) + actual_signals))
            
            # Validate complexity based on word count and structure
            word_count = normalized_doc.word_count
            if word_count < 3000:
                if enhanced.get('complexity') == 'advanced':
                    enhanced['complexity'] = 'intermediate'
            elif word_count > 10000:
                if enhanced.get('complexity') == 'basic':
                    enhanced['complexity'] = 'intermediate'
            
            # Validate granularity based on content length and structure
            heading_count = sum(1 for block in normalized_doc.blocks if block.block_type == 'heading')
            if heading_count > 10 and word_count > 8000:
                if enhanced.get('granularity') in ['unified', 'shallow']:
                    enhanced['granularity'] = 'moderate'
            elif heading_count > 15 and word_count > 15000:
                if enhanced.get('granularity') != 'deep':
                    enhanced['granularity'] = 'deep'
            elif heading_count < 3 and word_count < 2000:
                enhanced['granularity'] = 'unified'
            
            # Add confidence scores and analysis metadata
            enhanced['analysis_metadata'] = {
                "word_count": word_count,
                "block_count": len(normalized_doc.blocks),
                "media_count": len(normalized_doc.media),
                "heading_count": heading_count,
                "code_blocks": code_count,
                "table_blocks": table_count,
                "list_blocks": list_count,
                "analysis_method": "llm_enhanced",
                "engine": "v2"
            }
            
            return enhanced
            
        except Exception as e:
            print(f"❌ V2 ANALYSIS: Error enhancing analysis - {e} - engine=v2")
            return llm_analysis
    
    async def _rule_based_analysis(self, normalized_doc) -> dict:
        """Fallback rule-based analysis when LLM is unavailable"""
        try:
            print(f"🔧 V2 ANALYSIS: Performing rule-based analysis fallback - engine=v2")
            
            word_count = normalized_doc.word_count
            block_count = len(normalized_doc.blocks)
            media_count = len(normalized_doc.media)
            
            # Count specific block types
            code_blocks = sum(1 for block in normalized_doc.blocks if block.block_type == 'code')
            table_blocks = sum(1 for block in normalized_doc.blocks if block.block_type == 'table')
            list_blocks = sum(1 for block in normalized_doc.blocks if block.block_type == 'list')
            heading_blocks = sum(1 for block in normalized_doc.blocks if block.block_type == 'heading')
            
            # Determine content type based on structure
            content_type = "conceptual"  # Default
            if code_blocks > 3:
                content_type = "tutorial"
            elif table_blocks > 2:
                content_type = "reference"
            elif "release" in normalized_doc.title.lower() or "changelog" in normalized_doc.title.lower():
                content_type = "release_notes"
            elif "policy" in normalized_doc.title.lower() or "compliance" in normalized_doc.title.lower():
                content_type = "compliance"
            
            # Determine audience
            audience = "end_user"  # Default
            if code_blocks > 2 or "api" in normalized_doc.title.lower():
                audience = "developer"
            elif "admin" in normalized_doc.title.lower() or "configuration" in normalized_doc.title.lower():
                audience = "admin"
            elif "business" in normalized_doc.title.lower() or "strategy" in normalized_doc.title.lower():
                audience = "business"
            
            # Determine format signals
            format_signals = []
            if code_blocks > 2:
                format_signals.append("code_heavy")
            if table_blocks > 1:
                format_signals.append("table_heavy")
            if list_blocks > 3:
                format_signals.append("list_heavy")
            if media_count > 2:
                format_signals.append("diagram_heavy")
            if not format_signals:
                format_signals.append("narrative")
            
            # Determine complexity
            if word_count < 3000:
                complexity = "basic"
            elif word_count > 10000:
                complexity = "advanced"
            else:
                complexity = "intermediate"
            
            # Determine granularity
            if word_count < 2000 and heading_blocks < 3:
                granularity = "unified"
            elif word_count > 15000 and heading_blocks > 15:
                granularity = "deep"
            elif word_count > 8000 and heading_blocks > 8:
                granularity = "moderate"
            else:
                granularity = "shallow"
            
            analysis = {
                "content_type": content_type,
                "audience": audience,
                "format_signals": format_signals,
                "complexity": complexity,
                "granularity": granularity,
                "analysis_metadata": {
                    "word_count": word_count,
                    "block_count": block_count,
                    "media_count": media_count,
                    "heading_count": heading_blocks,
                    "code_blocks": code_blocks,
                    "table_blocks": table_blocks,
                    "list_blocks": list_blocks,
                    "analysis_method": "rule_based_fallback",
                    "engine": "v2"
                }
            }
            
            print(f"🎯 V2 ANALYSIS: Rule-based analysis complete - {content_type} / {audience} / {granularity} - engine=v2")
            return analysis
            
        except Exception as e:
            print(f"❌ V2 ANALYSIS: Error in rule-based analysis - {e} - engine=v2")
            return self._create_basic_fallback_analysis()
    
    def _create_basic_fallback_analysis(self) -> dict:
        """Create basic fallback analysis for error cases"""
        return {
            "content_type": "conceptual",
            "audience": "end_user", 
            "format_signals": ["narrative"],
            "complexity": "intermediate",
            "granularity": "shallow",
            "analysis_metadata": {
                "analysis_method": "basic_fallback",
                "engine": "v2"
            }
        }
    
    async def _store_analysis(self, analysis: dict, run_id: str, doc_id: str) -> dict:
        """Store analysis results with the processing run"""
        try:
            # Create comprehensive analysis record
            analysis_record = {
                "analysis_id": str(uuid.uuid4()),
                "run_id": run_id,
                "doc_id": doc_id,
                "analysis": analysis,
                "created_at": datetime.utcnow().isoformat(),
                "engine": "v2",
                "version": "2.0"
            }
            
            # Store in analysis collection
            # TODO: Import db from appropriate location
            # await db.v2_analysis.insert_one(analysis_record)
            
            print(f"📊 V2 ANALYSIS: Analysis stored with run {run_id} - engine=v2")
            return analysis_record
            
        except Exception as e:
            print(f"❌ V2 ANALYSIS: Error storing analysis - {e} - engine=v2")
            return {"analysis": analysis, "run_id": run_id, "doc_id": doc_id}
    
    async def _create_fallback_analysis(self, run_id: str, doc_id: str) -> dict:
        """Create and store fallback analysis for error cases"""
        fallback = self._create_basic_fallback_analysis()
        return await self._store_analysis(fallback, run_id, doc_id)
    
    async def get_analysis_for_run(self, run_id: str) -> dict:
        """Retrieve stored analysis for a processing run"""
        try:
            # TODO: Import db from appropriate location
            # analysis_record = await db.v2_analysis.find_one({"run_id": run_id})
            analysis_record = None  # Placeholder
            
            if analysis_record:
                return analysis_record
            else:
                print(f"⚠️ V2 ANALYSIS: No analysis found for run {run_id} - engine=v2")
                return None
        except Exception as e:
            print(f"❌ V2 ANALYSIS: Error retrieving analysis - {e} - engine=v2")
            return None


# Global V2 Multi-Dimensional Analyzer instance
v2_analyzer = V2MultiDimensionalAnalyzer()