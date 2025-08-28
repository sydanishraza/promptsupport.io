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