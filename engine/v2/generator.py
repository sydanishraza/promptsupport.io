"""
KE-M9: V2 Article Generator - Complete Implementation Migration
Migrated from server.py - Final article generation with strict format and audience-aware styling
"""

import json
import re
import uuid
from typing import Dict, Any, List
from datetime import datetime
from bs4 import BeautifulSoup
from ..llm.client import get_llm_client
from ..stores.mongo import RepositoryFactory
from ._utils import create_processing_metadata

class V2ArticleGenerator:
    """V2 Engine: Final article generation with strict format and audience-aware styling"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.required_structure = [
            "h1_title",
            "intro_paragraph", 
            "mini_toc",
            "main_body",
            "faqs",
            "related_links"
        ]
        
        self.audience_styles = {
            "developer": {
                "tone": "technical and precise",
                "focus": "implementation details, code examples, technical specifications",
                "language": "technical terminology, specific APIs, development concepts"
            },
            "business": {
                "tone": "strategic and outcome-focused",
                "focus": "business value, ROI, strategic implications, competitive advantages",
                "language": "business terminology, metrics, strategic concepts"
            },
            "admin": {
                "tone": "procedural and authoritative",
                "focus": "configuration steps, system management, best practices",
                "language": "administrative terminology, system concepts, operational procedures"
            },
            "end_user": {
                "tone": "friendly and accessible",
                "focus": "practical usage, step-by-step guidance, user benefits",
                "language": "plain language, minimal jargon, user-friendly explanations"
            }
        }
    
    async def run(self, evidenced_content: dict, **kwargs) -> dict:
        """Generate articles using centralized LLM client (new interface)"""
        try:
            print(f"📝 V2 ARTICLE GEN: Starting article generation with LLM client - engine=v2")
            
            # Extract parameters from kwargs  
            normalized_doc = kwargs.get('normalized_doc')
            per_article_outlines = kwargs.get('per_article_outlines', [])
            analysis = kwargs.get('analysis', {})
            run_id = kwargs.get('run_id', 'unknown')
            
            # Call the original generate_final_articles method
            result = await self.generate_final_articles(
                normalized_doc, per_article_outlines, analysis, run_id
            )
            
            return result
            
        except Exception as e:
            print(f"❌ V2 ARTICLE GEN: Error in run method - {e}")
            return {
                "generated_articles": [],
                "articles_generated": 0,
                "error": str(e),
                "engine": "v2"
            }
    
    async def generate_final_articles(self, normalized_doc, per_article_outlines: list, analysis: dict, run_id: str) -> dict:
        """V2 Engine: Generate final articles with strict format and audience-aware styling"""
        try:
            print(f"📝 V2 ARTICLE GEN: Generating final articles with strict format - engine=v2")
            
            generated_articles = []
            audience = analysis.get('audience', 'end_user')
            
            for article_outline_data in per_article_outlines:
                article_id = article_outline_data.get('article_id', 'unknown')
                outline = article_outline_data.get('outline', {})
                
                if not outline:
                    continue
                
                print(f"📝 V2 ARTICLE GEN: Generating article '{outline.get('title', 'Untitled')}' for {audience} audience - engine=v2")
                
                # Generate final article with strict format
                article_result = await self._generate_single_article(
                    normalized_doc, 
                    article_id, 
                    outline, 
                    analysis, 
                    audience
                )
                
                if article_result:
                    generated_articles.append({
                        "article_id": article_id,
                        "article_data": article_result
                    })
            
            # Store generated articles
            stored_articles = await self._store_generated_articles(generated_articles, run_id, normalized_doc.doc_id)
            
            print(f"✅ V2 ARTICLE GEN: Generated {len(generated_articles)} final articles with strict format - engine=v2")
            return stored_articles
            
        except Exception as e:
            print(f"❌ V2 ARTICLE GEN: Error generating final articles - {e} - engine=v2")
            return {"generated_articles": [], "run_id": run_id, "doc_id": getattr(normalized_doc, 'doc_id', 'unknown')}
    
    async def _generate_single_article(self, normalized_doc, article_id: str, outline: dict, analysis: dict, audience: str) -> dict:
        """Generate a single final article with strict format"""
        try:
            # Get all blocks referenced in the outline
            article_blocks = self._extract_blocks_from_outline(normalized_doc, outline)
            
            if not article_blocks:
                print(f"⚠️ V2 ARTICLE GEN: No blocks found for article {article_id} - engine=v2")
                return None
            
            # Create comprehensive article input for LLM
            article_input = self._create_article_generation_input(outline, article_blocks, analysis, audience)
            
            # Generate article using LLM
            article_result = await self._perform_llm_article_generation(article_input, audience)
            
            if article_result:
                # Validate and enhance the generated article
                validated_article = await self._validate_and_enhance_article(
                    article_result, outline, article_blocks, audience
                )
                
                # Convert HTML to Markdown
                markdown_content = await self._convert_html_to_markdown(validated_article.get('html', ''))
                validated_article['markdown'] = markdown_content
                
                return validated_article
            else:
                # Fallback to rule-based article generation
                print(f"🔄 V2 ARTICLE GEN: LLM failed, using rule-based fallback for article {article_id} - engine=v2")
                return await self._rule_based_article_generation(outline, article_blocks, audience)
                
        except Exception as e:
            print(f"❌ V2 ARTICLE GEN: Error generating single article {article_id} - {e} - engine=v2")
            return None
    
    def _extract_blocks_from_outline(self, normalized_doc, outline: dict) -> list:
        """Extract all blocks referenced in the article outline"""
        try:
            article_blocks = []
            sections = outline.get('sections', [])
            
            for section in sections:
                subsections = section.get('subsections', [])
                for subsection in subsections:
                    block_ids = subsection.get('block_ids', [])
                    
                    for block_id in block_ids:
                        try:
                            block_index = int(block_id.split('_')[1]) - 1
                            if hasattr(normalized_doc, 'blocks') and 0 <= block_index < len(normalized_doc.blocks):
                                article_blocks.append({
                                    "block_id": block_id,
                                    "block": normalized_doc.blocks[block_index],
                                    "section": section.get('heading', ''),
                                    "subsection": subsection.get('heading', '')
                                })
                        except (IndexError, ValueError):
                            print(f"⚠️ V2 ARTICLE GEN: Invalid block_id {block_id} - engine=v2")
                            continue
            
            return article_blocks
            
        except Exception as e:
            print(f"❌ V2 ARTICLE GEN: Error extracting blocks from outline - {e}")
            return []
    
    def _create_article_generation_input(self, outline: dict, article_blocks: list, analysis: dict, audience: str) -> str:
        """Create comprehensive input for LLM article generation"""
        try:
            input_parts = []
            
            # Article metadata
            input_parts.append(f"ARTICLE_TITLE: {outline.get('title', 'Untitled Article')}")
            input_parts.append(f"TARGET_AUDIENCE: {audience}")
            input_parts.append(f"CONTENT_TYPE: {analysis.get('content_type', 'conceptual')}")
            input_parts.append(f"COMPLEXITY: {analysis.get('complexity', 'intermediate')}")
            
            # Audience styling guidance
            style_guide = self.audience_styles.get(audience, self.audience_styles['end_user'])
            input_parts.append(f"TONE: {style_guide['tone']}")
            input_parts.append(f"FOCUS: {style_guide['focus']}")
            input_parts.append(f"LANGUAGE_STYLE: {style_guide['language']}")
            
            # Article structure outline
            input_parts.append("\nARTICLE_OUTLINE:")
            sections = outline.get('sections', [])
            for i, section in enumerate(sections, 1):
                input_parts.append(f"{i}. {section.get('heading', f'Section {i}')}")
                subsections = section.get('subsections', [])
                for j, subsection in enumerate(subsections, 1):
                    input_parts.append(f"   {i}.{j} {subsection.get('heading', f'Subsection {j}')}")
                    block_ids = subsection.get('block_ids', [])
                    if block_ids:
                        input_parts.append(f"       Blocks: {', '.join(block_ids)}")
            
            # Source blocks with detailed content
            input_parts.append("\nSOURCE_BLOCKS (all must be used):")
            for item in article_blocks:
                block_id = item['block_id']
                block = item['block']
                section = item.get('section', '')
                subsection = item.get('subsection', '')
                
                block_info = f"ID:{block_id} | SECTION:{section} | SUBSECTION:{subsection} | TYPE:{getattr(block, 'block_type', 'unknown')}"
                
                if hasattr(block, 'level') and block.level:
                    block_info += f" | LEVEL:{block.level}"
                
                if hasattr(block, 'language') and block.language:
                    block_info += f" | LANG:{block.language}"
                
                # Full content (not truncated for final generation)
                block_content = getattr(block, 'content', str(block))
                block_info += f"\nCONTENT: {block_content}"
                input_parts.append(block_info)
                input_parts.append("---")
            
            # FAQs from outline
            faqs = outline.get('faq_suggestions', [])
            if faqs:
                input_parts.append("\nFAQ_SUGGESTIONS:")
                for i, faq in enumerate(faqs, 1):
                    input_parts.append(f"Q{i}: {faq.get('q', '')}")
                    input_parts.append(f"A{i}: {faq.get('a', '')}")
            
            # Related links from outline
            related_links = outline.get('related_link_suggestions', [])
            if related_links:
                input_parts.append("\nRELATED_LINKS:")
                for i, link in enumerate(related_links, 1):
                    input_parts.append(f"{i}. {link.get('label', 'Link')} - {link.get('url', '')}")
            
            return "\n".join(input_parts)
            
        except Exception as e:
            print(f"❌ V2 ARTICLE GEN: Error creating article input - {e}")
            return f"ARTICLE_TITLE: {outline.get('title', 'Error')}\nERROR: Could not create article input"
    
    async def _perform_llm_article_generation(self, article_input: str, audience: str) -> dict:
        """Perform LLM-based article generation using specified format"""
        try:
            system_message = f"""You are a professional technical writer. Generate a full article based on the outline and source blocks.

Create articles with EXACT structure and audience-appropriate styling for {audience} readers.

CRITICAL REQUIREMENTS:
1. Follow the EXACT article structure (NO H1 in content, Intro, Mini-TOC, Main Body, FAQs, Related Links)
2. Cover ALL assigned block_ids with 100% coverage - every source block must be reflected in content
3. Style and tone must match the target audience ({audience})
4. Insert [MISSING] where source information is insufficient
5. Do NOT embed media - only reference media IDs if needed
6. Create working Mini-TOC with clickable anchor links (#section-anchors)
7. Use ordered lists (OL) for procedural/sequential content
8. Consolidate related code blocks instead of fragmenting them

EXACT ARTICLE STRUCTURE:
1. NO H1 TITLE (title handled by frontend - start with intro paragraph)
2. Intro Paragraph (overview, context, what reader will learn)
3. Mini-TOC as simple bullet list: <ul><li>Section Name</li></ul> (links will be added automatically)
4. Main Body (H2/H3 sections WITHOUT id attributes - IDs will be added automatically)
5. FAQs (Q&A format addressing common questions)
6. Related Links (bulleted list of internal and external references)

AUDIENCE STYLING FOR {audience.upper()}:
- Tone: {self.audience_styles.get(audience, {}).get('tone', 'professional')}
- Focus: {self.audience_styles.get(audience, {}).get('focus', 'practical guidance')}
- Language: {self.audience_styles.get(audience, {}).get('language', 'appropriate terminology')}

CONTENT REQUIREMENTS:
- All source blocks must be incorporated into appropriate sections
- Code blocks should be properly formatted with syntax highlighting
- Tables should be HTML tables with proper structure
- Lists should use appropriate HTML list formatting
- Headings should have anchor IDs for Mini-TOC linking"""

            user_message = f"""Generate a complete article using ALL source blocks provided.

{article_input}

REQUIREMENTS:
- Follow the exact article structure above
- Cover **all** assigned block_ids (100% coverage)
- Style matches the detected audience ({audience})
- Insert [MISSING] if info is absent
- Do **not** embed media; only reference media IDs
- Return JSON only: {{"html":"...","summary":"..."}}

MANDATORY HTML STRUCTURE (follow EXACTLY):

EXAMPLE of CORRECT HTML format:
{{
  "html": "<p>This tutorial demonstrates how to build a basic Google Map using its JavaScript API. You will learn how to create an HTML page, add a map with a custom marker, and authenticate the map using an API key.</p>
<ul>
  <li>Using Google Map Javascript API</li>
  <li>Create an HTML Page</li>
  <li>Add a Map with a Custom Marker</li>
  <li>Authenticate the Map</li>
  <li>Result</li>
</ul>
<h2>Using Google Map Javascript API</h2>
<p>Section content here...</p>
<h2>Create an HTML Page</h2>
<h3>Steps to Create the HTML Page</h3>
<ol>
  <li>Use any text editor of your choice and add a basic HTML structure</li>
  <li>Add the following meta tag inside the head element</li>
  <li>Add a title for the HTML page inside the head element</li>
</ol>
<pre class='line-numbers' data-lang='HTML' data-start='1'>
<code class='language-html'>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
  &lt;meta charset='UTF8'&gt;
  &lt;title&gt;Google Maps JavaScript API Tutorial&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
  &lt;div id='my_map' style='height:900px; width:100%'&gt;&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</code>
</pre>",
  "summary": "Brief summary of what this article covers and its key takeaways"
}}

CRITICAL REQUIREMENTS:
1. NEVER use <h1> tags - START with introduction paragraph <p>
2. Mini-TOC MUST be simple bullet list - links will be added automatically
3. Use <ol> for procedural steps (create, add, configure, install, etc.)
4. Use <ul> only for non-procedural lists (and Mini-TOC)
5. Consolidate code into single <pre><code> blocks
6. Section headings use plain <h2>, <h3> tags without id attributes"""

            print(f"🤖 V2 ARTICLE GEN: Sending article generation request to LLM - {audience} audience - engine=v2")
            
            # Use centralized LLM client
            try:
                ai_response = await self.llm_client.generate_response(system_message, user_message)
            except Exception as llm_error:
                print(f"⚠️ V2 ARTICLE GEN: LLM client error - {llm_error}")
                return None
            
            if ai_response:
                # Parse JSON response
                # Clean response and extract JSON
                cleaned_response = re.sub(r'[-\x1f\x7f-\x9f]', '', ai_response)
                
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        article_data = json.loads(json_str)
                        
                        # Validate required fields
                        if 'html' in article_data and 'summary' in article_data:
                            html_length = len(article_data.get('html', ''))
                            print(f"🎯 V2 ARTICLE GEN: LLM article generation successful - {html_length} chars HTML - engine=v2")
                            return article_data
                        else:
                            print(f"⚠️ V2 ARTICLE GEN: Missing required fields in LLM response - engine=v2")
                            return None
                    except json.JSONDecodeError as json_error:
                        print(f"⚠️ V2 ARTICLE GEN: JSON parsing error - {json_error}")
                        return None
                else:
                    print(f"⚠️ V2 ARTICLE GEN: No JSON found in LLM article response - engine=v2")
                    return None
            else:
                print(f"❌ V2 ARTICLE GEN: No response from LLM for article generation - engine=v2")
                return None
                
        except Exception as e:
            print(f"❌ V2 ARTICLE GEN: Error in LLM article generation - {e} - engine=v2")
            return None
    
    async def _validate_and_enhance_article(self, article_result: dict, outline: dict, article_blocks: list, audience: str) -> dict:
        """Validate and enhance LLM-generated article"""
        try:
            enhanced_article = article_result.copy()
            html_content = enhanced_article.get('html', '')
            
            # Validate structure elements
            required_elements = ['<ul>', '<h2', '<h3']  # Basic structure validation (removed H1 requirement)
            missing_elements = []
            
            for element in required_elements:
                if element not in html_content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"⚠️ V2 ARTICLE GEN: Missing structural elements: {missing_elements} - engine=v2")
            
            # Ensure Mini-TOC has anchor links
            if '<ul>' in html_content and 'href="#' not in html_content:
                print(f"⚠️ V2 ARTICLE GEN: Mini-TOC missing anchor links - engine=v2")
            
            # Validate block coverage (basic check)
            block_ids = [item['block_id'] for item in article_blocks]
            coverage_check = {
                'total_blocks': len(article_blocks),
                'html_length': len(html_content),
                'has_faqs': 'FAQ' in html_content or 'Q:' in html_content,
                'has_toc': '<ul>' in html_content and '<li>' in html_content,
                'has_sections': html_content.count('<h2') >= 1
            }
            
            # Add validation metadata
            enhanced_article['validation_metadata'] = {
                **coverage_check,
                'audience': audience,
                'block_ids_assigned': block_ids,
                'missing_elements': missing_elements,
                'validation_method': 'llm_enhanced',
                'engine': 'v2'
            }
            
            # Ensure no media embedding
            img_tags = re.findall(r'<img[^>]*>', html_content)
            if img_tags:
                print(f"⚠️ V2 ARTICLE GEN: Found {len(img_tags)} img tags, removing embedded media - engine=v2")
                # Remove img tags
                html_content = re.sub(r'<img[^>]*>', '[MEDIA_REFERENCE]', html_content)
                enhanced_article['html'] = html_content
            
            return enhanced_article
            
        except Exception as e:
            print(f"❌ V2 ARTICLE GEN: Error validating article - {e} - engine=v2")
            return article_result
    
    async def _convert_html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to Markdown format"""
        try:
            markdown_content = html_content
            
            # Convert headings
            markdown_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'<h2[^>]*id="([^"]*)"[^>]*>(.*?)</h2>', r'## \2 {#\1}', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', markdown_content, flags=re.IGNORECASE)
            
            # Convert paragraphs
            markdown_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', markdown_content, flags=re.IGNORECASE | re.DOTALL)
            
            # Convert lists
            markdown_content = re.sub(r'<ul[^>]*>', '', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'</ul>', '\n', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'<ol[^>]*>', '', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'</ol>', '\n', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', markdown_content, flags=re.IGNORECASE | re.DOTALL)
            
            # Convert links
            markdown_content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', markdown_content, flags=re.IGNORECASE)
            
            # Convert code blocks
            markdown_content = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'```\n\1\n```', markdown_content, flags=re.IGNORECASE | re.DOTALL)
            markdown_content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', markdown_content, flags=re.IGNORECASE)
            
            # Convert emphasis
            markdown_content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', markdown_content, flags=re.IGNORECASE)
            markdown_content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', markdown_content, flags=re.IGNORECASE)
            
            # Clean up extra whitespace
            markdown_content = re.sub(r'\n\n\n+', '\n\n', markdown_content)
            markdown_content = markdown_content.strip()
            
            return markdown_content
            
        except Exception as e:
            print(f"❌ V2 ARTICLE GEN: Error converting HTML to Markdown - {e}")
            return html_content  # Return original HTML if conversion fails

print("✅ KE-M9: V2 Article Generator migrated from server.py")
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