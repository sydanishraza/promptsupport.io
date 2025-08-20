#!/usr/bin/env python3
"""
TEST ARTICLE DUPLICATION FIX
Test the updated fix that prevents duplicate overview articles when introduction content exists
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://article-genius-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def log_test_result(message, status="INFO"):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_duplication_fix():
    """Test the duplication fix with content that has introduction sections"""
    try:
        log_test_result("🎯 TESTING UPDATED DUPLICATION FIX", "CRITICAL")
        
        # Create content with clear introduction section
        test_content = """
# Node.js Express API Development Guide

## Introduction

This comprehensive guide covers Node.js Express API development from setup to deployment. Express.js is a minimal and flexible Node.js web application framework that provides a robust set of features for web and mobile applications.

In this guide, you'll learn how to build RESTful APIs, handle authentication, implement middleware, manage databases, and deploy your applications to production environments.

### Prerequisites

Before starting this guide, you should have:
- Basic knowledge of JavaScript and Node.js
- Understanding of HTTP protocols and REST principles
- Node.js and npm installed on your system
- A code editor like VS Code

### What You'll Build

By the end of this guide, you'll have built a complete Express API with:
- User authentication and authorization
- CRUD operations for resources
- Database integration with MongoDB
- Error handling and validation
- API documentation with Swagger

## Project Setup

Let's start by setting up a new Node.js project and installing the necessary dependencies.

### Initialize Project

```bash
mkdir express-api-guide
cd express-api-guide
npm init -y
```

### Install Dependencies

```javascript
npm install express mongoose bcryptjs jsonwebtoken
npm install --save-dev nodemon jest supertest
```

### Project Structure

```
express-api-guide/
├── src/
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   ├── middleware/
│   └── utils/
├── tests/
├── package.json
└── server.js
```

## Basic Express Server

Create a basic Express server with essential middleware.

### Server Configuration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Express API is running!' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

## Database Integration

Connect your Express application to MongoDB using Mongoose.

### Database Connection

```javascript
const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error('Database connection failed:', error.message);
    process.exit(1);
  }
};

connectDB();
```

### User Model

```javascript
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  }
}, {
  timestamps: true
});

// Hash password before saving
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 12);
  next();
});

module.exports = mongoose.model('User', userSchema);
```

## Authentication System

Implement JWT-based authentication for your API.

### JWT Middleware

```javascript
const jwt = require('jsonwebtoken');
const User = require('../models/User');

const auth = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.id);
    
    if (!user) {
      return res.status(401).json({ error: 'Invalid token' });
    }

    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

module.exports = auth;
```

### Auth Routes

```javascript
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');

const router = express.Router();

// Register
router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    
    const user = new User({ username, email, password });
    await user.save();
    
    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET);
    
    res.status(201).json({
      message: 'User created successfully',
      token,
      user: { id: user._id, username, email }
    });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET);
    
    res.json({
      message: 'Login successful',
      token,
      user: { id: user._id, username: user.username, email }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
```

## API Routes and Controllers

Create RESTful routes with proper controllers for your resources.

### Product Model

```javascript
const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  category: {
    type: String,
    required: true
  },
  inStock: {
    type: Boolean,
    default: true
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Product', productSchema);
```

### Product Controller

```javascript
const Product = require('../models/Product');

// Get all products
exports.getProducts = async (req, res) => {
  try {
    const products = await Product.find().populate('createdBy', 'username');
    res.json(products);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

// Create product
exports.createProduct = async (req, res) => {
  try {
    const product = new Product({
      ...req.body,
      createdBy: req.user._id
    });
    await product.save();
    res.status(201).json(product);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Update product
exports.updateProduct = async (req, res) => {
  try {
    const product = await Product.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    
    res.json(product);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

// Delete product
exports.deleteProduct = async (req, res) => {
  try {
    const product = await Product.findByIdAndDelete(req.params.id);
    
    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }
    
    res.json({ message: 'Product deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
```

## Error Handling and Validation

Implement comprehensive error handling and input validation.

### Error Middleware

```javascript
const errorHandler = (err, req, res, next) => {
  let error = { ...err };
  error.message = err.message;

  // Mongoose bad ObjectId
  if (err.name === 'CastError') {
    const message = 'Resource not found';
    error = { message, statusCode: 404 };
  }

  // Mongoose duplicate key
  if (err.code === 11000) {
    const message = 'Duplicate field value entered';
    error = { message, statusCode: 400 };
  }

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const message = Object.values(err.errors).map(val => val.message);
    error = { message, statusCode: 400 };
  }

  res.status(error.statusCode || 500).json({
    success: false,
    error: error.message || 'Server Error'
  });
};

module.exports = errorHandler;
```

## Testing

Write comprehensive tests for your API endpoints.

### Test Setup

```javascript
const request = require('supertest');
const app = require('../server');
const User = require('../models/User');

describe('Auth Endpoints', () => {
  beforeEach(async () => {
    await User.deleteMany({});
  });

  describe('POST /api/auth/register', () => {
    it('should register a new user', async () => {
      const userData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123'
      };

      const response = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(201);

      expect(response.body.user.username).toBe(userData.username);
      expect(response.body.token).toBeDefined();
    });
  });
});
```

## Deployment

Deploy your Express API to production environments.

### Environment Configuration

```javascript
// config/config.js
module.exports = {
  development: {
    port: process.env.PORT || 3000,
    mongodb: process.env.MONGODB_URI || 'mongodb://localhost:27017/express-api-dev'
  },
  production: {
    port: process.env.PORT || 8000,
    mongodb: process.env.MONGODB_URI
  }
};
```

### Docker Configuration

```dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

## Conclusion

This guide covered the essential aspects of building a production-ready Express.js API. You've learned about project setup, database integration, authentication, CRUD operations, error handling, testing, and deployment.

Continue exploring advanced topics like rate limiting, caching, monitoring, and microservices architecture to further enhance your API development skills.
"""

        log_test_result("📤 Processing content with Introduction section to test duplication fix...")
        
        # Process the content
        response = requests.post(
            f"{API_BASE}/content/process",
            json={
                "content": test_content,
                "content_type": "text",
                "metadata": {"test_type": "duplication_fix_test", "original_filename": "express_api_guide_with_intro.md"}
            },
            timeout=300
        )
        
        if response.status_code != 200:
            log_test_result(f"❌ Content processing failed: Status {response.status_code}", "ERROR")
            return False
        
        process_data = response.json()
        job_id = process_data.get('job_id')
        
        log_test_result(f"✅ Content processing started, Job ID: {job_id}")
        
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
                    
                    log_test_result(f"📊 Processing status: {status} (elapsed: {elapsed:.1f}s)")
                    
                    if status == 'completed':
                        processing_time = time.time() - processing_start
                        log_test_result(f"✅ Processing completed in {processing_time:.1f} seconds", "SUCCESS")
                        
                        # Wait for articles to be saved
                        time.sleep(3)
                        
                        # Check generated articles
                        library_response = requests.get(f"{API_BASE}/content-library", timeout=30)
                        if library_response.status_code == 200:
                            data = library_response.json()
                            articles = data.get('articles', [])
                            
                            # Find articles from this test
                            test_articles = []
                            for article in articles:
                                title = article.get('title', '').lower()
                                source = article.get('source_document', '').lower()
                                
                                if 'express_api_guide_with_intro' in source or 'express api guide with intro' in title:
                                    test_articles.append(article)
                            
                            log_test_result(f"📄 Found {len(test_articles)} articles for Express API guide")
                            
                            # Analyze article types
                            overview_count = 0
                            intro_count = 0
                            complete_guide_count = 0
                            
                            for article in test_articles:
                                title = article.get('title', '').lower()
                                article_type = article.get('article_type', '').lower()
                                
                                log_test_result(f"   📄 Article: {article.get('title', 'Untitled')} (type: {article_type})")
                                
                                if 'overview' in title or article_type == 'overview':
                                    overview_count += 1
                                elif 'introduction' in title or 'intro' in title:
                                    intro_count += 1
                                elif 'complete' in title and 'guide' in title:
                                    complete_guide_count += 1
                            
                            log_test_result(f"📊 DUPLICATION FIX TEST RESULTS:")
                            log_test_result(f"   Overview articles: {overview_count}")
                            log_test_result(f"   Introduction articles: {intro_count}")
                            log_test_result(f"   Complete guide articles: {complete_guide_count}")
                            
                            # CRITICAL TEST: Should NOT have both overview and introduction
                            if overview_count > 0 and intro_count > 0:
                                log_test_result(f"❌ DUPLICATION FIX FAILED: {overview_count} overviews + {intro_count} intros", "ERROR")
                                return False
                            elif overview_count == 0 and intro_count == 0 and complete_guide_count > 0:
                                log_test_result(f"✅ DUPLICATION FIX WORKING: No duplicate overview/intro - using complete guide approach", "SUCCESS")
                                return True
                            elif intro_count > 0 and overview_count == 0:
                                log_test_result(f"✅ DUPLICATION FIX WORKING: Introduction content preserved, no duplicate overview created", "SUCCESS")
                                return True
                            elif overview_count > 0 and intro_count == 0:
                                log_test_result(f"✅ DUPLICATION FIX WORKING: Overview created, no introduction duplication", "SUCCESS")
                                return True
                            else:
                                log_test_result(f"⚠️ UNEXPECTED RESULT: {overview_count} overviews, {intro_count} intros, {complete_guide_count} complete guides")
                                return False
                        else:
                            log_test_result(f"❌ Failed to get Content Library: {library_response.status_code}")
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
        log_test_result(f"❌ Duplication fix test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Article Duplication Fix")
    print("=" * 50)
    
    success = test_duplication_fix()
    
    if success:
        print("\n🎉 DUPLICATION FIX TEST PASSED!")
        print("✅ The fix is working correctly - no duplicate overview articles created")
        sys.exit(0)
    else:
        print("\n❌ DUPLICATION FIX TEST FAILED!")
        print("❌ The fix needs further attention")
        sys.exit(1)