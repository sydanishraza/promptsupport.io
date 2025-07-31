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
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
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

# HTML preprocessing pipeline imports
import mammoth
import pypandoc
# from pdfminer.six import extract_text as pdf_extract_text
from lxml import etree
from lxml.html import fromstring as html_fromstring, tostring as html_tostring
import shutil
import subprocess

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
                if current_word_count > 3000:  # Increased from 800 to 3000 words per article
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
                "ai_model": "gpt-4o-mini (with claude + local llm fallback)",
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

# === HTML PREPROCESSING PIPELINE FOR ACCURATE IMAGE REINSERTION ===

class DocumentPreprocessor:
    """
    Revolutionary 3-phase HTML preprocessing pipeline for accurate image reinsertion
    Phase 1: Convert documents to structured HTML with block IDs and image tokenization
    Phase 2: AI processing that preserves tokens and structure  
    Phase 3: Token replacement with rich image HTML
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.asset_dir = f"static/uploads/session_{session_id}"
        self.block_counter = 0
        self.image_counter = 0
        self.extracted_images = {}
        
        # Ensure asset directory exists
        os.makedirs(self.asset_dir, exist_ok=True)
    
    async def preprocess_document(self, file_path: str, file_type: str) -> tuple[list, dict]:
        """
        Phase 1: Convert document to multiple structured HTML chunks with block IDs and image tokenization
        Returns: (html_chunks_list, image_assets)
        """
        print(f"🔄 Phase 1: Starting HTML preprocessing with structural chunking for {file_type} document")
        
        try:
            # Convert document to HTML based on type
            if file_type.lower() in ['docx', 'doc']:
                html_content, images = await self._convert_docx_to_html(file_path)
            elif file_type.lower() == 'pdf':
                html_content, images = await self._convert_pdf_to_html(file_path)
            elif file_type.lower() in ['ppt', 'pptx']:
                html_content, images = await self._convert_ppt_to_html(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            print(f"📄 Converted to HTML: {len(html_content)} characters, {len(images)} images extracted")
            
            # NEW APPROACH: Create structural HTML chunks at conversion level
            html_chunks = self._create_structural_html_chunks(html_content, images)
            print(f"📚 Created {len(html_chunks)} structural HTML chunks")
            
            # Assign block IDs and tokenize images for each chunk
            processed_chunks = []
            for i, chunk_data in enumerate(html_chunks):
                print(f"🏗️ Processing chunk {i+1}/{len(html_chunks)}: {chunk_data['title']}")
                
                # Assign structural block IDs
                structured_html = self._assign_block_ids_to_chunk(chunk_data['content'], chunk_data['section_id'])
                
                # Tokenize images for this chunk
                tokenized_html = self._tokenize_images_in_chunk(structured_html, chunk_data['images'])
                
                processed_chunk = {
                    'section_id': chunk_data['section_id'],
                    'title': chunk_data['title'],
                    'content': tokenized_html,
                    'images': chunk_data['images'],
                    'token_estimate': len(tokenized_html) // 4
                }
                
                processed_chunks.append(processed_chunk)
                print(f"✅ Chunk {i+1} processed: ~{processed_chunk['token_estimate']:,} tokens")
            
            return processed_chunks, self.extracted_images
            
        except Exception as e:
            print(f"❌ Phase 1 preprocessing failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def _convert_docx_to_html(self, file_path: str) -> tuple[str, list]:
        """Convert DOCX to HTML using mammoth with image extraction"""
        try:
            print(f"📄 Starting DOCX conversion: {file_path}")
            
            with open(file_path, "rb") as docx_file:
                # Use mammoth to convert with image handling
                def image_handler(image):
                    self.image_counter += 1
                    
                    # Determine file extension from content type
                    content_type = getattr(image, 'content_type', 'image/png')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = 'jpg'
                    elif 'png' in content_type:
                        ext = 'png'
                    elif 'gif' in content_type:
                        ext = 'gif'
                    else:
                        ext = 'png'  # Default to PNG
                    
                    image_filename = f"img_{self.image_counter}.{ext}"
                    image_path = os.path.join(self.asset_dir, image_filename)
                    
                    # Get image data - mammoth uses different attribute names
                    try:
                        # Try different possible attribute names for image data
                        if hasattr(image, 'open'):
                            # mammoth Image object has 'open' method
                            with image.open() as image_data:
                                image_bytes = image_data.read()
                        elif hasattr(image, 'bytes'):
                            image_bytes = image.bytes
                        elif hasattr(image, 'data'):
                            image_bytes = image.data
                        else:
                            print(f"⚠️ Unknown image data format for image {self.image_counter}")
                            # Create a placeholder to continue processing
                            image_bytes = b''
                    except Exception as img_error:
                        print(f"❌ Failed to extract image {self.image_counter}: {img_error}")
                        # Create a placeholder to continue processing
                        image_bytes = b''
                    
                    # Save image to disk if we have data
                    if image_bytes:
                        try:
                            with open(image_path, "wb") as img_file:
                                img_file.write(image_bytes)
                            print(f"💾 Saved image: {image_filename} ({len(image_bytes)} bytes)")
                        except Exception as save_error:
                            print(f"❌ Failed to save image {image_filename}: {save_error}")
                    
                    # Store image metadata
                    image_id = f"doc_{self.session_id}_img_{self.image_counter}"
                    self.extracted_images[image_id] = {
                        'filename': image_filename,
                        'path': image_path,
                        'url': f"/api/static/uploads/session_{self.session_id}/{image_filename}",
                        'alt_text': f"Image {self.image_counter}",
                        'content_type': content_type
                    }
                    
                    return {
                        "src": f"IMAGE_PLACEHOLDER_{image_id}"  # Placeholder for tokenization
                    }
                
                try:
                    # Convert with image handling
                    result = mammoth.convert_to_html(docx_file, convert_image=image_handler)
                    html_content = result.value
                    messages = result.messages
                    
                    # Log any conversion messages
                    if messages:
                        for message in messages:
                            if message.type == "warning":
                                print(f"⚠️ Mammoth warning: {message.message}")
                            elif message.type == "error":
                                print(f"❌ Mammoth error: {message.message}")
                    
                    print(f"✅ DOCX converted to HTML: {len(html_content)} characters")
                    
                except Exception as conversion_error:
                    print(f"❌ Mammoth conversion failed: {conversion_error}")
                    # Fallback: try to extract text without images
                    try:
                        result = mammoth.convert_to_html(docx_file)
                        html_content = result.value
                        print(f"⚠️ Fallback conversion successful (no images): {len(html_content)} characters")
                    except Exception as fallback_error:
                        print(f"❌ Fallback conversion also failed: {fallback_error}")
                        return f"<p>Failed to convert DOCX: {str(fallback_error)}</p>", []
                
                # Extract image placeholders and create image list
                images = []
                for image_id, image_data in self.extracted_images.items():
                    if f"IMAGE_PLACEHOLDER_{image_id}" in html_content:
                        images.append({
                            'id': image_id,
                            'filename': image_data['filename'],
                            'url': image_data['url'],
                            'alt_text': image_data['alt_text']
                        })
                
                print(f"🖼️ Extracted {len(images)} images from DOCX")
                return html_content, images
                
        except Exception as e:
            print(f"❌ DOCX conversion failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to basic text extraction
            return f"<p>Failed to convert DOCX: {str(e)}</p>", []
    
    async def _convert_pdf_to_html(self, file_path: str) -> tuple[str, list]:
        """Convert PDF to HTML using basic text extraction"""
        try:
            # For now, use a simple fallback approach
            # TODO: Implement proper PDF processing when pdfminer.six is available
            html_content = "<p>PDF processing temporarily unavailable - HTML preprocessing pipeline active</p>"
            images = []
            
            return html_content, images
            
        except Exception as e:
            print(f"❌ PDF conversion failed: {e}")
            return f"<p>Failed to convert PDF: {str(e)}</p>", []
    
    async def _convert_ppt_to_html(self, file_path: str) -> tuple[str, list]:
        """Convert PowerPoint to HTML with slide structure"""
        try:
            # Try to use python-pptx for basic extraction
            from pptx import Presentation
            
            prs = Presentation(file_path)
            html_parts = []
            images = []
            
            for i, slide in enumerate(prs.slides):
                html_parts.append(f"<h2>Slide {i + 1}</h2>")
                
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        html_parts.append(f"<p>{shape.text}</p>")
                    elif shape.shape_type == 13:  # Picture type
                        # Handle images in slides
                        self.image_counter += 1
                        image_id = f"ppt_{self.session_id}_img_{self.image_counter}"
                        images.append({
                            'id': image_id,
                            'filename': f"slide_{i+1}_img_{self.image_counter}.png",
                            'alt_text': f"Slide {i+1} Image {self.image_counter}"
                        })
                        html_parts.append(f"<p>IMAGE_PLACEHOLDER_{image_id}</p>")
            
            html_content = '\n'.join(html_parts)
            return html_content, images
            
        except Exception as e:
            print(f"❌ PowerPoint conversion failed: {e}")
            return f"<p>Failed to convert PowerPoint: {str(e)}</p>", []
    
    def _create_structural_html_chunks(self, html_content: str, images: list) -> list:
        """
        OPTIMIZED: Create fewer, larger structural HTML chunks for faster processing
        Only break at H1 boundaries with larger chunk sizes to reduce processing time
        FALLBACK: If no H1 elements exist, create a single chunk with all content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            chunks = []
            current_chunk_content = []
            current_section_id = "intro"
            current_title = "Introduction"
            section_counter = 0
            
            # Distribute images across chunks based on document position
            chunk_images = {}  # Will map section_id to list of images
            
            # Check if document has any H1 elements
            h1_elements = soup.find_all('h1')
            has_h1_structure = len(h1_elements) > 0
            
            print(f"📊 Document analysis: {len(h1_elements)} H1 elements found")
            
            if not has_h1_structure:
                # FALLBACK: No H1 structure - create single chunk with all content
                print("📄 No H1 structure detected - creating single comprehensive chunk")
                all_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'div', 'table'])
                if all_elements:
                    chunk_html = self._create_chunk_html(all_elements)
                    if self._is_chunk_valid(chunk_html):
                        chunks.append({
                            'section_id': 'full_document',
                            'title': 'Complete Document',
                            'content': chunk_html,
                            'images': images  # Assign all images to this single chunk
                        })
                        print(f"✅ Created single comprehensive chunk: {len(chunk_html)} characters")
            else:
                # OPTIMIZATION: Only split at H1 boundaries (not H2) and allow larger chunks
                for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'div', 'table']):
                    
                    # ONLY break at H1 boundaries for major sections (removed H2 breaking)
                    if element.name == 'h1':
                        # Save current chunk if it has content
                        if current_chunk_content:
                            chunk_html = self._create_chunk_html(current_chunk_content)
                            if self._is_chunk_valid(chunk_html):
                                chunks.append({
                                    'section_id': current_section_id,
                                    'title': current_title,
                                    'content': chunk_html,
                                    'images': chunk_images.get(current_section_id, [])
                                })
                        
                        # Start new chunk
                        section_counter += 1
                        current_section_id = f"section_{section_counter}"
                        current_title = element.get_text().strip()[:50] + ("..." if len(element.get_text()) > 50 else "")
                        current_chunk_content = [element]
                        chunk_images[current_section_id] = []
                    
                    else:
                        # Add to current chunk - allow much larger chunks
                        current_chunk_content.append(element)
                        
                        # OPTIMIZATION: Increased chunk size limit from 28K to 80K chars (~20K tokens)
                        # This reduces the number of chunks and API calls significantly
                        current_chunk_html = self._create_chunk_html(current_chunk_content)
                        if len(current_chunk_html) > 80000:  # ~20K tokens (nearly double previous limit)
                            # Save current chunk
                            chunks.append({
                                'section_id': current_section_id,
                                'title': current_title,
                                'content': current_chunk_html,
                                'images': chunk_images.get(current_section_id, [])
                            })
                            
                            # Start new sub-chunk
                            section_counter += 1
                            current_section_id = f"section_{section_counter}"
                            current_title = f"{current_title} (continued)"
                            current_chunk_content = []
                            chunk_images[current_section_id] = []
                
                # Add final chunk if using H1 structure
                if current_chunk_content:
                    chunk_html = self._create_chunk_html(current_chunk_content)
                    if self._is_chunk_valid(chunk_html):
                        chunks.append({
                            'section_id': current_section_id,
                            'title': current_title,
                            'content': chunk_html,
                            'images': chunk_images.get(current_section_id, [])
                        })
                
                # Distribute images across chunks based on original document position
                self._distribute_images_to_chunks(chunks, images)
            
            print(f"📋 OPTIMIZED: Created {len(chunks)} larger structural chunks ({'H1-based' if has_h1_structure else 'single-chunk fallback'})")
            return chunks
            
        except Exception as e:
            print(f"❌ Structural chunking failed: {e}")
            # Fallback: create single chunk
            return [{
                'section_id': 'full_document',
                'title': 'Full Document',
                'content': html_content,
                'images': images
            }]
    
    def _create_chunk_html(self, elements: list) -> str:
        """Create valid HTML from a list of elements"""
        if not elements:
            return ""
        
        html_parts = []
        for element in elements:
            html_parts.append(str(element))
        
        return '\n'.join(html_parts)
    
    def _is_chunk_valid(self, chunk_html: str) -> bool:
        """Check if chunk has substantial content - reduced threshold for simple documents"""
        text_content = BeautifulSoup(chunk_html, 'html.parser').get_text().strip()
        return len(text_content) > 20  # Reduced from 100 to 20 characters for simple documents
    
    def _distribute_images_to_chunks(self, chunks: list, images: list):
        """Distribute images to appropriate chunks based on content proximity"""
        try:
            for image in images:
                image_id = image['id']
                best_chunk_idx = 0
                
                # Simple distribution: spread images evenly across chunks
                # In a more sophisticated implementation, we could analyze image placement context
                chunk_idx = len([img for img in images[:images.index(image)]]) % len(chunks)
                
                if chunk_idx < len(chunks):
                    chunks[chunk_idx]['images'].append(image)
                    print(f"📷 Assigned image {image_id} to chunk {chunk_idx + 1}")
                
        except Exception as e:
            print(f"⚠️ Image distribution failed: {e}, assigning all images to first chunk")
            if chunks:
                chunks[0]['images'] = images
    
    def _assign_block_ids_to_chunk(self, chunk_html: str, section_id: str) -> str:
        """
        Assign unique data-block-id to every content block within a chunk
        Uses section-specific naming: section_1_para_1, section_1_heading_2, etc.
        """
        try:
            soup = BeautifulSoup(chunk_html, 'html.parser')
            element_counter = 0
            
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'div', 'table']):
                element_counter += 1
                block_id = f"{section_id}_{element.name}_{element_counter}"
                element['data-block-id'] = block_id
                self.block_counter += 1
                
                print(f"📋 Assigned block ID: {block_id} to <{element.name}>")
            
            return str(soup)
            
        except Exception as e:
            print(f"❌ Block ID assignment failed for chunk: {e}")
            return chunk_html
    
    def _tokenize_images_in_chunk(self, chunk_html: str, chunk_images: list) -> str:
        """
        Replace image placeholders with positioned tokens within a specific chunk
        """
        try:
            tokenized_html = chunk_html
            
            for image in chunk_images:
                image_id = image['id']
                placeholder = f"IMAGE_PLACEHOLDER_{image_id}"
                
                if placeholder in tokenized_html:
                    # Create rich image token with metadata
                    image_token = f"""<!-- IMAGE_BLOCK:{image_id} -->
<div data-image-id="{image_id}" data-original-filename="{image.get('filename', '')}" data-alt="{image.get('alt_text', '')}">
    [IMAGE: {image.get('alt_text', 'Image')}]
</div>
<!-- END_IMAGE_BLOCK:{image_id} -->"""
                    
                    tokenized_html = tokenized_html.replace(placeholder, image_token)
                    print(f"🏷️ Tokenized image: {image_id} in chunk")
            
            return tokenized_html
            
        except Exception as e:
            print(f"❌ Image tokenization failed for chunk: {e}")
            return chunk_html
    
    def _tokenize_images(self, structured_html: str, images: list) -> str:
        """
        Phase 1c: Replace image placeholders with positioned tokens
        Creates <!-- IMAGE_BLOCK:xxx --> tokens that AI can preserve
        """
        try:
            tokenized_html = structured_html
            
            for image in images:
                image_id = image['id']
                placeholder = f"IMAGE_PLACEHOLDER_{image_id}"
                
                # Create rich image token with metadata
                image_token = f"""<!-- IMAGE_BLOCK:{image_id} -->
<div data-image-id="{image_id}" data-original-filename="{image.get('filename', '')}" data-alt="{image.get('alt_text', '')}">
    [IMAGE: {image.get('alt_text', 'Image')}]
</div>
<!-- END_IMAGE_BLOCK:{image_id} -->"""
                
                tokenized_html = tokenized_html.replace(placeholder, image_token)
                print(f"🏷️ Tokenized image: {image_id}")
            
            return tokenized_html
            
        except Exception as e:
            print(f"❌ Image tokenization failed: {e}")
            return structured_html
    
    async def process_with_ai_preserving_tokens(self, html_chunks: list, template_data: dict) -> list:
        """
        Phase 2: AI processing that preserves tokens and block structure
        Processes multiple HTML chunks independently
        """
        print(f"🤖 Phase 2: Starting AI processing with {len(html_chunks)} structural chunks")
        
        processed_chunks = []
        
        try:
            for i, chunk_data in enumerate(html_chunks):
                print(f"🔄 Processing chunk {i+1}/{len(html_chunks)}: {chunk_data['title']}")
                print(f"📊 Chunk tokens: ~{chunk_data['token_estimate']:,}")
                
                # Process this chunk with AI
                processed_content = await self._process_chunk_with_ai(chunk_data, template_data, i)
                
                # Create processed chunk data
                processed_chunk = {
                    'section_id': chunk_data['section_id'],
                    'title': chunk_data['title'],
                    'content': processed_content,
                    'images': chunk_data['images'],
                    'original_token_estimate': chunk_data['token_estimate']
                }
                
                processed_chunks.append(processed_chunk)
                print(f"✅ Chunk {i+1} processed successfully")
                
                # Small delay between chunks to avoid rate limiting
                await asyncio.sleep(1)
            
            print(f"✅ All {len(processed_chunks)} chunks processed successfully")
            return processed_chunks
                
        except Exception as e:
            print(f"❌ AI processing failed: {e}")
            import traceback
            traceback.print_exc()
            return html_chunks  # Return original chunks as fallback
    
    async def _process_chunk_with_ai(self, chunk_data: dict, template_data: dict, chunk_index: int) -> str:
        """Process a single HTML chunk with AI while preserving structure"""
        try:
            system_message = """You are an expert content writer improving a section of a technical document.

CRITICAL REQUIREMENTS:
1. PRESERVE ALL <!-- IMAGE_BLOCK:xxx --> tokens EXACTLY as they appear
2. PRESERVE ALL <!-- END_IMAGE_BLOCK:xxx --> tokens EXACTLY as they appear  
3. MAINTAIN all data-block-id attributes on HTML elements
4. PRESERVE the [IMAGE: ...] placeholders within image blocks
5. Keep the HTML structure intact (headings, paragraphs, lists)

Your task is to:
- Improve the text content for clarity, readability, and engagement
- Expand content where appropriate while maintaining focus on this section
- Ensure professional tone and comprehensive coverage
- Preserve all structural elements and image tokens

Do NOT:
- Remove or modify any image tokens or data-block-id attributes
- Change the basic HTML structure or heading hierarchy
- Generate new fake images or remove existing image references
- Merge or split major sections"""

            user_message = f"""Please improve this document section while preserving all structure and tokens:

SECTION: {chunk_data['title']}

{chunk_data['content']}

Focus on:
- Making content more comprehensive and informative
- Improving readability and flow within this section
- Maintaining professional tone
- Preserving all image positions and tokens exactly as they are"""

            # Use the existing LLM fallback system with chunk-specific session ID
            chunk_session_id = f"{self.session_id}_chunk_{chunk_index}"
            improved_content = await call_llm_with_fallback(system_message, user_message, chunk_session_id)
            
            if improved_content:
                print(f"✅ AI processing complete for chunk {chunk_index + 1}: {len(improved_content)} characters")
                return improved_content
            else:
                print(f"⚠️ AI processing failed for chunk {chunk_index + 1}, returning original content")
                return chunk_data['content']
                
        except Exception as e:
            print(f"❌ AI processing failed for chunk {chunk_index + 1}: {e}")
            return chunk_data['content']
    
    def replace_tokens_with_rich_images(self, processed_chunks: list) -> list:
        """
        Phase 3: Replace image tokens with rich HTML figure elements for all chunks
        """
        print(f"🖼️ Phase 3: Starting token replacement across {len(processed_chunks)} chunks")
        
        final_chunks = []
        
        try:
            for i, chunk_data in enumerate(processed_chunks):
                print(f"🎨 Processing tokens in chunk {i+1}: {chunk_data['title']}")
                
                result_html = chunk_data['content']
                
                # Find all image blocks and replace with rich HTML
                import re
                
                pattern = r'<!-- IMAGE_BLOCK:([^>]+) -->(.*?)<!-- END_IMAGE_BLOCK:\1 -->'
                matches = re.findall(pattern, result_html, re.DOTALL)
                
                images_replaced = 0
                for image_id, block_content in matches:
                    if image_id in self.extracted_images:
                        image_data = self.extracted_images[image_id]
                        
                        # Create rich figure element
                        rich_image_html = f"""<figure style="margin: 20px 0; text-align: center;">
    <img src="{image_data['url']}" 
         alt="{image_data['alt_text']}" 
         style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);" />
    <figcaption style="margin-top: 8px; font-size: 14px; color: #6b7280; font-style: italic;">
        {image_data['alt_text']}
    </figcaption>
</figure>"""
                        
                        # Replace the entire image block
                        full_token = f"<!-- IMAGE_BLOCK:{image_id} -->{block_content}<!-- END_IMAGE_BLOCK:{image_id} -->"
                        result_html = result_html.replace(full_token, rich_image_html)
                        images_replaced += 1
                        
                        print(f"🎨 Replaced token {image_id} with rich HTML in chunk {i+1}")
                    else:
                        print(f"⚠️ Image data not found for token: {image_id} in chunk {i+1}")
                
                # Create final chunk data
                final_chunk = {
                    'section_id': chunk_data['section_id'],
                    'title': chunk_data['title'],
                    'content': result_html,
                    'images_replaced': images_replaced,
                    'original_images': len(chunk_data.get('images', []))
                }
                
                final_chunks.append(final_chunk)
                print(f"✅ Chunk {i+1} token replacement complete: {images_replaced} images embedded")
            
            print(f"🎉 Phase 3 complete: Token replacement finished for all {len(final_chunks)} chunks")
            return final_chunks
            
        except Exception as e:
            print(f"❌ Token replacement failed: {e}")
            import traceback
            traceback.print_exc()
            return processed_chunks  # Return processed chunks without token replacement

# === END HTML PREPROCESSING PIPELINE ===

async def extract_document_title(file_path: str, file_extension: str, html_content: str = None) -> str:
    """
    Extract the document title from the first heading or title style
    Priority: H1 > Title style > First paragraph > Filename
    """
    try:
        if file_extension == 'docx':
            # Try to extract from DOCX structure first
            try:
                from docx import Document
                doc = Document(file_path)
                
                # Check for Title style first
                for para in doc.paragraphs:
                    if para.style.name == 'Title' and para.text.strip():
                        title = para.text.strip()
                        print(f"📋 Found Title style: {title}")
                        return title
                
                # Check for Heading 1
                for para in doc.paragraphs:
                    if para.style.name == 'Heading 1' and para.text.strip():
                        title = para.text.strip()
                        print(f"📋 Found Heading 1: {title}")
                        return title
                
                # Check for first non-empty paragraph as fallback
                for para in doc.paragraphs:
                    if para.text.strip() and len(para.text.strip()) < 100:  # Likely a title
                        title = para.text.strip()
                        print(f"📋 Found first paragraph title: {title}")
                        return title
                        
            except Exception as docx_error:
                print(f"⚠️ DOCX title extraction failed: {docx_error}")
        
        # Fallback: Extract from HTML content if available
        if html_content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for H1 elements
            h1_elements = soup.find_all('h1')
            if h1_elements and h1_elements[0].get_text().strip():
                title = h1_elements[0].get_text().strip()
                print(f"📋 Found H1 in HTML: {title}")
                return title
            
            # Look for any heading elements
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                if heading.get_text().strip():
                    title = heading.get_text().strip()
                    print(f"📋 Found heading in HTML: {title}")
                    return title
            
            # Look for first paragraph that might be a title
            paragraphs = soup.find_all('p')
            if paragraphs:
                first_text = paragraphs[0].get_text().strip()
                if first_text and len(first_text) < 100:
                    print(f"📋 Found paragraph title in HTML: {first_text}")
                    return first_text
        
        # Final fallback: use filename without extension
        filename = os.path.basename(file_path)
        if '.' in filename:
            title = filename.rsplit('.', 1)[0]
        else:
            title = filename
        
        # Clean up the filename title
        title = title.replace('_', ' ').replace('-', ' ')
        title = ' '.join(word.capitalize() for word in title.split())
        
        print(f"📋 Using cleaned filename as title: {title}")
        return title
        
    except Exception as e:
        print(f"❌ Title extraction failed: {e}")
        return "Untitled Document"

async def polish_article_content(content: str, title: str, template_data: dict) -> dict:
    """
    Final content polishing pass using LLM for professional formatting and structure
    This applies technical writing standards and clean HTML formatting
    Handles large content by applying basic structure without LLM polishing
    """
    try:
        print(f"✨ Starting final content polishing for: {title}")
        
        # Check content size - skip LLM polishing for very large content
        content_length = len(content)
        max_polishing_size = 50000  # ~12K tokens - safe for LLM processing
        
        if content_length > max_polishing_size:
            print(f"📊 Content too large for LLM polishing ({content_length} chars > {max_polishing_size}), applying basic structure")
            
            # Apply basic HTML structure without LLM processing
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Create structured HTML with proper semantic elements
            structured_html = f"""<article>
    <header>
        <h1>{title}</h1>
    </header>
    <section class="content">
        {content}
    </section>
</article>"""
            
            return {
                'html': structured_html,
                'markdown': structured_html,
                'content': structured_html,
                'polished': False,
                'polishing_skipped': 'content_too_large',
                'word_count': len(content.split())
            }
        
        # For smaller content, proceed with LLM polishing
        print(f"📝 Content size suitable for LLM polishing ({content_length} chars)")
        
        # Create comprehensive prompt for content polishing
        system_message = """You are a professional technical writer and content editor. Your task is to transform the provided content into a publish-ready, professional article with clean HTML structure.

REQUIREMENTS:
1. Create clean, semantic HTML markup (no code blocks, no markdown)
2. Use proper HTML5 semantic elements: <article>, <header>, <section>, <h1>, <h2>, <h3>, <p>, <ul>, <ol>, <figure>
3. Ensure professional tone and technical writing standards
4. Maintain all data-block-id attributes for image placement
5. Create logical content structure with proper headings hierarchy
6. Improve readability and flow while preserving technical accuracy
7. Add introductory and concluding sections if missing
8. Format code examples, API references, and technical details appropriately

OUTPUT FORMAT: Return ONLY clean HTML content without any markdown formatting, code blocks, or wrapper elements."""

        user_message = f"""Transform this content into a professional, publish-ready article:

TITLE: {title}

CONTENT: {content}

TEMPLATE CONTEXT: {json.dumps(template_data, indent=2)}

Create a well-structured, professional article with proper HTML formatting suitable for a knowledge base or documentation platform."""

        # Use the LLM fallback system for content polishing
        polished_content = await call_llm_with_fallback(system_message, user_message)
        
        if polished_content and len(polished_content.strip()) > 100:
            print(f"✅ Content polishing successful: {len(polished_content)} characters")
            
            # Extract clean HTML and ensure proper structure
            polished_html = polished_content.strip()
            
            # Remove any remaining code block markers
            if polished_html.startswith('```'):
                lines = polished_html.split('\n')
                polished_html = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
            
            # Ensure the content starts with proper article structure
            if not polished_html.startswith('<article>') and not polished_html.startswith('<header>'):
                polished_html = f'<article>\n<header><h1>{title}</h1></header>\n{polished_html}\n</article>'
            
            return {
                'html': polished_html,
                'markdown': polished_html,  # Use HTML as markdown for now
                'content': polished_html,
                'polished': True,
                'word_count': len(polished_html.split())
            }
        else:
            print(f"❌ Content polishing failed or produced insufficient content")
            # Return original content with basic HTML structure
            structured_content = f'<article>\n<header><h1>{title}</h1></header>\n<section>\n{content}\n</section>\n</article>'
            return {
                'html': structured_content,
                'markdown': structured_content,
                'content': structured_content,
                'polished': False,
                'polishing_failed': True,
                'word_count': len(content.split())
            }
    
    except Exception as e:
        print(f"❌ Content polishing error: {e}")
        # Return original content with basic structure
        structured_content = f'<article>\n<header><h1>{title}</h1></header>\n<section>\n{content}\n</section>\n</article>'
        return {
            'html': structured_content,
            'markdown': structured_content,
            'content': structured_content,
            'polished': False,
            'polishing_error': str(e),
            'word_count': len(content.split())
        }

async def process_with_html_preprocessing_pipeline(file_path: str, file_extension: str, template_data: dict, training_session: dict) -> list:
    """
    Process documents using the new HTML preprocessing pipeline with structural chunking
    """
    try:
        print(f"🔄 Starting HTML preprocessing pipeline with structural chunking for {file_extension} file")
        
        # Initialize the document preprocessor
        session_id = training_session['session_id']
        preprocessor = DocumentPreprocessor(session_id)
        
        # Phase 1: Convert document to structural HTML chunks with tokenized images
        html_chunks, image_assets = await preprocessor.preprocess_document(file_path, file_extension)
        
        # Phase 2: AI processing for each chunk independently
        processed_chunks = await preprocessor.process_with_ai_preserving_tokens(html_chunks, template_data)
        
        # Phase 3: Replace tokens with rich image HTML in all chunks
        final_chunks = preprocessor.replace_tokens_with_rich_images(processed_chunks)
        
        # Extract document title for proper article naming
        document_title = await extract_document_title(file_path, file_extension, 
                                                     final_chunks[0]['content'] if final_chunks else None)
        
        # Combine chunks into articles
        articles = []
        
        for i, chunk_data in enumerate(final_chunks):
            # Determine article title based on document structure
            if len(final_chunks) == 1:
                # Single article - use document title
                article_title = document_title
            else:
                # Multiple articles - use section title with document context
                section_title = chunk_data['title']
                if section_title.lower() in ['introduction', 'complete document', 'full document']:
                    article_title = document_title
                else:
                    article_title = f"{section_title} | {document_title}"
            
            # Phase 4: Final content polishing for professional output
            polished_result = await polish_article_content(
                chunk_data['content'], 
                article_title, 
                template_data
            )
            
            # Create article from processed and polished chunk
            article = {
                "id": str(uuid.uuid4()),
                "title": article_title,
                "html": polished_result['html'],
                "markdown": polished_result['markdown'],
                "content": polished_result['content'],
                "media": [
                    {
                        "url": img_data['url'],
                        "alt": img_data['alt_text'],
                        "caption": img_data.get('caption', ''),
                        "placement": "inline",
                        "filename": img_data['filename']
                    }
                    for img_data in image_assets.values()
                    if any(img['id'] in chunk_data['content'] for img in [{'id': k} for k in image_assets.keys()])
                ],
                "tags": ["extracted", "generated", "html-pipeline", "structural-chunk", "polished"],
                "status": "training",
                "template_id": training_session['template_id'],
                "session_id": training_session['session_id'],
                "word_count": polished_result['word_count'],
                "image_count": chunk_data.get('images_replaced', 0),
                "format": "html",
                "created_at": datetime.utcnow().isoformat(),
                "ai_processed": True,
                "ai_model": "gpt-4o-mini (with claude + local llm fallback)",
                "training_mode": True,
                "content_polished": polished_result['polished'],
                "metadata": {
                    "source_filename": training_session['filename'],
                    "template_applied": training_session['template_id'],
                    "phase": "html_preprocessing_pipeline_polished",
                    "file_extension": file_extension,
                    "chunk_index": i + 1,
                    "total_chunks": len(final_chunks),
                    "section_id": chunk_data['section_id'],
                    "images_in_chunk": chunk_data.get('images_replaced', 0),
                    "document_title": document_title,
                    "final_polishing_applied": polished_result['polished']
                }
            }
            
            articles.append(article)
            print(f"📄 Created polished article: {article_title} ({len(polished_result['html'])} chars, {chunk_data.get('images_replaced', 0)} images)")
        
        total_images = sum(chunk.get('images_replaced', 0) for chunk in final_chunks)
        print(f"✅ HTML preprocessing pipeline complete: {len(articles)} articles, {total_images} total images, final polishing applied")
        return articles
        
    except Exception as e:
        print(f"❌ HTML preprocessing pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to text processing
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return await process_text_with_template(content, template_data, training_session)
        except:
            return []

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

async def call_local_llm(system_message: str, user_message: str) -> Optional[str]:
    """
    DISABLED: Local LLM fallback disabled due to performance issues.
    The local LLM implementation was causing 30+ minute delays and crashes.
    Better to fail fast than wait indefinitely for broken fallback.
    """
    print("⚠️ Local LLM fallback is disabled for performance optimization")
    return None

async def call_built_in_local_llm(system_message: str, user_message: str) -> Optional[str]:
    """
    DISABLED: Built-in local LLM disabled due to performance issues.
    The transformers library was downloading 2GB+ models during processing
    and causing NumPy compatibility crashes. Better to fail fast.
    """
    print("⚠️ Built-in local LLM is disabled for performance optimization")
    return None

async def call_llm_with_fallback(system_message: str, user_message: str, session_id: str = None) -> Optional[str]:
    """
    Call LLM with three-tier fallback system:
    1. OpenAI (GPT-4o-mini) - Primary
    2. Claude (Anthropic) - Secondary fallback
    3. Local LLM - Final fallback
    Returns the response text or None if all fail
    """
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    # Try OpenAI first
    if OPENAI_API_KEY:
        try:
            print("🤖 Attempting OpenAI (GPT-4o-mini) call...")
            
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 8000,  # Increased from 6000 to 8000
                "temperature": 0.1
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120  # Increased to 120 seconds to reduce timeout issues
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
                "max_tokens": 8000,  # Increased from 6000 to 8000
                "temperature": 0.1,
                "system": system_message,
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=120  # Increased to 120 seconds to reduce timeout issues
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
    
    # Try Local LLM as final fallback
    try:
        print("🤖 Attempting Local LLM fallback...")
        local_response = await call_local_llm(system_message, user_message)
        if local_response:
            return local_response
    except Exception as e:
        print(f"❌ Local LLM also failed: {e}")
    
    print("❌ All LLM options failed - no AI response available")
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
        
        # DEBUG: Check if uploaded file is valid for DOCX
        if file.filename.lower().endswith('.docx'):
            print(f"🔍 DEBUG: Checking DOCX file validity")
            # Check if file starts with ZIP signature (DOCX files are ZIP archives)
            if file_content[:4] == b'PK\x03\x04':
                print(f"✅ Valid DOCX file - has ZIP signature")
            else:
                print(f"❌ Invalid DOCX file - missing ZIP signature")
                print(f"🔍 File starts with: {file_content[:20]}")
                # Try to analyze the content
                try:
                    content_str = file_content.decode('utf-8', errors='ignore')[:100]
                    print(f"🔍 Content preview: {content_str}")
                except:
                    print(f"🔍 Binary content, cannot decode as text")
        
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
        
        # Additional DEBUG: Verify saved file
        if file.filename.lower().endswith('.docx'):
            try:
                import zipfile
                with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                    print(f"✅ Saved DOCX is valid ZIP with {len(zip_ref.namelist())} entries")
            except Exception as zip_error:
                print(f"❌ Saved file is not a valid ZIP: {zip_error}")
        
        # Process based on file type - NEW HTML PREPROCESSING PIPELINE
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else 'txt'
        
        # Use HTML preprocessing pipeline for supported document types
        if file_extension in ['docx', 'doc', 'pdf', 'ppt', 'pptx']:
            print(f"🔄 Using HTML preprocessing pipeline for {file_extension}")
            articles = await process_with_html_preprocessing_pipeline(temp_file_path, file_extension, template_data, training_session)
        elif file_extension in ['xls', 'xlsx']:
            print("🔍 Processing Excel file")
            articles = await process_excel_with_template(temp_file_path, template_data, training_session)
        elif file_extension in ['html', 'htm']:
            print("🔍 Processing HTML file")
            articles = await process_html_with_template(temp_file_path, template_data, training_session)
        elif file_extension in ['txt', 'md']:
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
        
        # Add articles to training session before storing
        training_session["articles"] = articles
        
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
            from lxml import etree  # Use lxml instead of xml.etree.ElementTree
        except ImportError:
            print("python-docx not installed, using fallback processing")
            return await process_text_with_template("", template_data, training_session)
        
        print(f"🔍 Phase 1: Starting enhanced DOCX content extraction")
        
        # Try to read as actual DOCX file
        try:
            doc = Document(file_path)
            print(f"✅ Successfully loaded DOCX file")
        except Exception as docx_error:
            print(f"⚠️ Failed to load as DOCX file: {docx_error}")
            print(f"🔄 Falling back to text processing")
            # If it's not a valid DOCX file, treat it as text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return await process_text_with_template(content, template_data, training_session)
            except Exception as text_error:
                print(f"❌ Text fallback also failed: {text_error}")
                return []
        
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
        
        # Phase 1: Enhanced Image Extraction using new contextual system
        contextual_images = extract_contextual_images_from_docx(file_path, doc, extracted_content, training_session)
        
        print(f"🔍 DEBUG - Contextual images returned: {len(contextual_images)}")
        for i, img in enumerate(contextual_images):
            print(f"  Image {i+1}: {img.get('filename', 'unknown')} - {img.get('url', 'no_url')}")
        
        print(f"✅ Phase 1 Complete: {len(extracted_content['structure'])} content blocks, {len(contextual_images)} images")
        
        # CRITICAL FIX: Force enhanced processing for DOCX files to prevent fallback bypass
        body_text_length = len(extracted_content.get("body_text", ""))
        structure_count = len(extracted_content.get('structure', []))
        total_content_length = body_text_length + sum(len(block.get('content', '')) for block in extracted_content.get('structure', []))
        
        print(f"🔍 DEBUG Processing decision metrics:")
        print(f"  - Contextual images: {len(contextual_images)}")
        print(f"  - Structure blocks: {structure_count}")
        print(f"  - Body text length: {body_text_length}")
        print(f"  - Total content length: {total_content_length}")
        
        # FORCE enhanced processing for any meaningful DOCX content
        # Use enhanced processing if:
        # 1. ANY images found, OR
        # 2. Multiple structure blocks (even 2+), OR  
        # 3. ANY substantial text content (lowered threshold)
        should_use_enhanced = (
            len(contextual_images) > 0 or 
            structure_count >= 1 or  # Changed from > 2 to >= 1
            body_text_length > 200 or  # Changed from 1000 to 200
            total_content_length > 500  # Added total content check
        )
        
        print(f"🚀 Processing decision: {'ENHANCED' if should_use_enhanced else 'SIMPLIFIED'}")
        
        if should_use_enhanced:
            print(f"✅ Using ENHANCED processing path: {len(contextual_images)} images, {structure_count} content blocks, {body_text_length} chars body text, {total_content_length} total chars")
            
            # ENHANCED CONTENT PREPARATION - Comprehensive content aggregation
            enhanced_content = ""
            content_sources = []
            
            # Process structured content with proper HTML
            structure_content = ""
            for block in extracted_content.get('structure', []):
                block_type = block.get('type', 'paragraph')
                content_text = block.get('content', '').strip()
                
                if not content_text:
                    continue
                    
                if block_type.startswith('h'):
                    # Handle h1, h2, h3, h4 properly
                    level = block_type[1] if len(block_type) > 1 and block_type[1].isdigit() else '2'
                    structure_content += f"<h{level}>{content_text}</h{level}>\n\n"
                elif block_type == 'heading':
                    level = block.get('level', 2)
                    structure_content += f"<h{level}>{content_text}</h{level}>\n\n"
                elif block_type == 'paragraph':
                    structure_content += f"<p>{content_text}</p>\n\n"
                elif block_type == 'list_item':
                    structure_content += f"<li>{content_text}</li>\n"
                else:
                    structure_content += f"<p>{content_text}</p>\n\n"
            
            if structure_content.strip():
                enhanced_content += structure_content
                content_sources.append(f"structured content ({len(structure_content)} chars)")
            
            # Add body text with formatting
            body_text = extracted_content.get("body_text", "").strip()
            if body_text:
                # Ensure body text is properly formatted
                if not body_text.startswith('<'):
                    # Convert plain text to HTML paragraphs
                    paragraphs = body_text.split('\n\n')
                    formatted_body = ""
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            formatted_body += f"<p>{para}</p>\n\n"
                    body_text = formatted_body
                
                enhanced_content += f"\n\n{body_text}"
                content_sources.append(f"body text ({len(body_text)} chars)")
            
            # Add table content
            table_content = ""
            for table in extracted_content.get("tables", []):
                if table.get("html"):
                    table_content += f"\n\n{table['html']}\n"
            
            if table_content.strip():
                enhanced_content += table_content
                content_sources.append(f"tables ({len(table_content)} chars)")
            
            # Ensure we have substantial content for processing
            enhanced_content = enhanced_content.strip()
            
            # If content is still insufficient, create more comprehensive content
            if len(enhanced_content) < 500:
                print("⚠️ Enhanced content insufficient, expanding with additional context")
                
                # Add headings as content if available
                headings_content = ""
                for heading in extracted_content.get("headings", []):
                    if heading.get("text"):
                        level = heading.get("level", 2)
                        headings_content += f"<h{level}>{heading['text']}</h{level}>\n"
                        headings_content += f"<p>This section covers {heading['text'].lower()} with comprehensive details and explanations.</p>\n\n"
                
                if headings_content:
                    enhanced_content += f"\n\n{headings_content}"
                    content_sources.append(f"expanded headings ({len(headings_content)} chars)")
            
            print(f"📊 Enhanced content sources: {', '.join(content_sources)}")
            print(f"📊 Total enhanced content: {len(enhanced_content)} chars")
            
            print(f"🎨 Enhanced content prepared: {len(enhanced_content)} chars with {len(contextual_images)} contextual images")
            
            # CRITICAL FIX: Ensure enhanced processing succeeds
            if len(enhanced_content) < 100:
                print("❌ Enhanced content too short, forcing fallback creation")
                enhanced_content = f"<h1>Document Processing</h1>\n<p>Processing content from {training_session.get('filename', 'document')} with {len(contextual_images)} images.</p>\n"
                
                # Add any available content
                if extracted_content.get("body_text"):
                    enhanced_content += f"<p>{extracted_content['body_text']}</p>\n"
                
                # Add table summaries
                for i, table in enumerate(extracted_content.get("tables", []), 1):
                    if table.get("data"):
                        enhanced_content += f"<p>Table {i}: Contains {len(table['data'])} rows of data.</p>\n"
            
            # Use enhanced template-based processing with contextual images
            articles = await create_articles_with_template(enhanced_content, contextual_images, template_data, training_session)
            
            print(f"📊 Enhanced processing result: {len(articles)} articles generated")
            
            # CRITICAL FIX: Don't give up on enhanced processing too easily
            if articles and len(articles) > 0:
                print(f"✅ Enhanced processing successful: {len(articles)} articles with images")
                return articles
            else:
                print("⚠️ Enhanced processing failed, trying recovery...")
                # Try recovery with simpler template approach
                recovery_articles = await create_recovery_articles(enhanced_content, contextual_images, template_data, training_session)
                if recovery_articles:
                    print(f"✅ Recovery successful: {len(recovery_articles)} articles")
                    return recovery_articles
                else:
                    print("❌ Recovery failed, falling back to simplified")
        
        # Fallback to simplified processing only if enhanced fails or has minimal content
        print(f"🔄 Using simplified processing fallback")
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
            
            print(f"🔄 Using simplified processing for DOCX fallback: {len(fallback_content)} chars")
            
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

def extract_contextual_images_from_docx(file_path: str, doc, extracted_content: dict, training_session: dict) -> list:
    """
    Enhanced image extraction with contextual tagging according to specifications
    Only extracts relevant images and tags them with proper context
    """
    contextual_images = []
    
    try:
        import zipfile
        from lxml import etree
        
        # Phase 1: Parse document structure to map images to context
        paragraph_contexts = []
        current_chapter = "Introduction"
        
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if not text:
                continue
                
            # Update current chapter context with better heading detection
            if is_heading(paragraph):
                # CRITICAL FIX: Limit chapter names to reasonable length
                chapter_text = text[:100] + "..." if len(text) > 100 else text
                current_chapter = chapter_text
                print(f"📖 DEBUG: New chapter detected: '{current_chapter}' (original length: {len(text)})")
            else:
                # CRITICAL FIX: Don't let long paragraphs become chapter names
                if len(text) > 150:
                    print(f"📄 DEBUG: Long paragraph ignored for chapter context: {len(text)} chars")
                
            paragraph_contexts.append({
                "index": i,
                "text": text,
                "chapter": current_chapter,
                "is_heading": is_heading(paragraph),
                "page_estimate": estimate_page_number(i, len(doc.paragraphs))
            })
        
        # Phase 2: Extract images with contextual filtering and tagging
        print(f"🖼️ Starting enhanced contextual image extraction from {file_path}")
        
        # Debug: Check if file exists and is accessible
        if not os.path.exists(file_path):
            print(f"❌ File does not exist: {file_path}")
            return []
        
        print(f"✅ File exists: {file_path}")
        
        # Debug: Try to open as ZIP file
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            print(f"✅ Successfully opened as ZIP file")
            file_list = zip_ref.namelist()
            print(f"📁 ZIP contains {len(file_list)} files")
            
            # Debug: Check for media files
            media_files = [f for f in file_list if f.startswith('word/media/')]
            print(f"🖼️ Found {len(media_files)} media files:")
            for media_file in media_files:
                print(f"  - {media_file}")
                
            if len(media_files) == 0:
                print("❌ No media files found in DOCX")
                return []
            # Get document relationships to map images to content
            try:
                rels_xml = zip_ref.read('word/_rels/document.xml.rels')
                rels_tree = etree.fromstring(rels_xml)
                image_relationships = {}
                
                for rel in rels_tree.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                    if 'image' in rel.get('Type', ''):
                        image_relationships[rel.get('Id')] = rel.get('Target')
                        
            except Exception as rel_error:
                print(f"⚠️ Could not parse image relationships: {rel_error}")
                image_relationships = {}
            
            # Parse document XML to find image positions
            try:
                doc_xml = zip_ref.read('word/document.xml')
                doc_tree = etree.fromstring(doc_xml)
                image_positions = extract_enhanced_image_positions_from_xml(doc_tree, paragraph_contexts)
            except Exception as xml_error:
                print(f"⚠️ Could not parse document XML for positions: {xml_error}")
                image_positions = []
            
            # Extract actual image files with contextual filtering
            for file_info in zip_ref.filelist:
                if not file_info.filename.startswith('word/media/'):
                    continue
                    
                filename = file_info.filename.split('/')[-1].lower()
                
                # Find contextual placement for this image FIRST
                image_context = find_enhanced_image_context(filename, image_positions, paragraph_contexts)
                
                # CRITICAL FIX: If enhanced context has insufficient text, use fallback context
                if image_context and len(image_context.get('paragraph_text', '').strip()) < 20:
                    print(f"⚠️ Enhanced context for {filename} has insufficient text ({len(image_context.get('paragraph_text', ''))} chars), creating fallback context")
                    fallback_context = create_fallback_image_context(filename, len(contextual_images) + 1, paragraph_contexts)
                    if fallback_context and len(fallback_context.get('paragraph_text', '').strip()) >= 20:
                        print(f"✅ Using fallback context for {filename} with {len(fallback_context.get('paragraph_text', ''))} chars")
                        image_context = fallback_context
                    else:
                        print(f"⚠️ Fallback context also has insufficient text for {filename}")
                
                if not image_context:
                    print(f"⚠️ No enhanced context found for {filename}, creating fallback context")
                    print(f"🔍 DEBUG: Image positions available: {len(image_positions)}")
                    print(f"🔍 DEBUG: Paragraph contexts available: {len(paragraph_contexts)}")
                    # CRITICAL FIX: Create fallback context instead of skipping
                    image_context = create_fallback_image_context(filename, len(contextual_images) + 1, paragraph_contexts)
                    if image_context:
                        print(f"✅ DEBUG: Successfully created fallback context for {filename}: {len(image_context.get('text', ''))} chars")
                    else:
                        print(f"❌ DEBUG: Failed to create fallback context for {filename}")
                
                if not image_context:
                    print(f"🚫 Skipping image after context creation failed: {filename}")
                    continue
                    
                print(f"🔍 DEBUG: Final image context for {filename}: chapter='{image_context.get('chapter', 'unknown')}', page={image_context.get('page', 0)}, text_length={len(image_context.get('paragraph_text', ''))}")
                    
                # CRITICAL FIX: Apply filtering rules AFTER context is created so filtering can use context
                if should_skip_image(filename, file_info, image_context):
                    continue
                
                # Extract and save the image
                image_data = zip_ref.read(file_info.filename)
                
                # Generate contextual filename
                safe_prefix = "".join(c for c in training_session.get('filename', 'doc') if c.isalnum())[:10]
                context_key = "".join(c for c in image_context['chapter'][:15] if c.isalnum())
                unique_filename = f"{safe_prefix}_{context_key}_{image_context['page']}_img{len(contextual_images)+1}_{str(uuid.uuid4())[:8]}.{filename.split('.')[-1]}"
                
                file_path_static = f"static/uploads/{unique_filename}"
                
                # Ensure upload directory exists
                os.makedirs("static/uploads", exist_ok=True)
                
                # Save image file
                with open(file_path_static, "wb") as f:
                    f.write(image_data)
                
                # Generate URL
                file_url = f"/api/static/uploads/{unique_filename}"
                
                # Create contextual image object according to specifications
                contextual_image = {
                    "image": file_url,
                    "page": image_context['page'],
                    "position": image_context['position'],
                    "chapter": image_context['chapter'],
                    "type": image_context['type'],
                    "filename": unique_filename,
                    "url": file_url,
                    "size": len(image_data),
                    "is_svg": filename.endswith('.svg'),
                    "caption": generate_contextual_caption(image_context, paragraph_contexts),
                    "alt_text": f"Figure {len(contextual_images) + 1}: {image_context['chapter']} illustration",
                    "original_filename": filename,
                    "context_paragraph": image_context.get('paragraph_text', ''),
                    "placement_priority": calculate_placement_priority(image_context)
                }
                
                contextual_images.append(contextual_image)
                print(f"✅ Extracted contextual image: {unique_filename} (Chapter: {image_context['chapter']}, Page: {image_context['page']})")
        
        # Sort images by their natural document flow order
        contextual_images.sort(key=lambda x: (x['page'], x['placement_priority']))
        
        print(f"🎯 Enhanced image extraction complete: {len(contextual_images)} contextual images extracted")
        return contextual_images
        
    except Exception as e:
        print(f"❌ Enhanced image extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def should_skip_image(filename: str, file_info, paragraph_context=None) -> bool:
    """
    Enhanced image filtering to skip decorative images and focus on content-relevant images
    """
    # Enhanced skip patterns for decorative/irrelevant images
    skip_patterns = [
        'logo', 'header', 'footer', 'watermark', 'background', 'banner',
        'cover', 'title', 'border', 'decoration', 'template', 'frame',
        'bullet', 'icon', 'symbol', 'separator', 'divider', 'ornament',
        'brand', 'trademark', 'copyright', 'signature', 'letterhead'
    ]
    
    # Check filename patterns
    filename_lower = filename.lower()
    if any(pattern in filename_lower for pattern in skip_patterns):
        print(f"🚫 Skipping decorative image (filename pattern): {filename}")
        return True
    
    # Skip very small images (likely decorative icons/bullets)
    if file_info.file_size < 8000:  # Less than 8KB
        print(f"🚫 Skipping small decorative image: {filename} ({file_info.file_size} bytes)")
        return True
    
    # Skip very large images that might be cover pages or backgrounds
    if file_info.file_size > 5000000:  # Greater than 5MB
        print(f"🚫 Skipping very large image (likely cover/background): {filename} ({file_info.file_size} bytes)")
        return True
    
    # Enhanced context-based filtering
    if paragraph_context:
        # CRITICAL FIX: Disable aggressive cover page filtering for now to allow content images
        # Most tutorial documents have important images on page 1
        page_estimate = paragraph_context.get('page_estimate', 0)
        chapter = paragraph_context.get('chapter', '').lower()
        
        # Only skip images that are clearly on cover/title pages
        if 'title' in chapter or 'cover' in chapter or 'table of contents' in chapter:
            print(f"🚫 Skipping image from cover page area: {filename}")
            return True
        
        print(f"✅ Allowing image - page {page_estimate}, chapter: '{chapter[:50]}...'")
        # ALLOW tutorial/content images that might be on page 1
    
    # Check for repeated/pattern-based image names (likely decorative) - MOVED UP
    import re
    if re.search(r'image\d+$|img\d+$|picture\d+$', filename_lower.split('.')[0]):
        # CRITICAL FIX: Allow generic numbered images when they have ANY context (including fallback)
        if not paragraph_context:
            print(f"🚫 Skipping generic numbered image without any context: {filename}")
            return True
        # For generic numbered images, use relaxed threshold for fallback context
        print(f"🔍 DEBUG: Context keys for {filename}: {list(paragraph_context.keys())}")
        context_text = paragraph_context.get('paragraph_text', '') or paragraph_context.get('text', '')
        print(f"🔍 DEBUG: Context text for {filename}: '{context_text[:50]}...' ({len(context_text)} chars)")
        
        if len(context_text.strip()) >= 20:  # Reduced threshold for generic numbered images with fallback
            print(f"✅ Allowing generic numbered image with fallback context: {filename} ({len(context_text)} chars context)")
            return False
        else:
            print(f"🚫 Skipping generic numbered image with insufficient context: {filename} ({len(context_text)} chars)")
            return True
            
    # For non-generic images, apply stricter context requirements
    if paragraph_context:
        # Skip images with minimal surrounding text (likely decorative) - MOVED DOWN and only for non-generic
        surrounding_text = paragraph_context.get('paragraph_text', '') or paragraph_context.get('text', '')
        if len(surrounding_text.strip()) < 50:
            print(f"🚫 Skipping non-generic image with minimal context: {filename}")
            return True
    
    return False





def is_heading(paragraph) -> bool:
    """
    Determine if a paragraph is a heading
    """
    try:
        # Check if paragraph uses a heading style
        if hasattr(paragraph, 'style') and paragraph.style:
            style_name = paragraph.style.name.lower()
            if 'heading' in style_name:
                return True
        
        # Check text characteristics
        text = paragraph.text.strip()
        if not text:
            return False
        
        # CRITICAL FIX: Be much more restrictive about what constitutes a heading
        # Reject anything that's too long to be a reasonable heading
        if len(text) > 80:  # Reduced from 100 to 80
            return False
            
        # Check for obvious non-heading patterns
        if any(phrase in text.lower() for phrase in ['add the following', 'in this section', 'as shown', 'follow these steps', 'copy the code']):
            return False
            
        # Short, capitalized text might be a heading
        if len(text) < 80 and (text.isupper() or text.istitle()):
            # Additional checks for instruction-like text
            if ':' in text and ('element' in text.lower() or 'following' in text.lower()):
                return False
            return True
            
        # Check for heading patterns (but be more restrictive)
        if len(text) < 50 and (re.match(r'^\d+\.?\s+[A-Z]', text) or re.match(r'^[A-Z][A-Za-z\s]*$', text)):
            return True
    
    except Exception:
        pass
    
    return False

def estimate_page_number(paragraph_index: int, total_paragraphs: int) -> int:
    """
    Estimate page number based on paragraph position
    Assumes ~30 paragraphs per page on average
    """
    return max(1, (paragraph_index // 30) + 1)





def embed_contextual_images_in_content(content: str, images: list) -> str:
    """
    Embed images in content using enhanced contextual placement according to specifications
    """
    if not images:
        return content
    
    print(f"🖼️ Embedding {len(images)} contextual images in content")
    
    # Parse content into sections based on headings
    content_sections = parse_content_into_sections(content)
    
    # Group images by chapter/section
    images_by_chapter = {}
    for img in images:
        chapter = img.get('chapter', 'Introduction')
        if chapter not in images_by_chapter:
            images_by_chapter[chapter] = []
        images_by_chapter[chapter].append(img)
    
    # Embed images in their appropriate sections
    enhanced_content = ""
    
    for section in content_sections:
        section_title = section['title']
        section_content = section['content']
        
        # Find matching images for this section
        matching_images = []
        
        # Exact chapter match
        if section_title in images_by_chapter:
            matching_images.extend(images_by_chapter[section_title])
        
        # Fuzzy matching for partial matches
        for chapter, chapter_images in images_by_chapter.items():
            if section_title.lower() in chapter.lower() or chapter.lower() in section_title.lower():
                matching_images.extend([img for img in chapter_images if img not in matching_images])
        
        # Add section header
        enhanced_content += section['header']
        
        if matching_images:
            # Insert images contextually within the section
            enhanced_content += insert_images_contextually(section_content, matching_images)
        else:
            # No images for this section, just add content
            enhanced_content += section_content
        
        enhanced_content += "\n\n"
    
    # Handle any remaining images that didn't match sections
    unmatched_images = []
    all_embedded_images = set()
    
    for section in content_sections:
        section_title = section['title']
        if section_title in images_by_chapter:
            all_embedded_images.update(img['url'] for img in images_by_chapter[section_title])
    
    for img in images:
        if img['url'] not in all_embedded_images:
            unmatched_images.append(img)
    
    if unmatched_images:
        print(f"📎 Adding {len(unmatched_images)} unmatched images at the end")
        enhanced_content += "\n\n<h2>Additional Resources</h2>\n"
        for img in unmatched_images:
            enhanced_content += create_image_figure_html(img)
            enhanced_content += "\n\n"
    
    return enhanced_content.strip()

def parse_content_into_sections(content: str) -> list:
    """
    Parse HTML content into logical sections based on headings
    """
    import re
    
    sections = []
    
    # Split content by heading tags
    heading_pattern = r'(<h[1-6][^>]*>.*?</h[1-6]>)'
    parts = re.split(heading_pattern, content, flags=re.DOTALL | re.IGNORECASE)
    
    current_section = {
        'title': 'Introduction',
        'header': '',
        'content': ''
    }
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Check if this part is a heading
        heading_match = re.match(r'<h[1-6][^>]*>(.*?)</h[1-6]>', part, re.DOTALL | re.IGNORECASE)
        
        if heading_match:
            # Save previous section if it has content
            if current_section['content'].strip():
                sections.append(current_section.copy())
            
            # Start new section
            heading_text = heading_match.group(1).strip()
            current_section = {
                'title': heading_text,
                'header': part,
                'content': ''
            }
        else:
            # Add to current section content
            current_section['content'] += part
    
    # Don't forget the last section
    if current_section['content'].strip():
        sections.append(current_section)
    
    return sections if sections else [{'title': 'Content', 'header': '', 'content': content}]

def insert_images_contextually(content: str, images: list) -> str:
    """
    Insert images at appropriate positions within section content
    """
    if not images:
        return content
    
    # Split content into paragraphs
    paragraphs = content.split('</p>')
    if len(paragraphs) <= 1:
        # No clear paragraph structure, insert images at the beginning
        image_html = ""
        for img in images:
            image_html += create_image_figure_html(img) + "\n\n"
        return image_html + content
    
    # Calculate ideal insertion points
    total_paragraphs = len(paragraphs) - 1  # Last split is usually empty
    images_per_position = max(1, len(images))
    
    enhanced_content = ""
    image_index = 0
    
    for i, paragraph in enumerate(paragraphs[:-1]):  # Skip last empty element
        enhanced_content += paragraph + '</p>'
        
        # Determine if we should insert an image after this paragraph
        if image_index < len(images):
            # Insert images based on their placement preferences
            should_insert = False
            current_img = images[image_index]
            
            # Check position preference from contextual data
            position_info = current_img.get('position', '')
            
            if f"after-paragraph-{i}" in position_info:
                should_insert = True
            elif i == total_paragraphs // 2 and image_index == 0:  # Middle of content
                should_insert = True
            elif i == total_paragraphs - 1 and image_index < len(images):  # End of content
                should_insert = True
            elif (i + 1) % max(1, total_paragraphs // len(images)) == 0:  # Even distribution
                should_insert = True
            
            if should_insert:
                enhanced_content += "\n\n" + create_image_figure_html(current_img)
                image_index += 1
        
        enhanced_content += "\n\n"
    
    # Insert any remaining images at the end
    while image_index < len(images):
        enhanced_content += create_image_figure_html(images[image_index]) + "\n\n"
        image_index += 1
    
    return enhanced_content

def create_image_figure_html(img: dict) -> str:
    """
    Create proper HTML figure element for an image using contextual data
    """
    # Use contextual data from the enhanced extraction
    image_url = img.get('url', img.get('image', ''))
    alt_text = img.get('alt_text', f"Figure: {img.get('chapter', 'Content')} illustration")
    caption = img.get('caption', f"Figure: {img.get('chapter', 'Document')} visual")
    
    # Create accessible, well-structured HTML figure
    figure_html = f'''<figure class="embedded-image" style="margin: 1.5rem 0; text-align: center;">
    <img src="{image_url}" 
         alt="{alt_text}" 
         style="max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
    <figcaption style="margin-top: 0.5rem; font-style: italic; color: #666; font-size: 0.9em;">
        {caption}
    </figcaption>
</figure>'''
    
    return figure_html

def _process_images_for_pdf(html_content: str) -> str:
    """
    Process HTML content to convert relative image URLs to absolute URLs for PDF generation
    """
    import re
    import os
    
    # Pattern to match img src attributes
    img_pattern = r'<img([^>]*?)src=["\']([^"\']*?)["\']([^>]*?)>'
    
    def replace_img_src(match):
        before_src = match.group(1)
        src_url = match.group(2)
        after_src = match.group(3)
        
        # If it's already an absolute URL or data URL, leave it as is
        if src_url.startswith(('http://', 'https://', 'data:')):
            return match.group(0)
        
        # If it's a relative URL starting with /api/static, convert to file path
        if src_url.startswith('/api/static/'):
            file_path = src_url.replace('/api/static/', '/app/backend/static/')
            
            # Check if file exists
            if os.path.exists(file_path):
                return f'<img{before_src}src="file://{file_path}"{after_src}>'
            else:
                print(f"⚠️ Image file not found: {file_path}")
                # Remove the img tag if file doesn't exist
                return f'<p style="color: #666; font-style: italic; text-align: center;">[Image not available: {os.path.basename(file_path)}]</p>'
        
        # For other relative URLs starting with /, convert to file paths
        if src_url.startswith('/'):
            file_path = f"/app/backend{src_url}"
            if os.path.exists(file_path):
                return f'<img{before_src}src="file://{file_path}"{after_src}>'
            else:
                print(f"⚠️ Image file not found: {file_path}")
                return f'<p style="color: #666; font-style: italic; text-align: center;">[Image not available: {os.path.basename(file_path)}]</p>'
        
        return match.group(0)
    
    # Replace all img src attributes
    processed_html = re.sub(img_pattern, replace_img_src, html_content)
    
    # Count original images and processed images
    original_images = len(re.findall(img_pattern, html_content))
    remaining_images = len(re.findall(img_pattern, processed_html))
    
    print(f"🖼️ Processed {original_images} images for PDF generation, {remaining_images} images available")
    
    return processed_html

def generate_pdf_from_html(html_content: str, title: str = "Generated Article") -> bytes:
    """
    Generate PDF from HTML content using WeasyPrint
    """
    try:
        from weasyprint import HTML, CSS
        import tempfile
        import os
        
        # Validate input
        if not html_content or len(html_content.strip()) < 10:
            raise ValueError("HTML content is empty or too short")
        
        print(f"🎨 Generating PDF for: '{title}' with {len(html_content)} characters")
        
        # Process HTML content to convert relative image URLs to absolute URLs
        processed_html_content = _process_images_for_pdf(html_content)
        
        # Create a complete HTML document with proper styling
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Arial', 'Helvetica', sans-serif;
                    line-height: 1.6;
                    margin: 2cm;
                    color: #333;
                    font-size: 12pt;
                }}
                
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 30px;
                    font-size: 24pt;
                    page-break-after: avoid;
                }}
                
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                    margin-bottom: 15px;
                    font-size: 18pt;
                    page-break-after: avoid;
                }}
                
                h3 {{
                    color: #5d6d7e;
                    margin-top: 25px;
                    margin-bottom: 12px;
                    font-size: 16pt;
                    page-break-after: avoid;
                }}
                
                p {{
                    margin-bottom: 12px;
                    text-align: justify;
                    orphans: 3;
                    widows: 3;
                }}
                
                ul, ol {{
                    margin-bottom: 15px;
                    padding-left: 25px;
                }}
                
                li {{
                    margin-bottom: 5px;
                }}
                
                figure.embedded-image {{
                    margin: 20px 0;
                    text-align: center;
                    page-break-inside: avoid;
                }}
                
                figure.embedded-image img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                
                img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    display: block;
                    margin: 10px auto;
                }}
                
                figcaption {{
                    margin-top: 8px;
                    font-style: italic;
                    color: #666;
                    font-size: 10pt;
                }}
                
                .article-metadata {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    margin-bottom: 25px;
                    border-radius: 4px;
                }}
                
                .no-content-notice {{
                    background-color: #fff3cd;
                    padding: 20px;
                    border: 1px solid #ffeaa7;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                
                .no-content-notice h2 {{
                    color: #856404;
                    margin-top: 0;
                }}
                
                .no-content-notice p {{
                    color: #856404;
                    margin-bottom: 8px;
                }}
                
                @page {{
                    margin: 2cm;
                    @top-center {{
                        content: "{title}";
                        font-size: 10pt;
                        color: #666;
                    }}
                    @bottom-center {{
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 10pt;
                        color: #666;
                    }}
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    page-break-inside: avoid;
                }}
                
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                
                th {{
                    background-color: #f5f5f5;
                    font-weight: bold;
                }}
                
                blockquote {{
                    margin: 20px 0;
                    padding: 15px 20px;
                    background-color: #f8f9fa;
                    border-left: 4px solid #3498db;
                    font-style: italic;
                }}
                
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 11pt;
                }}
                
                pre {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-wrap: break-word;
                    white-space: pre-wrap;
                    font-family: 'Courier New', monospace;
                    font-size: 10pt;
                }}
            </style>
        </head>
        <body>
            {processed_html_content}
        </body>
        </html>
        """
        
        # Log the HTML content for debugging
        print(f"📄 HTML document length: {len(full_html)} characters")
        print(f"📝 HTML preview: {full_html[:300]}...")
        
        # Generate PDF using WeasyPrint
        print("🔧 Starting WeasyPrint PDF generation...")
        pdf_bytes = HTML(string=full_html).write_pdf()
        
        # Validate PDF output
        if not pdf_bytes:
            raise ValueError("WeasyPrint returned no PDF data")
        
        if len(pdf_bytes) < 1000:
            raise ValueError(f"Generated PDF is too small: {len(pdf_bytes)} bytes")
        
        # Check for valid PDF header
        if not pdf_bytes.startswith(b'%PDF-'):
            raise ValueError("Generated data does not appear to be a valid PDF")
        
        print(f"✅ PDF generated successfully: {len(pdf_bytes)} bytes")
        return pdf_bytes
        
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/api/content-library/article/{article_id}/download-pdf")
async def download_article_pdf(article_id: str):
    """Download a Content Library article as PDF"""
    try:
        print(f"🔍 Generating PDF for Content Library article: {article_id}")
        
        # Find the article in Content Library
        article = await db.content_library.find_one({"id": article_id})
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Get article content and title
        title = article.get("title", "Generated Article")
        content = article.get("content", "")
        
        # Debug logging for content validation
        print(f"📄 Article title: '{title}'")
        print(f"📏 Content length: {len(content)} characters")
        print(f"📝 Content preview: {content[:200]}...")
        
        if not content or len(content.strip()) < 50:
            # Provide fallback content if article is empty or too short
            print("⚠️ Article content is empty or too short, providing fallback content")
            content = f"""
            <h1>{title}</h1>
            <div class="article-metadata">
                <p><strong>Article ID:</strong> {article_id}</p>
                <p><strong>Created:</strong> {article.get('created_at', 'Unknown')}</p>
                <p><strong>Source:</strong> {article.get('source_type', 'Unknown')}</p>
            </div>
            <div class="no-content-notice">
                <h2>Content Not Available</h2>
                <p>This article appears to have empty or insufficient content for PDF generation.</p>
                <p>Please ensure the article has been properly processed and contains meaningful content.</p>
            </div>
            """
        
        # Clean title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_title[:50]}.pdf"  # Limit filename length
        
        # Generate PDF
        print(f"🎨 Starting PDF generation with {len(content)} characters of content")
        pdf_bytes = generate_pdf_from_html(content, title)
        
        # Validate PDF was actually generated
        if not pdf_bytes or len(pdf_bytes) < 1000:
            print(f"❌ Generated PDF is too small: {len(pdf_bytes) if pdf_bytes else 0} bytes")
            raise HTTPException(status_code=500, detail="PDF generation produced invalid output")
        
        print(f"✅ PDF generated successfully: {len(pdf_bytes)} bytes")
        
        # Create PDF stream response
        def generate():
            yield pdf_bytes
        
        # Return streaming response with proper headers
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'application/pdf',
            'Content-Length': str(len(pdf_bytes))
        }
        
        return StreamingResponse(
            generate(),
            media_type='application/pdf',
            headers=headers
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 404) without modification
        raise
    except Exception as e:
        print(f"❌ Content Library PDF download error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/training/article/{session_id}/{article_index}/download-pdf")
async def download_training_article_pdf(session_id: str, article_index: int):
    """Download a Training Interface article as PDF"""
    try:
        print(f"🔍 Generating PDF for Training article: {session_id}, index: {article_index}")
        
        # Find the training session
        training_session = await db.training_sessions.find_one({"session_id": session_id})
        
        if not training_session:
            raise HTTPException(status_code=404, detail="Training session not found")
        
        # Get the specific article
        articles = training_session.get("articles", [])
        
        if article_index >= len(articles) or article_index < 0:
            raise HTTPException(status_code=404, detail="Article not found in session")
        
        article = articles[article_index]
        
        # Get article content and title
        title = article.get("title", f"Training Article {article_index + 1}")
        content = article.get("content", "")
        
        # Debug logging for content validation
        print(f"📄 Training article title: '{title}'")
        print(f"📏 Content length: {len(content)} characters")
        print(f"📝 Content preview: {content[:200]}...")
        
        if not content or len(content.strip()) < 50:
            # Provide fallback content if article is empty or too short
            print("⚠️ Training article content is empty or too short, providing fallback content")
            content = f"""
            <h1>{title}</h1>
            <div class="article-metadata">
                <p><strong>Training Session:</strong> {session_id}</p>
                <p><strong>Article Index:</strong> {article_index}</p>
                <p><strong>Template:</strong> {training_session.get('template', 'Unknown')}</p>
                <p><strong>Filename:</strong> {training_session.get('filename', 'Unknown')}</p>
            </div>
            <div class="no-content-notice">
                <h2>Content Not Available</h2>
                <p>This training article appears to have empty or insufficient content for PDF generation.</p>
                <p>Please ensure the document was properly processed and contains meaningful content.</p>
                <p>Try re-processing the document or check the original file for content.</p>
            </div>
            """
        
        # Clean title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"Lab_{safe_title[:40]}.pdf"  # Limit filename length
        
        # Generate PDF
        print(f"🎨 Starting PDF generation with {len(content)} characters of content")
        pdf_bytes = generate_pdf_from_html(content, title)
        
        # Validate PDF was actually generated
        if not pdf_bytes or len(pdf_bytes) < 1000:
            print(f"❌ Generated PDF is too small: {len(pdf_bytes) if pdf_bytes else 0} bytes")
            raise HTTPException(status_code=500, detail="PDF generation produced invalid output")
        
        print(f"✅ PDF generated successfully: {len(pdf_bytes)} bytes")
        
        # Create PDF stream response
        def generate():
            yield pdf_bytes
        
        # Return streaming response with proper headers
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'application/pdf',
            'Content-Length': str(len(pdf_bytes))
        }
        
        return StreamingResponse(
            generate(),
            media_type='application/pdf',
            headers=headers
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions (like 404) without modification
        raise
    except Exception as e:
        print(f"❌ Training PDF download error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return await process_text_with_template(content, template_data, training_session)
            except:
                return []
        
        # Try to process as actual PDF file
        try:
            # Open PDF with PyMuPDF for comprehensive extraction
            doc = fitz.open(file_path)
            print(f"✅ Successfully loaded PDF file with {len(doc)} pages")
        except Exception as pdf_error:
            print(f"⚠️ Failed to load as PDF file: {pdf_error}")
            print(f"🔄 Falling back to text processing")
            # If it's not a valid PDF file, treat it as text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return await process_text_with_template(content, template_data, training_session)
            except Exception as text_error:
                print(f"❌ Text fallback also failed: {text_error}")
                return []
        
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
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return await process_text_with_template(content, template_data, training_session)
            except:
                return []
        
        # Try to process as actual PowerPoint file
        try:
            prs = Presentation(file_path)
            print(f"✅ Successfully loaded PowerPoint file with {len(prs.slides)} slides")
        except Exception as ppt_error:
            print(f"⚠️ Failed to load as PowerPoint file: {ppt_error}")
            print(f"🔄 Falling back to text processing")
            # If it's not a valid PowerPoint file, treat it as text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return await process_text_with_template(content, template_data, training_session)
            except Exception as text_error:
                print(f"❌ Text fallback also failed: {text_error}")
                return []
        
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

async def create_recovery_articles(content: str, images: list, template_data: dict, training_session: dict) -> list:
    """Recovery function for enhanced processing failures - creates simplified articles"""
    try:
        print(f"🔧 Recovery processing: {len(content)} chars, {len(images)} images")
        
        # Create a single simplified article with all content
        article_id = str(uuid.uuid4())
        
        # Basic HTML structure
        html_content = f"<h1>Document Content from {training_session.get('filename', 'Document')}</h1>\n"
        html_content += content
        
        # Add images at the end
        for i, img in enumerate(images):
            html_content += f'\n<figure class="embedded-image">'
            html_content += f'<img src="{img["url"]}" alt="{img["alt_text"]}" style="max-width: 100%; height: auto; margin: 1rem 0;">'
            html_content += f'<figcaption>{img.get("caption", f"Figure {i + 1}")}</figcaption>'
            html_content += f'</figure>\n'
        
        # Create media array
        media_array = []
        for img in images:
            media_array.append({
                "url": img['url'],
                "alt": img['alt_text'],
                "caption": img.get('caption', ''),
                "placement": img.get('placement', 'inline'),
                "filename": img['filename']
            })
        
        article = {
            "id": article_id,
            "title": f"Recovery Article from {training_session['filename']}",
            "html": html_content,
            "markdown": html_content.replace('<h1>', '# ').replace('</h1>', '').replace('<p>', '').replace('</p>', '\n'),
            "content": html_content,
            "media": media_array,
            "tags": ["extracted", "recovery", "simplified"],
            "status": "training",
            "template_id": training_session['template_id'],
            "session_id": training_session['session_id'],
            "word_count": len(html_content.split()),
            "image_count": len(media_array),
            "format": "html",
            "created_at": datetime.utcnow().isoformat(),
            "ai_processed": False,
            "ai_model": "recovery_mode",
            "training_mode": True,
            "metadata": {
                "article_number": 1,
                "source_filename": training_session['filename'],
                "template_applied": training_session['template_id'],
                "phase": "recovery_processing"
            }
        }
        
        print(f"✅ Recovery article created: {len(html_content)} chars, {len(media_array)} images")
        return [article]
        
    except Exception as e:
        print(f"❌ Recovery processing also failed: {e}")
        return []

async def create_recovery_articles(content: str, images: list, template_data: dict, training_session: dict) -> list:
    """Recovery function for enhanced processing failures - creates simplified articles"""
    try:
        print(f"🔧 Recovery processing: {len(content)} chars, {len(images)} images")
        
        # Create a single simplified article with all content
        article_id = str(uuid.uuid4())
        
        # Basic HTML structure
        html_content = f"<h1>Document Content from {training_session.get('filename', 'Document')}</h1>\n"
        html_content += content
        
        # Add images at the end
        for i, img in enumerate(images):
            html_content += f'\n<figure class="embedded-image">'
            html_content += f'<img src="{img["url"]}" alt="{img["alt_text"]}" style="max-width: 100%; height: auto; margin: 1rem 0;">'
            html_content += f'<figcaption>{img.get("caption", f"Figure {i + 1}")}</figcaption>'
            html_content += f'</figure>\n'
        
        # Create media array
        media_array = []
        for img in images:
            media_array.append({
                "url": img['url'],
                "alt": img['alt_text'],
                "caption": img.get('caption', ''),
                "placement": img.get('placement', 'inline'),
                "filename": img['filename']
            })
        
        article = {
            "id": article_id,
            "title": f"Recovery Article from {training_session['filename']}",
            "html": html_content,
            "markdown": html_content.replace('<h1>', '# ').replace('</h1>', '').replace('<p>', '').replace('</p>', '\n'),
            "content": html_content,
            "media": media_array,
            "tags": ["extracted", "recovery", "simplified"],
            "status": "training",
            "template_id": training_session['template_id'],
            "session_id": training_session['session_id'],
            "word_count": len(html_content.split()),
            "image_count": len(media_array),
            "format": "html",
            "created_at": datetime.utcnow().isoformat(),
            "ai_processed": False,
            "ai_model": "recovery_mode",
            "training_mode": True,
            "metadata": {
                "article_number": 1,
                "source_filename": training_session['filename'],
                "template_applied": training_session['template_id'],
                "phase": "recovery_processing"
            }
        }
        
        print(f"✅ Recovery article created: {len(html_content)} chars, {len(media_array)} images")
        return [article]
        
    except Exception as e:
        print(f"❌ Recovery processing also failed: {e}")
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
            
            # CRITICAL FIX: Prevent multiple H1 tags in single article
            # First try splitting on major headings
            if '<h1>' in content:
                sections = content.split('<h1>')
                for i, section in enumerate(sections):
                    if section.strip():
                        if i == 0:
                            # First section without H1 prefix
                            natural_sections.append(section)
                        else:
                            # Convert H1 to H2 for subsequent sections to avoid multiple H1s
                            section = '<h2>' + section.replace('</h1>', '</h2>', 1)
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
        
        # Enhanced image distribution with contextual matching
        section_images = distribute_images_contextually(natural_sections, images)
        
        # Create articles from natural sections with enhanced processing
        for i, section in enumerate(natural_sections):
            if section.strip():
                assigned_images = section_images[i] if i < len(section_images) else []
                
                print(f"📄 Creating comprehensive article {i+1} with {len(assigned_images)} images")
                
                article = await create_single_article_with_template(
                    section, 
                    assigned_images,
                    template_data, 
                    training_session,
                    i + 1,
                    len(natural_sections)
                )
                
                if article:
                    articles.append(article)
        
        print(f"✅ Created {len(articles)} comprehensive articles from {content_length} chars and {image_count} images")
        return articles
        
    except Exception as e:
        print(f"❌ Enhanced article creation error: {e}")
        import traceback
        traceback.print_exc()
        return []

def analyze_document_structure(content: str) -> list:
    """
    Analyze document structure to determine natural breaking points
    """
    sections = []
    
    # Enhanced structure detection
    if '<h1>' in content or '<h2>' in content:
        # Split on major headings with intelligent merging
        if '<h1>' in content:
            sections = intelligent_split_on_headings(content, 'h1')
        else:
            sections = intelligent_split_on_headings(content, 'h2')
    elif content.count('\n\n') > 10:
        # Handle paragraph-based documents
        sections = intelligent_paragraph_grouping(content)
    else:
        # Single comprehensive section for shorter documents
        sections = [content]
    
    # Filter and validate sections
    validated_sections = []
    for section in sections:
        if len(section.strip()) > 200:  # Minimum meaningful content
            validated_sections.append(section.strip())
        elif validated_sections:
            # Merge small sections with previous one
            validated_sections[-1] += "\n\n" + section.strip()
    
    return validated_sections if validated_sections else [content]

def intelligent_split_on_headings(content: str, heading_tag: str) -> list:
    """
    Intelligently split content on headings while preserving context
    """
    import re
    
    # Pattern to match heading tags
    pattern = f'<{heading_tag}[^>]*>(.*?)</{heading_tag}>'
    headings = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
    
    if not headings:
        return [content]
    
    # Split and reconstruct sections
    sections = []
    parts = re.split(f'<{heading_tag}[^>]*>.*?</{heading_tag}>', content, flags=re.IGNORECASE | re.DOTALL)
    heading_matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
    
    # Reconstruct sections with their headings
    for i, match in enumerate(heading_matches):
        section_content = match.group(0)  # Include the heading
        if i + 1 < len(parts):
            section_content += parts[i + 1]  # Add content after heading
        
        if section_content.strip():
            sections.append(section_content.strip())
    
    return sections if sections else [content]

def intelligent_paragraph_grouping(content: str) -> list:
    """
    Group paragraphs intelligently to form coherent sections
    """
    paragraphs = content.split('\n\n')
    sections = []
    current_section = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Check if this paragraph starts a new logical section
        if is_section_boundary(paragraph, current_section):
            if current_section.strip():
                sections.append(current_section.strip())
            current_section = paragraph
        else:
            current_section += "\n\n" + paragraph if current_section else paragraph
        
        # Ensure sections don't get too long (but allow substantial content)
        if len(current_section) > 15000:  # Increased from 8000
            sections.append(current_section.strip())
            current_section = ""
    
    if current_section.strip():
        sections.append(current_section.strip())
    
    return sections

def is_section_boundary(paragraph: str, current_section: str) -> bool:
    """
    Determine if a paragraph represents a natural section boundary
    """
    # Check for topic transition indicators
    transition_indicators = [
        'next step', 'following section', 'in addition', 'furthermore',
        'alternatively', 'however', 'on the other hand', 'similarly',
        'step ', 'phase ', 'part ', 'section ', 'chapter '
    ]
    
    paragraph_lower = paragraph.lower()
    
    # Strong indicators of new section
    if any(indicator in paragraph_lower for indicator in transition_indicators):
        return True
    
    # Check if starting a numbered list or procedure
    if re.match(r'^\d+\.', paragraph.strip()):
        return len(current_section) > 1000  # Only if current section has substance
    
    return False

def distribute_images_contextually(sections: list, images: list) -> list:
    """
    Distribute images across sections based on contextual relevance
    """
    if not images:
        return [[] for _ in sections]
    
    section_images = [[] for _ in sections]
    
    for image in images:
        best_section_idx = find_best_section_for_image(image, sections)
        if best_section_idx is not None:
            section_images[best_section_idx].append(image)
        else:
            # Distribute evenly if no clear match
            min_images_idx = min(range(len(section_images)), key=lambda i: len(section_images[i]))
            section_images[min_images_idx].append(image)
    
    return section_images

def find_best_section_for_image(image: dict, sections: list) -> int:
    """
    Find the best section for an image based on contextual matching
    """
    image_chapter = image.get('chapter', '').lower()
    image_context = image.get('context_text', '').lower()
    
    best_score = 0
    best_section = None
    
    for i, section in enumerate(sections):
        section_lower = section.lower()
        score = 0
        
        # Match based on chapter name
        if image_chapter and image_chapter in section_lower:
            score += 50
        
        # Match based on context keywords
        context_words = image_context.split()[:10]  # First 10 words of context
        for word in context_words:
            if len(word) > 3 and word in section_lower:
                score += 5
        
        # Prefer sections with visual references
        if any(keyword in section_lower for keyword in ['figure', 'diagram', 'image', 'shows', 'illustrates']):
            score += 20
        
        if score > best_score:
            best_score = score
            best_section = i
    
    return best_section if best_score > 10 else None

async def create_single_article_with_template(content: str, images: list, template_data: dict, training_session: dict, article_number: int, total_articles: int = 1) -> dict:
    """Create a single comprehensive article with enhanced structure and quality using segmented generation"""
    try:
        print(f"🔍 Creating comprehensive article {article_number}/{total_articles} with {len(images)} images")
        
        # Generate intelligent title based on content, not filename
        title = generate_contextual_title(content, article_number, training_session)
        
        # CRITICAL FIX: Use segmented generation for comprehensive coverage - OPTIMIZED
        if len(content) > 5000:  # Increased threshold from 2000 to 5000 chars
            print("📝 Using segmented generation for comprehensive coverage")
            final_content = await generate_comprehensive_article_segmented(content, images, template_data, title)
        else:
            print("📝 Using single-pass generation for shorter content")
            final_content = await generate_single_pass_article(content, images, template_data, title)
        
        if not final_content:
            print("⚠️ No AI content generated, creating enhanced fallback")
            final_content = create_structured_fallback_content(content, images, title)
        
        # Post-process the AI content for quality assurance
        final_content = enhance_content_quality(final_content, images)
        
        # Extract or generate final title from content
        final_title = extract_content_title(final_content) or title
        
        # Create comprehensive article with enhanced metadata
        article = {
            "id": str(uuid.uuid4()),
            "title": final_title,
            "content": final_content,
            "word_count": len(final_content.split()),
            "image_count": len(images),
            "status": "training",
            "template_id": template_data.get("template_id", "enhanced_processing"),
            "session_id": training_session.get("session_id"),
            "training_mode": True,
            "ai_processed": True,
            "ai_model": "enhanced_knowledge_engine",
            "has_images": len(images) > 0,
            "has_structure": check_content_structure(final_content),
            "processing_metadata": {
                "article_number": article_number,
                "total_articles": total_articles,
                "original_length": len(content),
                "enhanced_length": len(final_content),
                "images_embedded": count_embedded_images(final_content),
                "generation_method": "segmented" if len(content) > 2000 else "single_pass"
            }
        }
        
        print(f"✅ Comprehensive article created: '{final_title}' ({article['word_count']} words)")
        return article
        
    except Exception as e:
        print(f"❌ Enhanced article creation error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def generate_comprehensive_article_segmented(content: str, images: list, template_data: dict, title: str) -> str:
    """Generate comprehensive article using segmented approach for full coverage"""
    try:
        print("🔄 Starting segmented generation for comprehensive coverage")
        
        # Step 1: Generate article outline and structure
        outline = await generate_article_outline(content, title, template_data)
        if not outline:
            print("⚠️ Could not generate outline, falling back to single-pass")
            return await generate_single_pass_article(content, images, template_data, title)
        
        print(f"📋 Generated article outline with sections")
        
        # Step 2: Split content into logical segments based on outline
        content_segments = split_content_into_segments(content, outline)
        print(f"📄 Split content into {len(content_segments)} segments")
        
        # Step 3: Distribute images across segments
        segment_images = distribute_images_to_segments(images, content_segments)
        
        # Step 4: Generate each segment comprehensively
        generated_sections = []
        generated_sections.append(f"<h1>{title}</h1>\n")
        
        for i, (segment, segment_imgs) in enumerate(zip(content_segments, segment_images)):
            print(f"🔄 Generating comprehensive section {i+1}/{len(content_segments)}")
            
            section_content = await generate_content_segment(
                segment, 
                segment_imgs, 
                template_data, 
                i + 1, 
                len(content_segments),
                outline
            )
            
            if section_content:
                generated_sections.append(section_content)
            else:
                print(f"⚠️ Failed to generate section {i+1}, using fallback")
                generated_sections.append(create_fallback_segment(segment, segment_imgs))
        
        # Step 5: Combine all sections
        final_content = "\n\n".join(generated_sections)
        
        print(f"✅ Segmented generation completed: {len(final_content.split())} words")
        return final_content
        
    except Exception as e:
        print(f"❌ Segmented generation error: {e}")
        return await generate_single_pass_article(content, images, template_data, title)

async def generate_article_outline(content: str, title: str, template_data: dict) -> dict:
    """Generate a structured outline for the article"""
    try:
        system_message = """You are an expert content strategist creating comprehensive article outlines.

Generate a detailed outline for a comprehensive knowledge base article. Return ONLY a JSON structure with no additional text.

Required JSON format:
{
    "title": "Article Title",
    "sections": [
        {
            "heading": "Section Title",
            "level": 2,
            "key_points": ["point 1", "point 2", "point 3"],
            "estimated_words": 500
        }
    ],
    "total_estimated_words": 2500
}

Create 2-3 major sections with detailed key points. Aim for balanced coverage with 1500-2500 total words."""

        user_message = f"""Create a comprehensive outline for this content:

TITLE: {title}

CONTENT TO OUTLINE:
{content[:2000]}...

Create a detailed outline with major sections, key points, and estimated word counts for comprehensive coverage."""

        outline_response = await call_llm_with_fallback(system_message, user_message)
        
        if outline_response:
            import json
            try:
                outline_data = json.loads(outline_response)
                if "sections" in outline_data and len(outline_data["sections"]) > 0:
                    return outline_data
            except json.JSONDecodeError:
                print("⚠️ Could not parse outline JSON")
        
        return None
        
    except Exception as e:
        print(f"❌ Outline generation error: {e}")
        return None

def split_content_into_segments(content: str, outline: dict) -> list:
    """Split content into segments based on outline structure"""
    if not outline or "sections" not in outline:
        # Fallback: split into 2 balanced segments for faster processing
        words = content.split()
        segments_count = 2  # Reduced from 4 to 2 segments
        segment_size = max(200, len(words) // segments_count)  # At least 200 words per segment
        
        segments = []
        for i in range(0, len(words), segment_size):
            segment_words = words[i:i + segment_size]
            if segment_words:  # Only add non-empty segments
                segments.append(" ".join(segment_words))
        
        return segments
    
    # Try to split based on outline sections - OPTIMIZED to 2 segments
    sections = outline["sections"]
    # Limit to maximum 2 segments for faster processing
    target_segments = min(2, len(sections))  # Reduced from 4-6 to 2 segments
    total_words = len(content.split())
    words_per_section = total_words // target_segments
    
    segments = []
    words = content.split()
    
    for i in range(target_segments):
        start_idx = i * words_per_section
        end_idx = min((i + 1) * words_per_section, len(words)) if i < target_segments - 1 else len(words)
        
        segment_words = words[start_idx:end_idx]
        if segment_words:
            segments.append(" ".join(segment_words))
    
    return segments

def distribute_images_to_segments(images: list, segments: list) -> list:
    """Distribute images across content segments"""
    if not images:
        return [[] for _ in segments]
    
    # Distribute images roughly evenly across segments
    segment_images = [[] for _ in segments]
    
    for i, image in enumerate(images):
        segment_idx = i % len(segments)
        segment_images[segment_idx].append(image)
    
    return segment_images

async def generate_content_segment(segment_content: str, segment_images: list, template_data: dict, segment_num: int, total_segments: int, outline: dict) -> str:
    """Generate a comprehensive content segment"""
    try:
        section_info = ""
        if outline and "sections" in outline and segment_num <= len(outline["sections"]):
            section_data = outline["sections"][segment_num - 1]
            section_info = f"""
SECTION FOCUS: {section_data.get('heading', f'Section {segment_num}')}
KEY POINTS TO COVER: {', '.join(section_data.get('key_points', []))}
TARGET LENGTH: {section_data.get('estimated_words', 600)} words"""

        system_message = f"""You are an expert technical writer creating comprehensive section content.

CRITICAL REQUIREMENTS:
1. Generate detailed, comprehensive content for this section
2. Write 400-800 words for thorough coverage - BALANCED LENGTH
3. Use professional technical documentation style with good detail
4. Include detailed explanations, comprehensive step-by-step procedures, and thorough information
5. Use proper HTML structure: <h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong>, <em>
6. Embed provided images with proper figure elements
7. NO meta-commentary - only detailed article content
8. NO truncation or summarization - provide COMPLETE detailed content
9. Focus on quality over quantity - comprehensive but concise

{section_info}

QUALITY STANDARDS:
- Comprehensive, detailed explanations with good depth
- Professional enterprise technical writing with thorough coverage
- Complete step-by-step procedures with detailed instructions
- Thorough coverage of all aspects with focused information
- Proper HTML semantic structure with rich formatting
- Target 400-800 words - comprehensive yet efficient content"""

        user_message = f"""Create comprehensive content for section {segment_num} of {total_segments}:

CONTENT TO EXPAND:
{segment_content}

AVAILABLE IMAGES: {len(segment_images)}
{format_available_images(segment_images)}

CRITICAL REQUIREMENTS:
- Write 400-800 words for comprehensive coverage - BALANCED LENGTH
- Include detailed explanations and complete comprehensive procedures
- Use proper HTML structure with headings and rich formatting
- Embed images contextually with provided HTML code
- Focus on thorough, professional technical documentation with good detail
- NO truncation or summarization - provide complete detailed comprehensive content
- Balance depth with efficiency - comprehensive but focused content
- Provide complete step-by-step instructions where applicable
- Include thorough background information and context

Generate comprehensive section content with good detail, proper HTML structure, and target 400-800 words."""

        segment_response = await call_llm_with_fallback(system_message, user_message)
        
        if segment_response:
            return segment_response.strip()
        
        return None
        
    except Exception as e:
        print(f"❌ Segment generation error: {e}")
        return None

def generate_contextual_title(content: str, article_number: int, training_session: dict) -> str:
    """Generate intelligent title based on content analysis"""
    import re
    
    # Extract from existing headings first
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    if h1_match:
        title_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        if 5 < len(title_text) < 100:
            return title_text
    
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.IGNORECASE | re.DOTALL)
    if h2_match:
        title_text = re.sub(r'<[^>]+>', '', h2_match.group(1)).strip()
        if 5 < len(title_text) < 100:
            return title_text
    
    # Analyze content for key topics
    clean_content = re.sub(r'<[^>]+>', '', content)
    words = clean_content.split()[:100]  # First 100 words
    
    # Look for topic keywords
    topic_keywords = ['guide', 'process', 'procedure', 'step', 'method', 'system', 'overview', 'management']
    found_topics = []
    
    for i, word in enumerate(words):
        if word.lower() in topic_keywords and i > 0:
            # Get context around the keyword
            start_idx = max(0, i-3)
            end_idx = min(len(words), i+4)
            context = ' '.join(words[start_idx:end_idx])
            found_topics.append(context)
    
    if found_topics:
        # Use the first relevant topic
        topic = found_topics[0]
        topic = re.sub(r'[^\w\s]', '', topic).strip()
        if len(topic) > 10:
            return topic.title()
    
    # Fallback to source-based naming
    source_name = training_session.get('filename', 'Document').replace('.docx', '').replace('.pdf', '')
    source_name = source_name.replace('_', ' ').replace('-', ' ')
    
    if article_number == 1:
        return f"Understanding {source_name}"
    else:
        return f"{source_name} - Section {article_number}"

def format_available_images(images: list) -> str:
    """Format available images for LLM reference with URLs for embedding"""
    if not images:
        return "No images available - focus on comprehensive text content"
    
    image_refs = []
    for i, img in enumerate(images, 1):
        chapter = img.get('chapter', 'Document')
        filename = img.get('filename', f'image{i}')
        caption = img.get('caption', f'Figure {i}')
        url = img.get('url', '')
        alt_text = img.get('alt_text', f'Figure {i}')
        
        image_refs.append(f"""IMAGE_{i}: 
- Filename: {filename}
- URL: {url}
- Caption: {caption}
- Alt Text: {alt_text}
- Chapter: {chapter}
- HTML to embed: <figure class="embedded-image"><img src="{url}" alt="{alt_text}" style="max-width: 100%; height: auto;"><figcaption>{caption}</figcaption></figure>""")
    
    return "\n\n".join(image_refs)

def create_structured_fallback_content(content: str, images: list, title: str) -> str:
    """Create structured fallback when AI is unavailable"""
    html = f"<h1>{title}</h1>\n\n"
    
    # Process content into structured HTML
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Detect if paragraph looks like a heading
        if len(para) < 80 and (para.isupper() or para.endswith(':') or para.count(' ') < 8):
            html += f"<h2>{para.rstrip(':')}</h2>\n\n"
        elif para.startswith('•') or para.startswith('-'):
            # Convert to list
            html += f"<ul>\n<li>{para[1:].strip()}</li>\n</ul>\n\n"
        else:
            html += f"<p>{para}</p>\n\n"
    
    # Add images if available
    if images:
        html += "<h2>Related Figures</h2>\n\n"
        for img in images[:2]:  # Limit for fallback
            html += f"""<figure class="embedded-image">
<img src="{img.get('url', '')}" alt="{img.get('alt_text', 'Figure')}" style="max-width: 100%; height: auto;">
<figcaption>{img.get('caption', 'Figure')}</figcaption>
</figure>\n\n"""
    
    return html

def enhance_content_quality(content: str, images: list) -> str:
    """Post-process content for quality and image integration"""
    if not content:
        return content
    
    # CRITICAL FIX: Remove HTML document wrappers that may come from LLM
    content = clean_html_wrappers(content)
    
    # Add missing images if AI didn't embed them
    if images and not any(img.get('url', '') in content for img in images):
        content = add_missing_images(content, images)
    
    # Clean HTML formatting
    import re
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Remove excessive newlines
    content = re.sub(r'</p>\s*<p>', '</p>\n\n<p>', content)  # Proper paragraph spacing
    
    return content.strip()

def clean_html_wrappers(content: str) -> str:
    """Remove HTML document wrappers and extract only body content"""
    import re
    
    # Remove HTML document structure wrappers
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<html[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<head>.*?</head>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<body[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</body>', '', content, flags=re.IGNORECASE)
    
    # CRITICAL FIX: Remove code blocks that contain HTML titles
    content = re.sub(r'```html\s*.*?```', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'```javascript\s*.*?```', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'```\s*.*?```', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # CRITICAL FIX: Remove duplicate h1 tags that repeat the title
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, flags=re.IGNORECASE | re.DOTALL)
    if len(h1_matches) > 1:
        # Keep only the first h1, remove the rest
        first_h1_found = False
        def replace_h1(match):
            nonlocal first_h1_found
            if not first_h1_found:
                first_h1_found = True
                return match.group(0)  # Keep the first one
            else:
                # Convert subsequent h1s to h2s
                inner_text = match.group(1)
                return f'<h2>{inner_text}</h2>'
        
        content = re.sub(r'<h1[^>]*>(.*?)</h1>', replace_h1, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove any remaining div wrappers that might have been added
    content = re.sub(r'^<div[^>]*>(.*)</div>$', r'\1', content.strip(), flags=re.IGNORECASE | re.DOTALL)
    
    # Ensure we still have content
    if not content.strip():
        return content
    
    # Ensure content starts with proper HTML tags (but not document structure)
    content = content.strip()
    if content and not content.startswith('<'):
        # Only wrap in paragraph if it's plain text
        if '\n' not in content[:100]:  # Single line text
            content = f"<p>{content}</p>"
        else:
            # Multi-line content, process paragraphs
            paragraphs = content.split('\n\n')
            html_parts = []
            for para in paragraphs:
                para = para.strip()
                if para:
                    html_parts.append(f"<p>{para}</p>")
            content = '\n\n'.join(html_parts)
    
    return content

def add_missing_images(content: str, images: list) -> str:
    """Add missing images at appropriate locations"""
    import re
    
    # Find insertion points after headings
    h2_positions = [m.end() for m in re.finditer(r'</h2>', content, re.IGNORECASE)]
    
    if not h2_positions:
        # Fall back to paragraph positions
        h2_positions = [m.end() for m in re.finditer(r'</p>', content, re.IGNORECASE)][:2]
    
    # Insert images at found positions
    offset = 0
    images_to_add = images[:min(len(h2_positions), 2)]  # Limit insertions
    
    for i, image in enumerate(images_to_add):
        if i < len(h2_positions):
            insert_pos = h2_positions[i] + offset
            
            img_html = f"""
<figure class="embedded-image">
<img src="{image.get('url', '')}" alt="{image.get('alt_text', 'Figure')}" style="max-width: 100%; height: auto;">
<figcaption>{image.get('caption', 'Figure')}</figcaption>
</figure>
"""
            content = content[:insert_pos] + img_html + content[insert_pos:]
            offset += len(img_html)
    
    return content

def extract_content_title(content: str) -> str:
    """Extract title from generated content"""
    import re
    
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    if h1_match:
        title_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        if 5 < len(title_text) < 120:
            return title_text
    return None

def check_content_structure(content: str) -> bool:
    """Check if content has proper structure"""
    import re
    has_headings = bool(re.search(r'<h[1-6][^>]*>', content, re.IGNORECASE))
    has_lists = bool(re.search(r'<[uo]l[^>]*>', content, re.IGNORECASE))
    return has_headings or has_lists

def count_embedded_images(content: str) -> int:
    """Count embedded images in content"""
    import re
    return len(re.findall(r'<img[^>]*>', content, re.IGNORECASE))

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
                ai_model = "gpt-4o-mini (with claude + local llm fallback)" if OPENAI_API_KEY else "claude-3-5-sonnet (with local llm fallback)"
                
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
            ai_model = "gpt-4o-mini (with claude + local llm fallback)" if OPENAI_API_KEY else "claude-3-5-sonnet (with local llm fallback)"
            
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

def get_heading_level(paragraph) -> int:
    """
    Determine the heading level of a paragraph
    """
    try:
        style_name = paragraph.style.name.lower()
        if 'heading 1' in style_name or 'title' in style_name:
            return 1
        elif 'heading 2' in style_name:
            return 2
        elif 'heading 3' in style_name:
            return 3
        elif 'heading 4' in style_name:
            return 4
        elif 'heading' in style_name:
            return 2  # Default for generic heading
        
        # Check for manual formatting that indicates headings
        if paragraph.runs:
            first_run = paragraph.runs[0]
            if first_run.bold and first_run.font.size and first_run.font.size.pt > 14:
                return 1
            elif first_run.bold and first_run.font.size and first_run.font.size.pt > 12:
                return 2
            elif first_run.bold:
                return 3
                
        return None
    except:
        return None

def clean_heading_text(text: str) -> str:
    """
    Clean heading text for better chapter naming
    """
    import re
    # Remove numbering, extra spaces, and special characters
    cleaned = re.sub(r'^\d+\.?\s*', '', text)  # Remove leading numbers
    cleaned = re.sub(r'[^\w\s-]', '', cleaned)  # Keep only alphanumeric, spaces, hyphens
    cleaned = ' '.join(cleaned.split())  # Normalize whitespace
    return cleaned.strip()

def detect_content_type(text: str) -> str:
    """
    Detect the type of content based on text patterns
    """
    text_lower = text.lower()
    
    if any(keyword in text_lower for keyword in ['figure', 'diagram', 'chart', 'table', 'image']):
        return 'visual_reference'
    elif any(keyword in text_lower for keyword in ['step', 'procedure', 'process', 'instruction']):
        return 'instructional'
    elif any(keyword in text_lower for keyword in ['note:', 'warning:', 'tip:', 'important:']):
        return 'callout'
    elif text.endswith(':') and len(text.split()) < 10:
        return 'list_header'
    else:
        return 'body_text'

def extract_enhanced_image_positions_from_xml(doc_tree, paragraph_contexts) -> list:
    """
    Enhanced XML parsing to find precise image positions with better context mapping
    """
    positions = []
    
    try:
        print(f"🔍 DEBUG: Starting XML position extraction")
        
        # Find all drawing elements (images) in the document
        drawings = doc_tree.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing')
        print(f"🔍 DEBUG: Found {len(drawings)} drawing elements in XML")
        
        for i, drawing in enumerate(drawings):
            print(f"🔍 DEBUG: Processing drawing {i+1}/{len(drawings)}")
            
            # CRITICAL FIX: Find the containing paragraph using multiple traversal methods
            paragraph_element = None
            
            # Method 1: XPath to find parent paragraph
            try:
                parent_paragraphs = drawing.xpath('./ancestor::*[local-name()="p"]')
                if parent_paragraphs:
                    paragraph_element = parent_paragraphs[-1]  # Get the closest paragraph parent
                    print(f"✅ DEBUG: Found paragraph via XPath for drawing {i+1}")
                else:
                    print(f"⚠️ DEBUG: No paragraph parent found via XPath for drawing {i+1}")
            except Exception as xpath_error:
                print(f"⚠️ DEBUG: XPath method failed for drawing {i+1}: {xpath_error}")
            
            # Method 2: Use iterancestors() if XPath fails
            if paragraph_element is None:
                try:
                    for ancestor in drawing.iterancestors():
                        if ancestor.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p':
                            paragraph_element = ancestor
                            print(f"✅ DEBUG: Found paragraph via iterancestors for drawing {i+1}")
                            break
                except Exception as ancestor_error:
                    print(f"⚠️ DEBUG: iterancestors method failed for drawing {i+1}: {ancestor_error}")
            
            # Method 3: Manual traversal using getparent() if available
            if paragraph_element is None:
                try:
                    current = drawing
                    while current is not None and hasattr(current, 'getparent'):
                        if current.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p':
                            paragraph_element = current
                            print(f"✅ DEBUG: Found paragraph via manual traversal for drawing {i+1}")
                            break
                        current = current.getparent()
                except Exception as manual_error:
                    print(f"⚠️ DEBUG: Manual traversal failed for drawing {i+1}: {manual_error}")
            
            if paragraph_element is not None:
                # Find paragraph index
                all_paragraphs = doc_tree.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
                try:
                    para_index = list(all_paragraphs).index(paragraph_element)
                    print(f"🔍 DEBUG: Drawing {i+1} found in paragraph {para_index}")
                    
                    if para_index < len(paragraph_contexts):
                        context = paragraph_contexts[para_index]
                        
                        # Enhanced position data
                        position_data = {
                            'paragraph_index': para_index,
                            'chapter': context['chapter'],
                            'page': context['page_estimate'],
                            'paragraph_text': context['text'],
                            'position_in_chapter': context.get('position_in_chapter', 0),
                            'content_type': context.get('content_type', 'body_text'),
                            'word_count': context.get('word_count', 0),
                            'is_heading': context.get('is_heading', False),
                            'position': 'inline',  # Add missing position field
                            'type': 'illustration'  # Add missing type field
                        }
                        
                        positions.append(position_data)
                        print(f"✅ DEBUG: Added position for drawing {i+1}: chapter={context['chapter']}, page={context['page_estimate']}")
                        
                except (ValueError, IndexError) as e:
                    print(f"⚠️ DEBUG: Error processing drawing {i+1}: {e}")
                    continue
            else:
                print(f"⚠️ DEBUG: Could not find paragraph for drawing {i+1}")
        
        print(f"📍 DEBUG: Final result - Found {len(positions)} image positions in document")
        return positions
        
    except Exception as e:
        print(f"❌ DEBUG: Error in enhanced XML parsing: {e}")
        import traceback
        traceback.print_exc()
        return []

def find_enhanced_image_context(filename: str, image_positions: list, paragraph_contexts: list) -> dict:
    """
    Find the most relevant context for an image with enhanced matching
    """
    print(f"🔍 DEBUG: Finding context for {filename}")
    print(f"🔍 DEBUG: Available image positions: {len(image_positions)}")
    print(f"🔍 DEBUG: Available paragraph contexts: {len(paragraph_contexts)}")
    
    if not image_positions:
        print(f"⚠️ DEBUG: No image positions available for {filename}")
        return None
    
    # Try to match based on proximity and content relevance
    best_context = None
    best_score = 0
    
    for i, position in enumerate(image_positions):
        print(f"🔍 DEBUG: Evaluating position {i+1}: {position}")
        score = 0
        
        # Score based on content type relevance
        if position.get('content_type') == 'visual_reference':
            score += 10
        elif position.get('content_type') == 'instructional':
            score += 8
        elif position.get('content_type') == 'body_text':
            score += 5
        
        # Score based on paragraph text length (more context is better)
        text_length = len(position.get('paragraph_text', ''))
        if text_length > 100:
            score += 5
        elif text_length > 50:
            score += 3
        
        # Avoid headings as image contexts unless they specifically reference visuals
        if position.get('is_heading', False):
            paragraph_text = position.get('paragraph_text', '').lower()
            if any(keyword in paragraph_text for keyword in ['figure', 'diagram', 'chart', 'image']):
                score += 3
            else:
                score -= 5
        
        # Prefer images not in the first page (likely cover content)
        if position.get('page', 0) > 1:
            score += 3
        
        print(f"🔍 DEBUG: Position {i+1} scored {score}")
        
        if score > best_score:
            best_score = score
            best_context = position
    
    print(f"🔍 DEBUG: Best context for {filename}: score={best_score}, context={best_context is not None}")
    return best_context

def create_fallback_image_context(filename: str, image_number: int, paragraph_contexts: list) -> dict:
    """
    Create a fallback context for images when enhanced context detection fails
    """
    try:
        # Find a good paragraph with reasonable chapter name
        fallback_paragraph = None
        for para in paragraph_contexts:
            # CRITICAL FIX: Skip paragraphs with excessively long chapter names
            chapter = para.get('chapter', 'Document Content')
            if len(chapter) > 100:
                continue  # Skip paragraphs with overly long chapter names
            
            # Prefer paragraphs with substantial text
            if len(para.get('text', '')) > 50 and not para.get('is_heading', False):
                fallback_paragraph = para
                break
                
        # If we found a good paragraph, use it
        if fallback_paragraph:
            chapter = fallback_paragraph.get('chapter', 'Document Content')
            # Further limit chapter names
            if len(chapter) > 80:
                chapter = chapter[:80] + "..."
                
            return {
                'page': fallback_paragraph.get('page_estimate', 1),
                'position': 'inline',
                'chapter': chapter,
                'type': 'illustration',
                'paragraph_text': f'Figure {image_number}: {filename.replace(".png", "").replace(".jpg", "").replace(".jpeg", "")} - Contextual illustration for {chapter}',
                'content_type': 'body_text',
                'is_heading': False,
                'paragraph_index': fallback_paragraph.get('index', 0),
                'position_in_chapter': image_number
            }

        # Continue with existing logic for remaining cases
        for para in paragraph_contexts:
            if (len(para.get('text', '').strip()) > 50 and 
                not para.get('is_heading', False) and
                para.get('page_estimate', 1) > 1):  # Skip cover page
                fallback_paragraph = para
                break
        
        # If no good paragraph found, use a generic one
        if not fallback_paragraph and paragraph_contexts:
            fallback_paragraph = paragraph_contexts[min(5, len(paragraph_contexts) - 1)]
        
        if not fallback_paragraph:
            # Last resort: create minimal context
            return {
                'page': 1,
                'position': 'inline',
                'chapter': 'Document Content',
                'type': 'illustration',
                'paragraph_text': f'Image {image_number} from document',
                'content_type': 'body_text',
                'is_heading': False,
                'paragraph_index': 0,
                'position_in_chapter': image_number
            }
        
        return {
            'page': fallback_paragraph.get('page_estimate', 1),
            'position': 'inline',
            'chapter': fallback_paragraph.get('chapter', 'Document Content'),
            'type': 'illustration',
            'paragraph_text': fallback_paragraph.get('text', f'Image {image_number} context'),
            'content_type': 'body_text',
            'is_heading': fallback_paragraph.get('is_heading', False),
            'paragraph_index': fallback_paragraph.get('index', 0),
            'position_in_chapter': image_number
        }
        
    except Exception as e:
        print(f"⚠️ Error creating fallback context: {e}")
        # Return minimal fallback context
        return {
            'page': 1,
            'position': 'inline',
            'chapter': 'Document Content',
            'type': 'illustration',
            'paragraph_text': f'Image {image_number} from document',
            'content_type': 'body_text',
            'is_heading': False,
            'paragraph_index': 0,
            'position_in_chapter': image_number
        }

def is_content_relevant_image(image_context: dict, paragraph_contexts: list) -> bool:
    """
    Determine if an image is relevant to the main content
    """
    if not image_context:
        return False
    
    # Check if the image is in a meaningful chapter
    chapter = image_context.get('chapter', '').lower()
    if any(skip_term in chapter for skip_term in ['table of contents', 'toc', 'index', 'references', 'bibliography']):
        return False
    
    # Check surrounding context for relevance indicators
    paragraph_text = image_context.get('paragraph_text', '').lower()
    context_indicators = ['step', 'process', 'example', 'shows', 'demonstrates', 'illustrates', 'figure', 'diagram']
    
    if any(indicator in paragraph_text for indicator in context_indicators):
        return True
    
    # Check if image has substantial surrounding content
    para_index = image_context.get('paragraph_index', 0)
    surrounding_text = ""
    
    # Get text from surrounding paragraphs
    for i in range(max(0, para_index - 2), min(len(paragraph_contexts), para_index + 3)):
        if i < len(paragraph_contexts):
            surrounding_text += paragraph_contexts[i].get('text', '') + " "
    
    # If there's substantial instructional content around the image, it's likely relevant
    if len(surrounding_text.strip()) > 200:
        return True
    
    return False

def determine_precise_position(image_context: dict, paragraph_contexts: list) -> str:
    """
    Determine precise position description for image embedding
    """
    position_in_chapter = image_context.get('position_in_chapter', 0)
    
    if position_in_chapter == 0:
        return "chapter-start"
    elif position_in_chapter <= 2:
        return "after-introduction"
    else:
        # Check content around the image
        paragraph_text = image_context.get('paragraph_text', '').lower()
        if any(keyword in paragraph_text for keyword in ['step', 'procedure', 'process']):
            return f"within-step-{position_in_chapter}"
        elif 'example' in paragraph_text:
            return f"within-example-{position_in_chapter}"
        else:
            return f"after-paragraph-{position_in_chapter}"

def determine_image_type(image_context: dict) -> str:
    """
    Determine the type of image based on context
    """
    paragraph_text = image_context.get('paragraph_text', '').lower()
    
    if 'diagram' in paragraph_text:
        return 'diagram'
    elif 'chart' in paragraph_text or 'graph' in paragraph_text:
        return 'chart'
    elif 'screenshot' in paragraph_text or 'screen' in paragraph_text:
        return 'screenshot'
    elif 'table' in paragraph_text:
        return 'table'
    elif any(keyword in paragraph_text for keyword in ['step', 'procedure', 'process']):
        return 'instructional'
    else:
        return 'illustration'

def calculate_placement_priority(image_context: dict) -> int:
    """
    Calculate placement priority for image ordering
    """
    priority = 100  # Base priority
    
    # Higher priority for instructional content
    if image_context.get('content_type') == 'instructional':
        priority += 50
    elif image_context.get('content_type') == 'visual_reference':
        priority += 30
    
    # Higher priority for images with more context
    text_length = len(image_context.get('paragraph_text', ''))
    if text_length > 200:
        priority += 20
    elif text_length > 100:
        priority += 10
    
    return priority

def generate_contextual_caption(image_context: dict, paragraph_contexts: list) -> str:
    """
    Generate a contextual caption for the image
    """
    chapter = image_context.get('chapter', 'Document Section')
    paragraph_text = image_context.get('paragraph_text', '')
    
    # Try to extract existing caption-like text
    if any(keyword in paragraph_text.lower() for keyword in ['figure', 'diagram', 'shows', 'illustrates']):
        # Use the paragraph text as basis for caption
        caption_base = paragraph_text[:100].strip()
        if caption_base.endswith('.'):
            caption_base = caption_base[:-1]
        return f"{caption_base}..."
    
    # Generate contextual caption based on chapter and position
    image_type = determine_image_type(image_context)
    return f"{image_type.title()} from {chapter}"



def create_fallback_segment(segment_content: str, segment_images: list) -> str:
    """Create fallback content for a segment when AI generation fails"""
    try:
        # Create basic HTML structure
        html = ""
        
        # Process segment content into paragraphs
        paragraphs = segment_content.split('\n\n')
        for para in paragraphs[:3]:  # Limit to first 3 paragraphs for fallback
            para = para.strip()
            if para:
                html += f"<p>{para}</p>\n\n"
        
        # Add images if available
        for img in segment_images[:1]:  # Limit to first image for fallback
            html += f"""<figure class="embedded-image">
<img src="{img.get('url', '')}" alt="{img.get('alt_text', 'Figure')}" style="max-width: 100%; height: auto;">
<figcaption>{img.get('caption', 'Figure')}</figcaption>
</figure>

"""
        
        return html
        
    except Exception as e:
        print(f"❌ Fallback segment creation error: {e}")
        return f"<p>{segment_content[:500]}...</p>"

async def generate_single_pass_article(content: str, images: list, template_data: dict, title: str) -> str:
    """Generate article using single-pass approach for shorter content"""
    try:
        system_message = f"""You are an expert technical writer creating comprehensive, professional knowledge base articles.

CRITICAL OUTPUT REQUIREMENTS:
1. Generate ONLY clean, semantic HTML content - absolutely NO meta-commentary, explanations, or processing notes
2. NEVER mention that you are processing content, creating articles, or analyzing documents
3. Start directly with content - no introductory phrases like "Here is the article" or "Based on the content"
4. Use proper HTML5 structure: <h2>, <h3>, <p>, <ul>, <ol>, <li>, <strong>, <em>, <blockquote>, <table>
5. Create contextual, descriptive titles that reflect actual content topics (NOT filename-based)
6. Write in professional, technical tone suitable for enterprise knowledge documentation
7. Include comprehensive coverage - do NOT truncate or summarize content artificially
8. Use proper heading hierarchy and logical content flow
9. Include step-by-step instructions, detailed procedures, and comprehensive explanations
10. Use callout sections for Notes, Tips, Warnings using appropriate HTML structure
11. NEVER generate code blocks with ```html or ```javascript - only generate actual HTML content
12. NEVER repeat the document title as it already exists in the h1 tag

TEMPLATE SPECIFICATIONS:
{json.dumps(template_data.get('processing_instructions', []), indent=2)}

QUALITY STANDARDS:
- COMPREHENSIVE coverage - include ALL important details from source content
- Clear, detailed step-by-step instructions where applicable  
- Professional enterprise technical writing style
- Proper heading hierarchy for content organization (h2 for major sections, h3 for subsections) - document already has h1 title
- Bullet points and numbered lists for procedures and key points
- Tables for structured data presentation
- No artificial content truncation or summarization

IMAGE INTEGRATION REQUIREMENTS:
- Embed ALL available images at contextually appropriate locations in the content
- Use proper HTML figure elements with captions exactly as provided
- Reference images naturally in the text flow (e.g., "as shown in Figure 1")
- CRITICAL: Only use the exact URLs provided in the image list
- Images should support and enhance the written content, not replace it"""

        user_message = f"""Transform this content into a comprehensive, well-structured knowledge base article with complete coverage:

CONTENT TO PROCESS:
{content}

CRITICAL REQUIREMENTS:
1. **Comprehensive Coverage**: Include ALL information from the source content - do not truncate or summarize
2. **Intelligent Title**: Create a meaningful title based on the main topic (NOT filename-based)
3. **Professional Structure**: Use proper headings (h2 for major sections, h3 for subsections) - DO NOT create additional h1 tags as the document already has a title
4. **Technical Quality**: Enterprise-level professional language for technical documentation
5. **Detailed Instructions**: Include complete step-by-step procedures with full detail
6. **Enhanced Formatting**: Proper lists, tables, callouts, and semantic HTML structure
7. **Complete Content**: Process the entire content without artificial limits or truncation

AVAILABLE IMAGES FOR EMBEDDING: {len(images)}
{format_available_images(images)}

CRITICAL IMAGE EMBEDDING INSTRUCTIONS:
- You MUST embed images at contextually appropriate locations throughout the article
- Use the exact HTML provided for each image in the list above
- Reference images in the text flow naturally (e.g., "As shown in Figure 1 below:", "The following screenshot demonstrates:")
- Embed images near relevant text sections, not grouped at the end
- If no images are available, focus on comprehensive text content only
- NEVER create placeholder text like [IMAGE_1] - only use actual provided images

CONTENT ENHANCEMENT REQUIREMENTS:
- Transform basic content into comprehensive enterprise documentation
- Maintain all technical details and procedural steps
- Add proper structure with detailed headings and sections
- Include implementation details, examples, and comprehensive explanations
- Use callout boxes for important notes, tips, or warnings
- Create tables for structured information where appropriate
- Ensure content flows logically from introduction through detailed procedures to conclusion
- Include troubleshooting information where relevant

CRITICAL: Return ONLY the complete HTML article content with semantic structure. Do not include any explanatory text, processing notes, or meta-commentary."""

        # Generate content with LLM
        ai_content = await call_llm_with_fallback(system_message, user_message)
        
        if ai_content:
            return ai_content.strip()
        
        return None
        
    except Exception as e:
        print(f"❌ Single-pass generation error: {e}")
        return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)