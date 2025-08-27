"""
TICKET 2: Anchor generation and heading ID management
Extracted from server.py V2ValidationSystem
"""

import re
import unicodedata
from typing import Optional
from bs4 import BeautifulSoup


def stable_slug(text: str, max_len: int = 60) -> str:
    """TICKET 2: Generate deterministic, URL-safe slugs from heading text"""
    # Normalize unicode characters to ASCII
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    
    # Convert to lowercase and replace spaces with hyphens
    s = re.sub(r"\s+", "-", norm.lower())
    
    # Remove non-alphanumeric characters except hyphens
    s = re.sub(r"[^a-z0-9-]", "", s)
    
    # Replace multiple consecutive hyphens with single hyphen
    s = re.sub(r"-{2,}", "-", s).strip("-")
    
    # Truncate to max length and provide fallback
    return s[:max_len] if s else "section"


def anchor_id(heading_text: str, prefix: Optional[str] = None) -> str:
    """Generate anchor ID with optional prefix"""
    base = stable_slug(heading_text)
    return f"{prefix}-{base}" if prefix else base


def assign_heading_ids(html: str) -> str:
    """TICKET 2: Assign deterministic IDs to headings before TOC generation"""
    soup = BeautifulSoup(html, 'html.parser')
    seen_slugs = {}
    assigned_count = 0
    
    # TICKET 2: Clean up duplicate content and headings before processing TOC
    # Remove duplicate H2 headings that repeat the article title or main topic
    article_title_words = set()
    for heading in soup.select("h2, h3, h4"):
        heading_text = heading.get_text(" ", strip=True).lower()
        
        # Remove headings that are just repetitions of the article topic
        # Look for headings like "Using Google Map Javascript API" when article is about Google Maps
        if len(heading_text.split()) <= 6:  # Short headings are more likely to be duplicates
            # Check for simple repetition patterns
            words = heading_text.split()
            if len(words) <= 4 and any(word in article_title_words for word in words):
                # Skip this check for now, need to be more careful
                pass
                
            # Remove specific pattern: heading that matches the first bullet point
            first_toc_item = soup.find('ul')
            if first_toc_item:
                first_item = first_toc_item.find('li')
                if first_item and heading_text == first_item.get_text(strip=True).lower():
                    print(f"🗑️ TICKET 2: Removing duplicate heading: '{heading_text[:30]}...'")
                    heading.decompose()
                    continue
    
    # Process H2 and H3 headings in document order
    for heading in soup.select("h2, h3, h4"):
        if not heading.get("id"):
            # Generate base slug from heading text
            heading_text = heading.get_text(" ", strip=True)
            base_slug = stable_slug(heading_text)
            
            # Handle duplicates with suffixes
            slug = base_slug
            counter = 2
            while slug in seen_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            # Assign the unique slug
            seen_slugs[slug] = True
            heading["id"] = slug
            assigned_count += 1
            
            print(f"📌 TICKET 2: Assigned ID '{slug}' to {heading.name}: '{heading_text[:50]}...'")
    
    print(f"📌 TICKET 2: Assigned {assigned_count} heading IDs")
    return str(soup)


def validate_heading_ladder(html: str) -> bool:
    """TICKET 2: Validate proper heading hierarchy (H2->H3->H4)"""
    soup = BeautifulSoup(html, 'html.parser')
    levels = []
    
    for tag in soup.find_all(["h2", "h3", "h4"]):
        level = int(tag.name[1])
        levels.append(level)
        
        # Check for proper progression
        if len(levels) > 1:
            prev_level = levels[-2]
            # H3 should not appear without H2, and levels shouldn't skip
            if (level == 3 and 2 not in levels) or (level - prev_level > 1):
                print(f"❌ TICKET 2: Heading ladder violation - {tag.name} after H{prev_level}")
                return False
    
    print(f"✅ TICKET 2: Heading ladder valid - {len(levels)} headings")
    return True