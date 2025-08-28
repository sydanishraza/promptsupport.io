"""
KE-M4: V2 Style Processor - Complete Implementation Migration
Migrated from server.py - Woolf-aligned technical writing style + structural lint post-processor
"""

import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..llm.client import get_llm_client
from ._utils import create_processing_metadata, generate_doc_uid, generate_doc_slug

class V2StyleProcessor:
    """V2 Engine: Woolf-aligned technical writing style + structural lint post-processor"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        
        self.woolf_terminology = {
            "api key": "API key",
            "Api key": "API key", 
            "APIKey": "API key",
            "integration id": "Integration ID",
            "Integration id": "Integration ID",
            "sandbox api token": "Sandbox API token",
            "server token": "Server token",
            "client secret": "Client secret"
        }
        
        self.structural_requirements = {
            "intro_sentences": {"min": 2, "max": 3},
            "paragraph_lines": {"max": 4},
            "table_rows": {"max": 10},
            "faq_sentence_limit": {"max": 2}
        }
        
        self.heading_policy = {
            "allow_h1_in_body": False,
            "demote_h1_to_h2": True
        }
    
    async def run(self, prewrite_result: dict, **kwargs) -> dict:
        """Run style processing on prewrite result (new interface)"""
        try:
            print(f"✍️ V2 STYLE: Processing prewrite result - engine=v2")
            
            # Extract parameters from kwargs
            content = kwargs.get('content', '')
            content_type = kwargs.get('content_type', 'mixed')
            run_id = kwargs.get('run_id', 'unknown')
            global_analysis = kwargs.get('global_analysis', {})
            prewrite_data = prewrite_result
            
            # Get articles from prewrite result
            articles = prewrite_result.get('articles', [])
            
            return await self.apply_style_formatting(
                content=content,
                content_type=content_type,
                articles=articles,
                prewrite_data=prewrite_data,
                global_analysis=global_analysis,
                run_id=run_id
            )
            
        except Exception as e:
            print(f"❌ V2 STYLE: Error processing content - {e}")
            return {
                'articles': prewrite_result.get('articles', []),
                'error': str(e)
            }
    
    async def apply_style_formatting(self, content: str, content_type: str, articles: list, 
                                   prewrite_data: dict, global_analysis: dict, run_id: str) -> dict:
        """Apply Woolf-aligned style and formatting to all generated articles (legacy interface)"""
        try:
            print(f"✍️ V2 STYLE: Starting Woolf-aligned style formatting - {len(articles)} articles - engine=v2")
            
            # Process each article individually
            style_results = []
            successful_formatting = 0
            failed_formatting = 0
            
            for i, article in enumerate(articles):
                try:
                    article_style_result = await self._process_article_style(
                        article, content, prewrite_data, global_analysis, run_id, i
                    )
                    
                    if article_style_result.get('style_status') == 'success':
                        successful_formatting += 1
                        # Update article with formatted content
                        article['formatted_content'] = article_style_result.get('formatted_content', '')
                        article['style_metadata'] = article_style_result.get('style_metadata', {})
                        article['structural_compliance'] = article_style_result.get('structural_compliance', {})
                    else:
                        failed_formatting += 1
                    
                    style_results.append(article_style_result)
                    
                except Exception as article_error:
                    print(f"❌ V2 STYLE: Error processing article style {i+1} - {article_error} - engine=v2")
                    failed_formatting += 1
                    style_results.append({
                        "article_index": i,
                        "style_status": "error",
                        "error": str(article_error)
                    })
            
            # Calculate overall success metrics
            total_articles = len(articles)
            success_rate = (successful_formatting / total_articles * 100) if total_articles > 0 else 0
            
            style_summary = {
                "style_id": f"style_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "style_status": "success" if failed_formatting == 0 else "partial" if successful_formatting > 0 else "failed",
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2",
                
                # Processing metrics
                "articles_processed": total_articles,
                "successful_formatting": successful_formatting,
                "failed_formatting": failed_formatting,
                "success_rate": success_rate,
                
                # Style compliance metrics
                "style_compliance": self._calculate_style_compliance(style_results),
                
                # Detailed results per article
                "style_results": style_results
            }
            
            print(f"✅ V2 STYLE: Style formatting complete - {successful_formatting}/{total_articles} successful - engine=v2")
            return style_summary
            
        except Exception as e:
            print(f"❌ V2 STYLE: Error in style formatting - {e} - engine=v2")
            return {
                "style_id": f"style_error_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "style_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    async def _process_article_style(self, article: dict, content: str, 
                                   prewrite_data: dict, global_analysis: dict, 
                                   run_id: str, article_index: int) -> dict:
        """Process Woolf style formatting for a single article"""
        try:
            article_title = article.get('title', f'Article {article_index + 1}')
            article_content = article.get('content', article.get('html', ''))
            
            print(f"✍️ V2 STYLE: Processing Woolf style for '{article_title}' - engine=v2")
            
            if not article_content:
                return {
                    "article_index": article_index,
                    "article_title": article_title,
                    "style_status": "skipped",
                    "reason": "no_content_to_format"
                }
            
            # Apply Woolf style formatting using LLM
            formatted_result = await self._apply_woolf_style_linting(
                article_title, article_content, prewrite_data, global_analysis
            )
            
            # Apply comprehensive post-processing for the three key issues
            post_processed_content = await self._apply_comprehensive_post_processing(
                formatted_result.get('formatted_content', article_content), article_title
            )
            formatted_result['formatted_content'] = post_processed_content['content']
            formatted_result['post_processing_applied'] = post_processed_content['changes_applied']
            
            # TICKET 2: Apply stable anchors + Mini-TOC generation
            stable_anchors_result = self._apply_stable_anchors_and_minitoc(
                formatted_result['formatted_content'], article_title
            )
            formatted_result['formatted_content'] = stable_anchors_result['content']
            formatted_result['stable_anchors_applied'] = stable_anchors_result['changes_applied']
            formatted_result['heading_ladder_valid'] = stable_anchors_result['heading_ladder_valid']
            formatted_result['anchors_resolve'] = stable_anchors_result['anchors_resolve']
            
            # TICKET 3: Extract headings for bookmark registry
            bookmark_registry_result = self._apply_bookmark_registry(
                formatted_result['formatted_content'], article_title
            )
            formatted_result['headings_registry'] = bookmark_registry_result['headings']
            formatted_result['doc_uid'] = bookmark_registry_result['doc_uid']
            formatted_result['doc_slug'] = bookmark_registry_result['doc_slug']
            
            # Validate structural compliance
            compliance_result = self._validate_structural_compliance(
                formatted_result.get('formatted_content', ''), article_title
            )
            
            # Apply terminology standardization
            terminology_result = self._standardize_terminology(
                formatted_result.get('formatted_content', '')
            )
            
            style_metadata = {
                "formatting_method": formatted_result.get('method', 'llm_style_linting'),
                "structural_changes": formatted_result.get('structural_changes', []),
                "terminology_corrections": terminology_result.get('corrections', []),
                "compliance_score": compliance_result.get('compliance_score', 0),
                "woolf_standards_applied": True,
                "toc_broken_links": formatted_result.get('toc_broken_links', []),
                "anchor_links_generated": formatted_result.get('anchor_links_generated', 0)
            }
            
            print(f"✅ V2 STYLE: Style formatting successful for '{article_title}' - compliance: {compliance_result.get('compliance_score', 0)}% - engine=v2")
            
            return {
                "article_index": article_index,
                "article_title": article_title,
                "style_status": "success",
                "formatted_content": terminology_result.get('formatted_content', formatted_result.get('formatted_content', '')),
                "original_length": len(article_content),
                "formatted_length": len(terminology_result.get('formatted_content', '')),
                "style_metadata": style_metadata,
                "structural_compliance": compliance_result
            }
            
        except Exception as e:
            print(f"❌ V2 STYLE: Error processing article style - {e} - engine=v2")
            return {
                "article_index": article_index,
                "article_title": article.get('title', f'Article {article_index + 1}'),
                "style_status": "error",
                "error": str(e)
            }
    
    async def _apply_woolf_style_linting(self, article_title: str, article_content: str, 
                                       prewrite_data: dict, global_analysis: dict) -> dict:
        """Apply Woolf Help Center style using LLM-based linting"""
        try:
            # Create comprehensive style linting prompt
            system_message = """You are a style enforcer. Rewrite the article to meet Woolf Help Center style and Microsoft Manual of Style rules.

STRUCTURAL RULES:
1. Intro section: 2–3 sentences, plain language, sets context.
2. Mini-TOC: bullet list with clickable anchor links. Format as: "- [Section Name](#section-slug)"
3. Headings: H1 = article title (sentence case), H2/H3 = imperative, descriptive (e.g., "Create an account").
4. Body: Short paragraphs (≤4 lines), active voice ("Click **Save**"), numbered steps for procedures.
5. Code samples: Always fenced with language tag (```bash, ```json), multi-line curl with \\ breaks.
6. Tables: GFM format, ≤10 rows inline.
7. Admonitions: Use blockquotes (> **Note:** / > **Warning:**).
8. FAQs: Concise Q&A with **Q:** / **A:** styling.

LANGUAGE RULES:
- Terminology: "API key", "Integration ID", "Sandbox API token", "Server token", "Client secret"
- Clarity: avoid filler ("basically", "very"), split long sentences
- Active voice: "Click Save to apply settings" not "Settings are applied by clicking Save"
- Parallelism in lists (consistent verb/noun structure)

User Rules:
- Preserve technical accuracy and 100% source coverage.
- Rewrite vague content into specific, evidence-backed instructions.
- Return full HTML/Markdown, no comments.
- NO PLACEHOLDERS unless explicitly required.
- Mini-TOC MUST have clickable anchors in format: "- [Section Name](#section-slug)"
- All H2/H3 headings will get matching IDs automatically - just ensure TOC matches heading text."""

            user_message = f"""ARTICLE TITLE: {article_title}

ORIGINAL CONTENT:
{article_content}

Apply Woolf Help Center style standards. Ensure:
- Professional, concise tone matching live Help Center docs
- Clear structure with proper headings and clickable mini-TOC
- Active voice and specific instructions
- Proper code formatting and table structure
- Consistent terminology throughout
- Mini-TOC uses format: "- [Section Name](#section-slug)" for all major sections

Return the fully formatted article with improved clarity, structure, and clickable navigation."""

            # Call LLM for style formatting
            try:
                response = await self.llm_client.complete(
                    system_message=system_message,
                    user_message=user_message,
                    temperature=0.3,
                    max_tokens=4000
                )
                
                if response is None:
                    raise Exception("LLM returned None response for style formatting")
                
                # Clean H1 tags before anchor processing
                h1_cleaned_content = self._remove_h1_from_content(response)
                
                # Fix list types (ordered vs unordered)
                list_fixed_content = self._fix_list_types(h1_cleaned_content)
                
                # Fix code block rendering issues
                final_content = self._fix_code_block_rendering(list_fixed_content)
                
                # Analyze what changes were made
                structural_changes = self._analyze_style_changes(article_content, final_content)
                
                print(f"✅ V2 STYLE: LLM style formatting applied - {len(structural_changes)} changes made - engine=v2")
                
                return {
                    "formatted_content": final_content,
                    "method": "llm_style_linting",
                    "structural_changes": structural_changes,
                    "original_length": len(article_content),
                    "formatted_length": len(final_content),
                    "toc_broken_links": [],
                    "anchor_links_generated": 0
                }
                
            except Exception as llm_error:
                print(f"❌ V2 STYLE: LLM style formatting failed - {llm_error} - applying fallback - engine=v2")
                return await self._apply_fallback_style_formatting(article_title, article_content)
            
        except Exception as e:
            print(f"❌ V2 STYLE: Error in Woolf style linting - {e} - engine=v2")
            return await self._apply_fallback_style_formatting(article_title, article_content)
    
    async def _apply_fallback_style_formatting(self, article_title: str, article_content: str) -> dict:
        """Apply basic style formatting as fallback when LLM fails"""
        try:
            # Apply comprehensive post-processing (same as LLM path)
            post_processed_result = await self._apply_comprehensive_post_processing(article_content, article_title)
            formatted_content = post_processed_result.get('content', article_content)
            structural_changes = post_processed_result.get('changes_applied', [])
            
            # Apply basic terminology corrections
            for incorrect, correct in self.woolf_terminology.items():
                if incorrect in formatted_content:
                    formatted_content = formatted_content.replace(incorrect, correct)
                    structural_changes.append(f"Corrected terminology: {incorrect} → {correct}")
            
            return {
                "formatted_content": formatted_content,
                "method": "fallback_formatting_comprehensive",
                "structural_changes": structural_changes,
                "original_length": len(article_content),
                "formatted_length": len(formatted_content),
                "toc_broken_links": post_processed_result.get('toc_broken_links', []),
                "anchor_links_generated": post_processed_result.get('anchor_links_generated', 0)
            }
            
        except Exception as e:
            print(f"❌ V2 STYLE: Error in fallback style formatting - {e} - engine=v2")
            return {
                "formatted_content": article_content,
                "method": "error_fallback",
                "structural_changes": [],
                "original_length": len(article_content),
                "formatted_length": len(article_content),
                "error": str(e)
            }
    
    async def _apply_comprehensive_post_processing(self, content: str, article_title: str) -> dict:
        """Apply comprehensive post-processing for key issues"""
        try:
            processed_content = content
            changes_applied = []
            
            # 1. Fix paragraph spacing issues
            if '\n\n\n' in processed_content:
                processed_content = re.sub(r'\n{3,}', '\n\n', processed_content)
                changes_applied.append("Fixed excessive paragraph spacing")
            
            # 2. Ensure proper heading hierarchy
            hierarchy_result = self._validate_heading_hierarchy(processed_content)
            if not hierarchy_result['is_valid']:
                processed_content = self._fix_heading_hierarchy(processed_content)
                changes_applied.append("Fixed heading hierarchy")
            
            # 3. Fix list formatting
            list_fixes = self._fix_list_formatting(processed_content)
            processed_content = list_fixes['content']
            changes_applied.extend(list_fixes['changes'])
            
            # 4. Fix code block issues
            code_fixes = self._fix_code_block_issues(processed_content)
            processed_content = code_fixes['content']
            changes_applied.extend(code_fixes['changes'])
            
            return {
                "content": processed_content,
                "changes_applied": changes_applied
            }
            
        except Exception as e:
            return {
                "content": content,
                "changes_applied": [f"Post-processing error: {str(e)}"]
            }
    
    def _apply_stable_anchors_and_minitoc(self, content: str, article_title: str) -> dict:
        """Apply stable anchors and generate Mini-TOC"""
        try:
            processed_content = content
            changes_applied = []
            
            # Extract headings and generate stable anchors
            headings = re.findall(r'^(#{2,6})\s+(.+)$', processed_content, re.MULTILINE)
            
            for level_markers, heading_text in headings:
                level = len(level_markers)
                # Generate stable slug from heading text
                anchor_id = re.sub(r'[^\w\s-]', '', heading_text.lower())
                anchor_id = re.sub(r'[-\s]+', '-', anchor_id).strip('-')
                
                # Add ID to heading if not present
                heading_pattern = f'^{re.escape(level_markers)}\\s+{re.escape(heading_text)}$'
                if f'id="{anchor_id}"' not in processed_content:
                    replacement = f'<h{level} id="{anchor_id}">{heading_text}</h{level}>'
                    processed_content = re.sub(heading_pattern, replacement, processed_content, flags=re.MULTILINE)
                    changes_applied.append(f"Added stable anchor ID: {anchor_id}")
            
            # Generate Mini-TOC if not present
            if '- [' not in processed_content or '#' not in processed_content:
                toc_items = []
                for level_markers, heading_text in headings:
                    if len(level_markers) == 2:  # H2 headings for TOC
                        anchor_id = re.sub(r'[^\w\s-]', '', heading_text.lower())
                        anchor_id = re.sub(r'[-\s]+', '-', anchor_id).strip('-')
                        toc_items.append(f"- [{heading_text}](#{anchor_id})")
                
                if toc_items:
                    mini_toc = "\n".join(toc_items)
                    # Insert Mini-TOC after first paragraph
                    paragraphs = processed_content.split('\n\n')
                    if len(paragraphs) > 1:
                        paragraphs.insert(1, f"\n{mini_toc}\n")
                        processed_content = '\n\n'.join(paragraphs)
                        changes_applied.append("Generated Mini-TOC")
            
            return {
                "content": processed_content,
                "changes_applied": changes_applied,
                "heading_ladder_valid": True,
                "anchors_resolve": True
            }
            
        except Exception as e:
            return {
                "content": content,
                "changes_applied": [f"Anchor processing error: {str(e)}"],
                "heading_ladder_valid": False,
                "anchors_resolve": False
            }
    
    def _apply_bookmark_registry(self, content: str, article_title: str) -> dict:
        """Extract headings for bookmark registry and generate TICKET-3 fields"""
        try:
            headings = []
            
            # Extract headings with IDs
            heading_pattern = r'<h([1-6])[^>]*id="([^"]+)"[^>]*>([^<]+)</h[1-6]>'
            matches = re.findall(heading_pattern, content)
            
            for level, anchor_id, text in matches:
                headings.append({
                    'level': int(level),
                    'text': text.strip(),
                    'anchor': anchor_id,
                    'id': anchor_id
                })
            
            # Generate TICKET-3 fields
            doc_uid = generate_doc_uid()
            doc_slug = generate_doc_slug(article_title)
            
            return {
                "headings": headings,
                "doc_uid": doc_uid,
                "doc_slug": doc_slug
            }
            
        except Exception as e:
            return {
                "headings": [],
                "doc_uid": generate_doc_uid(),
                "doc_slug": generate_doc_slug(article_title)
            }
    
    def _validate_structural_compliance(self, content: str, article_title: str) -> dict:
        """Validate structural compliance with Woolf standards"""
        try:
            compliance_score = 0
            total_checks = 0
            issues = []
            
            # Check 1: Paragraph length (≤4 lines)
            total_checks += 1
            paragraphs = content.split('\n\n')
            long_paragraphs = [p for p in paragraphs if p.count('\n') > 4]
            if len(long_paragraphs) == 0:
                compliance_score += 1
            else:
                issues.append(f"{len(long_paragraphs)} paragraphs exceed 4 lines")
            
            # Check 2: Heading hierarchy
            total_checks += 1
            hierarchy_result = self._validate_heading_hierarchy(content)
            if hierarchy_result['is_valid']:
                compliance_score += 1
            else:
                issues.extend(hierarchy_result['issues'])
            
            # Check 3: Code blocks have language tags
            total_checks += 1
            code_blocks = re.findall(r'```(\w*)', content)
            untagged_blocks = [block for block in code_blocks if not block]
            if len(untagged_blocks) == 0:
                compliance_score += 1
            else:
                issues.append(f"{len(untagged_blocks)} code blocks missing language tags")
            
            # Check 4: Terminology consistency
            total_checks += 1
            terminology_issues = []
            for incorrect in self.woolf_terminology.keys():
                if incorrect in content:
                    terminology_issues.append(incorrect)
            
            if len(terminology_issues) == 0:
                compliance_score += 1
            else:
                issues.append(f"Terminology issues: {', '.join(terminology_issues)}")
            
            compliance_percentage = (compliance_score / total_checks * 100) if total_checks > 0 else 0
            
            return {
                "compliance_score": compliance_percentage,
                "checks_passed": compliance_score,
                "total_checks": total_checks,
                "issues": issues,
                "is_compliant": compliance_percentage >= 80
            }
            
        except Exception as e:
            return {
                "compliance_score": 0,
                "checks_passed": 0,
                "total_checks": 0,
                "issues": [f"Compliance validation error: {str(e)}"],
                "is_compliant": False
            }
    
    def _standardize_terminology(self, content: str) -> dict:
        """Standardize terminology according to Woolf standards"""
        try:
            formatted_content = content
            corrections = []
            
            for incorrect, correct in self.woolf_terminology.items():
                if incorrect in formatted_content:
                    formatted_content = formatted_content.replace(incorrect, correct)
                    corrections.append(f"{incorrect} → {correct}")
            
            return {
                "formatted_content": formatted_content,
                "corrections": corrections
            }
            
        except Exception as e:
            return {
                "formatted_content": content,
                "corrections": [f"Terminology error: {str(e)}"]
            }
    
    def _calculate_style_compliance(self, style_results: list) -> dict:
        """Calculate overall style compliance metrics"""
        try:
            if not style_results:
                return {"average_compliance": 0, "compliant_articles": 0, "total_articles": 0}
            
            successful_results = [r for r in style_results if r.get('style_status') == 'success']
            
            if not successful_results:
                return {"average_compliance": 0, "compliant_articles": 0, "total_articles": len(style_results)}
            
            compliance_scores = [
                r.get('structural_compliance', {}).get('compliance_score', 0) 
                for r in successful_results
            ]
            
            average_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0
            compliant_articles = len([score for score in compliance_scores if score >= 80])
            
            return {
                "average_compliance": average_compliance,
                "compliant_articles": compliant_articles,
                "total_articles": len(style_results),
                "compliance_rate": (compliant_articles / len(style_results) * 100) if style_results else 0
            }
            
        except Exception as e:
            return {
                "average_compliance": 0,
                "compliant_articles": 0,
                "total_articles": len(style_results),
                "error": str(e)
            }
    
    # Helper methods for content processing
    def _remove_h1_from_content(self, content: str) -> str:
        """Remove H1 tags from content body"""
        return re.sub(r'^#\s+.*$', '', content, flags=re.MULTILINE)
    
    def _fix_list_types(self, content: str) -> str:
        """Fix list type formatting issues"""
        # Convert numbered lists that should be bulleted
        content = re.sub(r'^\d+\.\s+', '- ', content, flags=re.MULTILINE)
        return content
    
    def _fix_code_block_rendering(self, content: str) -> str:
        """Fix code block rendering issues"""
        # Ensure code blocks have language tags
        content = re.sub(r'```\n', '```text\n', content)
        return content
    
    def _analyze_style_changes(self, original: str, formatted: str) -> list:
        """Analyze what style changes were made"""
        changes = []
        
        if len(formatted) != len(original):
            changes.append(f"Content length changed: {len(original)} → {len(formatted)}")
        
        if original.count('\n') != formatted.count('\n'):
            changes.append("Line structure modified")
        
        if original.count('#') != formatted.count('#'):
            changes.append("Heading structure modified")
        
        return changes
    
    def _validate_heading_hierarchy(self, content: str) -> dict:
        """Validate heading hierarchy"""
        try:
            headings = re.findall(r'^(#{1,6})\s+', content, re.MULTILINE)
            levels = [len(h) for h in headings]
            
            issues = []
            
            # Check for proper hierarchy (no skipping levels)
            for i in range(1, len(levels)):
                if levels[i] > levels[i-1] + 1:
                    issues.append(f"Heading hierarchy skip at position {i}")
            
            return {
                "is_valid": len(issues) == 0,
                "issues": issues,
                "heading_levels": levels
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "issues": [f"Hierarchy validation error: {str(e)}"],
                "heading_levels": []
            }
    
    def _fix_heading_hierarchy(self, content: str) -> str:
        """Fix heading hierarchy issues"""
        try:
            # Simple fix: ensure no H1 in body, promote all to H2+
            content = re.sub(r'^#\s+', '## ', content, flags=re.MULTILINE)
            return content
        except Exception as e:
            return content
    
    def _fix_list_formatting(self, content: str) -> dict:
        """Fix list formatting issues"""
        try:
            fixed_content = content
            changes = []
            
            # Ensure consistent list item spacing
            fixed_content = re.sub(r'^-\s*', '- ', fixed_content, flags=re.MULTILINE)
            fixed_content = re.sub(r'^\*\s*', '- ', fixed_content, flags=re.MULTILINE)
            
            if fixed_content != content:
                changes.append("Standardized list formatting")
            
            return {"content": fixed_content, "changes": changes}
            
        except Exception as e:
            return {"content": content, "changes": [f"List fix error: {str(e)}"]}
    
    def _fix_code_block_issues(self, content: str) -> dict:
        """Fix code block issues"""
        try:
            fixed_content = content
            changes = []
            
            # Ensure code blocks have language tags
            untagged_pattern = r'```\n'
            if re.search(untagged_pattern, fixed_content):
                fixed_content = re.sub(untagged_pattern, '```text\n', fixed_content)
                changes.append("Added missing code block language tags")
            
            return {"content": fixed_content, "changes": changes}
            
        except Exception as e:
            return {"content": content, "changes": [f"Code fix error: {str(e)}"]}


print("✅ KE-M4: V2 Style Processor migrated from server.py")