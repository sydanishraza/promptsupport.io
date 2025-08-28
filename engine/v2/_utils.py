"""
KE-M16: V2 Engine Utilities
Shared utility functions extracted from server.py for V2 processing stages
"""

import uuid
import hashlib
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..models.io import NormDoc, Section


def generate_run_id() -> str:
    """Generate unique run ID for V2 processing"""
    return f"v2_run_{uuid.uuid4().hex[:12]}_{int(datetime.utcnow().timestamp())}"


def generate_article_id(title: str) -> str:
    """Generate stable article ID from title"""
    # Create a hash-based ID that's stable for the same title
    title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()[:12]
    timestamp = int(datetime.utcnow().timestamp())
    return f"v2_article_{title_hash}_{timestamp}"


def generate_doc_uid() -> str:
    """Generate document UID for TICKET-3 compliance"""
    return f"doc_{uuid.uuid4().hex[:16]}"


def generate_doc_slug(title: str) -> str:
    """Generate URL-friendly document slug for TICKET-3 compliance"""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def extract_heading_anchors(content: str) -> List[Dict[str, Any]]:
    """Extract heading anchors from content for TICKET-3 compliance"""
    anchors = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            text = stripped.lstrip('# ').strip()
            anchor_id = generate_doc_slug(text)
            
            anchors.append({
                'level': level,
                'text': text,
                'anchor': anchor_id,
                'id': anchor_id,
                'position': i
            })
    
    return anchors


def extract_cross_references(content: str) -> List[Dict[str, Any]]:
    """Extract cross-references from content for TICKET-3 compliance"""
    xrefs = []
    
    # Look for markdown-style links [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.finditer(link_pattern, content)
    
    for match in matches:
        text = match.group(1)
        url = match.group(2)
        
        # Check if it's an internal reference
        if url.startswith('#') or 'doc_uid' in url:
            xrefs.append({
                'text': text,
                'url': url,
                'type': 'internal',
                'anchor_id': url.lstrip('#') if url.startswith('#') else None
            })
        else:
            xrefs.append({
                'text': text,
                'url': url,
                'type': 'external'
            })
    
    return xrefs


def normalize_content_for_processing(content: str) -> str:
    """Normalize content for consistent V2 processing"""
    # Remove excessive whitespace
    normalized = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Normalize heading markers
    normalized = re.sub(r'^#{1,6}\s*', lambda m: '#' * min(len(m.group()), 6) + ' ', normalized, flags=re.MULTILINE)
    
    # Clean up list markers
    normalized = re.sub(r'^\s*[•\-\*]\s+', '- ', normalized, flags=re.MULTILINE)
    
    # Normalize code blocks
    normalized = re.sub(r'```(\w+)?\n', r'```\1\n', normalized)
    
    return normalized.strip()


def calculate_content_stats(content: str) -> Dict[str, Any]:
    """Calculate content statistics for analysis"""
    lines = content.split('\n')
    words = content.split()
    
    # Count different elements
    headings = len([line for line in lines if line.strip().startswith('#')])
    paragraphs = len([line for line in lines if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('-')])
    lists = len([line for line in lines if line.strip().startswith('-')])
    code_blocks = content.count('```') // 2
    
    return {
        'total_lines': len(lines),
        'total_words': len(words),
        'total_chars': len(content),
        'headings_count': headings,
        'paragraphs_count': paragraphs,
        'lists_count': lists,
        'code_blocks_count': code_blocks,
        'avg_words_per_paragraph': round(len(words) / max(1, paragraphs), 1)
    }


def ensure_ticket3_fields(article: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure article has all required TICKET-3 fields"""
    if 'doc_uid' not in article:
        article['doc_uid'] = generate_doc_uid()
    
    if 'doc_slug' not in article and 'title' in article:
        article['doc_slug'] = generate_doc_slug(article['title'])
    
    if 'headings' not in article and 'content' in article:
        article['headings'] = extract_heading_anchors(article['content'])
    
    if 'xrefs' not in article and 'content' in article:
        article['xrefs'] = extract_cross_references(article['content'])
    
    return article


def create_processing_metadata(stage_name: str, **kwargs) -> Dict[str, Any]:
    """Create standardized processing metadata"""
    return {
        'stage': stage_name,
        'engine': 'v2',
        'timestamp': datetime.utcnow().isoformat(),
        'processing_id': f"{stage_name}_{uuid.uuid4().hex[:8]}",
        **kwargs
    }


def merge_article_metadata(article: Dict[str, Any], new_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Merge new metadata into article while preserving existing data"""
    if 'metadata' not in article:
        article['metadata'] = {}
    
    # Preserve existing metadata and add new
    article['metadata'].update(new_metadata)
    
    return article


def validate_v2_article_structure(article: Dict[str, Any]) -> Dict[str, bool]:
    """Validate article has required V2 structure"""
    return {
        'has_title': 'title' in article and bool(article['title']),
        'has_content': 'content' in article and bool(article['content']),
        'has_doc_uid': 'doc_uid' in article and bool(article['doc_uid']),
        'has_doc_slug': 'doc_slug' in article and bool(article['doc_slug']),
        'has_headings': 'headings' in article and isinstance(article['headings'], list),
        'has_xrefs': 'xrefs' in article and isinstance(article['xrefs'], list),
        'has_metadata': 'metadata' in article and isinstance(article['metadata'], dict)
    }


def create_fallback_article(title: str = "Generated Article", error: str = "") -> Dict[str, Any]:
    """Create fallback article structure when processing fails"""
    article = {
        'id': generate_article_id(title),
        'title': title,
        'content': f'<h1>{title}</h1><p>Content processing in progress...</p>',
        'metadata': create_processing_metadata('fallback', error=error),
        'created_at': datetime.utcnow().isoformat(),
        'engine': 'v2'
    }
    
    return ensure_ticket3_fields(article)


async def create_article_from_blocks_v2(blocks, title: str, normalized_doc) -> Dict[str, Any]:
    """V2 ENGINE: Create a single article from content blocks with media references (no embedding)"""
    try:
        # Convert blocks to HTML content with NO IMAGE EMBEDDING
        html_parts = []
        
        for block in blocks:
            if block.block_type == 'heading':
                level = min(block.level, 6) if block.level else 2  # Default to H2 if no level
                html_parts.append(f"<h{level}>{block.content}</h{level}>")
            elif block.block_type == 'paragraph':
                html_parts.append(f"<p>{block.content}</p>")
            elif block.block_type == 'list':
                # Detect if it's ordered or unordered list
                list_items = []
                if isinstance(block.content, str):
                    lines = block.content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                            list_items.append(line[1:].strip())
                        elif line and any(line.startswith(f"{i}.") for i in range(1, 20)):
                            list_items.append(line.split('.', 1)[1].strip())
                        elif line:
                            list_items.append(line)
                
                if list_items:
                    # Detect ordered vs unordered
                    is_ordered = any(block.content.startswith(f"{i}.") for i in range(1, 10))
                    list_tag = 'ol' if is_ordered else 'ul'
                    html_parts.append(f"<{list_tag}>")
                    for item in list_items:
                        html_parts.append(f"<li>{item}</li>")
                    html_parts.append(f"</{list_tag}>")
                else:
                    html_parts.append(f"<p>{block.content}</p>")
                    
            elif block.block_type == 'code':
                language = block.language if hasattr(block, 'language') and block.language else ''
                if language:
                    html_parts.append(f"<pre><code class='language-{language}'>{block.content}</code></pre>")
                else:
                    html_parts.append(f"<pre><code>{block.content}</code></pre>")
            elif block.block_type == 'quote':
                html_parts.append(f"<blockquote>{block.content}</blockquote>")
            elif block.block_type == 'table':
                # Simple table conversion - could be enhanced
                html_parts.append(f"<div class='table-container'>{block.content}</div>")
            else:
                # Default: treat as paragraph
                html_parts.append(f"<p>{block.content}</p>")
        
        # Create the article structure
        content = '\n'.join(html_parts)
        
        article = {
            'id': generate_article_id(title),
            'title': title,
            'content': content,
            'html': content,  # For compatibility
            'metadata': create_processing_metadata('blocks_to_article', 
                                                 source_blocks=len(blocks),
                                                 normalized_doc_id=getattr(normalized_doc, 'doc_id', 'unknown')),
            'created_at': datetime.utcnow().isoformat(),
            'engine': 'v2'
        }
        
        # Ensure TICKET-3 compliance
        article = ensure_ticket3_fields(article)
        
        return article
        
    except Exception as e:
        print(f"❌ V2 UTILS: Error creating article from blocks - {e}")
        return create_fallback_article(title, str(e))


def classify_content_complexity(content: str) -> str:
    """Classify content complexity for processing strategy"""
    stats = calculate_content_stats(content)
    
    word_count = stats['total_words']
    headings = stats['headings_count']
    code_blocks = stats['code_blocks_count']
    
    # Simple classification logic
    if word_count > 5000 or headings > 10 or code_blocks > 5:
        return 'complex'
    elif word_count > 2000 or headings > 5 or code_blocks > 2:
        return 'moderate'
    elif word_count < 500 and headings < 3:
        return 'simple'
    else:
        return 'moderate'


def estimate_processing_time(complexity: str, content_length: int) -> str:
    """Estimate processing time based on content characteristics"""
    base_time = {
        'simple': 2,      # minutes
        'moderate': 5,    # minutes  
        'complex': 10,    # minutes
        'highly_complex': 15  # minutes
    }.get(complexity, 5)
    
    # Adjust for content length
    if content_length > 10000:
        base_time += 3
    elif content_length > 5000:
        base_time += 1
    
    return f"{base_time}-{base_time + 2} minutes"


print("✅ KE-M16: V2 Engine utilities loaded")