from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio
import tempfile
import aiofiles
import json
import hashlib
import re

# MongoDB
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import pymongo

# LLM Chat Integration - Disabled for MVP
# from emergentintegrations.llm.chat import LlmChat, UserMessage

# AssemblyAI
import assemblyai as aai

# Environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = AsyncIOMotorClient(MONGO_URL)
db = client.promptsupport

# Simple in-memory text store for MVP (no vector embeddings)
text_store: Dict[str, Dict[str, Any]] = {}

# AssemblyAI
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "be9ebbc1c2fb4b9e9a011549ec0e75a0")

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    session_id: str

class DocumentInfo(BaseModel):
    id: str
    filename: str
    type: str
    status: str
    processed_at: Optional[datetime]

# API Routes

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "PromptSupport API"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process documents (text, audio, video)"""
    try:
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        file_type = file.content_type or "text/plain"
        
        # Store document metadata in MongoDB
        doc_metadata = {
            "_id": doc_id,
            "filename": file.filename,
            "type": file_type,
            "status": "processing",
            "uploaded_at": datetime.utcnow(),
            "processed_at": None
        }
        await db.documents.insert_one(doc_metadata)
        
        # Process based on file type
        if file_type.startswith("text/") or file.filename.endswith(('.txt', '.md', '.doc', '.docx')):
            # Text document processing
            text_content = content.decode('utf-8')
            await process_text_document(doc_id, text_content, file.filename)
            
        elif file_type.startswith("audio/") or file_type.startswith("video/"):
            # Audio/video processing with AssemblyAI
            await process_media_file(doc_id, content, file.filename)
            
        else:
            # Unsupported file type
            await db.documents.update_one(
                {"_id": doc_id},
                {"$set": {"status": "error", "error": "Unsupported file type"}}
            )
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        return {"document_id": doc_id, "status": "processing", "filename": file.filename}
        
    except Exception as e:
        return {"error": str(e)}

async def process_text_document(doc_id: str, text_content: str, filename: str):
    """Process text document and store chunks"""
    try:
        # Split text into chunks (simple splitting for MVP)
        chunks = split_text_into_chunks(text_content)
        
        # Store in simple in-memory text store
        for i, chunk in enumerate(chunks):
            point_id = f"{doc_id}_{i}"
            text_store[point_id] = {
                "text": chunk,
                "keywords": extract_keywords(chunk),
                "payload": {
                    "document_id": doc_id,
                    "chunk_index": i,
                    "text": chunk,
                    "filename": filename
                }
            }
        
        # Update document status
        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {
                "status": "completed",
                "processed_at": datetime.utcnow(),
                "chunk_count": len(chunks)
            }}
        )
        
    except Exception as e:
        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {"status": "error", "error": str(e)}}
        )

async def process_media_file(doc_id: str, file_content: bytes, filename: str):
    """Process audio/video file with AssemblyAI"""
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name
        
        # Upload to AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(temp_path)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"AssemblyAI error: {transcript.error}")
        
        # Process transcribed text
        await process_text_document(doc_id, transcript.text, filename)
        
        # Clean up temp file
        os.unlink(temp_path)
        
    except Exception as e:
        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {"status": "error", "error": str(e)}}
        )

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 100):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = text.rfind('.', start, end)
            if last_period > start + chunk_size // 2:
                end = last_period + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        
    return chunks

def extract_keywords(text: str) -> List[str]:
    """Extract simple keywords from text for basic search"""
    # Simple keyword extraction - remove common words and extract meaningful terms
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    # Extract words (alphanumeric sequences)
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    
    # Filter out common words and short words
    keywords = [word for word in words if len(word) > 2 and word not in common_words]
    
    # Return unique keywords
    return list(set(keywords))

def search_similar_chunks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search for similar chunks using simple keyword matching"""
    query_keywords = set(extract_keywords(query))
    results = []
    
    for point_id, data in text_store.items():
        chunk_keywords = set(data["keywords"])
        
        # Calculate simple similarity based on keyword overlap
        if query_keywords and chunk_keywords:
            similarity = len(query_keywords.intersection(chunk_keywords)) / len(query_keywords.union(chunk_keywords))
        else:
            similarity = 0.0
        
        # Also check for direct text matches
        if query.lower() in data["text"].lower():
            similarity += 0.3
        
        if similarity > 0.1:  # Lower threshold for keyword matching
            results.append({
                "id": point_id,
                "score": similarity,
                "payload": data["payload"]
            })
    
    # Sort by similarity score (descending) and limit results
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

@app.post("/api/chat")
async def chat_with_documents(chat_request: ChatMessage):
    """Chat with AI using document context - MVP version returns search results"""
    try:
        session_id = chat_request.session_id
        user_query = chat_request.message
        
        # Search similar content using keyword matching
        search_results = search_similar_chunks(user_query, limit=5)
        
        # Extract context and sources
        context_chunks = []
        sources = []
        for result in search_results:
            context_chunks.append(result["payload"]["text"])
            sources.append(result["payload"]["filename"])
        
        # For MVP, return a simple response with found context
        if context_chunks:
            ai_response = f"I found {len(context_chunks)} relevant document sections related to your query:\n\n" + "\n\n---\n\n".join(context_chunks[:2])  # Limit to first 2 chunks
        else:
            ai_response = "I couldn't find any relevant documents for your query. Please try uploading some documents first or rephrase your question."
        
        # Store chat history in MongoDB
        chat_record = {
            "session_id": session_id,
            "user_message": user_query,
            "ai_response": ai_response,
            "sources": list(set(sources)),
            "timestamp": datetime.utcnow()
        }
        await db.chat_history.insert_one(chat_record)
        
        return ChatResponse(
            response=ai_response,
            sources=list(set(sources)),
            session_id=session_id
        )
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/documents")
async def list_documents():
    """Get list of uploaded documents"""
    try:
        documents = await db.documents.find({}).to_list(length=100)
        return [DocumentInfo(
            id=doc["_id"],
            filename=doc["filename"],
            type=doc["type"],
            status=doc["status"],
            processed_at=doc.get("processed_at")
        ) for doc in documents]
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = await db.chat_history.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).to_list(length=50)
        
        # Convert ObjectId to string for JSON serialization
        for record in history:
            if "_id" in record:
                record["_id"] = str(record["_id"])
        
        return history
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)