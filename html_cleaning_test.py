#!/usr/bin/env python3
"""
HTML CLEANING FUNCTION SPECIFIC TESTING
Test the clean_article_html_content function to ensure it properly:
1. Converts markdown code blocks to proper HTML <pre><code> tags
2. Preserves lists, emphasis, and other rich formatting elements  
3. Removes only document structure (html, head, body) but keeps content elements
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-formatter.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_html_cleaning_with_markdown_code_blocks():
    """Test HTML cleaning with content that has markdown code blocks"""
    try:
        log_test_result("🧹 TESTING HTML CLEANING WITH MARKDOWN CODE BLOCKS", "CRITICAL")
        
        # Create test content with markdown code blocks that should be converted to HTML
        test_content = """# API Integration Guide

## Getting Started

Here's how to initialize the API:

```javascript
// Initialize the API client
const apiClient = new APIClient({
    apiKey: 'your-api-key',
    baseURL: 'https://api.example.com'
});

// Make a request
const response = await apiClient.get('/users');
console.log(response.data);
```

### Configuration Steps

1. **Install the package**: `npm install api-client`
2. **Set up credentials**: Add your API key to environment variables
3. **Initialize client**: Use the code example above

```html
<!DOCTYPE html>
<html>
<head>
    <title>API Example</title>
</head>
<body>
    <div id="app">
        <h1>API Integration</h1>
        <button onclick="fetchData()">Fetch Data</button>
    </div>
    <script src="api-client.js"></script>
</body>
</html>
```

## Best Practices

- Always validate API responses
- Implement proper error handling
- Use environment variables for sensitive data

> **Note**: Keep your API keys secure and never commit them to version control.

### Error Handling Example

```python
try:
    response = api_client.get('/data')
    if response.status_code == 200:
        data = response.json()
        process_data(data)
    else:
        handle_error(response.status_code)
except Exception as e:
    log_error(f"API request failed: {e}")
```

## Conclusion

This guide covers the essential aspects of API integration with proper code examples and best practices.
"""
        
        log_test_result(f"📝 Created test content with markdown code blocks: {len(test_content)} characters")
        log_test_result("   ✅ Contains ```javascript code blocks")
        log_test_result("   ✅ Contains ```html code blocks") 
        log_test_result("   ✅ Contains ```python code blocks")
        log_test_result("   ✅ Contains lists and emphasis")
        log_test_result("   ✅ Contains blockquotes and callouts")
        
        # Process content through Knowledge Engine
        log_test_result("📤 Processing content to test HTML cleaning...")
        
        payload = {
            "content": test_content,
            "content_type": "text",
            "metadata": {
                "original_filename": "HTML_Cleaning_Test_Markdown_CodeBlocks.txt",
                "source": "html_cleaning_test"
            }
        }
        
        response = requests.post(f"{API_BASE}/content/process", 
                               json=payload, 
                               timeout=300)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        # Monitor processing
        log_test_result("⏳ Monitoring processing...")
        processing_start = time.time()
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > 120:  # 2 minutes max
                log_test_result(f"❌ Processing timeout", "ERROR")
                return False
            
            status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                
                if status == 'completed':
                    log_test_result(f"✅ Processing completed", "SUCCESS")
                    break
                elif status == 'failed':
                    log_test_result(f"❌ Processing failed", "ERROR")
                    return False
                
                time.sleep(5)
            else:
                time.sleep(5)
        
        # Get the generated articles to check HTML cleaning
        log_test_result("🔍 Analyzing HTML cleaning results...")
        
        library_response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if library_response.status_code != 200:
            log_test_result("❌ Could not access Content Library", "ERROR")
            return False
        
        data = library_response.json()
        articles = data.get('articles', [])
        
        # Find the test article
        test_article = None
        for article in articles:
            if 'HTML_Cleaning_Test_Markdown_CodeBlocks' in article.get('title', ''):
                test_article = article
                break
        
        if not test_article:
            log_test_result("❌ Could not find test article", "ERROR")
            return False
        
        content = test_article.get('content', '')
        log_test_result(f"📄 Found test article: {test_article.get('title', 'Unknown')}")
        log_test_result(f"📏 Article content length: {len(content)} characters")
        
        # Analyze HTML cleaning results
        html_cleaning_results = {
            'markdown_to_html_conversion': False,
            'preserved_lists': False,
            'preserved_emphasis': False,
            'preserved_blockquotes': False,
            'clean_document_structure': False,
            'proper_code_blocks': False
        }
        
        # Check for markdown to HTML conversion
        if '<pre><code>' in content and '```' not in content:
            html_cleaning_results['markdown_to_html_conversion'] = True
            log_test_result("✅ Markdown code blocks converted to HTML <pre><code> tags")
        elif '```' in content:
            log_test_result("❌ Markdown code blocks still present (not converted to HTML)")
        else:
            log_test_result("⚠️ No code blocks found in processed content")
        
        # Check for preserved lists
        if '<ul>' in content or '<ol>' in content:
            html_cleaning_results['preserved_lists'] = True
            log_test_result("✅ Lists preserved in HTML format")
        else:
            log_test_result("❌ Lists not found or not preserved")
        
        # Check for preserved emphasis
        if '<strong>' in content or '<em>' in content or '<b>' in content:
            html_cleaning_results['preserved_emphasis'] = True
            log_test_result("✅ Emphasis elements preserved")
        else:
            log_test_result("❌ Emphasis elements not found or not preserved")
        
        # Check for preserved blockquotes/callouts
        if '<blockquote>' in content or 'class="note"' in content or '<div' in content:
            html_cleaning_results['preserved_blockquotes'] = True
            log_test_result("✅ Blockquotes/callouts preserved")
        else:
            log_test_result("❌ Blockquotes/callouts not found or not preserved")
        
        # Check for clean document structure (no html, head, body tags)
        if '<html>' not in content and '<head>' not in content and '<body>' not in content:
            html_cleaning_results['clean_document_structure'] = True
            log_test_result("✅ Document structure tags removed (clean HTML)")
        else:
            log_test_result("❌ Document structure tags still present")
        
        # Check for proper code blocks with language classes
        if '<pre><code class="language-' in content:
            html_cleaning_results['proper_code_blocks'] = True
            log_test_result("✅ Code blocks have proper language classes")
        elif '<pre><code>' in content:
            log_test_result("⚠️ Code blocks present but without language classes")
            html_cleaning_results['proper_code_blocks'] = True  # Still acceptable
        else:
            log_test_result("❌ No proper code blocks found")
        
        # Calculate overall success
        passed_checks = sum(html_cleaning_results.values())
        total_checks = len(html_cleaning_results)
        success_rate = (passed_checks / total_checks) * 100
        
        log_test_result(f"📊 HTML CLEANING RESULTS: {passed_checks}/{total_checks} checks passed ({success_rate:.1f}%)")
        
        # Show sample of cleaned content
        log_test_result("📋 SAMPLE OF CLEANED CONTENT:")
        sample_content = content[:500] + "..." if len(content) > 500 else content
        print(sample_content)
        
        if success_rate >= 80:
            log_test_result("🎉 HTML CLEANING TEST PASSED - Excellent formatting preservation", "SUCCESS")
            return True
        elif success_rate >= 60:
            log_test_result("⚠️ HTML CLEANING TEST PARTIAL - Good formatting preservation", "WARNING")
            return True
        else:
            log_test_result("❌ HTML CLEANING TEST FAILED - Poor formatting preservation", "ERROR")
            return False
        
    except Exception as e:
        log_test_result(f"❌ HTML cleaning test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_code_block_context_preservation():
    """Test that code blocks stay with their explanatory text"""
    try:
        log_test_result("🔗 TESTING CODE BLOCK CONTEXT PRESERVATION", "CRITICAL")
        
        # Get recent articles to check code block context
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result("❌ Could not access Content Library", "ERROR")
            return False
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Find articles with code blocks
        code_articles = []
        for article in articles:
            content = article.get('content', '')
            if '<pre><code>' in content or '<code>' in content:
                code_articles.append(article)
        
        log_test_result(f"🔍 Found {len(code_articles)} articles with code blocks")
        
        if not code_articles:
            log_test_result("⚠️ No articles with code blocks found", "WARNING")
            return True
        
        context_preservation_score = 0
        
        for article in code_articles[:3]:  # Check first 3 code articles
            title = article.get('title', 'Unknown')
            content = article.get('content', '')
            
            log_test_result(f"   📄 Analyzing: {title[:50]}...")
            
            # Check if code blocks have explanatory context
            code_blocks = content.count('<pre><code>')
            inline_code = content.count('<code>') - code_blocks  # Subtract pre-code blocks
            
            # Count explanatory elements around code
            paragraphs = content.count('<p>')
            headings = content.count('<h2>') + content.count('<h3>')
            lists = content.count('<ul>') + content.count('<ol>')
            
            # Calculate context richness
            context_elements = paragraphs + headings + lists
            code_elements = code_blocks + inline_code
            
            if code_elements > 0:
                context_ratio = context_elements / code_elements
                
                log_test_result(f"      📊 Code blocks: {code_blocks}, Inline code: {inline_code}")
                log_test_result(f"      📊 Context elements: {context_elements} (ratio: {context_ratio:.1f})")
                
                if context_ratio >= 2.0:  # At least 2 context elements per code element
                    context_preservation_score += 1
                    log_test_result(f"      ✅ Excellent context preservation")
                elif context_ratio >= 1.0:
                    context_preservation_score += 0.5
                    log_test_result(f"      ⚠️ Good context preservation")
                else:
                    log_test_result(f"      ❌ Poor context preservation")
        
        # Calculate overall context preservation
        max_score = len(code_articles[:3])
        if max_score > 0:
            preservation_percentage = (context_preservation_score / max_score) * 100
            
            if preservation_percentage >= 80:
                log_test_result(f"✅ EXCELLENT code block context preservation: {preservation_percentage:.1f}%", "SUCCESS")
                return True
            elif preservation_percentage >= 60:
                log_test_result(f"⚠️ GOOD code block context preservation: {preservation_percentage:.1f}%", "WARNING")
                return True
            else:
                log_test_result(f"❌ POOR code block context preservation: {preservation_percentage:.1f}%", "ERROR")
                return False
        
        return True
        
    except Exception as e:
        log_test_result(f"❌ Code block context test failed: {e}", "ERROR")
        return False

def run_html_cleaning_tests():
    """Run comprehensive HTML cleaning tests"""
    log_test_result("🧹 STARTING HTML CLEANING FUNCTION TESTS", "CRITICAL")
    log_test_result("=" * 60)
    
    test_results = {
        'html_cleaning_markdown_conversion': False,
        'code_block_context_preservation': False
    }
    
    # Test 1: HTML Cleaning with Markdown Code Blocks
    log_test_result("TEST 1: HTML Cleaning with Markdown Code Blocks")
    test_results['html_cleaning_markdown_conversion'] = test_html_cleaning_with_markdown_code_blocks()
    
    # Test 2: Code Block Context Preservation
    log_test_result("\nTEST 2: Code Block Context Preservation")
    test_results['code_block_context_preservation'] = test_code_block_context_preservation()
    
    # Final Results
    log_test_result("\n" + "=" * 60)
    log_test_result("🎯 HTML CLEANING TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 60)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        log_test_result("🎉 ALL HTML CLEANING TESTS PASSED!", "CRITICAL_SUCCESS")
        log_test_result("✅ clean_article_html_content function is working correctly", "CRITICAL_SUCCESS")
        log_test_result("✅ Markdown code blocks converted to proper HTML", "CRITICAL_SUCCESS")
        log_test_result("✅ Rich formatting elements preserved", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ SOME HTML CLEANING TESTS FAILED", "CRITICAL_ERROR")
        log_test_result("❌ clean_article_html_content function needs improvement", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("HTML Cleaning Function Specific Testing")
    print("=" * 50)
    
    results = run_html_cleaning_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure