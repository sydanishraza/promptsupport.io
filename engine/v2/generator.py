"""
KE-PR6: V2 Article Generator with Centralized LLM Client
Extracted from server.py - LLM-driven article generation with style enforcement and evidence tagging
"""

from ..llm.client import get_llm_client
from ..llm.prompts import ARTICLE_SECTION_PROMPT, ARTICLE_OUTLINE_PROMPT

class V2ArticleGenerator:
    """V2 Engine: LLM-driven article generation with style enforcement and evidence tagging"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.generation_templates = [
            "technical_article", "how_to_guide", "reference_doc", "tutorial", "overview"
        ]
        self.style_guidelines = [
            "woolf_aligned", "scannable_headings", "actionable_language", 
            "technical_accuracy", "evidence_based"
        ]
    
    async def generate(self, prewritten_content: dict, **kwargs) -> dict:
        """Generate complete articles from prewritten content using centralized LLM client"""
        try:
            print(f"📝 V2 GENERATOR: Starting article generation with LLM client - engine=v2")
            
            # Use centralized LLM client for generation
            articles = []
            
            # Extract articles from prewritten content
            prewritten_articles = prewritten_content.get('articles', [])
            
            for article_data in prewritten_articles:
                generated_article = await self._generate_single_article(article_data)
                if generated_article:
                    articles.append(generated_article)
            
            result = {
                "articles": articles,
                "generation_metadata": {
                    "llm_provider": self.llm_client.provider,
                    "articles_generated": len(articles),
                    "engine": "v2"
                }
            }
            
            print(f"✅ V2 GENERATOR: Generated {len(articles)} articles - engine=v2")
            return result
            
        except Exception as e:
            print(f"❌ V2 GENERATOR: Error in article generation - {e}")
            return {"articles": [], "error": str(e)}
    
    async def _generate_single_article(self, article_data: dict) -> dict:
        """Generate a single article using centralized LLM client"""
        try:
            title = article_data.get('title', 'Generated Article')
            outline = article_data.get('outline', {})
            source_blocks = article_data.get('source_blocks', [])
            
            # Create article input for LLM
            article_input = self._prepare_article_input(title, outline, source_blocks)
            
            # Generate article content using centralized LLM client
            system_message = """You are a professional technical writer. Generate a full article based on the outline and source blocks.

REQUIREMENTS:
1. Follow the provided outline structure exactly
2. Use all relevant information from source blocks
3. Apply Woolf/PromptSupport style guidelines:
   - Clear, scannable headings (H2, H3 hierarchy)
   - Concise, actionable language
   - Technical accuracy with accessibility
   - Logical flow and smooth transitions
4. Include code examples, tables, and technical details from source
5. Add evidence tags where appropriate
6. Ensure completeness and technical depth
7. Use markdown formatting for structure

Generate a comprehensive, well-structured article."""

            user_message = f"Generate an article based on this input:\n\n{article_input}"
            
            # Use centralized LLM client
            generated_content = await self.llm_client.complete(
                system_message=system_message,
                user_message=user_message,
                temperature=0.3,
                max_tokens=6000
            )
            
            if generated_content:
                # Process and format the generated content
                processed_article = {
                    "id": f"article_{article_data.get('id', 'generated')}",
                    "title": title,
                    "content": generated_content,
                    "outline": outline,
                    "metadata": {
                        "generated_by": "v2_generator",
                        "llm_provider": self.llm_client.provider,
                        "source_blocks": len(source_blocks),
                        "generation_timestamp": "2024-01-01T00:00:00Z"  # Placeholder
                    }
                }
                
                print(f"✅ V2 GENERATOR: Generated article '{title}' ({len(generated_content)} chars)")
                return processed_article
            else:
                print(f"⚠️ V2 GENERATOR: No content generated for '{title}'")
                return None
                
        except Exception as e:
            print(f"❌ V2 GENERATOR: Error generating article - {e}")
            return None
    
    def _prepare_article_input(self, title: str, outline: dict, source_blocks: list) -> str:
        """Prepare structured input for article generation"""
        try:
            input_parts = [f"ARTICLE TITLE: {title}"]
            
            # Add outline structure
            if outline:
                input_parts.append("\nARTICLE OUTLINE:")
                sections = outline.get('sections', [])
                for section in sections:
                    section_title = section.get('title', 'Section')
                    input_parts.append(f"- {section_title}")
                    
                    subsections = section.get('subsections', [])
                    for subsection in subsections:
                        input_parts.append(f"  - {subsection.get('title', 'Subsection')}")
            
            # Add source content
            if source_blocks:
                input_parts.append("\nSOURCE CONTENT BLOCKS:")
                for i, block in enumerate(source_blocks[:10]):  # Limit to first 10 blocks
                    block_content = block.get('content', '')[:500]  # Limit block size
                    input_parts.append(f"Block {i+1}: {block_content}")
            
            return "\n".join(input_parts)
            
        except Exception as e:
            print(f"⚠️ V2 GENERATOR: Error preparing article input - {e}")
            return f"ARTICLE TITLE: {title}\nERROR: Could not prepare full input"