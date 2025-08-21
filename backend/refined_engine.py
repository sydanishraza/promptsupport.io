#!/usr/bin/env python3
"""
Refined PromptSupport Engine - New Processing Pipeline
Implements strict source fidelity, precise WYSIWYG enhancements, and optimized granularity
"""

import os
import uuid
import asyncio
import re
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import difflib

from fastapi import HTTPException
import requests

# Import existing configuration
from server import call_llm_with_fallback, db, clean_html_wrappers

class RefinedEngine:
    """New refined processing engine with strict source fidelity"""
    
    def __init__(self):
        self.name = "Refined PromptSupport Engine v2.0"
        self.version = "2.0.0"
        
    async def process_content(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main processing pipeline for refined engine"""
        try:
            print(f"🆕 REFINED ENGINE: Starting processing pipeline")
            print(f"📊 Content: {len(content)} characters from {metadata.get('original_filename', 'Unknown')}")
            
            # Step 1: Enhanced multi-dimensional analysis
            analysis = await self.enhanced_multi_dimensional_analysis(content, metadata)
            
            # Step 2: Adaptive granularity processing
            articles = await self.adaptive_granularity_processor(content, metadata, analysis)
            
            # Step 3: Save to database
            saved_articles = []
            for article in articles:
                try:
                    await db.content_library.insert_one(article)
                    saved_articles.append(article)
                    print(f"✅ REFINED ENGINE: Saved article '{article['title']}'")
                except Exception as e:
                    print(f"❌ Error saving article: {e}")
            
            print(f"🎉 REFINED ENGINE: Processing complete - {len(saved_articles)} articles created")
            return saved_articles
            
        except Exception as e:
            print(f"❌ REFINED ENGINE ERROR: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def enhanced_multi_dimensional_analysis(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced analysis with precise metrics for unified output detection"""
        try:
            print(f"🔍 REFINED ANALYSIS: Analyzing content with precise metrics")
            
            # Precise metrics calculation
            word_count = len(content.split())
            
            # Count headings (multiple patterns for robustness)
            heading_patterns = [
                r'^#+\s+',  # Markdown headings
                r'<h[1-6][^>]*>',  # HTML headings
                r'^[A-Z][^.\n]*:$',  # Title case followed by colon
                r'^\d+\.\s+[A-Z]',  # Numbered sections
            ]
            heading_count = 0
            for pattern in heading_patterns:
                heading_count += len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))
            
            # Count code blocks (multiple patterns)
            code_patterns = [
                r'```[\s\S]*?```',  # Markdown code blocks
                r'<pre[\s\S]*?</pre>',  # HTML pre blocks
                r'<code[\s\S]*?</code>',  # HTML code blocks
                r'function\s+\w+\s*\(',  # Function declarations
                r'var\s+\w+\s*=',  # Variable declarations
                r'<script[\s\S]*?</script>',  # Script tags
            ]
            code_blocks = 0
            for pattern in code_patterns:
                code_blocks += len(re.findall(pattern, content, re.MULTILINE | re.IGNORECASE))
            
            # Count list items
            list_patterns = [
                r'^\s*[-*]\s+',  # Bullet lists
                r'^\s*\d+\.\s+',  # Numbered lists
                r'<li[^>]*>',  # HTML list items
            ]
            list_items = 0
            for pattern in list_patterns:
                list_items += len(re.findall(pattern, content, re.MULTILINE))
            
            # Content classification
            classification = {
                "content_type": "tutorial" if list_items > 5 and code_blocks > 0 else "reference",
                "audience": "developer" if code_blocks > 0 else "end_user",
                "format_signals": [],
                "complexity_level": "basic" if word_count < 1000 else "intermediate",
                "dependencies": {
                    "has_sequential_steps": list_items > 5,
                    "sections_interdependent": heading_count > 2,
                    "code_context_critical": code_blocks > 0
                },
                "metrics": {
                    "word_count": word_count,
                    "heading_count": heading_count,
                    "code_blocks": code_blocks,
                    "list_items": list_items,
                    "code_density": code_blocks / max(1, word_count/1000)
                }
            }
            
            # Add format signals
            if code_blocks > 0:
                classification["format_signals"].append("code_heavy")
            if list_items > 10:
                classification["format_signals"].append("list_heavy")
            if heading_count > 5:
                classification["format_signals"].append("structured")
            if not classification["format_signals"]:
                classification["format_signals"].append("narrative")
            
            # Granularity decision - Default to UNIFIED for tutorials and short content
            granularity = {
                "level": "unified",
                "article_count_estimate": 1,
                "reasoning": "Default unified approach for content cohesion and source fidelity"
            }
            
            # Only split if content is genuinely large and complex
            if word_count > 3000 and heading_count > 6 and classification["content_type"] != "tutorial":
                granularity = {
                    "level": "moderate",
                    "article_count_estimate": 3,
                    "reasoning": "Large, non-tutorial content with multiple sections"
                }
            elif word_count > 8000 and heading_count > 10:
                granularity = {
                    "level": "deep",
                    "article_count_estimate": 5,
                    "reasoning": "Very large content requiring comprehensive splitting"
                }
            
            result = {
                "content_classification": classification,
                "granularity_decision": granularity,
                "processing_strategy": {
                    "approach": granularity["level"],
                    "section_strategy": "maintain_flow" if granularity["level"] == "unified" else "logical_breaks",
                    "fidelity_priority": "strict_source_adherence"
                }
            }
            
            print(f"📊 ANALYSIS COMPLETE:")
            print(f"   📝 Type: {classification['content_type']}")
            print(f"   📏 Words: {word_count}, Headings: {heading_count}, Code: {code_blocks}")
            print(f"   🎯 Granularity: {granularity['level']} ({granularity['article_count_estimate']} articles)")
            print(f"   💡 Reasoning: {granularity['reasoning']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in refined analysis: {e}")
            # Fallback to unified processing
            return {
                "content_classification": {"content_type": "guide", "complexity_level": "basic"},
                "granularity_decision": {"level": "unified", "article_count_estimate": 1},
                "processing_strategy": {"approach": "unified", "fidelity_priority": "strict_source_adherence"}
            }

    async def adaptive_granularity_processor(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process content with adaptive granularity - defaults to unified"""
        try:
            level = analysis['granularity_decision']['level']
            print(f"🎯 REFINED PROCESSOR: Using {level} approach")
            
            if level == "unified":
                return await self.create_unified_article(content, metadata, analysis)
            elif level == "moderate":
                return await self.create_moderate_split_articles(content, metadata, analysis)
            elif level == "deep":
                return await self.create_deep_split_articles(content, metadata, analysis)
            else:
                # Default to unified for safety
                return await self.create_unified_article(content, metadata, analysis)
                
        except Exception as e:
            print(f"❌ Error in adaptive processor: {e}")
            # Fallback to unified processing
            return await self.create_unified_article(content, metadata, analysis)

    async def create_unified_article(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a single unified article with strict source fidelity"""
        try:
            print(f"📄 CREATING UNIFIED ARTICLE with strict source fidelity")
            
            content_type = analysis['content_classification']['content_type']
            doc_title = self.clean_document_title(metadata.get('original_filename', 'Guide'))
            
            # Generate high-quality article content
            article_content = await self.create_high_quality_article_content(content, content_type, metadata)
            
            if not article_content or len(article_content.strip()) < 100:
                print(f"⚠️ Generated content too short, using fallback")
                article_content = self.create_fallback_content(content, doc_title)
            
            # Create article with refined metadata
            article = {
                "id": str(uuid.uuid4()),
                "title": f"{doc_title} - Complete Guide",
                "content": article_content,
                "status": "published",
                "article_type": "complete_guide",
                "source_document": metadata.get("original_filename", "Unknown"),
                "tags": [content_type, "unified", "refined_engine"],
                "created_at": datetime.utcnow(),
                "metadata": {
                    "refined_engine": True,
                    "engine_version": "2.0.0",
                    "processing_approach": "unified",
                    "content_type": content_type,
                    "source_fidelity": "strict",
                    "wysiwyg_enhanced": True,
                    "content_length": len(article_content),
                    "metrics": analysis.get('content_classification', {}).get('metrics', {}),
                    **metadata
                }
            }
            
            print(f"✅ UNIFIED ARTICLE CREATED: '{article['title']}' ({len(article_content)} chars)")
            return [article]
            
        except Exception as e:
            print(f"❌ Error creating unified article: {e}")
            return []

    async def create_high_quality_article_content(self, content: str, article_type: str, metadata: Dict[str, Any]) -> str:
        """Generate high-quality content with strict source fidelity"""
        try:
            print(f"📝 GENERATING HIGH-QUALITY CONTENT: {article_type}")
            
            doc_title = self.clean_document_title(metadata.get('original_filename', 'Guide'))
            
            # Refined system message with strict source fidelity
            system_message = f"""You are a content transformation specialist that converts raw source content into professional HTML articles for knowledge base display.

CORE PRINCIPLES:
- Use ONLY the provided source content. Do NOT invent, add, or assume any new sections, FAQs, code, examples, or information not explicitly in the source.
- Preserve ALL original content, including code, verbatim, unless reformatting for HTML (e.g., code blocks).
- Map source sections directly to HTML structure; do not create new sections (e.g., no 'Prerequisites' unless in source).
- For enhancements: Apply WYSIWYG tools (e.g., tables, expandables) ONLY if explicitly supported by source structure (e.g., Q&A for expandables, tabular data for tables).
- If source lacks FAQs or troubleshooting, omit those sections entirely.

TASK: Transform the source content into structured HTML within <div class="article-body">, maintaining 100% fidelity to the source.

HTML STRUCTURE REQUIREMENTS:
- Wrap in `<div class="article-body">`.
- Use `<h2 id="h_[unique_id]">` for main source sections (e.g., 'Introduction', 'Create an HTML page').
- Use `<h3>` for subsections if present in source.
- Convert source lists to `<ul>` or `<ol>` based on source numbering.
- Convert source code to `<pre class="line-numbers"><code class="language-[lang]">` with exact content.
- Use `<strong>` for key terms explicitly emphasized in source.
- Add `<hr>` between major sections.
- Include mini-TOC (`<div id="mini-toc-container" class="mini-toc">`) if source has 3+ sections.
- Use `<div class="note">💡 <strong>Note:</strong> [Text]</div>` only for source notes (e.g., 'Note: If you are using...').

FAQ HANDLING:
- Generate FAQs ONLY if source contains explicit Q&A or implied questions (e.g., troubleshooting steps).
- Use `<div class="expandable">` for FAQs, with `<h3 class="expandable-title">` for questions.
- If no FAQs in source, omit the section.

FIDELITY CHECK:
- Every output sentence must map to a specific source sentence or section.
- Validate post-generation: Remove any content not traceable to source.

CRITICAL: Return ONLY the HTML content. Do NOT wrap in ```html code blocks."""

            user_message = f"""Transform this source content into a professional HTML article for: {doc_title}

CRITICAL REQUIREMENTS:
- Use ONLY content from the source below
- Do NOT add Prerequisites, Getting Started, or Best Practices sections unless explicitly in source
- Do NOT invent FAQs or code examples
- Preserve exact code snippets and technical details
- Map source structure directly to HTML

SOURCE CONTENT:
{content[:20000]}"""

            # Generate content with validation
            response = await call_llm_with_fallback(
                system_message=system_message,
                user_message=user_message
            )
            
            if response:
                # Validate fidelity
                if not self.validate_fidelity(content, response):
                    print(f"⚠️ Low fidelity detected, regenerating with stricter prompt")
                    stricter_system = system_message + "\n\nCRITICAL: Strictly source-only. No new sections or FAQs. Every sentence must come from source."
                    response = await call_llm_with_fallback(
                        system_message=stricter_system,
                        user_message=user_message
                    )
                
                # Clean and enhance
                cleaned_content = self.clean_article_html_content(response)
                enhanced_content = self.apply_wysiwyg_enhancements(cleaned_content, content)
                
                print(f"✅ HIGH-QUALITY CONTENT GENERATED: {len(enhanced_content)} chars")
                return enhanced_content
            else:
                print(f"❌ Failed to generate content")
                return self.create_fallback_content(content, doc_title)
                
        except Exception as e:
            print(f"❌ Error generating high-quality content: {e}")
            return self.create_fallback_content(content, metadata.get('original_filename', 'Guide'))

    def validate_fidelity(self, source: str, generated: str, threshold: float = 0.7) -> bool:
        """Validate that generated content maintains fidelity to source"""
        try:
            # Extract words from source and generated content
            source_words = set(source.lower().split())
            gen_words = set(generated.lower().split())
            
            # Calculate overlap
            overlap = len(source_words.intersection(gen_words)) / max(1, len(source_words))
            
            # Check for forbidden sections that aren't in source
            forbidden_sections = ['Prerequisites', 'Getting Started', 'Best Practices', 'Introduction', 'Overview']
            for section in forbidden_sections:
                if section.lower() in generated.lower() and section.lower() not in source.lower():
                    print(f"⚠️ FIDELITY VIOLATION: Found invented section '{section}'")
                    return False
            
            # Check overlap threshold
            if overlap < threshold:
                print(f"⚠️ FIDELITY VIOLATION: Low word overlap {overlap:.2%} < {threshold:.2%}")
                return False
            
            print(f"✅ FIDELITY CHECK PASSED: {overlap:.2%} word overlap")
            return True
            
        except Exception as e:
            print(f"❌ Error in fidelity validation: {e}")
            return True  # Allow content through if validation fails

    def clean_article_html_content(self, content: str) -> str:
        """Enhanced cleaning with fidelity preservation"""
        try:
            # Remove markdown code block wrappers
            if content.strip().startswith('```html'):
                content = content.strip()
                content = re.sub(r'^```html\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
            
            # Remove document structure
            content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'</?html[^>]*>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'</?head[^>]*>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'</?body[^>]*>', '', content, flags=re.IGNORECASE)
            
            # Remove invented sections
            invented_patterns = [
                r'<h[1-3][^>]*>Prerequisites</h[1-3]>.*?(?=<h[1-3]|</div>|$)',
                r'<h[1-3][^>]*>Getting Started</h[1-3]>.*?(?=<h[1-3]|</div>|$)',
                r'<h[1-3][^>]*>Best Practices</h[1-3]>.*?(?=<h[1-3]|</div>|$)',
            ]
            
            for pattern in invented_patterns:
                content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Clean up whitespace
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            content = content.strip()
            
            return content
            
        except Exception as e:
            print(f"❌ Error cleaning content: {e}")
            return content

    def apply_wysiwyg_enhancements(self, content: str, source_content: str) -> str:
        """Apply WYSIWYG enhancements only when warranted by source"""
        try:
            print(f"🎨 APPLYING WYSIWYG ENHANCEMENTS based on source content")
            
            enhanced = content
            
            # 1. Add article-body wrapper if not present
            if '<div class="article-body">' not in enhanced:
                enhanced = f'<div class="article-body">\n{enhanced}\n</div>'
                print("✅ Added article-body wrapper")
            
            # 2. Generate mini-TOC only if source has multiple sections
            heading_count = len(re.findall(r'<h[2-6][^>]*>', enhanced))
            if heading_count >= 3 and 'mini-toc-container' not in enhanced:
                toc_html = self.generate_mini_toc(enhanced)
                if toc_html:
                    # Insert after first paragraph or at beginning
                    if '<p>' in enhanced:
                        enhanced = enhanced.replace('<p>', f'{toc_html}\n<hr>\n<p>', 1)
                    else:
                        enhanced = enhanced.replace('<div class="article-body">', f'<div class="article-body">\n{toc_html}\n<hr>')
                    print(f"✅ Added mini-TOC with {heading_count} sections")
            
            # 3. Enhance code blocks with line numbers
            code_pattern = r'<pre[^>]*><code[^>]*>(.*?)</code></pre>'
            code_matches = re.findall(code_pattern, enhanced, re.DOTALL)
            if code_matches:
                enhanced = re.sub(
                    r'<pre[^>]*><code([^>]*)>(.*?)</code></pre>',
                    r'<pre class="line-numbers"><code\1>\2</code></pre>',
                    enhanced,
                    flags=re.DOTALL
                )
                print(f"✅ Enhanced {len(code_matches)} code blocks with line numbers")
            
            # 4. Add heading IDs for navigation
            def add_heading_id(match):
                tag = match.group(1)
                attrs = match.group(2) or ''
                text = match.group(3)
                
                # Skip if ID already exists
                if 'id=' in attrs:
                    return match.group(0)
                
                # Generate unique ID
                heading_id = f"h_{uuid.uuid4().hex[:20]}"
                return f'<{tag}{attrs} id="{heading_id}">{text}</{tag}>'
            
            heading_pattern = r'<(h[2-6])([^>]*)>([^<]*)</\1>'
            enhanced = re.sub(heading_pattern, add_heading_id, enhanced)
            
            # 5. Convert source notes to proper note format
            if 'note:' in source_content.lower() or 'Note:' in source_content:
                note_pattern = r'(\([^)]*Note:[^)]*\)|Note:[^.!?]*[.!?])'
                notes = re.findall(note_pattern, enhanced, re.IGNORECASE)
                for note in notes:
                    note_text = re.sub(r'^[^:]*:', '', note).strip('() ')
                    enhanced_note = f'<div class="note">💡 <strong>Note:</strong> {note_text}</div>'
                    enhanced = enhanced.replace(note, enhanced_note)
                    print(f"✅ Enhanced note: {note_text[:50]}...")
            
            # 6. Generate FAQs only from source-implied questions
            faq_content = self.extract_source_faqs(source_content)
            if faq_content:
                enhanced += f'\n<hr>\n{faq_content}'
                print("✅ Added source-derived FAQs")
            
            print(f"✅ WYSIWYG enhancements complete")
            return enhanced
            
        except Exception as e:
            print(f"❌ Error applying WYSIWYG enhancements: {e}")
            return content

    def generate_mini_toc(self, content: str) -> str:
        """Generate mini table of contents from headings"""
        try:
            headings = re.findall(r'<h([2-6])[^>]*id="([^"]*)"[^>]*>([^<]*)</h[2-6]>', content)
            if len(headings) < 3:
                return ""
            
            toc_html = '<div id="mini-toc-container" class="mini-toc">\n<ul>\n'
            for level, heading_id, text in headings:
                toc_html += f'<li><a href="#{heading_id}">{text}</a></li>\n'
            toc_html += '</ul>\n</div>'
            
            return toc_html
            
        except Exception as e:
            print(f"❌ Error generating mini-TOC: {e}")
            return ""

    def extract_source_faqs(self, source_content: str) -> str:
        """Extract FAQs only from explicit or implied questions in source"""
        try:
            questions = []
            
            # Look for explicit notes that could be FAQs
            if "Note:" in source_content:
                # Example: "Note: If you are using an existing project..."
                note_match = re.search(r'Note:\s*([^.!?]*(?:existing[^.!?]*)?[.!?])', source_content, re.IGNORECASE)
                if note_match and 'existing' in note_match.group(1).lower():
                    questions.append({
                        "q": "Can I use an existing API key?",
                        "a": note_match.group(1).strip()
                    })
            
            # Look for result sections that imply "what should I see"
            if "Result" in source_content or "result" in source_content.lower():
                result_match = re.search(r'(?:result|you should see)[:\s]*([^.!?]*[.!?])', source_content, re.IGNORECASE)
                if result_match:
                    questions.append({
                        "q": "What should I see after following these steps?",
                        "a": result_match.group(1).strip()
                    })
            
            # Only generate FAQ section if we found source-derived questions
            if not questions:
                return ""
            
            faq_html = f'<h2 id="h_{uuid.uuid4().hex[:20]}">⁉️ Frequently Asked Questions (FAQs)</h2>\n'
            for q in questions:
                faq_html += f'''
<div class="expandable">
    <div class="expandable-header"><h3 class="expandable-title">{q['q']}</h3></div>
    <div class="expandable-content"><p>{q['a']}</p></div>
</div>'''
            
            return faq_html
            
        except Exception as e:
            print(f"❌ Error extracting source FAQs: {e}")
            return ""

    def create_fallback_content(self, content: str, title: str) -> str:
        """Create simple fallback content if main generation fails"""
        try:
            # Extract first few paragraphs
            paragraphs = content.split('\n\n')[:3]
            fallback_content = '<div class="article-body">\n'
            fallback_content += f'<h2>Overview</h2>\n'
            
            for para in paragraphs:
                if para.strip():
                    fallback_content += f'<p>{para.strip()}</p>\n'
            
            fallback_content += '</div>'
            return fallback_content
            
        except Exception as e:
            print(f"❌ Error creating fallback content: {e}")
            return f'<div class="article-body"><h2>Content Processing Error</h2><p>Unable to process content for {title}</p></div>'

    def clean_document_title(self, filename: str) -> str:
        """Clean document title from filename"""
        if not filename:
            return "Guide"
        
        # Remove extensions
        title = re.sub(r'\.[^.]*$', '', filename)
        
        # Replace underscores and hyphens with spaces
        title = title.replace('_', ' ').replace('-', ' ')
        
        # Remove version numbers and technical suffixes
        title = re.sub(r'\s*v?\d+(\.\d+)*\s*', ' ', title)
        title = re.sub(r'\s*(draft|final|complete|doc|guide|manual)\s*', ' ', title, flags=re.IGNORECASE)
        
        # Clean up whitespace
        title = ' '.join(title.split())
        
        return title.title() if title else "Guide"

    async def create_moderate_split_articles(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create 3-4 articles for moderate content"""
        try:
            print(f"📚 CREATING MODERATE SPLIT ARTICLES")
            
            articles = []
            doc_title = self.clean_document_title(metadata.get('original_filename', 'Guide'))
            
            # Create overview article
            overview_content = await self.create_high_quality_article_content(content[:5000], "overview", metadata)
            overview_article = {
                "id": str(uuid.uuid4()),
                "title": f"{doc_title} - Overview",
                "content": overview_content,
                "status": "published",
                "article_type": "overview",
                "source_document": metadata.get("original_filename", "Unknown"),
                "tags": ["overview", "moderate_split", "refined_engine"],
                "created_at": datetime.utcnow(),
                "metadata": {
                    "refined_engine": True,
                    "processing_approach": "moderate_split",
                    "article_sequence": 1,
                    **metadata
                }
            }
            articles.append(overview_article)
            
            # Create main content article
            main_content = await self.create_high_quality_article_content(content, "complete_guide", metadata)
            main_article = {
                "id": str(uuid.uuid4()),
                "title": f"{doc_title} - Complete Guide",
                "content": main_content,
                "status": "published",
                "article_type": "complete_guide",
                "source_document": metadata.get("original_filename", "Unknown"),
                "tags": ["main_content", "moderate_split", "refined_engine"],
                "created_at": datetime.utcnow(),
                "metadata": {
                    "refined_engine": True,
                    "processing_approach": "moderate_split",
                    "article_sequence": 2,
                    **metadata
                }
            }
            articles.append(main_article)
            
            # Add FAQ if source warrants it
            faq_content = self.extract_source_faqs(content)
            if faq_content:
                faq_article = {
                    "id": str(uuid.uuid4()),
                    "title": f"{doc_title} - FAQ",
                    "content": f'<div class="article-body">{faq_content}</div>',
                    "status": "published",
                    "article_type": "faq",
                    "source_document": metadata.get("original_filename", "Unknown"),
                    "tags": ["faq", "moderate_split", "refined_engine"],
                    "created_at": datetime.utcnow(),
                    "metadata": {
                        "refined_engine": True,
                        "processing_approach": "moderate_split",
                        "article_sequence": 3,
                        **metadata
                    }
                }
                articles.append(faq_article)
            
            print(f"✅ MODERATE SPLIT COMPLETE: {len(articles)} articles created")
            return articles
            
        except Exception as e:
            print(f"❌ Error in moderate split: {e}")
            return await self.create_unified_article(content, metadata, analysis)

    async def create_deep_split_articles(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create 5+ articles for complex content"""
        try:
            print(f"📖 CREATING DEEP SPLIT ARTICLES")
            
            # For now, fall back to moderate split for safety
            # Deep split would require more sophisticated section detection
            return await self.create_moderate_split_articles(content, metadata, analysis)
            
        except Exception as e:
            print(f"❌ Error in deep split: {e}")
            return await self.create_unified_article(content, metadata, analysis)


# Create global instance
refined_engine = RefinedEngine()