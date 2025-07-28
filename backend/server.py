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
from bson import ObjectId

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
import markdown
from bs4 import BeautifulSoup
from media_intelligence import media_intelligence

# Load environment variables
load_dotenv()

# Helper function to convert ObjectId to string for JSON serialization
def objectid_to_str(data):
    """Convert ObjectId to string for JSON serialization"""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [objectid_to_str(item) for item in data]
    return data

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

# Mount static files for serving uploaded images under /api/static route
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/api/static", StaticFiles(directory=static_dir), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DOCUMENT PROCESSING HELPER FUNCTIONS ===

def is_table_of_contents(text: str, position: int = 0) -> bool:
    """Detect Table of Contents sections"""
    toc_indicators = [
        'table of contents',
        'contents',
        'index',
        '...........',  # Dotted lines common in TOCs
    ]
    
    text_lower = text.lower()
    
    # Check for TOC title
    if any(indicator in text_lower for indicator in toc_indicators[:3]):
        return True
        
    # Check for dotted lines or page numbers (TOC formatting)
    if ('.' * 5 in text) or (re.search(r'\d+$', text.strip())):
        return True
        
    # Check if this looks like a TOC entry (short line with numbers)
    if len(text) < 100 and re.search(r'^\w.*\d+$', text.strip()):
        return True
        
    return False

def is_header_footer_or_page_number(text: str) -> bool:
    """Detect headers, footers, and page numbers"""
    # Page numbers (just numbers or "Page X")
    if re.match(r'^(page\s+)?\d+$', text.lower().strip()):
        return True
        
    # Very short text that might be headers/footers
    if len(text.strip()) < 10 and not any(c.isalpha() for c in text):
        return True
        
    # Common header/footer patterns
    header_footer_patterns = [
        r'^\d+$',  # Just numbers
        r'^page \d+',  # Page numbers
        r'confidential',
        r'proprietary',
        r'draft',
        r'version \d+',
    ]
    
    return any(re.search(pattern, text.lower()) for pattern in header_footer_patterns)

def is_legal_disclaimer(text: str) -> bool:
    """Detect legal disclaimers and copyright notices"""
    legal_patterns = [
        r'copyright',
        r'©',
        r'all rights reserved',
        r'proprietary and confidential',
        r'trademark',
        r'disclaimer',
        r'terms of use',
        r'privacy policy',
        r'legal notice'
    ]
    
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in legal_patterns)

def is_cover_page(paragraphs_sample: list) -> bool:
    """Detect if the first few paragraphs constitute a cover page"""
    if not paragraphs_sample:
        return False
        
    first_page_text = '\n'.join([p.text for p in paragraphs_sample[:5] if hasattr(p, 'text')])
    
    cover_indicators = [
        len(first_page_text.split('\n')) <= 5 and any(word in first_page_text.upper() for word in ['GUIDE', 'MANUAL', 'DOCUMENT', 'REPORT']),
        first_page_text.count('\n') <= 3 and len(first_page_text) < 200,
        any(pattern in first_page_text.upper() for pattern in ['COPYRIGHT', '©', 'ALL RIGHTS RESERVED'])
    ]
    
    return any(cover_indicators)

def detect_heading_level_from_text(text: str) -> int:
    """Detect heading level from text patterns"""
    text = text.strip()
    
    # Check for numbered headings
    if re.match(r'^\d+\.?\s+', text):
        return 2
    if re.match(r'^\d+\.\d+\.?\s+', text):
        return 3
    if re.match(r'^\d+\.\d+\.\d+\.?\s+', text):
        return 4
        
    # Check for text patterns that suggest headings
    if text.isupper() and len(text) < 100:
        return 1
    if text.endswith(':') and len(text) < 80:
        return 3
        
    return None

async def regenerate_articles_with_enhanced_context(extracted_content: dict, contextual_images: list, template_data: dict, training_session: dict) -> list:
    """Phase 2: Enhanced article regeneration with contextual analysis"""
    try:
        print(f"🪄 Phase 2: Starting enhanced article regeneration")
        
        # Analyze content structure for semantic splitting
        articles_data = []
        current_article = {
            "content_blocks": [],
            "images": [],
            "headings": [],
            "title": ""
        }
        
        h1_count = 0
        
        for block in extracted_content['structure']:
            block_type = block['type']
            content = block['content']
            
            # Major heading changes trigger new articles
            if block_type == 'h1':
                # Save current article if it has content
                if current_article['content_blocks']:
                    articles_data.append(current_article)
                
                # Start new article
                h1_count += 1
                current_article = {
                    "content_blocks": [block],
                    "images": [],
                    "headings": [content],
                    "title": content or f"Article {h1_count}"
                }
            elif block_type == 'h2' and len(current_article['content_blocks']) > 0:
                # H2 might trigger new article if current is getting long
                current_word_count = sum(len(b['content'].split()) for b in current_article['content_blocks'])
                if current_word_count > 800:  # Max words per article
                    # Save current article and start new one
                    articles_data.append(current_article)
                    current_article = {
                        "content_blocks": [block],
                        "images": [],
                        "headings": [content],
                        "title": content or f"Article {len(articles_data) + 1}"
                    }
                else:
                    current_article['content_blocks'].append(block)
                    current_article['headings'].append(content)
            else:
                current_article['content_blocks'].append(block)
        
        # Add final article
        if current_article['content_blocks']:
            articles_data.append(current_article)
        
        # Distribute images across articles based on context
        images_per_article = len(contextual_images) // max(1, len(articles_data))
        for i, article_data in enumerate(articles_data):
            start_idx = i * images_per_article
            end_idx = start_idx + images_per_article if i < len(articles_data) - 1 else len(contextual_images)
            article_data['images'] = contextual_images[start_idx:end_idx]
        
        # Generate final articles
        final_articles = []
        
        for i, article_data in enumerate(articles_data):
            # Create structured content
            html_content = await generate_enhanced_html_content(article_data, template_data)
            markdown_content = await generate_enhanced_markdown_content(article_data, template_data)
            
            # Create media array with placement info
            media_array = []
            for img in article_data['images']:
                media_array.append({
                    "url": img['url'],
                    "alt": img['alt_text'],
                    "caption": img.get('caption', ''),
                    "placement": img.get('placement', 'inline'),
                    "filename": img['filename']
                })
            
            article = {
                "id": str(uuid.uuid4()),
                "title": f"Article {i+1} From {training_session['filename']}" if not article_data['title'] else article_data['title'],
                "html": html_content,
                "markdown": markdown_content,
                "content": html_content,  # For backward compatibility
                "media": media_array,
                "tags": ["extracted", "generated", "enhanced"],
                "status": "training",
                "template_id": training_session['template_id'],
                "session_id": training_session['session_id'],
                "word_count": len(html_content.split()),
                "image_count": len(media_array),
                "format": "html",
                "created_at": datetime.utcnow().isoformat(),
                "ai_processed": True,
                "ai_model": "gpt-4o (with claude fallback)",
                "training_mode": True,
                "metadata": {
                    "article_number": i + 1,
                    "source_filename": training_session['filename'],
                    "template_applied": training_session['template_id'],
                    "phase": "enhanced_extraction"
                }
            }
            
            final_articles.append(article)
            print(f"📄 Generated enhanced article {i+1}: {len(html_content)} chars, {len(media_array)} images")
        
        print(f"✅ Phase 2 Complete: Generated {len(final_articles)} enhanced articles")
        return final_articles
        
    except Exception as e:
        print(f"❌ Enhanced regeneration error: {e}")
        import traceback
        traceback.print_exc()
        return []

async def generate_enhanced_html_content(article_data: dict, template_data: dict) -> str:
    """Generate HTML content for an article"""
    html_parts = []
    
    # Add title
    if article_data['title']:
        html_parts.append(f"<h1>{article_data['title']}</h1>")
    
    # Process content blocks
    image_index = 0
    
    for block in article_data['content_blocks']:
        block_type = block['type']
        content = block['content']
        
        if block_type.startswith('h'):
            level = block_type[1]
            html_parts.append(f"<{block_type}>{content}</{block_type}>")
        elif block_type == 'paragraph':
            html_parts.append(f"<p>{content}</p>")
            
            # Insert image after some paragraphs
            if image_index < len(article_data['images']) and len(html_parts) % 3 == 0:
                img = article_data['images'][image_index]
                img_html = f'<figure class="embedded-image"><img src="{img["url"]}" alt="{img["alt_text"]}" style="max-width: 100%; height: auto; margin: 1rem 0;"><figcaption>{img.get("caption", f"Figure {image_index + 1}")}</figcaption></figure>'
                html_parts.append(img_html)
                image_index += 1
    
    # Add remaining images at the end
    while image_index < len(article_data['images']):
        img = article_data['images'][image_index]
        img_html = f'<figure class="embedded-image"><img src="{img["url"]}" alt="{img["alt_text"]}" style="max-width: 100%; height: auto; margin: 1rem 0;"><figcaption>{img.get("caption", f"Figure {image_index + 1}")}</figcaption></figure>'
        html_parts.append(img_html)
        image_index += 1
    
    return '\n\n'.join(html_parts)

async def generate_enhanced_markdown_content(article_data: dict, template_data: dict) -> str:
    """Generate Markdown content for an article"""
    md_parts = []
    
    # Add title
    if article_data['title']:
        md_parts.append(f"# {article_data['title']}")
    
    # Process content blocks
    image_index = 0
    
    for block in article_data['content_blocks']:
        block_type = block['type']
        content = block['content']
        
        if block_type == 'h1':
            md_parts.append(f"# {content}")
        elif block_type == 'h2':
            md_parts.append(f"## {content}")
        elif block_type == 'h3':
            md_parts.append(f"### {content}")
        elif block_type == 'h4':
            md_parts.append(f"#### {content}")
        elif block_type == 'paragraph':
            # Convert HTML formatting to Markdown
            md_content = content.replace('<strong>', '**').replace('</strong>', '**')
            md_content = md_content.replace('<em>', '*').replace('</em>', '*')
            md_content = md_content.replace('<u>', '_').replace('</u>', '_')
            md_parts.append(md_content)
            
            # Insert image after some paragraphs
            if image_index < len(article_data['images']) and len(md_parts) % 3 == 0:
                img = article_data['images'][image_index]
                md_parts.append(f"![{img['alt_text']}]({img['url']})")
                if img.get('caption'):
                    md_parts.append(f"*{img['caption']}*")
                image_index += 1
    
    # Add remaining images at the end
    while image_index < len(article_data['images']):
        img = article_data['images'][image_index]
        md_parts.append(f"![{img['alt_text']}]({img['url']})")
        if img.get('caption'):
            md_parts.append(f"*{img['caption']}*")
        image_index += 1
    
    return '\n\n'.join(md_parts)

# === END HELPER FUNCTIONS ===

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

async def call_llm_with_fallback(system_message: str, user_message: str, session_id: str = None) -> Optional[str]:
    """
    Call LLM with OpenAI first, fallback to Claude if OpenAI fails
    Returns the response text or None if both fail
    """
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    # Try OpenAI first
    if OPENAI_API_KEY:
        try:
            print("🤖 Attempting OpenAI (GPT-4o) call...")
            
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 6000,
                "temperature": 0.1
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30  # Reduced from 45 to 30 seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                print(f"✅ OpenAI response successful: {len(ai_response)} characters")
                return ai_response
            else:
                error_msg = str(response.status_code) + " " + response.text
                print(f"❌ OpenAI failed: {error_msg}")
                
                # Check if it's a quota/rate limit error
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    print("🔄 OpenAI quota/rate limit exceeded, switching to Claude...")
                else:
                    print("🔄 OpenAI error detected, switching to Claude...")
                    
        except Exception as e:
            print(f"❌ OpenAI failed with exception: {e}")
            print("🔄 Switching to Claude...")
    
    # Try Claude as fallback
    if ANTHROPIC_API_KEY:
        try:
            print("🤖 Attempting Claude fallback call...")
            
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 6000,
                "system": system_message,
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30  # Reduced from 45 to 30 seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["content"][0]["text"]
                print(f"✅ Claude response successful: {len(ai_response)} characters")
                return ai_response
            else:
                print(f"❌ Claude also failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Claude also failed with exception: {e}")
    
    print("❌ Both OpenAI and Claude failed - no LLM response available")
    return None

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
    """Provide AI writing assistance using LLM with fallback"""
    try:
        # Prepare prompt based on mode
        prompts = {
            "completion": f"Continue this text naturally and coherently:\n\n{request.content}\n\nContinuation:",
            "improvement": f"Analyze this text and suggest specific improvements for clarity, engagement, and readability:\n\n{request.content}\n\nSuggestions:",
            "grammar": f"Check this text for grammar, spelling, and style issues and provide corrections:\n\n{request.content}\n\nCorrections:",
            "analysis": f"Analyze this content for readability, structure, tone, and provide insights:\n\n{request.content}\n\nAnalysis:"
        }
        
        prompt = prompts.get(request.mode, prompts["completion"])
        system_message = "You are a helpful writing assistant. Provide clear, actionable suggestions."
        
        # Use fallback system to get AI response
        session_id = str(uuid.uuid4())
        ai_response = await call_llm_with_fallback(system_message, prompt, session_id)
        
        if ai_response:
            # Split response into suggestions
            suggestions = [s.strip() for s in ai_response.split('\n') if s.strip()]
            
            return {
                "suggestions": suggestions[:3],  # Limit to 3 suggestions
                "mode": request.mode,
                "success": True
            }
        else:
            return {"error": "AI service temporarily unavailable", "suggestions": []}
                
    except Exception as e:
        print(f"AI assistance error: {str(e)}")
        return {"error": str(e), "suggestions": []}

@app.post("/api/content-analysis")
async def content_analysis(request: AIAssistanceRequest):
    """Analyze content for insights using LLM with fallback"""
    try:
        # Strip HTML tags for analysis
        text_content = re.sub(r'<[^>]*>', '', request.content)
        
        # Basic metrics
        words = len(text_content.split())
        sentences = len([s for s in re.split(r'[.!?]+', text_content) if s.strip()])
        paragraphs = len([p for p in text_content.split('\n\n') if p.strip()])
        
        # Get AI analysis using fallback system
        system_message = "You are a content analysis expert. Provide readability score (0-100), tone assessment, and key insights."
        user_message = f"Analyze this content:\n\n{text_content[:1000]}"
        
        session_id = str(uuid.uuid4())
        ai_response = await call_llm_with_fallback(system_message, user_message, session_id)
        
        ai_insights = ""
        readability_score = 70  # Default
        
        if ai_response:
            ai_insights = ai_response
            
            # Extract readability score if mentioned
            score_match = re.search(r'readability.*?(\d+)', ai_insights, re.IGNORECASE)
            if score_match:
                readability_score = int(score_match.group(1))
        else:
            ai_insights = "AI analysis temporarily unavailable"
        
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
    """Get all assets from the asset library including both file-based and embedded images"""
    try:
        content_collection = db["content_library"]
        assets_collection = db["assets"]
        
        # Get file-based assets from the new assets collection
        file_assets_cursor = assets_collection.find({})
        file_assets = await file_assets_cursor.to_list(length=200)
        
        # Get direct image assets from content_library (legacy)
        direct_assets_cursor = content_collection.find({"type": {"$in": ["image", "media"]}})
        direct_assets = await direct_assets_cursor.to_list(length=100)
        
        # Get articles with embedded images
        articles_cursor = content_collection.find({"content": {"$regex": "data:image", "$options": "i"}})
        articles_with_images = await articles_cursor.to_list(length=200)
        
        formatted_assets = []
        
        # Add file-based assets (new system)
        for asset in file_assets:
            formatted_assets.append({
                "id": asset.get("id", str(asset.get("_id"))),
                "name": asset.get("original_filename", asset.get("name", "Untitled")),
                "original_filename": asset.get("original_filename"),
                "type": "image",
                "url": asset.get("url"),  # File URL instead of base64
                "data": asset.get("url"),  # For compatibility, use URL as data
                "created_at": asset.get("created_at"),
                "size": asset.get("size", 0),
                "storage_type": "file"
            })
        
        # Add direct assets (legacy base64 system)
        for asset in direct_assets:
            if asset.get("data"):
                formatted_assets.append({
                    "id": asset.get("id", str(asset.get("_id"))),
                    "name": asset.get("title", asset.get("name", "Untitled")),
                    "type": "image",
                    "data": asset.get("data"),
                    "created_at": asset.get("created_at"),
                    "size": len(asset.get("data", "")) if asset.get("data") else 0,
                    "storage_type": "base64"
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
                                "size": len(image_data),
                                "storage_type": "embedded"
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
        
        # Generate URL for the file (using /api/static prefix for proper routing)
        file_url = f"/api/static/uploads/{unique_filename}"
        
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

# Training endpoints
@app.post("/api/training/process")
async def training_process_document(
    file: UploadFile = File(...),
    template_id: str = Form(...),
    training_mode: str = Form(default="true"),
    template_instructions: str = Form(default="{}")
):
    """Process document with specific training template"""
    start_time = datetime.utcnow()
    
    try:
        print(f"🚀 Starting training process for {file.filename}")
        
        # Parse template instructions
        template_data = json.loads(template_instructions)
        print(f"📋 Template data parsed: {len(template_data)} keys")
        
        # Create training session metadata
        training_session = {
            "session_id": str(uuid.uuid4()),
            "template_id": template_id,
            "filename": file.filename,
            "training_mode": training_mode == "true",
            "timestamp": datetime.utcnow().isoformat(),
            "template_data": template_data
        }
        
        print(f"📝 Created training session: {training_session['session_id']}")
        
        # Process the uploaded file
        file_content = await file.read()
        print(f"📄 File content read: {len(file_content)} bytes")
        
        # Add file size check to prevent excessive processing
        max_file_size = 50 * 1024 * 1024  # 50MB limit
        if len(file_content) > max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large ({len(file_content)} bytes). Maximum size: {max_file_size} bytes"
            )
        
        # Save file temporarily for processing
        temp_file_path = f"temp_uploads/{file.filename}"
        os.makedirs("temp_uploads", exist_ok=True)
        
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file_content)
        
        print(f"💾 Temporary file saved: {temp_file_path}")
        
        # Process based on file type
        if file.filename.lower().endswith('.docx'):
            print("🔍 Processing DOCX file")
            articles = await process_docx_with_template(temp_file_path, template_data, training_session)
        elif file.filename.lower().endswith('.doc'):
            print("🔍 Processing DOC file")
            articles = await process_doc_with_template(temp_file_path, template_data, training_session)
        elif file.filename.lower().endswith('.pdf'):
            print("🔍 Processing PDF file")
            articles = await process_pdf_with_template(temp_file_path, template_data, training_session)
        elif file.filename.lower().endswith(('.ppt', '.pptx')):
            print("🔍 Processing PowerPoint file")
            articles = await process_ppt_with_template(temp_file_path, template_data, training_session)
        elif file.filename.lower().endswith(('.xls', '.xlsx')):
            print("🔍 Processing Excel file")
            articles = await process_excel_with_template(temp_file_path, template_data, training_session)
        elif file.filename.lower().endswith(('.html', '.htm')):
            print("🔍 Processing HTML file")
            articles = await process_html_with_template(temp_file_path, template_data, training_session)
        elif file.filename.lower().endswith(('.txt', '.md')):
            print("🔍 Processing text file")
            # Read text content
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            articles = await process_text_with_template(content, template_data, training_session)
        else:
            print("🔍 Processing as default text file")
            # Default text processing
            try:
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Handle binary files
                content = f"Binary file: {file.filename} - content extraction not supported"
            articles = await process_text_with_template(content, template_data, training_session)
        
        print(f"📚 Processing complete: {len(articles)} articles generated")
        
        # Clean up temp file
        try:
            os.remove(temp_file_path)
            print(f"🧹 Cleaned up temp file: {temp_file_path}")
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup error: {cleanup_error}")
        
        # Store training session in database
        await db.training_sessions.insert_one(training_session)
        print(f"💾 Training session stored in database")
        
        # Calculate images processed and processing time
        total_images = sum(article.get("image_count", 0) for article in articles)
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        print(f"🖼️ Total images processed: {total_images}")
        print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
        
        return {
            "success": True,
            "session_id": training_session["session_id"],
            "articles": articles,
            "images_processed": total_images,
            "processing_time": round(processing_time, 2),
            "template_applied": template_id
        }
        
    except Exception as e:
        print(f"❌ Training processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/training/evaluate")
async def training_evaluate_result(request: dict):
    """Evaluate training result"""
    try:
        session_id = request.get("session_id")
        result_id = request.get("result_id")
        evaluation = request.get("evaluation")
        feedback = request.get("feedback", "")
        
        # Store evaluation in database
        evaluation_data = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "result_id": result_id,
            "evaluation": evaluation,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await db.training_evaluations.insert_one(evaluation_data)
        
        return {
            "success": True,
            "evaluation_id": evaluation_data["id"],
            "message": f"Result {evaluation} successfully"
        }
        
    except Exception as e:
        print(f"Training evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/training/templates")
async def get_training_templates():
    """Get all training templates"""
    try:
        templates_cursor = db.training_templates.find({})
        templates = await templates_cursor.to_list(length=100)
        
        return {
            "templates": templates,
            "total": len(templates)
        }
        
    except Exception as e:
        print(f"Get training templates error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/training/sessions")
async def get_training_sessions():
    """Get training session history"""
    try:
        sessions_cursor = db.training_sessions.find({}).sort("timestamp", -1)
        sessions = await sessions_cursor.to_list(length=100)
        
        # Convert ObjectId to string for JSON serialization
        clean_sessions = objectid_to_str(sessions)
        
        return {
            "sessions": clean_sessions,
            "total": len(clean_sessions)
        }
        
    except Exception as e:
        print(f"Get training sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_docx_with_template(file_path: str, template_data: dict, training_session: dict) -> list:
    """Enhanced DOCX processing with Phase 1 content extraction specification"""
    try:
        # Import docx processing libraries
        try:
            from docx import Document
            from docx.shared import Inches
            import zipfile
            from xml.etree import ElementTree as ET
        except ImportError:
            print("python-docx not installed, using fallback processing")
            return await process_text_with_template("", template_data, training_session)
        
        print(f"🔍 Phase 1: Starting enhanced DOCX content extraction")
        
        # Read DOCX content
        doc = Document(file_path)
        
        # Phase 1: Enhanced Text Extraction
        extracted_content = {
            "body_text": "",
            "headings": [],
            "tables": [],
            "lists": [],
            "structure": [],
            "inline_formatting": []
        }
        
        # Skip cover page detection
        skip_first_page = is_cover_page(doc.paragraphs[:5])
        if skip_first_page:
            print(f"🚫 Detected and skipping cover page")
        
        # Extract meaningful content with structure preservation
        paragraph_start = 1 if skip_first_page else 0
        
        for i, paragraph in enumerate(doc.paragraphs[paragraph_start:], paragraph_start):
            text = paragraph.text.strip()
            if not text:
                continue
                
            # Skip Table of Contents detection
            if is_table_of_contents(text, i):
                print(f"🚫 Skipping Table of Contents at paragraph {i}")
                continue
                
            # Skip page numbers and headers/footers
            if is_header_footer_or_page_number(text):
                print(f"🚫 Skipping header/footer/page number: {text[:50]}...")
                continue
                
            # Skip legal disclaimers
            if is_legal_disclaimer(text):
                print(f"🚫 Skipping legal disclaimer: {text[:50]}...")
                continue
            
            # Detect heading levels
            heading_level = detect_heading_level_from_text(text)
            if not heading_level:
                # Try to detect from style
                style_name = paragraph.style.name.lower()
                if 'heading 1' in style_name or 'title' in style_name:
                    heading_level = 1
                elif 'heading 2' in style_name:
                    heading_level = 2
                elif 'heading 3' in style_name:
                    heading_level = 3
                elif 'heading 4' in style_name:
                    heading_level = 4
            
            if heading_level:
                extracted_content["headings"].append({
                    "level": heading_level,
                    "text": text,
                    "position": i
                })
                extracted_content["structure"].append({
                    "type": f"h{heading_level}",
                    "content": text,
                    "position": i
                })
                print(f"📋 Heading H{heading_level}: {text[:50]}...")
            else:
                # Regular body text with inline formatting preservation
                formatted_text = preserve_inline_formatting(paragraph)
                extracted_content["body_text"] += formatted_text + "\n\n"
                extracted_content["structure"].append({
                    "type": "paragraph",
                    "content": formatted_text,
                    "position": i
                })
        
        # Extract tables
        for i, table in enumerate(doc.tables):
            table_data = extract_table_data(table)
            extracted_content["tables"].append({
                "index": i,
                "data": table_data,
                "html": table_to_html(table_data)
            })
            print(f"📊 Extracted table {i+1} with {len(table_data)} rows")
        
        # Phase 1: Enhanced Image Extraction
        contextual_images = []
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for file_info in zip_ref.filelist:
                    if file_info.filename.startswith('word/media/'):
                        # Check if image is contextual (not decorative)
                        filename = file_info.filename.split('/')[-1].lower()
                        
                        # Skip logos and decorative elements
                        skip_patterns = ['logo', 'header', 'footer', 'watermark', 'background', 'banner']
                        if any(pattern in filename for pattern in skip_patterns):
                            print(f"🚫 Skipping decorative image: {filename}")
                            continue
                        
                        image_data = zip_ref.read(file_info.filename)
                        
                        # Generate meaningful filename
                        safe_prefix = "".join(c for c in training_session.get('filename', 'doc') if c.isalnum())[:10]
                        unique_filename = f"{safe_prefix}_{filename}_{str(uuid.uuid4())[:8]}"
                        file_path_static = f"static/uploads/{unique_filename}"
                        
                        # Ensure upload directory exists
                        os.makedirs("static/uploads", exist_ok=True)
                        
                        # Save image file
                        with open(file_path_static, "wb") as f:
                            f.write(image_data)
                        
                        # Generate URL
                        file_url = f"/api/static/uploads/{unique_filename}"
                        
                        contextual_images.append({
                            "filename": unique_filename,
                            "url": file_url,
                            "size": len(image_data),
                            "is_svg": filename.endswith('.svg'),
                            "caption": f"Document image {len(contextual_images) + 1}",
                            "placement": "contextual",
                            "alt_text": f"Figure {len(contextual_images) + 1}: Content illustration"
                        })
                        
                        print(f"🖼️ Extracted contextual image: {unique_filename}")
                        
        except Exception as e:
            print(f"⚠️ Image extraction error: {e}")
        
        print(f"✅ Phase 1 Complete: {len(extracted_content['structure'])} content blocks, {len(contextual_images)} images")
        
        # Fallback to simplified processing if enhanced fails
        try:
            # Convert extracted structure to simple text content for fallback
            fallback_content = extracted_content.get("body_text", "")
            
            # Add headings to content
            for heading in extracted_content.get("headings", []):
                if heading.get("text"):
                    fallback_content += f"\n\n{'#' * heading.get('level', 1)} {heading['text']}\n"
            
            # Add table content
            for table in extracted_content.get("tables", []):
                if table.get("html"):
                    fallback_content += f"\n\n{table['html']}\n"
            
            print(f"🔄 Using simplified processing for DOCX: {len(fallback_content)} chars")
            
            # Use the working template-based processing
            articles = await create_articles_with_template(fallback_content, contextual_images, template_data, training_session)
            
            return articles
            
        except Exception as fallback_error:
            print(f"❌ Fallback processing failed: {fallback_error}")
            return []
        
    except Exception as e:
        print(f"❌ Enhanced DOCX processing error: {e}")
        import traceback
        traceback.print_exc()
        return []

def preserve_inline_formatting(paragraph) -> str:
    """Extract text with inline formatting preserved as HTML"""
    html_text = ""
    
    try:
        for run in paragraph.runs:
            text = run.text
            if not text:
                continue
                
            # Apply formatting
            if run.bold:
                text = f"<strong>{text}</strong>"
            if run.italic:
                text = f"<em>{text}</em>"
            if run.underline:
                text = f"<u>{text}</u>"
                
            html_text += text
    except:
        # Fallback to plain text
        return paragraph.text
        
    return html_text if html_text else paragraph.text

def extract_table_data(table) -> list:
    """Extract table data as list of lists"""
    data = []
    try:
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                row_data.append(cell.text.strip())
            data.append(row_data)
    except:
        pass
    return data

def table_to_html(table_data: list) -> str:
    """Convert table data to HTML"""
    if not table_data:
        return ""
        
    html = "<table>"
    
    # First row as header
    if table_data:
        html += "<thead><tr>"
        for cell in table_data[0]:
            html += f"<th>{cell}</th>"
        html += "</tr></thead>"
    
    # Rest as body
    if len(table_data) > 1:
        html += "<tbody>"
        for row in table_data[1:]:
            html += "<tr>"
            for cell in row:
                html += f"<td>{cell}</td>"
            html += "</tr>"
        html += "</tbody>"
        
    html += "</table>"
    return html

async def process_pdf_with_template(file_path: str, template_data: dict, training_session: dict) -> list:
    """Process PDF file with comprehensive text and image extraction"""
    try:
        print(f"🔍 Starting comprehensive PDF processing: {file_path}")
        
        # Import PDF processing libraries
        try:
            import PyPDF2
            import fitz  # PyMuPDF for image extraction
        except ImportError:
            print("⚠️ PDF processing libraries not fully available, using fallback")
            return await process_text_with_template("", template_data, training_session)
        
        # Open PDF with PyMuPDF for comprehensive extraction
        doc = fitz.open(file_path)
        
        # Extract text and images with contextual positioning
        full_text = ""
        all_images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text from page
            page_text = page.get_text()
            if page_text.strip():
                full_text += f"\n\n=== Page {page_num + 1} ===\n{page_text}\n"
            
            # Extract images from page with filtering
            image_list = page.get_images(full=True)
            page_rect = page.rect
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data and properties
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    # Get image position on page
                    img_rects = page.get_image_rects(xref)
                    
                    # Filter out header/footer images and small decorative elements
                    should_include = True
                    
                    if img_rects:
                        for rect in img_rects:
                            # Check if image is in header (top 15% of page)
                            if rect.y1 < page_rect.height * 0.15:
                                print(f"🚫 Skipping header image on page {page_num + 1}")
                                should_include = False
                                break
                            # Check if image is in footer (bottom 15% of page)  
                            elif rect.y0 > page_rect.height * 0.85:
                                print(f"🚫 Skipping footer image on page {page_num + 1}")
                                should_include = False
                                break
                            # Check if image is very small (likely decorative)
                            elif rect.width < 100 or rect.height < 100:
                                print(f"🚫 Skipping small decorative image on page {page_num + 1}")
                                should_include = False
                                break
                    
                    # Skip if image is too small in actual pixels or filtered out
                    if not should_include or pix.width < 100 or pix.height < 100:
                        pix = None
                        continue
                    
                    # Skip if image appears to be a logo (very wide and short, or very narrow and tall)
                    aspect_ratio = pix.width / pix.height
                    if aspect_ratio > 5 or aspect_ratio < 0.2:
                        print(f"🚫 Skipping logo-like image (aspect ratio: {aspect_ratio:.2f}) on page {page_num + 1}")
                        pix = None
                        continue
                    
                    # Convert to RGB if CMYK
                    if pix.n - pix.alpha < 4:
                        img_data = pix.tobytes("png")
                    else:
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        img_data = pix1.tobytes("png")
                        pix1 = None
                    
                    # Generate unique filename
                    safe_prefix = "".join(c for c in training_session.get('filename', 'pdf') if c.isalnum())[:10]
                    unique_filename = f"{safe_prefix}_page{page_num + 1}_img{img_index + 1}_{str(uuid.uuid4())[:8]}.png"
                    file_path_static = f"static/uploads/{unique_filename}"
                    
                    # Ensure upload directory exists
                    os.makedirs("static/uploads", exist_ok=True)
                    
                    # Save image to disk
                    with open(file_path_static, "wb") as f:
                        f.write(img_data)
                    
                    # Generate URL
                    image_url = f"/api/static/uploads/{unique_filename}"
                    
                    # Store image info with contextual position
                    all_images.append({
                        "filename": unique_filename,
                        "url": image_url,
                        "page": page_num + 1,
                        "position": img_index + 1,
                        "width": pix.width,
                        "height": pix.height,
                        "size": len(img_data),
                        "is_svg": False
                    })
                    
                    print(f"✅ Extracted PDF image: Page {page_num + 1}, Image {img_index + 1} -> {image_url}")
                    
                    pix = None
                    
                except Exception as img_error:
                    print(f"⚠️ Error extracting image {img_index + 1} from page {page_num + 1}: {img_error}")
                    continue
        
        doc.close()
        
        # Basic PDF metadata
        try:
            pdf_file = open(file_path, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pdf_info = pdf_reader.metadata
            if pdf_info:
                metadata_text = "\n\n=== Document Information ===\n"
                if pdf_info.get('/Title'):
                    metadata_text += f"Title: {pdf_info['/Title']}\n"
                if pdf_info.get('/Author'):
                    metadata_text += f"Author: {pdf_info['/Author']}\n"
                if pdf_info.get('/Subject'):
                    metadata_text += f"Subject: {pdf_info['/Subject']}\n"
                full_text = metadata_text + full_text
            pdf_file.close()
        except Exception as e:
            print(f"⚠️ Error extracting PDF metadata: {e}")
        
        print(f"✅ PDF extraction complete: {len(full_text)} characters, {len(all_images)} images")
        
        # Check if we have meaningful content
        if not full_text.strip():
            print("⚠️ No text content extracted from PDF")
            return []
        
        # Process with template including images
        articles = await create_articles_with_template(full_text, all_images, template_data, training_session)
        
        print(f"✅ PDF processing generated {len(articles)} articles")
        
        return articles
        
    except Exception as e:
        print(f"❌ PDF processing error: {e}")
        import traceback
        traceback.print_exc()
        return []

async def process_ppt_with_template(file_path: str, template_data: dict, training_session: dict) -> list:
    """Process PowerPoint file with comprehensive text and image extraction"""
    try:
        print(f"🔍 Starting comprehensive PowerPoint processing: {file_path}")
        
        # Import PowerPoint processing library
        try:
            from pptx import Presentation
            from pptx.enum.shapes import MSO_SHAPE_TYPE
        except ImportError:
            print("⚠️ python-pptx not installed, using fallback processing")
            return await process_text_with_template("", template_data, training_session)
        
        # Read PowerPoint content
        prs = Presentation(file_path)
        
        # Extract text content and images from all slides
        full_text = ""
        all_images = []
        slide_count = 0
        
        for slide_num, slide in enumerate(prs.slides):
            slide_text = f"\n\n=== Slide {slide_num + 1} ===\n"
            slide_count += 1
            
            # Extract text and images from all shapes in the slide
            for shape_index, shape in enumerate(slide.shapes):
                # Extract text from shape
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text += shape.text + "\n"
                
                # Extract images from shape
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    try:
                        # Get image data
                        image = shape.image
                        image_bytes = image.blob
                        
                        # Skip if image is too small
                        if len(image_bytes) < 1000:
                            continue
                        
                        # Determine image format
                        image_ext = image.ext
                        if not image_ext:
                            image_ext = "png"  # Default to PNG
                        
                        # Generate unique filename
                        safe_prefix = "".join(c for c in training_session.get('filename', 'ppt') if c.isalnum())[:10]
                        unique_filename = f"{safe_prefix}_slide{slide_num + 1}_shape{shape_index + 1}_{str(uuid.uuid4())[:8]}.{image_ext}"
                        file_path_static = f"static/uploads/{unique_filename}"
                        
                        # Ensure upload directory exists
                        os.makedirs("static/uploads", exist_ok=True)
                        
                        # Save image to disk
                        with open(file_path_static, "wb") as f:
                            f.write(image_bytes)
                        
                        # Generate URL
                        image_url = f"/api/static/uploads/{unique_filename}"
                        
                        # Store image info with contextual position
                        all_images.append({
                            "filename": unique_filename,
                            "url": image_url,
                            "slide": slide_num + 1,
                            "shape_index": shape_index + 1,
                            "format": image_ext,
                            "size": len(image_bytes),
                            "is_svg": False
                        })
                        
                        print(f"✅ Extracted PPT image: Slide {slide_num + 1}, Shape {shape_index + 1} -> {image_url}")
                        
                    except Exception as img_error:
                        print(f"⚠️ Error extracting image from slide {slide_num + 1}, shape {shape_index + 1}: {img_error}")
                        continue
                
                # Extract images from grouped shapes
                elif hasattr(shape, "shapes"):
                    for sub_shape in shape.shapes:
                        if sub_shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                            try:
                                # Get image data
                                image = sub_shape.image
                                image_bytes = image.blob
                                
                                # Skip if image is too small
                                if len(image_bytes) < 1000:
                                    continue
                                
                                # Determine image format
                                image_ext = image.ext
                                if not image_ext:
                                    image_ext = "png"
                                
                                # Generate unique filename
                                safe_prefix = "".join(c for c in training_session.get('filename', 'ppt') if c.isalnum())[:10]
                                unique_filename = f"{safe_prefix}_slide{slide_num + 1}_subshape_{str(uuid.uuid4())[:8]}.{image_ext}"
                                file_path_static = f"static/uploads/{unique_filename}"
                                
                                # Ensure upload directory exists
                                os.makedirs("static/uploads", exist_ok=True)
                                
                                # Save image to disk
                                with open(file_path_static, "wb") as f:
                                    f.write(image_bytes)
                                
                                # Generate URL
                                image_url = f"/api/static/uploads/{unique_filename}"
                                
                                # Store image info
                                all_images.append({
                                    "filename": unique_filename,
                                    "url": image_url,
                                    "slide": slide_num + 1,
                                    "format": image_ext,
                                    "size": len(image_bytes),
                                    "is_svg": False
                                })
                                
                                print(f"✅ Extracted PPT grouped image: Slide {slide_num + 1} -> {image_url}")
                                
                            except Exception as img_error:
                                print(f"⚠️ Error extracting grouped image from slide {slide_num + 1}: {img_error}")
                                continue
            
            # Add slide text if it has content
            if slide_text.strip() != f"=== Slide {slide_num + 1} ===":
                full_text += slide_text
        
        print(f"✅ PowerPoint extraction complete: {len(full_text)} characters, {len(all_images)} images from {slide_count} slides")
        
        # Check if we have meaningful content
        if not full_text.strip():
            print("⚠️ No text content extracted from PowerPoint")
            return []
        
        # Process with template including images
        articles = await create_articles_with_template(full_text, all_images, template_data, training_session)
        
        print(f"✅ PowerPoint processing generated {len(articles)} articles")
        
        return articles
        
    except Exception as e:
        print(f"❌ PowerPoint processing error: {e}")
        import traceback
        traceback.print_exc()
        return []

async def process_text_with_template(content: str, template_data: dict, training_session: dict) -> list:
    """Process text content with training template"""
    try:
        # Apply template processing instructions
        processing_instructions = template_data.get("processing_instructions", [])
        
        # For plain text files, let's add some structure
        if not content.strip():
            content = f"Text content from {training_session.get('filename', 'unknown file')}"
        
        # Generate articles based on template
        articles = await create_articles_with_template(content, [], template_data, training_session)
        
        return articles
        
    except Exception as e:
        print(f"Text processing error: {e}")
        return []

async def process_doc_with_template(file_path: str, template_data: dict, training_session: dict) -> list:
    """Process DOC file with comprehensive text extraction"""
    try:
        print(f"🔍 Starting DOC processing: {file_path}")
        
        # Import doc processing libraries
        try:
            import subprocess
            import os
        except ImportError:
            print("⚠️ Required libraries not available, using fallback processing")
            return await process_text_with_template("", template_data, training_session)
        
        # Try to extract text using antiword (if available)
        try:
            result = subprocess.run(['antiword', file_path], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                full_text = result.stdout
                print(f"✅ DOC text extracted using antiword: {len(full_text)} characters")
            else:
                raise Exception("antiword failed")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Fallback: read as binary and extract readable text
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Basic text extraction from DOC binary
                # DOC files contain text mixed with binary data
                text_parts = []
                current_text = ""
                
                for byte in content:
                    if 32 <= byte <= 126:  # Printable ASCII
                        current_text += chr(byte)
                    else:
                        if len(current_text) > 3:  # Only keep meaningful text chunks
                            text_parts.append(current_text)
                        current_text = ""
                
                if current_text:
                    text_parts.append(current_text)
                
                full_text = " ".join(text_parts)
                print(f"✅ DOC text extracted using binary parsing: {len(full_text)} characters")
                
            except Exception as e:
                print(f"⚠️ Error extracting DOC content: {e}")
                full_text = f"Error processing DOC file: {training_session.get('filename', 'unknown')}"
        
        # Process with template (DOC files typically don't have easily accessible embedded images)
        articles = await create_articles_with_template(full_text, [], template_data, training_session)
        
        print(f"✅ DOC processing generated {len(articles)} articles")
        
        return articles
        
    except Exception as e:
        print(f"❌ DOC processing error: {e}")
        return []

async def process_excel_with_template(file_path: str, template_data: dict, training_session: dict) -> list:
    """Process Excel file with comprehensive text and image extraction"""
    try:
        print(f"🔍 Starting comprehensive Excel processing: {file_path}")
        
        # Import Excel processing libraries
        try:
            from openpyxl import load_workbook
            from openpyxl.drawing.image import Image as OpenpyxlImage
            import pandas as pd
        except ImportError:
            print("⚠️ openpyxl/pandas not installed, using fallback processing")
            return await process_text_with_template("", template_data, training_session)
        
        # Read Excel file with openpyxl for comprehensive extraction
        try:
            workbook = load_workbook(file_path)
            full_text = ""
            all_images = []
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                full_text += f"\n\n=== Sheet: {sheet_name} ===\n"
                
                # Extract text content from cells
                for row in sheet.iter_rows(values_only=True):
                    row_text = " | ".join([str(cell) for cell in row if cell is not None])
                    if row_text.strip():
                        full_text += row_text + "\n"
                
                # Extract images from sheet
                if hasattr(sheet, '_images'):
                    for img_index, img in enumerate(sheet._images):
                        try:
                            # Get image data
                            image_data = img.ref
                            
                            # Skip if no image data
                            if not hasattr(image_data, 'read'):
                                continue
                            
                            image_bytes = image_data.read()
                            
                            # Skip if image is too small
                            if len(image_bytes) < 1000:
                                continue
                            
                            # Generate unique filename
                            safe_prefix = "".join(c for c in training_session.get('filename', 'excel') if c.isalnum())[:10]
                            unique_filename = f"{safe_prefix}_{sheet_name}_img{img_index + 1}_{str(uuid.uuid4())[:8]}.png"
                            file_path_static = f"static/uploads/{unique_filename}"
                            
                            # Ensure upload directory exists
                            os.makedirs("static/uploads", exist_ok=True)
                            
                            # Save image to disk
                            with open(file_path_static, "wb") as f:
                                f.write(image_bytes)
                            
                            # Generate URL
                            image_url = f"/api/static/uploads/{unique_filename}"
                            
                            # Store image info
                            all_images.append({
                                "filename": unique_filename,
                                "url": image_url,
                                "sheet": sheet_name,
                                "size": len(image_bytes),
                                "is_svg": False
                            })
                            
                            print(f"✅ Extracted Excel image: {sheet_name} -> {image_url}")
                            
                        except Exception as img_error:
                            print(f"⚠️ Error extracting image from sheet {sheet_name}: {img_error}")
                            continue
                
            workbook.close()
            
        except Exception as e:
            print(f"⚠️ Error reading Excel file with openpyxl: {e}")
            
            # Fallback with pandas
            try:
                excel_file = pd.ExcelFile(file_path)
                full_text = ""
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    full_text += f"\n\n=== Sheet: {sheet_name} ===\n"
                    
                    if not df.empty:
                        # Add column headers
                        full_text += "Columns: " + ", ".join(df.columns.astype(str)) + "\n\n"
                        
                        # Add data rows (limit to first 100 rows)
                        for idx, row in df.head(100).iterrows():
                            row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                            if row_text.strip():
                                full_text += row_text + "\n"
                        
                        if len(df) > 100:
                            full_text += f"\n... and {len(df) - 100} more rows\n"
                    else:
                        full_text += "Empty sheet\n"
                
                all_images = []  # No image extraction in pandas fallback
                
            except Exception as pandas_error:
                print(f"⚠️ Error with pandas fallback: {pandas_error}")
                full_text = f"Error processing Excel file: {training_session.get('filename', 'unknown')}"
                all_images = []
        
        print(f"✅ Excel extraction complete: {len(full_text)} characters, {len(all_images)} images")
        
        # Process with template
        articles = await create_articles_with_template(full_text, all_images, template_data, training_session)
        
        print(f"✅ Excel processing generated {len(articles)} articles")
        
        return articles
        
    except Exception as e:
        print(f"❌ Excel processing error: {e}")
        return []

async def process_html_with_template(file_path: str, template_data: dict, training_session: dict) -> list:
    """Process HTML file with comprehensive text and image extraction"""
    try:
        print(f"🔍 Starting comprehensive HTML processing: {file_path}")
        
        # Read HTML content
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML and extract text content and images
        try:
            from bs4 import BeautifulSoup
            import requests
            import base64
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            full_text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in full_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            full_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract images
            all_images = []
            img_tags = soup.find_all('img')
            
            for i, img in enumerate(img_tags):
                src = img.get('src', '')
                alt = img.get('alt', f'Image {i+1}')
                
                if src.startswith('data:image'):
                    # Base64 embedded image
                    try:
                        # Extract base64 data
                        header, data = src.split(',', 1)
                        image_data = base64.b64decode(data)
                        
                        # Determine file extension
                        if 'svg' in header:
                            ext = 'svg'
                            is_svg = True
                        elif 'png' in header:
                            ext = 'png'
                            is_svg = False
                        elif 'jpg' in header or 'jpeg' in header:
                            ext = 'jpg'
                            is_svg = False
                        else:
                            ext = 'png'
                            is_svg = False
                        
                        if is_svg:
                            # SVG images keep base64 format
                            all_images.append({
                                "filename": f"html_image_{i+1}.{ext}",
                                "data": src,
                                "size": len(src),
                                "is_svg": True,
                                "alt": alt
                            })
                        else:
                            # Non-SVG images save to disk
                            safe_prefix = "".join(c for c in training_session.get('filename', 'html') if c.isalnum())[:10]
                            unique_filename = f"{safe_prefix}_img{i+1}_{str(uuid.uuid4())[:8]}.{ext}"
                            file_path_static = f"static/uploads/{unique_filename}"
                            
                            # Ensure upload directory exists
                            os.makedirs("static/uploads", exist_ok=True)
                            
                            # Save image to disk
                            with open(file_path_static, "wb") as f:
                                f.write(image_data)
                            
                            # Generate URL
                            image_url = f"/api/static/uploads/{unique_filename}"
                            
                            all_images.append({
                                "filename": unique_filename,
                                "url": image_url,
                                "size": len(image_data),
                                "is_svg": False,
                                "alt": alt
                            })
                            
                            print(f"✅ Extracted HTML embedded image: {unique_filename}")
                    
                    except Exception as img_error:
                        print(f"⚠️ Error processing embedded image {i+1}: {img_error}")
                        continue
                
                elif src.startswith('http') or src.startswith('/'):
                    # External or relative URL - add reference to text
                    full_text += f"\n[Referenced image: {src} - Alt: {alt}]\n"
                    
        except ImportError:
            print("⚠️ BeautifulSoup not available, using basic text extraction")
            # Fallback: basic HTML tag removal
            import re
            full_text = re.sub(r'<[^>]+>', '', html_content)
            all_images = []
        except Exception as e:
            print(f"⚠️ Error parsing HTML: {e}")
            full_text = html_content
            all_images = []
        
        print(f"✅ HTML extraction complete: {len(full_text)} characters, {len(all_images)} images")
        
        # Process with template
        articles = await create_articles_with_template(full_text, all_images, template_data, training_session)
        
        print(f"✅ HTML processing generated {len(articles)} articles")
        
        return articles
        
    except Exception as e:
        print(f"❌ HTML processing error: {e}")
        return []

async def create_articles_with_template(content: str, images: list, template_data: dict, training_session: dict) -> list:
    """Create articles using template specifications - processing full content without artificial limits"""
    try:
        content_length = len(content)
        image_count = len(images)
        
        print(f"📊 Content analysis: {content_length} chars, {image_count} images")
        print(f"🔍 DEBUG - Template data keys: {list(template_data.keys())}")
        print(f"🔍 DEBUG - Training session keys: {list(training_session.keys())}")
        print(f"🔍 DEBUG - Content preview: {content[:200]}...")
        
        # Check if content is empty
        if not content or not content.strip():
            print("❌ DEBUG - Content is empty or only whitespace")
            return []
            
        # Remove artificial limits and process full content
        # Use natural content structure to determine article splitting
        articles = []
        
        # Analyze content for natural breaking points
        natural_sections = []
        
        # Look for major headings and section breaks
        if '<h1>' in content or '<h2>' in content or '\n\n' in content:
            # Content has structure, split intelligently
            
            # First try splitting on major headings
            if '<h1>' in content:
                sections = content.split('<h1>')
                for i, section in enumerate(sections):
                    if section.strip():
                        if i > 0:  # Add back the h1 tag
                            section = '<h1>' + section
                        natural_sections.append(section)
            elif '<h2>' in content:
                sections = content.split('<h2>')
                for i, section in enumerate(sections):
                    if section.strip():
                        if i > 0:  # Add back the h2 tag
                            section = '<h2>' + section
                        natural_sections.append(section)
            else:
                # Split on double line breaks for paragraph-based content
                sections = content.split('\n\n')
                current_section = ""
                
                for section in sections:
                    # Aim for sections of reasonable length (2000-8000 chars)
                    if len(current_section + section) > 8000 and current_section:
                        natural_sections.append(current_section.strip())
                        current_section = section
                    else:
                        current_section += "\n\n" + section if current_section else section
                
                if current_section.strip():
                    natural_sections.append(current_section.strip())
        else:
            # No clear structure, treat as single section
            natural_sections = [content]
        
        # Filter out very small sections and merge with adjacent ones
        filtered_sections = []
        for i, section in enumerate(natural_sections):
            if len(section.strip()) < 500 and i < len(natural_sections) - 1:
                # Merge small section with next one
                natural_sections[i + 1] = section + "\n\n" + natural_sections[i + 1]
            elif len(section.strip()) >= 100:  # Only include sections with substantial content
                filtered_sections.append(section)
        
        natural_sections = filtered_sections if filtered_sections else [content]
        
        print(f"📝 Identified {len(natural_sections)} natural content sections")
        
        # Distribute images across sections based on content relevance and context
        images_per_section = []
        if images:
            base_images_per_section = max(1, len(images) // len(natural_sections))
            remaining_images = len(images) % len(natural_sections)
            
            for i in range(len(natural_sections)):
                section_image_count = base_images_per_section
                if i < remaining_images:
                    section_image_count += 1
                images_per_section.append(section_image_count)
        else:
            images_per_section = [0] * len(natural_sections)
        
        # Create articles from natural sections
        image_index = 0
        for i, section in enumerate(natural_sections):
            if section.strip():
                # Get images for this section
                section_images = []
                for j in range(images_per_section[i]):
                    if image_index < len(images):
                        section_images.append(images[image_index])
                        image_index += 1
                
                print(f"📄 Creating article {i+1} with {len(section_images)} images")
                
                article = await create_single_article_with_template(
                    section, 
                    section_images,
                    template_data, 
                    training_session,
                    i + 1
                )
                articles.append(article)
        
        print(f"✅ Created {len(articles)} articles from {content_length} chars and {image_count} images")
        return articles
        
    except Exception as e:
        print(f"❌ Article creation error: {e}")
        import traceback
        traceback.print_exc()
        return []

async def create_single_article_with_template(content: str, images: list, template_data: dict, training_session: dict, article_number: int) -> dict:
    """Create a single article using template specifications"""
    try:
        print(f"🔍 Creating article {article_number} with {len(images)} images")
        
        # Generate title
        title = f"Article {article_number} from {training_session['filename']}"
        
        # Generate content using LLM with template instructions
        system_message = f"""You are an expert technical writer. Process the following content according to these template specifications:

TEMPLATE INSTRUCTIONS:
{json.dumps(template_data, indent=2)}

Your task is to:
1. Follow the processing instructions exactly
2. Generate content that meets the output requirements
3. Apply the specified formatting and structure
4. Ensure quality benchmarks are met
5. Generate clean HTML output suitable for a WYSIWYG editor

IMPORTANT: Output clean HTML with proper tags like <h1>, <h2>, <p>, <ul>, <ol>, <li>, <strong>, <em>, etc.
DO NOT use Markdown syntax (##, **, *, etc.) - use HTML tags only.

Generate clean, professional content suitable for a knowledge base."""
        
        user_message = f"""Please process this content according to the template:

CONTENT:
{content}

AVAILABLE IMAGES: {len(images)} images
{[img.get('filename', f'image_{i+1}') for i, img in enumerate(images)]}

INSTRUCTIONS:
1. Generate well-structured HTML content with proper headings, paragraphs, and lists
2. Create multiple sections if the content warrants it
3. Include placeholders like {{image_1}}, {{image_2}}, etc. where images should be contextually placed
4. Ensure the content is informative, well-organized, and professionally written
5. Use proper HTML formatting throughout

Generate a properly structured article following the template specifications."""
        
        # Use LLM to generate content with better image placement instructions
        print(f"🤖 Calling LLM for article generation...")
        ai_content = await call_llm_with_fallback(system_message, user_message)
        
        print(f"🔍 DEBUG - LLM response received: {ai_content is not None}")
        print(f"🔍 DEBUG - LLM response length: {len(ai_content) if ai_content else 0}")
        
        if not ai_content:
            print("⚠️ No AI content generated, using fallback")
            ai_content = f"<h1>{title}</h1>\n<p>{content}</p>"
        
        print(f"✅ AI content generated: {len(ai_content)} characters")
        
        # Enhanced image embedding with contextual placement and content balance
        if images:
            print(f"🖼️ Processing {len(images)} images for contextual embedding")
            
            # Check content-to-image ratio to ensure balanced articles
            text_content = ai_content.replace('<', ' <').replace('>', '> ')  # Add spaces around tags
            text_only = ''.join(c for c in text_content if c.isalnum() or c.isspace())
            word_count = len(text_only.split())
            
            # Limit images based on text content to prevent image-heavy articles
            max_images_for_content = max(3, word_count // 100)  # At least 100 words per image
            images_to_use = images[:max_images_for_content] if len(images) > max_images_for_content else images
            
            if len(images_to_use) < len(images):
                print(f"🎯 Limiting to {len(images_to_use)} images (from {len(images)}) to maintain content balance")
            
            # Distribute images evenly throughout the content
            content_sections = ai_content.split('</p>')
            section_count = len(content_sections)
            
            for i, image in enumerate(images_to_use):
                print(f"🔍 Processing image {i+1}: {image.get('filename', 'unknown')}")
                
                # Generate proper image HTML with fallback handling
                image_html = ""
                
                if image.get('is_svg', False) and image.get('data'):
                    image_html = f'<figure class="embedded-image"><img src="{image["data"]}" alt="Content Image {i+1}" style="max-width: 100%; height: auto; margin: 1rem 0;"><figcaption>Figure {i+1}</figcaption></figure>'
                    print(f"✅ SVG image embedded successfully")
                elif image.get('url'):
                    # Ensure URL is properly formatted and accessible
                    image_url = image['url']
                    if not image_url.startswith('http') and not image_url.startswith('/'):
                        image_url = f"/api/static/uploads/{image_url.split('/')[-1]}"
                    
                    image_html = f'<figure class="embedded-image"><img src="{image_url}" alt="Content Image {i+1}" style="max-width: 100%; height: auto; margin: 1rem 0;"><figcaption>Figure {i+1}</figcaption></figure>'
                    print(f"✅ Image URL embedded: {image_url}")
                else:
                    print(f"⚠️ Skipping image {i+1} - no valid URL or data")
                    continue
                
                # Intelligent placement strategy
                placed = False
                
                # Strategy 1: Replace explicit placeholders first
                placeholder_patterns = [
                    f"{{image_{i+1}}}",
                    f"{{IMAGE_{i+1}}}",
                    f"[image_{i+1}]",
                    f"[IMAGE_{i+1}]",
                    f"{{img_{i+1}}}",
                    f"{{IMG_{i+1}}}"
                ]
                
                for pattern in placeholder_patterns:
                    if pattern in ai_content:
                        ai_content = ai_content.replace(pattern, image_html)
                        placed = True
                        print(f"✅ Replaced placeholder {pattern} with image HTML")
                        break
                
                # Strategy 2: Insert at natural break points if no placeholder found
                if not placed and section_count > 1:
                    # Calculate where to place this image (distribute evenly)
                    target_section = min(int((i + 1) * section_count / len(images_to_use)), section_count - 2)
                    
                    if target_section < len(content_sections) - 1:
                        # Insert after the target paragraph
                        content_sections[target_section] += f"</p>\n\n{image_html}\n"
                        placed = True
                        print(f"✅ Placed image {i+1} after section {target_section}")
                
                # Strategy 3: Append at end if all else fails (but with text separation)
                if not placed:
                    ai_content += f"\n\n{image_html}\n"
                    placed = True
                    print(f"✅ Appended image {i+1} at end")
            
            # Reconstruct content if we modified sections
            if '</p>' in ai_content and len(content_sections) > 1:
                ai_content = '</p>'.join(content_sections)
        
        # Ensure the article has sufficient text content
        final_text = ''.join(c for c in ai_content if c.isalnum() or c.isspace())
        final_word_count = len(final_text.split())
        
        if final_word_count < 100:
            print(f"⚠️ Article has only {final_word_count} words, enhancing with additional content")
            # Add more descriptive content to avoid image-heavy articles
            ai_content += f"\n\n<section><h3>Additional Context</h3><p>This section provides comprehensive coverage of the topic with detailed explanations and analysis relevant to the content above.</p></section>"
        else:
            print("ℹ️ No images to embed")
        
        # Clean and format content
        formatted_content = clean_article_content(ai_content)
        
        # Create article object
        article = {
            "id": str(uuid.uuid4()),
            "title": clean_article_title(title),
            "content": formatted_content,
            "status": "training",
            "template_id": training_session["template_id"],
            "session_id": training_session["session_id"],
            "word_count": len(formatted_content.split()),
            "image_count": len(images),
            "format": "html",
            "created_at": datetime.utcnow().isoformat(),
            "ai_processed": True,
            "ai_model": "gpt-4o (with claude fallback)",
            "training_mode": True,
            "metadata": {
                "article_number": article_number,
                "source_filename": training_session["filename"],
                "template_applied": training_session["template_id"]
            }
        }
        
        print(f"✅ Article created: {article['title']}, {article['word_count']} words, {article['image_count']} images")
        
        return article
        
    except Exception as e:
        print(f"❌ Single article creation error: {e}")
        return {
            "id": str(uuid.uuid4()),
            "title": f"Error Article {article_number}",
            "content": f"<p>Error processing content: {str(e)}</p>",
            "status": "error",
            "template_id": training_session["template_id"],
            "session_id": training_session["session_id"],
            "word_count": 0,
            "image_count": 0,
            "format": "html",
            "created_at": datetime.utcnow().isoformat(),
            "training_mode": True
        }

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
    
    # Add document batch identifier to prevent content mixing
    document_batch_id = str(uuid.uuid4())
    metadata['document_batch_id'] = document_batch_id
    metadata['processing_timestamp'] = datetime.utcnow().isoformat()
    
    print(f"🔍 DEBUG: Processing document batch {document_batch_id} for {metadata.get('original_filename', 'unknown')}")
    
    # Determine content splitting strategy with document isolation
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

def clean_article_content(content: str) -> str:
    """Post-process article content to ensure HTML format and remove metadata"""
    if not content:
        return content
    
    # Remove common metadata patterns
    metadata_patterns = [
        r'\*\*Document Statistics:\*\*.*?(?=\n\n|\n#|\Z)',  # Document statistics sections
        r'\*\*Media Assets.*?(?=\n\n|\n#|\Z)',  # Media asset summaries
        r'\*\*Total.*?(?=\n\n|\n#|\Z)',  # Total counts
        r'\*Figure \d+:.*?\d+ bytes.*?\n',  # Image metadata with byte counts
        r'\- \*\*Image \d+\*\*:.*?bytes.*?\n',  # Image lists with metadata
        r'\*\*Note:\*\*.*?extracted.*?\n',  # Extraction notes
        r'\*.*?\d+ bytes.*?\*',  # Any text with byte counts
        r'\.docx|\.pdf|\.txt|\.doc|\.xlsx',  # File extensions
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO timestamps
        r'Character count: \d+',  # Character counts
        r'Added from document assets',  # Asset source references
        r'\[Asset Library\]|\[Fallback\]',  # Asset source indicators
    ]
    
    for pattern in metadata_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    
    # Convert common Markdown to HTML if still present
    markdown_to_html_patterns = [
        # Headers (process in reverse order to avoid conflicts)
        (r'^#{6}\s+(.+)$', r'<h6>\1</h6>'),
        (r'^#{5}\s+(.+)$', r'<h5>\1</h5>'),
        (r'^#{4}\s+(.+)$', r'<h4>\1</h4>'),
        (r'^#{3}\s+(.+)$', r'<h3>\1</h3>'),
        (r'^#{2}\s+(.+)$', r'<h2>\1</h2>'),
        (r'^#{1}\s+(.+)$', r'<h1>\1</h1>'),
        
        # Bold and italic
        (r'\*\*(.+?)\*\*', r'<strong>\1</strong>'),
        (r'\*(.+?)\*', r'<em>\1</em>'),
        
        # Code blocks
        (r'```[\w]*\n(.*?)\n```', r'<pre><code>\1</code></pre>'),
        (r'`(.+?)`', r'<code>\1</code>'),
        
        # Links (markdown style) to HTML
        (r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>'),
        
        # Images (markdown style) to HTML
        (r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" style="max-width: 100%; height: auto;">'),
        
        # Blockquotes
        (r'^>\s*(.+)$', r'<blockquote>\1</blockquote>'),
        
        # Horizontal rules
        (r'^---+$', r'<hr>'),
    ]
    
    for pattern, replacement in markdown_to_html_patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Handle unordered lists (bullet points)
    def process_unordered_lists(text):
        lines = text.split('\n')
        processed_lines = []
        in_list = False
        
        for line in lines:
            # Check if line is a list item (starts with -, *, or •)
            if re.match(r'^[-*•]\s+', line.strip()):
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                # Convert to HTML list item
                item_text = re.sub(r'^[-*•]\s+', '', line.strip())
                processed_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                processed_lines.append(line)
        
        # Close list if we end while still in one
        if in_list:
            processed_lines.append('</ul>')
        
        return '\n'.join(processed_lines)
    
    # Handle ordered lists (numbered)
    def process_ordered_lists(text):
        lines = text.split('\n')
        processed_lines = []
        in_list = False
        
        for line in lines:
            # Check if line is a numbered list item
            if re.match(r'^\d+\.\s+', line.strip()):
                if not in_list:
                    processed_lines.append('<ol>')
                    in_list = True
                # Convert to HTML list item
                item_text = re.sub(r'^\d+\.\s+', '', line.strip())
                processed_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    processed_lines.append('</ol>')
                    in_list = False
                processed_lines.append(line)
        
        # Close list if we end while still in one
        if in_list:
            processed_lines.append('</ol>')
        
        return '\n'.join(processed_lines)
    
    # Apply list processing
    content = process_unordered_lists(content)
    content = process_ordered_lists(content)
    
    # Clean up extra whitespace and newlines
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Multiple newlines to double
    content = re.sub(r'^\s+|\s+$', '', content)  # Trim whitespace
    
    # Ensure paragraphs are properly wrapped in <p> tags if not already
    lines = content.split('\n\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip if already has HTML tags or is a list item
        if (line.startswith(('<', '-', '*', '1.', '2.', '3.', '4.', '5.')) or 
            '<' in line or
            line.startswith('•')):
            processed_lines.append(line)
        else:
            # Wrap plain text in paragraph tags
            processed_lines.append(f'<p>{line}</p>')
    
    return '\n\n'.join(processed_lines)

def clean_article_title(title: str) -> str:
    """Clean article title to remove filename references and metadata"""
    if not title:
        return title
    
    # Remove file extensions and common filename patterns
    title = re.sub(r'\.(docx|pdf|txt|doc|xlsx|pptx|md)$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'_+|-+', ' ', title)  # Replace underscores/dashes with spaces
    title = re.sub(r'\s+', ' ', title).strip()  # Normalize whitespace
    
    # Remove common metadata prefixes
    metadata_prefixes = [
        r'^Document:\s*',
        r'^File:\s*',
        r'^Article:\s*',
        r'^Content:\s*',
        r'^\d+\.\s*',  # Numbered prefixes
    ]
    
    for prefix in metadata_prefixes:
        title = re.sub(prefix, '', title, flags=re.IGNORECASE)
    
    # Capitalize properly
    title = title.title()
    
    return title.strip()


async def should_split_into_multiple_articles(content: str, file_extension: str) -> bool:
    """Determine if content should be split into multiple articles - Enhanced for better topic separation"""
    
    # Make splitting more aggressive for better content organization
    if len(content) < 800:  # Further lowered threshold
        return False
    
    # Always split presentations
    if file_extension in ['ppt', 'pptx']:
        return True
    
    # Always split multi-sheet spreadsheets
    if file_extension in ['xls', 'xlsx'] and 'Sheet:' in content:
        return True
    
    # Enhanced heading detection with more patterns including chapter indicators
    heading_patterns = [
        '===', '##', '# ', '####', '##### ', 
        'Chapter', 'Section', 'Part ', 'Module', 'Unit', 'Lesson',
        'Overview', 'Introduction', 'Conclusion', 'Summary',
        'Getting Started', 'Configuration', 'Setup', 'Installation',
        'Administration', 'Management', 'Process', 'Procedure',
        'Step ', 'Phase ', 'Stage ', 'Level ', 'Activity ',
        'Tutorial', 'Guide', 'How to', 'Instructions',
        'Requirements', 'Prerequisites', 'Implementation',
        'Architecture', 'Design', 'Structure', 'Framework',
        'API', 'Reference', 'Documentation', 'Specification',
        'Fundamentals', 'Basics', 'Advanced', 'Best Practices',
        'Tips', 'Techniques', 'Methods', 'Strategies',
        'Analysis', 'Planning', 'Execution', 'Monitoring'
    ]
    
    heading_count = 0
    content_lower = content.lower()
    
    for pattern in heading_patterns:
        heading_count += content_lower.count(pattern.lower())
    
    # Check for document structure indicators (more comprehensive)
    has_table_of_contents = any(toc in content_lower for toc in [
        'table of contents', 'contents:', 'index:', 'toc', 
        'outline:', 'structure:', 'agenda:'
    ])
    
    has_multiple_sections = content.count('\n\n') > 5  # Reduced threshold
    has_enumerated_sections = len([line for line in content.split('\n') 
                                 if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.'))]) > 2
    
    # Check for topic transitions (common transitional phrases)
    topic_transitions = [
        'moving on to', 'next topic', 'another important', 'in addition',
        'furthermore', 'meanwhile', 'on the other hand', 'alternatively',
        'let\'s discuss', 'now we\'ll cover', 'another aspect', 'different approach'
    ]
    
    transition_count = sum(content_lower.count(phrase) for phrase in topic_transitions)
    
    # More aggressive splitting logic - prioritize multiple focused articles
    return (
        heading_count >= 2 or  # Just 2 headings needed
        has_table_of_contents or
        (has_multiple_sections and len(content) > 1200) or  # Further reduced length threshold  
        has_enumerated_sections or
        transition_count >= 1 or  # Single topic transition indicates multiple topics
        len(content) > 4000 or  # Reduced from 6000 - split documents earlier
        (file_extension == 'docx' and len(content) > 2000) or  # DOCX files split more aggressively
        (len(content) > 8000 and heading_count >= 4)  # Rich documents with multiple headings
    )

async def create_multiple_articles_from_content(content: str, metadata: Dict[str, Any]) -> List[Dict]:
    """Create multiple structured articles from content using LLM with fallback"""
    
    system_message = """You are a professional technical content writer creating a comprehensive knowledge base. Generate ONLY clean HTML suitable for WYSIWYG display. NEVER use Markdown syntax. NEVER include source metadata like filenames, dates, or file sizes. Respond ONLY with valid JSON."""
    
    user_message = f"""Transform this content into multiple, well-structured, production-ready articles with clean HTML formatting for WYSIWYG editor.

CRITICAL: This content contains embedded media (images, diagrams, charts) that MUST be preserved and embedded at their contextually appropriate locations.

Original Content:
{content[:25000]}

TRANSFORMATION REQUIREMENTS:

1. **Content Analysis & Intelligent Splitting**:
   - Identify ALL distinct topics, chapters, sections, or processes
   - Create 6-15 focused articles for rich documents (prefer more specific articles over long ones)
   - Each article should cover ONE specific topic/process in depth
   - Split by logical boundaries: procedures, concepts, features, components, chapters
   - Prioritize user-friendly, digestible article lengths (600-1500 words each)
   - For documents with 6+ chapters, create 1 article per chapter plus overview/conclusion articles

2. **Media Contextual Embedding & Distribution**:
   - PRESERVE and DISTRIBUTE all embedded images across ALL articles
   - Each article MUST include 2-4 images relevant to its content
   - Place images at their ORIGINAL contextual location within the content flow
   - For URL-based images: <img src="/api/static/uploads/filename.ext" alt="descriptive alt text" style="max-width: 100%; height: auto;">
   - For SVG images: <img src="data:image/svg+xml;base64,..." alt="descriptive alt text" style="max-width: 100%; height: auto;">
   - Add proper figure captions: <p><em>Figure X: Descriptive caption explaining the image relevance</em></p>
   - Reference images in surrounding text: "As illustrated in Figure X below..."
   - CRITICAL: All provided images must be distributed across the complete article set
   - Never create articles without images if images are available in the source content

3. **HTML Content Formatting (NOT Markdown)**:
   - Generate clean HTML suitable for WYSIWYG editor display
   - Use proper HTML heading hierarchy: <h1>, <h2>, <h3>, <h4>
   - Format lists as <ul> and <ol> with <li> elements
   - Use <p> tags for paragraphs with proper spacing
   - Create tables with <table>, <thead>, <tbody>, <tr>, <th>, <td>
   - Use <blockquote> for callouts and important notes
   - Add <strong> for emphasis, <em> for italics
   - Use <code> for inline code, <pre><code> for code blocks
   - NO MARKDOWN SYNTAX - Only clean HTML that renders properly

4. **Content Enhancement & Professional Writing**:
   - Completely rewrite content for clarity, flow, and technical accuracy
   - Remove ALL source metadata from article content (no filenames, timestamps, byte counts)
   - Add context, explanations, and helpful details where needed
   - Improve technical language while maintaining original intent
   - Add smooth transitions and logical connections between concepts
   - Include troubleshooting tips, best practices, and common scenarios

5. **Professional Article Structure**:
   - Start with compelling <h1> title and introduction explaining purpose
   - Include "What You'll Learn" and "Prerequisites" sections where relevant
   - Organize content with clear heading hierarchy and logical flow
   - Add comprehensive conclusions with "Key Takeaways" and "Next Steps"
   - Create actionable content that users can immediately implement
   - Cross-reference related topics without hardcoded links

6. **Clean Metadata Management**:
   - Generate descriptive, SEO-friendly titles (no filename references)
   - Write detailed summaries (3-4 sentences) explaining value proposition
   - Create comprehensive tag lists including technical terms, processes, categories
   - Generate practical takeaways that highlight key learning points
   - Keep ALL source metadata OUT of article content

CRITICAL OUTPUT RULES:
- Generate ONLY HTML tags: <h1>, <h2>, <p>, <ul>, <ol>, <li>, <img>, <blockquote>, <strong>, <em>
- NEVER use Markdown: NO ##, **, [], (), ```, ---, or similar symbols
- NEVER mention filenames, dates, byte counts, or metadata
- Images: Use <img src="URL" alt="description" style="max-width:100%;">

RESPONSE FORMAT - Return valid JSON:
{{
    "articles": [
        {{
            "title": "Professional, descriptive title focused on the specific topic (no filename references)",
            "summary": "Detailed 3-4 sentence summary explaining what this article covers, why it's important, and what value it provides",
            "content": "<h1>Article Title</h1><h2>Overview</h2><p>Detailed introduction explaining the purpose and scope...</p><h2>What You'll Learn</h2><ul><li>Learning objective 1</li><li>Learning objective 2</li></ul><h2>Main Content</h2><h3>Section 1</h3><p>Detailed explanation with context...</p><img src='/api/static/uploads/image.png' alt='Descriptive alt text' style='max-width: 100%; height: auto;'><p><em>Figure 1: Caption explaining image relevance and content</em></p><p>As shown in Figure 1 above, the process demonstrates...</p><h3>Section 2</h3><blockquote><strong>💡 Pro Tip:</strong> Include helpful insights and best practices</blockquote><ol><li><strong>Step 1:</strong> Detailed explanation with specifics</li><li><strong>Step 2:</strong> More comprehensive details</li></ol><h2>Key Takeaways</h2><ul><li>Specific, actionable takeaway 1</li><li>Practical insight 2</li></ul><h2>Next Steps</h2><p>Recommended follow-up actions and related topics to explore.</p>",
            "tags": ["primary-category", "technical-term-1", "technical-term-2", "process-name", "feature-name"],
            "takeaways": ["Specific, actionable takeaway 1", "Practical insight 2", "Key concept 3", "Best practice 4"]
        }}
    ]
}}"""

    # Try to get AI response using fallback system
    session_id = str(uuid.uuid4())
    ai_response = await call_llm_with_fallback(system_message, user_message, session_id)
    
    if ai_response:
        try:
            print(f"✅ AI response received: {len(ai_response)} characters")
            
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
                # Clean title and content using post-processing functions
                raw_title = article_info.get("title", f"Article {i+1}")
                raw_content = article_info.get("content", "Content not available")
                
                cleaned_title = clean_article_title(raw_title)
                cleaned_content = clean_article_content(raw_content)
                
                # Determine which AI model was used
                ai_model = "gpt-4o (with claude fallback)" if OPENAI_API_KEY else "claude-3-5-sonnet"
                
                article_record = {
                    "id": str(uuid.uuid4()),
                    "title": cleaned_title,
                    "content": cleaned_content,
                    "summary": article_info.get("summary", "Generated from uploaded content"),
                    "tags": article_info.get("tags", [metadata.get('type', 'upload')]),
                    "takeaways": article_info.get("takeaways", []),
                    "source_type": metadata.get('type', 'text_processing'),
                    "status": "draft",
                    "metadata": {
                        **metadata,
                        "ai_processed": True,
                        "ai_model": ai_model,
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
        except Exception as e:
            print(f"❌ Error processing AI response: {e}")
    else:
        print("❌ No AI response available from either OpenAI or Claude")
    
    # Fallback to single article
    print("🔄 Falling back to single article creation...")
    return [await create_single_article_from_content(content, metadata)]

async def create_single_article_from_content(content: str, metadata: Dict[str, Any]) -> Dict:
    """Create a single comprehensive article from content using LLM with fallback"""
    
    system_message = """You are a professional technical content writer. Generate ONLY clean HTML suitable for WYSIWYG display. NEVER use Markdown syntax. NEVER include source metadata like filenames, dates, or file sizes. Respond ONLY with valid JSON."""
    
    user_message = f"""Transform this content into a comprehensive, production-ready knowledge base article with clean HTML formatting.

CRITICAL: This content may contain embedded media (images, diagrams, charts) that MUST be preserved and embedded at their contextually appropriate locations.

Original Content:
{content[:20000]}

TRANSFORMATION REQUIREMENTS:

1. **Media Contextual Embedding & Preservation**:
   - PRESERVE and EMBED all available images, charts, diagrams, and media
   - Distribute images throughout the article at contextually appropriate locations
   - For URL-based images: <img src="/api/static/uploads/filename.ext" alt="descriptive alt text" style="max-width: 100%; height: auto;">
   - For SVG images: <img src="data:image/svg+xml;base64,..." alt="descriptive alt text" style="max-width: 100%; height: auto;">
   - Add proper figure captions: <p><em>Figure X: Descriptive caption explaining the image relevance</em></p>
   - Reference images in surrounding text: "As illustrated in Figure X below..."
   - CRITICAL: Use ALL provided images in the article - do not skip any images
   - Never place images at the end - embed them where they contextually belong

2. **HTML Content Formatting (NOT Markdown)**:
   - Generate clean HTML suitable for WYSIWYG editor display
   - Use proper HTML heading hierarchy: <h1>, <h2>, <h3>, <h4>
   - Format lists as <ul> and <ol> with <li> elements
   - Use <p> tags for paragraphs with proper spacing
   - Create tables with <table>, <thead>, <tbody>, <tr>, <th>, <td>
   - Use <blockquote> for callouts and important notes
   - Add <strong> for emphasis, <em> for italics
   - Use <code> for inline code, <pre><code> for code blocks
   - NO MARKDOWN SYNTAX - Only clean HTML that renders properly

3. **Content Enhancement & Professional Writing**:
   - Completely rewrite content for clarity, flow, and technical accuracy
   - Remove ALL source metadata from article content (no filenames, timestamps, byte counts)
   - Add context, explanations, and helpful details where needed
   - Improve technical language while maintaining original intent
   - Add smooth transitions and logical connections between concepts
   - Include troubleshooting tips, best practices, and common scenarios

4. **Professional Article Structure**:
   - Start with compelling <h1> title and introduction explaining purpose
   - Include "What You'll Learn" and "Prerequisites" sections where relevant
   - Organize content with clear heading hierarchy and logical flow
   - Add comprehensive conclusions with "Key Takeaways" and "Next Steps"
   - Create actionable content that users can immediately implement

5. **Clean Metadata Management**:
   - Generate descriptive, SEO-friendly title (no filename references)
   - Write detailed summary (3-4 sentences) explaining value proposition
   - Create comprehensive tag list including technical terms and processes
   - Generate practical takeaways highlighting key learning points
   - Keep ALL source metadata OUT of article content

CRITICAL OUTPUT RULES:
- Generate ONLY HTML tags: <h1>, <h2>, <p>, <ul>, <ol>, <li>, <img>, <blockquote>, <strong>, <em>
- NEVER use Markdown: NO ##, **, [], (), ```, ---, or similar symbols
- NEVER mention filenames, dates, byte counts, or metadata
- Images: Use <img src="URL" alt="description" style="max-width:100%;">

RESPONSE FORMAT - Return valid JSON:
{{
    "title": "Professional, descriptive title focused on the content topic (no filename references)",
    "summary": "Detailed 3-4 sentence summary explaining what this article covers, why it's important, and what specific value it provides",
    "content": "<h1>Article Title</h1><h2>Overview</h2><p>Detailed introduction explaining the purpose, scope, and importance...</p><h2>What You'll Learn</h2><ul><li>Learning objective 1</li><li>Learning objective 2</li></ul><h2>Main Content</h2><h3>Section 1</h3><p>Detailed explanation with context and examples...</p><img src='/api/static/uploads/image.png' alt='Descriptive alt text' style='max-width: 100%; height: auto;'><p><em>Figure 1: Caption explaining image relevance</em></p><p>As shown in Figure 1 above...</p><h3>Section 2</h3><blockquote><strong>💡 Pro Tip:</strong> Include helpful insights and best practices</blockquote><ol><li><strong>Step 1:</strong> Detailed explanation with specifics</li><li><strong>Step 2:</strong> More comprehensive details</li></ol><h2>Key Takeaways</h2><ul><li>Specific, actionable takeaway 1</li><li>Practical insight 2</li></ul><h2>Next Steps</h2><p>Recommended follow-up actions and related topics to explore.</p>",
    "tags": ["primary-category", "technical-term-1", "technical-term-2", "process-name", "feature-name"],
    "takeaways": ["Specific, actionable takeaway 1", "Practical insight 2", "Key concept 3", "Best practice 4"]
}}"""

    # Try to get AI response using fallback system
    session_id = str(uuid.uuid4())
    ai_response = await call_llm_with_fallback(system_message, user_message, session_id)
    
    if ai_response:
        try:
            print(f"✅ AI response received: {len(ai_response)} characters")
            
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
            
            # Create article record with cleaned content
            raw_title = article_data.get("title", metadata.get('original_filename', 'Processed Content'))
            raw_content = article_data.get("content", content)
            
            cleaned_title = clean_article_title(raw_title)
            cleaned_content = clean_article_content(raw_content)
            
            # Determine which AI model was used based on session info
            ai_model = "gpt-4o (with claude fallback)" if OPENAI_API_KEY else "claude-3-5-sonnet"
            
            article_record = {
                "id": str(uuid.uuid4()),
                "title": cleaned_title,
                "content": cleaned_content,
                "summary": article_data.get("summary", "Content processed by Knowledge Engine"),
                "tags": article_data.get("tags", [metadata.get('type', 'upload')]),
                "takeaways": article_data.get("takeaways", []),
                "source_type": metadata.get('type', 'text_processing'),
                "status": "draft",
                "metadata": {
                    **metadata,
                    "ai_processed": True,
                    "ai_model": ai_model,
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
        except Exception as e:
            print(f"❌ Error processing AI response: {e}")
    else:
        print("❌ No AI response available from either OpenAI or Claude")
    
    # Fallback to basic article
    print("🔄 Falling back to basic article creation...")
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
                
                # Extract embedded images and media - IMPROVED TO SAVE AS FILES
                async def extract_media_from_docx(doc, filename_prefix):
                    """Extract embedded images from docx document and save as files"""
                    media_files = []
                    saved_assets = []
                    
                    try:
                        # Access the document's media files
                        image_index = 0
                        for rel in doc.part.rels.values():
                            if "image" in rel.target_ref:
                                image_index += 1
                                # Get image data
                                image_part = rel.target_part
                                image_data = image_part.blob
                                
                                # Determine image format
                                content_type = image_part.content_type
                                if 'png' in content_type:
                                    img_format = 'png'
                                elif 'jpeg' in content_type or 'jpg' in content_type:
                                    img_format = 'jpeg'
                                elif 'gif' in content_type:
                                    img_format = 'gif'
                                elif 'webp' in content_type:
                                    img_format = 'webp'
                                elif 'svg' in content_type:
                                    img_format = 'svg'
                                    # Only SVG should remain base64
                                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                                    media_files.append({
                                        'type': 'image',
                                        'format': img_format,
                                        'data': f"data:{content_type};base64,{image_base64}",
                                        'content_type': content_type,
                                        'size': len(image_data),
                                        'is_svg': True
                                    })
                                    print(f"✅ Extracted SVG image as base64: {len(image_data)} bytes")
                                    continue
                                else:
                                    img_format = 'png'  # default
                                
                                # For non-SVG images, save as files to Asset Library
                                try:
                                    # Generate unique filename
                                    safe_prefix = "".join(c for c in filename_prefix if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
                                    unique_filename = f"{safe_prefix}_img_{image_index}_{str(uuid.uuid4())[:8]}.{img_format}"
                                    file_path = f"static/uploads/{unique_filename}"
                                    
                                    # Ensure upload directory exists
                                    os.makedirs("static/uploads", exist_ok=True)
                                    
                                    # Save file to disk
                                    async with aiofiles.open(file_path, "wb") as buffer:
                                        await buffer.write(image_data)
                                    
                                    # Generate URL for the file (using /api/static prefix)
                                    file_url = f"/api/static/uploads/{unique_filename}"
                                    
                                    # Save asset metadata to database
                                    assets_collection = db["assets"]
                                    asset_data = {
                                        "id": str(uuid.uuid4()),
                                        "original_filename": f"extracted_image_{image_index}.{img_format}",
                                        "filename": unique_filename,
                                        "title": f"Image {image_index} from {filename_prefix}",
                                        "name": f"Image {image_index} from {filename_prefix}",
                                        "type": "image",
                                        "url": file_url,
                                        "file_path": file_path,
                                        "content_type": content_type,
                                        "size": len(image_data),
                                        "source": "docx_extraction",
                                        "source_document": filename_prefix,
                                        "created_at": datetime.utcnow().isoformat(),
                                        "updated_at": datetime.utcnow().isoformat()
                                    }
                                    
                                    await assets_collection.insert_one(asset_data)
                                    saved_assets.append(asset_data)
                                    
                                    # Store file URL instead of base64 data
                                    media_files.append({
                                        'type': 'image',
                                        'format': img_format,
                                        'url': file_url,
                                        'content_type': content_type,
                                        'size': len(image_data),
                                        'is_svg': False,
                                        'asset_id': asset_data["id"]
                                    })
                                    
                                    print(f"✅ Extracted and saved image: {img_format}, {len(image_data)} bytes -> {file_url}")
                                
                                except Exception as save_error:
                                    print(f"⚠️ Error saving image as file: {save_error}")
                                    # Fallback to base64 if file save fails
                                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                                    media_files.append({
                                        'type': 'image',
                                        'format': img_format,
                                        'data': f"data:{content_type};base64,{image_base64}",
                                        'content_type': content_type,
                                        'size': len(image_data),
                                        'is_svg': False,
                                        'fallback': True
                                    })
                                
                    except Exception as e:
                        print(f"⚠️ Media extraction error: {e}")
                    
                    print(f"📁 Saved {len(saved_assets)} images to Asset Library")
                    return media_files
                
                # Extract media from document - simplified approach for better AI processing
                embedded_media = await extract_media_from_docx(doc, file.filename.replace('.docx', '').replace('.doc', ''))
                print(f"🔍 DEBUG: Extracted {len(embedded_media)} media items from DOCX")
                
                # Improve image distribution across articles by including image references in prompts
                image_references = ""
                image_distribution_info = ""
                
                if embedded_media:
                    print(f"🔍 DEBUG: Processing {len(embedded_media)} images for distribution")
                    
                    for i, media in enumerate(embedded_media, 1):
                        if media.get('is_svg', False):
                            # SVG images remain as base64
                            image_references += f'\n<img src="{media["data"]}" alt="Figure {i}: Document Image" style="max-width: 100%; height: auto;">\n<p><em>Figure {i}: Document Image</em></p>\n'
                            print(f"🔍 DEBUG: Added SVG image {i} HTML reference for AI positioning")
                        elif media.get('url'):
                            # Non-SVG images use file URL references
                            image_references += f'\n<img src="{media["url"]}" alt="Figure {i}: Document Image" style="max-width: 100%; height: auto;">\n<p><em>Figure {i}: Document Image</em></p>\n'
                            print(f"🔍 DEBUG: Added image {i} URL HTML reference for AI positioning: {media['url']}")
                        else:
                            # Fallback for base64 data
                            image_references += f'\n<img src="{media["data"]}" alt="Figure {i}: Document Image" style="max-width: 100%; height: auto;">\n<p><em>Figure {i}: Document Image</em></p>\n'
                            print(f"🔍 DEBUG: Added image {i} base64 HTML reference for AI positioning")
                    
                    # Create distribution instructions for AI
                    image_distribution_info = f"""
CRITICAL IMAGE DISTRIBUTION REQUIREMENTS:
- This document contains {len(embedded_media)} images that MUST be distributed across ALL articles
- Each article should include 2-4 images contextually relevant to its topic
- Images should be embedded using the exact HTML format provided above
- Do not create articles without images unless absolutely necessary
- Ensure all {len(embedded_media)} images are used across the complete set of articles
"""
                
                # Process document content cleanly without metadata
                extracted_content = f"# {file.filename}\n\n{image_distribution_info}\n\n{image_references}\n\n"
                
                # Process document elements in order - simplified for cleaner content
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
                    
                    elif isinstance(block, Table):
                        extracted_content += f"\n## Table\n\n"
                        
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
                        
                print(f"✅ Simplified extraction: {len(extracted_content)} characters from Word document, {len(embedded_media)} images provided for AI contextual positioning")
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
    """Chat with AI using processed content as context and LLM fallback"""
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

        # Use fallback system to get AI response
        ai_response = await call_llm_with_fallback(system_message, message, session_id)
        
        if not ai_response:
            raise HTTPException(status_code=500, detail="AI service temporarily unavailable")
        
        # Store conversation in database
        conversation_record = {
            "session_id": session_id,
            "user_message": message,
            "ai_response": ai_response,
            "model_provider": "openai_claude_fallback",
            "model_name": "gpt-4o/claude-3-5-sonnet",
            "context_used": len(context_chunks),
            "timestamp": datetime.utcnow()
        }
        
        await db.conversations.insert_one(conversation_record)
        
        return {
            "response": ai_response,
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