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
    
    async def _determine_version_metadata(self, source_hash: str, existing_version_info: dict, run_id: str) -> dict:
        """Determine version number and supersedes relationship"""
        try:
            version_metadata = {
                "source_hash": source_hash,
                "version_timestamp": datetime.utcnow().isoformat(),
                "run_id": run_id
            }
            
            if existing_version_info["has_existing_versions"]:
                # This is an update to existing content
                latest_version = existing_version_info["latest_version"]
                
                if latest_version:
                    # Increment version number
                    previous_version = latest_version.get('version', 0)
                    version_metadata["version"] = previous_version + 1
                    version_metadata["supersedes"] = latest_version.get('run_id', 'unknown')
                    version_metadata["change_summary"] = "Content update detected"
                else:
                    # Found content in library but no version record
                    version_metadata["version"] = 2  # Assume this is version 2
                    version_metadata["supersedes"] = "content_library_existing"
                    version_metadata["change_summary"] = "Update to existing content library article"
            else:
                # This is new content
                version_metadata["version"] = 1
                version_metadata["supersedes"] = None
                version_metadata["change_summary"] = "New content version"
            
            supersedes_text = version_metadata.get('supersedes', 'none')
            if version_metadata.get('supersedes'):
                supersedes_info = f"(supersedes: {supersedes_text})"
            else:
                supersedes_info = "(new)"
            
            print(f"📊 V2 VERSIONING: Version metadata determined - v{version_metadata['version']} {supersedes_info} - run {run_id} - engine=v2")
            return version_metadata
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error determining version metadata - {e} - run {run_id} - engine=v2")
            return {
                "source_hash": source_hash,
                "version": 1,
                "supersedes": None,
                "version_timestamp": datetime.utcnow().isoformat(),
                "change_summary": "Version metadata error",
                "run_id": run_id
            }
    
    async def _add_version_metadata_to_articles(self, articles: list, version_metadata: dict, run_id: str) -> list:
        """Add version metadata to all articles"""
        try:
            print(f"🏷️ V2 VERSIONING: Adding version metadata to {len(articles)} articles - run {run_id} - engine=v2")
            
            versioned_articles = []
            
            for article in articles:
                # Create versioned article with metadata
                versioned_article = article.copy()
                
                # Add version metadata
                versioned_article['version_metadata'] = version_metadata.copy()
                
                # Add version-specific fields to main article metadata
                if 'metadata' not in versioned_article:
                    versioned_article['metadata'] = {}
                
                versioned_article['metadata']['version'] = version_metadata['version']
                versioned_article['metadata']['source_hash'] = version_metadata['source_hash']
                versioned_article['metadata']['version_timestamp'] = version_metadata['version_timestamp']
                
                if version_metadata.get('supersedes'):
                    versioned_article['metadata']['supersedes'] = version_metadata['supersedes']
                    versioned_article['metadata']['is_update'] = True
                else:
                    versioned_article['metadata']['is_update'] = False
                
                versioned_articles.append(versioned_article)
            
            print(f"🏷️ V2 VERSIONING: Version metadata added to all articles - v{version_metadata['version']} - run {run_id} - engine=v2")
            return versioned_articles
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error adding version metadata to articles - {e} - run {run_id} - engine=v2")
            return articles  # Return original articles on error
    
    async def _create_version_record(self, version_metadata: dict, generated_articles_result: dict, 
                                   publishing_result: dict, run_id: str) -> dict:
        """Create comprehensive version record for storage"""
        try:
            version_record = {
                "version_record_id": f"version_{run_id}_{int(datetime.utcnow().timestamp())}",
                "run_id": run_id,
                "engine": "v2",
                
                # Version metadata
                **version_metadata,
                
                # Processing metadata
                "processing_metadata": {
                    "articles_generated": len(generated_articles_result.get('generated_articles', [])),
                    "publishing_status": publishing_result.get('publishing_status', 'unknown'),
                    "published_articles": publishing_result.get('published_articles', 0),
                    "coverage_achieved": publishing_result.get('coverage_achieved', 0)
                },
                
                # Version chain metadata
                "version_chain": {
                    "is_initial_version": version_metadata.get('version', 1) == 1,
                    "is_update": version_metadata.get('supersedes') is not None,
                    "previous_run_id": version_metadata.get('supersedes'),
                    "version_number": version_metadata.get('version', 1)
                },
                
                # Storage metadata
                "created_at": datetime.utcnow().isoformat(),
                "record_type": "v2_version_record"
            }
            
            return version_record
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error creating version record - {e} - run {run_id} - engine=v2")
            return {
                "version_record_id": f"version_{run_id}_error",
                "run_id": run_id,
                "engine": "v2",
                "error": str(e)
            }
    
    async def _store_version_record(self, version_record: dict, run_id: str) -> bool:
        """Store version record in database"""
        try:
            from pymongo import MongoClient
            import os
            
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/promptsupport')
            client = MongoClient(mongo_url)
            db = client.get_default_database()
            
            result = await db.v2_version_records.insert_one(version_record)
            
            if result.inserted_id:
                print(f"💾 V2 VERSIONING: Version record stored - ID: {result.inserted_id} - run {run_id} - engine=v2")
                return True
            else:
                print(f"❌ V2 VERSIONING: Failed to store version record - run {run_id} - engine=v2")
                return False
                
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error storing version record - {e} - run {run_id} - engine=v2")
            return False
    
    async def _generate_version_diff(self, previous_run_id: str, current_run_id: str, current_articles: list) -> dict:
        """Generate diff between current and previous version"""
        try:
            print(f"🔍 V2 VERSIONING: Generating diff - current: {current_run_id} vs previous: {previous_run_id} - engine=v2")
            
            # Step 1: Find previous version articles
            previous_articles = []
            
            # Search in content library for previous version articles
            from pymongo import MongoClient
            import os
            
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/promptsupport')
            client = MongoClient(mongo_url)
            db = client.get_default_database()
            
            async for article in db.content_library.find({"metadata.run_id": previous_run_id, "engine": "v2"}):
                previous_articles.append(article)
            
            # Also search in v2_version_records for previous articles
            previous_version_record = await db.v2_version_records.find_one({"run_id": previous_run_id})
            
            if not previous_articles and not previous_version_record:
                print(f"⚠️ V2 VERSIONING: No previous version data found for diff - run {current_run_id} - engine=v2")
                return {
                    "diff_status": "no_previous_version",
                    "message": f"No previous version found for run_id: {previous_run_id}",
                    "current_run_id": current_run_id,
                    "previous_run_id": previous_run_id
                }
            
            # Step 2: Compare articles and generate diff
            diff_analysis = await self._compare_article_versions(previous_articles, current_articles, previous_run_id, current_run_id)
            
            # Step 3: Create diff result structure
            diff_result = {
                "diff_id": f"diff_{current_run_id}_{int(datetime.utcnow().timestamp())}",
                "current_run_id": current_run_id,
                "previous_run_id": previous_run_id,
                "diff_status": "success",
                "comparison_timestamp": datetime.utcnow().isoformat(),
                "engine": "v2",
                
                # Article count comparison
                "article_counts": {
                    "previous": len(previous_articles),
                    "current": len(current_articles),
                    "difference": len(current_articles) - len(previous_articles)
                },
                
                # Detailed diff analysis
                **diff_analysis
            }
            
            print(f"✅ V2 VERSIONING: Diff generated - {len(diff_analysis.get('title_changes', []))} title changes, {len(diff_analysis.get('content_changes', []))} content changes - run {current_run_id} - engine=v2")
            return diff_result
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error generating version diff - {e} - run {current_run_id} - engine=v2")
            return {
                "diff_status": "error",
                "error": str(e),
                "current_run_id": current_run_id,
                "previous_run_id": previous_run_id
            }
    
    async def _compare_article_versions(self, previous_articles: list, current_articles: list, 
                                      previous_run_id: str, current_run_id: str) -> dict:
        """Compare previous and current articles to identify differences"""
        try:
            comparison_result = {
                "title_changes": [],
                "toc_changes": [],
                "section_changes": [],
                "faq_changes": [],
                "related_links_changes": [],
                "content_changes": [],
                "new_articles": [],
                "removed_articles": [],
                "unchanged_articles": []
            }
            
            # Create title-based lookup for previous articles
            previous_lookup = {}
            for prev_article in previous_articles:
                title = prev_article.get('title', '').strip().lower()
                if title:
                    previous_lookup[title] = prev_article
            
            # Compare each current article with previous version
            for curr_article in current_articles:
                current_title = curr_article.get('title', '').strip()
                current_title_lower = current_title.lower()
                
                if current_title_lower in previous_lookup:
                    # Article exists in both versions - compare content
                    prev_article = previous_lookup[current_title_lower]
                    article_diff = await self._compare_individual_articles(prev_article, curr_article)
                    
                    if article_diff['has_changes']:
                        # Add changes to respective categories
                        if article_diff.get('title_changed'):
                            comparison_result["title_changes"].append(article_diff['title_diff'])
                        if article_diff.get('toc_changed'):
                            comparison_result["toc_changes"].append(article_diff['toc_diff'])
                        if article_diff.get('sections_changed'):
                            comparison_result["section_changes"].extend(article_diff['section_diffs'])
                        if article_diff.get('faq_changed'):
                            comparison_result["faq_changes"].append(article_diff['faq_diff'])
                        if article_diff.get('related_links_changed'):
                            comparison_result["related_links_changes"].append(article_diff['related_links_diff'])
                        if article_diff.get('content_changed'):
                            comparison_result["content_changes"].append(article_diff['content_diff'])
                    else:
                        comparison_result["unchanged_articles"].append({
                            "title": current_title,
                            "article_id": curr_article.get('id', 'unknown')
                        })
                    
                    # Remove from previous lookup to track removed articles
                    del previous_lookup[current_title_lower]
                else:
                    # New article in current version
                    comparison_result["new_articles"].append({
                        "title": current_title,
                        "article_id": curr_article.get('id', 'unknown'),
                        "content_preview": self._get_content_preview(curr_article.get('content', ''))
                    })
            
            # Any remaining articles in previous_lookup are removed articles
            for removed_title, removed_article in previous_lookup.items():
                comparison_result["removed_articles"].append({
                    "title": removed_article.get('title', ''),
                    "article_id": removed_article.get('id', 'unknown'),
                    "content_preview": self._get_content_preview(removed_article.get('content', ''))
                })
            
            return comparison_result
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error comparing article versions - {e} - engine=v2")
            return {"error": str(e)}
    
    async def _compare_individual_articles(self, prev_article: dict, curr_article: dict) -> dict:
        """Compare two individual articles and identify specific changes"""
        try:
            article_diff = {
                "has_changes": False,
                "article_title": curr_article.get('title', ''),
                "article_id": curr_article.get('id', 'unknown')
            }
            
            # Compare titles
            prev_title = prev_article.get('title', '').strip()
            curr_title = curr_article.get('title', '').strip()
            
            if prev_title != curr_title:
                article_diff["title_changed"] = True
                article_diff["title_diff"] = {
                    "previous": prev_title,
                    "current": curr_title,
                    "change_type": "title_modified"
                }
                article_diff["has_changes"] = True
            
            # Compare content for significant changes
            prev_content = prev_article.get('content', '')
            curr_content = curr_article.get('content', '')
            
            content_similarity = self._calculate_content_similarity(prev_content, curr_content)
            
            if content_similarity < 0.8:  # Significant content change threshold
                article_diff["content_changed"] = True
                article_diff["content_diff"] = {
                    "similarity_score": content_similarity,
                    "change_type": "significant_content_change",
                    "previous_preview": self._get_content_preview(prev_content),
                    "current_preview": self._get_content_preview(curr_content),
                    "word_count_change": self._count_words(curr_content) - self._count_words(prev_content)
                }
                article_diff["has_changes"] = True
            
            # Extract and compare table of contents
            prev_toc = self._extract_toc_from_content(prev_content)
            curr_toc = self._extract_toc_from_content(curr_content)
            
            if prev_toc != curr_toc:
                article_diff["toc_changed"] = True
                article_diff["toc_diff"] = {
                    "previous": prev_toc,
                    "current": curr_toc,
                    "change_type": "toc_structure_change"
                }
                article_diff["has_changes"] = True
            
            return article_diff
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error comparing individual articles - {e} - engine=v2")
            return {"has_changes": False, "error": str(e)}
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings"""
        try:
            # Simple word-based similarity calculation
            import re
            
            # Extract words from both contents
            words1 = set(re.findall(r'\w+', content1.lower()))
            words2 = set(re.findall(r'\w+', content2.lower()))
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            
            similarity = intersection / union if union > 0 else 0.0
            return similarity
            
        except Exception:
            return 0.5  # Fallback similarity score
    
    def _get_content_preview(self, content: str, max_length: int = 200) -> str:
        """Get a preview of content for diff display"""
        try:
            import re
            # Strip HTML tags for preview
            text_content = re.sub(r'<[^>]+>', '', content).strip()
            
            if len(text_content) <= max_length:
                return text_content
            
            return text_content[:max_length] + "..."
            
        except Exception:
            return "Content preview unavailable"
    
    def _extract_toc_from_content(self, content: str) -> list:
        """Extract table of contents (headings) from HTML content"""
        try:
            import re
            
            headings = []
            # Find all headings (h1, h2, h3, etc.)
            heading_pattern = r'<h([1-6])[^>]*>(.*?)</h[1-6]>'
            matches = re.findall(heading_pattern, content, re.IGNORECASE)
            
            for level, text in matches:
                # Clean heading text
                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                headings.append({
                    "level": int(level),
                    "text": clean_text
                })
            
            return headings
            
        except Exception:
            return []
    
    def _count_words(self, content: str) -> int:
        """Count words in content"""
        try:
            import re
            # Strip HTML and count words
            text_content = re.sub(r'<[^>]+>', ' ', content)
            words = re.findall(r'\w+', text_content)
            return len(words)
        except Exception:
            return 0

    def _create_versioning_result(self, status: str, run_id: str, additional_data: dict) -> dict:
        """Create a standard versioning result structure"""
        return {
            "versioning_id": f"versioning_{run_id}_{int(datetime.utcnow().timestamp())}",
            "run_id": run_id,
            "versioning_status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "engine": "v2",
            **additional_data
        }

    def _analyze_version_chains(self, versioning_results: list) -> dict:
        """Analyze version chains from versioning results"""
        try:
            # Group by source hash to find version chains
            source_chains = {}
            
            for result in versioning_results:
                source_hash = result.get('version_metadata', {}).get('source_hash')
                if source_hash:
                    if source_hash not in source_chains:
                        source_chains[source_hash] = []
                    source_chains[source_hash].append(result)
            
            # Analyze chains
            chain_analysis = {
                "total_source_content": len(source_chains),
                "content_with_multiple_versions": len([chain for chain in source_chains.values() if len(chain) > 1]),
                "longest_version_chain": max([len(chain) for chain in source_chains.values()]) if source_chains else 0,
                "average_versions_per_content": sum([len(chain) for chain in source_chains.values()]) / len(source_chains) if source_chains else 0
            }
            
            return chain_analysis
            
        except Exception as e:
            print(f"❌ V2 VERSIONING: Error analyzing version chains - {e}")
            return {"error": str(e)}

print("✅ KE-M14: V2 Versioning System migrated from server.py")