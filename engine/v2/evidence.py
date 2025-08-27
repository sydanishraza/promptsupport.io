"""
KE-PR5: V2 Evidence Tagging System - Complete Implementation
Extracted from server.py - Evidence paragraph tagging with block ID attribution and fidelity enforcement
"""

from typing import Dict, Any, List
from ..llm.client import get_llm_client
from ..llm.prompts import EVIDENCE_TAGGING_PROMPT

class V2EvidenceTaggingSystem:
    """V2 Engine: Evidence paragraph tagging with block ID attribution, fidelity enforcement, and source traceability"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.evidence_levels = ['HIGH', 'MEDIUM', 'LOW', 'SPECULATION']
        self.source_types = [
            'technical_documentation', 'code_example', 'official_specification',
            'expert_consensus', 'best_practice', 'opinion', 'assumption'
        ]
    
    async def tag_evidence(self, coded_content: dict, **kwargs) -> dict:
        """Tag content with evidence levels and source attribution"""
        try:
            print(f"🔍 V2 EVIDENCE: Starting evidence tagging - engine=v2")
            
            articles = coded_content.get('articles', [])
            tagged_articles = []
            total_tags_added = 0
            
            for article in articles:
                tagged_article = await self._tag_article_evidence(article)
                tagged_articles.append(tagged_article)
                
                # Count evidence tags
                evidence_metadata = tagged_article.get('evidence_metadata', {})
                tags_added = evidence_metadata.get('evidence_tags_added', 0)
                total_tags_added += tags_added
            
            result = {
                'articles': tagged_articles,
                'evidence_metadata': {
                    'articles_processed': len(tagged_articles),
                    'total_evidence_tags': total_tags_added,
                    'tagging_rate': round((total_tags_added / max(1, len(tagged_articles))) * 100, 1),
                    'engine': 'v2'
                }
            }
            
            print(f"✅ V2 EVIDENCE: Tagged {len(tagged_articles)} articles with {total_tags_added} evidence tags")
            return result
            
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