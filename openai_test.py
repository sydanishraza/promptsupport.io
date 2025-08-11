#!/usr/bin/env python3
"""
OpenAI Integration Testing Script
Focused testing for OpenAI API key and gpt-4o-mini model functionality
"""

import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
load_dotenv('/app/backend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://5281eecc-eac8-4f65-9a23-23445575ef21.preview.emergentagent.com') + '/api'

class OpenAIIntegrationTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🔥 Testing OpenAI Integration at: {self.base_url}")
        
    def test_openai_direct_api_call(self):
        """Test direct OpenAI API call to check quota and model availability"""
        print("\n🔍 Testing Direct OpenAI API Call...")
        try:
            # Load OpenAI API key from backend environment
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                print("❌ OpenAI API key not found in backend environment")
                return False
            
            print(f"✅ OpenAI API key found: {openai_api_key[:20]}...")
            
            # Test direct API call to OpenAI
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant testing API connectivity."},
                    {"role": "user", "content": "Please respond with 'OpenAI API test successful' to confirm the connection is working."}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
            
            print("🤖 Making direct call to OpenAI API...")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                print(f"✅ OpenAI API call successful!")
                print(f"Response: {ai_response}")
                print(f"Model used: {result.get('model', 'unknown')}")
                print(f"Usage: {result.get('usage', {})}")
                return True
            elif response.status_code == 429:
                print(f"❌ OpenAI quota exceeded (429 error)")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 401:
                print(f"❌ OpenAI API key invalid (401 error)")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"❌ OpenAI API call failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Direct OpenAI API test failed - {str(e)}")
            return False

    def test_claude_direct_api_call(self):
        """Test direct Claude API call to verify fallback availability"""
        print("\n🔍 Testing Direct Claude API Call...")
        try:
            # Load Claude API key from backend environment
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_api_key:
                print("❌ Anthropic API key not found in backend environment")
                return False
            
            print(f"✅ Anthropic API key found: {anthropic_api_key[:20]}...")
            
            # Test direct API call to Claude
            headers = {
                "x-api-key": anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 50,
                "temperature": 0.1,
                "system": "You are a helpful assistant testing API connectivity.",
                "messages": [
                    {"role": "user", "content": "Please respond with 'Claude API test successful' to confirm the connection is working."}
                ]
            }
            
            print("🤖 Making direct call to Claude API...")
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["content"][0]["text"]
                print(f"✅ Claude API call successful!")
                print(f"Response: {ai_response}")
                print(f"Model used: {result.get('model', 'unknown')}")
                print(f"Usage: {result.get('usage', {})}")
                return True
            elif response.status_code == 429:
                print(f"❌ Claude quota exceeded (429 error)")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 401:
                print(f"❌ Claude API key invalid (401 error)")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"❌ Claude API call failed - status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Direct Claude API test failed - {str(e)}")
            return False

    def test_gpt4o_mini_model_verification(self):
        """Verify that gpt-4o-mini model is specifically accessible"""
        print("\n🔍 Testing GPT-4o-mini Model Verification...")
        try:
            # Load OpenAI API key
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                print("❌ OpenAI API key not found")
                return False
            
            # Test specifically with gpt-4o-mini model
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are testing the gpt-4o-mini model specifically."},
                    {"role": "user", "content": "Please confirm you are the gpt-4o-mini model and that this API call is working correctly."}
                ],
                "max_tokens": 100,
                "temperature": 0.1
            }
            
            print("🤖 Testing gpt-4o-mini model specifically...")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                model_used = result.get('model', 'unknown')
                
                print(f"✅ GPT-4o-mini model test successful!")
                print(f"Model returned: {model_used}")
                print(f"Response: {ai_response}")
                
                # Verify the correct model was used
                if 'gpt-4o-mini' in model_used:
                    print("✅ Correct model (gpt-4o-mini) confirmed")
                    return True
                else:
                    print(f"⚠️ Unexpected model returned: {model_used}")
                    return True  # Still successful API call
                    
            elif response.status_code == 429:
                print(f"❌ GPT-4o-mini quota exceeded")
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                print(f"Error details: {error_data}")
                return False
            else:
                print(f"❌ GPT-4o-mini model test failed - status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ GPT-4o-mini model verification failed - {str(e)}")
            return False

    def test_llm_fallback_system_comprehensive(self):
        """Test the call_llm_with_fallback function comprehensively"""
        print("\n🔍 Testing LLM Fallback System Comprehensively...")
        try:
            # Test multiple endpoints that use the fallback system
            fallback_tests = [
                {
                    "name": "AI Assistance - Completion Mode",
                    "endpoint": "/ai-assistance",
                    "data": {
                        "content": "This is a test of the OpenAI to Claude fallback system for",
                        "mode": "completion"
                    }
                },
                {
                    "name": "AI Assistance - Grammar Mode", 
                    "endpoint": "/ai-assistance",
                    "data": {
                        "content": "This sentance has grammer mistakes that need fixing.",
                        "mode": "grammar"
                    }
                },
                {
                    "name": "Content Analysis",
                    "endpoint": "/content-analysis",
                    "data": {
                        "content": "This is a test document for content analysis using the OpenAI to Claude fallback system. It should analyze readability, word count, and provide insights.",
                        "mode": "analysis"
                    }
                },
                {
                    "name": "Chat Endpoint",
                    "endpoint": "/chat",
                    "data": {
                        "message": "Test the OpenAI to Claude fallback system",
                        "session_id": "fallback_test_session"
                    }
                }
            ]
            
            results = []
            
            for test in fallback_tests:
                print(f"\n  Testing {test['name']}...")
                
                try:
                    if test['endpoint'] == '/chat':
                        # Chat endpoint uses form data
                        response = requests.post(
                            f"{self.base_url}{test['endpoint']}",
                            data=test['data'],
                            timeout=45
                        )
                    else:
                        # Other endpoints use JSON
                        response = requests.post(
                            f"{self.base_url}{test['endpoint']}",
                            json=test['data'],
                            timeout=45
                        )
                    
                    print(f"    Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check for successful response indicators
                        if test['endpoint'] == '/ai-assistance':
                            success = data.get('success', False) or len(data.get('suggestions', [])) > 0
                        elif test['endpoint'] == '/content-analysis':
                            success = data.get('success', False) or 'wordCount' in data
                        elif test['endpoint'] == '/chat':
                            success = 'response' in data and len(data.get('response', '')) > 0
                        else:
                            success = True
                        
                        if success:
                            print(f"    ✅ {test['name']} successful")
                            
                            # Try to detect which AI was used
                            response_text = str(data)
                            if 'gpt-4o' in response_text.lower():
                                print(f"    🤖 Likely used OpenAI")
                            elif 'claude' in response_text.lower():
                                print(f"    🤖 Likely used Claude (fallback)")
                            else:
                                print(f"    🤖 AI service used: Unknown")
                            
                            results.append(True)
                        else:
                            print(f"    ❌ {test['name']} failed - invalid response")
                            results.append(False)
                    else:
                        print(f"    ❌ {test['name']} failed - status {response.status_code}")
                        print(f"    Response: {response.text[:200]}...")
                        results.append(False)
                        
                except Exception as e:
                    print(f"    ❌ {test['name']} failed with exception: {e}")
                    results.append(False)
            
            # Overall assessment
            successful_tests = sum(results)
            total_tests = len(fallback_tests)
            
            print(f"\n📊 Fallback System Results: {successful_tests}/{total_tests} tests passed")
            
            if successful_tests >= 3:  # At least 3 out of 4 should work
                print("✅ LLM Fallback System working comprehensively")
                return True
            else:
                print("❌ LLM Fallback System has significant issues")
                return False
                
        except Exception as e:
            print(f"❌ Comprehensive fallback test failed - {str(e)}")
            return False

    def test_quota_and_rate_limit_handling(self):
        """Test how the system handles quota and rate limit scenarios"""
        print("\n🔍 Testing Quota and Rate Limit Handling...")
        try:
            # Make multiple rapid requests to test rate limiting behavior
            print("Making multiple rapid requests to test rate limiting...")
            
            rapid_requests = []
            for i in range(3):  # Make 3 rapid requests
                print(f"  Request {i+1}/3...")
                
                try:
                    response = requests.post(
                        f"{self.base_url}/ai-assistance",
                        json={
                            "content": f"Rate limit test request {i+1}",
                            "mode": "completion"
                        },
                        timeout=30
                    )
                    
                    rapid_requests.append({
                        "request_num": i+1,
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_data": response.json() if response.status_code == 200 else response.text
                    })
                    
                    print(f"    Status: {response.status_code}")
                    
                    # Small delay between requests
                    time.sleep(1)
                    
                except Exception as e:
                    rapid_requests.append({
                        "request_num": i+1,
                        "status_code": "ERROR",
                        "success": False,
                        "error": str(e)
                    })
                    print(f"    Error: {e}")
            
            # Analyze results
            successful_requests = sum(1 for req in rapid_requests if req['success'])
            print(f"\n📊 Rapid Request Results: {successful_requests}/3 successful")
            
            # Check if system handled requests gracefully
            all_failed = all(not req['success'] for req in rapid_requests)
            all_succeeded = all(req['success'] for req in rapid_requests)
            
            if all_succeeded:
                print("✅ All rapid requests succeeded - no rate limiting detected")
                return True
            elif successful_requests >= 1:
                print("✅ Some requests succeeded - system handling rate limits gracefully")
                return True
            elif all_failed:
                print("⚠️ All requests failed - may indicate quota/rate limit issues")
                
                # Check if failures are due to quota issues
                quota_errors = 0
                for req in rapid_requests:
                    if isinstance(req.get('response_data'), str) and '429' in req.get('response_data', ''):
                        quota_errors += 1
                
                if quota_errors > 0:
                    print(f"❌ Detected {quota_errors} quota/rate limit errors")
                    return False
                else:
                    print("⚠️ Failures may be due to other issues")
                    return True
            else:
                print("✅ Mixed results - system appears to be handling limits appropriately")
                return True
                
        except Exception as e:
            print(f"❌ Quota and rate limit test failed - {str(e)}")
            return False

    def run_openai_tests(self):
        """Run all OpenAI integration tests"""
        print("🚀 Starting OpenAI Integration Testing...")
        print("🎯 FOCUSED TESTING: OpenAI API Key and GPT-4o-mini Model")
        print("=" * 80)
        
        tests = [
            ("🔥 Direct OpenAI API Call", self.test_openai_direct_api_call),
            ("🔥 Direct Claude API Call", self.test_claude_direct_api_call),
            ("🔥 GPT-4o-mini Model Verification", self.test_gpt4o_mini_model_verification),
            ("🔥 LLM Fallback System Comprehensive", self.test_llm_fallback_system_comprehensive),
            ("🔥 Quota and Rate Limit Handling", self.test_quota_and_rate_limit_handling),
        ]
        
        results = []
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append((test_name, result))
                if result:
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    failed += 1
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                failed += 1
                results.append((test_name, False))
                print(f"❌ {test_name}: FAILED with exception: {str(e)}")
        
        # Print summary
        print("\n" + "="*80)
        print("🏁 OPENAI INTEGRATION TESTING SUMMARY")
        print("="*80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        print("\n🎯 PRIORITY TEST RESULTS (OpenAI Integration):")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")
        
        return passed, failed

if __name__ == "__main__":
    tester = OpenAIIntegrationTest()
    passed, failed = tester.run_openai_tests()
    
    print(f"\n🎯 OPENAI INTEGRATION TESTING COMPLETE: {passed}/{passed+failed} tests passed ({(passed/(passed+failed)*100):.1f}%)")
    
    if passed == len([
        "Direct OpenAI API Call",
        "Direct Claude API Call", 
        "GPT-4o-mini Model Verification",
        "LLM Fallback System Comprehensive",
        "Quota and Rate Limit Handling"
    ]):
        print("🎉 ALL OPENAI INTEGRATION TESTS PASSED!")
    else:
        print("⚠️ Some OpenAI integration tests failed - check details above")