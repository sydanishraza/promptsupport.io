"""
TICKET 3: Universal bookmarks and document registry
Extracted from server.py V2ValidationSystem and V2StyleProcessor
"""

import time
import random
import string
import re
import unicodedata
from typing import Dict, Any, List
from bs4 import BeautifulSoup


def extract_headings_registry(html: str) -> List[Dict[str, Any]]:
    """TICKET 3: Extract headings for bookmark registry"""
    soup = BeautifulSoup(html, 'html.parser')
    headings = []
    order = 1
    
    for heading in soup.select("h2, h3, h4"):
        if heading.get("id"):
            headings.append({
                "id": heading.get("id"),
                "text": heading.get_text(" ", strip=True),
                "level": int(heading.name[1]),
                "order": order
            })
            order += 1
            print(f"📖 TICKET 3: Registered bookmark #{order-1}: '{heading.name}#{heading.get('id')}' - '{heading.get_text()[:50]}...'")
    
    print(f"📖 TICKET 3: Extracted {len(headings)} headings for bookmark registry")
    return headings


def generate_doc_uid() -> str:
    """TICKET 3: Generate immutable document UID using ULID"""
    # Simple ULID-like implementation (timestamp + randomness)
    timestamp = int(time.time() * 1000)  # milliseconds
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    
    # Format: 01JZ + timestamp_base36 + random
    timestamp_b36 = format(timestamp, 'x').upper()[-8:]  # Last 8 chars of hex timestamp
    doc_uid = f"01JZ{timestamp_b36}{random_part[:8]}"
    
    print(f"🆔 TICKET 3: Generated doc_uid: {doc_uid}")
    return doc_uid


def generate_doc_slug(title: str) -> str:
    """TICKET 3: Generate human-readable document slug from title"""
    # Use the same stable_slug logic but optimized for document titles
    norm = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"\s+", "-", norm.lower())
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    
    # Limit length for document slugs
    doc_slug = slug[:80] if slug else "untitled-document"
    
    print(f"🏷️ TICKET 3: Generated doc_slug: '{doc_slug}' from title: '{title[:50]}...'")
    return doc_slug


async def backfill_registry(limit: int = None) -> Dict[str, Any]:
    """TICKET 3: Backfill existing v2 articles with bookmark registry data"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    try:
        # Connect to database
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
        client = AsyncIOMotorClient(mongo_url)
        db = client.promptsupport_db
        
        # Query for V2 articles missing bookmark data
        query = {
            "engine": "v2",
            "$or": [
                {"doc_uid": {"$exists": False}},
                {"doc_slug": {"$exists": False}}, 
                {"headings": {"$exists": False}},
                {"doc_uid": None},
                {"doc_slug": None},
                {"headings": None}
            ]
        }
        
        # KE-PR9: Use repository pattern to find articles needing backfill
        try:
            from ..stores.mongo import RepositoryFactory
            content_repo = RepositoryFactory.get_content_library()
            # Find V2 articles that need bookmark backfill
            all_articles = await content_repo.find_by_engine("v2", limit=limit if limit else None)
            
            # Filter articles needing backfill (missing TICKET-3 fields)
            articles = []
            for article in all_articles:
                needs_backfill = (
                    not article.get("doc_uid") or 
                    not article.get("doc_slug") or 
                    not article.get("headings")
                )
                if needs_backfill:
                    articles.append(article)
                    
        except Exception as repo_error:
            print(f"❌ KE-PR9.3: Repository error for bookmark backfill - {repo_error}")
            # Return empty list instead of falling back to direct DB
            articles = []
        
        print(f"📖 TICKET 3: Found {len(articles)} V2 articles needing bookmark backfill")
        
        processed_count = 0
        error_count = 0
        
        for article in articles:
            try:
                title = article.get('title', 'Untitled')
                content = article.get('html', article.get('content', ''))
                
                if not content:
                    print(f"⚠️ TICKET 3: Skipping article '{title}' - no content found")
                    continue
                
                # Generate missing identifiers
                doc_uid = article.get('doc_uid') or generate_doc_uid()
                doc_slug = article.get('doc_slug') or generate_doc_slug(title)
                
                # Extract headings for bookmark registry
                headings = extract_headings_registry(content)
                
                # Update article with bookmark data
                update_data = {
                    "doc_uid": doc_uid,
                    "doc_slug": doc_slug,
                    "headings": headings,
                    "bookmarks_updated": True
                }
                
                # KE-PR9: Update article using repository pattern
                try:
                    from ..stores.mongo import RepositoryFactory
                    content_repo = RepositoryFactory.get_content_library()
                    
                    # Use upsert_content to preserve TICKET-3 fields
                    success = await content_repo.upsert_content(doc_uid, update_data)
                    if not success:
                        print(f"⚠️ KE-PR9: Repository update failed, using direct DB for {title}")
                        raise Exception("Repository update failed")
                        
                except Exception as repo_error:
                    print(f"⚠️ KE-PR9: Bookmark update fallback to direct DB: {repo_error}")
                    # Fallback to direct database update
                    await db.content_library.update_one(
                        {"_id": article["_id"]}, 
                        {"$set": update_data}
                    )
                
                processed_count += 1
                print(f"✅ TICKET 3: Updated article '{title}' with {len(headings)} bookmarks - doc_uid: {doc_uid}")
                
            except Exception as e:
                error_count += 1
                print(f"❌ TICKET 3: Error processing article '{article.get('title', 'Unknown')}': {e}")
        
        print(f"🎉 TICKET 3: Backfill complete - {processed_count} articles updated, {error_count} errors")
        
        return {
            "articles_processed": processed_count,
            "errors": error_count,
            "total_found": len(articles),
            "status": "success" if error_count == 0 else "completed_with_errors"
        }
        
    except Exception as e:
        print(f"❌ TICKET 3: Backfill registry failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "articles_processed": 0
        }


async def get_registry(doc_uid: str) -> Dict[str, Any]:
    """TICKET 3: Get bookmark registry for a specific document"""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    try:
        # KE-PR9: Use repository pattern to get document registry
        try:
            from ..stores.mongo import RepositoryFactory
            content_repo = RepositoryFactory.get_content_library()
            doc = await content_repo.find_by_doc_uid(
                doc_uid, 
                projection={"headings": 1, "doc_slug": 1, "title": 1, "_id": 0}
            )
        except Exception as repo_error:
            print(f"⚠️ KE-PR9: Registry lookup fallback to direct DB: {repo_error}")
            # Fallback to direct database access
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            
            # Connect to database
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
            client = AsyncIOMotorClient(mongo_url)
            db = client.promptsupport_db
            
            doc = await db.content_library.find_one(
                {"doc_uid": doc_uid},
                {"headings": 1, "doc_slug": 1, "title": 1, "_id": 0}
            )
        
        if not doc:
            return {}
        
        return {
            "doc_uid": doc_uid,
            "doc_slug": doc.get("doc_slug"),
            "title": doc.get("title"),
            "headings": doc.get("headings", [])
        }
        
    except Exception as e:
        print(f"❌ TICKET 3: Error getting registry for {doc_uid}: {e}")
        return {}