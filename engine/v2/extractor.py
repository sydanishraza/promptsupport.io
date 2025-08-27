"""
KE-PR4: V2 Content Extractor
Extracted from server.py - Advanced content extraction with provenance tracking
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List

class ContentBlock:
    """Simple content block for V2 extraction compatibility"""
    def __init__(self, block_type: str, content: str, metadata: Dict[str, Any] = None):
        self.block_type = block_type
        self.content = content
        self.metadata = metadata or {}

class MediaRecord:
    """Simple media record for V2 extraction compatibility"""
    def __init__(self, media_type: str, url: str, metadata: Dict[str, Any] = None):
        self.media_type = media_type
        self.url = url
        self.metadata = metadata or {}

class NormalizedDocument:
    """V2 Compatible NormalizedDocument for pipeline integration"""
    def __init__(self, doc_id: str = None, title: str = "Text Content", original_filename: str = None,
                 file_id: str = None, mime_type: str = "text/plain", word_count: int = 0,
                 blocks: List[ContentBlock] = None, media: List[MediaRecord] = None,
                 metadata: Dict[str, Any] = None, extraction_metadata: Dict[str, Any] = None):
        self.doc_id = doc_id or str(uuid.uuid4())
        self.title = title
        self.original_filename = original_filename
        self.file_id = file_id or f"text_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
        self.mime_type = mime_type
        self.word_count = word_count
        self.blocks = blocks or []
        self.media = media or []
        self.metadata = metadata or {}
        self.extraction_metadata = extraction_metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class V2ContentExtractor:
    """V2 Engine: Advanced content extraction with 100% capture and provenance tracking"""
    
    def __init__(self):
        pass
    
    async def extract_raw_text(self, content: str, title: str = "Text Content") -> NormalizedDocument:
        """Extract and normalize raw text content into NormalizedDocument format"""
        try:
            print(f"📝 V2 EXTRACTOR: Extracting raw text content - {len(content)} chars - engine=v2")
            
            # Generate unique identifiers
            file_id = f"text_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            blocks = []
            word_count = 0
            
            # Split content into paragraphs and detect structure
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            for i, paragraph in enumerate(paragraphs):
                if not paragraph:
                    continue
                    
                # Detect block type
                if paragraph.startswith('#'):
                    # Heading
                    level = len(paragraph) - len(paragraph.lstrip('#'))
                    text = paragraph.lstrip('# ').strip()
                    block_type = f"heading_h{min(level, 6)}"
                elif paragraph.startswith('```'):
                    # Code block
                    text = paragraph
                    block_type = "code"
                elif paragraph.startswith('- ') or paragraph.startswith('* '):
                    # List
                    text = paragraph
                    block_type = "list"
                else:
                    # Regular paragraph
                    text = paragraph
                    block_type = "paragraph"
                
                # Count words
                word_count += len(text.split())
                
                # Create content block
                block = ContentBlock(
                    block_type=block_type,
                    content=text,
                    metadata={
                        "block_index": i,
                        "length": len(text),
                        "word_count": len(text.split())
                    }
                )
                blocks.append(block)
            
            # Create normalized document
            normalized_doc = NormalizedDocument(
                title=title,
                original_filename=title,
                file_id=file_id,
                mime_type="text/plain",
                word_count=word_count,
                blocks=blocks,
                media=[],  # No media in text extraction
                metadata={"content_length": len(content), "block_count": len(blocks)},
                extraction_metadata={"extraction_method": "v2_text_extractor", "engine": "v2"}
            )
            
            print(f"✅ V2 EXTRACTOR: Extracted {len(blocks)} blocks, {word_count} words - engine=v2")
            return normalized_doc
            
        except Exception as e:
            print(f"❌ V2 EXTRACTOR: Error extracting content - {e}")
            # Return minimal document
            fallback_block = ContentBlock(
                block_type="paragraph",
                content=content[:1000] if content else "No content",
                metadata={"extraction_error": str(e)}
            )
            
            return NormalizedDocument(
                title=title,
                file_id=f"error_{int(datetime.utcnow().timestamp())}",
                word_count=len(content.split()) if content else 0,
                blocks=[fallback_block],
                extraction_metadata={"extraction_method": "v2_text_extractor_fallback", "error": str(e)}
            )