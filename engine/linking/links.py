"""
TICKET 3: Environment-aware link building
Extracted from server.py V2ValidationSystem LinkBuilder functionality
"""

import os
from typing import Dict, Any


def build_href(target_doc: Dict[str, Any], anchor_id: str, route_map: Dict[str, Any]) -> str:
    """TICKET 3: Build environment-aware href for cross-document links"""
    try:
        base_url = route_map.get("baseUrl", "").rstrip("/")
        routes = route_map.get("routes", {})
        prefer = route_map.get("prefer", "slug")
        
        # Choose route based on preference and availability
        if prefer == "slug" and target_doc.get("doc_slug"):
            route_template = routes.get("articleBySlug", "/articles/:slug")
            path = route_template.replace(":slug", target_doc["doc_slug"])
        else:
            route_template = routes.get("articleByUid", "/library/:uid")
            path = route_template.replace(":uid", target_doc["doc_uid"])
        
        # Build complete href
        href = f"{base_url}{path}#{anchor_id}" if anchor_id else f"{base_url}{path}"
        
        print(f"🔗 TICKET 3: Built href '{href}' for doc '{target_doc.get('title', 'Unknown')[:30]}...' -> #{anchor_id}")
        return href
        
    except Exception as e:
        print(f"❌ TICKET 3: Error building href - {e}")
        return f"#{anchor_id}"  # Fallback to local anchor


def get_default_route_map(environment: str = "content_library") -> Dict[str, Any]:
    """TICKET 3: Get default route map for different environments"""
    route_maps = {
        "content_library": {
            "env": "content_library",
            "baseUrl": "",  # Same domain
            "routes": {
                "articleByUid": "/library/:uid",
                "articleBySlug": "/library/articles/:slug"
            },
            "prefer": "uid"
        },
        "knowledge_base": {
            "env": "knowledge_base", 
            "baseUrl": "https://kb.example.com",
            "routes": {
                "articleByUid": "/library/:uid",
                "articleBySlug": "/articles/:slug"
            },
            "prefer": "slug"
        },
        "dev_docs": {
            "env": "dev_docs",
            "baseUrl": "https://docs.example.com", 
            "routes": {
                "articleByUid": "/docs/:uid",
                "articleBySlug": "/docs/:slug"
            },
            "prefer": "slug"
        }
    }
    
    return route_maps.get(environment, route_maps["content_library"])


def build_link(doc_slug: str, anchor_id: str, base_url: str = None) -> str:
    """Simple link builder for basic use cases"""
    if not base_url:
        base_url = os.getenv("PUBLIC_BASE_URL", "https://preview.local")
    
    base_url = base_url.rstrip("/")
    if anchor_id:
        return f"{base_url}/docs/{doc_slug}#{anchor_id}"
    else:
        return f"{base_url}/docs/{doc_slug}"