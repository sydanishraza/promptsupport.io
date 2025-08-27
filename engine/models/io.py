from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SourceSpan(BaseModel):
    source_id: str
    location: str        # e.g., "docx:p3" or "pdf:p12:xywh"
    char_start: int
    char_end: int

class RawBlock(BaseModel):
    type: str            # heading|paragraph|code|table|list|image
    text: Optional[str] = None
    level: Optional[int] = None
    attrs: Dict[str, Any] = {}
    sources: List[SourceSpan] = []

class RawBundle(BaseModel):
    job_id: str
    source_id: str
    blocks: List[RawBlock]
    media_ids: List[str] = []
    metadata: Dict[str, Any] = {}

class Section(BaseModel):
    id: str
    heading: str
    anchor_id: str
    content_html: str
    media_ids: List[str] = []
    provenance: List[SourceSpan] = []

class NormDoc(BaseModel):
    job_id: str
    outline: List[Dict[str, Any]]
    sections: List[Section]
    citations: Dict[str, List[SourceSpan]] = {}