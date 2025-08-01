#!/usr/bin/env python3
"""
Training Interface Backend API Tests
Focused tests for training interface functionality
"""

import requests
import json
import os
import io
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://75e2f69d-4b6d-467e-9338-70ba63fa8c3f.preview.emergentagent.com') + '/api'

def test_training_interface_backend_api():
    """Test the /api/training/* endpoints"""
    print("\n🔍 Testing Training Interface Backend API...")
    try:
        # Test 1: GET /api/training/templates
        print("Testing GET /api/training/templates...")
        response = requests.get(f"{BACKEND_URL}/training/templates", timeout=15)
        print(f"Templates Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Templates endpoint working - {data.get('total', 0)} templates found")
        else:
            print(f"❌ Templates endpoint failed - {response.status_code}")
            return False
        
        # Test 2: GET /api/training/sessions
        print("Testing GET /api/training/sessions...")
        response = requests.get(f"{BACKEND_URL}/training/sessions", timeout=15)
        print(f"Sessions Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sessions endpoint working - {data.get('total', 0)} sessions found")
        else:
            print(f"❌ Sessions endpoint failed - {response.status_code}")
            return False
        
        # Test 3: POST /api/training/process
        print("Testing POST /api/training/process...")
        
        test_content = """Training Interface Test Document

This document tests the training interface processing capabilities with optimized performance.

Key Features:
1. Template-based processing
2. Optimized segmentation
3. Reduced processing time
4. Quality maintenance

Content for Processing:
This content should be processed efficiently using the optimized pipeline while maintaining professional quality output."""

        file_data = io.BytesIO(test_content.encode('utf-8'))
        
        files = {
            'file': ('training_test.txt', file_data, 'text/plain')
        }
        
        form_data = {
            'template_id': 'phase1_document_processing',
            'training_mode': 'true',
            'template_instructions': json.dumps({
                "template_id": "phase1_document_processing",
                "processing_instructions": "Process with optimized settings",
                "output_requirements": {
                    "format": "html",
                    "max_articles": 2
                }
            })
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=90
        )
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Process Status Code: {response.status_code}")
        print(f"Processing time: {processing_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                articles = data.get("articles", [])
                session_id = data.get("session_id")
                print(f"✅ Processing endpoint working - {len(articles)} articles, session: {session_id}")
                
                # Test 4: POST /api/training/evaluate
                print("Testing POST /api/training/evaluate...")
                
                eval_data = {
                    "session_id": session_id,
                    "result_id": articles[0].get("id") if articles else "test_id",
                    "evaluation": "accept",
                    "feedback": "Test evaluation feedback"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/training/evaluate",
                    json=eval_data,
                    timeout=15
                )
                
                print(f"Evaluate Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ Evaluation endpoint working - evaluation ID: {data.get('evaluation_id')}")
                        return True
                    else:
                        print("❌ Evaluation endpoint failed - no success")
                        return False
                else:
                    print(f"❌ Evaluation endpoint failed - {response.status_code}")
                    return False
            else:
                print("❌ Processing endpoint failed - no success")
                return False
        else:
            print(f"❌ Processing endpoint failed - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Training interface test failed - {str(e)}")
        return False

def test_performance_metrics():
    """Test performance metrics and responsiveness"""
    print("\n🔍 Testing Performance Metrics and Responsiveness...")
    try:
        test_content = """Performance Metrics Test Document

This document tests the performance optimizations in the processing pipeline.

Optimization Targets:
- Processing time under 90 seconds
- Reduced API calls
- Efficient content generation
- Maintained quality standards

Test Content:
This content should be processed quickly while maintaining comprehensive output quality."""

        file_data = io.BytesIO(test_content.encode('utf-8'))
        
        files = {
            'file': ('performance_test.txt', file_data, 'text/plain')
        }
        
        form_data = {
            'template_id': 'performance_test',
            'training_mode': 'true',
            'template_instructions': json.dumps({
                "template_id": "performance_test",
                "processing_instructions": "Optimize for performance",
                "output_requirements": {
                    "format": "html",
                    "max_processing_time": 60
                }
            })
        }
        
        print("🔍 Testing performance metrics...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/training/process",
            files=files,
            data=form_data,
            timeout=90
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️ Processing time: {processing_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                articles = data.get("articles", [])
                
                print(f"✅ Performance test successful")
                print(f"📚 Articles generated: {len(articles)}")
                
                # Verify processing efficiency
                if processing_time <= 60:
                    print("✅ PROCESSING EFFICIENCY: Fast processing achieved")
                    return True
                elif processing_time <= 90:
                    print("⚠️ PROCESSING EFFICIENCY: Acceptable processing time")
                    return True
                else:
                    print("❌ PROCESSING EFFICIENCY: Processing too slow")
                    return False
            else:
                print(f"❌ Performance test failed: {data}")
                return False
        else:
            print(f"❌ Performance test failed - status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Performance metrics test failed - {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Training Interface Backend API Tests")
    print("=" * 60)
    
    tests = [
        ("Training Interface Backend API", test_training_interface_backend_api),
        ("Performance Metrics", test_performance_metrics)
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            failed += 1
            results.append((test_name, False))
        
        print("-" * 60)
    
    print(f"\n📊 TEST SUMMARY:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")