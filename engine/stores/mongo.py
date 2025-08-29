"""
KE-PR9: MongoDB & Assets Repositories (Stores)
Centralized MongoDB operations with repository pattern for clean data layer abstraction
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pymongo.errors import PyMongoError
import motor.motor_asyncio

# Import settings for MongoDB connection
try:
    from ...config.settings import settings
    MONGO_URI = settings.MONGO_URI
except ImportError:
    # Fallback if settings not available
    MONGO_URI = os.getenv("MONGO_URL", "mongodb://localhost:27017/promptsupport")

print(f"🔌 KE-PR9: Initializing MongoDB repository with URI: {MONGO_URI[:50]}...")

# MongoDB client and database instances
_mongo_client = None
_db = None

def get_mongo_client():
    """Get or create MongoDB client"""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    return _mongo_client

def get_database():
    """Get or create database instance"""
    global _db
    if _db is None:
        client = get_mongo_client()
        # Extract database name from URI or use default
        if '/' in MONGO_URI.split('://')[-1]:
            db_name = MONGO_URI.split('://')[-1].split('/')[1].split('?')[0]
        else:
            db_name = "promptsupport"
        _db = client[db_name]
    return _db

def get_collection(name: str):
    """Get collection by name"""
    try:
        db = get_database()
        return db[name]
    except Exception as e:
        print(f"❌ KE-PR9: Error getting collection {name}: {e}")
        raise

# ========================================
# CONTENT LIBRARY REPOSITORY
# ========================================

class ContentLibraryRepository:
    """Repository for content library operations with TICKET-3 field support"""
    
    def __init__(self):
        self.collection = get_collection("content_library")
    
    async def insert_article(self, article: Dict[str, Any]) -> str:
        """Insert new article with TICKET-3 fields preservation"""
        try:
            # Ensure required TICKET-3 fields are preserved
            if 'doc_uid' not in article:
                from ..linking.bookmarks import generate_doc_uid
                article['doc_uid'] = generate_doc_uid()
            
            if 'doc_slug' not in article and 'title' in article:
                from ..linking.bookmarks import generate_doc_slug
                article['doc_slug'] = generate_doc_slug(article['title'])
            
            # Ensure headings array exists
            if 'headings' not in article:
                article['headings'] = []
            
            # Ensure xrefs array exists
            if 'xrefs' not in article:
                article['xrefs'] = []
            
            # Add timestamps
            article['created_at'] = datetime.utcnow()
            article['updated_at'] = datetime.utcnow()
            
            result = await self.collection.insert_one(article)
            print(f"✅ KE-PR9: Article inserted - {article.get('title', 'Untitled')} - ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ KE-PR9: Error inserting article: {e}")
            raise
    
    async def upsert_content(self, doc_uid: str, payload: Dict[str, Any]) -> bool:
        """Upsert content by doc_uid with TICKET-3 support"""
        try:
            # Ensure TICKET-3 fields are preserved in update
            if 'headings' not in payload:
                existing = await self.find_by_doc_uid(doc_uid, projection={'headings': 1})
                if existing and 'headings' in existing:
                    payload['headings'] = existing['headings']
            
            if 'xrefs' not in payload:
                existing = await self.find_by_doc_uid(doc_uid, projection={'xrefs': 1})
                if existing and 'xrefs' in existing:
                    payload['xrefs'] = existing['xrefs']
            
            payload['updated_at'] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"doc_uid": doc_uid}, 
                {"$set": payload}, 
                upsert=True
            )
            
            print(f"✅ KE-PR9: Content upserted - doc_uid: {doc_uid}")
            return result.acknowledged
            
        except Exception as e:
            print(f"❌ KE-PR9: Error upserting content: {e}")
            raise
    
    async def find_by_doc_uid(self, doc_uid: str, projection: Optional[Dict] = None) -> Optional[Dict]:
        """Find article by doc_uid"""
        try:
            result = await self.collection.find_one({"doc_uid": doc_uid}, projection)
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"❌ KE-PR9: Error finding by doc_uid {doc_uid}: {e}")
            return None
    
    async def find_by_doc_slug(self, doc_slug: str, projection: Optional[Dict] = None) -> Optional[Dict]:
        """Find article by doc_slug (TICKET-3 requirement)"""
        try:
            result = await self.collection.find_one({"doc_slug": doc_slug}, projection)
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"❌ KE-PR9: Error finding by doc_slug {doc_slug}: {e}")
            return None
    
    async def find_by_engine(self, engine: str = "v2", limit: Optional[int] = None) -> List[Dict]:
        """Find articles by engine type"""
        try:
            query = {"engine": engine}
            cursor = self.collection.find(query)
            
            if limit:
                cursor = cursor.limit(limit)
            
            articles = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for article in articles:
                if '_id' in article:
                    article['_id'] = str(article['_id'])
            
            return articles
        except Exception as e:
            print(f"❌ KE-PR9: Error finding by engine {engine}: {e}")
            return []
    
    async def find_by_run_id(self, run_id: str, engine: str = "v2") -> List[Dict]:
        """Find articles by processing run_id"""
        try:
            query = {"metadata.run_id": run_id, "engine": engine}
            cursor = self.collection.find(query)
            articles = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for article in articles:
                if '_id' in article:
                    article['_id'] = str(article['_id'])
            
            return articles
        except Exception as e:
            print(f"❌ KE-PR9: Error finding by run_id {run_id}: {e}")
            return []
    
    async def update_headings(self, doc_uid: str, headings: List[Dict]) -> bool:
        """Update headings array for TICKET-3 support"""
        try:
            result = await self.collection.update_one(
                {"doc_uid": doc_uid},
                {"$set": {"headings": headings, "updated_at": datetime.utcnow()}}
            )
            return result.acknowledged
        except Exception as e:
            print(f"❌ KE-PR9: Error updating headings for {doc_uid}: {e}")
            return False
    
    async def update_xrefs(self, doc_uid: str, xrefs: List[Dict]) -> bool:
        """Update cross-references array for TICKET-3 support"""
        try:
            result = await self.collection.update_one(
                {"doc_uid": doc_uid},
                {"$set": {"xrefs": xrefs, "updated_at": datetime.utcnow()}}
            )
            return result.acknowledged
        except Exception as e:
            print(f"❌ KE-PR9: Error updating xrefs for {doc_uid}: {e}")
            return False
    
    async def find_by_id(self, article_id: str, projection: Optional[Dict] = None) -> Optional[Dict]:
        """Find article by id field (KE-PR9.4)"""
        try:
            result = await self.collection.find_one({"id": article_id}, projection)
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"❌ KE-PR9.4: Error finding by id {article_id}: {e}")
            return None
    
    async def update_by_id(self, article_id: str, updates: Dict[str, Any]) -> bool:
        """Update article by id field (KE-PR9.4)"""
        try:
            # Preserve TICKET-3 fields during updates
            updates['updated_at'] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"id": article_id},
                {"$set": updates}
            )
            
            if result.matched_count > 0:
                print(f"✅ KE-PR9.4: Article updated by id - {article_id}")
                return True
            else:
                print(f"⚠️ KE-PR9.4: No article found with id - {article_id}")
                return False
                
        except Exception as e:
            print(f"❌ KE-PR9.4: Error updating article {article_id}: {e}")
            return False
    
    async def update_by_object_id(self, object_id: str, updates: Dict[str, Any]) -> bool:
        """Update article by MongoDB ObjectId (KE-PR9.4 - legacy compatibility)"""
        try:
            from bson import ObjectId
            
            # Preserve TICKET-3 fields during updates
            updates['updated_at'] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(object_id)},
                {"$set": updates}
            )
            
            if result.matched_count > 0:
                print(f"✅ KE-PR9.4: Article updated by ObjectId - {object_id}")
                return True
            else:
                print(f"⚠️ KE-PR9.4: No article found with ObjectId - {object_id}")
                return False
                
        except Exception as e:
            print(f"❌ KE-PR9.4: Error updating article by ObjectId {object_id}: {e}")
            return False

    async def delete_by_id(self, article_id: str) -> bool:
        """Delete article by id"""
        try:
            result = await self.collection.delete_one({"id": article_id})
            print(f"✅ KE-PR9: Article deleted - ID: {article_id}")
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ KE-PR9: Error deleting article {article_id}: {e}")
            return False
    
    async def find_recent(self, limit: int = 100) -> List[Dict]:
        """Find recent articles"""
        try:
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            articles = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for article in articles:
                if '_id' in article:
                    article['_id'] = str(article['_id'])
            
            return articles
        except Exception as e:
            print(f"❌ KE-PR9: Error finding recent articles: {e}")
            return []

# ========================================
# QA RESULTS REPOSITORY
# ========================================

class QAResultsRepository:
    """Repository for QA results operations (KE-PR7 support)"""
    
    def __init__(self):
        self.collection = get_collection("qa_results")
    
    async def insert_qa_report(self, qa_report: Dict[str, Any]) -> str:
        """Insert QA report"""
        try:
            qa_report['created_at'] = datetime.utcnow()
            qa_report['engine'] = 'v2'
            
            result = await self.collection.insert_one(qa_report)
            print(f"✅ KE-PR9: QA report inserted - ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ KE-PR9: Error inserting QA report: {e}")
            raise
    
    async def find_recent_qa_summaries(self, limit: int = 10) -> List[Dict]:
        """Find recent QA summaries"""
        try:
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            reports = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for report in reports:
                if '_id' in report:
                    report['_id'] = str(report['_id'])
            
            return reports
        except Exception as e:
            print(f"❌ KE-PR9: Error finding QA summaries: {e}")
            return []
    
    async def find_by_job_id(self, job_id: str) -> List[Dict]:
        """Find QA reports by job_id"""
        try:
            cursor = self.collection.find({"job_id": job_id}).sort("created_at", -1)
            reports = await cursor.to_list(length=None)
            
            # Convert ObjectId to string
            for report in reports:
                if '_id' in report:
                    report['_id'] = str(report['_id'])
            
            return reports
        except Exception as e:
            print(f"❌ KE-PR9: Error finding QA reports by job_id: {e}")
            return []

# ========================================
# V2 PROCESSING RESULTS REPOSITORIES
# ========================================

class V2AnalysisRepository:
    """Repository for V2 analysis results"""
    
    def __init__(self):
        self.collection = get_collection("v2_analysis")
    
    async def store_analysis(self, analysis_record: Dict[str, Any]) -> str:
        """Store V2 analysis result"""
        try:
            analysis_record['created_at'] = datetime.utcnow()
            result = await self.collection.insert_one(analysis_record)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ KE-PR9: Error storing analysis: {e}")
            raise
    
    async def get_analysis(self, run_id: str) -> Optional[Dict]:
        """Get analysis by run_id"""
        try:
            result = await self.collection.find_one({"run_id": run_id})
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"❌ KE-PR9: Error getting analysis: {e}")
            return None

class V2OutlineRepository:
    """Repository for V2 outline results"""
    
    def __init__(self):
        self.global_collection = get_collection("v2_global_outlines")
        self.per_article_collection = get_collection("v2_per_article_outlines")
    
    async def store_global_outline(self, outline_record: Dict[str, Any]) -> str:
        """Store global outline result"""
        try:
            outline_record['created_at'] = datetime.utcnow()
            result = await self.global_collection.insert_one(outline_record)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ KE-PR9: Error storing global outline: {e}")
            raise
    
    async def store_per_article_outlines(self, outlines_record: Dict[str, Any]) -> str:
        """Store per-article outlines result"""
        try:
            outlines_record['created_at'] = datetime.utcnow()
            result = await self.per_article_collection.insert_one(outlines_record)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ KE-PR9: Error storing per-article outlines: {e}")
            raise
    
    async def get_global_outline(self, run_id: str) -> Optional[Dict]:
        """Get global outline by run_id"""
        try:
            result = await self.global_collection.find_one({"run_id": run_id})
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"❌ KE-PR9: Error getting global outline: {e}")
            return None

class V2ValidationRepository:
    """Repository for V2 validation results"""
    
    def __init__(self):
        self.collection = get_collection("v2_validation_results")
    
    async def store_validation(self, validation_record: Dict[str, Any]) -> str:
        """Store validation result"""
        try:
            validation_record['created_at'] = datetime.utcnow()
            result = await self.collection.insert_one(validation_record)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ KE-PR9: Error storing validation: {e}")
            raise
    
    async def find_validations(self, query: Dict = None, limit: int = 10) -> List[Dict]:
        """Find validation results"""
        try:
            if query is None:
                query = {}
            
            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            return results
        except Exception as e:
            print(f"❌ KE-PR9: Error finding validations: {e}")
            return []

# ========================================
# ASSETS AND MEDIA REPOSITORIES
# ========================================

class AssetsRepository:
    """Repository for assets/media operations"""
    
    def __init__(self):
        self.collection = get_collection("assets")
    
    async def insert_assets(self, assets: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple assets"""
        try:
            for asset in assets:
                asset['created_at'] = datetime.utcnow()
            
            result = await self.collection.insert_many(assets)
            print(f"✅ KE-PR9: {len(assets)} assets inserted")
            return [str(id) for id in result.inserted_ids]
            
        except Exception as e:
            print(f"❌ KE-PR9: Error inserting assets: {e}")
            raise
    
    async def find_assets(self, query: Dict = None, limit: int = 100) -> List[Dict]:
        """Find assets"""
        try:
            if query is None:
                query = {}
            
            cursor = self.collection.find(query).limit(limit)
            assets = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for asset in assets:
                if '_id' in asset:
                    asset['_id'] = str(asset['_id'])
            
            return assets
        except Exception as e:
            print(f"❌ KE-PR9: Error finding assets: {e}")
            return []

class MediaLibraryRepository:
    """Repository for media library operations"""
    
    def __init__(self):
        self.collection = get_collection("media_library")
    
    async def insert_media_asset(self, media_asset: Dict[str, Any]) -> str:
        """Insert media asset"""
        try:
            media_asset['created_at'] = datetime.utcnow()
            result = await self.collection.insert_one(media_asset)
            print(f"✅ KE-PR9: Media asset inserted - ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ KE-PR9: Error inserting media asset: {e}")
            raise

# ========================================
# V2 PROCESSING REPOSITORY
# ========================================

class V2ProcessingRepository:
    """Repository for general V2 processing operations"""
    
    def __init__(self):
        self.collection = get_collection("v2_processing")
    
    async def store_processing_result(self, processing_record: Dict[str, Any]) -> str:
        """Store V2 processing result"""
        try:
            processing_record['created_at'] = datetime.utcnow()
            result = await self.collection.insert_one(processing_record)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ KE-PR9: Error storing processing result: {e}")
            raise
    
    async def get_processing_result(self, run_id: str) -> Optional[Dict]:
        """Get processing result by run_id"""
        try:
            result = await self.collection.find_one({"run_id": run_id})
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"❌ KE-PR9: Error getting processing result: {e}")
            return None
    
    async def find_recent_processing(self, limit: int = 10) -> List[Dict]:
        """Find recent processing results"""
        try:
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string
            for result in results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            return results
        except Exception as e:
            print(f"❌ KE-PR9: Error finding recent processing results: {e}")
            return []

# ========================================
# KE-PR9.5: PROCESSING JOBS REPOSITORY
# ========================================

class ProcessingJobsRepository:
    """Repository for processing job operations (KE-PR9.5)"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.processing_jobs
    
    async def insert_job(self, job_data: Dict[str, Any]) -> str:
        """Insert new processing job"""
        try:
            job_data['created_at'] = datetime.utcnow()
            job_data['status'] = job_data.get('status', 'pending')
            job_data['job_id'] = job_data.get('job_id', f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(job_data))}")
            
            result = await self.collection.insert_one(job_data)
            
            if result.inserted_id:
                print(f"✅ ProcessingJobs: Job inserted - {job_data.get('job_id', str(result.inserted_id))}")
                return str(result.inserted_id)
            else:
                print(f"❌ ProcessingJobs: Failed to insert job")
                return None
                
        except Exception as e:
            print(f"❌ ProcessingJobs: Error inserting job - {e}")
            return None
    
    async def update_job_status(self, job_id: str, status: str, details: Optional[Dict] = None) -> bool:
        """Update job status by job ID"""
        try:
            from bson import ObjectId
            
            updates = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if details:
                updates.update(details)
                
            # Try to update by ObjectId first, then by job_id field
            result = None
            try:
                result = await self.collection.update_one(
                    {"_id": ObjectId(job_id)},
                    {"$set": updates}
                )
            except:
                # Fallback to job_id field
                result = await self.collection.update_one(
                    {"job_id": job_id},
                    {"$set": updates}
                )
            
            if result and result.matched_count > 0:
                print(f"✅ ProcessingJobs: Job updated - {job_id} -> {status}")
                return True
            else:
                print(f"⚠️ ProcessingJobs: No job found with id - {job_id}")
                return False
                
        except Exception as e:
            print(f"❌ ProcessingJobs: Error updating job {job_id} - {e}")
            return False
    
    async def find_job(self, job_id: str) -> Optional[Dict]:
        """Find job by ID (ObjectId or job_id field)"""
        try:
            from bson import ObjectId
            
            # Try ObjectId first, then job_id field
            job = None
            try:
                job = await self.collection.find_one({"_id": ObjectId(job_id)})
            except:
                job = await self.collection.find_one({"job_id": job_id})
            
            if job and '_id' in job:
                job['_id'] = str(job['_id'])
            
            return job
            
        except Exception as e:
            print(f"❌ ProcessingJobs: Error finding job {job_id} - {e}")
            return None
    
    async def find_jobs_by_status(self, status: str, limit: int = 50) -> List[Dict]:
        """Find jobs by status"""
        try:
            cursor = self.collection.find({"status": status}).sort("created_at", -1).limit(limit)
            jobs = await cursor.to_list(length=limit)
            
            for job in jobs:
                if '_id' in job:
                    job['_id'] = str(job['_id'])
            
            return jobs
            
        except Exception as e:
            print(f"❌ ProcessingJobs: Error finding jobs by status {status} - {e}")
            return []
    
    async def find_recent_jobs(self, limit: int = 20) -> List[Dict]:
        """Find recent jobs across all statuses"""
        try:
            cursor = self.collection.find({}).sort("created_at", -1).limit(limit)
            jobs = await cursor.to_list(length=limit)
            
            for job in jobs:
                if '_id' in job:
                    job['_id'] = str(job['_id'])
            
            return jobs
            
        except Exception as e:
            print(f"❌ ProcessingJobs: Error finding recent jobs - {e}")
            return []
    
    async def count_jobs(self) -> int:
        """Count total number of processing jobs (KE-PR9.5)"""
        try:
            count = await self.collection.count_documents({})
            return count
        except Exception as e:
            print(f"❌ ProcessingJobs: Error counting jobs - {e}")
            return 0

# ========================================
# REPOSITORY FACTORY
# ========================================

class RepositoryFactory:
    """Factory for creating repository instances"""
    
    @staticmethod
    def get_content_library() -> ContentLibraryRepository:
        """Get content library repository"""
        return ContentLibraryRepository()
    
    @staticmethod
    def get_qa_results() -> QAResultsRepository:
        """Get QA results repository"""
        return QAResultsRepository()
    
    @staticmethod
    def get_v2_analysis() -> V2AnalysisRepository:
        """Get V2 analysis repository"""
        return V2AnalysisRepository()
    
    @staticmethod
    def get_v2_outlines() -> V2OutlineRepository:
        """Get V2 outlines repository"""
        return V2OutlineRepository()
    
    @staticmethod
    def get_v2_validation() -> V2ValidationRepository:
        """Get V2 validation repository"""
        return V2ValidationRepository()
    
    @staticmethod
    def get_assets() -> AssetsRepository:
        """Get assets repository"""
        return AssetsRepository()
    
    @staticmethod
    def get_media_library() -> MediaLibraryRepository:
        """Get media library repository"""
        return MediaLibraryRepository()
    
    @staticmethod
    def get_processing_jobs() -> ProcessingJobsRepository:
        """Get processing jobs repository (KE-PR9.5)"""
        return ProcessingJobsRepository()
    
    @staticmethod
    def get_v2_processing():
        """Get V2 processing repository for general V2 operations"""
        return V2ProcessingRepository()

# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

async def upsert_content(doc_uid: str, payload: Dict[str, Any]) -> bool:
    """Convenience function for content upsert"""
    repo = RepositoryFactory.get_content_library()
    return await repo.upsert_content(doc_uid, payload)

async def fetch_article_by_slug(slug: str, projection: Optional[Dict] = None) -> Optional[Dict]:
    """Convenience function for fetching by doc_slug (TICKET-3 requirement)"""
    repo = RepositoryFactory.get_content_library()
    return await repo.find_by_doc_slug(slug, projection)

async def fetch_article_by_uid(doc_uid: str, projection: Optional[Dict] = None) -> Optional[Dict]:
    """Convenience function for fetching by doc_uid (TICKET-3 requirement)"""
    repo = RepositoryFactory.get_content_library()
    return await repo.find_by_doc_uid(doc_uid, projection)

async def update_article_headings(doc_uid: str, headings: List[Dict]) -> bool:
    """Convenience function for updating headings (TICKET-3 requirement)"""
    repo = RepositoryFactory.get_content_library()
    return await repo.update_headings(doc_uid, headings)

async def update_article_xrefs(doc_uid: str, xrefs: List[Dict]) -> bool:
    """Convenience function for updating cross-references (TICKET-3 requirement)"""
    repo = RepositoryFactory.get_content_library()
    return await repo.update_xrefs(doc_uid, xrefs)

# KE-PR9.4: New convenience functions for id-based operations
async def fetch_article_by_id(article_id: str, projection: Optional[Dict] = None) -> Optional[Dict]:
    """Convenience function for fetching by article id (KE-PR9.4)"""
    repo = RepositoryFactory.get_content_library()
    return await repo.find_by_id(article_id, projection)

async def update_article_by_id(article_id: str, updates: Dict[str, Any]) -> bool:
    """Convenience function for updating by article id (KE-PR9.4)"""
    repo = RepositoryFactory.get_content_library()
    return await repo.update_by_id(article_id, updates)

# KE-PR9.5: Processing jobs convenience functions
async def insert_processing_job(job_data: Dict[str, Any]) -> str:
    """Convenience function for inserting processing job (KE-PR9.5)"""
    repo = RepositoryFactory.get_processing_jobs()
    return await repo.insert_job(job_data)

async def update_processing_job_status(job_id: str, status: str, details: Optional[Dict] = None) -> bool:
    """Convenience function for updating processing job status (KE-PR9.5)"""
    repo = RepositoryFactory.get_processing_jobs()
    return await repo.update_job_status(job_id, status, details)

async def count_processing_jobs() -> int:
    """Convenience function for counting processing jobs (KE-PR9.5)"""
    repo = RepositoryFactory.get_processing_jobs()
    return await repo.count_jobs()



# ========================================
# INTEGRATION TEST HELPER
# ========================================

async def test_mongo_roundtrip() -> bool:
    """Simple integration test for read/write roundtrip"""
    try:
        print("🧪 KE-PR9: Testing MongoDB read/write roundtrip...")
        
        # Test content library roundtrip
        repo = RepositoryFactory.get_content_library()
        
        test_article = {
            "id": "test_article_ke_pr9",
            "title": "KE-PR9 Test Article", 
            "content": "Test content for MongoDB repository",
            "doc_uid": "test-uid-ke-pr9",
            "doc_slug": "ke-pr9-test-article",
            "headings": [{"id": "test-heading", "text": "Test Heading", "level": 2}],
            "xrefs": [{"target": "test-ref", "type": "internal"}],
            "engine": "v2"
        }
        
        # Insert test article
        article_id = await repo.insert_article(test_article)
        print(f"✅ KE-PR9: Test article inserted - ID: {article_id}")
        
        # Read back by doc_uid
        retrieved = await repo.find_by_doc_uid("test-uid-ke-pr9")
        if not retrieved:
            print("❌ KE-PR9: Failed to retrieve test article by doc_uid")
            return False
        
        # Read back by doc_slug
        retrieved_slug = await repo.find_by_doc_slug("ke-pr9-test-article")
        if not retrieved_slug:
            print("❌ KE-PR9: Failed to retrieve test article by doc_slug")
            return False
        
        # Verify TICKET-3 fields
        if 'headings' not in retrieved or 'xrefs' not in retrieved:
            print("❌ KE-PR9: TICKET-3 fields missing in retrieved article")
            return False
        
        # Update test
        updated = await repo.upsert_content("test-uid-ke-pr9", {"title": "Updated Title"})
        if not updated:
            print("❌ KE-PR9: Failed to update test article")
            return False
        
        # Cleanup
        await repo.delete_by_id("test_article_ke_pr9")
        
        print("✅ KE-PR9: MongoDB roundtrip test passed!")
        return True
        
    except Exception as e:
        print(f"❌ KE-PR9: MongoDB roundtrip test failed: {e}")
        return False

# ========================================
# INITIALIZATION
# ========================================

print("✅ KE-PR9: MongoDB repository layer initialized")
print("✅ KE-PR9: TICKET-3 fields (doc_uid, doc_slug, headings, xrefs) supported")
print("✅ KE-PR9: Repository pattern ready for centralized data access")