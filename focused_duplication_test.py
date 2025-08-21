#!/usr/bin/env python3
"""
FOCUSED ARTICLE DUPLICATION FIX TESTING
Testing the specific fix for duplicate overview articles when introduction content exists
Focus: Verify that create_overview_article_with_sections() properly checks for existing intro sections
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://content-pipeline-4.preview.emergentagent.com"
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

def get_articles_by_source(source_filename):
    """Get all articles from a specific source document"""
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        if response.status_code != 200:
            log_test_result(f"❌ Failed to get Content Library: {response.status_code}")
            return []
        
        data = response.json()
        articles = data.get('articles', [])
        
        # Filter articles by source document
        source_articles = []
        for article in articles:
            source = article.get('source_document', '').lower()
            title = article.get('title', '').lower()
            
            # Match by source document or title containing the source filename
            if source_filename.lower() in source or source_filename.lower() in title:
                source_articles.append(article)
        
        return source_articles
        
    except Exception as e:
        log_test_result(f"❌ Error getting articles by source: {e}")
        return []

def test_introduction_content_processing():
    """Test content with introduction section - should NOT create overview article"""
    try:
        log_test_result("🎯 TESTING INTRODUCTION CONTENT PROCESSING", "CRITICAL")
        
        # Create content with clear introduction section
        test_content = """
# React Component Development Guide

## Introduction

This comprehensive guide covers React component development from basics to advanced patterns. React components are the building blocks of React applications, allowing you to split the UI into independent, reusable pieces.

In this guide, you'll learn how to create functional and class components, manage state and props, handle events, and implement advanced patterns like higher-order components and render props.

### Prerequisites

Before starting this guide, you should have:
- Basic knowledge of JavaScript ES6+
- Understanding of HTML and CSS
- Node.js installed on your system
- Familiarity with npm or yarn

## Component Basics

React components can be defined as functions or classes. Function components are simpler and are the recommended approach for new development.

### Function Components

```jsx
function Welcome(props) {
  return <h1>Hello, {props.name}!</h1>;
}
```

### Class Components

```jsx
class Welcome extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}!</h1>;
  }
}
```

## State Management

State allows components to create and manage their own data. With hooks, function components can now use state.

### useState Hook

```jsx
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}
```

## Props and Communication

Props are how components communicate with each other. They flow down from parent to child components.

### Passing Props

```jsx
function App() {
  return (
    <div>
      <Welcome name="Alice" />
      <Welcome name="Bob" />
    </div>
  );
}
```

## Event Handling

React uses SyntheticEvents to handle user interactions consistently across browsers.

```jsx
function Button() {
  const handleClick = (e) => {
    e.preventDefault();
    console.log('Button clicked!');
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

## Advanced Patterns

### Higher-Order Components

```jsx
function withLoading(Component) {
  return function WithLoadingComponent({ isLoading, ...props }) {
    if (isLoading) {
      return <div>Loading...</div>;
    }
    return <Component {...props} />;
  };
}
```

### Render Props

```jsx
function DataProvider({ children }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetchData().then(setData);
  }, []);

  return children({ data, loading: !data });
}
```

## Best Practices

1. Keep components small and focused
2. Use descriptive names
3. Extract reusable logic into custom hooks
4. Optimize performance with React.memo when needed
5. Follow consistent file and folder structure

## Conclusion

React components are powerful tools for building maintainable user interfaces. By understanding the fundamentals and advanced patterns covered in this guide, you'll be well-equipped to build robust React applications.
"""

        log_test_result("📤 Processing content with Introduction section...")
        
        # Process the content
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content,
                "content_type": "text",
                "metadata": {"test_type": "introduction_test", "original_filename": "react_component_guide_with_intro.md"}
            },
            timeout=300
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        # Monitor processing
        processing_start = time.time()
        max_wait_time = 180
        
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
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Wait a moment for articles to be saved
                        time.sleep(2)
                        
                        # Check generated articles
                        articles = get_articles_by_source("react_component_guide_with_intro")
                        log_test_result(f"📄 Found {len(articles)} articles for React guide with intro")
                        
                        # Analyze article types
                        overview_count = 0
                        intro_count = 0
                        complete_guide_count = 0
                        
                        for article in articles:
                            title = article.get('title', '').lower()
                            article_type = article.get('article_type', '').lower()
                            
                            if 'overview' in title or article_type == 'overview':
                                overview_count += 1
                                log_test_result(f"   📖 Overview article: {article.get('title', 'Untitled')}")
                            elif 'introduction' in title or 'intro' in title:
                                intro_count += 1
                                log_test_result(f"   🎯 Introduction article: {article.get('title', 'Untitled')}")
                            elif 'complete' in title and 'guide' in title:
                                complete_guide_count += 1
                                log_test_result(f"   📚 Complete guide: {article.get('title', 'Untitled')}")
                            else:
                                log_test_result(f"   📄 Other article: {article.get('title', 'Untitled')} (type: {article_type})")
                        
                        log_test_result(f"📊 ARTICLE ANALYSIS FOR CONTENT WITH INTRODUCTION:")
                        log_test_result(f"   Overview articles: {overview_count}")
                        log_test_result(f"   Introduction articles: {intro_count}")
                        log_test_result(f"   Complete guide articles: {complete_guide_count}")
                        
                        # CRITICAL TEST: Should NOT have both overview and introduction
                        if overview_count > 0 and intro_count > 0:
                            log_test_result(f"❌ DUPLICATION DETECTED: {overview_count} overviews + {intro_count} intros", "ERROR")
                            return False
                        elif overview_count == 0 and intro_count == 0 and complete_guide_count > 0:
                            log_test_result(f"✅ CORRECT: No duplicate overview/intro - using complete guide approach", "SUCCESS")
                            return True
                        elif intro_count > 0 and overview_count == 0:
                            log_test_result(f"✅ CORRECT: Introduction content preserved, no duplicate overview created", "SUCCESS")
                            return True
                        else:
                            log_test_result(f"⚠️ UNEXPECTED: {overview_count} overviews, {intro_count} intros, {complete_guide_count} complete guides")
                            return False
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(5)
                else:
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ Introduction content test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def test_no_introduction_content_processing():
    """Test content without introduction section - should create overview article"""
    try:
        log_test_result("🎯 TESTING NO-INTRODUCTION CONTENT PROCESSING", "CRITICAL")
        
        # Create content WITHOUT introduction section
        test_content = """
# API Authentication Methods

## Token-Based Authentication

Token-based authentication is a stateless authentication mechanism where the server generates a token for authenticated users.

### JWT Tokens

JSON Web Tokens (JWTs) are a popular choice for token-based authentication:

```javascript
const jwt = require('jsonwebtoken');

// Generate token
const token = jwt.sign(
  { userId: user.id, email: user.email },
  process.env.JWT_SECRET,
  { expiresIn: '24h' }
);
```

### Token Validation

```javascript
const verifyToken = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

## OAuth 2.0 Integration

OAuth 2.0 provides a secure way to authenticate users through third-party providers.

### Authorization Code Flow

```javascript
app.get('/auth/google', passport.authenticate('google', {
  scope: ['profile', 'email']
}));

app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    res.redirect('/dashboard');
  }
);
```

### Refresh Tokens

```javascript
const refreshAccessToken = async (refreshToken) => {
  try {
    const response = await axios.post('https://oauth2.googleapis.com/token', {
      client_id: process.env.GOOGLE_CLIENT_ID,
      client_secret: process.env.GOOGLE_CLIENT_SECRET,
      refresh_token: refreshToken,
      grant_type: 'refresh_token'
    });
    
    return response.data.access_token;
  } catch (error) {
    throw new Error('Failed to refresh token');
  }
};
```

## API Key Authentication

API keys provide a simple authentication method for server-to-server communication.

### Implementation

```javascript
const validateApiKey = async (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey) {
    return res.status(401).json({ error: 'API key required' });
  }
  
  const isValid = await verifyApiKey(apiKey);
  if (!isValid) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  
  next();
};
```

### Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each API key to 100 requests per windowMs
  keyGenerator: (req) => req.headers['x-api-key'],
  message: 'Too many requests from this API key'
});
```

## Session-Based Authentication

Traditional session-based authentication using cookies and server-side sessions.

### Session Configuration

```javascript
const session = require('express-session');
const MongoStore = require('connect-mongo');

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({
    mongoUrl: process.env.MONGODB_URI
  }),
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));
```

## Security Best Practices

### Password Hashing

```javascript
const bcrypt = require('bcrypt');

const hashPassword = async (password) => {
  const saltRounds = 12;
  return await bcrypt.hash(password, saltRounds);
};

const verifyPassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};
```

### CORS Configuration

```javascript
const cors = require('cors');

app.use(cors({
  origin: process.env.FRONTEND_URL,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization', 'x-api-key']
}));
```
"""

        log_test_result("📤 Processing content without Introduction section...")
        
        # Process the content
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content,
                "content_type": "text",
                "metadata": {"test_type": "no_introduction_test", "original_filename": "api_auth_methods_no_intro.md"}
            },
            timeout=300
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        # Monitor processing
        processing_start = time.time()
        max_wait_time = 180
        
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
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Wait a moment for articles to be saved
                        time.sleep(2)
                        
                        # Check generated articles
                        articles = get_articles_by_source("api_auth_methods_no_intro")
                        log_test_result(f"📄 Found {len(articles)} articles for API auth guide without intro")
                        
                        # Analyze article types
                        overview_count = 0
                        intro_count = 0
                        complete_guide_count = 0
                        
                        for article in articles:
                            title = article.get('title', '').lower()
                            article_type = article.get('article_type', '').lower()
                            
                            if 'overview' in title or article_type == 'overview':
                                overview_count += 1
                                log_test_result(f"   📖 Overview article: {article.get('title', 'Untitled')}")
                            elif 'introduction' in title or 'intro' in title:
                                intro_count += 1
                                log_test_result(f"   🎯 Introduction article: {article.get('title', 'Untitled')}")
                            elif 'complete' in title and 'guide' in title:
                                complete_guide_count += 1
                                log_test_result(f"   📚 Complete guide: {article.get('title', 'Untitled')}")
                            else:
                                log_test_result(f"   📄 Other article: {article.get('title', 'Untitled')} (type: {article_type})")
                        
                        log_test_result(f"📊 ARTICLE ANALYSIS FOR CONTENT WITHOUT INTRODUCTION:")
                        log_test_result(f"   Overview articles: {overview_count}")
                        log_test_result(f"   Introduction articles: {intro_count}")
                        log_test_result(f"   Complete guide articles: {complete_guide_count}")
                        
                        # CRITICAL TEST: Should create overview OR complete guide (but not both intro and overview)
                        if overview_count > 0 and intro_count > 0:
                            log_test_result(f"❌ UNEXPECTED DUPLICATION: {overview_count} overviews + {intro_count} intros", "ERROR")
                            return False
                        elif overview_count > 0 or complete_guide_count > 0:
                            log_test_result(f"✅ CORRECT: Overview or complete guide created as expected", "SUCCESS")
                            return True
                        else:
                            log_test_result(f"⚠️ UNEXPECTED: No overview or complete guide created")
                            return False
                        
                    elif status == 'failed':
                        log_test_result(f"❌ Processing failed: {status_data.get('error', 'Unknown error')}", "ERROR")
                        return False
                    
                    time.sleep(5)
                else:
                    time.sleep(5)
                    
            except Exception as e:
                log_test_result(f"⚠️ Status check error: {e}")
                time.sleep(5)
    
    except Exception as e:
        log_test_result(f"❌ No introduction content test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

def run_focused_duplication_test():
    """Run focused test suite for article duplication fix verification"""
    log_test_result("🚀 STARTING FOCUSED ARTICLE DUPLICATION FIX TEST", "CRITICAL")
    log_test_result("=" * 80)
    
    test_results = {
        'backend_health': False,
        'introduction_content_test': False,
        'no_introduction_content_test': False
    }
    
    # Test 1: Backend Health
    log_test_result("TEST 1: Backend Health Check")
    test_results['backend_health'] = test_backend_health()
    
    if not test_results['backend_health']:
        log_test_result("❌ Backend health check failed - aborting remaining tests", "CRITICAL_ERROR")
        return test_results
    
    # Test 2: Content WITH introduction section
    log_test_result("\nTEST 2: CONTENT WITH INTRODUCTION SECTION")
    test_results['introduction_content_test'] = test_introduction_content_processing()
    
    # Test 3: Content WITHOUT introduction section
    log_test_result("\nTEST 3: CONTENT WITHOUT INTRODUCTION SECTION")
    test_results['no_introduction_content_test'] = test_no_introduction_content_processing()
    
    # Final Results Summary
    log_test_result("\n" + "=" * 80)
    log_test_result("🎯 FOCUSED TEST RESULTS SUMMARY", "CRITICAL")
    log_test_result("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        log_test_result(f"{test_name.replace('_', ' ').title()}: {status}")
    
    log_test_result(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        log_test_result("🎉 CRITICAL SUCCESS: Article duplication fix is working correctly!", "CRITICAL_SUCCESS")
        log_test_result("✅ System correctly handles both introduction and non-introduction content", "CRITICAL_SUCCESS")
        log_test_result("✅ No duplicate overview articles created when introduction content exists", "CRITICAL_SUCCESS")
    else:
        log_test_result("❌ CRITICAL FAILURE: Article duplication fix needs attention", "CRITICAL_ERROR")
        
        if not test_results['introduction_content_test']:
            log_test_result("❌ Issue: Content with introduction sections still creates duplicate overviews", "CRITICAL_ERROR")
        if not test_results['no_introduction_content_test']:
            log_test_result("❌ Issue: Content without introduction sections not creating proper overviews", "CRITICAL_ERROR")
    
    return test_results

if __name__ == "__main__":
    print("Focused Article Duplication Fix Testing")
    print("=" * 50)
    
    results = run_focused_duplication_test()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure