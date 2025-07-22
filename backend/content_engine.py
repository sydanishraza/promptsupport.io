"""
Enhanced Content Engine for PromptSupport
Handles multiple input sources: files, URLs, recordings, integrations
"""
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tempfile
import os
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import re
import json

# LLM Integration
# from emergentintegrations.llm.chat import LlmChat, UserMessage

class ContentEngine:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
    async def process_url(self, url: str, source_type: str = "webpage") -> Dict[str, Any]:
        """Process URL content - web scraping and content extraction"""
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
            
            # Handle different URL types
            if 'youtube.com' in url or 'youtu.be' in url:
                return await self.process_youtube_url(url)
            elif 'github.com' in url:
                return await self.process_github_url(url)
            else:
                return await self.process_webpage_url(url)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"URL processing failed: {str(e)}",
                "content": "",
                "metadata": {}
            }
    
    async def process_webpage_url(self, url: str) -> Dict[str, Any]:
        """Scrape and process webpage content"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Untitled"
            
            # Extract main content
            content_selectors = [
                'main', 'article', '.content', '#content', 
                '.main-content', '.post-content', '.entry-content'
            ]
            
            content_element = None
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    break
            
            if not content_element:
                content_element = soup.find('body')
            
            # Extract text content
            text_content = content_element.get_text().strip() if content_element else ""
            
            # Clean up whitespace
            text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
            text_content = re.sub(r' +', ' ', text_content)
            
            # Extract metadata
            metadata = {
                "title": title_text,
                "url": url,
                "source_type": "webpage",
                "word_count": len(text_content.split()),
                "scraped_at": datetime.utcnow().isoformat()
            }
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata["description"] = meta_desc.get('content', '').strip()
            
            return {
                "success": True,
                "content": text_content,
                "metadata": metadata,
                "raw_html": str(soup) if len(str(soup)) < 50000 else str(soup)[:50000] + "..."
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Webpage processing failed: {str(e)}",
                "content": "",
                "metadata": {}
            }
    
    async def process_youtube_url(self, url: str) -> Dict[str, Any]:
        """Process YouTube video URL (extract transcript if available)"""
        try:
            # For MVP, we'll extract basic video info
            # In production, we'd use youtube-dl or yt-dlp for transcript extraction
            
            video_id = self.extract_youtube_id(url)
            if not video_id:
                raise ValueError("Could not extract YouTube video ID")
            
            # Basic video info (in production, use YouTube API)
            metadata = {
                "title": f"YouTube Video: {video_id}",
                "url": url,
                "video_id": video_id,
                "source_type": "youtube",
                "scraped_at": datetime.utcnow().isoformat()
            }
            
            # Note: In production implementation, we would:
            # 1. Use YouTube Data API to get video details
            # 2. Use yt-dlp to extract transcript/captions
            # 3. Fall back to audio extraction + AssemblyAI if no transcript
            
            content = f"YouTube Video: {url}\n\nNote: Transcript extraction will be implemented in the next version. For now, please upload the video file directly for transcription."
            
            return {
                "success": True,
                "content": content,
                "metadata": metadata,
                "requires_video_processing": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"YouTube processing failed: {str(e)}",
                "content": "",
                "metadata": {}
            }
    
    async def process_github_url(self, url: str) -> Dict[str, Any]:
        """Process GitHub repository or file URL"""
        try:
            # Handle GitHub API for better content extraction
            if 'github.com' in url:
                # Convert github.com URL to raw content if it's a file
                if '/blob/' in url:
                    raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                    return await self.process_webpage_url(raw_url)
                else:
                    # Process as regular webpage for repo main page
                    return await self.process_webpage_url(url)
            
            return {
                "success": False,
                "error": "Unsupported GitHub URL format",
                "content": "",
                "metadata": {}
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"GitHub processing failed: {str(e)}",
                "content": "",
                "metadata": {}
            }
    
    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def enhance_content_with_ai(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Use GPT-4o to enhance content structure and extract insights"""
        # LLM integration temporarily disabled
        return {
            "enhanced_content": content,
            "tags": [],
            "summary": metadata.get("description", "AI enhancement temporarily disabled"),
            "key_points": []
        }
        
        # TODO: Re-enable when LLM integration is available
        # try:
        #     if not self.openai_api_key or len(content.strip()) < 50:
        #         return {
        #             "enhanced_content": content,
        #             "tags": [],
        #             "summary": metadata.get("description", ""),
        #             "key_points": []
        #         }
        #     
        #     # Create AI chat for content enhancement
        #     system_message = """You are a content analysis expert. Your job is to analyze and enhance content for a knowledge base.
        # 
        # Given content, provide:
        # 1. A concise summary (2-3 sentences)
        # 2. 5-10 relevant tags/keywords
        # 3. Key points or takeaways (bullet format)
        # 4. Content category (documentation, tutorial, reference, etc.)
        # 
        # Respond in valid JSON format:
        # {
        #   "summary": "Brief summary here",
        #   "tags": ["tag1", "tag2", "tag3"],
        #   "key_points": ["Point 1", "Point 2", "Point 3"],
        #   "category": "category_name"
        # }"""
        # 
        #     chat = LlmChat(
        #         api_key=self.openai_api_key,
        #         session_id=f"content_analysis_{uuid.uuid4()}",
        #         system_message=system_message
        #     ).with_model("openai", "gpt-4o")
        #     
        #     # Truncate content if too long
        #     analysis_content = content[:4000] if len(content) > 4000 else content
        #     
        #     user_message = UserMessage(
        #         text=f"Please analyze this content:\n\nTitle: {metadata.get('title', 'Unknown')}\nContent:\n{analysis_content}"
        #     )
        #     
        #     response = await chat.send_message(user_message)
        #     
        #     # Try to parse JSON response
        #     try:
        #         enhanced_data = json.loads(response)
        #         return {
        #             "enhanced_content": content,
        #             "summary": enhanced_data.get("summary", ""),
        #             "tags": enhanced_data.get("tags", []),
        #             "key_points": enhanced_data.get("key_points", []),
        #             "category": enhanced_data.get("category", "general")
        #         }
        #     except json.JSONDecodeError:
        #         # Fallback if JSON parsing fails
        #         return {
        #             "enhanced_content": content,
        #             "tags": [],
        #             "summary": response[:200] + "..." if len(response) > 200 else response,
        #             "key_points": []
        #         }
        #         
        # except Exception as e:
        #     return {
        #         "enhanced_content": content,
        #         "tags": [],
        #         "summary": f"AI enhancement failed: {str(e)}",
        #         "key_points": []
        #     }
    
    def create_content_chunks(self, content: str, chunk_size: int = 1000, overlap: int = 100) -> List[Dict[str, Any]]:
        """Enhanced content chunking with semantic awareness"""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append({
                    "index": chunk_index,
                    "text": current_chunk.strip(),
                    "word_count": len(current_chunk.split()),
                    "char_count": len(current_chunk)
                })
                
                # Start new chunk with overlap
                if overlap > 0:
                    words = current_chunk.split()
                    overlap_words = words[-overlap//10:] if len(words) > overlap//10 else words[-1:]
                    current_chunk = " ".join(overlap_words) + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                
                chunk_index += 1
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "index": chunk_index,
                "text": current_chunk.strip(),
                "word_count": len(current_chunk.split()),
                "char_count": len(current_chunk)
            })
        
        return chunks
    
    async def process_recording(self, audio_data: bytes, filename: str) -> Dict[str, Any]:
        """Process recorded audio/video content"""
        try:
            # Save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Use AssemblyAI for transcription
            import assemblyai as aai
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(temp_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"AssemblyAI error: {transcript.error}")
            
            # Clean up temp file
            os.unlink(temp_path)
            
            metadata = {
                "title": f"Recording: {filename}",
                "source_type": "recording",
                "filename": filename,
                "transcribed_at": datetime.utcnow().isoformat(),
                "duration": getattr(transcript, 'duration', 0) / 1000 if hasattr(transcript, 'duration') else 0
            }
            
            return {
                "success": True,
                "content": transcript.text,
                "metadata": metadata,
                "transcript_data": {
                    "confidence": getattr(transcript, 'confidence', 0),
                    "words": getattr(transcript, 'words', [])
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Recording processing failed: {str(e)}",
                "content": "",
                "metadata": {}
            }

# Global content engine instance
content_engine = ContentEngine()