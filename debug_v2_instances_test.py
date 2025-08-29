#!/usr/bin/env python3
"""
Debug V2 Instances Test
Check if V2 instances are properly initialized and working
"""

import requests
import json
import sys

# Backend URL from environment
BACKEND_URL = "https://happy-buck.preview.emergentagent.com/api"

def test_engine_status():
    """Test engine status endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/engine", timeout=10)
        print(f"Engine Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Engine: {data.get('engine')}")
            print(f"Status: {data.get('status')}")
            print(f"Features count: {len(data.get('features', []))}")
            return True
        return False
    except Exception as e:
        print(f"Engine status error: {e}")
        return False

def test_simple_processing():
    """Test very simple content processing"""
    try:
        simple_payload = {
            "content": "Hello world",
            "content_type": "text",
            "processing_mode": "v2_only"
        }
        
        print("Testing simple processing...")
        response = requests.post(f"{BACKEND_URL}/content/process", 
                               json=simple_payload, timeout=30)
        
        print(f"Simple Processing: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Job ID: {data.get('job_id')}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"Error detail: {error_data.get('detail', 'No detail')}")
            except:
                print(f"Raw response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Simple processing error: {e}")
        return False

def test_markdown_processing():
    """Test markdown content processing"""
    try:
        markdown_payload = {
            "content": "# Test\n\nThis is a test.",
            "content_type": "markdown",
            "processing_mode": "v2_only"
        }
        
        print("Testing markdown processing...")
        response = requests.post(f"{BACKEND_URL}/content/process", 
                               json=markdown_payload, timeout=30)
        
        print(f"Markdown Processing: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"Error detail: {error_data.get('detail', 'No detail')}")
            except:
                print(f"Raw response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Markdown processing error: {e}")
        return False

def main():
    print("🔍 DEBUG V2 INSTANCES TEST")
    print("=" * 50)
    
    # Test 1: Engine status
    print("\n1. Testing engine status...")
    engine_ok = test_engine_status()
    
    # Test 2: Simple processing
    print("\n2. Testing simple processing...")
    simple_ok = test_simple_processing()
    
    # Test 3: Markdown processing
    print("\n3. Testing markdown processing...")
    markdown_ok = test_markdown_processing()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Engine Status: {'✅' if engine_ok else '❌'}")
    print(f"Simple Processing: {'✅' if simple_ok else '❌'}")
    print(f"Markdown Processing: {'✅' if markdown_ok else '❌'}")
    
    if all([engine_ok, simple_ok, markdown_ok]):
        print("🎉 All basic tests passed!")
        return 0
    else:
        print("❌ Some tests failed - V2 instances may have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())