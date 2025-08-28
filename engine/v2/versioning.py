"""
KE-M14: V2 Versioning System - Complete Implementation Migration
Migrated from server.py - Versioning and diff system for reprocessing support and version comparison
"""

import uuid
import hashlib
from datetime import datetime
from ..stores.mongo import RepositoryFactory
from ._utils import create_processing_metadata

class V2VersioningSystem:
    """V2 Engine: Versioning and diff system for reprocessing support and version comparison"""
    
    def __init__(self):
        self.version_metadata_fields = [
            'source_hash', 'version', 'supersedes', 'version_timestamp', 'change_summary'
        ]
        
        self.diff_comparison_fields = [
            'title', 'toc', 'sections', 'faq', 'related_links', 'content_changes'
        ]
    
    async def run(self, content: dict, **kwargs) -> dict:
        """Run versioning using centralized interface (new interface)"""
        try:
            print("🔄 V2 VERSIONING: Starting versioning process - engine=v2")
            
            # Extract parameters from kwargs
            source_content = kwargs.get('content', '')
            content_type = kwargs.get('content_type', 'unknown')
            articles = kwargs.get('articles', [])
            generated_articles_result = kwargs.get('generated_articles_result', {})
            publishing_result = kwargs.get('publishing_result', {})
            run_id = kwargs.get('run_id', 'unknown')
            
            # Call the original manage_versioning method
            result = await self.manage_versioning(
                source_content, content_type, articles, generated_articles_result, 
                publishing_result, run_id
            )
            
            return result
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error in run method - {e}")
            return {
                "versioning_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    async def manage_versioning(self, content: str, content_type: str, articles: list, 
                              generated_articles_result: dict, publishing_result: dict, run_id: str) -> dict:
        """V2 Engine: Manage versioning for content and articles"""
        try:
            print(f"🔄 V2 VERSIONING: Starting versioning management - run {run_id} - engine=v2")
            
            # Step 1: Calculate source hash for change detection
            source_hash = self._calculate_source_hash(content, content_type)
            
            # Step 2: Check for existing versions
            existing_version_info = await self._find_existing_versions(source_hash, content_type, run_id)
            
            # Step 3: Determine version number and supersedes relationship
            version_metadata = await self._determine_version_metadata(
                source_hash, existing_version_info, run_id
            )
            
            # Step 4: Store version metadata with articles
            versioned_articles = await self._add_version_metadata_to_articles(
                articles, version_metadata, run_id
            )
            
            # Step 5: Create version record
            version_record = await self._create_version_record(
                version_metadata, generated_articles_result, publishing_result, run_id
            )
            
            # Step 6: Store version record
            await self._store_version_record(version_record, run_id)
            
            # Step 7: Generate diff if this is an update
            diff_result = None
            if version_metadata.get('supersedes'):
                diff_result = await self._generate_version_diff(
                    version_metadata['supersedes'], run_id, versioned_articles
                )
            
            versioning_result = {
                "versioning_id": f"versioning_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "versioning_status": "success",
                "version_metadata": version_metadata,
                "version_record": version_record,
                "diff_result": diff_result,
                "versioned_articles_count": len(versioned_articles),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
            
            version_number = version_metadata.get('version', 1)
            is_update = version_metadata.get('supersedes') is not None
            
            update_text = "(update)" if is_update else "(new)"
            print(f"✅ V2 VERSIONING: Versioning complete - Version {version_number} {update_text} - run {run_id} - engine=v2")
            return versioning_result
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error in versioning management - {e} - run {run_id} - engine=v2")
            return self._create_versioning_result("error", run_id, {"error": str(e)})
    
    def _calculate_source_hash(self, content: str, content_type: str) -> str:
        """Calculate hash of source content for change detection"""
        try:
            # Normalize content for consistent hashing
            normalized_content = content.strip().lower()
            
            # Include content type in hash to distinguish different types of same content
            hash_input = f"{content_type}:{normalized_content}"
            
            # Calculate SHA-256 hash
            source_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
            
            hash_preview = source_hash[:16] + "..."
            print(f"📊 V2 VERSIONING: Source hash calculated - {hash_preview} (type: {content_type})")
            return source_hash
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error calculating source hash - {e}")
            # Fallback to timestamp-based hash
            import time
            fallback_hash = hashlib.sha256(f"{content_type}:{time.time()}".encode()).hexdigest()
            return fallback_hash
    
    async def _find_existing_versions(self, source_hash: str, content_type: str, run_id: str) -> dict:
        """Find existing versions of content based on source hash"""
        try:
            hash_preview = source_hash[:16] + "..."
            print(f"🔍 V2 VERSIONING: Searching for existing versions - hash: {hash_preview} - run {run_id} - engine=v2")
            
            # Search for existing version records with same source hash
            existing_versions = []
            content_library_versions = []
            
            # Use repository pattern with fallback to direct DB access
            try:
                from pymongo import MongoClient
                import os
                
                mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/promptsupport')
                client = MongoClient(mongo_url)
                db = client.get_default_database()
                
                # Search version records
                async for version_record in db.v2_version_records.find({"source_hash": source_hash}).sort("version", -1):
                    existing_versions.append(version_record)
                
                # Search content library for articles with same source hash
                async for article in db.content_library.find({"version_metadata.source_hash": source_hash}).sort("version_metadata.version", -1):
                    if article.get('engine') == 'v2':  # Only V2 articles
                        content_library_versions.append(article)
                
            except Exception as db_error:
                print(f"⚠️ V2 VERSIONING: Database access error - {db_error}")
            
            existing_version_info = {
                "has_existing_versions": len(existing_versions) > 0 or len(content_library_versions) > 0,
                "version_records": existing_versions,
                "content_library_versions": content_library_versions,
                "latest_version": existing_versions[0] if existing_versions else None,
                "total_versions": len(existing_versions)
            }
            
            if existing_version_info["has_existing_versions"]:
                latest_version = existing_version_info["latest_version"]
                if latest_version:
                    version_num = latest_version.get('version', 'unknown')
                    print(f"📋 V2 VERSIONING: Found {existing_version_info['total_versions']} existing versions - latest: v{version_num} - run {run_id} - engine=v2")
                else:
                    print(f"📋 V2 VERSIONING: Found existing content in library - run {run_id} - engine=v2")
            else:
                print(f"🆕 V2 VERSIONING: No existing versions found - this is a new content version - run {run_id} - engine=v2")
            
            return existing_version_info
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error finding existing versions - {e} - run {run_id} - engine=v2")
            return {
                "has_existing_versions": False,
                "version_records": [],
                "content_library_versions": [],
                "latest_version": None,
                "total_versions": 0
            }
    
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