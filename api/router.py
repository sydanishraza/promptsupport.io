"""
KE-PR8: API Router Split & Feature Flags (Kill Switches)
Centralized API routing with domain organization and feature flags for V1/Hybrid endpoints
"""

import os
import uuid
import asyncio
import mimetypes
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

# Feature flags for KE-PR8
ENABLE_V1 = os.getenv("ENABLE_V1", "false").lower() == "true"
ENABLE_HYBRID = os.getenv("ENABLE_HYBRID", "false").lower() == "true"

print(f"🚩 KE-PR8: Feature flags - V1: {ENABLE_V1}, Hybrid: {ENABLE_HYBRID}")

# Create main router
router = APIRouter()

# Import necessary models and dependencies from server
# These imports will be resolved when the router is included in server.py


# ========================================
# HEALTH & SYSTEM ROUTES
# ========================================

@router.get("/api/health")
def health():
    """System health check - always available"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "feature_flags": {
            "v1_enabled": ENABLE_V1,
            "hybrid_enabled": ENABLE_HYBRID
        }
    }


# ========================================
# CONTENT PROCESSING ROUTES (V2 Engine)
# ========================================

@router.post("/api/content/process")
async def process_content_v2_route(
    content: str = Form(...), 
    content_type: str = Form("text")
):
    """V2 Engine: Process text content through complete V2 pipeline"""
    try:
        print(f"🚀 V2 ENGINE: Processing content via API router - {len(content)} chars - engine=v2")
        
        # Import here to avoid circular imports
        import sys
        import os
        backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
        if backend_path not in sys.path:
            sys.path.append(backend_path)
        
        # Import the function from server
        sys.path.insert(0, backend_path)
        from server import process_text_content_v2_pipeline
        
        metadata = {
            "content_type": content_type,
            "source": "api_router",
            "engine": "v2"
        }
        
        articles = await process_text_content_v2_pipeline(content, metadata)
        
        if articles:
            return {
                "status": "completed",
                "articles": articles,
                "article_count": len(articles),
                "engine": "v2",
                "message": "Content processed successfully through V2 pipeline"
            }
        else:
            return {
                "status": "completed",
                "articles": [],
                "article_count": 0,
                "engine": "v2",
                "message": "Content processed but no articles generated"
            }
            
    except Exception as e:
        print(f"❌ V2 ENGINE: Error in content processing - {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/api/content/upload")
async def upload_content_v2_route(
    file: UploadFile = File(...),
    enable_audio_processing: bool = Form(False)
):
    """V2 Engine: Upload and process files through V2 pipeline"""
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    from server import process_file_upload_v2
    
    try:
        print(f"📁 V2 ENGINE: File upload via API router - {file.filename} - engine=v2")
        
        result = await process_file_upload_v2(file, enable_audio_processing)
        
        return {
            "status": "completed",
            "result": result,
            "engine": "v2",
            "filename": file.filename
        }
        
    except Exception as e:
        print(f"❌ V2 ENGINE: Error in file upload processing - {e}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.post("/api/content/process-url")
async def process_url_v2_route(
    url: str = Form(...),
    enable_audio_processing: bool = Form(False)
):
    """V2 Engine: Process URL content through V2 pipeline"""
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    from server import process_url_content_v2
    
    try:
        print(f"🌐 V2 ENGINE: URL processing via API router - {url} - engine=v2")
        
        result = await process_url_content_v2(url, enable_audio_processing)
        
        return {
            "status": "completed",
            "result": result,
            "engine": "v2",
            "url": url
        }
        
    except Exception as e:
        print(f"❌ V2 ENGINE: Error in URL processing - {e}")
        raise HTTPException(status_code=500, detail=f"URL processing failed: {str(e)}")


# ========================================
# CONTENT LIBRARY ROUTES  
# ========================================

@router.get("/api/content/library")
async def get_content_library():
    """Get all articles from content library using repository layer"""
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    try:
        # Try to use repository layer first
        from server import mongo_repo_available, RepositoryFactory
        
        if mongo_repo_available:
            content_repo = RepositoryFactory.get_content_library()
            articles = await content_repo.find_recent(limit=100)
            
            return {
                "articles": articles,
                "count": len(articles),
                "source": "repository_layer"
            }
        else:
            # KE-PR9: Try repository pattern first, then fallback
            try:
                from app.engine.stores.mongo import RepositoryFactory
                content_repo = RepositoryFactory.get_content_library()
                articles = await content_repo.find_recent(limit=100)
            except Exception as repo_error:
                print(f"❌ KE-PR9.3: Repository access failed - {repo_error}")
                raise HTTPException(status_code=500, detail=f"Database access failed: {str(repo_error)}")
            
            return {
                "articles": articles,
                "count": len(articles),
                "source": "direct_database"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching library: {str(e)}")

@router.post("/api/content-library")
async def create_article():
    """Create new article - V1 route with feature flag"""
    if not ENABLE_V1:
        raise HTTPException(
            status_code=410, 
            detail="V1 endpoints are disabled. This functionality has been deprecated."
        )
    
    from backend.server import SaveArticleRequest
    
    # V1 implementation would go here
    return {"message": "V1 article creation (deprecated)"}

@router.put("/api/content-library/{article_id}")
async def update_article(article_id: str):
    """Update article - V1 route with feature flag"""
    if not ENABLE_V1:
        raise HTTPException(
            status_code=410,
            detail="V1 endpoints are disabled. Use V2 content processing instead."
        )
    
    # V1 implementation would go here
    return {"message": f"V1 article update for {article_id} (deprecated)"}

@router.delete("/api/content/library/{article_id}")
async def delete_article(article_id: str):
    """Delete article from content library using repository layer"""
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    try:
        # Try to use repository layer first
        from server import mongo_repo_available, RepositoryFactory
        
        if mongo_repo_available:
            content_repo = RepositoryFactory.get_content_library()
            success = await content_repo.delete_by_id(article_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Article not found")
            
            return {"message": "Article deleted successfully", "source": "repository_layer"}
        else:
            # KE-PR9: Try repository pattern first, then fallback  
            try:
                from app.engine.stores.mongo import RepositoryFactory
                content_repo = RepositoryFactory.get_content_library()
                success = await content_repo.delete_by_id(article_id)
                
                if not success:
                    raise HTTPException(status_code=404, detail="Article not found")
                
                return {"message": "Article deleted successfully", "source": "repository_layer_fallback"}
            except Exception as repo_error:
                print(f"⚠️ KE-PR9: Repository fallback to direct DB access: {repo_error}")
                # Final fallback to direct database access
                from server import db
                result = await db.content_library.delete_one({"id": article_id})
                
                if result.deleted_count == 0:
                    raise HTTPException(status_code=404, detail="Article not found")
                
                return {"message": "Article deleted successfully", "source": "direct_database"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting article: {str(e)}")


# ========================================
# ASSETS MANAGEMENT ROUTES
# ========================================

@router.get("/api/assets")
async def get_assets():
    """Get all assets"""
    try:
        # Use static directory from backend
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'static')
        upload_dir = os.path.join(static_dir, 'uploads')
        
        assets = []
        
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    assets.append({
                        "id": filename,
                        "filename": filename,
                        "size": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "type": mimetypes.guess_type(filename)[0] or "unknown"
                    })
        
        return {"assets": assets, "count": len(assets)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching assets: {str(e)}")

@router.post("/api/assets/upload")
async def upload_asset(file: UploadFile = File(...)):
    """Upload asset file"""
    try:
        # Use static directory from backend
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'static')
        upload_dir = os.path.join(static_dir, 'uploads')
        
        # Ensure upload directory exists
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "message": "Asset uploaded successfully",
            "asset_id": unique_filename,
            "filename": file.filename,
            "size": len(content),
            "type": file.content_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading asset: {str(e)}")

@router.delete("/api/assets/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete asset file"""
    try:
        # Use static directory from backend
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'static')
        upload_dir = os.path.join(static_dir, 'uploads')
        file_path = os.path.join(upload_dir, asset_id)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Asset not found")
        
        os.remove(file_path)
        
        return {"message": "Asset deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting asset: {str(e)}")

@router.get("/api/assets/{asset_id}")
async def get_asset(asset_id: str):
    """Get asset file"""
    try:
        # Use static directory from backend
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'static')
        upload_dir = os.path.join(static_dir, 'uploads')
        file_path = os.path.join(upload_dir, asset_id)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return FileResponse(
            path=file_path,
            filename=asset_id,
            media_type=mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving asset: {str(e)}")


# ========================================
# ENGINE STATUS & DIAGNOSTICS ROUTES
# ========================================

@router.get("/api/engine")
async def get_engine_status():
    """V2 Engine status with QA summaries"""
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    from server import get_recent_qa_summaries
    
    try:
        # Get QA summaries
        qa_summaries = await get_recent_qa_summaries(limit=5)
        
        return {
            "engine": "v2",
            "legacy": "disabled",
            "status": "active",
            "version": "2.0",
            "feature_flags": {
                "v1_enabled": ENABLE_V1,
                "hybrid_enabled": ENABLE_HYBRID
            },
            "endpoints": {
                "text_processing": "/api/content/process",
                "file_upload": "/api/content/upload",
                "url_processing": "/api/content/process-url",
                "content_library": "/api/content/library",
                "assets": "/api/assets",
                "engine_status": "/api/engine",
                "health_check": "/api/health"
            },
            "features": [
                "v2_processing_pipeline",
                "machine_readable_qa_reports",
                "publish_gates_p0_blocking",
                "centralized_llm_client",
                "api_router_organization",
                "feature_flags_kill_switches",
                "domain_based_routing"
            ],
            "qa_summaries": qa_summaries,
            "qa_summary_count": len(qa_summaries),
            "message": "V2 Engine active with organized API routing and feature flags"
        }
        
    except Exception as e:
        return {
            "engine": "v2",
            "status": "error",
            "error": str(e),
            "feature_flags": {
                "v1_enabled": ENABLE_V1,
                "hybrid_enabled": ENABLE_HYBRID
            }
        }


# ========================================
# VALIDATION & QA DIAGNOSTICS ROUTES
# ========================================

@router.get("/api/validation/diagnostics")
async def get_validation_diagnostics(run_id: str = None, validation_id: str = None):
    """V2 Validation diagnostics"""
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    from server import db
    
    try:
        query_filter = {}
        if run_id:
            query_filter["run_id"] = run_id
        if validation_id:
            query_filter["validation_id"] = validation_id
        
        if not db:
            return {
                "total_validations": 0,
                "validation_results": [],
                "message": "Database not initialized"
            }
        
        # KE-PR9: Use repository pattern for validation results
        try:
            from app.engine.stores.mongo import RepositoryFactory
            validation_repo = RepositoryFactory.get_v2_validation()
            
            if not query_filter:
                validation_results = await validation_repo.find_validations(limit=10)
            else:
                validation_results = await validation_repo.find_validations(query_filter, limit=100)
                
        except Exception as repo_error:
            print(f"⚠️ KE-PR9: Validation repo fallback to direct DB access: {repo_error}")
            # Fallback to direct database access
            if not query_filter:
                try:
                    validation_results = await db.v2_validation_results.find().sort("timestamp", -1).limit(10).to_list(10)
                except Exception as db_error:
                    # Collection might not exist yet
                    validation_results = []
            else:
                try:
                    validation_results = await db.v2_validation_results.find(query_filter).sort("timestamp", -1).to_list(100)
                except Exception as db_error:
                    validation_results = []
            
            # Convert ObjectId to string for fallback case
            for result in validation_results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
                result['_id'] = str(result['_id'])
        
        return {
            "total_validations": len(validation_results),
            "passed_validations": len([r for r in validation_results if r.get('validation_status') == 'passed']),
            "validation_results": validation_results
        }
        
    except Exception as e:
        return {
            "total_validations": 0,
            "validation_results": [],
            "error": str(e)
        }

@router.get("/api/qa/diagnostics")
async def get_qa_diagnostics(run_id: str = None, qa_id: str = None):
    """V2 QA diagnostics using repository layer"""
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    
    try:
        # Try to use repository layer first
        from server import mongo_repo_available, RepositoryFactory
        
        if mongo_repo_available:
            qa_repo = RepositoryFactory.get_qa_results()
            
            if run_id:
                qa_results = await qa_repo.find_by_job_id(run_id)
            else:
                qa_results = await qa_repo.find_recent_qa_summaries(limit=10)
            
            return {
                "total_qa_runs": len(qa_results),
                "passed_qa_runs": len([r for r in qa_results if len(r.get('flags', [])) == 0]),
                "qa_runs_with_issues": len([r for r in qa_results if len(r.get('flags', [])) > 0]),
                "qa_results": qa_results,
                "source": "repository_layer"
            }
        else:
            # Fallback to direct database access
            from server import qa_results_collection
            
            query_filter = {}
            if run_id:
                query_filter["job_id"] = run_id
            if qa_id:
                query_filter["qa_id"] = qa_id
            
            if not qa_results_collection:
                return {
                    "total_qa_runs": 0,
                    "qa_results": [],
                    "message": "QA results collection not initialized",
                    "source": "direct_database"
                }
            
            if not query_filter:
                try:
                    qa_results = await qa_results_collection.find().sort("created_at", -1).limit(10).to_list(10)
                except Exception as db_error:
                    qa_results = []
            else:
                try:
                    qa_results = await qa_results_collection.find(query_filter).sort("created_at", -1).to_list(100)
                except Exception as db_error:
                    qa_results = []
            
            # Convert ObjectId to string
            for result in qa_results:
                if '_id' in result:
                    result['_id'] = str(result['_id'])
            
            return {
                "total_qa_runs": len(qa_results),
                "passed_qa_runs": len([r for r in qa_results if len(r.get('flags', [])) == 0]),
                "qa_runs_with_issues": len([r for r in qa_results if len(r.get('flags', [])) > 0]),
                "qa_results": qa_results,
                "source": "direct_database"
            }
        
    except Exception as e:
        return {
            "total_qa_runs": 0,
            "qa_results": [],
            "error": str(e),
            "source": "error_fallback"
        }


# ========================================
# V1 LEGACY ROUTES (WITH KILL SWITCHES)
# ========================================

@router.post("/api/ai-assistance")
async def ai_assistance_v1():
    """V1 AI Assistance - Legacy route with kill switch"""
    if not ENABLE_V1:
        raise HTTPException(
            status_code=410,
            detail="V1 AI assistance endpoints are disabled. Use V2 content processing instead."
        )
    
    # V1 implementation would go here
    return {"message": "V1 AI assistance (deprecated)"}

@router.post("/api/content-analysis")
async def content_analysis_v1():
    """V1 Content Analysis - Legacy route with kill switch"""
    if not ENABLE_V1:
        raise HTTPException(
            status_code=410,
            detail="V1 content analysis endpoints are disabled. Use V2 multi-dimensional analysis instead."
        )
    
    # V1 implementation would go here
    return {"message": "V1 content analysis (deprecated)"}


# ========================================
# HYBRID ROUTES (V1/V2 COMPATIBILITY)
# ========================================

@router.get("/api/content/export")
async def export_content_hybrid():
    """Hybrid content export - requires hybrid flag"""
    if not ENABLE_HYBRID:
        raise HTTPException(
            status_code=410,
            detail="Hybrid endpoints are disabled. Use V2-native content processing."
        )
    
    # Hybrid implementation would go here
    return {"message": "Hybrid content export (compatibility mode)"}


# ========================================
# TRAINING & MODEL ROUTES
# ========================================

@router.post("/api/training/start")
async def start_training():
    """Start training process - V1 route with kill switch"""
    if not ENABLE_V1:
        raise HTTPException(
            status_code=410,
            detail="V1 training endpoints are disabled. Training functionality has been integrated into V2 pipeline."
        )
    
    return {"message": "V1 training (deprecated)"}

@router.get("/api/training/status")
async def get_training_status():
    """Get training status - V1 route with kill switch"""
    if not ENABLE_V1:
        raise HTTPException(
            status_code=410,
            detail="V1 training endpoints are disabled."
        )
    
    return {"message": "V1 training status (deprecated)"}


# ========================================
# STYLE & FORMATTING ROUTES
# ========================================

@router.post("/api/style/apply")
async def apply_style():
    """Apply style - V1 route with kill switch"""
    if not ENABLE_V1:
        raise HTTPException(
            status_code=410,
            detail="V1 style endpoints are disabled. Use V2 Woolf-aligned style processing."
        )
    
    return {"message": "V1 style application (deprecated)"}

@router.get("/api/style/templates")
async def get_style_templates():
    """Get style templates - V1 route with kill switch"""
    if not ENABLE_V1:
        raise HTTPException(
            status_code=410,
            detail="V1 style templates are disabled. V2 uses integrated Woolf guidelines."
        )
    
    return {"message": "V1 style templates (deprecated)"}


# ========================================
# TICKET3 BOOKMARKS & LINKING ROUTES
# ========================================

@router.get("/api/bookmarks")
async def get_bookmarks():
    """Get bookmarks registry - Ticket3 functionality"""
    try:
        from app.engine.linking.bookmarks import get_registry
        
        registry = get_registry()
        return {
            "bookmarks": registry,
            "count": len(registry),
            "engine": "v2_ticket3"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bookmarks: {str(e)}")

@router.post("/api/bookmarks/backfill")
async def backfill_bookmarks():
    """Backfill bookmarks registry - Ticket3 functionality"""  
    try:
        from app.engine.linking.bookmarks import backfill_registry
        
        result = backfill_registry()
        return {
            "message": "Bookmarks registry backfilled",
            "result": result,
            "engine": "v2_ticket3"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error backfilling bookmarks: {str(e)}")

@router.get("/api/links/build")
async def build_link(doc_uid: str, anchor_id: str, environment: str = "production"):
    """Build environment-aware link - Ticket3 functionality"""
    try:
        from app.engine.linking.links import build_link
        
        link = build_link(doc_uid, anchor_id, environment)
        return {
            "link": link,
            "doc_uid": doc_uid,
            "anchor_id": anchor_id,
            "environment": environment,
            "engine": "v2_ticket3"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building link: {str(e)}")


# ========================================
# MISC ROUTES
# ========================================

@router.get("/")
async def root():
    """Root endpoint"""
    return HTMLResponse("""
    <html>
        <head><title>PromptSupport V2 Engine</title></head>
        <body>
            <h1>PromptSupport V2 Content Processing Engine</h1>
            <p>API Routes organized with KE-PR8 Router Architecture</p>
            <ul>
                <li><a href="/api/health">Health Check</a></li>
                <li><a href="/api/engine">Engine Status</a></li>
                <li><a href="/api/content/library">Content Library</a></li>
            </ul>
            <p>Feature Flags: V1={}, Hybrid={}</p>
        </body>
    </html>
    """.format(ENABLE_V1, ENABLE_HYBRID))

# ========================================
# ERROR HANDLERS
# ========================================

def create_410_response(feature_name: str) -> HTTPException:
    """Create standardized 410 Gone response for disabled features"""
    return HTTPException(
        status_code=410,
        detail=f"{feature_name} has been disabled. Please use V2 endpoints instead."
    )


# ========================================
# ROUTER CONFIGURATION
# ========================================

# Add any additional middleware or configuration here
print(f"✅ KE-PR8: API Router initialized with {len(router.routes)} routes")
print(f"🚩 KE-PR8: Feature flags - V1 endpoints: {'ENABLED' if ENABLE_V1 else 'DISABLED'}")
print(f"🚩 KE-PR8: Feature flags - Hybrid endpoints: {'ENABLED' if ENABLE_HYBRID else 'DISABLED'}")