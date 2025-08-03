#!/usr/bin/env python3
"""
Test to verify the markdown conversion issue
"""

import re

def convert_markdown_to_html(markdown_content: str) -> str:
    """
    Convert Markdown content to HTML for proper H1 detection
    Uses simple regex-based conversion for common patterns
    """
    try:
        html_content = markdown_content
        
        # Convert headers (most important for H1 detection)
        html_content = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#### (.*)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^##### (.*)$', r'<h5>\1</h5>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^###### (.*)$', r'<h6>\1</h6>', html_content, flags=re.MULTILINE)
        
        # Convert paragraphs (wrap non-tag lines in <p> tags)
        lines = html_content.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                processed_lines.append('')
            elif line.startswith('<h') or line.startswith('</'):
                processed_lines.append(line)
            elif not any(line.startswith(tag) for tag in ['<', '*', '-', '+']):
                # Wrap non-empty, non-header lines in paragraph tags
                processed_lines.append(f'<p>{line}</p>')
            else:
                processed_lines.append(line)
        
        html_content = '\n'.join(processed_lines)
        
        print(f"📝 Converted Markdown to HTML - {len(re.findall(r'<h1>', html_content))} H1 tags found")
        return html_content
        
    except Exception as e:
        print(f"❌ Markdown conversion failed: {e}")
        return markdown_content  # Return original if conversion fails

# Test the markdown content from our test
test_markdown = """# Introduction to Machine Learning Systems

Machine learning has revolutionized how we approach complex data problems. This comprehensive guide covers the fundamental concepts, implementation strategies, and best practices for building robust ML systems.

## Core Concepts
Machine learning systems rely on algorithms that can learn patterns from data without being explicitly programmed for every scenario.

# Deep Learning Architectures

Deep learning represents a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns in data.

## Neural Network Fundamentals
Neural networks consist of interconnected nodes (neurons) organized in layers that process information through weighted connections.

# Model Training and Optimization

Training machine learning models involves finding optimal parameters through iterative optimization processes.

## Loss Functions
Loss functions quantify the difference between predicted and actual outcomes, guiding the optimization process.

# Production Deployment Strategies

Deploying machine learning models to production requires careful consideration of scalability, monitoring, and maintenance.

## Model Serving Infrastructure
Production ML systems need robust infrastructure to handle real-time predictions and batch processing."""

print("🔍 MARKDOWN CONVERSION TEST")
print("=" * 50)
print("Original markdown content:")
print(f"H1 sections (# headers): {test_markdown.count('# ')}")
print(f"HTML H1 tags: {test_markdown.count('<h1>')}")

print("\nAfter conversion:")
converted = convert_markdown_to_html(test_markdown)
print(f"H1 sections (# headers): {converted.count('# ')}")
print(f"HTML H1 tags: {converted.count('<h1>')}")

print("\nConverted content preview:")
print(converted[:500] + "...")

# Test the chunking logic
if '<h1>' in converted:
    sections = converted.split('<h1>')
    print(f"\nChunking test: {len(sections)} sections would be created")
    for i, section in enumerate(sections[:3]):  # Show first 3
        if section.strip():
            print(f"Section {i}: {section[:100]}...")
else:
    print("\nChunking test: No H1 tags found - would create single article")