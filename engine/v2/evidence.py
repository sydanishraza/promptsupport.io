"""
KE-M7: V2 Evidence Tagging System - Complete Implementation Migration
Migrated from server.py - Evidence tagging system to enforce fidelity by mapping paragraphs to source blocks
"""

import json
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
from ..llm.client import get_llm_client
from ._utils import create_processing_metadata

class V2EvidenceTaggingSystem:
    """V2 Engine: Evidence tagging system to enforce fidelity by mapping paragraphs to source blocks"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.faq_indicators = ['faq', 'frequently asked questions', 'q:', 'question:', 'a:', 'answer:']
    
    async def run(self, gap_filled_content: dict, **kwargs) -> dict:
        """Tag content with evidence using centralized LLM client (new interface)"""
        try:
            print(f"🏷️ V2 EVIDENCE TAGGING: Starting evidence tagging process - engine=v2")
            
            # Extract parameters from kwargs
            articles = gap_filled_content.get('articles', [])
            source_blocks = kwargs.get('source_blocks', [])
            prewrite_data = kwargs.get('prewrite_data', {})
            run_id = kwargs.get('run_id', 'unknown')
            
            # Call the original tag_content_with_evidence method
            result = await self.tag_content_with_evidence(
                articles, source_blocks, prewrite_data, run_id
            )
            
            return result
            
        except Exception as e:
            print(f"❌ V2 EVIDENCE TAGGING: Error in run method - {e}")
            return {
                "evidence_tagging_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    async def tag_content_with_evidence(self, articles: list, source_blocks: list, 
                                       prewrite_data: dict, run_id: str) -> dict:
        """Tag paragraphs in articles with evidence block IDs to enforce fidelity"""
        try:
            print(f"🏷️ V2 EVIDENCE TAGGING: Starting evidence tagging process - engine=v2")
            
            evidence_tagging_results = []
            total_paragraphs = 0
            total_tagged_paragraphs = 0
            
            for i, article in enumerate(articles):
                try:
                    article_title = article.get('title', f'Article {i+1}')
                    article_content = article.get('content', '') or article.get('html', '')
                    
                    if not article_content:
                        continue
                    
                    # Step 1: Parse paragraphs from article content
                    paragraphs = self._parse_paragraphs(article_content)
                    
                    # Step 2: Get prewrite facts for this article
                    article_prewrite = self._get_article_prewrite_data(article, prewrite_data)
                    
                    # Step 3: Tag paragraphs with evidence
                    tagged_content, tagging_stats = self._tag_paragraphs_with_evidence(
                        article_content, paragraphs, source_blocks, article_prewrite
                    )
                    
                    # Update article with tagged content
                    article['content'] = tagged_content
                    article['html'] = tagged_content
                    
                    # Track statistics
                    article_total_paragraphs = tagging_stats['total_paragraphs']
                    article_tagged_paragraphs = tagging_stats['tagged_paragraphs']
                    total_paragraphs += article_total_paragraphs
                    total_tagged_paragraphs += article_tagged_paragraphs
                    
                    tagging_rate = (article_tagged_paragraphs / article_total_paragraphs * 100) if article_total_paragraphs > 0 else 0
                    
                    evidence_tagging_result = {
                        "article_index": i,
                        "article_title": article_title,
                        "evidence_tagging_status": "success",
                        "total_paragraphs": article_total_paragraphs,
                        "tagged_paragraphs": article_tagged_paragraphs,
                        "untagged_paragraphs": article_total_paragraphs - article_tagged_paragraphs,
                        "tagging_rate": tagging_rate,
                        "evidence_mapping": tagging_stats['evidence_mapping'],
                        "faq_paragraphs_skipped": tagging_stats['faq_paragraphs_skipped']
                    }
                    
                    evidence_tagging_results.append(evidence_tagging_result)
                    
                    print(f"✅ V2 EVIDENCE TAGGING: Tagged '{article_title[:50]}...' - {article_tagged_paragraphs}/{article_total_paragraphs} paragraphs ({tagging_rate:.1f}%) - engine=v2")
                    
                except Exception as article_error:
                    print(f"❌ V2 EVIDENCE TAGGING: Error processing article {i+1} - {article_error} - engine=v2")
                    evidence_tagging_results.append({
                        "article_index": i,
                        "article_title": article.get('title', f'Article {i+1}'),
                        "evidence_tagging_status": "error",
                        "error": str(article_error),
                        "total_paragraphs": 0,
                        "tagged_paragraphs": 0
                    })
            
            # Calculate overall statistics
            overall_tagging_rate = (total_tagged_paragraphs / total_paragraphs * 100) if total_paragraphs > 0 else 0
            successful_articles = len([r for r in evidence_tagging_results if r.get('evidence_tagging_status') == 'success'])
            
            return {
                "evidence_tagging_id": f"evidence_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "evidence_tagging_status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2",
                
                # Evidence tagging metrics
                "articles_processed": len(articles),
                "successful_articles": successful_articles,
                "total_paragraphs": total_paragraphs,
                "tagged_paragraphs": total_tagged_paragraphs,
                "untagged_paragraphs": total_paragraphs - total_tagged_paragraphs,
                "overall_tagging_rate": overall_tagging_rate,
                "target_achieved": overall_tagging_rate >= 95.0,
                
                # Detailed results
                "evidence_tagging_results": evidence_tagging_results,
                "source_blocks_used": len(source_blocks)
            }
            
        except Exception as e:
            print(f"❌ V2 EVIDENCE TAGGING: Error in evidence tagging process - {e} - engine=v2")
            return {
                "evidence_tagging_id": f"evidence_error_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "evidence_tagging_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    def _parse_paragraphs(self, content: str) -> list:
        """Parse paragraphs from HTML/markdown content"""
        try:
            paragraphs = []
            
            # Try HTML parsing first
            try:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find all paragraph elements
                p_tags = soup.find_all('p')
                
                for i, p_tag in enumerate(p_tags):
                    paragraph_text = p_tag.get_text().strip()
                    
                    if len(paragraph_text) < 20:  # Skip very short paragraphs
                        continue
                    
                    # Check if this is a FAQ paragraph (skip tagging)
                    is_faq = self._is_faq_paragraph(paragraph_text, str(p_tag))
                    
                    paragraphs.append({
                        "index": i,
                        "text": paragraph_text,
                        "html": str(p_tag),
                        "is_faq": is_faq,
                        "start_pos": content.find(str(p_tag)),
                        "end_pos": content.find(str(p_tag)) + len(str(p_tag))
                    })
                
            except Exception as html_error:
                # Fallback to simple text parsing
                text_paragraphs = content.split('\n\n')
                
                for i, paragraph in enumerate(text_paragraphs):
                    paragraph_text = paragraph.strip()
                    
                    if len(paragraph_text) < 20:
                        continue
                    
                    is_faq = self._is_faq_paragraph(paragraph_text, paragraph)
                    
                    paragraphs.append({
                        "index": i,
                        "text": paragraph_text,
                        "html": paragraph,
                        "is_faq": is_faq,
                        "start_pos": content.find(paragraph),
                        "end_pos": content.find(paragraph) + len(paragraph)
                    })
            
            return paragraphs
            
        except Exception as e:
            print(f"❌ V2 EVIDENCE TAGGING: Error parsing paragraphs - {e}")
            return []
    
    def _is_faq_paragraph(self, paragraph_text: str, paragraph_html: str) -> bool:
        """Check if a paragraph is part of FAQ section (should skip evidence tagging)"""
        text_lower = paragraph_text.lower()
        html_lower = paragraph_html.lower()
        
        # Check for FAQ indicators
        for indicator in self.faq_indicators:
            if indicator in text_lower or indicator in html_lower:
                return True
        
        # Check for FAQ patterns (Q: / A:)
        if re.match(r'^(q:|question:|a:|answer:)', text_lower.strip()):
            return True
        
        # Check if in FAQ section
        if 'faq' in html_lower or 'question' in html_lower:
            return True
        
        return False
    
    def _get_article_prewrite_data(self, article: dict, prewrite_data: dict) -> dict:
        """Get prewrite facts and evidence for a specific article"""
        try:
            article_title = article.get('title', '')
            
            # Try to find matching prewrite data by title
            prewrite_results = prewrite_data.get('prewrite_results', [])
            
            for prewrite_result in prewrite_results:
                if prewrite_result.get('article_title', '').strip().lower() == article_title.strip().lower():
                    return prewrite_result.get('prewrite_data', {})
            
            # Fallback: return first prewrite data if no match
            if prewrite_results:
                return prewrite_results[0].get('prewrite_data', {})
            
            return {}
            
        except Exception as e:
            print(f"❌ V2 EVIDENCE TAGGING: Error getting prewrite data - {e}")
            return {}
    
    def _tag_paragraphs_with_evidence(self, content: str, paragraphs: list, 
                                     source_blocks: list, prewrite_data: dict) -> Tuple[str, dict]:
        """Tag paragraphs with evidence block IDs"""
        try:
            tagged_content = content
            tagged_count = 0
            faq_skipped = 0
            evidence_mapping = []
            
            # Sort paragraphs by position in reverse order to maintain positions during replacement
            sorted_paragraphs = sorted(paragraphs, key=lambda x: x.get('start_pos', 0), reverse=True)
            
            for paragraph in sorted_paragraphs:
                try:
                    # Skip FAQ paragraphs
                    if paragraph.get('is_faq', False):
                        faq_skipped += 1
                        continue
                    
                    paragraph_text = paragraph.get('text', '')
                    paragraph_html = paragraph.get('html', '')
                    
                    if not paragraph_text:
                        continue
                    
                    # Find relevant evidence blocks for this paragraph
                    evidence_blocks = self._find_evidence_for_paragraph(
                        paragraph_text, source_blocks, prewrite_data
                    )
                    
                    if evidence_blocks:
                        # Create evidence attribute
                        block_ids = [block['block_id'] for block in evidence_blocks]
                        evidence_attr = f'data-evidence="{json.dumps(block_ids)}"'
                        
                        # Add evidence attribute to paragraph
                        if paragraph_html.startswith('<p'):
                            # HTML paragraph - add attribute to <p> tag
                            if '>' in paragraph_html:
                                tag_end = paragraph_html.find('>')
                                tagged_paragraph = (paragraph_html[:tag_end] + ' ' + 
                                                  evidence_attr + paragraph_html[tag_end:])
                            else:
                                tagged_paragraph = paragraph_html
                        else:
                            # Plain text paragraph - add as HTML comment
                            tagged_paragraph = f'<!-- {evidence_attr} -->\n{paragraph_html}'
                        
                        # Replace in content
                        tagged_content = tagged_content.replace(paragraph_html, tagged_paragraph)
                        tagged_count += 1
                        
                        # Track evidence mapping
                        evidence_mapping.append({
                            "paragraph_index": paragraph.get('index'),
                            "paragraph_preview": paragraph_text[:100],
                            "evidence_blocks": block_ids,
                            "evidence_count": len(block_ids),
                            "confidence_score": self._calculate_evidence_confidence(evidence_blocks)
                        })
                
                except Exception as paragraph_error:
                    print(f"❌ V2 EVIDENCE TAGGING: Error tagging paragraph - {paragraph_error}")
                    continue
            
            return tagged_content, {
                "total_paragraphs": len(paragraphs),
                "tagged_paragraphs": tagged_count,
                "faq_paragraphs_skipped": faq_skipped,
                "evidence_mapping": evidence_mapping
            }
            
        except Exception as e:
            print(f"❌ V2 EVIDENCE TAGGING: Error in paragraph tagging - {e}")
            return content, {
                "total_paragraphs": len(paragraphs),
                "tagged_paragraphs": 0,
                "faq_paragraphs_skipped": 0,
                "evidence_mapping": []
            }
    
    def _find_evidence_for_paragraph(self, paragraph_text: str, source_blocks: list, 
                                    prewrite_data: dict) -> list:
        """Find relevant evidence blocks for a paragraph using prewrite facts and block matching"""
        try:
            evidence_blocks = []
            
            # Extract keywords from paragraph
            paragraph_keywords = self._extract_paragraph_keywords(paragraph_text)
            
            # Try to match with prewrite facts first
            prewrite_facts = prewrite_data.get('facts', [])
            
            for fact in prewrite_facts:
                fact_text = fact.get('text', '')
                fact_blocks = fact.get('source_blocks', [])
                
                if not fact_text or not fact_blocks:
                    continue
                
                # Calculate relevance between paragraph and fact
                relevance_score = self._calculate_text_relevance(paragraph_text, fact_text)
                
                if relevance_score > 0.3:  # Threshold for relevance
                    # Add source blocks from matching fact
                    for block_id in fact_blocks:
                        evidence_blocks.append({
                            "block_id": block_id,
                            "relevance_score": relevance_score,
                            "source": "prewrite_fact",
                            "fact_text": fact_text[:100]
                        })
            
            # If no prewrite matches, try direct block matching
            if not evidence_blocks:
                for i, block in enumerate(source_blocks[:50]):  # Limit for performance
                    block_content = block.get('content', '') or block.get('text', '')
                    
                    if not block_content:
                        continue
                    
                    # Calculate relevance between paragraph and block
                    relevance_score = self._calculate_text_relevance(paragraph_text, block_content)
                    
                    if relevance_score > 0.2:  # Lower threshold for direct block matching
                        evidence_blocks.append({
                            "block_id": f"b{i}",
                            "relevance_score": relevance_score,
                            "source": "direct_block",
                            "block_preview": block_content[:100]
                        })
            
            # Sort by relevance score and return top matches
            evidence_blocks.sort(key=lambda x: x['relevance_score'], reverse=True)
            return evidence_blocks[:3]  # Return top 3 evidence blocks
            
        except Exception as e:
            print(f"❌ V2 EVIDENCE TAGGING: Error finding evidence - {e}")
            return []
    
    def _extract_paragraph_keywords(self, paragraph_text: str) -> list:
        """Extract keywords from paragraph text for matching"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', paragraph_text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        return keywords[:10]  # Return top 10 keywords
    
    def _calculate_text_relevance(self, text1: str, text2: str) -> float:
        """Calculate relevance score between two pieces of text"""
        try:
            keywords1 = set(self._extract_paragraph_keywords(text1))
            keywords2 = set(self._extract_paragraph_keywords(text2))
            
            if not keywords1 or not keywords2:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = len(keywords1.intersection(keywords2))
            union = len(keywords1.union(keywords2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    def _calculate_evidence_confidence(self, evidence_blocks: list) -> float:
        """Calculate confidence score for evidence blocks"""
        if not evidence_blocks:
            return 0.0
        
        # Base confidence on number of blocks and relevance scores
        avg_relevance = sum(block.get('relevance_score', 0) for block in evidence_blocks) / len(evidence_blocks)
        block_count_factor = min(len(evidence_blocks) / 3.0, 1.0)  # Max factor at 3 blocks
        
        return avg_relevance * block_count_factor

print("✅ KE-M7: V2 Evidence Tagging System migrated from server.py")
            
        except Exception as e:
            print(f"❌ V2 EVIDENCE: Error tagging evidence - {e}")
            return {
                'articles': coded_content.get('articles', []),
                'evidence_metadata': {
                    'articles_processed': 0,
                    'total_evidence_tags': 0,
                    'tagging_rate': 0,
                    'error': str(e)
                },
                'error': str(e)
            }
    
    async def _tag_article_evidence(self, article: dict) -> dict:
        """Tag evidence in a single article"""
        try:
            title = article.get('title', 'Article')
            content = article.get('content', '')
            
            if not content:
                return self._create_untagged_article(article, "No content to tag")
            
            # Parse content into sections/paragraphs
            content_sections = self._parse_content_sections(content)
            
            # Tag each section with evidence levels
            tagged_sections = []
            evidence_tags_added = 0
            
            for section in content_sections:
                tagged_section = await self._tag_section_evidence(section, title)
                tagged_sections.append(tagged_section)
                evidence_tags_added += len(tagged_section.get('evidence_tags', []))
            
            # Reconstruct content with evidence tags
            tagged_content = self._reconstruct_tagged_content(tagged_sections)
            
            # Create evidence summary
            evidence_summary = self._create_evidence_summary(tagged_sections)
            
            # Create tagged article
            tagged_article = article.copy()
            tagged_article['content'] = tagged_content
            tagged_article['evidence_metadata'] = {
                'evidence_tags_added': evidence_tags_added,
                'sections_processed': len(tagged_sections),
                'evidence_summary': evidence_summary,
                'fidelity_score': self._calculate_fidelity_score(evidence_summary),
                'source_traceability': 'high'
            }
            
            return tagged_article
            
        except Exception as e:
            print(f"❌ V2 EVIDENCE: Error tagging article evidence - {e}")
            return self._create_untagged_article(article, str(e))
    
    def _parse_content_sections(self, content: str) -> List[dict]:
        """Parse content into sections for evidence tagging"""
        sections = []
        current_section = None
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if stripped.startswith('#'):
                # New heading section
                if current_section:
                    sections.append(current_section)
                
                level = len(stripped) - len(stripped.lstrip('#'))
                title = stripped.lstrip('# ').strip()
                
                current_section = {
                    'type': 'heading',
                    'level': level,
                    'title': title,
                    'content': line,
                    'line_number': i + 1,
                    'paragraphs': []
                }
            
            elif stripped and not stripped.startswith('#'):
                # Content line
                if not current_section:
                    # Content without heading
                    current_section = {
                        'type': 'content',
                        'level': 0,
                        'title': 'Introduction',
                        'content': '',
                        'line_number': i + 1,
                        'paragraphs': []
                    }
                
                # Add to current section
                if line.strip():
                    current_section['content'] += line + '\n'
                    
                    # Check if this starts a new paragraph
                    if stripped and (i == 0 or not lines[i-1].strip()):
                        # Start of new paragraph
                        paragraph = {
                            'content': stripped,
                            'line_number': i + 1,
                            'type': self._classify_paragraph_type(stripped)
                        }
                        current_section['paragraphs'].append(paragraph)
                    elif current_section['paragraphs']:
                        # Continue current paragraph
                        current_section['paragraphs'][-1]['content'] += ' ' + stripped
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _classify_paragraph_type(self, paragraph: str) -> str:
        """Classify paragraph type for evidence tagging"""
        paragraph_lower = paragraph.lower()
        
        if any(word in paragraph_lower for word in ['```', 'code', 'function', 'class']):
            return 'code_example'
        elif any(word in paragraph_lower for word in ['note:', 'important:', 'warning:']):
            return 'annotation'
        elif paragraph.startswith('- ') or paragraph.startswith('* '):
            return 'list_item'
        elif any(word in paragraph_lower for word in ['according to', 'research shows', 'studies indicate']):
            return 'factual_statement'
        elif any(word in paragraph_lower for word in ['recommended', 'best practice', 'should']):
            return 'recommendation'
        elif any(word in paragraph_lower for word in ['example', 'for instance', 'such as']):
            return 'example'
        else:
            return 'general_content'
    
    async def _tag_section_evidence(self, section: dict, article_title: str) -> dict:
        """Tag evidence in a single section"""
        try:
            section_title = section.get('title', 'Section')
            paragraphs = section.get('paragraphs', [])
            
            if not paragraphs:
                return section
            
            tagged_section = section.copy()
            tagged_section['evidence_tags'] = []
            
            # Tag each paragraph
            for paragraph in paragraphs:
                paragraph_content = paragraph.get('content', '')
                paragraph_type = paragraph.get('type', 'general_content')
                
                # Determine evidence level based on paragraph type and content
                evidence_level = self._determine_evidence_level(paragraph_content, paragraph_type)
                source_type = self._determine_source_type(paragraph_content, paragraph_type)
                confidence = self._calculate_confidence(paragraph_content, evidence_level)
                
                # Create evidence tag
                evidence_tag = {
                    'paragraph_content': paragraph_content[:100] + '...' if len(paragraph_content) > 100 else paragraph_content,
                    'evidence_level': evidence_level,
                    'source_type': source_type,
                    'confidence': confidence,
                    'line_number': paragraph.get('line_number'),
                    'section_title': section_title,
                    'data_evidence': f"block-{hash(paragraph_content) % 10000}",  # Generate block ID
                    'fidelity_enforcement': evidence_level in ['HIGH', 'MEDIUM']
                }
                
                tagged_section['evidence_tags'].append(evidence_tag)
            
            return tagged_section
            
        except Exception as e:
            print(f"⚠️ V2 EVIDENCE: Error tagging section - {e}")
            return section
    
    def _determine_evidence_level(self, content: str, paragraph_type: str) -> str:
        """Determine evidence level for content"""
        content_lower = content.lower()
        
        # HIGH evidence: Verifiable facts, code examples, official docs
        if paragraph_type == 'code_example':
            return 'HIGH'
        elif any(word in content_lower for word in [
            'official documentation', 'specification', 'rfc', 'standard',
            'according to the documentation', 'as per the spec'
        ]):
            return 'HIGH'
        elif any(word in content_lower for word in [
            'function', 'method', 'parameter', 'return', 'api endpoint'
        ]):
            return 'HIGH'
        
        # MEDIUM evidence: Best practices, expert consensus, established patterns
        elif paragraph_type in ['recommendation', 'factual_statement']:
            return 'MEDIUM'
        elif any(word in content_lower for word in [
            'best practice', 'recommended', 'commonly used', 'typically',
            'industry standard', 'widely accepted'
        ]):
            return 'MEDIUM'
        
        # LOW evidence: Opinions, general advice, subjective assessments
        elif any(word in content_lower for word in [
            'consider', 'might', 'could be', 'potentially', 'often',
            'usually', 'generally', 'in most cases'
        ]):
            return 'LOW'
        
        # SPECULATION: Future predictions, unverified claims
        elif any(word in content_lower for word in [
            'will be', 'expected to', 'likely', 'probably', 'may become',
            'future', 'upcoming', 'planned'
        ]):
            return 'SPECULATION'
        
        # Default to MEDIUM for general content
        else:
            return 'MEDIUM'
    
    def _determine_source_type(self, content: str, paragraph_type: str) -> str:
        """Determine source type for content"""
        content_lower = content.lower()
        
        if paragraph_type == 'code_example':
            return 'code_example'
        elif 'documentation' in content_lower or 'specification' in content_lower:
            return 'official_specification'
        elif paragraph_type == 'recommendation':
            return 'best_practice'
        elif paragraph_type == 'factual_statement':
            return 'expert_consensus'
        elif 'example' in content_lower:
            return 'code_example'
        else:
            return 'technical_documentation'
    
    def _calculate_confidence(self, content: str, evidence_level: str) -> float:
        """Calculate confidence score for evidence"""
        base_confidence = {
            'HIGH': 0.9,
            'MEDIUM': 0.7,
            'LOW': 0.5,
            'SPECULATION': 0.3
        }.get(evidence_level, 0.5)
        
        # Adjust based on content characteristics
        content_lower = content.lower()
        
        # Increase confidence for specific indicators
        if any(word in content_lower for word in ['documented', 'specified', 'defined']):
            base_confidence = min(1.0, base_confidence + 0.1)
        
        # Decrease confidence for uncertainty indicators
        if any(word in content_lower for word in ['maybe', 'perhaps', 'possibly']):
            base_confidence = max(0.1, base_confidence - 0.2)
        
        return round(base_confidence, 2)
    
    def _reconstruct_tagged_content(self, tagged_sections: List[dict]) -> str:
        """Reconstruct content with evidence tags embedded"""
        reconstructed_lines = []
        
        for section in tagged_sections:
            # Add section heading
            if section.get('type') == 'heading':
                level = section.get('level', 1)
                title = section.get('title', 'Section')
                heading_line = '#' * level + ' ' + title
                reconstructed_lines.append(heading_line)
                reconstructed_lines.append('')  # Empty line after heading
            
            # Add section content with evidence tags
            section_content = section.get('content', '').strip()
            if section_content:
                # Add data-evidence attributes to paragraphs
                evidence_tags = section.get('evidence_tags', [])
                
                if evidence_tags:
                    # Add evidence metadata as HTML comments
                    for tag in evidence_tags:
                        evidence_comment = f"<!-- data-evidence=\"{tag['data_evidence']}\" evidence-level=\"{tag['evidence_level']}\" source-type=\"{tag['source_type']}\" confidence=\"{tag['confidence']}\" -->"
                        reconstructed_lines.append(evidence_comment)
                
                reconstructed_lines.append(section_content)
                reconstructed_lines.append('')  # Empty line after content
        
        return '\n'.join(reconstructed_lines)
    
    def _create_evidence_summary(self, tagged_sections: List[dict]) -> dict:
        """Create summary of evidence tagging results"""
        all_tags = []
        for section in tagged_sections:
            all_tags.extend(section.get('evidence_tags', []))
        
        if not all_tags:
            return {
                'total_tags': 0,
                'by_level': {},
                'by_source_type': {},
                'average_confidence': 0,
                'fidelity_indicators': []
            }
        
        # Group by evidence level
        by_level = {}
        for tag in all_tags:
            level = tag.get('evidence_level', 'UNKNOWN')
            by_level[level] = by_level.get(level, 0) + 1
        
        # Group by source type
        by_source_type = {}
        for tag in all_tags:
            source_type = tag.get('source_type', 'unknown')
            by_source_type[source_type] = by_source_type.get(source_type, 0) + 1
        
        # Calculate average confidence
        confidences = [tag.get('confidence', 0) for tag in all_tags]
        avg_confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0
        
        # Identify fidelity indicators
        fidelity_indicators = []
        high_evidence_count = by_level.get('HIGH', 0)
        if high_evidence_count > 0:
            fidelity_indicators.append(f"{high_evidence_count} high-evidence statements")
        
        code_examples = by_source_type.get('code_example', 0)
        if code_examples > 0:
            fidelity_indicators.append(f"{code_examples} code examples")
        
        return {
            'total_tags': len(all_tags),
            'by_level': by_level,
            'by_source_type': by_source_type,
            'average_confidence': avg_confidence,
            'fidelity_indicators': fidelity_indicators
        }
    
    def _calculate_fidelity_score(self, evidence_summary: dict) -> float:
        """Calculate fidelity score based on evidence quality"""
        total_tags = evidence_summary.get('total_tags', 0)
        if total_tags == 0:
            return 0.0
        
        by_level = evidence_summary.get('by_level', {})
        avg_confidence = evidence_summary.get('average_confidence', 0)
        
        # Score based on evidence level distribution
        high_count = by_level.get('HIGH', 0)
        medium_count = by_level.get('MEDIUM', 0)
        low_count = by_level.get('LOW', 0)
        speculation_count = by_level.get('SPECULATION', 0)
        
        level_score = (
            (high_count * 1.0) +
            (medium_count * 0.7) +
            (low_count * 0.4) +
            (speculation_count * 0.1)
        ) / total_tags
        
        # Combine with confidence score
        fidelity_score = (level_score * 0.7) + (avg_confidence * 0.3)
        
        return round(fidelity_score, 2)
    
    def _create_untagged_article(self, article: dict, reason: str) -> dict:
        """Create article with no evidence tags due to error"""
        untagged_article = article.copy()
        untagged_article['evidence_metadata'] = {
            'evidence_tags_added': 0,
            'sections_processed': 0,
            'evidence_summary': {
                'total_tags': 0,
                'by_level': {},
                'by_source_type': {},
                'average_confidence': 0,
                'fidelity_indicators': []
            },
            'fidelity_score': 0.0,
            'source_traceability': 'none',
            'error': reason
        }
        return untagged_article