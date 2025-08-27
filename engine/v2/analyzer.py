"""
KE-PR6: V2 Multi-Dimensional Analyzer with Centralized LLM Client
Extracted from server.py - Deep content analysis with LLM-driven insights and rule-based validation
"""

from typing import Dict, Any, List
from ..llm.client import get_llm_client
from ..llm.prompts import CONTENT_ANALYSIS_PROMPT

class V2MultiDimensionalAnalyzer:
    """V2 Engine: Deep content analysis with LLM-driven insights and rule-based validation using centralized LLM client"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.analysis_dimensions = [
            'content_type', 'technical_depth', 'audience_level', 'granularity', 
            'structure', 'completeness', 'complexity'
        ]
        self.content_types = [
            'api_documentation', 'tutorial', 'how_to_guide', 'reference', 
            'troubleshooting', 'overview', 'specification', 'mixed'
        ]
    
    async def run(self, normalized_doc) -> dict:
        """
        Perform comprehensive multi-dimensional analysis using centralized LLM client
        Returns enhanced analysis with both LLM insights and rule-based validation
        """
        try:
            print(f"🔍 V2 ANALYZER: Starting multi-dimensional analysis with LLM client - engine=v2")
            
            # Create document preview for analysis
            doc_preview = self._create_document_preview(normalized_doc)
            
            # Perform LLM-based analysis using centralized client
            llm_analysis = await self._perform_llm_analysis(doc_preview)
            
            # Enhance with rule-based analysis
            enhanced_analysis = await self._enhance_analysis(llm_analysis, normalized_doc)
            
            analysis_result = {
                "content_analysis": enhanced_analysis,
                "analysis_metadata": {
                    "llm_provider": self.llm_client.provider,
                    "dimensions_analyzed": len(self.analysis_dimensions),
                    "engine": "v2",
                    "document_stats": {
                        "word_count": getattr(normalized_doc, 'word_count', 0),
                        "blocks_analyzed": len(getattr(normalized_doc, 'blocks', [])),
                        "title": getattr(normalized_doc, 'title', 'Unknown')
                    }
                }
            }
            
            print(f"✅ V2 ANALYZER: Analysis complete - {enhanced_analysis.get('content_type', 'unknown')} content")
            return analysis_result
            
        except Exception as e:
            print(f"❌ V2 ANALYZER: Error in multi-dimensional analysis - {e}")
            return {
                "content_analysis": self._get_fallback_analysis(),
                "error": str(e)
            }
    
    def _create_document_preview(self, normalized_doc) -> str:
        """Create a structured preview of the document for LLM analysis"""
        try:
            preview_parts = []
            
            # Document metadata
            title = getattr(normalized_doc, 'title', 'Unknown Document')
            word_count = getattr(normalized_doc, 'word_count', 0)
            preview_parts.append(f"DOCUMENT: {title}")
            preview_parts.append(f"WORD_COUNT: {word_count}")
            
            # Content blocks preview
            blocks = getattr(normalized_doc, 'blocks', [])
            preview_parts.append(f"CONTENT_BLOCKS: {len(blocks)}")
            
            # Sample content blocks (first few for analysis)
            for i, block in enumerate(blocks[:5]):  # Limit to first 5 blocks
                block_type = getattr(block, 'block_type', 'unknown')
                content = getattr(block, 'content', '')[:200]  # First 200 chars
                preview_parts.append(f"Block_{i+1}[{block_type}]: {content}")
            
            if len(blocks) > 5:
                preview_parts.append(f"... and {len(blocks) - 5} more blocks")
            
            return "\n".join(preview_parts)
            
        except Exception as e:
            print(f"❌ V2 ANALYZER: Error creating document preview - {e}")
            return f"DOCUMENT: {getattr(normalized_doc, 'title', 'Error')}\nERROR: Could not create preview"
    
    async def _perform_llm_analysis(self, doc_preview: str) -> dict:
        """Perform LLM-based analysis using centralized client"""
        try:
            system_message = """You are a documentation analyst. Classify the uploaded resource for technical documentation purposes.

ANALYSIS DIMENSIONS:
1. CONTENT_TYPE: [api_documentation, tutorial, how_to_guide, reference, troubleshooting, overview, specification, mixed]
2. TECHNICAL_DEPTH: [surface, intermediate, deep, expert]
3. AUDIENCE_LEVEL: [beginner, intermediate, advanced, expert]
4. GRANULARITY: [high_level, detailed, comprehensive]
5. STRUCTURE: [well_structured, moderately_structured, needs_organization]
6. COMPLETENESS: [complete, mostly_complete, partial, incomplete]
7. COMPLEXITY: [simple, moderate, complex, highly_complex]

Return your analysis in this JSON format:
{
  "content_type": "detected_type",
  "technical_depth": "detected_depth",
  "audience_level": "detected_level",
  "granularity": "detected_granularity",
  "structure": "detected_structure",
  "completeness": "detected_completeness",
  "complexity": "detected_complexity",
  "key_topics": ["topic1", "topic2", "topic3"],
  "recommended_article_count": 3,
  "confidence_score": 0.85
}"""

            user_message = f"Analyze this document content:\n\n{doc_preview}"
            
            # Use centralized LLM client
            response = await self.llm_client.complete(
                system_message=system_message,
                user_message=user_message,
                temperature=0.1,
                max_tokens=1000
            )
            
            if response:
                # Try to parse JSON response
                import json
                try:
                    llm_analysis = json.loads(response)
                    print(f"✅ V2 ANALYZER: LLM analysis complete - {llm_analysis.get('content_type', 'unknown')}")
                    return llm_analysis
                except json.JSONDecodeError:
                    # Fallback parsing if JSON is malformed
                    print("⚠️ V2 ANALYZER: LLM response not valid JSON, using fallback parsing")
                    return self._parse_llm_response(response)
            else:
                print("⚠️ V2 ANALYZER: No response from LLM, using rule-based fallback")
                return None
                
        except Exception as e:
            print(f"❌ V2 ANALYZER: Error in LLM analysis - {e}")
            return None
    
    async def _enhance_analysis(self, llm_analysis: dict, normalized_doc) -> dict:
        """Enhance LLM analysis with rule-based insights and validation"""
        try:
            if not llm_analysis:
                # Pure rule-based analysis if LLM failed
                return self._rule_based_analysis(normalized_doc)
            
            enhanced = llm_analysis.copy()
            
            # Add rule-based validation and enhancement
            blocks = getattr(normalized_doc, 'blocks', [])
            word_count = getattr(normalized_doc, 'word_count', 0)
            
            # Validate and enhance granularity based on word count
            if word_count > 5000:
                enhanced['granularity'] = 'comprehensive'
            elif word_count > 2000:
                enhanced['granularity'] = 'detailed'
            else:
                enhanced['granularity'] = 'high_level'
            
            # Enhance structure assessment
            heading_blocks = [b for b in blocks if getattr(b, 'block_type', '').startswith('heading')]
            if len(heading_blocks) >= len(blocks) * 0.2:  # 20% or more are headings
                enhanced['structure'] = 'well_structured'
            elif len(heading_blocks) >= len(blocks) * 0.1:  # 10% or more are headings
                enhanced['structure'] = 'moderately_structured'
            else:
                enhanced['structure'] = 'needs_organization'
            
            # Add processing recommendations
            enhanced['processing_recommendations'] = {
                'recommended_split_strategy': self._recommend_split_strategy(enhanced),
                'suggested_enhancements': self._suggest_enhancements(enhanced),
                'estimated_processing_time': self._estimate_processing_time(word_count)
            }
            
            print(f"✅ V2 ANALYZER: Enhanced analysis complete")
            return enhanced
            
        except Exception as e:
            print(f"❌ V2 ANALYZER: Error enhancing analysis - {e}")
            return llm_analysis or self._get_fallback_analysis()
    
    def _rule_based_analysis(self, normalized_doc) -> dict:
        """Fallback rule-based analysis when LLM is unavailable"""
        try:
            blocks = getattr(normalized_doc, 'blocks', [])
            word_count = getattr(normalized_doc, 'word_count', 0)
            title = getattr(normalized_doc, 'title', '').lower()
            
            # Rule-based content type detection
            content_type = 'mixed'
            if 'api' in title or any('api' in getattr(b, 'content', '').lower() for b in blocks[:3]):
                content_type = 'api_documentation'
            elif 'tutorial' in title or 'guide' in title:
                content_type = 'tutorial'
            elif 'how to' in title:
                content_type = 'how_to_guide'
            elif 'reference' in title:
                content_type = 'reference'
            
            # Rule-based technical depth
            technical_depth = 'intermediate'
            if word_count > 8000:
                technical_depth = 'deep'
            elif word_count < 1000:
                technical_depth = 'surface'
            
            return {
                'content_type': content_type,
                'technical_depth': technical_depth,
                'audience_level': 'intermediate',
                'granularity': 'detailed' if word_count > 2000 else 'high_level',
                'structure': 'moderately_structured',
                'completeness': 'mostly_complete',
                'complexity': 'moderate',
                'key_topics': ['general_content'],
                'recommended_article_count': max(1, min(5, word_count // 2000)),
                'confidence_score': 0.6,
                'analysis_method': 'rule_based_fallback'
            }
            
        except Exception as e:
            print(f"❌ V2 ANALYZER: Error in rule-based analysis - {e}")
            return self._get_fallback_analysis()
    
    def _get_fallback_analysis(self) -> dict:
        """Emergency fallback analysis"""
        return {
            'content_type': 'mixed',
            'technical_depth': 'intermediate',
            'audience_level': 'intermediate',
            'granularity': 'detailed',
            'structure': 'moderately_structured',
            'completeness': 'partial',
            'complexity': 'moderate',
            'key_topics': ['unknown_content'],
            'recommended_article_count': 2,
            'confidence_score': 0.3,
            'analysis_method': 'emergency_fallback'
        }
    
    def _parse_llm_response(self, response: str) -> dict:
        """Fallback parsing for non-JSON LLM responses"""
        # Basic parsing logic for when LLM doesn't return valid JSON
        analysis = self._get_fallback_analysis()
        
        # Try to extract key information from text response
        response_lower = response.lower()
        
        # Content type detection
        for content_type in self.content_types:
            if content_type.replace('_', ' ') in response_lower:
                analysis['content_type'] = content_type
                break
        
        return analysis
    
    def _recommend_split_strategy(self, analysis: dict) -> str:
        """Recommend content splitting strategy based on analysis"""
        content_type = analysis.get('content_type', 'mixed')
        complexity = analysis.get('complexity', 'moderate')
        
        if content_type == 'api_documentation' and complexity in ['complex', 'highly_complex']:
            return 'split_by_endpoints'
        elif content_type in ['tutorial', 'how_to_guide']:
            return 'split_by_steps'
        elif complexity == 'highly_complex':
            return 'split_by_topics'
        else:
            return 'minimal_split'
    
    def _suggest_enhancements(self, analysis: dict) -> List[str]:
        """Suggest content enhancements based on analysis"""
        suggestions = []
        
        if analysis.get('structure') == 'needs_organization':
            suggestions.append('Add clear section headings')
        
        if analysis.get('completeness') in ['partial', 'incomplete']:
            suggestions.append('Fill content gaps')
        
        if analysis.get('technical_depth') == 'surface':
            suggestions.append('Add more technical details')
        
        return suggestions
    
    def _estimate_processing_time(self, word_count: int) -> str:
        """Estimate processing time based on word count"""
        if word_count > 10000:
            return '15-20 minutes'
        elif word_count > 5000:
            return '8-12 minutes'
        elif word_count > 2000:
            return '4-6 minutes'
        else:
            return '2-3 minutes'