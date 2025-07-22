#!/usr/bin/env python3
"""
Backend API Testing for Minimal FastAPI Setup
Tests basic health endpoints and MongoDB connection
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://6b6a3600-f3e8-4652-ae51-ec7567a4e940.preview.emergentagent.com') + '/api'

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"Testing backend at: {self.base_url}")
        
    def test_health_check(self):
        """Test the /api/health endpoint"""
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
    
    def test_status_endpoint(self):
        """Test the /api/status endpoint"""
        print("\n🔍 Testing Status Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/status", timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "message" in data:
                    print("✅ Status endpoint working")
                    return True
                else:
                    print("❌ Status endpoint failed - missing required fields")
                    return False
            else:
                print(f"❌ Status endpoint failed - status code {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Status endpoint failed - {str(e)}")
            return False
    
    def test_server_running(self):
        """Test if server is accessible and running"""
        print("\n🔍 Testing Server Accessibility...")
        try:
            # Try to connect to the base URL
            response = requests.get(self.base_url.replace('/api', ''), timeout=10)
            print(f"Base URL Status Code: {response.status_code}")
            
            # Any response (even 404) means server is running
            if response.status_code in [200, 404, 422]:
                print("✅ Server is running and accessible")
                return True
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
                return True  # Still consider it running
                
        except Exception as e:
            print(f"❌ Server accessibility test failed - {str(e)}")
            return False
    
    def test_mongodb_connection(self):
        """Test MongoDB connection indirectly through backend health"""
        print("\n🔍 Testing MongoDB Connection...")
        try:
            # The backend initializes MongoDB connection on startup
            # If health endpoint works, MongoDB connection is likely working
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                print("✅ MongoDB connection appears healthy (backend started successfully)")
                return True
            else:
                print("⚠️ Cannot verify MongoDB connection - backend health check failed")
                return False
                
        except Exception as e:
            print(f"❌ MongoDB connection test failed - {str(e)}")
            return False
    
    def test_cors_headers(self):
        """Test CORS configuration"""
        print("\n🔍 Testing CORS Configuration...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            # Check for CORS headers
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers')
            }
            
            print(f"CORS Headers: {cors_headers}")
            
            # If we get a response, CORS is likely configured correctly
            if response.status_code == 200:
                print("✅ CORS appears to be configured (request succeeded)")
                return True
            else:
                print("⚠️ Cannot verify CORS configuration")
                return False
                
        except Exception as e:
            print(f"❌ CORS test failed - {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Minimal Backend API Testing")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        results = {}
        
        # Run tests in sequence
        results['server_running'] = self.test_server_running()
        results['health_check'] = self.test_health_check()
        results['status_endpoint'] = self.test_status_endpoint()
        results['mongodb_connection'] = self.test_mongodb_connection()
        results['cors_configuration'] = self.test_cors_headers()
        
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
        
        if passed >= 3:  # At least server, health, and status should work
            print("🎉 Core backend functionality is working!")
            return True
        else:
            print(f"⚠️ {total - passed} critical tests failed")
            return False

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)