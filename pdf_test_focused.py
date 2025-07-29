#!/usr/bin/env python3
"""
Focused PDF Generation Testing
Tests the fixed PDF generation functionality with enhanced validation
"""

import requests
import json
import time
import os
import tempfile

class PDFTestRunner:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.session = requests.Session()
        self.test_results = {}
    
    def test_content_library_pdf_download(self):
        """Test Content Library PDF download functionality"""
        print("\n🔍 Testing Content Library PDF Download...")
        
        try:
            # First get existing articles
            response = self.session.get(f"{self.base_url}/content-library", timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Could not access Content Library - status {response.status_code}")
                return False
            
            data = response.json()
            articles = data.get('articles', [])
            
            if not articles:
                print("⚠️ No articles found, creating test article...")
                test_article = self.create_test_article()
                if not test_article:
                    return False
                article_id = test_article['id']
                title = test_article['title']
            else:
                article = articles[0]
                article_id = article.get('id')
                title = article.get('title', 'Test Article')
                print(f"📄 Using article: '{title}' (ID: {article_id})")
            
            if not article_id:
                print("❌ No valid article ID")
                return False
            
            # Test PDF download
            print(f"📥 Testing PDF download for article: {article_id}")
            pdf_response = self.session.get(
                f"{self.base_url}/content-library/article/{article_id}/download-pdf",
                timeout=30
            )
            
            print(f"📊 PDF Response Status: {pdf_response.status_code}")
            print(f"📦 Content-Type: {pdf_response.headers.get('content-type', 'unknown')}")
            print(f"📏 Content Length: {len(pdf_response.content)} bytes")
            
            if pdf_response.status_code != 200:
                print(f"❌ PDF download failed - status {pdf_response.status_code}")
                print(f"Response: {pdf_response.text[:200]}")
                return False
            
            # Validate PDF content
            if len(pdf_response.content) < 1000:
                print(f"❌ PDF too small: {len(pdf_response.content)} bytes (expected >1000)")
                return False
            
            if not pdf_response.content.startswith(b'%PDF-'):
                print(f"❌ Invalid PDF header: {pdf_response.content[:10]}")
                return False
            
            # Save PDF to verify it's valid
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_response.content)
                pdf_path = tmp_file.name
            
            print(f"✅ PDF downloaded successfully:")
            print(f"   📄 Size: {len(pdf_response.content)} bytes")
            print(f"   🔖 Header: {pdf_response.content[:8]}")
            print(f"   💾 Saved to: {pdf_path}")
            
            # Cleanup
            try:
                os.unlink(pdf_path)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Content Library PDF test error: {e}")
            return False
    
    def test_training_interface_pdf_download(self):
        """Test Training Interface PDF download functionality"""
        print("\n🔍 Testing Training Interface PDF Download...")
        
        try:
            # Get training sessions
            response = self.session.get(f"{self.base_url}/training/sessions", timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Could not access training sessions - status {response.status_code}")
                return False
            
            sessions = response.json()
            
            if not sessions:
                print("⚠️ No training sessions found, creating test session...")
                session_id = self.create_test_training_session()
                if not session_id:
                    return False
            else:
                session_id = sessions[0].get('session_id')
                print(f"📄 Using training session: {session_id}")
            
            if not session_id:
                print("❌ No valid session ID")
                return False
            
            # Test PDF download for first article
            article_index = 0
            print(f"📥 Testing PDF download for session: {session_id}, article: {article_index}")
            
            pdf_response = self.session.get(
                f"{self.base_url}/training/article/{session_id}/{article_index}/download-pdf",
                timeout=30
            )
            
            print(f"📊 PDF Response Status: {pdf_response.status_code}")
            print(f"📦 Content-Type: {pdf_response.headers.get('content-type', 'unknown')}")
            print(f"📏 Content Length: {len(pdf_response.content)} bytes")
            
            if pdf_response.status_code != 200:
                print(f"❌ Training PDF download failed - status {pdf_response.status_code}")
                print(f"Response: {pdf_response.text[:200]}")
                return False
            
            # Validate PDF content
            if len(pdf_response.content) < 1000:
                print(f"❌ Training PDF too small: {len(pdf_response.content)} bytes (expected >1000)")
                return False
            
            if not pdf_response.content.startswith(b'%PDF-'):
                print(f"❌ Invalid training PDF header: {pdf_response.content[:10]}")
                return False
            
            # Save PDF to verify it's valid
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_response.content)
                pdf_path = tmp_file.name
            
            print(f"✅ Training PDF downloaded successfully:")
            print(f"   📄 Size: {len(pdf_response.content)} bytes")
            print(f"   🔖 Header: {pdf_response.content[:8]}")
            print(f"   💾 Saved to: {pdf_path}")
            
            # Cleanup
            try:
                os.unlink(pdf_path)
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Training PDF test error: {e}")
            return False
    
    def test_pdf_with_fallback_content(self):
        """Test PDF generation with fallback content"""
        print("\n🔍 Testing PDF Generation with Fallback Content...")
        
        try:
            # Create an article with minimal content to trigger fallback
            test_data = {
                "title": "Minimal Content Test",
                "content": "Short",  # This should trigger fallback content
                "author": "PDF Test",
                "source_type": "manual"
            }
            
            # Create the article
            response = self.session.post(
                f"{self.base_url}/content-library/create",
                json=test_data,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"❌ Could not create test article - status {response.status_code}")
                return False
            
            article_data = response.json()
            article_id = article_data.get('id')
            
            if not article_id:
                print("❌ No article ID returned")
                return False
            
            print(f"📄 Created minimal content article: {article_id}")
            
            # Test PDF download (should use fallback content)
            pdf_response = self.session.get(
                f"{self.base_url}/content-library/article/{article_id}/download-pdf",
                timeout=30
            )
            
            if pdf_response.status_code != 200:
                print(f"❌ Fallback PDF download failed - status {pdf_response.status_code}")
                return False
            
            # This should be larger due to fallback content
            if len(pdf_response.content) < 2000:
                print(f"❌ Fallback PDF too small: {len(pdf_response.content)} bytes")
                return False
            
            print(f"✅ Fallback PDF generated successfully: {len(pdf_response.content)} bytes")
            
            # Cleanup - delete test article
            try:
                self.session.delete(f"{self.base_url}/content-library/article/{article_id}")
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Fallback content test error: {e}")
            return False
    
    def create_test_article(self):
        """Create a test article for PDF testing"""
        test_data = {
            "title": "PDF Quality Test Article", 
            "content": """
            <h1>PDF Quality Test Article</h1>
            <p>This is a comprehensive test article for PDF generation functionality.</p>
            
            <h2>Section 1: Basic Content</h2>
            <p>This section contains basic paragraph content to test text rendering in PDF format. The content should be properly formatted with appropriate spacing and typography.</p>
            
            <h2>Section 2: Lists and Formatting</h2>
            <ul>
                <li>First list item with standard formatting</li>
                <li>Second item with <strong>bold text</strong> and <em>italic text</em></li>
                <li>Third item with mixed content</li>
            </ul>
            
            <h2>Section 3: Tables</h2>
            <table border="1">
                <tr><th>Column 1</th><th>Column 2</th><th>Column 3</th></tr>
                <tr><td>Data 1</td><td>Data 2</td><td>Data 3</td></tr>
                <tr><td>Test A</td><td>Test B</td><td>Test C</td></tr>
            </table>
            
            <p>This article should generate a substantial PDF with proper formatting, styling, and professional appearance.</p>
            """,
            "author": "PDF Test System",
            "source_type": "manual"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/content-library/create", json=test_data)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Failed to create test article: {e}")
        
        return None
    
    def create_test_training_session(self):
        """Create a test training session"""
        # This would require uploading a document to create a training session
        # For now, return None to indicate no session created
        print("⚠️ Cannot create training session without document upload")
        return None
    
    def run_all_tests(self):
        """Run all PDF generation tests"""
        print("🧪 Starting Comprehensive PDF Generation Testing")
        print("=" * 60)
        
        tests = [
            ("Content Library PDF Download", self.test_content_library_pdf_download),
            ("Training Interface PDF Download", self.test_training_interface_pdf_download),  
            ("PDF Fallback Content", self.test_pdf_with_fallback_content)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n🔬 Running: {test_name}")
            try:
                result = test_func()
                results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"📊 {test_name}: {status}")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE PDF TESTING SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL PDF GENERATION TESTS PASSED!")
            print("✅ Fixed PDF generation functionality is working correctly")
        else:
            print("⚠️ Some PDF tests failed - review the output above")
        
        return passed == total

if __name__ == "__main__":
    runner = PDFTestRunner()
    success = runner.run_all_tests()
    exit(0 if success else 1)