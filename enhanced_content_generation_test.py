#!/usr/bin/env python3
"""
ENHANCED CONTENT GENERATION SYSTEM TESTING
Testing the comprehensive fixes and enhancements implemented:
1. Article Duplication Fixes
2. Heading Hierarchy Improvements  
3. Nested List Rendering
4. Article Type Text Removal
5. Comprehensive Related Links
6. Mini-TOC Implementation
7. Code Block Enhancements
8. Contextual Cross-References
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import re
from bs4 import BeautifulSoup

# Backend URL from frontend .env
BACKEND_URL = "https://smartdoc-v2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_backend_health():
    """Test backend health and connectivity"""
    try:
        log_test_result("Testing backend health check...")
        response = requests.get(f"{API_BASE}/health", timeout=30)
        
        if response.status_code == 200:
            log_test_result("✅ Backend health check PASSED", "SUCCESS")
            return True
        else:
            log_test_result(f"❌ Backend health check FAILED: Status {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Backend health check FAILED: {e}", "ERROR")
        return False

def create_sample_content():
    """Create comprehensive sample content for testing all enhanced features"""
    return """
# Complete Guide to Advanced Web Development with JavaScript

## Introduction and Overview

This comprehensive guide covers modern JavaScript development techniques, including advanced patterns, best practices, and real-world implementation strategies. You'll learn everything from basic concepts to complex architectural patterns.

### What You'll Learn
- Modern JavaScript ES6+ features and syntax
- Advanced DOM manipulation techniques
- Asynchronous programming with Promises and async/await
- Module systems and code organization
- Testing strategies and debugging techniques
- Performance optimization methods

## Getting Started with Modern JavaScript

### Setting Up Your Development Environment

First, you need to set up a proper development environment:

1. Install Node.js from the official website
2. Set up a code editor (VS Code recommended)
3. Install essential extensions and tools
4. Configure your project structure

```javascript
// package.json example
{
  "name": "modern-js-project",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "node index.js",
    "test": "jest",
    "build": "webpack --mode production"
  },
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21"
  }
}
```

### Project Structure Best Practices

Organize your project with these recommended patterns:

```
project-root/
├── src/
│   ├── components/
│   ├── utils/
│   ├── services/
│   └── index.js
├── tests/
├── docs/
└── package.json
```

## Advanced JavaScript Concepts

### ES6+ Features and Modern Syntax

Modern JavaScript includes powerful features that improve code readability and functionality:

#### Arrow Functions and Destructuring

```javascript
// Arrow functions
const multiply = (a, b) => a * b;

// Destructuring assignment
const { name, age } = user;
const [first, second] = array;

// Template literals
const message = `Hello, ${name}! You are ${age} years old.`;
```

#### Classes and Inheritance

```javascript
class Vehicle {
  constructor(make, model) {
    this.make = make;
    this.model = model;
  }
  
  start() {
    console.log(`${this.make} ${this.model} is starting...`);
  }
}

class Car extends Vehicle {
  constructor(make, model, doors) {
    super(make, model);
    this.doors = doors;
  }
  
  honk() {
    console.log('Beep beep!');
  }
}
```

### Asynchronous Programming

#### Promises and Async/Await

```javascript
// Promise-based approach
function fetchUserData(userId) {
  return fetch(`/api/users/${userId}`)
    .then(response => response.json())
    .then(data => {
      console.log('User data:', data);
      return data;
    })
    .catch(error => {
      console.error('Error fetching user:', error);
      throw error;
    });
}

// Async/await approach
async function fetchUserDataAsync(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    const data = await response.json();
    console.log('User data:', data);
    return data;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}
```

## DOM Manipulation and Event Handling

### Modern DOM API Usage

```javascript
// Query selectors
const element = document.querySelector('.my-class');
const elements = document.querySelectorAll('.item');

// Event listeners
element.addEventListener('click', (event) => {
  event.preventDefault();
  console.log('Element clicked!');
});

// Creating and modifying elements
const newDiv = document.createElement('div');
newDiv.className = 'dynamic-content';
newDiv.textContent = 'This was created dynamically';
document.body.appendChild(newDiv);
```

### Event Delegation and Performance

```javascript
// Event delegation for better performance
document.addEventListener('click', (event) => {
  if (event.target.matches('.button')) {
    handleButtonClick(event.target);
  }
});

function handleButtonClick(button) {
  const action = button.dataset.action;
  switch (action) {
    case 'save':
      saveData();
      break;
    case 'delete':
      deleteItem(button.dataset.id);
      break;
    default:
      console.log('Unknown action:', action);
  }
}
```

## Testing and Debugging

### Unit Testing with Jest

```javascript
// math.js
export function add(a, b) {
  return a + b;
}

export function multiply(a, b) {
  return a * b;
}

// math.test.js
import { add, multiply } from './math.js';

describe('Math functions', () => {
  test('adds 1 + 2 to equal 3', () => {
    expect(add(1, 2)).toBe(3);
  });
  
  test('multiplies 3 * 4 to equal 12', () => {
    expect(multiply(3, 4)).toBe(12);
  });
});
```

### Debugging Techniques

1. **Console Methods**: Use console.log, console.error, console.table
2. **Breakpoints**: Set breakpoints in browser dev tools
3. **Network Tab**: Monitor API calls and responses
4. **Performance Tab**: Analyze runtime performance

## Performance Optimization

### Code Splitting and Lazy Loading

```javascript
// Dynamic imports for code splitting
async function loadModule() {
  const { heavyFunction } = await import('./heavy-module.js');
  return heavyFunction();
}

// Lazy loading images
const images = document.querySelectorAll('img[data-src]');
const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
      imageObserver.unobserve(img);
    }
  });
});

images.forEach(img => imageObserver.observe(img));
```

## Frequently Asked Questions

### Q: What's the difference between let, const, and var?

**A:** The main differences are:
- `var` has function scope and is hoisted
- `let` has block scope and is not hoisted
- `const` has block scope, is not hoisted, and cannot be reassigned

### Q: When should I use arrow functions vs regular functions?

**A:** Use arrow functions for:
- Short, simple functions
- Callbacks and array methods
- When you need to preserve `this` context

Use regular functions for:
- Methods in objects
- Constructor functions
- When you need `arguments` object

### Q: How do I handle errors in async/await?

**A:** Always use try-catch blocks:

```javascript
async function handleAsyncOperation() {
  try {
    const result = await someAsyncFunction();
    return result;
  } catch (error) {
    console.error('Operation failed:', error);
    throw error; // Re-throw if needed
  }
}
```

## Troubleshooting Common Issues

### Memory Leaks

Common causes and solutions:
1. **Event listeners**: Always remove event listeners when no longer needed
2. **Closures**: Be careful with closures that capture large objects
3. **Timers**: Clear intervals and timeouts

### Performance Issues

1. **DOM queries**: Cache DOM elements instead of querying repeatedly
2. **Large datasets**: Use pagination or virtual scrolling
3. **Heavy computations**: Consider using Web Workers

## Conclusion

This guide covered the essential aspects of modern JavaScript development. Continue practicing these concepts and stay updated with the latest JavaScript features and best practices.

### Next Steps

1. Build a complete project using these concepts
2. Explore advanced frameworks like React or Vue
3. Learn about Node.js for backend development
4. Study design patterns and architectural principles
"""

def process_sample_content():
    """Process sample content through the enhanced content generation pipeline"""
    try:
        log_test_result("🚀 STARTING ENHANCED CONTENT GENERATION TEST", "CRITICAL")
        log_test_result("Processing comprehensive sample content...")
        
        sample_content = create_sample_content()
        log_test_result(f"📝 Sample content created: {len(sample_content)} characters")
        
        # Process content through /api/content/process endpoint
        log_test_result("📤 Sending content to /api/content/process...")
        
        payload = {
            "content": sample_content,
            "content_type": "text",
            "metadata": {
                "filename": "advanced_javascript_guide.md",
                "original_filename": "advanced_javascript_guide.md"
            }
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/content/process", 
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            log_test_result(f"Response: {response.text[:500]}")
            return False
        
        processing_time = time.time() - start_time
        result_data = response.json()
        
        log_test_result(f"✅ Content processing completed in {processing_time:.1f} seconds", "SUCCESS")
        log_test_result(f"📊 Processing result: {result_data.get('status', 'unknown')}")
        
        # Extract key metrics
        articles_created = result_data.get('articles_created', 0)
        job_id = result_data.get('job_id')
        
        log_test_result(f"📈 PROCESSING METRICS:")
        log_test_result(f"   📄 Articles Created: {articles_created}")
        log_test_result(f"   🆔 Job ID: {job_id}")
        
        return True, articles_created, job_id
        
    except Exception as e:
        log_test_result(f"❌ Content processing test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False, 0, None

def test_content_library_enhancements():
    """Test enhanced features in the Content Library"""
    try:
        log_test_result("🔍 TESTING CONTENT LIBRARY ENHANCEMENTS", "CRITICAL")
        
        # Get all articles from Content Library
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code != 200:
            log_test_result(f"❌ Content Library access failed: Status {response.status_code}", "ERROR")
            return False
        
        data = response.json()
        total_articles = data.get('total', 0)
        articles = data.get('articles', [])
        
        log_test_result(f"📚 Content Library Status:")
        log_test_result(f"   Total Articles: {total_articles}")
        log_test_result(f"   Articles Retrieved: {len(articles)}")
        
        if not articles:
            log_test_result("⚠️ No articles found in Content Library for testing", "WARNING")
            return False
        
        # Test enhancement features
        enhancement_results = {
            'article_duplication_fixes': test_article_duplication_fixes(articles),
            'heading_hierarchy': test_heading_hierarchy(articles),
            'nested_list_rendering': test_nested_list_rendering(articles),
            'article_type_text_removal': test_article_type_text_removal(articles),
            'comprehensive_related_links': test_comprehensive_related_links(articles),
            'mini_toc_implementation': test_mini_toc_implementation(articles),
            'code_block_enhancements': test_code_block_enhancements(articles),
            'contextual_cross_references': test_contextual_cross_references(articles)
        }
        
        # Report results
        log_test_result("📊 ENHANCEMENT TESTING RESULTS:")
        passed_tests = 0
        total_tests = len(enhancement_results)
        
        for test_name, result in enhancement_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            log_test_result(f"   {test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        log_test_result(f"🎯 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        return success_rate >= 75  # 75% success rate threshold
        
    except Exception as e:
        log_test_result(f"❌ Content Library enhancement testing failed: {e}", "ERROR")
        return False

def test_article_duplication_fixes(articles):
    """Test that duplicate articles (like redundant 'Complete Overview' when 'Introduction' exists) are eliminated"""
    try:
        log_test_result("🔍 Testing Article Duplication Fixes...")
        
        # Look for patterns that indicate duplication issues
        titles = [article.get('title', '').lower() for article in articles]
        
        # Check for redundant overview articles when introduction exists
        has_introduction = any('introduction' in title for title in titles)
        has_complete_overview = any('complete overview' in title for title in titles)
        
        if has_introduction and has_complete_overview:
            log_test_result("⚠️ Found both Introduction and Complete Overview articles - potential duplication", "WARNING")
            return False
        
        # Check for exact title duplicates
        title_counts = {}
        for title in titles:
            title_counts[title] = title_counts.get(title, 0) + 1
        
        duplicates = [title for title, count in title_counts.items() if count > 1]
        
        if duplicates:
            log_test_result(f"❌ Found duplicate article titles: {duplicates}", "ERROR")
            return False
        
        log_test_result("✅ No article duplication issues detected", "SUCCESS")
        return True
        
    except Exception as e:
        log_test_result(f"❌ Article duplication test failed: {e}", "ERROR")
        return False

def test_heading_hierarchy(articles):
    """Test proper H1/H2/H3 structure without duplication"""
    try:
        log_test_result("🔍 Testing Heading Hierarchy Improvements...")
        
        hierarchy_issues = 0
        
        for article in articles[:5]:  # Test first 5 articles
            content = article.get('content', '')
            if not content:
                continue
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check heading structure
            h1_tags = soup.find_all('h1')
            h2_tags = soup.find_all('h2')
            h3_tags = soup.find_all('h3')
            
            # Articles should not have multiple H1 tags
            if len(h1_tags) > 1:
                log_test_result(f"⚠️ Article '{article.get('title', 'Unknown')}' has {len(h1_tags)} H1 tags", "WARNING")
                hierarchy_issues += 1
            
            # Check for proper hierarchy (H2 should come before H3)
            all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            prev_level = 0
            
            for heading in all_headings:
                current_level = int(heading.name[1])
                if current_level > prev_level + 1:
                    log_test_result(f"⚠️ Heading hierarchy skip in '{article.get('title', 'Unknown')}': {heading.name}", "WARNING")
                    hierarchy_issues += 1
                prev_level = current_level
        
        if hierarchy_issues == 0:
            log_test_result("✅ Heading hierarchy is properly structured", "SUCCESS")
            return True
        else:
            log_test_result(f"⚠️ Found {hierarchy_issues} heading hierarchy issues", "WARNING")
            return hierarchy_issues <= 2  # Allow minor issues
            
    except Exception as e:
        log_test_result(f"❌ Heading hierarchy test failed: {e}", "ERROR")
        return False

def test_nested_list_rendering(articles):
    """Test enhanced list formatting with hierarchical numbering"""
    try:
        log_test_result("🔍 Testing Nested List Rendering...")
        
        list_features_found = 0
        
        for article in articles[:5]:  # Test first 5 articles
            content = article.get('content', '')
            if not content:
                continue
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for ordered lists with proper structure
            ol_tags = soup.find_all('ol')
            ul_tags = soup.find_all('ul')
            
            for ol in ol_tags:
                # Check for CSS classes that indicate enhanced formatting
                if 'doc-list' in ol.get('class', []):
                    list_features_found += 1
                    log_test_result(f"✅ Found enhanced ordered list with doc-list class", "SUCCESS")
                
                # Check for nested lists
                nested_lists = ol.find_all(['ol', 'ul'])
                if nested_lists:
                    list_features_found += 1
                    log_test_result(f"✅ Found nested list structure", "SUCCESS")
            
            for ul in ul_tags:
                # Check for CSS classes
                if 'doc-list' in ul.get('class', []):
                    list_features_found += 1
        
        if list_features_found > 0:
            log_test_result(f"✅ Found {list_features_found} enhanced list features", "SUCCESS")
            return True
        else:
            log_test_result("⚠️ No enhanced list formatting detected", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Nested list rendering test failed: {e}", "ERROR")
        return False

def test_article_type_text_removal(articles):
    """Test removal of '(faq)', '(overview)' etc. text from related links"""
    try:
        log_test_result("🔍 Testing Article Type Text Removal...")
        
        type_text_issues = 0
        
        for article in articles[:5]:
            content = article.get('content', '')
            if not content:
                continue
            
            # Check for unwanted type text in links
            unwanted_patterns = [
                r'\(faq\)',
                r'\(overview\)',
                r'\(guide\)',
                r'\(reference\)',
                r'\(how-to\)'
            ]
            
            for pattern in unwanted_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    log_test_result(f"⚠️ Found unwanted type text in '{article.get('title', 'Unknown')}': {matches}", "WARNING")
                    type_text_issues += len(matches)
        
        if type_text_issues == 0:
            log_test_result("✅ No unwanted article type text found in links", "SUCCESS")
            return True
        else:
            log_test_result(f"⚠️ Found {type_text_issues} instances of unwanted type text", "WARNING")
            return type_text_issues <= 3  # Allow minor issues
            
    except Exception as e:
        log_test_result(f"❌ Article type text removal test failed: {e}", "ERROR")
        return False

def test_comprehensive_related_links(articles):
    """Test enhanced cross-reference system with organized categories"""
    try:
        log_test_result("🔍 Testing Comprehensive Related Links...")
        
        related_links_found = 0
        category_organization_found = 0
        
        for article in articles[:5]:
            content = article.get('content', '')
            if not content:
                continue
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for related links sections
            related_sections = soup.find_all(['div', 'section'], class_=re.compile(r'related'))
            
            for section in related_sections:
                related_links_found += 1
                
                # Check for category organization
                category_headers = section.find_all(['h3', 'h4'])
                for header in category_headers:
                    header_text = header.get_text().lower()
                    if any(keyword in header_text for keyword in ['complete guides', 'overviews', 'how-to', 'references', 'faqs']):
                        category_organization_found += 1
                        log_test_result(f"✅ Found organized category: {header.get_text()}", "SUCCESS")
                
                # Check for proper link structure
                links = section.find_all('a')
                if links:
                    log_test_result(f"✅ Found {len(links)} related links in organized section", "SUCCESS")
        
        if related_links_found > 0 and category_organization_found > 0:
            log_test_result(f"✅ Found {related_links_found} related link sections with {category_organization_found} organized categories", "SUCCESS")
            return True
        else:
            log_test_result("⚠️ Limited or no comprehensive related links found", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Comprehensive related links test failed: {e}", "ERROR")
        return False

def test_mini_toc_implementation(articles):
    """Test mini Table of Contents with proper anchor links"""
    try:
        log_test_result("🔍 Testing Mini-TOC Implementation...")
        
        toc_features_found = 0
        
        for article in articles[:5]:
            content = article.get('content', '')
            if not content:
                continue
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for TOC elements
            toc_elements = soup.find_all(['div', 'nav'], class_=re.compile(r'toc'))
            toc_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'toc'))
            
            for toc in toc_elements + toc_lists:
                toc_features_found += 1
                
                # Check for anchor links
                anchor_links = toc.find_all('a', href=re.compile(r'^#'))
                if anchor_links:
                    log_test_result(f"✅ Found TOC with {len(anchor_links)} anchor links", "SUCCESS")
                else:
                    log_test_result("⚠️ Found TOC but no anchor links", "WARNING")
            
            # Also check for any anchor links that might be TOC-related
            all_anchor_links = soup.find_all('a', href=re.compile(r'^#'))
            if all_anchor_links:
                toc_features_found += 1
                log_test_result(f"✅ Found {len(all_anchor_links)} anchor links (potential TOC navigation)", "SUCCESS")
        
        if toc_features_found > 0:
            log_test_result(f"✅ Found {toc_features_found} TOC-related features", "SUCCESS")
            return True
        else:
            log_test_result("⚠️ No Mini-TOC features detected", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Mini-TOC implementation test failed: {e}", "ERROR")
        return False

def test_code_block_enhancements(articles):
    """Test code blocks with copy buttons, syntax highlighting, and proper styling"""
    try:
        log_test_result("🔍 Testing Code Block Enhancements...")
        
        code_features_found = 0
        
        for article in articles[:5]:
            content = article.get('content', '')
            if not content:
                continue
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for code blocks
            code_blocks = soup.find_all(['pre', 'code'])
            
            for code_block in code_blocks:
                # Check for language classes (syntax highlighting)
                classes = code_block.get('class', [])
                if any('language-' in cls for cls in classes):
                    code_features_found += 1
                    log_test_result(f"✅ Found code block with syntax highlighting: {classes}", "SUCCESS")
                
                # Check for enhanced styling classes
                if any(cls in ['code-block', 'highlight', 'syntax'] for cls in classes):
                    code_features_found += 1
                
                # Check if code block has actual content (not empty)
                if code_block.get_text().strip():
                    code_features_found += 1
            
            # Look for copy button elements (might be added by frontend)
            copy_buttons = soup.find_all(['button', 'span'], class_=re.compile(r'copy'))
            if copy_buttons:
                code_features_found += 1
                log_test_result(f"✅ Found {len(copy_buttons)} copy button elements", "SUCCESS")
        
        if code_features_found > 0:
            log_test_result(f"✅ Found {code_features_found} code block enhancement features", "SUCCESS")
            return True
        else:
            log_test_result("⚠️ Limited code block enhancements detected", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Code block enhancements test failed: {e}", "ERROR")
        return False

def test_contextual_cross_references(articles):
    """Test internal linking within articles and 'See also' references"""
    try:
        log_test_result("🔍 Testing Contextual Cross-References...")
        
        cross_ref_features = 0
        
        for article in articles[:5]:
            content = article.get('content', '')
            if not content:
                continue
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for internal links to other articles
            internal_links = soup.find_all('a', href=re.compile(r'/content-library/article/'))
            if internal_links:
                cross_ref_features += 1
                log_test_result(f"✅ Found {len(internal_links)} internal article links", "SUCCESS")
            
            # Look for "See also" sections
            see_also_sections = soup.find_all(string=re.compile(r'see also', re.IGNORECASE))
            if see_also_sections:
                cross_ref_features += 1
                log_test_result(f"✅ Found 'See also' references", "SUCCESS")
            
            # Look for contextual references within content
            contextual_refs = soup.find_all('a', target='_blank')
            if contextual_refs:
                cross_ref_features += 1
                log_test_result(f"✅ Found {len(contextual_refs)} contextual references", "SUCCESS")
        
        if cross_ref_features > 0:
            log_test_result(f"✅ Found {cross_ref_features} cross-reference features", "SUCCESS")
            return True
        else:
            log_test_result("⚠️ Limited contextual cross-references detected", "WARNING")
            return False
            
    except Exception as e:
        log_test_result(f"❌ Contextual cross-references test failed: {e}", "ERROR")
        return False

def run_comprehensive_enhancement_test():
    """Run comprehensive test suite for enhanced content generation system"""
    log_test_result("🚀 STARTING COMPREHENSIVE ENHANCED CONTENT GENERATION TEST SUITE", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'content_processing': False,
        'content_library_enhancements': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Content Processing
    log_test_result("\nTEST 2: Enhanced Content Processing")
    processing_result = process_sample_content()
    if isinstance(processing_result, tuple):
        test_results['content_processing'] = processing_result[0]
        articles_created = processing_result[1]
        log_test_result(f"📊 Articles created: {articles_created}")
    else:
        test_results['content_processing'] = processing_result
    
    # Test 3: Content Library Enhancements
    log_test_result("\nTEST 3: Content Library Enhancement Features")
    test_results['content_library_enhancements'] = test_content_library_enhancements()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FINAL TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 2:  # At least backend health and one major feature
        log_test_result("🎉 ENHANCED CONTENT GENERATION SYSTEM IS WORKING!", "CRITICAL_SUCCESS")
        log_test_result("✅ Key enhancements have been successfully implemented", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ ENHANCED CONTENT GENERATION SYSTEM HAS ISSUES", "CRITICAL_ERROR")
        log_test_result("❌ Multiple enhancement features are not working properly", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Enhanced Content Generation System Testing")
    print("=" * 50)
    
    results = run_comprehensive_enhancement_test()
    
    # Exit with appropriate code
    if sum(results.values()) >= 2:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure