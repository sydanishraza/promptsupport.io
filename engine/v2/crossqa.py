"""
KE-M11: V2 Cross-Article QA System - Complete Implementation Migration
Migrated from server.py - Cross-article quality assurance for coherence, deduplication, and consistency
"""

import json
import re
from typing import Dict, List
from datetime import datetime
from bs4 import BeautifulSoup
from ..llm.client import get_llm_client

class V2CrossArticleQASystem:
    """V2 Engine: Cross-article quality assurance for coherence, deduplication, and consistency"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.duplicate_threshold = 0.8  # Similarity threshold for duplicate detection
        self.terminology_patterns = [
            # Common API terminology variations
            {"standard": "API key", "variations": ["Api key", "APIKey", "api key", "API-key", "api_key"]},
            {"standard": "API endpoint", "variations": ["Api endpoint", "APIEndpoint", "api endpoint", "API-endpoint", "api_endpoint"]},
            {"standard": "HTTP request", "variations": ["Http request", "HTTPRequest", "http request", "HTTP-request", "http_request"]},
            {"standard": "JSON response", "variations": ["Json response", "JSONResponse", "json response", "JSON-response", "json_response"]},
            {"standard": "OAuth token", "variations": ["Oauth token", "OAuthToken", "oauth token", "OAuth-token", "oauth_token"]},
            # Add more patterns as needed
        ]
    
    async def run(self, content: dict, **kwargs) -> dict:
        """Run cross-article QA using centralized LLM client (new interface)"""
        try:
            print("🔍 V2 CROSS-ARTICLE QA: Starting QA process - engine=v2")
            
            # Extract parameters from kwargs
            generated_articles_result = kwargs.get('generated_articles_result', {})
            run_id = kwargs.get('run_id', 'unknown')
            
            # Call the original perform_cross_article_qa method
            result = await self.perform_cross_article_qa(generated_articles_result, run_id)
            
            return result
            
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error in run method - {e}")
            return {
                "qa_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    async def perform_cross_article_qa(self, generated_articles_result: dict, run_id: str) -> dict:
        """V2 Engine: Perform comprehensive cross-article quality assurance"""
        try:
            print(f"🔍 V2 CROSS-ARTICLE QA: Starting comprehensive QA analysis - run {run_id} - engine=v2")
            
            generated_articles = generated_articles_result.get('generated_articles', [])
            if len(generated_articles) < 2:
                print(f"⚠️ V2 CROSS-ARTICLE QA: Less than 2 articles, skipping cross-article analysis - run {run_id} - engine=v2")
                return self._create_qa_result("insufficient_articles", run_id, {"article_count": len(generated_articles)})
            
            # Prepare article set for analysis
            article_set = self._prepare_article_set(generated_articles)
            
            # Step 1: LLM-based cross-article analysis
            llm_qa_result = await self._perform_llm_cross_article_analysis(article_set, run_id)
            
            # Step 2: Programmatic validation and enhancement
            programmatic_qa_result = await self._perform_programmatic_qa_analysis(article_set, run_id)
            
            # Step 3: Consolidate findings
            consolidated_qa_result = self._consolidate_qa_findings(llm_qa_result, programmatic_qa_result, run_id)
            
            # Step 4: Perform consolidation pass
            consolidation_result = await self._perform_consolidation_pass(
                generated_articles, consolidated_qa_result, run_id
            )
            
            # Step 5: Create final QA result
            final_qa_result = {
                **consolidated_qa_result,
                "consolidation_result": consolidation_result,
                "qa_id": f"qa_{run_id}_{int(datetime.utcnow().timestamp())}",
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
            
            print(f"✅ V2 CROSS-ARTICLE QA: Analysis complete - Found {len(consolidated_qa_result.get('duplicates', []))} duplicates, {len(consolidated_qa_result.get('invalid_related_links', []))} invalid links - run {run_id} - engine=v2")
            return final_qa_result
            
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error in cross-article QA - {e} - run {run_id} - engine=v2")
            return self._create_qa_result("error", run_id, {"error": str(e)})
    
    def _prepare_article_set(self, generated_articles: list) -> dict:
        """Prepare article set for cross-article analysis"""
        try:
            article_set = {
                "articles": [],
                "total_count": len(generated_articles)
            }
            
            for generated_article in generated_articles:
                article_id = generated_article.get('article_id', 'unknown')
                article_data = generated_article.get('article_data', {})
                html_content = article_data.get('html', '')
                
                # Extract structured data from HTML
                structured_article = self._extract_structured_data(article_id, html_content)
                article_set["articles"].append(structured_article)
            
            return article_set
            
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error preparing article set - {e}")
            return {"articles": [], "total_count": 0}
    
    def _extract_structured_data(self, article_id: str, html_content: str) -> dict:
        """Extract structured data from HTML content"""
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1')
            title = title_tag.get_text().strip() if title_tag else "Untitled"
            
            # Extract sections
            sections = []
            section_tags = soup.find_all(['h2', 'h3'])
            for tag in section_tags:
                sections.append({
                    "level": tag.name,
                    "heading": tag.get_text().strip(),
                    "id": tag.get('id', ''),
                    "content": self._get_section_content(tag)
                })
            
            # Extract FAQs
            faqs = []
            faq_patterns = [
                r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)',
                r'<h3[^>]*>Q:\s*(.*?)</h3>\s*<p[^>]*>A:\s*(.*?)</p>',
                r'Question:\s*(.*?)\s*Answer:\s*(.*?)(?=Question:|$)'
            ]
            
            for pattern in faq_patterns:
                matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    faqs.append({
                        "question": match.group(1).strip(),
                        "answer": match.group(2).strip()
                    })
            
            # Extract related links
            related_links = []
            link_tags = soup.find_all('a', href=True)
            for link in link_tags:
                href = link.get('href', '')
                if href.startswith('#') or href.startswith('/') or href.startswith('http'):
                    related_links.append({
                        "label": link.get_text().strip(),
                        "url": href,
                        "is_internal": href.startswith('#') or href.startswith('/')
                    })
            
            return {
                "article_id": article_id,
                "title": title,
                "sections": sections,
                "faqs": faqs,
                "related_links": related_links,
                "content_length": len(html_content),
                "html_content": html_content[:1000]  # Truncated for analysis
            }
            
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error extracting structured data from {article_id} - {e}")
            return {
                "article_id": article_id,
                "title": "Error",
                "sections": [],
                "faqs": [],
                "related_links": [],
                "content_length": 0,
                "html_content": ""
            }
    
    def _get_section_content(self, heading_tag) -> str:
        """Get content under a heading tag"""
        try:
            content_parts = []
            next_element = heading_tag.next_sibling
            
            while next_element:
                if hasattr(next_element, 'name'):
                    if next_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    content_parts.append(str(next_element))
                next_element = next_element.next_sibling
            
            return ' '.join(content_parts)[:500]  # Truncate for analysis
            
        except Exception as e:
            return f"Error extracting content: {str(e)}"
    
    async def _perform_llm_cross_article_analysis(self, article_set: dict, run_id: str) -> dict:
        """V2 Engine: LLM-based cross-article analysis"""
        try:
            print(f"🤖 V2 CROSS-ARTICLE QA: Starting LLM cross-article analysis - run {run_id} - engine=v2")
            
            # Create system message
            system_message = """You are a documentation reviewer ensuring coherence across articles.

Your task is to analyze a set of articles and identify:
1. Duplicates: Repeated content (intros/sections) across articles
2. Invalid related links: Links that don't point to existing articles/sections
3. Duplicate FAQs: Same questions appearing across multiple articles
4. Terminology issues: Inconsistent usage of terms across articles

Be thorough but precise. Focus on actual duplicates and issues, not minor variations.

Return ONLY JSON in the exact format specified."""

            # Create user message with article set
            user_message = f"""Identify duplicates, invalid related links, duplicate FAQs, and terminology issues. Return JSON.

ARTICLE SET:
{json.dumps(article_set, indent=2)}

Analyze these articles and return ONLY JSON in this exact format:
{{
  "duplicates": [
    {{
      "article_id": "a1",
      "other_article_id": "a2", 
      "section": "Intro",
      "similarity_score": 0.95,
      "duplicate_type": "identical_content"
    }}
  ],
  "invalid_related_links": [
    {{
      "article_id": "a3",
      "label": "Nonexistent Link",
      "url": "/kb/missing",
      "issue": "target_not_found"
    }}
  ],
  "duplicate_faqs": [
    {{
      "question": "How to install X?",
      "article_ids": ["a1", "a2"],
      "identical_answer": true
    }}
  ],
  "terminology_issues": [
    {{
      "term": "API key",
      "inconsistent_usages": ["Api key", "APIKey", "api_key"],
      "suggested_standard": "API key",
      "article_ids": ["a1", "a2", "a3"]
    }}
  ]
}}"""

            # Call LLM for analysis
            print(f"🤖 V2 CROSS-ARTICLE QA: Sending cross-article analysis request to LLM - run {run_id} - engine=v2")
            try:
                ai_response = await self.llm_client.generate_response(system_message, user_message)
            except Exception as llm_error:
                print(f"⚠️ V2 CROSS-ARTICLE QA: LLM client error, using fallback - {llm_error}")
                return self._create_fallback_qa_analysis(article_set)
            
            if ai_response:
                # Parse JSON response
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    qa_data = json.loads(json_match.group(0))
                    
                    # Validate required fields
                    required_fields = ['duplicates', 'invalid_related_links', 'duplicate_faqs', 'terminology_issues']
                    if all(field in qa_data for field in required_fields):
                        duplicates_count = len(qa_data.get('duplicates', []))
                        invalid_links_count = len(qa_data.get('invalid_related_links', []))
                        duplicate_faqs_count = len(qa_data.get('duplicate_faqs', []))
                        terminology_issues_count = len(qa_data.get('terminology_issues', []))
                        
                        print(f"🔍 V2 CROSS-ARTICLE QA: LLM found {duplicates_count} duplicates, {invalid_links_count} invalid links, {duplicate_faqs_count} duplicate FAQs, {terminology_issues_count} terminology issues - run {run_id} - engine=v2")
                        return qa_data
                    else:
                        print(f"⚠️ V2 CROSS-ARTICLE QA: Missing fields in LLM response - run {run_id} - engine=v2")
                        return self._create_fallback_qa_analysis(article_set)
                else:
                    print(f"⚠️ V2 CROSS-ARTICLE QA: No JSON found in LLM response - run {run_id} - engine=v2")
                    return self._create_fallback_qa_analysis(article_set)
            else:
                print(f"❌ V2 CROSS-ARTICLE QA: No LLM response for cross-article analysis - run {run_id} - engine=v2")
                return self._create_fallback_qa_analysis(article_set)
                
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error in LLM cross-article analysis - {e} - run {run_id} - engine=v2")
            return self._create_fallback_qa_analysis(article_set)
    
    def _create_fallback_qa_analysis(self, article_set: dict) -> dict:
        """Create fallback QA analysis using programmatic methods"""
        try:
            articles = article_set.get('articles', [])
            
            # Basic duplicate detection
            duplicates = []
            for i, article_a in enumerate(articles):
                for j, article_b in enumerate(articles[i+1:], i+1):
                    # Check title similarity
                    title_a = article_a.get('title', '').lower()
                    title_b = article_b.get('title', '').lower()
                    
                    if title_a and title_b and self._calculate_similarity(title_a, title_b) > self.duplicate_threshold:
                        duplicates.append({
                            "article_id": article_a.get('article_id'),
                            "other_article_id": article_b.get('article_id'),
                            "section": "title",
                            "similarity_score": self._calculate_similarity(title_a, title_b),
                            "duplicate_type": "similar_title"
                        })
            
            # Basic FAQ duplicate detection
            duplicate_faqs = []
            faq_questions = {}
            
            for article in articles:
                article_id = article.get('article_id')
                faqs = article.get('faqs', [])
                
                for faq in faqs:
                    question = faq.get('question', '').lower().strip()
                    if question:
                        if question in faq_questions:
                            faq_questions[question].append(article_id)
                        else:
                            faq_questions[question] = [article_id]
            
            for question, article_ids in faq_questions.items():
                if len(article_ids) > 1:
                    duplicate_faqs.append({
                        "question": question,
                        "article_ids": article_ids,
                        "identical_answer": False  # Can't determine without deeper analysis
                    })
            
            # Basic terminology detection
            terminology_issues = []
            for pattern in self.terminology_patterns:
                standard = pattern["standard"]
                variations = pattern["variations"]
                found_variations = []
                found_in_articles = []
                
                for article in articles:
                    html_content = article.get('html_content', '').lower()
                    for variation in variations:
                        if variation.lower() in html_content:
                            if variation not in found_variations:
                                found_variations.append(variation)
                            if article.get('article_id') not in found_in_articles:
                                found_in_articles.append(article.get('article_id'))
                
                if len(found_variations) > 1:
                    terminology_issues.append({
                        "term": standard,
                        "inconsistent_usages": found_variations,
                        "suggested_standard": standard,
                        "article_ids": found_in_articles
                    })
            
            print(f"🔧 V2 CROSS-ARTICLE QA: Fallback analysis found {len(duplicates)} duplicates, {len(duplicate_faqs)} duplicate FAQs, {len(terminology_issues)} terminology issues")
            
            return {
                "duplicates": duplicates,
                "invalid_related_links": [],  # Requires URL resolution
                "duplicate_faqs": duplicate_faqs,
                "terminology_issues": terminology_issues,
                "analysis_method": "fallback_programmatic"
            }
            
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error in fallback QA analysis - {e}")
            return {
                "duplicates": [],
                "invalid_related_links": [],
                "duplicate_faqs": [],
                "terminology_issues": [],
                "analysis_method": "error"
            }
    
    def _calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate text similarity using simple word overlap"""
        try:
            words_a = set(text_a.lower().split())
            words_b = set(text_b.lower().split())
            
            if not words_a or not words_b:
                return 0.0
            
            intersection = len(words_a & words_b)
            union = len(words_a | words_b)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            return 0.0
    
    async def _perform_programmatic_qa_analysis(self, article_set: dict, run_id: str) -> dict:
        """V2 Engine: Programmatic QA analysis for validation"""
        try:
            print(f"🔍 V2 CROSS-ARTICLE QA: Performing programmatic QA validation - run {run_id} - engine=v2")
            
            articles = article_set.get('articles', [])
            
            # Validate related links
            invalid_related_links = []
            existing_article_ids = set(article.get('article_id', '') for article in articles)
            existing_sections = set()
            
            # Build section index
            for article in articles:
                article_id = article.get('article_id', '')
                sections = article.get('sections', [])
                for section in sections:
                    section_id = section.get('id', '')
                    if section_id:
                        existing_sections.add(f"#{section_id}")
                        existing_sections.add(f"{article_id}#{section_id}")
            
            # Check related links validity
            for article in articles:
                article_id = article.get('article_id', '')
                related_links = article.get('related_links', [])
                
                for link in related_links:
                    url = link.get('url', '')
                    label = link.get('label', '')
                    is_internal = link.get('is_internal', False)
                    
                    if is_internal:
                        # Check if internal link exists
                        if url.startswith('#'):
                            if url not in existing_sections:
                                invalid_related_links.append({
                                    "article_id": article_id,
                                    "label": label,
                                    "url": url,
                                    "issue": "section_anchor_not_found"
                                })
                        elif url.startswith('/'):
                            # Check if it's a reference to another article
                            if not any(article_ref in url for article_ref in existing_article_ids):
                                invalid_related_links.append({
                                    "article_id": article_id,
                                    "label": label,
                                    "url": url,
                                    "issue": "internal_article_not_found"
                                })
            
            # Additional consistency checks
            title_consistency = self._check_title_consistency(articles)
            section_consistency = self._check_section_consistency(articles)
            
            programmatic_result = {
                "invalid_related_links_validated": invalid_related_links,
                "title_consistency": title_consistency,
                "section_consistency": section_consistency,
                "analysis_method": "programmatic_validation"
            }
            
            print(f"🔍 V2 CROSS-ARTICLE QA: Programmatic validation found {len(invalid_related_links)} invalid links - run {run_id} - engine=v2")
            return programmatic_result
            
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error in programmatic QA analysis - {e} - run {run_id} - engine=v2")
            return {
                "invalid_related_links_validated": [],
                "title_consistency": {"consistent": True, "issues": []},
                "section_consistency": {"consistent": True, "issues": []},
                "analysis_method": "error"
            }
    
    def _check_title_consistency(self, articles: list) -> dict:
        """Check title formatting consistency"""
        try:
            title_patterns = []
            for article in articles:
                title = article.get('title', '')
                if title:
                    pattern = {
                        "has_numbers": any(char.isdigit() for char in title),
                        "has_colons": ':' in title,
                        "has_dashes": '-' in title,
                        "title_case": title.istitle(),
                        "length": len(title)
                    }
                    title_patterns.append(pattern)
            
            # Analyze consistency
            if not title_patterns:
                return {"consistent": True, "issues": []}
            
            consistency_issues = []
            title_case_count = sum(1 for p in title_patterns if p['title_case'])
            if 0 < title_case_count < len(title_patterns):
                consistency_issues.append("Inconsistent title case formatting")
            
            return {
                "consistent": len(consistency_issues) == 0,
                "issues": consistency_issues,
                "title_patterns": title_patterns
            }
            
        except Exception as e:
            return {
                "consistent": False,
                "issues": [f"Error checking title consistency: {str(e)}"]
            }
    
    def _check_section_consistency(self, articles: list) -> dict:
        """Check section heading consistency"""
        try:
            section_patterns = []
            all_headings = []
            
            for article in articles:
                sections = article.get('sections', [])
                for section in sections:
                    heading = section.get('heading', '')
                    if heading:
                        all_headings.append(heading)
                        pattern = {
                            "level": section.get('level', 'h2'),
                            "has_numbers": any(char.isdigit() for char in heading),
                            "title_case": heading.istitle(),
                            "length": len(heading)
                        }
                        section_patterns.append(pattern)
            
            # Check for consistency issues
            consistency_issues = []
            if len(all_headings) > 1:
                title_case_count = sum(1 for p in section_patterns if p['title_case'])
                if 0 < title_case_count < len(section_patterns):
                    consistency_issues.append("Inconsistent section heading case")
            
            return {
                "consistent": len(consistency_issues) == 0,
                "issues": consistency_issues,
                "total_sections": len(section_patterns)
            }
            
        except Exception as e:
            return {
                "consistent": False,
                "issues": [f"Error checking section consistency: {str(e)}"]
            }
    
    def _consolidate_qa_findings(self, llm_result: dict, programmatic_result: dict, run_id: str) -> dict:
        """Consolidate LLM and programmatic QA findings"""
        try:
            # Merge LLM and programmatic results
            consolidated = {
                "duplicates": llm_result.get('duplicates', []),
                "invalid_related_links": llm_result.get('invalid_related_links', []),
                "duplicate_faqs": llm_result.get('duplicate_faqs', []),
                "terminology_issues": llm_result.get('terminology_issues', []),
                "run_id": run_id,
                "analysis_methods": []
            }
            
            # Add programmatic validation for invalid links
            programmatic_invalid_links = programmatic_result.get('invalid_related_links_validated', [])
            for link in programmatic_invalid_links:
                # Check if not already found by LLM
                if not any(existing_link.get('url') == link.get('url') 
                         for existing_link in consolidated['invalid_related_links']):
                    consolidated['invalid_related_links'].append(link)
            
            # Add analysis methods used
            if llm_result.get('analysis_method') != 'error':
                consolidated['analysis_methods'].append('llm_analysis')
            if programmatic_result.get('analysis_method') != 'error':
                consolidated['analysis_methods'].append('programmatic_validation')
            
            # Add additional findings
            consolidated['title_consistency'] = programmatic_result.get('title_consistency', {})
            consolidated['section_consistency'] = programmatic_result.get('section_consistency', {})
            
            # Summary statistics
            consolidated['summary'] = {
                "total_duplicates": len(consolidated['duplicates']),
                "total_invalid_links": len(consolidated['invalid_related_links']),
                "total_duplicate_faqs": len(consolidated['duplicate_faqs']),
                "total_terminology_issues": len(consolidated['terminology_issues']),
                "issues_found": (
                    len(consolidated['duplicates']) + 
                    len(consolidated['invalid_related_links']) + 
                    len(consolidated['duplicate_faqs']) + 
                    len(consolidated['terminology_issues'])
                )
            }
            
            print(f"🔍 V2 CROSS-ARTICLE QA: Consolidated findings - {consolidated['summary']['issues_found']} total issues - run {run_id} - engine=v2")
            return consolidated
            
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error consolidating QA findings - {e} - run {run_id} - engine=v2")
            return {
                "duplicates": [],
                "invalid_related_links": [],
                "duplicate_faqs": [],
                "terminology_issues": [],
                "summary": {"issues_found": 0}
            }
    
    async def _perform_consolidation_pass(self, generated_articles: list, qa_findings: dict, run_id: str) -> dict:
        """V2 Engine: Perform consolidation pass to resolve QA issues"""
        try:
            print(f"🔧 V2 CROSS-ARTICLE QA: Starting consolidation pass - run {run_id} - engine=v2")
            
            consolidation_actions = []
            
            # Handle duplicates
            duplicates = qa_findings.get('duplicates', [])
            for duplicate in duplicates:
                action = await self._handle_duplicate_content(generated_articles, duplicate, run_id)
                consolidation_actions.append(action)
            
            # Handle invalid related links
            invalid_links = qa_findings.get('invalid_related_links', [])
            for invalid_link in invalid_links:
                action = await self._handle_invalid_related_link(generated_articles, invalid_link, run_id)
                consolidation_actions.append(action)
            
            # Handle duplicate FAQs
            duplicate_faqs = qa_findings.get('duplicate_faqs', [])
            for duplicate_faq in duplicate_faqs:
                action = await self._handle_duplicate_faq(generated_articles, duplicate_faq, run_id)
                consolidation_actions.append(action)
            
            # Handle terminology issues
            terminology_issues = qa_findings.get('terminology_issues', [])
            for terminology_issue in terminology_issues:
                action = await self._handle_terminology_issue(generated_articles, terminology_issue, run_id)
                consolidation_actions.append(action)
            
            consolidation_result = {
                "actions_taken": consolidation_actions,
                "total_actions": len(consolidation_actions),
                "successful_actions": len([a for a in consolidation_actions if a.get('status') == 'success']),
                "failed_actions": len([a for a in consolidation_actions if a.get('status') == 'failed']),
                "consolidation_method": "automated_pass"
            }
            
            print(f"🔧 V2 CROSS-ARTICLE QA: Consolidation complete - {consolidation_result['successful_actions']}/{consolidation_result['total_actions']} successful actions - run {run_id} - engine=v2")
            return consolidation_result
            
        except Exception as e:
            print(f"❌ V2 CROSS-ARTICLE QA: Error in consolidation pass - {e} - run {run_id} - engine=v2")
            return {
                "actions_taken": [],
                "total_actions": 0,
                "successful_actions": 0,
                "failed_actions": 0,
                "consolidation_method": "error"
            }
    
    async def _handle_duplicate_content(self, generated_articles: list, duplicate: dict, run_id: str) -> dict:
        """Handle duplicate content between articles"""
        try:
            article_id = duplicate.get('article_id')
            other_article_id = duplicate.get('other_article_id')
            section = duplicate.get('section', 'unknown')
            
            # For now, just record the action (full implementation would modify articles)
            action = {
                "type": "duplicate_content",
                "article_id": article_id,
                "other_article_id": other_article_id,
                "section": section,
                "action": "recorded_for_manual_review",
                "status": "success",
                "details": f"Duplicate {section} content identified between {article_id} and {other_article_id}"
            }
            
            print(f"📝 V2 CROSS-ARTICLE QA: Recorded duplicate content - {article_id} <-> {other_article_id} - run {run_id} - engine=v2")
            return action
            
        except Exception as e:
            return {
                "type": "duplicate_content",
                "action": "error",
                "status": "failed",
                "error": str(e)
            }
    
    async def _handle_invalid_related_link(self, generated_articles: list, invalid_link: dict, run_id: str) -> dict:
        """Handle invalid related links"""
        try:
            article_id = invalid_link.get('article_id')
            url = invalid_link.get('url')
            label = invalid_link.get('label')
            
            # Find the article and attempt to fix the link
            for generated_article in generated_articles:
                if generated_article.get('article_id') == article_id:
                    article_data = generated_article.get('article_data', {})
                    html_content = article_data.get('html', '')
                    
                    # Simple approach: remove the invalid link or mark it for review
                    # In a full implementation, this would intelligently fix or replace links
                    if url in html_content:
                        # Mark for manual review rather than auto-remove
                        action = {
                            "type": "invalid_related_link",
                            "article_id": article_id,
                            "url": url,
                            "label": label,
                            "action": "marked_for_manual_review",
                            "status": "success",
                            "details": f"Invalid link '{label}' -> '{url}' marked for review"
                        }
                        
                        print(f"🔗 V2 CROSS-ARTICLE QA: Marked invalid link for review - {article_id}: {url} - run {run_id} - engine=v2")
                        return action
            
            return {
                "type": "invalid_related_link",
                "article_id": article_id,
                "action": "article_not_found",
                "status": "failed"
            }
            
        except Exception as e:
            return {
                "type": "invalid_related_link",
                "action": "error", 
                "status": "failed",
                "error": str(e)
            }
    
    async def _handle_duplicate_faq(self, generated_articles: list, duplicate_faq: dict, run_id: str) -> dict:
        """Handle duplicate FAQ across articles"""
        try:
            question = duplicate_faq.get('question')
            article_ids = duplicate_faq.get('article_ids', [])
            
            # For now, record the duplication for potential consolidation
            action = {
                "type": "duplicate_faq",
                "question": question,
                "article_ids": article_ids,
                "action": "recorded_for_consolidation",
                "status": "success",
                "details": f"Duplicate FAQ '{question}' found in {len(article_ids)} articles",
                "consolidation_recommendation": "Consider creating a centralized FAQ section"
            }
            
            print(f"❓ V2 CROSS-ARTICLE QA: Recorded duplicate FAQ - '{question}' in {len(article_ids)} articles - run {run_id} - engine=v2")
            return action
            
        except Exception as e:
            return {
                "type": "duplicate_faq",
                "action": "error",
                "status": "failed", 
                "error": str(e)
            }
    
    async def _handle_terminology_issue(self, generated_articles: list, terminology_issue: dict, run_id: str) -> dict:
        """Handle terminology consistency issues"""
        try:
            term = terminology_issue.get('term')
            inconsistent_usages = terminology_issue.get('inconsistent_usages', [])
            suggested_standard = terminology_issue.get('suggested_standard')
            article_ids = terminology_issue.get('article_ids', [])
            
            # Record terminology standardization action
            action = {
                "type": "terminology_issue",
                "term": term,
                "inconsistent_usages": inconsistent_usages,
                "suggested_standard": suggested_standard,
                "article_ids": article_ids,
                "action": "recorded_for_standardization",
                "status": "success",
                "details": f"Terminology '{term}' has {len(inconsistent_usages)} variations across {len(article_ids)} articles",
                "standardization_recommendation": f"Standardize all variations to '{suggested_standard}'"
            }
            
            print(f"📝 V2 CROSS-ARTICLE QA: Recorded terminology issue - '{term}' needs standardization - run {run_id} - engine=v2")
            return action
            
        except Exception as e:
            return {
                "type": "terminology_issue",
                "action": "error",
                "status": "failed",
                "error": str(e)
            }
    
    def _create_qa_result(self, status: str, run_id: str, additional_data: dict) -> dict:
        """Create a standard QA result structure"""
        return {
            "qa_id": f"qa_{run_id}_{int(datetime.utcnow().timestamp())}",
            "run_id": run_id,
            "qa_status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "engine": "v2",
            **additional_data
        }

print("✅ KE-M11: V2 Cross-Article QA System migrated from server.py")