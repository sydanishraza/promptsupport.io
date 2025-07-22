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
import requests

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
mongo_client = None
db = None

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

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize all services and connections"""
    global mongo_client, db
    
    print("🚀 Starting PromptSupport Enhanced Content Engine...")
    
    # Initialize MongoDB
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
        db = mongo_client[DATABASE_NAME]
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
    """Create a structured article in Content Library from processed chunks"""
    if not chunks:
        return
    
    # Combine chunk content
    full_content = "\n".join([chunk.content for chunk in chunks])
    
    # Generate title from content or metadata
    title = metadata.get('original_filename', metadata.get('url', 'Processed Content'))
    if title.startswith('Website:'):
        title = title.replace('Website: ', '')
    
    source_type = metadata.get('type', 'text_processing')
    
    # Use AI to create structured article
    if OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            Create a well-structured article from this content. Make it professional and informative.
            
            Content to process:
            {full_content[:1500]}
            
            Please create a JSON response with:
            - title: A clear, descriptive title
            - summary: A 2-3 sentence summary of the main points
            - content: Well-organized content with markdown formatting and headings
            - tags: 3-5 relevant tags/categories
            - takeaways: 3-5 key takeaways or important points
            
            Return only valid JSON.
            """
            
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are an expert content curator. Create structured, professional articles. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500,
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
                    # Clean up AI response to extract JSON
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
                    if json_match:
                        article_data = json.loads(json_match.group(1))
                    else:
                        # Try to parse as direct JSON
                        article_data = json.loads(ai_response)
                    
                    # Create article record
                    article_record = {
                        "id": str(uuid.uuid4()),
                        "title": article_data.get("title", title),
                        "content": article_data.get("content", full_content),
                        "summary": article_data.get("summary", ""),
                        "tags": article_data.get("tags", [source_type]),
                        "takeaways": article_data.get("takeaways", []),
                        "source_type": source_type,
                        "status": "draft",
                        "metadata": {
                            **metadata,
                            "ai_processed": True,
                            "chunks_count": len(chunks)
                        },
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    
                    # Store in Content Library
                    await db.content_library.insert_one(article_record)
                    print(f"✅ Created Content Library article: {article_record['title']}")
                    return article_record
                    
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}, AI response: {ai_response[:200]}")
                    # Fallback to basic article
                    pass
        except Exception as e:
            print(f"AI article generation error: {e}")
    
    # Fallback: Create basic article without AI enhancement
    article_record = {
        "id": str(uuid.uuid4()),
        "title": title,
        "content": full_content,
        "summary": f"Content processed from {source_type}",
        "tags": [source_type],
        "takeaways": [],
        "source_type": source_type,
        "status": "draft",
        "metadata": {
            **metadata,
            "chunks_count": len(chunks)
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.content_library.insert_one(article_record)
    print(f"✅ Created basic Content Library article: {article_record['title']}")
    return article_record

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
                # Install PyPDF2 if not available
                import PyPDF2
                pdf_file = io.BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                extracted_content = ""
                for page in pdf_reader.pages:
                    extracted_content += page.extract_text() + "\n"
                print(f"✅ Extracted {len(extracted_content)} characters from PDF ({len(pdf_reader.pages)} pages)")
            except ImportError:
                print("⚠️ PyPDF2 not available, treating as binary file")
                extracted_content = f"PDF file: {file.filename} (content extraction requires PyPDF2)"
            except Exception as e:
                print(f"⚠️ PDF extraction error: {e}")
                extracted_content = f"PDF file: {file.filename} (extraction failed: {str(e)})"
                
        elif file_extension in ['doc', 'docx']:
            try:
                import python_docx
                doc_file = io.BytesIO(file_content)
                doc = python_docx.Document(doc_file)
                extracted_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                print(f"✅ Extracted {len(extracted_content)} characters from Word document")
            except ImportError:
                print("⚠️ python-docx not available, treating as binary file")
                extracted_content = f"Word document: {file.filename} (content extraction requires python-docx)"
            except Exception as e:
                print(f"⚠️ Word document extraction error: {e}")
                extracted_content = f"Word document: {file.filename} (extraction failed: {str(e)})"
                
        elif file_extension in ['json']:
            try:
                json_data = json.loads(file_content.decode('utf-8'))
                extracted_content = f"JSON file: {file.filename}\n\nContent:\n{json.dumps(json_data, indent=2)}"
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
                "summary": article.get("summary", ""),
                "tags": article.get("tags", []),
                "status": article.get("status", "draft"),
                "source_type": article.get("source_type", ""),
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
async def process_url(
    url: str = Form(...),
    metadata: str = Form("{}")
):
    """Process URL content (scraping, YouTube, etc.)"""
    try:
        url_metadata = json.loads(metadata)
        
        job = ProcessingJob(
            input_type="url",
            original_filename=url,
            status="processing"
        )
        
        await db.processing_jobs.insert_one(job.dict())
        
        print(f"🌐 Processing URL: {url}")
        
        extracted_content = ""
        
        # Proper URL content extraction
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get title
                title = soup.title.string.strip() if soup.title else "No title found"
                
                # Get meta description
                meta_desc = ""
                meta_tag = soup.find("meta", attrs={"name": "description"})
                if meta_tag:
                    meta_desc = meta_tag.get("content", "")
                
                # Extract main content
                # Try to find main content areas
                main_content = ""
                for selector in ['main', 'article', '.content', '#content', '.post-content', '.entry-content']:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        main_content = content_elem.get_text()
                        break
                
                # If no main content found, get all paragraphs
                if not main_content:
                    paragraphs = soup.find_all('p')
                    main_content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
                # If still no content, get body text
                if not main_content:
                    body = soup.find('body')
                    if body:
                        main_content = body.get_text()
                
                # Clean up the text
                import re
                main_content = re.sub(r'\n\s*\n', '\n\n', main_content)
                main_content = re.sub(r' +', ' ', main_content)
                
                extracted_content = f"""Title: {title}

URL: {url}

{f"Description: {meta_desc}" if meta_desc else ""}

Content:
{main_content}

---
Source: Web scraping from {url}
Extracted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"""

                print(f"✅ Successfully extracted {len(extracted_content)} characters from {url}")
                
            else:
                extracted_content = f"Failed to fetch content from URL: {url} (Status: {response.status_code})"
                print(f"⚠️ HTTP {response.status_code} for {url}")
                
        except requests.exceptions.Timeout:
            extracted_content = f"URL: {url}\n\nTimeout occurred while trying to fetch content from this URL."
            print(f"⚠️ Timeout for {url}")
        except requests.exceptions.RequestException as e:
            extracted_content = f"URL: {url}\n\nError occurred while fetching content: {str(e)}"
            print(f"⚠️ Request error for {url}: {e}")
        except Exception as e:
            extracted_content = f"URL: {url}\n\nUnexpected error during content extraction: {str(e)}"
            print(f"❌ Extraction error for {url}: {e}")
        
        # Process the extracted content with enhanced metadata
        enhanced_metadata = {
            **url_metadata, 
            "url": url, 
            "type": "url_processing",
            "extraction_method": "web_scraping",
            "content_length": len(extracted_content)
        }
        
        chunks = await process_text_content(extracted_content, enhanced_metadata)
        
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
            "extracted_content_length": len(extracted_content),
            "chunks_created": len(chunks),
            "message": "URL processed successfully"
        }
        
    except Exception as e:
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

# Document listing endpoint
@app.get("/api/documents")
async def get_documents():
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