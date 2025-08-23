#!/usr/bin/env python3
"""
Debug WYSIWYG Compatibility - Check what LLM is actually generating
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://woolf-style-lint.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def get_latest_articles():
    """Get the latest articles to examine their content"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Get the most recent articles
            recent_articles = articles[:3]  # Get first 3 articles
            
            log_test_result(f"Found {len(recent_articles)} recent articles")
            
            for i, article in enumerate(recent_articles):
                title = article.get('title', 'Untitled')
                content = article.get('content', '')
                
                log_test_result(f"\n=== ARTICLE {i+1}: {title} ===")
                log_test_result(f"Content length: {len(content)} characters")
                
                # Check if wrapped in code block
                if content.strip().startswith('<pre><code class="language-html">'):
                    log_test_result("❌ CRITICAL ISSUE: Article wrapped in <pre><code class='language-html'>", "ERROR")
                    
                    # Show first 500 chars to see the structure
                    log_test_result("First 500 characters:")
                    print(content[:500])
                    print("...")
                    
                    # Show last 100 chars to see the ending
                    log_test_result("Last 100 characters:")
                    print("..." + content[-100:])
                    
                else:
                    log_test_result("✅ Article NOT wrapped in code block", "SUCCESS")
                    
                    # Show first 200 chars to see the structure
                    log_test_result("First 200 characters:")
                    print(content[:200])
                    print("...")
                
                log_test_result("=" * 60)
            
            return recent_articles
        else:
            log_test_result(f"❌ Content Library retrieval failed: Status {response.status_code}", "ERROR")
            return []
            
    except Exception as e:
        log_test_result(f"❌ Article retrieval failed: {e}", "ERROR")
        return []

def test_clean_function_directly():
    """Test the clean function directly with problematic content"""
    try:
        log_test_result("Testing clean_article_html_content function directly...")
        
        # Simulate problematic content that should be cleaned
        test_content = '''<pre><code class="language-html"><h2>Test Article</h2>
<p>This is test content that should not be wrapped in code blocks.</p>
<ul>
<li>Item 1</li>
<li>Item 2</li>
</ul>
<pre><code class="language-javascript">
function test() {
    console.log("This should remain in code block");
}
</code></pre>
</code></pre>'''
        
        log_test_result(f"Test content length: {len(test_content)} characters")
        log_test_result("Test content starts with:", test_content[:100])
        
        # Make a request to test the cleaning function
        # We'll need to create a simple endpoint or test this differently
        log_test_result("Note: Direct function testing would require backend modification")
        
    except Exception as e:
        log_test_result(f"❌ Direct function test failed: {e}", "ERROR")

if __name__ == "__main__":
    print("Debug WYSIWYG Compatibility Testing")
    print("=" * 50)
    
    # Get and examine latest articles
    articles = get_latest_articles()
    
    # Test clean function concept
    test_clean_function_directly()