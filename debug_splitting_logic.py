#!/usr/bin/env python3
"""
Debug the should_split_into_multiple_articles function
"""

# Test content from the review request
MULTI_SECTION_TEST_CONTENT = """# Enterprise Software Documentation

## Chapter 1: System Architecture Overview
This chapter covers the foundational architecture of our enterprise software platform, including core components, data flow patterns, and integration points that form the backbone of the system.

### Core Components
- Authentication Service
- Data Processing Engine  
- User Interface Layer
- Database Management System
- API Gateway

### Integration Patterns
The system uses microservices architecture with event-driven communication patterns.

## Chapter 2: User Management and Authentication
Comprehensive guide to user management, role-based access control, and authentication mechanisms implemented throughout the platform.

### Authentication Methods
- Single Sign-On (SSO)
- Multi-Factor Authentication (MFA)
- OAuth 2.0/OpenID Connect
- LDAP Integration

### Role Management
Define and manage user roles with granular permissions."""

def debug_splitting_logic(content: str, file_extension: str = "md") -> bool:
    """Debug version of should_split_into_multiple_articles function"""
    print(f"🔍 Debugging splitting logic for content ({len(content)} characters)")
    print(f"File extension: {file_extension}")
    
    # Enhanced rules for splitting - more permissive to enable better content generation
    if len(content) < 1000:  # Lowered threshold
        print(f"❌ Content too short: {len(content)} < 1000")
        return False
    else:
        print(f"✅ Content length check passed: {len(content)} >= 1000")
    
    # Always split presentations
    if file_extension in ['ppt', 'pptx']:
        print(f"✅ Presentation file - auto split")
        return True
    
    # Always split multi-sheet spreadsheets
    if file_extension in ['xls', 'xlsx'] and 'Sheet:' in content:
        print(f"✅ Multi-sheet spreadsheet - auto split")
        return True
    
    # Check for multiple headings/sections (more comprehensive patterns)
    heading_patterns = [
        '===', '##', '# ', 
        'Chapter', 'Section', 'Part ', 'Module',
        'Overview', 'Introduction', 'Conclusion',
        'Getting Started', 'Configuration', 'Setup',
        'Administration', 'Management', 'Process',
        'Step ', 'Phase ', 'Stage '
    ]
    
    heading_count = 0
    content_lower = content.lower()
    
    print(f"\n📊 Heading pattern analysis:")
    for pattern in heading_patterns:
        count = content_lower.count(pattern.lower())
        if count > 0:
            print(f"  '{pattern}': {count} occurrences")
        heading_count += count
    
    print(f"Total heading count: {heading_count}")
    
    # Check for document structure indicators
    has_table_of_contents = any(toc in content_lower for toc in ['table of contents', 'contents:', 'index:'])
    has_multiple_sections = content.count('\n\n') > 10  # Multiple paragraph breaks
    has_enumerated_sections = len([line for line in content.split('\n') if line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]) > 3
    
    double_newline_count = content.count('\n\n')
    print(f"\n📋 Structure indicators:")
    print(f"  Table of contents: {has_table_of_contents}")
    print(f"  Multiple sections (>10 paragraph breaks): {has_multiple_sections} (found {double_newline_count} breaks)")
    print(f"  Enumerated sections: {has_enumerated_sections}")
    
    # More permissive splitting logic
    should_split = (
        heading_count >= 2 or  # Just 2 headings needed
        has_table_of_contents or
        (has_multiple_sections and len(content) > 2000) or
        has_enumerated_sections or
        len(content) > 8000  # Very long documents should always be split
    )
    
    print(f"\n🎯 Splitting decision logic:")
    print(f"  heading_count >= 2: {heading_count >= 2} ({heading_count} >= 2)")
    print(f"  has_table_of_contents: {has_table_of_contents}")
    print(f"  has_multiple_sections AND len > 2000: {has_multiple_sections and len(content) > 2000}")
    print(f"  has_enumerated_sections: {has_enumerated_sections}")
    print(f"  len(content) > 8000: {len(content) > 8000} ({len(content)} > 8000)")
    
    print(f"\n🏁 FINAL DECISION: {'SPLIT' if should_split else 'NO SPLIT'}")
    
    return should_split

if __name__ == "__main__":
    print("🚀 Debugging Multi-Article Splitting Logic")
    print("=" * 60)
    
    result = debug_splitting_logic(MULTI_SECTION_TEST_CONTENT)
    
    print(f"\nResult: {result}")
    
    if not result:
        print("\n🔧 RECOMMENDATIONS:")
        print("1. The content has 'Chapter' patterns but may need more heading indicators")
        print("2. Consider adding more paragraph breaks or enumerated sections")
        print("3. The content might be processed as a single comprehensive article instead")