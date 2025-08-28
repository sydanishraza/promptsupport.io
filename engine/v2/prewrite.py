"""
KE-M3: V2 Prewrite System - Complete Implementation Migration
Migrated from server.py - Section-grounded prewrite pass with facts extraction
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..llm.client import get_llm_client
from ._utils import create_processing_metadata

class V2PrewriteSystem:
    """V2 Engine: Section-Grounded Prewrite Pass - Facts extraction before article generation"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.prewrite_storage_path = "/app/backend/static/prewrite_data"
        os.makedirs(self.prewrite_storage_path, exist_ok=True)
    
    async def run(self, per_article_outlines: dict, **kwargs) -> dict:
        """Run prewrite system on per-article outlines (new interface)"""
        try:
            print(f"🔍 V2 PREWRITE: Processing per-article outlines - engine=v2")
            
            # Extract parameters from kwargs
            content = kwargs.get('content', '')
            content_type = kwargs.get('content_type', 'mixed')
            run_id = kwargs.get('run_id', 'unknown')
            global_analysis = kwargs.get('global_analysis', {})
            
            # Get articles from per-article outlines
            articles = per_article_outlines.get('articles', [])
            
            return await self.execute_prewrite_pass(
                content=content,
                content_type=content_type,
                articles=articles,
                per_article_outlines=per_article_outlines,
                global_analysis=global_analysis,
                run_id=run_id
            )
            
        except Exception as e:
            print(f"❌ V2 PREWRITE: Error processing content - {e}")
            return {
                'articles': per_article_outlines.get('articles', []),
                'error': str(e)
            }
    
    async def execute_prewrite_pass(self, content: str, content_type: str, articles: list, 
                                  per_article_outlines: dict, global_analysis: dict, run_id: str) -> dict:
        """Execute section-grounded prewrite pass for all articles (legacy interface)"""
        try:
            print(f"🔍 V2 PREWRITE: Starting section-grounded prewrite pass - {len(articles)} articles - engine=v2")
            
            # Process each article individually
            prewrite_results = []
            successful_prewrites = 0
            failed_prewrites = 0
            
            for i, article in enumerate(articles):
                try:
                    article_prewrite = await self._process_article_prewrite(
                        article, content, per_article_outlines, global_analysis, run_id, i
                    )
                    
                    if article_prewrite.get('prewrite_status') == 'success':
                        successful_prewrites += 1
                        # Add prewrite data to article for use in generation
                        article['prewrite_data'] = article_prewrite.get('prewrite_data', {})
                        article['prewrite_file'] = article_prewrite.get('prewrite_file', '')
                    else:
                        failed_prewrites += 1
                    
                    prewrite_results.append(article_prewrite)
                    
                except Exception as article_error:
                    print(f"❌ V2 PREWRITE: Error processing article {i+1} - {article_error} - engine=v2")
                    failed_prewrites += 1
                    prewrite_results.append({
                        "article_index": i,
                        "prewrite_status": "error",
                        "error": str(article_error)
                    })
            
            # Calculate overall success metrics
            total_articles = len(articles)
            success_rate = (successful_prewrites / total_articles * 100) if total_articles > 0 else 0
            
            prewrite_summary = {
                "prewrite_id": f"prewrite_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "prewrite_status": "success" if failed_prewrites == 0 else "partial" if successful_prewrites > 0 else "failed",
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2",
                
                # Processing metrics
                "articles_processed": total_articles,
                "successful_prewrites": successful_prewrites,
                "failed_prewrites": failed_prewrites,
                "success_rate": success_rate,
                
                # Detailed results per article
                "prewrite_results": prewrite_results,
                
                # Content analysis
                "content_analysis": {
                    "content_type": content_type,
                    "content_length": len(content),
                    "source_blocks_available": len(self._extract_content_blocks(content)),
                    "prewrite_files_created": successful_prewrites
                }
            }
            
            print(f"✅ V2 PREWRITE: Prewrite pass complete - {successful_prewrites}/{total_articles} successful - engine=v2")
            return prewrite_summary
            
        except Exception as e:
            print(f"❌ V2 PREWRITE: Error in prewrite pass - {e} - engine=v2")
            return {
                "prewrite_id": f"prewrite_error_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "prewrite_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    async def _process_article_prewrite(self, article: dict, content: str, 
                                      per_article_outlines: dict, global_analysis: dict, 
                                      run_id: str, article_index: int) -> dict:
        """Process prewrite for a single article"""
        try:
            article_title = article.get('title', f'Article {article_index + 1}')
            print(f"📝 V2 PREWRITE: Processing prewrite for '{article_title}' - engine=v2")
            
            # Get article outline - handle both dict and list structures
            if isinstance(per_article_outlines, dict):
                article_outline = per_article_outlines.get(f'article_{article_index}', {})
            else:
                # Handle case where per_article_outlines is a list or other structure
                article_outline = {}
                if isinstance(per_article_outlines, list) and article_index < len(per_article_outlines):
                    article_outline = per_article_outlines[article_index]
            
            sections = article_outline.get('sections', []) if isinstance(article_outline, dict) else []
            
            if not sections:
                print(f"⚠️ V2 PREWRITE: No outline sections found for article {article_index} - engine=v2")
                return {
                    "article_index": article_index,
                    "article_title": article_title,
                    "prewrite_status": "skipped",
                    "reason": "no_outline_sections"
                }
            
            # Extract content blocks for fact extraction
            content_blocks = self._extract_content_blocks(content)
            
            # Generate section-grounded prewrite using LLM
            prewrite_data = await self._generate_section_prewrite(
                article_title, sections, content_blocks, global_analysis
            )
            
            # Validate prewrite data
            validation_result = self._validate_prewrite_data(prewrite_data, sections)
            
            if not validation_result['is_valid']:
                print(f"❌ V2 PREWRITE: Prewrite validation failed for '{article_title}' - {validation_result['reason']} - engine=v2")
                return {
                    "article_index": article_index,
                    "article_title": article_title,
                    "prewrite_status": "validation_failed",
                    "validation_error": validation_result['reason']
                }
            
            # Save prewrite.json file
            prewrite_filename = f"prewrite_{run_id}_article_{article_index}.json"
            prewrite_filepath = os.path.join(self.prewrite_storage_path, prewrite_filename)
            
            prewrite_file_data = {
                "article_index": article_index,
                "article_title": article_title,
                "run_id": run_id,
                "created_at": datetime.utcnow().isoformat(),
                "prewrite_data": prewrite_data,
                "validation_result": validation_result
            }
            
            # Convert to bytes and save
            json_content = json.dumps(prewrite_file_data, indent=2, ensure_ascii=False)
            json_bytes = json_content.encode('utf-8')
            
            # Ensure prewrite directory exists
            os.makedirs(self.prewrite_storage_path, exist_ok=True)
            
            try:
                # Try to use assets store if available
                from ..stores.assets import save_bytes
                content_hash, relative_path = save_bytes(json_bytes, prewrite_filename, self.prewrite_storage_path)
            except ImportError:
                # Fallback to direct file write
                with open(prewrite_filepath, 'w', encoding='utf-8') as f:
                    f.write(json_content)
            
            print(f"✅ V2 PREWRITE: Saved prewrite file - {prewrite_filename} - {len(prewrite_data.get('sections', []))} sections - engine=v2")
            
            return {
                "article_index": article_index,
                "article_title": article_title,
                "prewrite_status": "success",
                "prewrite_file": prewrite_filepath,
                "prewrite_data": prewrite_data,
                "validation_result": validation_result,
                "sections_processed": len(prewrite_data.get('sections', [])),
                "total_facts_extracted": sum([len(section.get('facts', [])) for section in prewrite_data.get('sections', [])])
            }
            
        except Exception as e:
            print(f"❌ V2 PREWRITE: Error processing article prewrite - {e} - engine=v2")
            return {
                "article_index": article_index,
                "article_title": article.get('title', f'Article {article_index + 1}'),
                "prewrite_status": "error",
                "error": str(e)
            }
    
    def _extract_content_blocks(self, content: str) -> list:
        """Extract content blocks with block_ids for fact extraction"""
        try:
            # Split content into logical blocks (paragraphs, sections, etc.)
            blocks = []
            
            # Split by double newlines first (paragraphs)
            paragraphs = content.split('\n\n')
            
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    block_id = f"b{i+1:03d}"  # Format: b001, b002, etc.
                    
                    # Determine block type
                    block_type = "paragraph"
                    if paragraph.strip().startswith('#'):
                        block_type = "heading"
                    elif paragraph.strip().startswith('```') or 'curl' in paragraph.lower():
                        block_type = "code"
                    elif '|' in paragraph and paragraph.count('|') > 2:
                        block_type = "table"
                    elif paragraph.strip().startswith(('- ', '* ', '1. ', '2. ')):
                        block_type = "list"
                    
                    blocks.append({
                        "block_id": block_id,
                        "type": block_type,
                        "content": paragraph.strip(),
                        "length": len(paragraph.strip()),
                        "index": i
                    })
            
            print(f"🔍 V2 PREWRITE: Extracted {len(blocks)} content blocks for fact extraction - engine=v2")
            return blocks
            
        except Exception as e:
            print(f"❌ V2 PREWRITE: Error extracting content blocks - {e} - engine=v2")
            return []
    
    async def _generate_section_prewrite(self, article_title: str, sections: list, 
                                       content_blocks: list, global_analysis: dict) -> dict:
        """Generate section-grounded prewrite using LLM"""
        try:
            # Prepare content blocks for LLM
            blocks_text = "\n\n".join([
                f"[BLOCK {block['block_id']}] ({block['type']})\n{block['content']}"
                for block in content_blocks
            ])
            
            # Create sections summary for context
            sections_summary = "\n".join([
                f"- {section.get('title', section.get('heading', 'Untitled Section'))}: {section.get('content_focus', 'General content')}"
                for section in sections
            ])
            
            # Create prewrite prompt for LLM
            system_message = """You are a fact extractor. Pull *verbatim or tightly paraphrased* facts from the provided blocks for each section.

User rules:
- Output JSON only.
- For each section: list 5–12 facts, each with `evidence_block_ids`.
- Extract any concrete examples (curl, parameters, object fields).
- If a required fact is missing, emit a `gap` entry with what is missing (no [MISSING] text here).

OUTPUT JSON FORMAT:
{
  "sections": [
    {
      "heading": "...",
      "facts": [{"text":"...", "evidence_block_ids":["b034","b091"]}, ...],
      "must_include_examples": [{"type":"curl","content":"..."},{"type":"table","headers":[...],"rows":[...]}, ...],
      "gaps":[{"need":"...", "where":"..."}, ...],
      "terms":["Integration ID","Server Token", "..."]
    }
  ]
}"""

            user_message = f"""Extract facts for article: "{article_title}"

REQUIRED SECTIONS:
{sections_summary}

SOURCE BLOCKS:
{blocks_text}

Extract facts for each section from the source blocks. Focus on concrete, actionable information."""

            # Use centralized LLM client
            llm_response = await self.llm_client.complete(
                system_message=system_message,
                user_message=user_message,
                temperature=0.2,
                max_tokens=3000
            )
            
            if llm_response:
                try:
                    # Parse JSON response
                    import re
                    # Clean response and extract JSON
                    cleaned_response = re.sub(r'[-\x1f\x7f-\x9f]', '', llm_response)
                    
                    # Try to extract JSON from response
                    json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        prewrite_data = json.loads(json_str)
                        
                        if 'sections' in prewrite_data:
                            print(f"✅ V2 PREWRITE: LLM prewrite successful - {len(prewrite_data['sections'])} sections - engine=v2")
                            return prewrite_data
                        else:
                            print(f"⚠️ V2 PREWRITE: Invalid prewrite structure from LLM - engine=v2")
                            return self._get_fallback_prewrite(sections, content_blocks)
                    else:
                        print(f"⚠️ V2 PREWRITE: No JSON found in LLM response - engine=v2")
                        return self._get_fallback_prewrite(sections, content_blocks)
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️ V2 PREWRITE: JSON parsing error - {e} - engine=v2")
                    return self._get_fallback_prewrite(sections, content_blocks)
            else:
                print(f"❌ V2 PREWRITE: No response from LLM - engine=v2")
                return self._get_fallback_prewrite(sections, content_blocks)
                
        except Exception as e:
            print(f"❌ V2 PREWRITE: Error generating prewrite - {e} - engine=v2")
            return self._get_fallback_prewrite(sections, content_blocks)
    
    def _get_fallback_prewrite(self, sections: list, content_blocks: list) -> dict:
        """Generate fallback prewrite when LLM fails"""
        try:
            fallback_sections = []
            
            for section in sections:
                section_title = section.get('title', section.get('heading', 'Untitled Section'))
                
                # Simple fact extraction - take first few blocks as facts
                facts = []
                for i, block in enumerate(content_blocks[:5]):  # Limit to first 5 blocks
                    facts.append({
                        "text": f"Content from {block['type']}: {block['content'][:100]}...",
                        "evidence_block_ids": [block['block_id']]
                    })
                
                fallback_sections.append({
                    "heading": section_title,
                    "facts": facts,
                    "must_include_examples": [],
                    "gaps": [{"need": "LLM processing", "where": "fact extraction"}],
                    "terms": []
                })
            
            return {
                "sections": fallback_sections,
                "fallback_method": "rule_based",
                "reason": "LLM processing failed"
            }
            
        except Exception as e:
            return {
                "sections": [],
                "fallback_method": "emergency",
                "error": str(e)
            }
    
    def _validate_prewrite_data(self, prewrite_data: dict, sections: list) -> dict:
        """Validate prewrite data structure and content"""
        try:
            # Check basic structure
            if not isinstance(prewrite_data, dict):
                return {"is_valid": False, "reason": "Prewrite data is not a dictionary"}
            
            if "sections" not in prewrite_data:
                return {"is_valid": False, "reason": "No sections found in prewrite data"}
            
            prewrite_sections = prewrite_data.get("sections", [])
            if not isinstance(prewrite_sections, list):
                return {"is_valid": False, "reason": "Sections is not a list"}
            
            # Check section count matches expected
            if len(prewrite_sections) != len(sections):
                return {"is_valid": False, "reason": f"Section count mismatch: expected {len(sections)}, got {len(prewrite_sections)}"}
            
            # Validate each section
            for i, prewrite_section in enumerate(prewrite_sections):
                if not isinstance(prewrite_section, dict):
                    return {"is_valid": False, "reason": f"Section {i} is not a dictionary"}
                
                required_fields = ["heading", "facts"]
                for field in required_fields:
                    if field not in prewrite_section:
                        return {"is_valid": False, "reason": f"Section {i} missing required field: {field}"}
                
                # Validate facts structure
                facts = prewrite_section.get("facts", [])
                if not isinstance(facts, list):
                    return {"is_valid": False, "reason": f"Section {i} facts is not a list"}
                
                for j, fact in enumerate(facts):
                    if not isinstance(fact, dict):
                        return {"is_valid": False, "reason": f"Section {i}, fact {j} is not a dictionary"}
                    
                    if "text" not in fact or "evidence_block_ids" not in fact:
                        return {"is_valid": False, "reason": f"Section {i}, fact {j} missing required fields"}
            
            return {
                "is_valid": True,
                "sections_validated": len(prewrite_sections),
                "total_facts": sum(len(section.get("facts", [])) for section in prewrite_sections)
            }
            
        except Exception as e:
            return {"is_valid": False, "reason": f"Validation error: {str(e)}"}


print("✅ KE-M3: V2 Prewrite System migrated from server.py")