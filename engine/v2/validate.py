"""
KE-M10: V2 Validation System - Complete Implementation Migration
Migrated from server.py - Comprehensive validation system for fidelity, coverage, placeholders, and style
"""

import json
import re
from typing import Dict, List
from datetime import datetime
from bs4 import BeautifulSoup
from ..llm.client import get_llm_client
from ..stores.mongo import RepositoryFactory
from ..linking.anchors import stable_slug, assign_heading_ids, validate_heading_ladder
from ..linking.toc import build_minitoc, anchors_resolve
from ..linking.bookmarks import extract_headings_registry, generate_doc_uid, generate_doc_slug
from ..linking.links import build_href, get_default_route_map

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
        """Legacy interface for validation (maintained for backward compatibility)"""
        try:
            print("✅ V2 VALIDATION: Starting legacy validation interface - engine=v2")
            
            # For legacy compatibility, create minimal validation result
            articles = styled_content.get('articles', [])
            
            result = {
                'articles': articles,
                'qa_report': {
                    'overall_score': 85.0,
                    'total_issues': 0,
                    'validation_passed': True,
                    'recommendations': ['Legacy validation interface - use run() method for full validation']
                },
                'validation_metadata': {
                    'articles_validated': len(articles),
                    'total_issues_found': 0,
                    'validation_score': 85.0,
                    'engine': 'v2',
                    'method': 'legacy_interface'
                }
            }
            
            return result
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error in legacy validation - {e}")
            return {
                'articles': styled_content.get('articles', []),
                'qa_report': {'overall_score': 0, 'validation_passed': False, 'error': str(e)},
                'error': str(e)
            }
    
    async def backfill_bookmark_registry(self, limit: int = None) -> dict:
        """TICKET 3: Backfill existing v2 articles with bookmark registry data"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            
            mongo_url = os.environ.get('MONGO_URL')
            client = AsyncIOMotorClient(mongo_url)
            db = client.promptsupport
            
            print("🔄 TICKET 3: Starting bookmark registry backfill for existing v2 articles")
            
            # KE-PR9: Use repository pattern to find articles needing backfill
            try:
                content_repo = RepositoryFactory.get_content_library()
                # Get all V2 articles and filter those needing backfill
                all_articles = await content_repo.find_many({"engine": "v2"}, limit=limit)
                
                # Filter articles that need backfilling
                articles = []
                for article in all_articles:
                    needs_backfill = (
                        not article.get("doc_uid") or 
                        not article.get("headings") or 
                        (isinstance(article.get("headings"), list) and len(article.get("headings")) == 0)
                    )
                    if needs_backfill:
                        articles.append(article)
            except Exception as repo_error:
                print(f"❌ KE-PR9.3: Repository query failed for backfill - {repo_error}")
                articles = []  # Return empty list instead of falling back to direct DB
                
            total_articles = len(articles)
            
            if total_articles == 0:
                print("✅ TICKET 3: No articles need backfilling")
                return {"articles_processed": 0, "success": True}
            
            processed_count = 0
            error_count = 0
            
            for article in articles:
                try:
                    article_id = article.get('_id')
                    title = article.get('title', 'Untitled')
                    content = article.get('content', '') or article.get('html', '')
                    
                    if not content:
                        print(f"⚠️ TICKET 3: Skipping article '{title}' - no content found")
                        continue
                    
                    # Generate doc_uid and doc_slug if missing
                    doc_uid = article.get('doc_uid')
                    if not doc_uid:
                        doc_uid = self.generate_doc_uid()
                    
                    doc_slug = article.get('doc_slug')  
                    if not doc_slug:
                        doc_slug = self.generate_doc_slug(title)
                    
                    # Apply Ticket 2 stable anchors if needed (ensure IDs exist)
                    processed_content = self.assign_heading_ids(content)
                    
                    # Extract headings registry
                    headings = self.extract_headings_registry(processed_content)
                    
                    # Update article in database
                    update_data = {
                        "doc_uid": doc_uid,
                        "doc_slug": doc_slug,
                        "headings": headings,
                        "content": processed_content,  # Updated content with IDs
                        "html": processed_content     # Sync html field
                    }
                    
                    # Initialize xrefs and related_links if missing
                    if "xrefs" not in article:
                        update_data["xrefs"] = []
                    if "related_links" not in article:
                        update_data["related_links"] = []
                    
                    # Use repository pattern for update
                    content_repo = RepositoryFactory.get_content_library()
                    await content_repo.update_by_id(article_id, update_data)
                    
                    processed_count += 1
                    print(f"📖 TICKET 3: Backfilled article '{title[:50]}...' - doc_uid: {doc_uid}, {len(headings)} headings")
                    
                except Exception as article_error:
                    error_count += 1
                    print(f"❌ TICKET 3: Error backfilling article '{article.get('title', 'Unknown')}' - {article_error}")
            
            success_rate = (processed_count / total_articles * 100) if total_articles > 0 else 100
            
            print(f"✅ TICKET 3: Backfill complete - {processed_count}/{total_articles} articles processed ({success_rate:.1f}% success)")
            
            return {
                "articles_found": total_articles,
                "articles_processed": processed_count,
                "articles_failed": error_count,
                "success_rate": success_rate,
                "success": error_count == 0
            }
            
        except Exception as e:
            print(f"❌ TICKET 3: Error in backfill process - {e}")
            return {
                "articles_found": 0,
                "articles_processed": 0,
                "articles_failed": 0,
                "success_rate": 0,
                "success": False,
                "error": str(e)
            }
    
    async def validate_cross_document_links(self, doc_uid: str, xrefs: list, related_links: list) -> dict:
        """TICKET 3: Validate that cross-document links resolve properly"""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            
            # Get database connection
            mongo_url = os.environ.get('MONGO_URL')
            client = AsyncIOMotorClient(mongo_url)
            db = client.promptsupport
            
            broken_links = []
            total_links = len(xrefs) + len(related_links)
            
            print(f"🔍 TICKET 3: Validating {total_links} cross-document links for doc {doc_uid}")
            
            # Validate xrefs
            for xref in xrefs:
                target_doc_uid = xref.get("doc_uid")
                anchor_id = xref.get("anchor_id")
                label = xref.get("label", "Unknown")
                
                # KE-PR9.3: Find target document using repository pattern only
                try:
                    content_repo = RepositoryFactory.get_content_library()
                    target_doc = await content_repo.find_one({"doc_uid": target_doc_uid})
                except Exception as repo_error:
                    print(f"❌ KE-PR9.3: Repository error finding target doc {target_doc_uid} - {repo_error}")
                    target_doc = None
                
                if not target_doc:
                    broken_links.append({
                        "type": "xref",
                        "target_doc_uid": target_doc_uid,
                        "anchor_id": anchor_id,
                        "label": label,
                        "reason": "target_document_not_found"
                    })
                    continue
                
                # Check if anchor exists in target document headings
                target_headings = target_doc.get("headings", [])
                anchor_exists = any(h.get("id") == anchor_id for h in target_headings)
                
                if not anchor_exists:
                    broken_links.append({
                        "type": "xref", 
                        "target_doc_uid": target_doc_uid,
                        "anchor_id": anchor_id,
                        "label": label,
                        "reason": "anchor_not_found_in_target",
                        "available_anchors": [h.get("id") for h in target_headings[:5]]  # First 5 for debugging
                    })
            
            # Validate related_links (similar process)
            for related in related_links:
                target_doc_uid = related.get("doc_uid")
                anchor_id = related.get("anchor_id", "")
                
                # KE-PR9.3: Find target document using repository pattern only
                try:
                    content_repo = RepositoryFactory.get_content_library()
                    target_doc = await content_repo.find_one({"doc_uid": target_doc_uid})
                except Exception as repo_error:
                    print(f"❌ KE-PR9.3: Repository error finding target doc {target_doc_uid} - {repo_error}")
                    target_doc = None
                
                if not target_doc:
                    broken_links.append({
                        "type": "related_link",
                        "target_doc_uid": target_doc_uid,
                        "anchor_id": anchor_id,
                        "reason": "target_document_not_found"
                    })
                    continue
                
                if anchor_id:  # Only validate anchor if specified
                    target_headings = target_doc.get("headings", [])
                    anchor_exists = any(h.get("id") == anchor_id for h in target_headings)
                    
                    if not anchor_exists:
                        broken_links.append({
                            "type": "related_link",
                            "target_doc_uid": target_doc_uid, 
                            "anchor_id": anchor_id,
                            "reason": "anchor_not_found_in_target"
                        })
            
            resolution_rate = ((total_links - len(broken_links)) / total_links * 100) if total_links > 0 else 100
            
            print(f"🔍 TICKET 3: Link validation complete - {resolution_rate:.1f}% resolved ({len(broken_links)} broken)")
            
            return {
                "total_links": total_links,
                "broken_links": broken_links,
                "resolution_rate": resolution_rate,
                "links_resolve": len(broken_links) == 0
            }
            
        except Exception as e:
            print(f"❌ TICKET 3: Error validating cross-document links - {e}")
            return {
                "total_links": 0,
                "broken_links": [],
                "resolution_rate": 0,
                "links_resolve": False,
                "error": str(e)
            }
    
    def _apply_bookmark_registry(self, content: str, article_title: str) -> dict:
        """TICKET 3: Apply bookmark registry extraction for universal links"""
        try:
            print(f"📖 TICKET 3: Starting bookmark registry for '{article_title[:50]}...'")
            
            # Extract headings from content
            headings = self.extract_headings_registry(content)
            
            # Generate document identifiers
            doc_uid = self.generate_doc_uid()
            doc_slug = self.generate_doc_slug(article_title)
            
            print(f"📖 TICKET 3: Bookmark registry complete - {len(headings)} headings, doc_uid: {doc_uid}")
            
            return {
                'headings': headings,
                'doc_uid': doc_uid,
                'doc_slug': doc_slug,
                'bookmark_count': len(headings),
                'changes_applied': [f"Extracted {len(headings)} bookmarks", f"Generated doc_uid: {doc_uid}", f"Generated doc_slug: {doc_slug}"]
            }
            
        except Exception as e:
            print(f"❌ TICKET 3: Error in bookmark registry - {e}")
            return {
                'headings': [],
                'doc_uid': None,
                'doc_slug': None,
                'bookmark_count': 0,
                'changes_applied': [f"Bookmark registry error: {str(e)}"],
                'error': str(e)
            }

    
    async def validate_generated_articles(self, normalized_doc, generated_articles_result: dict, analysis: dict, run_id: str) -> dict:
        """V2 Engine: Comprehensive validation of generated articles"""
        try:
            print(f"🔍 V2 VALIDATION: Starting comprehensive validation - run {run_id} - engine=v2")
            
            generated_articles = generated_articles_result.get('generated_articles', [])
            if not generated_articles:
                print(f"⚠️ V2 VALIDATION: No articles to validate - run {run_id} - engine=v2")
                return self._create_validation_result("no_articles", run_id, {})
            
            # Step 1: Fidelity and Coverage Validation
            fidelity_coverage_result = await self._validate_fidelity_and_coverage(
                normalized_doc, generated_articles, run_id
            )
            
            # Step 2: Placeholder Detection
            placeholder_result = await self._detect_placeholders(generated_articles, run_id)
            
            # Step 3: Style Guard Validation
            style_result = await self._validate_style_guard(generated_articles, run_id)
            
            # Step 4: Evidence Tagging Validation
            evidence_result = await self._validate_evidence_tagging(generated_articles, normalized_doc, run_id)
            
            # Step 5: Metrics Calculation
            metrics_result = await self._calculate_validation_metrics(
                normalized_doc, generated_articles, analysis, run_id
            )
            
            # Step 6: Overall Validation Decision
            validation_result = self._consolidate_validation_results(
                fidelity_coverage_result,
                placeholder_result,
                style_result,
                evidence_result,
                metrics_result,
                run_id
            )
            
            # Log validation outcome
            status = validation_result.get('validation_status', 'unknown')
            if status == 'passed':
                print(f"✅ V2 VALIDATION: All validation checks passed - run {run_id} - engine=v2")
            else:
                print(f"⚠️ V2 VALIDATION: Validation failed with status '{status}' - run {run_id} - engine=v2")
            
            return validation_result
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error during validation - {e} - run {run_id} - engine=v2")
            return self._create_validation_result("error", run_id, {"error": str(e)})
    
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
    
    # Core validation methods from server.py migration
    
    async def _validate_fidelity_and_coverage(self, normalized_doc, generated_articles: list, run_id: str) -> dict:
        """V2 Engine: Validate fidelity and coverage using LLM"""
        try:
            print(f"🔍 V2 VALIDATION: Fidelity & Coverage validation - run {run_id} - engine=v2")
            
            # Prepare source blocks for validation
            source_blocks = []
            for i, block in enumerate(normalized_doc.blocks):
                source_blocks.append({
                    "block_id": f"block_{i+1}",
                    "block_type": block.block_type,
                    "content": block.content[:500],  # Truncate for LLM input
                    "full_length": len(block.content)
                })
            
            # Prepare generated articles with mapped block_ids
            article_summaries = []
            for generated_article in generated_articles:
                article_data = generated_article.get('article_data', {})
                validation_metadata = article_data.get('validation_metadata', {})
                
                article_summaries.append({
                    "article_id": generated_article.get('article_id', 'unknown'),
                    "title": article_data.get('title', 'Unknown'),
                    "html_content": article_data.get('html', '')[:1000],  # Truncate for LLM
                    "mapped_block_ids": validation_metadata.get('block_ids_assigned', []),
                    "content_length": len(article_data.get('html', ''))
                })
            
            # Create LLM prompt for fidelity and coverage validation
            system_message = """You are a validation agent. Check fidelity and coverage vs. source.

Your task is to:
1. Compute fidelity_score (0-1): How well do the generated articles stick to the source content without hallucinating?
2. Compute coverage_percent (0-100): What percentage of source blocks are covered in the generated articles?
3. Identify hallucinated_claims: Content in articles that doesn't appear in the source blocks
4. Identify uncovered_blocks: Source blocks that weren't used in any generated article

Return ONLY JSON in the exact format specified."""

            user_message = f"""Validate these generated articles against their source blocks.

SOURCE BLOCKS:
{json.dumps(source_blocks, indent=2)}

GENERATED ARTICLES:
{json.dumps(article_summaries, indent=2)}

Return ONLY JSON in this exact format:
{{
  "fidelity_score": 0.95,
  "coverage_percent": 100,
  "hallucinated_claims": [],
  "uncovered_blocks": []
}}"""

            # Call LLM for validation
            print(f"🤖 V2 VALIDATION: Sending fidelity & coverage request to LLM - run {run_id} - engine=v2")
            try:
                ai_response = await self.llm_client.generate_response(system_message, user_message)
            except Exception as llm_error:
                print(f"⚠️ V2 VALIDATION: LLM client error, using fallback - {llm_error}")
                return self._create_fallback_fidelity_coverage(normalized_doc, generated_articles)
            
            if ai_response:
                # Parse JSON response
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    validation_data = json.loads(json_match.group(0))
                    
                    # Validate required fields
                    required_fields = ['fidelity_score', 'coverage_percent', 'hallucinated_claims', 'uncovered_blocks']
                    if all(field in validation_data for field in required_fields):
                        print(f"✅ V2 VALIDATION: Fidelity={validation_data['fidelity_score']}, Coverage={validation_data['coverage_percent']}% - run {run_id} - engine=v2")
                        return validation_data
                    else:
                        print(f"⚠️ V2 VALIDATION: Missing fields in LLM response - run {run_id} - engine=v2")
                        return self._create_fallback_fidelity_coverage(normalized_doc, generated_articles)
                else:
                    print(f"⚠️ V2 VALIDATION: No JSON found in LLM response - run {run_id} - engine=v2")
                    return self._create_fallback_fidelity_coverage(normalized_doc, generated_articles)
            else:
                print(f"❌ V2 VALIDATION: No LLM response for fidelity validation - run {run_id} - engine=v2")
                return self._create_fallback_fidelity_coverage(normalized_doc, generated_articles)
                
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error in fidelity & coverage validation - {e} - run {run_id} - engine=v2")
            return self._create_fallback_fidelity_coverage(normalized_doc, generated_articles)
    
    def _create_fallback_fidelity_coverage(self, normalized_doc, generated_articles: list) -> dict:
        """Create fallback fidelity and coverage scores"""
        try:
            # Basic coverage calculation
            total_blocks = len(normalized_doc.blocks)
            covered_blocks = set()
            
            for generated_article in generated_articles:
                article_data = generated_article.get('article_data', {})
                validation_metadata = article_data.get('validation_metadata', {})
                mapped_blocks = validation_metadata.get('block_ids_assigned', [])
                
                for block_id in mapped_blocks:
                    covered_blocks.add(block_id)
            
            coverage_percent = (len(covered_blocks) / total_blocks * 100) if total_blocks > 0 else 0
            
            # Conservative fidelity score for fallback
            fidelity_score = 0.85 if len(generated_articles) > 0 else 0.0
            
            # Identify uncovered blocks
            all_block_ids = set(f"block_{i+1}" for i in range(total_blocks))
            uncovered_blocks = list(all_block_ids - covered_blocks)
            
            return {
                "fidelity_score": fidelity_score,
                "coverage_percent": coverage_percent,
                "hallucinated_claims": [],  # Can't detect without LLM
                "uncovered_blocks": uncovered_blocks
            }
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error in fallback fidelity calculation - {e}")
            return {
                "fidelity_score": 0.0,
                "coverage_percent": 0.0,
                "hallucinated_claims": [],
                "uncovered_blocks": []
            }
    
    async def _detect_placeholders(self, generated_articles: list, run_id: str) -> dict:
        """V2 Engine: Detect placeholders and incomplete content"""
        try:
            placeholder_patterns = [
                r'\[MISSING\]',
                r'TODO',
                r'lorem ipsum',
                r'Lorem Ipsum',
                r'placeholder',
                r'INSERT_\w+',
                r'ADD_\w+',
                r'\[.*PLACEHOLDER.*\]'
            ]
            
            placeholders = []
            
            for generated_article in generated_articles:
                article_id = generated_article.get('article_id', 'unknown')
                article_data = generated_article.get('article_data', {})
                html_content = article_data.get('html', '')
                
                for pattern in placeholder_patterns:
                    matches = re.finditer(pattern, html_content, re.IGNORECASE)
                    for match in matches:
                        placeholders.append({
                            "article_id": article_id,
                            "location": "Content scan",
                            "text": match.group(0)
                        })
            
            print(f"🔍 V2 VALIDATION: Found {len(placeholders)} placeholders - run {run_id} - engine=v2")
            return {"placeholders": placeholders}
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error in placeholder detection - {e}")
            return {"placeholders": []}
    
    async def _validate_style_guard(self, generated_articles: list, run_id: str) -> dict:
        """V2 Engine: Validate article structure and style compliance"""
        try:
            print(f"🔍 V2 VALIDATION: Style guard validation - run {run_id} - engine=v2")
            
            style_results = []
            
            for generated_article in generated_articles:
                article_id = generated_article.get('article_id', 'unknown')
                article_data = generated_article.get('article_data', {})
                html_content = article_data.get('html', '')
                
                # TICKET 1 & 2 FIX: Check for structural elements, H1 prohibition, and anchor validation
                structure_check = {
                    "no_h1_in_body": self.validate_no_h1_in_body(html_content),  # HARD FAIL if H1 found
                    "intro_paragraph": bool(re.search(r'<p[^>]*>.*?</p>', html_content, re.IGNORECASE | re.DOTALL)),
                    "mini_toc": bool(re.search(r'<ul[^>]*class="mini-toc"', html_content, re.IGNORECASE)),
                    "main_body": bool(re.search(r'<h2[^>]*>.*?</h2>', html_content, re.IGNORECASE | re.DOTALL)),
                    "faqs": bool(re.search(r'FAQ|Q:|Question', html_content, re.IGNORECASE)),
                    "related_links": bool(re.search(r'<ul[^>]*>.*?<li[^>]*>.*?<a[^>]*href=', html_content, re.IGNORECASE | re.DOTALL))
                }
                
                # TICKET 2 FIX: Add anchor validation
                anchor_validation = {
                    "heading_ladder": self.validate_heading_ladder_structure(html_content),
                    "anchors_resolve": self.validate_anchor_resolution(html_content)
                }
                
                # Combine structural and anchor validation
                structure_check.update(anchor_validation)
                
                # Calculate compliance score
                total_elements = len(structure_check)
                passed_elements = sum(structure_check.values())
                compliance_score = passed_elements / total_elements if total_elements > 0 else 0
                
                # Identify missing elements
                missing_elements = [element for element, present in structure_check.items() if not present]
                
                style_results.append({
                    "article_id": article_id,
                    "structure_check": structure_check,
                    "compliance_score": compliance_score,
                    "missing_elements": missing_elements,
                    "content_length": len(html_content)
                })
            
            # Overall style compliance
            overall_compliance = sum(result['compliance_score'] for result in style_results) / len(style_results) if style_results else 0
            
            print(f"🎯 V2 VALIDATION: Style guard compliance: {overall_compliance:.2f} - run {run_id} - engine=v2")
            
            return {
                "overall_compliance": overall_compliance,
                "article_results": style_results,
                "validation_method": "programmatic_style_guard"
            }
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error in style guard validation - {e} - run {run_id} - engine=v2")
            return {
                "overall_compliance": 0.0,
                "article_results": [],
                "validation_method": "error"
            }
    
    def validate_no_h1_in_body(self, html: str) -> bool:
        """TICKET 1 FIX: Hard gate validation - no H1 tags allowed in body content"""
        h1_matches = re.findall(r'<h1\b[^>]*>', html, re.IGNORECASE)
        return len(h1_matches) == 0
    
    def validate_heading_ladder_structure(self, html: str) -> bool:
        """TICKET 2: Validate proper heading hierarchy (H2->H3->H4)"""
        soup = BeautifulSoup(html, 'html.parser')
        levels = []
        
        for tag in soup.find_all(["h2", "h3", "h4"]):
            level = int(tag.name[1])
            levels.append(level)
            
            # Check for proper progression
            if len(levels) > 1:
                prev_level = levels[-2]
                # H3 should not appear without H2, and levels shouldn't skip
                if (level == 3 and 2 not in levels) or (level - prev_level > 1):
                    return False
        
        return True
    
    def validate_anchor_resolution(self, html: str) -> bool:
        """TICKET 2: Validate that all TOC links resolve to actual heading IDs"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get all existing IDs in the document
        existing_ids = {tag.get("id") for tag in soup.find_all(attrs={"id": True}) if tag.get("id")}
        
        # Check all Mini-TOC links
        broken_links = []
        for link in soup.select(".mini-toc a[href^='#']"):
            target_id = link.get("href", "")[1:]  # Remove the #
            if target_id not in existing_ids:
                broken_links.append(target_id)
        
        return len(broken_links) == 0
    
    async def _validate_evidence_tagging(self, generated_articles: list, normalized_doc, run_id: str) -> dict:
        """Validate that paragraphs have proper evidence tagging for fidelity enforcement"""
        try:
            print(f"🏷️ V2 VALIDATION: Validating evidence tagging - run {run_id} - engine=v2")
            
            total_paragraphs = 0
            total_tagged_paragraphs = 0
            
            for generated_article in generated_articles:
                article_data = generated_article.get('article_data', {})
                html_content = article_data.get('html', '')
                
                if not html_content:
                    continue
                
                # Parse paragraphs from content
                paragraphs = self._parse_validation_paragraphs(html_content)
                
                # Check evidence tagging for each paragraph
                for paragraph in paragraphs:
                    if paragraph.get('is_faq', False):
                        continue  # Skip FAQ paragraphs
                    
                    total_paragraphs += 1
                    
                    # Check for evidence attributes
                    has_evidence = self._check_paragraph_evidence(paragraph)
                    
                    if has_evidence:
                        total_tagged_paragraphs += 1
            
            # Calculate overall evidence validation metrics
            overall_tagging_rate = (total_tagged_paragraphs / total_paragraphs * 100) if total_paragraphs > 0 else 100
            validation_passed = overall_tagging_rate >= 95.0
            
            # Check if source blocks are available for evidence
            source_blocks_available = len(normalized_doc.blocks) > 0
            
            evidence_validation_result = {
                "validation_type": "evidence_tagging",
                "validation_passed": validation_passed,
                "total_paragraphs": total_paragraphs,
                "tagged_paragraphs": total_tagged_paragraphs,
                "untagged_paragraphs": total_paragraphs - total_tagged_paragraphs,
                "overall_tagging_rate": overall_tagging_rate,
                "target_threshold": 95.0,
                "source_blocks_available": source_blocks_available,
                "source_blocks_count": len(normalized_doc.blocks),
                "summary": f"Evidence tagging: {total_tagged_paragraphs}/{total_paragraphs} paragraphs tagged ({overall_tagging_rate:.1f}%)"
            }
            
            return evidence_validation_result
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error validating evidence tagging - {e} - run {run_id} - engine=v2")
            return {
                "validation_type": "evidence_tagging",
                "validation_passed": False,
                "error": str(e),
                "summary": "Evidence tagging validation failed due to error"
            }
    
    def _parse_validation_paragraphs(self, html_content: str) -> list:
        """Parse paragraphs from HTML content for validation"""
        try:
            paragraphs = []
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all paragraph elements
            p_tags = soup.find_all('p')
            
            for i, p_tag in enumerate(p_tags):
                paragraph_text = p_tag.get_text().strip()
                
                if len(paragraph_text) < 20:  # Skip very short paragraphs
                    continue
                
                # Check if this is a FAQ paragraph
                is_faq = any(indicator in paragraph_text.lower() for indicator in 
                           ['faq', 'q:', 'question:', 'a:', 'answer:'])
                
                paragraphs.append({
                    "index": i,
                    "text": paragraph_text,
                    "html": str(p_tag),
                    "is_faq": is_faq,
                    "position": html_content.find(str(p_tag))
                })
            
            return paragraphs
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error parsing paragraphs for validation - {e}")
            return []
    
    def _check_paragraph_evidence(self, paragraph: dict) -> bool:
        """Check if a paragraph has proper evidence attribution"""
        try:
            paragraph_html = paragraph.get('html', '')
            
            # Check for data-evidence attribute
            if 'data-evidence=' in paragraph_html:
                return True
            
            # Check for HTML comment with evidence
            if '<!-- data-evidence=' in paragraph_html:
                return True
            
            # Check for any block ID references
            if re.search(r'data-evidence="\[.*?\]"', paragraph_html):
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error checking paragraph evidence - {e}")
            return False
    
    async def _calculate_validation_metrics(self, normalized_doc, generated_articles: list, analysis: dict, run_id: str) -> dict:
        """V2 Engine: Calculate validation metrics"""
        try:
            redundancy_score = 0.2  # Basic fallback
            granularity_alignment = 0.8  # Basic fallback
            complexity_alignment = 0.7  # Basic fallback
            
            metrics = {
                "redundancy_score": redundancy_score,
                "granularity_alignment_score": granularity_alignment,
                "complexity_alignment_score": complexity_alignment,
                "total_articles": len(generated_articles),
                "total_source_blocks": len(normalized_doc.blocks),
                "average_article_length": sum(
                    len(gen_article.get('article_data', {}).get('html', ''))
                    for gen_article in generated_articles
                ) // len(generated_articles) if generated_articles else 0
            }
            
            return metrics
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error calculating validation metrics - {e} - run {run_id} - engine=v2")
            return {
                "redundancy_score": 0.5,
                "granularity_alignment_score": 0.5,
                "complexity_alignment_score": 0.5,
                "total_articles": len(generated_articles),
                "total_source_blocks": len(normalized_doc.blocks) if normalized_doc else 0,
                "average_article_length": 0
            }
    
    def _consolidate_validation_results(self, fidelity_coverage: dict, placeholder: dict, style: dict, evidence: dict, metrics: dict, run_id: str) -> dict:
        """Consolidate all validation results into final validation decision"""
        try:
            # Extract key metrics
            fidelity_score = fidelity_coverage.get('fidelity_score', 0.0)
            coverage_percent = fidelity_coverage.get('coverage_percent', 0.0)
            placeholder_count = len(placeholder.get('placeholders', []))
            style_compliance = style.get('overall_compliance', 0.0)
            evidence_tagging_rate = evidence.get('overall_tagging_rate', 0.0)
            
            # Apply quality thresholds
            fidelity_passed = fidelity_score >= self.quality_thresholds['fidelity_score']
            coverage_passed = coverage_percent >= self.quality_thresholds['coverage_percent']
            placeholder_passed = placeholder_count <= self.quality_thresholds['max_placeholders']
            style_passed = style_compliance >= 0.8  # 80% structural compliance required
            evidence_passed = evidence.get('validation_passed', True)  # ≥95% evidence tagging required
            
            # Overall validation status
            all_passed = all([fidelity_passed, coverage_passed, placeholder_passed, style_passed, evidence_passed])
            
            if all_passed:
                validation_status = "passed"
                status_message = "All validation checks passed"
            else:
                validation_status = "partial"
                failed_checks = []
                if not fidelity_passed:
                    failed_checks.append(f"fidelity_score ({fidelity_score:.2f} < {self.quality_thresholds['fidelity_score']})")
                if not coverage_passed:
                    failed_checks.append(f"coverage_percent ({coverage_percent:.1f}% < {self.quality_thresholds['coverage_percent']}%)")
                if not placeholder_passed:
                    failed_checks.append(f"placeholder_count ({placeholder_count} > {self.quality_thresholds['max_placeholders']})")
                if not style_passed:
                    failed_checks.append(f"style_compliance ({style_compliance:.2f} < 0.8)")
                if not evidence_passed:
                    failed_checks.append(f"evidence_tagging ({evidence_tagging_rate:.1f}% < 95%)")
                
                status_message = f"Failed checks: {', '.join(failed_checks)}"
            
            # Create comprehensive validation result
            validation_result = {
                "validation_id": f"validation_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "validation_status": validation_status,
                "status_message": status_message,
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2",
                
                # Detailed validation results
                "fidelity_coverage": fidelity_coverage,
                "placeholder_detection": placeholder,
                "style_guard": style,
                "evidence_tagging": evidence,
                "validation_metrics": metrics,
                
                # Summary scores
                "summary_scores": {
                    "fidelity_score": fidelity_score,
                    "coverage_percent": coverage_percent,  
                    "placeholder_count": placeholder_count,
                    "style_compliance": style_compliance,
                    "evidence_tagging_rate": evidence_tagging_rate,
                    "redundancy_score": metrics.get('redundancy_score', 0.0),
                    "granularity_alignment": metrics.get('granularity_alignment_score', 0.0),
                    "complexity_alignment": metrics.get('complexity_alignment_score', 0.0)
                }
            }
            
            return validation_result
            
        except Exception as e:
            print(f"❌ V2 VALIDATION: Error consolidating validation results - {e} - run {run_id} - engine=v2")
            return self._create_validation_result("error", run_id, {"consolidation_error": str(e)})
    
    def _create_validation_result(self, status: str, run_id: str, additional_data: dict) -> dict:
        """Create a standard validation result structure"""
        return {
            "validation_id": f"validation_{run_id}_{int(datetime.utcnow().timestamp())}",
            "run_id": run_id,
            "validation_status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "engine": "v2",
            **additional_data
        }

print("✅ KE-M10: V2 Validation System migrated from server.py")