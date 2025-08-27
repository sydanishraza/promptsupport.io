"""
TICKET 2: Table of Contents generation and validation
Extracted from server.py V2ValidationSystem
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .anchors import stable_slug


def build_toc(headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds nested TOC from a list of headings: [{text, level, anchor_id}]"""
    stack = [{"level": 0, "children": []}]
    for h in headings:
        node = {k: h[k] for k in ("text", "level", "anchor_id") if k in h}
        node["children"] = []
        while stack and h["level"] <= stack[-1]["level"]:
            stack.pop()
        stack[-1]["children"].append(node)
        stack.append(node)
    return stack[0]["children"]


def build_minitoc(html: str) -> str:
    """TICKET 2: Build Mini-TOC with clickable links using assigned IDs"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all headings that need TOC entries (H2 and H3)
    headings = soup.select("h2, h3")
    
    if not headings:
        print("⚠️ TICKET 2: No headings found for Mini-TOC")
        return str(soup)
    
    # CRITICAL FIX: Process headings in order and ensure consistent ID assignment
    toc_items = []
    
    for heading in headings:
        heading_text = heading.get_text(" ", strip=True)
        
        # Ensure heading has an ID using the same stable_slug function
        if not heading.get("id"):
            heading_id = stable_slug(heading_text)
            heading["id"] = heading_id
            print(f"📌 TICKET 2: Assigned missing ID '{heading_id}' to heading '{heading_text[:30]}...'")
        else:
            heading_id = heading.get("id")
        
        # Add to TOC items list
        toc_items.append({
            'level': heading.name[1],  # '2' or '3'
            'text': heading_text,
            'id': heading_id,
            'element': heading
        })
        
        print(f"🔗 TICKET 2: TOC entry '{heading_text[:30]}...' -> #{heading_id}")
    
    # Create Mini-TOC container with proper structure
    toc_div = soup.new_tag("div", **{"class": "mini-toc"})
    toc_ul = soup.new_tag("ul")
    
    for item in toc_items:
        # Create TOC item with proper indentation based on heading level
        li = soup.new_tag("li", **{"class": f"toc-l{item['level']}"})
        a = soup.new_tag("a", href=f"#{item['id']}", **{"class": "toc-link"})
        a.string = item['text']
        li.append(a)
        toc_ul.append(li)
    
    toc_div.append(toc_ul)
    
    # TICKET 2: Remove old static TOC lists before inserting the new functional Mini-TOC
    # Look for <ul> lists that appear to be old TOCs (contain heading-like text)
    static_toc_removed = 0
    
    for ul in soup.find_all('ul'):
        # Skip if this is already part of our new mini-toc structure
        if ul.find_parent(class_="mini-toc"):
            continue
            
        # Check if this UL looks like an old static TOC
        li_items = ul.find_all('li', recursive=False)
        if len(li_items) >= 3:  # Likely a TOC if it has 3+ items
            # Check if items match our heading structure
            matching_headings = 0
            for li in li_items:
                li_text = li.get_text(strip=True)
                # Check if this text matches any of our headings
                for item in toc_items:
                    if li_text.lower() == item['text'].lower():
                        matching_headings += 1
                        break
            
            # If 60%+ of the items match our headings, it's likely an old TOC
            if matching_headings / len(li_items) >= 0.6:
                print(f"🗑️ TICKET 2: Removing old static TOC list with {len(li_items)} items ({matching_headings} matching headings)")
                ul.decompose()  # Remove the old static TOC
                static_toc_removed += 1
    
    # Insert Mini-TOC at the beginning of content (after any existing TOC)
    existing_toc = soup.find(class_="mini-toc")
    if existing_toc:
        existing_toc.replace_with(toc_div)
        print("🔄 TICKET 2: Replaced existing Mini-TOC")
    else:
        # Insert at beginning of content
        first_content = soup.find(['p', 'h2', 'h3', 'div'])
        if first_content:
            first_content.insert_before(toc_div)
        else:
            # Fallback: insert at beginning
            if soup.body:
                soup.body.insert(0, toc_div)
            else:
                soup.insert(0, toc_div)
    
    if static_toc_removed > 0:
        print(f"✅ TICKET 2: Mini-TOC built with {len(toc_items)} clickable links, removed {static_toc_removed} old static TOC(s)")
    else:
        print(f"✅ TICKET 2: Mini-TOC built with {len(toc_items)} clickable links")
    return str(soup)


def anchors_resolve(html: str) -> bool:
    """TICKET 2: Validate that all TOC links resolve to actual heading IDs"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get all existing IDs in the document
    existing_ids = {tag.get("id") for tag in soup.find_all(attrs={"id": True}) if tag.get("id")}
    
    # Check all Mini-TOC links
    broken_links = []
    for link in soup.select(".mini-toc a[href^='#']"):
        target_id = link.get("href", "")[1:]  # Remove the #
        if target_id not in existing_ids:
            broken_links.append(target_id)
    
    if broken_links:
        print(f"❌ TICKET 2: {len(broken_links)} broken anchor links: {broken_links}")
        return False
    
    toc_links = soup.select('.mini-toc a[href^="#"]')
    print(f"✅ TICKET 2: All {len(toc_links)} anchor links resolve correctly")
    return True