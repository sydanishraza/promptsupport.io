#!/usr/bin/env python3
"""
Simple Processing Test - Direct API Investigation
"""

import requests
import json
import time

BACKEND_URL = "https://content-pipeline-5.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_simple_processing():
    """Test simple content processing"""
    print("🧪 Testing simple content processing...")
    
    # Simple test content
    content = """# Test Document
    
## Introduction
This is a test document to investigate processing behavior.

## Chapter 1: Getting Started
This chapter covers basic setup and configuration.

### 1.1 System Requirements
- Modern web browser
- Internet connection
- User account

### 1.2 Installation
1. Download the software
2. Run the installer
3. Complete setup wizard

## Chapter 2: Basic Usage
This chapter explains how to use the system.

### 2.1 Login Process
1. Open the application
2. Enter credentials
3. Click login button

### 2.2 Navigation
- Use the main menu
- Access different sections
- Find help resources

## Conclusion
This document provides basic information about the system."""
    
    try:
        # Test content processing
        payload = {
            "content": content,
            "content_type": "text",
            "metadata": {"source": "simple_test"}
        }
        
        print(f"📤 Sending content ({len(content)} chars)...")
        response = requests.post(f"{API_BASE}/content/process", 
                               json=payload, 
                               headers={'Content-Type': 'application/json'},
                               timeout=60)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Processing successful:")
            print(f"   Job ID: {data.get('job_id', 'N/A')}")
            print(f"   Chunks created: {data.get('chunks_created', 0)}")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Processing failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_content_library():
    """Check content library"""
    print("\n🔍 Checking Content Library...")
    
    try:
        response = requests.get(f"{API_BASE}/content-library", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            articles = data.get('articles', [])
            
            print(f"📚 Content Library: {total} total articles")
            
            # Show recent articles
            for i, article in enumerate(articles[:5]):
                title = article.get('title', 'Untitled')
                created = article.get('created_at', 'Unknown')
                print(f"   {i+1}. {title[:50]}... ({created})")
            
            return True
        else:
            print(f"❌ Content Library access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Starting Simple Processing Test")
    
    # Test health
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return
    
    # Run tests
    test_simple_processing()
    check_content_library()
    
    print("\n✅ Simple processing test completed")

if __name__ == "__main__":
    main()