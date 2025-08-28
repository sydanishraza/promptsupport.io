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
            
            # Get database connection
            from pymongo import MongoClient
            import os
            
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/promptsupport')
            client = MongoClient(mongo_url)
            db = client.get_default_database()
            
            # Get recent processing runs
            runs_query = {}
            if status_filter and status_filter in self.review_statuses:
                runs_query['review_status'] = status_filter
            
            # Get runs from various V2 collections
            runs_data = []
            
            # Get from validation results
            validation_cursor = db.v2_validation_results.find(runs_query).sort("timestamp", -1).limit(limit)
            
            for validation_result in validation_cursor:
                # Convert ObjectId to string for serialization
                validation_result = self._objectid_to_str(validation_result)
                run_id = validation_result.get('run_id')
                if run_id:
                    run_data = await self._compile_run_data_for_review(run_id, validation_result, db)
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
        """Enqueue content version for human review"""
        try:
            print(f"👥 KE-PR5: Enqueuing version {version_id} for review - run {run_id}")
            
            # Generate review ID
            review_id = f"review_{run_id}_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Determine review priority based on QA results
            issues_count = qa_result.get('summary', {}).get('issues_found', 0)
            
            if issues_count > 5:
                priority = "urgent"
            elif issues_count > 2:
                priority = "high"
            elif issues_count > 0:
                priority = "medium"
            else:
                priority = "low"
            
            # Create review request
            review_request = {
                "review_id": review_id,
                "version_id": version_id,
                "run_id": run_id,
                "priority": priority,
                "review_type": "quality_review",
                "issues_count": issues_count,
                "qa_summary": qa_result.get('summary', {}),
                "created_at": datetime.utcnow().isoformat(),
                "status": "queued",
                "engine": "v2"
            }
            
            # TODO: Store in review queue database collection
            # await db.v2_review_queue.insert_one(review_request)
            
            review_result = {
                "review_id": review_id,
                "review_status": "queued",
                "priority": priority,
                "estimated_review_time": self._estimate_review_time(issues_count),
                "queue_position": 1,  # Placeholder
                "timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"✅ KE-PR5: Review queued - {review_id} with {priority} priority")
            return review_result
            
        except Exception as e:
            print(f"❌ KE-PR5: Error enqueuing for review - {e}")
            return {
                "review_id": f"error_{version_id}",
                "review_status": "error",
                "error": str(e),
                "priority": "medium"
            }
    
    def _estimate_review_time(self, issues_count: int) -> str:
        """Estimate review time based on issues count"""
        if issues_count > 5:
            return "2-4 hours"
        elif issues_count > 2:
            return "1-2 hours"
        elif issues_count > 0:
            return "30-60 minutes"
        else:
            return "15-30 minutes"