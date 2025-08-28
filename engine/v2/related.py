"""
KE-M5: V2 Related Links System - Complete Implementation Migration
Migrated from server.py - Enhanced related links with content library indexing
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..llm.client import get_llm_client
from ._utils import create_processing_metadata
import re

class V2RelatedLinksSystem:
    """V2 Engine: Enhanced related links system with content library indexing and similarity matching"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or get_llm_client()
        self.content_index = {}  # Cache for content library index
        self.index_last_updated = None
    
    async def run(self, styled_content: dict, **kwargs) -> dict:
        """Run related links generation for styled content (new interface)"""
        try:
            print(f"🔗 V2 RELATED LINKS: Processing styled content - engine=v2")
            
            articles = styled_content.get('articles', [])
            processed_articles = []
            
            for article in articles:
                # Generate related links for each article
                related_result = await self.generate_related_links(
                    article=article,
                    source_content=article.get('content', ''),
                    source_blocks=[],  # Will be extracted from content
                    run_id=kwargs.get('run_id', 'unknown')
                )
                
                # Add related links to article
                processed_article = article.copy()
                processed_article['related_links'] = related_result.get('related_links', [])
                processed_article['related_links_metadata'] = {
                    'total_links': related_result.get('total_links_count', 0),
                    'internal_links': related_result.get('internal_links_count', 0),
                    'external_links': related_result.get('external_links_count', 0),
                    'generation_status': related_result.get('related_links_status', 'unknown')
                }
                
                processed_articles.append(processed_article)
            
            return {
                'articles': processed_articles,
                'related_links_metadata': create_processing_metadata('related_links',
                    articles_processed=len(processed_articles),
                    total_links_generated=sum(a.get('related_links_metadata', {}).get('total_links', 0) for a in processed_articles)
                )
            }
            
        except Exception as e:
            print(f"❌ V2 RELATED LINKS: Error processing content - {e}")
            return {
                'articles': styled_content.get('articles', []),
                'error': str(e)
            }
    
    async def generate_related_links(self, article: dict, source_content: str, 
                                   source_blocks: list, run_id: str) -> dict:
        """Generate comprehensive related links for an article (legacy interface)"""
        try:
            article_title = article.get('title', 'Untitled')
            print(f"🔗 V2 RELATED LINKS: Generating related links for '{article_title}' - engine=v2")
            
            # Step 1: Build/update content library index
            await self._update_content_index()
            
            # Step 2: Find related internal articles
            internal_links = await self._find_internal_related_articles(article)
            
            # Step 3: Extract external links from source content and blocks
            external_links = await self._extract_source_external_links(source_content, source_blocks)
            
            # Step 4: Merge and format final related links
            final_related_links = self._merge_and_format_links(internal_links, external_links)
            
            related_links_count = len(final_related_links)
            internal_count = len([l for l in final_related_links if l.get('type') == 'internal'])
            external_count = len([l for l in final_related_links if l.get('type') == 'external'])
            
            print(f"✅ V2 RELATED LINKS: Generated {related_links_count} links ({internal_count} internal, {external_count} external) for '{article_title}' - engine=v2")
            
            return {
                "related_links_id": f"related_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "article_title": article_title,
                "related_links_status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2",
                
                # Related links data
                "related_links": final_related_links,
                "internal_links_count": internal_count,
                "external_links_count": external_count,
                "total_links_count": related_links_count,
                
                # Metadata
                "content_library_articles_indexed": len(self.content_index),
                "similarity_method": "keyword_and_semantic"
            }
            
        except Exception as e:
            print(f"❌ V2 RELATED LINKS: Error generating related links - {e} - engine=v2")
            return {
                "related_links_id": f"related_error_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "related_links_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    async def _update_content_index(self):
        """Build/update lightweight vector/keyword index over content_library"""
        try:
            # Check if index needs updating (update every 5 minutes)
            now = datetime.utcnow()
            if (self.index_last_updated and 
                (now - self.index_last_updated).total_seconds() < 300):
                return  # Index is still fresh
            
            print(f"🔍 V2 RELATED LINKS: Updating content library index - engine=v2")
            
            new_index = {}
            
            # Try to use repository pattern first
            try:
                from ..stores.mongo import RepositoryFactory
                content_repo = RepositoryFactory.get_content_library()
                articles = await content_repo.find_all_articles(limit=100)
            except Exception:
                # Fallback to direct database access
                from ..stores.mongo import RepositoryFactory
                
                # Use repository pattern instead of direct database access
                content_repo = RepositoryFactory.get_content_library()
                articles = await content_repo.find_recent(limit=100)
            
            # Index articles by keywords and metadata
            for article in articles:
                article_id = str(article.get('_id', article.get('id', 'unknown')))
                title = article.get('title', '')
                content = article.get('content', '')
                
                # Extract keywords
                keywords = self._extract_keywords(title + ' ' + content)
                
                new_index[article_id] = {
                    'title': title,
                    'keywords': keywords,
                    'content_preview': content[:200],
                    'doc_uid': article.get('doc_uid'),
                    'doc_slug': article.get('doc_slug'),
                    'created_at': article.get('created_at'),
                    'engine': article.get('engine', 'unknown')
                }
            
            self.content_index = new_index
            self.index_last_updated = now
            
            print(f"✅ V2 RELATED LINKS: Indexed {len(new_index)} articles - engine=v2")
            
        except Exception as e:
            print(f"❌ V2 RELATED LINKS: Error updating content index - {e}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for similarity matching"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter common words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
            'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy',
            'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'
        }
        
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return top keywords by frequency
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(20)]
    
    async def _find_internal_related_articles(self, article: dict) -> List[dict]:
        """Find related articles from content library"""
        try:
            article_title = article.get('title', '')
            article_content = article.get('content', '')
            article_keywords = self._extract_keywords(article_title + ' ' + article_content)
            
            related_articles = []
            
            # Find articles with similar keywords
            for indexed_id, indexed_article in self.content_index.items():
                similarity_score = self._calculate_similarity(article_keywords, indexed_article['keywords'])
                
                if similarity_score > 0.1:  # Minimum similarity threshold
                    doc_uid = indexed_article.get('doc_uid')
                    doc_slug = indexed_article.get('doc_slug')
                    
                    # Build link URL based on available identifiers
                    if doc_uid:
                        link_url = f"/article/{doc_uid}"
                    elif doc_slug:
                        link_url = f"/article/{doc_slug}"
                    else:
                        link_url = f"/article/{indexed_id}"
                    
                    related_articles.append({
                        'type': 'internal',
                        'title': indexed_article['title'],
                        'url': link_url,
                        'doc_uid': doc_uid,
                        'doc_slug': doc_slug,
                        'similarity_score': similarity_score,
                        'preview': indexed_article['content_preview'],
                        'engine': indexed_article['engine']
                    })
            
            # Sort by similarity and return top matches
            related_articles.sort(key=lambda x: x['similarity_score'], reverse=True)
            return related_articles[:5]  # Top 5 related articles
            
        except Exception as e:
            print(f"❌ V2 RELATED LINKS: Error finding internal articles - {e}")
            return []
    
    def _calculate_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Calculate similarity between two keyword lists"""
        if not keywords1 or not keywords2:
            return 0.0
        
        # Simple Jaccard similarity
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _extract_source_external_links(self, source_content: str, source_blocks: list) -> List[dict]:
        """Extract external links from source content and blocks"""
        try:
            external_links = []
            
            # Extract links from content using regex
            url_pattern = r'https?://[^\s<>"\'(){}[\]]+[^\s<>"\'(){}[\].,;:]'
            urls = re.findall(url_pattern, source_content)
            
            for url in urls:
                # Clean up URL
                clean_url = url.strip()
                
                # Extract domain for title
                domain_match = re.search(r'https?://([^/]+)', clean_url)
                domain = domain_match.group(1) if domain_match else 'External Link'
                
                external_links.append({
                    'type': 'external',
                    'title': f"External: {domain}",
                    'url': clean_url,
                    'domain': domain,
                    'source': 'content_extraction'
                })
            
            # Extract links from markdown-style links
            markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            markdown_matches = re.findall(markdown_pattern, source_content)
            
            for text, url in markdown_matches:
                if url.startswith('http'):
                    external_links.append({
                        'type': 'external',
                        'title': text,
                        'url': url,
                        'source': 'markdown_link'
                    })
            
            # Remove duplicates
            seen_urls = set()
            unique_links = []
            for link in external_links:
                if link['url'] not in seen_urls:
                    seen_urls.add(link['url'])
                    unique_links.append(link)
            
            return unique_links[:10]  # Limit to 10 external links
            
        except Exception as e:
            print(f"❌ V2 RELATED LINKS: Error extracting external links - {e}")
            return []
    
    def _merge_and_format_links(self, internal_links: List[dict], external_links: List[dict]) -> List[dict]:
        """Merge and format internal and external links"""
        try:
            all_links = []
            
            # Add internal links (prioritized)
            for link in internal_links:
                all_links.append({
                    'type': 'internal',
                    'title': link['title'],
                    'url': link['url'],
                    'doc_uid': link.get('doc_uid'),
                    'doc_slug': link.get('doc_slug'),
                    'similarity_score': link.get('similarity_score'),
                    'preview': link.get('preview', ''),
                    'engine': link.get('engine', 'unknown'),
                    'priority': 'high'
                })
            
            # Add external links
            for link in external_links:
                all_links.append({
                    'type': 'external',
                    'title': link['title'],
                    'url': link['url'],
                    'domain': link.get('domain', ''),
                    'source': link.get('source', 'unknown'),
                    'priority': 'medium'
                })
            
            # Sort by priority and similarity
            def sort_key(link):
                priority_weight = {'high': 3, 'medium': 2, 'low': 1}.get(link.get('priority', 'low'), 1)
                similarity_weight = link.get('similarity_score', 0) if link['type'] == 'internal' else 0
                return priority_weight + similarity_weight
            
            all_links.sort(key=sort_key, reverse=True)
            
            return all_links[:15]  # Limit total links
            
        except Exception as e:
            print(f"❌ V2 RELATED LINKS: Error merging links - {e}")
            return []


print("✅ KE-M5: V2 Related Links System migrated from server.py")