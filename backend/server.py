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

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import motor.motor_asyncio
from pymongo import MongoClient
import aiofiles
from dotenv import load_dotenv

# AI Integration imports
from emergentintegrations.llm.chat import LlmChat, UserMessage
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from jose import jwt, JWTError
import assemblyai as aai
from sentence_transformers import SentenceTransformer
import magic
from PIL import Image

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients
mongo_client: motor.motor_asyncio.AsyncIOMotorClient = None
db: motor.motor_asyncio.AsyncIOMotorDatabase = None
qdrant_client: QdrantClient = None
embedding_model: SentenceTransformer = None

# Pydantic Models
class DocumentChunk(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
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

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize all services and connections"""
    global mongo_client, db, qdrant_client, embedding_model
    
    print("🚀 Starting PromptSupport Enhanced Content Engine...")
    
    # Initialize MongoDB
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        db = mongo_client[DATABASE_NAME]
        await db.admin.command('ping')
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise
    
    # Initialize Qdrant (will create client even if server not running for now)
    try:
        qdrant_client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            api_key=QDRANT_API_KEY if QDRANT_API_KEY else None
        )
        print("✅ Qdrant client initialized")
    except Exception as e:
        print(f"⚠️ Qdrant client initialization warning: {e}")
    
    # Initialize embedding model
    try:
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence transformer model loaded")
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        raise
    
    # Configure AssemblyAI
    if ASSEMBLYAI_API_KEY:
        aai.settings.api_key = ASSEMBLYAI_API_KEY
        print("✅ AssemblyAI configured")
    
    print("🎉 Enhanced Content Engine started successfully!")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "mongodb": "connected" if mongo_client else "disconnected",
            "qdrant": "initialized" if qdrant_client else "not initialized",
            "embedding_model": "loaded" if embedding_model else "not loaded",
            "assemblyai": "configured" if ASSEMBLYAI_API_KEY else "not configured"
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
                "embedding_model": "all-MiniLM-L6-v2"
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
        await db.processing_jobs.update_one(
            {"job_id": job.job_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )
        raise HTTPException(status_code=500, detail=str(e))

async def process_text_content(content: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
    """Process text content into chunks with embeddings"""
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
                    embedding = embedding_model.encode(chunk_text).tolist()
                    chunk = DocumentChunk(
                        content=chunk_text,
                        metadata=metadata,
                        embedding=embedding
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
            embedding = embedding_model.encode(chunk_text).tolist()
            chunk = DocumentChunk(
                content=chunk_text,
                metadata=metadata,
                embedding=embedding
            )
            chunks.append(chunk)
            await db.document_chunks.insert_one(chunk.dict())
        
        return chunks
        
    except Exception as e:
        print(f"Error processing text content: {e}")
        raise

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
        file_type = magic.from_buffer(file_content, mime=True)
        
        print(f"Processing file: {file.filename}, Type: {file_type}")
        
        chunks = []
        
        if file_type.startswith('text/'):
            # Process text file
            text_content = file_content.decode('utf-8')
            chunks = await process_text_content(text_content, file_metadata)
            
        elif file_type.startswith('audio/') or file_type.startswith('video/'):
            # Process audio/video with AssemblyAI
            if not ASSEMBLYAI_API_KEY:
                raise HTTPException(status_code=400, detail="AssemblyAI not configured")
            
            # Save file temporarily
            temp_filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
            async with aiofiles.open(temp_filename, "wb") as f:
                await f.write(file_content)
            
            try:
                # Transcribe with AssemblyAI
                transcriber = aai.Transcriber()
                transcript = transcriber.transcribe(temp_filename)
                
                if transcript.status == aai.TranscriptStatus.error:
                    raise Exception(f"Transcription failed: {transcript.error}")
                
                # Process transcribed text
                file_metadata["transcription"] = True
                file_metadata["original_type"] = file_type
                chunks = await process_text_content(transcript.text, file_metadata)
                
            finally:
                # Clean up temp file
                import os
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                    
        elif file_type.startswith('image/'):
            # Process image (extract text if any, or just store metadata)
            file_metadata["image_data"] = base64.b64encode(file_content).decode('utf-8')
            file_metadata["original_type"] = file_type
            
            # Create a single chunk with image metadata
            chunk = DocumentChunk(
                content=f"Image file: {file.filename}",
                metadata=file_metadata
            )
            chunks = [chunk]
            await db.document_chunks.insert_one(chunk.dict())
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
        
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
            "file_type": file_type,
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

# Semantic search endpoint
@app.post("/api/search")
async def search_content(request: SearchRequest):
    """Perform semantic search across processed content"""
    try:
        if not embedding_model:
            raise HTTPException(status_code=500, detail="Embedding model not available")
        
        # Generate query embedding
        query_embedding = embedding_model.encode(request.query).tolist()
        
        # Search in MongoDB (simple implementation)
        # In production, this would use Qdrant for vector similarity
        search_results = []
        
        # For now, simple text search in chunks
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

# AI Chat endpoint
@app.post("/api/chat")
async def chat_with_ai(
    message: str = Form(...),
    session_id: str = Form(...),
    model_provider: str = Form("openai"),
    model_name: str = Form("gpt-4o")
):
    """Chat with AI using processed content as context"""
    try:
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

        # Initialize chat based on provider
        if model_provider == "openai" and OPENAI_API_KEY:
            chat = LlmChat(
                api_key=OPENAI_API_KEY,
                session_id=session_id,
                system_message=system_message
            ).with_model("openai", model_name)
            
        elif model_provider == "anthropic" and ANTHROPIC_API_KEY:
            chat = LlmChat(
                api_key=ANTHROPIC_API_KEY,
                session_id=session_id,
                system_message=system_message
            ).with_model("anthropic", "claude-3-5-sonnet-20241022")
            
        else:
            raise HTTPException(status_code=400, detail="AI provider not configured or invalid")
        
        # Send message
        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        # Store conversation in database
        conversation_record = {
            "session_id": session_id,
            "user_message": message,
            "ai_response": response,
            "model_provider": model_provider,
            "model_name": model_name,
            "context_used": len(context_chunks),
            "timestamp": datetime.utcnow()
        }
        
        await db.conversations.insert_one(conversation_record)
        
        return {
            "response": response,
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

# List all documents/chunks
@app.get("/api/documents")
async def list_documents():
    """List all processed documents and chunks"""
    try:
        documents = []
        async for chunk in db.document_chunks.find().limit(50):
            documents.append({
                "id": chunk["id"],
                "content_preview": chunk["content"][:100] + "..." if len(chunk["content"]) > 100 else chunk["content"],
                "metadata": chunk.get("metadata", {}),
                "created_at": chunk.get("created_at")
            })
        
        return {
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)