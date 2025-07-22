from fastapi import FastAPI, UploadFile, File, HTTPException, Form
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

# MongoDB
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import pymongo

# Content Engine
from content_engine import content_engine

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

class URLRequest(BaseModel):
    url: str
    source_type: str = "webpage"

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
    metadata: Optional[Dict[str, Any]] = {}

# API Routes

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "PromptSupport Enhanced Content Engine"}

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
            "processed_at": None,
            "source": "file_upload"
        }
        await db.documents.insert_one(doc_metadata)
        
        # Process based on file type
        if file_type.startswith("text/") or file.filename.endswith(('.txt', '.md', '.doc', '.docx')):
            # Text document processing
            text_content = content.decode('utf-8')
            await process_text_document(doc_id, text_content, file.filename, "file_upload")
            
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

@app.post("/api/process-url")
async def process_url(url_request: URLRequest):
    """Process URL content - web scraping, YouTube, GitHub, etc."""
    try:
        doc_id = str(uuid.uuid4())
        
        # Store initial document metadata
        doc_metadata = {
            "_id": doc_id,
            "filename": url_request.url,
            "type": "url",
            "status": "processing",
            "uploaded_at": datetime.utcnow(),
            "processed_at": None,
            "source": "url_processing",
            "url": url_request.url
        }
        await db.documents.insert_one(doc_metadata)
        
        # Process URL using content engine
        result = await content_engine.process_url(url_request.url, url_request.source_type)
        
        if result["success"]:
            # Process the extracted content
            await process_text_document(
                doc_id, 
                result["content"], 
                result["metadata"].get("title", url_request.url),
                "url_processing",
                result["metadata"]
            )
            
            return {
                "document_id": doc_id, 
                "status": "processing", 
                "url": url_request.url,
                "title": result["metadata"].get("title", ""),
                "metadata": result["metadata"]
            }
        else:
            # Update document with error
            await db.documents.update_one(
                {"_id": doc_id},
                {"$set": {"status": "error", "error": result["error"]}}
            )
            return {"error": result["error"], "document_id": doc_id}
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/process-recording")
async def process_recording(file: UploadFile = File(...)):
    """Process recorded audio/video content"""
    try:
        doc_id = str(uuid.uuid4())
        
        # Read recording data
        recording_data = await file.read()
        
        # Store initial document metadata
        doc_metadata = {
            "_id": doc_id,
            "filename": file.filename,
            "type": "recording",
            "status": "processing",
            "uploaded_at": datetime.utcnow(),
            "processed_at": None,
            "source": "recording"
        }
        await db.documents.insert_one(doc_metadata)
        
        # Process recording using content engine
        result = await content_engine.process_recording(recording_data, file.filename)
        
        if result["success"]:
            # Process the transcribed content
            await process_text_document(
                doc_id,
                result["content"],
                result["metadata"].get("title", file.filename),
                "recording",
                result["metadata"]
            )
            
            return {
                "document_id": doc_id,
                "status": "processing", 
                "filename": file.filename,
                "metadata": result["metadata"]
            }
        else:
            # Update document with error
            await db.documents.update_one(
                {"_id": doc_id},
                {"$set": {"status": "error", "error": result["error"]}}
            )
            return {"error": result["error"], "document_id": doc_id}
        
    except Exception as e:
        return {"error": str(e)}

async def process_text_document(doc_id: str, text_content: str, filename: str, source: str, extra_metadata: Dict[str, Any] = None):
    """Process text document with enhanced content analysis"""
    try:
        # Enhanced content analysis with AI
        metadata = extra_metadata or {}
        enhanced_result = await content_engine.enhance_content_with_ai(text_content, metadata)
        
        # Create enhanced chunks
        chunks_data = content_engine.create_content_chunks(text_content)
        
        # Store in simple in-memory text store with enhanced data
        for chunk_data in chunks_data:
            point_id = f"{doc_id}_{chunk_data['index']}"
            text_store[point_id] = {
                "text": chunk_data["text"],
                "keywords": extract_keywords(chunk_data["text"]),
                "enhanced_data": enhanced_result,
                "chunk_metadata": chunk_data,
                "payload": {
                    "document_id": doc_id,
                    "chunk_index": chunk_data['index'],
                    "text": chunk_data["text"],
                    "filename": filename,
                    "source": source,
                    "tags": enhanced_result.get("tags", []),
                    "category": enhanced_result.get("category", "general")
                }
            }
        
        # Update document status with enhanced metadata
        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {
                "status": "completed",
                "processed_at": datetime.utcnow(),
                "chunk_count": len(chunks_data),
                "summary": enhanced_result.get("summary", ""),
                "tags": enhanced_result.get("tags", []),
                "key_points": enhanced_result.get("key_points", []),
                "category": enhanced_result.get("category", "general"),
                "word_count": sum(chunk["word_count"] for chunk in chunks_data)
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
        # Use content engine for recording processing
        result = await content_engine.process_recording(file_content, filename)
        
        if result["success"]:
            # Process the transcribed content
            await process_text_document(
                doc_id,
                result["content"],
                filename,
                "media_file",
                result["metadata"]
            )
        else:
            await db.documents.update_one(
                {"_id": doc_id},
                {"$set": {"status": "error", "error": result["error"]}}
            )
        
    except Exception as e:
        await db.documents.update_one(
            {"_id": doc_id},
            {"$set": {"status": "error", "error": str(e)}}
        )

def extract_keywords(text: str) -> List[str]:
    """Extract simple keywords from text for basic search"""
    # Enhanced keyword extraction
    import re
    
    # Common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
        'his', 'her', 'its', 'our', 'their', 'much', 'many', 'most', 'more', 'some', 'any', 'no',
        'not', 'only', 'just', 'very', 'so', 'now', 'then', 'than', 'too', 'also', 'well', 'here',
        'there', 'where', 'when', 'why', 'how', 'what', 'who', 'which', 'all', 'each', 'every',
        'both', 'either', 'neither', 'such', 'same', 'different', 'other', 'another', 'first',
        'last', 'next', 'previous', 'new', 'old', 'good', 'bad', 'big', 'small', 'long', 'short'
    }
    
    # Extract words and phrases
    words = re.findall(r'\b[a-zA-Z0-9_-]+\b', text.lower())
    
    # Filter keywords
    keywords = []
    for word in words:
        if len(word) >= 3 and word not in stop_words:
            keywords.append(word)
    
    # Extract important phrases (2-3 word combinations)
    phrases = []
    for i in range(len(words) - 1):
        if len(words[i]) >= 3 and len(words[i+1]) >= 3:
            phrase = f"{words[i]} {words[i+1]}"
            if not any(w in stop_words for w in [words[i], words[i+1]]):
                phrases.append(phrase)
    
    # Combine and deduplicate
    all_keywords = list(set(keywords + phrases))
    
    # Return top keywords based on frequency
    from collections import Counter
    word_freq = Counter(keywords)
    top_words = [word for word, freq in word_freq.most_common(20)]
    
    return top_words + [p for p in phrases if p not in top_words][:10]

def search_similar_chunks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Enhanced search with category and tag matching"""
    query_keywords = set(extract_keywords(query))
    query_lower = query.lower()
    results = []
    
    for point_id, data in text_store.items():
        chunk_keywords = set(data["keywords"])
        enhanced_data = data.get("enhanced_data", {})
        
        score = 0.0
        
        # Keyword matching
        if query_keywords and chunk_keywords:
            keyword_similarity = len(query_keywords.intersection(chunk_keywords)) / len(query_keywords.union(chunk_keywords))
            score += keyword_similarity * 0.4
        
        # Direct text matching
        if query_lower in data["text"].lower():
            score += 0.3
        
        # Tag matching
        tags = enhanced_data.get("tags", [])
        if tags and any(tag.lower() in query_lower for tag in tags):
            score += 0.2
        
        # Category matching
        category = enhanced_data.get("category", "")
        if category and category.lower() in query_lower:
            score += 0.1
        
        if score > 0.05:  # Lower threshold for better recall
            results.append({
                "id": point_id,
                "score": score,
                "payload": data["payload"],
                "enhanced_data": enhanced_data
            })
    
    # Sort by similarity score (descending) and limit results
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

@app.post("/api/chat")
async def chat_with_documents(chat_request: ChatMessage):
    """Enhanced chat with AI using document context"""
    try:
        session_id = chat_request.session_id
        user_query = chat_request.message
        
        # Search similar content using enhanced search
        search_results = search_similar_chunks(user_query, limit=5)
        
        # Extract context and sources with enhanced metadata
        context_chunks = []
        sources = []
        categories = []
        tags = []
        
        for result in search_results:
            payload = result["payload"]
            enhanced_data = result.get("enhanced_data", {})
            
            context_chunks.append(payload["text"])
            sources.append(payload["filename"])
            
            if enhanced_data.get("category"):
                categories.append(enhanced_data["category"])
            if enhanced_data.get("tags"):
                tags.extend(enhanced_data["tags"])
        
        # Enhanced response with metadata
        if context_chunks:
            unique_categories = list(set(categories))
            unique_tags = list(set(tags))
            
            ai_response = f"""I found {len(context_chunks)} relevant document sections for your query.

**Relevant Content:**

{context_chunks[0][:500] + '...' if len(context_chunks[0]) > 500 else context_chunks[0]}

**Additional Context:**
- Categories: {', '.join(unique_categories) if unique_categories else 'General'}
- Tags: {', '.join(unique_tags[:5]) if unique_tags else 'None'}
- Sources: {len(set(sources))} document(s)"""
        else:
            ai_response = "I couldn't find relevant documents for your query. Try uploading documents or processing URLs first, or rephrase your question with different keywords."
        
        # Store chat history in MongoDB
        chat_record = {
            "session_id": session_id,
            "user_message": user_query,
            "ai_response": ai_response,
            "sources": list(set(sources)),
            "categories": list(set(categories)),
            "tags": list(set(tags)),
            "search_results_count": len(search_results),
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
    """Get list of uploaded documents with enhanced metadata"""
    try:
        documents = await db.documents.find({}).to_list(length=100)
        return [DocumentInfo(
            id=doc["_id"],
            filename=doc["filename"],
            type=doc["type"],
            status=doc["status"],
            processed_at=doc.get("processed_at"),
            metadata={
                "source": doc.get("source", "unknown"),
                "summary": doc.get("summary", ""),
                "tags": doc.get("tags", []),
                "category": doc.get("category", "general"),
                "word_count": doc.get("word_count", 0),
                "chunk_count": doc.get("chunk_count", 0)
            }
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

@app.get("/api/analytics/content")
async def get_content_analytics():
    """Get content analytics and insights"""
    try:
        # Document counts by type
        doc_pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        doc_stats = await db.documents.aggregate(doc_pipeline).to_list(length=100)
        
        # Document counts by status
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_stats = await db.documents.aggregate(status_pipeline).to_list(length=100)
        
        # Top categories and tags
        category_pipeline = [
            {"$match": {"category": {"$exists": True}}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        category_stats = await db.documents.aggregate(category_pipeline).to_list(length=100)
        
        # Chat activity
        chat_count = await db.chat_history.count_documents({})
        
        return {
            "total_documents": await db.documents.count_documents({}),
            "total_chats": chat_count,
            "documents_by_type": {item["_id"]: item["count"] for item in doc_stats},
            "documents_by_status": {item["_id"]: item["count"] for item in status_stats},
            "top_categories": [{"category": item["_id"], "count": item["count"]} for item in category_stats],
            "content_chunks": len(text_store)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)