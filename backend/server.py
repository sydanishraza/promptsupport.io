from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio
import tempfile
import aiofiles

# MongoDB
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import pymongo

# Vector embeddings and search  
from qdrant_client import QdrantClient
from qdrant_client.http import models
import openai
from sentence_transformers import SentenceTransformer

# LLM Chat Integration
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# OpenAI for embeddings
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

# Qdrant Vector DB
qdrant_client = QdrantClient(
    host="localhost",
    port=6333,
    timeout=60
)

try:
    # Try cloud connection if API key is provided
    if os.getenv("QDRANT_API_KEY"):
        qdrant_client = QdrantClient(
            url="https://localhost:6333",  # This will be replaced with actual cloud URL when provided
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=60
        )
except Exception as e:
    print(f"Failed to connect to Qdrant cloud, using local: {e}")
    qdrant_client = QdrantClient(host="localhost", port=6333, timeout=60)

# AssemblyAI
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "be9ebbc1c2fb4b9e9a011549ec0e75a0")

# Embedding model for local processing
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

COLLECTION_NAME = "document_embeddings"

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

# Initialize Qdrant collection if it doesn't exist
async def init_qdrant():
    try:
        collections = qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if COLLECTION_NAME not in collection_names:
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=384,  # all-MiniLM-L6-v2 embedding size
                    distance=models.Distance.COSINE
                )
            )
    except Exception as e:
        print(f"Qdrant initialization error: {e}")

@app.on_event("startup")
async def startup_event():
    await init_qdrant()

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
    """Process text document and store embeddings"""
    try:
        # Split text into chunks (simple splitting for MVP)
        chunks = split_text_into_chunks(text_content)
        
        # Generate embeddings for each chunk
        embeddings = embedding_model.encode(chunks)
        
        # Store in Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = f"{doc_id}_{i}"
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload={
                        "document_id": doc_id,
                        "chunk_index": i,
                        "text": chunk,
                        "filename": filename
                    }
                )
            )
        
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        
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

@app.post("/api/chat")
async def chat_with_documents(chat_request: ChatMessage):
    """Chat with AI using document context"""
    try:
        session_id = chat_request.session_id
        user_query = chat_request.message
        
        # Generate embedding for user query
        query_embedding = embedding_model.encode([user_query])
        
        # Search similar content in Qdrant
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding[0].tolist(),
            limit=5,
            score_threshold=0.7
        )
        
        # Extract context and sources
        context_chunks = []
        sources = []
        for result in search_results:
            context_chunks.append(result.payload["text"])
            sources.append(result.payload["filename"])
        
        # Create context for LLM
        context = "\n\n---\n\n".join(context_chunks)
        
        # Initialize LLM chat with context
        system_message = f"""You are an intelligent support assistant for PromptSupport. You have access to the following knowledge base:

{context}

Please answer questions based on this context. If you don't have relevant information, let the user know. Be helpful, accurate, and concise."""

        chat = LlmChat(
            api_key=os.getenv("OPENAI_API_KEY"),
            session_id=session_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        # Send message and get response
        user_message = UserMessage(text=user_query)
        ai_response = await chat.send_message(user_message)
        
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
        
        return history
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)