"""
KE-M6: V2 Gap Filling System - Complete Implementation Migration
Migrated from server.py - Intelligent gap filling system with in-corpus retrieval and LLM
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from ..llm.client import get_llm_client
from ..stores.mongo import RepositoryFactory
from ._utils import create_processing_metadata

class V2GapFillingSystem:
    """V2 Engine: Intelligent gap filling system to replace [MISSING] placeholders with in-corpus retrieval"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.gap_patterns = [
            r'\[MISSING\]',
            r'\[PLACEHOLDER\]',
            r'\[TBD\]',
            r'\[TODO\]',
            r'\[FILL\]'
        ]
    
    async def run(self, evidenced_content: dict, **kwargs) -> dict:
        """Fill content gaps using centralized LLM client and contextual analysis (new interface)"""
        try:
            print(f"🔧 V2 GAP FILLING: Starting intelligent gap filling with LLM client - engine=v2")
            
            # Extract parameters from kwargs
            articles = evidenced_content.get('articles', [])
            source_content = kwargs.get('content', '')
            source_blocks = kwargs.get('source_blocks', [])
            run_id = kwargs.get('run_id', 'unknown')
            enrich_mode = kwargs.get('enrich_mode', 'internal')
            
            # Call the original fill_content_gaps method
            result = await self.fill_content_gaps(
                articles, source_content, source_blocks, run_id, enrich_mode
            )
            
            return result
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error in run method - {e}")
            return {
                "gap_filling_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    async def fill_content_gaps(self, articles: list, source_content: str, 
                               source_blocks: list, run_id: str, 
                               enrich_mode: str = "internal") -> dict:
        """Fill gaps in articles using in-corpus retrieval and pattern synthesis"""
        try:
            print(f"🔍 V2 GAP FILLING: Starting gap filling process - mode: {enrich_mode} - engine=v2")
            
            gap_filling_results = []
            total_gaps_found = 0
            total_gaps_filled = 0
            
            for i, article in enumerate(articles):
                try:
                    article_title = article.get('title', f'Article {i+1}')
                    article_content = article.get('content', '') or article.get('html', '')
                    
                    if not article_content:
                        continue
                    
                    # Step 1: Detect gaps in the article
                    gaps_detected = self._detect_gaps(article_content, article_title)
                    
                    if not gaps_detected:
                        # No gaps found
                        gap_filling_results.append({
                            "article_index": i,
                            "article_title": article_title,
                            "gap_filling_status": "no_gaps",
                            "gaps_found": 0,
                            "gaps_filled": 0,
                            "patches_applied": []
                        })
                        continue
                    
                    total_gaps_found += len(gaps_detected)
                    
                    # Step 2: Retrieve relevant content for gap filling
                    retrieval_results = await self._retrieve_gap_context(
                        gaps_detected, source_content, source_blocks, enrich_mode
                    )
                    
                    # Step 3: Generate patches using LLM
                    patches = await self._generate_gap_patches(
                        gaps_detected, retrieval_results, enrich_mode
                    )
                    
                    # Step 4: Apply patches to article content
                    patched_content, applied_patches = self._apply_patches(
                        article_content, patches
                    )
                    
                    # Update article with patched content
                    article['content'] = patched_content
                    article['html'] = patched_content
                    
                    # Track gap filling metadata
                    gaps_filled_count = len(applied_patches)
                    total_gaps_filled += gaps_filled_count
                    
                    gap_filling_result = {
                        "article_index": i,
                        "article_title": article_title,
                        "gap_filling_status": "success" if gaps_filled_count > 0 else "no_patches",
                        "gaps_found": len(gaps_detected),
                        "gaps_filled": gaps_filled_count,
                        "patches_applied": applied_patches,
                        "retrieval_sources": len(retrieval_results),
                        "enrich_mode": enrich_mode
                    }
                    
                    gap_filling_results.append(gap_filling_result)
                    
                    print(f"✅ V2 GAP FILLING: Processed '{article_title[:50]}...' - {gaps_filled_count}/{len(gaps_detected)} gaps filled - engine=v2")
                    
                except Exception as article_error:
                    print(f"❌ V2 GAP FILLING: Error processing article {i+1} - {article_error} - engine=v2")
                    gap_filling_results.append({
                        "article_index": i,
                        "article_title": article.get('title', f'Article {i+1}'),
                        "gap_filling_status": "error",
                        "error": str(article_error),
                        "gaps_found": 0,
                        "gaps_filled": 0
                    })
            
            # Calculate success metrics
            successful_articles = len([r for r in gap_filling_results if r.get('gap_filling_status') == 'success'])
            gap_fill_rate = (total_gaps_filled / total_gaps_found * 100) if total_gaps_found > 0 else 100
            
            return {
                "gap_filling_id": f"gaps_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "gap_filling_status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2",
                
                # Gap filling metrics
                "articles_processed": len(articles),
                "articles_with_gaps": len([r for r in gap_filling_results if r.get('gaps_found', 0) > 0]),
                "successful_gap_filling": successful_articles,
                "total_gaps_found": total_gaps_found,
                "total_gaps_filled": total_gaps_filled,
                "gap_fill_rate": gap_fill_rate,
                "enrich_mode": enrich_mode,
                
                # Detailed results
                "gap_filling_results": gap_filling_results
            }
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error in gap filling process - {e} - engine=v2")
            return {
                "gap_filling_id": f"gaps_error_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "gap_filling_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    def _detect_gaps(self, content: str, article_title: str) -> list:
        """Detect gap placeholders in article content"""
        try:
            gaps_found = []
            
            for pattern in self.gap_patterns:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                for match in matches:
                    # Get surrounding context for better gap understanding
                    start_pos = max(0, match.start() - 100)
                    end_pos = min(len(content), match.end() + 100)
                    context = content[start_pos:end_pos]
                    
                    # Try to infer what type of content is missing
                    gap_type = self._infer_gap_type(context, match.group())
                    
                    gaps_found.append({
                        "pattern": match.group(),
                        "position": match.start(),
                        "context": context,
                        "gap_type": gap_type,
                        "section": self._extract_section_name(content, match.start())
                    })
            
            return gaps_found
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error detecting gaps - {e}")
            return []
    
    def _infer_gap_type(self, context: str, gap_placeholder: str) -> str:
        """Infer the type of content that should fill the gap based on context"""
        context_lower = context.lower()
        
        # API-related gaps
        if any(keyword in context_lower for keyword in ['api', 'endpoint', 'request', 'response']):
            return "api_detail"
        
        # Code-related gaps
        if any(keyword in context_lower for keyword in ['code', 'function', 'method', 'class']):
            return "code_example"
        
        # Configuration gaps
        if any(keyword in context_lower for keyword in ['config', 'setting', 'parameter', 'option']):
            return "configuration"
        
        # Authentication gaps
        if any(keyword in context_lower for keyword in ['auth', 'token', 'key', 'credential']):
            return "authentication"
        
        # Step or procedure gaps
        if any(keyword in context_lower for keyword in ['step', 'follow', 'process', 'procedure']):
            return "procedure_step"
        
        # Default to generic content
        return "generic_content"
    
    def _extract_section_name(self, content: str, position: int) -> str:
        """Extract the section name where the gap occurs"""
        try:
            # Look for the nearest heading before the gap position
            content_before = content[:position]
            
            # Find H2/H3 headings
            heading_pattern = r'<h[23][^>]*>(.*?)</h[23]>|^#{1,3}\s+(.+)$'
            headings = list(re.finditer(heading_pattern, content_before, re.MULTILINE | re.IGNORECASE))
            
            if headings:
                last_heading = headings[-1]
                heading_text = last_heading.group(1) or last_heading.group(2)
                return heading_text.strip() if heading_text else "Unknown Section"
            
            return "Introduction"
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error extracting section name - {e}")
            return "Unknown Section"
    
    async def _retrieve_gap_context(self, gaps: list, source_content: str, 
                                   source_blocks: list, enrich_mode: str) -> list:
        """Retrieve relevant content to fill gaps from available sources"""
        try:
            retrieval_results = []
            
            for gap in gaps:
                gap_type = gap.get('gap_type', 'generic_content')
                section = gap.get('section', 'Unknown Section')
                context = gap.get('context', '')
                
                # Extract keywords from gap context for retrieval
                keywords = self._extract_gap_keywords(context, gap_type)
                
                # Search in source content and blocks
                relevant_blocks = self._search_source_blocks(
                    keywords, source_blocks, gap_type
                )
                
                # If internal mode, also search content library
                if enrich_mode == "internal":
                    library_results = await self._search_content_library(keywords, gap_type)
                    relevant_blocks.extend(library_results)
                
                retrieval_results.append({
                    "gap_context": context,
                    "gap_type": gap_type,
                    "section": section,
                    "keywords": keywords,
                    "relevant_blocks": relevant_blocks[:10],  # Limit to top 10 results
                    "source_count": len(relevant_blocks)
                })
            
            return retrieval_results
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error in gap context retrieval - {e}")
            return []
    
    def _extract_gap_keywords(self, context: str, gap_type: str) -> list:
        """Extract relevant keywords from gap context for retrieval"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had'
        }
        
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', context.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Add gap-type specific keywords
        type_keywords = {
            'api_detail': ['api', 'endpoint', 'request', 'response', 'method'],
            'code_example': ['code', 'function', 'example', 'syntax'],
            'configuration': ['config', 'setting', 'parameter', 'value'],
            'authentication': ['auth', 'token', 'key', 'credential', 'login'],
            'procedure_step': ['step', 'process', 'procedure', 'follow']
        }
        
        if gap_type in type_keywords:
            keywords.extend(type_keywords[gap_type])
        
        return list(set(keywords))[:10]  # Return unique keywords, limit to 10
    
    def _search_source_blocks(self, keywords: list, source_blocks: list, gap_type: str) -> list:
        """Search source blocks for content relevant to filling the gap"""
        try:
            relevant_blocks = []
            
            for i, block in enumerate(source_blocks[:100]):  # Limit search scope
                block_content = block.get('content', '') or block.get('text', '')
                
                if not block_content:
                    continue
                
                # Calculate relevance score
                relevance_score = 0
                content_lower = block_content.lower()
                
                for keyword in keywords:
                    if keyword.lower() in content_lower:
                        relevance_score += 1
                
                # Bonus for gap type specific content
                if gap_type == 'api_detail' and any(term in content_lower for term in ['api', 'endpoint', 'http']):
                    relevance_score += 2
                elif gap_type == 'code_example' and any(term in content_lower for term in ['```', 'code', 'function']):
                    relevance_score += 2
                elif gap_type == 'authentication' and any(term in content_lower for term in ['token', 'auth', 'key']):
                    relevance_score += 2
                
                if relevance_score > 0:
                    relevant_blocks.append({
                        "block_id": f"b{i}",
                        "content": block_content[:500],  # Limit block size
                        "relevance_score": relevance_score,
                        "block_type": block.get('block_type', 'text')
                    })
            
            # Sort by relevance score
            relevant_blocks.sort(key=lambda x: x['relevance_score'], reverse=True)
            return relevant_blocks
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error searching source blocks - {e}")
            return []
    
    async def _search_content_library(self, keywords: list, gap_type: str) -> list:
        """Search content library for relevant gap-filling content using repository pattern"""
        try:
            library_results = []
            
            # Use repository pattern for content library access
            repository = get_repository()
            
            try:
                # Search content library for articles with matching keywords
                articles = await repository.content_library.find({"engine": "v2"}, limit=20)
                
                for article in articles:
                    try:
                        content = article.get('content', '') or article.get('html', '')
                        title = article.get('title', '')
                        
                        if not content:
                            continue
                        
                        # Calculate keyword relevance
                        content_lower = content.lower()
                        relevance_score = 0
                        
                        for keyword in keywords:
                            if keyword.lower() in content_lower:
                                relevance_score += 1
                            if keyword.lower() in title.lower():
                                relevance_score += 2  # Title matches get higher score
                        
                        if relevance_score > 0:
                            # Extract relevant snippet
                            snippet = self._extract_relevant_snippet(content, keywords)
                            
                            library_results.append({
                                "block_id": f"lib_{str(article.get('_id', ''))}",
                                "content": snippet,
                                "relevance_score": relevance_score,
                                "block_type": "library_article",
                                "source_title": title
                            })
                    
                    except Exception as article_error:
                        continue
                
            except Exception as repo_error:
                print(f"⚠️ V2 GAP FILLING: Repository error, using direct DB access - {repo_error}")
                # Fallback to direct database access if repository fails
                from pymongo import MongoClient
                import os
                
                try:
                    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/promptsupport')
                    client = MongoClient(mongo_url)
                    db = client.get_default_database()
                    
                    articles_cursor = db.content_library.find({"engine": "v2"}).limit(20)
                    
                    for article in articles_cursor:
                        try:
                            content = article.get('content', '') or article.get('html', '')
                            title = article.get('title', '')
                            
                            if not content:
                                continue
                            
                            # Calculate keyword relevance
                            content_lower = content.lower()
                            relevance_score = 0
                            
                            for keyword in keywords:
                                if keyword.lower() in content_lower:
                                    relevance_score += 1
                                if keyword.lower() in title.lower():
                                    relevance_score += 2  # Title matches get higher score
                            
                            if relevance_score > 0:
                                # Extract relevant snippet
                                snippet = self._extract_relevant_snippet(content, keywords)
                                
                                library_results.append({
                                    "block_id": f"lib_{str(article.get('_id', ''))}",
                                    "content": snippet,
                                    "relevance_score": relevance_score,
                                    "block_type": "library_article",
                                    "source_title": title
                                })
                        
                        except Exception as article_error:
                            continue
                
                except Exception as db_error:
                    print(f"❌ V2 GAP FILLING: Direct DB access also failed - {db_error}")
            
            # Sort by relevance
            library_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return library_results[:5]  # Return top 5 library results
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error searching content library - {e}")
            return []
    
    def _extract_relevant_snippet(self, content: str, keywords: list) -> str:
        """Extract a relevant snippet from content based on keywords"""
        try:
            # Find the best paragraph that contains multiple keywords
            paragraphs = content.split('\n')
            
            best_paragraph = ""
            best_score = 0
            
            for paragraph in paragraphs:
                if len(paragraph.strip()) < 20:
                    continue
                
                score = 0
                paragraph_lower = paragraph.lower()
                
                for keyword in keywords:
                    if keyword.lower() in paragraph_lower:
                        score += 1
                
                if score > best_score:
                    best_score = score
                    best_paragraph = paragraph
            
            if best_paragraph:
                return best_paragraph[:400] + "..." if len(best_paragraph) > 400 else best_paragraph
            
            # Fallback to first 400 characters
            return content[:400] + "..." if len(content) > 400 else content
            
        except Exception as e:
            return content[:400] + "..." if len(content) > 400 else content
    
    async def _generate_gap_patches(self, gaps: list, retrieval_results: list, 
                                   enrich_mode: str) -> list:
        """Generate patches for gaps using LLM with retrieved context"""
        try:
            patches = []
            
            for i, gap in enumerate(gaps):
                try:
                    retrieval_result = retrieval_results[i] if i < len(retrieval_results) else {}
                    relevant_blocks = retrieval_result.get('relevant_blocks', [])
                    
                    if not relevant_blocks and enrich_mode == "internal":
                        # No relevant content found for internal mode - skip
                        continue
                    
                    # Create LLM prompt for gap patching
                    patch_result = await self._create_gap_patch(
                        gap, relevant_blocks, enrich_mode
                    )
                    
                    if patch_result:
                        patches.append(patch_result)
                
                except Exception as gap_error:
                    print(f"❌ V2 GAP FILLING: Error generating patch for gap - {gap_error}")
                    continue
            
            return patches
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error generating gap patches - {e}")
            return []
    
    async def _create_gap_patch(self, gap: dict, relevant_blocks: list, enrich_mode: str) -> dict:
        """Create a single gap patch using LLM"""
        try:
            gap_context = gap.get('context', '')
            gap_type = gap.get('gap_type', 'generic_content')
            section = gap.get('section', 'Unknown Section')
            
            # Create evidence text from relevant blocks
            evidence_text = ""
            support_block_ids = []
            
            if relevant_blocks:
                for block in relevant_blocks[:5]:  # Use top 5 blocks
                    evidence_text += f"Block {block['block_id']}: {block['content']}\n\n"
                    support_block_ids.append(block['block_id'])
            
            # Create LLM prompt based on enrich mode
            if enrich_mode == "external" and not evidence_text.strip():
                # External mode with no evidence - use standard patterns
                system_message = """You are a gap-filler. Create concise, generic content for missing information using standard API patterns and best practices.

RULES FOR EXTERNAL MODE:
- Use only generic, industry-standard patterns
- No vendor-specific facts or details
- Mark as "(Assumed Standard Practice)" 
- Keep to 1-2 sentences maximum
- Set confidence to "low" when using generic patterns

Output format:
{"text": "content", "confidence": "low", "support_block_ids": [], "reasoning": "explanation"}"""
                
                user_message = f"""Gap Context: {gap_context}
Gap Type: {gap_type}
Section: {section}

Create generic filler content for this gap using standard industry practices. Mark as assumed standard practice."""

            else:
                # Internal mode with evidence
                system_message = """You are a gap-filler. Propose concise content to replace gaps strictly from the provided evidence.

RULES FOR INTERNAL MODE:
- If evidence supports a specific value, output 1-2 sentence patch with high confidence
- If evidence is generic patterns, output template sentence with low confidence
- Only use information from provided evidence blocks
- Reference support_block_ids for evidence used

Output format:
{"text": "content", "confidence": "high|low", "support_block_ids": ["b1","b2"], "reasoning": "explanation"}"""

                user_message = f"""Gap Context: {gap_context}
Gap Type: {gap_type}
Section: {section}

Available Evidence:
{evidence_text}

Create a patch for this gap using only the provided evidence. If evidence is insufficient, return null."""
            
            # Call LLM for gap patch using centralized client
            try:
                llm_response = await self.llm_client.generate_response(
                    system_message, user_message
                )
            except Exception as llm_error:
                print(f"⚠️ V2 GAP FILLING: LLM client error, skipping gap - {llm_error}")
                return None
            
            if not llm_response:
                return None
            
            # Parse LLM response
            try:
                patch_data = json.loads(llm_response)
                
                return {
                    "location": f"Section: {section}",
                    "text": patch_data.get('text', ''),
                    "support_block_ids": patch_data.get('support_block_ids', support_block_ids),
                    "confidence": patch_data.get('confidence', 'medium'),
                    "gap_pattern": gap.get('pattern', '[MISSING]'),
                    "gap_position": gap.get('position', 0),
                    "reasoning": patch_data.get('reasoning', ''),
                    "enrich_mode": enrich_mode
                }
                
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "location": f"Section: {section}",
                    "text": llm_response.strip(),
                    "support_block_ids": support_block_ids,
                    "confidence": "medium",
                    "gap_pattern": gap.get('pattern', '[MISSING]'),
                    "gap_position": gap.get('position', 0),
                    "reasoning": "LLM response parsing fallback",
                    "enrich_mode": enrich_mode
                }
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error creating gap patch - {e}")
            return None
    
    def _apply_patches(self, content: str, patches: list) -> Tuple[str, list]:
        """Apply patches to content, replacing gaps with generated content"""
        try:
            patched_content = content
            applied_patches = []
            
            # Sort patches by position in reverse order to maintain positions
            sorted_patches = sorted(patches, key=lambda x: x.get('gap_position', 0), reverse=True)
            
            for patch in sorted_patches:
                gap_pattern = patch.get('gap_pattern', '[MISSING]')
                replacement_text = patch.get('text', '')
                confidence = patch.get('confidence', 'medium')
                
                if not replacement_text:
                    continue
                
                # Add confidence indicator if low confidence
                if confidence == 'low':
                    replacement_text += " (Assumed Standard Practice)"
                
                # Replace the gap pattern with the patch
                if gap_pattern in patched_content:
                    patched_content = patched_content.replace(gap_pattern, replacement_text, 1)
                    applied_patches.append({
                        "location": patch.get('location', ''),
                        "original": gap_pattern,
                        "replacement": replacement_text,
                        "confidence": confidence,
                        "support_block_ids": patch.get('support_block_ids', []),
                        "reasoning": patch.get('reasoning', '')
                    })
            
            return patched_content, applied_patches
            
        except Exception as e:
            print(f"❌ V2 GAP FILLING: Error applying patches - {e}")
            return content, []

print("✅ KE-M6: V2 Gap Filling System migrated from server.py")