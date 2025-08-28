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