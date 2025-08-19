#!/usr/bin/env python3
"""
Test the clean_article_html_content function directly
"""

import re

def clean_article_html_content(content: str) -> str:
    """Clean HTML content to remove document structure while preserving rich formatting - WYSIWYG OPTIMIZED"""
    import re
    
    # CRITICAL FIX 1: Remove markdown HTML code block wrappers that break WYSIWYG editors
    if content.strip().startswith('```html'):
        print(f"🚨 CRITICAL FIX: Removing markdown HTML code block wrapper")
        content = content.strip()
        # Remove opening ```html
        content = re.sub(r'^```html\s*', '', content)
        # Remove closing ```
        content = re.sub(r'\s*```$', '', content)
    
    # CRITICAL FIX 2: Remove any full-article code block wrapping that breaks WYSIWYG editors
    if content.strip().startswith('<pre><code class="language-html">') and content.strip().endswith('</code></pre>'):
        print(f"🚨 CRITICAL FIX: Removing WYSIWYG-breaking code block wrapper")
        content = content.strip()
        content = content.replace('<pre><code class="language-html">', '', 1)
        content = content.rsplit('</code></pre>', 1)[0]
    
    # Remove any other variations of full-article wrapping
    content = re.sub(r'^<pre><code[^>]*>(.*)</code></pre>$', r'\1', content, flags=re.DOTALL)
    
    # ENHANCED FIX 3: Remove HTML document structure elements
    content = re.sub(r'<!DOCTYPE[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</?html[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</?head[^>]*>', '', content, flags=re.IGNORECASE) 
    content = re.sub(r'</?body[^>]*>', '', content, flags=re.IGNORECASE)
    
    # Additional cleaning specific to article content
    # Remove only document structure elements, preserve content elements
    content = re.sub(r'<meta[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<link[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up excessive whitespace but preserve code block formatting
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    content = re.sub(r'^\s+|\s+$', '', content)
    
    return content

# Test with the actual content from the article
test_content = """```html
<h2>Overview of the Google Cloud Platform Guide</h2>
<p>This guide serves as a comprehensive resource for users looking to navigate the Google Cloud Platform (GCP). It provides essential information on setting up an account, configuring services, and understanding the features available within GCP.</p>
<h3>Key Highlights and Benefits</h3>
<ul class="doc-list">
<li>Access to a wide range of cloud services tailored for various needs.</li>
<li>Step-by-step guidance on account creation and configuration.</li>
<li>Insights into advanced customization options for experienced users.</li>
<li>Solutions to common troubleshooting issues encountered on the platform.</li>
</ul>
```"""

print("Original content:")
print(repr(test_content))
print("\nCleaned content:")
cleaned = clean_article_html_content(test_content)
print(repr(cleaned))
print("\nFinal content:")
print(cleaned)