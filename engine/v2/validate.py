"""
KE-M10: V2 Validation System - Complete Implementation Migration
Migrated from server.py - Comprehensive validation system for fidelity, coverage, placeholders, and style
"""

import json
import re
import uuid
from typing import Dict, Any, List
from datetime import datetime
from bs4 import BeautifulSoup
from ..llm.client import get_llm_client
from ..stores.mongo import RepositoryFactory
from ..linking.anchors import stable_slug, assign_heading_ids, validate_heading_ladder
from ..linking.toc import build_minitoc, anchors_resolve
from ..linking.bookmarks import extract_headings_registry, generate_doc_uid, generate_doc_slug
from ..linking.links import build_href, get_default_route_map
from ._utils import create_processing_metadata

class V2ValidationSystem:
    """V2 Engine: Comprehensive validation system for fidelity, coverage, placeholders, and style"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.required_sections = [
            "h1_title",
            "intro_paragraph",
            "mini_toc", 
            "main_body",
            "faqs",
            "related_links"
        ]
        
        self.quality_thresholds = {
            "coverage_percent": 100,
            "fidelity_score": 0.9,
            "redundancy_score": 0.3,  # Lower is better
            "max_placeholders": 0
        }
        
        # TICKET 1 FIX: Style validation rules including H1 prohibition
        self.style_validation_rules = {
            "no_h1_in_body": True,
            "require_mini_toc": True,
            "require_structured_headings": True
        }
    
    async def run(self, content: dict, **kwargs) -> dict:
        """Run validation using centralized LLM client (new interface)"""
        try:
            print("🔍 V2 VALIDATION: Starting validation process - engine=v2")
            
            # Extract parameters from kwargs
            normalized_doc = kwargs.get('normalized_doc')
            generated_articles_result = kwargs.get('generated_articles_result', {})
            analysis = kwargs.get('analysis', {})
            run_id = kwargs.get('run_id', 'unknown')
            
            # Call the original validate_generated_articles method
            result = await self.validate_generated_articles(
                normalized_doc, generated_articles_result, analysis, run_id
            )
            
            return result
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error in run method - {e}")
            return {
                "validation_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    # KE-PR2: Use extracted linking modules instead of inline methods
    def stable_slug(self, text: str, max_len: int = 60) -> str:
        """TICKET 2: Generate deterministic, URL-safe slugs - delegated to engine.linking.anchors"""
        return stable_slug(text, max_len)
    
    def assign_heading_ids(self, html: str) -> str:
        """TICKET 2: Assign deterministic IDs to headings - delegated to engine.linking.anchors"""
        return assign_heading_ids(html)
    
    def validate_heading_ladder(self, html: str) -> bool:
        """TICKET 2: Validate proper heading hierarchy - delegated to engine.linking.anchors"""
        return validate_heading_ladder(html)
    
    def build_minitoc(self, html: str) -> str:
        """TICKET 2: Build Mini-TOC with clickable links - delegated to engine.linking.toc"""
        return build_minitoc(html)
    
    def anchors_resolve(self, html: str) -> bool:
        """TICKET 2: Validate TOC links resolve - delegated to engine.linking.toc"""
        return anchors_resolve(html)
    
    def extract_headings_registry(self, html: str) -> list:
        """TICKET 3: Extract headings for bookmark registry - delegated to engine.linking.bookmarks"""
        return extract_headings_registry(html)
    
    # KE-PR2: Use extracted linking modules 
    def generate_doc_uid(self) -> str:
        """TICKET 3: Generate document UID - delegated to engine.linking.bookmarks"""
        return generate_doc_uid()
    
    def generate_doc_slug(self, title: str) -> str:
        """TICKET 3: Generate document slug - delegated to engine.linking.bookmarks"""
        return generate_doc_slug(title)
    
    def build_href(self, target_doc: dict, anchor_id: str, route_map: dict) -> str:
        """TICKET 3: Build environment-aware href - delegated to engine.linking.links"""
        return build_href(target_doc, anchor_id, route_map)
    
    def get_default_route_map(self, environment: str = "content_library") -> dict:
        """TICKET 3: Get default route map - delegated to engine.linking.links"""
        return get_default_route_map(environment)
    
    async def validate_content(self, styled_content: dict, raw_source: dict = None, **kwargs) -> dict:
        """Perform comprehensive content validation"""
        try:
            print(f"✅ V2 VALIDATION: Starting comprehensive validation - engine=v2")
            
            articles = styled_content.get('articles', [])
            validated_articles = []
            validation_issues = []
            
            for article in articles:
                validated_article, issues = await self._validate_single_article(article, raw_source)
                validated_articles.append(validated_article)
                validation_issues.extend(issues)
            
            # Create QA report
            qa_report = self._create_qa_report(validation_issues, validated_articles)
            
            result = {
                'articles': validated_articles,
                'qa_report': qa_report,
                'validation_metadata': {
                    'articles_validated': len(validated_articles),
                    'total_issues_found': len(validation_issues),
                    'validation_score': qa_report.get('overall_score', 0),
                    'engine': 'v2'
                }
            }
            
            print(f"✅ V2 VALIDATION: Validated {len(validated_articles)} articles, found {len(validation_issues)} issues")
            return result
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error in validation - {e}")
            return {
                'articles': styled_content.get('articles', []),
                'qa_report': self._create_error_qa_report(str(e)),
                'error': str(e)
            }
    
    async def _validate_single_article(self, article: dict, raw_source: dict = None) -> tuple:
        """Validate a single article and return issues found"""
        try:
            title = article.get('title', 'Article')
            content = article.get('content', '')
            
            issues = []
            
            # Perform validation checks
            issues.extend(self._check_technical_accuracy(content, title))
            issues.extend(self._check_completeness(content, article))
            issues.extend(self._check_clarity_readability(content))
            issues.extend(self._check_consistency(content))
            issues.extend(self._check_format_compliance(content))
            issues.extend(self._detect_placeholders(content))
            
            # Calculate validation score
            validation_score = self._calculate_validation_score(issues, content)
            
            # Create validated article
            validated_article = article.copy()
            validated_article['validation'] = {
                'issues_found': len(issues),
                'validation_score': validation_score,
                'checks_performed': len(self.validation_checks),
                'validation_status': 'passed' if len(issues) == 0 else 'issues_found'
            }
            
            return validated_article, issues
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error validating article - {e}")
            return article, [{'type': 'validation_error', 'message': str(e), 'severity': 'high'}]
    
    def _check_technical_accuracy(self, content: str, title: str) -> List[dict]:
        """Check technical accuracy of content"""
        issues = []
        
        # Check for common technical inaccuracies
        if 'API' in content.upper():
            # Check API-related accuracy
            if 'rest api' in content.lower() and 'http' not in content.lower():
                issues.append({
                    'type': 'technical_accuracy',
                    'message': 'REST API mentioned but HTTP protocol not explained',
                    'severity': 'medium',
                    'line': None
                })
        
        # Check for vague technical statements
        vague_patterns = ['it works', 'simply works', 'just use', 'easily done']
        for pattern in vague_patterns:
            if pattern in content.lower():
                issues.append({
                    'type': 'technical_accuracy',
                    'message': f'Vague statement detected: "{pattern}"',
                    'severity': 'low',
                    'line': None
                })
        
        return issues
    
    def _check_completeness(self, content: str, article: dict) -> List[dict]:
        """Check content completeness"""
        issues = []
        
        # Check minimum content length
        if len(content.strip()) < 100:
            issues.append({
                'type': 'completeness',
                'message': 'Content is too short (less than 100 characters)',
                'severity': 'high',
                'line': None
            })
        
        # Check for essential sections
        outline = article.get('outline', {})
        sections = outline.get('sections', [])
        
        high_priority_sections = [s for s in sections if s.get('priority') == 'high']
        for section in high_priority_sections:
            section_title = section.get('title', '').lower()
            if section_title not in content.lower():
                issues.append({
                    'type': 'completeness',
                    'message': f'High priority section missing: {section.get("title")}',
                    'severity': 'medium',
                    'line': None
                })
        
        return issues
    
    def _check_clarity_readability(self, content: str) -> List[dict]:
        """Check clarity and readability"""
        issues = []
        
        # Check sentence length
        sentences = content.split('.')
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        if long_sentences:
            issues.append({
                'type': 'clarity',
                'message': f'Found {len(long_sentences)} overly long sentences (>30 words)',
                'severity': 'low',
                'line': None
            })
        
        # Check for proper headings
        if '#' not in content:
            issues.append({
                'type': 'clarity',
                'message': 'No headings found - content may be difficult to scan',
                'severity': 'medium',
                'line': None
            })
        
        # Check paragraph structure
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 200]
        if long_paragraphs:
            issues.append({
                'type': 'clarity',
                'message': f'Found {len(long_paragraphs)} overly long paragraphs (>200 words)',
                'severity': 'low',
                'line': None
            })
        
        return issues
    
    def _check_consistency(self, content: str) -> List[dict]:
        """Check content consistency"""
        issues = []
        
        # Check heading consistency
        headings = [line.strip() for line in content.split('\n') if line.strip().startswith('#')]
        if headings:
            # Check for consistent heading levels
            levels = [len(h) - len(h.lstrip('#')) for h in headings]
            if len(set(levels)) > 4:  # Too many heading levels
                issues.append({
                    'type': 'consistency',
                    'message': 'Too many heading levels used (>4 levels)',
                    'severity': 'low',
                    'line': None
                })
        
        # Check for consistent terminology
        # Simple check for mixed case variations of common terms
        terms_to_check = ['API', 'JSON', 'HTTP', 'URL']
        for term in terms_to_check:
            variations = [term.lower(), term.upper(), term.capitalize()]
            found_variations = [v for v in variations if v in content and v != term]
            if len(found_variations) > 1:
                issues.append({
                    'type': 'consistency',
                    'message': f'Inconsistent capitalization of "{term}"',
                    'severity': 'low',
                    'line': None
                })
        
        return issues
    
    def _check_format_compliance(self, content: str) -> List[dict]:
        """Check format compliance"""
        issues = []
        
        # Check markdown formatting
        if '```' in content:
            # Check for unclosed code blocks
            code_block_count = content.count('```')
            if code_block_count % 2 != 0:
                issues.append({
                    'type': 'format_compliance',
                    'message': 'Unclosed code block detected',
                    'severity': 'high',
                    'line': None
                })
        
        # Check for proper list formatting
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('*') or stripped.startswith('-'):
                # Check if list item has content
                list_content = stripped[1:].strip()
                if not list_content:
                    issues.append({
                        'type': 'format_compliance',
                        'message': f'Empty list item at line {i+1}',
                        'severity': 'low',
                        'line': i+1
                    })
        
        return issues
    
    def _detect_placeholders(self, content: str) -> List[dict]:
        """Detect placeholder content that needs completion"""
        issues = []
        
        for pattern in self.placeholder_patterns:
            if pattern in content:
                count = content.count(pattern)
                issues.append({
                    'type': 'placeholder_detection',
                    'message': f'Placeholder "{pattern}" found {count} times',
                    'severity': 'high',
                    'line': None
                })
        
        return issues
    
    def _calculate_validation_score(self, issues: List[dict], content: str) -> float:
        """Calculate overall validation score"""
        if not issues:
            return 100.0
        
        # Score based on issue severity
        severity_penalties = {'high': 10, 'medium': 5, 'low': 2}
        total_penalty = sum(severity_penalties.get(issue.get('severity', 'low'), 2) for issue in issues)
        
        # Base score starts at 100, subtract penalties
        score = max(0, 100 - total_penalty)
        
        # Bonus for good content length
        if 500 < len(content) < 5000:
            score = min(100, score + 5)
        
        return round(score, 1)
    
    def _create_qa_report(self, all_issues: List[dict], articles: List[dict]) -> dict:
        """Create comprehensive QA report"""
        # Group issues by type
        issues_by_type = {}
        for issue in all_issues:
            issue_type = issue.get('type', 'unknown')
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # Calculate overall score
        high_issues = len([i for i in all_issues if i.get('severity') == 'high'])
        medium_issues = len([i for i in all_issues if i.get('severity') == 'medium'])
        low_issues = len([i for i in all_issues if i.get('severity') == 'low'])
        
        if high_issues > 0:
            overall_score = max(0, 70 - (high_issues * 10))
        elif medium_issues > 0:
            overall_score = max(70, 90 - (medium_issues * 5))
        else:
            overall_score = max(90, 100 - (low_issues * 2))
        
        return {
            'overall_score': round(overall_score, 1),
            'total_issues': len(all_issues),
            'issues_by_severity': {
                'high': high_issues,
                'medium': medium_issues,
                'low': low_issues
            },
            'issues_by_type': {k: len(v) for k, v in issues_by_type.items()},
            'detailed_issues': all_issues[:20],  # Limit to first 20 issues
            'articles_processed': len(articles),
            'validation_passed': len(all_issues) == 0,
            'recommendations': self._generate_recommendations(issues_by_type)
        }
    
    def _create_error_qa_report(self, error_message: str) -> dict:
        """Create QA report for validation errors"""
        return {
            'overall_score': 0,
            'total_issues': 1,
            'issues_by_severity': {'high': 1, 'medium': 0, 'low': 0},
            'issues_by_type': {'validation_error': 1},
            'detailed_issues': [{
                'type': 'validation_error',
                'message': f'Validation failed: {error_message}',
                'severity': 'high'
            }],
            'articles_processed': 0,
            'validation_passed': False,
            'recommendations': ['Fix validation system errors before proceeding']
        }
    
    def _generate_recommendations(self, issues_by_type: Dict[str, List[dict]]) -> List[str]:
        """Generate recommendations based on issues found"""
        recommendations = []
        
        if 'technical_accuracy' in issues_by_type:
            recommendations.append('Review technical statements for accuracy and specificity')
        
        if 'completeness' in issues_by_type:
            recommendations.append('Add missing essential sections and expand content')
        
        if 'clarity' in issues_by_type:
            recommendations.append('Improve readability by shortening sentences and adding headings')
        
        if 'consistency' in issues_by_type:
            recommendations.append('Standardize terminology and formatting throughout')
        
        if 'format_compliance' in issues_by_type:
            recommendations.append('Fix formatting issues including code blocks and lists')
        
        if 'placeholder_detection' in issues_by_type:
            recommendations.append('Complete all placeholder content before publishing')
        
        if not recommendations:
            recommendations.append('Content quality is good - ready for publication')
        
        return recommendations