#!/usr/bin/env python3
"""
Debug V2 Pipeline Issues
"""

import requests
import json
import sys

# Backend URL from environment
BACKEND_URL = "https://engineextract.preview.emergentagent.com/api"

def test_simple_processing():
    """Test simple content processing to debug the issue"""
    print("🔍 Testing simple V2 content processing...")
    
    # Very simple content
    test_content = "# Test Document\n\nThis is a simple test."
    
    payload = {
        "content": test_content,
        "content_type": "text",
        "processing_mode": "v2_only"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/content/process", 
                               json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 500:
            print("❌ Internal Server Error")
            try:
                error_data = response.json()
                print(f"Error Detail: {error_data}")
            except:
                print(f"Raw Response: {response.text}")
        else:
            data = response.json()
            print(f"✅ Success: {data}")
            
    except Exception as e:
        print(f"❌ Request Exception: {e}")

def test_engine_status():
    """Test engine status"""
    print("🔍 Testing engine status...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/engine", timeout=10)
        print(f"Engine Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Engine Status: {data.get('status')}")
            print(f"Engine Version: {data.get('version')}")
            print(f"Features Count: {len(data.get('features', []))}")
        else:
            print(f"Engine Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Engine Request Exception: {e}")

if __name__ == "__main__":
    print("🚀 V2 Pipeline Debug Testing")
    print("=" * 50)
    
    test_engine_status()
    print()
    test_simple_processing()