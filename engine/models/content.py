from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class MediaAsset(BaseModel):
    id: str
    type: str            # image|video
    format: str          # png|jpg|jpeg|gif|mp4
    path: str
    hash: str
    caption: Optional[str] = None
    alt: Optional[str] = None
    source_ref: Optional[str] = None

class ArticleVersion(BaseModel):
    id: str
    article_id: str
    content_html: str
    outline: List[Dict[str, Any]]
    sections: List[Dict[str, Any]]
    provenance: List[Dict[str, Any]]
    media_refs: List[str]
    qa_report: Dict[str, Any]