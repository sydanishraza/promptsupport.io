"""
KE-PR4: V2 Versioning System
Extracted from server.py - Versioning and diff system for reprocessing support
"""

import uuid
import hashlib
from datetime import datetime

class V2VersioningSystem:
    """V2 Engine: Versioning and diff system for reprocessing support and version comparison"""
    
    def __init__(self):
        self.version_metadata_fields = [
            'source_hash', 'version', 'supersedes', 'version_timestamp', 'change_summary'
        ]
        
        self.diff_comparison_fields = [
            'title', 'toc', 'sections', 'faq', 'related_links', 'content_changes'
        ]
    
    async def create_version_from_articles(self, articles: list, run_id: str) -> dict:
        """Create version metadata from processed articles"""
        try:
            print(f"📦 KE-PR5: Creating version from {len(articles)} articles - run {run_id}")
            
            # Generate version ID
            version_id = f"v_{run_id}_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Calculate content hash from all articles
            content_hash = self._calculate_articles_hash(articles)
            
            # Create version metadata
            version_metadata = {
                "version_id": version_id,
                "run_id": run_id,
                "content_hash": content_hash,
                "article_count": len(articles),
                "created_at": datetime.utcnow().isoformat(),
                "engine": "v2",
                "processing_version": "2.0"
            }
            
            # Add article summaries
            article_summaries = []
            for article in articles:
                summary = {
                    "article_id": article.get('id'),
                    "title": article.get('title'),
                    "content_length": len(article.get('content', '')),
                    "article_type": article.get('article_type', 'unknown'),
                    "status": article.get('status', 'draft')
                }
                article_summaries.append(summary)
            
            version_metadata["articles"] = article_summaries
            
            version_result = {
                "version_id": version_id,
                "version_metadata": version_metadata,
                "versioning_status": "success",
                "created_articles": len(articles),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"✅ KE-PR5: Version created - {version_id} with {len(articles)} articles")
            return version_result
            
        except Exception as e:
            print(f"❌ KE-PR5: Error creating version from articles - {e}")
            return {
                "version_id": f"error_{run_id}",
                "versioning_status": "error",
                "error": str(e),
                "created_articles": len(articles) if articles else 0
            }
    
    def _calculate_articles_hash(self, articles: list) -> str:
        """Calculate hash from all article contents"""
        try:
            if not articles:
                return hashlib.sha256("empty".encode()).hexdigest()[:16]
            
            # Combine all article contents and titles for hashing
            combined_content = ""
            for article in articles:
                title = article.get('title', '')
                content = article.get('content', '')
                combined_content += f"{title}:{content}|"
            
            # Create hash
            content_hash = hashlib.sha256(combined_content.encode('utf-8')).hexdigest()[:16]
            return content_hash
            
        except Exception as e:
            print(f"⚠️ Error calculating articles hash: {e}")
            return f"hash_error_{int(datetime.utcnow().timestamp())}"