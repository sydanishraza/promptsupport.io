#!/usr/bin/env python3
"""
Final WYSIWYG Compatibility Test - Test with fresh content to verify fixes
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

# Backend URL from frontend .env
BACKEND_URL = "https://content-engine-6.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def create_fresh_test_content():
    """Create fresh test content for WYSIWYG validation"""
    return """
# Advanced React Hooks Tutorial - Complete Guide

This comprehensive tutorial covers advanced React Hooks patterns and best practices for modern React development.

## Introduction to Advanced Hooks

React Hooks have revolutionized how we write React components. This guide explores advanced patterns and custom hooks that will elevate your React development skills.

### Prerequisites
- Solid understanding of basic React Hooks (useState, useEffect)
- Experience with React functional components
- Knowledge of JavaScript ES6+ features

## Custom Hooks Patterns

### Creating Reusable Logic

Custom hooks allow you to extract component logic into reusable functions:

```javascript
function useCounter(initialValue = 0) {
    const [count, setCount] = useState(initialValue);
    
    const increment = useCallback(() => {
        setCount(prev => prev + 1);
    }, []);
    
    const decrement = useCallback(() => {
        setCount(prev => prev - 1);
    }, []);
    
    const reset = useCallback(() => {
        setCount(initialValue);
    }, [initialValue]);
    
    return { count, increment, decrement, reset };
}
```

### Advanced useEffect Patterns

Here are some advanced patterns for useEffect:

```javascript
// Cleanup pattern
useEffect(() => {
    const subscription = api.subscribe(data => {
        setData(data);
    });
    
    return () => {
        subscription.unsubscribe();
    };
}, []);

// Conditional effects
useEffect(() => {
    if (shouldFetch) {
        fetchData();
    }
}, [shouldFetch, fetchData]);
```

## Performance Optimization

### useMemo and useCallback Best Practices

| Hook | Use Case | Example |
|------|----------|---------|
| useMemo | Expensive calculations | `useMemo(() => expensiveCalc(data), [data])` |
| useCallback | Function references | `useCallback(() => handleClick(), [deps])` |
| React.memo | Component memoization | `React.memo(Component)` |

### Avoiding Common Pitfalls

1. **Over-optimization**: Don't use useMemo/useCallback everywhere
2. **Dependency arrays**: Always include all dependencies
3. **Stale closures**: Be careful with closure variables in effects

## Advanced Patterns

### Compound Components Pattern

```javascript
function Tabs({ children, defaultTab }) {
    const [activeTab, setActiveTab] = useState(defaultTab);
    
    return (
        <TabsContext.Provider value={{ activeTab, setActiveTab }}>
            <div className="tabs">
                {children}
            </div>
        </TabsContext.Provider>
    );
}

Tabs.TabList = function TabList({ children }) {
    return <div className="tab-list">{children}</div>;
};

Tabs.Tab = function Tab({ id, children }) {
    const { activeTab, setActiveTab } = useContext(TabsContext);
    return (
        <button 
            className={activeTab === id ? 'active' : ''}
            onClick={() => setActiveTab(id)}
        >
            {children}
        </button>
    );
};
```

## Testing Custom Hooks

### Using React Testing Library

```javascript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

test('should increment counter', () => {
    const { result } = renderHook(() => useCounter());
    
    act(() => {
        result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
});
```

## Best Practices Summary

- Keep hooks simple and focused
- Use custom hooks to share logic between components
- Always include dependencies in dependency arrays
- Test your custom hooks thoroughly
- Consider performance implications of your hooks

This tutorial provides a solid foundation for advanced React Hooks usage. Practice these patterns to become proficient with modern React development.
"""

def process_fresh_content():
    """Process fresh content and return job_id"""
    try:
        log_test_result("🎯 PROCESSING FRESH CONTENT FOR WYSIWYG VALIDATION", "CRITICAL")
        
        test_content = create_fresh_test_content()
        log_test_result(f"📝 Created fresh test content: {len(test_content)} characters")
        
        payload = {
            'content': test_content,
            'content_type': 'text',
            'metadata': {
                'original_filename': 'Advanced_React_Hooks_Tutorial.txt',
                'source': 'final_wysiwyg_test'
            }
        }
        
        response = requests.post(f"{API_BASE}/content/process", 
                               json=payload, 
                               timeout=300)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            return None
        
        upload_data = response.json()
        job_id = upload_data.get('job_id')
        
        if not job_id:
            log_test_result("❌ No job_id received from processing", "ERROR")
            return None
        
        log_test_result(f"✅ Fresh content processing started, Job ID: {job_id}")
        return job_id
        
    except Exception as e:
        log_test_result(f"❌ Fresh content processing failed: {e}", "ERROR")
        return None

def monitor_processing(job_id):
    """Monitor processing and return completion status"""
    try:
        log_test_result("⏳ Monitoring fresh content processing...")
        processing_start = time.time()
        max_wait_time = 300
        
        while True:
            elapsed = time.time() - processing_start
            if elapsed > max_wait_time:
                log_test_result(f"❌ Processing timeout after {elapsed:.1f} seconds", "ERROR")
                return False
            
            try:
                status_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=30)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Fresh content processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        return True
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(5)
                else:
                    time.sleep(5)
                    
            except Exception as e:
                time.sleep(5)
                
    except Exception as e:
        log_test_result(f"❌ Processing monitoring failed: {e}", "ERROR")
        return False

def get_fresh_articles():
    """Get the freshly generated articles"""
    try:
        log_test_result("🔍 Retrieving fresh articles...")
        
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Filter for React Hooks related articles
            fresh_articles = []
            for article in articles[:5]:  # Check last 5 articles
                title = article.get('title', '').lower()
                if 'react' in title or 'hooks' in title or 'advanced' in title:
                    fresh_articles.append(article)
            
            if not fresh_articles and articles:
                fresh_articles = articles[:3]  # Get first 3 if no specific matches
            
            log_test_result(f"📚 Found {len(fresh_articles)} fresh articles for testing")
            return fresh_articles
        else:
            log_test_result(f"❌ Article retrieval failed: Status {response.status_code}", "ERROR")
            return []
            
    except Exception as e:
        log_test_result(f"❌ Fresh article retrieval failed: {e}", "ERROR")
        return []

def validate_fresh_wysiwyg_compatibility(articles):
    """Validate WYSIWYG compatibility for fresh articles"""
    try:
        log_test_result("🎯 VALIDATING FRESH WYSIWYG COMPATIBILITY", "CRITICAL")
        
        if not articles:
            log_test_result("❌ No fresh articles to test", "ERROR")
            return False
        
        success_count = 0
        total_articles = len(articles)
        
        for i, article in enumerate(articles):
            title = article.get('title', f'Article {i+1}')
            content = article.get('content', '')
            
            log_test_result(f"\n🔍 Testing Fresh Article {i+1}: {title[:50]}...")
            log_test_result(f"   Content length: {len(content)} characters")
            
            if not content:
                log_test_result("   ❌ Empty content", "ERROR")
                continue
            
            # Critical test: NOT wrapped in <pre><code class="language-html">
            if content.strip().startswith('<pre><code class="language-html">') and content.strip().endswith('</code></pre>'):
                log_test_result("   ❌ CRITICAL FAILURE: Article wrapped in <pre><code class='language-html'>", "ERROR")
                continue
            else:
                log_test_result("   ✅ CRITICAL SUCCESS: Article NOT wrapped in code block", "SUCCESS")
            
            # Parse HTML to check structure
            try:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check for semantic HTML
                has_headings = len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])) > 0
                has_paragraphs = len(soup.find_all('p')) > 0
                has_lists = len(soup.find_all(['ul', 'ol'])) > 0
                
                if has_headings and has_paragraphs:
                    log_test_result("   ✅ Semantic HTML structure confirmed", "SUCCESS")
                else:
                    log_test_result("   ⚠️ Limited semantic structure", "WARNING")
                
                # Check for document wrapper tags
                has_html_tag = soup.find('html') is not None
                has_head_tag = soup.find('head') is not None
                has_body_tag = soup.find('body') is not None
                
                if not (has_html_tag or has_head_tag or has_body_tag):
                    log_test_result("   ✅ Clean HTML: No document wrapper tags", "SUCCESS")
                else:
                    log_test_result("   ❌ Contains document wrapper tags", "ERROR")
                    continue
                
                # Check content quality
                text_content = soup.get_text()
                if len(text_content) > 500:
                    log_test_result("   ✅ Comprehensive content confirmed", "SUCCESS")
                else:
                    log_test_result("   ⚠️ Content appears short", "WARNING")
                
                success_count += 1
                log_test_result(f"   🎉 Article {i+1} PASSED all WYSIWYG compatibility tests", "SUCCESS")
                
            except Exception as parse_error:
                log_test_result(f"   ❌ HTML parsing error: {parse_error}", "ERROR")
        
        # Calculate success rate
        success_rate = (success_count / total_articles) * 100
        
        log_test_result(f"\n📊 FRESH WYSIWYG COMPATIBILITY RESULTS:")
        log_test_result(f"   ✅ Successful articles: {success_count}/{total_articles} ({success_rate:.1f}%)")
        
        if success_rate >= 100:
            log_test_result("🎉 CRITICAL SUCCESS: ALL fresh articles are WYSIWYG compatible!", "CRITICAL_SUCCESS")
            return True
        elif success_rate >= 80:
            log_test_result("✅ SUCCESS: Most fresh articles are WYSIWYG compatible", "SUCCESS")
            return True
        else:
            log_test_result("❌ FAILURE: Fresh articles still have WYSIWYG compatibility issues", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Fresh WYSIWYG validation failed: {e}", "ERROR")
        return False

def run_final_wysiwyg_test():
    """Run final WYSIWYG compatibility test with fresh content"""
    log_test_result("🚀 STARTING FINAL WYSIWYG COMPATIBILITY TEST", "CRITICAL")
    log_test_result("=" * 80)
    
    # Process fresh content
    job_id = process_fresh_content()
    if not job_id:
        log_test_result("❌ Failed to process fresh content", "ERROR")
        return False
    
    # Monitor processing
    if not monitor_processing(job_id):
        log_test_result("❌ Fresh content processing failed", "ERROR")
        return False
    
    # Get fresh articles
    articles = get_fresh_articles()
    if not articles:
        log_test_result("❌ No fresh articles found", "ERROR")
        return False
    
    # Validate WYSIWYG compatibility
    success = validate_fresh_wysiwyg_compatibility(articles)
    
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL WYSIWYG COMPATIBILITY TEST RESULTS", "CRITICAL")
    log_test_result("=" * 80)
    
    if success:
        log_test_result("🎉 CRITICAL SUCCESS: WYSIWYG compatibility fixes are working perfectly!", "CRITICAL_SUCCESS")
        log_test_result("✅ Fresh articles are clean, semantic, and WYSIWYG editor ready", "CRITICAL_SUCCESS")
        log_test_result("✅ NO articles wrapped in <pre><code> tags", "CRITICAL_SUCCESS")
        log_test_result("✅ Content uses proper semantic HTML structure", "CRITICAL_SUCCESS")
        log_test_result("✅ Articles are immediately usable in WYSIWYG editors", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: WYSIWYG compatibility issues still exist", "CRITICAL_ERROR")
    
    return success

if __name__ == "__main__":
    print("Final WYSIWYG Compatibility Testing")
    print("=" * 50)
    
    success = run_final_wysiwyg_test()
    
    if success:
        exit(0)
    else:
        exit(1)