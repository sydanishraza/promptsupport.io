"""
KE-PR6: V2 Gap Filling System with Centralized LLM Client
Extracted from server.py - Intelligent content gap detection and filling using LLM
"""

from ..llm.client import get_llm_client
from ..llm.prompts import GAP_FILLING_PROMPT

class V2GapFillingSystem:
    """V2 Engine: Intelligent gap filling with in-corpus retrieval and pattern synthesis using centralized LLM client"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.gap_patterns = [
            "[MISSING]", "[TODO]", "[TBD]", "[PLACEHOLDER]", "...", "[CONTENT_NEEDED]"
        ]
        self.gap_types = [
            "missing_explanation", "missing_example", "missing_code", 
            "missing_section", "incomplete_sentence", "missing_link"
        ]
    
    async def run(self, evidenced_content: dict, **kwargs) -> dict:
        """Fill content gaps using centralized LLM client and contextual analysis"""
        try:
            print(f"🔧 V2 GAP FILLING: Starting intelligent gap filling with LLM client - engine=v2")
            
            articles = evidenced_content.get('articles', [])
            filled_articles = []
            
            for article in articles:
                filled_article = await self._fill_article_gaps(article)
                filled_articles.append(filled_article)
            
            result = {
                "articles": filled_articles,
                "gap_filling_metadata": {
                    "llm_provider": self.llm_client.provider,
                    "articles_processed": len(filled_articles),
                    "engine": "v2"
                }
            }
            
            print(f"✅ V2 GAP FILLING: Processed {len(filled_articles)} articles - engine=v2")
            return result
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error in gap filling - {e}")
            return {"articles": evidenced_content.get('articles', []), "error": str(e)}
    
    async def _fill_article_gaps(self, article: dict) -> dict:
        """Fill gaps in a single article using centralized LLM client"""
        try:
            content = article.get('content', '')
            title = article.get('title', 'Article')
            
            # Detect gaps in content
            gaps_detected = self._detect_gaps(content)
            
            if not gaps_detected:
                # No gaps found, return original
                return article
            
            print(f"🔍 V2 GAP FILLING: Found {len(gaps_detected)} gaps in '{title}'")
            
            # Fill gaps using LLM
            filled_content = await self._fill_gaps_with_llm(content, title, gaps_detected)
            
            # Create filled article
            filled_article = article.copy()
            filled_article['content'] = filled_content
            filled_article['metadata'] = article.get('metadata', {})
            filled_article['metadata']['gap_filling'] = {
                'gaps_detected': len(gaps_detected),
                'gaps_filled': True,
                'llm_provider': self.llm_client.provider
            }
            
            return filled_article
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error filling article gaps - {e}")
            return article  # Return original on error
    
    def _detect_gaps(self, content: str) -> list:
        """Detect various types of content gaps"""
        gaps = []
        
        # Look for explicit gap markers
        for pattern in self.gap_patterns:
            if pattern in content:
                # Find position and context
                start = 0
                while True:
                    pos = content.find(pattern, start)
                    if pos == -1:
                        break
                    
                    # Get surrounding context (50 chars before/after)
                    context_start = max(0, pos - 50)
                    context_end = min(len(content), pos + len(pattern) + 50)
                    context = content[context_start:context_end]
                    
                    gaps.append({
                        'type': 'explicit_marker',
                        'pattern': pattern,
                        'position': pos,
                        'context': context
                    })
                    
                    start = pos + len(pattern)
        
        # Detect structural gaps (incomplete sections)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Look for incomplete sections (heading followed by empty or minimal content)
            if line.strip().startswith('#') and i < len(lines) - 1:
                next_content = ''
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith('#'):
                    next_content += lines[j] + '\n'
                    j += 1
                
                if len(next_content.strip()) < 50:  # Very short section
                    gaps.append({
                        'type': 'incomplete_section',
                        'heading': line.strip(),
                        'position': i,
                        'content_length': len(next_content.strip())
                    })
        
        return gaps
    
    async def _fill_gaps_with_llm(self, content: str, title: str, gaps: list) -> str:
        """Fill detected gaps using centralized LLM client"""
        try:
            # Prepare gap filling prompt
            gaps_summary = self._summarize_gaps(gaps)
            
            system_message = """You are a technical writer specializing in comprehensive documentation. Fill in missing content while maintaining consistency with the existing material.

GUIDELINES:
1. Identify content gaps marked with [MISSING], [TODO], or incomplete sections
2. Generate contextually appropriate content that fits naturally
3. Match the existing writing style and technical level
4. Ensure factual accuracy and avoid speculation
5. Maintain consistency with surrounding content
6. Use appropriate technical terminology
7. Keep additions concise but informative

Fill the identified gaps with appropriate, well-written content that enhances the document's completeness."""

            user_message = f"""Document Title: {title}

Gap Analysis:
{gaps_summary}

Content with gaps to fill:
{content}

Please fill the identified gaps with appropriate content while maintaining the document's style and technical accuracy."""

            # Use centralized LLM client
            filled_content = await self.llm_client.complete(
                system_message=system_message,
                user_message=user_message,
                temperature=0.4,
                max_tokens=4000
            )
            
            if filled_content:
                print(f"✅ V2 GAP FILLING: Successfully filled gaps using {self.llm_client.provider}")
                return filled_content
            else:
                print("⚠️ V2 GAP FILLING: No response from LLM, returning original content")
                return content
                
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error filling gaps with LLM - {e}")
            return content
    
    def _summarize_gaps(self, gaps: list) -> str:
        """Create a summary of detected gaps for LLM context"""
        if not gaps:
            return "No explicit gaps detected."
        
        summary_parts = [f"Found {len(gaps)} gaps:"]
        
        for i, gap in enumerate(gaps[:10]):  # Limit to first 10 gaps
            gap_type = gap.get('type', 'unknown')
            
            if gap_type == 'explicit_marker':
                pattern = gap.get('pattern', '')
                context = gap.get('context', '')[:100]
                summary_parts.append(f"{i+1}. Explicit marker '{pattern}' in context: {context}")
            
            elif gap_type == 'incomplete_section':
                heading = gap.get('heading', '')
                content_length = gap.get('content_length', 0)
                summary_parts.append(f"{i+1}. Incomplete section '{heading}' ({content_length} chars)")
        
        if len(gaps) > 10:
            summary_parts.append(f"... and {len(gaps) - 10} more gaps")
        
        return "\n".join(summary_parts)