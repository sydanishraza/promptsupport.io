"""
Cross-document linking modules.
TICKET 2/3 anchor and bookmark management.
"""

from .anchors import stable_slug, anchor_id, assign_heading_ids, validate_heading_ladder
from .toc import build_toc, build_minitoc, anchors_resolve
from .bookmarks import extract_headings_registry, generate_doc_uid, generate_doc_slug, backfill_registry, get_registry
from .links import build_href, get_default_route_map

__all__ = [
    "stable_slug", "anchor_id", "assign_heading_ids", "validate_heading_ladder",
    "build_toc", "build_minitoc", "anchors_resolve", 
    "extract_headings_registry", "generate_doc_uid", "generate_doc_slug", "backfill_registry", "get_registry",
    "build_href", "get_default_route_map"
]