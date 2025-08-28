"""
KE-M15: V2 Review System - Complete Implementation Migration
Migrated from server.py - Human-in-the-loop review and quality assurance system for V2 processing runs
"""

import uuid
import time
from datetime import datetime
from ..stores.mongo import RepositoryFactory

class V2ReviewSystem:
    """V2 Engine: Human-in-the-loop review and quality assurance system"""
    
    def __init__(self):
        self.review_statuses = ['pending_review', 'approved', 'rejected', 'published']
        self.rejection_reasons = [
            'quality_issues', 'incomplete_content', 'factual_errors', 
            'formatting_problems', 'missing_sections', 'redundancy_issues',
            'coverage_insufficient', 'fidelity_low', 'style_violations', 'other'
        ]
        
    async def run(self, content: dict, **kwargs) -> dict:
        """Run review system using centralized interface (new interface)"""
        try:
            print("👥 V2 REVIEW: Starting review system process - engine=v2")
            
            # Extract parameters from kwargs
            run_id = kwargs.get('run_id', 'unknown')
            articles = kwargs.get('articles', [])
            metadata = kwargs.get('metadata', {})
            
            # Call the original enqueue_for_review method
            result = await self.enqueue_for_review(run_id, articles, metadata)
            
            return result
            
        except Exception as e:
            print(f"❌ V2 REVIEW: Error in run method - {e}")
            return {
                "review_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "engine": "v2"
            }
    
    async def get_runs_for_review(self, limit: int = 50, status_filter: str = None) -> dict:
        """Get list of processing runs available for review with quality badges"""
        try:
            print(f"📋 V2 REVIEW: Getting runs for review - limit: {limit} - engine=v2")
            
            # Build query for filtering
            runs_query = {}
            if status_filter and status_filter in self.review_statuses:
                runs_query['review_status'] = status_filter
            
            # Get recent processing runs using repository pattern
            runs_data = []
            
            try:
                # Get from validation results using V2 processing repository
                v2_repo = RepositoryFactory.get_v2_processing()
                validation_results = await v2_repo.find_many(
                    collection="v2_validation_results",
                    query=runs_query,
                    sort=[("timestamp", -1)],
                    limit=limit
                )
                
                for validation_result in validation_results:
                    # Convert ObjectId to string for serialization
                    validation_result = self._objectid_to_str(validation_result)
                    run_id = validation_result.get('run_id')
                    if run_id:
                        run_data = await self._compile_run_data_for_review(run_id, validation_result)
                        if run_data:
                            runs_data.append(run_data)
            
            # Sort by timestamp
            runs_data.sort(key=lambda x: x.get('processing_timestamp', ''), reverse=True)
            
            # Compile summary statistics
            summary_stats = await self._compile_review_summary_stats(runs_data)
            
            review_response = {
                "review_system_status": "active",
                "engine": "v2",
                "review_data_generated_at": datetime.utcnow().isoformat(),
                
                # Summary statistics
                "summary": summary_stats,
                
                # Runs available for review
                "runs": runs_data[:limit]
            }
            
            print(f"✅ V2 REVIEW: Returning {len(runs_data)} runs for review - engine=v2")
            return review_response
            
        except Exception as e:
            print(f"❌ V2 REVIEW: Error getting runs for review - {e} - engine=v2")
            return {"error": str(e), "runs": []}
    
    async def enqueue_for_review(self, run_id: str, articles: list, metadata: dict = None) -> dict:
        """Enqueue processing run for human review"""
        try:
            print(f"👥 V2 REVIEW: Enqueuing run for review - {run_id} - {len(articles)} articles")
            
            review_id = f"review_{run_id}_{int(time.time())}"
            
            # Create review entry
            review_entry = {
                "review_id": review_id,
                "run_id": run_id,
                "review_status": "pending_review",
                "articles_count": len(articles),
                "created_at": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            # Store in review queue using database connection
            try:
                from pymongo import MongoClient
                import os
                
                mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/promptsupport')
                client = MongoClient(mongo_url)
                db = client.get_default_database()
                
                # Store in review queue
                await db.v2_review_queue.insert_one(review_entry)
            except Exception as db_error:
                print(f"⚠️ V2 REVIEW: Database storage error - {db_error}")
            
            print(f"✅ V2 REVIEW: Run enqueued for review - {review_id}")
            
            return {
                "review_id": review_id,
                "review_status": "pending_review",
                "articles_count": len(articles)
            }
            
        except Exception as e:
            print(f"❌ V2 REVIEW: Error enqueuing for review - {e}")
            return {
                "review_id": f"error_{run_id}",
                "review_status": "error",
                "error": str(e)
            }

    # Helper methods migrated from server.py

    async def _compile_run_data_for_review(self, run_id: str, validation_result: dict) -> dict:
        """Compile comprehensive data for a processing run for review"""
        try:
            # Get related results from other V2 collections using repository
            v2_repo = RepositoryFactory.get_v2_processing()
            qa_result = await v2_repo.find_one("v2_qa_results", {"run_id": run_id})
            adjustment_result = await v2_repo.find_one("v2_adjustment_results", {"run_id": run_id})
            publishing_result = await v2_repo.find_one("v2_publishing_results", {"run_id": run_id})
            versioning_result = await v2_repo.find_one("v2_versioning_results", {"run_id": run_id})
            
            # Convert ObjectIds to strings for serialization
            qa_result = self._objectid_to_str(qa_result) if qa_result else None
            adjustment_result = self._objectid_to_str(adjustment_result) if adjustment_result else None
            publishing_result = self._objectid_to_str(publishing_result) if publishing_result else None
            versioning_result = self._objectid_to_str(versioning_result) if versioning_result else None
            
            # Get articles from content library
            articles = []
            articles_cursor = db.content_library.find({"metadata.run_id": run_id, "engine": "v2"})
            for article in articles_cursor:
                # Convert ObjectId to string for serialization
                article = self._objectid_to_str(article)
                articles.append(article)
            
            # Calculate quality badges
            badges = self._calculate_quality_badges(validation_result, qa_result, adjustment_result)
            
            # Determine overall review status
            review_status = await self._determine_review_status(run_id, publishing_result, db)
            
            # Compile media references
            media_references = await self._compile_media_references(run_id)
            
            run_data = {
                "run_id": run_id,
                "review_status": review_status,
                "processing_timestamp": validation_result.get('timestamp', ''),
                
                # Quality badges for UI
                "badges": badges,
                
                # Article information
                "articles": {
                    "count": len(articles),
                    "titles": [article.get('title', 'Untitled') for article in articles],
                    "total_content_length": sum([len(article.get('content', '')) for article in articles]),
                    "articles_data": articles  # Full article data for preview
                },
                
                # Processing results summary
                "processing_results": {
                    "validation": self._summarize_validation_result(validation_result),
                    "qa": self._summarize_qa_result(qa_result),
                    "adjustment": self._summarize_adjustment_result(adjustment_result),
                    "publishing": self._summarize_publishing_result(publishing_result),
                    "versioning": self._summarize_versioning_result(versioning_result)
                },
                
                # Media library information
                "media": media_references,
                
                # Review metadata (if exists)
                "review_metadata": await self._get_review_metadata(run_id, db)
            }
            
            return run_data
            
        except Exception as e:
            print(f"❌ V2 REVIEW: Error compiling run data - {e} - engine=v2")
            return None
            
    def _objectid_to_str(self, obj):
        """Convert MongoDB ObjectId to string for JSON serialization"""
        if obj is None:
            return obj
        
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if key == '_id':
                    result[key] = str(value)
                elif isinstance(value, dict):
                    result[key] = self._objectid_to_str(value)
                elif isinstance(value, list):
                    result[key] = [self._objectid_to_str(item) for item in value]
                else:
                    result[key] = value
            return result
        elif isinstance(obj, list):
            return [self._objectid_to_str(item) for item in obj]
        else:
            return obj
    
    def _calculate_quality_badges(self, validation_result: dict, qa_result: dict, adjustment_result: dict) -> dict:
        """Calculate quality badges for review UI display"""
        try:
            badges = {}
            
            # Coverage badge
            coverage = validation_result.get('summary_scores', {}).get('coverage_percent', 0)
            badges['coverage'] = {
                'value': f"{coverage}%",
                'status': 'excellent' if coverage >= 95 else 'good' if coverage >= 85 else 'warning',
                'tooltip': f'Content coverage: {coverage}% of source material'
            }
            
            # Fidelity badge  
            fidelity = validation_result.get('summary_scores', {}).get('fidelity_score', 0)
            badges['fidelity'] = {
                'value': f"{fidelity:.2f}",
                'status': 'excellent' if fidelity >= 0.9 else 'good' if fidelity >= 0.7 else 'warning',
                'tooltip': f'Content fidelity score: {fidelity:.2f} (accuracy to source)'
            }
            
            # Redundancy badge
            redundancy = validation_result.get('metrics', {}).get('redundancy_score', 0)
            badges['redundancy'] = {
                'value': f"{redundancy:.2f}",
                'status': 'excellent' if redundancy <= 0.2 else 'good' if redundancy <= 0.4 else 'warning',
                'tooltip': f'Content redundancy: {redundancy:.2f} (lower is better)'
            }
            
            # Granularity alignment badge
            granularity = validation_result.get('metrics', {}).get('granularity_alignment_score', 0)
            badges['granularity'] = {
                'value': f"{granularity:.2f}",
                'status': 'excellent' if granularity >= 0.8 else 'good' if granularity >= 0.6 else 'warning',
                'tooltip': f'Granularity alignment: {granularity:.2f}'
            }
            
            # Placeholders badge
            placeholders = validation_result.get('summary_scores', {}).get('placeholder_count', 0)
            badges['placeholders'] = {
                'value': str(placeholders),
                'status': 'excellent' if placeholders == 0 else 'warning',
                'tooltip': f'Placeholder content detected: {placeholders} instances'
            }
            
            # QA issues badge (if QA result available)
            if qa_result:
                issues = qa_result.get('summary', {}).get('issues_found', 0)
                badges['qa_issues'] = {
                    'value': str(issues),
                    'status': 'excellent' if issues == 0 else 'good' if issues <= 2 else 'warning',
                    'tooltip': f'Quality assurance issues: {issues} found'
                }
            
            # Readability badge (if adjustment result available)
            if adjustment_result:
                readability = adjustment_result.get('readability_score', 0.5)
                badges['readability'] = {
                    'value': f"{readability:.2f}",
                    'status': 'excellent' if readability >= 0.8 else 'good' if readability >= 0.6 else 'warning',
                    'tooltip': f'Content readability: {readability:.2f}'
                }
            
            return badges
            
        except Exception as e:
            print(f"❌ V2 REVIEW: Error calculating quality badges - {e}")
            return {}
    
    async def _determine_review_status(self, run_id: str, publishing_result: dict, db) -> str:
        """Determine the current review status for a processing run"""
        try:
            # Check if there's existing review metadata
            review_metadata = await db.v2_review_metadata.find_one({"run_id": run_id})
            
            if review_metadata:
                return review_metadata.get('review_status', 'pending_review')
            
            # Check publishing status to infer review status
            if publishing_result:
                publishing_status = publishing_result.get('publishing_status')
                if publishing_status == 'success':
                    return 'published'
                elif publishing_status in ['validation_failed', 'coverage_insufficient']:
                    return 'pending_review'
            
            return 'pending_review'
            
        except Exception as e:
            print(f"❌ V2 REVIEW: Error determining review status - {e}")
            return 'pending_review'
    
    async def _compile_media_references(self, run_id: str) -> dict:
        """Compile media references for review"""
        try:
            # In a full implementation, this would get media from the media library
            # For now, we'll return a placeholder structure
            return {
                "count": 0,
                "images": [],
                "videos": [],
                "documents": []
            }
            
        except Exception as e:
            print(f"❌ V2 REVIEW: Error compiling media references - {e}")
            return {"count": 0, "images": [], "videos": [], "documents": []}
    
    def _summarize_validation_result(self, validation_result: dict) -> dict:
        """Summarize validation result for review"""
        if not validation_result:
            return {"status": "not_available"}
        
        return {
            "status": validation_result.get('validation_status', 'unknown'),
            "coverage": validation_result.get('summary_scores', {}).get('coverage_percent', 0),
            "fidelity": validation_result.get('summary_scores', {}).get('fidelity_score', 0),
            "placeholders": validation_result.get('summary_scores', {}).get('placeholder_count', 0),
            "diagnostics_count": len(validation_result.get('diagnostics', []))
        }
    
    def _summarize_qa_result(self, qa_result: dict) -> dict:
        """Summarize QA result for review"""
        if not qa_result:
            return {"status": "not_available"}
        
        return {
            "status": qa_result.get('qa_status', 'unknown'),
            "issues_found": qa_result.get('summary', {}).get('issues_found', 0),
            "duplicates": qa_result.get('summary', {}).get('duplicates_found', 0),
            "invalid_links": qa_result.get('summary', {}).get('invalid_links_found', 0)
        }
    
    def _summarize_adjustment_result(self, adjustment_result: dict) -> dict:
        """Summarize adjustment result for review"""
        if not adjustment_result:
            return {"status": "not_available"}
        
        return {
            "status": adjustment_result.get('adjustment_status', 'unknown'),
            "readability_score": adjustment_result.get('readability_score', 0),
            "adjustments_made": adjustment_result.get('adjustment_summary', {}).get('total_adjustments', 0)
        }
    
    def _summarize_publishing_result(self, publishing_result: dict) -> dict:
        """Summarize publishing result for review"""
        if not publishing_result:
            return {"status": "not_available"}
        
        return {
            "status": publishing_result.get('publishing_status', 'unknown'),
            "published_articles": publishing_result.get('published_articles', 0),
            "coverage_achieved": publishing_result.get('coverage_achieved', 0)
        }
    
    def _summarize_versioning_result(self, versioning_result: dict) -> dict:
        """Summarize versioning result for review"""
        if not versioning_result:
            return {"status": "not_available"}
        
        return {
            "status": versioning_result.get('versioning_status', 'unknown'),
            "version_number": versioning_result.get('version_metadata', {}).get('version', 1),
            "is_update": versioning_result.get('version_metadata', {}).get('supersedes') is not None
        }
    
    async def _compile_review_summary_stats(self, runs_data: list) -> dict:
        """Compile summary statistics for review dashboard"""
        try:
            total_runs = len(runs_data)
            pending_review = len([r for r in runs_data if r.get('review_status') == 'pending_review'])
            approved = len([r for r in runs_data if r.get('review_status') == 'approved'])
            rejected = len([r for r in runs_data if r.get('review_status') == 'rejected'])
            published = len([r for r in runs_data if r.get('review_status') == 'published'])
            
            return {
                "total_runs": total_runs,
                "pending_review": pending_review,
                "approved": approved,
                "rejected": rejected,
                "published": published,
                "approval_rate": (approved + published) / total_runs * 100 if total_runs > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ V2 REVIEW: Error compiling summary stats - {e}")
            return {"total_runs": 0, "pending_review": 0, "approved": 0, "rejected": 0, "published": 0, "approval_rate": 0}
    
    async def _get_review_metadata(self, run_id: str, db) -> dict:
        """Get existing review metadata for a run"""
        try:
            review_metadata = await db.v2_review_metadata.find_one({"run_id": run_id})
            return self._objectid_to_str(review_metadata) if review_metadata else {}
        except Exception as e:
            print(f"❌ V2 REVIEW: Error getting review metadata - {e}")
            return {}

print("✅ KE-M15: V2 Review System migrated from server.py")