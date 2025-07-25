#!/usr/bin/env python3
"""
PromptSupport Enhanced Content Engine Backend
FastAPI server with AI integrations for content processing
"""

import os
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import io
import base64

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import motor.motor_asyncio
from pymongo import MongoClient
import aiofiles
from dotenv import load_dotenv
import requests
import httpx
import re
from bs4 import BeautifulSoup
from media_intelligence import media_intelligence

# Load environment variables
load_dotenv()

# Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "promptsupport_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Initialize FastAPI app
app = FastAPI(
    title="PromptSupport Enhanced Content Engine",
    description="AI-native content processing and management system",
    version="1.0.0"
)

# Mount static files for serving uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients
mongo_client = None
db = None
content_library_collection = None

# Pydantic Models
class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProcessingJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "processing"  # processing, completed, failed
    input_type: str  # text, audio, video, url, image
    original_filename: Optional[str] = None
    chunks: List[DocumentChunk] = []
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class ContentProcessRequest(BaseModel):
    content: str
    content_type: str = "text"
    metadata: Dict[str, Any] = {}

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    filter_metadata: Optional[Dict[str, Any]] = None

class AIAssistanceRequest(BaseModel):
    content: str
    mode: str = "completion"  # completion, improvement, grammar, analysis
    context: Optional[str] = None

class SaveArticleRequest(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    status: str = "draft"  # draft, published

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize all services and connections"""
    global mongo_client, db, content_library_collection
    
    print("🚀 Starting PromptSupport Enhanced Content Engine...")
    
    # Initialize MongoDB
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        db = mongo_client[DATABASE_NAME]
        content_library_collection = db.content_library
        # Test the connection
        await mongo_client.server_info()
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise
    
    # Check API keys
    if OPENAI_API_KEY:
        print("✅ OpenAI API key configured")
    if ANTHROPIC_API_KEY:
        print("✅ Anthropic API key configured")
    if ASSEMBLYAI_API_KEY:
        print("✅ AssemblyAI API key configured")
    if QDRANT_API_KEY:
        print("✅ Qdrant API key configured")
    
    print("🎉 Enhanced Content Engine started successfully!")

@app.post("/api/ai-assistance")
async def ai_assistance(request: AIAssistanceRequest):
    """Provide AI writing assistance using OpenAI"""
    try:
        if not OPENAI_API_KEY:
            return {"error": "OpenAI API key not configured", "suggestions": []}
        
        # Prepare prompt based on mode
        prompts = {
            "completion": f"Continue this text naturally and coherently:\n\n{request.content}\n\nContinuation:",
            "improvement": f"Analyze this text and suggest specific improvements for clarity, engagement, and readability:\n\n{request.content}\n\nSuggestions:",
            "grammar": f"Check this text for grammar, spelling, and style issues and provide corrections:\n\n{request.content}\n\nCorrections:",
            "analysis": f"Analyze this content for readability, structure, tone, and provide insights:\n\n{request.content}\n\nAnalysis:"
        }
        
        prompt = prompts.get(request.mode, prompts["completion"])
        
        # Make request to OpenAI
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are a helpful writing assistant. Provide clear, actionable suggestions."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Split response into suggestions
                suggestions = [s.strip() for s in ai_response.split('\n') if s.strip()]
                
                return {
                    "suggestions": suggestions[:3],  # Limit to 3 suggestions
                    "mode": request.mode,
                    "success": True
                }
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return {"error": "AI service temporarily unavailable", "suggestions": []}
                
    except Exception as e:
        print(f"AI assistance error: {str(e)}")
        return {"error": str(e), "suggestions": []}

@app.post("/api/content-analysis")
async def content_analysis(request: AIAssistanceRequest):
    """Analyze content for insights using OpenAI"""
    try:
        if not OPENAI_API_KEY:
            return {"error": "OpenAI API key not configured"}
        
        # Strip HTML tags for analysis
        text_content = re.sub(r'<[^>]*>', '', request.content)
        
        # Basic metrics
        words = len(text_content.split())
        sentences = len([s for s in re.split(r'[.!?]+', text_content) if s.strip()])
        paragraphs = len([p for p in text_content.split('\n\n') if p.strip()])
        
        # Get AI analysis
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": "You are a content analysis expert. Provide readability score (0-100), tone assessment, and key insights."},
                        {"role": "user", "content": f"Analyze this content:\n\n{text_content[:1000]}"}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.3
                }
            )
            
            ai_insights = ""
            readability_score = 70  # Default
            
            if response.status_code == 200:
                result = response.json()
                ai_insights = result["choices"][0]["message"]["content"]
                
                # Extract readability score if mentioned
                score_match = re.search(r'readability.*?(\d+)', ai_insights, re.IGNORECASE)
                if score_match:
                    readability_score = int(score_match.group(1))
        
        return {
            "wordCount": words,
            "sentences": sentences,
            "paragraphs": paragraphs,
            "readingTime": max(1, words // 200),  # Avg 200 words per minute
            "readabilityScore": readability_score,
            "characterCount": len(text_content),
            "aiInsights": ai_insights,
            "success": True
        }
        
    except Exception as e:
        print(f"Content analysis error: {str(e)}")
        return {"error": str(e)}

@app.put("/api/content-library/{article_id}")
async def update_article(article_id: str, request: SaveArticleRequest):
    """Update an existing article"""
    try:
        collection = db["content_library"]
        
        update_data = {
            "title": request.title,
            "content": request.content,
            "status": request.status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await collection.update_one(
            {"id": article_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
            
        return {"success": True, "message": f"Article {request.status}"}
        
    except Exception as e:
        print(f"Update article error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content-library")
async def create_article(request: SaveArticleRequest):
    """Create a new article"""
    try:
        collection = db["content_library"]
        
        article_data = {
            "id": str(uuid.uuid4()),
            "title": request.title,
            "content": request.content,
            "status": request.status,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "type": "article"
        }
        
        await collection.insert_one(article_data)
        
        return {"success": True, "id": article_data["id"], "message": f"Article {request.status}"}
        
    except Exception as e:
        print(f"Create article error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assets")
async def get_assets():
    """Get all assets from the asset library including embedded images from articles"""
    try:
        collection = db["content_library"]
        
        # Get direct image assets
        direct_assets_cursor = collection.find({"type": {"$in": ["image", "media"]}})
        direct_assets = await direct_assets_cursor.to_list(length=100)
        
        # Get articles with embedded images
        articles_cursor = collection.find({"content": {"$regex": "data:image", "$options": "i"}})
        articles_with_images = await articles_cursor.to_list(length=200)
        
        formatted_assets = []
        
        # Add direct assets
        for asset in direct_assets:
            if asset.get("data"):
                formatted_assets.append({
                    "id": asset.get("id", str(asset.get("_id"))),
                    "name": asset.get("title", asset.get("name", "Untitled")),
                    "type": "image",
                    "data": asset.get("data"),
                    "created_at": asset.get("created_at"),
                    "size": len(asset.get("data", "")) if asset.get("data") else 0
                })
        
        # Extract images from articles
        import re
        for article in articles_with_images:
            content = article.get("content", "")
            if content:
                # Find all base64 images in content using multiple patterns
                patterns = [
                    r'(data:image/[^;]+;base64,[A-Za-z0-9+/=]+)',  # Standard pattern
                    r'(data:image/[^;]+;base64,[^)\\s]+)',         # Match until ) or whitespace
                    r'(data:image/[^;]+;base64,[^)]+)',           # Match until )
                ]
                
                image_matches = []
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    image_matches.extend(matches)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_matches = []
                for match in image_matches:
                    if match not in seen:
                        seen.add(match)
                        unique_matches.append(match)
                
                for i, image_data in enumerate(unique_matches):
                    # Skip very small images (likely placeholders) but be more lenient
                    if len(image_data) > 50:  # Reduced from 100 to 50
                        asset_id = f"{article.get('id', str(article.get('_id')))}_img_{i}"
                        asset_name = f"Image from {article.get('title', 'article')[:30]}"
                        
                        # Check if this asset is already added
                        if not any(a.get('id') == asset_id for a in formatted_assets):
                            formatted_assets.append({
                                "id": asset_id,
                                "name": asset_name,
                                "type": "image", 
                                "data": image_data,
                                "created_at": article.get("created_at"),
                                "size": len(image_data)
                            })
        
        # Sort by creation date (newest first) - handle mixed datetime/string types
        def safe_sort_key(asset):
            created_at = asset.get('created_at', '')
            if isinstance(created_at, str):
                return created_at
            elif hasattr(created_at, 'isoformat'):
                return created_at.isoformat()
            else:
                return ''
        
        formatted_assets.sort(key=safe_sort_key, reverse=True)
        
        return {"assets": formatted_assets, "total": len(formatted_assets)}
        
    except Exception as e:
        print(f"Get assets error: {str(e)}")
        return {"assets": [], "total": 0}

@app.post("/api/assets/upload")
async def upload_asset(file: UploadFile = File(...)):
    """Upload an asset to the asset library with proper file storage"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else 'jpg'
        unique_filename = f"{str(uuid.uuid4())}.{file_extension}"
        file_path = f"static/uploads/{unique_filename}"
        
        # Ensure upload directory exists
        os.makedirs("static/uploads", exist_ok=True)
        
        # Save file to disk
        file_data = await file.read()
        
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(file_data)
        
        # Generate URL for the file
        file_url = f"/static/uploads/{unique_filename}"
        
        # Save metadata to database
        collection = db["assets"]
        
        asset_data = {
            "id": str(uuid.uuid4()),
            "original_filename": file.filename,
            "filename": unique_filename,
            "title": file.filename,
            "name": file.filename,
            "type": "image",
            "url": file_url,
            "file_path": file_path,
            "content_type": file.content_type,
            "size": len(file_data),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await collection.insert_one(asset_data)
        
        return {
            "success": True,
            "asset": {
                "id": asset_data["id"],
                "name": asset_data["name"],
                "type": asset_data["type"],
                "url": file_url,
                "original_filename": file.filename,
                "size": len(file_data)
            }
        }
        
    except Exception as e:
        print(f"Upload asset error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "mongodb": "connected" if mongo_client else "disconnected",
            "openai": "configured" if OPENAI_API_KEY else "not configured",
            "anthropic": "configured" if ANTHROPIC_API_KEY else "not configured",
            "assemblyai": "configured" if ASSEMBLYAI_API_KEY else "not configured",
            "qdrant": "configured" if QDRANT_API_KEY else "not configured"
        }
    }

# Status endpoint
@app.get("/api/status")
async def get_status():
    """Get system status and statistics"""
    try:
        # Get document count from MongoDB
        doc_count = await db.documents.count_documents({})
        job_count = await db.processing_jobs.count_documents({})
        
        return {
            "status": "operational",
            "message": "Enhanced Content Engine running",
            "statistics": {
                "total_documents": doc_count,
                "processing_jobs": job_count,
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content processing endpoint
@app.post("/api/content/process")
async def process_content(request: ContentProcessRequest):
    """Process text content with AI"""
    try:
        job = ProcessingJob(
            input_type=request.content_type,
            status="processing"
        )
        
        # Store job in database
        await db.processing_jobs.insert_one(job.dict())
        
        # Process content based on type
        if request.content_type == "text":
            chunks = await process_text_content(request.content, request.metadata)
        else:
            raise HTTPException(status_code=400, detail=f"Content type {request.content_type} not supported yet")
        
        # Update job with results
        job.chunks = chunks
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        
        await db.processing_jobs.update_one(
            {"job_id": job.job_id},
            {"$set": job.dict()}
        )
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "chunks_created": len(chunks),
            "message": "Content processed successfully"
        }
        
    except Exception as e:
        # Update job with error
        if 'job' in locals():
            await db.processing_jobs.update_one(
                {"job_id": job.job_id},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )
        raise HTTPException(status_code=500, detail=str(e))

async def process_text_content(content: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
    """Process text content into chunks"""
    try:
        # Simple chunking strategy (split by sentences, max 500 chars)
        sentences = content.split('.')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) > 500 and current_chunk:
                # Create chunk
                chunk_text = current_chunk.strip()
                if chunk_text:
                    chunk = DocumentChunk(
                        content=chunk_text,
                        metadata=metadata
                    )
                    chunks.append(chunk)
                    
                    # Store chunk in database
                    await db.document_chunks.insert_one(chunk.dict())
                
                current_chunk = sentence
            else:
                current_chunk += sentence + "."
        
        # Handle remaining content
        if current_chunk.strip():
            chunk_text = current_chunk.strip()
            chunk = DocumentChunk(
                content=chunk_text,
                metadata=metadata
            )
            chunks.append(chunk)
            await db.document_chunks.insert_one(chunk.dict())
        
        # After processing chunks, create Content Library article
        try:
            await create_content_library_article_from_chunks(chunks, metadata)
        except Exception as e:
            print(f"Warning: Could not create Content Library article: {e}")
        
        return chunks
        
    except Exception as e:
        print(f"Error processing text content: {e}")
        raise

async def create_content_library_article_from_chunks(chunks: List[DocumentChunk], metadata: Dict[str, Any]):
    """Create structured articles in Content Library from processed chunks"""
    if not chunks:
        return
    
    # Combine chunk content
    full_content = "\n".join([chunk.content for chunk in chunks])
    
    # Generate title from content or metadata
    title = metadata.get('original_filename', metadata.get('url', 'Processed Content'))
    if title.startswith('Website:'):
        title = title.replace('Website: ', '')
    
    source_type = metadata.get('type', 'text_processing')
    file_extension = metadata.get('file_extension', '')
    
    # Determine if we should create multiple articles based on content structure
    should_create_multiple = await should_split_into_multiple_articles(full_content, file_extension)
    
    if should_create_multiple:
        articles = await create_multiple_articles_from_content(full_content, metadata)
        for article in articles:
            await db.content_library.insert_one(article)
            print(f"✅ Created AI-enhanced Content Library article: '{article['title']}'")
        return articles
    else:
        # Create single comprehensive article
        article = await create_single_article_from_content(full_content, metadata)
        if article:
            print(f"🔍 DEBUG: Before DB insert - article keys: {list(article.keys())}")
            print(f"🔍 DEBUG: Before DB insert - has content: {'content' in article}")
            print(f"🔍 DEBUG: Before DB insert - content preview: {article.get('content', 'NO CONTENT')[:100]}...")
            await db.content_library.insert_one(article)
            print(f"✅ Created AI-enhanced Content Library article: '{article['title']}'")
            return [article]
        else:
            # Fallback: Create basic article without AI enhancement
            return await create_basic_fallback_article(full_content, metadata)

async def should_split_into_multiple_articles(content: str, file_extension: str) -> bool:
    """Determine if content should be split into multiple articles"""
    # Enhanced rules for splitting - more permissive to enable better content generation
    # 1. Documents with clear sections (even if shorter)
    # 2. Documents with multiple headings
    # 3. Presentations (each slide becomes an article)
    # 4. Spreadsheets with multiple sheets
    # 5. Documents with distinct topics or chapters
    
    if len(content) < 1000:  # Lowered threshold
        return False
    
    # Always split presentations
    if file_extension in ['ppt', 'pptx']:
        return True
    
    # Always split multi-sheet spreadsheets
    if file_extension in ['xls', 'xlsx'] and 'Sheet:' in content:
        return True
    
    # Check for multiple headings/sections (more comprehensive patterns)
    heading_patterns = [
        '===', '##', '# ', 
        'Chapter', 'Section', 'Part ', 'Module',
        'Overview', 'Introduction', 'Conclusion',
        'Getting Started', 'Configuration', 'Setup',
        'Administration', 'Management', 'Process',
        'Step ', 'Phase ', 'Stage '
    ]
    
    heading_count = 0
    content_lower = content.lower()
    
    for pattern in heading_patterns:
        heading_count += content_lower.count(pattern.lower())
    
    # Check for document structure indicators
    has_table_of_contents = any(toc in content_lower for toc in ['table of contents', 'contents:', 'index:'])
    has_multiple_sections = content.count('\n\n') > 10  # Multiple paragraph breaks
    has_enumerated_sections = len([line for line in content.split('\n') if line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]) > 3
    
    # More permissive splitting logic
    return (
        heading_count >= 2 or  # Just 2 headings needed
        has_table_of_contents or
        (has_multiple_sections and len(content) > 2000) or
        has_enumerated_sections or
        len(content) > 8000  # Very long documents should always be split
    )

async def create_multiple_articles_from_content(content: str, metadata: Dict[str, Any]) -> List[Dict]:
    """Create multiple structured articles from content"""
    if not OPENAI_API_KEY:
        return await create_basic_fallback_article(content, metadata)
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Enhanced prompt for comprehensive article generation
        prompt = f"""
        You are an expert technical writer and content strategist creating a comprehensive knowledge base from this document. Your goal is to transform the raw content into multiple, well-structured, production-ready articles that feel like they were written by a professional technical writer.

        IMPORTANT: This content contains embedded media (images, diagrams, charts) that MUST be preserved and included in the generated articles.

        Original Content:
        {content[:15000]}

        TRANSFORMATION REQUIREMENTS:

        1. **Content Analysis & Splitting**:
           - Identify all distinct topics, chapters, sections, or processes
           - Create 3-8 focused articles (depending on content richness)
           - Each article should cover ONE specific topic/process in depth
           - Split logically by function, process, or conceptual area

        2. **Media Preservation & Integration**:
           - PRESERVE all embedded images, charts, diagrams, and media exactly as they appear
           - Include ALL data URLs (data:image/jpeg;base64,... or data:image/png;base64,...)
           - Maintain image captions and context
           - Place images strategically within article content for maximum relevance
           - Reference images in the text when appropriate (e.g., "As shown in the diagram below...")

        3. **Content Enhancement & Rewriting**:
           - Completely rewrite content for clarity, flow, and technical accuracy
           - Add context, explanations, and helpful details where needed
           - Improve technical language while maintaining original intent
           - Add transitions and logical connections between concepts
           - Include troubleshooting tips, best practices, and common scenarios

        4. **Professional Structure & Formatting**:
           - Use comprehensive markdown formatting with proper headings hierarchy
           - Create detailed outlines with multiple heading levels (H1, H2, H3, H4)
           - Add bullet points, numbered lists, and checklists where appropriate
           - Include tables for data presentation when relevant
           - Add callouts, notes, warnings, and tips using markdown blockquotes
           - Create step-by-step procedures with clear numbering
           - Add code blocks or configuration examples where applicable

        5. **Production-Ready Features**:
           - Write compelling introductions that explain purpose and scope
           - Add comprehensive conclusions with next steps and related topics
           - Include "Prerequisites", "What You'll Learn", and "Key Takeaways" sections
           - Add cross-references to related articles/topics
           - Create actionable content that users can immediately implement

        6. **Metadata & SEO**:
           - Generate descriptive, SEO-friendly titles
           - Write detailed summaries (3-4 sentences) explaining value proposition
           - Create comprehensive tag lists including technical terms, processes, and categories
           - Generate practical takeaways that highlight key learning points

        RESPONSE FORMAT - Return valid JSON:
        {{
            "articles": [
                {{
                    "title": "Comprehensive, descriptive title that clearly indicates the specific topic",
                    "summary": "Detailed 3-4 sentence summary explaining what this article covers, why it's important, and what value it provides to the reader",
                    "content": "# Article Title\\n\\n## Overview\\n\\nDetailed introduction explaining the purpose, scope, and importance of this topic...\\n\\n## Prerequisites\\n\\n- Requirement 1\\n- Requirement 2\\n\\n## What You'll Learn\\n\\n- Learning objective 1\\n- Learning objective 2\\n\\n## Main Content\\n\\n### Section 1\\n\\nDetailed explanation with context...\\n\\n![Image Description](data:image/jpeg;base64,...)\\n\\n*Figure 1: Caption describing the image and its relevance*\\n\\n#### Subsection 1.1\\n\\nSpecific details and examples...\\n\\n### Section 2\\n\\n> **💡 Pro Tip:** Add helpful insights and best practices\\n\\nStep-by-step procedures:\\n\\n1. **Step 1**: Detailed explanation\\n   - Sub-step a\\n   - Sub-step b\\n\\n2. **Step 2**: More details\\n\\n### Common Issues & Troubleshooting\\n\\n> **⚠️ Warning:** Important considerations\\n\\n- Issue 1 and solution\\n- Issue 2 and solution\\n\\n## Key Takeaways\\n\\n- Takeaway 1\\n- Takeaway 2\\n\\n## Next Steps\\n\\n- Recommended follow-up actions\\n- Related topics to explore\\n\\n## Related Articles\\n\\n- Link to related article 1\\n- Link to related article 2",
                    "tags": ["primary-category", "technical-term-1", "technical-term-2", "process-name", "feature-name", "user-type"],
                    "takeaways": ["Specific, actionable takeaway 1", "Practical insight 2", "Key concept 3", "Best practice 4"]
                }}
            ]
        }}

        QUALITY STANDARDS:
        - Each article should be 1000-3000 words when rendered
        - Content should feel authoritative and professionally written
        - Include practical examples and real-world applications
        - Maintain consistency in tone and style across all articles
        - Ensure content is immediately actionable and valuable
        - MUST preserve all embedded media and data URLs exactly as provided
        """
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are an expert technical writer and content strategist creating comprehensive knowledge base articles. Always respond with valid JSON containing multiple focused, production-ready articles. CRITICAL: Preserve ALL embedded media including full base64 data URLs exactly as provided."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 8000,
            "temperature": 0.3
        }
        
        print(f"🤖 Calling OpenAI GPT-4o for multiple article generation...")
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            
            print(f"✅ OpenAI response received: {len(ai_response)} characters")
            
            try:
                # Clean up AI response to extract JSON
                import re
                
                # Remove any markdown code blocks
                json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL | re.IGNORECASE)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = ai_response
                
                # Parse JSON
                articles_data = json.loads(json_str)
                
                # Create article records
                articles = []
                for i, article_info in enumerate(articles_data.get('articles', [])):
                    article_record = {
                        "id": str(uuid.uuid4()),
                        "title": article_info.get("title", f"Article {i+1} from {metadata.get('original_filename', 'Upload')}"),
                        "content": article_info.get("content", "Content not available"),
                        "summary": article_info.get("summary", "Generated from uploaded content"),
                        "tags": article_info.get("tags", [metadata.get('type', 'upload')]),
                        "takeaways": article_info.get("takeaways", []),
                        "source_type": metadata.get('type', 'text_processing'),
                        "status": "draft",
                        "metadata": {
                            **metadata,
                            "ai_processed": True,
                            "ai_model": "gpt-4o",
                            "article_index": i + 1,
                            "total_articles": len(articles_data.get('articles', [])),
                            "processing_timestamp": datetime.utcnow().isoformat()
                        },
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    articles.append(article_record)
                
                print(f"✅ Generated {len(articles)} articles from content")
                return articles
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Raw AI response: {ai_response[:500]}...")
                # Fallback to single article
                return await create_single_article_from_content(content, metadata)
        else:
            print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
            return await create_single_article_from_content(content, metadata)
            
    except Exception as e:
        print(f"❌ Multiple articles generation error: {e}")
        return await create_single_article_from_content(content, metadata)

async def create_single_article_from_content(content: str, metadata: Dict[str, Any]) -> Dict:
    """Create a single comprehensive article from content"""
    # Use AI to create structured article
    if OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            You are an expert technical writer and content strategist. Transform the following raw content into a comprehensive, production-ready knowledge base article that feels professionally written and immediately actionable.

            IMPORTANT: This content may contain embedded media (images, diagrams, charts) that MUST be preserved and included in the generated article.

            Original Content:
            {content[:12000]}

            TRANSFORMATION REQUIREMENTS:

            1. **Media Preservation & Integration**:
               - PRESERVE all embedded images, charts, diagrams, and media exactly as they appear
               - Include ALL data URLs (data:image/jpeg;base64,... or data:image/png;base64,...)
               - Maintain image captions and context
               - Place images strategically within article content for maximum relevance
               - Reference images in the text when appropriate (e.g., "As illustrated in the figure below...")

            2. **Content Enhancement & Rewriting**:
               - Completely rewrite for clarity, flow, and technical accuracy
               - Add context, explanations, and helpful details
               - Improve technical language while maintaining original intent
               - Add transitions and logical connections between concepts
               - Include troubleshooting tips, best practices, and common scenarios

            3. **Professional Structure & Formatting**:
               - Use comprehensive markdown formatting with proper heading hierarchy
               - Create detailed outline with multiple heading levels (H1, H2, H3, H4)
               - Add bullet points, numbered lists, and checklists
               - Include tables for data presentation when relevant
               - Add callouts, notes, warnings, and tips using blockquotes
               - Create step-by-step procedures with clear numbering

            4. **Production-Ready Features**:
               - Write compelling introduction explaining purpose and scope
               - Add comprehensive conclusion with next steps
               - Include "Prerequisites", "What You'll Learn", and "Key Takeaways" sections
               - Add practical examples and real-world applications
               - Create actionable content users can immediately implement

            5. **Metadata & SEO**:
               - Generate descriptive, SEO-friendly title
               - Write detailed summary (3-4 sentences) explaining value proposition
               - Create comprehensive tag list including technical terms and processes
               - Generate practical takeaways highlighting key learning points

            RESPONSE FORMAT - Return valid JSON:
            {{
                "title": "Comprehensive, descriptive title that clearly indicates the specific topic and value",
                "summary": "Detailed 3-4 sentence summary explaining what this article covers, why it's important, and what specific value it provides to the reader",
                "content": "# Article Title\\n\\n## Overview\\n\\nDetailed introduction explaining the purpose, scope, and importance...\\n\\n## Prerequisites\\n\\n- Requirement 1\\n- Requirement 2\\n\\n## What You'll Learn\\n\\n- Learning objective 1\\n- Learning objective 2\\n\\n## Main Content\\n\\n### Section 1\\n\\nDetailed explanation with context and examples...\\n\\n![Image Description](data:image/jpeg;base64,...)\\n\\n*Figure 1: Caption describing the image and its relevance*\\n\\n#### Subsection 1.1\\n\\nSpecific implementation details...\\n\\n### Section 2\\n\\n> **💡 Pro Tip:** Include helpful insights and best practices\\n\\nStep-by-step procedures:\\n\\n1. **Step 1**: Detailed explanation\\n   - Sub-step a with specifics\\n   - Sub-step b with examples\\n\\n2. **Step 2**: More comprehensive details\\n\\n### Common Issues & Troubleshooting\\n\\n> **⚠️ Warning:** Important considerations and limitations\\n\\n- Common issue 1 and detailed solution\\n- Common issue 2 and prevention tips\\n\\n## Key Takeaways\\n\\n- Specific, actionable takeaway 1\\n- Practical insight 2\\n- Best practice 3\\n\\n## Next Steps\\n\\n- Recommended follow-up actions\\n- Related topics to explore\\n\\n## Additional Resources\\n\\n- Relevant documentation links\\n- Related processes or tools",
                "tags": ["primary-category", "technical-term-1", "technical-term-2", "process-name", "feature-name", "user-type", "difficulty-level"],
                "takeaways": ["Specific, actionable takeaway 1", "Practical insight 2", "Key concept 3", "Best practice 4", "Implementation tip 5"]
            }}

            QUALITY STANDARDS:
            - Article should be 800-2500 words when rendered
            - Content should feel authoritative and professionally written
            - Include practical examples and real-world applications
            - Ensure content is immediately actionable and valuable
            - Maintain consistent professional tone throughout
            - MUST preserve all embedded media and data URLs exactly as provided
            """
            
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are an expert technical writer and content strategist. Transform raw content into comprehensive, production-ready knowledge base articles. Always respond with valid JSON only. CRITICAL: Preserve ALL embedded media including full base64 data URLs exactly as provided."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 6000,
                "temperature": 0.2
            }
            
            print(f"🤖 Calling OpenAI GPT-4o for single article generation...")
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                
                print(f"✅ OpenAI response received: {len(ai_response)} characters")
                
                try:
                    # Clean up AI response to extract JSON
                    import re
                    
                    # Remove any markdown code blocks
                    json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL | re.IGNORECASE)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        json_str = ai_response
                    
                    # Parse JSON
                    article_data = json.loads(json_str)
                    
                    print(f"✅ Parsed article data: title='{article_data.get('title', 'N/A')}', tags={article_data.get('tags', [])}")
                    print(f"🔍 DEBUG: Article data keys: {list(article_data.keys())}")
                    print(f"🔍 DEBUG: Content field present: {'content' in article_data}")
                    print(f"🔍 DEBUG: Content preview: {article_data.get('content', 'NO CONTENT')[:100]}...")
                    
                    # Create article record
                    article_record = {
                        "id": str(uuid.uuid4()),
                        "title": article_data.get("title", metadata.get('original_filename', 'Processed Content')),
                        "content": article_data.get("content", content),
                        "summary": article_data.get("summary", "Content processed by Knowledge Engine"),
                        "tags": article_data.get("tags", [metadata.get('type', 'upload')]),
                        "takeaways": article_data.get("takeaways", []),
                        "source_type": metadata.get('type', 'text_processing'),
                        "status": "draft",
                        "metadata": {
                            **metadata,
                            "ai_processed": True,
                            "ai_model": "gpt-4o",
                            "processing_timestamp": datetime.utcnow().isoformat()
                        },
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    
                    print(f"🔍 DEBUG: Article record content field: {article_record.get('content', 'NO CONTENT')[:100]}...")
                    
                    return article_record
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"Raw AI response: {ai_response[:500]}...")
                    # Fallback to basic article
                    pass
            else:
                print(f"❌ OpenAI API error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ AI article generation error: {e}")
    else:
        print("⚠️ OpenAI API key not available")
    
    # Fallback to basic article
    return await create_basic_fallback_article(content, metadata)

async def create_basic_fallback_article(content: str, metadata: Dict[str, Any]) -> List[Dict]:
    """Create basic article without AI enhancement"""
    title = metadata.get('original_filename', metadata.get('url', 'Processed Content'))
    if title.startswith('Website:'):
        title = title.replace('Website: ', '')
    
    source_type = metadata.get('type', 'text_processing')
    
    article_record = {
        "id": str(uuid.uuid4()),
        "title": title,
        "content": content,
        "summary": f"Content processed from {source_type}",
        "tags": [source_type],
        "takeaways": [],
        "source_type": source_type,
        "status": "draft",
        "metadata": {
            **metadata,
            "ai_processed": False,
            "processing_timestamp": datetime.utcnow().isoformat()
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.content_library.insert_one(article_record)
    print(f"✅ Created basic Content Library article: {article_record['title']}")
    return [article_record]

# File upload endpoint
@app.post("/api/content/upload")
async def upload_file(
    file: UploadFile = File(...),
    metadata: str = Form("{}")
):
    """Upload and process files (text, audio, video, images)"""
    try:
        # Parse metadata
        file_metadata = json.loads(metadata)
        
        # Create processing job
        job = ProcessingJob(
            input_type="file",
            original_filename=file.filename,
            status="processing"
        )
        
        await db.processing_jobs.insert_one(job.dict())
        
        # Read file content
        file_content = await file.read()
        
        # Get file extension for proper handling
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        print(f"Processing file: {file.filename}, Extension: {file_extension}, Size: {len(file_content)} bytes")
        
        extracted_content = ""
        
        # Extract content based on file type
        if file_extension in ['txt', 'md', 'csv']:
            try:
                extracted_content = file_content.decode('utf-8')
                print(f"✅ Extracted {len(extracted_content)} characters from text file")
            except UnicodeDecodeError:
                extracted_content = file_content.decode('latin-1', errors='ignore')
                print(f"⚠️ Used latin-1 fallback, extracted {len(extracted_content)} characters")
                
        elif file_extension == 'pdf':
            try:
                import PyPDF2
                pdf_file = io.BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                extracted_content = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    extracted_content += f"=== Page {page_num + 1} ===\n{page_text}\n\n"
                print(f"✅ Extracted {len(extracted_content)} characters from PDF ({len(pdf_reader.pages)} pages)")
            except ImportError:
                print("⚠️ PyPDF2 not available, treating as binary file")
                extracted_content = f"PDF file: {file.filename} (content extraction requires PyPDF2)"
            except Exception as e:
                print(f"⚠️ PDF extraction error: {e}")
                extracted_content = f"PDF file: {file.filename} (extraction failed: {str(e)})"
                
        elif file_extension in ['doc', 'docx']:
            try:
                import docx
                from docx.document import Document as DocxDocument
                from docx.oxml.text.paragraph import CT_P
                from docx.oxml.table import CT_Tbl
                from docx.text.paragraph import Paragraph
                from docx.table import _Cell, Table
                import base64
                
                doc_file = io.BytesIO(file_content)
                doc = docx.Document(doc_file)
                
                # Initialize comprehensive content extraction
                extracted_content = f"# Document: {file.filename}\n\n"
                
                # Extract document properties if available
                if hasattr(doc.core_properties, 'title') and doc.core_properties.title:
                    extracted_content += f"**Document Title:** {doc.core_properties.title}\n\n"
                if hasattr(doc.core_properties, 'author') and doc.core_properties.author:
                    extracted_content += f"**Author:** {doc.core_properties.author}\n\n"
                if hasattr(doc.core_properties, 'subject') and doc.core_properties.subject:
                    extracted_content += f"**Subject:** {doc.core_properties.subject}\n\n"
                
                # Extract embedded images and media
                def extract_media_from_docx(doc):
                    """Extract embedded images from docx document"""
                    media_files = []
                    try:
                        # Access the document's media files
                        for rel in doc.part.rels.values():
                            if "image" in rel.target_ref:
                                # Get image data
                                image_part = rel.target_part
                                image_data = image_part.blob
                                
                                # Convert to base64 for embedding
                                image_base64 = base64.b64encode(image_data).decode('utf-8')
                                
                                # Determine image format
                                content_type = image_part.content_type
                                if 'png' in content_type:
                                    img_format = 'png'
                                elif 'jpeg' in content_type or 'jpg' in content_type:
                                    img_format = 'jpeg'
                                elif 'gif' in content_type:
                                    img_format = 'gif'
                                else:
                                    img_format = 'png'  # default
                                
                                media_files.append({
                                    'type': 'image',
                                    'format': img_format,
                                    'data': image_base64,
                                    'content_type': content_type,
                                    'size': len(image_data)
                                })
                                
                                print(f"✅ Extracted image: {img_format}, {len(image_data)} bytes")
                    except Exception as e:
                        print(f"⚠️ Media extraction error: {e}")
                    
                    return media_files
                
                # Extract media from document
                embedded_media = extract_media_from_docx(doc)
                print(f"🔍 DEBUG: Extracted {len(embedded_media)} media items from DOCX")
                for i, media in enumerate(embedded_media):
                    print(f"🔍 DEBUG: Media {i+1}: {media['format']}, {media['size']} bytes, type: {media['content_type']}")
                
                # Process document elements in order
                def iter_block_items(parent):
                    """Generate a reference to each paragraph and table child within parent, in document order."""
                    if isinstance(parent, DocxDocument):
                        parent_elm = parent.element.body
                    elif isinstance(parent, _Cell):
                        parent_elm = parent._tc
                    else:
                        raise ValueError("Unknown parent type")
                    
                    for child in parent_elm:
                        if isinstance(child, CT_P):
                            yield Paragraph(child, parent)
                        elif isinstance(child, CT_Tbl):
                            yield Table(child, parent)
                
                table_count = 0
                image_count = 0
                media_index = 0  # Track which embedded media to use next
                
                for block in iter_block_items(doc):
                    if isinstance(block, Paragraph):
                        if block.text.strip():
                            # Enhanced paragraph processing with style detection
                            style_name = block.style.name
                            text = block.text.strip()
                            
                            # Handle different paragraph styles
                            if style_name.startswith('Heading 1') or style_name == 'Title':
                                extracted_content += f"# {text}\n\n"
                            elif style_name.startswith('Heading 2'):
                                extracted_content += f"## {text}\n\n"
                            elif style_name.startswith('Heading 3'):
                                extracted_content += f"### {text}\n\n"
                            elif style_name.startswith('Heading 4'):
                                extracted_content += f"#### {text}\n\n"
                            elif style_name.startswith('Heading'):
                                extracted_content += f"##### {text}\n\n"
                            elif 'List' in style_name or text.startswith(('•', '-', '*')):
                                extracted_content += f"- {text}\n"
                            elif text.startswith(tuple(f"{i}." for i in range(1, 20))):
                                extracted_content += f"{text}\n"
                            else:
                                extracted_content += f"{text}\n\n"
                            
                            # Check for images in paragraph using multiple methods
                            has_image_in_paragraph = False
                            
                            # Method 1: Check for drawing objects (shapes/images)
                            for run in block.runs:
                                # Check for inline shapes (images)
                                if hasattr(run, '_element') and run._element.xpath('.//a:blip'):
                                    has_image_in_paragraph = True
                                    break
                                # Check for drawing elements
                                if hasattr(run, '_element') and run._element.xpath('.//w:drawing'):
                                    has_image_in_paragraph = True
                                    break
                            
                            # Method 2: If paragraph is very short and we have unused embedded media, assume it contains an image
                            if not has_image_in_paragraph and len(text.strip()) < 50 and media_index < len(embedded_media):
                                # Check if this looks like an image caption or placeholder
                                image_keywords = ['figure', 'image', 'diagram', 'chart', 'graph', 'screenshot', 'photo']
                                if any(keyword in text.lower() for keyword in image_keywords) or text.strip() == '':
                                    has_image_in_paragraph = True
                            
                            # If we found an image reference and have embedded media available
                            if has_image_in_paragraph and media_index < len(embedded_media):
                                media_item = embedded_media[media_index]
                                media_index += 1
                                image_count += 1
                                
                                # Embed image as base64 data URL
                                data_url = f"data:{media_item['content_type']};base64,{media_item['data']}"
                                extracted_content += f"\n![Image {image_count}]({data_url})\n\n"
                                extracted_content += f"*Image {image_count}: {media_item['format'].upper()} image ({media_item['size']} bytes)*\n\n"
                                print(f"🔍 DEBUG: Successfully embedded image {image_count} as base64 data URL (length: {len(data_url)})")
                    
                    elif isinstance(block, Table):
                        table_count += 1
                        extracted_content += f"\n## Table {table_count}\n\n"
                        
                        # Extract table headers if first row looks like headers
                        rows = [[cell.text.strip() for cell in row.cells] for row in block.rows]
                        if rows:
                            headers = rows[0]
                            data_rows = rows[1:]
                            
                            # Check if first row are likely headers (short, title-case)
                            if all(len(cell) < 50 and any(c.isupper() for c in cell) for cell in headers if cell):
                                # Create markdown table with headers
                                extracted_content += "| " + " | ".join(headers) + " |\n"
                                extracted_content += "|" + "|".join([" --- " for _ in headers]) + "|\n"
                                for row in data_rows:
                                    extracted_content += "| " + " | ".join(row) + " |\n"
                            else:
                                # Regular table without headers
                                for row in rows:
                                    extracted_content += "| " + " | ".join(row) + " |\n"
                        
                        extracted_content += "\n"
                
                # If we still have unused embedded media, add them at the end
                while media_index < len(embedded_media):
                    media_item = embedded_media[media_index]
                    media_index += 1
                    image_count += 1
                    
                    data_url = f"data:{media_item['content_type']};base64,{media_item['data']}"
                    extracted_content += f"\n![Image {image_count}]({data_url})\n\n"
                    extracted_content += f"*Image {image_count}: {media_item['format'].upper()} image ({media_item['size']} bytes) - Added from document assets*\n\n"
                    print(f"🔍 DEBUG: Added remaining embedded image {image_count} at end of document")
                    
                # Add comprehensive media summary
                if len(embedded_media) > 0:
                    extracted_content += f"\n---\n\n**Media Assets Extracted and Embedded:**\n\n"
                    for i, media in enumerate(embedded_media, 1):
                        extracted_content += f"- **Image {i}**: {media['format'].upper()} format, {media['size']} bytes\n"
                    extracted_content += f"\n**Total Images Embedded:** {len(embedded_media)}\n\n"
                    
                if image_count > len(embedded_media):
                    missed_images = image_count - len(embedded_media)
                    extracted_content += f"**Note:** {missed_images} additional image(s) referenced but not extracted\n\n"
                    
                if table_count > 0:
                    extracted_content += f"**Structured Data:** {table_count} tables with detailed information\n\n"
                    extracted_content += f"**Structured Data:** {table_count} tables with detailed information\n\n"
                
                # Add document statistics
                total_paragraphs = len([p for p in doc.paragraphs if p.text.strip()])
                extracted_content += f"**Document Statistics:**\n"
                extracted_content += f"- Total paragraphs: {total_paragraphs}\n"
                extracted_content += f"- Tables: {table_count}\n"
                extracted_content += f"- Images/Diagrams: {image_count}\n"
                extracted_content += f"- Character count: {len(extracted_content)}\n\n"
                        
                print(f"✅ Enhanced extraction: {len(extracted_content)} characters, {table_count} tables, {image_count} images from Word document")
            except ImportError:
                print("⚠️ python-docx not available, treating as binary file")
                extracted_content = f"Word document: {file.filename} (content extraction requires python-docx)"
            except Exception as e:
                print(f"⚠️ Word document extraction error: {e}")
                extracted_content = f"Word document: {file.filename} (extraction failed: {str(e)})"

        elif file_extension in ['xls', 'xlsx']:
            try:
                import openpyxl
                import pandas as pd
                
                excel_file = io.BytesIO(file_content)
                workbook = openpyxl.load_workbook(excel_file)
                
                extracted_content = f"Spreadsheet: {file.filename}\n\n"
                
                for sheet_name in workbook.sheetnames:
                    sheet = workbook[sheet_name]
                    extracted_content += f"=== Sheet: {sheet_name} ===\n"
                    
                    # Get sheet data
                    data = []
                    for row in sheet.iter_rows(values_only=True):
                        if any(cell is not None for cell in row):
                            data.append([str(cell) if cell is not None else "" for cell in row])
                    
                    # Convert to readable format
                    if data:
                        # First row might be headers
                        headers = data[0] if data else []
                        extracted_content += "Headers: " + " | ".join(headers[:10]) + "\n\n"  # Limit to first 10 columns
                        
                        # Sample data rows (first 10)
                        for i, row in enumerate(data[1:11]):  # Skip header, limit to 10 rows
                            extracted_content += f"Row {i+1}: " + " | ".join(row[:10]) + "\n"
                        
                        if len(data) > 11:
                            extracted_content += f"... and {len(data)-11} more rows\n"
                    
                    extracted_content += "\n"
                
                print(f"✅ Extracted content from Excel file with {len(workbook.sheetnames)} sheets")
            except ImportError:
                print("⚠️ openpyxl not available, treating as binary file")
                extracted_content = f"Excel file: {file.filename} (content extraction requires openpyxl)"
            except Exception as e:
                print(f"⚠️ Excel extraction error: {e}")
                extracted_content = f"Excel file: {file.filename} (extraction failed: {str(e)})"

        elif file_extension in ['ppt', 'pptx']:
            try:
                import pptx
                
                ppt_file = io.BytesIO(file_content)
                presentation = pptx.Presentation(ppt_file)
                
                extracted_content = f"Presentation: {file.filename}\n\n"
                
                for i, slide in enumerate(presentation.slides):
                    extracted_content += f"=== Slide {i+1} ===\n"
                    
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text.strip():
                            extracted_content += f"{shape.text}\n"
                        elif shape.has_table:
                            table = shape.table
                            extracted_content += "\nTable:\n"
                            for row in table.rows:
                                row_data = [cell.text.strip() for cell in row.cells]
                                extracted_content += " | ".join(row_data) + "\n"
                    
                    extracted_content += "\n"
                
                print(f"✅ Extracted content from PowerPoint with {len(presentation.slides)} slides")
            except ImportError:
                print("⚠️ python-pptx not available, treating as binary file")
                extracted_content = f"PowerPoint file: {file.filename} (content extraction requires python-pptx)"
            except Exception as e:
                print(f"⚠️ PowerPoint extraction error: {e}")
                extracted_content = f"PowerPoint file: {file.filename} (extraction failed: {str(e)})"
                
        elif file_extension in ['json']:
            try:
                json_data = json.loads(file_content.decode('utf-8'))
                extracted_content = f"JSON file: {file.filename}\n\nStructured Data:\n{json.dumps(json_data, indent=2)}"
                print(f"✅ Extracted JSON content from {file.filename}")
            except Exception as e:
                print(f"⚠️ JSON parsing error: {e}")
                extracted_content = file_content.decode('utf-8', errors='ignore')
                
        else:
            # For other file types, create descriptive content
            extracted_content = f"""File: {file.filename}
File Type: {file_extension.upper()} file
Size: {len(file_content)} bytes
Uploaded: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

This is a {file_extension.upper()} file that has been uploaded to the knowledge base. While the specific content cannot be extracted automatically, this file is now part of your knowledge repository and can be referenced in conversations."""

        # Add file metadata to content
        enriched_content = f"""Document: {file.filename}

{extracted_content}

---
File Information:
- Original filename: {file.filename}
- File type: {file_extension.upper()}
- Upload date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
- Source: Knowledge Engine File Upload"""

        # Process the extracted content
        enhanced_metadata = {
            **file_metadata,
            "original_filename": file.filename,
            "file_extension": file_extension,
            "file_size": len(file_content),
            "extraction_method": "automated"
        }
        
        chunks = await process_text_content(enriched_content, enhanced_metadata)
        
        # Update job
        job.chunks = chunks
        job.status = "completed" 
        job.completed_at = datetime.utcnow()
        
        await db.processing_jobs.update_one(
            {"job_id": job.job_id},
            {"$set": job.dict()}
        )
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "file_type": file_extension,
            "extracted_content_length": len(extracted_content),
            "chunks_created": len(chunks),
            "message": "File processed successfully"
        }
        
    except Exception as e:
        # Update job with error
        if 'job' in locals():
            await db.processing_jobs.update_one(
                {"job_id": job.job_id},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )
        raise HTTPException(status_code=500, detail=str(e))

# Simple search endpoint
@app.post("/api/search")
async def search_content(request: SearchRequest):
    """Perform text search across processed content"""
    try:
        search_results = []
        
        # Simple text search in chunks
        async for chunk in db.document_chunks.find(
            {"content": {"$regex": request.query, "$options": "i"}}).limit(request.limit):
            search_results.append({
                "id": chunk["id"],
                "content": chunk["content"],
                "metadata": chunk.get("metadata", {}),
                "created_at": chunk.get("created_at")
            })
        
        return {
            "query": request.query,
            "results": search_results,
            "total_found": len(search_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# OpenAI Chat endpoint using direct API call
@app.post("/api/chat")
async def chat_with_ai(
    message: str = Form(...),
    session_id: str = Form(...),
    model_provider: str = Form("openai"),
    model_name: str = Form("gpt-4o")
):
    """Chat with AI using processed content as context"""
    try:
        if not OPENAI_API_KEY and model_provider == "openai":
            raise HTTPException(status_code=400, detail="OpenAI API key not configured")
        
        # Get relevant chunks for context (simple implementation)
        context_chunks = []
        async for chunk in db.document_chunks.find(
            {"content": {"$regex": message, "$options": "i"}}).limit(3):
            context_chunks.append(chunk["content"])
        
        # Build context
        context = "\n".join(context_chunks) if context_chunks else ""
        system_message = f"""You are a helpful AI assistant for PromptSupport. 
Use the following context to answer questions accurately:

Context:
{context}

If the context doesn't contain relevant information, provide general assistance."""

        response_text = ""
        
        if model_provider == "openai" and OPENAI_API_KEY:
            # Direct OpenAI API call
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result["choices"][0]["message"]["content"]
            else:
                raise HTTPException(status_code=500, detail=f"OpenAI API error: {response.text}")
                
        else:
            raise HTTPException(status_code=400, detail="AI provider not configured or invalid")
        
        # Store conversation in database
        conversation_record = {
            "session_id": session_id,
            "user_message": message,
            "ai_response": response_text,
            "model_provider": model_provider,
            "model_name": model_name,
            "context_used": len(context_chunks),
            "timestamp": datetime.utcnow()
        }
        
        await db.conversations.insert_one(conversation_record)
        
        return {
            "response": response_text,
            "session_id": session_id,
            "context_chunks_used": len(context_chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get processing job status
@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a processing job"""
    try:
        job = await db.processing_jobs.find_one({"job_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "input_type": job.get("input_type"),
            "chunks_created": len(job.get("chunks", [])),
            "error_message": job.get("error_message"),
            "created_at": job.get("created_at"),
            "completed_at": job.get("completed_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content Library integration endpoint
@app.post("/api/content-library/create")
async def create_content_library_article(
    title: str = Form(...),
    content: str = Form(...),
    source_job_id: str = Form(...),
    source_type: str = Form(...),
    metadata: str = Form("{}")
):
    """Create structured article in Content Library from processed content"""
    try:
        article_metadata = json.loads(metadata)
        
        # Use AI to generate structured article
        if OPENAI_API_KEY:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Create prompt for article generation
            prompt = f"""
            Create a structured article from the following content. Extract key information and organize it professionally.
            
            Source Content:
            {content[:2000]}...
            
            Please provide:
            1. A clear, descriptive title
            2. A concise summary (2-3 sentences)
            3. Main content organized with headings
            4. 3-5 relevant tags
            5. Key takeaways or important points
            
            Format as JSON with keys: title, summary, content, tags, takeaways
            """
            
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are an expert content curator who creates well-structured articles from raw content."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                try:
                    # Parse AI response as JSON
                    import json
                    import re
                    # Extract JSON from response if it's wrapped in markdown
                    json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
                    if json_match:
                        article_data = json.loads(json_match.group(1))
                    else:
                        article_data = json.loads(ai_response)
                    
                    # Create article record for Content Library
                    article_record = {
                        "id": str(uuid.uuid4()),
                        "title": article_data.get("title", title),
                        "content": article_data.get("content", content),
                        "summary": article_data.get("summary", ""),
                        "tags": article_data.get("tags", []),
                        "takeaways": article_data.get("takeaways", []),
                        "source_job_id": source_job_id,
                        "source_type": source_type,
                        "status": "draft",
                        "metadata": article_metadata,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    
                    # Store in Content Library collection
                    await db.content_library.insert_one(article_record)
                    
                    return {
                        "success": True,
                        "article_id": article_record["id"],
                        "title": article_record["title"],
                        "message": "Article created successfully in Content Library"
                    }
                    
                except json.JSONDecodeError:
                    # Fallback if AI doesn't return proper JSON
                    article_record = {
                        "id": str(uuid.uuid4()),
                        "title": title,
                        "content": content,
                        "summary": f"Extracted from {source_type}",
                        "tags": [source_type],
                        "source_job_id": source_job_id,
                        "source_type": source_type,
                        "status": "draft",
                        "metadata": article_metadata,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    
                    await db.content_library.insert_one(article_record)
                    
                    return {
                        "success": True,
                        "article_id": article_record["id"],
                        "title": article_record["title"],
                        "message": "Basic article created successfully in Content Library"
                    }
        
        # Fallback without AI
        article_record = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "summary": f"Content extracted from {source_type}",
            "tags": [source_type],
            "source_job_id": source_job_id,
            "source_type": source_type,
            "status": "draft",
            "metadata": article_metadata,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.content_library.insert_one(article_record)
        
        return {
            "success": True,
            "article_id": article_record["id"],
            "title": article_record["title"],
            "message": "Article created successfully in Content Library"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get Content Library articles
@app.get("/api/content-library")
async def get_content_library_articles():
    """Get all Content Library articles"""
    try:
        articles = []
        async for article in db.content_library.find().sort("created_at", -1):
            articles.append({
                "id": article["id"],
                "title": article["title"],
                "content": article.get("content", ""),  # Added content field!
                "summary": article.get("summary", ""),
                "tags": article.get("tags", []),
                "status": article.get("status", "draft"),
                "source_type": article.get("source_type", ""),
                "takeaways": article.get("takeaways", []),  # Added takeaways too
                "metadata": article.get("metadata", {}),    # Added metadata
                "created_at": article.get("created_at"),
                "updated_at": article.get("updated_at")
            })
        
        return {
            "articles": articles,
            "total": len(articles)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# URL processing endpoint  
@app.post("/api/content/process-url")
async def process_url_content(
    url: str = Form(...),
    metadata: str = Form("{}")
):
    """Process URL content by scraping and generating articles"""
    try:
        # Parse metadata
        url_metadata = json.loads(metadata)
        
        # Create processing job
        job = ProcessingJob(
            input_type="url",
            url=url,
            status="processing"
        )
        
        await db.processing_jobs.insert_one(job.dict())
        
        print(f"🌐 Processing URL: {url}")
        
        # Scrape website content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract title
        page_title = soup.find('title')
        title = page_title.get_text().strip() if page_title else url
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '').strip() if meta_desc else ""
        
        # Extract main content
        main_content = ""
        
        # Try to find main content areas
        content_selectors = [
            'main', 'article', '.content', '#content', 
            '.post', '.entry', '.article-body', '.main-content'
        ]
        
        content_found = False
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                main_content = content_area.get_text(separator='\n', strip=True)
                content_found = True
                break
        
        # If no main content area found, extract from body
        if not content_found:
            body = soup.find('body')
            if body:
                # Remove navigation, footer, sidebar elements
                for element in body.find_all(['nav', 'footer', 'aside', '.sidebar', '.navigation']):
                    element.decompose()
                main_content = body.get_text(separator='\n', strip=True)
        
        # Clean up content
        lines = main_content.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
        extracted_content = '\n'.join(cleaned_lines)
        
        # Create enriched content
        enriched_content = f"""Website: {title}
URL: {url}

{f"Description: {description}" if description else ""}

=== Main Content ===

{extracted_content}

---
Source Information:
- Original URL: {url}
- Page Title: {title}
- Scraped Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
- Content Length: {len(extracted_content)} characters
- Source: Knowledge Engine URL Processing"""
        
        print(f"✅ Extracted {len(extracted_content)} characters from URL")
        
        # Process the extracted content
        enhanced_metadata = {
            **url_metadata,
            "url": url,
            "page_title": title,
            "page_description": description,
            "content_length": len(extracted_content),
            "type": "url_processing"
        }
        
        chunks = await process_text_content(enriched_content, enhanced_metadata)
        
        # Update job
        job.chunks = chunks
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        
        await db.processing_jobs.update_one(
            {"job_id": job.job_id},
            {"$set": job.dict()}
        )
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "url": url,
            "page_title": title,
            "extracted_content_length": len(extracted_content),
            "chunks_created": len(chunks),
            "message": "URL processed successfully"
        }
        
    except requests.RequestException as e:
        # Update job with error
        if 'job' in locals():
            await db.processing_jobs.update_one(
                {"job_id": job.job_id},
                {"$set": {"status": "failed", "error_message": f"Failed to fetch URL: {str(e)}"}}
            )
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        # Update job with error
        if 'job' in locals():
            await db.processing_jobs.update_one(
                {"job_id": job.job_id},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )
        raise HTTPException(status_code=500, detail=str(e))

# Recording processing endpoint
@app.post("/api/content/process-recording")
async def process_recording(
    recording_type: str = Form(...),  # 'screen', 'audio', 'video', 'screenshot'
    duration: int = Form(0),
    title: str = Form(""),
    metadata: str = Form("{}")
):
    """Process recorded content (screen, audio, video, screenshots)"""
    try:
        recording_metadata = json.loads(metadata)
        
        job = ProcessingJob(
            input_type="recording",
            original_filename=f"{recording_type}_recording_{title}",
            status="processing"
        )
        
        await db.processing_jobs.insert_one(job.dict())
        
        # Simulate recording processing
        if recording_type == "screenshot":
            content = f"Screenshot captured: {title}\n\nThis screenshot shows important visual information that has been processed and can be referenced in conversations."
        elif recording_type == "screen":
            content = f"Screen recording captured: {title} (Duration: {duration}s)\n\nThis screen recording demonstrates key processes and workflows that have been analyzed and processed."
        elif recording_type == "audio":
            content = f"Audio recording processed: {title} (Duration: {duration}s)\n\nThis audio content has been transcribed and processed for searchability."
        else:
            content = f"Video recording processed: {title} (Duration: {duration}s)\n\nThis video content has been analyzed and key information extracted."
        
        # Process the content
        chunks = await process_text_content(content, {**recording_metadata, "recording_type": recording_type, "duration": duration})
        
        # Update job
        job.chunks = chunks
        job.status = "completed" 
        job.completed_at = datetime.utcnow()
        
        await db.processing_jobs.update_one(
            {"job_id": job.job_id},
            {"$set": job.dict()}
        )
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "recording_type": recording_type,
            "duration": duration,
            "chunks_created": len(chunks),
            "message": "Recording processed successfully"
        }
        
    except Exception as e:
        if 'job' in locals():
            await db.processing_jobs.update_one(
                {"job_id": job.job_id},
                {"$set": {"status": "failed", "error_message": str(e)}}
            )
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced document listing with article links
@app.get("/api/documents")
async def list_documents():
    """List all processed documents with article information"""
    try:
        documents = []
        
        async for chunk in db.document_chunks.find().sort("created_at", -1):
            # Find related articles for this document
            related_articles = []
            if 'original_filename' in chunk.get('metadata', {}):
                filename = chunk['metadata']['original_filename']
                async for article in db.content_library.find({
                    "metadata.original_filename": filename
                }):
                    related_articles.append({
                        "id": article["id"],
                        "title": article["title"],
                        "summary": article["summary"]
                    })
            
            documents.append({
                "id": chunk["id"],
                "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "metadata": chunk.get("metadata", {}),
                "created_at": chunk.get("created_at"),
                "related_articles": related_articles,
                "articles_count": len(related_articles)
            })
        
        return {
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update Content Library article
@app.put("/api/content-library/{article_id}")
async def update_content_library_article(
    article_id: str,
    title: str = Form(...),
    content: str = Form(...),
    status: str = Form("draft"),
    tags: str = Form("[]"),
    metadata: str = Form("{}")
):
    """Update an existing Content Library article with version history"""
    try:
        # Parse JSON fields
        tags_list = json.loads(tags) if tags else []
        metadata_dict = json.loads(metadata) if metadata else {}
        
        # Get existing article for version history
        existing_article = await db.content_library.find_one({"id": article_id})
        if not existing_article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Create version history entry
        version_entry = {
            "version": existing_article.get("version", 1) + 1,
            "title": existing_article.get("title", ""),
            "content": existing_article.get("content", ""),
            "status": existing_article.get("status", "draft"),
            "tags": existing_article.get("tags", []),
            "updated_at": existing_article.get("updated_at", datetime.utcnow().isoformat()),
            "updated_by": "user"
        }
        
        # Add to version history
        version_history = existing_article.get("version_history", [])
        version_history.append(version_entry)
        
        # Update article
        updated_article = {
            "title": title,
            "content": content,
            "status": status,
            "tags": tags_list,
            "metadata": {**existing_article.get("metadata", {}), **metadata_dict},
            "version": version_entry["version"],
            "version_history": version_history,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": "user"
        }
        
        await db.content_library.update_one(
            {"id": article_id},
            {"$set": updated_article}
        )
        
        return {
            "success": True,
            "article_id": article_id,
            "version": updated_article["version"],
            "message": "Article updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create new Content Library article
@app.post("/api/content-library")
async def create_content_library_article(
    title: str = Form(...),
    content: str = Form(...),
    status: str = Form("draft"),
    tags: str = Form("[]"),
    metadata: str = Form("{}")
):
    """Create a new Content Library article"""
    try:
        # Parse JSON fields
        tags_list = json.loads(tags) if tags else []
        metadata_dict = json.loads(metadata) if metadata else {}
        
        # Create new article
        article_id = str(datetime.utcnow().timestamp()).replace('.', '')
        new_article = {
            "id": article_id,
            "title": title,
            "content": content,
            "status": status,
            "tags": tags_list,
            "metadata": metadata_dict,
            "source_type": "user_created",
            "version": 1,
            "version_history": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "created_by": "user",
            "updated_by": "user"
        }
        
        await db.content_library.insert_one(new_article)
        
        return {
            "success": True,
            "article_id": article_id,
            "message": "Article created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get article version history
@app.get("/api/content-library/{article_id}/versions")
async def get_article_version_history(article_id: str):
    """Get version history for an article"""
    try:
        article = await db.content_library.find_one({"id": article_id})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        version_history = article.get("version_history", [])
        current_version = {
            "version": article.get("version", 1),
            "title": article.get("title", ""),
            "content": article.get("content", ""),
            "status": article.get("status", "draft"),
            "tags": article.get("tags", []),
            "updated_at": article.get("updated_at"),
            "updated_by": article.get("updated_by", "system"),
            "is_current": True
        }
        
        return {
            "current_version": current_version,
            "version_history": version_history,
            "total_versions": len(version_history) + 1
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Restore article version
@app.post("/api/content-library/{article_id}/restore/{version}")
async def restore_article_version(article_id: str, version: int):
    """Restore an article to a specific version"""
    try:
        article = await db.content_library.find_one({"id": article_id})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        version_history = article.get("version_history", [])
        target_version = None
        
        for v in version_history:
            if v.get("version") == version:
                target_version = v
                break
        
        if not target_version:
            raise HTTPException(status_code=404, detail="Version not found")
        
        # Save current version to history before restoring
        current_version_entry = {
            "version": article.get("version", 1),
            "title": article.get("title", ""),
            "content": article.get("content", ""),
            "status": article.get("status", "draft"),
            "tags": article.get("tags", []),
            "updated_at": article.get("updated_at"),
            "updated_by": article.get("updated_by", "system")
        }
        version_history.append(current_version_entry)
        
        # Restore to target version
        new_version = article.get("version", 1) + 1
        restored_article = {
            "title": target_version.get("title", ""),
            "content": target_version.get("content", ""),
            "status": target_version.get("status", "draft"),
            "tags": target_version.get("tags", []),
            "version": new_version,
            "version_history": version_history,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": "user",
            "restored_from_version": version
        }
        
        await db.content_library.update_one(
            {"id": article_id},
            {"$set": restored_article}
        )
        
        return {
            "success": True,
            "article_id": article_id,
            "restored_from_version": version,
            "new_version": new_version,
            "message": f"Article restored to version {version}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/content-library")
async def create_content_library_article(request: Request):
    """Create a new article in the Content Library"""
    try:
        data = await request.json()
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = f"article_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # Set timestamps
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = datetime.now().isoformat()
        
        # Set defaults
        data.setdefault('version', 1)
        data.setdefault('views', 0)
        data.setdefault('status', 'draft')
        data.setdefault('source', 'manual')
        data.setdefault('tags', [])
        data.setdefault('metadata', {})
        
        # Calculate word count
        content = data.get('content', '')
        if content:
            # Remove HTML tags and count words
            import re
            text_content = re.sub(r'<[^>]+>', '', content)
            data['wordCount'] = len(text_content.split())
        else:
            data['wordCount'] = 0
        
        # Insert into database
        await content_library_collection.insert_one(data)
        
        return {
            "success": True,
            "message": "Article created successfully",
            "article": data
        }
        
    except Exception as e:
        print(f"❌ Error creating article: {str(e)}")
        return {"success": False, "error": str(e)}


@app.delete("/api/content-library/{article_id}")
async def delete_content_library_article(article_id: str):
    """Delete an article from the Content Library"""
    try:
        result = await content_library_collection.delete_one({"id": article_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {
            "success": True,
            "message": "Article deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
async def analyze_media_intelligence(request: Request):
    """
    Comprehensive media analysis using LLM + Vision models
    Provides intelligent classification, contextual placement, and auto-generated captions
    """
    try:
        form = await request.form()
        
        # Get media data and context
        base64_data = form.get("media_data", "")
        alt_text = form.get("alt_text", "")
        article_context = form.get("context", "")
        
        if not base64_data:
            return {"success": False, "error": "No media data provided"}
        
        # Perform comprehensive analysis
        analysis = await media_intelligence.analyze_media_comprehensive(
            base64_data=base64_data,
            alt_text=alt_text,
            context=article_context
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "enhanced_html": media_intelligence.create_enhanced_media_html(analysis, base64_data)
        }
        
    except Exception as e:
        print(f"❌ Media analysis error: {str(e)}")
        return {"success": False, "error": str(e)}


@app.post("/api/media/process-article")
async def process_article_media(request: Request):
    """
    Process all media in an article with intelligent placement and captions
    """
    try:
        form = await request.form()
        
        article_content = form.get("content", "")
        article_id = form.get("article_id", "")
        
        if not article_content:
            return {"success": False, "error": "No article content provided"}
        
        # Extract all media from markdown content
        media_items = extract_media_from_content(article_content)
        
        if not media_items:
            return {
                "success": True,
                "message": "No media found in article",
                "processed_content": article_content,
                "media_count": 0
            }
        
        # Process each media item with intelligence
        processed_media = []
        enhanced_content = article_content
        
        for i, media_item in enumerate(media_items):
            try:
                # Analyze media with context
                analysis = await media_intelligence.analyze_media_comprehensive(
                    base64_data=media_item['data_url'],
                    alt_text=media_item['alt_text'],
                    context=article_content
                )
                
                # Generate contextual placement
                placement = media_intelligence.generate_contextual_placement(
                    analysis, article_content
                )
                
                # Create enhanced HTML
                enhanced_html = media_intelligence.create_enhanced_media_html(
                    analysis, media_item['data_url']
                )
                
                # Replace original markdown with enhanced HTML
                enhanced_content = enhanced_content.replace(
                    media_item['original_markdown'],
                    enhanced_html
                )
                
                processed_media.append({
                    "index": i,
                    "original_alt": media_item['alt_text'],
                    "analysis": analysis,
                    "placement": placement,
                    "enhanced_html": enhanced_html
                })
                
            except Exception as e:
                print(f"❌ Error processing media item {i}: {str(e)}")
                # Keep original media on error
                processed_media.append({
                    "index": i,
                    "error": str(e),
                    "original_alt": media_item['alt_text']
                })
        
        # Update article in database if article_id provided
        if article_id and article_id != "":
            try:
                await content_library_collection.update_one(
                    {"id": article_id},
                    {
                        "$set": {
                            "content": enhanced_content,
                            "media_processed": True,
                            "media_count": len(processed_media),
                            "updated_at": datetime.now().isoformat()
                        }
                    }
                )
            except Exception as e:
                print(f"❌ Error updating article in database: {str(e)}")
        
        return {
            "success": True,
            "processed_content": enhanced_content,
            "media_count": len(media_items),
            "processed_media": processed_media,
            "message": f"Successfully processed {len(processed_media)} media items with intelligence"
        }
        
    except Exception as e:
        print(f"❌ Article media processing error: {str(e)}")
        return {"success": False, "error": str(e)}


@app.get("/api/media/stats")
async def get_media_statistics():
    """
    Get comprehensive media statistics across all articles
    """
    try:
        # Query all articles
        articles = await content_library_collection.find({}).to_list(length=None)
        
        stats = {
            "total_articles": len(articles),
            "articles_with_media": 0,
            "total_media_items": 0,
            "media_by_format": {},
            "media_by_type": {},
            "processed_articles": 0,
            "intelligence_analysis": {
                "vision_analyzed": 0,
                "auto_captioned": 0,
                "contextually_placed": 0
            }
        }
        
        for article in articles:
            content = article.get("content", "")
            
            # Count media items
            media_items = extract_media_from_content(content)
            if media_items:
                stats["articles_with_media"] += 1
                stats["total_media_items"] += len(media_items)
                
                # Analyze media formats and types
                for media in media_items:
                    data_url = media['data_url']
                    if 'image/png' in data_url:
                        stats["media_by_format"]["PNG"] = stats["media_by_format"].get("PNG", 0) + 1
                        stats["media_by_type"]["Image"] = stats["media_by_type"].get("Image", 0) + 1
                    elif 'image/jpeg' in data_url:
                        stats["media_by_format"]["JPEG"] = stats["media_by_format"].get("JPEG", 0) + 1
                        stats["media_by_type"]["Image"] = stats["media_by_type"].get("Image", 0) + 1
                    elif 'image/gif' in data_url:
                        stats["media_by_format"]["GIF"] = stats["media_by_format"].get("GIF", 0) + 1
                        stats["media_by_type"]["Image"] = stats["media_by_type"].get("Image", 0) + 1
                    elif 'image/svg' in data_url:
                        stats["media_by_format"]["SVG"] = stats["media_by_format"].get("SVG", 0) + 1
                        stats["media_by_type"]["Image"] = stats["media_by_type"].get("Image", 0) + 1
                    elif 'video/mp4' in data_url:
                        stats["media_by_format"]["MP4"] = stats["media_by_format"].get("MP4", 0) + 1
                        stats["media_by_type"]["Video"] = stats["media_by_type"].get("Video", 0) + 1
            
            # Check if article was processed with intelligence
            if article.get("media_processed"):
                stats["processed_articles"] += 1
                stats["intelligence_analysis"]["vision_analyzed"] += article.get("media_count", 0)
                stats["intelligence_analysis"]["auto_captioned"] += article.get("media_count", 0)
                stats["intelligence_analysis"]["contextually_placed"] += article.get("media_count", 0)
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        print(f"❌ Media statistics error: {str(e)}")
        return {"success": False, "error": str(e)}


def extract_media_from_content(content: str) -> List[Dict[str, str]]:
    """
    Extract all media items from markdown content
    
    Returns:
        List of dictionaries containing media information
    """
    import re
    media_items = []
    
    # Pattern for markdown images with base64 data
    image_pattern = r'!\[(.*?)\]\((data:image\/[^;]+;base64,[^)]+)\)'
    
    # Pattern for markdown videos with base64 data  
    video_pattern = r'!\[(.*?)\]\((data:video\/[^;]+;base64,[^)]+)\)'
    
    # Find all image matches
    for match in re.finditer(image_pattern, content):
        alt_text, data_url = match.groups()
        media_items.append({
            'type': 'image',
            'alt_text': alt_text,
            'data_url': data_url,
            'original_markdown': match.group(0)
        })
    
    # Find all video matches
    for match in re.finditer(video_pattern, content):
        alt_text, data_url = match.groups()
        media_items.append({
            'type': 'video',
            'alt_text': alt_text,
            'data_url': data_url,
            'original_markdown': match.group(0)
        })
    
    return media_items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)