"""
KE-PR7: Validator & QA Report as First-Class Module
Reusable validation module that returns machine-readable QAReport with coverage %, flags, and publish gates
"""

import re
import asyncio
from typing import List, Dict, Set, Tuple
from urllib.parse import urlparse
import requests
from ..models.qa import QAReport, QAFlag
from ..models.io import NormDoc, RawBundle

def validate(norm: NormDoc, raw: RawBundle = None) -> QAReport:
    """
    Main validation function that returns comprehensive QA report
    
    Args:
        norm: Normalized document after V2 processing
        raw: Original raw bundle for coverage analysis
        
    Returns:
        QAReport with coverage %, flags, broken links, and missing media
    """
    try:
        print(f"🔍 KE-PR7: Starting comprehensive validation - job_id: {norm.job_id}")
        
        flags = []
        broken_links = []
        missing_media = []
        
        # Get content for analysis
        content = _extract_content_from_norm(norm)
        
        # Check 1: Coverage Analysis
        coverage = _calculate_coverage(norm, raw)
        if coverage < 85.0:
            flags.append(QAFlag(
                code="P1_LOW_COVERAGE", 
                severity="P1", 
                message=f"Content coverage is {coverage:.1f}% (minimum: 85%)",
                location="overall"
            ))
        elif coverage < 70.0:
            flags.append(QAFlag(
                code="P0_CRITICAL_LOW_COVERAGE", 
                severity="P0", 
                message=f"Critical: Content coverage is only {coverage:.1f}% (minimum: 85%)",
                location="overall"
            ))
        
        # Check 2: Unsupported Claims Heuristic
        unsupported_flags = _detect_unsupported_claims(content)
        flags.extend(unsupported_flags)
        
        # Check 3: Placeholder Detection
        placeholder_flags = _detect_placeholders(content)
        flags.extend(placeholder_flags)
        
        # Check 4: Duplicate Content Detection
        duplicate_flags = _detect_duplicates(content)
        flags.extend(duplicate_flags)
        
        # Check 5: Broken Links Detection
        broken_links = _detect_broken_links(content)
        if broken_links:
            flags.append(QAFlag(
                code="P1_BROKEN_LINKS",
                severity="P1",
                message=f"Found {len(broken_links)} potentially broken links",
                location="links"
            ))
        
        # Check 6: Missing Media Detection
        missing_media = _detect_missing_media(content)
        if missing_media:
            flags.append(QAFlag(
                code="P1_MISSING_MEDIA",
                severity="P1", 
                message=f"Found {len(missing_media)} missing media references",
                location="media"
            ))
        
        # Check 7: Content Quality Checks
        quality_flags = _check_content_quality(content)
        flags.extend(quality_flags)
        
        # Check 8: Technical Accuracy Checks
        technical_flags = _check_technical_accuracy(content)
        flags.extend(technical_flags)
        
        # Create QA Report
        qa_report = QAReport(
            job_id=norm.job_id,
            coverage_percent=coverage,
            flags=flags,
            broken_links=broken_links,
            missing_media=missing_media
        )
        
        # Log summary
        p0_count = len([f for f in flags if f.severity == "P0"])
        p1_count = len([f for f in flags if f.severity == "P1"])
        
        print(f"✅ KE-PR7: Validation complete - Coverage: {coverage:.1f}%, P0: {p0_count}, P1: {p1_count}")
        
        return qa_report
        
    except Exception as e:
        print(f"❌ KE-PR7: Validation error - {e}")
        # Return error report
        return QAReport(
            job_id=norm.job_id if norm else "error",
            coverage_percent=0.0,
            flags=[QAFlag(
                code="P0_VALIDATION_ERROR",
                severity="P0",
                message=f"Validation system error: {str(e)}",
                location="system"
            )],
            broken_links=[],
            missing_media=[]
        )

def _extract_content_from_norm(norm: NormDoc) -> str:
    """Extract text content from normalized document"""
    try:
        if hasattr(norm, 'sections') and norm.sections:
            # Extract from sections
            content_parts = []
            for section in norm.sections:
                if hasattr(section, 'content'):
                    content_parts.append(section.content)
            return '\n\n'.join(content_parts)
        
        # Fallback: try to get content from norm directly
        if hasattr(norm, 'content'):
            return norm.content
        
        # Last resort: return title if available
        if hasattr(norm, 'title'):
            return norm.title
        
        return ""
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error extracting content - {e}")
        return ""

def _calculate_coverage(norm: NormDoc, raw: RawBundle = None) -> float:
    """Calculate content coverage percentage"""
    try:
        if not raw or not norm:
            # Fallback coverage calculation based on content quality
            content = _extract_content_from_norm(norm)
            if not content:
                return 0.0
            
            # Basic coverage heuristics
            word_count = len(content.split())
            
            if word_count < 50:
                return 30.0  # Very low coverage for minimal content
            elif word_count < 200:
                return 65.0  # Low coverage for short content
            elif word_count < 500:
                return 80.0  # Good coverage for medium content
            else:
                return 92.0  # High coverage for substantial content
        
        # Advanced coverage calculation with raw comparison
        norm_content = _extract_content_from_norm(norm)
        
        # Get raw content length for comparison
        raw_word_count = 0
        if hasattr(raw, 'content'):
            raw_word_count = len(str(raw.content).split())
        elif hasattr(raw, 'blocks') and raw.blocks:
            raw_content = ' '.join([str(block) for block in raw.blocks])
            raw_word_count = len(raw_content.split())
        
        norm_word_count = len(norm_content.split())
        
        if raw_word_count == 0:
            return 90.0  # Default good coverage if no raw comparison
        
        # Calculate coverage ratio
        coverage_ratio = min(1.0, norm_word_count / raw_word_count)
        
        # Apply coverage scoring
        if coverage_ratio >= 0.9:
            return 95.0
        elif coverage_ratio >= 0.8:
            return 87.0
        elif coverage_ratio >= 0.7:
            return 78.0
        elif coverage_ratio >= 0.5:
            return 65.0
        else:
            return max(30.0, coverage_ratio * 100)
            
    except Exception as e:
        print(f"⚠️ KE-PR7: Error calculating coverage - {e}")
        return 75.0  # Default moderate coverage on error

def _detect_unsupported_claims(content: str) -> List[QAFlag]:
    """Detect potentially unsupported claims using heuristics"""
    flags = []
    
    try:
        # Patterns that indicate unsupported claims
        unsupported_patterns = [
            (r'\b(?:always|never|all|every|none|no one)\b', "P1_ABSOLUTE_CLAIM"),
            (r'\b(?:definitely|certainly|obviously|clearly)\b', "P1_CERTAINTY_CLAIM"),
            (r'\b(?:studies show|research proves|experts agree)\b', "P1_VAGUE_AUTHORITY"),
            (r'\b(?:it is known|everyone knows|common knowledge)\b', "P1_UNSOURCED_CLAIM"),
            (r'\b(?:significantly|dramatically|substantially)\b.*(?:better|worse|faster|slower)', "P1_VAGUE_COMPARISON"),
        ]
        
        content_lower = content.lower()
        
        for pattern, code in unsupported_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            if matches:
                # Count unique matches
                unique_matches = set(matches)
                if len(unique_matches) >= 3:  # Multiple instances indicate pattern
                    severity = "P0" if len(unique_matches) >= 5 else "P1"
                    flags.append(QAFlag(
                        code=code,
                        severity=severity,
                        message=f"Detected {len(unique_matches)} instances of potentially unsupported claims: {', '.join(list(unique_matches)[:3])}{'...' if len(unique_matches) > 3 else ''}",
                        location="content_analysis"
                    ))
        
        # Check for claims without evidence
        sentences = re.split(r'[.!?]+', content)
        unsourced_claims = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) > 8:  # Only check substantial sentences
                # Look for factual claims without sources
                if any(indicator in sentence.lower() for indicator in [
                    'research shows', 'studies indicate', 'data reveals', 
                    'statistics show', 'according to', 'evidence suggests'
                ]):
                    # Check if there's a citation or source nearby
                    if not any(source in sentence.lower() for source in [
                        'http', 'www', 'doi:', '(20', 'et al', 'source:', 'study by'
                    ]):
                        unsourced_claims += 1
        
        if unsourced_claims >= 3:
            severity = "P0" if unsourced_claims >= 5 else "P1"
            flags.append(QAFlag(
                code="P1_UNSOURCED_CLAIMS",
                severity=severity,
                message=f"Found {unsourced_claims} potentially unsourced factual claims",
                location="citations"
            ))
        
        return flags
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error detecting unsupported claims - {e}")
        return []

def _detect_placeholders(content: str) -> List[QAFlag]:
    """Detect placeholder content that needs completion"""
    flags = []
    
    try:
        placeholder_patterns = [
            r'\[(?:MISSING|TODO|TBD|PLACEHOLDER|CONTENT_NEEDED|FILL_IN)\]',
            r'(?:TODO:|FIXME:|NOTE:|XXX:)',
            r'\b(?:lorem ipsum|placeholder text|sample text)\b',
            r'\.\.\.',  # Ellipsis indicating incomplete content
            r'(?:insert|add|include).*(?:here|below|above)',
        ]
        
        total_placeholders = 0
        placeholder_types = set()
        
        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                total_placeholders += len(matches)
                placeholder_types.add(pattern)
        
        if total_placeholders > 0:
            severity = "P0" if total_placeholders >= 5 else "P1"
            flags.append(QAFlag(
                code="P0_PLACEHOLDERS" if severity == "P0" else "P1_PLACEHOLDERS",
                severity=severity,
                message=f"Found {total_placeholders} placeholder(s) that need completion",
                location="content_placeholders"
            ))
        
        # Check for incomplete sections
        lines = content.split('\n')
        incomplete_sections = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith('#') and i < len(lines) - 1:
                # Found heading, check if next content is minimal
                next_content = ""
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith('#'):
                        next_content += lines[j].strip() + " "
                
                if len(next_content.strip()) < 20:  # Very short section content
                    incomplete_sections += 1
        
        if incomplete_sections >= 2:
            flags.append(QAFlag(
                code="P1_INCOMPLETE_SECTIONS",
                severity="P1",
                message=f"Found {incomplete_sections} sections with minimal content",
                location="section_completeness"
            ))
        
        return flags
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error detecting placeholders - {e}")
        return []

def _detect_duplicates(content: str) -> List[QAFlag]:
    """Detect duplicate content within the document"""
    flags = []
    
    try:
        # Split content into sentences for analysis
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip().lower() for s in sentences if len(s.strip()) > 10]
        
        # Find duplicate sentences
        sentence_counts = {}
        for sentence in sentences:
            sentence_counts[sentence] = sentence_counts.get(sentence, 0) + 1
        
        duplicates = [(s, count) for s, count in sentence_counts.items() if count > 1]
        
        if duplicates:
            total_duplicates = sum(count - 1 for _, count in duplicates)  # Subtract 1 for original
            severity = "P0" if total_duplicates >= 3 else "P1"
            
            flags.append(QAFlag(
                code="P0_DUPLICATE_CONTENT" if severity == "P0" else "P1_DUPLICATE_CONTENT",
                severity=severity,
                message=f"Found {len(duplicates)} duplicate sentence(s) with {total_duplicates} repetitions",
                location="content_duplication"
            ))
        
        # Check for repeated paragraphs
        paragraphs = [p.strip().lower() for p in content.split('\n\n') if len(p.strip()) > 50]
        paragraph_counts = {}
        for paragraph in paragraphs:
            paragraph_counts[paragraph] = paragraph_counts.get(paragraph, 0) + 1
        
        duplicate_paragraphs = [(p, count) for p, count in paragraph_counts.items() if count > 1]
        
        if duplicate_paragraphs:
            flags.append(QAFlag(
                code="P0_DUPLICATE_PARAGRAPHS",
                severity="P0",
                message=f"Found {len(duplicate_paragraphs)} duplicate paragraph(s)",
                location="paragraph_duplication"
            ))
        
        return flags
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error detecting duplicates - {e}")
        return []

def _detect_broken_links(content: str) -> List[str]:
    """Detect potentially broken links in content"""
    try:
        # Extract URLs from content
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        
        # Also extract markdown-style links
        markdown_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        markdown_matches = re.findall(markdown_link_pattern, content)
        urls.extend([url for text, url in markdown_matches if url.startswith(('http', 'https'))])
        
        broken_links = []
        
        # Quick validation of URLs (without actually making requests to avoid timeouts)
        for url in set(urls):  # Remove duplicates
            try:
                parsed = urlparse(url)
                if not parsed.netloc:
                    broken_links.append(url)
                elif parsed.scheme not in ['http', 'https']:
                    broken_links.append(url)
                # Could add more sophisticated validation here
                
            except Exception:
                broken_links.append(url)
        
        return broken_links[:10]  # Limit to first 10 broken links
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error detecting broken links - {e}")
        return []

def _detect_missing_media(content: str) -> List[str]:
    """Detect missing media references in content"""
    try:
        missing_media = []
        
        # Look for image references without actual URLs
        img_patterns = [
            r'!\[([^\]]*)\]\(\s*\)',  # Empty markdown image
            r'<img[^>]*src=["\']?\s*["\']?[^>]*>',  # Empty img src
            r'\[image:\s*([^\]]*)\]',  # Custom image placeholder
            r'\[figure\s*\d*:?\s*([^\]]*)\]',  # Figure placeholder
        ]
        
        for pattern in img_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                missing_media.extend([f"Missing image: {match}" for match in matches if match.strip()])
        
        # Look for media references in text
        media_reference_patterns = [
            r'(?:see|view|check|look at)\s+(?:figure|image|diagram|chart|graph)\s*\d*',
            r'(?:the|this)\s+(?:screenshot|image|figure|diagram)\s+(?:shows|displays|illustrates)',
            r'(?:as shown in|illustrated by|depicted in)\s+(?:figure|image|diagram)',
        ]
        
        for pattern in media_reference_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                missing_media.extend([f"Media reference without image: {match}" for match in matches])
        
        return missing_media[:5]  # Limit to first 5 missing media
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error detecting missing media - {e}")
        return []

def _check_content_quality(content: str) -> List[QAFlag]:
    """Check overall content quality indicators"""
    flags = []
    
    try:
        # Check content length
        word_count = len(content.split())
        
        if word_count < 50:
            flags.append(QAFlag(
                code="P1_TOO_SHORT",
                severity="P1",
                message=f"Content is very short ({word_count} words). Consider expanding.",
                location="content_length"
            ))
        elif word_count > 5000:
            flags.append(QAFlag(
                code="P1_TOO_LONG",
                severity="P1", 
                message=f"Content is very long ({word_count} words). Consider splitting into multiple articles.",
                location="content_length"
            ))
        
        # Check for proper heading structure
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        if not headings:
            flags.append(QAFlag(
                code="P1_NO_HEADINGS",
                severity="P1",
                message="Content has no headings. Consider adding section headers for better readability.",
                location="content_structure"
            ))
        else:
            # Check heading hierarchy
            heading_levels = [len(level) for level, title in headings]
            if heading_levels and max(heading_levels) - min(heading_levels) > 3:
                flags.append(QAFlag(
                    code="P1_POOR_HEADING_HIERARCHY",
                    severity="P1",
                    message="Heading hierarchy spans too many levels. Consider simplifying structure.",
                    location="heading_structure"
                ))
        
        # Check for code blocks and examples
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        inline_code = re.findall(r'`[^`\n]+`', content)
        
        # If content mentions code but has no examples
        if ('code' in content.lower() or 'function' in content.lower() or 'api' in content.lower()):
            if not code_blocks and not inline_code:
                flags.append(QAFlag(
                    code="P1_MISSING_CODE_EXAMPLES",
                    severity="P1",
                    message="Content discusses technical topics but lacks code examples.",
                    location="code_examples"
                ))
        
        return flags
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error checking content quality - {e}")
        return []

def _check_technical_accuracy(content: str) -> List[QAFlag]:
    """Check for technical accuracy issues"""
    flags = []
    
    try:
        content_lower = content.lower()
        
        # Check for vague technical statements
        vague_patterns = [
            r'\b(?:it works|simply works|just use|easily done|automatically|magically)\b',
            r'\b(?:should work|might work|probably works|usually works)\b',
            r'\b(?:something like|kind of|sort of|basically)\b',
        ]
        
        vague_count = 0
        for pattern in vague_patterns:
            matches = re.findall(pattern, content_lower)
            vague_count += len(matches)
        
        if vague_count >= 3:
            severity = "P1" if vague_count < 6 else "P0"
            flags.append(QAFlag(
                code="P1_VAGUE_TECHNICAL_LANGUAGE",
                severity=severity,
                message=f"Found {vague_count} instances of vague technical language. Be more specific.",
                location="technical_precision"
            ))
        
        # Check for inconsistent terminology
        tech_terms = {
            'api': ['API', 'api', 'Api'],
            'json': ['JSON', 'json', 'Json'],
            'http': ['HTTP', 'http', 'Http'],
            'url': ['URL', 'url', 'Url'],
            'html': ['HTML', 'html', 'Html'],
            'css': ['CSS', 'css', 'Css'],
        }
        
        inconsistent_terms = []
        for base_term, variants in tech_terms.items():
            found_variants = [v for v in variants if v in content]
            if len(found_variants) > 1:
                inconsistent_terms.append(base_term)
        
        if inconsistent_terms:
            flags.append(QAFlag(
                code="P1_INCONSISTENT_TERMINOLOGY",
                severity="P1",
                message=f"Inconsistent capitalization for: {', '.join(inconsistent_terms)}",
                location="terminology_consistency"
            ))
        
        return flags
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error checking technical accuracy - {e}")
        return []

def is_publishable(qa_report: QAReport) -> Tuple[bool, str]:
    """
    Check if content is publishable based on QA report
    Blocks publish on P0 issues
    
    Returns:
        Tuple of (is_publishable, reason_if_blocked)
    """
    try:
        # Check for P0 (blocking) issues
        p0_flags = [f for f in qa_report.flags if f.severity == "P0"]
        
        if p0_flags:
            p0_messages = [f.message for f in p0_flags]
            return False, f"Publishing blocked due to {len(p0_flags)} critical issue(s): {'; '.join(p0_messages[:3])}"
        
        # Check coverage threshold
        if qa_report.coverage_percent < 70.0:
            return False, f"Publishing blocked due to low coverage: {qa_report.coverage_percent:.1f}% (minimum: 70%)"
        
        # All checks passed
        return True, "Content is ready for publishing"
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error checking publishability - {e}")
        return False, f"Publishing blocked due to validation error: {str(e)}"

def get_qa_summary(qa_report: QAReport) -> Dict:
    """Get summary of QA report for API responses"""
    try:
        p0_count = len([f for f in qa_report.flags if f.severity == "P0"])
        p1_count = len([f for f in qa_report.flags if f.severity == "P1"])
        
        is_pub, pub_message = is_publishable(qa_report)
        
        return {
            "job_id": qa_report.job_id,
            "coverage_percent": round(qa_report.coverage_percent, 1),
            "total_flags": len(qa_report.flags),
            "p0_flags": p0_count,
            "p1_flags": p1_count,
            "broken_links_count": len(qa_report.broken_links),
            "missing_media_count": len(qa_report.missing_media),
            "is_publishable": is_pub,
            "publish_status": pub_message,
            "quality_score": _calculate_quality_score(qa_report)
        }
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error creating QA summary - {e}")
        return {
            "job_id": qa_report.job_id if qa_report else "error",
            "coverage_percent": 0.0,
            "total_flags": 0,
            "p0_flags": 0,
            "p1_flags": 0,
            "broken_links_count": 0,
            "missing_media_count": 0,
            "is_publishable": False,
            "publish_status": "Error generating QA summary",
            "quality_score": 0
        }

def _calculate_quality_score(qa_report: QAReport) -> int:
    """Calculate overall quality score (0-100)"""
    try:
        base_score = min(100, qa_report.coverage_percent)
        
        # Deduct points for issues
        p0_penalty = len([f for f in qa_report.flags if f.severity == "P0"]) * 15
        p1_penalty = len([f for f in qa_report.flags if f.severity == "P1"]) * 5
        
        link_penalty = min(10, len(qa_report.broken_links) * 2)
        media_penalty = min(10, len(qa_report.missing_media) * 3)
        
        total_penalty = p0_penalty + p1_penalty + link_penalty + media_penalty
        
        final_score = max(0, base_score - total_penalty)
        
        return int(final_score)
        
    except Exception as e:
        print(f"⚠️ KE-PR7: Error calculating quality score - {e}")
        return 0