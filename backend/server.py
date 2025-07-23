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
from bs4 import BeautifulSoup

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

        Original Content:
        {content[:8000]}

        TRANSFORMATION REQUIREMENTS:

        1. **Content Analysis & Splitting**:
           - Identify all distinct topics, chapters, sections, or processes
           - Create 3-8 focused articles (depending on content richness)
           - Each article should cover ONE specific topic/process in depth
           - Split logically by function, process, or conceptual area

        2. **Content Enhancement & Rewriting**:
           - Completely rewrite content for clarity, flow, and technical accuracy
           - Add context, explanations, and helpful details where needed
           - Improve technical language while maintaining original intent
           - Add transitions and logical connections between concepts
           - Include troubleshooting tips, best practices, and common scenarios

        3. **Professional Structure & Formatting**:
           - Use comprehensive markdown formatting with proper headings hierarchy
           - Create detailed outlines with multiple heading levels (H1, H2, H3, H4)
           - Add bullet points, numbered lists, and checklists where appropriate
           - Include tables for data presentation when relevant
           - Add callouts, notes, warnings, and tips using markdown blockquotes
           - Create step-by-step procedures with clear numbering
           - Add code blocks or configuration examples where applicable

        4. **Production-Ready Features**:
           - Write compelling introductions that explain purpose and scope
           - Add comprehensive conclusions with next steps and related topics
           - Include "Prerequisites", "What You'll Learn", and "Key Takeaways" sections
           - Add cross-references to related articles/topics
           - Create actionable content that users can immediately implement

        5. **Metadata & SEO**:
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
                    "content": "# Article Title\\n\\n## Overview\\n\\nDetailed introduction explaining the purpose, scope, and importance of this topic...\\n\\n## Prerequisites\\n\\n- Requirement 1\\n- Requirement 2\\n\\n## What You'll Learn\\n\\n- Learning objective 1\\n- Learning objective 2\\n\\n## Main Content\\n\\n### Section 1\\n\\nDetailed explanation with context...\\n\\n#### Subsection 1.1\\n\\nSpecific details and examples...\\n\\n### Section 2\\n\\n> **💡 Pro Tip:** Add helpful insights and best practices\\n\\nStep-by-step procedures:\\n\\n1. **Step 1**: Detailed explanation\\n   - Sub-step a\\n   - Sub-step b\\n\\n2. **Step 2**: More details\\n\\n### Common Issues & Troubleshooting\\n\\n> **⚠️ Warning:** Important considerations\\n\\n- Issue 1 and solution\\n- Issue 2 and solution\\n\\n## Key Takeaways\\n\\n- Takeaway 1\\n- Takeaway 2\\n\\n## Next Steps\\n\\n- Recommended follow-up actions\\n- Related topics to explore\\n\\n## Related Articles\\n\\n- Link to related article 1\\n- Link to related article 2",
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
        """
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are an expert content curator creating knowledge base articles. Always respond with valid JSON containing multiple focused articles."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
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
            
            # Enhanced prompt for better article generation
            prompt = f"""
            You are an expert content curator and technical writer. Create a comprehensive, well-structured article from the following content.

            Original Content:
            {content[:4000]}

            Instructions:
            1. Create a clear, descriptive title that captures the main topic
            2. Write a compelling 2-3 sentence summary that highlights the key value
            3. Structure the content with proper headings and organization
            4. Use markdown formatting (## for headings, **bold**, etc.)
            5. Extract 3-5 highly relevant tags/keywords
            6. List 3-5 actionable key takeaways
            7. Make the content informative and easy to read

            Respond with valid JSON in this exact format:
            {{
                "title": "Clear, descriptive title here",
                "summary": "Compelling 2-3 sentence summary of the content's main value and purpose",
                "content": "# Main Title\\n\\n## Introduction\\n\\nWell-organized content here with proper markdown formatting...\\n\\n## Key Points\\n\\n- Point 1\\n- Point 2\\n\\n## Conclusion\\n\\nSummary and next steps...",
                "tags": ["tag1", "tag2", "tag3", "tag4"],
                "takeaways": ["First key takeaway", "Second key takeaway", "Third key takeaway"]
            }}
            """
            
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are an expert content curator and technical writer. Create professional, well-structured articles from raw content. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2500,
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
                doc_file = io.BytesIO(file_content)
                doc = docx.Document(doc_file)
                
                # Extract paragraphs with formatting info
                extracted_content = f"Document: {file.filename}\n\n"
                for para in doc.paragraphs:
                    if para.text.strip():
                        # Check if paragraph might be a heading
                        if para.style.name.startswith('Heading'):
                            extracted_content += f"## {para.text}\n\n"
                        else:
                            extracted_content += f"{para.text}\n\n"
                
                # Extract tables if present
                if doc.tables:
                    extracted_content += "\n=== TABLES ===\n"
                    for i, table in enumerate(doc.tables):
                        extracted_content += f"\nTable {i+1}:\n"
                        for row in table.rows:
                            row_data = [cell.text.strip() for cell in row.cells]
                            extracted_content += " | ".join(row_data) + "\n"
                        extracted_content += "\n"
                        
                print(f"✅ Extracted {len(extracted_content)} characters from Word document")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)