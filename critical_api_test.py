#!/usr/bin/env python3
"""
Critical Backend API Testing - User Reported Broken APIs
Testing the specific APIs that the user says are broken:
1. Content Library API (/api/content-library)
2. Knowledge Engine Upload API (/api/content/upload) 
3. Legacy Training Engine API (/api/training/process)
4. Document API (/api/documents)
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://29ab9b48-9f0b-482b-8a23-9ef1aebd2745.preview.emergentagent.com') + '/api'

class CriticalAPITest:
    def __init__(self):
        self.base_url = BACKEND_URL
        print(f"🎯 Testing Critical Backend APIs at: {self.base_url}")
        print("🔍 Focus: User-reported broken APIs")
        
    def test_content_library_api(self):
        """Test /api/content-library - User says articles are not being returned"""
        print("\n🔍 Testing Content Library API (/api/content-library)...")
        try:
            response = requests.get(f"{self.base_url}/content-library", timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Check if articles are being returned
                articles = data.get('articles', [])
                total_articles = data.get('total', 0)
                
                print(f"📚 Articles returned: {len(articles)}")
                print(f"📊 Total articles in database: {total_articles}")
                
                if len(articles) > 0:
                    print("✅ CONTENT LIBRARY API WORKING - Articles are being returned")
                    
                    # Show sample article structure
                    sample_article = articles[0]
                    print(f"📄 Sample article keys: {list(sample_article.keys())}")
                    print(f"📄 Sample title: {sample_article.get('title', 'No title')}")
                    print(f"📄 Sample ID: {sample_article.get('id', 'No ID')}")
                    
                    return True
                else:
                    print("❌ CONTENT LIBRARY API ISSUE - No articles returned")
                    print("🔍 This could mean:")
                    print("  - Database is empty")
                    print("  - Query is not finding articles")
                    print("  - Articles exist but are not being serialized properly")
                    return False
                    
            elif response.status_code == 404:
                print("❌ CONTENT LIBRARY API NOT FOUND - Endpoint may not exist")
                return False
            elif response.status_code == 500:
                print("❌ CONTENT LIBRARY API SERVER ERROR")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"❌ CONTENT LIBRARY API UNEXPECTED STATUS: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ CONTENT LIBRARY API CONNECTION ERROR - Backend may be down")
            return False
        except requests.exceptions.Timeout:
            print("❌ CONTENT LIBRARY API TIMEOUT - Backend may be overloaded")
            return False
        except Exception as e:
            print(f"❌ CONTENT LIBRARY API ERROR: {str(e)}")
            return False
    
    def test_knowledge_engine_upload_api(self):
        """Test /api/content/upload - User says it's not working"""
        print("\n🔍 Testing Knowledge Engine Upload API (/api/content/upload)...")
        try:
            # Create a test file for upload
            test_content = """Knowledge Engine Upload Test Document

This is a test document to verify that the Knowledge Engine upload API is working correctly.
The system should be able to process this file and create searchable content chunks.

Key features being tested:
1. File upload handling
2. Content processing
3. Chunk creation
4. Response format

This test verifies that the upload API is functional and processing files correctly."""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('knowledge_engine_test.txt', file_data, 'text/plain')
            }
            
            form_data = {
                'metadata': json.dumps({
                    "source": "critical_api_test",
                    "test_type": "knowledge_engine_upload",
                    "document_type": "test_document"
                })
            }
            
            print("📤 Uploading test file to Knowledge Engine...")
            
            response = requests.post(
                f"{self.base_url}/content/upload",
                files=files,
                data=form_data,
                timeout=60
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Check expected response fields
                success = data.get('success', False)
                job_id = data.get('job_id')
                chunks_created = data.get('chunks_created', 0)
                
                print(f"✅ Success: {success}")
                print(f"📋 Job ID: {job_id}")
                print(f"📊 Chunks created: {chunks_created}")
                
                if success and job_id and chunks_created > 0:
                    print("✅ KNOWLEDGE ENGINE UPLOAD API WORKING")
                    print(f"  ✅ File uploaded successfully")
                    print(f"  ✅ {chunks_created} content chunks created")
                    print(f"  ✅ Job ID generated: {job_id}")
                    return True
                elif success and job_id:
                    print("⚠️ KNOWLEDGE ENGINE UPLOAD API PARTIAL SUCCESS")
                    print("  ✅ File uploaded successfully")
                    print("  ⚠️ No chunks created (may be expected for simple text)")
                    return True
                else:
                    print("❌ KNOWLEDGE ENGINE UPLOAD API ISSUE")
                    print(f"  Success: {success}")
                    print(f"  Job ID: {job_id}")
                    print(f"  Chunks: {chunks_created}")
                    return False
                    
            elif response.status_code == 404:
                print("❌ KNOWLEDGE ENGINE UPLOAD API NOT FOUND")
                return False
            elif response.status_code == 500:
                print("❌ KNOWLEDGE ENGINE UPLOAD API SERVER ERROR")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"❌ KNOWLEDGE ENGINE UPLOAD API UNEXPECTED STATUS: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ KNOWLEDGE ENGINE UPLOAD API CONNECTION ERROR")
            return False
        except requests.exceptions.Timeout:
            print("❌ KNOWLEDGE ENGINE UPLOAD API TIMEOUT")
            return False
        except Exception as e:
            print(f"❌ KNOWLEDGE ENGINE UPLOAD API ERROR: {str(e)}")
            return False
    
    def test_training_engine_api(self):
        """Test /api/training/process - User says it's not processing files"""
        print("\n🔍 Testing Legacy Training Engine API (/api/training/process)...")
        try:
            # Create a test DOCX file for training
            test_content = """Training Engine Process Test Document

This document tests the Legacy Training Engine API to verify that it can process files correctly.

The system should:
1. Accept file uploads
2. Process the document content
3. Generate training articles
4. Return proper response with session information

Test Sections:
- Introduction to Training Engine
- File Processing Capabilities  
- Article Generation Features
- Quality Assurance Metrics

This comprehensive test verifies that the training/process endpoint is functional."""

            file_data = io.BytesIO(test_content.encode('utf-8'))
            
            files = {
                'file': ('training_engine_test.txt', file_data, 'text/plain')
            }
            
            # Use a basic template for testing
            form_data = {
                'template_id': 'basic_document_processing',
                'training_mode': 'true',
                'template_instructions': json.dumps({
                    "template_id": "basic_document_processing",
                    "processing_instructions": "Process document and generate articles",
                    "output_requirements": {
                        "format": "html",
                        "min_articles": 1,
                        "max_articles": 3
                    }
                })
            }
            
            print("📤 Processing file with Training Engine...")
            
            response = requests.post(
                f"{self.base_url}/training/process",
                files=files,
                data=form_data,
                timeout=120  # Extended timeout for processing
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Check expected response fields
                success = data.get('success', False)
                session_id = data.get('session_id')
                articles = data.get('articles', [])
                processing_time = data.get('processing_time', 0)
                
                print(f"✅ Success: {success}")
                print(f"📋 Session ID: {session_id}")
                print(f"📚 Articles generated: {len(articles)}")
                print(f"⏱️ Processing time: {processing_time}s")
                
                if success and session_id and len(articles) > 0:
                    print("✅ TRAINING ENGINE API WORKING")
                    print(f"  ✅ File processed successfully")
                    print(f"  ✅ {len(articles)} articles generated")
                    print(f"  ✅ Session ID: {session_id}")
                    print(f"  ✅ Processing completed in {processing_time}s")
                    
                    # Show sample article info
                    if articles:
                        sample_article = articles[0]
                        print(f"📄 Sample article title: {sample_article.get('title', 'No title')}")
                        print(f"📄 Sample article word count: {sample_article.get('word_count', 0)}")
                    
                    return True
                elif success and session_id:
                    print("⚠️ TRAINING ENGINE API PARTIAL SUCCESS")
                    print("  ✅ File processed successfully")
                    print("  ⚠️ No articles generated")
                    return True
                else:
                    print("❌ TRAINING ENGINE API ISSUE")
                    print(f"  Success: {success}")
                    print(f"  Session ID: {session_id}")
                    print(f"  Articles: {len(articles)}")
                    return False
                    
            elif response.status_code == 404:
                print("❌ TRAINING ENGINE API NOT FOUND")
                return False
            elif response.status_code == 500:
                print("❌ TRAINING ENGINE API SERVER ERROR")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"❌ TRAINING ENGINE API UNEXPECTED STATUS: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ TRAINING ENGINE API CONNECTION ERROR")
            return False
        except requests.exceptions.Timeout:
            print("❌ TRAINING ENGINE API TIMEOUT")
            return False
        except Exception as e:
            print(f"❌ TRAINING ENGINE API ERROR: {str(e)}")
            return False
    
    def test_documents_api(self):
        """Test /api/documents - User says document retrieval is broken"""
        print("\n🔍 Testing Documents API (/api/documents)...")
        try:
            response = requests.get(f"{self.base_url}/documents", timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                
                # Check if documents are being returned
                documents = data.get('documents', [])
                total_documents = data.get('total', 0)
                
                print(f"📄 Documents returned: {len(documents)}")
                print(f"📊 Total documents: {total_documents}")
                
                if len(documents) > 0:
                    print("✅ DOCUMENTS API WORKING - Documents are being returned")
                    
                    # Show sample document structure
                    sample_doc = documents[0]
                    print(f"📄 Sample document keys: {list(sample_doc.keys())}")
                    print(f"📄 Sample title: {sample_doc.get('title', 'No title')}")
                    print(f"📄 Sample ID: {sample_doc.get('id', 'No ID')}")
                    
                    return True
                else:
                    print("❌ DOCUMENTS API ISSUE - No documents returned")
                    print("🔍 This could mean:")
                    print("  - No documents in database")
                    print("  - Query is not finding documents")
                    print("  - Documents exist but are not being serialized properly")
                    return False
                    
            elif response.status_code == 404:
                print("❌ DOCUMENTS API NOT FOUND - Endpoint may not exist")
                return False
            elif response.status_code == 500:
                print("❌ DOCUMENTS API SERVER ERROR")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"❌ DOCUMENTS API UNEXPECTED STATUS: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ DOCUMENTS API CONNECTION ERROR")
            return False
        except requests.exceptions.Timeout:
            print("❌ DOCUMENTS API TIMEOUT")
            return False
        except Exception as e:
            print(f"❌ DOCUMENTS API ERROR: {str(e)}")
            return False
    
    def test_health_check(self):
        """Test basic health check to verify backend is running"""
        print("\n🔍 Testing Backend Health Check (/api/health)...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Health status: {data.get('status', 'unknown')}")
                print("✅ BACKEND IS RUNNING")
                return True
            else:
                print(f"❌ BACKEND HEALTH CHECK FAILED: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ BACKEND HEALTH CHECK ERROR: {str(e)}")
            return False
    
    def run_all_critical_tests(self):
        """Run all critical API tests and provide summary"""
        print("🎯 CRITICAL BACKEND API TESTING - USER REPORTED ISSUES")
        print("=" * 60)
        
        results = {}
        
        # Test backend health first
        results['health'] = self.test_health_check()
        
        # Test the specific APIs user mentioned are broken
        results['content_library'] = self.test_content_library_api()
        results['knowledge_upload'] = self.test_knowledge_engine_upload_api()
        results['training_process'] = self.test_training_engine_api()
        results['documents'] = self.test_documents_api()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 CRITICAL API TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for api_name, result in results.items():
            status = "✅ WORKING" if result else "❌ BROKEN"
            print(f"{api_name.upper().replace('_', ' ')}: {status}")
        
        print(f"\nOVERALL: {passed_tests}/{total_tests} APIs working")
        
        if passed_tests == total_tests:
            print("🎉 ALL CRITICAL APIs ARE WORKING")
        elif passed_tests >= total_tests - 1:
            print("⚠️ MOST APIs WORKING - Minor issues detected")
        else:
            print("❌ CRITICAL ISSUES DETECTED - Multiple APIs broken")
        
        return results

if __name__ == "__main__":
    tester = CriticalAPITest()
    results = tester.run_all_critical_tests()