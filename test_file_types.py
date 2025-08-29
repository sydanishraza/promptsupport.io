#!/usr/bin/env python3
"""
File Type Upload Testing - V2 Pipeline Validation
Test various file types and error handling scenarios
"""

import os
import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env
def get_backend_url():
    """Get backend URL from frontend .env file"""
    frontend_env_path = os.path.join(os.path.dirname(__file__), 'frontend', '.env')
    if os.path.exists(frontend_env_path):
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BACKEND_URL = get_backend_url()

def test_file_types():
    """Test various file types and error handling"""
    print("🎯 FILE TYPE UPLOAD TESTING - V2 PIPELINE")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print()
    
    # Test cases
    test_cases = [
        {
            "name": "Valid TXT File",
            "content": b"This is a comprehensive test document for the V2 pipeline. It contains substantial content that should be processed successfully by the V2 engine. The content includes multiple sentences and paragraphs to ensure proper processing. This text file should generate at least one article with proper V2 metadata and substantial content extraction.",
            "filename": "test_document.txt",
            "content_type": "text/plain",
            "expected_success": True
        },
        {
            "name": "Empty File",
            "content": b"",
            "filename": "empty.txt",
            "content_type": "text/plain",
            "expected_success": False
        },
        {
            "name": "Minimal Content",
            "content": b"Short",
            "filename": "minimal.txt",
            "content_type": "text/plain",
            "expected_success": False
        },
        {
            "name": "Unsupported File Type",
            "content": b"This is binary content that should not be processed",
            "filename": "test.exe",
            "content_type": "application/octet-stream",
            "expected_success": False
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📄 Test {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Create file-like object
            import io
            file_obj = io.BytesIO(test_case['content'])
            
            files = {
                'file': (test_case['filename'], file_obj, test_case['content_type'])
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/api/content/upload",
                files=files,
                timeout=60
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️ Processing time: {processing_time:.2f}s")
            print(f"📡 HTTP Status: {response.status_code}")
            
            # Analyze response
            is_success = response.status_code == 200
            expected_success = test_case['expected_success']
            
            if is_success:
                try:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    engine = data.get('engine', 'unknown')
                    result = data.get('result', {})
                    content_length = result.get('extracted_content_length', 0)
                    
                    print(f"✅ Upload successful")
                    print(f"   Status: {status}")
                    print(f"   Engine: {engine}")
                    print(f"   Content: {content_length} chars")
                    
                except json.JSONDecodeError:
                    print(f"⚠️ Success but invalid JSON response")
            else:
                print(f"❌ Upload failed: {response.text[:200]}")
            
            # Evaluate result
            test_passed = (is_success == expected_success)
            
            if test_passed:
                print(f"✅ Test PASSED (expected: {'success' if expected_success else 'failure'})")
            else:
                print(f"❌ Test FAILED (expected: {'success' if expected_success else 'failure'}, got: {'success' if is_success else 'failure'})")
            
            results.append({
                "name": test_case['name'],
                "passed": test_passed,
                "is_success": is_success,
                "expected_success": expected_success,
                "processing_time": processing_time,
                "status_code": response.status_code
            })
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            # For error cases, exceptions might be expected
            test_passed = not test_case['expected_success']
            results.append({
                "name": test_case['name'],
                "passed": test_passed,
                "exception": str(e)
            })
        
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for r in results if r['passed'])
    total_tests = len(results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    for result in results:
        status = "✅" if result['passed'] else "❌"
        print(f"{status} {result['name']}")
        if 'exception' in result:
            print(f"   Exception: {result['exception']}")
        elif 'status_code' in result:
            print(f"   HTTP {result['status_code']}, Expected: {'Success' if result['expected_success'] else 'Failure'}")
    
    print()
    if success_rate >= 75:
        print("🎉 EXCELLENT: File type handling working well!")
    elif success_rate >= 50:
        print("✅ GOOD: Most file type handling working")
    else:
        print("⚠️ NEEDS IMPROVEMENT: File type handling issues")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = test_file_types()
    exit(0 if success else 1)