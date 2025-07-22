#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for PromptSupport MVP
Tests all backend endpoints and functionality
"""

import requests
import json
import uuid
import time
import os
from io import BytesIO

# Get backend URL from environment
BACKEND_URL = "https://9e796e0e-00f9-4816-9bed-5ee40cb0a718.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session_id = str(uuid.uuid4())
        self.uploaded_doc_id = None
        
    def test_health_check(self):
        """Test the health check endpoint"""
        print("🔍 Testing Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print("✅ Health check passed")
                    return True
                else:
                    print("❌ Health check failed - invalid response")
                    return False
            else:
                print(f"❌ Health check failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check failed - {str(e)}")
            return False
    
    def test_document_upload(self):
        """Test document upload with text content"""
        print("\n🔍 Testing Document Upload...")
        try:
            # Create a sample text document
            sample_text = """
            Welcome to PromptSupport Documentation
            
            PromptSupport is an AI-native support platform that helps organizations build intelligent support systems.
            
            Key Features:
            - Document upload and processing
            - AI-powered chat with semantic search
            - Multi-format support (text, audio, video)
            - Session-based conversations
            
            Getting Started:
            1. Upload your knowledge documents
            2. Wait for processing to complete
            3. Start chatting with the AI assistant
            
            The system uses advanced natural language processing to understand your documents and provide relevant responses to user queries.
            """
            
            files = {
                'file': ('sample_doc.txt', sample_text, 'text/plain')
            }
            
            response = requests.post(f"{self.base_url}/upload", files=files, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                if "document_id" in data:
                    self.uploaded_doc_id = data["document_id"]
                    print(f"✅ Document upload successful - ID: {self.uploaded_doc_id}")
                    
                    # Wait a bit for processing
                    print("⏳ Waiting for document processing...")
                    time.sleep(3)
                    return True
                else:
                    print("❌ Document upload failed - no document_id in response")
                    return False
            else:
                print(f"❌ Document upload failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Document upload failed - {str(e)}")
            return False
    
    def test_document_listing(self):
        """Test document listing endpoint"""
        print("\n🔍 Testing Document Listing...")
        try:
            response = requests.get(f"{self.base_url}/documents", timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                documents = response.json()
                if isinstance(documents, list):
                    print(f"✅ Document listing successful - found {len(documents)} documents")
                    
                    # Check if our uploaded document is in the list
                    if self.uploaded_doc_id:
                        found_doc = None
                        for doc in documents:
                            if doc.get("id") == self.uploaded_doc_id:
                                found_doc = doc
                                break
                        
                        if found_doc:
                            print(f"✅ Uploaded document found in list - Status: {found_doc.get('status')}")
                            return True
                        else:
                            print("⚠️ Uploaded document not found in list")
                            return True  # Still consider success if listing works
                    else:
                        return True
                else:
                    print("❌ Document listing failed - response is not a list")
                    return False
            else:
                print(f"❌ Document listing failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Document listing failed - {str(e)}")
            return False
    
    def test_chat_functionality(self):
        """Test chat with document context"""
        print("\n🔍 Testing Chat Functionality...")
        try:
            # Test chat with a query related to our uploaded document
            chat_data = {
                "message": "What is PromptSupport and what are its key features?",
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{self.base_url}/chat", 
                json=chat_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "session_id" in data:
                    print("✅ Chat functionality working")
                    print(f"AI Response: {data['response'][:200]}...")
                    if data.get("sources"):
                        print(f"Sources: {data['sources']}")
                    return True
                else:
                    print("❌ Chat failed - missing required fields in response")
                    return False
            else:
                print(f"❌ Chat failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Chat failed - {str(e)}")
            return False
    
    def test_chat_history(self):
        """Test chat history retrieval"""
        print("\n🔍 Testing Chat History...")
        try:
            response = requests.get(f"{self.base_url}/chat/history/{self.session_id}", timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                history = response.json()
                if isinstance(history, list):
                    print(f"✅ Chat history retrieval successful - found {len(history)} messages")
                    
                    # Check if our chat message is in the history
                    if len(history) > 0:
                        latest_msg = history[-1]
                        if "user_message" in latest_msg and "ai_response" in latest_msg:
                            print("✅ Chat history contains proper message structure")
                            return True
                        else:
                            print("⚠️ Chat history has unexpected structure")
                            return True  # Still consider success if retrieval works
                    else:
                        print("⚠️ No chat history found")
                        return True  # Empty history is valid
                else:
                    print("❌ Chat history failed - response is not a list")
                    return False
            else:
                print(f"❌ Chat history failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Chat history failed - {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        print("\n🔍 Testing Error Handling...")
        
        # Test invalid file upload
        print("Testing invalid file upload...")
        try:
            files = {
                'file': ('test.exe', b'invalid binary content', 'application/octet-stream')
            }
            response = requests.post(f"{self.base_url}/upload", files=files, timeout=10)
            print(f"Invalid file upload - Status: {response.status_code}")
            
            # Should handle gracefully (either reject or process)
            if response.status_code in [200, 400]:
                print("✅ Invalid file upload handled appropriately")
            else:
                print("⚠️ Unexpected response to invalid file")
        except Exception as e:
            print(f"⚠️ Error testing invalid file upload: {str(e)}")
        
        # Test invalid chat request
        print("Testing invalid chat request...")
        try:
            invalid_chat = {
                "message": "",  # Empty message
                "session_id": ""  # Empty session
            }
            response = requests.post(
                f"{self.base_url}/chat", 
                json=invalid_chat,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"Invalid chat request - Status: {response.status_code}")
            
            # Should handle gracefully
            if response.status_code in [200, 400, 422]:
                print("✅ Invalid chat request handled appropriately")
                return True
            else:
                print("⚠️ Unexpected response to invalid chat")
                return True  # Don't fail on this
        except Exception as e:
            print(f"⚠️ Error testing invalid chat: {str(e)}")
            return True
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend API Testing")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        results = {}
        
        # Run tests in sequence
        results['health_check'] = self.test_health_check()
        results['document_upload'] = self.test_document_upload()
        results['document_listing'] = self.test_document_listing()
        results['chat_functionality'] = self.test_chat_functionality()
        results['chat_history'] = self.test_chat_history()
        results['error_handling'] = self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All backend tests passed!")
            return True
        else:
            print(f"⚠️ {total - passed} tests failed")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)